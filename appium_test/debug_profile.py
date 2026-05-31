"""
Debug: Dump profile page UI to see Sign In element.
"""
import time
import json
import os
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy

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
    
    # Find "Sign In" anywhere
    all_els = driver.find_elements(*uia('new UiSelector().descriptionContains("Sign In")'))
    print(f"\nElements with 'Sign In' in desc: {len(all_els)}")
    for el in all_els:
        print(f"  class={el.get_attribute('className')}, desc='{el.get_attribute('content-desc')}', clickable={el.get_attribute('clickable')}")

try:
    # Navigate to profile
    profile_btn = driver.find_element(*uia('new UiSelector().descriptionContains("Profile")'))
    profile_btn.click()
    time.sleep(3)
    
    dump_page('07_profile_page')

finally:
    driver.quit()