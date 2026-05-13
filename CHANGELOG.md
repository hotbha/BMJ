# Changelog

All notable changes to BookMyJuice (BMJ).
Based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), [SemVer](https://semver.org/).

---

## [Unreleased]

### Planned
- Redis caching (RedisConfig, CacheService, CacheWarmupService)
- FCM server push for notifications
- DLQ for exhausted webhook retries
- Scheduled retry with exponential backoff
- Chargebee webhook signature verification
- Post-MVP: multiple addresses, loyalty, offline

---

## [0.1.0] - 2026-05-13 - Current Sprint

### Added
- **Delivery Domain**: ServiceAreaEntity, delivery fee calc, address capture in signup
- **Rate Limiting**: Bucket4j RateLimitService + RateLimitingFilter for OTP
- **Profile Config**: @Profile("dev") on test controllers
- **Sensitive Data**: .env for all secrets via spring-dotenv
- **FCM Persistence**: fcm_token + updated_at on users table
- **Push Foundation**: Flutter FirebaseNotificationService, backend FCM token endpoint
- **Webhook Idempotency**: IdempotencyService with DB dedup, retry (max 3), cleanup (4h, 24h TTL)
- **WebhookEvent Entity**: eventId, eventType, processingStatus, retryCount, errorMessage, processedAt
- **WebhookEventProcessor**: @Transactional handlers for all Chargebee events
- **Delivery Calculation**: server-side delivery_fee with free threshold

### Changed
- BRD v2.1: Delivery Domain, NFR-011 to NFR-015, Usability renumbering
- WEBHOOK_RELIABILITY.md: Implemented vs Planned sections
- CACHING_STRATEGY.md: Implemented vs Planned sections

### Fixed
- Webhook duplicates: COMPLETED returns 200, PROCESSING skips

---

## [0.0.1] - 2026-04-11 - Foundation

### Added
- Unified signup (Email, Phone, Google), JWT auth, guest cart merge
- Product catalog, single-mode cart, server-side pricing
- Chargebee checkout via Hosted Pages, webhook processing
- Subscription management (pause/resume/cancel), day-wise scheduling
- Order history with pagination, invoice URLs
- Local push notifications via flutter_local_notifications
- Spring caching annotations, MySQL schema, Flyway migrations
- CI/CD pipeline (GitHub Actions)

---

[0.1.0]: https://github.com/hotbha/BMJ/compare/v0.0.1...v0.1.0
[0.0.1]: https://github.com/hotbha/BMJ/releases/tag/v0.0.1
