# BookMyJuice (BMJ) Testing Guide

Comprehensive testing procedures for backend, mobile app, and automated E2E test suites.

## 1. Backend Testing (Spring Boot / Maven)

Run unit and integration tests for `bmjServer`:
```bash
cd bmjServer
mvn clean test
```

To run a specific test class:
```bash
mvn test -Dtest=ItemItemPriceRelationshipTest
```

To run JaCoCo code coverage report:
```bash
mvn test jacoco:report
```
Target report directory: `bmjServer/target/site/jacoco/index.html`.

---

## 2. Mobile App Testing (Flutter)

Navigate to the `lush` directory:
```bash
cd lush
```

### Run Unit & Widget Tests
```bash
flutter test
```

### Run Specific Test Suites
```bash
flutter test test/unit/bloc/auth_bloc_test.dart
flutter test test/unit/bloc/product_catalog_bloc_test.dart
flutter test test/subscription_bloc_test.dart
```

---

## 3. End-to-End (E2E) Testing (Appium)

### Prerequisites
- Appium Server v2.x installed globally (`npm i -g appium`)
- Android SDK & Emulator or connected physical test device

### Run E2E Test Suite
```bash
# Ensure Appium server is running on port 4723
appium

# Execute test suite runner in project root
python scripts/run_e2e_tests.py
```
Reports are stored in `.e2e-reports/` and `E2E_BLACK_BOX_TEST_REPORT.md`.
