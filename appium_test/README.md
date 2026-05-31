# BookMyJuice Appium E2E Test Suite

Real integration E2E tests for the BookMyJuice Flutter mobile app.

## Prerequisites

- Python 3.10+
- Appium server (`npm install -g appium`)
- Android device with Wi-Fi ADB Debugging enabled (wireless, port 5555)
- bmjServer running locally (`mvn spring-boot:run`) or deployed
- Firebase Auth test account (email/password provider — credentials must be pre-created)
- Chargebee TEST site API key

## Setup

### Wireless ADB Connection
This suite connects to the Android device over Wi-Fi ADB (no USB required after initial pairing).
```powershell
# Verify device is connected
adb devices

# If not found, connect wirelessly
adb connect <DEVICE_IP>:5555

# Verify connection is stable (ping both ways)
adb shell ping -c 1 8.8.8.8
```

### Python Dependencies & Appium
```bash
# Install Python dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Start Appium (PowerShell)
Start-Process -NoNewWindow appium --port 4723
```

## Project Structure

```
appium_test/
├── config/
│   ├── device_config.json      # Appium desired capabilities
│   └── test_config.py          # Environment config (reads .env)
├── pages/
│   ├── base_page.py            # Base page object with helpers
│   ├── login_page.py
│   ├── signup_page.py
│   ├── home_page.py
│   ├── catalog_page.py
│   ├── item_detail_page.py
│   ├── cart_page.py
│   ├── order_checkout_page.py
│   ├── address_page.py
│   ├── profile_page.py
│   ├── notification_centre_page.py
│   ├── subscription_plans_page.py
│   ├── subscription_summary_page.py
│   ├── subscription_active_page.py
│   ├── pause_subscription_page.py
│   ├── resume_subscription_page.py
│   └── cancel_subscription_page.py
├── tests/
│   ├── suite_1_auth/           # Authentication tests (12)
│   ├── suite_2_address/        # Address management tests (8)
│   ├── suite_3_catalog/        # Catalog & search tests (10)
│   ├── suite_4_subscription/   # Subscription lifecycle tests (16)
│   ├── suite_5_orders/         # Order placement tests (14)
│   ├── suite_6_notifications/  # Notification tests (10)
│   ├── suite_7_profile/        # Profile management tests (8)
│   ├── suite_8_navigation/     # Navigation tests (10)
│   └── suite_9_edge_cases/     # Edge case tests (12)
├── conftest.py                 # Pytest fixtures
├── preflight.py                # Environment validation
├── run_all.sh                  # Full suite runner
├── run_smoke.sh                # Smoke test runner
└── requirements.txt

Total: 100 test cases across 9 suites
```

## Running Tests

### Smoke Test (Auth + Catalog + Subscription + Orders)
```bash
bash run_smoke.sh
```

### Full Test Suite (all 100 tests)
```bash
bash run_all.sh
```

### Individual Suite
```bash
python3 -m pytest tests/suite_1_auth/ -v --capture=no
```

## Test Architecture

- **Real integration only**: No mocks, stubs, or simulated responses
- **Real Firebase Auth**: Actual user creation/login via Firebase
- **Real Chargebee**: Subscriptions created/paused/canceled on Chargebee TEST
- **Real bmjServer**: Orders placed against running server
- **Real FCM**: Push notifications via bmjServer test endpoint
- **Auto-screenshots**: Captured on any test failure
- **Cleanup fixtures**: Subscriptions/orders cleaned between tests

## Test Credentials

All test accounts must be pre-created in **Firebase Auth** (email/password provider) before running the suite:

```python
# Required environment variables (.env)
TEST_EMAIL=<pre-created-email>@example.com
TEST_PASSWORD=<pre-created-password>
```

> **Important:** These credentials must exist in Firebase Auth's email/password provider. The test suite does NOT auto-create them. Use the Firebase Console or Admin SDK to create the test user before running tests.

## Known Limitations

1. **Google OAuth Not Automatable**: Google Sign-In (Google OAuth) **cannot be automated** via Appium on real Android devices. It requires Google Play Services account mocking which is only possible on emulators. Only email/password authentication is used in this test suite.
2. **Dashboard-First Architecture**: The app starts on the **Dashboard** screen, even for unauthenticated users. Navigation flows in test cases must account for this — they navigate from Dashboard → Profile → Login, not from a standalone Splash/Login screen.
3. **AutoLoginFailed Race Condition**: On cold launch, the `AutoLoginFailed` event may fire before Appium has settled. Add a **4-second stabilisation wait** (`time.sleep(4)`) before the first Appium interaction to avoid flakiness.
4. **Wireless ADB Stability**: Intermittent Wi-Fi signal can cause ADB disconnections. The test suite verifies device presence before each phase and reconnects if needed.

## Reports

- HTML report: `reports/e2e_full_report.html` (or `smoke_report.html`)
- Screenshots: `reports/screenshots/FAIL_*.png`
- Logs: `reports/appium.log`, `reports/full_output.log`
