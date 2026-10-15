# BookMyJuice (BMJ) Known Issues Matrix

Tracking matrix for system bugs, severity ratings, root causes, workarounds, and permanent fixes.

| Issue ID | Severity | Problem Summary | Root Cause | Workaround | Permanent Fix |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **BUG-001** | P0 | Backend compilation failure in `SubscriptionApiService.java` | Incorrect Chargebee SDK method call (`.item()` instead of `.getItem()`) | Override method in localized wrapper | Fixed in `SubscriptionApiService.java` using Chargebee v3.x `getItem()` API |
| **BUG-002** | P0 | Google Sign-In failure ("Connection closed before full header") | Backend container crashing or unready during token validation endpoint request | Restart backend manually | Added healthcheck gate to `docker-compose.yml` (`/api/health` probe) |
| **BUG-003** | P1 | Catalog showing subscription items in One-Time tab | Catalog item filtering did not check item price period units | Manually filter in UI view model | Updated `menu_tab.dart` to check `periodUnit == 'ONE_TIME'` or `null` |
| **BUG-004** | P1 | Subscription plans empty / showing hardcoded fallback | `_buildSubscribeContent()` state builder logic bypassed loaded plans | Fallback mock plans hardcoded in UI | Restructured `SubscriptionBloc` state builder to display real Chargebee data |
| **BUG-005** | P2 | Ambiguous user navigation after login | Login success state did not navigate to main dashboard | Manual tap back button | Connected `AuthenticationSuccess` directly to Home Dashboard with active subscription card |
