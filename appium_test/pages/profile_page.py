"""
Profile Page Object — maps to my_account_page.dart, profile/address_screen.dart
"""
from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage


class ProfilePage(BasePage):
    """Page object for profile/my account screen."""

    PROFILE_NAME = (AppiumBy.ACCESSIBILITY_ID, 'profile_name')
    PROFILE_EMAIL = (AppiumBy.ACCESSIBILITY_ID, 'profile_email')
    PROFILE_PHONE = (AppiumBy.ACCESSIBILITY_ID, 'profile_phone')
    LOGOUT_BUTTON = (AppiumBy.ACCESSIBILITY_ID, 'logout_button')
    DELETE_ACCOUNT_BUTTON = (AppiumBy.ACCESSIBILITY_ID, 'delete_account_button')
    EDIT_PROFILE_BUTTON = (AppiumBy.ACCESSIBILITY_ID, 'edit_profile_button')
    SETTINGS_BUTTON = (AppiumBy.ACCESSIBILITY_ID, 'settings_button')
    ORDER_HISTORY_BUTTON = (AppiumBy.ACCESSIBILITY_ID, 'order_history_button')
    ADDRESS_BUTTON = (AppiumBy.ACCESSIBILITY_ID, 'address_button')

    def get_name(self) -> str:
        return self.get_text(*self.PROFILE_NAME)

    def get_email(self) -> str:
        return self.get_text(*self.PROFILE_EMAIL)

    def logout(self):
        """Perform logout."""
        self.tap(*self.LOGOUT_BUTTON)
        self.wait_for_loading_gone()
        return self

    def navigate_to_order_history(self):
        self.tap(*self.ORDER_HISTORY_BUTTON)
        return self

    def navigate_to_addresses(self):
        self.tap(*self.ADDRESS_BUTTON)
        return self