# BookMyJuice — Product Alignment Report

**Audience:** Product, Engineering, Design
**Scope:** Alignment between (1) Flutter app screens & services, (2) Spring Boot REST API, (3) SRS/BRD/Functional-Spec documentation, (4) Chargebee integration, (5) Stitch design artifacts.
**Nature of this document:** Read-only analysis. **No source code, config, or design files were modified.**
**Date:** 15 October 2026
**Status:** Baseline alignment audit
**Post-audit addendum:** **§J** records the V1 launch freeze executed on 15 October 2026, including the code changes made *after* this audit, their verification results, and the findings it resolved.

### Contents

| Section | Topic |
| :--- | :--- |
| 0 | Method & evidence base |
| A | Flutter screen inventory — what is actually shipped |
| B | Stitch design → Flutter screen mapping |
| C | SRS / documentation → implementation alignment |
| D | Dead, duplicate & legacy artifacts |
| E | Chargebee integration alignment |
| F | API surface: server vs client vs documentation |
| G | Prioritised alignment actions (P0 / P1 / P2) |
| H | Summary scorecard |
| I | Appendix — reproducible verification commands |
| J | V1 launch freeze — execution & verification (addendum) |


---

## 0. Method & Evidence Base

| Artifact | Location | What was inspected |
| :--- | :--- | :--- |
| Flutter app | `x:\BMJ\lush` | `lib\main.dart` (route table + `onGenerateRoute`), `lib\get_it.dart`, 111 declared screen/widget classes across `lib\**\*.dart`, all service/repository HTTP call sites |
| Backend | `x:\BMJ\bmjServer` | 21 files in `com.bookmyjuice.controllers` (20 REST controllers + 1 empty/0-byte), 13 REST controllers in `com.bookmyjuice.controllers.webhooks`, 30 files in `com.bookmyjuice.services` |
| Docs (SRS) | `x:\BMJ\docs` | 36 documents incl. `README.md`, `API.md`, `DESIGN_SYSTEM.md`, `SUBSCRIPTIONS.md`, `BRD_Business_Requirements.md`, `FUNCTIONAL_SPEC.md`, `USE_CASES.md`, `UC-BOTTLE-TRACKING.md`, `KNOWN_ISSUES.md`, `ADR-001..004` |
| Designs | `x:\BMJ\Stitch` | 31 `code.html` + `screen.png` artifacts in 2 export folders; 2 `DESIGN.md` token sets |

### Techniques used

1. **Static route extraction** — parsed `main.dart` `routes:` map and `onGenerateRoute` switch to build the authoritative list of navigable destinations.
2. **Reachability analysis** — for every class declared as `extends StatefulWidget|StatelessWidget`, counted non-self-file textual references across `lib\**\*.dart`. A class with **0 external references** cannot be instantiated by any other file and is therefore unreachable unless it is the `runApp` root.
3. **Endpoint extraction** — regex-extracted `@RequestMapping` / `@GetMapping` / `@PostMapping` / `@PutMapping` / `@DeleteMapping` / `@PatchMapping` from every controller to produce the server-side surface.
4. **Consumption mapping** — extracted every `Uri.parse('.../api/...')` call site in Dart to produce the client-side surface, then diffed against the server-side surface.

**Caveat on reachability counts:** a few classes are reachable through `AuthWrapper` conditionals or as private children of reachable screens rather than named routes (e.g. `SignUpScreen`, `LinkGoogleAccountScreen`, `_PriceRow`). These were individually verified. `AuthWrapper` and `BookMyJuiceApp` report 0 references as a false negative — they are reachable via `runApp` in their own file.

---

## A. Flutter Screen Inventory — What Is Actually Shipped Today

**Summary: 111 declared screen/widget classes → 48 reachable screens + 13 reachable shared widgets → 50 unreachable classes.**

### A.1 Reachable screens (48 distinct screens)

**A.1.1 Authentication & onboarding (24)**

| Route | Widget | Source file |
| :--- | :--- | :--- |
| `/` | `AuthWrapper` (splash + auth gate) | `main.dart` |
| `/mobileNumberPage` | `MobileNumberPage` | `screens\enter_mobile_number.dart` |
| `/phone-login` | `PhoneLoginScreen` | `screens\phone_login_screen.dart` |
| `/otp` | `OTPLoginPage` | `screens\otp_login_page.dart` |
| `/login` | `LoginPage` | `screens\login_page.dart` |
| `/signup-method-selection` | `SignupMethodSelectionScreen` | `screens\signup_method_selection_screen.dart` |
| `/email-signup` | `EmailSignupScreen` | `screens\email_signup_screen.dart` |
| `/email-verification` | `EmailVerificationScreen` | `screens\email_verification_screen.dart` |
| `/phone-entry-after-email` | `PhoneEntryAfterEmailScreen` | `screens\phone_entry_after_email_screen.dart` |
| `/phone-signup` | `PhoneSignupScreen` | `screens\phone_signup_screen.dart` |
| `/phone-otp-verification` | `PhoneOtpVerificationScreen` | `screens\phone_otp_verification_screen.dart` |
| `/email-entry-after-phone` | `EmailEntryAfterPhoneScreen` | `screens\email_entry_after_phone_screen.dart` |
| `/email-verification-after-phone` | `EmailVerificationAfterPhoneScreen` | `screens\email_verification_after_phone_screen.dart` |
| `/google-signup` | `GoogleSignupScreen` | `screens\google_signup_screen.dart` |
| `/google-phone-entry` | `GooglePhoneEntryScreen` | `screens\google_phone_entry_screen.dart` |
| `/address-entry` | `AddressEntryScreen` | `screens\address_entry_screen.dart` |
| `/create-password` | `CreatePasswordScreen` | `screens\create_password_screen.dart` |
| `/forgotPasswordPage` | `ForgotPasswordPage` | `screens\forgot_password_page.dart` |
| `/forgot-password` | `ForgotPasswordScreen` | `screens\forgot_password_screen.dart` |
| `/reset-password-mobile-otp` | `ResetPasswordMobileScreen` | `screens\reset_password_mobile_screen.dart` |
| `/reset-password-email-code` | `ResetPasswordEmailScreen` | `screens\reset_password_email_screen.dart` |
| `/delete-account` | `DeleteAccountScreen` | `screens\delete_account_screen.dart` |
| *(AuthWrapper conditional)* | `SignUpScreen` | `screens\sign_up_screen.dart` |
| *(AuthWrapper conditional)* | `LinkGoogleAccountScreen` | `screens\link_google_account_screen.dart` |

> ⚠️ `SignUpScreen` and `LinkGoogleAccountScreen` are **not** addressable by named route — only through branches inside `AuthWrapper` (`main.dart:432`, `main.dart:437`). Deep-linking to them is impossible.



**A.1.2 Core commerce (15)**

| Route | Widget | Source file |
| :--- | :--- | :--- |
| `/dashboard`, `/menu`, `/home` | `Dashboard` | `screens\dashboard.dart` |
| *(tab)* | `HomeTab` | `screens\home_tab.dart` |
| *(tab)* | `MenuTab` | `screens\menu_tab.dart` |
| *(tab)* | `OrdersTab` | `screens\orders_tab.dart` |
| *(tab)* | `ProfileTab` | `screens\profile_tab.dart` |
| `/catalog`, `/product-catalog` | `ProductCatalogScreen` | `screens\product_catalog_screen.dart` |
| `/productDetails` | `DetailPage` | `screens\detail.dart` |
| `/cart` | `CartScreen` | `screens\cart_screen.dart` |
| `/checkout` | `CheckoutScreen` (WebView of hosted payment page) | `screens\checkout_screen.dart` |
| `/address-selection` | `AddressSelectionScreen` | `screens\address_selection_screen.dart` |
| `/delivery-slot-selection` | `DeliverySlotSelectionScreen` | `screens\delivery_slot_selection_screen.dart` |
| `/orders` | `OrderHistoryPage` | `screens\order_history_page.dart` |
| `/order-history` | `OrderHistoryScreen` | `screens\order_history_screen.dart` |
| `/order-detail` | `OrderDetailScreen` | `screens\order\order_detail_screen.dart` |
| `/invoices` | `InvoiceViewScreen` | `screens\invoice_view_screen.dart` |

**A.1.3 Subscription lifecycle (6)**

| Route | Widget | Source file |
| :--- | :--- | :--- |
| `/plan-selection` | `PlanSelectionScreen` (embeds checkout WebView) | `screens\plan_selection_screen.dart` |
| `/manage-subscriptions` | `SubscriptionManagementScreen` | `screens\subscription_management_screen.dart` |
| `/subscription-family` | `SubscriptionFamilyScreen` | `screens\subscription\subscription_family_screen.dart` |
| `/subscription-plan` | `SubscriptionPlanScreen` | `screens\subscription\subscription_plan_screen.dart` |
| `/subscription-schedule` | `SubscriptionScheduleScreen` | `screens\subscription\subscription_schedule_screen.dart` |
| `/subscription-summary` | `SubscriptionSummaryScreen` | `screens\subscription\subscription_summary_screen.dart` |

**A.1.4 Account, engagement & support (5)**

