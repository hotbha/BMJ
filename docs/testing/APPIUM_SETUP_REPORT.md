# Appium E2E Setup Report

## Semantic Keys Added

| Screen | Keys Added |
|--------|-----------|
| `splash_page.dart` | splash_screen, splash_logo, splash_title |
| `login_page.dart` | login_tab_sign_in, login_tab_sign_up, login_email_field, login_password_field, login_signin_button, login_forgot_password, google_signin_button, phone_otp_button, signup_email_card, signup_phone_card, signup_google_card |
| `cart_screen.dart` | cart_list, cart_total, checkout_button, empty_cart_message, quantity_increase_button, quantity_decrease_button, remove_item_button |
| `checkout_screen.dart` | checkout_address_display, change_address_button, checkout_item_list, checkout_total_display, place_order_button, checkout_loading_indicator |
| `order_checkout_screen.dart` | order_address, change_address_button, order_item_list, order_total, place_order_button, order_loading, order_success_message |
| `notification_centre_screen.dart` | notification_list, empty_notification_text, mark_all_read_button, notification_back_button |
| `my_account_page.dart` | profile_name, profile_email, profile_phone, logout_button, delete_account_button, edit_profile_button, order_history_button, address_button |
| `profile/address_screen.dart` | address_flat_field, address_building_field, address_street_field, address_area_field, address_city_field, address_pincode_field, address_instructions_field, save_address_button, address_list, add_new_address_button |
| `subscription/active_subscription_screen.dart` | active_subscription_back, subscription_status_chip, pause_subscription_button, resume_subscription_button, cancel_subscription_button, modify_schedule_button, active_subscription_plan_name, next_delivery_date |
| `subscription/pause_subscription_screen.dart` | pause_duration_dropdown, pause_option_1_week, pause_option_2_weeks, pause_option_1_month, confirm_pause_button, cancel_pause_button |
| `subscription/resume_subscription_screen.dart` | resume_now_button, resume_on_next_cycle_button, confirm_resume_button, cancel_resume_button |
| `subscription/cancel_subscription_screen.dart` | cancel_reason_dropdown, cancel_reason_expensive, cancel_reason_not_needed, cancel_reason_other, confirm_cancel_button, cancel_cancel_button |
| `subscription/subscription_summary_screen.dart` | subscription_summary_title, summary_plan_name, summary_frequency, summary_total, summary_confirm_button, summary_edit_button |
| `subscription_family_screen.dart` | family_delight, family_premium |
| `subscription_plan_screen.dart` | subscription_plan_card, confirm_plan_button, subscription_plan_name, subscription_plan_price |
| `subscription_schedule_screen.dart` | schedule_day_monday, frequency_weekly, frequency_biweekly, frequency_monthly, schedule_day_tuesday, schedule_day_wednesday, schedule_day_thursday, schedule_day_friday, schedule_day_saturday, schedule_day_sunday, review_order_button, start_subscription_button, plan_selector |
| `detail.dart` | item_detail_name, item_detail_price, item_detail_description, add_to_cart_button, add_subscription_button, quantity_selector, item_detail_back |
| `product_catalog_screen.dart` | catalog_list, catalog_search_field, catalog_empty_results, catalog_loading, family_filter_juice, family_filter_smoothie, family_filter_detox |
| `dashboard.dart` | dashboard_title, notification_bell, subscription_card, catalog_card, cart_button, profile_button |
| `address_entry_screen.dart` | address_flat_field, address_building_field, address_street_field, address_area_field, address_city_field, address_pincode_field, address_delivery_instructions_field, save_address_button, address_pincode_error |
| `address_screen.dart` | address_list, add_new_address_button |

## Page Objects

