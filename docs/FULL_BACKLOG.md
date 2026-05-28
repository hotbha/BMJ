# Full Implementation Backlog

> **Date:** 2026-05-28
> **All items must ship.** No Phase 2.

## Status Key
- 🔴 Not started
- 🟡 In progress
- 🟢 Complete
- 🔵 Blocked (reason noted)

## GROUP A — Address Screen (launch blocker)

| ID | Item | Status | Effort |
|----|------|--------|--------|
| A1 | Full address entry screen | 🟡 Implementing | 1h |
| A2 | Pincode serviceability check | 🟡 Implementing | 30m |
| A3 | Address pre-fill from saved profile | 🟡 Implementing | 15m |

## GROUP B — BLoC Stubs

| ID | Item | Status | Effort |
|----|------|--------|--------|
| B2 | ProductsBloc — wire all 6 handlers to real service | 🔴 | 2h |
| B3 | ProductCatalogBloc — fix camelCase keys | 🔴 | 30m |
| B4 | AuthBloc — remove remaining double-emit patterns | 🔴 | 30m |
| B5 | UserBloc — UpdateUserProfile + RefreshUserProfile | 🔴 | 1h |

## GROUP C — Push Notifications (FCM)

| ID | Item | Status | Effort |
|----|------|--------|--------|
| C1 | Firebase FCM config (google-services.json) | 🔴 | 1h |
| C2 | Order placed / renewal / delivery / bottle notifications | 🔴 | 2h |
| C3 | In-app notification centre screen | 🔴 | 1.5h |
| C4 | Notification badge on dashboard AppBar | 🔴 | 30m |

## GROUP D — Subscription Management

| ID | Item | Status | Effort |
|----|------|--------|--------|
| D1 | Active subscription detail screen | 🔴 | 1h |
| D2 | Pause subscription screen | 🔴 | 1h |
| D3 | Resume subscription screen | 🔴 | 30m |
| D4 | Cancel subscription screen | 🔴 | 1h |
| D5 | Modify schedule screen (reuse S1 Screen 3 widget) | 🔴 | 1h |

## GROUP E — Order History

| ID | Item | Status | Effort |
|----|------|--------|--------|
| E1 | Order history list screen | 🔴 | 1h |
| E2 | Order detail screen | 🔴 | 1h |
| E3 | Reorder button on order detail | 🔴 | 30m |

## GROUP F — Referral System

| ID | Item | Status | Effort |
|----|------|--------|--------|
| F1 | Referral code generation (backend) | 🔴 | 1h |
| F2 | Referral screen (share + count) | 🔴 | 1h |
| F3 | Referral field during signup | 🔴 | 30m |

## GROUP G — Analytics

| ID | Item | Status | Effort |
|----|------|--------|--------|
| G1 | Firebase Analytics setup | 🔴 | 30m |
| G2 | Track key events (subscription, order, referral) | 🔴 | 1h |
| G3 | Analytics wrapper class | 🔴 | 30m |

## GROUP H — Multi-city Support

| ID | Item | Status | Effort |
|----|------|--------|--------|
| H1 | City selection screen on first launch | 🔴 | 1h |
| H2 | Serviceable cities list | 🔴 | 30m |
| H3 | City-filtered catalog | 🔴 | 30m |

## GROUP I — B2B / Office Subscriptions

| ID | Item | Status | Effort |
|----|------|--------|--------|
| I1 | Business account flag | 🔴 | 30m |
| I2 | Bulk subscription screen | 🔴 | 2h |
| I3 | GST invoice generation | 🔴 | 1h |

## GROUP J — Loyalty Points

| ID | Item | Status | Effort |
|----|------|--------|--------|
| J1 | Points model + display | 🔴 | 1h |
| J2 | Earn points on orders (backend hook) | 🔴 | 1h |
| J3 | Redeem points at checkout | 🔴 | 1h |

## Estimated Implementation Order

1. **A** (address) — launch blocker → **NOW**
2. **B** (BLoC stubs) — data integrity
3. **C** (notifications) — user engagement
4. **D** (subscription management) — retention
5. **E** (order history) — UX completeness
6. **F** (referral) — growth
7. **G** (analytics) — observability
8. **H** (multi-city) — scale
9. **I** (B2B) — revenue expansion
10. **J** (loyalty) — retention