# Subscription Screen Flow Specification

> **Date:** 2026-05-28
> **Catalog structure:** Item (family + size or family + juice + size) + Item Prices (weekly + monthly)

## Screen 1 — Family Selection

3 cards: Delight, Signature, Premium
- Each card: emoji, name, tagline, description
- Source: metadata from items of that family
- Tap → Screen 2 filtered to that family

## Screen 2 — Plan Selection

### Section A: "Choose a Plan" (generic items for selected family)
- 3 cards — one per size: 200ml | 300ml | 500ml
- Each card shows BOTH prices:
  - Weekly: ₹[price] (6 bottles)
  - Monthly: ₹[price] (24 bottles)
- Duration toggle on card: Weekly | Monthly
- Tap card → Screen 3 (day-wise, all days empty)
- Carries: selected itemId + selected itemPriceId

### Section B: "Start with a Favourite"
- Grid of 5 juice cards for this family
- Each juice card: name, weekly price for 200ml
- Tap juice → size selector (200ml | 300ml | 500ml)
  - Each size option shows weekly + monthly price
  - Customer picks size + duration
- → Screen 3 (day-wise, all days pre-filled)
- Carries: selected itemId + selected itemPriceId

## Screen 3 — Day-wise Juice Selection

- Header: shows selected plan name + size + price
- Checkbox top: "Same Everyday" (default: ON)
  - ON → changing one day updates all 6 days
  - OFF → each day independent
- 6 rows: Mon | Tue | Wed | Thu | Fri | Sat (Sunday excluded)
- Each row: day label + juice dropdown
- Dropdown: juices of selected family only

For juice_specific entry:
- All 6 rows pre-filled with default_juice
- "Same Everyday" checked ON

For generic entry:
- All 6 rows empty
- "Same Everyday" checked ON
- All 6 rows must be filled to enable CTA

CTA: "Review Order" (disabled until all days filled)
→ Screen 4

## Screen 4 — Summary + Checkout

- Plan: [Family] [Size] [Weekly/Monthly]
- Price: ₹[amount] per [week/month]
- Schedule: Mon–Sat with juice names
- Delivery address (from profile)
- CTA: "Start Subscription" → Chargebee checkout
- Carries: itemPriceId + day-wise juice metadata

## Data Model — SubscriptionSelection

```dart
class SubscriptionSelection {
  final String itemId;
  final String itemPriceId;  // weekly or monthly price
  final String family;
  final String size;
  final String period;       // 'weekly' | 'monthly'
  final int priceInPaise;
  final Map<String, String> daySchedule;
  final String? defaultJuice;

  Map<String, dynamic> toChargebeeMetadata() => {
    'item_id': itemId,
    'item_price_id': itemPriceId,
    'period': period,
    'day_schedule': daySchedule,
    'default_juice': defaultJuice,
  };
}