# Webhook Reliability — BookMyJuice

**Document Version:** 1.0  
**Last Updated:** 2026-05-08

---

## Architecture

```
Chargebee Event ──► Signature Verification ──► Idempotency Check ──► Process ──► Success
                                                       │                        │
                                                       ▼                        ▼
                                                  Duplicate?              Failure ──► DLQ
                                                       │                        │
                                                       ▼                        ▼
                                                  Return 200 OK         Scheduled Retry
```

---

## 1. Webhook Signature Verification

All Chargebee webhooks are verified using HMAC-SHA256 before processing.

### Implementation

```java
public class WebhookSignatureService {
    public boolean verifySignature(String rawBody, String signatureHeader) {
        // Parse t=<timestamp>,v1=<hmac> from header
        // Compute HMAC-SHA256(timestamp + "." + rawBody, webhookSecret)
        // Compare with v1 value using constant-time comparison
    }
}
```

### Configuration

```properties
chargebee.webhook.secret=${CHARGEBEE_WEBHOOK_SECRET}
```

### Failure Handling

| Failure | Action |
|---------|--------|
| Missing signature header | Reject with 400 |
| Invalid signature | Reject with 401, log security alert |
| Expired timestamp (>5 min skew) | Reject with 403, log security alert |
| Parse error | Reject with 400 |

---

## 2. Idempotent Processing

Process each Chargebee event ID **exactly once**.

### Database Schema

```sql
CREATE TABLE webhook_events (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    event_id VARCHAR(100) NOT NULL UNIQUE,
    event_type VARCHAR(100) NOT NULL,
    status ENUM('PROCESSING', 'COMPLETED', 'FAILED') NOT NULL DEFAULT 'PROCESSING',
    payload JSON,
    error_message TEXT,
    attempts INT NOT NULL DEFAULT 1,
    max_attempts INT NOT NULL DEFAULT 5,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    INDEX idx_event_id (event_id),
    INDEX idx_status (status),
    INDEX idx_created (created_at)
);
```

### Processing Flow

1. Check if `event_id` exists in `webhook_events`
2. If exists and `COMPLETED` → Return 200 OK (idempotent)
3. If exists and `PROCESSING` → Return 409 Conflict (another worker is processing)
4. If exists and `FAILED` → Attempt retry if `attempts < max_attempts`
5. If not exists → INSERT with `PROCESSING` status, process event
6. On success → UPDATE status to `COMPLETED`
7. On failure → UPDATE status to `FAILED`, increment `attempts`

---

## 3. Dead Letter Queue (DLQ)

Events that fail after `max_attempts` (default: 5) are moved to the DLQ.

### Database Schema

```sql
CREATE TABLE webhook_dlq (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    event_id VARCHAR(100) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    payload JSON,
    error_message TEXT,
    last_error TEXT,
    failed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    max_attempts INT NOT NULL,
    attempts_made INT NOT NULL,
    resolved BOOLEAN NOT NULL DEFAULT FALSE,
    resolved_at TIMESTAMP NULL,
    resolution_notes TEXT,
    INDEX idx_unresolved (resolved, failed_at)
);
```

### DLQ Management

- Events in DLQ require manual intervention or scheduled retry
- Admin endpoint `POST /api/admin/webhooks/dlq/{id}/retry` to re-process
- Alerting when DLQ count > threshold
- Monitoring dashboard for DLQ health

---

## 4. Scheduled Retry Mechanism

```java
@Component
public class WebhookRetryService {
    @Scheduled(fixedDelay = 60000) // Every 60 seconds
    public void retryFailedEvents() {
        // Query webhook_events where status = FAILED AND attempts < max_attempts
        // Exponential backoff: 2^attempts minutes
        // Re-process each eligible event
    }
}
```

### Backoff Strategy

| Attempt | Delay Before Retry |
|---------|-------------------|
| 1 | Immediate (via retry header) |
| 2 | 2 minutes |
| 3 | 4 minutes |
| 4 | 8 minutes |
| 5 | 16 minutes → DLQ |

