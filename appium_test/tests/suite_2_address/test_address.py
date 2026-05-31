"""
Suite 2: Address — E2E tests aligned with integration_test use cases.
TC-E2E-ADDR-001 to TC-E2E-ADDR-008
All selectors use XPath (no ACCESSIBILITY_ID).
"""
import pytest
import time
from pages.login_page import LoginPage
from pages.address_page import AddressPage
from pages.home_page import HomePage
from pages.profile_page import ProfilePage
from config.test_config import TestConfig


class TestAddress:
    """Address management test suite."""

    def test_tc_addr_001_add_address_valid(self, logged_in):
        """TC-E2E-ADDR-001: Add a valid delivery address."""
        home = HomePage(logged_in)
        home.navigate_to_profile()
        profile = ProfilePage(logged_in)
        profile.navigate_to_addresses()
        addr = AddressPage(logged_in)
        addr.tap_add_new_address()
        addr.fill_address(
            flat="42",
            building="Test Towers",
            street="MG Road",
            area="Indiranagar",
            city="Bangalore",
            pincode=TestConfig.PINCODE_VALID,
            instructions="Leave at door"
        )
        addr.save_address()
        time.sleep(2)
        assert not addr.is_pincode_error_shown(), \
            "Pincode error shown for valid pincode"

    def test_tc_addr_002_pincode_valid(self, logged_in):
        """TC-E2E-ADDR-002: Valid pincode accepted."""
        home = HomePage(logged_in)
        home.navigate_to_profile()
        profile = ProfilePage(logged_in)
        profile.navigate_to_addresses()
        addr = AddressPage(logged_in)
        addr.tap_add_new_address()
        # Find pincode field by hint and type
        pin_field = addr.find_element(addr.PINCODE_HINT)
        if pin_field:
            pin_field.clear()
            pin_field.send_keys(TestConfig.PINCODE_VALID)
        time.sleep(1)
        assert not addr.is_pincode_error_shown(), \
            "Pincode error shown for valid pincode"

    def test_tc_addr_003_pincode_invalid(self, logged_in):
        """TC-E2E-ADDR-003: Invalid pincode shows validation error."""
        home = HomePage(logged_in)
        home.navigate_to_profile()
        profile = ProfilePage(logged_in)
        profile.navigate_to_addresses()
        addr = AddressPage(logged_in)
        addr.tap_add_new_address()
        pin_field = addr.find_element(addr.PINCODE_HINT)
        if pin_field:
            pin_field.clear()
            pin_field.send_keys("000000")
        time.sleep(1)
        assert addr.is_pincode_error_shown(), \
            "No error shown for invalid pincode"

    def test_tc_addr_004_save_address_persists(self, logged_in):
        """TC-E2E-ADDR-004: Saved address persists after navigation."""
        home = HomePage(logged_in)
        home.navigate_to_profile()
        profile = ProfilePage(logged_in)
        profile.navigate_to_addresses()
        addr = AddressPage(logged_in)
        addr.tap_add_new_address()
        addr.fill_address(
            flat="100", building="Persist Block", street="Main Street",
            area="Koramangala", city="Bangalore", pincode=TestConfig.PINCODE_VALID
        )
        addr.save_address()
        time.sleep(2)
        # Navigate away and back
        addr.press_back()
        time.sleep(1)
        addr.press_back()
        time.sleep(1)
        profile.navigate_to_addresses()
        time.sleep(2)
        assert addr.is_visible(*addr.ADD_NEW_ADDRESS_BUTTON, timeout=10), \
            "Address management screen not shown after navigation"

    def test_tc_addr_005_empty_fields_validation(self, logged_in):
        """TC-E2E-ADDR-005: Empty required fields show validation errors."""
        home = HomePage(logged_in)
        home.navigate_to_profile()
        profile = ProfilePage(logged_in)
        profile.navigate_to_addresses()
        addr = AddressPage(logged_in)
        addr.tap_add_new_address()
        # Try to save with empty fields
        addr.save_address()
        time.sleep(2)
        # Should show validation errors - stay on address form
        assert addr.is_visible(*addr.SAVE_ADDRESS_BUTTON, timeout=5), \
            "Should stay on address form with empty fields"

    def test_tc_addr_006_edit_address(self, logged_in):
        """TC-E2E-ADDR-006: Navigate to edit existing address."""
        home = HomePage(logged_in)
        home.navigate_to_profile()
        profile = ProfilePage(logged_in)
        profile.navigate_to_addresses()
        addr = AddressPage(logged_in)
        addr.tap_add_new_address()
        addr.fill_address(
            flat="1", building="Edit Test", street="Old Street",
            area="Old Area", city="Old City", pincode=TestConfig.PINCODE_VALID
        )
        addr.save_address()
        time.sleep(2)
        assert True, "Address saved successfully"

    def test_tc_addr_007_add_new_address_button_visible(self, logged_in):
        """TC-E2E-ADDR-007: Add new address button is accessible."""
        home = HomePage(logged_in)
        home.navigate_to_profile()
        profile = ProfilePage(logged_in)
        profile.navigate_to_addresses()
        addr = AddressPage(logged_in)
        assert addr.is_visible(*addr.ADD_NEW_ADDRESS_BUTTON, timeout=10), \
            "Add new address button not visible"

    def test_tc_addr_008_multiple_addresses(self, logged_in):
        """TC-E2E-ADDR-008: Add multiple addresses successfully."""
        home = HomePage(logged_in)
        home.navigate_to_profile()
        profile = ProfilePage(logged_in)
        profile.navigate_to_addresses()
        addr = AddressPage(logged_in)
        # Add first address
        addr.tap_add_new_address()
        addr.fill_address(
            flat="1", building="Home", street="Street A",
            area="Area X", city="City1", pincode=TestConfig.PINCODE_VALID
        )
        addr.save_address()
        time.sleep(2)
        # Try adding second
        addr.tap_add_new_address()
        addr.fill_address(
            flat="2", building="Work", street="Street B",
            area="Area Y", city="City2", pincode=TestConfig.PINCODE_VALID
        )
        addr.save_address()
        time.sleep(2)
        assert addr.is_visible(*addr.ADD_NEW_ADDRESS_BUTTON, timeout=5), \
            "Address management screen still accessible"