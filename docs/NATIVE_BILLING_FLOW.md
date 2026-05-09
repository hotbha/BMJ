# Native Billing Flow — BookMyJuice

**Document Version:** 1.0  
**Last Updated:** 2026-05-08

---

## Overview

This document defines the boundary between native BMJ screens and Chargebee-hosted surfaces in the billing/purchase flow. The guiding principle is:

> **All plan discovery and review is native. Only final payment completion is Chargebee hosted checkout.**

---

## What Remains Native (BMJ Flutter Screens)

| Screen | Purpose | Data Source |
|--------|---------|-------------|
| Plan Catalog | Browse available subscription plans | Local MySQL/Redis cache (synced via webhook) |
| Plan Detail | View plan features, pricing, comparison | Local cache |
| Plan Comparison | Side-by-side plan comparison | Local cache |
| One-Time Product Detail | Browse individual juice products | Local cache |
| Cart / Review | View selected items, modify quantities | Local state + API |
| Address Selection | Choose delivery address | BMJ delivery API |
| Delivery Slot Picker | Select delivery time slot | BMJ delivery API |
| Pre-Checkout Review | Final validation before payment | BMJ billing API |
| Subscription Management | View/manage active subscriptions | Local cache + Chargebee API (server-side) |
| Billing Summary | Invoice/payment history | Local cache |
| Order History | Past orders | Local cache |

## What Remains Chargebee Hosted

| Surface | Purpose | When Used |
|---------|---------|-----------|
| Hosted Checkout | Secure payment completion, 3D Secure, card storage | Final step after native review |

## What is Removed (No Longer Used)

| Surface | Why Removed | Replacement |
|---------|-------------|-------------|
| Pricing Table (Chargebee Hosted) | Fragmented UX, inconsistent branding | Native plan catalog screen |
| Pricing Page Sessions (Chargebee) | No longer needed for plan discovery | Native plan detail + comparison |
| Hosted Plan Selection Pages | Slower, limits customization | Native cart/review flow |
| Customer Portal (Chargebee) | Limited brand control | Native subscription management |
| Plan Detail Hosted Pages | Removes user from app context | Native plan detail screen |

---

## Exact Checkout Handoff Boundary

### Sequence: Subscription Purchase

```
┌──────────┐        ┌──────────┐        ┌──────────┐        ┌──────────┐
│ Flutter  │        │bmjServer │        │  MySQL   │        │Chargebee │
│  (Native)│        │          │        │ (Cache)  │        │          │
└────┬─────┘        └────┬─────┘        └────┬─────┘        └────┬─────┘
     │                   │                   │                   │
     │ 1. GET /api/plans │                   │                   │
     │──────────────────►│                   │                   │
     │                   │ 2. SELECT * FROM  │                   │
     │                   │    plans          │                   │
     │                   │──────────────────►│                   │
     │                   │◄──────────────────│                   │
     │◄──────────────────│                   │                   │
     │                   │                   │                   │
     │ 3. User browses, selects plan         │                   │
     │    (all native screens)               │                   │
     │                   │                   │                   │
     │ 4. POST /api/billing/checkout/review  │                   │
     │──────────────────►│                   │                   │
     │                   │ 5. Validate cart  │                   │
     │                   │    Check pricing  │                   │
     │                   │    Verify delivery│                   │
     │◄──────────────────│                   │                   │
     │                   │                   │                   │
     │ 6. POST /api/billing/checkout/start   │                   │
     │──────────────────►│                   │                   │
     │                   │ 7. HostedPage     │                   │
     │                   │    .checkoutNew() │                   │
     │                   │──────────────────────────────────────►│
     │                   │◄──────────────────────────────────────│
     │◄─── { url } ─────│                   │                   │
     │                   │                   │                   │
     │ 8. Open WebView   │                   │                   │
     │    (Hosted Checkout)                  │                   │
     │──────────────────────────────────────────────────────────►│
     │                   │                   │                   │
     │ 9. User completes payment on Chargebee                   │
     │◄──────────────────────────────────────────────────────────│
     │                   │                   │                   │
     │                   │ 10. Webhook:      │                   │
     │                   │     subscription  │                   │
     │                   │     .created      │                   │
     │                   │◄──────────────────────────────────────│
     │                   │                   │                   │
     │                   │ 11. INSERT INTO   │                   │
     │                   │     subscriptions │                   │
     │                   │──────────────────►│                   │
     │                   │                   │                   │
     │ 12. Refresh UI    │                   │                   │
     │◄─── success ─────│                   │                   │
```

