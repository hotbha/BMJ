"""
Debug script to dump login page elements and find the Forgot Password button.
"""
import json
from appium import webdriver
from appium.options.android import UiAutomator2Options
import time

with open('config/device_config.json') as f:
    config = json.load(f)

options = UiAutomator2Options()
for k, v in config.items():
    options.set_capability(k, v)

driver = webdriver.Remote('http://127.0.0.1:4723', options=options)
time.sleep(4)

# Navigate to login first via profile
profile_btns = driver.find_elements('xpath', '//android.widget.Button[@content-desc]')
for btn in profile_btns:
    desc = btn.get_attribute('content-desc') or ''
    if 'Profile' in desc:
        btn.click()
        break
time.sleep(2)

# Find and tap Sign In view
views = driver.find_elements('xpath', '//android.view.View[@content-desc="Sign In"]')
for v in views:
    print('Found Sign In View, clicking...')
    v.click()
    break
time.sleep(3)

# Now dump the login page elements
print('\n=== Login Page Elements ===')
els = driver.find_elements('xpath', '//*[@content-desc]')
for el in els:
    desc = el.get_attribute('content-desc') or ''
    if desc.strip():
        clz = el.get_attribute('className') or ''
        class_name = clz.split('.')[-1] if '.' in clz else clz
        print('  [' + class_name + '] content-desc=[' + desc + ']')

# Also try to find using textContains for Forgot Password
print('\n=== Searching for Forgot Password text ===')
els2 = driver.find_elements('xpath', '//*[contains(@content-desc, "Forgot") or contains(@content-desc, "forgot")]')
for el in els2:
    desc = el.get_attribute('content-desc') or ''
    clz = el.get_attribute('className') or ''
    class_name = clz.split('.')[-1] if '.' in clz else clz
    print('  [' + class_name + '] content-desc=[' + desc + ']')

driver.quit()