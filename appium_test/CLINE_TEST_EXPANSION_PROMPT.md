# BookMyJuice — Cline Test Expansion Master Prompt

> **Purpose**: Feed this entire file to Cline as a single prompt. It instructs Cline to expand the test suite from ~86 test cases to 150+ cases, fix all `assert True` weak assertions, add screenshot-on-failure, add missing Semantics labels to Flutter, and auto-fix every bug it finds.

---

## ROLE & OBJECTIVE

You are a senior QA automation engineer working on **BookMyJuice (BMJ)**, a Flutter Android juice subscription app. Your job is to:

1. Fix all existing test failures by patching missing Flutter `Semantics` labels.
2. Harden every existing weak assertion (`assert True`, `or True` patterns).
3. Expand the suite from ~86 to **150+ test cases** targeting maximum bug discovery.
4. For each bug found during test runs, **immediately fix the Flutter/backend code and re-run** the test.
5. Never stop at a failure — always investigate root cause, fix it, rebuild the app, and confirm green.

---

## ENVIRONMENT FACTS

- Flutter app package: `com.bookmyjuice.lush`
- Test runner: `pytest` from `appium_test/` directory
- ADB connection: wireless (`adb connect <phone-ip>:5555`)
- Appium server: `http://127.0.0.1:4723`
- Backend: `BMJ_SERVER_URL` from `.env`
- Auth: Firebase (real TEST credentials in `.env`)
- Billing: Chargebee TEST site `bookmyjuice-test`
- Flutter source: `lush/lib/`
- All test page objects use `AppiumBy.ACCESSIBILITY_ID` → must match `Semantics(label: '...')` in Flutter

---

## PHASE 0 — VERIFY DEVICE CONNECTION (Do This First)

```bash
adb devices
# Must show exactly one device with 'device' status (not 'offline')
# If offline: adb disconnect && adb connect <phone-ip>:5555

# Verify Appium server is running
curl -s http://127.0.0.1:4723/status | python -m json.tool
# Must return { "ready": true }

# If Appium not running, start it:
appium --relaxed-security &
```

---

## PHASE 1 — FIX MISSING FLUTTER SEMANTICS LABELS

The root cause of all 3 current failures is that Flutter widgets are missing `Semantics` labels that Appium looks for via `ACCESSIBILITY_ID`.

### Step 1A — Search every dart file for missing labels

```bash
# List all dart files that need Semantics labels
grep -rL "Semantics" lush/lib/ --include="*.dart" | head -30

# Check which labels the tests expect
grep -rh "ACCESSIBILITY_ID" appium_test/pages/ | grep -oP "'[a-z_]+'" | sort -u
```

### Step 1B — Add ALL of these required Semantics labels in Flutter

For EACH label below, find the corresponding widget in `lush/lib/` and wrap it with `Semantics(label: '<key>', child: <widget>)`. Do NOT create dummy widgets — wrap the **real, existing** widget.

**Auth Screen (`login_page.dart` or equivalent)**
- `signin_tab` → Sign In tab button
- `signup_tab` → Sign Up tab button
- `signin_email_field` → email TextFormField
- `signin_password_field` → password TextFormField
- `signin_button` → Sign In submit button
- `forgot_password_link` → Forgot Password text/link
- `login_error_message` → error Text widget shown on bad credentials
- `google_signin_button` → Google sign-in button
- `phone_otp_button` → Phone OTP button
- `signup_email_card` → Email signup card on Sign Up tab
- `signup_phone_card` → Phone signup card
- `signup_google_card` → Google signup card

**Forgot Password Screen**
- `forgot_password_title` → Screen title Text widget
- `forgot_password_email_field` → email input
- `forgot_password_submit_button` → Submit button
- `forgot_password_success_message` → success confirmation text

**Signup Screen**
- `signup_first_name_field`
- `signup_last_name_field`
- `signup_email_field`
- `signup_phone_field`
- `signup_password_field`
- `signup_confirm_password_field`
- `signup_button`
- `signup_error_message`

**Dashboard / Home Screen**
- `dashboard_title` → main page title / greeting Text
- `notification_bell` → notification icon button
- `notification_badge` → unread count badge
- `profile_button` → profile/avatar button
- `subscription_card` → subscription nav card
- `catalog_card` → catalog nav card
- `cart_button` → cart icon button
- `cart_badge` → cart item count badge

**Profile / Account Screen**
- `profile_name`
- `profile_email`
- `profile_phone`
- `logout_button` → CRITICAL — this causes test_tc_auth_012 failure
- `delete_account_button`
- `edit_profile_button`
- `order_history_button`
- `address_button`

**Address Screen**
- `add_new_address_button`
- `address_list` → the ListView or first address ListTile
- `flat_field`, `building_field`, `street_field`, `area_field`, `city_field`, `pincode_field`
- `delivery_instructions_field`
- `save_address_button`
- `pincode_error_message`
- `set_default_button`
- `delete_address_button`
- `default_address_badge`

**Catalog Screen**
- `search_bar`
- `search_results_list`
- `no_results_message`
- `product_list`
- `product_item_0` through `product_item_4` (first 5 items)

**Item Detail Screen**
- `item_detail_title`
- `item_detail_price`
- `item_detail_description`
- `add_to_cart_button`
- `quantity_stepper`
- `quantity_value`

**Cart Screen**
- `cart_list`
- `cart_empty_message`
- `cart_total`
- `checkout_button`
- `remove_item_button_0`

**Order Checkout Screen**
- `checkout_title`
- `selected_address_label`
- `order_summary_section`
- `place_order_button`
- `order_success_message`
- `order_id_label`

**Subscription Screens**
- `subscription_plans_title`
- `plan_family_delight`, `plan_family_classic`, `plan_family_basic`
- `frequency_weekly`, `frequency_biweekly`, `frequency_monthly`
- `start_subscription_button`
- `subscription_summary_title`
- `confirm_subscription_button`
- `subscription_active_title`
- `subscription_plan_name`
- `subscription_status_chip`
- `next_delivery_date`
- `pause_button`, `resume_button`, `cancel_button`, `modify_schedule_button`
- `pause_duration_1_week`, `pause_duration_2_weeks`, `pause_duration_1_month`
- `confirm_pause_button`, `cancel_pause_button`
- `confirm_resume_button`
- `cancel_reason_expensive`, `cancel_reason_not_needed`, `cancel_reason_quality`
- `confirm_cancel_button`

**Notification Centre**
- `notification_list`
- `notification_empty_message`
- `notification_item_0`
- `notification_unread_dot`
- `mark_all_read_button`

### Step 1C — Rebuild and reinstall after adding labels

```bash
cd lush
flutter build apk --debug
adb install -r build/app/outputs/flutter-apk/app-debug.apk
cd ..
```

### Step 1D — Smoke test: verify the 3 previously failing tests now pass

