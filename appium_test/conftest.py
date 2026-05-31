"""
Pytest configuration and fixtures for BookMyJuice E2E tests.
"""
import os
import sys
import json
import base64
import time
import pytest
import requests
from appium import webdriver
from appium.options.android import UiAutomator2Options
from config.test_config import TestConfig


def load_device_config():
    config_path = os.path.join(os.path.dirname(__file__), 'config', 'device_config.json')
    with open(config_path) as f:
        return json.load(f)


@pytest.fixture(scope='session')
def driver():
    """Create Appium driver session. Session-scoped to avoid restarting app between tests."""
    device_config = load_device_config()
    options = UiAutomator2Options()
    for key, value in device_config.items():
        options.set_capability(key, value)
    
    driver = webdriver.Remote('http://127.0.0.1:4723', options=options)
    driver.implicitly_wait(TestConfig.IMPLICIT_WAIT)
    
    yield driver
    
    if driver:
        driver.quit()


@pytest.fixture(scope='function')
def logged_in(driver):
    """Login via app UI with real Firebase Auth credentials.
    
    Navigation flow: Dashboard → Profile tab → tap "Sign In" → login page
    The app shows Dashboard to ALL users (including unauthenticated) on first launch.
    
    Handles being on any screen: ensures we get back to Dashboard first,
    then navigates to Profile → Sign In → login.
    """
    from pages.home_page import HomePage
    from pages.profile_page import ProfilePage
    from pages.login_page import LoginPage

    # Step 1: Ensure we're on Dashboard (handle being on login or other screens)
    home = HomePage(driver)
    login_page = LoginPage(driver)
    
    if login_page.is_displayed(timeout=3):
        # Already on login page — just fill credentials
        pass
    else:
        if not home.is_dashboard_displayed(timeout=8):
            home.wait_for_dashboard(timeout=12)
        # Step 2: Navigate from Dashboard to Profile tab
        home.navigate_to_profile()
        # Step 3: Tap Sign In on guest profile
        profile = ProfilePage(driver)
        profile.tap_sign_in()
        # Step 4: Wait for login page
        login_page.wait_for_element(*login_page.WELCOME_BACK,
                                    timeout=TestConfig.EXPLICIT_WAIT)

    # Step 5: Perform login
    login_page.login(TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD)

    # Step 6: After login Navigator.pop(), we're back on Dashboard but may be on
    # Profile tab. The nav bar uses onlyShowSelected, so "Home" label is only
    # visible when Home tab is selected. Confirm dashboard via top-bar header.
    # Then try navigating to Home tab; it's non-fatal if we can't since tests
    # handle being on any tab.
    time.sleep(3)
    try:
        home.navigate_to_home()
    except (TimeoutException, NoSuchElementException):
        # Home label not visible (Profile tab selected). Use press_back fallback.
        # We're on Dashboard after login pop(), so press_back is harmless.
        home.press_back()
        time.sleep(1)
        try:
            home.navigate_to_home()
        except (TimeoutException, NoSuchElementException):
            pass
    home.wait_for_dashboard(timeout=TestConfig.EXPLICIT_WAIT)
    yield driver


@pytest.fixture(scope='function')
def clean_subscription(logged_in):
    """Cancel any active Chargebee subscription before subscription tests."""
    api_key = TestConfig.CHARGEBEE_API_KEY
    site = TestConfig.CHARGEBEE_SITE
    auth_str = base64.b64encode(f"{api_key}:".encode()).decode()
    headers = {'Authorization': f'Basic {auth_str}'}
    
    try:
        r = requests.get(
            f'https://{site}.chargebee.com/api/v2/subscriptions',
            headers=headers,
            params={'status[is]': 'active'},
            timeout=15
        )
        for sub_entry in r.json().get('list', []):
            sub_id = sub_entry['subscription']['id']
            requests.post(
                f'https://{site}.chargebee.com/api/v2/subscriptions/{sub_id}/cancel',
                headers=headers,
                timeout=15
            )
    except Exception as e:
        print(f"Warning: Could not cleanup subscriptions: {e}")
    
    yield logged_in


@pytest.fixture(scope='function')
def clean_orders(logged_in):
    """Cancel any incomplete orders before order tests."""
    server_url = TestConfig.SERVER_URL
    try:
        r = requests.get(
            f'{server_url}/api/orders',
            params={'status': 'pending'},
            timeout=10
        )
        for order in r.json().get('orders', []):
            order_id = order.get('id')
            if order_id:
                requests.delete(
                    f'{server_url}/api/orders/{order_id}',
                    timeout=10
                )
    except Exception as e:
        print(f"Warning: Could not cleanup orders: {e}")
    
    yield logged_in


# Auto-screenshot on test failure
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.failed:
        driver = None
        for name in ('driver', 'logged_in', 'clean_subscription', 'clean_orders'):
            try:
                driver = item.funcargs.get(name)
                if driver:
                    break
            except (KeyError, AttributeError):
                continue
        
        if driver:
            screenshots_dir = os.path.join(
                os.path.dirname(__file__), 'reports', 'screenshots'
            )
            os.makedirs(screenshots_dir, exist_ok=True)
            name = item.name.replace('::', '_').replace('/', '_')
            path = os.path.join(screenshots_dir, f'FAIL_{name}.png')
            try:
                driver.save_screenshot(path)
                print(f"\n  [Screenshot saved]: {path}")
            except Exception as e:
                print(f"\n  [Could not save screenshot]: {e}")