| Route | Widget | Source file |
| :--- | :--- | :--- |
| `/user-profile` | `UserProfileScreen` | `screens\user_profile_screen.dart` |
| `/myaccount` | `MyAccountPage` | `screens\my_account_page.dart` |
| `/notifications` | `NotificationsScreen` | `screens\notifications.dart` |
| `/referral` | `ReferralScreen` | `screens\referral\referral_screen.dart` |
| `/day-wise-schedule` | `DayWiseScheduleScreen` | `screens\day_wise_schedule_screen.dart` |

### A.2 Reachable shared widgets (13)

`AppCard`, `AppTextField`, `CartBadgeIcon`, `CartIcon`, `FilterOptions`, `GlassCard`, `ItemCardView`, `ItemListView`, `Menu`, `ShimmerCartItem`, `ShimmerProductCard`, `SizeSelectionModal`, `_PriceRow`.



### A.3 Screen-to-service wiring (live data paths only)

| Screen | Data path | Endpoint actually hit |
| :--- | :--- | :--- |
| `HomeTab`, `MenuTab`, `Dashboard`, `ProductCatalogScreen` | `ProductCatalogBloc` → `UserRepository.getChargeItems()` | `GET /api/test/charge-items` |
| `DetailPage`, `ItemListView` | `ItemService` → `UserRepository.getChargeItems()` | `GET /api/test/charge-items` |
| `CartScreen` | `CartBloc` → `CartRepository` → `CartService` | `/api/v1/cart/**` |
| `CheckoutScreen`, `PlanSelectionScreen` | `subscription_service.dart` (legacy) + `subscription_service_v2.dart` | `/api/test/generate_*_pricing_page`, `/api/v1/subscribe/direct`, `/api/v2/checkout/with-items` |
| `OrderHistoryScreen`, `OrderHistoryPage`, `OrdersTab` | `OrderBloc` → `OrderService` | `/api/orders/**` |
| `OrderDetailScreen` | `OrderService` | `/api/orders/{id}` |
| `InvoiceViewScreen` | `InvoiceService` | `/api/invoices/**` |
| `ReferralScreen` | `ReferralBloc` → `ReferralRepository` | `/api/referral/code`, `/api/referral/apply` |
| `AddressSelectionScreen`, `AddressEntryScreen` | address service | `/api/v1/address/**` |
| `DeliverySlotSelectionScreen` | delivery service | `/api/v1/delivery/**` |
| `NotificationsScreen` | `FirebaseNotificationService` (FCM push only) | **no REST endpoint** |
| `Dashboard` (subscription card) | `subscription_service.dart` | `GET /api/v1/subscriptions/**` |

> ⚠️ **Primary catalog defect:** the shipped catalog reads from the **test** namespace `GET /api/test/charge-items`, not from the documented `GET /api/v1/products`. See §F.3.

### A.4 Tabs and shell behaviour

`Dashboard` is a single `StatefulWidget` hosting 4 tab bodies (`HomeTab`, `MenuTab`, `OrdersTab`, `ProfileTab`). Tab switching is index-based, not route-based, so `/menu`, `/home` and `/dashboard` all render the same `Dashboard`. **There is no routeable URL for an individual tab** — a browser/deep-link user cannot land directly on Orders or Profile.

---


## B. Stitch Design → Flutter Screen Mapping

**Inventory:** 31 `code.html` design artifacts in 2 export batches under `x:\BMJ\Stitch`:

- `stitch_bookmyjuice_flutter_bloc_ui\` — 26 designs (primary batch)
- `stitch_bookmyjuice_flutter_bloc_ui (1)\` — 5 designs (additions: `notifications`, `sign_in_email_entry`, `sign_in_email_otp_verification`, `sign_in_with_google`, `sign_up_gateway`)
- 3 `DESIGN.md` token files: `vibrant_zest_architecture` (×2, duplicated across batches) and `lush_architecture` (×1)

### B.1 Design → implementation status

| # | Design folder | `<title>` | Flutter screen | Status |
| :--- | :--- | :--- | :--- | :--- |
| 1 | `address_entry_onboarding` | Address Entry | `AddressEntryScreen` | ✅ Implemented |
| 2 | `create_password` | Create Password | `CreatePasswordScreen` | ✅ Implemented |
| 3 | `create_password_step_3` | Delivery Address | `AddressEntryScreen` | ⚠️ Duplicate of #1/#5 with misleading name |
| 4 | `create_your_profile_step_1` | Sign Up | `SignUpScreen` | ⚠️ Implemented but **not routeable** |
| 5 | `delivery_address_selection` | Address Selection | `AddressSelectionScreen` | ✅ Implemented |
| 6 | `email_signup_verification` | Email Signup | `EmailSignupScreen` | ✅ Implemented |
| 7 | `google_sign_up_phone_binding` | Google Sign-Up & Phone Binding | `GoogleSignupScreen` + `GooglePhoneEntryScreen` | ⚠️ One design → two screens |
| 8 | `juice_detail_selection` | Product Detail | `DetailPage` (`/productDetails`) | ✅ Implemented |
| 9 | `link_google_account` | Link Google Account | `LinkGoogleAccountScreen` | ⚠️ Implemented but **not routeable** |
| 10 | `otp_verification` | OTP Verification | `OTPLoginPage` (`/otp`) | ✅ Implemented |
| 11 | `phone_login_entry` | Phone Login | `PhoneLoginScreen` (`/phone-login`) | ✅ Implemented |
| 12 | `referral_rewards_program` | Referral & Rewards | `ReferralScreen` (`/referral`) | ✅ Implemented |
| 13 | `shopping_cart_savings_summary` | Cart | `CartScreen` (`/cart`) | ✅ Implemented |
| 14 | `signup_method_selection` | Signup Method Selection | `SignupMethodSelectionScreen` | ✅ Implemented |
| 15 | `sign_in_email_otp_verification` | Verify Email | `EmailVerificationScreen` | ✅ Implemented |
| 16 | `sign_in_phone_entry` | Sign In | `LoginPage` | ⚠️ Overlaps #11 |
| 17 | `sign_in_phone_otp_verification` | Verify Your Number | `PhoneOtpVerificationScreen` | ✅ Implemented |
| 18 | `simplified_weekly_scheduler` | Subscription Schedule | `SubscriptionScheduleScreen` | ✅ Implemented |
| 19 | `subscription_management_portal` | Subscription Management | `SubscriptionManagementScreen` | ✅ Implemented |
| 20 | `subscription_plan_comparison` | Select Plan | `PlanSelectionScreen` + `SubscriptionPlanScreen` | ⚠️ Two screens ship, one design |
| 21 | `unified_discovery_dashboard` | Home | `Dashboard` / `HomeTab` | ✅ Implemented |
| 22 | `unified_home_dashboard` | Home | `Dashboard` / `HomeTab` | ❌ **Redundant** — same title as #21, competing designs |
| 23 | `verify_email_otp_step_1.1` | Verify Your Email | `EmailVerificationScreen`, `EmailVerificationAfterPhoneScreen` | ⚠️ Third design for same flow |
| 24 | `verify_phone_otp_step_2.1` | Verify Phone OTP - Step 2.1 | `PhoneOtpVerificationScreen` | ⚠️ Duplicate of #17 |
| 25 | `verify_phone_step_2` | Verify Phone Number | `PhoneOtpVerificationScreen` | ⚠️ Duplicate of #17 |
| 26 | `weekly_subscription_scheduler` | Subscription Schedule | `SubscriptionScheduleScreen` | ⚠️ Duplicate of #18 |
| 27 | `notifications` | Notification Centre | `NotificationCentreScreen` | ❌ **Orphaned** — class has 0 references; `/notifications` renders a different file (`notifications.dart`) |
| 28 | `sign_in_email_entry` | Sign In | `LoginPage` | ✅ Implemented |
| 29 | `sign_in_email_otp_verification` | Verify Email | `EmailVerificationScreen` | ⚠️ Duplicate of #15 (cross-batch) |
| 30 | `sign_in_with_google` | Sign In with Google | `GoogleSignupScreen` | ✅ Implemented |
| 31 | `sign_up_gateway` | Authentication | `AuthWrapper` / `SignupMethodSelectionScreen` | ⚠️ Ambiguous mapping |



### B.2 Prioritised flows with **no** Stitch design

| Flutter capability | Route | Design coverage |
| :--- | :--- | :--- |
| Order history / order list | `/orders`, `/order-history` | ❌ None |
| Order detail | `/order-detail` | ❌ None |
| Invoice viewing | `/invoices` | ❌ None |
| Delivery slot selection | `/delivery-slot-selection` | ❌ None |
| Subscription family / plan / summary drill-downs | `/subscription-family`, `/subscription-plan`, `/subscription-summary` | ❌ None (only schedule + management portal designed) |
| My Account / user profile | `/myaccount`, `/user-profile` | ❌ None |
| Delete account | `/delete-account` | ❌ None |
| Day-wise schedule | `/day-wise-schedule` | ❌ None |
| Bottle tracking | *(no route — UI is dead)* | ❌ None |
| Product search results | within `/catalog` | ❌ None |
| Dashboard tab bodies (Orders, Profile) | tab index | ❌ None |
| Pause / Cancel / Resume / Modify subscription | *(no route — UIs are dead)* | ❌ None |

### B.3 Design-token alignment — three competing palettes

| Source | Primary | Notes | Implemented? |
| :--- | :--- | :--- | :--- |
| `docs\DESIGN_SYSTEM.md` (L103-106, L235-239) | `#FF8C42` (`primaryOrange`) | Font: **Google Sans** | ✅ Yes |
| `lush\lib\theme\app_colors.dart` | `#FF8C42`; gradient `#FFA726 → #FF7043`; teal accent `#4ECDC4` | `nearlyBlack = #213333` | ✅ Shipped |
| Stitch `vibrant_zest_architecture\DESIGN.md` | `#FFB690`; brand Orange 500 `#F97316` | "high-energy, performance-driven" | ❌ **Not implemented** |
| Stitch `lush_architecture\DESIGN.md` | `#FFBC49` ("Golden Nectar") | Gold→Bronze `#E7A003` glow, dark glassmorphism, max-width 430px | ❌ **Not implemented** |

