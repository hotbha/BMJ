"""
Pytest configuration and fixtures for BookMyJuice E2E tests.
"""
import os
import sys
import json
import base64
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
    """Login via app UI with real Firebase Auth credentials."""
    from pages.login_page import LoginPage
    page = LoginPage(driver)
    page.navigate_to_login()
    page.login(TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD)
    page.wait_for_loading_gone()
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
                print(f"\n  📸 Screenshot saved: {path}")
            except Exception as e:
                print(f"\n  ⚠️  Could not save screenshot: {e}")