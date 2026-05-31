"""Dump all key screens with proper navigation to understand actual UI hierarchy."""
import json
import os
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

def dump(name):
    time.sleep(3)
    ps = driver.page_source
    path = os.path.join(report_dir, f'screen_{name}.xml')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(ps)
    
    root = ET.fromstring(ps.encode())
    texts = set()
    for elem in root.iter():
        cd = elem.get('content-desc', '')
        if cd and cd.strip():
            texts.add(cd.strip())
        t = elem.get('text', '')
        if t and t.strip():
            texts.add('[text]: ' + t.strip())
    
    print(f'\n=== SCREEN: {name} ===')
    print('--- TEXT ---')
    for t in sorted(texts):
        print(f'  {t}')
    
    print('--- CLICKABLE ---')
    for elem in root.iter():
        if elem.get('clickable') == 'true':
            cd = elem.get('content-desc', '')
            cl = elem.get('class', '')
            rid = elem.get('resource-id', '')
            print(f'  class={cl} desc="{cd}" rid="{rid}"')
    
    print(f'  Saved to {path}')

# 1. Dashboard Home (already there from launch)
dump('01_dashboard_home')

# 2. Navigate to Profile
try:
    profile_btns = driver.find_elements(AppiumBy.ANDROID_UIAUTOMATOR, 
        'new UiSelector().descriptionContains("Profile")')
    # Pick the last one (nav button at bottom, not any stray ones)
    profile_btns[-1].click()
    time.sleep(2)
    dump('02_profile_guest')
    
    # 3. Click Sign In - use the GlassCard which is a view with description "Sign In"
    sign_in_btns = driver.find_elements(AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().description("Sign In")')
    if sign_in_btns:
        sign_in_btns[0].click()
        time.sleep(3)
        dump('03_login_page')
    else:
        print("  Sign In button not found by exact description match")
        # Try descriptionContains
        btns = driver.find_elements(AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().descriptionContains("Sign In")')
        print(f"  Found {len(btns)} elements containing 'Sign In' in desc")
        for i, b in enumerate(btns):
            print(f"    [{i}] desc='{b.get_attribute('content-desc')}' class='{b.get_attribute('className')}'")
except Exception as e:
    print(f"  Error during navigation: {e}")

# 4. Back to home, navigate to Menu tab
try:
    driver.press_keycode(4)  # back
    time.sleep(2)
    driver.press_keycode(4)  # back
    time.sleep(2)
    menu_btns = driver.find_elements(AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().descriptionContains("Menu")')
    if menu_btns:
        menu_btns[-1].click()
        time.sleep(2)
        dump('04_menu_tab')
except Exception as e:
    print(f"  Menu nav error: {e}")

driver.quit()
print('\n=== DONE ===')