# BookMyJuice - Business Requirements Document (BRD)

**Document Version:** 2.0 (Consolidated)
**Date:** April 11, 2026
**Project:** BookMyJuice - Cold-Pressed Juice Subscription Platform
**Stakeholders:** Product Owner, Development Team, QA Team, Beta Users

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Project Scope](#2-project-scope)
3. [Business Requirements](#3-business-requirements)
4. [Product Decisions & Rules](#4-product-decisions--rules)
5. [Non-Functional Requirements](#5-non-functional-requirements)
6. [Requirements Traceability Matrix](#6-requirements-traceability-matrix)
7. [Development Phases](#7-development-phases)
8. [Risk Assessment](#8-risk-assessment)
9. [Appendix: Discovered Requirements](#9-appendix-discovered-requirements)

---

## 1. Executive Summary

### 1.1 Business Objective
BookMyJuice is a cold-pressed juice subscription and on-demand ordering platform targeting health-conscious consumers seeking convenient, fresh juice delivery.

### 1.2 System Architecture
```
┌──────────────┐     REST/JSON      ┌──────────────┐    Chargebee API     ┌─────────────┐
│  Mobile App  │ ◄────────────────► │  bmjServer   │ ◄──────────────────► │  Chargebee  │
│  (Flutter)   │                    │  (Spring Boot│                      │  (Hosted    │
│              │                    │   + MySQL)   │ ◄──── webhooks ───── │   Pages)    │
└──────────────┘                    └──────────────┘                      └─────────────┘
```

### 1.3 Golden Rules
1. Mobile app **NEVER** talks to Chargebee directly
2. Mobile app **NEVER** calculates prices locally
3. Mobile app **NEVER** shows optimistic status — always refetch from bmjServer
4. bmjServer is the **only** data source for the mobile app
5. Chargebee is the **only** source of billing truth; bmjServer syncs via webhooks
6. All prices are in **cents** (minor currency units). Mobile divides by 100 for display
7. All timestamps are **UTC**. Mobile converts to local timezone for display

### 1.4 MVP Success Metrics
| Metric | Target | Measurement Period |
|--------|--------|-------------------|
| User Signups | 50 users | Week 1-2 |
| Active Users (DAU) | 20 users | Week 2 |
| Subscription Conversions | 5 users | Week 1-2 |
| One-Time Orders | 10 orders | Week 1-2 |
| App Crash Rate | < 1% | Week 1-2 |
| API Uptime | > 99% | Week 1-2 |
| Payment Success Rate | > 90% | Week 1-2 |

---

## 2. Project Scope

### 2.1 In Scope (MVP)
- User registration and authentication (Email + Phone OTP + Google Sign-In)
- Unified signup flow with 3 entry points (Email-First, Phone-First, Google)
- Product catalog browsing (juices with size variants: 200ml, 300ml, 500ml)
- Shopping cart management (single-mode: either one-time OR subscription items)
- One-time checkout via Chargebee Hosted Pages
- Subscription plan selection and purchase (18 plans: 3 categories × 3 sizes × 2 frequencies)
- Subscription management (pause, resume, cancel with 9 PM cutoff)
- User profile and address management
- Order history viewing with pagination
- Push notifications for key events
- Guest cart with merge on login

### 2.2 Out of Scope (Post-MVP)
- Multiple delivery addresses
- Scheduled delivery slots selection
- Loyalty points and referral programs
- Advanced analytics dashboard
- Biometric authentication
- Offline mode
- iOS native app (App Store)

### 2.3 Platform Support
| Platform | MVP Support | Post-MVP |
|----------|-------------|----------|
| Android (Mobile) | APK (Manual Install) | Play Store |
| iOS | ❌ Not in MVP | App Store |
| Web | ✅ Browser Access | PWA |
| Backend API | ✅ REST API (Spring Boot) | GraphQL |

---

## 3. Business Requirements

### 3.1 User Management

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| BR-001 | Users can register with email/password and verify email | P0 | Email verification code sent, 6-digit, 10-min expiry |
| BR-002 | Users can register with phone/OTP and verify phone | P0 | 6-digit OTP, 10-min expiry, 10-digit Indian numbers |
| BR-003 | Users can signup with Google (email pre-verified) | P0 | Google OAuth returns verified email, phone still required |
| BR-004 | Guest users can build cart before login | P0 | Cart persisted in SharedPreferences + server with user_id=NULL |
| BR-005 | On login, guest cart merges into authenticated server cart | P0 | User chooses which cart to keep on conflict; discarded cart permanently deleted |
| BR-006 | JWT tokens valid for 30 days with no refresh token workflow | P0 | Token stored in SharedPreferences; **auto-login checks ONLY token validity** — does NOT invoke Google Sign-In or phone OTP. Expired/missing token shows login screen. |
| BR-007 | Users can manage profile information and address | P1 | View/update name, phone, complete address |
| BR-008 | Guest users can browse product catalog without authentication | P0 | Product endpoints return data with optional auth; cart/checkout require login |
| BR-009 | Users can reset password via two methods | P0 | (1) Reset via mobile OTP — user enters phone, receives 6-digit OTP, verifies OTP, sets new password. (2) Reset via email OTP — user enters email, receives 6-digit verification code, verifies code, sets new password. Both methods enforce same password complexity rules as signup. |
| BR-010 | Google Sign-In triggered ONLY by user clicking Google button on login screen | P0 | Auto-login never invokes Google. When guest clicks Google button: (a) show account picker, (b) if user with that Google ID exists → auto-login with JWT, (c) if not → start signup with pre-filled email + name from Google account. |
| BR-011 | Phone Sign-In triggered ONLY by user clicking Phone button on login screen | P0 | Auto-login never invokes phone OTP. When guest clicks Phone button: (a) show phone input, (b) verify with 6-digit OTP, (c) if user with that verified phone exists → auto-login with JWT, (d) if not → start signup with pre-filled verified phone number. |

### 3.2 Product Catalog

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| BR-010 | Users can browse juice products with details | P0 | Products display with images, descriptions, prices, size options |
| BR-011 | Products show both one-time and subscription pricing | P0 | One-time price + subscription plans (weekly/monthly) visible |
| BR-012 | Products can be filtered by category | P1 | Categories: Delight, Signature, Premium |

### 3.3 Cart & Pricing

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| BR-020 | Cart is single-mode (one-time OR subscription, never both) | P0 | Adding opposite-type item returns 409, user chooses |
| BR-021 | Mobile app MUST NOT calculate prices locally | P0 | All pricing from bmjServer API (subtotal, tax, delivery_fee, total) |
| BR-022 | Cart shows price breakdown | P0 | Subtotal, tax, delivery fee, grand total displayed |
| BR-023 | MVP delivery fee is ₹0 (free delivery for all orders) | P0 | Delivery fee always 0 for MVP, no threshold calculation |
| BR-024 | Tax is sourced from Chargebee pricing data only | P0 | bmjServer passes through Chargebee tax amount; no independent tax calculation in app or server |

### 3.4 Checkout & Payment

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| BR-030 | Checkout performed via Chargebee Hosted Pages | P0 | Hosted page opened in WebView |
| BR-031 | bmjServer creates hosted page, returns URL to mobile | P0 | POST /api/v1/checkout/initiate returns URL + session ID |
| BR-032 | After payment, mobile refetches confirmed state from bmjServer | P0 | No optimistic UI, always refetch |
| BR-033 | Chargebee sends webhooks to bmjServer for billing events | P0 | Webhooks processed idempotently, MySQL updated |

### 3.5 Subscriptions

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| BR-040 | Users can view all subscriptions (multiple simultaneous allowed) | P0 | List all subscriptions with status, dates, pricing |
| BR-041 | Users can pause subscription before 9 PM IST for next-day skip | P0 | Pause scheduled, status updates via webhook. 9 PM IST cutoff enforced for all users |
| BR-042 | Users can resume subscription before 9 PM IST for next-day activation | P0 | Resume scheduled, status updates via webhook. 9 PM IST cutoff enforced for all users |
| BR-043 | Users can cancel subscriptions (immediately/end of term/specific date) | P0 | Cancel option selected, processed via Chargebee |
| BR-044 | No limit on number of pause/resume cycles | P0 | Unlimited pause/resume allowed |
| BR-045 | Mobile sends subscription actions to bmjServer; bmjServer calls Chargebee | P0 | No direct Chargebee calls from mobile |
| BR-046 | App must refetch confirmed state from bmjServer after any action | P0 | POST returns 202, mobile must GET to confirm |
| BR-047 | User can have multiple active subscriptions simultaneously | P0 | No restriction on subscription count |

### 3.6 Orders & Status

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| BR-050 | Order status shown in app is fetched from bmjServer database | P0 | GET /api/v1/orders returns MySQL data |
| BR-051 | Chargebee is upstream source of billing/status changes via webhooks | P0 | Webhooks update MySQL, then mobile fetches |
| BR-052 | Users can view order history with pagination | P0 | Default 20/page, sortable by date |
| BR-053 | Users can view order details including items, pricing, shipping | P0 | Full order details with line items, status timeline |
| BR-054 | Invoice PDFs viewed via Chargebee-hosted URLs | P1 | GET /api/v1/orders/:id/invoice returns hosted URL |

### 3.7 Notifications

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| BR-060 | Push notifications sent for payment failures | P0 | flutter_local_notifications triggered on payment_failed webhook processing (local-only for MVP, no FCM server) |
| BR-061 | Push notifications sent for subscription actions | P1 | flutter_local_notifications on subscription_paused/resumed/cancelled (local-only for MVP) |
| BR-062 | Push notifications sent for order events | P1 | flutter_local_notifications on order_updated/delivered (local-only for MVP) |

---

## 4. Product Decisions & Rules

### 4.1 Core Product Decisions

| ID | Decision | Detail |
|----|----------|--------|
| PD-01 | Authentication First | No Guest Checkout. Users must Sign up, Sign in, or Auto-login before accessing Cart or Checkout |
| PD-02 | Cart Logic | Cart is **Single-Mode**. A cart must contain **either** One-Time items **OR** Subscription Plans. Mixing is forbidden |
| PD-03 | Cart Totals | Mobile App **MUST NOT** calculate prices. It displays only values returned by bmjServer API |
| PD-04 | Checkout Flows | Separate endpoints: `POST /api/v1/checkout` (One-Time) and `POST /api/v1/subscribe` (Subscription) |
| PD-05 | Subscription Config | Mobile App provides **Day-Wise Schedule** (JSON) to bmjServer. bmjServer passes as `metadata` to Chargebee |
| PD-06 | Chargebee Setup | 18 Plans (3 Categories × 3 Sizes × 2 Frequencies). `plan_{category}_{size}_{frequency}` |
| PD-07 | Status Ownership | Mobile App reads status **ONLY** from bmjServer. bmjServer syncs from Chargebee via Webhooks |
| PD-08 | Address Pre-fill | bmjServer passes `hosted_page[customer][billing_address]` to Chargebee when generating Hosted Page URLs |

### 4.2 Product Catalog Mapping (Chargebee → bmjServer)

| Chargebee Entity | BookMyJuice Concept | Mapping Logic |
|------------------|---------------------|---------------|
| **Item** (`type='charge'`) | **One-Time Juice** | `id` → `id`, `name`, `image_url` (from `meta_data`) |
| **Plan** (`type='plan'`) | **Subscription Plan** | `id` → `plan_id`, `name`, `image_url` (from `meta_data`) |
| **Item.meta_data** | **Display Data** | Stores `{"category": "Delight", "image_url": "..."}` |

### 4.3 Subscription Day-Wise Scheduling

User selects juices for specific days in Mobile App. **Week contains 6 days (Sunday is holiday/off).**

**UI Behavior:**
- Sunday is shown as "Holiday" (non-selectable)
- A "Same juice everyday" checkbox is displayed at the top
  - When checked: User selects one juice → mapped to all 6 active days (Mon–Sat)
  - When unchecked: User selects juice per day independently

**Schedule JSON (sent to bmjServer):**
```json
{
  "Monday": "juice_abc",
  "Tuesday": "juice_abc",
  "Wednesday": "juice_pineapple",
  "Thursday": "juice_abc",
  "Friday": "juice_abc",
  "Saturday": "juice_abc"
}
```

This JSON is stored in the `meta_data` of the Chargebee subscription. Applicable to **all plan types** (weekly and monthly).

**Implementation Status:** ⏳ Not yet implemented — needs to be built.

### 4.4 UI/UX Requirements (Discovered During Implementation)

| ID | Requirement | Detail |
|----|-------------|--------|
| UI-001 | Loading States | All async operations must show loading indicator |
| UI-002 | Error Handling | Graceful error handling with fallback UI for all API calls |
| UI-003 | Status Color Coding | Active: Green, Paused: Orange, Cancelled: Red, Expired: Grey |
| UI-004 | Date Formatting | All dates displayed as DD/MM/YYYY |
| UI-005 | Billing Display | Billing period as "₹X / Frequency" format |
| UI-006 | Conditional Buttons | Different action buttons based on subscription status |
| UI-007 | Token Management | JWT retrieved from SharedPreferences for all API calls |

---

## 5. Non-Functional Requirements

### 5.1 Performance

| ID | Requirement | Target | Measurement |
|----|-------------|--------|-------------|
| NFR-001 | API response time < 2 seconds for 95th percentile | p95 < 2000ms | Backend logging, monitoring |
| NFR-002 | App cold start < 3 seconds | < 3000ms | Flutter performance metrics |
| NFR-003 | Screen render < 16ms (60 FPS) | 60 FPS | Flutter DevTools |

### 5.2 Security

| ID | Requirement | Target | Measurement |
|----|-------------|--------|-------------|
| NFR-004 | All API calls over HTTPS | 100% HTTPS | Network inspection |
| NFR-005 | Passwords hashed with BCrypt (cost factor 10) | 100% compliance | Code review, security scan |
| NFR-006 | JWT tokens stored securely | SharedPreferences with encryption | Code review |
| NFR-007 | Webhook signature validation | Reject invalid with 401 | X-Chargebee-Webhook-Signature header check |

### 5.3 Reliability

| ID | Requirement | Target | Measurement |
|----|-------------|--------|-------------|
| NFR-008 | API uptime > 99% | 99% during beta | Uptime monitoring |
| NFR-009 | App crash rate < 1% | < 1% of sessions | Crash reporting |
| NFR-010 | Idempotent webhook processing | No duplicate events | Deduplicate by event.id |

### 5.4 Usability

| ID | Requirement | Target | Measurement |
|----|-------------|--------|-------------|
| NFR-011 | First-time user completes signup in < 2 minutes | < 120 seconds | User testing |
| NFR-012 | All text meets WCAG 2.1 AA contrast ratio (4.5:1) | 100% compliance | Accessibility scanner |

---

## 6. Requirements Traceability Matrix

| Business Req | Functional Req | Use Case | Test Cases | Status |
|--------------|----------------|----------|------------|--------|
| BR-001 to BR-003 | FR-AUTH-001 to FR-AUTH-008 | UC-AUTH-001 to UC-AUTH-003 | TC-AUTH-EF-*, TC-AUTH-PF-*, TC-AUTH-GS-* | ✅ Implemented |
| BR-006 | FR-AUTH-004 | UC-AUTH-004 | TC-AUTH-005, TC-AUTH-006 | ✅ Implemented |
| BR-010 | FR-AUTH-003 | UC-AUTH-005 | TC-AUTH-007, TC-AUTH-008 | ✅ Implemented |
| BR-011 | FR-AUTH-002 | UC-AUTH-006 | TC-AUTH-009, TC-AUTH-010 | ✅ Implemented |
| BR-010 to BR-012 | FR-PROD-001 to FR-PROD-005 | UC-PROD-* | TC-PROD-* | ✅ Implemented |
| BR-020 to BR-024 | FR-CART-001 to FR-CART-006 | UC-CART-* | TC-CART-* | ✅ Implemented |
| BR-030 to BR-033 | FR-CHK-001 to FR-CHK-004 | UC-CHK-* | TC-CHK-* | ✅ Implemented |
| BR-040 to BR-047 | FR-SUB-001 to FR-SUB-009 | UC-SUB-* | TC-SUB-* | ✅ Implemented |
| BR-050 to BR-054 | FR-ORD-001 to FR-ORD-003 | UC-ORD-* | TC-ORD-* | ✅ Implemented |
| BR-060 to BR-062 | FR-PUSH-001 to FR-PUSH-003 | UC-PUSH-* | TC-PUSH-* | ⏳ Pending |

---

## 7. Development Phases

### Phase 1: Foundation (Days 1-3)
- ✅ Setup development environment
- ✅ Configure CI/CD pipeline
- ✅ Setup test frameworks
- ✅ Database schema verification
- ✅ Chargebee test site configuration

### Phase 2: Authentication (Days 4-7)
- ✅ Implement unified signup flow (Email-First, Phone-First, Google)
- ✅ Implement JWT authentication with 30-day expiry
- ✅ Implement auto-login with token persistence
- ✅ Write unit and integration tests
- ✅ **Milestone: User can register and login**

### Phase 3: Product Catalog (Days 8-10)
- ✅ Implement product listing from Chargebee
- ✅ Implement product details with size variants
- ✅ Implement category filtering
- ✅ **Milestone: User can browse products**

### Phase 4: Shopping Cart (Days 11-13)
- ✅ Implement cart with single-mode constraint
- ✅ Implement cart merge for guest→auth login
- ✅ Implement price breakdown from bmjServer
- ✅ Implement cart persistence (SharedPreferences)
- ✅ **Milestone: User can add to cart**

### Phase 5: Checkout (Days 14-17)
- ✅ Implement one-time checkout via Chargebee Hosted Pages
- ✅ Implement subscription checkout
- ✅ Implement webhook handlers for order/subscription events
- ✅ **Milestone: User can complete purchase**

### Phase 6: Subscription Management (Days 18-20)
- ✅ Implement subscription listing
- ✅ Implement pause/resume/cancel with 9 PM cutoff
- ✅ Implement day-wise schedule management
- ✅ **Milestone: User can manage subscriptions**

### Phase 7: Order Management (Days 21-23)
- ✅ Implement order history with pagination
- ✅ Implement order details view
- ✅ Implement invoice URL retrieval
- ✅ **Milestone: User can view orders**

### Phase 8: Testing & Beta Preparation (Days 24-25)
- ✅ Full regression testing
- ✅ Build release APK
- ✅ Deploy to staging
- ✅ Prepare beta user instructions

### Phase 9: Beta Launch (Days 26-30)
- ✅ Onboard 10-20 beta users
- ✅ Monitor system performance
- ✅ Collect and triage feedback
- ✅ Fix critical bugs within 24 hours
- **Milestone: MVP launched to beta users**

---

## 8. Risk Assessment

| Risk ID | Risk Description | Probability | Impact | Mitigation |
|---------|------------------|-------------|--------|------------|
| RISK-001 | Chargebee API rate limits | Medium | High | Implement caching, batch requests |
| RISK-002 | Payment failures in test mode | High | Medium | Clear error messages, retry logic |
| RISK-003 | Database connection failures | Low | High | Connection pooling, retry logic |
| RISK-004 | JWT token security breach | Low | Critical | Short expiry, secure storage |
| RISK-005 | Beta user dropoff | Medium | Medium | Engaging onboarding, support |
| RISK-006 | Performance degradation under load | Medium | High | Load testing, monitoring |
| RISK-007 | Out-of-order webhook events | Medium | Medium | Resource version comparison |

---

## 9. Appendix: Discovered Requirements

### 9.1 Requirements Discovered During Implementation

During subscription card integration and testing, the following requirements were identified but not in original specifications. All have been implemented:

| ID | Requirement | Category | Status |
|----|-------------|----------|--------|
| REQ-SUB-001 | Dashboard shall automatically fetch and display user's subscription data on load | Subscription Display | ✅ Implemented |
| REQ-SUB-002 | Dashboard shall display loading indicator while fetching subscription data | Loading State | ✅ Implemented |
| REQ-SUB-003 | Dashboard shall handle subscription fetch errors gracefully with fallback UI | Error Handling | ✅ Implemented |
| REQ-AUTH-004 | Application shall retrieve JWT token from SharedPreferences for authenticating API requests | Token Management | ✅ Implemented |
| REQ-SUB-004 | Subscription status displayed with color-coded badges (Active:Green, Paused:Orange, Cancelled:Red, Expired:Grey) | Status Display | ✅ Implemented |
| REQ-SUB-005 | Subscription dates formatted as DD/MM/YYYY for display | Date Formatting | ✅ Implemented |
| REQ-SUB-006 | Billing period displayed as "₹X / Frequency" format | Billing Display | ✅ Implemented |
| REQ-SUB-007 | Different action buttons based on subscription status (Manage/Subscribe) | Conditional UI | ✅ Implemented |
| REQ-SUB-008 | Navigate to Chargebee hosted pages for subscription management | Navigation | ✅ Implemented |
| REQ-MODEL-001 | Subscription model provides helper methods for formatting dates, billing, status colors/text | Data Model | ✅ Implemented |

### 9.2 Lessons Learned

1. **Loading States Matter** - Always specify loading indicators for async operations
2. **Error Handling is Critical** - Always handle API errors gracefully with fallback UI
3. **Data Formatting Needs Specification** - Dates (DD/MM/YYYY), Currency (₹), Status colors
4. **Token Management is Implicit** - Specify storage mechanism and retrieval for API calls
5. **Conditional UI Based on Data** - Different UI states based on subscription status

---

## Appendix A: Glossary

| Term | Definition |
|------|------------|
| AOV | Average Order Value |
| BR | Business Requirement |
| FR | Functional Requirement |
| NFR | Non-Functional Requirement |
| UC | Use Case |
| TC | Test Case |
| JWT | JSON Web Token |
| DAU | Daily Active Users |
| MVP | Minimum Viable Product |
| SDLC | Software Development Life Cycle |
| FCM | Firebase Cloud Messaging |
| OTP | One-Time Password |

---

**Document Control:**
- **Created:** March 27, 2026
- **Last Updated:** April 11, 2026 (Consolidated)
- **Version:** 2.0
- **Status:** ✅ Approved for Beta Release
