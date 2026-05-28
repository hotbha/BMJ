"""
Login Page Object — maps to login_page.dart
"""
from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage
from config.test_config import TestConfig


class LoginPage(BasePage):
    """Page object for the unified auth screen with Sign In / Sign Up tabs."""

    # ── Tab Locators ──
    TAB_SIGN_IN = (AppiumBy.ACCESSIBILITY_ID, 'signin_tab')
    TAB_SIGN_UP = (AppiumBy.ACCESSIBILITY_ID, 'signup_tab')

    # ── Sign In Form ──
    EMAIL_FIELD = (AppiumBy.ACCESSIBILITY_ID, 'signin_email_field')
    PASSWORD_FIELD = (AppiumBy.ACCESSIBILITY_ID, 'signin_password_field')
    SIGNIN_BUTTON = (AppiumBy.ACCESSIBILITY_ID, 'signin_button')
    FORGOT_PASSWORD_LINK = (AppiumBy.ACCESSIBILITY_ID, 'forgot_password_link')
    ERROR_MESSAGE = (AppiumBy.ACCESSIBILITY_ID, 'login_error_message')

    # ── Social / Alternative Login ──
    GOOGLE_SIGNIN_BUTTON = (AppiumBy.ACCESSIBILITY_ID, 'google_signin_button')
    PHONE_OTP_BUTTON = (AppiumBy.ACCESSIBILITY_ID, 'phone_otp_button')

    # ── Sign Up Tab ──
    SIGNUP_EMAIL_CARD = (AppiumBy.ACCESSIBILITY_ID, 'signup_email_card')
    SIGNUP_PHONE_CARD = (AppiumBy.ACCESSIBILITY_ID, 'signup_phone_card')
    SIGNUP_GOOGLE_CARD = (AppiumBy.ACCESSIBILITY_ID, 'signup_google_card')

    def navigate_to_login(self):
        """Navigate to login screen. App should first launch to splash."""
        from pages.splash_page import SplashPage
        splash = SplashPage(self.driver)
        splash.wait_for_splash()
        splash.navigate_to_login()
        return self

    def login(self, email: str, password: str):
        """Perform login with email and password."""
        self.tap(*self.TAB_SIGN_IN)
        self.type_text(*self.EMAIL_FIELD, email)
        self.type_text(*self.PASSWORD_FIELD, password)
        self.tap(*self.SIGNIN_BUTTON)
        self.wait_for_loading_gone(TestConfig.API_WAIT)
        return self

    def tap_signup_tab(self):
        """Switch to Sign Up tab."""
        self.tap(*self.TAB_SIGN_UP)
        return self

    def tap_signin_tab(self):
        """Switch to Sign In tab."""
        self.tap(*self.TAB_SIGN_IN)
        return self

    def tap_forgot_password(self):
        """Navigate to forgot password screen."""
        self.tap(*self.FORGOT_PASSWORD_LINK)
        return self

    def tap_google_signin(self):
        """Start Google sign-in flow."""
        self.tap(*self.GOOGLE_SIGNIN_BUTTON)
        return self

    def tap_phone_otp(self):
        """Navigate to phone OTP login."""
        self.tap(*self.PHONE_OTP_BUTTON)
        return self

    def tap_signup_email(self):
        """Navigate to email signup flow."""
        self.tap(*self.SIGNUP_EMAIL_CARD)
        return self

    def tap_signup_phone(self):
        """Navigate to phone signup flow."""
        self.tap(*self.SIGNUP_PHONE_CARD)
        return self

    def tap_signup_google(self):
        """Navigate to Google signup flow."""
        self.tap(*self.SIGNUP_GOOGLE_CARD)
        return self

    def get_error_message(self) -> str:
        """Get error message text if visible."""
        return self.get_text(*self.ERROR_MESSAGE)

    def is_error_displayed(self) -> bool:
        """Check if error message is displayed."""
        return self.is_visible(*self.ERROR_MESSAGE)