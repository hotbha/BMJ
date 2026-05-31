"""
Login Page Object — maps to login_page.dart
Uses content-desc-based ANDROID_UIAUTOMATOR selectors since Flutter renders
text in content-desc attribute, not text attribute.

Navigation flow: Dashboard → Profile tab → tap "Sign In" → /login route
"""
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from pages.base_page import BasePage
from config.test_config import TestConfig


class LoginPage(BasePage):
    """Page object for the unified auth screen with Sign In / Sign Up tabs."""

    # ── Accessibility IDs (from Semantics labels in login_page.dart) ──
    ACC_WELCOME_BACK = (AppiumBy.ACCESSIBILITY_ID, "Welcome Back!")
    ACC_EMAIL_FIELD = (AppiumBy.ACCESSIBILITY_ID, "Email address")
    ACC_PASSWORD_FIELD = (AppiumBy.ACCESSIBILITY_ID, "Password")
    ACC_FORGOT_PASSWORD = (AppiumBy.ACCESSIBILITY_ID, "Forgot Password")
    ACC_SIGNIN_BUTTON = (AppiumBy.ACCESSIBILITY_ID, "Sign In")
    ACC_GOOGLE_BUTTON = (AppiumBy.ACCESSIBILITY_ID, "Google")
    ACC_PHONE_OTP_BUTTON = (AppiumBy.ACCESSIBILITY_ID, "Phone OTP")
    ACC_SIGNUP_EMAIL = (AppiumBy.ACCESSIBILITY_ID, "Sign up with Email")
    ACC_SIGNUP_PHONE = (AppiumBy.ACCESSIBILITY_ID, "Sign up with Phone")
    ACC_SIGNUP_GOOGLE = (AppiumBy.ACCESSIBILITY_ID, "Sign up with Google")

    # ── Header (fallback UiAutomator selectors) ──
    FRESH_JUICES_HEADER = BasePage.desc("Fresh Juices, Delivered Daily")
    WELCOME_BACK = BasePage.desc("Welcome Back!")
    SIGN_IN_SUBTITLE = BasePage.desc("Sign in to your account")

    # ── Tab Locators (uses real newline character as in content-desc) ──
    TAB_SIGN_IN = BasePage.desc_contains("Sign In\nTab 1")
    TAB_SIGN_UP = BasePage.desc_contains("Sign Up\nTab 2")

    # ── Sign In Form (ACCESSIBILITY_ID preferred for Semantics-labeled elements) ──
    # Email is EditText instance 0 (hint="Email address")
    # Password is EditText instance 1 (hint="Password")
    EMAIL_FIELD = ACC_EMAIL_FIELD
    PASSWORD_FIELD = ACC_PASSWORD_FIELD
    SIGNIN_BUTTON = ACC_SIGNIN_BUTTON
    FORGOT_PASSWORD_LINK = ACC_FORGOT_PASSWORD

    # ── Social / Alternative Login ──
    GOOGLE_SIGNIN_BUTTON = ACC_GOOGLE_BUTTON
    PHONE_OTP_BUTTON = ACC_PHONE_OTP_BUTTON
    OR_LABEL = BasePage.desc("OR")

    # ── Error / Toast ──
    ERROR_MESSAGE = BasePage.desc_contains("Login Failed")

    # ── Sign Up Tab — method cards (ACCESSIBILITY_ID preferred) ──
    SIGNUP_EMAIL_CARD = ACC_SIGNUP_EMAIL
    SIGNUP_PHONE_CARD = ACC_SIGNUP_PHONE
    SIGNUP_GOOGLE_CARD = ACC_SIGNUP_GOOGLE

    # ── Sign Up Tab Labels ──
    CREATE_ACCOUNT_LABEL = BasePage.desc("Create Your Account")
    SIGNUP_SUBTITLE = BasePage.desc("Choose your preferred signup method")

    # ── Forgot Password screen markers ──
    FORGOT_PASSWORD_SCREEN = BasePage.desc_contains("Reset")
    RESET_PASSWORD_BUTTON = BasePage.desc_contains("Reset")
    RESET_EMAIL_FIELD = BasePage.edit_text_instance(0)

    def navigate_to_login(self):
        """Navigate to login screen from Dashboard via Profile tab.
        Flow: Dashboard → tap Profile tab → tap Sign In → login page"""
        from pages.home_page import HomePage
        home = HomePage(self.driver)
        home.navigate_to_profile()
        from pages.profile_page import ProfilePage
        profile = ProfilePage(self.driver)
        profile.tap_sign_in()
        self.wait_for_element(*self.TAB_SIGN_IN, timeout=TestConfig.API_WAIT)
        return self

    def login(self, email: str, password: str):
        """Perform login with email and password."""
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
        """Navigate to forgot password screen. Scrolls to element first, then taps."""
        # Forgot Password link is at bottom of scrollable form; scroll to it first
        try:
            self.scroll_to_desc("Forgot Password")
        except (TimeoutException, NoSuchElementException):
            pass  # May already be visible
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

    def is_displayed(self, timeout: int = None) -> bool:
        """Check if login page is displayed (any recognisable element)."""
        return (
            self.is_visible(*self.TAB_SIGN_IN, timeout=timeout or 5) or
            self.is_visible(*self.WELCOME_BACK, timeout=timeout or 5) or
            self.is_visible(*self.EMAIL_FIELD, timeout=2) or
            self.is_visible(*self.FRESH_JUICES_HEADER, timeout=2)
        )

    def is_forgot_password_displayed(self) -> bool:
        """Check if forgot password screen is displayed."""
        return self.is_visible(*self.FORGOT_PASSWORD_SCREEN)

    def has_navigated_away(self, timeout: int = None) -> bool:
        """Check if we navigated away from login screen (to dashboard/home)."""
        from pages.home_page import HomePage
        home = HomePage(self.driver)
        try:
            result = home.is_dashboard_displayed()
            return result
        except (TimeoutException, NoSuchElementException):
            return False

    def wait_for_element(self, by, value, timeout=None):
        """Wait for an element to be visible."""
        return self.find_visible_element(by, value, timeout)