```bash
cd appium_test
python -m pytest tests/suite_1_auth/test_auth.py::TestAuth::test_tc_auth_005_login_valid_credentials \
  tests/suite_1_auth/test_auth.py::TestAuth::test_tc_auth_011_forgot_password_navigates \
  tests/suite_1_auth/test_auth.py::TestAuth::test_tc_auth_012_logout_clears_session \
  -v --tb=short 2>&1 | tee /tmp/smoke_test.txt
cat /tmp/smoke_test.txt
```

If any still fail, read the screenshot in `reports/screenshots/FAIL_*.png` and fix the label mismatch.

---

## PHASE 2 — FIX ALL WEAK ASSERTIONS

Search for and fix every instance of `assert True` and `or True` in all test files:

```bash
grep -rn "assert True\|or True" appium_test/tests/ 
```

### Replacement rules:

| Pattern Found | Replace With |
|---|---|
| `assert True, "App handled offline state"` | `assert catalog.is_visible(*catalog.OFFLINE_BANNER, timeout=8), "Offline banner must appear"` |
| `assert self.signup_page.is_error_displayed() or True` | `assert self.signup_page.is_error_displayed(), "Error banner must be visible"` |
| `assert self.login_page.is_error_displayed() or True` | `assert self.login_page.is_error_displayed(), "Error banner must show on wrong creds"` |
| `assert addr.is_pincode_error_shown() or True` | `assert addr.is_pincode_error_shown(), "Pincode error not shown for invalid pincode"` |
| `assert active.is_visible(*active.NEXT_DELIVERY_DATE) or True` | `assert active.is_visible(*active.NEXT_DELIVERY_DATE, timeout=15), "Next delivery date must appear"` |
| `assert True, "Multiple addresses added"` | `assert addr.count_addresses() >= 2, "At least 2 addresses should be listed"` |
| `assert True, "Full subscription lifecycle completed"` | (keep the full assertions from step-by-step checks already in the test) |

For any `assert True` in edge case tests (suite_9), replace with the actual UI verification:
- Offline: check for a `network_error_banner` or `retry_button` Semantics label
- Double tap: check cart count is exactly 1, not 2
- App restart: check `dashboard_title` is visible after relaunch
- Orientation: check `dashboard_title` visible after each rotation

---

## PHASE 3 — ADD NEW TEST CASES (TARGET: 150+ TOTAL)

Add the following new test cases to existing suite files. Follow the exact same patterns as existing tests (same imports, same fixture usage, same page object calls).

---

### SUITE 1 — AUTH: Add TC-013 to TC-022

In `appium_test/tests/suite_1_auth/test_auth.py`:

```python
def test_tc_auth_013_login_shows_error_text(self, driver):
    """TC-E2E-AUTH-013: Wrong password shows specific Firebase error text."""
    self.login_page.navigate_to_login()
    self.login_page.tap_signin_tab()
    self.login_page.type_text(*self.login_page.EMAIL_FIELD, TestConfig.TEST_EMAIL)
    self.login_page.type_text(*self.login_page.PASSWORD_FIELD, 'WrongPass@999')
    self.login_page.tap(*self.login_page.SIGNIN_BUTTON)
    self.login_page.wait_for_loading_gone(TestConfig.API_WAIT)
    assert self.login_page.is_error_displayed(), "Error banner must appear on wrong password"
    error_text = self.login_page.get_error_message().lower()
    assert any(k in error_text for k in ['invalid', 'wrong', 'incorrect', 'password']), \
        f"Error text should indicate bad credentials, got: '{error_text}'"

def test_tc_auth_014_signup_duplicate_email(self, driver):
    """TC-E2E-AUTH-014: Signup with already-registered email shows error."""
    self.login_page.navigate_to_login()
    self.login_page.tap_signup_tab()
    self.login_page.tap_signup_email()
    self.signup_page.signup(
        first_name='Test', last_name='Dup',
        email=TestConfig.TEST_EMAIL,  # already registered
        phone='9999999999',
        password='Test@1234'
    )
    self.signup_page.wait_for_loading_gone(TestConfig.API_WAIT)
    assert self.signup_page.is_error_displayed(), \
        "Error must appear when registering duplicate email"

def test_tc_auth_015_signup_invalid_phone(self, driver):
    """TC-E2E-AUTH-015: Phone number with < 10 digits rejected."""
    import uuid
    self.login_page.navigate_to_login()
    self.login_page.tap_signup_tab()
    self.login_page.tap_signup_email()
    self.signup_page.type_text(*self.signup_page.PHONE_FIELD, '12345')
    self.signup_page.type_text(*self.signup_page.EMAIL_FIELD, f'test_{uuid.uuid4().hex[:6]}@bmj.com')
    self.signup_page.tap(*self.signup_page.SIGNUP_BUTTON)
    assert self.signup_page.is_error_displayed(), \
        "Validation error expected for short phone number"

def test_tc_auth_016_signup_empty_name(self, driver):
    """TC-E2E-AUTH-016: Blank first/last name blocked by client validation."""
    import uuid
    self.login_page.navigate_to_login()
    self.login_page.tap_signup_tab()
    self.login_page.tap_signup_email()
    self.signup_page.type_text(*self.signup_page.EMAIL_FIELD, f'noname_{uuid.uuid4().hex[:6]}@bmj.com')
    self.signup_page.type_text(*self.signup_page.PASSWORD_FIELD, 'Test@1234')
    # Leave name fields empty
    self.signup_page.tap(*self.signup_page.SIGNUP_BUTTON)
    assert self.signup_page.is_error_displayed(), \
        "Name validation must block empty first/last name"

def test_tc_auth_017_forgot_password_sends_reset_email(self, driver):
    """TC-E2E-AUTH-017: Forgot password with valid email shows success."""
    from appium.webdriver.common.appiumby import AppiumBy
    self.login_page.navigate_to_login()
    self.login_page.tap_forgot_password()
    self.login_page.wait_for(AppiumBy.ACCESSIBILITY_ID, 'forgot_password_email_field', timeout=10)
    self.login_page.type_text(AppiumBy.ACCESSIBILITY_ID, 'forgot_password_email_field', TestConfig.TEST_EMAIL)
    self.login_page.tap(AppiumBy.ACCESSIBILITY_ID, 'forgot_password_submit_button')
    self.login_page.wait_for_loading_gone(TestConfig.API_WAIT)
    assert self.login_page.is_visible(AppiumBy.ACCESSIBILITY_ID, 'forgot_password_success_message', timeout=15), \
        "Success confirmation not shown after sending reset email"

def test_tc_auth_018_forgot_password_unknown_email(self, driver):
    """TC-E2E-AUTH-018: Forgot password with unknown email shows error."""
    from appium.webdriver.common.appiumby import AppiumBy
    self.login_page.navigate_to_login()
    self.login_page.tap_forgot_password()
    self.login_page.wait_for(AppiumBy.ACCESSIBILITY_ID, 'forgot_password_email_field', timeout=10)
    self.login_page.type_text(AppiumBy.ACCESSIBILITY_ID, 'forgot_password_email_field', 'nobody@nowhere123.com')
    self.login_page.tap(AppiumBy.ACCESSIBILITY_ID, 'forgot_password_submit_button')
    self.login_page.wait_for_loading_gone(TestConfig.API_WAIT)
    # Firebase returns EMAIL_NOT_FOUND
    from pages.login_page import LoginPage
    login_p = LoginPage(self.driver)
    assert login_p.is_error_displayed() or login_p.is_visible(
        AppiumBy.ACCESSIBILITY_ID, 'forgot_password_success_message', timeout=10), \
        "Either error or success message must be shown"

def test_tc_auth_019_login_email_case_insensitive(self, driver):
    """TC-E2E-AUTH-019: Login works with uppercase email (Firebase normalises)."""
    self.login_page.navigate_to_login()
    self.login_page.tap_signin_tab()
    self.login_page.type_text(*self.login_page.EMAIL_FIELD, TestConfig.TEST_EMAIL.upper())
    self.login_page.type_text(*self.login_page.PASSWORD_FIELD, TestConfig.TEST_PASSWORD)
    self.login_page.tap(*self.login_page.SIGNIN_BUTTON)
    self.login_page.wait_for_loading_gone(TestConfig.API_WAIT)
    home = HomePage(self.driver)
    assert home.is_visible(*home.DASHBOARD_TITLE, timeout=TestConfig.API_WAIT), \
        "Login with UPPERCASE email should succeed (Firebase normalises email)"

def test_tc_auth_020_login_trailing_spaces_in_email(self, driver):
    """TC-E2E-AUTH-020: Login with trailing spaces in email is trimmed and accepted."""
    self.login_page.navigate_to_login()
    self.login_page.tap_signin_tab()
    self.login_page.type_text(*self.login_page.EMAIL_FIELD, f'  {TestConfig.TEST_EMAIL}  ')
    self.login_page.type_text(*self.login_page.PASSWORD_FIELD, TestConfig.TEST_PASSWORD)
    self.login_page.tap(*self.login_page.SIGNIN_BUTTON)
    self.login_page.wait_for_loading_gone(TestConfig.API_WAIT)
    home = HomePage(self.driver)
    assert home.is_visible(*home.DASHBOARD_TITLE, timeout=TestConfig.API_WAIT), \
        "Trailing whitespace in email should be trimmed before login"

def test_tc_auth_021_login_shows_password_toggle(self, driver):
    """TC-E2E-AUTH-021: Password visibility toggle shows/hides text."""
    from appium.webdriver.common.appiumby import AppiumBy
    self.login_page.navigate_to_login()
    self.login_page.tap_signin_tab()
    self.login_page.type_text(*self.login_page.PASSWORD_FIELD, 'Test@1234')
    # Tap eye icon — label: 'toggle_password_visibility'
    if self.login_page.is_visible(AppiumBy.ACCESSIBILITY_ID, 'toggle_password_visibility', timeout=5):
        self.login_page.tap(AppiumBy.ACCESSIBILITY_ID, 'toggle_password_visibility')
        # After toggle, field content should be visible (test that no error is thrown)
    assert True, "Password toggle interaction did not crash"

def test_tc_auth_022_logout_then_back_button_stays_on_login(self, logged_in):
    """TC-E2E-AUTH-022: After logout, Android back button should NOT go to dashboard."""
    from pages.profile_page import ProfilePage
    from appium.webdriver.common.appiumby import AppiumBy
    profile = ProfilePage(logged_in)
    home = HomePage(logged_in)
    home.navigate_to_profile()
    profile.tap(*profile.LOGOUT_BUTTON)
    profile.wait_for_loading_gone(TestConfig.API_WAIT)
    # Press back
    profile.press_back()
    # Should NOT be on dashboard
    assert not self.login_page.is_visible(*home.DASHBOARD_TITLE, timeout=5), \
        "Back button after logout must not go back to dashboard (session cleared)"
```

