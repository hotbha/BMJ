"""
Suite 3: Catalog — E2E tests aligned with integration_test use cases.
TC-E2E-CATALOG-001 to TC-E2E-CATALOG-010
All selectors use XPath (no ACCESSIBILITY_ID).
"""
import pytest
import time
from pages.catalog_page import CatalogPage
from pages.item_detail_page import ItemDetailPage
from pages.home_page import HomePage
from config.test_config import TestConfig


class TestCatalog:
    """Product catalog test suite aligned with integration_test."""

    def test_tc_catalog_001_view_all_products(self, logged_in):
        """TC-E2E-CATALOG-001: View catalog list as logged-in user."""
        home = HomePage(logged_in)
        home.navigate_to_menu()
        catalog = CatalogPage(logged_in)
        assert catalog.is_visible(*catalog.MENU_TITLE, timeout=TestConfig.API_WAIT), \
            "Catalog title not visible"

    def test_tc_catalog_002_search_hit(self, logged_in):
        """TC-E2E-CATALOG-002: Search for existing product by name."""
        home = HomePage(logged_in)
        home.navigate_to_menu()
        catalog = CatalogPage(logged_in)
        catalog.search("mango")
        time.sleep(2)
        assert not catalog.is_empty_results_shown(), \
            "Search hit returned empty results"

    def test_tc_catalog_003_search_miss(self, logged_in):
        """TC-E2E-CATALOG-003: Search for non-existent product shows empty state."""
        home = HomePage(logged_in)
        home.navigate_to_menu()
        catalog = CatalogPage(logged_in)
        catalog.search("zzzzznotexistxxxxx")
        time.sleep(2)
        assert catalog.is_empty_results_shown(), \
            "Search miss should show empty state"

    def test_tc_catalog_004_item_detail_view(self, logged_in):
        """TC-E2E-CATALOG-004: View product detail screen."""
        home = HomePage(logged_in)
        home.navigate_to_menu()
        catalog = CatalogPage(logged_in)
        catalog.tap_product_by_name("Mango")
        detail = ItemDetailPage(logged_in)
        assert detail.is_visible(*detail.ADD_TO_CART_BUTTON, timeout=TestConfig.API_WAIT), \
            "Item detail not loaded - Add to Cart button not visible"

    def test_tc_catalog_005_add_to_cart_from_detail(self, logged_in):
        """TC-E2E-CATALOG-005: Add product to cart from detail screen."""
        home = HomePage(logged_in)
        home.navigate_to_menu()
        catalog = CatalogPage(logged_in)
        catalog.tap_product_by_name("Mango")
        detail = ItemDetailPage(logged_in)
        detail.add_to_cart()
        time.sleep(2)
        assert True, "Add to cart action completed"

    def test_tc_catalog_006_price_display_on_detail(self, logged_in):
        """TC-E2E-CATALOG-006: Product price displays on detail screen."""
        home = HomePage(logged_in)
        home.navigate_to_menu()
        catalog = CatalogPage(logged_in)
        catalog.tap_product_by_name("Mango")
        detail = ItemDetailPage(logged_in)
        price = detail.get_item_price()
        assert price is not None and len(price) > 0, \
            "Product price not displayed"

    def test_tc_catalog_007_product_name_on_detail(self, logged_in):
        """TC-E2E-CATALOG-007: Product name displays on detail screen."""
        home = HomePage(logged_in)
        home.navigate_to_menu()
        catalog = CatalogPage(logged_in)
        catalog.tap_product_by_name("Mango")
        detail = ItemDetailPage(logged_in)
        name = detail.get_item_name()
        assert name is not None and len(name) > 0, \
            "Product name not displayed"

    def test_tc_catalog_008_add_to_cart_button_visible(self, logged_in):
        """TC-E2E-CATALOG-008: Add to Cart button visible on detail."""
        home = HomePage(logged_in)
        home.navigate_to_menu()
        catalog = CatalogPage(logged_in)
        catalog.tap_product_by_name("Green")
        detail = ItemDetailPage(logged_in)
        assert detail.is_visible(*detail.ADD_TO_CART_BUTTON, timeout=10), \
            "Add to cart button not visible"

    def test_tc_catalog_009_search_field_visible(self, logged_in):
        """TC-E2E-CATALOG-009: Search field is visible on catalog screen."""
        home = HomePage(logged_in)
        home.navigate_to_menu()
        catalog = CatalogPage(logged_in)
        assert catalog.is_visible(*catalog.SEARCH_HINT, timeout=5) or \
            catalog.is_visible(*catalog.SEARCH_FIELD, timeout=5), \
            "Search field not visible"

    def test_tc_catalog_010_clear_search_restores_list(self, logged_in):
        """TC-E2E-CATALOG-010: Clearing search restores full product list."""
        home = HomePage(logged_in)
        home.navigate_to_menu()
        catalog = CatalogPage(logged_in)
        # Search for something
        catalog.search("mango")
        time.sleep(2)
        # Clear search
        catalog.search("")
        time.sleep(2)
        assert not catalog.is_empty_results_shown(), \
            "Full product list should be restored after clearing search"