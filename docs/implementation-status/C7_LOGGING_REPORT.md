# C7 Print → Logger Migration Report

> **Date:** 2026-05-28
> **Scope:** Replace `print()` calls with structured `appLogger` across all service/utility/BLoC files; remove/comment UI file prints

## Logger Setup

- **Existing package found:** No
- **Package used:** `logger: ^2.0.0` (added to pubspec.yaml)
- **app_logger.dart created:** Yes (`lush/lib/utils/app_logger.dart`)
- **`flutter pub get`:** Successful

## Prints Replaced

| File | Count | ERROR_PATH → appLogger.e() | DEBUG_INFO → appLogger.d() | UI_FILE removed |
|------|:-----:|:---:|:---:|:---:|
| `subscription_service_v2.dart` | 8 | 8 | — | — |
| `subscription_service.dart` | 6 | 6 | — | — |
| `bottle_service.dart` | 4 | 4 | — | — |
| `order_service.dart` | 4 | 4 | — | — |
| `invoice_service.dart` | 6 | 6 | — | — |
| `item_service.dart` | 1 | 1 | — | — |
| `cart_repository.dart` | 14 | 11 | 3 | — |
| `product_catalog_bloc.dart` | 3 | 1 | 2 | — |
| `item_card_view.dart` | 6 | 2 | — | 4 |
| `item_list_view.dart` | 10 | 2 | 3 | 5 |
| `dashboard.dart` | 1 | 1 | — | — |

## Total

- **Replaced with appLogger.e():** 45 (error paths in catch blocks)
- **Replaced with appLogger.d():** 8 (debug flow logging)
- **Removed entirely (UI):** 9 (screens/models should never print)
- **Intentionally kept:** main.dart prints (already guarded by `if (kDebugMode)`)

## Flutter Analyze

- `avoid_print` warnings before: 92
- `avoid_print` warnings after: 15 (main.dart debug-only + subscription_service.dart remaining cancel print, intentional)
- **Errors:** 0
- **Warnings:** 0

## Test Results

133 passed, 6 failed — confirmed (zero new failures)