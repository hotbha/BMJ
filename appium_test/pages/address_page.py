"""
Address Page Object — maps to address_screen.dart, address_entry_screen.dart
Uses text-based selectors matching actual UI strings.
"""
from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage
from config.test_config import TestConfig


class AddressPage(BasePage):
    """Page object for address entry/manage screen."""

    # Address Entry Screen (address_entry_screen.dart)
    # AppBar title
    ADD_ADDRESS_TITLE = (AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().descriptionContains("Add Address")')

    # Form fields by hint text
    FLAT_HINT = (AppiumBy.XPATH, '//android.widget.EditText[@hint="Flat / House No."]')
    BUILDING_HINT = (AppiumBy.XPATH, '//android.widget.EditText[@hint="Building / Apartment"]')
    STREET_HINT = (AppiumBy.XPATH, '//android.widget.EditText[@hint="Street / Road"]')
    AREA_HINT = (AppiumBy.XPATH, '//android.widget.EditText[@hint="Area / Locality"]')
    CITY_HINT = (AppiumBy.XPATH, '//android.widget.EditText[@hint="City"]')
    PINCODE_HINT = (AppiumBy.XPATH, '//android.widget.EditText[@hint="Pincode"]')
    INSTRUCTIONS_HINT = (AppiumBy.XPATH, '//android.widget.EditText[@hint="Delivery instructions (optional)"]')

    # Button
    SAVE_ADDRESS_BUTTON = (AppiumBy.XPATH, '//android.widget.TextView[@content-desc="Save Address"]')

    # Address Selection Screen (address_selection_screen.dart)
    SELECT_ADDRESS_TITLE = (AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().descriptionContains("Select Address")')
    DELIVER_HERE_BUTTON = (AppiumBy.XPATH, '//android.widget.TextView[@content-desc="Deliver Here"]')
    ADD_NEW_ADDRESS_BUTTON = (AppiumBy.XPATH, '//android.widget.TextView[@content-desc="Add New Address"]')

    # Address Screen (address_screen.dart) — manage saved addresses
    MANAGE_ADDRESSES_TITLE = (AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().descriptionContains("Address")')

    # Error / validation
    PINCODE_ERROR = (AppiumBy.XPATH, '//android.widget.TextView[contains(@content-desc, "pincode") or contains(@content-desc, "Pincode")]')

    def fill_address(self, flat: str, building: str, street: str,
                     area: str, city: str, pincode: str,
                     instructions: str = ''):
        """Fill address form fields."""
        self.type_text(*self.FLAT_HINT, flat)
        self.type_text(*self.BUILDING_HINT, building)
        self.type_text(*self.STREET_HINT, street)
        self.type_text(*self.AREA_HINT, area)
        self.type_text(*self.CITY_HINT, city)
        self.type_text(*self.PINCODE_HINT, pincode)
        if instructions:
            self.type_text(*self.INSTRUCTIONS_HINT, instructions)
        return self

    def save_address(self):
        """Tap save button."""
        self.scroll_to_text("Save Address")
        self.tap(*self.SAVE_ADDRESS_BUTTON)
        self.wait_for_loading_gone(TestConfig.API_WAIT)
        return self

    def tap_deliver_here(self):
        """Select an address for delivery."""
        self.tap(*self.DELIVER_HERE_BUTTON)
        return self

    def tap_add_new_address(self):
        """Open new address form."""
        self.tap(*self.ADD_NEW_ADDRESS_BUTTON)
        return self

    def is_pincode_error_shown(self) -> bool:
        return self.is_visible(*self.PINCODE_ERROR)