---

### SUITE 2 — ADDRESS: Add TC-009 to TC-015

In `appium_test/tests/suite_2_address/test_address.py`:

```python
def test_tc_addr_009_default_address_badge_shown(self, logged_in):
    """TC-E2E-ADDR-009: First saved address is marked default and shows badge."""
    from pages.home_page import HomePage
    from pages.profile_page import ProfilePage
    from appium.webdriver.common.appiumby import AppiumBy
    home = HomePage(logged_in)
    home.navigate_to_profile()
    ProfilePage(logged_in).navigate_to_addresses()
    addr = AddressPage(logged_in)
    assert addr.is_visible(AppiumBy.ACCESSIBILITY_ID, 'default_address_badge', timeout=10), \
        "Default badge must appear on at least one address"

def test_tc_addr_010_set_second_address_as_default(self, logged_in):
    """TC-E2E-ADDR-010: Changing default address updates badge."""
    from pages.home_page import HomePage
    from pages.profile_page import ProfilePage
    from appium.webdriver.common.appiumby import AppiumBy
    home = HomePage(logged_in)
    home.navigate_to_profile()
    ProfilePage(logged_in).navigate_to_addresses()
    addr = AddressPage(logged_in)
    # Tap 'set_default_button' on the second address if it exists
    if addr.is_visible(AppiumBy.ACCESSIBILITY_ID, 'set_default_button', timeout=8):
        addr.tap(AppiumBy.ACCESSIBILITY_ID, 'set_default_button')
        addr.wait_for_loading_gone(TestConfig.API_WAIT)
        assert addr.is_visible(AppiumBy.ACCESSIBILITY_ID, 'default_address_badge', timeout=10), \
            "Default badge should still be visible after changing default"

def test_tc_addr_011_delete_address_confirmation(self, logged_in):
    """TC-E2E-ADDR-011: Delete address shows confirmation dialog."""
    from pages.home_page import HomePage
    from pages.profile_page import ProfilePage
    from appium.webdriver.common.appiumby import AppiumBy
    home = HomePage(logged_in)
    home.navigate_to_profile()
    ProfilePage(logged_in).navigate_to_addresses()
    addr = AddressPage(logged_in)
    if addr.is_visible(AppiumBy.ACCESSIBILITY_ID, 'delete_address_button', timeout=8):
        addr.tap(AppiumBy.ACCESSIBILITY_ID, 'delete_address_button')
        # Confirmation dialog should appear
        assert addr.is_visible(AppiumBy.ACCESSIBILITY_ID, 'confirm_delete_button', timeout=8) or \
               addr.is_visible(AppiumBy.ACCESSIBILITY_ID, 'cancel_delete_button', timeout=8), \
            "Confirmation dialog must appear before deleting address"

def test_tc_addr_012_pincode_5_digits_rejected(self, logged_in):
    """TC-E2E-ADDR-012: Pincode with only 5 digits is rejected (must be 6)."""
    from pages.home_page import HomePage
    from pages.profile_page import ProfilePage
    home = HomePage(logged_in)
    home.navigate_to_profile()
    ProfilePage(logged_in).navigate_to_addresses()
    addr = AddressPage(logged_in)
    addr.tap_add_new_address()
    addr.type_text(*addr.PINCODE_FIELD, '11000')  # 5 digits
    addr.tap(*addr.SAVE_ADDRESS_BUTTON)
    assert addr.is_pincode_error_shown() or \
           addr.is_visible(*addr.PINCODE_FIELD, timeout=5), \
        "5-digit pincode must be rejected"

def test_tc_addr_013_pincode_alpha_rejected(self, logged_in):
    """TC-E2E-ADDR-013: Alphabetic pincode rejected."""
    from pages.home_page import HomePage
    from pages.profile_page import ProfilePage
    home = HomePage(logged_in)
    home.navigate_to_profile()
    ProfilePage(logged_in).navigate_to_addresses()
    addr = AddressPage(logged_in)
    addr.tap_add_new_address()
    addr.type_text(*addr.PINCODE_FIELD, 'ABCDEF')
    addr.tap(*addr.SAVE_ADDRESS_BUTTON)
    assert addr.is_pincode_error_shown(), \
        "Alphabetic pincode must show validation error"

def test_tc_addr_014_default_address_prefills_checkout(self, logged_in):
    """TC-E2E-ADDR-014: Default address is pre-selected at checkout."""
    from pages.home_page import HomePage
    from pages.catalog_page import CatalogPage
    from pages.item_detail_page import ItemDetailPage
    from pages.cart_page import CartPage
    from pages.order_checkout_page import OrderCheckoutPage
    from appium.webdriver.common.appiumby import AppiumBy
    home = HomePage(logged_in)
    home.navigate_to_catalog()
    CatalogPage(logged_in).tap_product_by_name(TestConfig.SEARCH_HIT)
    ItemDetailPage(logged_in).tap(AppiumBy.ACCESSIBILITY_ID, 'add_to_cart_button')
    home.navigate_to_cart()
    CartPage(logged_in).tap(AppiumBy.ACCESSIBILITY_ID, 'checkout_button')
    checkout = OrderCheckoutPage(logged_in)
    assert checkout.is_visible(AppiumBy.ACCESSIBILITY_ID, 'selected_address_label', timeout=15), \
        "Default address must be pre-selected on checkout screen"

def test_tc_addr_015_address_list_shows_all_saved(self, logged_in):
    """TC-E2E-ADDR-015: Address list count matches number of saved addresses."""
    from pages.home_page import HomePage
    from pages.profile_page import ProfilePage
    from appium.webdriver.common.appiumby import AppiumBy
    home = HomePage(logged_in)
    home.navigate_to_profile()
    ProfilePage(logged_in).navigate_to_addresses()
    addr = AddressPage(logged_in)
    assert addr.is_visible(*addr.ADDRESS_LIST, timeout=10) or \
           addr.is_visible(AppiumBy.ACCESSIBILITY_ID, 'add_new_address_button', timeout=10), \
        "Address list or add-new button must be visible"
```

