# BMJ Lush App — E2E Human Test Guide

## Pre-conditions
- bmjServer running on localhost:8080
- Flutter app running on emulator or device
- Chargebee TEST site active
- Android: `adb shell setprop debug.firebase.analytics.app com.bookmyjuice.lush` (for analytics verification)

## Known Issues Found During Diagnosis

| # | Issue | Severity | Fix Applied |
|---|-------|----------|-------------|
| 1 | `AndroidManifest.xml`: `android:usesCleartextTraffic="true"` was outside the `<application>` tag — not an actual attribute. All HTTP API calls silently failed on Android 9+ | **CRITICAL** | ✅ Moved into `<application>` tag attributes |
| 2 | Dashboard redesign removed all BLoC data-loading dispatches: no `LoadCart`, `LoadProductCatalog`, `_loadSubscriptionData()` in initState | **CRITICAL** | ⬜ Dashboard needs data-loading events restored |
| 3 | Menu/Orders/Profile tabs show placeholder colors instead of actual screens | **HIGH** | ⬜ Wire actual screen widgets |
| 4 | API base URL defaults to `http://10.0.2.2:8080` — correct for emulator, but physical devices need explicit `--dart-define=API_BASE_URL=http://192.168.x.x:8080` | **MEDIUM** | ⬜ Update instructions below |

---

## TEST SUITE 1 — Authentication

### T1.1 Sign Up (New User)
**Steps:**
1. Open app → tap "Sign Up"
2. Enter name, email, phone, password
3. Enter referral code field (leave blank for first test)
4. Tap "Create Account"
**Expected:** OTP screen appears
5. Enter OTP (check bmjServer logs for OTP printed)
**Expected:** Dashboard loads with user name in header

### T1.2 Login (Existing User)
**Steps:**
1. Tap "Login"
2. Enter email + password
3. Tap Login
**Expected:** Dashboard loads, "Good morning [name] 👋" visible

### T1.3 Logout
**Steps:**
1. Open drawer → tap Logout
**Expected:** Returns to login screen, JWT cleared

### T1.4 Invalid Login
**Steps:**
1. Enter wrong password → tap Login
**Expected:** Error toast shown, not stuck on loading

---

## TEST SUITE 2 — Dashboard

### T2.1 Dashboard loads correctly
**Expected after login:**
- Green gradient header with user name
- Subscription card (or "No active plan" if none)
- Stats strip visible
- NavigationBar at bottom: Home, Menu, Orders, Profile

### T2.2 Notification bell
**Steps:** Tap bell icon in header
**Expected:** Notification screen or badge updates

### T2.3 Drawer navigation
**Steps:** Tap hamburger icon → verify all drawer items navigate correctly:
- [ ] My Account
- [ ] Subscriptions
- [ ] Order History
- [ ] Refer & Earn
- [ ] Menu
- [ ] My Cart
- [ ] Notifications
- [ ] Settings
- [ ] Logout

---

## TEST SUITE 3 — Product Menu

### T3.1 Browse catalog
**Steps:**
1. Tap "Menu" in bottom NavigationBar
**Expected:** Product list loads, juice items visible with gradient cards

### T3.2 Search
**Steps:** Type in search bar (e.g. "mango")
**Expected:** Results filter in real-time

### T3.3 Filter by category
**Steps:** Tap a category chip (e.g. "Delight", "Signature", "Premium")
**Expected:** Only matching juices shown

### T3.4 Filter by size
**Steps:** Tap size chip (e.g. "200ml", "300ml", "500ml")
**Expected:** Products filtered by size

### T3.5 View item detail
**Steps:** Tap any juice item card
**Expected:** Detail screen opens with name, price gradient, description, quantity selector, add-to-cart

---

## TEST SUITE 4 — Cart & Orders

### T4.1 Add to cart
**Steps:**
1. On item detail → tap "Add to Cart"
**Expected:** SnackBar shows "added to cart", badge updates

### T4.2 View cart
**Steps:**
1. Tap cart icon in AppBar or navigate to Cart
**Expected:** Cart items listed with quantity, total, "Checkout" button

