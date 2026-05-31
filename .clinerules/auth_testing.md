# BookMyJuice — Cline Auth Testing Rules
# Version: 3.0 — Root Cause Confirmed from Logcat
# Last Updated: June 2026

---

## ⚡ CONFIRMED ROOT CAUSE — READ THIS FIRST

From live logcat analysis (June 2026), Google Sign-In fails with:

```
✅ Signed in: pbharat.hotwani@gmail.com       ← GOOGLE OAUTH WORKS
✅ Display Name: Bharat Hotwani               ← TOKEN IS VALID
❌ SocketException: No route to host          ← BACKEND IS UNREACHABLE
   address = 192.168.1.6, port = 60090
   uri = http://192.168.1.6:8080/api/auth/google
```

**The Google Sign-In itself is WORKING. The problem is the backend server at
`192.168.1.6:8080` is not reachable from the Android device.**

Secondary bug: `AuthenticationBloc` emits `SignUpStarted` on SocketException
instead of `AuthError` — causing app to navigate to signup screen on any network error.

---

## MANDATORY PRE-TEST CHECKLIST

Before running ANY auth test, verify ALL of these:

### Step 1: Check ADB Connection
```bash
adb devices
# Expected: <DEVICE_IP>:5555   device
# If not: adb connect <DEVICE_IP>:5555
```

### Step 2: Discover Current Machine IP
```bash
# Windows PowerShell
(Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -like '*Wi-Fi*'}).IPAddress

# Linux/Mac
hostname -I | awk '{print $1}'

# Or check ifconfig
ifconfig | grep 'inet ' | grep -v 127.0.0.1
```
Save this IP — call it `$MACHINE_IP`

### Step 3: Verify Backend is Running
```bash
# From dev machine
curl http://localhost:8080/api/health
# Expected: {"status": "ok"} or 200 OK

# If server is down — START IT:
cd backend  # or wherever the server code is
npm start   # or: ./gradlew bootRun  or: python manage.py runserver 0.0.0.0:8080
```

### Step 4: Verify Backend is Reachable FROM the Android Device
```bash
# This is the critical check that was failing in the logcat
adb shell curl http://$MACHINE_IP:8080/api/health
# Expected: {"status": "ok"}
# If this FAILS — the auth tests WILL fail. Fix network first.

# Common fixes:
# Windows: Allow port 8080 in Windows Firewall
#   netsh advfirewall firewall add rule name="BMJ Backend" dir=in action=allow protocol=TCP localport=8080
# Linux: sudo ufw allow 8080
# Mac: System Preferences > Security > Firewall > Allow port 8080
```

### Step 5: Verify BASE_URL in Flutter App Matches
```bash
# Check current config
grep -r 'BASE_URL\|baseUrl\|8080' flutter_app/lib/ --include='*.dart' -l
grep -r 'BASE_URL\|baseUrl\|8080' flutter_app/.env 2>/dev/null

# If IP is wrong, update it:
# Option A: Edit .env file
#   BASE_URL=http://$MACHINE_IP:8080
# Then REBUILD AND REINSTALL the APK

# Option B: If configurable at runtime, use app settings
```

### Step 6: Clear Logcat Buffer
```bash
adb logcat -c
```

**IF ANY OF STEPS 2-5 FAIL — STOP. Fix the infrastructure. Do not run tests.**

---

## TASK 1: FIX THE AUTH BLOC BUG

The `AuthenticationBloc` has a bug: on `SocketException` (backend unreachable),
it emits `SignUpStarted` instead of `AuthError`. This must be fixed.

### How to Find the File
```bash
grep -r 'SignUpStarted\|GoogleSignIn\|SocketException' flutter_app/lib/ --include='*.dart' -l
```

### What to Look For and Fix

**WRONG (current behavior):**
```dart
} catch (e) {
  emit(SignUpStarted(user));  // ← BUG: wrong state on network error
}
```

**CORRECT (required behavior):**
```dart
} on SocketException catch (e) {
  // FIX: BUG-001 — emit AuthError, NOT SignUpStarted
  emit(AuthError(
    'Cannot connect to server. Check your network connection.\n'
    'Server: ${e.address?.address}:${e.port}'
  ));
} on ClientException catch (e) {
  emit(AuthError('Network error: ${e.message}'));
} catch (e) {
  emit(AuthError('Sign-In failed: $e'));
}
```

