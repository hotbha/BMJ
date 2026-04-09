# BookMyJuice - Business Requirements Document (BRD)

**Document Version:** 1.0  
**Date:** March 27, 2026  
**Project:** BookMyJuice MVP  
**Stakeholders:** Product Owner, Development Team, QA Team, Beta Users  

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Project Scope](#2-project-scope)
3. [Business Requirements](#3-business-requirements)
4. [Functional Requirements](#4-functional-requirements)
5. [Non-Functional Requirements](#5-non-functional-requirements)
6. [Requirements Traceability Matrix](#6-requirements-traceability-matrix)
7. [Use Case Specifications](#7-use-case-specifications)
8. [Test Strategy](#8-test-strategy)
9. [Development Phases](#9-development-phases)
10. [Risk Assessment](#10-risk-assessment)

---

## 1. Executive Summary

### 1.1 Business Objective
BookMyJuice is a cold-pressed juice subscription and on-demand ordering platform targeting health-conscious consumers seeking convenient, fresh juice delivery.

### 1.2 MVP Goal
Launch a minimum viable product within 2 weeks to validate:
- Customer willingness to subscribe to juice plans
- User experience of mobile ordering flow
- Payment processing via Chargebee
- Backend stability under beta load

### 1.3 Success Metrics
| Metric | Target | Measurement Period |
|--------|--------|-------------------|
| User Signups | 50 users | Week 1-2 |
| Active Users (DAU) | 20 users | Week 2 |
| Subscription Conversions | 5 users | Week 1-2 |
| One-Time Orders | 10 orders | Week 1-2 |
| App Crash Rate | < 1% | Week 1-2 |
| API Uptime | > 99% | Week 1-2 |
| Payment Success Rate | > 90% | Week 1-2 |

---

## 2. Project Scope

### 2.1 In Scope (MVP)
- User registration and authentication (Email + Google Sign-In)
- Product catalog browsing (juices with size variants)
- Shopping cart management
- One-time checkout via Chargebee
- Subscription plan selection and purchase
- User profile management
- Order history viewing
- Basic admin dashboard (provided by chargebee only)

### 2.2 Out of Scope (Post-MVP)
- Phone OTP authentication
- Push notifications
- Offline mode
- Multiple delivery addresses
- Scheduled delivery slots
- Loyalty points
- Referral program
- Dark mode
- Biometric authentication
- Advanced analytics dashboard

### 2.3 Platform Support
| Platform | MVP Support | Post-MVP |
|----------|-------------|----------|
| Android (Mobile) | APK (Manual Install) | Play Store |
| iOS | ❌ Not in MVP | App Store |
| Web | ✅ Browser Access | PWA |
| Backend API | ✅ REST API | GraphQL |

---

## 3. Business Requirements

### BR-001: User Registration & Authentication
| ID | BR-001 |
|----|--------|
| **Requirement** | Users shall be able to create accounts and authenticate securely |
| **Priority** | P0 - Critical |
| **Business Value** | Enable personalized experience and order tracking |
| **Acceptance Criteria** | User can register with email, login, and maintain session |
| **Dependencies** | Chargebee customer sync |
| **Risk** | High - Blocking feature |

### BR-002: Product Discovery
| ID | BR-002 |
|----|--------|
| **Requirement** | Users shall be able to browse available juice products with details |
| **Priority** | P0 - Critical |
| **Business Value** | Enable product selection and upselling |
| **Acceptance Criteria** | Products display with images, descriptions, prices, size options |
| **Dependencies** | Chargebee item sync |
| **Risk** | Medium |

### BR-003: Shopping Cart
| ID | BR-003 |
|----|--------|
| **Requirement** | Users shall be able to add products to cart and manage quantities |
| **Priority** | P0 - Critical |
| **Business Value** | Enable multi-item purchases and increase AOV |
| **Acceptance Criteria** | Cart persists across sessions, quantities update correctly |
| **Dependencies** | Local storage |
| **Risk** | Medium |

### BR-004: Checkout & Payment
| ID | BR-004 |
|----|--------|
| **Requirement** | Users shall be able to complete secure payments via Chargebee |
| **Priority** | P0 - Critical |
| **Business Value** | Revenue generation |
| **Acceptance Criteria** | Payment flow completes, orders are recorded |
| **Dependencies** | Chargebee integration |
| **Risk** | High - Revenue blocking |

### BR-005: Subscription Management
| ID | BR-005 |
|----|--------|
| **Requirement** | Users shall be able to purchase and manage subscriptions |
| **Priority** | P0 - Critical |
| **Business Value** | Recurring revenue model |
| **Acceptance Criteria** | Subscription plans display, purchase flow works |
| **Dependencies** | Chargebee subscription API |
| **Risk** | High - Business model blocking |

### BR-006: Order History
| ID | BR-006 |
|----|--------|
| **Requirement** | Users shall be able to view past orders and subscriptions |
| **Priority** | P1 - High |
| **Business Value** | Customer support and retention |
| **Acceptance Criteria** | Orders display with status, details accessible |
| **Dependencies** | Order webhook sync |
| **Risk** | Low |

---

## 4. Functional Requirements

### 4.1 Authentication Module

#### FR-AUTH-001: Email Registration
```yaml
ID: FR-AUTH-001
Parent: BR-001
Description: User registers with email and password
Inputs:
  - Email (valid format, unique)
  - Password (min 8 chars, 1 uppercase, 1 lowercase, 1 number, 1 special)
  - First Name (required)
  - Last Name (required)
  - Phone (10 digits)
Process:
  1. Validate all fields
  2. Check email uniqueness
  3. Hash password with BCrypt
  4. Create user in database
  5. Create Chargebee customer
  6. Return success with user ID
Outputs:
  - Success: User ID
  - Failure: Error message
Preconditions: None
Postconditions: User account created
Business Rules:
  - Email must be unique
  - Password must meet complexity requirements
  - Phone must be 10 digits
```

#### FR-AUTH-002: Email Login
```yaml
ID: FR-AUTH-002
Parent: BR-001
Description: User logs in with email and password
Inputs:
  - Email
  - Password
Process:
  1. Find user by email
  2. Verify password hash
  3. Generate JWT token (15 min expiry)
  4. Generate refresh token (7 day expiry)
  5. Return tokens and user profile
Outputs:
  - Success: JWT token, refresh token, user profile
  - Failure: "Invalid credentials"
Preconditions: User account exists
Postconditions: User authenticated
Business Rules:
  - Token expires in 15 minutes
  - Refresh token expires in 7 days
```

#### FR-AUTH-003: Google Sign-In
```yaml
ID: FR-AUTH-003
Parent: BR-001
Description: User authenticates via Google OAuth
Inputs:
  - Google ID token
Process:
  1. Validate Google ID token
  2. Extract user info (email, name)
  3. Find or create user account
  4. Generate JWT tokens
  5. Return tokens and profile
Outputs:
  - Success: JWT tokens, user profile, isNewUser flag
  - Failure: "Google authentication failed"
Preconditions: Google OAuth configured
Postconditions: User authenticated
Business Rules:
  - Email from Google is trusted (no verification needed)
```

#### FR-AUTH-004: Auto-Login
```yaml
ID: FR-AUTH-004
Parent: BR-001
Description: User is automatically logged in on app launch
Inputs:
  - Stored JWT token (from SharedPreferences)
Process:
  1. Retrieve stored token
  2. Validate token not expired
  3. Call /api/auth/autologin endpoint
  4. If valid, load user profile
  5. If invalid, redirect to login
Outputs:
  - Success: User profile loaded
  - Failure: Redirect to login
Preconditions: User previously logged in with "Remember Me"
Postconditions: User authenticated or redirected
Business Rules:
  - Token stored securely in SharedPreferences
```

### 4.2 Product Catalog Module

#### FR-PROD-001: List Products
```yaml
ID: FR-PROD-001
Parent: BR-002
Description: Display all available juice products
Inputs:
  - Authentication token
  - Optional: Category filter
  - Optional: Size filter
Process:
  1. Call GET /api/test/charge-items
  2. Filter by type=CHARGE (one-time) or type=PLAN (subscription)
  3. Group by item family
  4. Return list with images, prices, descriptions
Outputs:
  - Success: List of Product objects
  - Failure: Error message
Preconditions: User authenticated
Postconditions: Products displayed
Business Rules:
  - Only active products shown
  - Prices from Chargebee item prices
```

#### FR-PROD-002: Product Details
```yaml
ID: FR-PROD-002
Parent: BR-002
Description: Display detailed product information
Inputs:
  - Product ID
Process:
  1. Fetch product from cached list
  2. Display all size variants with prices
  3. Show nutritional info if available
  4. Show product images
Outputs:
  - Product detail view
Preconditions: Product list loaded
Postconditions: User viewing product details
Business Rules:
  - All size variants must be displayed
```

### 4.3 Shopping Cart Module

#### FR-CART-001: Add to Cart
```yaml
ID: FR-CART-001
Parent: BR-003
Description: Add product with selected size to cart
Inputs:
  - Product object
  - Selected price/size
  - Quantity (default 1)
Process:
  1. Check if item already in cart (same product + same size)
  2. If exists, increment quantity
  3. If not, add new cart item
  4. Save cart to SharedPreferences
  5. Update cart badge count
Outputs:
  - Success: Cart updated
  - Failure: Error message
Preconditions: User viewing product
Postconditions: Item in cart
Business Rules:
  - Same product with different sizes are separate items
  - Max quantity per item: 99
```

#### FR-CART-002: Update Cart Quantity
```yaml
ID: FR-CART-002
Parent: BR-003
Description: Increase or decrease item quantity
Inputs:
  - Cart item ID
  - Change amount (+1 or -1)
Process:
  1. Find cart item
  2. Apply change
  3. If quantity <= 0, remove item
  4. Save cart
  5. Recalculate total
Outputs:
  - Updated cart total
Preconditions: Item in cart
Postconditions: Cart updated
Business Rules:
  - Quantity cannot be negative
  - Zero quantity removes item
```

#### FR-CART-003: Remove from Cart
```yaml
ID: FR-CART-003
Parent: BR-003
Description: Remove item from cart
Inputs:
  - Cart item ID
Process:
  1. Find and remove item
  2. Save cart
  3. Update total
Outputs:
  - Success confirmation
Preconditions: Item in cart
Postconditions: Item removed
Business Rules: None
```

#### FR-CART-004: Calculate Cart Total
```yaml
ID: FR-CART-004
Parent: BR-003
Description: Calculate subtotal, tax, and total
Inputs:
  - Cart items list
Process:
  1. Sum (price × quantity) for all items = Subtotal
  2. Calculate tax (18% of subtotal)
  3. Add delivery fee (if subtotal < 500)
  4. Subtotal + Tax + Delivery = Total
Outputs:
  - Subtotal
  - Tax amount
  - Delivery fee
  - Grand total
Preconditions: Cart has items
Postconditions: Totals displayed
Business Rules:
  - Tax rate: 18%
  - Free delivery above ₹500
  - Delivery fee: ₹40
```

### 4.4 Checkout Module

#### FR-CHK-001: One-Time Checkout
```yaml
ID: FR-CHK-001
Parent: BR-004
Description: Generate Chargebee hosted page for one-time purchase
Inputs:
  - Cart items (itemPriceId, quantity)
  - Customer ID
Process:
  1. Call POST /api/test/cartCheckout
  2. Backend creates Chargebee hosted page
  3. Return hosted page URL
  4. Open URL in WebView
  5. Handle return URL
Outputs:
  - Success: Order confirmation
  - Failure: Error message
Preconditions: Cart has items, user authenticated
Postconditions: Order placed or cancelled
Business Rules:
  - Hosted page expires in 1 hour
  - Payment must complete within session
```

#### FR-CHK-002: Subscription Checkout
```yaml
ID: FR-CHK-002
Parent: BR-005
Description: Generate Chargebee hosted page for subscription
Inputs:
  - Plan ID
  - Customer ID
Process:
  1. Call GET /api/test/generate_pricing_page_session_url
  2. Get plan-specific URL
  3. Open URL in WebView
  4. Handle subscription activation webhook
Outputs:
  - Success: Subscription active
  - Failure: Error message
Preconditions: User authenticated
Postconditions: Subscription active
Business Rules:
  - Subscription starts immediately
  - First charge at time of purchase
```

### 4.5 Order Management Module

#### FR-ORD-001: View Order History
```yaml
ID: FR-ORD-001
Parent: BR-006
Description: Display list of past orders
Inputs:
  - Customer ID
  - Authentication token
Process:
  1. Call GET /api/test/ordersByCustomerId
  2. Fetch orders from database
  3. Display list sorted by date (newest first)
  4. Show order number, date, total, status
Outputs:
  - List of orders
Preconditions: User authenticated
Postconditions: Orders displayed
Business Rules:
  - Only current user's orders shown
  - Maximum 50 orders displayed
```

#### FR-ORD-002: View Order Details
```yaml
ID: FR-ORD-002
Parent: BR-006
Description: Display detailed order information
Inputs:
  - Order ID
Process:
  1. Call GET /api/orders/{orderId}
  2. Fetch order details
  3. Display items, prices, status timeline
Outputs:
  - Order detail view
Preconditions: Order exists
Postconditions: Order details displayed
Business Rules:
  - Status timeline shows all state changes
```

---

## 5. Non-Functional Requirements

### 5.1 Performance
| ID | NFR-001 |
|----|---------|
| **Requirement** | API response time < 2 seconds for 95th percentile |
| **Measurement** | Backend logging, monitoring |
| **Target** | p95 < 2000ms |
| **Criticality** | High |

| ID | NFR-002 |
|----|---------|
| **Requirement** | App cold start < 3 seconds |
| **Measurement** | Flutter performance metrics |
| **Target** | < 3000ms |
| **Criticality** | Medium |

| ID | NFR-003 |
|----|---------|
| **Requirement** | Screen render < 16ms (60 FPS) |
| **Measurement** | Flutter DevTools |
| **Target** | 60 FPS |
| **Criticality** | Medium |

### 5.2 Security
| ID | NFR-004 |
|----|---------|
| **Requirement** | All API calls over HTTPS |
| **Measurement** | Network inspection |
| **Target** | 100% HTTPS |
| **Criticality** | Critical |

| ID | NFR-005 |
|----|---------|
| **Requirement** | Passwords hashed with BCrypt (cost factor 10) |
| **Measurement** | Code review, security scan |
| **Target** | 100% compliance |
| **Criticality** | Critical |

| ID | NFR-006 |
|----|---------|
| **Requirement** | JWT tokens stored securely |
| **Measurement** | Code review |
| **Target** | SharedPreferences with encryption |
| **Criticality** | High |

### 5.3 Reliability
| ID | NFR-007 |
|----|---------|
| **Requirement** | API uptime > 99% |
| **Measurement** | Uptime monitoring |
| **Target** | 99% during beta |
| **Criticality** | High |

| ID | NFR-008 |
|----|---------|
| **Requirement** | App crash rate < 1% |
| **Measurement** | Crash reporting |
| **Target** | < 1% of sessions |
| **Criticality** | High |

### 5.4 Usability
| ID | NFR-009 |
|----|---------|
| **Requirement** | First-time user completes signup in < 2 minutes |
| **Measurement** | User testing |
| **Target** | < 120 seconds |
| **Criticality** | Medium |

| ID | NFR-010 |
|----|---------|
| **Requirement** | All text meets WCAG 2.1 AA contrast ratio (4.5:1) |
| **Measurement** | Accessibility scanner |
| **Target** | 100% compliance |
| **Criticality** | Medium |

---

## 6. Requirements Traceability Matrix

| Business Req | Functional Req | Use Case | Test Case ID | Test Type | Status |
|--------------|----------------|----------|--------------|-----------|--------|
| BR-001 | FR-AUTH-001 | UC-001 | TC-AUTH-001 | Unit | ⏳ Pending |
| BR-001 | FR-AUTH-002 | UC-002 | TC-AUTH-002 | Unit | ⏳ Pending |
| BR-001 | FR-AUTH-003 | UC-003 | TC-AUTH-003 | Integration | ⏳ Pending |
| BR-001 | FR-AUTH-004 | UC-004 | TC-AUTH-004 | E2E | ⏳ Pending |
| BR-002 | FR-PROD-001 | UC-005 | TC-PROD-001 | Unit | ⏳ Pending |
| BR-002 | FR-PROD-002 | UC-006 | TC-PROD-002 | Integration | ⏳ Pending |
| BR-003 | FR-CART-001 | UC-007 | TC-CART-001 | Unit | ⏳ Pending |
| BR-003 | FR-CART-002 | UC-008 | TC-CART-002 | Unit | ⏳ Pending |
| BR-003 | FR-CART-003 | UC-009 | TC-CART-003 | Unit | ⏳ Pending |
| BR-003 | FR-CART-004 | UC-010 | TC-CART-004 | Unit | ⏳ Pending |
| BR-004 | FR-CHK-001 | UC-011 | TC-CHK-001 | Integration | ⏳ Pending |
| BR-005 | FR-CHK-002 | UC-012 | TC-CHK-002 | Integration | ⏳ Pending |
| BR-006 | FR-ORD-001 | UC-013 | TC-ORD-001 | E2E | ⏳ Pending |
| BR-006 | FR-ORD-002 | UC-014 | TC-ORD-002 | E2E | ⏳ Pending |

---

## 7. Use Case Specifications

### UC-001: User Registration
```yaml
Use Case ID: UC-001
Name: User Registration
Actor: Guest User
Preconditions: User is not logged in
Postconditions: User account created, user logged in
Main Flow:
  1. User navigates to signup screen
  2. User enters email, password, name, phone
  3. User taps "Sign Up"
  4. System validates all fields
  5. System checks email uniqueness
  6. System creates user account
  7. System creates Chargebee customer
  8. System logs in user
  9. System navigates to dashboard
Alternate Flows:
  - 4a. Validation fails:
    - 4a1. Display error messages
    - 4a2. User corrects and resubmits
  - 5a. Email already exists:
    - 5a1. Display "Email already registered"
    - 5a2. Offer login or password reset
Exception Flows:
  - 6a. Chargebee API fails:
    - 6a1. Rollback user creation
    - 6a2. Display "Registration failed, try again"
Business Rules:
  - Email must be unique
  - Password must meet complexity requirements
  - Phone must be 10 digits
UI Requirements:
  - Email field with validation
  - Password field with strength indicator
  - First name, last name fields
  - Phone field with numeric validation
  - Submit button (disabled until valid)
```

### UC-002: User Login
```yaml
Use Case ID: UC-002
Name: User Login
Actor: Registered User
Preconditions: User has account
Postconditions: User authenticated, on dashboard
Main Flow:
  1. User navigates to login screen
  2. User enters email and password
  3. User taps "Login"
  4. System validates credentials
  5. System generates JWT tokens
  6. System stores tokens
  7. System navigates to dashboard
Alternate Flows:
  - 4a. Invalid credentials:
    - 4a1. Display "Invalid email or password"
    - 4a2. User retries
  - 4b. Account locked (5 failed attempts):
    - 4b1. Display "Account locked, reset password"
    - 4b2. Offer password reset
Exception Flows:
  - 5a. Network error:
    - 5a1. Display "Network error, check connection"
    - 5a2. Retry button
Business Rules:
  - Account locks after 5 failed attempts
  - Lock duration: 15 minutes
UI Requirements:
  - Email field
  - Password field
  - "Remember Me" checkbox
  - Login button
  - "Forgot Password" link
  - "Sign Up" link
```

*(Continued for all 14 use cases...)*

---

## 8. Test Strategy

### 8.1 Testing Levels

#### Level 1: Unit Tests
- **Target:** Individual functions, methods, classes
- **Framework:** JUnit 5 (Backend), flutter_test (Frontend)
- **Coverage Target:** 80% line coverage
- **Execution:** On every commit

#### Level 2: Integration Tests
- **Target:** Module interactions, API endpoints
- **Framework:** Spring Boot Test (Backend), integration_test (Frontend)
- **Coverage Target:** All critical paths
- **Execution:** Nightly

#### Level 3: End-to-End Tests
- **Target:** Complete user flows
- **Framework:** Flutter integration_test
- **Coverage Target:** All use cases
- **Execution:** Before release

#### Level 4: User Acceptance Testing
- **Target:** Business requirements validation
- **Participants:** Beta users
- **Duration:** 2 weeks
- **Success Criteria:** All BRs met

### 8.2 Test Environment

| Environment | Purpose | Access |
|-------------|---------|--------|
| Local Dev | Development | Developers |
| Staging | Integration testing | QA, Product |
| Production | Beta users | Beta testers |

### 8.3 Test Data Management

```yaml
Test Users:
  - test_user_1@test.com / Test123!
  - test_user_2@test.com / Test123!
  - google_user@test.com (Google Sign-In)

Test Products:
  - Charge Items: Juice products (250ml, 500ml)
  - Plans: Premium, Signature, Delight

Test Payment:
  - Chargebee Test Mode
  - Test cards provided by Chargebee
```

---

## 9. Development Phases

### Phase 1: Foundation (Days 1-3)
- [ ] Setup development environment
- [ ] Configure CI/CD pipeline
- [ ] Setup test frameworks
- [ ] Database schema verification
- [ ] Chargebee test site configuration

### Phase 2: Authentication (Days 4-7)
- [ ] Implement FR-AUTH-001 to FR-AUTH-004
- [ ] Write unit tests (TC-AUTH-001 to TC-AUTH-004)
- [ ] Write integration tests
- [ ] Security review
- [ ] **Milestone: User can register and login**

### Phase 3: Product Catalog (Days 8-10)
- [ ] Implement FR-PROD-001, FR-PROD-002
- [ ] Write unit tests (TC-PROD-001, TC-PROD-002)
- [ ] UI implementation
- [ ] **Milestone: User can browse products**

### Phase 4: Shopping Cart (Days 11-13)
- [ ] Implement FR-CART-001 to FR-CART-004
- [ ] Write unit tests (TC-CART-001 to TC-CART-004)
- [ ] Local storage implementation
- [ ] **Milestone: User can add to cart**

### Phase 5: Checkout (Days 14-17)
- [ ] Implement FR-CHK-001, FR-CHK-002
- [ ] Write integration tests (TC-CHK-001, TC-CHK-002)
- [ ] Chargebee hosted page integration
- [ ] WebView implementation
- [ ] **Milestone: User can complete purchase**

### Phase 6: Order Management (Days 18-20)
- [ ] Implement FR-ORD-001, FR-ORD-002
- [ ] Write E2E tests (TC-ORD-001, TC-ORD-002)
- [ ] Order history UI
- [ ] **Milestone: User can view orders**

### Phase 7: Testing & Bug Fixes (Days 21-25)
- [ ] Full regression testing
- [ ] Performance testing
- [ ] Security testing
- [ ] Bug fixes
- [ ] **Milestone: Release candidate ready**

### Phase 8: Beta Launch (Days 26-30)
- [ ] Deploy to staging
- [ ] Onboard beta users (10-20 users)
- [ ] Collect feedback
- [ ] Monitor metrics
- [ ] **Milestone: MVP launched**

---

## 10. Risk Assessment

| Risk ID | Risk Description | Probability | Impact | Mitigation |
|---------|------------------|-------------|--------|------------|
| RISK-001 | Chargebee API rate limits | Medium | High | Implement caching, batch requests |
| RISK-002 | Payment failures in test mode | High | Medium | Clear error messages, retry logic |
| RISK-003 | Gradle build issues | Medium | Medium | Use web build as fallback |
| RISK-004 | Database connection failures | Low | High | Connection pooling, retry logic |
| RISK-005 | JWT token security breach | Low | Critical | Short expiry, secure storage |
| RISK-006 | Beta user dropoff | Medium | Medium | Engaging onboarding, support |
| RISK-007 | Performance degradation under load | Medium | High | Load testing, monitoring |

---

## Appendix A: Glossary

| Term | Definition |
|------|------------|
| AOV | Average Order Value |
| BR | Business Requirement |
| FR | Functional Requirement |
| NFR | Non-Functional Requirement |
| UC | Use Case |
| TC | Test Case |
| JWT | JSON Web Token |
| DAU | Daily Active Users |
| MVP | Minimum Viable Product |
| SDLC | Software Development Life Cycle |

---

## Appendix B: Document Approval

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Product Owner | | | |
| Tech Lead | | | |
| QA Lead | | | |
| Project Manager | | | |

---

**Document Control:**
- **Created:** March 27, 2026
- **Last Updated:** March 27, 2026
- **Version:** 1.0
- **Status:** Draft
