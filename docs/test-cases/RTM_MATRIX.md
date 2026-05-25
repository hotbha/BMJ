# BookMyJuice — Requirements Traceability Matrix (RTM)

> **Document Version:** 1.1
> **Last Updated:** 2026-05-23
> **Total Requirements:** 35 (BR-001 to BR-073 + NFRs)
> **Total Test Cases:** 221 E2E + 52 Existing (Unit/Integration) = **273 Total**
> **Total Use Cases:** 13 (UC-AUTH-001 to UC-AUTH-007c + UC-01 to UC-11)

---

## 1. Module Summary

| Module | BRs Covered | Use Cases | E2E Test Cases | Existing Tests | Total | Coverage |
|--------|-------------|-----------|----------------|----------------|-------|----------|
| **Authentication** | BR-001 to BR-003, BR-006, BR-009 to BR-011 | UC-AUTH-001 to UC-AUTH-007c | 60 + 18 SG | 56+68=124 | 202 | Full |
| **Product Catalog** | BR-008, BR-010 to BR-012 | UC-01 | 12 | — | 12 | Full |
| **Cart** | BR-004, BR-005, BR-020 to BR-024 | UC-01, UC-02 | 16 | 14 | 30 | Full |
| **Checkout/Billing** | BR-030 to BR-033 | UC-03, UC-04 | 16 | 5 | 21 | Full |
| **Subscriptions** | BR-040 to BR-047 | UC-05, UC-06, UC-07 | 16 | — | 16 | Full |
| **Orders** | BR-050 to BR-054 | UC-08, UC-09 | 10 | — | 10 | Full |
| **Delivery** | BR-070 to BR-073 | Delivery domain | 10 | — | 10 | Full |
| **Notifications** | BR-060 to BR-062 | UC-10, UC-11 | 10 | 7 | 17 | Local only |
| **Profile** | BR-007 | Profile mgmt | 6 | 3 | 9 | Full |
| **Non-Functional** | NFR-001 to NFR-017 | NFR | 19 | 7+5=12 | 31 | Full |
| **Phone UX** | BR-001, BR-006, BR-008, BR-011 | UC-AUTH-001 to UC-AUTH-007, UC-01 | 12 | — | 12 | New |
| **Cross-Module** | BR-001 to BR-073 | UC-AUTH-001 to UC-11 | 12 | — | 12 | New |
| **TOTAL** | **35** | **13** | **221** | **52** | **273** | **Full** |

---

## 2. Authentication RTM

| BR ID | Description | Use Case | E2E TCs | Status |
|-------|-------------|----------|---------|--------|
| BR-001 | Register with email/password + email verification | UC-AUTH-001 | AUTH-001 to AUTH-015 | Tested |
| BR-002 | Register with phone/OTP + phone verification | UC-AUTH-001, UC-AUTH-002 | AUTH-001, AUTH-008 to AUTH-010, AUTH-016 to AUTH-020, AUTH-043 to AUTH-048 | Tested |
| BR-003 | Signup with Google (email pre-verified) | UC-AUTH-003 | AUTH-021 to AUTH-024 | Tested |
| BR-006 | JWT 30-day expiry, auto-login checks ONLY token | UC-AUTH-004 | AUTH-025 to AUTH-034, AUTH-056, AUTH-057 | Tested |
| BR-009 | Reset password via mobile OTP or email OTP | UC-AUTH-004 | AUTH-049 to AUTH-054 | Tested |
| BR-010 | Google Sign-In ONLY on user tap | UC-AUTH-005 | AUTH-023, AUTH-034 to AUTH-038 | Tested |
| BR-011 | Phone Sign-In ONLY on user tap | UC-AUTH-006 | AUTH-034, AUTH-039 to AUTH-042 | Tested |

**60 E2E Authentication Test Cases:** Covers all 12 sub-areas: Email-First signup (15), Phone-First signup (5), Google signup (4), User Login (6), Auto-Login (4), Google Sign-In (4), Phone Sign-In (4), Firebase signup (4), Firebase login (2), Password Reset (6), Rate Limiting/Security (3), Edge Cases (3).

---

## 3. Product Catalog RTM

| BR ID | Description | Use Case | E2E TCs | Status |
|-------|-------------|----------|---------|--------|
| BR-008 | Guest browsing without auth | UC-01 | CAT-001, CAT-004, CAT-005 | Tested |
| BR-010 | Products display with images, descriptions, prices | UC-01 | CAT-001, CAT-002, CAT-007 | Tested |
| BR-011 | Both one-time and subscription pricing | UC-01 | CAT-002, CAT-008, CAT-009 | Tested |
| BR-012 | Category filtering | UC-01 | CAT-003, CAT-006, CAT-010 | Tested |

