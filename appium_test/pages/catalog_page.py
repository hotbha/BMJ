"""
Catalog Page Object — maps to product_catalog_screen.dart
"""
from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage


class CatalogPage(BasePage):
    """Page object for product catalog."""

    CATALOG_LIST = (AppiumBy.ACCESSIBILITY_ID, 'catalog_list')
    SEARCH_FIELD = (AppiumBy.ACCESSIBILITY_ID, 'catalog_search_field')
    FAMILY_FILTER_JUICE = (AppiumBy.ACCESSIBILITY_ID, 'family_filter_juice')
    FAMILY_FILTER_SMOOTHIE = (AppiumBy.ACCESSIBILITY_ID, 'family_filter_smoothie')
    FAMILY_FILTER_DETOX = (AppiumBy.ACCESSIBILITY_ID, 'family_filter_detox')
    EMPTY_RESULTS = (AppiumBy.ACCESSIBILITY_ID, 'catalog_empty_results')
    LOADING_INDICATOR = (AppiumBy.ACCESSIBILITY_ID, 'catalog_loading')

    def tap_product_by_name(self, product_name: str):
        """Tap on a product item in the catalog by name."""
        ui_string = (
            f'new UiScrollable(new UiSelector().scrollable(true))'
            f'.scrollIntoView(new UiSelector().textContains("{product_name}"))'
        )
        el = self.driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, ui_string)
        el.click()
        return self

    def search(self, query: str):
        """Type search query and submit."""
        self.type_text(*self.SEARCH_FIELD, query)
        self.driver.press_keycode(66)  # KEYCODE_ENTER
        self.wait_for_loading_gone()
        return self

    def filter_by_family(self, family: str):
        """Filter products by family name."""
        family_map = {
            'juice': self.FAMILY_FILTER_JUICE,
            'smoothie': self.FAMILY_FILTER_SMOOTHIE,
            'detox': self.FAMILY_FILTER_DETOX,
        }
        locator = family_map.get(family.lower())
        if locator:
            self.tap(*locator)
        return self

    def get_product_count(self) -> int:
        """Get count of visible product items."""
        els = self.find_elements(
            AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().className("android.widget.LinearLayout")'
        )
        return len(els)

    def is_empty_results_shown(self) -> bool:
        return self.is_visible(*self.EMPTY_RESULTS)