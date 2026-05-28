"""
Cart Page Object — maps to cart_screen.dart
"""
from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage


class CartPage(BasePage):
    """Page object for cart screen."""

    CART_LIST = (AppiumBy.ACCESSIBILITY_ID, 'cart_list')
    CART_TOTAL = (AppiumBy.ACCESSIBILITY_ID, 'cart_total')
    CHECKOUT_BUTTON = (AppiumBy.ACCESSIBILITY_ID, 'checkout_button')
    EMPTY_CART_MESSAGE = (AppiumBy.ACCESSIBILITY_ID, 'empty_cart_message')
    QUANTITY_INCREASE = (AppiumBy.ACCESSIBILITY_ID, 'quantity_increase')
    QUANTITY_DECREASE = (AppiumBy.ACCESSIBILITY_ID, 'quantity_decrease')
    REMOVE_ITEM_BUTTON = (AppiumBy.ACCESSIBILITY_ID, 'remove_item_button')

    @staticmethod
    def quantity_field(item_id: str):
        """Get quantity field for a specific item."""
        return (AppiumBy.ACCESSIBILITY_ID, f'quantity_{item_id}')

    def get_cart_total(self) -> str:
        return self.get_text(*self.CART_TOTAL)

    def tap_checkout(self):
        """Proceed to checkout."""
        self.tap(*self.CHECKOUT_BUTTON)
        self.wait_for_loading_gone()
        return self

    def is_empty(self) -> bool:
        return self.is_visible(*self.EMPTY_CART_MESSAGE)

    def increase_quantity(self):
        self.tap(*self.QUANTITY_INCREASE)
        return self

    def decrease_quantity(self):
        self.tap(*self.QUANTITY_DECREASE)
        return self

    def remove_item(self):
        self.tap(*self.REMOVE_ITEM_BUTTON)
        return self