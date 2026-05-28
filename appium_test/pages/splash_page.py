"""
Splash Page Object — maps to splash_page.dart
"""
from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage


class SplashPage(BasePage):
    """Page object for splash screen."""

    SPLASH_LOGO = (AppiumBy.ACCESSIBILITY_ID, 'splash_logo')
    SPLASH_TITLE = (AppiumBy.ACCESSIBILITY_ID, 'splash_title')
    LOGIN_BUTTON = (AppiumBy.ACCESSIBILITY_ID, 'splash_login_button')

    def wait_for_splash(self, timeout: int = 10):
        """Wait for splash screen to load."""
        self.find_visible_element(*self.SPLASH_LOGO, timeout)
        return self

    def navigate_to_login(self):
        """Tap login button to navigate to login screen."""
        self.tap(*self.LOGIN_BUTTON)
        return self