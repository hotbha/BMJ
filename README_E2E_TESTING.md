# BookMyJuice E2E Testing Guide

**Version:** 1.0  
**Date:** March 31, 2026  
**Framework:** Patrol CLI + Flutter Integration Test

---

## 🎯 Overview

BookMyJuice uses **Patrol CLI** for E2E testing across all devices:
- ✅ Emulators (Android/iOS)
- ✅ Physical Devices (25053PC47I)
- ✅ CI/CD (GitHub Actions, GitLab CI)

---

## 📦 Installation

### Prerequisites
```bash
# Node.js 18+ required
node --version  # v18.0.0 or higher

# Flutter 3.x
flutter --version

# Patrol CLI
dart pub global activate patrol_cli
```

### Install Dependencies
```bash
cd lush
flutter pub get

cd ..
npm install
```

---

## 🚀 Quick Start

### Run All E2E Tests
```bash
npm run e2e
```

### Run on Specific Device
```bash
# Physical device
npm run e2e:physical

# Emulator
npm run e2e:emulator

# Custom device
npm run e2e:device --device=25053PC47I
```

### Run Specific Test Suite
```bash
# Complete flow (login → catalog → cart → checkout → orders)
npm run e2e:full

# Signup flow only
npm run e2e:signup

# Checkout flow only
npm run e2e:checkout

# Cart flow only
npm run e2e:cart

# Orders flow only
npm run e2e:orders
```

---

## 🛠️ Makefile Commands

### Help
```bash
make help
```

### Run Tests
```bash
# All tests on default device
make test-e2e

# Specific device
make test-device DEVICE=25053PC47I

# Physical device
make test-physical

# Emulator
make test-emulator

# Specific flow
make test-checkout
make test-signup
make test-cart
make test-orders

# Complete suite
make test-full
```

### Reporting
```bash
# Run with JSON reporting
make test-report

# Clean reports
make e2e-clean

# Clean + run with reporting
make e2e-all
```

### CI/CD Mode
```bash
# Headless mode for CI
make test-ci

# With video recording
make test-video

# With screenshots
make test-screenshots
```

---

## 📊 Test Reports

### Output Location
```
.e2e-reports/
├── results.json          # JSON test results
├── videos/               # Test run videos
└── screenshots/          # Test screenshots
```

### View Results
```bash
# JSON results
cat .e2e-reports/results.json | jq

# Videos
open .e2e-reports/videos/

# Screenshots
open .e2e-reports/screenshots/
```

---

## 📱 Device Configuration

### List Available Devices
```bash
patrol devices
```

### Example Output
```
List of attached devices:
- emulator-5554 (Android Emulator)
- 25053PC47I (Physical Device)
```

### Configure Device
```bash
# In package.json
{
  "config": {
    "device": "25053PC47I"
  }
}

# Or via command line
npm run e2e:device --device=25053PC47I
```

---

## 🧪 Test Suites

### 1. Complete E2E Suite
**File:** `lush/integration_test/e2e_suite.dart`

**Coverage:**
- Login → Catalog → Cart → Checkout → Orders
- Full revenue flow verification

**Run:**
```bash
npm run e2e:full
```

### 2. Signup Flow
**File:** `lush/integration_test/e2e_signup_test.dart`

**Coverage:**
- Email signup
- Phone signup
- Google signup

**Run:**
```bash
npm run e2e:signup
```

### 3. Checkout Flow
**File:** `lush/integration_test/e2e_checkout_test.dart`

**Coverage:**
- Cart → Checkout
- Chargebee payment
- Order confirmation

**Run:**
```bash
npm run e2e:checkout
```

### 4. Cart Flow
**File:** `lush/integration_test/e2e_cart_test.dart`

**Coverage:**
- Add to cart
- Update quantity
- Remove items
- Clear cart

**Run:**
```bash
npm run e2e:cart
```

### 5. Orders Flow
**File:** `lush/integration_test/e2e_orders_test.dart`

**Coverage:**
- View order history
- Order details
- Order status

**Run:**
```bash
npm run e2e:orders
```

---

## ⚙️ Configuration

### Environment Variables
```bash
# API Base URL
export API_BASE_URL=http://192.168.1.6:8080

# Test Credentials
export E2E_EMAIL=test@bookmyjuice.com
export E2E_PASS=SecurePass123!
```

### Dart Defines
```bash
patrol test \
  --dart-define=E2E=true \
  --dart-define=API_BASE_URL=http://192.168.1.6:8080 \
  --dart-define=E2E_EMAIL=test@bookmyjuice.com \
  --dart-define=E2E_PASS=SecurePass123!
```

---

## 🔧 VSCode Integration

### Run E2E Tests from VSCode

1. **Open Command Palette** (Ctrl+Shift+P / Cmd+Shift+P)
2. **Select Task:** `Tasks: Run Task`
3. **Choose E2E Task:**
   - `E2E: Run All Tests`
   - `E2E: Run on Physical Device`
   - `E2E: Run on Emulator`
   - `E2E: Run with Video`
   - `E2E: Run with Reporting`
   - `E2E: Complete Flow Test`
   - `E2E: Checkout Flow`

### Keyboard Shortcuts
```json
{
  "key": "ctrl+shift+e",
  "command": "workbench.action.tasks.runTask",
  "args": "E2E: Run All Tests"
}
```

---

## 📈 CI/CD Integration

### GitHub Actions
```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: subosito/flutter-action@v2
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install Dependencies
        run: |
          flutter pub get
          npm install
      
      - name: Run E2E Tests
        run: npm run e2e:ci
      
      - name: Upload Reports
        uses: actions/upload-artifact@v3
        with:
          name: e2e-reports
          path: .e2e-reports/
```

### GitLab CI
```yaml
e2e:
  stage: test
  image: ghcr.io/leancodepl/patrol:latest
  script:
    - flutter pub get
    - npm install
    - npm run e2e:ci
  artifacts:
    reports:
      junit: .e2e-reports/results.xml
    paths:
      - .e2e-reports/
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. Device Not Found
```bash
# Check device connection
patrol devices

# Restart ADB
adb kill-server
adb start-server

# Reconnect device
adb reconnect
```

#### 2. Test Timeout
```bash
# Increase timeout
patrol test --timeout=60s
```

#### 3. Element Not Found
```bash
# Enable verbose logging
patrol test --verbose

# Take screenshot for debugging
patrol test --screenshots
```

#### 4. Patrol CLI Not Found
```bash
# Install globally
dart pub global activate patrol_cli

# Add to PATH
export PATH="$PATH":"$HOME/.pub-cache/bin"
```

---

## 📚 Resources

| Resource | Link |
|----------|------|
| Patrol Documentation | https://patrol.leancode.co/ |
| Flutter Integration Test | https://docs.flutter.dev/testing/integration-tests |
| BookMyJuice Test Cases | `docs/Test_Cases_Detailed.md` |
| E2E Test Suite | `lush/integration_test/e2e_suite.dart` |

---

## 🎯 Success Criteria

- ✅ All E2E tests pass on emulator
- ✅ All E2E tests pass on physical device (25053PC47I)
- ✅ Reports generated in `.e2e-reports/`
- ✅ CI/CD pipeline runs E2E tests
- ✅ Test coverage > 80% for critical flows

---

**Last Updated:** March 31, 2026  
**Maintained By:** BookMyJuice QA Team
