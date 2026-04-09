# ADR-003: Chargebee Integration & Data Sync Strategy

**Date:** March 27, 2026  
**Status:** ACCEPTED  
**Supersedes:** N/A  

---

## Context

BookMyJuice requires a robust billing and subscription management system. We've chosen Chargebee as our billing platform. However, we need to clearly define:

1. What data lives where (Chargebee vs. bmjServer)
2. How data stays in sync between systems
3. When to call Chargebee API vs. use local cache
4. How user authentication maps to Chargebee customers
5. **How developers should work with Chargebee (Chargebee MCP)**

### Key Requirements

- **Single Source of Truth:** Avoid data conflicts between systems
- **Performance:** Minimize Chargebee API calls (rate limits, latency)
- **Reliability:** System should work even if Chargebee API is temporarily unavailable
- **User Experience:** Fast data retrieval for catalog, orders, subscriptions
- **Data Ownership:** Clear separation of authentication vs. billing data
- **Developer Experience:** Use Chargebee MCP to understand and work with Chargebee

---

## Decision

### 0. Development Tooling - Chargebee MCP (CRITICAL)

**MANDATORY:** All developers MUST use Chargebee MCP (Model Context Protocol) in VSCode

**Why:**
- Most functionalities are managed by Chargebee, not custom-built
- Developers need to understand Chargebee architecture quickly
- Real-time access to API documentation and examples
- Test API calls without writing code
- Understand webhook payloads and events

**Setup:**
1. Install Chargebee MCP extension in VSCode
2. Configure with test site credentials
3. Use MCP to query Chargebee documentation
4. Test API calls via MCP before implementing

**Example MCP Queries:**
```
"How does Chargebee hosted page checkout work?"
"What API endpoint to create a subscription?"
"What webhook events are triggered when payment fails?"
"Show me the Chargebee customer object structure"
"How to pause a subscription via API?"
"List all subscription webhook events"
```

**Reference:** See `CONTRIBUTING.md` for detailed Chargebee MCP setup instructions

---

## Decision

### 1. System Boundaries

#### Chargebee (Billing Platform) - SOURCE OF TRUTH FOR:
- ✅ Products/Items (juices with variants)
- ✅ Plans (subscription plans)
- ✅ Pricing (all price points, discounts)
- ✅ Categories (Delight, Signature, Premium)
- ✅ Subscriptions (lifecycle: active, paused, cancelled)
- ✅ Invoices (billing records)
- ✅ Orders (transaction records)
- ✅ Payments (payment transactions)
- ✅ Customers (billing details, shipping addresses)

#### bmjServer (Application Server) - SOURCE OF TRUTH FOR:
- ✅ User Authentication (ONLY)
- ✅ Login credentials (email, password hash)
- ✅ JWT tokens
- ✅ User roles (USER, ADMIN, MODERATOR)
- ✅ Session management
- ✅ Authorization rules

### 2. One-to-One User-Customer Mapping

**Principle:** Every authenticated user MUST have a corresponding Chargebee customer

```
┌─────────────────┐         ┌──────────────────┐
│   bmjServer     │         │    Chargebee     │
│                 │         │                  │
│  User Table     │◄───────►│  Customer        │
│  ───────────    │  1:1    │  ───────────     │
│  id             │  map    │  id              │
│  email          │         │  email           │
│  password_hash  │         │  (no password)   │
│  roles          │         │  billing_info    │
│  chargebee_    │         │  shipping_info   │
│  customer_id ───┘         │                  │
└─────────────────┘         └──────────────────┘
```

**Implementation:**
- During signup: Create User in bmjServer → Create Customer in Chargebee
- Store `chargebee_customer_id` in users table
- All Chargebee operations reference this customer_id

### 3. Data Sync Strategy

#### Sync Mechanisms

**A. Webhooks (Real-Time)**
```
Chargebee Event → Webhook → bmjServer → Update Local DB
```

**Webhooks to Implement:**
- `customer.created` → Sync customer details
- `customer.updated` → Update customer details
- `subscription.created` → Create/update subscription
- `subscription.updated` → Update subscription
- `subscription.cancelled` → Update subscription status
- `invoice.created` → Create invoice record
- `invoice.paid` → Update payment status
- `invoice.failed` → Update payment status
- `payment.succeeded` → Create payment record
- `payment.failed` → Log payment failure
- `item.created` → Create product
- `item.updated` → Update product
- `item_price.created` → Create price
- `plan.created` → Create plan
- `plan.updated` → Update plan

**B. ChargebeeSyncService (Batch/Startup)**
```
Application Startup → ChargebeeSyncService → Fetch All → Update Local DB
```

**Sync Scope:**
- All items (products)
- All item prices
- All plans
- All subscriptions for existing users
- Recent invoices (last 90 days)

**Frequency:**
- On application startup
- Scheduled daily sync (optional)
- Manual trigger via admin endpoint

#### Local Cache Tables (bmjServer MySQL)

```sql
-- Synced from Chargebee
items               -- Products/juices
item_prices         -- Size-based pricing
plans               -- Subscription plans
subscriptions       -- User subscriptions
invoices            -- Billing invoices
orders              -- Order records
payments            -- Payment transactions
customers           -- Customer billing details (mirror)

-- Managed locally
users               -- Authentication credentials
roles               -- User roles
user_roles          -- Role assignments
```