**Also fix the GoogleSignIn handler for null check:**
```dart
final googleUser = await GoogleSignIn().signIn();
if (googleUser == null) {
  // User cancelled — do nothing, stay on screen
  return;  // ← Do NOT emit any state
}

final googleAuth = await googleUser.authentication;
if (googleAuth.idToken == null) {
  emit(AuthError('Google authentication failed: empty token'));
  return;
}
```

### After Fixing
```bash
# Rebuild and reinstall
cd flutter_app
flutter build apk --debug
adb install -r build/app/outputs/flutter-apk/app-debug.apk
```

---

## TASK 2: RUN AUTH TESTS IN ORDER

### Test Execution — Strict Order

```bash
cd appium_test

# First: smoke test — does app launch?
python -m pytest tests/suite_1_auth/test_auth.py::TestAuth::test_tc_auth_001_app_launch_shows_dashboard -v -s

# Second: can we navigate to login?
python -m pytest tests/suite_1_auth/test_auth.py::TestAuth::test_tc_auth_003_navigate_to_login_via_profile -v -s

# Third: email login (simplest, most reliable — do this before Google)
python -m pytest tests/suite_1_auth/test_auth.py::TestAuth::test_tc_auth_005_login_valid_credentials -v -s

# Fourth: Google Sign-In (ONLY after backend is confirmed reachable)
python -m pytest tests/suite_1_auth/ -v -s --tb=long -k 'google' 2>&1 | tee reports/google_auth_run.log

# Fifth: Full auth suite
python -m pytest tests/suite_1_auth/ -v --tb=short 2>&1 | tee reports/auth_full_run.log
```

---

## TASK 3: WRITE MISSING AUTH TESTS

Create `appium_test/tests/suite_1_auth/test_google_signin.py` if it doesn't exist:

