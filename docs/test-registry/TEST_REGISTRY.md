# BookMyJuice Test Registry

> **Last Updated:** 2026-05-11  
> **Owner:** QA Engineering

## Coverage Goals

| Module | Unit | Integration | E2E | Total |
|--------|------|-------------|-----|-------|
| AUTH | 10 | 1 | 1 | 12 |
| BILLING | 5 | 2 | 1 | 8 |
| CART | 5 | 1 | 0 | 6 |
| DELIVERY | 10 | 3 | 1 | 14 |
| WEBHOOK | 4 | 2 | 0 | 6 |
| CACHE | 4 | 1 | 0 | 5 |
| THEME | 26 | 0 | 0 | 26 |
| SECURITY | 7 | 1 | 0 | 8 |
| CICD | 3 | 0 | 0 | 3 |
| **TOTAL** | **74** | **11** | **3** | **88** |

## Test Case Records

### AUTH Module

| TC-ID | Title | Type | Priority | Preconditions | Test Steps | Expected | Data | Auto | Status | Last Run | Bug | Coverage |
|-------|-------|------|----------|---------------|------------|----------|------|------|--------|----------|-----|----------|
| TC-AUTH-001 | Successful user signup with valid email | Unit | High | Mock UserRepo, PasswordEncoder, RoleRepo | POST /api/auth/signup with valid email, password, name | 500 (Chargebee not mocked) | email=test@example.com, password=SecurePass123! | ✅ | — | — | AuthController.java:signup |
| TC-AUTH-002 | Signup with duplicate email fails | Unit | High | Mock userRepo.existsByEmail=true | POST /api/auth/signup with existing email | 400 BAD_REQUEST | email=existing@example.com | ✅ | — | — | AuthController.java:signup |
| TC-AUTH-003 | Successful login | Unit | High | Mock AuthManager, JwtUtils | POST /api/auth/signin with valid credentials | 200 + JWT token | user=test@example.com, pass=SecurePass123! | ✅ | — | — | AuthController.java:signin |
| TC-AUTH-004 | Login with invalid credentials | Unit | High | Mock AuthManager throws BadCredentials | POST /api/auth/signin with wrong password | BadCredentialsException thrown | user=test@example.com, pass=WrongPassword | ✅ | — | — | AuthController.java:signin |
| TC-AUTH-005 | Login with non-existent user | Unit | High | Mock AuthManager throws BadCredentials | POST /api/auth/signin with unknown email | BadCredentialsException thrown | user=nonexistent@example.com | ✅ | — | — | AuthController.java:signin |
| TC-AUTH-006 | JWT generation with valid user | Unit | High | Mock Authentication | JwtUtils.generateJwtToken | Token with 3 dot-separated segments | UserDetails: 1L, test@example.com | ✅ | — | — | JwtUtils.java |
| TC-AUTH-007 | JWT validation with valid token | Unit | High | Mock Authentication | generate then validateJwtToken | true | Generated token | ✅ | — | — | JwtUtils.java |
| TC-AUTH-008 | JWT validation with empty token | Unit | Medium | — | validateJwtToken("") | false | "" | ✅ | — | — | JwtUtils.java |
| TC-AUTH-009 | JWT validation with null token | Unit | Medium | — | validateJwtToken(null) | false | null | ✅ | — | — | JwtUtils.java |
| TC-AUTH-010 | JWT parsing extracts username | Unit | High | Mock Authentication | generate then getUserNameFromJwtToken | "testuser" | UserDetails: testuser | ✅ | — | — | JwtUtils.java |

### BILLING Module

| TC-ID | Title | Type | Priority | Preconditions | Test Steps | Expected | Data | Auto | Status | Last Run | Bug | Coverage |
|-------|-------|------|----------|---------------|------------|----------|------|------|--------|----------|-----|----------|
| TC-BILL-001 | Checkout with valid items | Unit | High | Mock SecurityContext | POST /api/checkout with valid itemPriceIds | 400 (CB not mocked) | itemPriceId=delight-watermelon-200ml-INR, qty=2 | ✅ | — | — | CheckoutController.java |
| TC-BILL-002 | Checkout with empty cart | Unit | High | Mock SecurityContext | POST /api/checkout with empty list | 200 OK | [] | ✅ | — | — | CheckoutController.java |
| TC-BILL-003 | Checkout with invalid item data | Unit | High | Mock SecurityContext | POST /api/checkout with missing itemPriceId | 400 BAD_REQUEST | {} | ✅ | — | — | CheckoutController.java |
| TC-BILL-004 | Checkout with single item | Unit | Medium | Mock SecurityContext | POST /api/checkout with one item | 400 (CB not mocked) | Single premium-pbc-500ml-INR | ✅ | — | — | CheckoutController.java |
| TC-BILL-005 | Checkout defaults quantity | Unit | Medium | Mock SecurityContext | POST /api/checkout without quantity field | 400 (CB not mocked) | No qty specified | ✅ | — | — | CheckoutController.java |

