"""
Debug script: Dump login page UI after various actions.
"""
import time
import json
import os
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy

# Load device config
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
    """Save page source to file."""
    time.sleep(2)
    source = driver.page_source
    path = os.path.join(os.path.dirname(__file__), 'reports', f'dump_{label}.xml')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(source)
    print(f"Saved {path} ({len(source)} chars)")
    
    print(f"\n=== {label} ===")
    
    # Find all elements with content-desc containing "Forgot"
    elements = driver.find_elements(*uia('new UiSelector().descriptionContains("Forgot")'))
    print(f"Elements with 'Forgot' in content-desc: {len(elements)}")
    for el in elements:
        print(f"  class={el.get_attribute('className')}, "
              f"desc='{el.get_attribute('content-desc')}', "
              f"clickable={el.get_attribute('clickable')}")
    
    # Find all elements with content-desc containing "Phone" or "OTP"
    elements = driver.find_elements(*uia('new UiSelector().descriptionContains("Phone")'))
    print(f"Elements with 'Phone' in content-desc: {len(elements)}")
    for el in elements:
        print(f"  class={el.get_attribute('className')}, "
              f"desc='{el.get_attribute('content-desc')}', "
              f"clickable={el.get_attribute('clickable')}")
    
    elements = driver.find_elements(*uia('new UiSelector().descriptionContains("OTP")'))
    print(f"Elements with 'OTP' in content-desc: {len(elements)}")
    for el in elements:
        print(f"  class={el.get_attribute('className')}, "
              f"desc='{el.get_attribute('content-desc')}', "
              f"clickable={el.get_attribute('clickable')}")

    # Find "Sign Up" elements
    elements = driver.find_elements(*uia('new UiSelector().descriptionContains("Sign Up")'))
    print(f"\nElements with 'Sign Up' in content-desc: {len(elements)}")
    for el in elements:
        print(f"  class={el.get_attribute('className')}, "
              f"desc='{el.get_attribute('content-desc')}', "
              f"clickable={el.get_attribute('clickable')}")

    # Find "Email" elements
    elements = driver.find_elements(*uia('new UiSelector().descriptionContains("Email")'))
    print(f"Elements with 'Email' in content-desc: {len(elements)}")
    for el in elements:
        print(f"  class={el.get_attribute('className')}, "
              f"desc='{el.get_attribute('content-desc')}', "
              f"clickable={el.get_attribute('clickable')}")

    # Find all Buttons with content-desc
    elements = driver.find_elements(*uia('new UiSelector().className("android.widget.Button")'))
    print(f"\nAll Button elements ({len(elements)}):")
    for el in elements:
        desc = el.get_attribute('content-desc') or ''
        if desc.strip():
            print(f"  desc='{desc}'")
    
    # Find all View elements with non-empty content-desc
    views = driver.find_elements(*uia('new UiSelector().className("android.view.View")'))
    print(f"\nAll View elements ({len(views)}):")
    count = 0
    for el in views:
        desc = el.get_attribute('content-desc') or ''
        if desc.strip():
            print(f"  desc='{desc[:200]}'")
            count += 1
            if count > 50:
                print("  ... (truncated)")
                break

try:
    print("=== Step 1: Current state (should be on dashboard) ===")
    dump_page('01_initial')
    
    # Navigate to login
    print("\n=== Step 2: Navigating to login ===")
    profile_btn = driver.find_element(*uia('new UiSelector().descriptionContains("Profile")'))
    profile_btn.click()
    time.sleep(2)
    
    signin = driver.find_element(*uia('new UiSelector().description("Sign In")'))
    signin.click()
    time.sleep(3)
    
    dump_page('02_login_page')
    
    # Tap Sign Up tab - use NEWLINE character, not literal \n
    print("\n=== Step 3: Tapping Sign Up tab ===")
    # Try with raw newline instead of escaped
    tabs = driver.find_elements(*uia('new UiSelector().className("android.view.View").descriptionContains("Sign Up")'))
    print(f"Sign Up tab candidates: {len(tabs)}")
    for tab in tabs:
        desc = tab.get_attribute('content-desc') or ''
        print(f"  desc='{desc}'")
    
    if tabs:
        tabs[0].click()
        time.sleep(2)
        dump_page('03_signup_tab')

    # Go back to login page
    driver.back()
    time.sleep(1)
    
    # Tap Forgot Password
    print("\n=== Step 4: Tap Forgot Password ===")
    forgot = driver.find_element(*uia('new UiSelector().descriptionContains("Forgot")'))
    forgot.click()
    time.sleep(2)
    
    dump_page('04_forgot_password')

finally:
    driver.quit()