### Chargebee Retry Support

Chargebee will retry webhooks that return non-2xx responses. Configure Chargebee to:
- Retry up to 3 times
- Use exponential backoff (5s, 30s, 5min)
- Send webhook failure notifications to ops email

---

## 5. Transactional Handlers

All webhook processing is wrapped in `@Transactional`:

```java
@Transactional
public ResponseEntity<String> processSubscriptionEvent(Event event) {
    try {
        // Database operations
        subscriptionService.saveOrUpdate(...);
        invoiceService.update(...);
        cacheService.evictSubscriptions(...);
        
        idempotencyService.markCompleted(event.id());
        return ResponseEntity.ok("Processed");
    } catch (Exception e) {
        idempotencyService.markFailed(event.id(), e.getMessage());
        return ResponseEntity.status(500).body("Failed");
    }
}
```

### Cache Eviction Hooks

After successful processing, relevant cache entries are evicted:

| Event Type | Cache Keys to Evict |
|------------|---------------------|
| `subscription.created` | `subscriptions:*`, `customer:${customerId}:subscriptions` |
| `subscription.updated` | `subscriptions:*`, `customer:${customerId}:subscriptions` |
| `subscription.cancelled` | `subscriptions:*`, `customer:${customerId}:subscriptions` |
| `invoice.created` | `invoices:*`, `customer:${customerId}:invoices` |
| `invoice.paid` | `invoices:*`, `customer:${customerId}:invoices` |
| `item.created` | `items:*`, `products:*` |
| `item.updated` | `items:*`, `products:*` |
| `item_price.created` | `prices:*`, `products:*` |
| `plan.created` | `plans:*` |
| `plan.updated` | `plans:*` |

---

## 6. Error Recording

```java
public class IdempotencyService {
    public void markEventFailed(String eventId, String errorMessage) {
        webhookEventRepository.updateStatus(eventId, EventStatus.FAILED, errorMessage);
    }
}
```

All errors are recorded with:
- Event ID
- Event type
- Timestamp
- Full error stack trace
- Payload snapshot

---

## 7. Operational Documentation

### Monitoring

| Metric | Alert Threshold |
|--------|----------------|
| DLQ count > 0 | Warning |
| Processing latency > 30s | Warning |
| Signature verification failures > 5/min | Critical |
| Retry attempts > 10/min | Warning |

### Chargebee Webhook Configuration

In Chargebee admin:
1. Navigate to Settings → Webhooks
2. Set endpoint: `https://api.bookmyjuice.co.in/api/webhooks/chargebee`
3. Enable all relevant events
4. Set retry policy: 3 retries with exponential backoff
5. Send failure notifications to `ops@bookmyjuice.co.in`
6. Test with Chargebee's webhook test tool

### Manual Operations

```bash
# List DLQ entries
GET /api/admin/webhooks/dlq

# Retry a specific DLQ entry
POST /api/admin/webhooks/dlq/{id}/retry

# Retry all DLQ entries
POST /api/admin/webhooks/dlq/retry-all

# Re-process a specific event by event ID
POST /api/admin/webhooks/reprocess/{eventId}
```

---

## 8. Testing

| Test Case | Type | Expected |
|-----------|------|----------|
| Valid signature | Unit | Processing proceeds |
| Invalid signature | Unit | 401 rejected |
| Expired timestamp | Unit | 403 rejected |
| Duplicate event (COMPLETED) | Integration | 200 OK, no processing |
| Duplicate event (PROCESSING) | Integration | 409 Conflict |
| Failed event retry (attempt < max) | Integration | Retry executed |
| Failed event retry (attempt >= max) | Integration | Moved to DLQ |
| Webhook processing error | Integration | Rollback + error recorded |
| Cache eviction on update | Integration | Cache cleared for keys |

---

**Document Maintained By:** Engineering Team  
**Last Review:** 2026-05-08  
**Next Review:** 2026-06-08
