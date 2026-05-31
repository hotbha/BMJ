"""Dump current screen's page source to understand the actual UI hierarchy."""
import json
import os
import sys
import time
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from xml.etree import ElementTree as ET

config_path = os.path.join(os.path.dirname(__file__), 'config', 'device_config.json')
with open(config_path) as f:
    device_config = json.load(f)

options = UiAutomator2Options()
for key, value in device_config.items():
    options.set_capability(key, value)

driver = webdriver.Remote('http://127.0.0.1:4723', options=options)
driver.implicitly_wait(30)

report_dir = os.path.join(os.path.dirname(__file__), 'reports')
os.makedirs(report_dir, exist_ok=True)

def dump_screen(name):
    time.sleep(3)
    page_source = driver.page_source
    output_path = os.path.join(report_dir, f'page_source_{name}.xml')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(page_source)
    
    root = ET.fromstring(page_source.encode())
    texts = []
    for elem in root.iter():
        text = elem.get('text', '')
        if text and text.strip():
            texts.append(text.strip())
        content_desc = elem.get('content-desc', '')
        if content_desc and content_desc.strip():
            texts.append(f"[desc]: {content_desc.strip()}")

    print(f"\n=== SCREEN: {name} ===")
    print("--- VISIBLE TEXT ---")
    for t in sorted(set(texts)):
        print(f"  {t}")
    
    print("\n--- CLICKABLE ELEMENTS ---")
    for elem in root.iter():
        cl = elem.get('class', '')
        text = elem.get('text', '')
        if elem.get('clickable') == 'true':
            cd = elem.get('content-desc', '')
            rid = elem.get('resource-id', '')
            print(f"  class={cl} text='{text}' desc='{cd}' rid='{rid}'")
    
    print(f"\n  Saved to: {output_path}")

# 1. Dump current screen (Dashboard Home tab)
dump_screen("01_dashboard_home")

# 2. Navigate to Profile tab
try:
    profile_tab = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().descriptionContains("Profile")')
    profile_tab.click()
    dump_screen("02_profile_guest")
    
    # 3. Click Sign In from Profile
    try:
        sign_in_btn = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().descriptionContains("Sign In")')
        sign_in_btn.click()
        dump_screen("03_login_page")
    except:
        print("  [Sign In button not found on Profile page]")
    
except:
    print("  [Profile tab not found]")

# 4. Go back to home and navigate to Menu tab
try:
    driver.press_keycode(4)  # Back
    time.sleep(2)
    driver.press_keycode(4)  # Back again if needed
    time.sleep(2)
    menu_tab = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().descriptionContains("Menu")')
    menu_tab.click()
    dump_screen("04_menu_tab")
except:
    print("  [Menu tab not found or navigation failed]")

driver.quit()
print("\n=== DUMP COMPLETE ===")