# C1 LushTheme → AppColors Migration Report

> **Date:** 2026-05-27  
> **Scope:** Migrate all LushTheme.* references to canonical AppColors/AppTextStyles tokens  
> **Reference:** docs/color_system.md  

## Files Migrated (11 total)

| # | File | LushTheme refs replaced | Tokens used | Import removed? |
|---|------|------------------------|-------------|----------------|
| 1 | `lush/lib/views/widgets/welcome_header.dart` | 14 | primaryOrange, lightBackground, white, secondaryTealDark, lightTextSecondary, lightTextPrimary, info, offWhite, grey | ✅ |
| 2 | `lush/lib/views/widgets/cart_icon.dart` | 2 | info | ✅ |
| 3 | `lush/lib/views/widgets/app_card.dart` | 8 | white, grey, lightTextPrimary, lightTextSecondary, info, offWhite | ✅ |
| 4 | `lush/lib/views/widgets/dashboard_components.dart` | 29 | info, lightTextPrimary, lightTextSecondary | ✅ |
| 5 | `lush/lib/views/widgets/subscription_info_card.dart` | 14 | info, lightTextPrimary, lightTextSecondary, grey | ✅ |
| 6 | `lush/lib/views/widgets/subscription_plan_card.dart` | 5 | fontFamily (AppTextStyles) | ✅ |
| 7 | `lush/lib/views/widgets/filter_options.dart` | 22 | info, lightTextPrimary, lightTextSecondary, primaryOrange, fontFamily | ✅ |
| 8 | `lush/lib/views/widgets/size_selection_modal.dart` | 10 | lightTextPrimary, lightTextSecondary | ✅ |
| 9 | `lush/lib/views/models/detailed_juice_card.dart` | 11 | fontFamily (AppTextStyles) | ✅ |
| 10 | `lush/lib/views/models/item_card_view.dart` | 5 | white, fontFamily | ✅ |
| 11 | `lush/lib/views/extensions/theme_extensions.dart` | 5 | offWhite, info, lightBackground, lightTextPrimary, lightTextSecondary | ✅ |

## Mapping Used

| LushTheme token | AppColors/AppTextStyles token |
|----------------|------------------------------|
| `orangeAccent` | `primaryOrange` |
| `background` | `lightBackground` |
| `white` | `white` |
| `nearlyWhite` | `offWhite` |
| `darkerText` | `lightTextPrimary` |
| `lightText` | `lightTextSecondary` |
| `grey` | `grey` |
| `nearlyBlue` | `info` |
| `nearlyDarkBlue` | `secondaryTealDark` |
| `fontName` | `AppTextStyles.fontFamily` |

## Unmapped Properties

None — all LushTheme properties had valid AppColors/AppTextStyles mappings.

## LushTheme References Remaining

Only in `lush/lib/theme.dart` (the shim definition itself). Zero consumer files reference LushTheme.

## Flutter Analyze

- **app_card.dart:** 0 issues (clean)
- **All 11 migrated files:** 1 error fixed (app_card syntax), 0 remaining
- **Full lib/:** 0 errors, 0 warnings (info-level only, pre-existing)

## Test Results

Same pre-existing baseline: 133 passed, 6 failed (zero new failures introduced).