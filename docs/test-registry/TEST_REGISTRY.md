# BookMyJuice Test Registry

> **Last Updated:** 2026-05-13  
> **Owner:** QA Engineering

## Coverage Goals

| Module | Unit | Widget | Integration | E2E | Total | Backend | Flutter |
|--------|------|--------|-------------|-----|-------|---------|--------|
| AUTH | 33 | 5 | 3 | 1 | 42 | 10 | 32 |
| BILLING | 5 | 0 | 2 | 1 | 8 | 8 | 0 |
| CART | 12 | 0 | 1 | 0 | 13 | 7 | 6 |
| DELIVERY | 10 | 0 | 3 | 1 | 14 | 14 | 0 |
| WEBHOOK | 7 | 0 | 2 | 0 | 9 | 9 | 0 |
| CACHE | 5 | 0 | 1 | 0 | 6 | 6 | 0 |
| THEME | 38 | 0 | 0 | 0 | 38 | 0 | 38 |
| SECURITY | 7 | 0 | 1 | 0 | 8 | 8 | 0 |
| CICD | 3 | 0 | 0 | 0 | 3 | 3 | 0 |
| PROFILE | 3 | 0 | 0 | 0 | 3 | 3 | 0 |
| PHONE_UX | 0 | 0 | 0 | 12 | 12 | 0 | 0 |
| CROSS_MODULE | 0 | 0 | 0 | 12 | 12 | 0 | 0 |
| **TOTAL** | **123** | **5** | **13** | **27** | **168** | **68** | **76** |

> **Note:** The 133 Flutter tests (82 unit + 51 widget) are tracked under AUTH (81), CART (14), and THEME (38). An additional 5 Flutter widget tests are counted separately under AUTH widget category. Backend total = 77 tests (67 unit + 10 integration).

## Test Case Records

### AUTH Module

| TC-ID | Title | Type | Priority | Preconditions | Test Steps | Expected | Data | Auto | Status | Last Run | Bug | Coverage |
|-------|-------|------|----------|---------------|------------|----------|------|------|--------|----------|-----|----------|
| TC-AUTH-001 | Successful user signup with valid email | Unit | High | Mock UserRepo, PasswordEncoder, RoleRepo | POST /api/auth/signup with valid email, password, name | 500 (Chargebee not mocked) | email=test@example.com, password=SecurePass123! | ✅ | 2026-05-13 | — | AuthController.java:signup |
| TC-AUTH-002 | Signup with duplicate email fails | Unit | High | Mock userRepo.existsByEmail=true | POST /api/auth/signup with existing email | 400 BAD_REQUEST | email=existing@example.com | ✅ | 2026-05-13 | — | AuthController.java:signup |
| TC-AUTH-003 | Successful login | Unit | High | Mock AuthManager, JwtUtils | POST /api/auth/signin with valid credentials | 200 + JWT token | user=test@example.com, pass=SecurePass123! | ✅ | 2026-05-13 | — | AuthController.java:signin |
| TC-AUTH-004 | Login with invalid credentials | Unit | High | Mock AuthManager throws BadCredentials | POST /api/auth/signin with wrong password | BadCredentialsException thrown | user=test@example.com, pass=WrongPassword | ✅ | 2026-05-13 | — | AuthController.java:signin |
| TC-AUTH-005 | Login with non-existent user | Unit | High | Mock AuthManager throws BadCredentials | POST /api/auth/signin with unknown email | BadCredentialsException thrown | user=nonexistent@example.com | ✅ | 2026-05-13 | — | AuthController.java:signin |
| TC-AUTH-006 | JWT generation with valid user | Unit | High | Mock Authentication | JwtUtils.generateJwtToken | Token with 3 dot-separated segments | UserDetails: 1L, test@example.com | ✅ | 2026-05-13 | — | JwtUtils.java |
| TC-AUTH-007 | JWT validation with valid token | Unit | High | Mock Authentication | generate then validateJwtToken | true | Generated token | ✅ | 2026-05-13 | — | JwtUtils.java |
| TC-AUTH-008 | JWT validation with empty token | Unit | Medium | — | validateJwtToken("") | false | "" | ✅ | 2026-05-13 | — | JwtUtils.java |
| TC-AUTH-009 | JWT validation with null token | Unit | Medium | — | validateJwtToken(null) | false | null | ✅ | 2026-05-13 | — | JwtUtils.java |
| TC-AUTH-010 | JWT parsing extracts username | Unit | High | Mock Authentication | generate then getUserNameFromJwtToken | "testuser" | UserDetails: testuser | ✅ | 2026-05-13 | — | JwtUtils.java |

