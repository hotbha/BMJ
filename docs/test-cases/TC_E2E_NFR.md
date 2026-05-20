# Non-Functional Requirements (NFR) — End-to-End (E2E) Black Box Test Cases

> **Document Version:** 1.0  
> **Last Updated:** 2026-05-18  
> **Module:** NFR (Cross-Cutting)  
> **Type:** E2E (Black Box)  
> **Automation Strategy:** Automated (k6 + Lighthouse + custom scripts)  

---

## Prerequisites

Refer to **`TEST_PREREQUISITES.md`** for full environment setup. Key items for this module:

| # | Pre-Requisite | Status |
|---|---------------|--------|
| P-01 | bmjServer deployed to staging with public URL | 🔴 Must Do |
| P-05 | k6 installed on test runner machine | 🔴 Must Do |
| P-06 | Lighthouse CLI or PageSpeed Insights access | 🔴 Must Do |
| P-07 | Postman / Newman installed for API collection | 🔴 Must Do |
| P-10 | Webhook.site listener or ngrok tunnel for webhook tests | 🔴 Must Do |
| P-11 | JWT secret key and test tokens for security tests | 🔴 Must Do |
| F-01 | Flutter APK built with API_BASE_URL=staging | 🔴 Must Do |

**Linked NFRs:** NFR-001, NFR-002, NFR-004, NFR-007, NFR-008, NFR-010, NFR-011  
**Linked SEC:** TC-SEC-001 through TC-SEC-007 (extended)  
**Security Note:** This module extends existing TC-SEC-001 to 007 with E2E integration coverage.

---

## Test Cases

---

### TC-E2E-NFR-001: API response time under 2 seconds for product listing

| Field | Value |
|-------|-------|
| **ID** | TC-E2E-NFR-001 |
| **Module** | NFR (Performance) |
| **Type** | E2E (Black Box) |
| **Priority** | P1 — High |
| **Severity** | S1 — Major |
| **Automation Status** | Automated (k6) |
| **Linked NFR** | NFR-001 |

**Preconditions:**
- [ ] bmjServer deployed and accessible from test runner
- [ ] Product catalog has at least 50 products loaded
- [ ] k6 script configured with test endpoint
- [ ] Test runner has stable network connection to staging server

**Test Steps:**
1. Execute k6 load test: `k6 run --vus 10 --duration 30s nfr-product-listing.js`
2. The script sends GET /api/v1/products with no filters
3. Collect p95 response time from k6 output
4. Record the p95 value
5. Repeat test 3 times at different times of day
6. Calculate average p95 across all runs

**Expected Results:**
1. k6 executes 10 virtual users over 30 seconds
2. All requests return HTTP 200
3. p95 response time is under 2000ms (2 seconds)
4. No request timeout errors
5. Consistent performance across multiple runs
6. Average p95 across runs < 2000ms

**Test Data:**
- Endpoint: GET /api/v1/products
- k6 VUs: 10, Duration: 30s
- Threshold: http_req_duration[95] < 2000
- Acceptable threshold: p95 < 2000ms

---
### TC-E2E-NFR-002: API response time under 2 seconds for login

| Field | Value |
|-------|-------|
| **ID** | TC-E2E-NFR-002 |
| **Module** | NFR (Performance) |
| **Type** | E2E (Black Box) |
| **Priority** | P1 — High |
| **Severity** | S1 — Major |
| **Automation Status** | Automated (k6) |
| **Linked NFR** | NFR-001 |

**Preconditions:**
- [ ] bmjServer deployed and accessible
- [ ] OTP service is mocked or configured to accept test OTP
- [ ] k6 script configured with login flow (request OTP + verify OTP)
- [ ] Test runner has stable network connection

**Test Steps:**
1. Execute k6 test: k6 run --vus 5 --duration 30s nfr-login.js
2. Script sends POST /api/v1/auth/request-otp with phone number
3. Script sends POST /api/v1/auth/verify-otp with OTP code
4. Collect p95 response time for verify-otp endpoint
5. Repeat 3 times at different times of day
6. Calculate average p95

