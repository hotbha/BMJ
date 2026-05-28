# BookMyJuice Color System — Reference Document

> **Purpose:** Document the canonical color class name(s), every defined color token, and a find-replace table for incorrect or legacy references.
>
> **Scope:** Flutter codebase under `lush/`. No `.dart` files were modified to produce this document.

---

## 1. Canonical Color Class Name(s)

### ✅ Primary: `AppColors`

| Attribute | Value |
|-----------|-------|
| **File** | `lush/lib/theme/app_colors.dart` |
| **Declaration** | `class AppColors { AppColors._(); … }` |
| **Import** | `import 'package:flutter/material.dart';` (no app-specific import needed — part of the theme library) |
| **Project uses** | **30** `.dart` files reference `AppColors.*` tokens |

All new code should use `AppColors.*` directly.

> ⚠️ **No other variant classes exist.** The following are **NOT present** anywhere in the codebase:
> - `AppAppColors` ❌ (zero references)
> - `AppAppAppColors` ❌ (zero references)

### 🔁 Legacy Shim: `LushTheme`

| Attribute | Value |
|-----------|-------|
| **File** | `lush/lib/theme.dart` |
| **Declaration** | `class LushTheme { LushTheme._(); … }` |
| **Status** | **DEPRECATED** — see docs/DESIGN_SYSTEM_FLUTTER_INTEGRATION.md checklist |
| **Project uses** | **10** `.dart` files still reference `LushTheme.*` |

Every `LushTheme.*` property is a simple delegation to the corresponding `AppColors.*` token. New code must prefer `AppColors` directly.

---

## 2. Every Color Token Defined (Name + Hex Value)

All values are from the canonical source `lush/lib/theme/app_colors.dart`.

### Brand — Primary (Orange)

| Token | Hex | Dart |
|-------|-----|------|
| `primaryOrange` | `#FF8C42` | `Color(0xFFFF8C42)` |
| `primaryOrangeDark` | `#E67E3A` | `Color(0xFFE67E3A)` |
| `primaryOrangeLight` | `#FFA96A` | `Color(0xFFFFA96A)` |

### Brand — Gradients

| Token | Hex | Dart |
|-------|-----|------|
| `gradientStart` | `#FFA726` | `Color(0xFFFFA726)` |
| `gradientEnd` | `#FF7043` | `Color(0xFFFF7043)` |

### Brand — Secondary (Teal)

| Token | Hex | Dart |
|-------|-----|------|
| `secondaryTeal` | `#4ECDC4` | `Color(0xFF4ECDC4)` |
| `secondaryTealDark` | `#45B7AF` | `Color(0xFF45B7AF)` |
| `secondaryTealLight` | `#7FD9D2` | `Color(0xFF7FD9D2)` |

### Semantic / Status Colors

| Token | Hex | Dart |
|-------|-----|------|
| `success` | `#4CAF50` | `Color(0xFF4CAF50)` |
| `warning` | `#FFC107` | `Color(0xFFFFC107)` |
| `error` | `#F44336` | `Color(0xFFF44336)` |
| `info` | `#2196F3` | `Color(0xFF2196F3)` |

### Neutral Colors

| Token | Hex | Dart |
|-------|-----|------|
| `white` | `#FFFFFF` | `Color(0xFFFFFFFF)` |
| `offWhite` | `#FEFEFE` | `Color(0xFFFEFEFE)` |
| `lightGrey` | `#F5F5F5` | `Color(0xFFF5F5F5)` |
| `grey` | `#9E9E9E` | `Color(0xFF9E9E9E)` |
| `darkGrey` | `#424242` | `Color(0xFF424242)` |
| `nearlyBlack` | `#213333` | `Color(0xFF213333)` |

### White Opacity Variants

| Token | Hex (ARGB) | Dart |
|-------|------------|------|
| `white54` | `#8AFFFFFF` (54%) | `Color(0x8AFFFFFF)` |
| `white70` | `#B3FFFFFF` (70%) | `Color(0xB3FFFFFF)` |

### Light Theme Surfaces