### T4.3 Update quantity
**Steps:** Tap +/- buttons on cart item
**Expected:** Quantity updates, total recalculates

### T4.4 Remove item
**Steps:** Tap delete icon on cart item
**Expected:** Item removed, empty state shows if cart is empty

### T4.5 Place order
**Steps:** Tap "Place Order" → confirm address
**Expected:** Order success screen, order appears in Orders tab

### T4.6 Order history
**Steps:** Tap "Orders" in bottom nav
**Expected:** Past orders listed with date, items, total, status chip

### T4.7 Reorder
**Steps:** Tap "Reorder" on a past order
**Expected:** Items added to cart, snackBar confirmation

---

## TEST SUITE 5 — Subscriptions

### T5.1 View plans (from drawer)
**Steps:**
1. Open drawer → tap Subscriptions
**Expected:** Subscription management screen loads

### T5.2 View plans (from plans screen)
**Steps:**
1. Navigate to the subscription plans screen
**Expected Plan card UI:**
- Green gradient header "Choose Your Plan"
- Poppins typography throughout
- Plan cards with: name, description (italic), price ₹X/month, ₹Y/day chip
- Green check_circle features: "Choose your daily juice variety", "Free doorstep delivery", "Pause or cancel anytime"
- "Select This Plan →" green button
- Amber "⭐ POPULAR" badge on second plan

### T5.3 Select a plan
**Steps:**
1. Tap "Select This Plan →" on any plan
**Expected:** Confirmation bottom sheet shows plan name + price
2. Tap "Confirm & Continue →"
**Expected:** Navigates to schedule screen

### T5.4 Create subscription
**Steps:**
1. On schedule screen → select juices per day → confirm
**Expected:** Subscription created, status = ACTIVE

### T5.5 Pause subscription
**Steps:**
1. Dashboard → subscription card → tap "Pause"
**Expected:** Subscription status changes to PAUSED

### T5.6 Resume subscription
**Steps:**
1. Tap "Resume" on paused subscription
**Expected:** Status returns to ACTIVE

### T5.7 Cancel subscription
**Steps:**
1. Tap "Cancel"
2. Select reason from dropdown
3. Confirm cancellation
**Expected:** Status changes to CANCELLED

---

## TEST SUITE 6 — Referral

### T6.1 View referral screen
**Steps:**
1. Open drawer → tap "Refer & Earn"
**Expected:** Referral screen with 3 cards visible:
- Card 1: Your Referral Code (large bold text) + Copy + Share buttons
- Card 2: Stats — Friends Joined count + Total Earned ₹X
- Card 3: How It Works — 4 steps with numbered circles

### T6.2 Copy referral code
**Steps:** Tap "Copy Code" button
**Expected:** SnackBar shows "Referral code copied!"

### T6.3 Share referral code
**Steps:** Tap "Share" button
**Expected:** System share sheet opens with referral message

### T6.4 Sign up with referral code
**Steps:**
1. Logout → Sign Up → enter referral code from T6.1
**Expected:** Signup succeeds, referral credited to referrer

---

## TEST SUITE 7 — Edge Cases

### T7.1 Offline handling
**Steps:**
1. Enable airplane mode
2. Try to load catalog
**Expected:** Error state shown with retry button (not crash or infinite spinner)

### T7.2 App kill and restart
**Steps:**
1. Force-stop app via app switcher
2. Reopen app
**Expected:** Session restored if logged in, login screen if session expired

### T7.3 Back navigation
**Steps:**
1. Navigate deep into screens (Dashboard → Menu → Item Detail)
2. Press Android back button repeatedly
**Expected:** Each press goes back one screen, eventually returns to Dashboard

### T7.4 Double-tap protection
**Steps:**
1. Rapidly double-tap "Add to Cart" button
**Expected:** Item added only once (no duplicates)

---

## TEST SUITE 8 — Analytics Verification

**Prerequisites:**
- Firebase project with Analytics enabled
- Device connected via adb

