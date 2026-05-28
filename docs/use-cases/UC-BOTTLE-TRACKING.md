# UC-BOTTLE-TRACKING: Bottle Tracking System

## Overview

The Bottle Tracking System manages the lifecycle of reusable bottles used in juice delivery. It records when bottles are issued to customers (with orders/subscriptions), tracks returns, and logs breakage/loss reports. This system supports BookMyJuice's sustainability initiative by providing visibility into bottle circulation.

## Actors

| Actor | Description |
|-------|-------------|
| **Customer** | End-user who orders juice and receives/returns bottles |
| **System (auto-dispatch)** | Automatically records bottle issuance on order payment confirmation |
| **Delivery Personnel** | Records bottle returns at pickup/delivery (future) |
| **Admin/Support** | Views ledger, manual adjustments, handles disputes |

## Use Cases

### UC-1: View Bottle Ledger

| Field | Value |
|-------|-------|
| **ID** | UC-BT-01 |
| **Name** | View Bottle Ledger |
| **Actor** | Customer |
| **Preconditions** | Customer is authenticated |
| **Postconditions** | Ledger entries displayed with computed balances |
| **Trigger** | User taps "My Bottles" in navigation drawer |

**Flow:**
1. User opens navigation drawer and taps "My Bottles"
2. System loads `GET /api/bottles/ledger`
3. System computes per-bottle-type balances: totalIssued, totalReturned, totalBroken, outstanding
4. System displays ledger cards with visual indicators (green for zero outstanding, red for positive)
5. System also loads recent transaction history via `GET /api/bottles/transactions`
6. User can pull-to-refresh to reload data

**Alternative Flows:**
- **Empty ledger:** Display "No Bottles Yet" message with recycling icon
- **Error/Unauthorized:** Show error message with Retry button
- **Loading:** Show CircularProgressIndicator

### UC-2: Auto-Dispatch Bottles on Payment

| Field | Value |
|-------|-------|
| **ID** | UC-BT-02 |
| **Name** | Auto-Dispatch Bottles on Payment |
| **Actor** | System |
| **Preconditions** | Order payment confirmed (INVOICE_PAID webhook received) |
| **Postconditions** | BottleTransactionEntity created with action=ISSUED |
| **Trigger** | WebhookEventProcessor receives INVOICE_PAID event |

**Flow:**
1. Chargebee sends INVOICE_PAID webhook to bmjServer
2. `WebhookEventProcessor.processRelatedEntitiesForInvoice()` is invoked
3. System extracts line items from invoice JSON
4. `bottleTrackingService.autoDispatchBottles()` is called with orderId and customerId
5. Default bottle type "glass_500ml" is used, quantity capped at 20
6. `BottleTrackingService.recordIssue()` creates a bottle_transactions row
7. Failure is logged but never breaks the checkout flow

**Business Rules:**
- Auto-dispatch is best-effort, non-blocking
- Default bottle type: glass_500ml
- Max bottles per order: 20 (sanity cap)
- Future enhancement: parse line items for bottle-type-specific auto-dispatch

### UC-3: Report Bottle Return

| Field | Value |
|-------|-------|
| **ID** | UC-BT-03 |
| **Name** | Report Bottle Return |
| **Actor** | Customer / Delivery Personnel |
| **Preconditions** | Customer has outstanding bottles |
| **Postconditions** | BottleTransactionEntity created with action=RETURNED |
| **Trigger** | Return reported via API |

**Flow:**
1. Customer returns bottles at delivery pickup
2. API call `POST /api/bottles/return` with orderId, bottleType, quantity
3. `BottleTrackingService.recordReturn()` creates transaction
4. Ledger is updated — outstanding balance decreases
5. Flutter app refreshes ledger display

### UC-4: Report Broken/Lost Bottles

| Field | Value |
|-------|-------|
| **ID** | UC-BT-04 |
| **Name** | Report Broken/Lost Bottles |
| **Actor** | Customer / Delivery Personnel |
| **Preconditions** | Customer has outstanding bottles; bottle is physically broken or lost |
| **Postconditions** | BottleTransactionEntity created with action=BROKEN |
| **Trigger** | Breakage/loss reported via API |

**Flow:**
1. Customer reports bottle as broken or lost
2. API call `POST /api/bottles/broken` with orderId, bottleType, quantity
3. `BottleTrackingService.recordBroken()` creates transaction
4. Ledger is updated — outstanding balance decreases (but tracked separately from returns)
5. Flutter app refreshes ledger display

