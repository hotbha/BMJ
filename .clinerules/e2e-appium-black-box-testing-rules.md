# BookMyJuice (BMJ) — Cline AI Rules

# Project: Appium Black-Box Testing via Wireless ADB

# Target: Android device connected over Wi-Fi ADB

---

## 🎯 MISSION

Your primary goal is to perform exhaustive Appium-based black-box testing of the BookMyJuice Flutter app running on a real Android device via wireless ADB. You must:

1. Identify and execute test cases with maximum screen/flow coverage
2. Detect bugs (crashes, UI glitches, wrong navigation, API failures)
3. Fix identified bugs directly in the source code
4. Re-run tests to verify fixes
5. Commit fixes with clear messages

---

## 📱 DEVICE & CONNECTION

- Connection: Wireless ADB (Wi-Fi)
- Verify device before every test run:

  ```bash
  adb devices
  ```

- If no device found, attempt reconnect:

  ```bash
  adb connect <DEVICE_IP>:5555
  ```

- Never assume the device is connected — always verify first
- Appium server must be running on localhost:4723 before any test execution
- Check Appium server status:

  ```bash
  curl http://localhost:4723/status
  ```

- If Appium is not running, start it:

  ```powershell
  Start-Process -NoNewWindow appium --address 127.0.0.1 --port 4723
  ```

---

## ⚙️ APPIUM CAPABILITIES (Flutter/Android)

Use these desired capabilities for all test sessions:

```python
desired_caps = {
    "platformName": "Android",
    "automationName": "UiAutomator2",
    "deviceName": "BMJ_Device",          # Will match any connected device
    "app": None,                          # App already installed
    "appPackage": "com.bookmyjuice.lush",
    "appActivity": ".MainActivity",
    "noReset": True,
    "fullReset": False,
    "newCommandTimeout": 120,
    "autoGrantPermissions": True,
    "unicodeKeyboard": True,
    "resetKeyboard": True,
    "adbExecTimeout": 20000,
    "uiautomator2ServerInstallTimeout": 60000,
    "androidInstallTimeout": 120000,
    "skipDeviceInitialization": False,
    "disableWindowAnimation": True,
}
```

---

## 🧪 TEST EXECUTION ORDER (Priority)

Always run tests in this exact order. Do NOT skip Auth before proceeding to downstream flows:

### ⚠️ IMPORTANT: Dashboard-First Navigation

The app starts on the **Dashboard** screen even for unauthenticated users. There is no standalone Splash or Login screen. To reach authentication screens, navigate:
```
Dashboard → Profile (bottom nav) → scroll to "Sign In" / "Sign Up" section
```

If the user is already authenticated, the Dashboard shows full content. Use the **"Public Mode"** indicators (e.g., limited catalog, "Sign In" prompt) to detect the unauthenticated state.

### PHASE 1 — Authentication (CRITICAL, fix before proceeding)

1. **TC-AUTH-001**: Launch app → Wait 4s for AutoLogin stabilisation → Verify Dashboard loads (public mode indicators visible)
2. **TC-AUTH-002**: Dashboard → Profile → Navigate to Sign Up → Fill valid details → Submit → Verify OTP screen or success
3. **TC-AUTH-003**: Sign Up with duplicate email → Verify error message shown
4. **TC-AUTH-004**: Sign Up with invalid phone → Verify inline validation
5. **TC-AUTH-005**: Sign Up with weak password → Verify strength error
6. **TC-AUTH-006**: Dashboard → Profile → Navigate to Sign In → Enter valid credentials → Submit → Verify home screen
7. **TC-AUTH-007**: Sign In with wrong password → Verify error toast/snackbar
8. **TC-AUTH-008**: Sign In with unregistered email → Verify error message
9. **TC-AUTH-009**: Forgot Password → Enter email → Verify reset flow initiated
10. **TC-AUTH-010**: Sign Out → Verify redirect to login screen

### PHASE 2 — Onboarding & Profile

11. TC-PROFILE-001: Complete profile setup post-signup
2. TC-PROFILE-002: Edit profile (name, address, phone)
3. TC-PROFILE-003: Upload profile picture

### PHASE 3 — Juice Catalog & Browse