| Token | Hex | Dart |
|-------|-----|------|
| `lightBackground` | `#FAFAFA` | `Color(0xFFFAFAFA)` |
| `lightSurface` | `#FFFFFF` | `Color(0xFFFFFFFF)` |
| `lightCard` | `#FFFFFF` | `Color(0xFFFFFFFF)` |
| `lightDivider` | `#E0E0E0` | `Color(0xFFE0E0E0)` |
| `lightTextPrimary` | `#213333` | `Color(0xFF213333)` |
| `lightTextSecondary` | `#424242` | `Color(0xFF424242)` |
| `lightTextDisabled` | `#BDBDBD` | `Color(0xFFBDBDBD)` |

### Dark Theme Surfaces

| Token | Hex | Dart |
|-------|-----|------|
| `darkBackground` | `#121212` | `Color(0xFF121212)` |
| `darkSurface` | `#1E1E1E` | `Color(0xFF1E1E1E)` |
| `darkCard` | `#1E1E1E` | `Color(0xFF1E1E1E)` |
| `darkDivider` | `#2C2C2C` | `Color(0xFF2C2C2C)` |
| `darkTextPrimary` | `#FEFEFE` | `Color(0xFFFEFEFE)` |
| `darkTextSecondary` | `#B0B0B0` | `Color(0xFFB0B0B0)` |
| `darkTextDisabled` | `#808080` | `Color(0xFF808080)` |

**Total: 31 unique tokens.**

---

## 3. Find-Replace Table

### 3a. Non‑existent class names

| Wrong | Correct | Notes |
|-------|---------|-------|
| `AppAppColors` | `AppColors` | **Does not exist** anywhere in the codebase (0 references). |
| `AppAppAppColors` | `AppColors` | **Does not exist** anywhere in the codebase (0 references). |
| `AppAppColors.*` | `AppColors.*` | Same as above — zero usage found. |

### 3b. Legacy `LushTheme.*` → Canonical `AppColors.*`

| Legacy (`LushTheme.*`) | Canonical (`AppColors.*`) | Files affected |
|-------------------------|---------------------------|----------------|
| `LushTheme.orangeAccent` | `AppColors.primaryOrange` | `app_card.dart`, `cart_icon.dart`, `dashboard_components.dart`, `filter_options.dart`, `size_selection_modal.dart`, `subscription_info_card.dart`, `subscription_plan_card.dart`, `welcome_header.dart` |
| `LushTheme.background` | `AppColors.lightBackground` | `theme_extensions.dart`, `dashboard_components.dart` |
| `LushTheme.white` | `AppColors.white` | `app_card.dart`, `item_card_view.dart` |
| `LushTheme.nearlyWhite` | `AppColors.offWhite` | `theme_extensions.dart` |
| `LushTheme.darkerText` | `AppColors.lightTextPrimary` | `theme_extensions.dart` |
| `LushTheme.lightText` | `AppColors.lightTextSecondary` | `theme_extensions.dart` |
| `LushTheme.grey` | `AppColors.grey` | (in widgets; check references) |
| `LushTheme.appbarColor` | `AppColors.primaryOrange` | (in widgets; check references) |
| `LushTheme.nearlyBlue` | `AppColors.info` | `theme_extensions.dart` |
| `LushTheme.nearlyDarkBlue` | `AppColors.secondaryTealDark` | (in widgets; check references) |
| `LushTheme.fontName` (string) | `AppTextStyles.fontFamily` | `detailed_juice_card.dart`, `item_card_view.dart` (not a color, but legacy dep) |

### 3c. Files using `LushTheme` (need migration)

| # | File | Path |
|---|------|------|
| 1 | `theme_extensions.dart` | `lush/lib/views/extensions/theme_extensions.dart` |
| 2 | `detailed_juice_card.dart` | `lush/lib/views/models/detailed_juice_card.dart` |
| 3 | `item_card_view.dart` | `lush/lib/views/models/item_card_view.dart` |
| 4 | `app_card.dart` | `lush/lib/views/widgets/app_card.dart` |
| 5 | `cart_icon.dart` | `lush/lib/views/widgets/cart_icon.dart` |
| 6 | `dashboard_components.dart` | `lush/lib/views/widgets/dashboard_components.dart` |
| 7 | `filter_options.dart` | `lush/lib/views/widgets/filter_options.dart` |
| 8 | `size_selection_modal.dart` | `lush/lib/views/widgets/size_selection_modal.dart` |
| 9 | `subscription_info_card.dart` | `lush/lib/views/widgets/subscription_info_card.dart` |
| 10 | `subscription_plan_card.dart` | `lush/lib/views/widgets/subscription_plan_card.dart` |
| 11 | `welcome_header.dart` | `lush/lib/views/widgets/welcome_header.dart` |
| 12 | `theme.dart` (definition) | `lush/lib/theme.dart` |

