"""Dump login page to find EditText indices."""
import json
import os
import time
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy

config_path = os.path.join(os.path.dirname(__file__), 'config', 'device_config.json')
with open(config_path) as f:
    device_config = json.load(f)

options = UiAutomator2Options()
for k, v in device_config.items():
    options.set_capability(k, v)

driver = webdriver.Remote('http://127.0.0.1:4723', options=options)
time.sleep(1)

# Navigate to login page
driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,
    'new UiSelector().descriptionContains("Profile")').click()
time.sleep(2)
driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,
    'new UiSelector().description("Sign In")').click()
time.sleep(3)

# Save page source
xml = driver.page_source
with open(os.path.join('reports', 'screen_login_dump.xml'), 'w', encoding='utf-8') as f:
    f.write(xml)

# Find all EditText 
els = driver.find_elements(AppiumBy.CLASS_NAME, 'android.widget.EditText')
print(f'Found {len(els)} EditText elements:')
for i, el in enumerate(els):
    hint = el.get_attribute('hint') or '(no hint)'
    text = el.get_attribute('text') or '(empty)'
    desc = el.get_attribute('content-desc') or '(no desc)'
    bounds = el.get_attribute('bounds') or '(no bounds)'
    print(f'  EditText[{i}]: hint="{hint}" text="{text}" desc="{desc}" bounds={bounds}')

# Try with UiAutomator instance selector
for i in range(5):
    try:
        el = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,
            f'new UiSelector().className("android.widget.EditText").instance({i})')
        hint = el.get_attribute('hint') or '(no hint)'
        print(f'  UiAutomator EditText instance({i}): hint="{hint}"')
    except Exception as e:
        print(f'  UiAutomator EditText instance({i}): NOT FOUND - {e}')

# Also check for the email/password fields in the full page source
print("\n--- Looking for 'Email' and 'Password' in XML ---")
count_email = xml.count('Email')
count_password = xml.count('Password')
print(f"'Email' occurs {count_email} times")
print(f"'Password' occurs {count_password} times")

# Find lines with EditText in XML
for line in xml.split('\n'):
    if 'EditText' in line:
        print(f"  XML: {line.strip()[:200]}")

driver.quit()