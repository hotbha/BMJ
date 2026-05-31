"""
Suite 1: Authentication — E2E tests aligned with integration_test use cases.
Covers: TC-E2E-AUTH-001 to TC-E2E-AUTH-013

Navigation flow: App launches → Splash → Dashboard (always, even for guests)
→ Profile tab → tap Sign In → Login page

The app ALWAYS shows Dashboard to all users first. Login is NOT the initial screen.
"""
import time
import uuid
import pytest
import requests
from pages.login_page import LoginPage
from pages.signup_page import SignupPage
from pages.home_page import HomePage
from pages.profile_page import ProfilePage
from pages.splash_page import SplashPage
from config.test_config import TestConfig


def delete_firebase_user(email: str, password: str):
    """Delete a Firebase user via Admin REST API."""
    api_key = TestConfig.FIREBASE_API_KEY
    if not api_key:
        return
    try:
        signin_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
        r = requests.post(signin_url, json={
            "email": email,
            "password": password,
            "returnSecureToken": True
        }, timeout=15)
        if r.status_code != 200:
            return
        id_token = r.json().get('idToken')
        if not id_token:
            return
        delete_url = f"https://identitytoolkit.googleapis.com/v1/accounts:delete?key={api_key}"
        requests.post(delete_url, json={"idToken": id_token}, timeout=15)
    except Exception:
        pass


def ensure_on_dashboard(driver):
    """Navigate back to the Dashboard from any screen by pressing back until dashboard is found."""
    home = HomePage(driver)
    if home.is_dashboard_displayed(timeout=3):
        return home
    # Press back up to 5 times until we reach dashboard
    for _ in range(5):
        driver.press_back()
        time.sleep(1)
        if home.is_dashboard_displayed(timeout=3):
            return home
    # Last resort: navigate via Profile if on login
    try:
        login = LoginPage(driver)
        if login.is_displayed(timeout=2):
            driver.press_back()  # Back from login lands on profile/dashboard
            time.sleep(2)
    except Exception:
        pass
    return home


def navigate_to_login_from_dashboard(driver):
    """Navigate from current state → Dashboard → Profile tab → Sign In → Login page.
    If already on login page, returns the LoginPage directly."""
    login = LoginPage(driver)
    if login.is_displayed(timeout=2):
        return login
    ensure_on_dashboard(driver)
    home = HomePage(driver)
    home.navigate_to_profile()
    profile = ProfilePage(driver)
    profile.tap_sign_in()
    login.wait_for_element(*login.WELCOME_BACK, timeout=TestConfig.EXPLICIT_WAIT)
    return login


