# Final Commit Strategy

> **Date:** 2026-10-30 · **Nothing is committed by this document.**
> Three git work trees are involved; each group names the repo it belongs to.

| Repo | Entries in flight |
| :--- | ---: |
| `X:\BMJ\lush` (Flutter app) | 141 |
| `X:\BMJ` (docs, scripts, the `bmjServer` submodule pointer) | 112 |
| `X:\BMJ\bmjServer` (Spring server) | 61 |

## Rules

1. **One intent per commit.** If a file is needed by two groups it ships in the *earlier* group (C1 → C7) and the later group notes the dependency.
2. Every commit must pass `flutter analyze` (**0 errors**) and `flutter test` (**418/418**) — except the server-only commits, which pass `mvn test` instead.
3. `C6` (formatter noise, if split that way) is mechanical: reviewers can verify with `git show <sha> --ignore-all-space --stat` (expect 0).
4. Nothing in these groups changes UI, screens or architecture — this is packaging of work already merged in the working tree.

## Order and purpose

| # | Commit | Purpose | Verify |
| :-: | :--- | :--- | :--- |
| C1 | `chore(security): release signing, manifest, endpoint config` | Make a release build possible and safe | `flutter build appbundle --release` succeeds; merged manifest has `INTERNET`/`POST_NOTIFICATIONS` |
| C2 | `feat(auth): Google + phone OTP only` | Remove the password/email surface, keep two providers | 418 tests |
| C3 | `feat(design-system): tokens, widgets, typography` | The shared UI vocabulary the rest depends on | 418 tests |
| C4 | `feat(ui): visual alignment across Home, PDP, Cart, Subscription` | The screen work | 418 tests + `_captures/after` regenerated |
| C5 | `feat(subscription): plans, catalog, management` | Subscription catalogue + management flows | 418 tests |
| C6 | `feat(subscription): day-wise delivery schedule` | Server + client schedule feature | `mvn test` + 418 tests |
| C7 | `test(qa): widget, integration and device coverage` | Test-suite additions that aren't tied to one feature | 418 tests |

## Exact files per group (repo: `X:\BMJ\lush`)

## C1 — 6 files

- `.gitignore` ΓÇö modified
- `android/app/build.gradle.kts` ΓÇö modified
- `android/app/src/debug/AndroidManifest.xml` ΓÇö modified
- `android/app/src/main/AndroidManifest.xml` ΓÇö modified
- `android/app/src/profile/AndroidManifest.xml` ΓÇö modified
- `lib/config/api_config.dart` ΓÇö modified

## C2 — 35 files

