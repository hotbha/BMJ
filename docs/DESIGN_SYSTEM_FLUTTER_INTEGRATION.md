# Design System → Flutter Integration

**Document Version:** 1.0  
**Last Updated:** 2026-05-08

---

## Overview

This document maps tokens from `docs/DESIGN_SYSTEM.md` to Flutter implementation. All tokens are implemented through Material 3 `ThemeData` with light and dark variants.

---

## Color Token Mapping

| Design Token | Hex | Flutter Constant | ThemeData Key |
|-------------|-----|-----------------|---------------|
| Primary Orange | `#FF8C42` | `AppColors.primaryOrange` | `colorScheme.primary` |
| Primary Orange Dark | `#E67E3A` | `AppColors.primaryOrangeDark` | `colorScheme.primaryContainer` |
| Primary Orange Light | `#FFA96A` | `AppColors.primaryOrangeLight` | — |
| Secondary Teal | `#4ECDC4` | `AppColors.secondaryTeal` | `colorScheme.secondary` |
| Secondary Teal Dark | `#45B7AF` | `AppColors.secondaryTealDark` | `colorScheme.secondaryContainer` |
| Secondary Teal Light | `#7FD9D2` | `AppColors.secondaryTealLight` | — |
| Success | `#4CAF50` | `AppColors.success` | — |
| Warning | `#FFC107` | `AppColors.warning` | — |
| Error | `#F44336` | `AppColors.error` | `colorScheme.error` |
| Info | `#2196F3` | `AppColors.info` | — |
| White | `#FFFFFF` | `AppColors.white` | — |
| Off White | `#FEFEFE` | `AppColors.offWhite` | — |
| Light Grey | `#F5F5F5` | `AppColors.lightGrey` | — |
| Grey | `#9E9E9E` | `AppColors.grey` | — |
| Dark Grey | `#424242` | `AppColors.darkGrey` | — |
| Nearly Black | `#213333` | `AppColors.nearlyBlack` | — |

### Light Theme Colors

| Role | Value | Code |
|------|-------|------|
| scaffoldBackground | `#FAFAFA` | `AppTheme.light.scaffoldBackgroundColor` |
| surface | `#FFFFFF` | `colorScheme.surface` |
| card | `#FFFFFF` | `cardTheme.color` |
| divider | `#E0E0E0` | `dividerTheme.color` |
| primary text | `#213333` | `on(primary/surface)` |
| secondary text | `#424242` | `onSurfaceVariant` |

### Dark Theme Colors

| Role | Value | Code |
|------|-------|------|
| scaffoldBackground | `#121212` | `AppTheme.dark.scaffoldBackgroundColor` |
| surface | `#1E1E1E` | `colorScheme.surface` |
| card | `#1E1E1E` | `cardTheme.color` |
| divider | `#2C2C2C` | `dividerTheme.color` |
| primary text | `#FEFEFE` | `on(primary/surface)` |
| secondary text | `#B0B0B0` | `onSurfaceVariant` |

---

## Typography Token Mapping

| Token | DESIGN_SYSTEM.md | Flutter `TextTheme` | Size/Weight |
|-------|-----------------|-------------------|-------------|
| Display Large | 57px/400 | `displayLarge` | 57, w400 |
| Display Medium | 45px/400 | `displayMedium` | 45, w400 |
| Headline Large | 32px/600 | `headlineLarge` | 32, w600 |
| Headline Medium | 28px/600 | `headlineMedium` | 28, w600 |
| Title Large | 22px/500 | `titleLarge` | 22, w500 |
| Title Medium | 16px/500 | `titleMedium` | 16, w500, 0.15sp |
| Body Large | 16px/400 | `bodyLarge` | 16, w400, 0.5sp |
| Body Medium | 14px/400 | `bodyMedium` | 14, w400, 0.25sp |
| Label Large | 14px/500 | `labelLarge` | 14, w500, 0.1sp |
| Label Small | 11px/500 | `labelSmall` | 11, w500, 0.5sp |

### Font Families

```
Primary: 'Google Sans' → GoogleFonts.productSans()
Fallback: 'Roboto'
```

---

## Spacing Token Mapping

| Token | DESIGN_SYSTEM.md | Flutter |
|-------|-----------------|---------|
| `space.xs` | 4dp | `AppSpacing.xs` → `4.0` |
| `space.sm` | 8dp | `AppSpacing.sm` → `8.0` |
| `space.md` | 16dp | `AppSpacing.md` → `16.0` |
| `space.lg` | 24dp | `AppSpacing.lg` → `24.0` |
| `space.xl` | 32dp | `AppSpacing.xl` → `32.0` |
| `space.xxl` | 48dp | `AppSpacing.xxl` → `48.0` |
| `space.xxxl` | 64dp | `AppSpacing.xxxl` → `64.0` |

---

## Component Theme Mapping

| Component | Token | ThemeData Key |
|-----------|-------|---------------|
| Primary Button | bg: orange, fg: white, radius: 12 | `elevatedButtonTheme` |
| Secondary Button | bg: transparent, border: orange, radius: 12 | `outlinedButtonTheme` |
| Text Button | fg: grey | `textButtonTheme` |
| Input Field | fill: white, border: grey, radius: 12, focus: orange | `inputDecorationTheme` |
| Card | radius: 16, elevation: 2 | `cardTheme` |
| App Bar | bg: surface, fg: primary | `appBarTheme` |
| Bottom Nav | indicator: orange | `navigationBarTheme` |
| Snackbar | bg: dark, fg: white, radius: 8 | `snackBarTheme` |

---

## File Structure

```
lush/lib/theme/
├── app_colors.dart        # Color constants
├── app_text_styles.dart   # Text theme factory
├── app_spacing.dart       # Spacing constants
├── app_icons.dart         # Icon constants
├── app_theme.dart         # Light + dark ThemeData
└── theme_cubit.dart       # Theme state management
```

---

## Implementation Checklist

- [x] `app_colors.dart` — all color tokens from DESIGN_SYSTEM.md
- [x] `app_text_styles.dart` — type scale from DESIGN_SYSTEM.md
- [x] `app_spacing.dart` — spacing scale from DESIGN_SYSTEM.md
- [x] `app_icons.dart` — icon constants from DESIGN_SYSTEM.md
- [x] `app_theme.dart` — light + dark Material3 ThemeData
- [x] `theme_cubit.dart` — theme preference persistence
- [x] `main.dart` — wrapped with ThemeCubit, BlocProvider, MaterialApp.themeMode
- [ ] Delete `lush/lib/theme.dart` (legacy)
- [ ] Tests added for theme and cubit

---

**Document Maintained By:** Engineering Team  
**Last Review:** 2026-05-08