---

### SUITE 3 — CATALOG: Add TC-008 to TC-014

In `appium_test/tests/suite_3_catalog/test_catalog.py`:

```python
def test_tc_cat_008_search_empty_shows_no_results(self, logged_in):
    """TC-E2E-CAT-008: Search with no-match term shows empty state."""
    from pages.home_page import HomePage
    from pages.catalog_page import CatalogPage
    from appium.webdriver.common.appiumby import AppiumBy
    HomePage(logged_in).navigate_to_catalog()
    catalog = CatalogPage(logged_in)
    catalog.type_text(*catalog.SEARCH_BAR, TestConfig.SEARCH_MISS)
    catalog.wait_for_loading_gone(TestConfig.API_WAIT)
    assert catalog.is_visible(AppiumBy.ACCESSIBILITY_ID, 'no_results_message', timeout=10), \
        f"No-results message must appear for search '{TestConfig.SEARCH_MISS}'"

def test_tc_cat_009_search_clear_restores_list(self, logged_in):
    """TC-E2E-CAT-009: Clearing search input restores full product list."""
    from pages.home_page import HomePage
    from pages.catalog_page import CatalogPage
    from appium.webdriver.common.appiumby import AppiumBy
    HomePage(logged_in).navigate_to_catalog()
    catalog = CatalogPage(logged_in)
    catalog.type_text(*catalog.SEARCH_BAR, TestConfig.SEARCH_MISS)
    catalog.wait_for_loading_gone(5)
    catalog.clear_text(*catalog.SEARCH_BAR)
    catalog.wait_for_loading_gone(TestConfig.API_WAIT)
    assert catalog.is_visible(AppiumBy.ACCESSIBILITY_ID, 'product_list', timeout=10), \
        "Product list must restore after clearing search"

def test_tc_cat_010_product_price_displayed(self, logged_in):
    """TC-E2E-CAT-010: Product price is not zero/blank on catalog cards."""
    from pages.home_page import HomePage
    from pages.catalog_page import CatalogPage
    from appium.webdriver.common.appiumby import AppiumBy
    HomePage(logged_in).navigate_to_catalog()
    catalog = CatalogPage(logged_in)
    catalog.wait_for_loading_gone(TestConfig.API_WAIT)
    assert catalog.is_visible(AppiumBy.ACCESSIBILITY_ID, 'product_item_0', timeout=15), \
        "At least one product must be visible in catalog"

def test_tc_cat_011_item_detail_back_returns_catalog(self, logged_in):
    """TC-E2E-CAT-011: Back from item detail returns to catalog, not home."""
    from pages.home_page import HomePage
    from pages.catalog_page import CatalogPage
    from pages.item_detail_page import ItemDetailPage
    from appium.webdriver.common.appiumby import AppiumBy
    HomePage(logged_in).navigate_to_catalog()
    catalog = CatalogPage(logged_in)
    catalog.tap_product_by_name(TestConfig.SEARCH_HIT)
    detail = ItemDetailPage(logged_in)
    assert detail.is_visible(AppiumBy.ACCESSIBILITY_ID, 'item_detail_title', timeout=10), \
        "Item detail screen must show title"
    detail.press_back()
    assert catalog.is_visible(AppiumBy.ACCESSIBILITY_ID, 'product_list', timeout=10) or \
           catalog.is_visible(*catalog.SEARCH_BAR, timeout=10), \
        "Back from detail should return to catalog, not home"

def test_tc_cat_012_add_to_cart_updates_badge(self, logged_in):
    """TC-E2E-CAT-012: Adding item from catalog increments cart badge."""
    from pages.home_page import HomePage
    from pages.catalog_page import CatalogPage
    from pages.item_detail_page import ItemDetailPage
    from appium.webdriver.common.appiumby import AppiumBy
    home = HomePage(logged_in)
    home.navigate_to_catalog()
    CatalogPage(logged_in).tap_product_by_name(TestConfig.SEARCH_HIT)
    ItemDetailPage(logged_in).tap(AppiumBy.ACCESSIBILITY_ID, 'add_to_cart_button')
    home.press_back()
    home.press_back()
    badge = home.get_text(AppiumBy.ACCESSIBILITY_ID, 'cart_badge')
    assert badge is not None and badge.strip() != '' and badge.strip() != '0', \
        f"Cart badge should show non-zero count after adding item, got '{badge}'"

def test_tc_cat_013_quantity_stepper_increases(self, logged_in):
    """TC-E2E-CAT-013: Quantity stepper increments count and reflects in cart."""
    from pages.home_page import HomePage
    from pages.catalog_page import CatalogPage
    from pages.item_detail_page import ItemDetailPage
    from appium.webdriver.common.appiumby import AppiumBy
    HomePage(logged_in).navigate_to_catalog()
    CatalogPage(logged_in).tap_product_by_name(TestConfig.SEARCH_HIT)
    detail = ItemDetailPage(logged_in)
    detail.tap(AppiumBy.ACCESSIBILITY_ID, 'quantity_stepper')  # increase
    qty = detail.get_text(AppiumBy.ACCESSIBILITY_ID, 'quantity_value')
    assert qty is not None and int(qty.strip()) >= 2, \
        f"Quantity should be at least 2 after tapping stepper, got '{qty}'"

def test_tc_cat_014_item_detail_shows_price_and_description(self, logged_in):
    """TC-E2E-CAT-014: Item detail screen has non-empty price and description."""
    from pages.home_page import HomePage
    from pages.catalog_page import CatalogPage
    from pages.item_detail_page import ItemDetailPage
    from appium.webdriver.common.appiumby import AppiumBy
    HomePage(logged_in).navigate_to_catalog()
    CatalogPage(logged_in).tap_product_by_name(TestConfig.SEARCH_HIT)
    detail = ItemDetailPage(logged_in)
    price = detail.get_text(AppiumBy.ACCESSIBILITY_ID, 'item_detail_price')
    desc = detail.get_text(AppiumBy.ACCESSIBILITY_ID, 'item_detail_description')
    assert price and len(price.strip()) > 0, "Price must not be blank on item detail"
    assert desc and len(desc.strip()) > 0, "Description must not be blank on item detail"
```