- `integration_test/fullstack_auth_and_pricing_test.dart` ΓÇö modified
- `integration_test/google_signup_test.dart` ΓÇö deleted
- `lib/UserRepository/user_repository.dart` ΓÇö modified
- `lib/bloc/AuthBloc/auth_bloc.dart` ΓÇö modified
- `lib/bloc/AuthBloc/auth_events.dart` ΓÇö modified
- `lib/bloc/AuthBloc/auth_state.dart` ΓÇö modified
- `lib/views/models/firebase_phone_auth.dart` ΓÇö deleted
- `lib/views/screens/create_password_screen.dart` ΓÇö deleted
- `lib/views/screens/email_entry_after_phone_screen.dart` ΓÇö deleted
- `lib/views/screens/email_signup_screen.dart` ΓÇö deleted
- `lib/views/screens/email_verification_after_phone_screen.dart` ΓÇö deleted
- `lib/views/screens/email_verification_screen.dart` ΓÇö deleted
- `lib/views/screens/forgot_password_page.dart` ΓÇö deleted
- `lib/views/screens/forgot_password_screen.dart` ΓÇö deleted
- `lib/views/screens/google_phone_entry_screen.dart` ΓÇö deleted
- `lib/views/screens/google_signup_screen.dart` ΓÇö modified
- `lib/views/screens/link_google_account_screen.dart` ΓÇö modified
- `lib/views/screens/login_page.dart` ΓÇö modified
- `lib/views/screens/otp_login_page.dart` ΓÇö deleted
- `lib/views/screens/phone_entry_after_email_screen.dart` ΓÇö deleted
- `lib/views/screens/phone_entry_screen.dart` ΓÇö new
- `lib/views/screens/phone_login_screen.dart` ΓÇö deleted
- `lib/views/screens/phone_otp_verification_screen.dart` ΓÇö modified
- `lib/views/screens/phone_signup_screen.dart` ΓÇö deleted
- `lib/views/screens/reset_password_email_screen.dart` ΓÇö deleted
- `lib/views/screens/reset_password_mobile_screen.dart` ΓÇö deleted
- `lib/views/screens/sign_up_screen.dart` ΓÇö deleted
- `lib/views/screens/signup_email_verification_screen.dart` ΓÇö new
- `lib/views/screens/signup_method_selection_screen.dart` ΓÇö deleted
- `test/unit/bloc/auth_bloc_test.dart` ΓÇö modified
- `test/widget/screens/auth_no_password_test.dart` ΓÇö new
- `test/widget/screens/login_page_test.dart` ΓÇö modified
- `test/widget/screens/phone_entry_screen_test.dart` ΓÇö new
- `test/widget/screens/signup_email_step_test.dart` ΓÇö new
- `test/widgets/signup_screen_test.dart` ΓÇö deleted

## C3 — 21 files

- `lib/theme/app_colors.dart` ΓÇö modified
- `lib/theme/app_radius.dart` ΓÇö modified
- `lib/theme/app_text_styles.dart` ΓÇö modified
- `lib/theme/app_theme.dart` ΓÇö modified
- `lib/theme/bmj_tokens.dart` ΓÇö new
- `lib/utils/font_utils.dart` ΓÇö modified
- `lib/utils/price_utils.dart` ΓÇö new
- `lib/widgets/bmj_amount_row.dart` ΓÇö new
- `lib/widgets/bmj_badge.dart` ΓÇö new
- `lib/widgets/bmj_empty_state.dart` ΓÇö new
- `lib/widgets/bmj_glass_bottom_nav.dart` ΓÇö new
- `lib/widgets/bmj_glass_button.dart` ΓÇö new
- `lib/widgets/bmj_glass_card.dart` ΓÇö new
- `lib/widgets/bmj_glass_header.dart` ΓÇö new
- `lib/widgets/bmj_glass_input.dart` ΓÇö new
- `lib/widgets/bmj_glass_sheet.dart` ΓÇö new
- `lib/widgets/bmj_pill.dart` ΓÇö new
- `lib/widgets/bmj_stat_tile.dart` ΓÇö new
- `test/theme/app_theme_test.dart` ΓÇö modified
- `test/theme/no_raw_white_test.dart` ΓÇö new
- `test/widget/bmj_design_system_test.dart` ΓÇö new

## C4 — 47 files