**12 E2E Catalog Test Cases:** Guest browsing (6), Authenticated browsing (4), Edge cases (2).

---

## 4. Cart RTM

| BR ID | Description | Use Case | E2E TCs | Status |
|-------|-------------|----------|---------|--------|
| BR-004 | Guest cart building before login | UC-01 | CART-001, CART-003, CART-004, CART-009 to CART-012 | Tested |
| BR-005 | Guest cart merge on login | UC-02 | CART-013 to CART-015 | Tested |
| BR-020 | Single-mode cart (one-time OR subscription) | UC-01 | CART-001, CART-002, CART-006 to CART-008, CART-016 | Tested |
| BR-021 | No local price calculation | UC-01 | CART-005, CART-016 | Tested |
| BR-022 | Price breakdown display | UC-01 | CART-005 | Tested |
| BR-023 | Delivery fee from Chargebee | UC-01 | CART-005 | Tested |
| BR-024 | Tax from Chargebee | UC-01 | CART-005 | Tested |

**16 E2E Cart Test Cases:** Add items (5), Single-mode enforcement (3), Item management (4), Cart merge (3), Edge cases (1).

---

## 5. Checkout & Billing RTM

| BR ID | Description | Use Case | E2E TCs | Status |
|-------|-------------|----------|---------|--------|
| BR-030 | Checkout via Chargebee Hosted Pages | UC-03, UC-04 | CHK-001, CHK-003 to CHK-005, CHK-007, CHK-009, CHK-014 | Tested |
| BR-031 | bmjServer creates hosted page, returns URL | UC-03, UC-04 | CHK-001, CHK-003, CHK-006, CHK-009 to CHK-012, CHK-016 | Tested |
| BR-032 | Mobile refetches confirmed state | UC-03, UC-04 | CHK-002, CHK-008, CHK-013, CHK-015 | Tested |
| BR-033 | Chargebee webhooks processed idempotently | UC-03, UC-04 | CHK-014 | Tested |

**16 E2E Checkout Test Cases:** One-time checkout (8), Subscription checkout (6), Edge cases (2).

---

## 6. Subscriptions RTM

| BR ID | Description | Use Case | E2E TCs | Status |
|-------|-------------|----------|---------|--------|
| BR-040 | View subscriptions (multiple allowed) | UC-05 to UC-07 | SUB-001, SUB-002 | Tested |
| BR-041 | Pause before 9 PM IST | UC-05 | SUB-003, SUB-004, SUB-005, SUB-013 | Tested |
| BR-042 | Resume before 9 PM IST | UC-06 | SUB-006, SUB-007, SUB-008, SUB-013 | Tested |
| BR-043 | Cancel (immediately/end_of_term/specific_date) | UC-07 | SUB-009, SUB-010, SUB-011, SUB-012 | Tested |
| BR-044 | No limit on pause/resume cycles | UC-05, UC-06 | SUB-014 | Tested |
| BR-045 | Mobile actions via bmjServer (no direct Chargebee) | UC-05 to UC-07 | CHK-009 to CHK-012 | Tested |
| BR-046 | Refetch after action (202 -> GET) | UC-05 to UC-07 | SUB-015, SUB-016 | Tested |
| BR-047 | Multiple active subscriptions | UC-05 to UC-07 | SUB-001 | Tested |

**16 E2E Subscription Test Cases:** List/view (2), Pause (4), Resume (3), Cancel (4), Multiple cycles (1), POST->GET pattern (2).

---

## 7. Orders RTM

| BR ID | Description | Use Case | E2E TCs | Status |
|-------|-------------|----------|---------|--------|
| BR-050 | Order status from bmjServer database | UC-08 | ORD-001, ORD-004, ORD-006 | Tested |
| BR-051 | Chargebee upstream via webhooks | UC-08, UC-09 | ORD-004, ORD-007 | Tested |
| BR-052 | Order history with pagination | UC-08 | ORD-002 | Tested |
| BR-053 | Order details with items, pricing, shipping | UC-08 | ORD-003 | Tested |
| BR-054 | Invoice PDF via Chargebee URL | UC-09 | ORD-004, ORD-008 | Tested |

**10 E2E Order Test Cases:** History (1), Pagination (1), Details (1), Invoice (2), Empty state (1), Status badges (1), Refetch (1), Failed payment (1), Network error (1).

---

## 8. Delivery RTM

| BR ID | Description | E2E TCs | Status |
|-------|-------------|---------|--------|
| BR-070 | Delivery address during signup | DEL-001, DEL-002, DEL-003 | Tested |
| BR-071 | Pincode-based serviceability | DEL-004, DEL-005, DEL-010 | Tested |
| BR-072 | Day-wise delivery schedule | DEL-006 to DEL-009 | Tested |
| BR-073 | Delivery fee sourced from Chargebee pricing data | DEL-009 | Tested |