14. TC-CATALOG-001: Home screen loads with juice categories
2. TC-CATALOG-002: Browse all categories
3. TC-CATALOG-003: View juice detail page (name, price, description, image)
4. TC-CATALOG-004: Search for a specific juice
5. TC-CATALOG-005: Filter juices by category/price
6. TC-CATALOG-006: Verify out-of-stock items are disabled

### PHASE 4 — Cart & Wishlist

20. TC-CART-001: Add item to cart from listing
2. TC-CART-002: Add item to cart from detail page
3. TC-CART-003: Increase/decrease item quantity in cart
4. TC-CART-004: Remove item from cart
5. TC-CART-005: Verify cart total calculation
6. TC-CART-006: Add to wishlist
7. TC-CART-007: Remove from wishlist

### PHASE 5 — Checkout & Payment

27. TC-CHECKOUT-001: Proceed to checkout from cart
2. TC-CHECKOUT-002: Select/add delivery address
3. TC-CHECKOUT-003: Select delivery time slot
4. TC-CHECKOUT-004: Apply valid promo code
5. TC-CHECKOUT-005: Apply invalid promo code → Verify error
6. TC-CHECKOUT-006: Select payment method (UPI/Card/COD)
7. TC-CHECKOUT-007: Place order → Verify order confirmation screen
8. TC-CHECKOUT-008: Verify order summary details are accurate

### PHASE 6 — Order History & Tracking

35. TC-ORDERS-001: View order history
2. TC-ORDERS-002: View order details
3. TC-ORDERS-003: Track active order status
4. TC-ORDERS-004: Cancel eligible order → Verify cancellation

### PHASE 7 — Subscriptions (if applicable)

39. TC-SUB-001: Browse subscription plans
2. TC-SUB-002: Subscribe to a plan
3. TC-SUB-003: Manage/cancel subscription

### PHASE 8 — Notifications & Settings

42. TC-NOTIF-001: Verify notification received on order placement
2. TC-SETTINGS-001: Change app language/preferences
3. TC-SETTINGS-002: Manage addresses
4. TC-SETTINGS-003: Change password

---

## 🔍 ELEMENT DISCOVERY STRATEGY

When an element cannot be found, use this priority order:

1. `resource-id` (most reliable for Flutter: `new UiSelector().resourceId(...)`)
2. `accessibility id` (content-desc)
3. `xpath` with text: `//android.widget.TextView[@text='Sign In']`
4. `class name` + index (last resort)

For Flutter apps, always try:

```python
driver.find_element(AppiumBy.ACCESSIBILITY_ID, "element_name")
```

If standard locators fail for Flutter, switch to **flutter_finder**:

```python
# Use flutter integration driver if available
driver.find_element("flutter", "ValueKey('signup_button')")
```

**Screenshot on every failure** — save to `appium_test/screenshots/` with timestamp + test name.

---

## 🐛 BUG IDENTIFICATION RULES

Log every issue found as follows and append to `appium_test/BUG_REPORT.md`:

```markdown
### BUG-[NNN]
- **Test Case**: TC-AUTH-002
- **Severity**: Critical / High / Medium / Low
- **Screen**: SignUpScreen
- **Steps to Reproduce**:
  1. Open app
  2. Tap Sign Up
  3. Enter valid details
  4. Tap Submit
- **Expected**: Navigate to OTP screen
- **Actual**: App crashes / Spinner hangs / Wrong screen shown
- **Error Log**: (paste Appium error or logcat snippet)
- **Status**: Open / Fixed
```

Severity classification:

- **Critical**: App crash, infinite spinner, cannot proceed
- **High**: Wrong navigation, data not saved, API error shown to user
- **Medium**: UI misalignment, wrong validation message
- **Low**: Typo, minor cosmetic issue

---

## 🔧 BUG FIXING RULES

After identifying a bug:

1. **Read the relevant source file** before making any change
2. **Make the minimal necessary fix** — do not refactor unrelated code
3. **Add a comment**: `// FIX: BUG-[NNN] - brief description`
4. **Re-run the specific test case** that failed to verify the fix
5. **Update BUG_REPORT.md** — mark status as `Fixed`
6. **Commit** with message format: `fix: BUG-[NNN] - <short description>`

Common Auth fixes to check first:

