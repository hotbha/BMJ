"""
Debug script to dump profile page elements and find the Sign In button.
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
time.sleep(3)

# Navigate to profile tab
profile_btns = driver.find_elements('xpath', '//android.widget.Button[@content-desc]')
for btn in profile_btns:
    desc = btn.get_attribute('content-desc') or ''
    if 'Profile' in desc or 'profile' in desc:
        print('Found Profile nav button: content-desc=[' + desc + ']')
        btn.click()
        break
time.sleep(3)

# Dump profile screen elements
els = driver.find_elements('xpath', '//*[@content-desc]')
for el in els:
    desc = el.get_attribute('content-desc') or ''
    if desc.strip():
        clz = el.get_attribute('className') or ''
        class_name = clz.split('.')[-1] if '.' in clz else clz
        print('  [' + class_name + '] content-desc=[' + desc + ']')

driver.quit()