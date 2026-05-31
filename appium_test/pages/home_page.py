"""
Home/Dashboard Page Object — maps to dashboard.dart + home_tab.dart
Flutter text renders in content-desc attribute.

Key point: Dashboard is ALWAYS shown to ALL users (including unauthenticated)
on app launch. Login is NOT the initial screen.
"""
from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage
from config.test_config import TestConfig


class HomePage(BasePage):
    """Page object for the main dashboard/home screen."""

    # Dashboard header
    BOOKMYJUICE_HEADER = BasePage.desc_contains("BookMyJuice")

    # Nav bar tab locators — using desc_contains because NavigationBar's internal
    # MergeSemantics always produces a combined content-desc like "Home\nTab 1 of 4".
    # We match on the NavigationDestination label text ("Home", "Catalog", etc.)
    # which is always present in the merged tree regardless of selected state.
    NAV_HOME = BasePage.desc_contains("Home")
    NAV_MENU = BasePage.desc_contains("Catalog")
    NAV_ORDERS = BasePage.desc_contains("Subscription")
    NAV_PROFILE = BasePage.desc_contains("Profile")

    # Hero / greeting (guest mode shows "Welcome to\nBookMyJuice!")
    WELCOME_TEXT = BasePage.desc_contains("Welcome to")
    WELCOME_TEXT_ALT = BasePage.desc_contains("Welcome to")

    # Offer carousel
    SUMMER_DETOX_OFFER = BasePage.desc_contains("Summer Detox")
    REFER_EARN_OFFER = BasePage.desc_contains("Refer")

    # Subscription section
    NO_ACTIVE_PLAN = BasePage.desc_contains("No Active Plan")
    START_SUBSCRIPTION = BasePage.desc_contains("Start your subscription")
    SUBSCRIBE_BUTTON = BasePage.desc_contains("Subscribe")
    MODIFY_BUTTON = BasePage.desc_contains("Modify")

    # Stats strip
    CALORIES_STAT = BasePage.desc_contains("Calories")
    FRESH_STAT = BasePage.desc_contains("Fresh")
    DELIVERY_STAT = BasePage.desc_contains("Delivery")

    # View Menu link
    VIEW_MENU = BasePage.desc_contains("View Menu")

    # Profile / orders section (only when authenticated)
    RECENT_ORDERS = BasePage.desc_contains("Recent Orders")

    def is_dashboard_displayed(self, timeout: int = None) -> bool:
        """Check if dashboard is displayed by looking for header or nav bar."""
        return (
            self.is_visible(*self.BOOKMYJUICE_HEADER, timeout=timeout or 5) or
            self.is_visible(*self.NAV_HOME, timeout=timeout or 5)
        )

    def wait_for_dashboard(self, timeout: int = None):
        """Wait for dashboard to appear (after splash auto-nav or login)."""
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        wt = WebDriverWait(self.driver, timeout or TestConfig.API_WAIT)
        wt.until(lambda d: self.is_dashboard_displayed(timeout=5))
        return self

    def navigate_to_menu(self):
        """Switch to Menu tab."""
        self.tap(*self.NAV_MENU)
        return self

    def navigate_to_orders(self):
        """Switch to Orders tab."""
        self.tap(*self.NAV_ORDERS)
        return self

    def navigate_to_profile(self):
        """Switch to Profile tab."""
        self.tap(*self.NAV_PROFILE)
        return self

    def tap_subscribe(self):
        """Tap Subscribe button."""
        self.tap(*self.SUBSCRIBE_BUTTON)
        return self

    def navigate_to_home(self):
        """Switch to Home dashboard tab."""
        self.tap(*self.NAV_HOME)
        return self