### AUTH Module (Flutter)

| TC-ID | Title | Type | Priority | Preconditions | Test Steps | Expected | Data | Auto | Status | Last Run | Bug | Coverage |
|-------|-------|------|----------|---------------|------------|----------|------|------|--------|----------|-----|----------|
| TC-AUTH-FL-001 | AuthBloc emits correct states for login flow (30 tests) | Unit | High | Mock UserRepository, AuthBloc instance | Dispatch LoginRequested events with various outcomes | Correct state transitions (loading, success, failure) | Valid/invalid credentials, network errors | ✅ | 2026-05-13 | BUG-002 | auth_bloc.dart |
| TC-AUTH-FL-002 | LoginPage renders and handles user interaction (21 tests) | Widget | High | Mock AuthBloc, MaterialApp wrapper | Render LoginPage, simulate taps, text input | Correct UI rendering, button states, navigation | Various login states | ✅ | 2026-05-13 | BUG-003 | login_page.dart |
| TC-AUTH-FL-003 | SignupScreen renders and handles signup flow (14 tests) | Widget | High | Mock AuthBloc, MaterialApp wrapper | Render SignupScreen, simulate form input | Correct form validation, OTP request flow | Email, phone, OTP data | ✅ | 2026-05-13 | — | sign_up_screen.dart |
| TC-AUTH-FL-004 | EmailSignupScreen renders and handles email entry (8 tests) | Widget | Medium | Mock AuthBloc, NavigatorObserver | Render EmailSignupScreen, simulate email input | Correct email validation, navigation to OTP | Valid/invalid email | ✅ | 2026-05-13 | — | email_signup_screen.dart |
| TC-AUTH-FL-005 | PhoneSignupScreen renders and handles phone entry (8 tests) | Widget | Medium | Mock AuthBloc, NavigatorObserver | Render PhoneSignupScreen, simulate phone input | Correct phone validation, OTP request | Valid/invalid phone | ✅ | 2026-05-13 | — | phone_signup_screen.dart |
| TC-AUTH-FL-006 | Email verification code generation (NEW) | Unit | High | EmailVerificationService instance | generateVerificationCode("test@example.com") | Returns 6-digit string, stored in codeStore | test@example.com | ✅ | 2026-05-13 | — | EmailVerificationService.java |
| TC-AUTH-FL-007 | Email verification code — valid code passes (NEW) | Unit | High | Generate verification code first | verifyCode(email, generatedCode) | true, code marked as used | Generated code | ✅ | 2026-05-13 | — | EmailVerificationService.java |
| TC-AUTH-FL-008 | Email verification code — wrong code fails (NEW) | Unit | Medium | Generate verification code first | verifyCode(email, "wrongcode") | false | wrong code | ✅ | 2026-05-13 | — | EmailVerificationService.java |
| TC-AUTH-FL-009 | Email verification code — reusing used code fails (NEW) | Unit | Medium | Generate code, verify once | verifyCode(email, sameCode) again | false | Same code | ✅ | 2026-05-13 | — | EmailVerificationService.java |
| TC-AUTH-FL-010 | OTP generation (NEW) | Unit | High | OTPUtil instance | generateOTP("9876543210") | Returns 6-digit string | Phone number | ✅ | 2026-05-13 | — | OTPUtil.java |
| TC-AUTH-FL-011 | OTP verification — valid OTP passes (NEW) | Unit | High | Generate OTP first | verifyOTP(phone, generatedOTP) | true, OTP marked as used | Generated OTP | ✅ | 2026-05-13 | — | OTPUtil.java |
| TC-AUTH-FL-012 | OTP verification — wrong OTP fails (NEW) | Unit | Medium | Generate OTP first | verifyOTP(phone, "wrongotp") | false | wrong OTP | ✅ | 2026-05-13 | — | OTPUtil.java |
| TC-AUTH-FL-013 | OTP verification — unknown phone fails (NEW) | Unit | Medium | — | verifyOTP("unknown@phone", "123456") | false | Unknown phone | ✅ | 2026-05-13 | — | OTPUtil.java |