- Verify API base URL is correct in `.env` or config file
- Check if OTP/verification endpoint is reachable from the test device
- Ensure Firebase/Auth provider credentials are valid in environment
- Look for `async/await` issues in auth bloc/controller causing silent failures
- Check if form validators are preventing submission due to hidden errors

---

## ⏱️ WAIT STRATEGY

Never use `time.sleep()` — always use explicit waits:

```python
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

wait = WebDriverWait(driver, 20)
element = wait.until(EC.presence_of_element_located((AppiumBy.ACCESSIBILITY_ID, "home_screen")))
```

For animations/transitions (Flutter): wait up to **5 seconds** for screen settle before asserting.

---

## 📂 FILE & FOLDER CONVENTIONS

Always use **Page Object Model (POM)** — no raw locators in test files.

---

## 🚫 WHAT NOT TO DO

- Do NOT hardcode credentials in test files — use `utils/test_data.py`
- Do NOT run tests without verifying ADB device is connected
- Do NOT skip Auth tests even if they seem to pass visually
- Do NOT use `fullReset: True` unless explicitly testing fresh install flow
- Do NOT modify the Flutter source without reading the full file first
- Do NOT ignore Appium server logs — always check Appium output for error details
- Do NOT commit broken code — verify the fix passes before committing

---

## ⚠️ KNOWN LIMITATIONS

1. **Google OAuth Not Automatable**: Google Sign-In uses Google Play Services account picker which **cannot be automated** via Appium on real devices. Only email/password auth flows are covered in this test suite.
2. **Dashboard-First Architecture**: All test flows start from the Dashboard, not a Splash/Login screen. Account for this in test case step definitions.
3. **AutoLoginFailed Race Condition**: On cold app launch, add a **4-second stabilisation wait** before the first Appium interaction to avoid flaky failures from `AutoLoginFailed` firing before Appium settles.
4. **App Package Name**: The actual package is `com.bookmyjuice.lush` (not `com.bookmyjuice.app`). Ensure all ADB commands and capabilities use the correct value.

## ✅ DEFINITION OF DONE

A test run is considered complete when:

- [ ] All 45 test cases have been attempted
- [ ] All Critical and High bugs are fixed and re-verified
- [ ] `BUG_REPORT.md` is updated with final status of all bugs
- [ ] `TEST_RESULTS.md` contains pass/fail count with timestamps
- [ ] Screenshots of all failures are saved in `appium_test/screenshots/`
- [ ] All fixes are committed to the repo with proper commit messages

---

## 🔑 TEST CREDENTIALS (update before use)

```python
# utils/test_data.py
VALID_USER = {
    "email": "testuser@bookmyjuice.com",
    "password": "Test@12345",
    "phone": "9999999999",
    "name": "Test User"
}

NEW_USER = {
    "email": f"newuser_{int(time.time())}@test.com",
    "password": "New@12345",
    "phone": "8888888888",
    "name": "New Test User"
}
```

---

## 📋 SESSION STARTUP CHECKLIST

Before every Cline session, auto-verify:

1. `adb devices` → device listed and authorized
2. `curl http://localhost:4723/status` → Appium running
3. App is installed: `adb shell pm list packages | findstr bookmyjuice`
4. App is in foreground or launchable
5. Network connectivity on device: `adb shell ping -c 1 8.8.8.8`

## ⚠️ KNOWN BUG: GoogleSignIn Event Redirect (auth_bloc.dart)

During the audit of the `AuthenticationBloc`, a confirmed bug was found in the `GoogleSignIn` event handler:

- **Bug**: When an existing user signs in via Google, the BLoC emits `SignUpStarted` instead of completing the login flow. This causes the user to be redirected back to the Login screen rather than proceeding to the Dashboard.
- **Root Cause**: The `GoogleSignIn` event handler in `auth_bloc.dart` checks if the user exists in the backend; if the response is `signup_required` (used for both new users AND existing Google users who haven't linked their account), it emits `SignUpStarted`, sending the user into the signup flow instead of the login/success path.
- **Workaround**: Users should use **email/password login** instead of Google Sign-In. Until this bug is fixed, Google Sign-In is not a viable authentication path.
- **Status**: Open — authentication flow needs refactoring to distinguish between "new user signup" and "existing user linking Google account."
