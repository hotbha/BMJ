# Test Registry — BookMyJuice

**Document Version:** 1.1  
**Last Updated:** 2026-05-09

---

## Status Legends

| Status | Label |
|--------|-------|
| ⏳ | Not Run |
| ✅ | Pass |
| ❌ | Fail |
| ⚠️ | Blocked |
| 🔄 | In Progress |

---

## AUTH — Authentication Module

| TC-ID | Title | Module | Type | Priority | Preconditions | Steps | Expected | Automation | Status |
|-------|-------|--------|------|----------|-------------|-------|----------|------------|--------|
| AUTH-001 | Unified signup creates user and Chargebee customer | AUTH | Integration | P1 | Chargebee test site configured | 1. POST /api/auth/unified-signup with valid data 2. Check users table 3. Check Chargebee customer exists | User created in DB, chargebee_customer_id populated | ✅ Automated | ✅ |
| AUTH-002 | Login with valid credentials returns JWT | AUTH | Integration | P1 | User exists with verified email | 1. POST /api/auth/signin with email/password 2. Check response | 200 OK, JWT token returned | ✅ Automated | ✅ |
| AUTH-003 | Login with invalid password returns 401 | AUTH | Unit | P1 | User exists | 1. POST /api/auth/signin with wrong password | 401 Unauthorized | ✅ Automated | ✅ |
| AUTH-004 | Refresh token rotation works | AUTH | Integration | P1 | Logged-in user with refresh token | 1. POST /api/auth/refresh with valid refresh token 2. Check old token invalidated | New tokens returned, old token revoked | ✅ Automated | ✅ |
| AUTH-005 | Logout-all revokes all sessions | AUTH | Integration | P1 | User has multiple active sessions | 1. POST /api/auth/logout-all 2. Try to use any old token | All tokens rejected | ✅ Automated | ✅ |
| AUTH-006 | 15-min JWT expiration enforced | AUTH | Unit | P1 | Valid JWT | 1. Wait 16 min 2. Use expired token | 401 Unauthorized | ✅ Automated | ✅ |
| AUTH-007 | Rate limiting on login endpoint | AUTH | Integration | P2 | - | 1. POST /api/auth/signin 10 times in 1 minute | 11th attempt returns 429 | ✅ Automated | ⏳ |
| AUTH-W001 | SignUp screen renders all required fields | AUTH | Widget | P1 | Mock bloc ready | 1. Pump SignUpScreen 2. Check fields present | Email, First Name, Last Name, Phone Number, Password, Confirm Password visible | ✅ Automated | ✅ |
| AUTH-W002 | Email field validation (empty, invalid, valid) | AUTH | Widget | P1 | Mock bloc ready | 1. Test empty email → "Email is required" 2. Test invalid-email → "Enter a valid email" 3. Test valid email → no error | Validation messages correct per input | ✅ Automated | ✅ |
| AUTH-W003 | Password field validation (empty, weak, no-special, strong) | AUTH | Widget | P1 | Mock bloc ready | 1. Test empty → "Password is required" 2. Test weak → "Password does not meet requirements" 3. Test strong → check_circle icons appear | Validation messages correct per input | ✅ Automated | ✅ |
| AUTH-W004 | Phone field validation (empty, <10 digits, invalid start, valid) | AUTH | Widget | P1 | Mock bloc ready | 1. Test empty → "Phone number is required" 2. Test invalid → "Enter a valid 10-digit number" 3. Test valid → no error | Validation messages correct per input | ✅ Automated | ✅ |
| AUTH-W005 | Form submission blocked with incomplete data | AUTH | Widget | P1 | Mock bloc ready | 1. Tap Create Account with all fields empty | All 5 required field errors shown | ✅ Automated | ✅ |
| AUTH-W006 | Password visibility toggle works | AUTH | Widget | P2 | Mock bloc ready | 1. Tap visibility_off icon 2. Check visibility_off → visibility_outlined | Icon toggles | ✅ Automated | ✅ |
| AUTH-W007 | Password requirements update in real-time | AUTH | Widget | P2 | Mock bloc ready | 1. Enter strong password 2. Check all 5 check_circle icons appear | check_circle count = 5 | ✅ Automated | ✅ |
| AUTH-W008 | Password mismatch shows error | AUTH | Widget | P2 | Mock bloc ready | 1. Enter different passwords 2. Tap Create Account | "Passwords do not match" shown | ✅ Automated | ✅ |
| AUTH-W009 | Navigate to login screen from signup | AUTH | Widget | P2 | Mock bloc ready, /login route defined | 1. Ensure Login link visible 2. Tap TextButton("Login") | Login Screen shown | ✅ Automated | ✅ |

---

## DELIVERY — Delivery Module