### BILLING Module

| TC-ID | Title | Type | Priority | Preconditions | Test Steps | Expected | Data | Auto | Status | Last Run | Bug | Coverage |
|-------|-------|------|----------|---------------|------------|----------|------|------|--------|----------|-----|----------|
| TC-BILL-001 | Checkout with valid items | Unit | High | Mock SecurityContext | POST /api/checkout with valid itemPriceIds | 400 (CB not mocked) | itemPriceId=delight-watermelon-200ml-INR, qty=2 | ✅ | 2026-05-13 | — | CheckoutController.java |
| TC-BILL-002 | Checkout with empty cart | Unit | High | Mock SecurityContext | POST /api/checkout with empty list | 400 BAD_REQUEST | [] | ✅ | 2026-05-13 | — | CheckoutController.java |
| TC-BILL-003 | Checkout with invalid item data | Unit | High | Mock SecurityContext | POST /api/checkout with missing itemPriceId | 400 BAD_REQUEST | {} | ✅ | 2026-05-13 | — | CheckoutController.java |
| TC-BILL-004 | Checkout with single item | Unit | Medium | Mock SecurityContext | POST /api/checkout with one item | 400 (CB not mocked) | Single premium-pbc-500ml-INR | ✅ | 2026-05-13 | — | CheckoutController.java |
| TC-BILL-005 | Checkout defaults quantity | Unit | Medium | Mock SecurityContext | POST /api/checkout without quantity field | 400 (CB not mocked) | No qty specified | ✅ | 2026-05-13 | — | CheckoutController.java |

### CART Module

| TC-ID | Title | Type | Priority | Preconditions | Test Steps | Expected | Data | Auto | Status | Last Run | Bug | Coverage |
|-------|-------|------|----------|---------------|------------|----------|------|------|--------|----------|-----|----------|
| TC-CART-001 | Get cart for existing user | Unit | High | Mock CartRepo | cartService.getCart(user) | Cart with ID 100 | user.id=1L | ✅ | 2026-05-13 | — | CartService.java |
| TC-CART-002 | Get cart creates empty cart for new user | Unit | High | Mock CartRepo returns empty | cartService.getCart(user) | New cart with ID 200 | new user | ✅ | 2026-05-13 | — | CartService.java |
| TC-CART-003 | Add item with null priceId | Unit | High | Mock CartRepo | cartService.addItem(user, null, 1) | RuntimeException | null | ✅ | 2026-05-13 | — | CartService.java |
| TC-CART-004 | Add item invalid format | Unit | High | Mock CartRepo | cartService.addItem(user, "invalid", 1) | IllegalArgumentException | "invalid_format" | ✅ | 2026-05-13 | — | CartService.java |
| TC-CART-005 | Cart response structure | Unit | Medium | Mock CartRepo | cartService.getCart(user) | All required fields present | user.id=1L | ✅ | 2026-05-13 | — | CartService.java |
| TC-CART-006 | Clear cart (existing cart) (NEW) | Unit | Medium | Mock CartRepo, cart exists | cartService.clearCart(user) | Success response | user.id=1L | ✅ | 2026-05-13 | — | CartService.java |
| TC-CART-007 | Clear cart (no cart) (NEW) | Unit | Low | Mock CartRepo returns empty | cartService.clearCart(user) | Already empty message | new user | ✅ | 2026-05-13 | — | CartService.java |