```python
"""
TC-GOOGLE-001 to TC-GOOGLE-005: Google Sign-In black-box tests
Tests the full Google OAuth → Backend JWT flow.

PRE-REQUISITE: Backend at BASE_URL must be running and reachable.
Verify: adb shell curl http://<MACHINE_IP>:8080/api/health
"""
import time
import subprocess
import pytest
import requests
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.login_page import LoginPage
from pages.home_page import HomePage
from pages.profile_page import ProfilePage
from config.test_config import TestConfig


def capture_logcat(tags="flutter,GoogleSignIn,FirebaseAuth", lines=100):
    """Capture logcat output for debugging."""
    try:
        result = subprocess.run(
            ['adb', 'logcat', '-d', '-t', str(lines), '-s', tags],
            capture_output=True, text=True, timeout=15
        )
        return result.stdout
    except Exception as e:
        return f"logcat capture failed: {e}"


def check_backend_health():
    """Check if backend is reachable from this machine."""
    try:
        r = requests.get(f"{TestConfig.BASE_URL}/api/health", timeout=5)
        return r.status_code == 200
    except Exception:
        return False


def check_backend_from_device():
    """Check if backend is reachable from Android device via ADB."""
    try:
        result = subprocess.run(
            ['adb', 'shell', 'curl', '-s', '-o', '/dev/null', '-w', '%{http_code}',
             '--connect-timeout', '5', f"{TestConfig.BASE_URL}/api/health"],
            capture_output=True, text=True, timeout=15
        )
        return result.stdout.strip() == '200'
    except Exception:
        return False


def navigate_to_login(driver):
    home = HomePage(driver)
    home.wait_for_dashboard(timeout=12)
    home.navigate_to_profile()
    profile = ProfilePage(driver)
    profile.tap_sign_in()
    login = LoginPage(driver)
    login.wait_for_element(*login.GOOGLE_SIGNIN_BUTTON, timeout=10)
    return login


@pytest.fixture(scope='module', autouse=True)
def verify_backend_reachable():
    """Skip all Google tests if backend is not reachable from device."""
    if not check_backend_health():
        pytest.skip(
            f"SKIPPING Google auth tests: Backend not reachable from machine "
            f"at {TestConfig.BASE_URL}. Run: cd backend && npm start"
        )
    if not check_backend_from_device():
        pytest.skip(
            f"SKIPPING Google auth tests: Backend not reachable FROM DEVICE "
            f"at {TestConfig.BASE_URL}. "
            f"Check firewall: netsh advfirewall firewall add rule "
            f"name='BMJ' dir=in action=allow protocol=TCP localport=8080"
        )


class TestGoogleSignIn:

    @pytest.fixture(autouse=True)
    def setup(self, driver):
        self.driver = driver
        subprocess.run(['adb', 'logcat', '-c'], timeout=5)  # clear buffer

    def test_google_001_button_visible(self, driver):
        """TC-GOOGLE-001: Google Sign-In button visible on login screen."""
        login = navigate_to_login(driver)
        assert login.is_visible(*login.GOOGLE_SIGNIN_BUTTON, timeout=5), \
            "Google Sign-In button not visible"

    def test_google_002_opens_account_picker(self, driver):
        """TC-GOOGLE-002: Tapping Google button opens OS account picker."""
        login = navigate_to_login(driver)
        login.tap(*login.GOOGLE_SIGNIN_BUTTON)
        time.sleep(3)

        wait = WebDriverWait(driver, 15)
        try:
            # Google account picker uses com.google.android.gms package
            wait.until(EC.presence_of_element_located((
                AppiumBy.XPATH,
                '//*[@package="com.google.android.gms"]'
                '| //*[contains(@text,"Choose an account")]'
                '| //*[contains(@text,"Sign in")]'
            )))
        except Exception:
            driver.save_screenshot('appium_test/reports/screenshots/google_002_fail.png')
            pytest.fail("Google account picker did not appear within 15s")

        # Press back to dismiss
        driver.press_keycode(4)
        time.sleep(1)

    def test_google_003_cancellation_stays_on_login(self, driver):
        """TC-GOOGLE-003: Cancelling picker keeps user on Login screen."""
        login = navigate_to_login(driver)
        login.tap(*login.GOOGLE_SIGNIN_BUTTON)
        time.sleep(3)

        # Cancel by pressing back
        driver.press_keycode(4)
        time.sleep(2)

        assert login.is_displayed(timeout=5), \
            "After cancelling Google picker, should stay on Login screen"
        home = HomePage(driver)
        assert not home.is_dashboard_displayed(timeout=2), \
            "Should NOT navigate to Dashboard after cancelling"

    def test_google_004_successful_signin_lands_on_dashboard(self, driver):
        """TC-GOOGLE-004: Full Google Sign-In → Backend JWT → Dashboard.
        
        This test selects pbharat.hotwani@gmail.com from the account picker.
        Requires: Backend running at BASE_URL, account on device.
        """
        login = navigate_to_login(driver)
        login.tap(*login.GOOGLE_SIGNIN_BUTTON)
        time.sleep(4)  # account picker appears

        wait = WebDriverWait(driver, 20)
        try:
            # Try to find and select the specific account
            account = wait.until(EC.presence_of_element_located((
                AppiumBy.XPATH,
                '//*[contains(@text,"pbharat.hotwani@gmail.com")]'
                '| //*[contains(@resource-id,"account_name")]'
            )))
            account.click()
        except Exception:
            # Account may auto-select if only one on device
            pass

        time.sleep(8)  # Wait for OAuth + backend call

        # Capture logcat for diagnostics
        logs = capture_logcat("flutter,GoogleSignIn,FirebaseAuth", 200)
        with open('appium_test/reports/google_signin_logcat.txt', 'w') as f:
            f.write(logs)

        home = HomePage(driver)
        on_dashboard = home.is_dashboard_displayed(timeout=10)

        if not on_dashboard:
            # Diagnose what went wrong
            driver.save_screenshot('appium_test/reports/screenshots/google_004_fail.png')

            if 'SocketException' in logs or 'No route to host' in logs:
                pytest.fail(
                    "BUG-001 CONFIRMED: Backend unreachable from device.\n"
                    "Fix: Start backend + open firewall port 8080.\n"
                    f"Backend URL: {TestConfig.BASE_URL}"
                )
            elif 'SignUpStarted' in logs:
                pytest.fail(
                    "BUG-002: AuthBloc emits SignUpStarted on error instead of AuthError.\n"
                    "Fix: AuthBloc catch block must emit AuthError on SocketException."
                )
            else:
                pytest.fail(
                    f"Google Sign-In did not reach Dashboard.\n"
                    f"Check: appium_test/reports/google_signin_logcat.txt\n"
                    f"Screenshot: appium_test/reports/screenshots/google_004_fail.png"
                )

    def test_google_005_backend_error_shows_error_stays_on_login(self, driver):
        """TC-GOOGLE-005: If backend returns 500, error shown and user stays on Login.
        
        This simulates a backend error (manually stop backend during test, or mock).
        Validates that AuthBloc does NOT navigate on error.
        """
        # This test validates the error handling behavior
        # It requires manual intervention OR mocking the backend
        # For now: verify that error handling state correctly shows login
        login = navigate_to_login(driver)
        assert login.is_displayed(timeout=5), \
            "Login screen must be visible as starting state"
        # TODO: Use a mock server or proxy to inject 500 response
        # Then tap Google Sign-In and verify error is shown + stays on login
        pytest.skip("Requires backend mock/proxy setup — implement with mitmproxy")
```

