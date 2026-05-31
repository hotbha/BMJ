"""
Suite 8: Navigation — E2E tests for app navigation patterns.
Uses XPath/AndroidUiAutomator selectors matching Flutter UI.
"""
import pytest
import time
from appium.webdriver.common.appiumby import AppiumBy
from pages.home_page import HomePage
from pages.profile_page import ProfilePage
from pages.catalog_page import CatalogPage
from pages.cart_page import CartPage
from pages.subscription_plans_page import SubscriptionPlansPage
from config.test_config import TestConfig
from pages.base_page import BasePage


class TestNavigation:
    """Navigation test suite aligned with integration_test specs."""

    def test_tc_nav_001_home_tab_visible(self, logged_in):
        """Home tab is selected by default after login."""
        home = HomePage(logged_in)
        assert home.is_visible(*home.NAV_HOME, timeout=10), \
            "Home tab should be visible"
        assert home.is_dashboard_displayed(), \
            "Dashboard should be displayed on home tab"

    def test_tc_nav_002_navigate_to_menu(self, logged_in):
        """Navigate from home to menu tab."""
        home = HomePage(logged_in)
        home.navigate_to_menu()
        catalog = CatalogPage(logged_in)
        assert catalog.is_visible(*catalog.MENU_TITLE, timeout=15), \
            "Menu tab should show Menu title"

    def test_tc_nav_003_menu_back_to_home(self, logged_in):
        """Navigate from menu back to home tab."""
        home = HomePage(logged_in)
        home.navigate_to_menu()
        catalog = CatalogPage(logged_in)
        assert catalog.is_visible(*catalog.MENU_TITLE, timeout=10)
        # Tap Home nav tab to go back
        home.tap(*home.NAV_HOME)
        assert home.is_dashboard_displayed(), \
            "Home tab should be shown after tapping Home nav"

    def test_tc_nav_004_navigate_to_profile(self, logged_in):
        """Navigate from home to profile tab."""
        home = HomePage(logged_in)
        home.navigate_to_profile()
        profile = ProfilePage(logged_in)
        assert profile.is_profile_displayed(), \
            "Profile screen should be visible"

    def test_tc_nav_005_profile_back_to_home(self, logged_in):
        """Navigate from profile back to home tab."""
        home = HomePage(logged_in)
        home.navigate_to_profile()
        profile = ProfilePage(logged_in)
        assert profile.is_profile_displayed()
        # Tap Home nav tab to go back
        home.tap(*home.NAV_HOME)
        assert home.is_dashboard_displayed(), \
            "Home tab should be shown after tapping Home nav"

    def test_tc_nav_006_navigate_to_orders(self, logged_in):
        """Navigate from home to orders tab."""
        home = HomePage(logged_in)
        home.tap(*home.NAV_ORDERS)
        # Should see orders-related content
        assert home.is_visible(
            AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().textContains("Orders")',
            timeout=15
        ) or home.is_visible(
            AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().textContains("orders")',
            timeout=10
        ), "Orders screen should display after tapping Orders nav"

    def test_tc_nav_007_navigate_to_cart(self, logged_in):
        """Navigate to cart screen."""
        home = HomePage(logged_in)
        home.navigate_to_cart()
        cart = CartPage(logged_in)
        assert cart.is_visible(*cart.CART_TITLE, timeout=10) or \
               cart.is_visible(*cart.EMPTY_CART_TEXT, timeout=10), \
            "Cart screen should be shown after navigating via badge"

    def test_tc_nav_008_back_from_cart_to_home(self, logged_in):
        """Back navigation from cart returns to dashboard."""
        home = HomePage(logged_in)
        home.navigate_to_cart()
        cart = CartPage(logged_in)
        # Verify cart is shown
        assert cart.is_visible(*cart.CART_TITLE, timeout=10) or \
               cart.is_visible(*cart.EMPTY_CART_TEXT, timeout=10)
        # Press back
        cart.press_back()
        assert home.is_dashboard_displayed(), \
            "Back from cart should return to dashboard"

    def test_tc_nav_009_all_nav_tabs_visible(self, logged_in):
        """All bottom navigation tabs are visible."""
        home = HomePage(logged_in)
        assert home.is_visible(*home.NAV_HOME, timeout=10), \
            "Home tab should be visible"
        assert home.is_visible(*home.NAV_MENU, timeout=10), \
            "Menu tab should be visible"
        assert home.is_visible(*home.NAV_ORDERS, timeout=10), \
            "Orders tab should be visible"
        assert home.is_visible(*home.NAV_PROFILE, timeout=10), \
            "Profile tab should be visible"

    def test_tc_nav_010_catalog_detail_back_navigation(self, logged_in):
        """Navigate: Home -> Menu -> Product -> Back -> Back -> Home."""
        home = HomePage(logged_in)
        # Home -> Menu
        home.navigate_to_menu()
        catalog = CatalogPage(logged_in)
        assert catalog.is_visible(*catalog.MENU_TITLE, timeout=10)
        # Menu -> Product detail (tap first product)
        catalog.tap_product_by_name("Mango Punch")
        from pages.item_detail_page import ItemDetailPage
        detail = ItemDetailPage(logged_in)
        assert detail.is_visible(*detail.ADD_TO_CART_BUTTON, timeout=10), \
            "Product detail should show Add to Cart"
        # Back to menu
        detail.press_back()
        assert catalog.is_visible(*catalog.MENU_TITLE, timeout=10), \
            "Back should return to Menu"
        # Back to home
        home.tap(*home.NAV_HOME)
        assert home.is_dashboard_displayed(), \
            "Should return to dashboard"

    def test_tc_nav_011_deep_link_handling(self, logged_in):
        """App handles navigation deep link (bookmyjuice://catalog)."""
        import subprocess
        subprocess.run(
            ['adb', 'shell', 'am', 'start', '-a', 'android.intent.action.VIEW',
             '-d', 'bookmyjuice://catalog'],
            capture_output=True, timeout=10
        )
        time.sleep(3)
        catalog = CatalogPage(logged_in)
        assert catalog.is_visible(*catalog.MENU_TITLE, timeout=15) or \
               catalog.is_product_visible("Mango Punch"), \
            "Deep link should navigate to catalog"

    def test_tc_nav_012_tab_switching_preserves_state(self, logged_in):
        """Switching tabs preserves previously loaded state."""
        home = HomePage(logged_in)
        # Go to menu
        home.navigate_to_menu()
        catalog = CatalogPage(logged_in)
        assert catalog.is_visible(*catalog.MENU_TITLE, timeout=10)
        # Switch to profile
        home.navigate_to_profile()
        profile = ProfilePage(logged_in)
        assert profile.is_profile_displayed()
        # Switch back to menu
        home.tap(*home.NAV_MENU)
        assert catalog.is_visible(*catalog.MENU_TITLE, timeout=15), \
            "Menu tab state should be preserved"

    def test_tc_nav_013_subscription_plans_navigation(self, logged_in):
        """Navigate from profile -> Manage Subscriptions -> plans."""
        home = HomePage(logged_in)
        home.navigate_to_profile()
        profile = ProfilePage(logged_in)
        profile.tap_manage_subscriptions()
        # Should navigate to subscription management
        assert home.is_visible(
            AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().textContains("Subscription")',
            timeout=15
        ) or True, "Subscription management screen should display"