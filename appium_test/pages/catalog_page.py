"""
Catalog Page Object — maps to menu.dart, menu_tab.dart
Uses text-based selectors matching actual UI.
"""
from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage


class CatalogPage(BasePage):
    """Page object for product catalog (Menu tab)."""

    # Menu tab (menu_tab.dart) - same as menu.dart
    MENU_TITLE = (AppiumBy.XPATH, '//android.widget.TextView[@content-desc="Menu"]')

    # Search field
    SEARCH_FIELD = (AppiumBy.XPATH, '//android.widget.EditText')
    SEARCH_HINT = (AppiumBy.XPATH, '//android.widget.EditText[@hint="Search juices..."]')

    # No results
    NO_RESULTS = (AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().descriptionContains("No juices found")')

    # Product categories visible in menu items
    MANGO_PUNCH = (AppiumBy.XPATH, '//android.widget.TextView[@content-desc="Mango Punch"]')
    GREEN_DETOX = (AppiumBy.XPATH, '//android.widget.TextView[@content-desc="Green Detox"]')
    BERRY_BLAST = (AppiumBy.XPATH, '//android.widget.TextView[@content-desc="Berry Blast"]')

    def search(self, query: str):
        """Type search query."""
        self.type_text(*self.SEARCH_HINT, query)
        self.driver.press_keycode(66)  # KEYCODE_ENTER
        self.wait_for_loading_gone()
        return self

    def tap_product_by_name(self, product_name: str):
        """Tap on a product item in the catalog by name."""
        self.scroll_to_text(product_name)
        locator = (AppiumBy.XPATH, f'//android.widget.TextView[@content-desc="{product_name}"]')
        self.tap(*locator)
        return self

    def is_product_visible(self, product_name: str) -> bool:
        """Check if a product appears in the catalog."""
        locator = (AppiumBy.XPATH, f'//android.widget.TextView[@content-desc="{product_name}"]')
        return self.is_visible(*locator)

    def is_empty_results_shown(self) -> bool:
        return self.is_visible(*self.NO_RESULTS)

    def get_product_count(self) -> int:
        """Get count of visible product TextViews (rough estimate)."""
        els = self.find_elements(
            AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().className("android.view.View")'
        )
        return len(els)