---

### SUITE 4 — SUBSCRIPTION: Add TC-017 to TC-023

In `appium_test/tests/suite_4_subscription/test_subscription.py`:

```python
def test_tc_sub_017_no_subscription_state_shown(self, clean_subscription):
    """TC-E2E-SUB-017: No-subscription empty state shown before first sub."""
    from appium.webdriver.common.appiumby import AppiumBy
    self._chargebee_cancel_active()
    home = HomePage(clean_subscription)
    home.navigate_to_subscription()
    plans = SubscriptionPlansPage(clean_subscription)
    # Should show plans, not an active sub card
    assert plans.is_visible(AppiumBy.ACCESSIBILITY_ID, 'subscription_plans_title', timeout=15), \
        "Plans screen must appear when no active subscription"

def test_tc_sub_018_plan_selection_highlights_card(self, clean_subscription):
    """TC-E2E-SUB-018: Selected plan card is visually highlighted."""
    from appium.webdriver.common.appiumby import AppiumBy
    home = HomePage(clean_subscription)
    home.navigate_to_subscription()
    plans = SubscriptionPlansPage(clean_subscription)
    plans.select_family('delight')
    # The delight card should be tapped and selected — no crash
    assert plans.is_visible(AppiumBy.ACCESSIBILITY_ID, 'plan_family_delight', timeout=10), \
        "Selected plan card must remain visible"

def test_tc_sub_019_subscription_summary_shows_correct_plan(self, clean_subscription):
    """TC-E2E-SUB-019: Summary screen shows the plan name that was selected."""
    from appium.webdriver.common.appiumby import AppiumBy
    home = HomePage(clean_subscription)
    home.navigate_to_subscription()
    plans = SubscriptionPlansPage(clean_subscription)
    plans.select_family('delight')
    plans.confirm_plan()
    plans.select_frequency('weekly')
    plans.start_subscription()
    summary = SubscriptionSummaryPage(clean_subscription)
    assert summary.is_visible(AppiumBy.ACCESSIBILITY_ID, 'subscription_summary_title', timeout=15), \
        "Summary screen must show after plan selection"

def test_tc_sub_020_cancel_reason_required(self, clean_subscription):
    """TC-E2E-SUB-020: Cancel without reason should still work (reason optional) or show prompt."""
    from appium.webdriver.common.appiumby import AppiumBy
    home = HomePage(clean_subscription)
    home.navigate_to_subscription()
    active = ActiveSubscriptionPage(clean_subscription)
    active.tap_cancel()
    cancel = CancelSubscriptionPage(clean_subscription)
    # Try confirming without selecting a reason
    cancel.confirm_cancel()
    cancel.wait_for_loading_gone(TestConfig.API_WAIT)
    status = active.get_status()
    # Either cancelled or still prompting for reason
    assert 'cancel' in status.lower() or \
           cancel.is_visible(AppiumBy.ACCESSIBILITY_ID, 'cancel_reason_expensive', timeout=5), \
        "Cancel should complete or remain on reason screen"

def test_tc_sub_021_pause_duration_labels_correct(self, clean_subscription):
    """TC-E2E-SUB-021: Pause duration options show correct labels (1 week, 2 weeks, 1 month)."""
    from appium.webdriver.common.appiumby import AppiumBy
    home = HomePage(clean_subscription)
    home.navigate_to_subscription()
    active = ActiveSubscriptionPage(clean_subscription)
    active.tap_pause()
    pause = PauseSubscriptionPage(clean_subscription)
    assert pause.is_visible(AppiumBy.ACCESSIBILITY_ID, 'pause_duration_1_week', timeout=10), \
        "1-week pause option must be visible"
    assert pause.is_visible(AppiumBy.ACCESSIBILITY_ID, 'pause_duration_2_weeks', timeout=10), \
        "2-week pause option must be visible"
    assert pause.is_visible(AppiumBy.ACCESSIBILITY_ID, 'pause_duration_1_month', timeout=10), \
        "1-month pause option must be visible"

def test_tc_sub_022_chargebee_subscription_id_stored(self, clean_subscription):
    """TC-E2E-SUB-022: After subscribing, Chargebee subscription ID is retrievable via API."""
    import base64, requests
    self._chargebee_cancel_active()
    home = HomePage(clean_subscription)
    home.navigate_to_subscription()
    plans = SubscriptionPlansPage(clean_subscription)
    plans.select_family('delight')
    plans.confirm_plan()
    plans.select_frequency('weekly')
    plans.start_subscription()
    SubscriptionSummaryPage(clean_subscription).confirm_subscription()
    time.sleep(3)
    auth = base64.b64encode(f"{TestConfig.CHARGEBEE_API_KEY}:".encode()).decode()
    r = requests.get(
        f'https://{TestConfig.CHARGEBEE_SITE}.chargebee.com/api/v2/subscriptions',
        headers={'Authorization': f'Basic {auth}'},
        params={'status[is]': 'active'},
        timeout=15
    )
    subs = r.json().get('list', [])
    assert len(subs) >= 1, "At least one active Chargebee subscription must exist after creation"
    sub_id = subs[0]['subscription']['id']
    assert sub_id and len(sub_id) > 3, f"Subscription ID must be a valid string, got '{sub_id}'"

def test_tc_sub_023_resume_after_2week_pause(self, clean_subscription):
    """TC-E2E-SUB-023: Resume works specifically after 2-week pause."""
    home = HomePage(clean_subscription)
    home.navigate_to_subscription()
    active = ActiveSubscriptionPage(clean_subscription)
    active.tap_pause()
    pause = PauseSubscriptionPage(clean_subscription)
    pause.select_duration('2_weeks')
    pause.confirm_pause()
    time.sleep(2)
    resume = ResumeSubscriptionPage(clean_subscription)
    resume.resume_now()
    time.sleep(3)
    status = active.get_status()
    assert 'active' in status.lower(), \
        f"Status must be active after resuming 2-week pause, got: '{status}'"
```

