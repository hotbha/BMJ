# BookMyJuice Test Registry — Test-to-Requirement Traceability

**Document Version:** 1.0  
**Last Updated:** 2026-06-10  
**Total Test Cases:** 368  
**Status:** ✅ 100% Passing

---

## Purpose

This document maps each test file to the functional requirements and quality attributes it covers, providing end-to-end traceability from business requirements to automated tests.

---

## Traceability Matrix

| ID | Requirement / Feature | Test File(s) | Test Count | BLoC | Coverage |
|----|----------------------|--------------|------------|------|----------|
| REQ-AUTH-01 | User sign-in (email/password) | `test/unit/bloc/auth_bloc_test.dart` | 21 | AuthBloc | ✅ |
| REQ-AUTH-02 | User sign-up / registration | `test/widgets/signup_screen_test.dart` | 10 | AuthBloc | ✅ |
| REQ-AUTH-03 | Input validation (email, phone, password) | `test/widgets/signup_validation_test.dart` | 19 | AuthBloc | ✅ |
| REQ-AUTH-04 | Google sign-in | `test/unit/bloc/auth_bloc_test.dart` | 2 | AuthBloc | ✅ |
| REQ-AUTH-05 | Phone OTP sign-in | `test/unit/bloc/auth_bloc_test.dart` | 2 | AuthBloc | ✅ |
| REQ-AUTH-06 | Forgot password flow | `test/unit/bloc/auth_bloc_test.dart` | 2 | AuthBloc | ✅ |
| REQ-AUTH-07 | Sign-out | `test/unit/bloc/auth_bloc_test.dart` | 2 | AuthBloc | ✅ |
| REQ-AUTH-08 | Login page UI | `test/widget/screens/login_page_test.dart` | 21 | AuthBloc | ✅ |
| REQ-CART-01 | View cart items | `test/unit/bloc/cart_bloc_test.dart` | 3 | CartBloc | ✅ |
| REQ-CART-01 | Cart API service | `test/unit/services/cart_service_test.dart` | 19 | — | ✅ |
| REQ-CART-02 | Add item to cart | `test/unit/bloc/cart_bloc_test.dart` | 2 | CartBloc | ✅ |
| REQ-CART-03 | Remove item from cart | `test/unit/bloc/cart_bloc_test.dart` | 2 | CartBloc | ✅ |
| REQ-CART-04 | Update item quantity | `test/unit/bloc/cart_bloc_test.dart` | 2 | CartBloc | ✅ |
| REQ-CART-05 | Clear cart | `test/unit/bloc/cart_bloc_test.dart` | 1 | CartBloc | ✅ |
| REQ-CART-06 | Apply / remove coupon | `test/unit/bloc/cart_bloc_test.dart` | 2 | CartBloc | ✅ |
| REQ-PROD-01 | Browse product catalog | `test/unit/bloc/product_catalog_bloc_test.dart` | 6 | ProductCatalogBloc | ✅ |
| REQ-PROD-02 | Product details | `test/unit/bloc/products_bloc_test.dart` | 4 | ProductsBloc | ✅ |
| REQ-PROD-03 | Product repository (API + cache) | `test/unit/repositories/products_repository_test.dart` | 17 | — | ✅ |
| REQ-PROD-04 | Product model serialization | `test/unit/models/products_model_test.dart` | 3 | — | ✅ |
| REQ-SUB-01 | View subscription plans | `test/subscription_bloc_test.dart` | 3 | SubscriptionBloc | ✅ |
| REQ-SUB-02 | Create subscription | `test/subscription_bloc_test.dart` | 2 | SubscriptionBloc | ✅ |
| REQ-SUB-02 | Subscription API service | `test/unit/services/subscription_service_test.dart` | 23 | — | ✅ |
| REQ-SUB-03 | Cancel subscription | `test/subscription_bloc_test.dart` | 1 | SubscriptionBloc | ✅ |
| REQ-SUB-04 | Pause / resume subscription | `test/subscription_bloc_test.dart` | 3 | SubscriptionBloc | ✅ |
| REQ-SUB-05 | Modify subscription schedule | `test/subscription_bloc_test.dart` | 1 | SubscriptionBloc | ✅ |
| REQ-SUB-06 | Subscription history | `test/subscription_bloc_test.dart` | 2 | SubscriptionBloc | ✅ |
| REQ-SUB-07 | Subscription screens UI | `test/subscription_screens_test.dart` | 14 | SubscriptionBloc | ✅ |
| REQ-ORD-01 | Place order | `test/unit/services/order_service_test.dart` | 3 | — | ✅ |
| REQ-ORD-01 | Order flow integration | `test/order_flow_test.dart` | 6 | — | ✅ |
| REQ-ORD-02 | Order history | `test/bloc/order_history_test.dart` | 2 | OrderHistoryBloc | ✅ |
| REQ-ORD-03 | Order details | `test/widget/order_history_widget_test.dart` | 2 | OrderHistoryBloc | ✅ |
| REQ-ORD-04 | Order model serialization | `test/unit/models/order_model_test.dart` | 17 | — | ✅ |
| REQ-USER-01 | User profile management | `test/unit/bloc/user_bloc_test.dart` | 6 | UserBloc | ✅ |
| REQ-NOTIF-01 | Notification list | `test/unit/bloc/notification_bloc_test.dart` | 4 | NotificationBloc | ✅ |
| REQ-NOTIF-02 | Mark notification as read | `test/unit/bloc/notification_bloc_test.dart` | 2 | NotificationBloc | ✅ |
| REQ-NOTIF-03 | Delete notification | `test/unit/bloc/notification_bloc_test.dart` | 2 | NotificationBloc | ✅ |
| REQ-NOTIF-04 | Notification model serialization | `test/unit/models/notification_model_test.dart` | 9 | — | ✅ |
| REQ-REF-01 | Referral info display | `test/bloc/referral_bloc_test.dart` | 1 | ReferralBloc | ✅ |
| REQ-REF-01 | Referral screen UI | `test/screens/referral_screen_test.dart` | 5 | ReferralBloc | ✅ |
| REQ-REF-02 | Submit referral code | `test/unit/repositories/referral_repository_test.dart` | 3 | ReferralBloc | ✅ |
| REQ-REF-03 | Referral rewards | `test/unit/repositories/referral_repository_test.dart` | 1 | ReferralBloc | ✅ |
| REQ-REF-04 | Referral info model | `test/unit/models/referral_info_test.dart` | 7 | — | ✅ |
| REQ-THEME-01 | Light/dark theme values | `test/theme/app_theme_test.dart` | 26 | — | ✅ |
| REQ-THEME-02 | Theme toggle | `test/theme/theme_cubit_test.dart` | 12 | ThemeCubit | ✅ |
| REQ-SMOKE-01 | App renders without crash | `test/widget_test.dart` | 1 | — | ✅ |