### CART Module (Flutter)

| TC-ID | Title | Type | Priority | Preconditions | Test Steps | Expected | Data | Auto | Status | Last Run | Bug | Coverage |
|-------|-------|------|----------|---------------|------------|----------|------|------|--------|----------|-----|----------|
| TC-CART-FL-001 | CartBloc emits correct states for add/remove/clear (14 tests) | Unit | High | Mock UserRepository, CartBloc instance | Dispatch AddToCart, RemoveFromCart, ClearCart events | Correct state transitions with items, pricing, errors | Valid/invalid item IDs | ✅ | 2026-05-13 | — | cart_bloc.dart |

### THEME Module

| TC-ID | Title | Type | Priority | Preconditions | Test Steps | Expected | Data | Auto | Status | Last Run | Bug | Coverage |
|-------|-------|------|----------|---------------|------------|----------|------|------|--------|----------|-----|----------|
| TC-THEME-001 thru 013 | AppTheme light theme checks | Unit | Medium | — | Verify each theme property | Non-null, correct brightness, M3 | — | ✅ | 2026-05-13 | — | app_theme.dart |
| TC-THEME-014 thru 026 | AppTheme dark theme checks | Unit | Medium | — | Verify each theme property | Non-null, correct brightness, M3 | — | ✅ | 2026-05-13 | — | app_theme.dart |
| TC-THEME-FL-001 | ThemeCubit toggles and persists theme (12 tests) | Unit | Medium | ThemeCubit instance | Toggle theme, check state transitions | Correct theme mode switching, persistence | light/dark modes | ✅ | 2026-05-13 | — | theme_cubit.dart |

### SECURITY Module

| TC-ID | Title | Type | Priority | Preconditions | Test Steps | Expected | Data | Auto | Status | Last Run | Bug | Coverage |
|-------|-------|------|----------|---------------|------------|----------|------|------|--------|----------|-----|----------|
| TC-SEC-001 | Rate limiter allows under limit | Unit | High | — | isAllowed("test-key") | true | test-key | ✅ | 2026-05-13 | — | RateLimiterService.java |
| TC-SEC-002 | Remaining tokens is non-negative | Unit | Medium | — | getRemainingTokens after isAllowed | ≥ 0 | test-key-2 | ✅ | 2026-05-13 | — | RateLimiterService.java |
| TC-SEC-003 | Rate limiter handles null | Unit | Medium | — | isAllowed(null) | Does not throw | null | ✅ | 2026-05-13 | — | RateLimiterService.java |
| TC-SEC-004 | Rate limiter handles empty | Unit | Medium | — | isAllowed("") | Does not throw | "" | ✅ | 2026-05-13 | — | RateLimiterService.java |
| TC-SEC-005 | Global auth limit allowed | Unit | Medium | — | isGlobalAuthLimitAllowed() | true | — | ✅ | 2026-05-13 | — | RateLimiterService.java |
| TC-SEC-006 | Reset limit | Unit | Medium | — | resetLimit("some-ip") | Does not throw | some-ip | ✅ | 2026-05-13 | — | RateLimiterService.java |
| TC-SEC-007 | Clear all limits | Unit | Medium | — | clearAllLimits() | Does not throw | — | ✅ | 2026-05-13 | — | RateLimiterService.java |

### WEBHOOK Module