**10 E2E Delivery Test Cases:** Address validation (3), Pincode check (3), Day-wise schedule (3), Fee check (1).

---

## 9. Notifications RTM

| BR ID | Description | Use Case | E2E TCs | Status |
|-------|-------------|----------|---------|--------|
| BR-060 | Payment failure notifications via FCM push | UC-10 | NOT-001 | FCM Push |
| BR-061 | Subscription action notifications via FCM push | UC-10 | NOT-002, NOT-003, NOT-004 | FCM Push |
| BR-062 | Order event notifications via FCM push | UC-11 | NOT-005 | FCM Push |

**10 E2E Notification Test Cases:** Payment failure (1), Subscription actions (3), Order events (1), Permission handling (1), Deep links (1), FCM token (1), Stacking (1), Foreground (1).

---

## 10. Profile RTM

| BR ID | Description | E2E TCs | Status |
|-------|-------------|---------|--------|
| BR-007 | Profile and address management | PRO-001 to PRO-006 | Tested |

**6 E2E Profile Test Cases:** View (1), Update name (1), Update address (1), Logout (1), Guest cart after logout (1), Delete account (1).

---

## 11. Non-Functional RTM

| NFR ID | Description | E2E TCs | Status |
|--------|-------------|---------|--------|
| NFR-001 | API response < 2s (p95) | NFR-001 | Tested |
| NFR-002 | Cold start < 3s | NFR-002 | Tested |
| NFR-003 | 60 FPS rendering | NFR-003 | Tested |
| NFR-004 | HTTPS only | NFR-004 | Tested |
| NFR-005 | BCrypt hashing (cost 10) | NFR-010 | Tested |
| NFR-006 | JWT stored securely | NFR-001 (token check) | Tested |
| NFR-007 | Webhook signature validation | NFR-006 | Tested |
| NFR-008 | API uptime > 99% | — | Monitoring |
| NFR-009 | Crash rate < 1% | — | Monitoring |
| NFR-010 | Idempotent webhooks | NFR-007 | Tested |
| NFR-011 | Rate limiting (10/5min per IP) | NFR-005, AUTH-030, AUTH-054, AUTH-055 | Tested |
| NFR-012 | FCM token persistence | NOT-008 | Tested |
| NFR-013 | @Profile('dev') gating | NFR-011 | Tested |
| NFR-014 | FCM integration (Flutter) | NOT-008 | Tested |
| NFR-015 | Secrets in .env | NFR-012 | Tested |
| NFR-016 | Signup < 2 min | NFR-014 | Tested |
| NFR-017 | WCAG 2.1 AA contrast | — | Accessibility tool |

**19 E2E NFR Test Cases:** Performance (3), Security (7), Reliability (3), Usability (4), Data management (2).

---

## 12. Coverage Summary

### Business Requirements Coverage

| Category | Total BRs | Covered | Coverage |
|----------|-----------|---------|----------|
| User Management | 3 | 3 | 100% |
| Product Catalog | 4 | 4 | 100% |
| Cart & Pricing | 7 | 7 | 100% |
| Checkout & Payment | 4 | 4 | 100% |
| Subscriptions | 8 | 8 | 100% |
| Orders & Status | 5 | 5 | 100% |
| Notifications | 3 | 3 | FCM Push |
| Delivery Domain | 4 | 4 | 100% |
| Profile | 1 | 1 | 100% |
| Security (BR-006, BR-009 to BR-011) | 4 | 4 | 100% |
| **Functional Total** | **43** | **43** | **100%** |
| Non-Functional | 15 | 13 | 87% |

### Use Case Coverage — 20/20 (100%)

All 20 use cases covered: UC-AUTH-001 to UC-AUTH-007c (10), UC-01 to UC-11 (10).

### Test Count Summary

| Category | Count |
|----------|-------|
| Authentication E2E | 60 |
| Auth Signup Gaps E2E | 18 |
| Product Catalog E2E | 12 |
| Cart E2E | 16 |
| Checkout E2E | 16 |
| Subscription E2E | 16 |
| Order E2E | 10 |
| Delivery E2E | 10 |
| Notification E2E | 10 |
| Profile E2E | 6 |
| Non-Functional E2E | 19 |
| Phone UX E2E | 12 |
| Cross-Module E2E | 12 |
| **Total E2E Test Cases** | **221** |
| Existing Backend Tests | 71 |
| Existing Flutter Tests | 82 |
| **Grand Total** | **274** |

---

**Document Control:**
- **Version:** 1.0
- **Last Updated:** 2026-05-19
- **Status:** Complete — 173 E2E Test Cases Generated + RTM Mapped
