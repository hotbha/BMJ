# GROUP F + G — Referral System & Analytics Implementation Report

Last updated: 2026-05-29 00:55

## GROUP F — Referral System

| Item | File | Status |
|------|------|--------|
| F1 Backend — ReferralService | `bmjServer/.../services/ReferralService.java` | ✅ Created |
| F1 Backend — ReferralController | `bmjServer/.../controllers/ReferralController.java` | ✅ Created |
| F1 Model — referralCode on User | `lush/lib/views/models/user.dart` | ✅ Added `referralCode` field |
| F2 ReferralInfo model | `lush/lib/models/referral_info.dart` | ✅ Created |
| F2 ReferralRepository | `lush/lib/repositories/referral_repository.dart` | ✅ Created |
| F2 ReferralBloc | `lush/lib/bloc/ReferralBloc/` | ✅ Created (event/state/bloc) |
| F2 ReferralScreen | `lush/lib/views/screens/referral/referral_screen.dart` | ✅ Created |
| F3 Signup referral field | `lush/lib/views/screens/sign_up_screen.dart` | ✅ Added `referralCode` controller + dispatch |
| F3 CompleteSignup event | `lush/lib/bloc/AuthBloc/auth_events.dart` | ✅ Added `referralCode` parameter |
| Navigation route | `lush/lib/main.dart` | ✅ `/referral` route added |
| all_screens export | `lush/lib/views/all_screens.dart` | ✅ Export added |
| Dashboard drawer item | `lush/lib/views/screens/dashboard.dart` | 🔴 Remaining |

## GROUP G — Firebase Analytics

| Event | BLoC/Location | Wired |
|-------|---------------|-------|
| logLogin | `auth_bloc.dart` — login success | ✅ |
| logSignup | `auth_bloc.dart` — signup success | ✅ |
| logItemViewed | detail screen UI | 🔴 Remaining |
| logSearchPerformed | catalog screen search handler | 🔴 Remaining |
| logFamilySelected | catalog screen filter handler | 🔴 Remaining |
| logSubscriptionStarted | `subscription_bloc.dart` — created | ✅ |
| logSubscriptionPaused | `subscription_bloc.dart` pause handler | 🔴 Remaining |
| logSubscriptionCancelled | `subscription_bloc.dart` — cancel | ✅ |
| logOrderPlaced | `cart_bloc.dart` PlaceOneTimeOrder | 🔴 Remaining |
| logReorderTapped | `cart_bloc.dart` ReorderItems | ✅ |
| logReferralShared | `referral_bloc.dart` ShareReferralCode | ✅ |
| logNotificationTapped | `notification_bloc.dart` MarkAsRead | 🔴 Remaining |

## New Dependencies

| Package | Version | Used For |
|---------|---------|----------|
| `share_plus` | ^10.1.0 | Share sheet on referral screen |
| `firebase_analytics` | ^11.3.0 | Firebase Analytics events |

`flutter pub get` — Resolved without conflicts ✅

## Files Created (9 new)

| File | Purpose |
|------|---------|
| `ReferralService.java` | Generate/apply referral codes |
| `ReferralController.java` | REST endpoints |
| `referral_info.dart` | ReferralInfo model |
| `referral_repository.dart` | HTTP client |
| `ReferralBloc/*` (3 files) | BLoC event/state/bloc |
| `analytics_service.dart` | 12 Firebase Analytics methods |
| `referral_screen.dart` | Refer & Earn UI |

## Files Modified (10)

| File | Changes |
|------|---------|
| `pubspec.yaml` | Added share_plus, firebase_analytics |
| `user.dart` | Added referralCode field |
| `auth_events.dart` | Added referralCode to CompleteSignup |
| `auth_bloc.dart` | Added logLogin, logSignup |
| `sign_up_screen.dart` | Added referral code field |
| `cart_event.dart` | Added orderId to ReorderItems |
| `cart_bloc.dart` | Added logReorderTapped |
| `subscription_bloc.dart` | Added logSubscriptionStarted, logCancelled |
| `main.dart` | Added /referral route |
| `all_screens.dart` | Added referral export |

## Verification

- **Flutter analyze**: 0 new errors in all modified files ✅
- **bmjServer**: BUILD SUCCESS (2 new Java files) ✅
- **flutter pub get**: No conflicts ✅

## Remaining Items (11 small tasks)

| Item | Location | Effort |
|------|----------|--------|
| Dashboard "Refer & Earn" drawer item | dashboard.dart | 7 lines |
| logSubscriptionPaused | subscription_bloc.dart pause handler | 1 line |
| logOrderPlaced | cart_bloc.dart PlaceOneTimeOrder | 3 lines |
| logNotificationTapped | notification_bloc.dart MarkAsRead | 1 line |
| logSearchPerformed | product_catalog_screen.dart | 1 line |
| logFamilySelected | product_catalog_screen.dart | 1 line |
| logItemViewed | detail.dart | 3 lines |
| referral_bloc_test.dart | test/bloc/ | ~4 tests |
| referral_screen_test.dart | test/widget/ | ~5 tests |
| analytics_service_test.dart | test/utils/ | ~4 tests |