- `android/build/reports/problems/problems-report.html` ΓÇö deleted
- `assets/carrot.png` ΓÇö modified
- `assets/fonts/` ΓÇö new
- `lib/main.dart` ΓÇö modified
- `lib/views/all_Screens.dart` ΓÇö modified
- `lib/views/models/detailed_juice_card.dart` ΓÇö modified
- `lib/views/models/item_card_view.dart` ΓÇö modified
- `lib/views/screens/Dashboard.dart` ΓÇö modified
- `lib/views/screens/Menu.dart` ΓÇö modified
- `lib/views/screens/address_entry_screen.dart` ΓÇö modified
- `lib/views/screens/address_selection_screen.dart` ΓÇö modified
- `lib/views/screens/cart_screen.dart` ΓÇö modified
- `lib/views/screens/checkout_screen.dart` ΓÇö modified
- `lib/views/screens/delete_account_screen.dart` ΓÇö modified
- `lib/views/screens/delivery_slot_selection_screen.dart` ΓÇö modified
- `lib/views/screens/detail.dart` ΓÇö modified
- `lib/views/screens/enter_mobile_number.dart` ΓÇö modified
- `lib/views/screens/home_tab.dart` ΓÇö modified
- `lib/views/screens/invoice_view_screen.dart` ΓÇö modified
- `lib/views/screens/menu_tab.dart` ΓÇö modified
- `lib/views/screens/my_account_page.dart` ΓÇö modified
- `lib/views/screens/notification_centre_screen.dart` ΓÇö modified
- `lib/views/screens/notifications.dart` ΓÇö modified
- `lib/views/screens/order/order_detail_screen.dart` ΓÇö modified
- `lib/views/screens/order_history_page.dart` ΓÇö modified
- `lib/views/screens/order_history_screen.dart` ΓÇö modified
- `lib/views/screens/orders/order_checkout_screen.dart` ΓÇö modified
- `lib/views/screens/orders/order_item_screen.dart` ΓÇö modified
- `lib/views/screens/orders_tab.dart` ΓÇö modified
- `lib/views/screens/profile/address_screen.dart` ΓÇö modified
- `lib/views/screens/profile_tab.dart` ΓÇö modified
- `lib/views/screens/referral/referral_screen.dart` ΓÇö modified
- `lib/views/screens/user_profile_screen.dart` ΓÇö modified
- `lib/views/widgets/cart_icon.dart` ΓÇö modified
- `lib/views/widgets/dashboard_components.dart` ΓÇö modified
- `lib/views/widgets/filter_options.dart` ΓÇö modified
- `lib/views/widgets/my_bottles_widget.dart` ΓÇö modified
- `lib/views/widgets/size_selection_modal.dart` ΓÇö modified
- `lib/views/widgets/size_selection_sheet.dart` ΓÇö new
- `lib/views/widgets/welcome_header.dart` ΓÇö modified
- `lib/widgets/app_drawer.dart` ΓÇö modified
- `lib/widgets/app_text_field.dart` ΓÇö modified
- `lib/widgets/cart_badge_icon.dart` ΓÇö modified
- `lib/widgets/glass_card.dart` ΓÇö modified
- `lib/widgets/hero_header.dart` ΓÇö modified
- `lib/widgets/stats_strip.dart` ΓÇö modified
- `pubspec.yaml` ΓÇö modified

## C5 — 24 files

- `lib/bloc/ProductCatalogBloc/product_catalog_bloc.dart` ΓÇö modified
- `lib/bloc/SubscriptionBloc/subscription_bloc.dart` ΓÇö modified
- `lib/services/subscription_service.dart` ΓÇö modified
- `lib/services/subscription_service_v2.dart` ΓÇö deleted
- `lib/utils/subscription_view_utils.dart` ΓÇö new
- `lib/views/screens/orders/order_catalog_screen.dart` ΓÇö modified
- `lib/views/screens/plan_selection_screen.dart` ΓÇö modified
- `lib/views/screens/product_catalog_screen.dart` ΓÇö modified
- `lib/views/screens/subscription/active_subscription_screen.dart` ΓÇö modified
- `lib/views/screens/subscription/cancel_subscription_screen.dart` ΓÇö modified
- `lib/views/screens/subscription/pause_subscription_screen.dart` ΓÇö modified
- `lib/views/screens/subscription/resume_subscription_screen.dart` ΓÇö modified
- `lib/views/screens/subscription/subscription_family_screen.dart` ΓÇö modified
- `lib/views/screens/subscription/subscription_plan_screen.dart` ΓÇö modified
- `lib/views/screens/subscription/subscription_plans_screen.dart` ΓÇö modified
- `lib/views/screens/subscription/subscription_summary_screen.dart` ΓÇö modified
- `lib/views/screens/subscription_management_screen.dart` ΓÇö modified
- `lib/views/screens/subscription_tab.dart` ΓÇö new
- `lib/views/widgets/subscription_plan_card.dart` ΓÇö modified
- `lib/widgets/subscription_card.dart` ΓÇö modified
- `test/subscription_bloc_test.dart` ΓÇö modified
- `test/subscription_screens_test.dart` ΓÇö modified
- `test/unit/bloc/product_catalog_bloc_test.dart` ΓÇö modified
- `test/unit/services/subscription_service_test.dart` ΓÇö modified