---

## Coverage Summary

| Domain | Requirements Mapped | Test Files | Total Tests | Status |
|--------|---------------------|------------|-------------|--------|
| Authentication | 8 | 4 | 75 | ✅ |
| Cart | 6 | 2 | 29 | ✅ |
| Products | 4 | 3 | 26 | ✅ |
| Subscriptions | 7 | 3 | 37 | ✅ |
| Orders | 4 | 4 | 28 | ✅ |
| User Profile | 1 | 1 | 6 | ✅ |
| Notifications | 4 | 2 | 17 | ✅ |
| Referrals | 4 | 3 | 16 | ✅ |
| Theme | 2 | 2 | 38 | ✅ |
| Smoke | 1 | 1 | 1 | ✅ |
| **Total** | **41** | **28** | **368** | **✅ 100%** |

---

## Untested Areas (Gaps)

| Area | Gap | Priority | Action Item |
|------|-----|----------|-------------|
| Checkout | Payment gateway integration not tested | High | Add payment service tests |
| Delivery | Slot selection, address management | Medium | Add delivery bloc tests |
| Admin | Admin panels, order management | Low | Future phase |
| E2E | Full end-to-end user journeys | High | Patrol tests (in progress) |

---

*Document Maintained By:* QA Team  
*Last Review:* 2026-06-10  
*Next Review:* 2026-07-10