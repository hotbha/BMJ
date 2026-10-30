---
name: Vibrant Zest Architecture
colors:
  surface: '#1c110b'
  surface-dim: '#1c110b'
  surface-bright: '#45362f'
  surface-container-lowest: '#160c06'
  surface-container-low: '#251913'
  surface-container: '#291d16'
  surface-container-high: '#352720'
  surface-container-highest: '#40322a'
  on-surface: '#f6ded3'
  on-surface-variant: '#e0c0b1'
  inverse-surface: '#f6ded3'
  inverse-on-surface: '#3c2d26'
  outline: '#a78b7d'
  outline-variant: '#584237'
  surface-tint: '#ffb690'
  primary: '#ffb690'
  on-primary: '#552100'
  primary-container: '#f97316'
  on-primary-container: '#582200'
  inverse-primary: '#9d4300'
  secondary: '#4ae176'
  on-secondary: '#003915'
  secondary-container: '#00b954'
  on-secondary-container: '#004119'
  tertiary: '#5dd9d0'
  on-tertiary: '#003734'
  tertiary-container: '#1caca3'
  on-tertiary-container: '#003936'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#ffdbca'
  primary-fixed-dim: '#ffb690'
  on-primary-fixed: '#341100'
  on-primary-fixed-variant: '#783200'
  secondary-fixed: '#6bff8f'
  secondary-fixed-dim: '#4ae176'
  on-secondary-fixed: '#002109'
  on-secondary-fixed-variant: '#005321'
  tertiary-fixed: '#7cf6ec'
  tertiary-fixed-dim: '#5dd9d0'
  on-tertiary-fixed: '#00201e'
  on-tertiary-fixed-variant: '#00504b'
  background: '#1c110b'
  on-background: '#f6ded3'
  surface-variant: '#40322a'
  surface-deep: '#0f1412'
  on-surface-bright: '#dfe4e0'
  zest-glow: rgba(249, 115, 22, 0.45)
  neon-lime: '#4be277'
typography:
  display-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 32px
    fontWeight: '800'
    lineHeight: 40px
    letterSpacing: -0.02em
  display-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 28px
    fontWeight: '800'
    lineHeight: 34px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 22px
    fontWeight: '700'
    lineHeight: 28px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 20px
    fontWeight: '700'
    lineHeight: 26px
    letterSpacing: 0em
  title-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 24px
    letterSpacing: 0.01em
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
    letterSpacing: 0.02em
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
    letterSpacing: 0.01em
  label-lg:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '700'
    lineHeight: 20px
    letterSpacing: 0.01em
  label-sm:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '700'
    lineHeight: 14px
    letterSpacing: 0.05em
  stat-num:
    fontFamily: Plus Jakarta Sans
    fontSize: 22px
    fontWeight: '800'
    lineHeight: 26px
    letterSpacing: -0.02em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 4px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
  margin-mobile: 16px
  margin-desktop: 32px
  gutter: 12px
  max-width-container: 430px
---

## Brand & Style

The design system evolves from a botanical aesthetic to a high-energy, performance-driven wellness platform. By shifting the primary focus to **Orange 500 (#f97316)**, the brand moves from "quietly organic" to "actively vitalizing." It targets health-conscious professionals who value efficiency and high-grade nutrition.

The visual style is **High-Contrast Glassmorphism**. This style maintains the premium depth of translucent, frosted layers while introducing a bold, industrial energy. The brand personality is authoritative, energetic, and precise. The "Book My Juice" identity (featuring the orange/citrus leaf motif) is the core anchor, dictating a design language that balances deep dark-mode surfaces with aggressive, high-visibility citrus accents. The emotional response is one of immediate "refreshment," "zest," and "tangible quality."

## Colors

The palette is anchored by a high-contrast relationship between deep botanical neutrals and vibrant citrus primaries.

- **Primary (Citrus Orange):** Used for critical conversion points, brand-level identity, and active selection glows. It provides the highest contrast against the dark background.
- **Secondary (Vibrant Green):** Representing the produce itself, used for health-specific indicators and secondary action buttons.
- **Tertiary (Mint Teal):** Used for informational badges and subtle cooling highlights.
- **Neutral (Vegetal Slate):** A deep, green-tinted charcoal that provides a more sophisticated, organic base than pure black.

The system is optimized for **Dark Mode** to allow the orange primary and glass effects to pop with maximum luminosity.

## Typography

This system uses **Plus Jakarta Sans** for headlines to provide a modern, slightly rounded, and welcoming feel that complements the "Book My Juice" logo. **Inter** is used for body text to maintain technical clarity and readability in data-rich layouts.

**Typography Guidelines:**
- **Emphasis:** High-priority headlines should use the Orange 500 primary color for branding impact.
- **Data:** Use the `stat-num` role for nutritional values and pricing.
- **Mobile Scaling:** For mobile devices, `display-lg` should be downscaled to 24px/30px to maintain content density.

## Layout & Spacing

The layout utilizes a **Fluid Grid** model with a specific focus on high-density mobile presentation.

- **Containerization:** All primary content is constrained to a 430px max-width on larger viewports to maintain a "mobile-first" experience even on desktop.
- **Rhythm:** A 4px base unit ensures mathematical consistency across all paddings and margins.
- **Grid Structure:** Product listings use a 2-column grid with a 12px gutter. Detail views use a single-stack model with a 16px side margin.
- **Touch Areas:** All buttons and interactive icons must maintain a 48x48px minimum footprint.

## Elevation & Depth

Visual hierarchy is established through **Tonal Layering and Glassmorphism** rather than traditional black shadows.

- **Layering:** Hierarchy is built through background blur (16px to 24px) and increasing container opacity.
- **The Orange Glow:** Primary interactive elements utilize an Orange 500 ambient aura (`rgba(249, 115, 22, 0.45)`) to signal "active" or "selectable" states.
- **Borders:** Containers use a 1px "Hairline Glass" border with 10% white opacity to provide definition against the deep vegetal background.
- **Scrims:** Bottom sheets use a 40% opacity black scrim with a 4px background blur to isolate the focused task.

## Shapes

The shape language reflects the rounded, organic nature of juice bottles and fresh fruit.

- **Inputs & Chips:** Use 0.5rem (8px) for a soft but functional feel.
- **Cards & Sheets:** Use 1rem (16px) for major containers and 1.5rem (24px) for bottom sheets to create a friendly, approachable aesthetic.
- **Pills:** Navigation indicators and specialized labels use full-round pill shapes to distinguish them from structural content.

## Components

### Buttons
- **Primary Action:** Solid Orange 500 background with white text and an orange ambient glow.
- **Secondary Action:** Frosted glass fill with a 1px Orange 500 border.

### Cards
- **Product Card:** Features a large image container with a "Glass Overlay" bottom section for titles and pricing. The "Add to Cart" action is an orange circular floating action button within the card.
- **Status Cards:** Use colored glass tints (Green for "In Transit," Orange for "Action Required").

### Input Fields
- **Search & Text:** Deep charcoal backgrounds (#1c211e) with a 1px border that turns Orange 500 on focus.

### Navigation
- **Floating Glass Bar:** A bottom-docked pill-shaped bar with a 24px backdrop blur. The active state is indicated by an orange dot and an orange glow behind the icon.

### Selection Controls
- **Checkboxes/Radios:** Use Orange 500 for the active state to ensure high visibility against the dark mode surfaces.