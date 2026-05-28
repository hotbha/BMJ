# BookMyJuice Appium E2E Test Suite

Real integration E2E tests for the BookMyJuice Flutter mobile app.

## Prerequisites

- Python 3.10+
- Appium server (`npm install -g appium`)
- Android device with USB Debugging enabled
- bmjServer running locally (`mvn spring-boot:run`)
- Firebase Auth test account
- Chargebee TEST site API key

## Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Start Appium
appium --port 4723
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

## Reports

- HTML report: `reports/e2e_full_report.html` (or `smoke_report.html`)
- Screenshots: `reports/screenshots/FAIL_*.png`
- Logs: `reports/appium.log`, `reports/full_output.log`