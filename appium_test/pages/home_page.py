"""
Home/Dashboard Page Object — maps to dashboard.dart
"""
from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage


class HomePage(BasePage):
    """Page object for the main dashboard/home screen."""

    DASHBOARD_TITLE = (AppiumBy.ACCESSIBILITY_ID, 'dashboard_title')
    NOTIFICATION_BELL = (AppiumBy.ACCESSIBILITY_ID, 'notification_bell')
    NOTIFICATION_BADGE = (AppiumBy.ACCESSIBILITY_ID, 'notification_badge')
    PROFILE_BUTTON = (AppiumBy.ACCESSIBILITY_ID, 'profile_button')
    SUBSCRIPTION_CARD = (AppiumBy.ACCESSIBILITY_ID, 'subscription_card')
    CATALOG_CARD = (AppiumBy.ACCESSIBILITY_ID, 'catalog_card')
    CART_BUTTON = (AppiumBy.ACCESSIBILITY_ID, 'cart_button')

    def navigate_to_catalog(self):
        """Navigate to product catalog."""
        self.tap(*self.CATALOG_CARD)
        return self

    def navigate_to_subscription(self):
        """Navigate to subscription flow."""
        self.tap(*self.SUBSCRIPTION_CARD)
        return self

    def navigate_to_notifications(self):
        """Open notification centre."""
        self.tap(*self.NOTIFICATION_BELL)
        return self

    def navigate_to_profile(self):
        """Open profile screen."""
        self.tap(*self.PROFILE_BUTTON)
        return self

    def navigate_to_cart(self):
        """Open cart screen."""
        self.tap(*self.CART_BUTTON)
        return self

    def get_dashboard_title(self) -> str:
        return self.get_text(*self.DASHBOARD_TITLE)