"""
Cart Page Object — maps to cart_screen.dart
Uses text-based selectors matching actual UI.
"""
from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage
from config.test_config import TestConfig


class CartPage(BasePage):
    """Page object for cart screen."""

    # Cart Screen (cart_screen.dart)
    # AppBar title
    CART_TITLE = (AppiumBy.XPATH, '//android.widget.TextView[@content-desc="My Cart"]')
    
    # Empty cart
    EMPTY_CART_TEXT = (AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().descriptionContains("Your cart is empty")')
    EMPTY_CART_SUBTITLE = (AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().descriptionContains("Add juices")')
    START_SHOPPING_BUTTON = (AppiumBy.XPATH, '//android.widget.TextView[@content-desc="Start Shopping"]')

    # Cart items - dynamic text
    CART_ITEM_PRICE = (AppiumBy.XPATH, '//android.widget.TextView[starts-with(@content-desc, "₹")]')
    
    # Quantity controls
    PLUS_BUTTON = (AppiumBy.XPATH, '//android.widget.TextView[@content-desc="+"]')
    MINUS_BUTTON = (AppiumBy.XPATH, '//android.widget.TextView[@content-desc="-"]')
    
    # Remove button
    REMOVE_BUTTON_XPATH = (AppiumBy.XPATH, '//android.widget.TextView[contains(@content-desc, "Remove")]')

    # Bottom checkout bar
    TOTAL_AMOUNT = (AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().descriptionContains("Total")')
    PLACE_ORDER_BUTTON = (AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().descriptionContains("Place Order")')

    def is_empty(self) -> bool:
        """Check if cart is empty."""
        return self.is_visible(*self.EMPTY_CART_TEXT)

    def get_total_text(self) -> str:
        """Get the total amount text."""
        return self.get_text(*self.TOTAL_AMOUNT)

    def tap_place_order(self):
        """Proceed to checkout."""
        self.tap(*self.PLACE_ORDER_BUTTON)
        self.wait_for_loading_gone(TestConfig.API_WAIT)
        return self

    def tap_start_shopping(self):
        """Navigate to catalog from empty cart."""
        self.tap(*self.START_SHOPPING_BUTTON)
        return self

    def tap_plus(self):
        """Increase quantity."""
        self.tap(*self.PLUS_BUTTON)
        return self

    def tap_minus(self):
        """Decrease quantity."""
        self.tap(*self.MINUS_BUTTON)
        return self

    def tap_remove(self):
        """Remove item from cart."""
        self.tap(*self.REMOVE_BUTTON_XPATH)
        return self