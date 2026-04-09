# BookMyJuice - Professional SDLC Implementation Plan

**Date:** March 27, 2026  
**Status:** Ready for Implementation  
**Methodology:** Agile with 2-Week Sprints  

---

## Executive Summary

I apologize for the previous rushed approach. You're absolutely right that proper software engineering requires:

1. ✅ **Comprehensive Requirements Documentation** - NOW COMPLETE
2. ✅ **Detailed Test Cases with Pass/Fail Criteria** - NOW COMPLETE  
3. ✅ **Requirements → Use Cases → Test Cases Traceability** - NOW COMPLETE
4. ✅ **Professional Development Tooling Setup** - NOW COMPLETE
5. ⏳ **Discrete Task Implementation Following SDLC** - READY TO START

---

## Documentation Created

| Document | Purpose | Status | Location |
|----------|---------|--------|----------|
| **BRD_Business_Requirements.md** | Business & Functional Requirements | ✅ Complete | `x:\BMJ\docs\` |
| **Test_Cases_Detailed.md** | 30 Test Cases with Pass/Fail Criteria | ✅ Complete | `x:\BMJ\docs\` |
| **Development_Tools_Configuration.md** | VS Code, MCP, Plugins, Testing Setup | ✅ Complete | `x:\BMJ\docs\` |
| **SDLC_Implementation_Plan.md** | This document - Implementation roadmap | ✅ Complete | `x:\BMJ\docs\` |

---

## Requirements Traceability Summary

### Business Requirements (6 Total)

| ID | Requirement | Priority | Linked Use Cases | Linked Test Cases |
|----|-------------|----------|------------------|-------------------|
| BR-001 | User Registration & Authentication | P0 | UC-001 to UC-004 | TC-AUTH-001 to TC-AUTH-008 |
| BR-002 | Product Discovery | P0 | UC-005 to UC-006 | TC-PROD-001 to TC-PROD-003 |
| BR-003 | Shopping Cart | P0 | UC-007 to UC-010 | TC-CART-001 to TC-CART-007 |
| BR-004 | Checkout & Payment | P0 | UC-011 | TC-CHK-001 to TC-CHK-002 |
| BR-005 | Subscription Management | P0 | UC-012 | TC-CHK-003 to TC-CHK-004 |
| BR-006 | Order History | P1 | UC-013 to UC-014 | TC-ORD-001 to TC-ORD-003 |

**Additional Test Coverage:**
- Performance: TC-PERF-001 to TC-PERF-002
- Security: TC-SEC-001 to TC-SEC-003

**Total Test Cases:** 30

---

## Implementation Phases (SDLC)

### Phase 1: Environment Setup (Days 1-2)

**Goal:** Professional development environment ready

#### Tasks:

- [ ] **TASK-1.1:** Install VS Code Extensions
  - **Duration:** 30 mins
  - **Command:** Run installation commands from `Development_Tools_Configuration.md` Section 1
  - **Acceptance:** All 15+ extensions installed

- [ ] **TASK-1.2:** Configure MCP Servers
  - **Duration:** 30 mins
  - **Action:** Setup GitHub MCP, Filesystem MCP
  - **Acceptance:** MCP servers responding in VS Code

- [ ] **TASK-1.3:** Update Flutter Test Dependencies
  - **Duration:** 15 mins
  - **File:** `lush/pubspec.yaml`
  - **Action:** Add dependencies from Section 3
  - **Acceptance:** `flutter pub get` succeeds

- [ ] **TASK-1.4:** Update Backend Test Dependencies  
  - **Duration:** 15 mins
  - **File:** `bmjServer/pom.xml`
  - **Action:** Add test dependencies from Section 4
  - **Acceptance:** `mvn clean compile` succeeds

- [ ] **TASK-1.5:** Create Test Directory Structure
  - **Duration:** 30 mins
  - **Action:** Create directories from Sections 3 & 4
  - **Acceptance:** All test directories exist

- [ ] **TASK-1.6:** Configure CI/CD Pipeline
  - **Duration:** 1 hour
  - **File:** `.github/workflows/ci-cd.yml`
  - **Action:** Copy from Section 6
  - **Acceptance:** GitHub Actions workflow visible

**Phase 1 Deliverables:**
- Fully configured development environment
- Test frameworks ready
- CI/CD pipeline configured

---

### Phase 2: Authentication Module (Days 3-7)

**Goal:** User can register, login, and maintain session

#### Sprint Backlog:

**Backend Tasks:**

- [ ] **TASK-2.1:** Implement FR-AUTH-001 (Email Registration)
  - **File:** `AuthController.java`, `UserService.java`
  - **Test:** TC-AUTH-001, TC-AUTH-002, TC-AUTH-003
  - **Duration:** 4 hours

- [ ] **TASK-2.2:** Implement FR-AUTH-002 (Email Login)
  - **File:** `AuthController.java`, `JwtUtils.java`
  - **Test:** TC-AUTH-004, TC-AUTH-005
  - **Duration:** 3 hours

- [ ] **TASK-2.3:** Implement FR-AUTH-003 (Google Sign-In)
  - **File:** `GoogleAuthController.java`
  - **Test:** TC-AUTH-008
  - **Duration:** 4 hours

- [ ] **TASK-2.4:** Implement FR-AUTH-004 (Auto-Login)
  - **File:** `AuthController.java`
  - **Test:** TC-AUTH-006, TC-AUTH-007
  - **Duration:** 2 hours

- [ ] **TASK-2.5:** Write Unit Tests for Authentication
  - **Files:** `AuthControllerTest.java`, `AuthServiceTest.java`
  - **Duration:** 4 hours
  - **Acceptance:** 80% code coverage

**Frontend Tasks:**

- [ ] **TASK-2.6:** Implement Login Screen UI
  - **File:** `lush/lib/views/screens/loginPage.dart`
  - **Duration:** 3 hours

- [ ] **TASK-2.7:** Implement Signup Screen UI
  - **File:** `lush/lib/views/screens/SignUpScreen.dart`
  - **Duration:** 3 hours

- [ ] **TASK-2.8:** Implement Auth BLoC
  - **Files:** `AuthBloc.dart`, `AuthEvents.dart`, `AuthState.dart`
  - **Duration:** 4 hours

- [ ] **TASK-2.9:** Write Flutter Unit Tests
  - **Files:** `auth_bloc_test.dart`, `login_screen_test.dart`
  - **Duration:** 3 hours

**Phase 2 Deliverables:**
- ✅ User registration working
- ✅ User login working
- ✅ Google Sign-In working
- ✅ Auto-login working
- ✅ All authentication tests passing

---

### Phase 3: Product Catalog Module (Days 8-10)

**Goal:** User can browse and view product details

#### Sprint Backlog:

**Backend Tasks:**

- [ ] **TASK-3.1:** Implement FR-PROD-001 (List Products)
  - **File:** `TestController.java`, `ItemService.java`
  - **Test:** TC-PROD-001, TC-PROD-002
  - **Duration:** 3 hours

- [ ] **TASK-3.2:** Implement FR-PROD-002 (Product Details)
  - **File:** `ItemService.java`
  - **Test:** TC-PROD-003
  - **Duration:** 2 hours

**Frontend Tasks:**

- [ ] **TASK-3.3:** Implement Products BLoC
  - **Files:** `ProductsBloc.dart`
  - **Duration:** 3 hours

- [ ] **TASK-3.4:** Implement Menu Screen
  - **File:** `Menu.dart`, `ItemListView.dart`
  - **Duration:** 4 hours

- [ ] **TASK-3.5:** Implement Product Detail Screen
  - **File:** `detail.dart`
  - **Duration:** 3 hours

- [ ] **TASK-3.6:** Write Product Module Tests
  - **Files:** `products_bloc_test.dart`, `product_card_test.dart`
  - **Duration:** 3 hours

**Phase 3 Deliverables:**
- ✅ Product list displays from Chargebee
- ✅ Product details screen working
- ✅ Size selection working
- ✅ All product tests passing

---

### Phase 4: Shopping Cart Module (Days 11-13)

**Goal:** User can add items and manage cart

#### Sprint Backlog:

**Frontend Tasks:**

- [ ] **TASK-4.1:** Implement Cart BLoC
  - **Files:** `CartBloc.dart`, `cartEvent.dart`, `cartState.dart`
  - **Test:** TC-CART-001 to TC-CART-007
  - **Duration:** 4 hours

- [ ] **TASK-4.2:** Implement Cart Repository
  - **File:** `cartRepository.dart`
  - **Duration:** 3 hours

- [ ] **TASK-4.3:** Implement Cart Screen UI
  - **File:** `CartScreen.dart`
  - **Duration:** 4 hours

- [ ] **TASK-4.4:** Implement Size Selection Modal
  - **File:** `size_selection_modal.dart`
  - **Duration:** 3 hours

- [ ] **TASK-4.5:** Write Cart Module Tests
  - **Files:** `cart_bloc_test.dart`, `cart_repository_test.dart`
  - **Duration:** 4 hours

**Phase 4 Deliverables:**
- ✅ Add to cart working
- ✅ Update quantity working
- ✅ Remove from cart working
- ✅ Cart total calculation correct
- ✅ Cart persists across sessions
- ✅ All cart tests passing

---

### Phase 5: Checkout Module (Days 14-17)

**Goal:** User can complete payment via Chargebee

#### Sprint Backlog:

**Backend Tasks:**

- [ ] **TASK-5.1:** Implement FR-CHK-001 (One-Time Checkout)
  - **File:** `CheckoutController.java`
  - **Test:** TC-CHK-001, TC-CHK-002
  - **Duration:** 4 hours

- [ ] **TASK-5.2:** Implement FR-CHK-002 (Subscription Checkout)
  - **File:** `PricingPageController.java`
  - **Test:** TC-CHK-003, TC-CHK-004
  - **Duration:** 4 hours

- [ ] **TASK-5.3:** Implement Order Webhook Handler
  - **File:** `OrderWebhookController.java`
  - **Duration:** 4 hours

**Frontend Tasks:**

- [ ] **TASK-5.4:** Implement Checkout Screen
  - **File:** `CheckoutScreen.dart`
  - **Duration:** 3 hours

- [ ] **TASK-5.5:** Implement Plan Selection Screen
  - **File:** `PlanSelectionScreen.dart`
  - **Duration:** 3 hours

- [ ] **TASK-5.6:** Implement Subscription Screen
  - **File:** `SubscriptionScreen.dart`
  - **Duration:** 3 hours

- [ ] **TASK-5.7:** Write Checkout Module Tests
  - **Files:** `checkout_flow_test.dart`
  - **Duration:** 4 hours

**Phase 5 Deliverables:**
- ✅ One-time checkout working
- ✅ Subscription checkout working
- ✅ Payment completion working
- ✅ Order webhook processing
- ✅ All checkout tests passing

---

### Phase 6: Order Management Module (Days 18-20)

**Goal:** User can view order history and details

#### Sprint Backlog:

**Backend Tasks:**

- [ ] **TASK-6.1:** Implement FR-ORD-001 (Order History)
  - **File:** `OrdersController.java`, `OrderService.java`
  - **Test:** TC-ORD-001, TC-ORD-002
  - **Duration:** 3 hours

- [ ] **TASK-6.2:** Implement FR-ORD-002 (Order Details)
  - **File:** `OrderController.java`
  - **Test:** TC-ORD-003
  - **Duration:** 3 hours

**Frontend Tasks:**

- [ ] **TASK-6.3:** Implement Order History Screen
  - **File:** `OrderHistoryPage.dart`, `OrderHistoryScreen.dart`
  - **Duration:** 4 hours

- [ ] **TASK-6.4:** Implement Invoice View Screen
  - **File:** `InvoiceViewScreen.dart`
  - **Duration:** 3 hours

- [ ] **TASK-6.5:** Write Order Module Tests
  - **Files:** `order_history_test.dart`
  - **Duration:** 3 hours

**Phase 6 Deliverables:**
- ✅ Order history displays
- ✅ Order details visible
- ✅ Empty state handled
- ✅ All order tests passing

---

### Phase 7: Integration Testing (Days 21-23)

**Goal:** All modules work together end-to-end

#### Sprint Backlog:

- [ ] **TASK-7.1:** Execute E2E Test - Registration to Checkout
  - **Test:** Full user journey
  - **Duration:** 4 hours

- [ ] **TASK-7.2:** Execute E2E Test - Subscription Flow
  - **Test:** UC-012 complete flow
  - **Duration:** 3 hours

- [ ] **TASK-7.3:** Execute Performance Tests
  - **Tests:** TC-PERF-001, TC-PERF-002
  - **Duration:** 3 hours

- [ ] **TASK-7.4:** Execute Security Tests
  - **Tests:** TC-SEC-001 to TC-SEC-003
  - **Duration:** 3 hours

- [ ] **TASK-7.5:** Fix Integration Issues
  - **Duration:** As needed

**Phase 7 Deliverables:**
- ✅ All E2E tests passing
- ✅ Performance targets met
- ✅ Security tests passing
- ✅ Integration issues resolved

---

### Phase 8: Beta Preparation (Days 24-25)

**Goal:** Ready for beta user testing

#### Sprint Backlog:

- [ ] **TASK-8.1:** Build Release APK
  - **Command:** `flutter build apk --release`
  - **Duration:** 1 hour

- [ ] **TASK-8.2:** Deploy Backend to Staging
  - **Duration:** 2 hours

- [ ] **TASK-8.3:** Prepare Beta User Instructions
  - **File:** `BETA_TESTING_GUIDE.md`
  - **Duration:** 2 hours

- [ ] **TASK-8.4:** Setup Monitoring & Logging
  - **Duration:** 3 hours

- [ ] **TASK-8.5:** Create Feedback Collection System
  - **Duration:** 2 hours

**Phase 8 Deliverables:**
- ✅ Release APK built
- ✅ Staging environment ready
- ✅ Beta user guide created
- ✅ Monitoring active
- ✅ Feedback system ready

---

### Phase 9: Beta Launch (Days 26-30)

**Goal:** MVP launched to beta users

#### Activities:

- [ ] Onboard 10-20 beta users
- [ ] Monitor system performance
- [ ] Collect and triage feedback
- [ ] Fix critical bugs within 24 hours
- [ ] Daily standup to review metrics

**Success Metrics:**
- 50+ user signups
- 5+ subscription purchases
- 10+ one-time orders
- < 1% crash rate
- > 90% payment success rate

---

## External Support Required

### MCP Servers (Recommended)

| MCP Server | Purpose | Priority | Setup Time |
|------------|---------|----------|------------|
| GitHub MCP | Repository management, PR creation | High | 15 mins |
| Filesystem MCP | File operations via AI | Medium | 10 mins |
| PostgreSQL MCP | Database queries | Low | 15 mins |

### VS Code Extensions (Mandatory)

All extensions listed in `Development_Tools_Configuration.md` Section 1

**Installation Time:** 30 mins  
**Command:** Run provided installation script

### Flutter Plugins (Mandatory)

```yaml
dev_dependencies:
  mockito: ^5.4.4
  mocktail: ^1.0.3
  bloc_test: ^9.1.7
  patrol: ^3.7.0
  flutter_lints: ^4.0.0
  build_runner: ^2.4.9
