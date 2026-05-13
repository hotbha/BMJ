# BookMyJuice Bug Registry

> **Last Updated:** 2026-05-09  
> **Owner:** QA Engineering

## Severity Definitions

- 🔴 **Critical** = security breach, app down, auth bypass, data corruption, production outage
- 🟠 **Major** = core feature broken, checkout blocked, slot booking broken, subscription command broken
- 🟡 **Minor** = partial feature issue, incorrect message, non-blocking UX issue
- 🟢 **Trivial** = typo, spacing, cosmetic-only issue

## Bug Statuses

- 🆕 New
- 🔍 Investigating
- 🔨 In Fix
- ✅ Fixed
- 🔁 Regression
- 🚫 Won't Fix

---

## Open Bugs

*(No open bugs currently registered.)*

---

## Resolved Bugs

| BUG-ID | Title | Module | Severity | Priority | Status | Fix Commit | Linked TC | Reported By | Fixed By |
|--------|-------|--------|----------|----------|--------|------------|-----------|-------------|----------|
| BUG-001 | IdempotencyService.java has duplicated/corrupt code at end of file | Webhook | 🟠 Major | High | ✅ Fixed | 73bd082 | TC-WEB-001 | Code Review | System |

**BUG-001 Details:**
- **Environment:** All (source code)
- **Platform:** Java 17 / Spring Boot
- **Steps to Reproduce:** Open IdempotencyService.java — observe duplicate `cleanupExpiredEvents()` method and broken `processedEvents` HashMap code after the closing brace of the `ProcessingStats` class.
- **Expected:** Clean file with no duplicate code.
- **Actual:** The file had orphan methods (`getTrackedEventCount()`, `clearAllEvents()`) duplicated after the closing brace of the class, referencing non-existent `processedEvents` field which was not declared at class level.
- **Root Cause:** Prior edits appended code after the class closing brace instead of integrating into the class body.
- **Resolution:** Rewrote entire file with `processedEvents` as a class-level `ConcurrentHashMap` and all methods properly scoped inside the class.

---

## Known Non-Bugs

| Issue | Rationale |
|-------|-----------|
| AuthController signup returns 500 in unit test | Expected — Chargebee static methods can't be mocked in simple JUnit tests. Integration tests with real/mocked Chargebee resolve this. |
| CheckoutController returns 400 in unit tests | Expected — Chargebee HostedPage static methods require live or mocked API. |

## Bug Metrics

- **Total reported:** 1
- **Open:** 0
- **Fixed:** 1
- **Won't Fix:** 0
- **Critical:** 0
- **Major:** 1
- **Minor:** 0
- **Trivial:** 0
