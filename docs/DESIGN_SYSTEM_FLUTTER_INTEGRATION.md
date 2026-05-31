# Design System → Flutter Integration

**Document Version:** 2.0  
**Last Updated:** 2026-05-29

---

## Overview

This document maps tokens from `docs/DESIGN_SYSTEM.md` to Flutter implementation. All tokens are implemented through Material 3 `ThemeData` with light and dark variants.

---

## Color Token Mapping

| Design Token | Hex | Flutter Constant | ThemeData Key |
|-------------|-----|-----------------|---------------|
| Primary Green | `#2E7D32` | `AppColors.primaryGreen` | `colorScheme.primary` |
| Primary Green Dark | `#1B5E20` | `AppColors.primaryGreenDark` | `colorScheme.primaryContainer` |
| Primary Green Light | `#43A047` | `AppColors.primaryGreenLight` | — |
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
| Primary Button | bg: green #2E7D32, fg: white, radius: 12 | `elevatedButtonTheme` |
| Secondary Button | bg: transparent, border: green, radius: 12 | `outlinedButtonTheme` |
| Text Button | fg: grey | `textButtonTheme` |
| Input Field | fill: white, border: grey, radius: 12, focus: green | `inputDecorationTheme` |
| Card | radius: 16, elevation: 2 | `cardTheme` |
| App Bar | bg: surface, fg: primary | `appBarTheme` |
| Bottom Nav | indicator: green | `navigationBarTheme` |
| Snackbar | bg: dark, fg: white, radius: 8 | `snackBarTheme` |

---

## Glassmorphism Color Tokens (v2.0)

New glass tokens added to `AppColors` (`lib/theme/app_colors.dart`):

| Token | Hex (Dark) | Hex (Light) | Flutter Constant |
|-------|-----------|------------|-----------------|
| Glass Background | `#0A0F0D` | `#F0F5F2` | `AppColors.glassBg` / `glassBgLight` |
| Glass Elevated | `#0F1613` | `#EAF0EC` | `AppColors.glassElevated` / `glassElevatedLight` |
| Glass Surface | 6% white | 40% white | `AppColors.glassSurface` / `glassSurfaceLight` |
| Glass Surface Strong | 8% white | — | `AppColors.glassSurfaceStrong` |
| Glass Border | 12% white | 20% black | `AppColors.glassBorder` / `glassBorderLight` |
| Glass Border Subtle | 8% white | — | `AppColors.glassBorderSubtle` |
| Glass Text Primary | `#E8F5E9` | text-primary | `AppColors.glassText` |
| Glass Text Dim | `#9FB0A8` | text-secondary | `AppColors.glassTextDim` |
| Glass Accent Green | `#22C55E` | — | `AppColors.glassAccent` |
| Glass Accent Dark | `#16A34A` | — | `AppColors.glassAccentDark` |
| Glass Orange | `#FB923C` | — | `AppColors.glassOrange` |
| Glass Pink | `#F472B6` | — | `AppColors.glassPink` |
| Glass Purple | `#A78BFA` | — | `AppColors.glassPurple` |
| Glass Glow Shadow | 25% neon green | — | `AppColors.glassGlow` |

## Border Radius Tokens (v2.0)

Added to `AppRadius` (`lib/theme/app_radius.dart`):

| Token | dp | Flutter Constant | Usage |
|-------|----|-----------------|-------|
| sm | 8 | `AppRadius.sm` | Chips, snackbars |
| md | 12 | `AppRadius.md` | Buttons, inputs, cards |
| lg | 16 | `AppRadius.lg` | Bottom sheets, large cards |
| xl | 24 | `AppRadius.xl` | Glass cards, hero cards, modals |
| xxl | 32 | `AppRadius.xxl` | Bottom nav inner, large containers |
| circular | 48 | `AppRadius.circular` | Circular/pill shapes |

## Glassmorphism Widgets (v2.0)

