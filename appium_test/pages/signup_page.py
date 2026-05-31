"""
Signup Page Object — maps to email_signup_screen.dart, email_verification_screen.dart,
phone_entry_after_email_screen.dart, create_password_screen.dart
The signup flow is multi-step: Email → OTP → Phone/Address → Create Password
"""
from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage
from config.test_config import TestConfig
import time


class SignupPage(BasePage):
    """Page object for the multi-step email signup flow."""

    # ── Step 1: Email Signup Screen ──
    EMAIL_FIELD = (AppiumBy.XPATH, '//android.widget.EditText[@hint="your.email@example.com"]')
    CONTINUE_BUTTON = (AppiumBy.XPATH, '//android.widget.TextView[@content-desc="Continue"]')

    # ── Step 2: Email Verification Screen ──
    VERIFY_EMAIL_BUTTON = (AppiumBy.XPATH, '//android.widget.TextView[@content-desc="Verify Email"]')
    PIN_INPUT = (AppiumBy.XPATH, '//android.widget.EditText')

    # ── Step 3: Phone Entry After Email Screen ──
    PHONE_FIELD = (AppiumBy.XPATH, '//android.widget.EditText[@hint="Enter phone number" or contains(@hint, "phone")]')
    NEXT_BUTTON = (AppiumBy.XPATH, '//android.widget.TextView[@content-desc="Next" or @content-desc="Continue"]')

    # ── Step 4: Create Password Screen ──
    PASSWORD_FIELD = (AppiumBy.XPATH, '//android.widget.EditText[@hint="Enter your password"]')
    CONFIRM_PASSWORD_FIELD = (AppiumBy.XPATH, '//android.widget.EditText[@hint="Re-enter your password"]')
    CREATE_ACCOUNT_BUTTON = (AppiumBy.XPATH, '//android.widget.TextView[@content-desc="Create Account"]')

    # ── Error / validation ──
    ERROR_MESSAGE = (AppiumBy.XPATH, '//android.widget.TextView[contains(@content-desc, "error") or contains(@content-desc, "invalid") or contains(@content-desc, "Error")]')
    TOAST_ERROR = (AppiumBy.XPATH, '//android.widget.TextView[contains(@content-desc, "Failed")]')

    def enter_email(self, email: str):
        """Step 1: Enter email on email signup screen."""
        self.wait_for_element(*self.EMAIL_FIELD, timeout=TestConfig.EXPLICIT_WAIT)
        self.type_text(*self.EMAIL_FIELD, email)
        self.tap(*self.CONTINUE_BUTTON)
        return self

    def enter_otp(self, otp: str = "111111"):
        """Step 2: Enter OTP verification code."""
        self.wait_for_element(*self.PIN_INPUT, timeout=TestConfig.EXPLICIT_WAIT)
        pin_input = self.find_element(*self.PIN_INPUT)
        pin_input.clear()
        pin_input.send_keys(otp)
        time.sleep(1)
        self.tap(*self.VERIFY_EMAIL_BUTTON)
        return self

    def enter_phone(self, phone: str = "9876543210"):
        """Step 3: Enter phone number (if phone entry screen is shown)."""
        try:
            self.wait_for_element(*self.PHONE_FIELD, timeout=5)
            self.type_text(*self.PHONE_FIELD, phone)
            self.tap(*self.NEXT_BUTTON)
        except Exception:
            # Phone screen may not appear if already collected
            pass
        return self

    def create_password(self, password: str, confirm_password: str = None):
        """Step 4: Enter password and submit."""
        self.wait_for_element(*self.PASSWORD_FIELD, timeout=TestConfig.EXPLICIT_WAIT)
        self.type_text(*self.PASSWORD_FIELD, password)
        self.type_text(*self.CONFIRM_PASSWORD_FIELD, confirm_password or password)
        # Wait for password validator to complete
        time.sleep(2)
        self.tap(*self.CREATE_ACCOUNT_BUTTON)
        self.wait_for_loading_gone(TestConfig.API_WAIT)
        return self

    def signup(self, first_name: str, last_name: str, email: str,
               phone: str, password: str, confirm_password: str = None):
        """Complete multi-step email signup flow."""
        self.enter_email(email)
        self.enter_otp()
        self.enter_phone(phone)
        self.create_password(password, confirm_password)
        return self

    def is_error_displayed(self) -> bool:
        return self.is_visible(*self.ERROR_MESSAGE) or self.is_visible(*self.TOAST_ERROR)

    def get_error_message(self) -> str:
        try:
            return self.get_text(*self.ERROR_MESSAGE)
        except Exception:
            try:
                return self.get_text(*self.TOAST_ERROR)
            except Exception:
                return "Error message not found"