| TC-ID | Title | Module | Type | Priority | Preconditions | Steps | Expected | Automation | Status |
|-------|-------|--------|------|----------|-------------|-------|----------|------------|--------|
| DEL-001 | Check serviceability by valid pincode | DELIVERY | Integration | P1 | Service area configured for pincode | 1. GET /api/delivery/serviceability?pincode=560001 | 200 OK, serviceable=true | ✅ Automated | ✅ |
| DEL-002 | Check serviceability by invalid pincode | DELIVERY | Integration | P1 | - | 1. GET /api/delivery/serviceability?pincode=999999 | 200 OK, serviceable=false | ✅ Automated | ✅ |
| DEL-003 | List available delivery slots | DELIVERY | Integration | P1 | Service area exists with active slots | 1. GET /api/delivery/slots?pincode=560001&date=2026-05-10 | 200 OK, slots array | ✅ Automated | ✅ |
| DEL-004 | Create new address | DELIVERY | Integration | P1 | Authenticated user | 1. POST /api/delivery/addresses with valid payload | 201 Created, address returned | ✅ Automated | ✅ |
| DEL-005 | Set default address | DELIVERY | Integration | P1 | User has 2+ addresses | 1. PUT /api/delivery/addresses/{id}/default | 200 OK, address is_default=true | ✅ Automated | ✅ |
| DEL-006 | Cannot access another user's address | DELIVERY | Unit | P1 | Two users with addresses | 1. User A tries GET /api/delivery/addresses/{userB_address_id} | 403 Forbidden | ✅ Automated | ✅ |
| DEL-007 | Slot booking with capacity check | DELIVERY | Integration | P1 | Slot with available capacity | 1. POST /api/delivery/slots/{id}/book | 200 OK, capacity decremented | ✅ Automated | ⏳ |

---

## BILLING — Billing Module

| TC-ID | Title | Module | Type | Priority | Preconditions | Steps | Expected | Automation | Status |
|-------|-------|--------|------|----------|-------------|-------|----------|------------|--------|
| BILL-001 | Browse native plan catalog | BILLING | Integration | P1 | Plans synced from Chargebee | 1. GET /api/plans | 200 OK, plans array from local cache | ✅ Automated | ✅ |
| BILL-002 | View plan details | BILLING | Integration | P1 | Plan exists in local cache | 1. GET /api/plans/{id} | 200 OK, plan details | ✅ Automated | ✅ |
| BILL-003 | Pre-checkout review validates cart | BILLING | Integration | P1 | Authenticated user with cart items | 1. POST /api/billing/checkout/review with items | 200 OK, price breakdown, delivery info | ✅ Automated | ✅ |
| BILL-004 | Start checkout returns hosted URL | BILLING | Integration | P1 | Valid review completed | 1. POST /api/billing/checkout/start | 200 OK, hosted page URL for Chargebee checkout | ✅ Automated | ✅ |
| BILL-005 | View user's subscriptions | BILLING | Integration | P1 | User has active subscription | 1. GET /api/billing/subscriptions/me | 200 OK, subscription details | ✅ Automated | ✅ |
| BILL-006 | Cancel subscription | BILLING | Integration | P1 | User has active subscription | 1. POST /api/billing/subscriptions/cancel {subscriptionId} | 200 OK, subscription cancelled | ✅ Automated | ✅ |
| BILL-007 | Change subscription plan | BILLING | Integration | P1 | User has active subscription | 1. POST /api/billing/subscriptions/change-plan {subscriptionId, newPlanId} | 200 OK, plan changed | ✅ Automated | ⏳ |

---

## WEBHOOK — Webhook Module

| TC-ID | Title | Module | Type | Priority | Preconditions | Steps | Expected | Automation | Status |
|-------|-------|--------|------|----------|-------------|-------|----------|------------|--------|
| WH-001 | Valid webhook signature processes event | WEBHOOK | Unit | P1 | Webhook secret configured | 1. Generate valid HMAC signature 2. POST /api/webhooks/subscriptions with header | 200 OK, event processed | ✅ Automated | ✅ |
| WH-002 | Invalid webhook signature returns 401 | WEBHOOK | Unit | P1 | - | 1. POST with invalid signature header | 401 Unauthorized | ✅ Automated | ✅ |
| WH-003 | Duplicate event ID returns 200 (idempotent) | WEBHOOK | Integration | P1 | Event already processed | 1. POST same event twice | 200 OK both times, DB updated once | ✅ Automated | ✅ |
| WH-004 | Failed event moves to DLQ after max retries | WEBHOOK | Integration | P1 | Event that always fails | 1. POST failing event max_attempts times | Event moved to webhook_dlq | ✅ Automated | ✅ |
| WH-005 | Subscription created event syncs to local DB | WEBHOOK | Integration | P1 | Chargebee test event available | 1. Simulate subscription.created webhook | Local subscriptions table updated | ✅ Automated | ✅ |
| WH-006 | Cache evicted on price update event | WEBHOOK | Integration | P1 | Products cached in Redis | 1. Simulate item_price.updated webhook | Cache cleared for prices | ✅ Automated | ⏳ |

