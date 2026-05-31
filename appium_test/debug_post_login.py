"""
Debug: Dump UI after login to see what screen appears.
Uses REAL credentials from .env via TestConfig.
"""
import time
import json
import os
import sys

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from config.test_config import TestConfig

config_path = os.path.join(os.path.dirname(__file__), 'config', 'device_config.json')
with open(config_path) as f:
    device_config = json.load(f)

options = UiAutomator2Options()
for key, value in device_config.items():
    options.set_capability(key, value)

driver = webdriver.Remote('http://127.0.0.1:4723', options=options)
driver.implicitly_wait(10)

def uia(selector):
    return (AppiumBy.ANDROID_UIAUTOMATOR, selector)

def dump_page(label: str):
    time.sleep(2)
    source = driver.page_source
    path = os.path.join(os.path.dirname(__file__), 'reports', f'dump_{label}.xml')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(source)
    print(f"Saved {path} ({len(source)} chars)")
    
    views = driver.find_elements(*uia('new UiSelector().className("android.view.View")'))
    print(f"\n=== {label} ===")
    for el in views:
        desc = el.get_attribute('content-desc') or ''
        if desc.strip():
            display = desc[:200].replace('\n', '\\n')
            print(f"  View: '{display}'")
    
    btns = driver.find_elements(*uia('new UiSelector().className("android.widget.Button")'))
    for el in btns:
        desc = el.get_attribute('content-desc') or ''
        if desc.strip():
            display = desc[:200].replace('\n', '\\n')
            print(f"  Button: '{display}'")
    
    edit_texts = driver.find_elements(*uia('new UiSelector().className("android.widget.EditText")'))
    for i, el in enumerate(edit_texts):
        desc = el.get_attribute('content-desc') or ''
        hint = el.get_attribute('text') or ''
        display_desc = desc[:100].replace('\n', '\\n') if desc else ''
        print(f"  EditText[{i}]: desc='{display_desc}' text='{hint[:50]}'")
    
    # Check if keyboard is visible
    try:
        is_keyboard = driver.is_keyboard_shown()
        print(f"\nKeyboard visible: {is_keyboard}")
    except:
        pass

try:
    # Launch the app
    print("=== Step 0: Launching app ===")
    driver.activate_app("com.bookmyjuice.app")
    time.sleep(5)
    dump_page('00_launched')
    
    print("=== Step 1: Navigate to login ===")
    # Wait for dashboard to appear
    try:
        home_els = driver.find_elements(*uia('new UiSelector().descriptionContains("BookMyJuice")'))
        if not home_els:
            # Try looking for other dashboard indicators
            home_els = driver.find_elements(*uia('new UiSelector().descriptionContains("Home")'))
        if home_els:
            print("Dashboard visible")
    except:
        print("Dashboard not found, checking current screen...")
    
    # Find and tap Profile tab
    profile_btn = driver.find_element(*uia('new UiSelector().descriptionContains("Profile")'))
    profile_btn.click()
    time.sleep(2)
    
    signin = driver.find_element(*uia('new UiSelector().description("Sign In")'))
    signin.click()
    time.sleep(3)
    
    dump_page('02a_login_page')
    
    print("=== Step 2: Type credentials ===")
    print(f"Using email: {TestConfig.TEST_EMAIL}")
    print(f"Using password: {TestConfig.TEST_PASSWORD}")
    
    email = driver.find_element(*uia('new UiSelector().className("android.widget.EditText").instance(0)'))
    email.click()
    email.clear()
    email.send_keys(TestConfig.TEST_EMAIL)
    time.sleep(1)
    
    # Hide keyboard
    try:
        driver.hide_keyboard()
    except:
        pass
    time.sleep(1)
    
    pwd = driver.find_element(*uia('new UiSelector().className("android.widget.EditText").instance(1)'))
    pwd.click()
    pwd.clear()
    pwd.send_keys(TestConfig.TEST_PASSWORD)
    time.sleep(1)
    
    # Hide keyboard
    try:
        driver.hide_keyboard()
    except:
        pass
    time.sleep(1)
    
    dump_page('02b_filled_form')
    
    print("=== Step 3: Tap Sign In ===")
    signin_btn = driver.find_element(*uia('new UiSelector().className("android.widget.Button").descriptionContains("Sign In")'))
    print(f"Found Sign In button: class={signin_btn.get_attribute('className')}, desc='{signin_btn.get_attribute('content-desc')}'")
    signin_btn.click()
    
    print("Waiting 3s for post-login...")
    time.sleep(3)
    dump_page('05_post_login_3s')
    
    print("Waiting 5s more...")
    time.sleep(5)
    dump_page('06_post_login_8s')
    
    print("Waiting 10s more...")
    time.sleep(10)
    dump_page('07_post_login_18s')

finally:
    driver.quit()