**Verdict:** the shipped Flutter theme is consistent with `docs\DESIGN_SYSTEM.md` (good doc↔code hygiene), but **neither Stitch architecture variant is reflected in the app**. Two parallel design-token sources (`DESIGN_SYSTEM.md` vs 2× Stitch `DESIGN.md`) is a governance risk. `vibrant_zest_architecture` is additionally duplicated byte-for-byte across the two export batches.

---


## C. SRS / Documentation → Implementation Alignment

**Document inventory:** 36 documents under `x:\BMJ\docs` (≈ 340 KB of Markdown + 1 XLSX). Largest: `business-requirements\BRD_Business_Requirements.md` (35.7 KB), `use-cases\USE_CASES.md` (35.6 KB), `data_models_map.md` (35.3 KB), `functional-specs\FUNCTIONAL_SPEC.md` (30.9 KB), `architecture\ADR-004-unified-signup-flow.md` (21.4 KB), `SUBSCRIPTIONS.md` (20.9 KB), `API.md` (45.6 KB).

### C.1 Requirements that are correctly implemented ✅

| Requirement source | Requirement | Implementation evidence |
| :--- | :--- | :--- |
| `USE_CASES.md` §9 (v1.3, "Dashboard-First Landing") | Splash → **Dashboard (Public Mode)**; auth failure must not block the user | `main.dart:418-460` — `AuthWrapper` returns `Dashboard(mode: DashboardMode.public)` for `AutoLoginFailed` and `InternetIssue`; full `Dashboard()` on `AuthenticationSuccess` |
| `USE_CASES.md` §3 + ADR-004 | Email, Phone and Google signup paths + OTP/code verification | 24 reachable auth screens (see §A.1.1) + `AuthController` (`POST /signup`, `/login-otp`, `/google`, `/unified-signup`, `/send-otp`, `/verify-otp`, `/send-email-verification`, `/verify-email-code`) |
| `API.md` §JWT Token Authentication | JWT persisted securely | `lush\lib\services\secure_storage_service.dart` (FlutterSecureStorage) |
| `API.md` `### Products` | Product catalog with family/search/featured | `ProductController` → `GET /api/v1/products`, `/family/{family}`, `/search`, `/featured` |
| `API.md` `### Serviceability` + `### Delivery Slots` | Service-area and slot lookup per city | `DeliveryController` → `GET /api/v1/delivery/service-areas`, `/service-areas/city/{city}`, `/slots`, `/slots/range` |
| `API.md` `### Address Management` | Address CRUD + default flag | `AddressController` (`PUT /{id}`, `DELETE /{id}`, `PATCH /{id}/default`) |
| `SUBSCRIPTIONS.md` | Customer can pause and resume | `PUT /api/subscriptions/{id}/pause`, `PUT /api/subscriptions/{id}/resume` — both wired from `subscription_service.dart` |
| `UC-BOTTLE-TRACKING.md` | Bottle ledger, returns, breakage | `BottleTrackingController` → `GET /api/bottles/ledger`, `/transactions`, `POST /return`, `/broken` |
| `API.md` `### Webhooks` | Chargebee events update local state in real time | 13 webhook controllers under `controllers\webhooks\` + `WebhookEventProcessor` + `WebhookEventRepository` + `IdempotencyService` |
| `DESIGN_SYSTEM.md` (L103-106, L235-239) | Primary `#FF8C42`, font Google Sans | `lush\lib\theme\app_colors.dart` matches exactly |
| `KNOWN_ISSUES.md` BUG-003 | One-time catalog must exclude subscription items | Filtering implemented in `menu_tab.dart` / `product_catalog_bloc.dart` |
| `KNOWN_ISSUES.md` BUG-005 | Login must navigate to Dashboard | `AuthWrapper` renders `Dashboard()` on `AuthenticationSuccess` |



### C.2 Documented but NOT correctly implemented ❌

