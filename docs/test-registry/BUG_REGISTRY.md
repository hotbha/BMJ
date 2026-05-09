# Bug Registry — BookMyJuice

**Document Version:** 1.1  
**Last Updated:** 2026-05-09

---

## Severity & Status Definitions

### Severity

| Icon | Label | Meaning |
|------|-------|---------|
| 🔴 | Critical | Security breach, app down, auth bypass, data corruption, production outage |
| 🟠 | Major | Core feature broken, checkout blocked, slot booking broken, subscription command broken |
| 🟡 | Minor | Partial feature issue, incorrect message, non-blocking UX issue |
| 🟢 | Trivial | Typo, spacing, cosmetic-only issue |

### Status

| Icon | Label | Meaning |
|------|-------|---------|
| 🆕 | New | Reported, not yet triaged |
| 🔍 | Investigating | Under investigation |
| 🔨 | In Fix | Developer assigned, working on fix |
| ✅ | Fixed | Fix merged |
| 🔁 | Regression | Bug returned after fix |
| 🚫 | Won't Fix | Accepted as-is |

---

## Bug List

| BUG-ID | Title | Module | Severity | Priority | Environment | Platform | Steps | Expected | Actual | Root Cause | Fix Commit | Status | Linked TC | Reported By |
|--------|-------|--------|----------|----------|-------------|----------|-------|----------|--------|------------|------------|--------|-----------|-------------|
| BUG-001 | PricingPageController returns 500 when Chargebee site unreachable | BILLING | 🟠 Major | P1 | Staging | Backend | 1. POST to pricing page endpoint 2. Chargebee API down | Graceful error message | 500 Internal Server Error | Missing error handling in PricingPageController | — | 🆕 | BILL-003 | QA Team |
| BUG-002 | Webhook duplicate event not idempotent for concurrent requests | WEBHOOK | 🟠 Major | P1 | Staging | Backend | 1. Send two concurrent webhook events with same ID | Single processing + 409 for second | Both processed, duplicate data | Race condition in IdempotencyService | — | 🆕 | WH-003 | QA Team |
| BUG-003 | Subscription screen freezes on slow network | BILLING | 🟠 Major | P1 | Staging | Android | 1. Open Subscription screen 2. Slow connection | Loading indicator | Screen freezes, no timeout | WebView loads Chargebee page without timeout | — | 🆕 | THEME-001 | QA Team (will be resolved by native screens) |
| BUG-004 | Dark theme text contrast below WCAG AA | THEME | 🟡 Minor | P2 | Local | Android | 1. Enable dark mode 2. View body text | Body text contrast ≥ 4.5:1 | Contrast ratio 3.8:1 | Dark theme secondary text color too light | — | 🆕 | THEME-002 | Dev Team |
| BUG-005 | Refresh token not invalidated on logout | AUTH | 🟠 Major | P1 | Staging | Backend | 1. Login 2. Logout 3. Use old refresh token | 401 Unauthorized | 200 OK, new tokens issued | Logout endpoint does not revoke refresh token | — | 🆕 | AUTH-004 | QA Team |
| BUG-006 | Empty cart checkout returns 500 | BILLING | 🟡 Minor | P2 | Staging | Backend | 1. POST /api/checkout/start with empty cart | Proper validation error | 500 Internal Server Error | Missing cart-empty check in CheckoutService | — | 🆕 | BILL-003 | QA Team |
| BUG-007 | SignUp screen "Create Account" button tappable despite disabled state | AUTH | 🟡 Minor | P2 | Local | Flutter Test | 1. SignUpScreen renders 2. Button has missing `onPressed` check | Tap raises form validation only | Toastification auto-dismiss timer leaks into test | Timer drain needed in test; `_handleSignUp` uses Toastification which creates 3s auto-dismiss PausableTimer | 73bd082 | ✅ Fixed | AUTH-W002 | Dev Team |
| BUG-008 | Flutter test buildTestApp lacks ToastificationWrapper | AUTH | 🟡 Minor | P2 | Local | Flutter Test | 1. Run signup_screen_test 2. Tap Create Account | Toast shows | "Toastification is not initialized!" assertion error | Missing ToastificationWrapper around test widget tree | 73bd082 | ✅ Fixed | AUTH-W002 | Dev Team |
| BUG-009 | SignUp widget test finds duplicate "Create Account" text from AppBar + button | AUTH | 🟢 Trivial | P3 | Local | Flutter Test | 1. Run "All required fields" test | Text found once | Text found twice | AppBar title and button share same text; test expects `findsOneWidget` | 73bd082 | ✅ Fixed | AUTH-W009 | Dev Team |

---

**Document Maintained By:** QA Team  
**Last Review:** 2026-05-09  
**Next Review:** 2026-06-09