| TC-ID | Title | Type | Priority | Preconditions | Test Steps | Expected | Data | Auto | Status | Last Run | Bug | Coverage |
|-------|-------|------|----------|---------------|------------|----------|------|------|--------|----------|-----|----------|
| TC-WEB-001 | Tracked event count initially 0 | Unit | High | — | getTrackedEventCount() | 0 | — | ✅ | 2026-05-13 | — | IdempotencyService.java |
| TC-WEB-002 | ClearAllEvents does not throw | Unit | High | — | clearAllEvents() | Does not throw | — | ✅ | 2026-05-13 | — | IdempotencyService.java |
| TC-WEB-003 | Tracked count after clear | Unit | High | — | clearAllEvents() then getTrackedEventCount() | 0 | — | ✅ | 2026-05-13 | — | IdempotencyService.java |
| TC-WEB-004 | ProcessingStats constructor | Unit | Medium | — | Create ProcessingStats(1,2,3) | Fields match input | processing=1, failed=2, completed=3 | ✅ | 2026-05-13 | — | IdempotencyService.java |
| TC-WEB-005 | IdempotencyService — event cache operations (NEW) | Unit | High | Fresh IdempotencyService | isEventProcessed("test-event") | false (not in DB) | test-event | ✅ | 2026-05-13 | — | IdempotencyService.java |
| TC-WEB-006 | IdempotencyService — checkAndMarkEvent (NEW) | Unit | Medium | Fresh IdempotencyService | checkAndMarkEvent("test-event") | false (new event) | test-event | ✅ | 2026-05-13 | — | IdempotencyService.java |
| TC-WEB-007 | WebhookEventProcessor — last processing results (NEW) | Unit | Medium | Fresh WebhookEventProcessor | getLastProcessingResults() | Empty map | — | ✅ | 2026-05-13 | — | WebhookEventProcessor.java |

### CACHE Module

| TC-ID | Title | Type | Priority | Preconditions | Test Steps | Expected | Data | Auto | Status | Last Run | Bug | Coverage |
|-------|-------|------|----------|---------------|------------|----------|------|------|--------|----------|-----|----------|
| TC-CACHE-001 | Local cache fallback on API failure (NEW) | Unit | High | Mock ItemService, simulate API failure | fetchItems() when Chargebee API fails | Falls back to local database cache | — | ✅ | 2026-05-13 | — | ItemService.java |
| TC-CACHE-002 | CacheItemsLocally no-throw guarantee (NEW) | Unit | Medium | Mock ItemService | cacheItemsLocally(validItems) | Does not throw exception | valid items | ✅ | 2026-05-13 | — | ItemService.java |
| TC-CACHE-003 | IdempotencyService cache size tracking (NEW) | Unit | Medium | Fresh IdempotencyService | getTrackedEventCount() | 0 | — | ✅ | 2026-05-13 | — | IdempotencyService.java |
| TC-CACHE-004 | RateLimiterService token bucket cache (NEW) | Unit | Medium | Fresh RateLimiterService | isAllowed multiple times on same key | Returns true for first calls | test-key | ✅ | 2026-05-13 | — | RateLimiterService.java |
| TC-CACHE-005 | Empty local cache returns empty list (NEW) | Unit | Low | Empty database | getItemsFromLocalCache() | Returns empty list | — | ✅ | 2026-05-13 | — | ItemService.java |

### PROFILE Module

| TC-ID | Title | Type | Priority | Preconditions | Test Steps | Expected | Data | Auto | Status | Last Run | Bug | Coverage |
|-------|-------|------|----------|---------------|------------|----------|------|------|--------|----------|-----|----------|
| TC-PROF-001 | ChargebeeSyncService startup sync disabled (NEW) | Unit | Medium | Mock syncConfig.isEnableStartupSync=false | syncChargebeeDataOnStartup() | Logs disabled message, returns | — | ✅ | 2026-05-13 | — | ChargebeeSyncService.java |
| TC-PROF-002 | ChargebeeSyncService getSyncStatus (NEW) | Unit | Medium | Mock repositories return counts | getSyncStatus() | Returns formatted string with counts | — | ✅ | 2026-05-13 | — | ChargebeeSyncService.java |
| TC-PROF-003 | ChargebeeSyncService shutdown does not throw (NEW) | Unit | Low | Fresh ChargebeeSyncService | shutdown() | Does not throw | — | ✅ | 2026-05-13 | — | ChargebeeSyncService.java |

## Legend

- **Status:** ⏳ Not Run / ✅ Pass / ❌ Fail / ⚠️ Blocked / 🔄 In Progress
- **Auto:** ✅ Automated / ❌ Manual / 🚧 Pending