| # | Requirement / statement in docs | Actual implementation | Impact |
| :--- | :--- | :--- | :--- |
| C-1 | `API.md:1783` — single webhook endpoint `POST /api/v1/webhooks/chargebee` | **13 separate endpoints**: `POST /api/webhooks/{addons, attached-items, charges, credit-notes, customers, invoices, item-prices, items, orders, payments, plans, subscriptions, transactions}` | Any reader integrating Chargebee from `API.md` configures the wrong URL and **no webhooks are received**. Actual URLs must be published. |
| C-2 | `API.md:1387` `### Checkout` describes one checkout contract | **4 competing checkout mechanisms**: `GET api/test/oneTimeCheckoutPageUrl` + `POST api/test/cartCheckout` (test ns), `POST /api/v2/checkout/with-items`, `POST /api/v1/subscribe/direct`, `GET api/test/generate_*_pricing_page*` (6 variants) | No single source of truth for checkout; regression risk on every checkout change. |
| C-3 | `API.md:1037` `### Order Management` documents `/api/orders` | Also a **second, legacy** order surface exists: `GET /api/test/orders`, `GET /api/test/ordersByCustomerId` | Duplicate contract, unclear which is authoritative. |
| C-4 | `API.md` never mentions `/api/test/**` | **6 live controllers** are mounted in the `api/test` namespace, exposing ~30 endpoints incl. `GET /api/test/all`, `/user`, `/mod`, `/admin`, `/chargebeeItems`, `/databaseItems`, `/charge-items` | Test/admin-shaped endpoints are shipped in the main API surface with no documented auth contract. |
| C-5 | `SUBSCRIPTIONS.md` plan change / schedule modification | Server exposes **no** schedule-modify endpoint. Flutter calls `PUT /api/subscriptions/{id}/modify` (does not exist). Plan change exists **only** as `POST api/test/generate_plan_change_session_url` (test namespace). | `ModifyScheduleScreen` can never work; the feature is doubly broken. |
| C-6 | `USE_CASES.md` §8 + `notifications` design (Stitch #27) | `notification_centre_screen.dart` + `NotificationBloc` exist, but the screen has **0 references**; `/notifications` renders a **different** file (`notifications.dart`) with no bloc. `NotificationBloc` is constructed in `main.dart:250` and consumed only by the dead screen. | The notification feature is implemented twice; the designed, state-managed one is not shipped. |
| C-7 | `UC-BOTTLE-TRACKING.md` end-to-end bottle UX | API is complete; **no reachable Flutter screen** (`MyBottlesScreen` = 0 refs, `bottle_service.dart` never called from live UI) | Backend capability with zero customer exposure. |
| C-8 | `SUBSCRIPTIONS.md` self-service portal | `SelfServePageController` `GET api/test/portal` exists but no Flutter screen or route consumes it | Dead capability. |
| C-9 | `ADR-003` webhook-driven single-source-of-truth | Implemented **and** additionally a pull-based `ChargebeeSyncController` (`/api/admin/chargebee-sync/status`, `/sync`, `/health`) | Two sync mechanisms; authorization model for `/api/admin/**` needs verification (see §G). |
| C-10 | `KNOWN_ISSUES.md` BUG-004 "subscription plans empty / hardcoded fallback" | Marked with a permanent fix, but a **hardcoded fallback plan list** was observed in the subscription UI path during this audit | Regression risk if plan fetch fails silently again. |

### C.3 Implemented but NOT documented (shadow surface)

| # | Implementation | Documentation gap |
| :--- | :--- | :--- |
| C-11 | `GET /api/test/charge-items` — **the endpoint the shipped product catalog actually uses** | Not documented in `API.md` |
| C-12 | `GET /api/subscriptions/pricing-page` — called by `subscription_service_v2.dart:178` | Does **not exist** on the server (inverse gap: client calls a non-existent endpoint) |
| C-13 | `PUT /api/subscriptions/{id}/cancel` — called by `subscription_service.dart:171` with the comment *"matching bmjServer /cancel endpoint"* | Server has **only** `DELETE /api/subscriptions/{id}`. The comment is factually wrong → cancel is broken wherever the legacy service is used. |
| C-14 | `MetadataTestController` — 8 endpoints incl. `POST /api/test/metadata/test-chargebee-webhook` | Undocumented test harness in production surface |
| C-15 | Two parallel subscription services (`subscription_service.dart` legacy, `subscription_service_v2.dart`) | Only one contract documented; they disagree on the cancel verb/path |
| C-16 | `ReferralController` (`GET /api/referral/code`, `POST /api/referral/apply`) | Referral is a live feature (reachable `ReferralScreen`) but has no `API.md` section |
| C-17 | `GET /api/test/health` **and** `GET /api/health` | Two health endpoints, one documented |



---

## D. Dead, Duplicate & Legacy Artifacts

### D.1 Dead screens (0 references — cannot be reached)

**Subscription self-service — highest business impact**

| Dead screen | File | Why it matters |
| :--- | :--- | :--- |
| `CancelSubscriptionScreen` | `screens\cancel_subscription_screen.dart` | Server **has** `DELETE /api/subscriptions/{id}`. UI is unreachable → **customers cannot cancel** through the app. |
| `PauseSubscriptionScreen` | `screens\pause_subscription_screen.dart` | Server **has** `PUT /{id}/pause`. UI unreachable. |
| `ResumeSubscriptionScreen` | `screens\resume_subscription_screen.dart` | Server **has** `PUT /{id}/resume`. UI unreachable. |
| `ModifyScheduleScreen` | `screens\modify_schedule_screen.dart` | No server endpoint either → feature missing on both sides. |
| `ActiveSubscriptionScreen` | `screens\active_subscription_screen.dart` | Superseded by `SubscriptionSummaryScreen`? |
| `SubscriptionPlansScreen` | `screens\subscription_plans_screen.dart` | Superseded by `PlanSelectionScreen` / `SubscriptionPlanScreen`. |

**Commerce & catalog**

| Dead screen | File | Notes |
| :--- | :--- | :--- |
| `OrderCatalogScreen` | `screens\order_catalog_screen.dart` | Superseded by `ProductCatalogScreen` |
| `OrderCheckoutScreen` | `screens\order_checkout_screen.dart` | Superseded by `CheckoutScreen` |
| `OrderItemScreen` | `screens\order_item_screen.dart` | Superseded by `OrderDetailScreen`; only `_PriceRow` from this file is alive |

**Account, engagement, notifications**

| Dead screen | File | Notes |
| :--- | :--- | :--- |
| `NotificationCentreScreen` | `screens\notification_centre_screen.dart` | **The Stitch-designed notification screen.** Its only consumer was `NotificationBloc`, itself unused. |
| `AddressScreen` | `screens\profile\address_screen.dart` | Contains a `TODO` referencing an unwired `UserBloc`; superseded by `AddressSelectionScreen` / `AddressEntryScreen` |
| `MyBottlesScreen` | `screens\my_bottles_widget.dart` | Bottle-tracking feature has a complete API and no UI |

### D.2 Dead widgets & components (0 references)

`AppDrawer`, `DetailedJuiceCard`, `HeroHeader`, `GlassChip`, `GlassSegmentToggle`, `StatsStrip`, `Weekdays`, `WelcomeHeader`, `WelcomeHeaderShimmer`, `SubscriptionInfoCard`, `SubscriptionPlanCard`, `ShimmerSubscriptionCard`, `HealthInsightCard`, `JuiceRecommendationCard`, `QuickActionCard`, `SectionHeader`, `AppCardHeader`, `AppLoadingCard`, plus private classes `_InvoiceDetailsDialog`, `_OrderDetailsDialog`, `_GlassOrderTile`, `_OrderHistoryGlass`, `_JuiceItemCard`, `_QtyButton`, `_GlassSegmentToggle`, `_SizeSelectionSheet`.

**Aggregate: 111 declared screen/widget classes → 50 unreachable (45%).**

### D.3 Duplicate implementations

| Concern | Implementation A (shipped) | Implementation B (dead/legacy) | Risk |
| :--- | :--- | :--- | :--- |
| Product catalog data | `ProductCatalogBloc` → `GET /api/test/charge-items` | `ProductsBloc` + `ProductsRepository` → `GET /api/products` (`ProductsBloc` is created in `main.dart:228` but **no widget consumes it**) | The correct, versioned API is unused; the app depends on a test endpoint |
| Subscription service | `subscription_service.dart` (bloc-based, **broken cancel/modify**) | `subscription_service_v2.dart` (correct `DELETE` cancel; used by `plan_selection_screen`, `subscription_management_screen`, `menu_tab`) | Two schemas in flight; legacy path has 2 non-existent endpoints |
| Product catalog screen | `ProductCatalogScreen` | `OrderCatalogScreen` | Two screens, one route |
| Order screens | `OrderHistoryScreen`, `OrderHistoryPage`, `OrderDetailScreen` | `OrderItemScreen`, `OrderCatalogScreen`, `OrderCheckoutScreen` | 6 order-related screens for one journey |
| Notifications | `notifications.dart` (shipped, no bloc) | `notification_centre_screen.dart` + `NotificationBloc` (dead) | Design/implementation divergence |
| Checkout | `CheckoutScreen` (WebView) | `_ChargebeeCheckoutWebView` private variants + `PlanSelectionScreen` embedded WebView | 3 WebView checkout entry points |
| Health check | `GET /api/health` | `GET /api/test/health` | Monitoring ambiguity |
| Address CRUD | `AddressController` (`/api/v1/address`) | `DeliveryController` address sub-resources (`/api/v1/delivery/addresses`) | Two address APIs, same entity |
| Order APIs | `OrderController` (`/api/orders`) | `OrdersController` (`/api/test/orders`) | Two order APIs |
| `SubscriptionCard` class name | `screens\subscription_card.dart` | `widgets\dashboard_components.dart` | Two classes with the **same name** that mutually import each other |
| Design tokens | `docs\DESIGN_SYSTEM.md` | `Stitch\...\lush_architecture\DESIGN.md`, `Stitch\...\vibrant_zest_architecture\DESIGN.md` | Three palettes, two of them unimplemented |

### D.4 Zero-byte / dead files

| File | Size | Note |
| :--- | :--- | :--- |
| `bmjServer\...\controllers\OneTimeCheckoutController.java` | **0 bytes** | Listed among controllers but contributes nothing; `CheckoutController` covers the same concern. Safe to delete or must be re-implemented. |



---

## E. Chargebee Integration Alignment

### E.1 Documented model

Per `ADR-003` and `chargebee_final_state.md`, Chargebee is the billing system of record:

| Layer | Owner | Content |
| :--- | :--- | :--- |
| Identity | bmjServer | Users, JWT, OTP, addresses, referrals |
| Billing | Chargebee (site `bookmyjuice-test`, INR/paise) | Item families (`delight`, `signature`, `premium`), 9 generic plans, 45 juice-specific plans, 15 one-time `charge` items, subscriptions, invoices, payments |
| Sync | bmjServer | Real-time inbound webhooks + `ChargebeeSyncService` reconciliation; local cache to survive Chargebee outages |

### E.2 Alignment status

| # | Aspect | Status | Evidence / gap |
| :--- | :--- | :--- | :--- |
| E-1 | Webhook ingestion exists | ✅ | 13 controllers in `controllers\webhooks\`, `WebhookEventProcessor`, `WebhookEventRepository`, `IdempotencyService` |
| E-2 | Webhook URL documented correctly | ❌ | `API.md` documents one URL (`/api/v1/webhooks/chargebee`); reality is 13 URLs at `/api/webhooks/*` (no `/v1`). **Chargebee dashboard config must match the 13 real URLs.** |
| E-3 | Idempotency for retried webhooks | ✅ | `IdempotencyService` present |
| E-4 | Reconciliation / self-heal | ✅ | `ChargebeeSyncController` → `GET /api/admin/chargebee-sync/status`, `POST /sync`, `GET /health` |
| E-5 | Hosted-page checkout for new subscription | ✅ | `api/test/generate_new_{premium,signature,delight}_subscription_pricing_page` + `GET api/test/generate_pricing_page_session_url` |
| E-6 | Hosted-page checkout in a documented contract | ❌ | All hosted-page generators live in the **undocumented `api/test` namespace** (6 endpoints). Should be promoted to `/api/v1/...`. |
| E-7 | Plan-change / upgrade flow | ⚠️ | Only `POST api/test/generate_plan_change_session_url` — test namespace, undocumented |
| E-8 | Existing-subscription management session | ⚠️ | `GET api/test/generate_existing_delight_subscription_session` — hardcodes **delight**; other families unsupported |
| E-9 | Customer self-serve portal | ⚠️ | `GET api/test/portal` — test namespace, no Flutter consumer |
| E-10 | Pause subscription | ✅ | `PUT /api/subscriptions/{id}/pause` wired to `Chargebee` via `SubscriptionApiService` |
| E-11 | Cancel subscription | ⚠️ | Server: `DELETE /api/subscriptions/{id}`. `subscription_service_v2.dart` matches ✅. `subscription_service.dart` calls non-existent `PUT /{id}/cancel` ❌. The cancel **UI** (`CancelSubscriptionScreen`) is dead. |
| E-12 | One-time checkout | ⚠️ | `GET api/test/oneTimeCheckoutPageUrl`, `POST api/test/cartCheckout`; `OneTimeCheckoutController.java` is an **empty 0-byte file** |
| E-13 | Catalog completeness | ⚠️ | `chargebee_final_state.md` L63-73 records **3 failed items** (`premium-black-grapes-*`) due to "Internal name must be unique" — never retried. Premium family is 12/15 items. |
| E-14 | Catalog family metadata correctness | ❌ | `chargebee_final_state.md` L22-23 lists family `signature` **twice** (rows "Signature" and "Premium"); the Premium row's ID should be `premium`. Downstream family filtering can misfile Premium items. |
| E-15 | Exact-once billing / duplicate subscription prevention | ❓ | Not verifiable in this audit; no idempotency key observed on `POST /api/subscriptions/create` or `POST /api/v1/subscribe/direct`. **Recommended verification.** |
| E-16 | Environment separation | ⚠️ | Only `bookmyjuice-test` is documented; no production-site runbook found in `docs`. |

### E.3 Chargebee-side findings requiring action

1. **Publish the 13 real webhook URLs** to the Chargebee dashboard config and correct `API.md:1783`.
2. **Re-run the 3 failed Premium Black Grapes imports** after cleaning conflicting internal names in the Chargebee dashboard (documented in `chargebee_final_state.md` L73 as still pending).
3. **Fix the duplicated `signature` family ID** in the documented family table (doc + verify actual Chargebee families).
4. **Promote hosted-page / portal endpoints out of `api/test`** so the billing contract is versioned and documented.
5. **Choose one cancel contract** — `DELETE /api/subscriptions/{id}` (server reality) — and remove `PUT /{id}/cancel` from the legacy service.



---

## F. API Surface: Server vs Client vs Documentation

### F.1 Server-side inventory

**33 REST controllers** → **≈103 REST operations**.

- `com.bookmyjuice.controllers` — 20 classes + 1 **empty file**
- `com.bookmyjuice.controllers.webhooks` — 13 classes
- `com.bookmyjuice.exception.GlobalExceptionHandler` — `@ControllerAdvice` (not an endpoint)

| Controller | Base path | Ops | Namespace |
| :--- | :--- | :--- | :--- |
| `AuthController` | `/api/auth` **and** `/api/v1/auth` | 14 | v1 ✅ (dual-mounted) |
| `AddressController` | `/api/v1/address` | 3 | v1 ✅ |
| `CartController` | `/api/v1/cart` | 4 | v1 ✅ |
| `DeliveryController` | `/api/v1/delivery` | 9 | v1 ✅ |
| `ProductController` | `/api/products` **and** `/api/v1/products` | 6 | v1 ✅ (dual-mounted, includes `/legacy`) |
| `SubscribeController` | `/api/v1/subscribe` | 1 | v1 ✅ |
| `CheckoutV2Controller` | `/api/v2/checkout` | 1 | v2 ⚠️ |
| `SubscriptionController` | `/api/subscriptions` | 7 | **unversioned** ⚠️ |
| `InvoiceController` | `/api/invoices` | 6 | **unversioned** ⚠️ |
| `OrderController` | `/api/orders` | 5 | **unversioned** ⚠️ |
| `BottleTrackingController` | `/api/bottles` | 4 | **unversioned** ⚠️ |
| `ReferralController` | `/api/referral` | 2 | **unversioned** ⚠️ |
| `HealthController` | `/api` | 1 | **unversioned** ⚠️ |
| `ChargebeeSyncController` | `/api/admin/chargebee-sync` | 3 | admin ⚠️ |
| `CheckoutController` | `api/test` | 2 | **test** ❌ |
| `OrdersController` | `api/test` | 2 | **test** ❌ |
| `PricingPageController` | `api/test` | 6 | **test** ❌ |
| `SelfServePageController` | `api/test` | 1 | **test** ❌ |
| `TestController` | `/api/test` | 8 | **test** ❌ |
| `MetadataTestController` | `/api/test/metadata` | 8 | **test** ❌ |
| `OneTimeCheckoutController` | *(none)* | 0 | **0-byte file** ❌ |
| 13 × `*WebhookController` | `/api/webhooks/*` | 13 | unversioned ⚠️ |

**Namespace hygiene: 7 controllers (~30 endpoints) live in `api/test`. 7 controllers are unversioned. Only 6 use `/api/v1`.**

### F.2 Client-server contract verification

| Client call (Flutter) | Server | Verdict |
| :--- | :--- | :--- |
| `GET /api/test/charge-items` (`ProductCatalogBloc`, `ItemService`) | ✅ `TestController` | Works — **but production catalog depends on a test endpoint** |
| `GET /api/subscriptions/pricing/plans` | ✅ `SubscriptionController` | ✅ Match |
| `GET /api/subscriptions/my` | ✅ | ✅ Match |
| `GET /api/subscriptions/{id}` | ✅ | ✅ Match |
| `POST /api/subscriptions/create` | ✅ | ✅ Match |
| `PUT /api/subscriptions/{id}/pause` | ✅ `PUT /{id}/pause` | ✅ Match |
| `PUT /api/subscriptions/{id}/resume` | ✅ `PUT /{id}/resume` | ✅ Match |
| `DELETE /api/subscriptions/{id}` (`_v2.dart`) | ✅ `DELETE /{id}` | ✅ Match |
| **`PUT /api/subscriptions/{id}/cancel`** (`subscription_service.dart:171`) | ❌ **No such mapping** | ❌ **404 — cancel broken** |
| **`PUT /api/subscriptions/{id}/modify`** (`subscription_service.dart:195`) | ❌ **No such mapping** | ❌ **404 — schedule modify broken** |
| **`GET /api/subscriptions/pricing-page`** (`_v2.dart:178`) | ❌ **No such mapping** | ❌ **404 — pricing page broken** |
| `/api/v1/cart/**` (`CartService`) | ✅ | ✅ Match |
| `/api/orders/**` (`OrderService`) | ✅ | ✅ Match |
| `/api/invoices/**` (`InvoiceService`) | ✅ | ✅ Match |
| `/api/referral/code`, `/api/referral/apply` | ✅ | ✅ Match |
| `/api/v1/address/**` | ✅ | ✅ Match |
| `/api/v1/delivery/**` | ✅ | ✅ Match |
| `/api/bottles/**` (`bottle_service.dart`) | ✅ | ⚠️ Server ready, **no reachable UI** |
| `/api/products`, `/api/v1/products` (`ProductsRepository`) | ✅ | ⚠️ Endpoint ready, **consumer blob is dead** |

**3 client→server 404s confirmed at the code level.** All three are in the legacy `subscription_service.dart` / `subscription_service_v2.dart` pair.



### F.3 Products API — dead-but-correct path

`ProductController` exposes a complete, versioned catalog API:

```
GET /api/products            GET /api/v1/products
GET /api/products/{id}
GET /api/products/family/{family}
GET /api/products/search?q=
GET /api/products/featured
GET /api/products/legacy
```

`lush\lib\repositories\products_repository.dart` is a correct client for all of these, and `ProductsBloc` (`lib\bloc\ProductsBloc\products_bloc.dart`) wraps it. `main.dart:228-230` even constructs the bloc and dispatches `LoadProducts()`.

**However, no widget ever reads `ProductsBloc`** (verified: `ProductsBloc` appears in only 2 files — `main.dart` for construction, and its own declaration). Consequently:

- the app's product data comes from `GET /api/test/charge-items` (name/description/status only), and
- the versioned, documented, richer `/api/v1/products` contract is **completely unused in production**.

This is the highest-value, lowest-risk alignment fix in the codebase.

### F.4 API documentation coverage

| Documented section (`API.md`) | Line | Server implementation | Verdict |
| :--- | :--- | :--- | :--- |
| `### Authentication` | 87 | `AuthController` | ✅ |
| `### User Management` | 438 | Split across `AuthController` (`DELETE /account`) | ⚠️ No dedicated user controller |
| `### Address Management` | 545 | `AddressController` | ✅ |
| `### Subscription Management` | 722 | `SubscriptionController` | ⚠️ Path differs: doc `/api/v1/subscriptions` vs real `/api/subscriptions` |
| `### Order Management` | 1037 | `OrderController` | ✅ |
| `### Cart Management` | 1174 | `CartController` | ✅ |
| `### Checkout` | 1387 | 4 competing mechanisms (test/v1/v2) | ❌ Ambiguous |
| `### Products` | 1499 | `ProductController` — **unused by app** | ⚠️ Documented but dead in practice |
| `### Health Check` | 1641 | `HealthController` + `TestController.health` | ⚠️ Duplicated |
| `### Serviceability` | 1673 | `DeliveryController` | ✅ |
| `### Delivery Slots` | 1710 | `DeliveryController` | ✅ |
| `### Webhooks` | 1775 | 13 controllers at different paths | ❌ Path mismatch |
| `### Bottle Tracking` | 1828 | `BottleTrackingController` — **no UI** | ⚠️ |
| *(none)* | — | `ReferralController` | ❌ Undocumented |
| *(none)* | — | `ChargebeeSyncController` | ❌ Undocumented |
| *(none)* | — | ~30 endpoints under `api/test` | ❌ Undocumented |



---

## G. Prioritised Alignment Actions

### P0 — Correctness / revenue risk

| ID | Action | Owner | Evidence |
| :--- | :--- | :--- | :--- |
| G-1 | **Fix or delete `subscription_service.dart` cancel + modify.** Replace `PUT /{id}/cancel` and `PUT /{id}/modify` with real contracts (`DELETE /{id}`) or migrate callers to `subscription_service_v2.dart` | Backend + Flutter | §F.2 — 3 confirmed 404s |
| G-2 | **Make `CancelSubscriptionScreen` / `PauseSubscriptionScreen` / `ResumeSubscriptionScreen` reachable** (add routes, wire to serving endpoints) or delete them | Flutter + Product | §D.1 — server supports all three, UI unreachable |
| G-3 | **Publish the 13 real Chargebee webhook URLs** and correct `API.md:1783` | Backend + Docs | §E-2 |
| G-4 | **Promote the product catalog off `GET /api/test/charge-items`** onto `GET /api/v1/products` by activating the existing `ProductsBloc` + `ProductsRepository` | Flutter | §F.3 |
| G-5 | **Re-verify `KNOWN_ISSUES` BUG-004** — confirm no hardcoded fallback plan list can reach production | Flutter + QA | §C.2 C-10 |

### P1 — Contract & documentation integrity

| ID | Action | Owner |
| :--- | :--- | :--- |
| G-6 | Version the unversioned controllers (`/api/subscriptions`, `/api/invoices`, `/api/orders`, `/api/bottles`, `/api/referral`, `/api/health`) or ratify them explicitly as v1 | Backend |
| G-7 | Move `api/test` billing endpoints (hosted-page generators, portal, plan-change) into `/api/v1/...`; restrict `api/test` to non-prod profiles | Backend |
| G-8 | Confirm authorization on `/api/admin/chargebee-sync/**` and `/api/test/**` | Backend + Security |
| G-9 | Reconcile checkout: choose ONE of the 4 mechanisms and deprecate the rest | Backend + Product |
| G-10 | Reconcile the two address APIs (`AddressController` vs `DeliveryController.addresses`) | Backend |
| G-11 | Fix `chargebee_final_state.md` family table (duplicate `signature` → `premium`) and retry the 3 failed Premium Black Grapes items | Product + Ops |
| G-12 | Consolidate duplicate service classes: `subscription_service.dart` vs `_v2`, `ProductsBloc` vs `ProductCatalogBloc` | Flutter |
| G-13 | Delete the 0-byte `OneTimeCheckoutController.java` or implement it | Backend |

### P2 — Hygiene, deduplication & design governance

| ID | Action |
| :--- | :--- |
| G-14 | Delete or formally archive the 50 unreachable screen/widget classes (incl. the duplicated `SubscriptionCard` class name) |
| G-15 | Deduplicate overlapping Stitch designs: 2 × "Home", 3 × phone-OTP verification, 3 × email verification, 2 × subscription schedule, 3 × address entry |
| G-16 | Commission the **missing** designs: order history, order detail, invoices, delivery slot selection, my account, delete account, day-wise schedule, subscription drill-downs, pause/cancel/resume |
| G-17 | Resolve the three-palette problem: adopt `DESIGN_SYSTEM.md` (`#FF8C42`) as canonical, regenerate or delete the unused Stitch `DESIGN.md` files, and remove the duplicated `vibrant_zest_architecture` copy |
| G-18 | Give notifications a single owner: ship `NotificationCentreScreen` + `NotificationBloc` **or** delete both and document the shipped `notifications.dart` |
| G-19 | Document referral, Chargebee-sync and address APIs in `API.md` |
| G-20 | Fix route aliases (`/dashboard`, `/menu`, `/home` render the same screen) and expose tab state as routeable URLs |

---

## H. Summary Scorecard

| Dimension | Alignment |
| :--- | :--- |
| Documented requirements → implemented | **~85%** — most core flows match; gaps in schedule-modify, bottle UI, notification design |
| Server API → client usage | **~78%** of endpoints consumed; catalog uses the wrong endpoint; 3 client calls 404 |
| Client → server contract correctness | **3 confirmed broken calls** (cancel, modify, pricing-page) |
| Doc → server path accuracy (`API.md`) | **~75%** — webhook path wrong, subscription base path wrong, referral/admin/test undocumented |
| Design (Stitch) → shipped UI | **~70%** of designs implemented; 12+ shipped flows have no design; 3 conflicting palettes |
| Code hygiene | **50 of 111** screen/widget classes unreachable; multiple duplicated features |

### Single most important finding

> The biggest alignment defect is not missing features — it is that **working backend capability is unreachable from the app** (pause, resume, cancel, bottle tracking, schedule modify, the entire versioned Products API), while the **app depends on test-namespace endpoints** and ships **two conflicting subscription service clients**, one of which calls **three endpoints that do not exist**.



---

## I. Appendix — Reproducible Verification Commands

All findings in this report are reproducible with these read-only PowerShell commands:

```powershell
# Controller inventory (real: 33 controllers + 1 empty file + 1 @ControllerAdvice)
Get-ChildItem x:\BMJ\bmjServer\src\main\java -Recurse -Filter '*Controller.java' |
  Select-Object Name, Length | Sort-Object Name

# Endpoint surface per controller
Get-ChildItem x:\BMJ\bmjServer\src\main\java -Recurse -Filter '*Controller.java' |
  Select-String -Pattern '@RequestMapping|@GetMapping|@PostMapping|@PutMapping|@DeleteMapping|@PatchMapping'

# Webhook endpoints actually mounted (13, none under /api/v1)
Get-ChildItem x:\BMJ\bmjServer\src\main\java -Recurse -Filter '*WebhookController.java' |
  Select-String -Pattern '@RequestMapping|@PostMapping'

# Flutter route table
Select-String -Path x:\BMJ\lush\lib\main.dart -Pattern "^\s+'/"

# Every HTTP call site in Flutter
Get-ChildItem x:\BMJ\lush\lib -Recurse -Filter *.dart |
  Select-String -Pattern "Uri\.parse\('.*api/"

# Unreachable widget detection (0 external references)
Get-ChildItem x:\BMJ\lush\lib -Recurse -Filter *.dart |
  Select-String -Pattern 'class (\w+) extends (StatelessWidget|StatefulWidget)'

# Design inventory
Get-ChildItem x:\BMJ\Stitch -Recurse -Filter code.html |
  Select-String -Pattern '<title>' -SimpleMatch
```

**Analysed:** 33 backend controllers, 30 backend services, 111 Flutter screen/widget classes, 11 Flutter services, 2 Flutter repositories, 36 documents, 31 Stitch designs, 3 design-token files.

**Change footprint:** no file in the application, server, documentation or design trees was created, modified or deleted as part of this analysis. The only artifact produced is `PRODUCT_ALIGNMENT_REPORT.md`.

---

---

## J. V1 Launch Freeze — Execution & Verification (15 October 2026)

> **Addendum, not an overwrite.** Sections 0–I above are the **read-only baseline audit** and
> remain valid as a snapshot of the tree at the audited revisions. This section records what was
> changed *afterwards* to satisfy the V1 launch freeze, verifies it, and re-anchors the findings
> the change resolved. The authoritative contract tables are
> [docs/BMJ_V1_SCOPE.md](docs/BMJ_V1_SCOPE.md) **§4** (old → new endpoint mapping) and **§6**
> (files changed).

### J.1 What the freeze changed

| Layer | Change |
| :--- | :--- |
| **Server** | Two new production controllers — `GET /api/v1/catalog/charge-items` (`CatalogController`, also `/api/catalog/...`) and `GET /api/v1/user/profile` (`UserProfileController`, also `/api/user/...`); new `GET /api/orders/by-customer`; new `PUT /api/subscriptions/{id}/cancel` alias (removes the 404 from §F.2); `permitAll` extended to `/api/catalog/**` + `/api/v1/catalog/**`; `TestController`, `OrdersController`, `CheckoutController`, `MetadataTestController` marked `@Deprecated` **NON-PRODUCTION** |
| **Flutter** | All 5 customer-facing flows repointed to production routes; the dead Chargebee Portal / Pricing-Page chain (7 methods, 251 lines) pruned from `user_repository.dart`; `subscription_service_v2.dart` and `views/screens/subscription/modify_schedule_screen.dart` **deleted**; `modifySchedule` + its bloc event/state/handler removed; checkout payload key corrected to `price_id` |
| **Docs / tests** | New `docs/BMJ_V1_SCOPE.md`; `docs/API.md` gained Catalog, Orders-by-customer, subscription-cancel and a **Non-Production Endpoints** section; integration tests now assert the production profile/checkout contracts and the `410 Gone` behaviour of retired routes |

**Net effect:** the Flutter app has **zero** `/api/test/*` call sites (two comments remain, no
calls), and every in-scope V1 flow runs on a production route.

### J.2 Verification (all commands executed 15 Oct 2026)

| # | Check | Observed result |
| :--- | :--- | :--- |
| 1 | Server compiles — `bmjServer\mvnw.cmd -o -DskipTests compile` | **BUILD SUCCESS**, `Compiling 172 source files`; `CatalogController.class` + `UserProfileController.class` emitted |
| 2 | Flutter static analysis — `lush\dart analyze lib test integration_test` | **0 errors** (38 warnings, 367 info — pre-existing lint noise only) |
| 3 | Flutter test suite — `lush\flutter test` | **351 passed, 12 failed** |
| 4 | Those 12 failures vs a **clean-HEAD worktree** (`git worktree add … HEAD --detach`) | **Identical 12 failures at HEAD `e1d11e6` (`+18 -12`)** → **0 regressions from the freeze** |
| 5 | `/api/test` call sites in `lush/lib` | 2 hits, **both comments** (one corrected to `/api/v1/catalog/charge-items`) |
| 6 | `@Deprecated` markers compile cleanly | BUILD SUCCESS re-run after adding them |

**Pre-existing failures (not V1 regressions, both from unmodified files):**

| Suite | Count | Root cause |
| :--- | :--- | :--- |
| `test/subscription_screens_test.dart` | 11 | `ProviderNotFoundException: Could not find the correct Provider<ThemeCubit>` — `buildTestApp()` installs only `BlocProvider<SubscriptionBloc>`; the three subscription screens now read `ThemeCubit` |
| `test/unit/bloc/product_catalog_bloc_test.dart` | 1 | Expects `ProductCatalogEmpty`, bloc emits `ProductCatalogFiltered` (test drift from HEAD `b4932b2`) |

### J.3 Status of findings raised in §§C, F and G

| Finding | Baseline state | Status after the freeze |
| :--- | :--- | :--- |
| **C-2** | 4 competing checkout mechanisms; the client used the test-namespace `POST /api/test/cartCheckout` | **Resolved for the client** — only `POST /api/v2/checkout/with-items` is called. The test-namespace checkout is `@Deprecated`; the pricing-page generators remain `410 Gone` |
| **C-3** | Duplicate order surface (`/api/test/orders`, `/api/test/ordersByCustomerId` alongside `/api/orders`) | **Resolved** — the client uses `GET /api/orders/by-customer`; `OrdersController` (`/api/test`) is `@Deprecated` |
| **C-5** | `ModifyScheduleScreen` called the non-existent `PUT /api/subscriptions/{id}/modify` | **Resolved** — caller, bloc event, bloc state, handler and screen all deleted, so no 404 remains. *(Plan change still exists only in the test namespace — unchanged.)* |
| **F.2 — 3 confirmed 404s** | `PUT /{id}/cancel`, `PUT /{id}/modify`, pricing-page session URL | **All three removed.** `cancel` now has a real server alias; `modify` was deleted client-side; the pricing-page chain was deleted and its route answers `410 Gone` |
| **G-1 (P0)** | Fix or delete the broken cancel + modify calls | **Done** — `PUT /api/subscriptions/{id}/cancel` alias added; `modifySchedule` removed |
| **G-4 (P0)** | Promote the catalog off `GET /api/test/charge-items` | **Done** — moved to `GET /api/v1/catalog/charge-items`. *(Note: not `/api/v1/products` as originally proposed; the existing `ProductsBloc` path stays dead.)* |
| **G-9 (P1)** | Reconcile checkout: 4 mechanisms → 1 | **Done client-side**; the server still exposes all four, three of them now `@Deprecated` |
| **G-12 (P1)** | Consolidate `subscription_service.dart` vs `_v2` | **Partially done** — `subscription_service_v2.dart` deleted; `ProductsBloc` vs `ProductCatalogBloc` duplication remains |
| **G-6 (P1)** | Version the unversioned controllers | **Partial** — `/api/v1/catalog` and `/api/v1/user` now exist; `/api/orders`, `/api/subscriptions`, `/api/invoices`, `/api/bottles`, `/api/referral` remain unversioned |
| **G-7 (P1)** | Move `api/test` billing endpoints into `/api/v1`; restrict `api/test` to non-prod profiles | **Partial** — catalog + profile promoted; Portal and Pricing Pages retired to `410 Gone`; **`/api/test/**` is still `permitAll`** (now documented, not restricted) |
| **G-8 (P1)** | Confirm authorization on `/api/test/**` | **Still open** — `permitAll` deliberately retained and now documented in `docs/API.md` + `BMJ_V1_SCOPE.md` §5 |
| **G-2 (P0)** | Pause/resume/cancel screens unreachable | **Re-verified 2026-10-16 — satisfied for V1.** The freeze was plumbing only, but `SubscriptionManagementScreen` was *already* wired and is reachable (Profile → Manage Subscriptions; home card → *Pause*): it calls `PUT /{id}/pause` / `/resume` / `/cancel`, all of which now exist, and its payload keys match `mapSubscriptionToResponse`. The four *standalone* screens this row was originally raised against are still unreachable — classified ARCHIVE, not required for V1. Residual work = one step of the **B5** device smoke. See `B6_DECISION_REPORT.md`. |
| **G-13 (P1)** | Delete/implement the 0-byte `OneTimeCheckoutController.java` | **Still open** |

### J.4 Corrected finding — Chargebee-customer coverage on signup / sign-in paths

An earlier note asserted that *“OTP signup creates no Chargebee customer, so checkout fails with
`Chargebee customer ID not found`”*. **Reading the code shows this is wrong for every
account-creation path.** Verified directly in
`bmjServer/src/main/java/com/bookmyjuice/controllers/AuthController.java`:

| Path | Creates a Chargebee customer? | On Chargebee failure |
| :--- | :--- | :--- |
| `POST /api/auth/signup` (legacy email) | **Yes** — `AuthController.java:794-806` | local user **deleted**, `500` returned (hard rollback) |
| `POST /api/auth/unified-signup` (**Google *and* OTP signup completion**) | **Yes** — `AuthController.java:696-717` | local user **deleted**, `500` returned (hard rollback) |
| `POST /api/auth/google` (sign-in of an existing user) | **Yes, backfilled** — `AuthController.java:241-268`, re-run on every sign-in while the id is null | *swallowed* — `logger.warn` only, user is kept |
| `POST /api/auth/login-otp` (sign-in of an existing user) | **No backfill** | n/a |
| `POST /api/auth/send-otp`, `/verify-otp` | n/a — pure OTP mechanics, no account creation (correct by design) | n/a |

**Residual exposure (narrow but real):**

1. A user whose account was created by `/api/auth/google` while `Customer.create()` was failing is
   kept with a **null `chargebeeCustomerId`** (only a warning is logged). They self-heal on their
   next Google sign-in because Step 7 retries, but until then **checkout hard-fails** with
   `Chargebee customer ID not found` — `CheckoutService.java:68`,
   `SubscriptionCheckoutService.java:87-89`.
2. `/api/auth/login-otp` has **no equivalent backfill**, so a user with a null
   `chargebeeCustomerId` who signs in by OTP can never self-heal → permanent checkout dead-end.

**Applied fix (2026-10-16, decision `D-2`).** The Google Step 7 block was mirrored into the
`login-otp` “user exists” branch (`AuthController#loginViaOtp`): if `chargebeeCustomerId` is empty,
call `Customer.create()` and persist the returned id. One `if` block on an existing path — no new
endpoint, no schema change. It is best-effort, so a Chargebee failure can never block a sign-in.

> **Why it needed approval first:** it **creates a Chargebee customer**, and the project guardrail
> reserves any Chargebee-side creation for explicit approval. Approval was granted on 2026-10-16
> (decision **D-2**), so the block is now implemented — see §J.8.

### J.5 Open decisions carried forward

| # | Decision | Why it is blocked / who owns it |
| :--- | :--- | :--- |
| **D-2** | Backfill `chargebeeCustomerId` in `login-otp` (§J.4) | ✅ **IMPLEMENTED 2026-10-16** — approved. `AuthController#loginViaOtp` now mirrors the Google Step 7 repair block: when the OTP sign-in finds an existing user with an empty `chargebeeCustomerId`, it calls `Customer.create()` and persists the id. Best-effort (a Chargebee failure is `logger.warn`-ed and sign-in still succeeds), so it cannot block a login. Removes the permanent checkout dead-end. |
| **D-3** | Branch strategy for the nested repositories: `lush/` and `bmjServer/` are **independent git repos (not submodules)** — both still on `main`, while the root repo sits on `feat/v1-launch-freeze` | **Still open** — repo owner; no nested branch was created |
| **D-4** | Breadth of the `410 Gone` guarantee — today only `lush/integration_test/fullstack_auth_and_pricing_test.dart` asserts it | **Still open** — QA + Backend |
| **D-5** | Stop advertising `POST /api/auth/unified-signup` as a standalone email + password signup path (V1 launch is Google + OTP) | ✅ **IMPLEMENTED 2026-10-16** — approved. The "Sign up with Email" card is removed from the LoginPage Sign Up tab; V1 offers **Phone (OTP)** and **Google** only. The endpoint itself is untouched (Google signup completion and OTP signup completion still call it). `login_page_test.dart`, `full_e2e_test.dart` assertions updated; the two email-first E2E templates are now explicitly `skip: true` pending re-authoring. |
| **D-6** | **Order history always returned `[]`.** `OrderEntity.customerId` is the *Chargebee* id (written by `OrderMapper.toEntity`), but `OrderController#getCustomerIdFromSecurityContext()` passed the *local numeric user id* into `findByCustomerId(...)`. Pre-existing — the retired `/api/test/ordersByCustomerId` passed the identical value | ✅ **IMPLEMENTED 2026-10-16** — approved. `OrderController` now resolves the Chargebee id via `resolveChargebeeCustomerId(localUserId)` (the `SubscriptionController:310-330` pattern, incl. the legacy `CustomerRepository` fallback) and feeds that into `OrderService#fetchOrdersByCustomerId`. `GET /api/orders` and `GET /api/orders/local/history` share the helper and are corrected with it. When no Chargebee id is resolvable an **empty** collection is returned with `200` (documented response shape preserved) instead of a misleading `401`. |
| **W0** | Repo hygiene before freeze: `lush` carries uncommitted UI work in `lib/views/screens/home_tab.dart` and `menu_tab.dart` (**210 insertions / 80 deletions, 2 files**) **unrelated to this change**; `lush/android/build/reports/problems/problems-report.html` is a **tracked build artifact** that churns on every Gradle run — **untracked by this session** (`git rm --cached` + `/android/build/` added to `lush/.gitignore`); `bmjServer` tracks **30 files under `logs/`** and currently shows **19 deleted + 26 untracked + 3 modified** log entries of pure rotation churn | **Still open** — repo owner, see §J.7 for the two `bmjServer` options |

### J.6 Defect detail — order history always returns `[]` (see **D-6**)

**Symptom.** `GET /api/orders/by-customer` — in-scope V1 flow 6 — always responds with an empty
array, so `OrderHistoryPage` can never list a customer's orders.

**Mechanism.** Two facts, both verified in source:

1. `order_entity.customer_id` stores the **Chargebee** customer id. Its only writers are
   `ChargebeeSyncService:427-436` and `OrderService:21-23` / `OrderApiService:102`, all of which go
   through `OrderMapper.toEntity`, which does `entity.setCustomerId(order.customerId())` — i.e. the
   Chargebee order's `customerId` (`cbdemo_xxxxx`).
2. `OrderRepository` is a plain derived query — `List<OrderEntity> findByCustomerId(String)` →
   `WHERE customer_id = ?` — and the controller feeds it the **local numeric id**
   (`userDetails.getId().toString()`), because `OrderController#getCustomerIdFromSecurityContext()`
   returns `getId()` despite its name.

**Why it is not a regression.** The retired `/api/test/ordersByCustomerId` used
`JwtUtils.getUserIdFromSecurityContext()`, which returns the *same* `userDetails.getId().toString()`.
The migration therefore changed the URL, not the lookup — the flow was equally empty before.

**Why it needed sign-off first.** The correct value is only obtainable by resolving local id → Chargebee
id (the pattern already written in `SubscriptionController:310-330`). That turns a permanently-empty
response into a populated one — a user-visible behaviour change that a launch freeze should not
introduce without a decision. Approval was granted on 2026-10-16 (**D-6**) and the fix is implemented;
see §J.8.

### J.7 W0 repo-hygiene remediation

**Verified repo state (post-freeze — no freeze file staged or committed anywhere).**

| Repo | HEAD (branch) | Staged | Working tree |
| :--- | :--- | :--- | :--- |
| root `x:\BMJ` | `be41c89` (`feat/v1-launch-freeze`) | *empty* | ` M bmjServer` + ` M lush` (gitlink moves), ` M docs/API.md` (+146); untracked: `docs/BMJ_V1_SCOPE.md`, `PRODUCT_ALIGNMENT_REPORT.md` (and the pre-existing `Stitch/`) |
| `lush/` | `e1d11e6` (`main`) | **`D` — `android/build/reports/problems/problems-report.html`** (the hygiene untrack, item 1) | 12 freeze files (10 modified + 2 deleted), the unrelated `home_tab.dart` / `menu_tab.dart` UI WIP, and the new `.gitignore` rule |
| `bmjServer/` | `fa34ca9` (`main`) | *empty* | 7 modified `src/main/java` paths (6 controllers + `WebSecurityConfig`), 2 untracked new controllers, log churn |

No freeze file was accidentally staged or committed in any of the three repositories.

**Fixed by this session**

1. `lush/android/build/reports/problems/problems-report.html` — a Gradle build artifact that was
   **tracked** (hence churned on every build). Untracked via
   `git -C lush rm --cached android/build/reports/problems/problems-report.html`, and
   `/android/build/` added to `lush/.gitignore` so it cannot come back. The file is **still on
   disk** (verified), and the change is reversible with `git -C lush reset -- android/build`.

2. **Line-ending churn normalized in five files**, so the freeze diff shows only real changes. Three
   server controllers and one integration test had been written with CRLF while their committed
   blobs are LF (or CRLF-mixed), which surfaced as phantom whole-file deletions:

   | File | Diff before | Diff after |
   | :--- | ---: | ---: |
   | `bmjServer/…/CheckoutController.java` | 84 / 67 | **17 / 0** |
   | `bmjServer/…/OrderController.java` | 199 / 168 | **31 / 0** |
   | `bmjServer/…/OrdersController.java` | 48 / 29 | **19 / 0** |
   | `lush/integration_test/fullstack_auth_and_pricing_test.dart` | 42 / 68 | **31 / 57** |
   | `lush/.gitignore` | 49 / 44 | **5 / 0** |

   Only newline bytes were touched — no content changed — and both checks were re-run afterwards:
   `mvnw -o -DskipTests compile` → **BUILD SUCCESS** (172 files) and
   `dart analyze lib test integration_test` → **0 errors**. Neither Java text blocks (`"""`) nor Dart
   multi-line strings (`'''` / `"""`) exist in the affected files, so no string literal could have
   changed value (checked explicitly).
   **One residual:** `lib/UserRepository/user_repository.dart` keeps 18 CR-only line pairs because its
   *committed* blob is itself mixed-EOL (**1480 CRLF + 18 LF**), so no global newline rule can
   reproduce it; its real change is 25 / 261 of a 279-line refactor, and the 18 pairs are cosmetic
   noise inside that refactor.

**Deliberately NOT actioned — needs the repo owner**

3. `lush/lib/views/screens/home_tab.dart` + `menu_tab.dart` — **210 insertions / 80 deletions** of
   UI work unrelated to this freeze. Neither `git stash` nor a commit is safe to do on someone
   else's behalf: stashing could strand in-flight work, committing would mix unrelated UI changes
   into the freeze branch. Open decision: **commit vs stash**.
4. `bmjServer/logs/**` — **30 tracked files**, currently showing **19 deleted + 26 untracked +
   3 modified** entries of pure rotation noise. Two options, owner's call:

   | Option | Commands | Effect |
   | :--- | :--- | :--- |
   | **A — untrack logs** (if they are pure runtime output) | `git -C bmjServer rm -r --cached logs`, then add `logs/` + `*.log` to `bmjServer/.gitignore` | removes all log churn from `status`; log files stay on disk and in history; a fresh clone no longer receives them |
   | **B — keep logs tracked** (if they are UAT evidence) | leave tracking as-is and commit only the freeze sources | churn continues, nothing is lost |

   Not actioned because `bmjServer`'s HEAD is *“Auto UAT done but bugs remain”* — the committed
   logs may be deliberate UAT evidence, and silently dropping 30 files from tracking inside another
   team's repo is not a plumbing change. Option **A** is the right long-term answer; it just needs
   one word from the repo owner.
5. Two stray root files predate this work: `temp_search.txt` (2026-05-13) and
   `temp_signin.json` (2026-05-20). Both were **deleted on 2026-10-16** under
   `SAFE_DELETE_LIST.md` §A2 (the credential they carried lives on in git history —
   see `BMJ_LAUNCH_CHECKLIST.md` finding I4).

> **Note for the commit step:** `docs/API.md` carries the freeze's API-level mapping too
> (§4 of `BMJ_V1_SCOPE.md` is the audit-level view; `docs/API.md` gained `### Catalog`,
> `GET /api/orders/by-customer`, the subscription-cancel contract note, and the
> `### Non-Production Endpoints (/api/test/*)` replacement table). Both must land together.

### J.8 Implementation of the approved decisions — D-2 / D-5 / D-6 (2026-10-16)

Decisions **D-2**, **D-5** and **D-6** were approved and implemented in one pass. **D-3**, **D-4** and
**W0** remain open (see §J.5) and are carried into `BMJ_LAUNCH_CHECKLIST.md`.

| Decision | Files changed | Implementation | Verification |
| :--- | :--- | :--- | :--- |
| **D-2** | `bmjServer/.../controllers/AuthController.java` | `loginViaOtp` gained a best-effort backfill: for an existing user with an empty `chargebeeCustomerId`, call `Customer.create()` and persist the returned id. Failure is `logger.warn`-ed; the sign-in path is unchanged. | `mvnw.cmd -o -DskipTests compile` → **BUILD SUCCESS** (172 sources). |
| **D-6** | `bmjServer/.../controllers/OrderController.java` | `getCustomerIdFromSecurityContext()` replaced by `currentUser()` + `resolveChargebeeCustomerId(localUserId)` (the `SubscriptionController:310-330` pattern, incl. the `CustomerRepository` fallback). All three order read routes use it. Unresolvable id → `200` + empty collection (previous response shape), not `401`. | `mvnw.cmd -o -DskipTests compile` → **BUILD SUCCESS**. No `OrderControllerTest` exists, so no unit suite regressed. **Live populated-response check still open** — needs a user with a Chargebee customer + a synced order. |
| **D-5** | `lush/lib/views/screens/login_page.dart`, `test/widget/screens/login_page_test.dart`, `integration_test/full_e2e_test.dart`, `integration_test/cart_test.dart`, `integration_test/physical_device_template_test.dart` | The “Sign up with Email” card is removed from the Sign Up tab (Phone OTP + Google remain). The email-first screens stay in the tree but become unreachable from the launch surface. Test expectations updated; the two email-first E2E templates are `skip: true` pending re-authoring. | `flutter test test/widget/screens/login_page_test.dart` → **21/21 pass**. |

**Full-suite re-verification after all three changes** (recorded as rows 12–16 of `BMJ_V1_SCOPE.md` §5):

| Check | Result |
| :--- | :--- |
| `bmjServer\mvnw.cmd -o -DskipTests compile` | **BUILD SUCCESS** — `Compiling 172 source files` |
| `lush\dart analyze lib test integration_test` | **0 errors** — 405 issues, the same count as before the change (no new diagnostics) |
| `lush\flutter test` | **351 passed / 12 failed** — byte-identical failure set to the clean `e1d11e6` baseline → **0 regressions** |

**Deliberately not done** (kept out of scope, carried forward): no `/api/test/**` route was removed or
restricted (`permitAll` still stands — **G-8**), `home_tab.dart` / `menu_tab.dart` UI work is still
uncommitted (**W0**), the nested repos still have no release branch (**D-3**), and `410 Gone` breadth
is still asserted by one test only (**D-4**).

*End of report.*

