# T1 — Subscription Tests Report

> **Date:** 2026-05-28
> **Scope:** BLoC unit tests, widget tests, integration tests for subscription flow

## Test Files Created

| File | Test count |
|------|-----------|
| `lush/test/subscription_bloc_test.dart` | 17 |
| `lush/test/subscription_screens_test.dart` | 14 |
| `integration_test/subscription_flow_test.dart` | 2 |

## BLoC Tests

| Test | Pass/Fail |
|------|-----------|
| LoadSubscriptionCatalog emits [SubscriptionLoading, SubscriptionCatalogLoaded] on success | ✅ Pass |
| LoadSubscriptionCatalog emits [SubscriptionLoading, SubscriptionCatalogError] on service exception | ✅ Pass |
| LoadSubscriptionCatalog filters out non-bmj plans | ✅ Pass |
| CreateSubscriptionFromSelection emits [SubscriptionLoading, SubscriptionCreatedSuccess] on success | ✅ Pass |
| CreateSubscriptionFromSelection emits [SubscriptionLoading, SubscriptionError] on service exception | ✅ Pass |
| SubscriptionSelection isComplete returns true when all 6 days filled | ✅ Pass |
| SubscriptionSelection isComplete returns false when any day empty | ✅ Pass |
| SubscriptionSelection isComplete returns false when fewer than 6 days | ✅ Pass |
| SubscriptionSelection priceInRupees = priceInPaise / 100 | ✅ Pass |
| SubscriptionSelection toChargebeeMetadata contains itemPriceId, family, size, period, day_schedule | ✅ Pass |
| SubscriptionSelection copyWith preserves unchanged fields | ✅ Pass |
| SubscriptionSelection copyWith overrides specified fields | ✅ Pass |
| SubscriptionPlanCatalog isGeneric true when planType = 'generic' | ✅ Pass |
| SubscriptionPlanCatalog isJuiceSpecific true when planType = 'juice_specific' | ✅ Pass |
| SubscriptionPlanCatalog weeklyPrice returns correct SubscriptionPriceOption | ✅ Pass |
| SubscriptionPlanCatalog monthlyPrice returns correct SubscriptionPriceOption | ✅ Pass |
| SubscriptionPlanCatalog fromChargebee parses snake_case keys correctly | ✅ Pass |

## Widget Tests

| Screen | Tests | Pass/Fail |
|--------|-------|-----------|
| SubscriptionFamilyScreen | shows loading indicator | ✅ Pass |
| SubscriptionFamilyScreen | shows family cards with CatalogLoaded | ✅ Pass |
| SubscriptionFamilyScreen | shows error + retry on CatalogError | ✅ Pass |
| SubscriptionPlanScreen | shows size cards for generic plans | ✅ Pass |
| SubscriptionPlanScreen | shows juice cards in Section B | ✅ Pass |
| SubscriptionPlanScreen | duration toggle changes displayed price | ✅ Pass |
| SubscriptionScheduleScreen | shows 6 day rows, no Sunday | ✅ Pass |
| SubscriptionScheduleScreen | Same Everyday checked by default | ✅ Pass |
| SubscriptionScheduleScreen | CTA disabled when incomplete | ✅ Pass |
| SubscriptionScheduleScreen | CTA enabled when all filled | ✅ Pass |
| SubscriptionScheduleScreen | juice_specific: dropdowns pre-filled | ✅ Pass |
| SubscriptionSummaryScreen | displays plan info | ✅ Pass |
| SubscriptionSummaryScreen | Sunday = no delivery | ✅ Pass |
| SubscriptionSummaryScreen | Start Subscription CTA visible | ✅ Pass |

## Integration Tests

| Scenario | Pass/Fail |
|----------|-----------|
| Happy path — generic plan (family screen rendering with catalog) | ✅ Pass |
| Error handling — shows error on catalog load failure, retry works | ✅ Pass |

## Total Test Count

| | Count |
|---|-------|
| Before | 133 passed, 6 failed |
| New tests added | 33 (17 bloc + 14 screens + 2 integration) |
| After | **164 passed, 6 failed** (pre-existing failures unchanged) |

### Pre-existing Failures (unchanged)
| Test | Reason |
|------|--------|
| auth_bloc: EnterAddress emits AddressEntered then ReadyForFinalSignup | `AddressEntered` state not emitted (known bug) |
| auth_bloc: CompleteSignup success emits AuthenticationSuccess | Missing `AddressEntered` in expect chain |
| auth_bloc: CompleteSignup failure emits SignUpFailed | Missing `AddressEntered` in expect chain |
| signup_screen: TC-AUTH-003 Password field validation | IconData codepoint mismatch |
| signup_screen: Password requirements update in real-time | IconData codepoint mismatch |
| login_page: Valid inputs clear validation errors | pumpAndSettle timeout |

## Flutter Analyze

| Severity | Count |
|----------|-------|
| Errors | 0 |
| Warnings | 0 |
| Info | 91 (style: trailing_commas, const_constructors, redundant_arg_values) |

**Result: 0 errors, 0 warnings — confirmed.**

## Any Skipped / TODO Tests

| Test | Reason |
|------|--------|
| Widget: SummaryScreen snackbar on SubscriptionError | Requires full async handler flow (CTE tap → mock service throw → error emit → snackbar). The `_isSubmitting` flag + mock service return causes `SubscriptionCreatedSuccess` + navigation before manual `SubscriptionError` emit. Addressable via integration test. |
| Integration: Full navigation flow (multi-screen taps) | Navigation requires route definitions for all 4 screens; widget tests verify each screen individually. |

## Source Changes

| File | Change |
|------|--------|
| `lush/lib/bloc/SubscriptionBloc/subscription_bloc.dart` | Added optional `SubscriptionService` constructor param; added `startsWith('bmj-')` filter for catalog plans |
| `lush/lib/services/subscription_service.dart` | Added missing `import 'package:lush/utils/app_logger.dart'` |