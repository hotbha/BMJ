# BookMyJuice - Documentation Index

**Last Updated:** June 8, 2026
**Version:** 2.1 (Post-Cleanup)
**Status:** ✅ Complete & Organized

---

## 📚 Documentation Structure

All BookMyJuice documentation is organized into **categories** within the `docs/` folder:

```
docs/
├── business-requirements/      # Business needs, goals, constraints
├── functional-specs/           # System behavior, APIs, data models
├── use-cases/                  # User interaction flows
├── test-cases/                 # Testing specifications
├── test-registry/              # Test tracking, bug registry, coverage
├── architecture/               # Technical decisions, system design
├── guides/                     # How-to guides, setup instructions
└── (root-level .md files)     # Standalone reference docs
```

---

## 📖 Document Catalog

### 1. Business Requirements (`docs/business-requirements/`)

| Document | Description | Audience |
|----------|-------------|----------|
| [BRD_Business_Requirements.md](business-requirements/BRD_Business_Requirements.md) | Complete business requirements document with 6 BRs, product decisions, non-functional requirements, traceability matrix, and risk assessment | Product Owners, PMs, QA |

**Contains:**
- 6 Business Requirements (BR-001 to BR-006) with 7 sub-requirements
- Product decisions & golden rules
- Non-functional requirements (Performance, Security, Reliability, Usability)
- Requirements traceability matrix
- Development phases (9 phases)
- Risk assessment
- Discovered requirements from implementation

---

### 2. Functional Specifications (`docs/functional-specs/`)

| Document | Description | Audience |
|----------|-------------|----------|
| [FUNCTIONAL_SPEC.md](functional-specs/FUNCTIONAL_SPEC.md) | Complete system functional specification including API specs, database schema, frontend architecture | Developers, Architects |

**Contains:**
- System architecture overview
- Complete API specifications (all endpoints)
- Authentication module (unified signup flow)
- Cart module (single-mode constraint, merge logic)
- Checkout module (Chargebee integration)
- Subscription module (pause/resume/cancel with 9 PM cutoff)
- Order module (history, details, invoices)
- Webhook module (idempotent processing)
- Push notification module
- Product catalog module
- Complete MySQL database schema
- Frontend BLoC structure

---

### 3. Use Cases (`docs/use-cases/`)

| Document | Description | Audience |
|----------|-------------|----------|
| [USE_CASES.md](use-cases/USE_CASES.md) | Detailed use cases for all user flows (15 use cases total) | Developers, QA, Product |

**Contains:**
- **Authentication (5 use cases):**
  - UC-AUTH-001: Email-First Signup
  - UC-AUTH-002: Phone-First Signup
  - UC-AUTH-003: Google Signup
  - UC-AUTH-004: User Login
  - UC-AUTH-005: Resend Verification Code
- **Cart & Browsing (2 use cases):**
  - UC-01: Guest Browsing & Cart Building
  - UC-02: Guest Login & Cart Merge
- **Checkout (2 use cases):**
  - UC-03: One-Time Purchase Checkout
  - UC-04: Subscription Purchase Checkout
- **Subscription Management (3 use cases):**
  - UC-05: Pause Subscription
  - UC-06: Resume Subscription
  - UC-07: Cancel Subscription
- **Order Management (2 use cases):**
  - UC-08: View Order History
  - UC-09: View Invoice
- **Notifications (1 use case):**
  - UC-10: Push Notification Deep Link
- Screen flow map

---

### 4. Test Cases (`docs/test-cases/`)

| Document | Description | Audience |
|----------|-------------|----------|
| [TEST_CASES.md](test-cases/TEST_CASES.md) | Comprehensive test specifications (65 test cases across 8 modules) | QA, Developers |

**Contains:**
- Test strategy (4 levels: Unit, Integration, E2E, UAT)
- Test environment setup
- Test data management
- **Authentication Tests (30 cases):** TC-AUTH-001 to TC-AUTH-GS-005
- **Product Catalog Tests (3 cases):** TC-PROD-001 to TC-PROD-003
- **Shopping Cart Tests (10 cases):** TC-CART-001 to TC-CART-010
- **Checkout Tests (4 cases):** TC-CHK-001 to TC-CHK-004
- **Subscription Tests (10 cases):** TC-SUB-001 to TC-SUB-010
- **Order Management Tests (3 cases):** TC-ORD-001 to TC-ORD-003
- **Performance Tests (2 cases):** TC-PERF-001 to TC-PERF-002
- **Security Tests (3 cases):** TC-SEC-001 to TC-SEC-003
- Test execution log template

