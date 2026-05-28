"""
Address Page Object — maps to address_screen.dart, address_entry_screen.dart
"""
from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage


class AddressPage(BasePage):
    """Page object for address entry/manage screen."""

    FLAT_FIELD = (AppiumBy.ACCESSIBILITY_ID, 'address_flat_field')
    BUILDING_FIELD = (AppiumBy.ACCESSIBILITY_ID, 'address_building_field')
    STREET_FIELD = (AppiumBy.ACCESSIBILITY_ID, 'address_street_field')
    AREA_FIELD = (AppiumBy.ACCESSIBILITY_ID, 'address_area_field')
    CITY_FIELD = (AppiumBy.ACCESSIBILITY_ID, 'address_city_field')
    PINCODE_FIELD = (AppiumBy.ACCESSIBILITY_ID, 'address_pincode_field')
    DELIVERY_INSTRUCTIONS_FIELD = (AppiumBy.ACCESSIBILITY_ID, 'address_delivery_instructions_field')
    SAVE_ADDRESS_BUTTON = (AppiumBy.ACCESSIBILITY_ID, 'save_address_button')
    PINCODE_ERROR = (AppiumBy.ACCESSIBILITY_ID, 'address_pincode_error')
    ADDRESS_LIST = (AppiumBy.ACCESSIBILITY_ID, 'address_list')
    ADD_NEW_ADDRESS_BUTTON = (AppiumBy.ACCESSIBILITY_ID, 'add_new_address_button')

    def fill_address(self, flat: str, building: str, street: str,
                     area: str, city: str, pincode: str,
                     instructions: str = ''):
        """Fill address form fields."""
        self.type_text(*self.FLAT_FIELD, flat)
        self.type_text(*self.BUILDING_FIELD, building)
        self.type_text(*self.STREET_FIELD, street)
        self.type_text(*self.AREA_FIELD, area)
        self.type_text(*self.CITY_FIELD, city)
        self.type_text(*self.PINCODE_FIELD, pincode)
        if instructions:
            self.type_text(*self.DELIVERY_INSTRUCTIONS_FIELD, instructions)
        return self

    def save_address(self):
        """Tap save button."""
        self.tap(*self.SAVE_ADDRESS_BUTTON)
        self.wait_for_loading_gone()
        return self

    def is_pincode_error_shown(self) -> bool:
        return self.is_visible(*self.PINCODE_ERROR)

    def get_pincode_error(self) -> str:
        return self.get_text(*self.PINCODE_ERROR)

    def tap_add_new_address(self):
        self.tap(*self.ADD_NEW_ADDRESS_BUTTON)
        return self