**Setup:**
```bash
adb shell setprop debug.firebase.analytics.app com.bookmyjuice.lush
```

**Test Actions & Expected Events:**
| Action | Expected Firebase Event | Visible in DebugView |
|--------|------------------------|---------------------|
| Login | `login` | ✅ |
| Sign Up | `signup` | ✅ |
| View product detail | `view_item` | ✅ |
| Search products | `search` | ✅ |
| Filter by category | `family_selected` | ✅ |
| Create subscription | `subscription_started` | ✅ |
| Pause subscription | `subscription_paused` | ✅ |
| Cancel subscription | `subscription_cancelled` | ✅ |
| Place order | `order_placed` | ✅ |
| Reorder | `reorder_tapped` | ✅ |
| Share referral | `share` | ✅ |

Events should appear in Firebase DebugView within 30 seconds.

---

## Running Instructions

### Build & Install APK
```bash
cd lush
flutter build apk --debug
adb install -r build/app/outputs/apk/debug/app-debug.apk
```

### Start bmjServer
```bash
cd bmjServer
mvn spring-boot:run
```
Verify: `curl http://localhost:8080/api/products` returns JSON.

### Run with custom API URL
For physical device (replace IP):
```bash
flutter build apk --debug --dart-define=API_BASE_URL=http://192.168.1.100:8080
```

---

## Test Result Log

| Suite | Test | Pass/Fail | Notes |
|-------|------|-----------|-------|
| Auth | T1.1 Sign Up | ⬜ | |
| Auth | T1.2 Login | ⬜ | |
| Auth | T1.3 Logout | ⬜ | |
| Auth | T1.4 Invalid Login | ⬜ | |
| Dashboard | T2.1 Load | ⬜ | |
| Dashboard | T2.2 Notification | ⬜ | |
| Dashboard | T2.3 Drawer | ⬜ | |
| Menu | T3.1 Browse | ⬜ | |
| Menu | T3.2 Search | ⬜ | |
| Menu | T3.3 Filter category | ⬜ | |
| Menu | T3.4 Filter size | ⬜ | |
| Menu | T3.5 Item detail | ⬜ | |
| Cart | T4.1 Add to cart | ⬜ | |
| Cart | T4.2 View cart | ⬜ | |
| Cart | T4.3 Update qty | ⬜ | |
| Cart | T4.4 Remove | ⬜ | |
| Cart | T4.5 Place order | ⬜ | |
| Cart | T4.6 Order history | ⬜ | |
| Cart | T4.7 Reorder | ⬜ | |
| Sub | T5.1 View (drawer) | ⬜ | |
| Sub | T5.2 View plans | ⬜ | |
| Sub | T5.3 Select plan | ⬜ | |
| Sub | T5.4 Create | ⬜ | |
| Sub | T5.5 Pause | ⬜ | |
| Sub | T5.6 Resume | ⬜ | |
| Sub | T5.7 Cancel | ⬜ | |
| Referral | T6.1 View | ⬜ | |
| Referral | T6.2 Copy | ⬜ | |
| Referral | T6.3 Share | ⬜ | |
| Referral | T6.4 Signup with code | ⬜ | |
| Edge | T7.1 Offline | ⬜ | |
| Edge | T7.2 Kill/restart | ⬜ | |
| Edge | T7.3 Back nav | ⬜ | |
| Edge | T7.4 Double-tap | ⬜ | |
| Analytics | T8 All events | ⬜ | |

---

## API Configuration Summary

| Setting | File | Current Value |
|---------|------|---------------|
| API base URL | `lush/lib/config/api_config.dart` | `http://10.0.2.2:8080` (emulator) or `--dart-define=API_BASE_URL=...` |
| Cleartext HTTP | `lush/android/.../AndroidManifest.xml` | ✅ `android:usesCleartextTraffic="true"` (fixed) |
| Chargebee site | `lush/lib/config/api_config.dart` | `bookmyjuice-test` |
| Chargebee key | `lush/lib/config/api_config.dart` | default: `test_ai_...` |