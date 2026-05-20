# BookMyJuice Bug Registry

> **Last Updated:** 2026-05-13  
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
| BUG-002 | auth_bloc_test.dart uses stale `googleSignIn_()` reference | AUTH (Flutter Test) | 🟡 Minor | Medium | ✅ Fixed | Current | TC-AUTH-BLOC-001 | Test Suite | System |
| BUG-003 | login_page_test.dart uses stale `toast_message`/`toast_heading` references | AUTH (Flutter Test) | 🟡 Minor | Medium | ✅ Fixed | Current | TC-LOGIN-PAGE-001 | Test Suite | System |

**BUG-001 Details:**
- **Environment:** All (source code)
- **Platform:** Java 17 / Spring Boot
- **Steps to Reproduce:** Open IdempotencyService.java — observe duplicate `cleanupExpiredEvents()` method and broken `processedEvents` HashMap code after the closing brace of the `ProcessingStats` class.
- **Expected:** Clean file with no duplicate code.
- **Actual:** The file had orphan methods (`getTrackedEventCount()`, `clearAllEvents()`) duplicated after the closing brace of the class, referencing non-existent `processedEvents` field which was not declared at class level.
- **Root Cause:** Prior edits appended code after the class closing brace instead of integrating into the class body.
- **Resolution:** Rewrote entire file with `processedEvents` as a class-level `ConcurrentHashMap` and all methods properly scoped inside the class.

**BUG-002 Details:**
- **Environment:** Flutter test suite (lush/test/unit/bloc/auth_bloc_test.dart)
- **Platform:** Dart 3.x / Flutter
- **Steps to Reproduce:** Run `flutter test` — test file fails compilation at 5 references to `googleSignIn_()`.
- **Expected:** Tests compile and pass.
- **Actual:** Method `googleSignIn_()` was renamed to `googleSignIn()` in `user_repository.dart` during analyzer fixes (Phase 1.1), but test file references were not updated.
- **Root Cause:** Stale references in test file after rename operation in source file.
- **Resolution:** Updated all 5 occurrences of `googleSignIn_()` → `googleSignIn()` in auth_bloc_test.dart.

**BUG-003 Details:**
- **Environment:** Flutter test suite (lush/test/widget/screens/login_page_test.dart)
- **Platform:** Dart 3.x / Flutter
- **Steps to Reproduce:** Run `flutter test` — test file fails compilation due to `toast_message` and `toast_heading` references.
- **Expected:** Tests compile and pass.
- **Actual:** Properties `toast_message` and `toast_heading` were renamed to `toastMessage` and `toastHeading` during analyzer fixes, but test file references were not updated.
- **Root Cause:** Stale references in test file after rename operation in source file (login_page.dart).
- **Resolution:** Updated `toast_message` → `toastMessage` and `toast_heading` → `toastHeading` in login_page_test.dart.

---

## Known Non-Bugs

| Issue | Rationale |
|-------|-----------|
| AuthController signup returns 500 in unit test | Expected — Chargebee static methods can't be mocked in simple JUnit tests. Integration tests with real/mocked Chargebee resolve this. |
| CheckoutController returns 400 in unit tests | Expected — Chargebee HostedPage static methods require live or mocked API. |

## Bug Metrics

- **Total reported:** 3
- **Open:** 0
- **Fixed:** 3
- **Won't Fix:** 0
- **Critical:** 0
- **Major:** 1
- **Minor:** 2
- **Trivial:** 0