Additional E2E test specs in `docs/test-cases/`:
- TC_E2E_AUTH.md, TC_E2E_AUTH_SIGNUP_GAPS.md, TC_E2E_CART.md, TC_E2E_CATALOG.md, TC_E2E_CHECKOUT.md, TC_E2E_CROSS_MODULE.md, TC_E2E_DELIVERY.md, TC_E2E_NFR.md, TC_E2E_NOTIFICATIONS.md, TC_E2E_ORDERS.md, TC_E2E_PHONE_UX.md, TC_E2E_PROFILE.md, TC_E2E_SUBSCRIPTIONS.md
- TC_AUTH.md, TC_BILLING.md, TC_CACHE.md, TC_CART.md, TC_PROFILE.md, TC_WEBHOOK.md
- RTM_MATRIX.md, ps_test.md, TEST_PREREQUISITES.md

---

### 5. Test Registry (`docs/test-registry/`)

| Document | Description |
|----------|-------------|
| [TEST_REGISTRY.md](test-registry/TEST_REGISTRY.md) | Central test case registry with cross-references to requirements |
| [BUG_REGISTRY.md](test-registry/BUG_REGISTRY.md) | Bug tracking and resolution log |
| [COVERAGE_REPORT.md](test-registry/COVERAGE_REPORT.md) | Test coverage metrics by module |

---

### 6. Architecture (`docs/architecture/`)

| Document | Description | Status |
|----------|-------------|--------|
| [ADR-001-database-selection.md](architecture/ADR-001-database-selection.md) | Decision: MySQL 8.0 as primary database | ✅ Accepted |
| [ADR-002-state-management-pattern.md](architecture/ADR-002-state-management-pattern.md) | Decision: BLoC Pattern with flutter_bloc | ✅ Accepted |
| [ADR-003-chargebee-integration-strategy.md](architecture/ADR-003-chargebee-integration-strategy.md) | Decision: Webhooks + Local Cache for Chargebee sync | ✅ Accepted |
| [ADR-004-unified-signup-flow.md](architecture/ADR-004-unified-signup-flow.md) | Decision: Multi-step signup with 3 entry points | ✅ Accepted |

---

### 7. Guides (`docs/guides/`)

| Document | Description | Audience |
|----------|-------------|----------|
| [CONTRIBUTING.md](guides/CONTRIBUTING.md) | Development guidelines, coding standards, git workflow, PR process | Developers |
| [DEVELOPMENT_TOOLS.md](guides/DEVELOPMENT_TOOLS.md) | VS Code extensions, MCP servers, test dependencies, CI/CD setup | Developers, DevOps |
| [DEVELOPMENT_SETUP.md](guides/DEVELOPMENT_SETUP.md) | Environment setup instructions | Developers |
| [RELEASE_NOTES.md](guides/RELEASE_NOTES.md) | Release history, beta testing guide, known issues | QA, Product, Beta Users |

---

### 8. Root-Level Reference Documents

The `docs/` root contains standalone reference documents for specific domains:

| Document | Description |
|----------|-------------|
| [API.md](API.md) | Complete API reference for all endpoints |
| [DELIVERY.md](DELIVERY.md) | Delivery domain — schema, endpoints, Flutter screens, cart integration |
| [SUBSCRIPTIONS.md](SUBSCRIPTIONS.md) | Subscription system — screen flow, service/BLoC mapping, Chargebee integration |
| [DESIGN_SYSTEM.md](DESIGN_SYSTEM.md) | Design tokens, components, glassmorphism, theming, Flutter integration |
| [AUDIT_MASTER_REPORT.md](AUDIT_MASTER_REPORT.md) | Codebase audit findings and recommendations |
| [ARCHITECTURE_OVERVIEW.md](ARCHITECTURE_OVERVIEW.md) | High-level system architecture |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Deployment instructions and environment config |
| [CICD_PIPELINE.md](CICD_PIPELINE.md) | CI/CD pipeline configuration |
| [QUALITY_MANAGEMENT.md](QUALITY_MANAGEMENT.md) | QA processes, test pyramid, coverage thresholds |
| [HUMAN_INTERVENTION_REQUIRED.md](HUMAN_INTERVENTION_REQUIRED.md) | Manual steps for setup and maintenance |
| [AUTH_REQUIREMENTS.md](AUTH_REQUIREMENTS.md) | Authentication requirements and flow details |
| [auth_flows.md](auth_flows.md) | Auth flow state machine diagrams |
| [bloc_event_map.md](bloc_event_map.md) | BLoC event-to-state mapping reference |
| [data_models_map.md](data_models_map.md) | Data model cross-reference across layers |
| [CACHING_STRATEGY.md](CACHING_STRATEGY.md) | Caching architecture and invalidation |
| [chargebee_final_state.md](chargebee_final_state.md) | Chargebee integration final state reference |
| [PRICING_STRUCTURE.md](PRICING_STRUCTURE.md) | Pricing model and subscription plans |
| [WEBHOOK_RELIABILITY.md](WEBHOOK_RELIABILITY.md) | Webhook processing reliability |
| [ANDROID_EMULATOR_SETUP.md](ANDROID_EMULATOR_SETUP.md) | Emulator configuration guide |
| [APPIUM_TEST_PLAN.md](APPIUM_TEST_PLAN.md) | Appium test plan and execution guide |

