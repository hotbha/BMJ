# BookMyJuice Design System

> A comprehensive design system for building consistent, accessible, and beautiful user experiences across the BookMyJuice mobile application.

## Table of Contents

- [Introduction](#introduction)
- [Design Principles](#design-principles)
- [Colors](#colors)
- [Typography](#typography)
- [Spacing & Layout](#spacing--layout)
- [Icons](#icons)
- [Components](#components)
- [Patterns](#patterns)
- [Accessibility](#accessibility)
- [Resources](#resources)

---

## Introduction

The BookMyJuice Design System is a living document that provides guidelines, components, and patterns for building consistent user experiences. This system is built on Material Design 3 principles with custom branding for BookMyJuice.

### Brand Identity

**Brand Values:**
- Fresh & Natural
- Healthy & Trustworthy
- Modern & Convenient
- Customer-Focused

**Brand Colors:**
- Primary: Orange (energy, vitality, freshness)
- Secondary: Teal (health, balance, tranquility)

---

## Design Principles

### 1. Clarity
Every screen should have a single clear purpose. Users should immediately understand what they can do.

**Implementation:**
- One primary action per screen
- Clear visual hierarchy
- Minimal cognitive load

### 2. Consistency
Use consistent patterns across the app to reduce learning curve.

**Implementation:**
- Reusable components
- Standardized interactions
- Predictable behavior

### 3. Feedback
Provide immediate feedback for every user action.

**Implementation:**
- Loading states
- Success/error messages
- Haptic feedback
- Visual state changes

### 4. Efficiency
Minimize the number of taps to complete common tasks.

**Implementation:**
- Smart defaults
- One-tap reordering
- Saved preferences
- Quick actions

### 5. Accessibility
Design for all users, regardless of ability.

**Implementation:**
- WCAG 2.1 AA compliance
- Screen reader support
- Dynamic text sizes
- High contrast modes

### 6. Performance
Maintain 60 FPS and fast load times.

**Implementation:**
- Optimized animations
- Lazy loading
- Efficient rendering
- Caching strategies

---

## Colors

### Brand Colors

```dart
// Primary Brand Colors
static const Color primaryOrange = Color(0xFFFF8C42);
static const Color primaryOrangeDark = Color(0xFFE67E3A);
static const Color primaryOrangeLight = Color(0xFFFFA96A);

// Secondary Brand Colors
static const Color secondaryTeal = Color(0xFF4ECDC4);
static const Color secondaryTealDark = Color(0xFF45B7AF);
static const Color secondaryTealLight = Color(0xFF7FD9D2);
```

### Semantic Colors

```dart
// Status Colors
static const Color success = Color(0xFF4CAF50);
static const Color warning = Color(0xFFFFC107);
static const Color error = Color(0xFFF44336);
static const Color info = Color(0xFF2196F3);

// Neutral Colors
static const Color white = Color(0xFFFFFFFF);
static const Color offWhite = Color(0xFFFEFEFE);
static const Color lightGrey = Color(0xFFF5F5F5);
static const Color grey = Color(0xFF9E9E9E);
static const Color darkGrey = Color(0xFF424242);
static const Color nearlyBlack = Color(0xFF213333);
```

### Light Theme Palette

```dart
static final ThemeData lightTheme = ThemeData(
  brightness: Brightness.light,
  primaryColor: primaryOrange,
  scaffoldBackgroundColor: Color(0xFFFAFAFA),
  surfaceColor: white,
  cardColor: white,
  dividerColor: Color(0xFFE0E0E0),
  
  textTheme: TextTheme(
    headlineLarge: TextStyle(color: nearlyBlack),
    headlineMedium: TextStyle(color: nearlyBlack),
    bodyLarge: TextStyle(color: nearlyBlack),
    bodyMedium: TextStyle(color: darkGrey),
    bodySmall: TextStyle(color: grey),
  ),
  
  inputDecorationTheme: InputDecorationTheme(
    filled: true,
    fillColor: white,
    border: OutlineInputBorder(
      borderRadius: BorderRadius.circular(12),
      borderSide: BorderSide(color: grey, width: 1),
    ),
    enabledBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(12),
      borderSide: BorderSide(color: grey, width: 1),
    ),
    focusedBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(12),
      borderSide: BorderSide(color: primaryOrange, width: 2),
    ),
    errorBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(12),
      borderSide: BorderSide(color: error, width: 1),
    ),
  ),
);
```

### Dark Theme Palette

```dart
static final ThemeData darkTheme = ThemeData(
  brightness: Brightness.dark,
  primaryColor: primaryOrange,
  scaffoldBackgroundColor: Color(0xFF121212),
  surfaceColor: Color(0xFF1E1E1E),
  cardColor: Color(0xFF1E1E1E),
  dividerColor: Color(0xFF2C2C2C),
  
  textTheme: TextTheme(
    headlineLarge: TextStyle(color: offWhite),
    headlineMedium: TextStyle(color: offWhite),
    bodyLarge: TextStyle(color: offWhite),
    bodyMedium: TextStyle(color: Color(0xFFB0B0B0)),
    bodySmall: TextStyle(color: Color(0xFF808080)),
  ),
  
  inputDecorationTheme: InputDecorationTheme(
    filled: true,
    fillColor: Color(0xFF2C2C2C),
    border: OutlineInputBorder(
      borderRadius: BorderRadius.circular(12),
      borderSide: BorderSide(color: Color(0xFF424242), width: 1),
    ),
    enabledBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(12),
      borderSide: BorderSide(color: Color(0xFF424242), width: 1),
    ),
    focusedBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(12),
      borderSide: BorderSide(color: primaryOrange, width: 2),
    ),
    errorBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(12),
      borderSide: BorderSide(color: error, width: 1),
    ),
  ),
);
```

### Color Usage Guidelines

| Use Case | Light Theme | Dark Theme |
|----------|-------------|------------|
| Primary Text | `#213333` | `#FEFEFE` |
| Secondary Text | `#757575` | `#B0B0B0` |
| Disabled Text | `#BDBDBD` | `#808080` |
| Background | `#FAFAFA` | `#121212` |
| Surface | `#FFFFFF` | `#1E1E1E` |
| Divider | `#E0E0E0` | `#2C2C2C` |
| Primary Button | `#FF8C42` | `#FF8C42` |

---

## Typography

### Font Families

```dart
// Primary Font (Google Sans via Google Fonts)
static const String fontFamilyPrimary = 'Google Sans';

// Fallback Font
static const String fontFamilySecondary = 'Roboto';
```

### Type Scale

| Style | Size | Weight | Line Height | Letter Spacing | Use Case |
|-------|------|--------|-------------|----------------|----------|
| Display Large | 57px | 400 | 64px | -0.25px | Hero sections |
| Display Medium | 45px | 400 | 52px | 0px | Major headings |
| Headline Large | 32px | 600 | 40px | 0px | Screen titles |
| Headline Medium | 28px | 600 | 36px | 0px | Section headers |
| Title Large | 22px | 500 | 28px | 0px | Card titles |
| Title Medium | 16px | 500 | 24px | 0.15px | Subtitles |
| Body Large | 16px | 400 | 24px | 0.5px | Paragraphs |
| Body Medium | 14px | 400 | 20px | 0.25px | Body text |
| Label Large | 14px | 500 | 20px | 0.1px | Buttons |
| Label Small | 11px | 500 | 16px | 0.5px | Captions |

### Implementation

```dart
static TextTheme get textTheme {
  return const TextTheme(
    displayLarge: TextStyle(
      fontSize: 57,
      fontWeight: FontWeight.w400,
      height: 64 / 57,
      letterSpacing: -0.25,
    ),
    displayMedium: TextStyle(
      fontSize: 45,
      fontWeight: FontWeight.w400,
      height: 52 / 45,
    ),
    headlineLarge: TextStyle(
      fontSize: 32,
      fontWeight: FontWeight.w600,
      height: 40 / 32,
    ),
    headlineMedium: TextStyle(
      fontSize: 28,
      fontWeight: FontWeight.w600,
      height: 36 / 28,
    ),
    titleLarge: TextStyle(
      fontSize: 22,
      fontWeight: FontWeight.w500,
      height: 28 / 22,
    ),
    titleMedium: TextStyle(
      fontSize: 16,
      fontWeight: FontWeight.w500,
      height: 24 / 16,
      letterSpacing: 0.15,
    ),
    bodyLarge: TextStyle(
      fontSize: 16,
      fontWeight: FontWeight.w400,
      height: 24 / 16,
      letterSpacing: 0.5,
    ),
    bodyMedium: TextStyle(
      fontSize: 14,
      fontWeight: FontWeight.w400,
      height: 20 / 14,
      letterSpacing: 0.25,
    ),
    labelLarge: TextStyle(
      fontSize: 14,
      fontWeight: FontWeight.w500,
      height: 20 / 14,
      letterSpacing: 0.1,
    ),
    labelSmall: TextStyle(
      fontSize: 11,
      fontWeight: FontWeight.w500,
      height: 16 / 11,
      letterSpacing: 0.5,
    ),
  );
}
```

### Typography Guidelines

**DO:**
- Use semantic text styles (headline, body, label)
- Maintain minimum 16px for input text (iOS requirement)
- Test with dynamic text sizing enabled
- Ensure sufficient contrast (4.5:1 for text)

**DON'T:**
- Use more than 3 font weights per screen
- Mix font families
- Use all caps for body text
- Go below 11px for any text

---

## Spacing & Layout

### Spacing Scale

Base unit: **4dp**

| Token | Value | Use Case |
|-------|-------|----------|
| `space.xs` | 4dp | Tight spacing (icon-text gap) |
| `space.sm` | 8dp | Small spacing (list items) |
| `space.md` | 16dp | Default spacing (padding) |
| `space.lg` | 24dp | Section spacing |
| `space.xl` | 32dp | Large section gaps |
| `space.xxl` | 48dp | Major divisions |
| `space.xxxl` | 64dp | Screen margins |

### Implementation

```dart
class AppSpacing {
  static const double xs = 4.0;
  static const double sm = 8.0;
  static const double md = 16.0;
  static const double lg = 24.0;
  static const double xl = 32.0;
  static const double xxl = 48.0;
  static const double xxxl = 64.0;
}
```

### Layout Grid

**Mobile (Phone):**
- Columns: 4
- Margins: 16dp
- Gutter: 16dp

**Tablet:**
- Columns: 8
- Margins: 24dp
- Gutter: 24dp

### Screen Layouts

```dart
// Standard screen padding
Padding(
  padding: const EdgeInsets.symmetric(
    horizontal: AppSpacing.md,
  ),
  child: Column(
    children: [...],
  ),
)

// Section spacing
SizedBox(height: AppSpacing.lg)

// Card padding
Padding(
  padding: const EdgeInsets.all(AppSpacing.md),
  child: Card(...),
)
```

---

## Icons

### Icon Guidelines

- **Size:** 24dp (standard), 20dp (small), 32dp (large)
- **Style:** Outlined for most uses, filled for active states
- **Color:** Follow text color hierarchy
- **Touch Target:** Minimum 48x48dp

### Icon Library

```dart
// Primary icon set
import 'package:font_awesome_flutter/font_awesome_flutter.dart';

// Common icons used in app
class AppIcons {
  // Navigation
  static const IconData home = Icons.home_outlined;
  static const IconData search = Icons.search;
  static const IconData cart = Icons.shopping_cart_outlined;
  static const IconData profile = Icons.person_outline;
  
  // Actions
  static const IconData add = Icons.add;
  static const IconData remove = Icons.remove;
  static const IconData close = Icons.close;
  static const IconData check = Icons.check;
  
  // Status
  static const IconData success = Icons.check_circle_outline;
  static const IconData error = Icons.error_outline;
  static const IconData warning = Icons.warning_amber;
  static const IconData info = Icons.info_outline;
  
  // Product
  static const IconData juice = Icons.local_drink_outlined;
  static const IconData subscription = Icons.repeat;
  static const IconData order = Icons.receipt_long;
}
```

---

## Components

### Buttons

#### Primary Button

```dart
// Usage
AppButton.primary(
  text: 'Add to Cart',
  onPressed: () {},
  icon: Icons.shopping_cart,
  isLoading: false,
  isFullWidth: true,
)

// Implementation
class AppButton extends StatelessWidget {
  final String text;
  final VoidCallback? onPressed;
  final IconData? icon;
  final bool isLoading;
  final bool isFullWidth;
  
  const AppButton.primary({
    required this.text,
    this.onPressed,
    this.icon,
    this.isLoading = false,
    this.isFullWidth = false,
    Key? key,
  }) : super(key: key);
  
  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: isFullWidth ? double.infinity : null,
      height: 48,
      child: ElevatedButton(
        onPressed: isLoading ? null : onPressed,
        style: ElevatedButton.styleFrom(
          backgroundColor: AppColors.primaryOrange,
          foregroundColor: AppColors.white,
          elevation: 2,
          padding: const EdgeInsets.symmetric(horizontal: 24),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
        child: isLoading
            ? const SizedBox(
                width: 20,
                height: 20,
                child: CircularProgressIndicator(
                  strokeWidth: 2,
                  valueColor: AlwaysStoppedAnimation<Color>(
                    AppColors.white,
                  ),
                ),
              )
            : Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  if (icon != null) ...[
                    Icon(icon, size: 20),
                    const SizedBox(width: 8),
                  ],
                  Text(
                    text,
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
      ),
    );
  }
}
```

#### Button Variants

| Variant | Background | Text | Border | Use Case |
|---------|------------|------|--------|----------|
| Primary | `#FF8C42` | White | None | Main actions |
| Secondary | Transparent | `#FF8C42` | `#FF8C42` (1px) | Alternative actions |
| Tertiary | Transparent | `#757575` | None | Low-emphasis actions |
| Disabled | `#E0E0E0` | `#9E9E9E` | None | Inactive state |

### Input Fields

```dart
// Usage
AppTextField(
  label: 'Email',
  hint: 'Enter your email',
  prefixIcon: Icons.email_outlined,
  keyboardType: TextInputType.emailAddress,
  validator: (value) {
    if (value == null || value.isEmpty) {
      return 'Email is required';
    }
    if (!isValidEmail(value)) {
      return 'Enter a valid email';
    }
    return null;
  },
)

// Implementation
class AppTextField extends StatelessWidget {
  final String? label;
  final String? hint;
  final IconData? prefixIcon;
  final IconData? suffixIcon;
  final TextInputType? keyboardType;
  final bool obscureText;
  final String? Function(String?)? validator;
  final TextEditingController? controller;
  
  const AppTextField({
    this.label,
    this.hint,
    this.prefixIcon,
    this.suffixIcon,
    this.keyboardType,
    this.obscureText = false,
    this.validator,
    this.controller,
    Key? key,
  }) : super(key: key);
  
  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (label != null) ...[
          Text(
            label!,
            style: const TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.w500,
              color: AppColors.nearlyBlack,
            ),
          ),
          const SizedBox(height: AppSpacing.xs),
        ],
        TextFormField(
          controller: controller,
          keyboardType: keyboardType,
          obscureText: obscureText,
          validator: validator,
          decoration: InputDecoration(
            hintText: hint,
            prefixIcon: prefixIcon != null
                ? Icon(prefixIcon, size: 20)
                : null,
            suffixIcon: suffixIcon != null
                ? Icon(suffixIcon, size: 20)
                : null,
            filled: true,
            fillColor: AppColors.white,
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(
                color: AppColors.grey,
                width: 1,
              ),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(
                color: AppColors.grey,
                width: 1,
              ),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(
                color: AppColors.primaryOrange,
                width: 2,
              ),
            ),
            errorBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(
                color: AppColors.error,
                width: 1,
              ),
            ),
            focusedErrorBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(
                color: AppColors.error,
                width: 2,
              ),
            ),
            contentPadding: const EdgeInsets.symmetric(
              horizontal: 16,
              vertical: 16,
            ),
          ),
        ),
      ],
    );
  }
}
```

### Cards

```dart
// Usage
AppCard(
  child: Column(
    children: [
      AppCardHeader(
        title: 'Active Subscription',
        action: TextButton(
          onPressed: () {},
          child: const Text('Manage'),
        ),
      ),
      const SizedBox(height: AppSpacing.md),
      // Card content
    ],
  ),
)

// Implementation
class AppCard extends StatelessWidget {
  final Widget child;
  final EdgeInsetsGeometry? padding;
  final VoidCallback? onTap;
  
  const AppCard({
    required this.child,
    this.padding,
    this.onTap,
    Key? key,
  }) : super(key: key);
  
  @override
  Widget build(BuildContext context) {
    final card = Card(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      child: Padding(
        padding: padding ?? const EdgeInsets.all(AppSpacing.md),
        child: child,
      ),
    );
    
    return onTap != null
        ? InkWell(
            onTap: onTap,
            borderRadius: BorderRadius.circular(16),
            child: card,
          )
        : card;
  }
}
```

### Loading States

```dart
// Shimmer Loading for Cards
class ShimmerCard extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Shimmer.fromColors(
      baseColor: AppColors.lightGrey,
      highlightColor: AppColors.white,
      child: Container(
        decoration: BoxDecoration(
          color: AppColors.white,
          borderRadius: BorderRadius.circular(16),
        ),
        padding: const EdgeInsets.all(AppSpacing.md),
        child: Column(
          children: [
            Container(
              height: 120,
              decoration: BoxDecoration(
                color: AppColors.white,
                borderRadius: BorderRadius.circular(12),
              ),
            ),
            const SizedBox(height: AppSpacing.md),
            Container(
              height: 20,
              width: double.infinity,
              decoration: BoxDecoration(
                color: AppColors.white,
                borderRadius: BorderRadius.circular(4),
              ),
            ),
            const SizedBox(height: AppSpacing.sm),
            Container(
              height: 16,
              width: 100,
              decoration: BoxDecoration(
                color: AppColors.white,
                borderRadius: BorderRadius.circular(4),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// Loading Indicator
class AppLoadingIndicator extends StatelessWidget {
  final String? message;
  
  const AppLoadingIndicator({this.message});
  
  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const CircularProgressIndicator(
            valueColor: AlwaysStoppedAnimation<Color>(
              AppColors.primaryOrange,
            ),
          ),
          if (message != null) ...[
            const SizedBox(height: AppSpacing.md),
            Text(
              message!,
              style: const TextStyle(
                color: AppColors.darkGrey,
                fontSize: 14,
              ),
            ),
          ],
        ],
      ),
    );
  }
}
```

### Empty States

```dart
// Usage
AppEmptyState(
  icon: Icons.shopping_cart_outlined,
  title: 'Your cart is empty',
  message: 'Add some delicious juices to get started!',
  actionText: 'Browse Products',
  onAction: () {
    Navigator.pushNamed(context, '/products');
  },
)

// Implementation
class AppEmptyState extends StatelessWidget {
  final IconData icon;
  final String title;
  final String message;
  final String? actionText;
  final VoidCallback? onAction;
  
  const AppEmptyState({
    required this.icon,
    required this.title,
    required this.message,
    this.actionText,
    this.onAction,
    Key? key,
  }) : super(key: key);
  
  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(AppSpacing.xl),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              icon,
              size: 64,
              color: AppColors.grey,
            ),
            const SizedBox(height: AppSpacing.lg),
            Text(
              title,
              style: const TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.w600,
                color: AppColors.nearlyBlack,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: AppSpacing.sm),
            Text(
              message,
              style: const TextStyle(
                fontSize: 14,
                color: AppColors.darkGrey,
              ),
              textAlign: TextAlign.center,
            ),
            if (actionText != null && onAction != null) ...[
              const SizedBox(height: AppSpacing.lg),
              AppButton.primary(
                text: actionText!,
                onPressed: onAction,
                isFullWidth: false,
              ),
            ],
          ],
        ),
      ),
    );
  }
}
```

### Error States

```dart
// Usage
AppErrorState(
  title: 'Something went wrong',
  message: 'Unable to load products. Please try again.',
  actionText: 'Retry',
  onAction: () {
    // Retry logic
  },
)

// Implementation
class AppErrorState extends StatelessWidget {
  final String title;
  final String message;
  final String? actionText;
  final VoidCallback? onAction;
  
  const AppErrorState({
    required this.title,
    required this.message,
    this.actionText,
    this.onAction,
    Key? key,
  }) : super(key: key);
  
  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(AppSpacing.xl),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(
              Icons.error_outline,
              size: 64,
              color: AppColors.error,
            ),
            const SizedBox(height: AppSpacing.lg),
            Text(
              title,
              style: const TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.w600,
                color: AppColors.nearlyBlack,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: AppSpacing.sm),
            Text(
              message,
              style: const TextStyle(
                fontSize: 14,
                color: AppColors.darkGrey,
              ),
              textAlign: TextAlign.center,
            ),
            if (actionText != null && onAction != null) ...[
              const SizedBox(height: AppSpacing.lg),
              AppButton.primary(
                text: actionText!,
                onPressed: onAction,
                isFullWidth: false,
              ),
            ],
          ],
        ),
      ),
    );
  }
}
```

---

## Patterns

### Authentication Flow

```
Splash Screen
    ↓
Onboarding (first launch only)
    ↓
Authentication
├── Login
├── Sign Up
├── Google Sign-In
└── Phone OTP
    ↓
Dashboard (Main App)
```

### Navigation Pattern

**Bottom Navigation Bar (5 items max):**
1. Home
2. Products
3. Cart
4. Orders
5. Profile

**Implementation:**
```dart
class MainNavigation extends StatelessWidget {
  final int currentIndex;
  
  const MainNavigation({required this.currentIndex});
  
  @override
  Widget build(BuildContext context) {
    return NavigationBar(
      selectedIndex: currentIndex,
      destinations: const [
        NavigationDestination(
          icon: Icon(Icons.home_outlined),
          activeIcon: Icon(Icons.home),
          label: 'Home',
        ),
        NavigationDestination(
          icon: Icon(Icons.storefront_outlined),
          activeIcon: Icon(Icons.storefront),
          label: 'Products',
        ),
        NavigationDestination(
          icon: Icon(Icons.shopping_cart_outlined),
          activeIcon: Icon(Icons.shopping_cart),
          label: 'Cart',
          badge: '3', // When items in cart
        ),
        NavigationDestination(
          icon: Icon(Icons.receipt_long_outlined),
          activeIcon: Icon(Icons.receipt_long),
          label: 'Orders',
        ),
        NavigationDestination(
          icon: Icon(Icons.person_outline),
          activeIcon: Icon(Icons.person),
          label: 'Profile',
        ),
      ],
      onDestinationSelected: (index) {
        // Handle navigation
      },
    );
  }
}
```

---

## Accessibility

### WCAG 2.1 AA Compliance

**Color Contrast:**
- Normal text: 4.5:1 minimum
- Large text (18px+ or 14px+ bold): 3:1 minimum
- UI components: 3:1 minimum

**Touch Targets:**
- Minimum size: 48x48dp
- Spacing between targets: 8dp minimum

**Screen Reader Support:**
```dart
// Add semantics to custom widgets
Semantics(
  label: 'Add to cart button',
  hint: 'Double tap to add product to your cart',
  button: true,
  child: AppButton.primary(
    text: 'Add to Cart',
    onPressed: () {},
  ),
)

// For images
Image(
  image: AssetImage('assets/product.png'),
  semanticLabel: 'Fresh Orange Juice bottle',
)
```

**Dynamic Text Size:**
```dart
// Use MediaQuery for responsive text
final textScaler = MediaQuery.of(context).textScaler;

Text(
  'Welcome to BookMyJuice',
  style: TextStyle(
    fontSize: textScaler.scale(16),
  ),
)
```

---

## Resources

### Design Files
- Figma: [Link to design file]
- Adobe XD: [Link to design file]

### Code Repositories
- Frontend: `x:\BMJ\lush`
- Design System Package: `x:\BMJ\lush\lib\theme.dart`

### Tools
- Color Contrast Checker: [WebAIM](https://webaim.org/resources/contrastchecker/)
- Material Design Color Tool: [Material.io](https://material.io/design/color/)
- Flutter Widget Catalog: [Flutter.dev](https://flutter.dev/docs/development/ui/widgets)

### Contact
For design system questions or contributions:
- Slack: #bookmyjuice-design
- Email: design@bookmyjuice.co.in

---

## Glassmorphism Design (v2.0)

> Implemented April 2026 — a premium glassmorphism design layer on top of the core design system, applied to the Dashboard, Menu, Orders, and Profile screens.

### Glassmorphism Principles

- **Frosted Glass Surfaces:** Semi-transparent backgrounds with backdrop blur (`BackdropFilter` + `ImageFilter.blur`) create depth.
- **Subtle Borders:** 0.5px borders with `Colors.white.withOpacity(0.15)` for dark, `Colors.black.withOpacity(0.06)` for light.
- **Gradient Accents:** Product cards use startColor/endColor gradients. Subscription plans and CTAs use brand gradient buttons.
- **Glow Effects:** Selected/premium elements get `BoxShadow` with colored glow for emphasis.

### Glassmorphism Token Reference

All tokens defined in `lib/theme/app_colors.dart` and `lib/theme/app_radius.dart`.

#### Dark Theme Glass Tokens

| Token | Hex/Value | Usage |
|-------|-----------|-------|
| `glassBg` | `#0A0F0D` | Background fill |
| `glassSurface` | `#FFFFFF` with 6% opacity | Card/surface background |
| `glassElevated` | `#FFFFFF` with 10% opacity | Elevated surfaces (bottom sheets) |
| `glassBorder` | `#FFFFFF` with 15% opacity | Card borders |
| `glassBorderSubtle` | `#FFFFFF` with 6% opacity | Subtle dividers |
| `glassText` | `#F1F1F1` | Primary text on glass |
| `glassTextDim` | `#A0A0A0` | Secondary/tertiary text |
| `glassAccent` | `#22C55E` (neon green) | Accent highlights, prices, active states |
| `glassGlow` | `#22C55E` with 20% opacity | Drop shadow glow |
| `glassOrange` | `#FF8C42` | Theme toggle icon accent |

#### Light Theme Glass Tokens

| Token | Hex/Value | Usage |
|-------|-----------|-------|
| `glassBgLight` | `#F8FAF9` | Background fill |
| `glassSurfaceLight` | `#FFFFFF` with 70% opacity | Card/surface background |
| `glassElevatedLight` | `#FFFFFF` with 90% opacity | Elevated surfaces |
| `glassBorderLight` | `#000000` with 8% opacity | Card borders |
| `glassTextPrimary` | `#1A1A1A` | Primary text |
| `lightTextPrimary` | `#1A1A1A` | Primary text (light theme) |
| `lightTextSecondary` | `#666666` | Secondary text |

#### Radius Tokens (`lib/theme/app_radius.dart`)

| Token | Value | Usage |
|-------|-------|-------|
| `sm` | 8.0 | Small chips, small tags |
| `md` | 12.0 | Buttons, input fields, small cards |
| `lg` | 16.0 | Cards, search bar, segment toggles |
| `xl` | 24.0 | GlassCards, bottom sheets, major containers |
| `xxl` | 32.0 | Hero sections, large containers |
| `circular` | 48.0 | Circular avatars, icon backgrounds |

### Typography for Glassmorphism

| Font | Weight | Usage |
|------|--------|-------|
| `Poppins` | 600 (SemiBold) | Headlines, card titles, prices, plan names |
| `Poppins` | 700 (Bold) | Prices, emphasis |
| `Inter` | 400 (Regular) | Body text, descriptions, secondary info |
| `Inter` | 500 (Medium) | Button labels, list items |
| `Inter` | 600 (SemiBold) | Category tags, active state labels |

### Glassmorphism Component Library

#### `GlassCard` (`lib/widgets/glass_card.dart`)

Universal glass container. Configurable blur, opacity, border, glow, gradient, and onTap.

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

#### `GlassChip`

Glassmorphism chip/tag for categories and filters.

```dart
GlassChip(
  label: 'Orange',
  isSelected: true,
  selectedColor: AppColors.glassAccent,
  onTap: () => _filterByCategory('Orange'),
)
```

#### `GlassSegmentToggle`

Glassmorphism toggle for One-Time / Subscribe segment control.

```dart
GlassSegmentToggle(
  segments: const ['One-Time', 'Subscribe'],
  selectedIndex: _segmentIndex,
  onSegmentChanged: (index) => setState(() => _segmentIndex = index),
)
```

#### `CartBadgeIcon` (`lib/widgets/cart_badge_icon.dart`)

Shopping bag icon with neon green badge count. Uses `BlocBuilder<CartBloc>` to compute total quantity.

```dart
CartBadgeIcon(
  iconSize: 20,
  onTap: () => Navigator.pushNamed(context, '/cart'),
)
```

### Dashboard Shell Architecture

The Dashboard now uses an `IndexedStack` with 4 tabs and a glassmorphism bottom nav:

| Tab | File | Description |
|-----|------|-------------|
| Home | `home_tab.dart` | Hero greeting, subscription card, stats strip, order today |
| Menu | `menu_tab.dart` | One-Time catalog + Subscribe plans with segment toggle |
| Orders | `orders_tab.dart` | Order history with glass tiles; sign-in CTA if unauthenticated |
| Profile | `profile_tab.dart` | Profile header, menu items, theme toggle, logout |

Glass bottom navigation uses `BackdropFilter` with `ClipRRect` and `NavigationBar`.

### Theme Support

Both light and dark themes fully support glassmorphism. The `ThemeCubit` provides `resolvedThemeMode` to determine which glass token set to use. All glass widgets auto-adapt by calling `context.watch<ThemeCubit>()`.

---

*Last Updated: May 29, 2026*
*Version: 2.0.0*