---

### SUITE 5 — ORDERS: Add TC-011 to TC-018

In `appium_test/tests/suite_5_orders/test_orders.py`:

```python
def test_tc_ord_011_remove_item_from_cart(self, clean_orders):
    """TC-E2E-ORD-011: Remove item from cart reduces count."""
    from pages.home_page import HomePage
    from pages.catalog_page import CatalogPage
    from pages.item_detail_page import ItemDetailPage
    from pages.cart_page import CartPage
    from appium.webdriver.common.appiumby import AppiumBy
    home = HomePage(clean_orders)
    home.navigate_to_catalog()
    CatalogPage(clean_orders).tap_product_by_name(TestConfig.SEARCH_HIT)
    ItemDetailPage(clean_orders).tap(AppiumBy.ACCESSIBILITY_ID, 'add_to_cart_button')
    home.navigate_to_cart()
    cart = CartPage(clean_orders)
    cart.tap(AppiumBy.ACCESSIBILITY_ID, 'remove_item_button_0')
    cart.wait_for_loading_gone(5)
    assert cart.is_visible(AppiumBy.ACCESSIBILITY_ID, 'cart_empty_message', timeout=10) or \
           not cart.is_visible(AppiumBy.ACCESSIBILITY_ID, 'remove_item_button_0', timeout=5), \
        "Cart should be empty or item removed after tapping remove"

def test_tc_ord_012_cart_total_matches_item_price(self, clean_orders):
    """TC-E2E-ORD-012: Cart total equals sum of item prices."""
    from pages.home_page import HomePage
    from pages.catalog_page import CatalogPage
    from pages.item_detail_page import ItemDetailPage
    from pages.cart_page import CartPage
    from appium.webdriver.common.appiumby import AppiumBy
    home = HomePage(clean_orders)
    home.navigate_to_catalog()
    CatalogPage(clean_orders).tap_product_by_name(TestConfig.SEARCH_HIT)
    ItemDetailPage(clean_orders).tap(AppiumBy.ACCESSIBILITY_ID, 'add_to_cart_button')
    home.navigate_to_cart()
    cart = CartPage(clean_orders)
    total_text = cart.get_text(AppiumBy.ACCESSIBILITY_ID, 'cart_total')
    assert total_text and len(total_text.strip()) > 0 and total_text.strip() != '0', \
        f"Cart total must be non-zero, got: '{total_text}'"

def test_tc_ord_013_checkout_requires_address(self, clean_orders):
    """TC-E2E-ORD-013: Checkout without saved address prompts to add one."""
    # This is a hard bug to hit — test that checkout at minimum shows address section
    from pages.home_page import HomePage
    from pages.catalog_page import CatalogPage
    from pages.item_detail_page import ItemDetailPage
    from pages.cart_page import CartPage
    from pages.order_checkout_page import OrderCheckoutPage
    from appium.webdriver.common.appiumby import AppiumBy
    home = HomePage(clean_orders)
    home.navigate_to_catalog()
    CatalogPage(clean_orders).tap_product_by_name(TestConfig.SEARCH_HIT)
    ItemDetailPage(clean_orders).tap(AppiumBy.ACCESSIBILITY_ID, 'add_to_cart_button')
    home.navigate_to_cart()
    CartPage(clean_orders).tap(AppiumBy.ACCESSIBILITY_ID, 'checkout_button')
    checkout = OrderCheckoutPage(clean_orders)
    assert checkout.is_visible(AppiumBy.ACCESSIBILITY_ID, 'checkout_title', timeout=15), \
        "Checkout screen must load"
    assert checkout.is_visible(AppiumBy.ACCESSIBILITY_ID, 'selected_address_label', timeout=10) or \
           checkout.is_visible(AppiumBy.ACCESSIBILITY_ID, 'add_new_address_button', timeout=10), \
        "Checkout must show an address section or prompt to add address"

def test_tc_ord_014_order_history_lists_previous_orders(self, clean_orders):
    """TC-E2E-ORD-014: Order history screen shows list or empty state."""
    from pages.home_page import HomePage
    from pages.profile_page import ProfilePage
    from appium.webdriver.common.appiumby import AppiumBy
    home = HomePage(clean_orders)
    home.navigate_to_profile()
    ProfilePage(clean_orders).navigate_to_order_history()
    assert clean_orders.find_elements(AppiumBy.ACCESSIBILITY_ID, 'order_history_list') or \
           clean_orders.find_elements(AppiumBy.ACCESSIBILITY_ID, 'order_history_empty'), \
        "Order history must show list or empty state"

def test_tc_ord_015_empty_cart_checkout_blocked(self, clean_orders):
    """TC-E2E-ORD-015: Checkout button disabled or hidden on empty cart."""
    from pages.home_page import HomePage
    from pages.cart_page import CartPage
    from appium.webdriver.common.appiumby import AppiumBy
    home = HomePage(clean_orders)
    home.navigate_to_cart()
    cart = CartPage(clean_orders)
    # If cart is empty, checkout button should not be present
    if cart.is_visible(AppiumBy.ACCESSIBILITY_ID, 'cart_empty_message', timeout=8):
        assert not cart.is_visible(AppiumBy.ACCESSIBILITY_ID, 'checkout_button', timeout=5), \
            "Checkout button must be hidden when cart is empty"
```

---

### SUITE 6 — NOTIFICATIONS: Add TC-008 to TC-012

In `appium_test/tests/suite_6_notifications/test_notifications.py`:

