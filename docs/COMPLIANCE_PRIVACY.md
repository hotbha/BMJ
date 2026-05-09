# Compliance & Privacy — BookMyJuice

**Document Version:** 1.0  
**Last Updated:** 2026-05-08

---

## 1. Data Classification

### Personally Identifiable Information (PII)

| Data Element | Location | Classification | Retention |
|-------------|----------|---------------|-----------|
| Email | BMJ users table, Chargebee customer | PII | Until right-to-erasure |
| Phone Number | BMJ users table, Chargebee customer | PII | Until right-to-erasure |
| Full Name | BMJ users table, Chargebee customer | PII | Until right-to-erasure |
| Address | BMJ user_addresses table, Chargebee customer | PII | Until right-to-erasure |
| Password Hash | BMJ users table | Sensitive Auth | Until account deletion |
| JWT Tokens | BMJ refresh_tokens table | Sensitive Auth | Until expiry or revocation |
| Payment Card Data | **NEVER stored in BMJ** (Chargebee only) | PCI DSS | N/A |
| Chargebee Customer ID | BMJ users table | Reference Identifier | Until right-to-erasure |
| Subscription IDs | BMJ subscriptions table | Reference Identifier | Until right-to-erasure |
| Invoice IDs | BMJ invoices table | Reference Identifier | Indefinite (legal requirement) |

### Data Ownership Boundaries

| Data | SSOT | BMJ Stores? |
|------|------|-------------|
| Billing Customer Record | Chargebee | Reference ID only |
| Payment Transactions | Chargebee | Reference cache |
| Invoices | Chargebee | Reference cache for display |
| Subscriptions | Chargebee | Reference cache for display |
| Order Records | Chargebee | Reference cache |
| Authentication Credentials | BMJ | Full ownership |
| Delivery Addresses | BMJ | Full ownership |
| Session Data | BMJ | Full ownership |
| Audit Logs | BMJ | Full ownership |
| Consent Records | BMJ | Full ownership |

---

## 2. Consent Tracking

### Consent Types

| Consent | Purpose | Legal Basis |
|---------|---------|-------------|
| `billing_processing` | Process billing data via Chargebee | Contractual necessity |
| `marketing_emails` | Send promotional emails | Explicit consent |
| `data_sharing` | Share anonymized data for analytics | Legitimate interest |
| `terms_accepted` | Accept terms of service | Contractual necessity |
| `privacy_policy_accepted` | Accept privacy policy | Legal obligation |

### Database Schema

```sql
CREATE TABLE consent_records (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    consent_type VARCHAR(50) NOT NULL,
    granted BOOLEAN NOT NULL,
    consent_version VARCHAR(20) NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    revoked_at TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_consent (user_id, consent_type)
);
```

---

## 3. Right-to-Erasure / Anonymization

### Process Flow

```
User requests deletion → bmjServer receives request
    ↓
1. Validate user identity
    ↓
2. Anonymize BMJ user record:
   - Set email to sha256(user_id)@anonymized.bookmyjuice.co.in
   - Clear phone number
   - Clear name, addresses
   - Set anonymized_at = NOW()
   - Disable login capability
    ↓
3. Chargebee boundary:
   - CANNOT delete Chargebee customer (legal/invoicing requirement)
   - DO record in user notes: "BMJ GDPR deletion requested [date]"
   - BMJ reference ID remains but PII is removed
    ↓
4. Audit trail:
   - Record deletion request in audit_log
   - Record Chargebee notification in audit_log
    ↓
5. Revoke all sessions:
   - Delete all refresh tokens
   - Invalidate all active JWT tokens
    ↓
6. Confirm to user
```

### Chargebee Data Handling

Since Chargebee is the SSOT for billing data:

- **We cannot delete** Chargebee customer records (invoices, subscriptions history are legal records)
- **We can request** Chargebee to anonymize customer PII (name, email, phone → "Deleted User")
- **BMJ must keep** `chargebee_customer_id` reference for tax/accounting reconciliation
- **No PII** should remain in BMJ's local copy after erasure

### API Endpoint