### Why Hosted Checkout is Retained

1. **PCI DSS Compliance**: Chargebee handles payment card data, 3D Secure, and card storage. Processing credit card data requires significant compliance overhead.
2. **Gateway Integration**: Chargebee manages connections to Razorpay, Stripe, and other payment gateways.
3. **SCA/Regulatory**: Strong Customer Authentication (PSD2, RBI guidelines) handled by Chargebee.
4. **Fraud Management**: Chargebee provides built-in fraud detection tools.
5. **No Reimplementation**: Building an alternative payment flow would duplicate infrastructure that Chargebee already provides.

### Why Pricing Tables/Pages are Removed

1. **User Experience**: Navigating between a native app and web-hosted pricing creates friction.
2. **Brand Consistency**: Native screens provide full control over look and feel.
3. **Performance**: Native rendering is faster than loading a Chargebee-hosted page.
4. **Offline Support**: Plan data can be cached locally for offline browsing.
5. **Comparison UX**: Side-by-side plan comparison is not feasible in hosted pricing tables.
6. **Delivery Integration**: Native screens can embed delivery slot selection, which cannot be done in hosted pricing pages.

---

## Webhook Reconciliation

After a user completes payment on hosted checkout:

1. Chargebee sends a webhook event (e.g., `subscription.created`, `invoice.paid`, `payment.succeeded`).
2. bmjServer's webhook handler processes the event with idempotency.
3. The local database is updated to reflect the new state.
4. Cache is evicted for affected entities (subscriptions, invoices).
5. On next app load or refresh, the Flutter app fetches updated data from bmjServer.
6. The user sees their active subscription/order in the native UI.

### Handling Delays

- The hosted checkout WebView may close before webhook processing completes.
- Flutter should poll or the user should be able to pull-to-refresh after checkout.
- Maximum expected delay: 2-5 seconds under normal conditions.

---

## Idempotency and Retry

- All checkout creation endpoints are idempotent.
- If a user returns to the review screen after a failed payment, they can retry without duplicate charges.
- Chargebee's hosted checkout generates a unique session per checkout attempt.
- Webhook processing uses Chargebee event IDs for deduplication.

---

## Compliance Notes

- Payment card data never touches BMJ servers.
- BMJ does not store PAN, CVV, or expiry dates.
- BMJ stores only reference identifiers (Chargebee customer ID, subscription ID, invoice ID).
- Right-to-erasure requests must leave billing records intact in Chargebee but anonymize PII in BMJ's local database.
- Consent records are stored in BMJ's audit tables for billing-related data processing.

---

## API Endpoints Summary

| Method | Endpoint | Purpose | Native/Hosted |
|--------|----------|---------|---------------|
| GET | `/api/products` | Product catalog | Native |
| GET | `/api/plans` | Subscription plans | Native |
| GET | `/api/plans/{id}` | Plan details | Native |
| POST | `/api/billing/checkout/review` | Pre-checkout validation | Native |
| POST | `/api/billing/checkout/start` | Start checkout, get hosted URL | Backend → Hosted |
| GET | `/api/billing/subscriptions/me` | User's subscriptions | Native |
| POST | `/api/billing/subscriptions/change-plan` | Change plan | Native |
| POST | `/api/billing/subscriptions/cancel` | Cancel subscription | Native |
| GET | `/api/billing/orders/me` | Order history | Native |
| GET | `/api/billing/invoices/me` | Invoice history | Native |

---

**Document Maintained By:** Engineering Team  
**Last Review:** 2026-05-08  
**Next Review:** 2026-06-08
