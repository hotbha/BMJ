"""
Base Page Object for BookMyJuice E2E tests.
Provides common wait, action, and assertion helpers using content-desc selectors.
"""
import os
from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from config.test_config import TestConfig


class BasePage:
    """Base class with reusable methods for all page objects."""

    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.wait = WebDriverWait(driver, TestConfig.EXPLICIT_WAIT)
        self.api_wait = WebDriverWait(driver, TestConfig.API_WAIT)

    # ── Locator Helpers ──

    @staticmethod
    def desc(text: str):
        """UiSelector by exact content-desc match."""
        return AppiumBy.ANDROID_UIAUTOMATOR, \
            f'new UiSelector().description("{text}")'

    @staticmethod
    def desc_contains(text: str):
        """UiSelector by content-desc contains."""
        return AppiumBy.ANDROID_UIAUTOMATOR, \
            f'new UiSelector().descriptionContains("{text}")'

    @staticmethod
    def edit_text_instance(instance: int = 0):
        """UiSelector by EditText class and instance index."""
        return AppiumBy.ANDROID_UIAUTOMATOR, \
            f'new UiSelector().className("android.widget.EditText").instance({instance})'

    @staticmethod
    def view_instance(instance: int = 0):
        """UiSelector by View class and instance index."""
        return AppiumBy.ANDROID_UIAUTOMATOR, \
            f'new UiSelector().className("android.view.View").instance({instance})'

    @staticmethod
    def button_contains(text: str):
        """UiSelector for button with description containing text."""
        return AppiumBy.ANDROID_UIAUTOMATOR, \
            f'new UiSelector().className("android.widget.Button").descriptionContains("{text}")'

    # ── Element Locators ──

    def find_element(self, by: str, value: str, timeout: int = None):
        """Find an element with explicit wait."""
        wt = WebDriverWait(self.driver, timeout or TestConfig.EXPLICIT_WAIT)
        return wt.until(EC.presence_of_element_located((by, value)))

    def find_elements(self, by: str, value: str, timeout: int = None):
        """Find all matching elements."""
        try:
            wt = WebDriverWait(self.driver, timeout or TestConfig.EXPLICIT_WAIT)
            return wt.until(EC.presence_of_all_elements_located((by, value)))
        except (TimeoutException, NoSuchElementException):
            return []

    def find_visible_element(self, by: str, value: str, timeout: int = None):
        """Find a visible element."""
        wt = WebDriverWait(self.driver, timeout or TestConfig.EXPLICIT_WAIT)
        return wt.until(EC.visibility_of_element_located((by, value)))

    def find_clickable_element(self, by: str, value: str, timeout: int = None):
        """Find a clickable element."""
        wt = WebDriverWait(self.driver, timeout or TestConfig.EXPLICIT_WAIT)
        return wt.until(EC.element_to_be_clickable((by, value)))

    # ── Actions ──

    def tap(self, by: str, value: str, timeout: int = None):
        """Tap an element.
        
        First tries find_clickable_element (works for android.widget.Button).
        Falls back to find_element + click for other element types.
        """
        try:
            el = self.find_clickable_element(by, value, timeout)
        except (TimeoutException, NoSuchElementException):
            el = self.find_element(by, value, timeout)
        el.click()
        return self

    def type_text(self, by: str, value: str, text: str, timeout: int = None):
        """Type text into an element (clear first)."""
        el = self.find_element(by, value, timeout)
        el.clear()
        el.send_keys(text)
        return self

    def get_text(self, by: str, value: str, timeout: int = None) -> str:
        """Get text content of an element."""
        el = self.find_element(by, value, timeout)
        return el.text

    def is_visible(self, by: str, value: str, timeout: int = None) -> bool:
        """Check if an element is visible."""
        try:
            self.find_visible_element(by, value, timeout or 5)
            return True
        except (TimeoutException, NoSuchElementException):
            return False

    def is_present(self, by: str, value: str, timeout: int = None) -> bool:
        """Check if an element is present in DOM."""
        try:
            self.find_element(by, value, timeout or 5)
            return True
        except (TimeoutException, NoSuchElementException):
            return False

    def wait_for_element_gone(self, by: str, value: str, timeout: int = None):
        """Wait for element to disappear."""
        wt = WebDriverWait(self.driver, timeout or TestConfig.API_WAIT)
        wt.until(EC.invisibility_of_element_located((by, value)))
        return self

    def wait_for_loading_gone(self, timeout: int = None):
        """Wait for any loading indicator to disappear."""
        for indicator in [
            (AppiumBy.ACCESSIBILITY_ID, 'loading_indicator'),
            (AppiumBy.CLASS_NAME, 'android.widget.ProgressBar'),
        ]:
            try:
                self.wait_for_element_gone(indicator[0], indicator[1], timeout or 10)
            except (TimeoutException, NoSuchElementException):
                pass
        return self

    # ── Scrolling ──

    def scroll_to_text(self, text: str):
        """Scroll to element containing text using UiScrollable."""
        ui_string = (
            f'new UiScrollable(new UiSelector().scrollable(true))'
            f'.scrollIntoView(new UiSelector().textContains("{text}"))'
        )
        self.driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, ui_string)
        return self

    def scroll_to_desc(self, text: str):
        """Scroll to element whose content-desc contains text using UiScrollable.
        
        Use this instead of scroll_to_text for Flutter apps, since Flutter
        renders text into the content-desc attribute, not the text attribute.
        """
        ui_string = (
            f'new UiScrollable(new UiSelector().scrollable(true))'
            f'.scrollIntoView(new UiSelector().descriptionContains("{text}"))'
        )
        self.driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, ui_string)
        return self

    def scroll_down(self):
        """Scroll down once."""
        size = self.driver.get_window_size()
        start_x = size['width'] // 2
        start_y = int(size['height'] * 0.8)
        end_y = int(size['height'] * 0.2)
        self.driver.swipe(start_x, start_y, start_x, end_y, 800)
        return self

    # ── Screenshot ──

    def screenshot(self, name: str) -> str:
        """Take a screenshot and save to reports directory."""
        screenshots_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'reports', 'screenshots'
        )
        os.makedirs(screenshots_dir, exist_ok=True)
        path = os.path.join(screenshots_dir, f'{name}.png')
        self.driver.save_screenshot(path)
        return path

    # ── Helpers ──

    def press_back(self):
        """Press Android back button."""
        self.driver.press_keycode(4)  # KEYCODE_BACK
        return self

    def press_home(self):
        """Press Android home button."""
        self.driver.press_keycode(3)  # KEYCODE_HOME
        return self

    def wait_for_text(self, text: str, timeout: int = None):
        """Wait for text to appear on screen using content-desc."""
        wt = WebDriverWait(self.driver, timeout or TestConfig.EXPLICIT_WAIT)
        wt.until(EC.presence_of_element_located(
            (AppiumBy.ANDROID_UIAUTOMATOR,
             f'new UiSelector().descriptionContains("{text}")')
        ))
        return self