class TestAuth:
    """Authentication test suite with correct Dashboard-first navigation."""

    @pytest.fixture(autouse=True)
    def setup(self, driver):
        self.driver = driver
        self.home = HomePage(driver)
        self.login_page = LoginPage(driver)
        self.signup_page = SignupPage(driver)
        self.profile_page = ProfilePage(driver)

    # ========== Smoke Test ==========
    def test_tc_auth_001_app_launch_shows_dashboard(self, driver):
        """TC-E2E-AUTH-001: App launches and shows Dashboard (not login)."""
        # Wait for splash auto-navigation to complete
        assert self.home.wait_for_dashboard(timeout=15), \
            "Dashboard not shown after app launch"
        # Verify key dashboard elements are visible
        assert self.home.is_visible(*self.home.NAV_HOME, timeout=5), \
            "Home nav tab not visible"
        assert self.home.is_visible(*self.home.NAV_PROFILE, timeout=5), \
            "Profile nav tab not visible"

    # ========== Dashboard Guest Mode ==========
    def test_tc_auth_002_guest_dashboard_shows_welcome(self, driver):
        """TC-E2E-AUTH-002: Guest dashboard shows welcome text and public elements."""
        self.home.wait_for_dashboard(timeout=12)
        assert self.home.is_visible(*self.home.BOOKMYJUICE_HEADER, timeout=5), \
            "Header not visible"
        assert self.home.is_visible(*self.home.NO_ACTIVE_PLAN, timeout=5), \
            "No Active Plan section not visible"

    # ========== Navigation to Login ==========
    def test_tc_auth_003_navigate_to_login_via_profile(self, driver):
        """TC-E2E-AUTH-003: Navigate from Dashboard → Profile → Sign In → Login."""
        login = navigate_to_login_from_dashboard(driver)
        assert login.is_displayed(timeout=5), \
            "Login screen not displayed via Profile → Sign In"

    def test_tc_auth_004_login_screen_elements_visible(self, driver):
        """TC-E2E-AUTH-004: Login page shows all expected form elements."""
        login = navigate_to_login_from_dashboard(driver)
        assert login.is_visible(*login.WELCOME_BACK, timeout=5), \
            "Welcome Back not visible"
        assert login.is_visible(*login.SIGN_IN_SUBTITLE, timeout=5), \
            "Sign in subtitle not visible"
        assert login.is_visible(*login.EMAIL_FIELD, timeout=5), \
            "Email field not visible"
        assert login.is_visible(*login.PASSWORD_FIELD, timeout=5), \
            "Password field not visible"
        assert login.is_visible(*login.FORGOT_PASSWORD_LINK, timeout=5), \
            "Forgot Password link not visible"
        assert login.is_visible(*login.SIGNIN_BUTTON, timeout=5), \
            "Sign In button not visible"
        assert login.is_visible(*login.GOOGLE_SIGNIN_BUTTON, timeout=5), \
            "Google button not visible"
        assert login.is_visible(*login.PHONE_OTP_BUTTON, timeout=5), \
            "Phone OTP button not visible"

    # ========== Login Flow ==========
    def test_tc_auth_005_login_valid_credentials(self, logged_in):
        """TC-E2E-AUTH-005: Login with valid credentials returns to Dashboard."""
        home = HomePage(logged_in)
        assert home.is_dashboard_displayed(timeout=15), \
            "Dashboard not shown after login"

    def test_tc_auth_006_login_invalid_password(self, driver):
        """TC-E2E-AUTH-006: Invalid password stays on login screen."""
        login = navigate_to_login_from_dashboard(driver)
        login.type_text(*login.EMAIL_FIELD, TestConfig.TEST_EMAIL)
        login.type_text(*login.PASSWORD_FIELD, "WrongPassword@999")
        login.tap(*login.SIGNIN_BUTTON)

        # Wait for Firebase error response (should see error toast)
        time.sleep(5)
        # Should NOT navigate to dashboard — stays on login screen
        the_home = HomePage(driver)
        dashboard_shown = the_home.is_dashboard_displayed(timeout=3)
        assert not dashboard_shown, \
            "Login should fail with invalid password — should not navigate to dashboard"

    def test_tc_auth_007_login_nonexistent_user(self, driver):
        """TC-E2E-AUTH-007: Non-existent email stays on login screen."""
        login = navigate_to_login_from_dashboard(driver)
        login.type_text(*login.EMAIL_FIELD, "nonexistent@nowhere.com")
        login.type_text(*login.PASSWORD_FIELD, "Test@1234")
        login.tap(*login.SIGNIN_BUTTON)

        time.sleep(5)
        the_home = HomePage(driver)
        dashboard_shown = the_home.is_dashboard_displayed(timeout=3)
        assert not dashboard_shown, \
            "Login should fail for nonexistent user"

    def test_tc_auth_008_login_empty_fields(self, driver):
        """TC-E2E-AUTH-008: Empty fields prevented by client-side validation."""
        login = navigate_to_login_from_dashboard(driver)
        login.tap(*login.SIGNIN_BUTTON)

        # Should stay on login screen — validation blocks submission
        assert login.is_displayed(timeout=5), \
            "Should stay on login screen with empty fields"

    def test_tc_auth_009_login_wrong_email_format(self, driver):
        """TC-E2E-AUTH-009: Invalid email format blocked by client-side validation."""
        login = navigate_to_login_from_dashboard(driver)
        login.type_text(*login.EMAIL_FIELD, "not-an-email")
        login.type_text(*login.PASSWORD_FIELD, "Test@1234")
        login.tap(*login.SIGNIN_BUTTON)

        assert login.is_displayed(timeout=5), \
            "Should stay on login screen with invalid email format"

    # ========== Sign Up Tab ==========
    def test_tc_auth_010_signup_tab_shows_options(self, driver):
        """TC-E2E-AUTH-010: Sign Up tab shows Email, Phone, Google signup options."""
        login = navigate_to_login_from_dashboard(driver)
        login.tap(*login.TAB_SIGN_UP)

        assert login.is_visible(*login.SIGNUP_EMAIL_CARD, timeout=5), \
            "Email signup card not visible"
        assert login.is_visible(*login.SIGNUP_PHONE_CARD, timeout=5), \
            "Phone signup card not visible"
        assert login.is_visible(*login.SIGNUP_GOOGLE_CARD, timeout=5), \
            "Google signup option not visible"

    # ========== Forgot Password ==========
    def test_tc_auth_011_forgot_password_navigates(self, driver):
        """TC-E2E-AUTH-011: Forgot Password shows reset screen."""
        login = navigate_to_login_from_dashboard(driver)
        login.tap_forgot_password()

        assert login.is_forgot_password_displayed(timeout=5), \
            "Forgot password screen not shown"

    # ========== Session Management ==========
    def test_tc_auth_012_logout_clears_session(self, logged_in):
        """TC-E2E-AUTH-012: Logout from authenticated profile returns to guest dashboard."""
        home = HomePage(logged_in)
        home.navigate_to_profile()

        profile = ProfilePage(logged_in)
        profile.confirm_logout()

        # After logout, should show guest dashboard
        time.sleep(3)
        assert home.is_dashboard_displayed(timeout=10), \
            "Dashboard not shown after logout"
        # Profile should show guest state
        home.navigate_to_profile()
        assert profile.is_guest(), \
            "Profile should show guest state after logout"

    def test_tc_auth_013_login_after_logout(self, logged_in):
        """TC-E2E-AUTH-013: Login works after previous logout via Profile."""
        # First logout from current session
        home = HomePage(logged_in)
        home.navigate_to_profile()
        profile = ProfilePage(logged_in)
        profile.confirm_logout()
        time.sleep(2)

        # Now login again from guest state
        home.wait_for_dashboard(timeout=10)
        login = navigate_to_login_from_dashboard(logged_in)
        login.login(TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD)

        # Verify dashboard shown after re-login
        assert home.is_dashboard_displayed(timeout=15), \
            "Login after logout failed"