| File | Locators |
|------|---------|
| `base_page.py` | find_element, tap, type_text, get_text, wait_for_loading_gone, scroll helpers |
| `login_page.py` | TAB_SIGN_IN, TAB_SIGN_UP, EMAIL_FIELD, PASSWORD_FIELD, SIGNIN_BUTTON, FORGOT_PASSWORD_LINK, GOOGLE_SIGNIN_BUTTON, PHONE_OTP_BUTTON, SIGNUP_EMAIL_CARD, SIGNUP_PHONE_CARD, SIGNUP_GOOGLE_CARD |
| `signup_page.py` | FIRST_NAME_FIELD, LAST_NAME_FIELD, EMAIL_FIELD, PHONE_FIELD, PASSWORD_FIELD, CONFIRM_PASSWORD_FIELD, SIGNUP_BUTTON |
| `home_page.py` | DASHBOARD_TITLE, NOTIFICATION_BELL, PROFILE_BUTTON, SUBSCRIPTION_CARD, CATALOG_CARD, CART_BUTTON |
| `catalog_page.py` | CATALOG_LIST, SEARCH_FIELD, FAMILY_FILTER, EMPTY_RESULTS |
| `item_detail_page.py` | ITEM_NAME, ITEM_PRICE, ADD_TO_CART_BUTTON |
| `cart_page.py` | CART_LIST, CART_TOTAL, CHECKOUT_BUTTON, EMPTY_CART_MESSAGE |
| `order_checkout_page.py` | ORDER_ADDRESS, ORDER_TOTAL, PLACE_ORDER_BUTTON, ORDER_SUCCESS_MESSAGE |
| `address_page.py` | FLAT_FIELD, BUILDING_FIELD, STREET_FIELD, CITY_FIELD, PINCODE_FIELD, SAVE_ADDRESS_BUTTON |
| `profile_page.py` | PROFILE_NAME, PROFILE_EMAIL, PROFILE_PHONE, LOGOUT_BUTTON |
| `notification_centre_page.py` | NOTIFICATION_LIST, EMPTY_NOTIFICATION_TEXT, MARK_ALL_READ_BUTTON |
| `subscription_plans_page.py` | PLAN_CARD, CONFIRM_PLAN_BUTTON, FAMILY_DELIGHT, FAMILY_PREMIUM, FREQUENCY_WEEKLY, FREQUENCY_MONTHLY |
| `subscription_summary_page.py` | SUMMARY_TITLE, SUMMARY_PLAN_NAME, SUMMARY_TOTAL, CONFIRM_BUTTON |
| `subscription_active_page.py` | STATUS_CHIP, PAUSE_BUTTON, RESUME_BUTTON, CANCEL_BUTTON, MODIFY_SCHEDULE_BUTTON |
| `pause_subscription_page.py` | PAUSE_DURATION_DROPDOWN, PAUSE_OPTIONS, CONFIRM_PAUSE_BUTTON |
| `resume_subscription_page.py` | RESUME_NOW_BUTTON, CONFIRM_RESUME_BUTTON |
| `cancel_subscription_page.py` | CANCEL_REASON_DROPDOWN, CONFIRM_CANCEL_BUTTON |
| `splash_page.py` | SPLASH_LOGO, SPLASH_TITLE, LOGIN_BUTTON |

## Test Files

| Suite | File | TC Count |
|-------|------|----------|
| 1 — Auth | `test_auth.py` | 12 |
| 2 — Address | `test_address.py` | 8 |
| 3 — Catalog | `test_catalog.py` | 10 |
| 4 — Subscription | `test_subscription.py` | 16 |
| 5 — Orders | `test_orders.py` | 14 |
| 6 — Notifications | `test_notifications.py` | 10 |
| 7 — Profile | `test_profile.py` | 8 |
| 8 — Navigation | `test_navigation.py` | 10 |
| 9 — Edge Cases | `test_edge_cases.py` | 12 |

**Total test cases: 100** ✅

## Infrastructure Files

| File | Purpose |
|------|---------|
| `requirements.txt` | Python dependencies |
| `.env.example` | Environment variables template |
| `config/device_config.json` | Appium desired capabilities |
| `config/test_config.py` | Python config with env validation |
| `conftest.py` | Pytest fixtures (driver, logged_in, clean_subscription, clean_orders, auto-screenshot) |
| `preflight.py` | 7 environment checks + human checklist |
| `run_all.sh` | Full suite runner |
| `run_smoke.sh` | Smoke test runner (auth, catalog, subscription, orders) |
| `README.md` | Setup & usage instructions |

## Verification

- **100 test cases** written across 9 test files
- **18 page objects** created with ACCESSIBILITY_ID locators
- **18+ Flutter screens** modified with Key() attributes
- **Real integrations only**: Firebase Auth, Chargebee TEST, bmjServer, FCM
- **Conftest** with auto-screenshot on failure
- **Preflight checker** with human checklist + 7 automated environment checks
- **Runners**: `run_smoke.sh` and `run_all.sh`
- **Fixtures**: `clean_subscription` (cancels Chargebee subs), `clean_orders` (clears pending orders)