**Expected Results:**
1. k6 executes 5 VUs over 30 seconds
2. All request-otp calls return HTTP 200
3. All verify-otp calls return HTTP 200 with JWT token
4. p95 for verify-otp < 2000ms
5. Consistent performance across runs
6. Average p95 < 2000ms

**Test Data:**
- Endpoints: POST /api/v1/auth/request-otp, POST /api/v1/auth/verify-otp
- k6 VUs: 5, Duration: 30s
- Phone: 9999999901 through 9999999905 (one per VU)
- OTP: 999999 (test OTP for staging)

---
### TC-E2E-NFR-003: App cold start under 3 seconds

| Field | Value |
|-------|-------|
| **ID** | TC-E2E-NFR-003 |
| **Module** | NFR (Performance) |
| **Type** | E2E (Black Box) |
| **Priority** | P1 — High |
| **Severity** | S1 — Major |
| **Automation Status** | Manual (Lighthouse / Android profiler) |
| **Linked NFR** | NFR-002 |

**Preconditions:**
- [ ] Flutter APK built in release mode (not debug)
- [ ] App installed on physical device (not emulator)
- [ ] App not running in background (force stop before test)
- [ ] Device running Android 12+ with consistent performance
- [ ] USB debugging enabled for activity manager timing

**Test Steps:**
1. Force stop the BookMyJuice app: adb shell am force-stop com.bookmyjuice.app
2. Clear any cached data: adb shell pm clear com.bookmyjuice.app (optional for consistent cold start)
3. Launch the app: adb shell am start -W com.bookmyjuice.app/.MainActivity
4. Record the TotalTime value from adb output
5. Note the time from tap to first interactive frame (splash screen loads)
6. Repeat steps 1-5 for 5 iterations
7. Calculate average cold start time

**Expected Results:**
1-2. App process cleared - no cached state
3. adb returns TotalTime, WaitTime, ThisTime metrics
4. TotalTime < 3000ms (3 seconds)
5. Splash screen appears within 2 seconds
6. All 5 iterations show TotalTime < 3000ms
7. Average cold start time < 2500ms (with buffer)

**Test Data:**
- App package: com.bookmyjuice.app
- Activity: .MainActivity
- adb command: adb shell am start -W com.bookmyjuice.app/.MainActivity
- Metric: TotalTime (includes process creation + activity launch)

---
### TC-E2E-NFR-004: All API calls use HTTPS (verify no HTTP calls)

| Field | Value |
|-------|-------|
| **ID** | TC-E2E-NFR-004 |
| **Module** | NFR (Security) |
| **Type** | E2E (Black Box) |
| **Priority** | P0 — Critical |
| **Severity** | S0 — Blocker |
| **Automation Status** | Automated (mitmproxy / Charles) |
| **Linked NFR** | NFR-004 |

**Preconditions:**
- [ ] mitmproxy or Charles Proxy installed on test machine
- [ ] Device configured to route traffic through proxy
- [ ] SSL certificate installed on device for proxy inspection
- [ ] App APK installed on device
- [ ] All app features ready for test (login, catalog, checkout)

**Test Steps:**
1. Start mitmproxy on test machine: mitmweb --listen-port 8080
2. Configure Android device WiFi proxy to point to test machine IP:8080
3. Install mitmproxy CA certificate on device
4. Launch the BookMyJuice app
5. Execute a full user journey:
   - Log in via OTP
   - Browse product catalog
   - Add items to cart
   - Initiate checkout
   - View profile
6. In mitmproxy, filter all captured requests by URL
7. Check for any HTTP (non-TLS) requests to the API domain
8. Verify all API calls use HTTPS with valid TLS certificate

**Expected Results:**
1-3. Proxy set up and traffic intercepting
4-5. App functions normally through proxy
6. Captured requests show API domain requests
7. Zero HTTP requests to api.bookmyjuice.co.in or staging API domain
8. All API calls use https:// - TLS handshake completes without errors

