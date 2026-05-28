"""
Item Detail Page Object — maps to detail.dart
"""
from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage


class ItemDetailPage(BasePage):
    """Page object for product detail screen."""

    ITEM_NAME = (AppiumBy.ACCESSIBILITY_ID, 'item_detail_name')
    ITEM_PRICE = (AppiumBy.ACCESSIBILITY_ID, 'item_detail_price')
    ITEM_DESCRIPTION = (AppiumBy.ACCESSIBILITY_ID, 'item_detail_description')
    ADD_TO_CART_BUTTON = (AppiumBy.ACCESSIBILITY_ID, 'add_to_cart_button')
    ADD_SUBSCRIPTION_BUTTON = (AppiumBy.ACCESSIBILITY_ID, 'add_subscription_button')
    QUANTITY_SELECTOR = (AppiumBy.ACCESSIBILITY_ID, 'quantity_selector')
    BACK_BUTTON = (AppiumBy.ACCESSIBILITY_ID, 'item_detail_back')

    def get_item_name(self) -> str:
        return self.get_text(*self.ITEM_NAME)

    def get_item_price(self) -> str:
        return self.get_text(*self.ITEM_PRICE)

    def add_to_cart(self):
        """Tap add to cart button."""
        self.tap(*self.ADD_TO_CART_BUTTON)
        self.wait_for_loading_gone()
        return self

    def go_back(self):
        """Navigate back to catalog."""
        self.tap(*self.BACK_BUTTON)
        return self