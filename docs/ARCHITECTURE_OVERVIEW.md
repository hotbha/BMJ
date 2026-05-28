# BookMyJuice Architecture Overview

> **Version:** 3.0 (Enterprise)  
> **Last Updated:** 2026-05-26  
> **Status:** ✅ Active — authoritative source

## Architecture Principles

1. **Chargebee is the single source of truth** for subscriptions, invoices, payments, orders, plans, and billing customer records.
2. **bmjServer orchestrates Chargebee APIs server-side only** — no secret keys exposed to Flutter.
3. **Hosted checkout retained only for final payment completion** — all other hosted pages (pricing, plan selection) removed and replaced with native Flutter screens.
4. **BMJ owns the delivery domain** (serviceability, addresses, delivery slots).
5. **Local persistence of Chargebee-owned data is read/cache/sync/audit only** — never an alternative source of truth.
6. **Redis caching for high-read data** with graceful degradation.
7. **Webhook processing is idempotent and reliable** with DLQ support.
8. **.env file is the single source for all secrets and credentials** — never committed to git.

## Secrets Management

All secrets, credentials, API keys, and passwords are managed through a single `.env` file at the project root.

### .env Variables

| Variable | Description | Source |
|----------|-------------|--------|
| `DB_USERNAME` | MySQL database user | `.env` |
| `DB_PASSWORD` | MySQL database password | `.env` |
| `DB_HOSTNAME` | MySQL host | `.env` |
| `DB_PORT` | MySQL port | `.env` |
| `DB_NAME` | MySQL database name | `.env` |
| `ADMIN_USER` | Spring admin username | `.env` |
| `ADMIN_PASSWORD` | Spring admin password | `.env` |
| `CHARGEBEE_SITE` | Chargebee site name | `.env` |
| `CHARGEBEE_API_KEY` | Chargebee API key | `.env` |
| `JWT_SECRET` | JWT signing secret | `.env` |
| `WEBHOOK_USERNAME` | Webhook basic auth username | `.env` |
| `WEBHOOK_PASSWORD` | Webhook basic auth password | `.env` |
| `MAIL_HOST` | SMTP host | `.env` |
| `MAIL_PORT` | SMTP port | `.env` |
| `MAIL_USERNAME` | SMTP username | `.env` |
| `MAIL_PASSWORD` | SMTP password | `.env` |
| `MAIL_FROM` | Mail from address | `.env` |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | `.env` |

### CI/CD Secrets

In GitHub Actions, each secret is configured as a repository secret (`secrets.X`). The CI pipelines reference them directly without a `.env` file.

### Flutter Build-Time Variables

Flutter uses `--dart-define` for build-time configuration:
- `API_BASE_URL` — Backend API base URL

## System Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────┐
│   Flutter   │────▶│   bmjServer     │────▶│  Chargebee  │
│   (Native)  │     │  (Spring Boot)  │     │   (SOT)     │
└─────────────┘     └──────────────────┘     └─────────────┘
       │                    │                       │
       │                    ├──▶ Redis (Cache)      │
       │                    ├──▶ MySQL (Local)      │
       │                    ├──▶ Webhook Ingestion  │
       │                    └──▶ Mail (SMTP)        │
       │                                            │
       └──── Hosted Checkout (final payment only) ──┘
```

## Data Flow

### Native Plan Discovery → Hosted Checkout

```
Flutter PlanCatalogScreen
  │ GET /api/plans (bmjServer reads from Chargebee-synced cache/DB)
  │
  ▼
Flutter PlanDetailScreen / ComparisonScreen
  │ User selects plan
  │
  ▼
Flutter AddressSelectionScreen
  │ Delivery slot picker
  │
  ▼
Flutter BillingReviewScreen
  │ POST /api/billing/checkout/review (bmjServer validates)
  │
  ▼
Flutter BillingReviewScreen (after review)
  │ POST /api/billing/checkout/start (bmjServer creates checkout session)
  │ Returns Chargebee hosted checkout URL
  │
  ▼
Flutter opens WebView → Chargebee Hosted Checkout ← SECURE PAYMENT ONLY
  │ Payment completed
  │
  ▼
Chargebee sends webhook → bmjServer → webhook_events table
  │ Update local subscription/order read model
  │ Auto-dispatch bottles on INVOICE_PAID
  │
  ▼
Flutter polls GET /api/billing/purchases/{id}/status → Success!
```

## Module Summary

| Module | Ownership | Description |
|--------|-----------|-------------|
| Auth | BMJ Server | JWT-based auth, refresh tokens, Google OAuth |
| Products/Plans 🔴 STUB | Chargebee (SOT) → BMJ (Cache) | Synced read model — ProductsBloc is a stub (BEM-007), all 6 handlers use mock data |
| Subscriptions 🔴 STUB | Chargebee (SOT) → BMJ (Cache) | BMJ manages local references — SubscriptionBloc is a stub (BEM-006), all 7 handlers use mock data |
| Orders | Chargebee (SOT) → BMJ (Cache) | BMJ manages delivery locally |
| Invoices | Chargebee (SOT) → BMJ (Cache) | Read-only view |
| Payments | Chargebee (SOT) | Handled in hosted checkout |
| Delivery | BMJ (SOT) | Addresses, slots, serviceability |
| Bottle Tracking | BMJ Server (SOT) | bottle_transactions table, ledger computation, auto-dispatch |
| Webhooks | BMJ Server | Idempotent ingestion, DLQ |
| Cache | Redis (BMJ-managed) | TTL-based, graceful degradation |
