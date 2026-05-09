# BookMyJuice - Functional Specification

**Document Version:** 1.0 (Consolidated)
**Date:** April 11, 2026
**Linked to:** BRD_Business_Requirements.md, API.md
**Status:** ✅ Approved for Development

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [API Specifications](#2-api-specifications)
3. [Authentication Module](#3-authentication-module)
4. [Cart Module](#4-cart-module)
5. [Checkout Module](#5-checkout-module)
6. [Subscription Module](#6-subscription-module)
7. [Order Module](#7-order-module)
8. [Webhook Module](#8-webhook-module)
9. [Push Notification Module](#9-push-notification-module)
10. [Product Catalog Module](#10-product-catalog-module)
11. [Database Schema](#11-database-schema)
12. [Frontend Specifications](#12-frontend-specifications)

---

## 1. System Overview

### 1.1 Architecture
```
┌──────────────┐     REST/JSON      ┌──────────────┐    Chargebee API     ┌─────────────┐
│  Mobile App  │ ◄────────────────► │  bmjServer   │ ◄──────────────────► │  Chargebee  │
│  (Flutter)   │                    │  (Spring Boot│                      │  (Hosted    │
│              │                    │   + MySQL)   │ ◄──── webhooks ───── │   Pages)    │
└──────────────┘                    └──────────────┘                      └─────────────┘
       │                                    │
       │                           ┌────────▼────────┐
       │                           │  FCM Push Server │
       │                           └──────────────────┘
```

### 1.2 Data Flow Architecture

**Write Operations (Commands):**
```
Flutter App → bmjServer → Chargebee API → Webhook → bmjServer → MySQL
```

**Read Operations (Queries):**
```
Flutter App → bmjServer → MySQL (local cache) → Response
```

**Example - Purchase Subscription:**
1. User selects plan → GET /api/v1/products (from MySQL cache)
2. User subscribes → POST /api/v1/checkout/initiate → Chargebee API
3. Payment complete → Chargebee webhook → subscription.created
4. bmjServer updates MySQL → Subscription visible in app

**Example - View Order History:**
1. User opens orders → GET /api/v1/orders
2. bmjServer queries MySQL → SELECT * FROM orders
3. Return cached data (no Chargebee API call needed)

### 1.3 Product Catalog Mapping

| Chargebee Entity | BookMyJuice Concept | Mapping Logic |
|------------------|---------------------|---------------|
| **Item** (`type='charge'`) | **One-Time Juice** | `id` → `id`, `name`, `image_url` (from `meta_data`) |
| **Plan** (`type='plan'`) | **Subscription Plan** | `id` → `plan_id`, `name`, `image_url` (from `meta_data`) |
| **Item.meta_data** | **Display Data** | Stores `{"category": "Delight", "image_url": "..."}` |

### 1.4 GET /api/v1/products Response Schema
```json
{
  "products": [
    {
      "id": "juice_abc",
      "name": "ABC Juice",
      "category": "Delight",
      "image_url": "https://cdn.../abc.jpg",
      "one_time_price": {
        "id": "charge_abc_200",
        "price": 7500,
        "currency": "INR"
      },
      "subscription_plans": [
        {
          "plan_id": "plan_delight_200_weekly",
          "frequency": "weekly",
          "price": 40000
        },
        {
          "plan_id": "plan_delight_200_monthly",
          "frequency": "monthly",
          "price": 150000
        }
      ]
    }
  ]
}
```

---

## 2. API Specifications

### Base URLs
| Environment | URL |
|-------------|-----|
| Development | `http://localhost:8080/api/v1` |
| Staging | `https://staging-api.bookmyjuice.co.in/api/v1` |
| Production | `https://api.bookmyjuice.co.in/api/v1` |

### Authentication
- JWT Bearer token in `Authorization` header
- Token expiry: 30 days (no refresh token workflow)
- Token stored in SharedPreferences
- **Auto-login:** Checks ONLY token validity via `GET /api/v1/auth/me`. Does NOT invoke Google Sign-In or phone OTP. If token expired/missing → show login screen.
- **Google Sign-In:** Triggered ONLY when user taps Google button on login screen. Never auto-invoked.
- **Phone Sign-In:** Triggered ONLY when user taps Phone button on login screen. Never auto-invoked.

### Login Flow Decision Tree
```
User opens app
  → Auto-login: Check JWT token in SharedPreferences
    → Valid token + server confirms → Dashboard
    → Expired/missing → Show Login Screen

Login Screen
  → User enters email + password → POST /api/v1/auth/login → JWT → Dashboard
  → User taps Google button → Show Google account picker
    → If user with Google ID exists → Login with JWT → Dashboard
    → If user NOT found → Signup screen with pre-filled email + name from Google
  → User taps Phone button → Enter phone → Send OTP → Verify OTP
    → If user with verified phone exists → Login with JWT → Dashboard
    → If user NOT found → Signup screen with pre-filled verified phone
```

### 3.1 Unified Signup Flow

Three entry points converging to same data collection:
1. **Email-First:** Email → Verify → Phone → Verify OTP → Address → Password
2. **Phone-First:** Phone → Verify OTP → Email → Verify → Address → Password  
3. **Google:** Google Auth (email verified) → Phone → Verify OTP → Address → Password

### 3.2 API Endpoints

| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/api/v1/auth/signup` | POST | No | Create user with email/password |
| `/api/v1/auth/login` | POST | No | Authenticate user, return JWT |
| `/api/v1/auth/logout` | POST | Yes | Invalidate JWT server-side |
| `/api/v1/auth/me` | GET | Yes | Get current user profile |
| `/api/v1/auth/unified-signup` | POST | No | Unified signup (any entry point) |
| `/api/v1/auth/send-email-verification` | POST | No | Send 6-digit email code |
| `/api/v1/auth/verify-email-code` | POST | No | Verify email code |
| `/api/v1/auth/send-otp` | POST | No | Send 6-digit phone OTP |
| `/api/v1/auth/verify-otp` | POST | No | Verify phone OTP |
| `/api/v1/auth/reset-password-mobile` | POST | No | Reset password via mobile OTP (phone → OTP → new password) |
| `/api/v1/auth/reset-password-email` | POST | No | Reset password via email OTP (email → verification code → new password) |

### 3.3 Password Requirements
- Minimum 8 characters
- At least 1 uppercase letter (A-Z)
- At least 1 lowercase letter (a-z)
- At least 2 numbers (0-9)
- At least 1 special character (!@#$%^&* etc.)
- No spaces or control characters

### 3.4 Password Reset

Two methods available:

**Method 1: Reset via Mobile OTP**
1. User enters registered phone number
2. System sends 6-digit OTP to phone (same OTPUtil as signup, 10-min expiry)
3. User enters OTP
4. System validates OTP
5. User enters new password (must meet complexity requirements)
6. System validates password, updates BCrypt hash in database
7. System clears any existing sessions for that user

**Method 2: Reset via Email OTP**
1. User enters registered email address
2. System sends 6-digit verification code to email (same EmailVerificationService as signup, 10-min expiry)
3. User enters verification code
4. System validates code
5. User enters new password (must meet complexity requirements)
6. System validates password, updates BCrypt hash in database
7. System clears any existing sessions for that user

**Common Rules for Both Methods:**
- Phone/email must be registered (user must exist)
- OTP/verification code: 6 digits, 10-minute expiry
- Rate limiting: 5 attempts per hour per phone/email
- Password must meet same complexity requirements as signup
- Old sessions invalidated after password change

### 3.5 Verification Code Rules
- 6-digit code, 10-minute expiry
- Resend available after 30 seconds
- Maximum 5 resend attempts per email/phone
- Maximum 3 verification attempts per code
- Old code invalidated when new code sent

---

## 4. Cart Module

### 4.1 Cart Rules
- Cart type determined by first item added
- Cannot mix one-time and subscription items
- Adding opposite-type item returns `409 Conflict` with both cart types for user choice
- Guest cart persisted via `cart_id` in SharedPreferences + server with `user_id = NULL`

### 4.2 API Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/v1/cart` | GET | Optional | Get cart with pricing |
| `/api/v1/cart/items` | POST | Optional | Add item to cart |
| `/api/v1/cart/items/:id` | PUT | Optional | Update item quantity (min 1, max 99) |
| `/api/v1/cart/items/:id` | DELETE | Optional | Remove item from cart |
| `/api/v1/cart` | DELETE | Optional | Clear entire cart |
| `/api/v1/cart/merge` | POST | Yes | Merge guest cart into authenticated cart |

### 4.3 Cart Response Schema
```json
{
  "cart_id": "cart_123",
  "cart_type": "onetime",
  "items": [
    {
      "id": "item_1",
      "chargebee_item_price_id": "charge_abc_200",
      "item_name": "ABC Juice 200ml",
      "quantity": 2,
      "unit_price": 7500
    }
  ],
  "pricing": {
    "subtotal": 15000,
    "tax": 2700,
    "delivery_fee": 0,
    "grand_total": 17700,
    "currency": "INR"
  }
}
```

**Notes:**
- `tax` value is sourced directly from Chargebee pricing data (passthrough, no calculation)
- `delivery_fee` is always 0 for MVP (free delivery)
- Mobile app MUST NOT calculate these values — display only what bmjServer returns

### 4.4 Cart Merge Flow
1. User logs in with guest cart items
2. Mobile calls `POST /api/v1/cart/merge` with `{ "guest_cart_id": "cart_guest_123" }`
3. If both carts exist with **different types**:
   - bmjServer returns `409 Conflict` with `{ "user_cart_type": "subscription", "guest_cart_type": "onetime" }`
   - Mobile shows dialog: "Which cart would you like to keep?"
   - User selects → Mobile calls merge again with `{ "keep": "guest" }` or `{ "keep": "user" }`
   - The **discarded cart is permanently deleted** (items included)
4. If same cart types → items merged automatically; duplicates take higher quantity
5. If no existing auth cart → guest cart simply reassigned

---

## 5. Checkout Module

### 5.1 API Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/v1/checkout/initiate` | POST | Yes | Create Chargebee hosted page, return URL + session ID |
| `/api/v1/checkout/complete` | POST | Yes | Finalize checkout, retrieve hosted page content |
| `/api/v1/checkout/status/:session_id` | GET | Yes | Poll checkout session status |

### 5.2 One-Time Checkout Flow
1. User taps "Proceed to Checkout" on Cart screen
2. Mobile calls `POST /api/v1/checkout/initiate` with cart contents
3. bmjServer calls Chargebee `POST /api/v2/hosted_pages/checkout_new_for_items`
4. Chargebee returns `{ hosted_page: { id: "hp_xxx", url: "https://..." } }`
5. bmjServer creates checkout session, returns `{ checkout_session_id: "cs_xxx", hosted_page_url: "https://..." }`
6. Mobile opens Payment WebView with the URL
7. User completes payment on Chargebee-hosted page
8. Chargebee redirects to `redirect_url?id=hp_xxx&state=succeeded`
9. Mobile calls `POST /api/v1/checkout/complete { checkout_session_id, hosted_page_id }`
10. bmjServer retrieves hosted page, syncs order/invoice/payment to MySQL
11. bmjServer clears user's cart, returns `{ order_id: "ord_xxx", status: "pending" }`
12. Mobile navigates to Order Confirmation screen
13. Mobile calls `GET /api/v1/orders/ord_xxx` to fetch confirmed state

### 5.3 Subscription Checkout Flow
Same as one-time, but:
- `subscription_items` includes a `plan`-type item at index 0
- After checkout complete, bmjServer creates both order AND subscription records
- Response includes `{ order_id, subscription_id, status: "active" }`
- Mobile navigates to Order Confirmation → shows subscription info

---

## 6. Subscription Module

### 6.1 API Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/v1/subscriptions` | GET | Yes | List all subscriptions for user |
| `/api/v1/subscriptions/:id` | GET | Yes | Get single subscription details |
| `/api/v1/subscriptions/:id/delivery-schedule` | GET | Yes | Get upcoming delivery dates |
| `/api/v1/subscriptions/:id/pause` | POST | Yes | Pause before 9 PM for next-day skip |
| `/api/v1/subscriptions/:id/resume` | POST | Yes | Resume before 9 PM for next-day activation |
| `/api/v1/subscriptions/:id/cancel` | POST | Yes | Cancel (immediately/end_of_term/specific_date) |
| `/api/v1/subscriptions/:id/remove-scheduled-pause` | POST | Yes | Cancel pending pause |
| `/api/v1/subscriptions/:id/remove-scheduled-resume` | POST | Yes | Cancel pending resume |
| `/api/v1/subscriptions/:id/remove-scheduled-cancellation` | POST | Yes | Cancel pending cancellation |

### 6.2 Subscription Actions

| Action | Mobile App Flow | Backend Logic |
|--------|----------------|---------------|
| **Pause** | User taps "Pause" → Confirm → POST to bmjServer | Calls Chargebee `pause` API. Updates local DB via Webhook |
| **Resume** | User taps "Resume" → Confirm → POST to bmjServer | Calls Chargebee `resume` API. Updates local DB via Webhook |
| **Cancel** | User taps "Cancel" → Confirm → POST to bmjServer | Calls Chargebee `cancel` API. Updates local DB via Webhook |

### 6.3 Subscription Response Schema
```json
{
  "id": "sub_123",
  "user_id": "user_456",
  "chargebee_subscription_id": "cb_sub_789",
  "status": "active",
  "plan_id": "plan_delight_200_monthly",
  "plan_name": "Delight 200ml Monthly",
  "billing_period": 2999,
  "billing_period_unit": "month",
  "current_term_start": 1712000000000,
  "current_term_end": 1714592000000,
  "next_billing_at": 1714592000000,
  "currency_code": "INR",
  "mrr": 2999,
  "items": [
    {
      "chargebee_item_price_id": "charge_abc_200",
      "item_name": "ABC Juice 200ml",
      "quantity": 1,
      "unit_price": 2999
    }
  ]
}
```

### 6.4 9 PM IST Cutoff Rule
- All subscription mutation endpoints return `202 Accepted` — mobile must refetch to get confirmed state
- **9 PM IST (Asia/Kolkata) cutoff** enforced for ALL users and servers (single timezone)
- If time >= 9 PM IST → bmjServer returns `400` → mobile shows "Actions available until 9 PM. Changes will take effect next day."

---

## 7. Order Module

### 7.1 API Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/v1/orders` | GET | Yes | List all orders (paginated, default 20/page) |
| `/api/v1/orders/:id` | GET | Yes | Get order details with line items, pricing, shipping |
| `/api/v1/orders/:id/invoice` | GET | Yes | Return Chargebee-hosted invoice URL |

### 7.2 Order Response Schema
```json
{
  "id": "ord_123",
  "user_id": "user_456",
  "chargebee_order_id": "cb_ord_789",
  "chargebee_invoice_id": "inv_012",
  "subscription_id": "sub_345",
  "status": "confirmed",
  "payment_status": "paid",
  "subtotal": 15000,
  "delivery_fee": 0,
  "tax": 2700,
  "discount": 0,
  "grand_total": 17700,
  "currency_code": "INR",
  "shipping_address": {
    "flat_no": "A-101",
    "society": "Green Valley",
    "area": "Sector 12",
    "city": "Gurgaon",
    "state": "Haryana",
    "zip": "122001",
    "country": "IN"
  },
  "items": [
    {
      "item_name": "ABC Juice 200ml",
      "quantity": 2,
      "unit_price": 7500,
      "total": 15000
    }
  ],
  "created_at": "2026-04-11T10:00:00Z",
  "updated_at": "2026-04-11T10:05:00Z"
}
```

---

## 8. Webhook Module

### 8.1 API Endpoint
- `POST /api/v1/webhooks/chargebee`

### 8.2 Security
- Validate `X-Chargebee-Webhook-Signature` header; reject invalid with `401`
- Idempotent processing — deduplicate by `event.id` in `webhook_events` table
- Out-of-order events handled via `resource_version` comparison
- Processed events trigger MySQL updates + push notifications (if applicable)
- Wrap webhook processing in database transaction for atomicity

### 8.3 Chargebee Object Mapping

| bmjServer Table | Chargebee Entity | Sync Mechanism |
|---|---|---|
| `users` | Customer | Webhook: `customer_created`, `customer_changed` |
| `subscriptions` | Subscription | Webhook: `subscription_created`, `subscription_changed`, `subscription_cancelled`, `subscription_paused`, `subscription_resumed` |
| `subscription_items` | Subscription Items | Embedded in subscription webhooks |
| `orders` | Order + Invoice | Webhook: `order_created`, `order_updated`, `order_delivered`, `invoice_generated` |
| `order_items` | Order Line Items | Embedded in order webhooks |
| `payments` | Transaction | Webhook: `payment_succeeded`, `payment_failed` |
| `webhook_events` | Webhook Event | All events (idempotent log) |

---

## 9. Push Notification Module

**MVP Approach:** Local-only notifications using `flutter_local_notifications` package. No FCM server push for MVP.

### 9.1 Trigger Points (Local)
Notifications are triggered locally when the app processes webhook results or user actions:
- `payment_failed` — After webhook processing confirms payment failure
- `subscription_paused` — After user pauses subscription and confirms state refetch
- `subscription_resumed` — After user resumes subscription and confirms state refetch
- `subscription_cancelled` — After user cancels subscription and confirms state refetch
- `order_updated` — When order status changes to "shipped"
- `order_delivered` — When order status changes to "delivered"

### 9.2 Implementation Notes
- All notifications are scheduled locally via `flutter_local_notifications`
- No FCM server-side push for MVP (simplifies infrastructure)
- Notification payload includes deep-link data for in-app navigation
- Post-MVP: Migrate to FCM server-side push for background/closed-app notifications

### 9.3 API Endpoints (Not needed for MVP)
FCM token registration endpoints are **deferred to post-MVP** since notifications are local-only.

---

## 10. Product Catalog Module

### 10.1 API Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/v1/products` | GET | Optional | List all products with pricing (guest browsing allowed) |
| `/api/v1/products/:id` | GET | Optional | Get product details (guest browsing allowed) |
| `/api/v1/plans` | GET | Optional | List subscription plans (guest browsing allowed) |

### 10.2 Product Categories
- **Delight:** Entry-level juices, affordable pricing
- **Signature:** Mid-range premium juices
- **Premium:** High-end exotic juices

### 10.3 Size Variants
- 200ml (Single serving)
- 300ml (Regular)
- 500ml (Large/Family)

---

## 11. Database Schema

### 11.1 MySQL Schema (bmjServer)

```sql
-- Users
CREATE TABLE users (
    id              VARCHAR(36) PRIMARY KEY,
    chargebee_customer_id VARCHAR(50) UNIQUE,
    email           VARCHAR(255) UNIQUE NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    first_name      VARCHAR(100),
    last_name       VARCHAR(100),
    phone           VARCHAR(20),
    timezone        VARCHAR(50) DEFAULT 'Asia/Kolkata',
    fcm_tokens      JSON,
    jwt_token       VARCHAR(500),
    jwt_expires_at  DATETIME,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Carts
CREATE TABLE carts (
    id              VARCHAR(36) PRIMARY KEY,
    user_id         VARCHAR(36) NULL,
    cart_type       ENUM('onetime', 'subscription') NOT NULL,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Cart Items
CREATE TABLE cart_items (
    id                  VARCHAR(36) PRIMARY KEY,
    cart_id             VARCHAR(36) NOT NULL,
    chargebee_item_price_id VARCHAR(100) NOT NULL,
    item_name           VARCHAR(255),
    item_type           ENUM('plan', 'addon', 'charge') NOT NULL,
    quantity            INT NOT NULL DEFAULT 1,
    unit_price          INT NOT NULL,
    created_at          DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (cart_id) REFERENCES carts(id) ON DELETE CASCADE
);

-- Subscriptions
CREATE TABLE subscriptions (
    id                      VARCHAR(36) PRIMARY KEY,
    user_id                 VARCHAR(36) NOT NULL,
    chargebee_subscription_id   VARCHAR(50) UNIQUE NOT NULL,
    status                  ENUM('future', 'trial', 'active', 'non_renewing', 'paused', 'cancelled') NOT NULL,
    plan_id                 VARCHAR(100),
    plan_name               VARCHAR(255),
    billing_period          INT,
    billing_period_unit     ENUM('day', 'week', 'month', 'year'),
    current_term_start      DATETIME,
    current_term_end        DATETIME,
    next_billing_at         DATETIME,
    pause_date              DATETIME,
    resume_date             DATETIME,
    cancelled_at            DATETIME,
    cancel_option           ENUM('immediately', 'end_of_term', 'specific_date'),
    scheduled_cancellation_at DATETIME,
    currency_code           VARCHAR(3) DEFAULT 'INR',
    mrr                     INT,
    resource_version        BIGINT,
    created_at              DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at              DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted                 BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Orders
CREATE TABLE orders (
    id                  VARCHAR(36) PRIMARY KEY,
    user_id             VARCHAR(36) NOT NULL,
    chargebee_order_id  VARCHAR(50),
    chargebee_invoice_id VARCHAR(50),
    subscription_id     VARCHAR(36) NULL,
    status              ENUM('pending', 'confirmed', 'preparing', 'shipped', 'delivered', 'cancelled', 'refunded') NOT NULL DEFAULT 'pending',
    payment_status      ENUM('not_paid', 'paid', 'failed', 'refunded') NOT NULL DEFAULT 'not_paid',
    subtotal            INT NOT NULL,
    delivery_fee        INT NOT NULL DEFAULT 0,
    tax                 INT NOT NULL,
    discount            INT NOT NULL DEFAULT 0,
    grand_total         INT NOT NULL,
    currency_code       VARCHAR(3) DEFAULT 'INR',
    shipping_address    JSON,
    resource_version    BIGINT,
    created_at          DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    delivered_at        DATETIME NULL,
    cancelled_at        DATETIME NULL,
    deleted             BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (subscription_id) REFERENCES subscriptions(id) ON DELETE SET NULL
);

-- Order Items
CREATE TABLE order_items (
    id                  VARCHAR(36) PRIMARY KEY,
    order_id            VARCHAR(36) NOT NULL,
    chargebee_item_price_id VARCHAR(100),
    item_name           VARCHAR(255) NOT NULL,
    quantity            INT NOT NULL,
    unit_price          INT NOT NULL,
    total               INT NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
);

-- Payments
CREATE TABLE payments (
    id                      VARCHAR(36) PRIMARY KEY,
    user_id                 VARCHAR(36) NOT NULL,
    chargebee_transaction_id VARCHAR(50),
    chargebee_invoice_id    VARCHAR(50),
    amount                  INT NOT NULL,
    currency_code           VARCHAR(3) DEFAULT 'INR',
    status                  ENUM('succeeded', 'failed', 'refunded', 'pending') NOT NULL,
    payment_method          VARCHAR(50),
    created_at              DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Webhook Events
CREATE TABLE webhook_events (
    id                  VARCHAR(36) PRIMARY KEY,
    chargebee_event_id  VARCHAR(100) UNIQUE NOT NULL,
    event_type          VARCHAR(100) NOT NULL,
    resource_version    BIGINT NOT NULL,
    payload             JSON NOT NULL,
    processed_at        DATETIME,
    created_at          DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Push Notification Log
CREATE TABLE push_notifications (
    id                  VARCHAR(36) PRIMARY KEY,
    user_id             VARCHAR(36) NOT NULL,
    fcm_token           VARCHAR(500) NOT NULL,
    title               VARCHAR(255) NOT NULL,
    body                TEXT NOT NULL,
    data                JSON,
    status              ENUM('sent', 'failed') NOT NULL,
    created_at          DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

---

## 12. Frontend Specifications

### 12.1 State Management
- **Pattern:** BLoC (Business Logic Component) with flutter_bloc
- **Structure:** Events → BLoC (Business Logic) → States → UI

### 12.2 App Structure
```
lush/
├── lib/
│   ├── bloc/                    # BLoC state management
│   │   ├── AuthBloc/           # Authentication
│   │   ├── CartBloc/           # Shopping cart
│   │   ├── ProductsBloc/       # Product catalog
│   │   ├── SubscriptionBloc/   # Subscriptions
│   │   └── UserBloc/           # User profile
│   ├── models/                  # Data models
│   ├── views/                   # UI screens
│   │   └── screens/            # All screens
│   ├── UserRepository/         # API client
│   ├── services/               # Business logic
│   └── main.dart               # App entry point
├── integration_test/           # E2E tests
└── test/                       # Unit tests
```

### 12.3 Token Management
- JWT token stored in SharedPreferences
- Retrieved for all authenticated API calls
- Auto-login on app launch if valid token exists
- Token cleared on logout or expiration

### 12.4 Cart Persistence
- Guest cart: `cart_id` stored in SharedPreferences
- Authenticated cart: server-side with `user_id`
- Cart merged on login via `POST /api/v1/cart/merge`

---

**Document Control:**
- **Created:** April 11, 2026 (Consolidated)
- **Version:** 1.0
- **Status:** ✅ Approved for Development
