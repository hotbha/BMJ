"""
Item Detail Page Object — maps to detail.dart
Uses text-based selectors.
"""
from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage
from config.test_config import TestConfig


class ItemDetailPage(BasePage):
    """Page object for product detail screen."""

    ADD_TO_CART_BUTTON = (AppiumBy.XPATH, '//android.widget.TextView[contains(@content-desc, "Add to Cart")]')
    ADD_TO_SUBSCRIPTION = (AppiumBy.XPATH, '//android.widget.TextView[contains(@content-desc, "Add to Subscription")]')
    BACK_BUTTON = (AppiumBy.XPATH, '//android.widget.EditText/preceding-sibling::android.widget.TextView')

    def add_to_cart(self):
        """Add item to cart."""
        self.scroll_to_text("Add to Cart")
        self.tap(*self.ADD_TO_CART_BUTTON)
        self.wait_for_loading_gone(TestConfig.API_WAIT)
        return self

    def go_back(self):
        """Navigate back."""
        self.tap(*self.BACK_BUTTON)
        return self

    def get_item_name(self) -> str:
        """Get item name from screen."""
        els = self.find_elements(AppiumBy.CLASS_NAME, 'android.widget.TextView')
        # First large text is typically the name
        for el in els:
            text = el.text
            if text and len(text) > 2 and text not in ('Menu', 'Add to Cart',
                'Add to Subscription', '+', '-'):
                return text
        return ''

    def get_item_price(self) -> str:
        """Get item price text."""
        try:
            return self.get_text(AppiumBy.XPATH, '//android.widget.TextView[starts-with(@content-desc, "₹")]')
        except Exception:
            return ''