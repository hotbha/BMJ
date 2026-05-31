import requests, time, json

url = 'http://127.0.0.1:4723/session/fa3e5f1c-f839-4d6b-9b9d-8f9427d37d2e'
headers = {'Content-Type': 'application/json'}

# Tap Profile tab on nav bar (coordinates from uiautomator dump)
payload = {
    'actions': [
        {'type': 'pointer', 'id': 'finger1', 'parameters': {'pointerType': 'touch'},
         'actions': [
             {'type': 'pointerMove', 'duration': 0, 'x': 1076, 'y': 2471},
             {'type': 'pointerDown', 'button': 0},
             {'type': 'pointerUp', 'button': 0}
         ]}
    ]
}
r = requests.post(f'{url}/actions', json=payload, headers=headers, timeout=15)
print('Tap status:', r.status_code)

time.sleep(3)

# Get page source
r2 = requests.get(f'{url}/source', headers=headers, timeout=15)
data = r2.json().get('value', '')

# Find all content-desc attributes
import re
matches = re.findall(r'content-desc="([^"]*)"', data)
for m in matches:
    if any(x in m.lower() for x in ['sign', 'profile']):
        print(f'Found: {repr(m)}')