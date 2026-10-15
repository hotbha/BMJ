# BookMyJuice (BMJ) Architecture Overview

High-level system design and data flows for the enterprise-grade juice subscription platform.

## System Topology

```
+-------------------------------------------------------------+
|                      Flutter App (lush)                     |
|            Catalog, Subscription & Auth Flows              |
+------------------------------+------------------------------+
                               |
                        HTTP / REST APIs
                               |
                               v
+-------------------------------------------------------------+
|                  Spring Boot Server (bmjServer)             |
|            Authentication, Catalog Sync, Subscriptions      |
+--------+---------------------+-----------------------+------+
         |                     |                       |
         v                     v                       v
  +--------------+      +--------------+      +-------------------+
  |   MySQL 8    |      |   Redis 7    |      |  Chargebee API    |
  | (Persisted)  |      |   (Cache)    |      | (Catalog 2.0/Web) |
  +--------------+      +--------------+      +-------------------+
```

---

## Critical Endpoints

| Route | Method | Access | Description |
| :--- | :--- | :--- | :--- |
| `/api/health` | GET | Public | Healthcheck gate for backend & dependent services |
| `/api/auth/google` | POST | Public | Google OAuth sign-in & JWT generation |
| `/api/test/charge-items` | GET | Public/Dev | Fetches raw Chargebee catalog items & item prices |
| `/api/subscriptions/pricing/plans` | GET | Public/User | Returns available subscription plans |
| `/api/subscriptions/my` | GET | User | Fetches active subscriptions for current authenticated user |
| `/api/subscriptions/create` | POST | User | Generates Chargebee Hosted Page checkout session URL |
| `/api/subscriptions/{id}/pause` | PUT | User | Pauses subscription (enforces 9 PM IST cutoff) |
| `/api/subscriptions/{id}/resume` | PUT | User | Resumes paused subscription (enforces 9 PM IST cutoff) |
| `/api/subscriptions/{id}` | DELETE | User | Cancels subscription (enforces 9 PM IST cutoff) |

---

## Data Flow Architecture

### 1. Catalog Sync Flow
1. Background cron worker calls Chargebee Catalog 2.0 API (`Item.list()` / `ItemPrice.list()`).
2. Catalog objects are normalized into local DB (`products`, `item_prices`) and cached in Redis.
3. Flutter client retrieves filtered items via `/api/test/charge-items` or `/api/subscriptions/pricing/plans`.

### 2. Subscription Creation Flow
1. User selects plan and size in Flutter app (`Subscribe` tab).
2. Flutter requests hosted checkout page URL via `POST /api/subscriptions/create`.
3. Backend invokes Chargebee Hosted Page API (`HostedPage.checkoutNewForItems()`).
4. Flutter opens Chargebee checkout page in webview.

### 3. Webhook Handling
1. Chargebee dispatches event webhooks (`subscription_created`, `subscription_changed`, `subscription_cancelled`) to `/api/v1/webhooks/chargebee`.
2. Backend verifies HMAC signature and updates local MySQL subscription entity state asynchronously.