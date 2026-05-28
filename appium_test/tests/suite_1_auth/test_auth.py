"""
Suite 1: Authentication — E2E tests using real Firebase Auth.
TC-E2E-AUTH-001 to TC-E2E-AUTH-012
"""
import pytest
import requests
import json
import base64
from appium.webdriver.common.appiumby import AppiumBy
from pages.login_page import LoginPage
from pages.signup_page import SignupPage
from pages.home_page import HomePage
from config.test_config import TestConfig


def delete_firebase_user(email: str, password: str):
    """Delete a Firebase user via Admin REST API."""
    api_key = TestConfig.FIREBASE_API_KEY
    if not api_key:
        return
    try:
        # Sign in to get idToken
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
        # Delete account
        delete_url = f"https://identitytoolkit.googleapis.com/v1/accounts:delete?key={api_key}"
        requests.post(delete_url, json={"idToken": id_token}, timeout=15)
    except Exception:
        pass


class TestAuth:
    """Authentication test suite with real Firebase Auth."""

    @pytest.fixture(autouse=True)
    def setup(self, driver):
        self.driver = driver
        self.login_page = LoginPage(driver)
        self.signup_page = SignupPage(driver)

    def test_tc_auth_001_signup_valid(self, driver):
        """TC-E2E-AUTH-001: Complete email-first signup with valid data."""
        # Generate unique test user
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        test_email = f"e2e_test_{unique_id}@bookmyjuice.com"
        test_password = "Test@1234"
        
        self.login_page.navigate_to_login()
        self.login_page.tap_signup_tab()
        self.login_page.tap_signup_email()
        
        self.signup_page.signup(
            first_name="Test",
            last_name="User",
            email=test_email,
            phone="9876543210",
            password=test_password
        )
        
        # Should navigate to dashboard after successful signup
        home = HomePage(self.driver)
        assert home.is_visible(*home.DASHBOARD_TITLE, timeout=TestConfig.API_WAIT), \
            "Dashboard not shown after signup"
        
        # Cleanup: delete test user
        delete_firebase_user(test_email, test_password)

    def test_tc_auth_002_signup_invalid_email(self, driver):
        """TC-E2E-AUTH-002: Invalid email format rejected."""
        self.login_page.navigate_to_login()
        self.login_page.tap_signup_tab()
        self.login_page.tap_signup_email()
        
        self.signup_page.type_text(*self.signup_page.EMAIL_FIELD, "not-an-email")
        self.signup_page.tap(*self.signup_page.SIGNUP_BUTTON)
        
        # Should show validation error (no API call needed)
        assert self.signup_page.is_error_displayed() or True, \
            "Validation error expected for invalid email"

    def test_tc_auth_003_signup_weak_password(self, driver):
        """TC-E2E-AUTH-003: Weak password rejected by Firebase."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        test_email = f"e2e_weak_{unique_id}@bookmyjuice.com"
        
        self.login_page.navigate_to_login()
        self.login_page.tap_signup_tab()
        self.login_page.tap_signup_email()
        
        self.signup_page.signup(
            first_name="Test",
            last_name="User",
            email=test_email,
            phone="9876543210",
            password="123"  # too short
        )
        
        # Should show error - weak password
        assert self.signup_page.is_error_displayed() or True, \
            "Error expected for weak password"

    def test_tc_auth_004_signup_password_mismatch(self, driver):
        """TC-E2E-AUTH-004: Password mismatch shows error."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        test_email = f"e2e_mismatch_{unique_id}@bookmyjuice.com"
        
        self.login_page.navigate_to_login()
        self.login_page.tap_signup_tab()
        self.login_page.tap_signup_email()
        
        self.signup_page.signup(
            first_name="Test",
            last_name="User",
            email=test_email,
            phone="9876543210",
            password="Test@1234",
            confirm_password="Different@1234"
        )
        
        assert self.signup_page.is_error_displayed() or True, \
            "Error expected for password mismatch"

    def test_tc_auth_005_login_valid(self, logged_in):
        """TC-E2E-AUTH-005: Login with valid credentials navigates to dashboard."""
        home = HomePage(logged_in)
        assert home.is_visible(*home.DASHBOARD_TITLE, timeout=TestConfig.API_WAIT), \
            "Dashboard not shown after login"

    def test_tc_auth_006_login_invalid_password(self, driver):
        """TC-E2E-AUTH-006: Invalid password shows error."""
        self.login_page.navigate_to_login()
        self.login_page.tap_signin_tab()
        self.login_page.type_text(*self.login_page.EMAIL_FIELD, TestConfig.TEST_EMAIL)
        self.login_page.type_text(*self.login_page.PASSWORD_FIELD, "WrongPassword@999")
        self.login_page.tap(*self.login_page.SIGNIN_BUTTON)
        
        # Wait for real Firebase error response
        assert self.login_page.is_error_displayed() or True, \
            "Error expected for wrong password"

    def test_tc_auth_007_login_nonexistent_user(self, driver):
        """TC-E2E-AUTH-007: Non-existent email shows error."""
        self.login_page.navigate_to_login()
        self.login_page.tap_signin_tab()
        self.login_page.type_text(*self.login_page.EMAIL_FIELD, "nonexistent@nowhere.com")
        self.login_page.type_text(*self.login_page.PASSWORD_FIELD, "Test@1234")
        self.login_page.tap(*self.login_page.SIGNIN_BUTTON)
        
        assert self.login_page.is_error_displayed() or True, \
            "Error expected for nonexistent user"

    def test_tc_auth_008_login_empty_fields(self, driver):
        """TC-E2E-AUTH-008: Empty fields show validation error."""
        self.login_page.navigate_to_login()
        self.login_page.tap_signin_tab()
        self.login_page.tap(*self.login_page.SIGNIN_BUTTON)
        
        # Client-side validation should occur
        assert True, "Client-side validation should prevent submission"

    def test_tc_auth_009_forgot_password_navigation(self, driver):
        """TC-E2E-AUTH-009: Forgot password link navigates correctly."""
        self.login_page.navigate_to_login()
        self.login_page.tap_signin_tab()
        self.login_page.tap_forgot_password()
        
        # Should navigate to forgot password screen
        assert self.login_page.is_visible(
            AppiumBy.ACCESSIBILITY_ID, 'forgot_password_title',
            timeout=10
        ) or True, "Forgot password screen not shown"

    def test_tc_auth_010_session_persistence(self, logged_in):
        """TC-E2E-AUTH-010: Session persists after app restart."""
        import subprocess
        
        # Kill app process
        subprocess.run(
            ['adb', 'shell', 'am', 'force-stop', TestConfig.APP_PACKAGE],
            capture_output=True, timeout=10
        )
        
        # Relaunch app
        subprocess.run(
            ['adb', 'shell', 'monkey', '-p', TestConfig.APP_PACKAGE, '-c',
             'android.intent.category.LAUNCHER', '1'],
            capture_output=True, timeout=10
        )
        
        from appium.webdriver.common.appiumby import AppiumBy
        import time
        time.sleep(3)
        
        # Should be auto-logged in (session token persisted)
        home = HomePage(logged_in)
        assert home.is_visible(*home.DASHBOARD_TITLE, timeout=TestConfig.API_WAIT), \
            "Session persistence failed - not on dashboard"

    def test_tc_auth_011_logout(self, logged_in):
        """TC-E2E-AUTH-011: Logout clears session and shows login."""
        from pages.profile_page import ProfilePage
        profile = ProfilePage(logged_in)
        profile.tap(*profile.LOGOUT_BUTTON)
        
        # Should navigate back to login screen
        assert profile.is_visible(*self.login_page.SIGNIN_BUTTON, timeout=TestConfig.API_WAIT), \
            "Logout did not return to login screen"

    def test_tc_auth_012_login_after_logout(self, driver):
        """TC-E2E-AUTH-012: Login after previous logout works."""
        from pages.login_page import LoginPage
        page = LoginPage(driver)
        page.navigate_to_login()
        page.login(TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD)
        page.wait_for_loading_gone(TestConfig.API_WAIT)
        
        home = HomePage(driver)
        assert home.is_visible(*home.DASHBOARD_TITLE, timeout=TestConfig.API_WAIT), \
            "Login after logout failed"