### CART Module

| TC-ID | Title | Type | Priority | Preconditions | Test Steps | Expected | Data | Auto | Status | Last Run | Bug | Coverage |
|-------|-------|------|----------|---------------|------------|----------|------|------|--------|----------|-----|----------|
| TC-CART-001 | Get cart for existing user | Unit | High | Mock CartRepo | cartService.getCart(user) | Cart with ID 100 | user.id=1L | ✅ | — | — | CartService.java |
| TC-CART-002 | Get cart creates empty cart for new user | Unit | High | Mock CartRepo returns empty | cartService.getCart(user) | New cart with ID 200 | new user | ✅ | — | — | CartService.java |
| TC-CART-003 | Add item with null priceId | Unit | High | Mock CartRepo | cartService.addItem(user, null, 1) | RuntimeException | null | ✅ | — | — | CartService.java |
| TC-CART-004 | Add item invalid format | Unit | High | Mock CartRepo | cartService.addItem(user, "invalid", 1) | IllegalArgumentException | "invalid_format" | ✅ | — | — | CartService.java |
| TC-CART-005 | Cart response structure | Unit | Medium | Mock CartRepo | cartService.getCart(user) | All required fields present | user.id=1L | ✅ | — | — | CartService.java |

### THEME Module

| TC-ID | Title | Type | Priority | Preconditions | Test Steps | Expected | Data | Auto | Status | Last Run | Bug | Coverage |
|-------|-------|------|----------|---------------|------------|----------|------|------|--------|----------|-----|----------|
| TC-THEME-001 thru 013 | AppTheme light theme checks | Unit | Medium | — | Verify each theme property | Non-null, correct brightness, M3 | — | ✅ | — | — | app_theme.dart |
| TC-THEME-014 thru 026 | AppTheme dark theme checks | Unit | Medium | — | Verify each theme property | Non-null, correct brightness, M3 | — | ✅ | — | — | app_theme.dart |

### SECURITY Module

| TC-ID | Title | Type | Priority | Preconditions | Test Steps | Expected | Data | Auto | Status | Last Run | Bug | Coverage |
|-------|-------|------|----------|---------------|------------|----------|------|------|--------|----------|-----|----------|
| TC-SEC-001 | Rate limiter allows under limit | Unit | High | — | isAllowed("test-key") | true | test-key | ✅ | — | — | RateLimiterService.java |
| TC-SEC-002 | Remaining tokens is non-negative | Unit | Medium | — | getRemainingTokens after isAllowed | ≥ 0 | test-key-2 | ✅ | — | — | RateLimiterService.java |
| TC-SEC-003 | Rate limiter handles null | Unit | Medium | — | isAllowed(null) | Does not throw | null | ✅ | — | — | RateLimiterService.java |
| TC-SEC-004 | Rate limiter handles empty | Unit | Medium | — | isAllowed("") | Does not throw | "" | ✅ | — | — | RateLimiterService.java |
| TC-SEC-005 | Global auth limit allowed | Unit | Medium | — | isGlobalAuthLimitAllowed() | true | — | ✅ | — | — | RateLimiterService.java |
| TC-SEC-006 | Reset limit | Unit | Medium | — | resetLimit("some-ip") | Does not throw | some-ip | ✅ | — | — | RateLimiterService.java |
| TC-SEC-007 | Clear all limits | Unit | Medium | — | clearAllLimits() | Does not throw | — | ✅ | — | — | RateLimiterService.java |

### WEBHOOK Module

| TC-ID | Title | Type | Priority | Preconditions | Test Steps | Expected | Data | Auto | Status | Last Run | Bug | Coverage |
|-------|-------|------|----------|---------------|------------|----------|------|------|--------|----------|-----|----------|
| TC-WEB-001 | Tracked event count initially 0 | Unit | High | — | getTrackedEventCount() | 0 | — | ✅ | — | — | IdempotencyService.java |
| TC-WEB-002 | ClearAllEvents does not throw | Unit | High | — | clearAllEvents() | Does not throw | — | ✅ | — | — | IdempotencyService.java |
| TC-WEB-003 | Tracked count after clear | Unit | High | — | clearAllEvents() then getTrackedEventCount() | 0 | — | ✅ | — | — | IdempotencyService.java |
| TC-WEB-004 | ProcessingStats constructor | Unit | Medium | — | Create ProcessingStats(1,2,3) | Fields match input | processing=1, failed=2, completed=3 | ✅ | — | — | IdempotencyService.java |

## Legend

- **Status:** ⏳ Not Run / ✅ Pass / ❌ Fail / ⚠️ Blocked / 🔄 In Progress
- **Auto:** ✅ Automated / ❌ Manual / 🚧 Pending
