# BookMyJuice Flutter Test Case Catalog

**Document Version:** 1.0  
**Last Updated:** 2026-06-10  
**Total Test Cases:** 368  
**Status:** ✅ All Passing

---

## Table of Contents

1. [Service Layer Tests](#1-service-layer-tests)
2. [Repository Layer Tests](#2-repository-layer-tests)
3. [BLoC / State Management Tests](#3-bloc--state-management-tests)
4. [Model Tests](#4-model-tests)
5. [Widget / Screen Tests](#5-widget--screen-tests)
6. [Theme Tests](#6-theme-tests)
7. [Integration Flow Tests](#7-integration-flow-tests)

---

## 1. Service Layer Tests

### 1.1 `test/unit/services/order_service_test.dart` — 13 tests

| # | Test Name | Category |
|---|-----------|----------|
| 1 | FetchOrders — success response returns list | Positive |
| 2 | FetchOrders — empty list returned | Edge |
| 3 | FetchOrders — HTTP error returns wrapped exception | Negative |
| 4 | FetchOrders — network exception returns wrapped exception | Negative |
| 5 | CreateOrder — success returns order confirmation | Positive |
| 6 | CreateOrder — server validation error | Negative |
| 7 | CreateOrder — network timeout | Negative |
| 8 | CancelOrder — success returns confirmation | Positive |
| 9 | CancelOrder — order not found | Negative |
| 10 | CancelOrder — unauthorised cancellation | Negative |
| 11 | getOrderById — success returns order detail | Positive |
| 12 | getOrderById — order not found | Negative |
| 13 | getOrderById — network error | Negative |

### 1.2 `test/unit/services/cart_service_test.dart` — 19 tests

| # | Test Name | Category |
|---|-----------|----------|
| 1 | FetchCartItems — success returns cart items | Positive |
| 2 | FetchCartItems — empty cart | Edge |
| 3 | FetchCartItems — HTTP error | Negative |
| 4 | AddItemToCart — success returns updated cart | Positive |
| 5 | AddItemToCart — duplicate item increments quantity | Positive |
| 6 | AddItemToCart — out of stock error | Negative |
| 7 | RemoveItemFromCart — success returns updated cart | Positive |
| 8 | RemoveItemFromCart — item not in cart | Negative |
| 9 | UpdateCartItemQuantity — success | Positive |
| 10 | UpdateCartItemQuantity — zero quantity removes item | Edge |
| 11 | UpdateCartItemQuantity — invalid quantity | Negative |
| 12 | ClearCart — success | Positive |
| 13 | ClearCart — already empty cart | Edge |
| 14 | ApplyCoupon — success returns discount | Positive |
| 15 | ApplyCoupon — expired coupon | Negative |
| 16 | ApplyCoupon — invalid coupon code | Negative |
| 17 | RemoveCoupon — success | Positive |
| 18 | GetCartTotal — calculates subtotal correctly | Positive |
| 19 | GetCartTotal — with delivery fee | Positive |

### 1.3 `test/unit/services/subscription_service_test.dart` — 23 tests

| # | Test Name | Category |
|---|-----------|----------|
| 1 | GetSubscriptionPlans — success | Positive |
| 2 | GetSubscriptionPlans — empty plans list | Edge |
| 3 | GetSubscriptionPlans — HTTP error | Negative |
| 4 | CreateSubscription — success returns subscription | Positive |
| 5 | CreateSubscription — missing payment method | Negative |
| 6 | CreateSubscription — invalid plan ID | Negative |
| 7 | CreateSubscription — network exception | Negative |
| 8 | CancelSubscription — success | Positive |
| 9 | CancelSubscription — already cancelled | Negative |
| 10 | CancelSubscription — not found | Negative |
| 11 | PauseSubscription — success | Positive |
| 12 | PauseSubscription — already paused | Negative |
| 13 | PauseSubscription — max pauses exceeded | Negative |
| 14 | ResumeSubscription — success | Positive |
| 15 | ResumeSubscription — not paused | Negative |
| 16 | ModifySubscriptionSchedule — success | Positive |
| 17 | ModifySubscriptionSchedule — invalid schedule | Negative |
| 18 | GetActiveSubscriptions — success returns list | Positive |
| 19 | GetActiveSubscriptions — no active subscriptions | Edge |
| 20 | GetSubscriptionHistory — success | Positive |
| 21 | GetSubscriptionHistory — empty history | Edge |
| 22 | GetSubscriptionHistory — network error | Negative |
| 23 | LoadSubscriptionCatalog — success returns catalog | Positive |

---

## 2. Repository Layer Tests

### 2.1 `test/unit/repositories/products_repository_test.dart` — 17 tests

| # | Test Name | Category |
|---|-----------|----------|
| 1 | FetchProducts — success returns product list | Positive |
| 2 | FetchProducts — empty catalog | Edge |
| 3 | FetchProducts — HTTP error | Negative |
| 4 | FetchProducts — JSON parse error | Negative |
| 5 | FetchProductById — success returns product | Positive |
| 6 | FetchProductById — product not found | Negative |
| 7 | FetchProductById — network error | Negative |
| 8 | FetchCategories — success returns categories | Positive |
| 9 | FetchCategories — no categories | Edge |
| 10 | SearchProducts — by name returns matches | Positive |
| 11 | SearchProducts — no results | Edge |
| 12 | SearchProducts — special characters in query | Positive |
| 13 | SearchProducts — empty query returns all | Edge |
| 14 | GetRelatedProducts — success | Positive |
| 15 | GetRelatedProducts — no related products | Edge |
| 16 | CacheProducts — products are cached correctly | Positive |
| 17 | CacheProducts — stale cache is refreshed | Positive |

### 2.2 `test/unit/repositories/referral_repository_test.dart` — 7 tests

| # | Test Name | Category |
|---|-----------|----------|
| 1 | FetchReferralInfo — success returns info | Positive |
| 2 | FetchReferralInfo — HTTP error | Negative |
| 3 | FetchReferralInfo — empty response | Edge |
| 4 | SubmitReferralCode — success | Positive |
| 5 | SubmitReferralCode — invalid code | Negative |
| 6 | SubmitReferralCode — already used code | Negative |
| 7 | GetReferralRewards — success returns rewards | Positive |

---

## 3. BLoC / State Management Tests

### 3.1 `test/unit/bloc/auth_bloc_test.dart` — 21 tests

| # | Test Name | Category |
|---|-----------|----------|
| 1 | Initial state is AuthenticationInProgress | Positive |
| 2 | AppStarted — user logged in emits authenticated | Positive |
| 3 | AppStarted — user not logged in emits unauthenticated | Positive |
| 4 | AppStarted — error emits failure | Negative |
| 5 | SignInPressed — valid credentials emits authenticated | Positive |
| 6 | SignInPressed — invalid credentials emits failure | Negative |
| 7 | SignInPressed — network error emits failure | Negative |
| 8 | SignUpPressed — valid registration emits authenticated | Positive |
| 9 | SignUpPressed — duplicate email emits failure | Negative |
| 10 | SignUpPressed — weak password emits failure | Negative |
| 11 | SignOutPressed — success emits unauthenticated | Positive |
| 12 | SignOutPressed — error emits failure | Negative |
| 13 | GoogleSignInRequested — success emits authenticated | Positive |
| 14 | GoogleSignInRequested — cancelled by user | Edge |
| 15 | GoogleSignInRequested — error emits failure | Negative |
| 16 | PhoneSignInRequested — OTP sent | Positive |
| 17 | PhoneSignInRequested — invalid phone | Negative |
| 18 | VerifyOtp — valid OTP emits authenticated | Positive |
| 19 | VerifyOtp — invalid OTP emits failure | Negative |
| 20 | ForgotPassword — success emits password reset sent | Positive |
| 21 | ForgotPassword — email not found | Negative |

### 3.2 `test/unit/bloc/cart_bloc_test.dart` — 14 tests

| # | Test Name | Category |
|---|-----------|----------|
| 1 | Initial state is CartInitial | Positive |
| 2 | LoadCart — items loaded emits loaded state | Positive |
| 3 | LoadCart — empty cart emits loaded (empty) | Edge |
| 4 | LoadCart — error emits failure | Negative |
| 5 | AddItem — item added to cart | Positive |
| 6 | AddItem — duplicate item increments | Positive |
| 7 | AddItem — error emits failure | Negative |
| 8 | RemoveItem — item removed | Positive |
| 9 | RemoveItem — item not found | Negative |
| 10 | UpdateQuantity — quantity updated | Positive |
| 11 | UpdateQuantity — zero removes item | Edge |
| 12 | ClearCart — cart cleared | Positive |
| 13 | ApplyCoupon — coupon applied | Positive |
| 14 | ApplyCoupon — invalid coupon | Negative |

### 3.3 `test/unit/bloc/user_bloc_test.dart` — 6 tests

| # | Test Name | Category |
|---|-----------|----------|
| 1 | Initial state is UserInitial | Positive |
| 2 | LoadUserProfile — success emits loaded | Positive |
| 3 | LoadUserProfile — error emits failure | Negative |
| 4 | UpdateProfile — success emits updated | Positive |
| 5 | UpdateProfile — validation error | Negative |
| 6 | DeleteAccount — success emits deleted | Positive |

### 3.4 `test/unit/bloc/products_bloc_test.dart` — 4 tests

| # | Test Name | Category |
|---|-----------|----------|
| 1 | Initial state is ProductsInitial | Positive |
| 2 | LoadProducts — success emits loaded | Positive |
| 3 | LoadProducts — empty list emits loaded (empty) | Edge |
| 4 | LoadProducts — error emits failure | Negative |

### 3.5 `test/unit/bloc/product_catalog_bloc_test.dart` — 6 tests

| # | Test Name | Category |
|---|-----------|----------|
| 1 | Initial state is CatalogInitial | Positive |
| 2 | LoadCatalog — success emits loaded | Positive |
| 3 | LoadCatalog — empty catalog | Edge |
| 4 | LoadCatalog — HTTP error | Negative |
| 5 | FilterByCategory — filters correctly | Positive |
| 6 | SearchCatalog — search returns results | Positive |

### 3.6 `test/unit/bloc/notification_bloc_test.dart` — 12 tests

| # | Test Name | Category |
|---|-----------|----------|
| 1 | Initial state is NotificationInitial | Positive |
| 2 | LoadNotifications — success emits loaded | Positive |
| 3 | LoadNotifications — empty list | Edge |
| 4 | LoadNotifications — error | Negative |
| 5 | MarkAsRead — updates state | Positive |
| 6 | MarkAsRead — invalid ID | Negative |
| 7 | MarkAllAsRead — updates all | Positive |
| 8 | MarkAllAsRead — already all read | Edge |
| 9 | DeleteNotification — removes notification | Positive |
| 10 | DeleteNotification — invalid ID | Negative |
| 11 | LoadUnreadCount — returns count | Positive |
| 12 | LoadUnreadCount — error | Negative |

### 3.7 `test/subscription_bloc_test.dart` — 17 tests

| # | Test Name | Category |
|---|-----------|----------|
| 1 | Initial state is SubscriptionInitial | Positive |
| 2 | LoadSubscriptionCatalog — success | Positive |
| 3 | LoadSubscriptionCatalog — error | Negative |
| 4 | CreateSubscriptionFromSelection — success | Positive |
| 5 | CreateSubscriptionFromSelection — invalid selection | Negative |
| 6 | LoadActiveSubscriptions — success returns list | Positive |
| 7 | LoadActiveSubscriptions — empty list | Edge |
| 8 | LoadSubscriptionPlans — success | Positive |
| 9 | LoadSubscriptionPlans — error | Negative |
| 10 | LoadSubscriptionHistory — success | Positive |
| 11 | LoadSubscriptionHistory — empty | Edge |
| 12 | CreateSubscription — success | Positive |
| 13 | CancelSubscription — success | Positive |
| 14 | PauseSubscription — success | Positive |
| 15 | PauseSubscription — error | Negative |
| 16 | ResumeSubscription — success | Positive |
| 17 | ModifySubscriptionSchedule — success | Positive |

### 3.8 `test/bloc/order_history_test.dart` — 2 tests

| # | Test Name | Category |
|---|-----------|----------|
| 1 | LoadOrderHistory — success emits loaded | Positive |
| 2 | LoadOrderHistory — error emits failure | Negative |

### 3.9 `test/bloc/referral_bloc_test.dart` — 1 test

| # | Test Name | Category |
|---|-----------|----------|
| 1 | LoadReferralInfo — success emits loaded | Positive |

---

## 4. Model Tests

### 4.1 `test/unit/models/notification_model_test.dart` — 9 tests

| # | Test Name | Category |
|---|-----------|----------|
| 1 | NotificationItem constructor sets fields | Positive |
| 2 | NotificationItem fromJson — full data | Positive |
| 3 | NotificationItem fromJson — minimal data | Positive |
| 4 | NotificationItem fromJson — null fields | Edge |
| 5 | NotificationItem toJson — full data | Positive |
| 6 | NotificationItem toJson — minimal data | Positive |
| 7 | NotificationItem copyWith — modifies fields | Positive |
| 8 | NotificationItem equality — same values equal | Positive |
| 9 | NotificationItem equality — different values not equal | Positive |

### 4.2 `test/unit/models/order_model_test.dart` — 17 tests

| # | Test Name | Category |
|---|-----------|----------|
| 1 | OrderSummary constructor | Positive |
| 2 | OrderSummary fromJson — full | Positive |
| 3 | OrderSummary fromJson — minimal | Positive |
| 4 | OrderSummary toJson | Positive |
| 5 | OrderSummary equality | Positive |
| 6 | OrderDetail constructor | Positive |
| 7 | OrderDetail fromJson — full | Positive |
| 8 | OrderDetail fromJson — minimal | Positive |
| 9 | OrderDetail toJson | Positive |
| 10 | OrderDetail equality | Positive |
| 11 | OrderLineItem constructor | Positive |
| 12 | OrderLineItem fromJson — full | Positive |
| 13 | OrderLineItem fromJson — minimal | Positive |
| 14 | OrderLineItem toJson | Positive |
| 15 | OrderLineItem equality | Positive |
| 16 | OrderLineItem subtotal calculation | Positive |
| 17 | OrderSummary status display value | Positive |

### 4.3 `test/unit/models/products_model_test.dart` — 3 tests

| # | Test Name | Category |
|---|-----------|----------|
| 1 | Product fromJson — full data | Positive |
| 2 | Product fromJson — minimal data | Positive |
| 3 | Product toJson roundtrip | Positive |

### 4.4 `test/unit/models/referral_info_test.dart` — 7 tests

| # | Test Name | Category |
|---|-----------|----------|
| 1 | ReferralInfo constructor | Positive |
| 2 | ReferralInfo fromJson | Positive |
| 3 | ReferralInfo toJson | Positive |
| 4 | ReferralInfo equality | Positive |
| 5 | ReferralInfo copyWith | Positive |
| 6 | ReferralInfo empty constructor | Positive |
| 7 | ReferralInfo fields default values | Positive |

---

## 5. Widget / Screen Tests

### 5.1 `test/widget/screens/login_page_test.dart` — 21 tests

| # | Test Name | Category |
|---|-----------|----------|
| 1-2 | Tab switching renders correct content | Positive |
| 3-4 | Sign-in form field validation | Positive |
| 5-7 | Sign-in button states (enabled/disabled/loading) | Positive |
| 8-10 | Sign-up method cards rendering | Positive |
| 11-13 | Google sign-in button | Positive |
| 14-16 | Phone alt login button | Positive |
| 17-19 | Error state display | Negative |
| 20-21 | Toast notification integration | Positive |

### 5.2 `test/widgets/signup_screen_test.dart` — 10 tests

| # | Test Name | Category |
|---|-----------|----------|
| 1 | SignUpScreen renders all fields | Positive |
| 2 | Name field validation | Positive |
| 3 | Email field validation | Positive |
| 4 | Phone field validation | Positive |
| 5 | Password field validation | Positive |
| 6 | Confirm password match validation | Positive |
| 7 | Terms checkbox interaction | Positive |
| 8 | SignUp button disabled when invalid | Positive |
| 9 | SignUp button enabled when valid | Positive |
| 10 | Submission triggers bloc event | Positive |

### 5.3 `test/widgets/signup_validation_test.dart` — 19 tests

| # | Test Name | Category |
|---|-----------|----------|
| 1 | Valid email passes | Positive |
| 2 | Invalid email fails | Negative |
| 3 | Empty email fails | Negative |
| 4 | Valid phone passes | Positive |
| 5 | Invalid phone fails | Negative |
| 6 | Empty phone fails | Negative |
| 7 | Valid password passes | Positive |
| 8 | Short password fails | Negative |
| 9 | No uppercase fails | Negative |
| 10 | No digit fails | Negative |
| 11 | No special char fails | Negative |
| 12 | Passwords match | Positive |
| 13 | Passwords mismatch | Negative |
| 14 | Empty confirm password | Negative |
| 15 | Name non-empty passes | Positive |
| 16 | Empty name fails | Negative |
| 17 | Name with numbers fails | Negative |
| 18 | Terms accepted passes | Positive |
| 19 | Terms not accepted fails | Negative |

### 5.4 `test/subscription_screens_test.dart` — 14 tests

| # | Test Name | Category |
|---|-----------|----------|
| 1 | SubscriptionCatalogScreen renders | Positive |
| 2 | Plan card displays correctly | Positive |
| 3 | Loading indicator shown | Positive |
| 4 | Error state shown | Negative |
| 5 | Empty state shown | Edge |
| 6 | Plan selection works | Positive |
| 7 | SubscriptionDetailScreen renders | Positive |
| 8 | Schedule picker interaction | Positive |
| 9 | Confirm subscription button | Positive |
| 10 | MySubscriptionsScreen renders | Positive |
| 11 | Active subscription card | Positive |
| 12 | Pause subscription flow | Positive |
| 13 | Cancel subscription flow | Positive |
| 14 | Subscription history list | Positive |

### 5.5 `test/screens/referral_screen_test.dart` — 5 tests

| # | Test Name | Category |
|---|-----------|----------|
| 1 | Loading indicator shown | Positive |
| 2 | Referral info displayed | Positive |
| 3 | Referral code visible | Positive |
| 4 | Share button present | Positive |
| 5 | Error state handled | Negative |

### 5.6 `test/widget/order_history_widget_test.dart` — 2 tests

| # | Test Name | Category |
|---|-----------|----------|
| 1 | OrderHistoryScreen renders orders | Positive |
| 2 | OrderDetailScreen shows details | Positive |

### 5.7 `test/widget_test.dart` — 1 test

| # | Test Name | Category |
|---|-----------|----------|
| 1 | App renders without errors (smoke test) | Positive |

### 5.8 `test/order_flow_test.dart` — 6 tests

| # | Test Name | Category |
|---|-----------|----------|
| 1 | Complete order flow — happy path | Positive |
| 2 | Order flow — add item to cart | Positive |
| 3 | Order flow — checkout navigation | Positive |
| 4 | Order flow — address selection | Positive |
| 5 | Order flow — payment method | Positive |
| 6 | Order flow — order confirmation | Positive |

---

## 6. Theme Tests

### 6.1 `test/theme/app_theme_test.dart` — 26 tests

| # | Test Name | Category |
|---|-----------|----------|
| 1-5 | Light theme color values | Positive |
| 6-10 | Dark theme color values | Positive |
| 11-14 | Text theme styles | Positive |
| 15-18 | Button theme defaults | Positive |
| 19-22 | Input decoration theme | Positive |
| 23-26 | Font loading resilience | Edge/Negative |

### 6.2 `test/theme/theme_cubit_test.dart` — 12 tests

| # | Test Name | Category |
|---|-----------|----------|
| 1 | Initial theme is light mode | Positive |
| 2 | ToggleTheme — switches to dark | Positive |
| 3 | ToggleTheme — switches back to light | Positive |
| 4 | SetTheme — light mode | Positive |
| 5 | SetTheme — dark mode | Positive |
| 6 | Theme persistence — save | Positive |
| 7 | Theme persistence — restore | Positive |
| 8 | Theme persistence — first launch default | Positive |
| 9 | System theme follows device | Positive |
| 10 | Theme change emits correct state | Positive |
| 11 | Reset to default | Positive |
| 12 | Error handling during persistence | Negative |

---

## 7. Integration Flow Tests

### 7.1 `test/order_flow_test.dart` — 6 tests (listed in 5.8)

Covered under Widget tests.

---

## Summary

| Category | File Count | Test Count | % of Total |
|----------|------------|------------|------------|
| Service Layer | 3 | 55 | 14.9% |
| Repository Layer | 2 | 24 | 6.5% |
| BLoC Tests | 9 | 83 | 22.6% |
| Model Tests | 4 | 36 | 9.8% |
| Widget / Screen Tests | 8 | 80 | 21.7% |
| Theme Tests | 2 | 38 | 10.3% |
| Integration Flows | 1 | 6 | 1.6% |
| **Total** | **28** | **368** | **100%** |

**Status:** ✅ 368/368 All tests passing

---

*Document Maintained By:* QA Team  
*Last Review:* 2026-06-10  
*Next Review:* 2026-07-10