### 4. API Call Strategy

#### Use Local Cache (DON'T call Chargebee API)

**Read Operations:**
- ✅ Fetch product catalog → `SELECT * FROM items`
- ✅ Fetch plans → `SELECT * FROM plans`
- ✅ Fetch user's subscriptions → `SELECT * FROM subscriptions WHERE customer_id = ?`
- ✅ Fetch order history → `SELECT * FROM orders WHERE customer_id = ?`
- ✅ Fetch invoices → `SELECT * FROM invoices WHERE customer_id = ?`
- ✅ Fetch payment history → `SELECT * FROM payments WHERE customer_id = ?`
- ✅ Fetch customer details → `SELECT * FROM customers WHERE id = ?`

**Benefits:**
- Fast response times (< 100ms)
- No Chargebee API rate limit concerns
- Works during Chargebee API downtime
- Reduced external dependencies

#### Call Chargebee API Directly

**Write Operations:**
- ✅ Create hosted page (checkout)
- ✅ Create new subscription
- ✅ Update existing subscription
- ✅ Cancel subscription
- ✅ Pause subscription
- ✅ Resume subscription
- ✅ Process payment
- ✅ Create/Update customer billing info

**Why Direct API Calls:**
- These are state-changing operations
- Chargebee is source of truth for billing
- Webhooks will sync changes back to local DB

### 5. Data Flow Examples

#### Example 1: User Signup

```
1. User submits signup form
   ↓
2. bmjServer creates User (with password hash)
   ↓
3. bmjServer creates Chargebee Customer
   ↓
4. Store chargebee_customer_id in users table
   ↓
5. Return JWT token to user
   ↓
6. User is now authenticated AND has Chargebee customer
```

#### Example 2: Purchase Subscription

```
1. User selects plan → Fetch from local plans table
   ↓
2. User clicks "Subscribe" → Create hosted page via Chargebee API
   ↓
3. User completes payment on Chargebee
   ↓
4. Chargebee sends webhook: subscription.created
   ↓
5. bmjServer webhook handler creates subscription in local DB
   ↓
6. User's subscription now visible in app (from local cache)
```

#### Example 3: View Order History

```
1. User opens "Order History" screen
   ↓
2. Flutter app calls: GET /api/orders
   ↓
3. bmjServer queries: SELECT * FROM orders WHERE customer_id = ?
   ↓
4. Return orders from local database
   ↓
5. NO Chargebee API call needed (fast!)
```

---

## Consequences

### Positive

1. **Performance:** Local cache provides sub-100ms response times
2. **Reliability:** System works during Chargebee API downtime
3. **Scalability:** No Chargebee API rate limit issues
4. **Clear Boundaries:** Authentication vs. Billing clearly separated
5. **Data Ownership:** Each system owns its domain
6. **Audit Trail:** Webhooks provide complete event history

### Negative

1. **Complexity:** Need to maintain sync logic
2. **Data Lag:** Small delay between Chargebee and local DB (webhook latency)
3. **Webhook Reliability:** Must handle failed webhooks gracefully
4. **Storage:** Local database stores duplicate of Chargebee data

### Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Webhook fails | Data out of sync | Retry logic, manual sync endpoint |
| Chargebee API down | Can't create subscriptions | Queue operations, retry later |
| Sync conflict | Data inconsistency | Chargebee is source of truth, overwrite local |
| Customer not mapped | User can't purchase | Validate during signup, admin fix tool |

---

## Implementation Checklist

### Backend (bmjServer)

- [ ] Add `chargebee_customer_id` column to users table
- [ ] Update signup flow to create Chargebee customer
- [ ] Implement all webhook handlers (listed above)
- [ ] Implement ChargebeeSyncService for startup sync
- [ ] Update all read endpoints to use local cache
- [ ] Update all write endpoints to call Chargebee API
- [ ] Add admin endpoint to manually trigger sync
- [ ] Add admin tool to fix user-customer mapping issues

### Frontend (Flutter)

- [ ] No changes needed (API remains same)
- [ ] Faster response times (benefit from local cache)
- [ ] Offline support for catalog browsing (future)

### Testing

- [ ] Test webhook handlers with Chargebee test events
- [ ] Test startup sync with test data
- [ ] Test user-customer mapping during signup
- [ ] Test subscription flow end-to-end
- [ ] Test order history retrieval (local cache)
- [ ] Test webhook failure scenarios

---

## References

- **Chargebee Webhooks:** https://www.chargebee.com/docs/2.0/webhooks.html
- **Chargebee API:** https://www.chargebee.com/docs/2.0/api.html
- **Existing Implementation:** `bmjServer/src/main/java/com/bookmyjuice/controllers/webhooks/`
- **Existing Sync:** `bmjServer/src/main/java/com/bookmyjuice/services/ChargebeeSyncService.java`

---

## Notes

This architecture follows the **CQRS (Command Query Responsibility Segregation)** pattern:
- **Commands (Write):** Chargebee API
- **Queries (Read):** Local MySQL cache

This is a common pattern for integrating with third-party billing platforms while maintaining performance and reliability.

---

**Approved By:** Development Team  
**Approval Date:** March 27, 2026  
**Review Date:** April 27, 2026 (or after beta launch)