### 3d. Files using `AppColors.*` directly (already canonical)

| # | File |
|---|------|
| 1 | `lush/lib/theme/app_colors.dart` *(definition)* |
| 2 | `lush/lib/theme/app_theme.dart` |
| 3 | `lush/lib/theme.dart` *(delegation layer)* |
| 4 | `lush/lib/widgets/app_text_field.dart` |
| 5–32 | **28 screen files** under `lush/lib/views/screens/` |
| — | `address_screen.dart` |
| — | `address_selection_screen.dart` |
| — | `cart_screen.dart` |
| — | `create_password_screen.dart` |
| — | `dashboard.dart` |
| — | `day_wise_schedule_screen.dart` |
| — | `delete_account_screen.dart` |
| — | `delivery_slot_selection_screen.dart` |
| — | `email_signup_screen.dart` |
| — | `forgot_password_screen.dart` |
| — | `google_signup_screen.dart` |
| — | `link_google_account_screen.dart` |
| — | `login_page.dart` |
| — | `menu.dart` |
| — | `notifications.dart` |
| — | `order_history_page.dart` |
| — | `phone_login_screen.dart` |
| — | `plan_selection_screen.dart` |
| — | `product_catalog_screen.dart` |
| — | `reset_password_email_screen.dart` |
| — | `reset_password_mobile_screen.dart` |
| — | `settings_page.dart` |
| — | `sign_up_screen.dart` |
| — | `signup_method_selection_screen.dart` |
| — | `splash_page.dart` |

---

## 4. Usage Statistics (AppColors tokens in screen files)

Token usage counts across all 28 screen files give a picture of which tokens are most heavily used:

| Token | Reference count |
|-------|:---------------:|
| `primaryOrange` | **113** |
| `white` | **101** |
| `lightTextPrimary` | **58** |
| `lightTextSecondary` | **49** |
| `error` | **34** |
| `grey` | **30** |
| `success` | **28** |
| `info` | **24** |
| `darkGrey` | **20** |
| `lightDivider` | **17** |
| `primaryOrangeDark` | **16** |
| `nearlyBlack` | **9** |
| `lightBackground` | **8** |
| `lightGrey` | **7** |
| `secondaryTeal` | **5** |
| `white54` | **4** |
| `white70` | **4** |
| `gradientEnd` | **3** |
| `gradientStart` | **2** |
| `lightTextDisabled` | **2** |
| `lightSurface` | **1** |
| *(remaining: 0 refs in screens)* | *(used only in theme definitions)* |

---

## 5. Underlying Files & Context

| Resource | Location |
|----------|----------|
| Canonical color definitions | `lush/lib/theme/app_colors.dart` (71 lines) |
| ThemeData factories (light + dark) | `lush/lib/theme/app_theme.dart` (427 lines) |
| Legacy backward-compatible shim | `lush/lib/theme.dart` (68 lines) |
| Design system spec (markdown) | `docs/DESIGN_SYSTEM.md` |
| Flutter integration map | `docs/DESIGN_SYSTEM_FLUTTER_INTEGRATION.md` |

---

## 6. Noisa / False‑positive check

The following nonexistent class names were searched across the entire `lush/` directory and **zero** results were found:

| Pattern | Results |
|---------|:-------:|
| `AppAppColors` | **0** files, **0** references |
| `AppAppAppColors` | **0** files, **0** references |
| `AppAppColors.` | **0** hits |
| `AppAppAppColors.` | **0** hits |

---

> **Generated:** 2026-05-26  
> **Tooling:** PowerShell `Select-String`, manual code review of `lush/lib/theme/app_colors.dart`  
> **Compliance:** Files match `docs/DESIGN_SYSTEM.md` and `docs/DESIGN_SYSTEM_FLUTTER_INTEGRATION.md` token maps.