```

**Installation Time:** 10 mins  
**Command:** `flutter pub get`

### Backend Plugins (Mandatory)

Already configured in pom.xml (Section 4 of Tools doc)

**Installation Time:** Automatic via Maven

---

## Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Gradle build issues | Medium | Medium | Use web build as fallback, fix Gradle separately |
| Chargebee API limits | Medium | High | Implement caching, use test mode wisely |
| Test environment issues | Low | High | Use H2 database for unit tests, Testcontainers for integration |
| Scope creep | High | Medium | Strict adherence to BRD, defer non-P0 features |
| Beta user dropoff | Medium | Medium | Engaging onboarding, responsive support |

---

## Next Immediate Actions

### Action 1: Review Documentation (Your Time: 30 mins)
- [ ] Review `BRD_Business_Requirements.md`
- [ ] Review `Test_Cases_Detailed.md`
- [ ] Review `Development_Tools_Configuration.md`
- [ ] Provide feedback/approval

### Action 2: Setup Development Environment (Your Time: 1 hour)
- [ ] Install VS Code extensions
- [ ] Configure MCP servers (if using)
- [ ] Update pubspec.yaml and pom.xml
- [ ] Create test directory structure

### Action 3: Begin Phase 1 Implementation (My Recommendation)
- [ ] Start with TASK-1.1 (VS Code Extensions)
- [ ] Proceed sequentially through Phase 1
- [ ] Report completion of each task
- [ ] Move to Phase 2 after all Phase 1 tasks complete

---

## Do You Want Me To:

**Option A:** Start implementing Phase 1 tasks immediately (recommended)
- I'll create all configuration files
- Install dependencies
- Setup test frameworks
- Create first test files

**Option B:** Wait for your review/feedback on documentation
- You review the 4 documents created
- Provide feedback/approvals
- Then I begin implementation

**Option C:** Focus on specific area first
- e.g., "Just setup testing infrastructure"
- e.g., "Just create backend unit tests"
- e.g., "Just configure CI/CD"

**Please let me know which option you prefer, and I'll proceed accordingly.**

---

**Document Control:**
- **Created:** March 27, 2026
- **Version:** 1.0
- **Status:** Awaiting Direction
