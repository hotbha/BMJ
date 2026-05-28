# C5 Dead Code Cleanup Report

> **Date:** 2026-05-28
> **Scope:** Remove unused fields, methods, and dead BLoC events

## Items Processed

| Item | File:line | Search result | Action taken |
|------|-----------|--------------|-------------|
| 1 | `create_password_screen.dart` | `_signupData` — 0 matches | **No-op** — field does not exist in codebase |
| 2 | `user_repository.dart:276` | Line 276 is `await _secureStorage.deleteAuthToken()` — no dead SharedPreferences | **No-op** — no unused variable at that line |
| 3 | `dashboard.dart` | `_buildLoginPromoCard` — 1 ref (only definition) | **Removed** — unused method (~70 lines) |
| 4 | `auth_events.dart` | Dead events: `AuthenticationStarted`, `AuthenticationLoggedIn`, `SignInFacebook` — 0 handler registrations, 0 test usages | **Removed** — 3 event classes deleted |

## Dead Auth Events

| Event | Used in tests? | Used in UI? | Used in handlers? | Action taken |
|-------|---------------|------------|-------------------|-------------|
| `AuthenticationStarted` | No | No | No | Removed |
| `AuthenticationLoggedIn` | No | No | No | Removed |
| `SignInFacebook` | No | No | No | Removed |

## Flutter Analyze

Before: 0 errors, 0 warnings (existing dead-code info warnings now resolved)
After: 0 errors, 0 warnings

## Test Results

Baseline: 133 passed, 6 failed — no new failures introduced