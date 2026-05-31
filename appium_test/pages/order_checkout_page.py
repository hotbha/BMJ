"""
Order Checkout Page Object — maps to checkout_screen.dart, delivery_slot_selection_screen.dart
"""
from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage
from config.test_config import TestConfig
import time


class OrderCheckoutPage(BasePage):
    """Page object for checkout flow."""

    # Delivery Slot Selection
    DELIVERY_SLOT_TITLE = (AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().descriptionContains("Delivery Slot")')
    CONFIRM_SLOT_BUTTON = (AppiumBy.XPATH, '//android.widget.TextView[@content-desc="Confirm Slot"]')

    # Checkout Screen
    CHECKOUT_TITLE = (AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().descriptionContains("Checkout")')
    PLACE_ORDER_BUTTON = (AppiumBy.XPATH, '//android.widget.TextView[contains(@content-desc, "Place Order")]')
    ORDER_TOTAL = (AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().descriptionContains("Total")')

    # Order Confirmation
    ORDER_CONFIRMED = (AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().descriptionContains("Order Placed")')
    ORDER_ID_TEXT = (AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().descriptionContains("Order #")')
    BACK_TO_HOME = (AppiumBy.XPATH, '//android.widget.TextView[contains(@content-desc, "Back to Home")]')

    def select_first_available_slot(self):
        """Select first available delivery slot."""
        try:
            self.wait_for_element(*self.CONFIRM_SLOT_BUTTON, timeout=10)
            self.tap(*self.CONFIRM_SLOT_BUTTON)
        except Exception:
            pass  # slot screen might not appear
        return self

    def place_order(self):
        """Complete order placement."""
        self.scroll_to_text("Place Order")
        self.tap(*self.PLACE_ORDER_BUTTON)
        self.wait_for_loading_gone(TestConfig.API_WAIT)
        time.sleep(3)  # Wait for order processing
        return self

    def is_order_confirmed(self) -> bool:
        """Check if order was successfully placed."""
        return self.is_visible(*self.ORDER_CONFIRMED)

    def get_order_id(self) -> str:
        """Get order ID from confirmation screen."""
        try:
            return self.get_text(*self.ORDER_ID_TEXT)
        except Exception:
            return ''

    def tap_back_to_home(self):
        """Return to dashboard after order."""
        self.tap(*self.BACK_TO_HOME)
        return self