**Test Data:**
- Proxy tool: mitmproxy / Charles Proxy v5
- API domain: .*bookmyjuice.* (staging API endpoint)
- Filter: !(https://.*bookmyjuice.*) to detect non-HTTPS calls
- Expected: 0 results for HTTP filter

---
### TC-E2E-NFR-005: OTP endpoint rate limited - 10th+ request in 5 min blocked

| Field | Value |
|-------|-------|
| **ID** | TC-E2E-NFR-005 |
| **Module** | NFR (Rate Limiting / Security) |
| **Type** | E2E (Black Box) |
| **Priority** | P1 — High |
| **Severity** | S1 — Major |
| **Automation Status** | Automated (k6 or curl script) |
| **Linked NFR** | NFR-011 |

**Preconditions:**
- [ ] bmjServer deployed with rate limiting configured
- [ ] Rate limit: 10 OTP requests per 5 minutes per IP
- [ ] Test runner has unique IP (not behind shared NAT with other tests)
- [ ] OTP endpoint is POST /api/v1/auth/request-otp
- [ ] Phone number is a valid test number (9999999901)

**Test Steps:**
1. Send POST /api/v1/auth/request-otp with phone=9999999901
2. Verify HTTP 200 response
3. Repeat steps 1-2 for 9 more times (total 10 requests)
4. Send the 11th POST /api/v1/auth/request-otp request (within same 5-minute window)
5. Observe HTTP status code and response body
6. Check response headers for rate limit information

**Expected Results:**
1-2. First request succeeds - HTTP 200, OTP sent/simulated
3. Requests 2-10 succeed - HTTP 200
4-5. 11th request returns HTTP 429 Too Many Requests
6. Response body contains error message: Rate limit exceeded. Try again in X seconds.
6. Response headers include: X-RateLimit-Limit, X-RateLimit-Remaining: 0, Retry-After

**Test Data:**
- Endpoint: POST /api/v1/auth/request-otp
- Phone: 9999999901
- Request body: {"phone": "9999999901"}
- Rate limit: 10 requests per 5 minutes
- Expected status on 11th request: 429

---
### TC-E2E-NFR-006: OTP rate limit resets after 5 minutes

| Field | Value |
|-------|-------|
| **ID** | TC-E2E-NFR-006 |
| **Module** | NFR (Rate Limiting) |
| **Type** | E2E (Black Box) |
| **Priority** | P2 — Medium |
| **Severity** | S2 — Minor |
| **Automation Status** | Automated (curl script with timer) |
| **Linked NFR** | NFR-011 |

**Preconditions:**
- [ ] Rate limit bucket is empty (no prior OTP requests in last 5 min)
- [ ] Test runner has unique IP
- [ ] Server clock and test clock are synchronized

**Test Steps:**
1. Send 10 OTP requests in quick succession (use script with 100ms delay)
2. Verify 11th request returns HTTP 429
3. Note the Retry-After header value
4. Wait exactly 5 minutes from the first request (or use Retry-After value)
5. Send a new OTP request after the wait period
6. Observe HTTP status code

**Expected Results:**
1-2. Rate limit triggered at 11th request - HTTP 429
3. Retry-After header indicates 300 seconds (5 minutes)
4. Timer expires after 5 minutes
5-6. New request succeeds - HTTP 200, OTP sent/simulated

**Test Data:**
- Endpoint: POST /api/v1/auth/request-otp
- Phone: 9999999902
- Wait time: 300 seconds (5 minutes) or value from Retry-After
- Expected: rate limit counter resets after window expires

---
### TC-E2E-NFR-007: Login endpoint rate limited (multiple failed attempts)

| Field | Value |
|-------|-------|
| **ID** | TC-E2E-NFR-007 |
| **Module** | NFR (Rate Limiting / Security) |
| **Type** | E2E (Black Box) |
| **Priority** | P1 — High |
| **Severity** | S1 — Major |
| **Automation Status** | Automated (curl script) |
| **Linked NFR** | NFR-011 |

**Preconditions:**
- [ ] bmjServer deployed with rate limiting on verify-otp endpoint
- [ ] Rate limit: N failed attempts per X minutes
- [ ] Test runner has unique IP
- [ ] Valid phone number for testing: 9999999903

**Test Steps:**
1. Request OTP: POST /api/v1/auth/request-otp with phone 9999999903
2. Submit wrong OTP: POST /api/v1/auth/verify-otp with otp=000000
3. Verify HTTP 400 or 401 with invalid OTP error
4. Repeat step 2 with wrong OTP for specified number of allowed attempts - 1
5. Submit one more wrong OTP attempt
6. Observe HTTP status code
7. Submit correct OTP to verify if lockout is per-IP or per-phone

**Expected Results:**
1. OTP request succeeds - HTTP 200
2-3. Invalid OTP returns HTTP 400/401 with error: Invalid or expired OTP
4. Failed attempts count increments
5-6. After N failed attempts, verify-otp returns HTTP 429 Too Many Requests
7. Even correct OTP returns 429 while rate limited (or OTP marked as used)

**Test Data:**
- Endpoint: POST /api/v1/auth/verify-otp
- Phone: 9999999903
- Wrong OTP: 000000
- Correct OTP: 999999 (test OTP)
- Rate limit: e.g., 5 failed attempts per 5 minutes

---
### TC-E2E-NFR-008: Invalid webhook signature → 401

| Field | Value |
|-------|-------|
| **ID** | TC-E2E-NFR-008 |
| **Module** | NFR (Webhook / Security) |
| **Type** | E2E (Black Box) |
| **Priority** | P0 — Critical |
| **Severity** | S0 — Blocker |
| **Automation Status** | Automated (curl / Postman) |
| **Linked NFR** | NFR-007 |

**Preconditions:**
- [ ] bmjServer webhook endpoint deployed: POST /api/v1/webhooks/chargebee
- [ ] Webhook secret key known from staging config
- [ ] Webhook payload template available (e.g., payment_succeeded.json)
- [ ] curl / Postman can POST to staging server

**Test Steps:**
1. Construct a valid Chargebee webhook payload (e.g., payment_succeeded)
2. Do NOT include any webhook signature in headers
3. Send POST request to /api/v1/webhooks/chargebee with raw JSON body
4. Observe HTTP status code and response body
5. Repeat with an invalid/malformed signature header
6. Try X-Chargebee-Signature: invalid_signature_value
7. Observe HTTP status code and response body

**Expected Results:**
1-2. Payload ready but no signature
3-4. Request with no signature returns HTTP 401 Unauthorized
4. Response body: {"error": "Invalid webhook signature"} or similar
5-6. Request with malformed/invalid signature header
7. Also returns HTTP 401 with signature validation error

**Test Data:**
- Endpoint: POST /api/v1/webhooks/chargebee
- Headers: Content-Type: application/json
- Invalid headers: X-Chargebee-Signature: invalid, or missing entirely
- Payload: sample Chargebee webhook event (payment_succeeded)
- Expected: HTTP 401 for both missing and invalid signatures

---
### TC-E2E-NFR-009: Valid webhook signature → accepted

| Field | Value |
|-------|-------|
| **ID** | TC-E2E-NFR-009 |
| **Module** | NFR (Webhook) |
| **Type** | E2E (Black Box) |
| **Priority** | P0 — Critical |
| **Severity** | S0 — Blocker |
| **Automation Status** | Automated (Python script + webhook secret) |
| **Linked NFR** | NFR-007 |

**Preconditions:**
- [ ] bmjServer webhook endpoint deployed: POST /api/v1/webhooks/chargebee
- [ ] Webhook signing secret available (from staging .env)
- [ ] HMAC-SHA256 signature generation script ready
- [ ] Valid Chargebee webhook sample payload available

**Test Steps:**
1. Load a valid Chargebee webhook payload (e.g., payment_succeeded.json)
2. Compute HMAC-SHA256 signature using webhook secret
3. Generate signature header as base64(HMAC-SHA256(secret, payload))
4. Send POST to /api/v1/webhooks/chargebee with:
   - Header: X-Chargebee-Signature: computed_signature
   - Header: Content-Type: application/json
   - Body: raw JSON payload
5. Observe HTTP status code
6. Check response body for success confirmation
7. Verify webhook was processed by checking DB (e.g., subscription status updated)

**Expected Results:**
1-3. Signature computed correctly per Chargebee HMAC specification
4. POST request sent to webhook endpoint
5. HTTP 200 OK - webhook accepted
6. Response body: {"status": "ok"} or similar success message
7. Backend processes webhook idempotently - DB updated accordingly

**Test Data:**
- Endpoint: POST /api/v1/webhooks/chargebee
- Headers: X-Chargebee-Signature, Content-Type: application/json
- Payload: sample Chargebee event with known content
- Signature algorithm: HMAC-SHA256, base64-encoded
- Expected: HTTP 200, webhook processed successfully

---
### TC-E2E-NFR-010: Webhook deduplication - same event.id processed once

| Field | Value |
|-------|-------|
| **ID** | TC-E2E-NFR-010 |
| **Module** | NFR (Webhook) |
| **Type** | E2E (Black Box) |
| **Priority** | P1 — High |
| **Severity** | S1 — Major |
| **Automation Status** | Automated (Python script) |
| **Linked NFR** | NFR-010 |

**Preconditions:**
- [ ] bmjServer deployed with idempotent webhook processing
- [ ] Webhook secret available for signature generation
- [ ] Chargebee webhook payload with unique event.id known (e.g., ev_12345)
- [ ] No prior processing of event ev_12345 in DB

**Test Steps:**
1. Generate valid HMAC-SHA256 signature for a webhook payload
2. Send first POST to /api/v1/webhooks/chargebee with the payload
3. Verify HTTP 200 - webhook accepted and processed
4. Immediately send second POST with identical payload (same event.id)
5. Observe HTTP status code and response body
6. Check DB to verify the event was processed only once
7. Check server logs for deduplication message

**Expected Results:**
1-3. First request: HTTP 200, webhook processed - DB updated
4-5. Second request (same event.id): HTTP 200 (not 4xx/5xx)
5. Response body includes: {"status": "ok", "duplicate": true} or similar flag
6. DB shows event processed exactly once (subscription updated only once)
7. Server logs: Skipping duplicate webhook event: ev_12345

**Test Data:**
- Endpoint: POST /api/v1/webhooks/chargebee
- Payload: event with id=ev_12345 (e.g., payment_success)
- DB table: webhook_events or similar dedup log
- Expected: HTTP 200 for both calls, but only one DB state change

---
### TC-E2E-NFR-011: API returns 401 for unauthenticated protected endpoints

| Field | Value |
|-------|-------|
| **ID** | TC-E2E-NFR-011 |
| **Module** | NFR (Security) |
| **Type** | E2E (Black Box) |
| **Priority** | P0 — Critical |
| **Severity** | S0 — Blocker |
| **Automation Status** | Automated (Postman / curl) |
| **Linked NFR** | NFR-004 |

**Preconditions:**
- [ ] bmjServer deployed and accessible
- [ ] List of protected endpoints known (e.g., /users/me, /subscriptions, /orders)
- [ ] No valid JWT token available for request

**Test Steps:**
1. Send GET /api/v1/users/me without any Authorization header
2. Observe HTTP status code
3. Send GET /api/v1/subscriptions without any Authorization header
4. Observe HTTP status code
5. Send GET /api/v1/orders without any Authorization header
6. Observe HTTP status code
7. Send POST /api/v1/cart/add with session-only (no JWT)
8. Observe HTTP status code
9. Repeat with malformed Authorization: Bearer invalid_token
10. Check response body for 401/error structure

**Expected Results:**
1-2. GET /users/me returns HTTP 401 Unauthorized
3-4. GET /subscriptions returns HTTP 401 Unauthorized
5-6. GET /orders returns HTTP 401 Unauthorized
7-8. POST /cart/add may work (guest cart) or return 401 depending on implementation
9-10. Malformed/invalid token also returns HTTP 401, not 5xx
10. Response body contains consistent error format: {"error": "Unauthorized", "message": "..."}

**Test Data:**
- Endpoints: GET /api/v1/users/me, GET /api/v1/subscriptions, GET /api/v1/orders
- Auth header: missing, empty, malformed (Bearer invalid)
- Expected status: 401 Unauthorized

---
### TC-E2E-NFR-012: JWT with wrong secret → rejected

| Field | Value |
|-------|-------|
| **ID** | TC-E2E-NFR-012 |
| **Module** | NFR (Security) |
| **Type** | E2E (Black Box) |
| **Priority** | P1 — High |
| **Severity** | S1 — Major |
| **Automation Status** | Automated (Postman / curl) |
| **Linked NFR** | NFR-004 |

**Preconditions:**
- [ ] bmjServer deployed with JWT secret configured in .env
- [ ] Valid JWT token for TA-04 available (test token)
- [ ] Python/JWT library available to generate tampered token

**Test Steps:**
1. Decode the valid JWT token for TA-04 (extract header and payload)
2. Generate a new JWT with same header and payload but signed with a different secret
3. Send GET /api/v1/users/me with Authorization: Bearer tampered_token
4. Observe HTTP status code and response body
5. Send the tampered token to other protected endpoints
6. Verify consistent rejection

**Expected Results:**
1. Valid JWT decoded - header.alg = HS256
2. Tampered token generated with wrong secret
3-4. Request returns HTTP 401 Unauthorized
4. Response: {"error": "Invalid or expired token"} or similar
5-6. All protected endpoints reject tampered token with 401

**Test Data:**
- Valid token: JWT for TA-04 signed with correct secret
- Tampered token: same header + payload, signed with wrong-secret-123
- Tool: jwt.io or python PyJWT library
- Expected: HTTP 401 for tampered token

---
### TC-E2E-NFR-013: Expired JWT token → rejected

| Field | Value |
|-------|-------|
| **ID** | TC-E2E-NFR-013 |
| **Module** | NFR (Security) |
| **Type** | E2E (Black Box) |
| **Priority** | P1 — High |
| **Severity** | S1 — Major |
| **Automation Status** | Automated (Python JWT + curl) |
| **Linked NFR** | NFR-004 |

**Preconditions:**
- [ ] bmjServer deployed with JWT expiry validation
- [ ] JWT secret known for test token generation
- [ ] Python PyJWT library available

**Test Steps:**
1. Generate a JWT token using PyJWT with exp claim set to past timestamp
   jwt.encode({"sub": "TA-04", "exp": datetime.utcnow() - timedelta(hours=1)}, secret, algorithm="HS256")
2. Send GET /api/v1/users/me with Authorization: Bearer expired_token
3. Observe HTTP status code and response body
4. Generate JWT with exp in future but other required claims missing
5. Send to protected endpoint - observe response

**Expected Results:**
1. Expired JWT generated with past exp timestamp
2-3. Request returns HTTP 401 Unauthorized
3. Response: {"error": "Token has expired"} or similar
4-5. Invalid claims also return HTTP 401 with appropriate error

**Test Data:**
- Secret: staging JWT secret from .env
- Expired token: exp = 1 hour in the past
- Endpoint: GET /api/v1/users/me
- Expected: HTTP 401 with token expiration error

---
### TC-E2E-NFR-014: BCrypt password hashing (verify stored hash is BCrypt)

| Field | Value |
|-------|-------|
| **ID** | TC-E2E-NFR-014 |
| **Module** | NFR (Security) |
| **Type** | E2E (Black Box) |
| **Priority** | P1 — High |
| **Severity** | S1 — Major |
| **Automation Status** | Automated (DB query + regex check) |
| **Linked NFR** | NFR-004 |

**Preconditions:**
- [ ] Database access to production/staging users table
- [ ] Read-only query access allowed
- [ ] Password field stored on user records (or external auth table)

**Test Steps:**
1. Query users table: SELECT password_hash FROM users LIMIT 10;
2. For each password_hash returned, check format:
   - Verify it starts with $2b$ or $2a$ (BCrypt prefix)
   - Verify minimum length of 60 characters
   - Verify format: $2b$10$<22-char-salt><31-char-hash>
3. Run regex: ^\$2[ab]\$\d{2}\$[A-Za-z0-9./]{53}$
4. If external auth is used (Auth0/Firebase), check password hashing config
5. Verify NO plain text or unsalted MD5/SHA1 hashes exist

**Expected Results:**
1. Query returns password_hash records
2. All hashes start with $2b$ or $2a$
3. All hashes match BCrypt regex pattern (60 chars total)
4. If using external auth: password policy confirmed as BCrypt
5. Zero instances of plain text, MD5, or SHA1 hashes in DB

**Test Data:**
- DB query: SELECT password_hash FROM users
- BCrypt regex: ^\$2[ab]\$\d{2}\$[A-Za-z0-9./]{53}$
- Expected: 100% of password hashes match BCrypt pattern

---
### TC-E2E-NFR-015: Sensitive data in .env not in source code

| Field | Value |
|-------|-------|
| **ID** | TC-E2E-NFR-015 |
| **Module** | NFR (Security) |
| **Type** | E2E (Black Box) |
| **Priority** | P1 — High |
| **Severity** | S1 — Major |
| **Automation Status** | Automated (git secrets scanner) |
| **Linked NFR** | NFR-004 |

**Preconditions:**
- [ ] Git repository cloned locally
- [ ] .env.example or .env.template available for reference
- [ ] git-secrets or similar scanner installed

**Test Steps:**
1. Install and configure git-secrets: git secrets --install
2. Add patterns for common secrets:
   - git secrets --add "JWT_SECRET.*"
   - git secrets --add "CHARGEBEE_API_KEY.*"
   - git secrets --add "DB_PASSWORD.*"
   - git secrets --add "WEBHOOK_SECRET.*"
3. Run git secrets --scan on the entire repository
4. Manually inspect .env.example for placeholder values
5. Verify .env is listed in .gitignore
6. Search for any hardcoded API keys/credentials in source code

**Expected Results:**
1-2. git-secrets installed and configured with secret patterns
3. git-secrets scan returns zero matches
4. .env.example contains only placeholder values (e.g., your-jwt-secret-here)
5. .env is present in .gitignore and NOT tracked by git
6. No hardcoded secrets found in source code files

**Test Data:**
- Tool: git-secrets (https://github.com/awslabs/git-secrets)
- File to check: .gitignore contains .env
- Expected: zero secrets committed to git history

---
### TC-E2E-NFR-016: Graceful error handling for 5xx server errors

| Field | Value |
|-------|-------|
| **ID** | TC-E2E-NFR-016 |
| **Module** | NFR (Reliability) |
| **Type** | E2E (Black Box) |
| **Priority** | P1 — High |
| **Severity** | S1 — Major |
| **Automation Status** | Manual (needs server-side trigger) |
| **Linked NFR** | NFR-008 |

**Preconditions:**
- [ ] bmjServer accessible
- [ ] Ability to trigger server error (e.g., by sending malformed request or stopping dependent service)
- [ ] App APK installed on device
- [ ] User is logged in as TA-04

**Test Steps:**
1. Trigger a server-side error:
   - Stop the Chargebee API dependency (or simulate network failure)
   - Send an invalid JSON payload to an API endpoint
   - Navigate to a feature that depends on the failing service
2. Observe the app UI on the device
3. Check if the app shows a user-friendly error message (not raw JSON/stack trace)
4. Verify the app does not crash
5. Check if the app allows retry (button or pull-to-refresh)
6. Restore the failing service
7. Trigger retry - verify operation completes successfully

**Expected Results:**
1. Server returns HTTP 5xx error
2. App shows user-friendly error UI (not crash or blank white screen)
3. Error message: Something went wrong. Please try again. (or similar)
4. App remains stable - does not crash
5. Retry mechanism visible (Refresh button or pull-to-refresh)
6-7. After service restored, retry succeeds and operation completes

**Test Data:**
- Error trigger: invalid JSON, server shutdown, network block
- Expected UI: error banner/snackbar on current screen
- Expected: no crash, no stack trace visible to user

---
### TC-E2E-NFR-017: Loading indicator shown during all async operations (UI)

| Field | Value |
|-------|-------|
| **ID** | TC-E2E-NFR-017 |
| **Module** | NFR (UI/UX) |
| **Type** | E2E (Black Box) |
| **Priority** | P2 — Medium |
| **Severity** | S2 — Minor |
| **Automation Status** | Manual (visual inspection) |
| **Linked NFR** | NFR-002 |

**Preconditions:**
- [ ] App installed on device or emulator
- [ ] Slow network condition can be simulated (e.g., WiFi throttling or airplane mode toggle)
- [ ] User is logged in as TA-04

**Test Steps:**
1. Enable airplane mode or throttle network to slow 3G
2. Log in as TA-04
3. Observe the login loading state
4. Navigate to Product Listing screen
5. Observe loading state during product fetch
6. Navigate to Orders screen
7. Observe loading state
8. Navigate to Subscription Management screen
9. Observe loading state
10. Disable slow network and verify loading indicator disappears after data loads

**Expected Results:**
1-2. Network condition simulated
3. Login screen shows CircularProgressIndicator or shimmer placeholder
4-5. Product listing shows shimmer/skeleton loader or spinner initially
6-7. Orders screen shows loading indicator while fetching order history
8-9. Subscription screen shows loading indicator while fetching subscription data
10. Loading indicators disappear after data loads or error occurs

**Test Data:**
- Network: airplane mode or throttle to 50 kbps
- UI elements to check: CircularProgressIndicator, Shimmer, SkeletonLoader
- Expected: every async operation has a visible loading state

---
### TC-E2E-NFR-018: Empty state handling for lists with no data

| Field | Value |
|-------|-------|
| **ID** | TC-E2E-NFR-018 |
| **Module** | NFR (UI/UX) |
| **Type** | E2E (Black Box) |
| **Priority** | P2 — Medium |
| **Severity** | S2 — Minor |
| **Automation Status** | Manual (visual inspection) |
| **Linked NFR** | NFR-002 |

**Preconditions:**
- [ ] Use a user account with no orders, no subscriptions (fresh TA-09 account)
- [ ] User is logged in
- [ ] Product catalog may have items (not empty)

**Test Steps:**
1. Log in as TA-09 (fresh user with no order/subscription history)
2. Navigate to Order History screen
3. Observe the UI
4. Navigate to Subscription Management screen
5. Observe the UI
6. Add a product to cart, then remove it
7. Navigate to Cart screen
8. Navigate to Address Management screen
9. Observe the UI for empty address list

**Expected Results:**
1. Fresh user logged in successfully
2-3. Orders screen shows empty state: illustration + text No orders yet + CTA button
4-5. Subscriptions screen shows: No subscriptions yet. Start your journey!
6-7. Empty cart screen: Your cart is empty + Browse Menu CTA
8-9. Address management: No addresses saved. Add a new address.
- All empty states include an illustration/icon, helpful text, and a CTA button

**Test Data:**
- User: TA-09 (fresh user, no history)
- Expected: all list views have empty state design (not blank/error screen)

---
### TC-E2E-NFR-019: Concurrent user sessions work for different users

| Field | Value |
|-------|-------|
| **ID** | TC-E2E-NFR-019 |
| **Module** | NFR (Concurrency) |
| **Type** | E2E (Black Box) |
| **Priority** | P2 — Medium |
| **Severity** | S1 — Major |
| **Automation Status** | Manual (two devices) or Automated (k6) |
| **Linked NFR** | NFR-001, NFR-008 |

**Preconditions:**
- [ ] Two physical devices OR two emulator instances
- [ ] Two separate user accounts: TA-04 and TA-05
- [ ] Both devices have stable internet access
- [ ] bmjServer deployed and accessible

**Test Steps:**
1. Device A: Log in as TA-04
2. Device B: Log in as TA-05
3. Device A: Browse catalog, add items to cart
4. Device B: Browse catalog, add different items to cart
5. Device A: View profile - verify it shows TA-04 data
6. Device B: View profile - verify it shows TA-05 data
7. Device A: Initiate checkout
8. Device B: Initiate checkout
9. Device A: Check order history
10. Device B: Check order history
11. Verify no data cross-contamination

**Expected Results:**
1-2. Both users logged in successfully with their own JWT tokens
3-4. Each device maintains separate cart state
5-6. Profile data shows correct user (no cross-contamination)
7-8. Each checkout processes correctly for each user
9-10. Order history shows only that user orders
11. No session leakage - no data from TA-04 visible on Device B and vice versa

**Test Data:**
- Device A User: TA-04 (e2e-existing@bookmyjuice.co.in / 9876543212)
- Device B User: TA-05 (user with active subscription)
- Expected: complete session isolation between users

---
