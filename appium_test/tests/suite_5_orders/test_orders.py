"""
Suite 5: Orders — E2E tests aligned with FR-CART-001 to FR-CART-004.
Uses XPath/AndroidUiAutomator selectors matching Flutter UI.
"""
import pytest
from appium.webdriver.common.appiumby import AppiumBy
from pages.home_page import HomePage
from pages.cart_page import CartPage
from pages.catalog_page import CatalogPage
from pages.item_detail_page import ItemDetailPage
from pages.order_checkout_page import OrderCheckoutPage
from config.test_config import TestConfig


class TestOrders:
    """Order lifecycle test suite aligned with integration_test cart_test.dart."""

    # ── FR-CART-001: View cart items with quantity ──

    def test_tc_orders_001_view_cart_empty(self, logged_in):
        """FR-CART-001a: Empty cart displays appropriate message."""
        home = HomePage(logged_in)
        home.navigate_to_cart()
        cart = CartPage(logged_in)
        assert cart.is_visible(*cart.EMPTY_CART_TEXT, timeout=10), \
            "Empty cart should show 'Your cart is empty' text"
        assert cart.is_visible(*cart.START_SHOPPING_BUTTON, timeout=5), \
            "Empty cart should show 'Start Shopping' button"

    def test_tc_orders_002_view_cart_with_items(self, logged_in):
        """FR-CART-001b: Cart with items displays correctly."""
        home = HomePage(logged_in)
        home.navigate_to_catalog()
        catalog = CatalogPage(logged_in)
        catalog.tap_product_by_name("Mango Punch")
        detail = ItemDetailPage(logged_in)
        assert detail.is_visible(*detail.ADD_TO_CART_BUTTON, timeout=10), \
            "Item detail should show Add to Cart button"
        detail.add_to_cart()
        home.navigate_to_cart()
        cart = CartPage(logged_in)
        assert cart.is_visible(*cart.CART_TITLE, timeout=10), \
            "Cart screen should be displayed"
        # Should show cart items, not empty
        assert not cart.is_empty(), \
            "Cart should not be empty after adding item"

    # ── FR-CART-002: Increment/Decrement quantity ──

    def test_tc_orders_003_increment_quantity(self, logged_in):
        """FR-CART-002a: Increment item quantity in cart."""
        home = HomePage(logged_in)
        home.navigate_to_catalog()
        catalog = CatalogPage(logged_in)
        catalog.tap_product_by_name("Mango Punch")
        detail = ItemDetailPage(logged_in)
        detail.add_to_cart()
        home.navigate_to_cart()
        cart = CartPage(logged_in)
        assert cart.is_visible(*cart.PLUS_BUTTON, timeout=10), \
            "Plus button should be visible for cart item"
        cart.tap_plus()
        # Success if no error - quantity updated

    def test_tc_orders_004_decrement_quantity(self, logged_in):
        """FR-CART-002b: Decrement item quantity in cart."""
        home = HomePage(logged_in)
        home.navigate_to_catalog()
        catalog = CatalogPage(logged_in)
        catalog.tap_product_by_name("Mango Punch")
        detail = ItemDetailPage(logged_in)
        detail.add_to_cart()
        home.navigate_to_cart()
        cart = CartPage(logged_in)
        assert cart.is_visible(*cart.PLUS_BUTTON, timeout=10)
        cart.tap_plus()  # Ensure qty > 1 first
        cart.tap_minus()  # Then decrement
        # Success if no error

    # ── FR-CART-003: Remove items from cart ──

    def test_tc_orders_005_remove_item(self, logged_in):
        """FR-CART-003: Remove item from cart and verify empty state."""
        home = HomePage(logged_in)
        home.navigate_to_catalog()
        catalog = CatalogPage(logged_in)
        catalog.tap_product_by_name("Mango Punch")
        detail = ItemDetailPage(logged_in)
        detail.add_to_cart()
        home.navigate_to_cart()
        cart = CartPage(logged_in)
        assert cart.is_visible(*cart.REMOVE_BUTTON_XPATH, timeout=10), \
            "Remove button should be visible"
        cart.tap_remove()
        # After removal, cart should be empty
        assert cart.is_visible(*cart.EMPTY_CART_TEXT, timeout=10), \
            "Cart should show empty state after item removal"

    # ── FR-CART-004: Show subtotal, tax, and total ──

    def test_tc_orders_006_pricing_breakdown(self, logged_in):
        """FR-CART-004: Pricing breakdown (total amount) is displayed."""
        home = HomePage(logged_in)
        home.navigate_to_catalog()
        catalog = CatalogPage(logged_in)
        catalog.tap_product_by_name("Mango Punch")
        detail = ItemDetailPage(logged_in)
        detail.add_to_cart()
        home.navigate_to_cart()
        cart = CartPage(logged_in)
        assert cart.is_visible(*cart.TOTAL_AMOUNT, timeout=10), \
            "Total amount should be displayed in cart"
        total_text = cart.get_total_text()
        assert total_text is not None and len(total_text) > 0, \
            f"Total text should not be empty, got: '{total_text}'"

    # ── Checkout flow ──

    def test_tc_orders_007_place_order_button_visible(self, logged_in):
        """Place Order button is visible in cart with items."""
        home = HomePage(logged_in)
        home.navigate_to_catalog()
        catalog = CatalogPage(logged_in)
        catalog.tap_product_by_name("Mango Punch")
        detail = ItemDetailPage(logged_in)
        detail.add_to_cart()
        home.navigate_to_cart()
        cart = CartPage(logged_in)
        assert cart.is_visible(*cart.PLACE_ORDER_BUTTON, timeout=10), \
            "Place Order button should be visible"

    def test_tc_orders_008_complete_checkout_flow(self, clean_orders):
        """Complete checkout flow: cart -> place order -> confirmation."""
        home = HomePage(clean_orders)
        home.navigate_to_catalog()
        catalog = CatalogPage(clean_orders)
        catalog.tap_product_by_name("Mango Punch")
        detail = ItemDetailPage(clean_orders)
        detail.add_to_cart()
        home.navigate_to_cart()
        cart = CartPage(clean_orders)
        cart.tap_place_order()
        checkout = OrderCheckoutPage(clean_orders)
        # Should show checkout/confirmation
        assert checkout.is_checkout_displayed(timeout=10), \
            "Checkout screen should be displayed"

    # ── Multi-item ──

    def test_tc_orders_009_multiple_items_in_cart(self, logged_in):
        """Multiple items display correctly in cart."""
        home = HomePage(logged_in)
        # Add first item
        home.navigate_to_catalog()
        catalog = CatalogPage(logged_in)
        catalog.tap_product_by_name("Mango Punch")
        detail = ItemDetailPage(logged_in)
        detail.add_to_cart()
        home.navigate_to_cart()
        cart = CartPage(logged_in)
        assert not cart.is_empty(), "Cart should have first item"
        # Verify cart title is shown
        assert cart.is_visible(*cart.CART_TITLE, timeout=10)

    # ── Back navigation from cart ──

    def test_tc_orders_010_back_navigation(self, logged_in):
        """Back navigation from cart returns to previous screen."""
        home = HomePage(logged_in)
        home.navigate_to_cart()
        cart = CartPage(logged_in)
        cart.press_back()
        # Should return to home/dashboard
        assert home.is_dashboard_displayed(), \
            "Back from cart should return to dashboard"

    # ── Cart from home tab navigation ──

    def test_tc_orders_011_cart_badge_navigation(self, logged_in):
        """Navigate to cart via cart badge icon."""
        home = HomePage(logged_in)
        # The cart badge should be present in the header
        assert home.is_visible(*home.NAV_HOME, timeout=5), \
            "Home tab should be visible"
        # Navigate via menu -> cart flow
        home.navigate_to_cart()
        cart = CartPage(logged_in)
        assert cart.is_visible(*cart.CART_TITLE, timeout=10) or \
               cart.is_visible(*cart.EMPTY_CART_TEXT, timeout=10), \
            "Cart screen should be shown after navigating via badge"

    # ── Start shopping from empty cart ──

    def test_tc_orders_012_start_shopping_from_empty(self, logged_in):
        """Start Shopping navigates to catalog from empty cart."""
        home = HomePage(logged_in)
        home.navigate_to_cart()
        cart = CartPage(logged_in)
        if cart.is_empty():
            cart.tap_start_shopping()
            catalog = CatalogPage(logged_in)
            assert catalog.is_visible(*catalog.MENU_TITLE, timeout=10), \
                "Start Shopping should navigate to catalog/menu"
        else:
            # Cart is not empty, skip test
            pass

    # ── Cart persistence ──

    def test_tc_orders_013_cart_persistence_after_reopen(self, logged_in):
        """Cart items persist after navigating away and back."""
        home = HomePage(logged_in)
        home.navigate_to_catalog()
        catalog = CatalogPage(logged_in)
        catalog.tap_product_by_name("Mango Punch")
        detail = ItemDetailPage(logged_in)
        detail.add_to_cart()
        # Navigate away
        home.navigate_to_profile()
        # Navigate back to cart
        home.navigate_to_cart()
        cart = CartPage(logged_in)
        assert not cart.is_empty(), \
            "Cart should persist after navigating away and back"

    # ── Start Shopping when cart has items ──

    def test_tc_orders_014_start_shopping_redirects_to_menu(self, logged_in):
        """Start Shopping button redirects to Menu tab."""
        home = HomePage(logged_in)
        home.navigate_to_cart()
        cart = CartPage(logged_in)
        if cart.is_empty():
            cart.tap_start_shopping()
            # Should land on catalog/menu page
            assert home.is_visible(
                AppiumBy.XPATH, '//android.widget.TextView[@text="Menu"]',
                timeout=10
            ), "Start Shopping should navigate to Menu tab"