---

## TASK 4: BUG TRACKING

Append all bugs to `appium_test/reports/BUG_REPORT.md` using this format:

```markdown
## BUG-001 [CRITICAL] — Google Sign-In: Backend Unreachable
- **Discovered:** June 2026 via logcat
- **Symptom:** Google picker opens, account selected, app returns to Login
- **Root Cause:** SocketException — backend at 192.168.1.6:8080 unreachable from device
- **Evidence:** `No route to host (OS Error: No route to host, errno = 113)`
- **Fix Required (Infrastructure):** Start backend, open firewall port 8080
- **Fix Required (Code):** AuthBloc must emit AuthError on SocketException, not SignUpStarted
- **Files to Fix:**
  - `flutter_app/lib/**/auth_bloc.dart` — fix catch block
  - `.env` — update BASE_URL to current machine IP
- **Status:** OPEN

## BUG-002 [HIGH] — AuthBloc Wrong State on Network Error  
- **Symptom:** Network failure emits `SignUpStarted` → app navigates to signup
- **Root Cause:** Catch block calls `emit(SignUpStarted(user))` incorrectly
- **Fix:** Replace with `emit(AuthError('Cannot connect to server'))`
- **Status:** OPEN
```

---

## TASK 5: AFTER FIXING — FULL REGRESSION

Once BUG-001 and BUG-002 are fixed and verified:

```bash
cd appium_test

# Full auth regression
python -m pytest tests/suite_1_auth/ -v --tb=short 2>&1 | tee reports/auth_regression.log

# If all auth pass, run next suite
python -m pytest tests/suite_2_address/ -v --tb=short
python -m pytest tests/suite_3_catalog/ -v --tb=short
# Continue through all suites...

# Final: full regression
python -m pytest tests/ -v --tb=short 2>&1 | tee reports/full_regression.log
```

---

## HARD RULES

1. **NEVER run auth tests without verifying `adb shell curl http://<IP>:8080/api/health` returns 200**
2. **NEVER use `time.sleep()` for UI waits — use `WebDriverWait` with explicit conditions**
3. **ALWAYS capture logcat on test failure and save to `reports/`**
4. **ALWAYS take a screenshot on test failure and save to `reports/screenshots/`**
5. **NEVER fix multiple bugs in one commit**
6. **ALWAYS rebuild and reinstall APK after any Flutter code change**
7. **ALWAYS verify device reconnects after APK reinstall** (`adb devices`)
8. **On `sign_in_failed` ApiException: 10** — SHA-1 not registered in Firebase (rare, different from current issue)
9. **On `sign_in_failed` ApiException: 12500** — Google Play Services outdated on device
10. **On `SocketException errno=113`** — Backend not running or firewall blocking — START THE SERVER

---

## BACKEND STARTUP COMMANDS (try each until one works)

```bash
# Option 1: Node.js
cd backend && npm install && npm start

# Option 2: Gradle (Spring Boot)
cd backend && ./gradlew bootRun

# Option 3: Python (Django/FastAPI)
cd backend && pip install -r requirements.txt && python manage.py runserver 0.0.0.0:8080

# Option 4: Docker
docker-compose up -d

# Verify it started:
curl http://localhost:8080/api/health
```