| Widget | File | Description |
|--------|------|-------------|
| `GlassCard` | `lib/widgets/glass_card.dart` | Reusable glassmorphism container with configurable blur/opacity/glow/gradient |
| `GlassChip` | `lib/widgets/glass_card.dart` | Glassmorphism category chip with selected state |
| `GlassSegmentToggle` | `lib/widgets/glass_card.dart` | Glassmorphism segment control (One-Time / Subscribe) |
| `CartBadgeIcon` | `lib/widgets/cart_badge_icon.dart` | Shopping bag icon with neon green badge count via `BlocBuilder<CartBloc>` |

### GlassCard Usage

```dart
GlassCard(
  padding: const EdgeInsets.all(20),
  borderRadius: AppRadius.xl,    // 24px default
  blur: 10.0,
  hasGlow: true,
  glowColor: AppColors.glassAccent,
  onTap: () => _handleTap(),
  child: /* content */,
)
```

### GlassChip Usage

```dart
GlassChip(
  label: 'Orange',
  isSelected: true,
  selectedColor: AppColors.glassAccent,
  onTap: () => _filterByCategory('Orange'),
)
```

## Dashboard Shell Architecture (v2.0)

The Dashboard uses `IndexedStack` with 4 tabs and glass bottom navigation:

| Tab | File | Description |
|-----|------|-------------|
| Home | `lib/views/screens/home_tab.dart` | Hero greeting, subscription card, stats strip, order today with glass cards |
| Menu | `lib/views/screens/menu_tab.dart` | One-Time catalog + Subscribe plans with `GlassSegmentToggle` |
| Orders | `lib/views/screens/orders_tab.dart` | Order history with glass tiles; sign-in CTA if unauthenticated |
| Profile | `lib/views/screens/profile_tab.dart` | Profile header, menu items, theme toggle chips, logout |

### Route Changes in `main.dart`

| Old Route | New Route |
|-----------|-----------|
| `/menu` → `Menu()` | `/menu` → `Dashboard()` |
| `/dashboard` → `Dashboard()` | (unchanged) |
| `/home` → `Dashboard()` | (unchanged) |

## File Structure

```
lush/lib/theme/
├── app_colors.dart        # Color constants (incl. glass tokens)
├── app_text_styles.dart   # Text theme factory
├── app_spacing.dart       # Spacing constants
├── app_radius.dart        # Border radius constants (v2.0)
├── app_icons.dart         # Icon constants
├── app_theme.dart         # Light + dark ThemeData
└── theme_cubit.dart       # Theme state management

lush/lib/widgets/
├── glass_card.dart        # GlassCard, GlassChip, GlassSegmentToggle (v2.0)
└── cart_badge_icon.dart   # CartBadgeIcon (v2.0)
```

---

## Implementation Checklist

- [x] `app_colors.dart` — all color tokens from DESIGN_SYSTEM.md + glassmorphism tokens
- [x] `app_text_styles.dart` — type scale from DESIGN_SYSTEM.md
- [x] `app_spacing.dart` — spacing scale from DESIGN_SYSTEM.md
- [x] `app_icons.dart` — icon constants from DESIGN_SYSTEM.md
- [x] `app_radius.dart` — border radius tokens (sm, md, lg, xl, xxl, circular)
- [x] `app_theme.dart` — light + dark Material3 ThemeData (seedColor uses primaryGreen)
- [x] `theme_cubit.dart` — theme preference persistence
- [x] `main.dart` — wrapped with ThemeCubit, BlocProvider, MaterialApp.themeMode
- [x] `glass_card.dart` — GlassCard, GlassChip, GlassSegmentToggle widgets
- [x] `cart_badge_icon.dart` — CartBadgeIcon with BlocBuilder<CartBloc>
- [x] `dashboard.dart` — glassmorphism shell with IndexedStack + 4 tabs
- [x] `home_tab.dart` — Home tab with glass cards, subscription, stats strip
- [x] `menu_tab.dart` — Menu tab with One-Time + Subscribe segment toggle
- [x] `orders_tab.dart` — Orders tab with glass history tiles
- [x] `profile_tab.dart` — Profile tab with theme toggle, glass avatar
- [ ] Delete `lush/lib/theme.dart` (legacy)
- [ ] Tests added for theme, cubit, and glass widgets

---

**Document Maintained By:** Engineering Team  
**Last Review:** 2026-05-29