## C6 — 3 files

- `lib/views/screens/day_wise_schedule_screen.dart` ΓÇö modified
- `lib/views/screens/subscription/modify_schedule_screen.dart` ΓÇö deleted
- `lib/views/screens/subscription/subscription_schedule_screen.dart` ΓÇö modified

## C7 — 5 files

- `integration_test/cart_test.dart` ΓÇö modified
- `integration_test/full_e2e_test.dart` ΓÇö modified
- `integration_test/physical_device_template_test.dart` ΓÇö modified
- `test/unit/utils/` ΓÇö new
- `test/widget/screens/product_detail_screen_test.dart` ΓÇö new

## Server repository (`X:\BMJ\bmjServer`, 61 entries)

The delivery-schedule work lives here and must land **before** C6's client half. Key files verified in this sprint:

- `src/main/java/com/bookmyjuice/models/entities/DeliveryScheduleEntity.java` (new)
- `src/main/java/com/bookmyjuice/repository/DeliveryScheduleRepository.java` (new)
- `src/main/java/com/bookmyjuice/services/DeliveryScheduleService.java` (new, 297 lines)
- `src/main/java/com/bookmyjuice/services/SubscriptionCheckoutService.java` (reserves the id)
- `src/main/java/com/bookmyjuice/services/SubscriptionApiService.java`, `controllers/SubscriptionController.java`
- `src/test/java/com/bookmyjuice/services/DeliveryScheduleServiceTest.java` (12 cases)
- `src/main/resources/application*.properties` (profile + Chargebee values)

Suggested server commits (same order as C2→C6): `feat(auth)`, `feat(catalog)`, `feat(subscription)`, `feat(schedule)`, `test(schedule)`. Then bump the submodule pointer in the parent repo as its own commit.

## Parent repository (`X:\BMJ`, 112 entries)

| Bucket | Contents |
| :--- | :--- |
| Chargebee investigation docs | `CHARGEBEE_*`, `CATALOG_*` (execution plan, price matrix, root cause, go-live recommendation, variant support request) |
| Launch docs | `LAUNCH_HARDENING_SPRINT.md`, `RELEASE_SIGNING_CHECK.md`, `AAB_RELEASE_REPORT.md`, `PRODUCTION_ENDPOINT_AUDIT.md`, `DEVICE_QA_RESULTS.md`, `CHARGEBEE_BETA_STATUS.md`, `ORPHAN_SCHEDULE_REMEDIATION.md`, `FINAL_COMMIT_STRATEGY.md` |
| Visual docs | `VISUAL_ALIGNMENT_AUDIT.md`, `VISUAL_REVIEW.md`, `BMJ_UX_REHAUL_PLAN.md` |
| Tooling | `_captures/**` (harness, scripts, evidence), `*.py`, `*.ps1` |
| Submodule | `bmjServer` pointer bump |

Land as `docs(launch): beta readiness evidence` + `chore(tooling): capture and rollout scripts`, after the app and server commits.

## Two files that must NOT be committed

- `X:\BMJ\lush\keystore_name.jks` and `X:\BMJ\lush\clientkeystore` — **already tracked**; run `git rm --cached` and rotate them (`RELEASE_SIGNING_CHECK.md` §4).
- `android/key.properties` and `X:/BMJ/_secrets/bmj-upload.jks` — must stay outside git (`.gitignore` now covers `*.jks` and `key.properties`).