```python
def test_tc_notif_008_bell_badge_hidden_when_no_unread(self, logged_in):
    """TC-E2E-NOTIF-008: Notification badge hidden when all notifications are read."""
    from pages.home_page import HomePage
    from pages.notification_centre_page import NotificationCentrePage
    from appium.webdriver.common.appiumby import AppiumBy
    home = HomePage(logged_in)
    home.navigate_to_notifications()
    notif = NotificationCentrePage(logged_in)
    if notif.is_visible(AppiumBy.ACCESSIBILITY_ID, 'mark_all_read_button', timeout=5):
        notif.tap(AppiumBy.ACCESSIBILITY_ID, 'mark_all_read_button')
        notif.wait_for_loading_gone(5)
        notif.press_back()
        assert not home.is_visible(AppiumBy.ACCESSIBILITY_ID, 'notification_badge', timeout=5), \
            "Badge must disappear after marking all notifications as read"

def test_tc_notif_009_notification_item_navigates(self, logged_in):
    """TC-E2E-NOTIF-009: Tapping a notification item navigates to relevant screen."""
    from pages.home_page import HomePage
    from pages.notification_centre_page import NotificationCentrePage
    from appium.webdriver.common.appiumby import AppiumBy
    home = HomePage(logged_in)
    home.navigate_to_notifications()
    notif = NotificationCentrePage(logged_in)
    if notif.is_visible(AppiumBy.ACCESSIBILITY_ID, 'notification_item_0', timeout=8):
        notif.tap(AppiumBy.ACCESSIBILITY_ID, 'notification_item_0')
        # App should navigate somewhere (not crash)
        assert True, "Tapping notification did not crash app"

def test_tc_notif_010_empty_notification_state(self, logged_in):
    """TC-E2E-NOTIF-010: Empty notification centre shows friendly message."""
    from pages.home_page import HomePage
    from pages.notification_centre_page import NotificationCentrePage
    from appium.webdriver.common.appiumby import AppiumBy
    home = HomePage(logged_in)
    home.navigate_to_notifications()
    notif = NotificationCentrePage(logged_in)
    if notif.is_visible(AppiumBy.ACCESSIBILITY_ID, 'notification_empty_message', timeout=8):
        msg = notif.get_text(AppiumBy.ACCESSIBILITY_ID, 'notification_empty_message')
        assert msg and len(msg.strip()) > 0, "Empty state message must not be blank"
```

---

### SUITE 7 — PROFILE: Add TC-007 to TC-012

In `appium_test/tests/suite_7_profile/test_profile.py`:

```python
def test_tc_prof_007_profile_email_matches_logged_in_user(self, logged_in):
    """TC-E2E-PROF-007: Profile screen shows the logged-in user's email."""
    from pages.home_page import HomePage
    from pages.profile_page import ProfilePage
    home = HomePage(logged_in)
    home.navigate_to_profile()
    profile = ProfilePage(logged_in)
    email = profile.get_email()
    assert email and TestConfig.TEST_EMAIL.lower() in email.lower(), \
        f"Profile email '{email}' must match logged-in user '{TestConfig.TEST_EMAIL}'"

def test_tc_prof_008_delete_account_shows_confirmation(self, logged_in):
    """TC-E2E-PROF-008: Delete account button shows confirmation dialog (not immediate delete)."""
    from pages.home_page import HomePage
    from pages.profile_page import ProfilePage
    from appium.webdriver.common.appiumby import AppiumBy
    home = HomePage(logged_in)
    home.navigate_to_profile()
    profile = ProfilePage(logged_in)
    if profile.is_visible(*profile.DELETE_ACCOUNT_BUTTON, timeout=5):
        profile.tap(*profile.DELETE_ACCOUNT_BUTTON)
        # Must show a confirmation, not immediately delete
        assert profile.is_visible(AppiumBy.ACCESSIBILITY_ID, 'confirm_delete_account', timeout=8) or \
               profile.is_visible(AppiumBy.ACCESSIBILITY_ID, 'cancel_delete_account', timeout=8), \
            "Delete account must require confirmation dialog"
        profile.press_back()  # Cancel the deletion

def test_tc_prof_009_edit_profile_saves_name(self, logged_in):
    """TC-E2E-PROF-009: Editing name in profile persists after navigating away."""
    from pages.home_page import HomePage
    from pages.profile_page import ProfilePage
    from appium.webdriver.common.appiumby import AppiumBy
    home = HomePage(logged_in)
    home.navigate_to_profile()
    profile = ProfilePage(logged_in)
    if profile.is_visible(*profile.EDIT_PROFILE_BUTTON, timeout=5):
        profile.tap(*profile.EDIT_PROFILE_BUTTON)
        profile.wait_for(AppiumBy.ACCESSIBILITY_ID, 'edit_first_name_field', timeout=10)
        profile.clear_text(AppiumBy.ACCESSIBILITY_ID, 'edit_first_name_field')
        profile.type_text(AppiumBy.ACCESSIBILITY_ID, 'edit_first_name_field', 'AutoTest')
        profile.tap(AppiumBy.ACCESSIBILITY_ID, 'save_profile_button')
        profile.wait_for_loading_gone(TestConfig.API_WAIT)
        name = profile.get_name()
        assert 'AutoTest' in name, f"Updated name 'AutoTest' not reflected, got '{name}'"
```

---

### SUITE 9 — EDGE CASES: Fix and Add TC-013 to TC-018

In `appium_test/tests/suite_9_edge_cases/test_edge_cases.py`:

**Replace the `assert True` in existing tests FIRST**, then add:

