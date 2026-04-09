# BookMyJuice AI Coding Instructions

A cold-pressed juice subscription + on-demand ordering platform with Flutter frontend and Spring Boot backend, integrated with Chargebee for billing.

## Project Structure

**Frontend:** `lush/` (Flutter)
- **State Management:** BLoC pattern with `flutter_bloc` (AuthBloc, CartBloc, ProductsBloc, SubscriptionBloc, UserBloc)
- **Repository Layer:** Service-based (UserRepository, CartRepository, ItemService)
- **API Client:** HTTP package with compile-time defines (API_BASE_URL)
- **Local Storage:** SharedPreferences for cart/auth state

**Backend:** `bmjServer/` (Spring Boot 3.1, Java 17, Maven)
- **Controllers:** REST endpoints split by domain (Auth, Subscription, Order, Invoice, Pricing, webhooks)
- **Services:** Business logic layer (SubscriptionService, OrderService, InvoiceService, etc.)
- **Repositories:** JPA Spring Data repositories for DB access
- **Chargebee Integration:** Webhook handlers, sync service (batch processing), customer/subscription sync
- **Security:** JWT tokens (JJWT library), BCrypt password hashing, role-based access (User/Admin)

## Key Build & Test Commands

**Frontend (Flutter):**
```bash
cd lush
flutter run --dart-define=API_BASE_URL=http://localhost:8080
flutter test --dart-define=API_BASE_URL=http://localhost:8080
flutter test integration_test --dart-define=E2E=true --dart-define=E2E_USER=<phone> --dart-define=E2E_PASS=<pass>
```

**Backend (Maven):**
```bash
cd bmjServer
./mvnw clean verify              # Full build + tests
./mvnw test                      # Tests only
```

**VS Code Tasks:** Use built-in Flutter/backend tasks for building.

## Critical Patterns & Conventions

### Flutter Architecture
- **BLoC Events/States:** Event classes trigger state changes; states include loading/success/error variants
- **Repositories handle API calls** via HTTP; services compose repository results
- **Cart persistence:** LocalStorage via SharedPreferences in CartRepository
- **API_BASE_URL:** Always passed as compile-time define `--dart-define=API_BASE_URL=...`; defaults to localhost:8080
- **Integration tests gated:** E2E tests only run if `--dart-define=E2E=true` flag provided

### Spring Boot Architecture
- **DTO/Entity separation:** Request/Response DTOs in `payload/`, JPA entities in `models/entities/`
- **Service layer orchestrates:** Controllers delegate to services; services call repositories + Chargebee APIs
- **Webhook deduplication:** IdempotencyService + event versioning to prevent duplicate processing
- **Chargebee sync:** ChargebeeSyncService batch-syncs customer/subscription/order data on startup (configurable)
- **JWT config:** Token secret in `bezkoder.app.jwtSecret` (environment variable required)
- **Rate limiting:** RateLimiterService with bucket4j library; applied to auth endpoints
- **Transaction logging:** WebhookEventProcessor routes events to domain-specific handlers (e.g., CustomerWebhookController)

### Database Schema
- **Core entities:** Customer, Subscription, Order, Invoice, Item, ItemPrice, Payment
- **Chargebee-synced:** Plans, Addons, Charges, CreditNotes, AttachedItems
- **Address entities:** BillingAddress, ShippingAddress linked to customers
- **MySQL 8.x:** Hibernate auto-update DDL (production uses managed schema)

### Chargebee Integration
- **Webhooks:** Separate controller per resource type (Customer, Subscription, Invoice, Payment, etc.)
- **Sync mechanism:** Batch-fetches from Chargebee API; configurable pool size (default 3 threads, 50-item batches)
- **Webhook tunneling:** Dev/localhost webhooks must use ngrok/tunnel; test site: `https://bookmyjuice-test.chargebee.com`
- **Subscription types:** Test site uses "test" key; production uses production key (env var)

### Environment Configuration
- **Dev/Prod profiles:** `application.properties` (default), `application-dev.properties`, `application-prod.properties`
- **Runtime overrides:** DB_USERNAME, DB_PASSWORD, JWT_SECRET, CHARGEBEE_API_KEY, MAIL_* via environment
- **Frontend:** API_BASE_URL via `--dart-define` (required for multi-backend testing)

## Common Developer Workflows

1. **Local full-stack dev:** Run backend on `:8080`, then `flutter run --dart-define=API_BASE_URL=http://localhost:8080`
2. **Webhook testing:** Use ngrok tunnel pointing to local backend; configure tunnel URL in Chargebee webhook settings
3. **E2E testing:** Provide E2E flag + test credentials; validates auth, pricing, checkout, subscriptions
4. **New endpoint:** Add Controller, Service, Repository; follow DTOs in payload/ for req/resp
5. **New webhook:** Create controller in webhooks/, add handler method, register in WebhookEventProcessor
6. **Building APK:** `flutter build apk --dart-define=API_BASE_URL=<prod-url>`

## Important Notes
- **Chargebee is production billing system:** Test credentials active; validate webhook logic before enabling production webhooks
- **Flutter compile-time defines:** Cannot be changed at runtime; must rebuild for different backends
- **Rate limiting:** Active on auth endpoints (RateLimiterService); tuning via bucket4j config if needed
- **Lombok annotations:** Used extensively in backend entities (@Data, @Builder); ensure lombok processor is installed
