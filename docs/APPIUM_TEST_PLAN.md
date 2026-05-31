# Appium Test Plan

> **Date:** 2026-06-01  
> **Status:** Updated — reflects Dashboard-first architecture, known limitations

This document defines Appium test scenarios for manual/automated device testing. Appium tests require a connected device or emulator.

> ⚠️ **IMPORTANT: Dashboard-First Navigation**  
> The app starts on the **Dashboard** screen even for unauthenticated users. There is no standalone Splash or Login screen. To reach authentication screens, navigate:  
> `Dashboard → Profile (bottom nav) → scroll to "Sign In" / "Sign Up" section`

## Device Matrix

| Platform | Device | Status |
|----------|--------|--------|
| Android Emulator | API 29+ | Primary |
| Physical Android | Any | Recommended |
| iOS | Any | Deferred to post-MVP |

## Framework

Use existing `integration_test/` pattern (Flutter `integration_test` package + `flutter test`). For Appium-native, use `flutter_driver` or Appium Flutter plugin.

---

## ⚠️ Known Limitations

1. **Google OAuth Not Automatable**: Google Sign-In uses Google Play Services account picker which **cannot be automated** via Appium on real devices. Only email/password auth flows are covered in this test suite.
2. **Dashboard-First Architecture**: All test flows start from the Dashboard, not a Login/Splash screen. Account for this in test step definitions.
3. **AutoLoginFailed Race Condition**: On cold app launch, add a **4-second stabilisation wait** before the first Appium interaction to avoid flaky failures from `AutoLoginFailed` firing before Appium settles.
4. **App Package Name**: The actual package is `com.bookmyjuice.lush` (not `com.bookmyjuice.app`). Ensure all ADB commands and capabilities use the correct value.
5. **Known Bug — GoogleSignIn Event Redirect**: The `GoogleSignIn` event handler in `auth_bloc.dart` emits `SignUpStarted` for existing users, causing redirect back to Login instead of the Dashboard. Use email/password login as a workaround.

---

## Priority 1 — Subscription Flow (Critical Path)

### APP-SUB-01: Generic plan happy path
- **Entry:** Dashboard → Subscribe button
- **Steps:**
  1. Navigate to subscription family screen
  2. Tap "Delight" family card
  3. Select "200ml" size, Weekly duration
  4. Select "Mix Punch" for Monday → verify all 6 days auto-filled
  5. Tap "Review Order"
  6. Verify summary shows: Delight, 200ml, Mix Punch for all 6 days
  7. Tap "Start Subscription"
- **Expected:** Success snackbar, navigation to dashboard

### APP-SUB-02: Juice-specific plan happy path
- **Entry:** Dashboard → Subscribe button
- **Steps:**
  1. Navigate to subscription family screen
  2. Tap "Premium" family card
  3. In Section B, tap "Black Grapes" juice card
  4. Verify bottom sheet opens
  5. Select "300ml", Monthly duration, tap "Select"
  6. Verify schedule screen shows Black Grapes for all 6 days
  7. Tap "Review Order" → "Start Subscription"
- **Expected:** Success snackbar, dashboard visible

### APP-SUB-03: Same Everyday toggle behavior
- **Entry:** Schedule screen (generic plan)
- **Steps:**
  1. Verify "Same Everyday" checkbox is checked by default
  2. Select a juice for Monday
  3. Verify all 6 days change to same juice
  4. Uncheck "Same Everyday"
  5. Change Tuesday to a different juice
  6. Verify only Tuesday changed, other days unchanged
- **Expected:** Toggle behavior correct

### APP-SUB-04: Incomplete schedule blocks CTA
- **Entry:** Schedule screen (generic plan, empty)
- **Steps:**
  1. Verify "Review Order" button is disabled
  2. Fill 3 of 6 days
  3. Verify button still disabled
  4. Fill remaining 3 days
  5. Verify button becomes enabled
- **Expected:** Validation works correctly

### APP-SUB-05: Back navigation preserves state
- **Entry:** Schedule screen
- **Steps:**
  1. Fill all 6 days with different juices
  2. Navigate back to plan screen
  3. Navigate forward to schedule screen
- **Expected:** Schedule selections preserved

## Priority 2 — Bottle Tracking

### APP-BOT-01: My Bottles section visible
- **Entry:** Dashboard → Profile
- **Steps:** Verify "My Bottles" section is present
- **Expected:** Section visible with bottle counts

### APP-BOT-02: Bottles count after order
- **Entry:** Place one-time order → Profile → My Bottles
- **Steps:** Verify withCustomer count increased
- **Expected:** Count reflects order quantity

### APP-BOT-03: View History navigation
- **Entry:** Profile → My Bottles → View History
- **Steps:** Tap "View History"
- **Expected:** History list screen opens

## Priority 3 — Auth Flows

### APP-AUTH-01: Phone OTP full flow
1. Dashboard → Profile → Sign Up tab → Phone card → Enter number → Verify OTP → Enter address → Set password → Dashboard

### APP-AUTH-02: Google Sign-In full flow
> ⚠️ **Not automatable via Appium on real devices.** Google Sign-In uses Google Play Services account picker, which cannot be automated. Manual testing only.
1. Dashboard → Profile → Sign In tab → Google button → Authenticate → Link account → Dashboard

### APP-AUTH-03: Auto-login on app restart
1. Login successfully → Close app → Reopen → Wait 4s for stabilisation → Verify logged in

### APP-AUTH-04: Logout clears session
1. Logout → Close app → Reopen → Wait 4s → Verify public Dashboard (login prompt visible)

## Priority 4 — One-time Orders

### APP-ORDER-01: Add item to cart
1. Browse catalog → Tap "Add" on a juice → Verify cart count updated

### APP-ORDER-02: Cart checkout
1. Cart → Verify items → Checkout → Verify order placed

### APP-ORDER-03: Order confirmation
1. Complete order → Verify confirmation screen with details