"""
Order/Checkout Page Object — maps to orders/order_checkout_screen.dart
Also handles checkout_screen.dart (legacy)
"""
from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage


class OrderCheckoutPage(BasePage):
    """Page object for order checkout screen."""

    ORDER_ADDRESS = (AppiumBy.ACCESSIBILITY_ID, 'order_address')
    CHANGE_ADDRESS_BUTTON = (AppiumBy.ACCESSIBILITY_ID, 'change_address_button')
    ORDER_ITEM_LIST = (AppiumBy.ACCESSIBILITY_ID, 'order_item_list')
    ORDER_TOTAL = (AppiumBy.ACCESSIBILITY_ID, 'order_total')
    PLACE_ORDER_BUTTON = (AppiumBy.ACCESSIBILITY_ID, 'place_order_button')
    ORDER_LOADING = (AppiumBy.ACCESSIBILITY_ID, 'order_loading')
    ORDER_SUCCESS_MESSAGE = (AppiumBy.ACCESSIBILITY_ID, 'order_success_message')

    def get_address_text(self) -> str:
        return self.get_text(*self.ORDER_ADDRESS)

    def get_order_total(self) -> str:
        return self.get_text(*self.ORDER_TOTAL)

    def place_order(self):
        """Place the order."""
        self.tap(*self.PLACE_ORDER_BUTTON)
        self.wait_for_loading_gone()
        return self

    def is_order_successful(self) -> bool:
        return self.is_visible(*self.ORDER_SUCCESS_MESSAGE)

    def change_address(self):
        self.tap(*self.CHANGE_ADDRESS_BUTTON)
        return self