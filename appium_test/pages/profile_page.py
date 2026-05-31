"""
Profile Page Object — maps to profile_tab.dart
Uses content-desc-based selectors from actual UI dump.

Guest Profile:
  - "Welcome to BookMyJuice!"
  - "Sign in to manage your account"
  - GlassCard "Sign In" button → /login

Authenticated Profile:
  - Order History, Refer & Earn, Invoices, Manage Subscriptions
  - Theme toggle, Logout with confirmation bottom sheet
"""
from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage
from config.test_config import TestConfig


class ProfilePage(BasePage):
    """Page object for profile tab shown in navigation."""

    # Accessibility IDs (from Semantics labels in profile_tab.dart)
    ACC_SIGN_IN = (AppiumBy.ACCESSIBILITY_ID, "Sign In")
    ACC_ORDER_HISTORY = (AppiumBy.ACCESSIBILITY_ID, "Order History")
    ACC_REFER_EARN = (AppiumBy.ACCESSIBILITY_ID, "Refer & Earn")
    ACC_INVOICES = (AppiumBy.ACCESSIBILITY_ID, "Invoices")
    ACC_MANAGE_SUBS = (AppiumBy.ACCESSIBILITY_ID, "Manage Subscriptions")

    # Guest profile (not authenticated)
    # From actual UI dump: "Welcome to\nBookMyJuice!" has \n
    # Sign In on profile is wrapped by GlassCard. Flutter's Semantics(label: 'Sign In')
    # may not produce an exact ACCESSIBILITY_ID match, so use desc_contains for reliability.
    WELCOME_GUEST = BasePage.desc_contains("Welcome to")
    SIGN_IN_PROMPT = BasePage.desc_contains("Sign in to manage")
    SIGN_IN_BUTTON_PROFILE = BasePage.desc_contains("Sign In")

    # Authenticated profile menu items
    ORDER_HISTORY_MENU = ACC_ORDER_HISTORY
    REFER_EARN_MENU = ACC_REFER_EARN
    INVOICES_MENU = ACC_INVOICES
    MANAGE_SUBS_MENU = ACC_MANAGE_SUBS
    THEME_TOGGLE = BasePage.desc_contains("Theme")

    # Logout — note: both menu item and confirm button share "Logout" content-desc
    LOGOUT_MENU = BasePage.desc_contains("Logout")
    LOGOUT_CONFIRM = BasePage.desc_contains("Logout")
    LOGOUT_CANCEL = BasePage.desc_contains("Cancel")

    # Version text
    VERSION_TEXT = BasePage.desc_contains("BookMyJuice v")

    def is_profile_displayed(self) -> bool:
        """Check if profile screen is visible."""
        return (self.is_visible(*self.SIGN_IN_BUTTON_PROFILE, timeout=5) or
                self.is_visible(*self.WELCOME_GUEST, timeout=5))

    def is_guest(self) -> bool:
        """Check if showing guest (unauthenticated) profile."""
        return self.is_visible(*self.WELCOME_GUEST, timeout=3)

    def tap_sign_in(self):
        """Tap Sign In on guest profile (View element, so use visible + direct click)."""
        # Wait for profile page to load before clicking
        self.wait_for_element(*self.SIGN_IN_BUTTON_PROFILE, timeout=TestConfig.API_WAIT)
        el = self.find_visible_element(*self.SIGN_IN_BUTTON_PROFILE)
        el.click()
        return self

    def tap_order_history(self):
        """Navigate to order history."""
        self.scroll_to_text("Order History")
        self.tap(*self.ORDER_HISTORY_MENU)
        return self

    def tap_manage_subscriptions(self):
        """Navigate to manage subscriptions."""
        self.scroll_to_text("Manage Subscriptions")
        self.tap(*self.MANAGE_SUBS_MENU)
        return self

    def confirm_logout(self):
        """Perform complete logout: tap Logout menu -> confirm."""
        self.scroll_to_text("Logout")
        self.tap(*self.LOGOUT_MENU)
        self.wait_for_element(*self.LOGOUT_CONFIRM,
                              timeout=TestConfig.EXPLICIT_WAIT)
        self.tap(*self.LOGOUT_CONFIRM)
        self.wait_for_loading_gone(TestConfig.API_WAIT)
        return self

    def tap_cancel_logout(self):
        """Cancel logout from bottom sheet."""
        self.scroll_to_text("Logout")
        self.tap(*self.LOGOUT_MENU)
        self.wait_for_element(*self.LOGOUT_CANCEL,
                              timeout=TestConfig.EXPLICIT_WAIT)
        self.tap(*self.LOGOUT_CANCEL)
        return self

    def wait_for_element(self, by, value, timeout=None):
        """Wait for an element to be visible."""
        return self.find_visible_element(by, value, timeout)