---

## 🎯 Quick Start by Role

### For New Developers
1. Read [CONTRIBUTING.md](guides/CONTRIBUTING.md) — Development setup & guidelines
2. Read [BRD_Business_Requirements.md](business-requirements/BRD_Business_Requirements.md) — Understand what the product does
3. Review [FUNCTIONAL_SPEC.md](functional-specs/FUNCTIONAL_SPEC.md) — Understand system architecture
4. Follow [DEVELOPMENT_TOOLS.md](guides/DEVELOPMENT_TOOLS.md) — Tooling setup

### For Developers (Daily Work)
1. [FUNCTIONAL_SPEC.md](functional-specs/FUNCTIONAL_SPEC.md) — API reference, data models
2. [USE_CASES.md](use-cases/USE_CASES.md) — User flows to implement
3. [architecture/ADR-*.md](architecture/) — Architecture decisions
4. [TEST_CASES.md](test-cases/TEST_CASES.md) — What to test

### For QA/Testers
1. [TEST_CASES.md](test-cases/TEST_CASES.md) — Complete test specifications
2. [BRD_Business_Requirements.md](business-requirements/BRD_Business_Requirements.md) — Requirements traceability
3. [TEST_REGISTRY.md](test-registry/TEST_REGISTRY.md) — Test case coverage & bug tracking
4. [RELEASE_NOTES.md](guides/RELEASE_NOTES.md) — Known issues

### For Product Managers
1. [BRD_Business_Requirements.md](business-requirements/BRD_Business_Requirements.md) — Scope & requirements
2. [USE_CASES.md](use-cases/USE_CASES.md) — User experience flows
3. [RELEASE_NOTES.md](guides/RELEASE_NOTES.md) — Release history & metrics

### For Beta Users
1. [RELEASE_NOTES.md](guides/RELEASE_NOTES.md) — What's included, how to test
2. [USE_CASES.md](use-cases/USE_CASES.md) — Expected user flows
3. [TEST_CASES.md](test-cases/TEST_CASES.md) — What to verify

---

## 📊 Documentation Statistics

| Category | Files | Total Size (Approx.) |
|----------|-------|---------------------|
| Business Requirements | 1 | 500+ lines |
| Functional Specifications | 1 | 800+ lines |
| Use Cases | 2 | 700+ lines |
| Test Cases | 22 | 3,000+ lines |
| Test Registry | 3 | 600+ lines |
| Architecture (ADRs) | 4 | 400+ lines |
| Guides | 4 | 1,600+ lines |
| Root-Level Reference Docs | 20 | 4,500+ lines |
| **TOTAL** | **57** | **12,000+ lines** |

---

## 🔍 How Documentation Was Consolidated

This documentation structure was created by consolidating **61 scattered .md files** from:
- Root directory (13 files)
- docs/ folder (24 files)
- bmjServer/ folder (9 files)
- lush/ folder (14 files)
- .github/ folder (1 file)

**Redundant files removed:**
- Multiple status update files (PROJECT_STATUS_SUMMARY, etc.)
- Duplicate implementation completion notices
- Separate undocumented requirements files (now in BRD appendix)
- Component-specific README files (consolidated into guides)
- Compliance/Privacy doc (described non-existent endpoints)
- Native billing doc (superseded by Chargebee Hosted Pages)
- Transient debugging notes
- One-time test artifacts
- Duplicate E2E bug tracker (consolidated into test-registry/)
- Manual testing guide (superseded by automated tests)
- Full backlog (not a living document)

**Files merged:**
- Delivery domain + Flutter delivery integration → single `DELIVERY.md`
- Subscription screens spec + service map → single `SUBSCRIPTIONS.md`
- Color system + Design system + Flutter integration → single `DESIGN_SYSTEM.md`

**Result:** Clean, minimal structure with maximum content per document.

---

## 📝 Document Maintenance

### Update Frequency
- **BRD:** Update when business requirements change
- **Functional Spec:** Update when APIs or architecture change
- **Use Cases:** Update when user flows change
- **Test Cases:** Update during test execution
- **Architecture:** Update only when new ADRs are created
- **Guides:** Update when tooling or processes change

### Version Control
All documentation is version-controlled in Git. Major updates should be committed with descriptive messages.

---

## 📞 Support

For questions about documentation:
- **Email:** dev@bookmyjuice.co.in
- **Slack:** #bookmyjuice-dev

---

**Documentation Status:** ✅ Complete & Organized
**Next Review:** June 22, 2026