---

## CACHE — Caching Module

| TC-ID | Title | Module | Type | Priority | Preconditions | Steps | Expected | Automation | Status |
|-------|-------|--------|------|----------|-------------|-------|----------|------------|--------|
| CACHE-001 | First request caches data | CACHE | Integration | P1 | Redis running | 1. GET /api/plans (first request) 2. Check Redis | Data present in cache | ✅ Automated | ✅ |
| CACHE-002 | Subsequent request returns cached data | CACHE | Integration | P1 | Data already cached | 1. GET /api/plans (second request) 2. Compare timing | Faster response | ✅ Automated | ✅ |
| CACHE-003 | Graceful degradation when Redis down | CACHE | Integration | P1 | Redis stopped | 1. GET /api/plans with Redis unavailable | 200 OK from DB fallback | ✅ Automated | ✅ |
| CACHE-004 | Cache eviction clears entries | CACHE | Integration | P1 | Data cached | 1. Evict cache for plans 2. GET /api/plans | Miss, refetched from DB | ✅ Automated | ⏳ |

---

## THEME — Theme Module

| TC-ID | Title | Module | Type | Priority | Preconditions | Steps | Expected | Automation | Status |
|-------|-------|--------|------|----------|-------------|-------|----------|------------|--------|
| THEME-001 | Light theme colors match design tokens | THEME | Unit | P2 | - | 1. Get light ThemeData 2. Check color values | Colors match DESIGN_SYSTEM.md | ✅ Automated | ✅ |
| THEME-002 | Dark theme colors match design tokens | THEME | Unit | P2 | - | 1. Get dark ThemeData 2. Check color values | Colors match DESIGN_SYSTEM.md | ✅ Automated | ✅ |
| THEME-003 | Theme cubit persists preference | THEME | Unit | P2 | SharedPreferences mock | 1. Create ThemeCubit 2. Set dark theme 3. Recreate cubit | Dark theme restored | ✅ Automated | ✅ |
| THEME-004 | System theme default works | THEME | Unit | P2 | Platform brightness mock | 1. Create ThemeCubit with system default 2. Check selected theme | Follows platform | ✅ Automated | ✅ |

---

## CICD — CI/CD

| TC-ID | Title | Module | Type | Priority | Preconditions | Steps | Expected | Automation | Status |
|-------|-------|--------|------|----------|-------------|-------|----------|------------|--------|
| CICD-001 | Backend build succeeds | CICD | Integration | P0 | CI environment | 1. Trigger backend CI | Build passes, tests pass | ✅ Automated | ✅ |
| CICD-002 | Flutter analyze passes | CICD | Integration | P1 | CI environment | 1. Trigger Flutter CI | analyze passes, no errors | ✅ Automated | ✅ |
| CICD-003 | Coverage gate enforced | CICD | Integration | P1 | Coverage < 80% scenario | 1. Commit with low coverage | CI fails | ✅ Automated | ✅ |

---

## SECURITY — Security & Compliance

| TC-ID | Title | Module | Type | Priority | Preconditions | Steps | Expected | Automation | Status |
|-------|-------|--------|------|----------|-------------|-------|----------|------------|--------|
| SEC-001 | Right-to-erasure anonymizes user | SECURITY | Integration | P1 | User exists with addresses/consent | 1. POST /api/v1/compliance/delete-account 2. Check user record | PII anonymized, Chargebee customer marked | ✅ Automated | ✅ |
| SEC-002 | Data export includes all user data | SECURITY | Integration | P1 | User with addresses, orders | 1. GET /api/v1/compliance/export-data | 200 OK, JSON with all categories | ✅ Automated | ⏳ |
| SEC-003 | Audit log records critical events | SECURITY | Unit | P1 | - | 1. Trigger LOGIN_SUCCESS 2. Check audit_log table | Entry created with event type | ✅ Automated | ✅ |
| SEC-004 | No secrets in code (scan) | SECURITY | Manual | P0 | - | 1. Scan repository for secrets | No hardcoded secrets | 🚫 Manual | ⏳ |
| SEC-005 | Password hashed with BCrypt | SECURITY | Unit | P1 | - | 1. Create user 2. Check password hash | Starts with $2a$10$ or $2b$10$ | ✅ Automated | ✅ |
| SEC-006 | Endpoint auth enforcement | SECURITY | Integration | P1 | - | 1. Call protected endpoint without token | 401 Unauthorized | ✅ Automated | ✅ |

---

**Document Maintained By:** QA Team  
**Last Review:** 2026-05-09  
**Next Review:** 2026-06-09