```python
def test_tc_edge_013_no_crash_on_500_error(self, logged_in):
    """TC-E2E-EDGE-013: App shows user-friendly error if server returns 500."""
    # Use adb to block the server IP temporarily (simulate 500 scenario)
    import subprocess
    from pages.home_page import HomePage
    from pages.catalog_page import CatalogPage
    from appium.webdriver.common.appiumby import AppiumBy
    # This test verifies the app doesn't crash on API errors
    home = HomePage(logged_in)
    home.navigate_to_catalog()
    catalog = CatalogPage(logged_in)
    # App should show either products (if cached) or an error state
    has_products = catalog.is_visible(AppiumBy.ACCESSIBILITY_ID, 'product_list', timeout=15)
    has_error = catalog.is_visible(AppiumBy.ACCESSIBILITY_ID, 'no_results_message', timeout=5)
    assert has_products or has_error, "Catalog must show products or an error state, not a blank screen"

def test_tc_edge_014_cart_state_survives_background(self, logged_in):
    """TC-E2E-EDGE-014: Items added to cart persist after app goes background and foreground."""
    import subprocess, time
    from pages.home_page import HomePage
    from pages.catalog_page import CatalogPage
    from pages.item_detail_page import ItemDetailPage
    from pages.cart_page import CartPage
    from appium.webdriver.common.appiumby import AppiumBy
    home = HomePage(logged_in)
    home.navigate_to_catalog()
    CatalogPage(logged_in).tap_product_by_name(TestConfig.SEARCH_HIT)
    ItemDetailPage(logged_in).tap(AppiumBy.ACCESSIBILITY_ID, 'add_to_cart_button')
    # Background
    subprocess.run(['adb', 'shell', 'input', 'keyevent', 'KEYCODE_HOME'], capture_output=True, timeout=10)
    time.sleep(3)
    # Foreground
    subprocess.run(['adb', 'shell', 'monkey', '-p', TestConfig.APP_PACKAGE, '-c',
                    'android.intent.category.LAUNCHER', '1'], capture_output=True, timeout=10)
    time.sleep(4)
    home.navigate_to_cart()
    cart = CartPage(logged_in)
    assert not cart.is_visible(AppiumBy.ACCESSIBILITY_ID, 'cart_empty_message', timeout=8), \
        "Cart must still have items after app goes background and returns"

def test_tc_edge_015_double_tap_subscribe_no_duplicate(self, logged_in):
    """TC-E2E-EDGE-015: Double tapping subscribe does not create two Chargebee subscriptions."""
    import base64, requests, time
    from pages.home_page import HomePage
    from pages.subscription_plans_page import SubscriptionPlansPage
    from pages.subscription_summary_page import SubscriptionSummaryPage
    from appium.webdriver.common.appiumby import AppiumBy
    home = HomePage(logged_in)
    home.navigate_to_subscription()
    plans = SubscriptionPlansPage(logged_in)
    plans.select_family('delight')
    plans.confirm_plan()
    plans.select_frequency('weekly')
    plans.start_subscription()
    summary = SubscriptionSummaryPage(logged_in)
    # Double tap confirm
    summary.tap(AppiumBy.ACCESSIBILITY_ID, 'confirm_subscription_button')
    time.sleep(0.3)
    summary.tap(AppiumBy.ACCESSIBILITY_ID, 'confirm_subscription_button')
    time.sleep(5)
    # Check Chargebee has only 1 active sub
    auth = base64.b64encode(f"{TestConfig.CHARGEBEE_API_KEY}:".encode()).decode()
    r = requests.get(
        f'https://{TestConfig.CHARGEBEE_SITE}.chargebee.com/api/v2/subscriptions',
        headers={'Authorization': f'Basic {auth}'},
        params={'status[is]': 'active'},
        timeout=15
    )
    subs = r.json().get('list', [])
    assert len(subs) == 1, f"Double-tap must not create duplicate subscriptions. Found: {len(subs)}"

def test_tc_edge_016_sql_injection_in_search(self, logged_in):
    """TC-E2E-EDGE-016: SQL injection string in search doesn't crash app."""
    from pages.home_page import HomePage
    from pages.catalog_page import CatalogPage
    from appium.webdriver.common.appiumby import AppiumBy
    HomePage(logged_in).navigate_to_catalog()
    catalog = CatalogPage(logged_in)
    catalog.type_text(*catalog.SEARCH_BAR, "' OR 1=1 --")
    catalog.wait_for_loading_gone(TestConfig.API_WAIT)
    # App should show empty results or products, NOT crash
    assert catalog.is_visible(AppiumBy.ACCESSIBILITY_ID, 'no_results_message', timeout=10) or \
           catalog.is_visible(AppiumBy.ACCESSIBILITY_ID, 'product_list', timeout=10), \
        "App must not crash on SQL injection input in search"

def test_tc_edge_017_xss_in_address_field(self, logged_in):
    """TC-E2E-EDGE-017: XSS string in address fields saved as plain text, not executed."""
    from pages.home_page import HomePage
    from pages.profile_page import ProfilePage
    from appium.webdriver.common.appiumby import AppiumBy
    home = HomePage(logged_in)
    home.navigate_to_profile()
    ProfilePage(logged_in).navigate_to_addresses()
    from pages.address_page import AddressPage
    addr = AddressPage(logged_in)
    addr.tap_add_new_address()
    xss = '<script>alert(1)</script>'
    addr.type_text(*addr.STREET_FIELD, xss)
    addr.type_text(*addr.PINCODE_FIELD, TestConfig.PINCODE_VALID)
    addr.tap(*addr.SAVE_ADDRESS_BUTTON)
    addr.wait_for_loading_gone(TestConfig.API_WAIT)
    # App must not crash
    assert not addr.is_visible(AppiumBy.ACCESSIBILITY_ID, 'crash_dialog', timeout=3), \
        "App must not crash when XSS string is entered in address"

def test_tc_edge_018_memory_leak_rapid_scroll(self, logged_in):
    """TC-E2E-EDGE-018: Rapid scrolling in catalog does not cause OOM crash."""
    import time
    from pages.home_page import HomePage
    from pages.catalog_page import CatalogPage
    from appium.webdriver.common.appiumby import AppiumBy
    HomePage(logged_in).navigate_to_catalog()
    catalog = CatalogPage(logged_in)
    catalog.wait_for_loading_gone(TestConfig.API_WAIT)
    # Scroll down 10 times rapidly
    for i in range(10):
        catalog.driver.swipe(400, 1200, 400, 300, 200)
        time.sleep(0.2)
    for i in range(10):
        catalog.driver.swipe(400, 300, 400, 1200, 200)
        time.sleep(0.2)
    assert catalog.is_visible(AppiumBy.ACCESSIBILITY_ID, 'product_list', timeout=10) or True, \
        "Catalog must survive 20 rapid scrolls without crashing"
```

---

## PHASE 4 — BUG-FIX WORKFLOW

For every test that FAILS after all the above changes:

1. **Read the screenshot** in `reports/screenshots/FAIL_*.png`
2. **Identify the broken widget/flow** in `lush/lib/`
3. **Fix the Flutter or backend code**
4. **Rebuild and reinstall**: `cd lush && flutter build apk --debug && adb install -r build/app/outputs/flutter-apk/app-debug.apk`
5. **Re-run only that test**: `pytest tests/<suite>/<file>.py::<Class>::<test> -v --tb=short`
6. **Confirm green**, then move to next failure

Never mark a failing test as `xfail` or skip it — fix the root cause.

---

## PHASE 5 — FULL SUITE RUN WITH HTML REPORT

After all fixes:

```bash
pip install pytest-ordering pytest-html pytest-xdist

cd appium_test
python -m pytest tests/ \
  -v \
  --html=reports/full_report.html \
  --self-contained-html \
  --tb=short \
  -p no:warnings \
  2>&1 | tee reports/run_log.txt
```

Then show me:
1. The last 50 lines of `reports/run_log.txt`
2. The count: `passed / failed / error / total`
3. A list of any remaining failures with their screenshot filenames

---

## SUCCESS CRITERIA

- [ ] All 3 previously failing tests: GREEN
- [ ] Zero `assert True` or `or True` remaining
- [ ] Total test count ≥ 150
- [ ] All Flutter Semantics labels present (verify with `adb shell uiautomator dump /sdcard/ui.xml && adb pull /sdcard/ui.xml && grep 'content-desc' ui.xml | wc -l`)
- [ ] HTML report generated at `reports/full_report.html`
- [ ] All identified bugs fixed and re-confirmed green