### UC-5: View Transaction History (Order-Level)

| Field | Value |
|-------|-------|
| **ID** | UC-BT-05 |
| **Name** | View Order Transaction History |
| **Actor** | Admin / Support |
| **Preconditions** | Order exists in system |
| **Postconditions** | Transaction list displayed |
| **Trigger** | Admin views order details |

**Flow:**
1. Admin views order details
2. System calls `GET /api/bottles/transactions?orderId={orderId}`
3. `BottleTrackingService.getOrderTransactions()` queries by order ID
4. Transaction history displayed in reverse chronological order

### UC-6: Manual Bottle Issue (Admin)

| Field | Value |
|-------|-------|
| **ID** | UC-BT-06 |
| **Name** | Manual Bottle Issue |
| **Actor** | Admin / Support |
| **Preconditions** | — |
| **Postconditions** | BottleTransactionEntity created with action=ISSUED |
| **Trigger** | Admin issues bottles manually via admin panel |

**Flow:**
1. Admin navigates to admin panel
2. Admin enters customerId, orderId, bottleType, quantity
3. System calls `BottleTrackingService.recordIssue()`
4. Transaction recorded, ledger updated
5. Admin notified of success

## Sequence Diagram (Auto-Dispatch)

```
Chargebee                    bmjServer                    Database
    |                            |                            |
    |--- INVOICE_PAID webhook -->|                            |
    |                            |                            |
    |                     WebhookEventProcessor               |
    |                     .processInvoiceEvent()              |
    |                            |                            |
    |                     BottleTrackingService               |
    |                     .autoDispatchBottles()              |
    |                            |                            |
    |                     recordIssue()                       |
    |                            |------- INSERT TX --------->|
    |                            |                            |
    |                            |<--- transaction saved -----|
    |                            |                            |
    |<--- 200 OK ---------------|                            |
```

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/bottles/ledger` | Bearer Token | Get computed ledger for authenticated customer |
| GET | `/api/bottles/transactions` | Bearer Token | Get transaction history |
| GET | `/api/bottles/transactions?orderId={id}` | Bearer Token | Get order-specific transactions |
| POST | `/api/bottles/return` | Bearer Token | Record bottle return |
| POST | `/api/bottles/broken` | Bearer Token | Record broken/lost bottle |

## Data Model

### bottle_transactions Table

| Column | Type | Description |
|--------|------|-------------|
| id | BIGINT (PK, AUTO) | Primary key |
| order_id | VARCHAR(255) | Chargebee order ID |
| customer_id | VARCHAR(255) | Chargebee customer ID |
| bottle_type | VARCHAR(100) | e.g., glass_500ml |
| quantity | INT | Number of bottles |
| action | VARCHAR(20) | ISSUED / RETURNED / BROKEN |
| reference_id | VARCHAR(255) | Optional external reference |
| notes | TEXT | Optional notes |
| created_at | TIMESTAMP | Auto-set |
| updated_at | TIMESTAMP | Auto-updated |

**Indexes:** customer_id, order_id, action

### BottleLedgerEntry (Computed View)

| Field | Type | Description |
|-------|------|-------------|
| customerId | String | Chargebee customer ID |
| bottleType | String | Bottle type key |
| totalIssued | int | Sum of all ISSUED transactions |
| totalReturned | int | Sum of all RETURNED transactions |
| totalBroken | int | Sum of all BROKEN transactions |
| outstanding | int | totalIssued - totalReturned - totalBroken |
| lastTransactionAt | String | ISO timestamp of most recent transaction |

## Security

- All endpoints require `@PreAuthorize` with USER/MODERATOR/ADMIN roles
- Ledger and transactions are scoped to the authenticated customer via `SecurityContext`
- Admin endpoints for cross-customer queries (future)

## Error Handling

- Auto-dispatch failures are logged but never propagated (non-blocking)
- API errors return standard `{status, message, data}` wrapper
- 401 Unauthorized returned for expired/invalid tokens
- Flutter shows user-friendly error messages with retry capability

## Future Enhancements

1. **Bottle type detection from line items:** Parse chargebee item metadata for bottle type
2. **Delivery personnel UI:** Mobile interface for recording returns at pickup
3. **Admin dashboard:** Cross-customer ledger views, manual adjustments
4. **Bottle deposit billing:** Charge for unreturned bottles after threshold
5. **QR-code scanning:** Scan bottles for quick return/reconciliation
6. **Analytics:** Bottle loss rates, turnover by region, sustainability reporting
