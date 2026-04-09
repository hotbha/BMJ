# BookMyJuice - Architecture Overview

**Document Version:** 2.0  
**Last Updated:** 2026-03-29  
**Status:** Updated for Unified Signup Flow

---

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Application Architecture](#application-architecture)
3. [Data Architecture](#data-architecture)
4. [Security Architecture](#security-architecture)
5. [Integration Architecture](#integration-architecture)
6. [Architecture Decision Records](#architecture-decision-records)

---

## System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        BookMyJuice System                        │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│   Flutter    │         │   bmjServer  │         │  Chargebee   │
│   Mobile App │◄───────►│  Spring Boot │◄───────►│    Billing   │
│   (iOS/Android)  REST   │     API      │  API     │   Platform   │
└──────────────┘         └──────────────┘         └──────────────┘
       │                        │                        │
       │                        ▼                        │
       │                 ┌──────────────┐               │
       │                 │    MySQL     │               │
       │                 │   Database   │               │
       │                 └──────────────┘               │
       │                                                │
       └─────────────────── Internet ───────────────────┘
```

### Components

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Mobile App** | Flutter (Dart) | User interface, BLoC state management |
| **Backend API** | Spring Boot 3.x (Java 17) | REST API, authentication, Chargebee integration |
| **Database** | MySQL 8.0 | User data, cached Chargebee data |
| **Billing** | Chargebee | Subscription management, invoicing, payments |

---

## Application Architecture

### Flutter App Structure

```
lush/
├── lib/
│   ├── bloc/                    # BLoC state management
│   │   ├── AuthBloc/           # Authentication (ADR-002)
│   │   ├── CartBloc/           # Shopping cart
│   │   ├── ProductsBloc/       # Product catalog
│   │   ├── SubscriptionBloc/   # Subscriptions
│   │   └── UserBloc/           # User profile
│   ├── models/                  # Data models
│   ├── views/                   # UI screens
│   │   └── screens/            # All screens (11 new signup screens)
│   ├── UserRepository/         # API client
│   ├── services/               # Business logic
│   └── main.dart               # App entry point
├── integration_test/           # E2E tests
└── test/                       # Unit tests
```

### BLoC Pattern (ADR-002)

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Events    │─────►│    BLoC     │─────►│    States   │
│  (User Actions)    │  (Business  │      │  (UI State) │
│                     │   Logic)    │      │             │
└─────────────┘      └─────────────┘      └─────────────┘
                            │
                            ▼
                     ┌─────────────┐
                     │ Repository  │
                     │  (API Call) │
                     └─────────────┘
```

### Backend Structure

```
bmjServer/
├── src/main/java/com/bookmyjuice/
│   ├── controllers/              # REST endpoints
│   │   ├── AuthController.java  # Authentication (new: unified signup)
│   │   ├── CheckoutController.java
│   │   ├── SubscriptionController.java
│   │   └── webhooks/            # Chargebee webhook handlers
│   ├── models/                   # JPA entities
│   ├── repository/               # Data access layer
│   ├── services/                 # Business logic
│   │   ├── ChargebeeSyncService.java
│   │   └── UserDetailsImpl.java
│   ├── security/                 # Spring Security config
│   │   └── jwt/                 # JWT utilities
│   ├── payload/                  # Request/Response DTOs
│   │   ├── request/             # Request DTOs (new: UnifiedSignupRequest)
│   │   └── response/            # Response DTOs
│   └── util/                     # Utilities
│       ├── OTPUtil.java
│       └── EmailVerificationService.java (new)
└── src/main/resources/
    └── application.properties   # Configuration
```

---

## Data Architecture

### Database Schema (ADR-001)

```sql
-- Users (Authentication)
CREATE TABLE users (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(100) UNIQUE NOT NULL,  -- Email for email-based auth
  email VARCHAR(100) UNIQUE NOT NULL,
  phone VARCHAR(20) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL,  -- BCrypt hash
  first_name VARCHAR(50),
  last_name VARCHAR(50),
  address VARCHAR(120),
  extended_addr VARCHAR(120),
  extended_addr2 VARCHAR(120),
  city VARCHAR(120),
  state VARCHAR(120),
  zip VARCHAR(10),
  country VARCHAR(2) DEFAULT 'IN',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Roles & Authorization
CREATE TABLE roles (...);
CREATE TABLE user_roles (...);

-- Chargebee Data (Synced via webhooks)
CREATE TABLE items (...);         -- Products
CREATE TABLE item_prices (...);   -- Pricing
CREATE TABLE plans (...);         -- Subscription plans
CREATE TABLE subscriptions (...); -- User subscriptions
CREATE TABLE invoices (...);      -- Invoices
CREATE TABLE orders (...);        -- Orders
CREATE TABLE payments (...);      -- Payments
CREATE TABLE customers (...);     -- Customer billing details
```

### Data Flow (ADR-003)

```
┌─────────────────────────────────────────────────────────────┐
│                    Data Flow Architecture                    │
└─────────────────────────────────────────────────────────────┘

Write Operations (Commands):
  Flutter App → bmjServer → Chargebee API → Webhook → bmjServer → MySQL

Read Operations (Queries):
  Flutter App → bmjServer → MySQL (local cache) → Response

Example: Purchase Subscription
  1. User selects plan → GET /api/plans (from MySQL cache)
  2. User subscribes → POST /api/subscribe → Chargebee API
  3. Payment complete → Chargebee webhook → subscription.created
  4. bmjServer updates MySQL → Subscription visible in app

Example: View Order History
  1. User opens orders → GET /api/orders
  2. bmjServer queries MySQL → SELECT * FROM orders
  3. Return cached data (no Chargebee API call needed)
```

---

## Security Architecture

### Authentication Flow (ADR-004)

```
┌─────────────────────────────────────────────────────────────┐
│              Unified Signup Security Architecture            │
└─────────────────────────────────────────────────────────────┘

Signup Flow:
  User Input → Validation → Email Verification → Phone Verification
      ↓
  Address Collection → Password Creation → BCrypt Hash
      ↓
  MySQL User Creation → Chargebee Customer Creation → JWT Token
      ↓
  Auto Login → Dashboard

Login Flow:
  User Credentials → Validation → BCrypt Verify → JWT Token
      ↓
  15-minute expiration → Auto-login with persisted token
```

### Security Measures

| Layer | Measure | Implementation |
|-------|---------|----------------|
| **Transport** | HTTPS | TLS 1.3 (production) |
| **Authentication** | JWT | 15-minute expiration, HS256 |
| **Password** | BCrypt | Work factor 10, auto-salt |
| **Verification** | 6-digit codes | 10-minute expiry, one-time use |
| **Rate Limiting** | Request throttling | 5/hour per email/phone |
| **Authorization** | Role-based | USER, ADMIN, MODERATOR |
| **Input Validation** | Bean Validation | @NotBlank, @Email, @Size |
| **SQL Injection** | Parameterized queries | Spring Data JPA |

---

## Integration Architecture

### Chargebee Integration (ADR-003)

```
┌─────────────────────────────────────────────────────────────┐
│                  Chargebee Integration                       │
└─────────────────────────────────────────────────────────────┘

System Boundaries:
  Chargebee (Source of Truth for):
    ✅ Products/Items
    ✅ Plans & Pricing
    ✅ Subscriptions
    ✅ Invoices
    ✅ Orders
    ✅ Payments
    ✅ Customer billing details

  bmjServer (Source of Truth for):
    ✅ User Authentication
    ✅ Login credentials
    ✅ JWT tokens
    ✅ User roles
    ✅ Session management

Data Sync Strategy:
  Real-time: Webhooks (Chargebee → bmjServer)
  Batch: ChargebeeSyncService (startup sync)
  Cache: Local MySQL for fast reads
```

### API Endpoints

| Category | Endpoints | Purpose |
|----------|-----------|---------|
| **Authentication** | POST /api/auth/signup, /signin, /unified-signup | User auth |
| **Email Verification** | POST /api/auth/send-email-verification, /verify-email-code | Email verification (new) |
| **Phone Verification** | POST /api/auth/send-otp, /verify-otp | Phone verification |
| **Products** | GET /api/products, /plans | Fetch catalog (from cache) |
| **Subscriptions** | GET /api/subscriptions, POST /api/subscribe | Manage subscriptions |
| **Orders** | GET /api/orders | Order history (from cache) |
| **Invoices** | GET /api/invoices | Invoice list (from cache) |
| **Webhooks** | POST /api/webhooks/* | Chargebee webhook handlers |

---

## Architecture Decision Records

### ADR Index

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| [ADR-001](ADR-001-database-selection.md) | Database Selection - MySQL 8.0 | ACCEPTED | 2026-03-27 |
| [ADR-002](ADR-002-state-management-pattern.md) | State Management - BLoC Pattern | ACCEPTED | 2026-03-27 |
| [ADR-003](ADR-003-chargebee-integration-strategy.md) | Chargebee Integration & Data Sync | ACCEPTED | 2026-03-27 |
| [ADR-004](ADR-004-unified-signup-flow.md) | Unified Signup Flow Architecture | ACCEPTED | 2026-03-29 |

### Key Decisions Summary

| Decision | Option Selected | Rationale |
|----------|-----------------|-----------|
| Database | MySQL 8.0 | Team expertise, Spring Boot integration, cost |
| State Management | BLoC | Separation of concerns, testability, Flutter best practices |
| Billing | Chargebee | Focus on core business, managed compliance |
| Data Sync | Webhooks + Local Cache | Performance, reliability, offline support |
| Signup Flow | Multi-step with 3 entry points | User choice, data quality, security |

---

## Deployment Architecture

### Development

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Flutter    │     │  Spring Boot │     │    MySQL     │
│   (localhost)│────►│  (port 8080) │────►│  (Docker)    │
└──────────────┘     └──────────────┘     └──────────────┘
                              │
                              ▼
                     ┌──────────────┐
                     │  Chargebee   │
                     │  Test Site   │
                     └──────────────┘
```

### Production (Planned)

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Flutter    │     │   Spring Boot│     │  AWS RDS     │
│   (App Store)│────►│   (EC2/ECS)  │────►│    MySQL     │
└──────────────┘     └──────────────┘     └──────────────┘
                              │
                              ▼
                     ┌──────────────┐
                     │  Chargebee   │
                     │  Production  │
                     └──────────────┘
```

---

## Monitoring & Observability

### Backend Monitoring

- **Spring Boot Actuator:** `/actuator/health`, `/actuator/metrics`
- **Logging:** SLF4J + Logback (JSON format)
- **Error Tracking:** Sentry (future)
- **APM:** New Relic / Datadog (future)

### Frontend Monitoring

- **Crash Reporting:** Firebase Crashlytics
- **Analytics:** Firebase Analytics (future)
- **Performance:** Flutter DevTools

### Business Metrics

- Signup completion rate
- Email verification success rate
- Phone verification success rate
- Google signup adoption rate
- Drop-off per signup step

---

## References

- **Requirements:** `../requirements.yaml`
- **Test Cases:** `../UNIFIED_SIGNUP_TEST_CASES.md`
- **Use Cases:** `../UNIFIED_SIGNUP_USE_CASES.md`
- **Implementation Summary:** `../UNIFIED_SIGNUP_IMPLEMENTATION_SUMMARY.md`
- **API Docs:** `../API.md`
- **Backend Status:** `../BACKEND_FRONTEND_STATUS.md`

---

**Document Maintained By:** Engineering Team  
**Last Review:** 2026-03-29  
**Next Review:** 2026-04-29 (post-beta launch)
