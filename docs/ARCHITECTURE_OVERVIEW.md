# BookMyJuice — Enterprise Architecture Overview

**Document Version:** 3.0  
**Last Updated:** 2026-05-08  
**Status:** Enterprise-Grade Production Architecture

---

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Application Architecture](#application-architecture)
3. [Data Architecture](#data-architecture)
4. [Security Architecture](#security-architecture)
5. [Integration Architecture](#integration-architecture)
6. [Chargebee Integration Boundaries](#chargebee-integration-boundaries)
7. [Native Billing Flow](#native-billing-flow)
8. [Deployment Architecture](#deployment-architecture)

---

## System Architecture

### High-Level Overview

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                           BookMyJuice Enterprise System                       │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────┐       ┌──────────────────────────────────┐
│         Flutter Mobile App       │       │      Chargebee Hosted Pages      │
│         (iOS / Android)          │       │                                  │
│                                  │       │  ┌────────────────────────────┐  │
│  ┌──── NATIVE BMJ VIEWS ──────┐ │       │  │   Hosted Checkout ONLY     │  │
│  │ Plan Discovery (native)    │ │       │  │   (Final Payment Step)     │  │
│  │ Plan Detail (native)       │ │       │  └────────────────────────────┘  │
│  │ Plan Comparison (native)   │ │       └──────────────────────────────────┘
│  │ Cart / Review (native)     │ │                        ▲
│  │ Address Management (native)│ │                        │ WebView
│  │ Delivery Slots (native)    │ │                        │ (handoff only)
│  │ Subscription Mgmt (native) │ │                        │
│  │ Billing Summary (native)   │ │       ┌────────────────┴─────────────────┐
│  └────────────────────────────┘ │       │        bmjServer (Spring Boot)   │
│                                  │◄─────►│                                  │
│  ┌────────────────────────────┐  │ REST  │  Auth | Billing | Delivery      │
│  │ Hosted Checkout WebView   │  │       │  Webhooks | Cache | Audit        │
│  │ (final payment only)      │──┘       └────────┬──────────┬─────────────┘
│  └────────────────────────────┘                   │          │
└──────────────────────────────────┘                │          │
                                                    ▼          ▼
                                            ┌──────────┐ ┌──────────┐
                                            │  MySQL   │ │  Redis   │
                                            │  (8.0)   │ │  Cache   │
                                            └──────────┘ └──────────┘
```

### Core Principles

1. **Chargebee is the SINGLE SOURCE OF TRUTH** for all billing/subscription/product data.
2. **BMJ never re-implements** subscription logic, invoicing, payment ledger, or order ledger.
3. **Local persistence** of Chargebee-owned data is read/cache/sync/audit only — never ownership.
4. **Final payment completion** may remain on Chargebee hosted checkout. All other user-facing billing flows are native BMJ screens.
5. **BMJ owns** authentication, authorization, session management, delivery domain, and chargebee API orchestration.

### Component Responsibilities

| Component | Technology | Owns | Does NOT Own |
|-----------|------------|------|--------------|
| **bmjServer** | Spring Boot 3.x / Java 17 | Auth, sessions, delivery, webhook ingestion, cache, audit | Subscriptions, invoices, payments, orders, products |
| **Flutter App** | Flutter 3.x / Dart | Native UX, BLoC state management, cart, address, slot picking | Payment processing, billing logic |
| **MySQL** | MySQL 8.0 | User auth data, local read cache of Chargebee entities | Billing authoritative records |
| **Redis** | Redis 7.x | App cache (products, plans, service areas, slots) | Persistence (ephemeral cache only) |
| **Chargebee** | Chargebee SaaS | Subscriptions, invoices, payments, orders, plans, items, prices, billing customer data | User auth, delivery data, non-billing user data |

---

## Application Architecture

### Flutter App Structure

```
lush/
├── lib/
│   ├── bloc/                    # BLoC state management
│   │   ├── AuthBloc/           # Authentication + session
│   │   ├── BillingBloc/        # Native billing flow
│   │   ├── CartBloc/           # Shopping cart
│   │   ├── DeliveryBloc/       # Serviceability, slots, addresses
│   │   ├── ProductsBloc/       # Product catalog
│   │   ├── SubscriptionBloc/   # Subscription management
│   │   ├── ThemeCubit/         # Theme (light/dark/system)
│   │   └── UserBloc/           # User profile
│   ├── models/                  # Data models
│   ├── theme/                   # AppColors, AppTextStyles, AppTheme, AppSpacing
│   ├── views/
│   │   ├── screens/            # All screens
│   │   └── widgets/            # Reusable widgets
│   ├── services/               # HTTP API clients
│   ├── repositories/           # Data access layer
│   └── main.dart               # App entry point (ThemeData-driven)
└── test/
```

### Backend Structure

```
bmjServer/
├── src/main/java/com/bookmyjuice/
│   ├── bmjServer.java                    # Main entry
│   ├── config/                           # Redis, Chargebee, Role config
│   ├── controllers/
│   │   ├── AuthController.java           # Login, signup, refresh, token
│   │   ├── BillingController.java        # Native billing endpoints
│   │   ├── CartController.java           # Cart CRUD
│   │   ├── CheckoutController.java       # Hosted checkout handoff
│   │   ├── CheckoutV2Controller.java     # V2 one-time checkout
│   │   ├── ComplianceController.java     # Right-to-erasure, consent
│   │   ├── DeliveryController.java       # Serviceability, slots, addresses
│   │   ├── SessionController.java        # Logout, logout-all
│   │   ├── SubscriptionController.java   # Subscription CRUD (native)
│   │   ├── webhooks/                     # Chargebee webhook handlers
│   │   └── ...                           # Product, Invoice, Order, etc.
│   ├── models/entities/                  # JPA entities
│   ├── repository/                       # Data access
│   ├── services/                         # Business logic
│   │   ├── DeliveryService.java
│   │   ├── WebhookSignatureService.java
│   │   ├── SessionManagementService.java
│   │   └── ...
│   ├── security/                         # JWT, rate limiting, webhook filter
│   └── util/                             # OTP, email, etc.
```

---

## Chargebee Integration Boundaries

### What Chargebee Owns (SSOT)

| Domain | Chargebee API | BMJ Local Cache |
|--------|--------------|-----------------|
| Products/Items | ✅ `Item` CRUD | ✅ Read-only cache via webhooks + startup sync |
| Item Prices | ✅ `ItemPrice` CRUD | ✅ Read-only cache via webhooks + startup sync |
| Plans | ✅ `Plan` CRUD | ✅ Read-only cache via webhooks + startup sync |
| Subscriptions | ✅ `Subscription` lifecycle | ✅ Reference cache via webhooks |
| Invoices | ✅ `Invoice` lifecycle | ✅ Reference cache for display |
| Payments | ✅ `Payment`/`Transaction` | ✅ Reference cache |
| Orders | ✅ `Order` lifecycle | ✅ Reference cache |
| Billing Customers | ✅ `Customer` CRUD | ✅ Reference mapping only |

### What BMJ Owns (SSOT)

| Domain | Source | Notes |
|--------|--------|-------|
| User Auth (credentials) | BMJ users table | Password hashes, roles |
| JWT Tokens | BMJ in-memory + refresh token table | Access + refresh token lifecycle |
| Session Management | BMJ refresh_tokens table | Revocation, logout-all |
| Delivery Domain | BMJ delivery tables | Service areas, slots, addresses |
| Audit Logs | BMJ audit_log table | Security event tracking |
| Consent Records | BMJ consent_records table | GDPR/privacy compliance |
| Anonymization State | BMJ users table | Right-to-erasure markers |

---

## Native Billing Flow

### Flow Diagram: Plan Discovery → Hosted Checkout

```
┌──────────────────────────────────────────────────────────────────────┐
│              NATIVE BMJ FLOW (Plan Discovery → Review)               │
└──────────────────────────────────────────────────────────────────────┘

  User opens app
      │
      ▼
┌──────────────────────┐
│  Native Plan Catalog │  ← Reads from local cache (MySQL/Redis)
│  (Plan cards,        │     Backed by webhook-synced plans
│   filter, compare)   │
└──────┬───────────────┘
       │ Select plan
       ▼
┌──────────────────────┐
│  Native Plan Detail  │  ← Full plan details, features, pricing
│  (Description,       │
│   features, CTA)     │
└──────┬───────────────┘
       │ Subscribe / Add to cart
       ▼
┌──────────────────────┐
│  Native Cart/Review  │  ← Cart contents, quantity, size
│  (Items, quantities, │
│   address, delivery) │
└──────┬───────────────┘
       │ Proceed to checkout
       ▼
┌──────────────────────┐
│  Native Pre-Checkout │  ← Address selection, slot selection,
│  Review + Validation │     billing summary, price breakdown
└──────┬───────────────┘
       │ Confirm
       ▼
╔══════════════════════╗
║  HOSTED CHECKOUT     ║  ← ONLY Chargebee-hosted step
║  (Chargebee WebView) ║     Secure payment completion
║  Payment, Auth,      ║     NO plan browsing or discovery
║  Confirmation        ║     NO pricing table
╚══════════════════════╝
       │
       ▼
┌──────────────────────┐
│  Native Confirmation │  ← Order placed, subscription active
│  (Order/success)     │     Data synced via webhook
└──────────────────────┘
```

### Why Hosted Checkout is Retained

- PCI DSS compliance for payment card data
- Chargebee handles secure 3D Secure, card storage, payment gateways
- Avoids re-implementing payment processing logic
- SCA/regulatory compliance delegated

### Why Pricing Tables/Pages are Removed

- Pricing tables and hosted pages create fragmented UX (leaving BMJ → Chargebee → BMJ)
- Native plan discovery provides consistent brand experience
- Faster page loads (no network round-trip to Chargebee for rendering)
- Full control over layout, comparison, filtering
- Better offline experience (cached plan data)

---

## Deployment Architecture

### Development

```
docker-compose up -d
  ├── MySQL 8.0 (port 3306)
  ├── Redis 7 (port 6379)  
  └── bmjServer Spring Boot (port 8080)
```

### Production (Target)

```
Flutter (App Store/Play Store) → API Gateway → bmjServer (ECS/EC2)
                                                    ├── MySQL RDS
                                                    ├── Redis ElastiCache (optional)
                                                    └── Chargebee API
```

---

## References

- [Chargebee Integration Strategy](architecture/ADR-003-chargebee-integration-strategy.md)
- [Native Billing Flow](NATIVE_BILLING_FLOW.md)
- [Webhook Reliability](WEBHOOK_RELIABILITY.md)
- [Caching Strategy](CACHING_STRATEGY.md)
- [Compliance & Privacy](COMPLIANCE_PRIVACY.md)
- [API Documentation](API.md)
- [Design System](DESIGN_SYSTEM.md)
- [Design System → Flutter Integration](DESIGN_SYSTEM_FLUTTER_INTEGRATION.md)

---

**Document Maintained By:** Engineering Team  
**Last Review:** 2026-05-08  
**Next Review:** 2026-06-08
