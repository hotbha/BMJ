---
name: Lush Architecture
colors:
  surface: '#181209'
  surface-dim: '#181209'
  surface-bright: '#40382d'
  surface-container-lowest: '#130d05'
  surface-container-low: '#211b11'
  surface-container: '#251f15'
  surface-container-high: '#30291f'
  surface-container-highest: '#3b3429'
  on-surface: '#eee0d1'
  on-surface-variant: '#d6c4ad'
  inverse-surface: '#eee0d1'
  inverse-on-surface: '#372f25'
  outline: '#9e8e79'
  outline-variant: '#514533'
  surface-tint: '#ffba40'
  primary: '#ffbc49'
  on-primary: '#432c00'
  primary-container: '#e69f01'
  on-primary-container: '#593b00'
  inverse-primary: '#7f5600'
  secondary: '#e9c082'
  on-secondary: '#432c00'
  secondary-container: '#5e420f'
  on-secondary-container: '#d7af73'
  tertiary: '#93ceff'
  on-tertiary: '#003450'
  tertiary-container: '#43b5ff'
  on-tertiary-container: '#004468'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#ffddae'
  primary-fixed-dim: '#ffba40'
  on-primary-fixed: '#281800'
  on-primary-fixed-variant: '#604000'
  secondary-fixed: '#ffddaf'
  secondary-fixed-dim: '#e9c082'
  on-secondary-fixed: '#281800'
  on-secondary-fixed-variant: '#5e420f'
  tertiary-fixed: '#cbe6ff'
  tertiary-fixed-dim: '#90cdff'
  on-tertiary-fixed: '#001e30'
  on-tertiary-fixed-variant: '#004b71'
  background: '#181209'
  on-background: '#eee0d1'
  surface-variant: '#3b3429'
typography:
  display-lg:
    fontFamily: Poppins
    fontSize: 32px
    fontWeight: '800'
    lineHeight: 40px
    letterSpacing: -0.02em
  display-md:
    fontFamily: Poppins
    fontSize: 28px
    fontWeight: '800'
    lineHeight: 34px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Poppins
    fontSize: 22px
    fontWeight: '700'
    lineHeight: 28px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Poppins
    fontSize: 20px
    fontWeight: '700'
    lineHeight: 26px
    letterSpacing: 0em
  title-lg:
    fontFamily: Poppins
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 24px
    letterSpacing: 0.01em
  title-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '600'
    lineHeight: 22px
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
  body-sm:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
    letterSpacing: 0em
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
    fontFamily: Poppins
    fontSize: 22px
    fontWeight: '900'
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
---

## Brand & Style

The design system embodies **"The Architecture of Scalable Wellness,"** translating the vitality of organic, cold-pressed produce into a high-performance digital environment. The brand personality is professional yet vibrant, striking a balance between botanical indulgence and clinical reliability.

The visual style is **Organic Glassmorphism**. It utilizes deep earthy backgrounds, translucent frosted overlays, and hairline borders to emulate droplets on glass bottles. The interface feels alive and pristine, using light transmission and colored glows to establish hierarchy. The emotional response should be one of "freshness," "precision," and "health-focused optimism."

## Colors

The palette is derived from the lifecycle of botanical growth—shifting from rich soil toward a golden, sun-ripened harvest.

- **Primary (Golden Nectar):** Used for interactive glows, active states, and high-priority CTA gradients. It provides a warm, high-energy contrast to the dark environment.
- **Secondary (Earthbound Bronze):** A muted, grounded tone used for structural elements, shadows, and low-priority containers.
- **Tertiary (Hydration Blue):** Applied to secondary highlights, icons, and refreshing accents, reinforcing the essential hydration roots of the system.
- **Neutral (Warm Pebble):** The foundational canvas. It replaces standard pure blacks with a high-clarity warm taupe for surface-level typography and contrast.

The system defaults to a **Dark Glass** mode for its premium feel, optimized for depth and luminosity.

## Typography

The system utilizes a dual-font strategy. **Poppins** provides an expressive, approachable lifestyle feel for headings, while **Inter** ensures high-density transactional data remains legible.

**Usage Rules:**
- **Tabular Numerals:** Always use tabular figures for pricing and countdowns to prevent layout jitter during BLoC state updates.
- **Hierarchy:** Prefer color shifts (e.g., using Neutral `#807669` variants) over radical size changes to maintain touch-friendly readability.
- **Scale:** On mobile screens, `display-lg` should be limited to hero greetings to ensure content density.

## Layout & Spacing

The layout follows a **Fluid Grid** model with a hard max-width of **430px** for the primary content container, ensuring a consistent experience across mobile and web.

**Key Principles:**
- **Rhythm:** A 4px base unit governs all dimensions.
- **Grid:** Use a 2-column grid for product catalogs with a 12px gap.
- **Safe Areas:** Adhere strictly to device safe-area insets. On web viewports, the content should center with an ambient radial gradient bleeding into the margins.
- **Touch Targets:** All interactive elements must maintain a minimum 48x48dp hit area.

## Elevation & Depth

This design system eschews traditional heavy drop shadows in favor of **Luminous Depth**. 

- **Layering:** Hierarchy is established through increasing opacity of glass fills and backdrop blurs (10px to 20px).
- **Glows:** Primary actions utilize a warm golden "aura" (`rgba(231, 160, 3, 0.35)`) instead of black shadows.
- **Borders:** Hairline translucent borders (0.5px to 1px) provide structural definition without adding visual bulk. 
- **Ambient Background:** The base layer features dual radial glows to provide a sense of environmental light behind the glass containers.

## Shapes

The shape language is **Soft and Organic**. 

- **Standard Radius:** 0.5rem (8px) for inputs and small chips.
- **Container Radius:** 1rem to 1.5rem (16px-24px) for cards and bottom sheets to reflect the rounded nature of cold-pressed bottles.
- **Pill Shapes:** Used exclusively for navigation toggles and loyalty streak indicators to differentiate them from functional product cards.

## Components

### Buttons
- **Primary:** High-contrast gradient (Golden Nectar to Bronze) with an 800-weight label and a warm drop glow.
- **Secondary:** Ghost style with a 1px translucent border and a subtle glass fill on interaction.

### Cards
- **GlassCard:** 16px blur with a 0.5px border. Subscription cards use tiered elevations and internal selector chips for volume (200ml, 300ml, 500ml).
- **Product Card:** Features a vibrant gradient header (radial) for product categories, with an immediate "Add +" action pill.

### State-Driven Elements
- **Inventory Chips:** Soft golden glows when selected to reflect active BLoC states.
- **Status Badges:** Use "Hydration Blue" for delivered, "Golden Nectar" for reminders, and a warm coral for out-of-stock.
- **Shimmer Skeletons:** Must match card radii exactly to prevent layout shift during data fetching.

### Navigation
- **Floating Glass Nav:** A docked pill-shaped container with 16px blur. Active icons feature an illuminated golden background pill and icon drop glow.