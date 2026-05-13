# Webhook Reliability - BookMyJuice

**Version:** 2.0
**Last Updated:** 2026-05-08

---

## Overview

This document describes webhook processing reliability. Sections:
**Implemented** vs **Planned**.

---

## IMPLEMENTED - Idempotency Service

`IdempotencyService` uses DB unique constraints + in-memory cache for dedup.

### WebhookEvent Entity Fields
eventId, eventType, processingStatus (PROCESSING/COMPLETED/FAILED),
retryCount, errorMessage, processedAt, version

### IdempotencyService Methods
- startEventProcessing, markEventCompleted, markEventFailed, isEventProcessed
- getEventsNeedingRetry, retryEvent, cleanupExpiredEvents, getProcessingStats
- Max retries: 3. Cleanup: 4h interval, 24h TTL.

### WebhookEventProcessor
@Transactional methods: processCustomerEvent, processSubscriptionEvent,
processItemEvent, processItemPriceEvent, processInvoiceEvent, processPaymentEvent.

---

## PLANNED - Not Yet Implemented

| Feature | Description |
|---------|-------------|
| DLQ | Separate webhook_dlq table |
| Scheduled Retry | @Scheduled with exponential backoff |
| Cache Eviction Hooks | Evict Redis after webhook |
| Signature Verification | HMAC-SHA256 |
| Admin DLQ Endpoints | GET/POST management |
| Monitoring Alerts | DLQ count, latency, failure |

---

## Webhook Controllers

controllers/webhooks/: Customer, Subscription, Invoice, Payment, Item,
ItemPrice, Plan, Charge, Addon, AttachedItem, CreditNote, Order, Transaction.

---

## Testing

Duplicate COMPLETED/ PROCESSING: IMPLEMENTED
Retry < / >= max: IMPLEMENTED
Signature verify / Cache eviction: PLANNED