```
POST /api/v1/compliance/delete-account
Authorization: Bearer <token>
Body: {
  "reason": "User requested deletion",
  "confirm": true
}
Response: 200 { "message": "Account scheduled for deletion" }
```

---

## 4. Data Retention Policy

| Data Type | Retention Period | Rationale |
|-----------|-----------------|-----------|
| Active user accounts | Indefinite | Active service |
| Anonymized user records | Indefinite | Legal requirement (invoice records) |
| Audit logs | 3 years | Security compliance |
| Webhook events | 90 days | Operational debugging |
| Webhook DLQ | Until resolved + 90 days | Operational |
| Refresh tokens | Until expired/revoked | Session management |
| Consent records | Indefinite | Proof of consent |
| Anonymized records | Indefinite | Cannot be re-identified |

---

## 5. Security Logging

### Audit Log Schema

```sql
CREATE TABLE audit_log (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT,
    event_type VARCHAR(100) NOT NULL,
    event_detail TEXT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    severity ENUM('INFO', 'WARNING', 'CRITICAL') NOT NULL DEFAULT 'INFO',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user (user_id),
    INDEX idx_event (event_type),
    INDEX idx_created (created_at),
    INDEX idx_severity (severity)
);
```

### Events Logged

| Event Type | Severity | Details |
|-----------|----------|---------|
| `LOGIN_SUCCESS` | INFO | User logged in |
| `LOGIN_FAILURE` | WARNING | Failed login attempt |
| `TOKEN_REFRESH` | INFO | Access token refreshed |
| `LOGOUT` | INFO | User logged out |
| `LOGOUT_ALL` | WARNING | User revoked all sessions |
| `PASSWORD_CHANGE` | INFO | Password changed |
| `ACCOUNT_DELETION_REQUEST` | CRITICAL | Right-to-erasure requested |
| `ACCOUNT_ANONYMIZED` | CRITICAL | Account anonymized |
| `CONSENT_GRANTED` | INFO | User granted consent |
| `CONSENT_REVOKED` | INFO | User revoked consent |
| `DATA_EXPORT_REQUESTED` | INFO | User requested data export |
| `SUSPICIOUS_ACTIVITY` | CRITICAL | Security alert |
| `WEBHOOK_SIGNATURE_FAILURE` | WARNING | Invalid webhook signature |

---

## 6. Data Subject Access Request (DSAR)

### Endpoint

```
GET /api/v1/compliance/export-data
Authorization: Bearer <token>
Response: 200 {
  "user": { ... },
  "consent_records": [...],
  "anonymized_if_applicable": true,
  "data_categories": ["profile", "addresses", "consent", "audit_events"],
  "exported_at": "2026-05-08T10:00:00Z"
}
```

### Process

1. User requests data export via app
2. BMJ collects: user profile, addresses, consent records, audit log entries
3. BMJ queries Chargebee for: invoice list, subscription list (reference only)
4. Package all data as JSON
5. Return to user within 30 days (GDPR requirement)

---

## 7. Security Measures

| Measure | Implementation |
|---------|---------------|
| Transport Security | TLS 1.3 (production) |
| Password Storage | BCrypt (work factor 10) |
| JWT Signing | HS256 with 32+ char secret |
| Rate Limiting | 10/min for auth, 100/min general |
| Input Validation | Bean Validation, whitelist patterns |
| SQL Injection | Parameterized queries (JPA) |
| CORS | Restricted origins (production) |
| Webhook Verification | HMAC-SHA256 signatures |
| Session Revocation | Refresh token blacklist |
| Audit Logging | Immutable log entries |
| Secrets Management | Environment variables, not code |

---

## 8. Compliance References

| Regulation | Scope | Status |
|-----------|-------|--------|
| **GDPR** (EU) | User data protection for EU users | Implemented |
| **DPDP Act** (India) | Indian data protection law | Implemented |
| **PCI DSS** | Payment card data | Delegated to Chargebee |
| **IT Act 2000** (India) | Indian IT law compliance | Implemented |

---

**Document Maintained By:** Engineering Team  
**Last Review:** 2026-05-08  
**Next Review:** 2026-06-08
