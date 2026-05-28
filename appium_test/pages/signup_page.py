"""
Signup Page Object — maps to sign_up_screen.dart
"""
from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage


class SignupPage(BasePage):
    """Page object for the email signup form."""

    FIRST_NAME_FIELD = (AppiumBy.ACCESSIBILITY_ID, 'signup_first_name_field')
    LAST_NAME_FIELD = (AppiumBy.ACCESSIBILITY_ID, 'signup_last_name_field')
    EMAIL_FIELD = (AppiumBy.ACCESSIBILITY_ID, 'signup_email_field')
    PHONE_FIELD = (AppiumBy.ACCESSIBILITY_ID, 'signup_phone_field')
    PASSWORD_FIELD = (AppiumBy.ACCESSIBILITY_ID, 'signup_password_field')
    CONFIRM_PASSWORD_FIELD = (AppiumBy.ACCESSIBILITY_ID, 'signup_confirm_password_field')
    SIGNUP_BUTTON = (AppiumBy.ACCESSIBILITY_ID, 'signup_button')
    ERROR_MESSAGE = (AppiumBy.ACCESSIBILITY_ID, 'signup_error_message')
    PASSWORD_REQUIREMENTS = (AppiumBy.ACCESSIBILITY_ID, 'signup_password_requirements')

    def signup(self, first_name: str, last_name: str, email: str,
               phone: str, password: str, confirm_password: str = None):
        """Fill the signup form and submit."""
        self.type_text(*self.FIRST_NAME_FIELD, first_name)
        self.type_text(*self.LAST_NAME_FIELD, last_name)
        self.type_text(*self.EMAIL_FIELD, email)
        self.type_text(*self.PHONE_FIELD, phone)
        self.type_text(*self.PASSWORD_FIELD, password)
        self.type_text(*self.CONFIRM_PASSWORD_FIELD, confirm_password or password)
        self.tap(*self.SIGNUP_BUTTON)
        self.wait_for_loading_gone()
        return self

    def is_error_displayed(self) -> bool:
        return self.is_visible(*self.ERROR_MESSAGE)

    def get_error_message(self) -> str:
        return self.get_text(*self.ERROR_MESSAGE)