# BookMyJuice - Documentation Index

**Last Updated:** April 11, 2026
**Version:** 2.0 (Consolidated)
**Status:** ✅ Complete & Organized

---

## 📚 Documentation Structure

All BookMyJuice documentation is now organized into **7 categories** within the `docs/` folder:

```
docs/
├── business-requirements/      # Business needs, goals, constraints
├── functional-specs/           # System behavior, APIs, data models
├── use-cases/                  # User interaction flows
├── test-cases/                 # Testing specifications
├── architecture/               # Technical decisions, system design
├── implementation-status/      # Progress tracking, build status
└── guides/                     # How-to guides, setup instructions
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

---

### 5. Architecture (`docs/architecture/`)

| Document | Description | Status |
|----------|-------------|--------|
| [ARCHITECTURE_OVERVIEW.md](architecture/ARCHITECTURE_OVERVIEW.md) | High-level system architecture, data flow, security architecture | ✅ Complete |
| [ADR-001-database-selection.md](architecture/ADR-001-database-selection.md) | Decision: MySQL 8.0 as primary database | ✅ Accepted |
| [ADR-002-state-management-pattern.md](architecture/ADR-002-state-management-pattern.md) | Decision: BLoC Pattern with flutter_bloc | ✅ Accepted |
| [ADR-003-chargebee-integration-strategy.md](architecture/ADR-003-chargebee-integration-strategy.md) | Decision: Webhooks + Local Cache for Chargebee sync | ✅ Accepted |
| [ADR-004-unified-signup-flow.md](architecture/ADR-004-unified-signup-flow.md) | Decision: Multi-step signup with 3 entry points | ✅ Accepted |

---

### 6. Implementation Status (`docs/implementation-status/`)

| Document | Description | Status |
|----------|-------------|--------|
| [IMPLEMENTATION_STATUS.md](implementation-status/IMPLEMENTATION_STATUS.md) | Complete MVP implementation status, feature checklist, deployment readiness | ✅ MVP Complete |

**Contains:**
- Executive summary
- Feature implementation status (all modules)
- Backend implementation (controllers, services, database)
- Frontend implementation (BLoCs, screens, widgets)
- Integration status (external & internal)
- Testing status (automated & manual)
- Known issues (non-blocking)
- Deployment readiness checklist
- Beta testing metrics

---

### 7. Guides (`docs/guides/`)

| Document | Description | Audience |
|----------|-------------|----------|
| [CONTRIBUTING.md](guides/CONTRIBUTING.md) | Development guidelines, coding standards, git workflow, PR process | Developers |
| [DEVELOPMENT_TOOLS.md](guides/DEVELOPMENT_TOOLS.md) | VS Code extensions, MCP servers, test dependencies, CI/CD setup | Developers, DevOps |
| [RELEASE_NOTES.md](guides/RELEASE_NOTES.md) | Release history, beta testing guide, known issues | QA, Product, Beta Users |

---

## 🎯 Quick Start by Role

### For New Developers
1. Read [CONTRIBUTING.md](guides/CONTRIBUTING.md) - Development setup & guidelines
2. Read [BRD_Business_Requirements.md](business-requirements/BRD_Business_Requirements.md) - Understand what the product does
3. Review [FUNCTIONAL_SPEC.md](functional-specs/FUNCTIONAL_SPEC.md) - Understand system architecture
4. Follow [DEVELOPMENT_TOOLS.md](guides/DEVELOPMENT_TOOLS.md) - Tooling setup

### For Developers (Daily Work)
1. [FUNCTIONAL_SPEC.md](functional-specs/FUNCTIONAL_SPEC.md) - API reference, data models
2. [USE_CASES.md](use-cases/USE_CASES.md) - User flows to implement
3. [architecture/ADR-*.md](architecture/) - Architecture decisions
4. [TEST_CASES.md](test-cases/TEST_CASES.md) - What to test

### For QA/Testers
1. [TEST_CASES.md](test-cases/TEST_CASES.md) - Complete test specifications
2. [BRD_Business_Requirements.md](business-requirements/BRD_Business_Requirements.md) - Requirements traceability
3. [IMPLEMENTATION_STATUS.md](implementation-status/IMPLEMENTATION_STATUS.md) - What's ready to test
4. [RELEASE_NOTES.md](guides/RELEASE_NOTES.md) - Known issues

### For Product Managers
1. [BRD_Business_Requirements.md](business-requirements/BRD_Business_Requirements.md) - Scope & requirements
2. [IMPLEMENTATION_STATUS.md](implementation-status/IMPLEMENTATION_STATUS.md) - Timeline & progress
3. [USE_CASES.md](use-cases/USE_CASES.md) - User experience flows
4. [RELEASE_NOTES.md](guides/RELEASE_NOTES.md) - Release history & metrics

### For Beta Users
1. [RELEASE_NOTES.md](guides/RELEASE_NOTES.md) - What's included, how to test
2. [USE_CASES.md](use-cases/USE_CASES.md) - Expected user flows
3. [TEST_CASES.md](test-cases/TEST_CASES.md) - What to verify

---

## 📊 Documentation Statistics

| Category | Files | Total Size (Approx.) |
|----------|-------|---------------------|
| Business Requirements | 1 | 500+ lines |
| Functional Specifications | 1 | 800+ lines |
| Use Cases | 1 | 600+ lines |
| Test Cases | 1 | 900+ lines |
| Architecture | 5 (4 ADRs + 1 overview) | 1000+ lines |
| Implementation Status | 1 | 500+ lines |
| Guides | 3 | 1500+ lines |
| **TOTAL** | **13** | **5,800+ lines** |

---

## 🔍 How Documentation Was Consolidated

This documentation structure was created by consolidating **61 scattered .md files** from:
- Root directory (13 files)
- docs/ folder (24 files)
- bmjServer/ folder (9 files)
- lush/ folder (14 files)
- .github/ folder (1 file)

**Redundant files removed:**
- Multiple status update files (MVP_LAUNCH_SUCCESS, PROJECT_STATUS_SUMMARY, etc.)
- Duplicate implementation completion notices
- Separate undocumented requirements files (now in BRD appendix)
- Component-specific README files (consolidated into guides)

**Result:** Clean, minimal structure with maximum content per document.

---

## 📝 Document Maintenance

### Update Frequency
- **BRD:** Update when business requirements change
- **Functional Spec:** Update when APIs or architecture change
- **Use Cases:** Update when user flows change
- **Test Cases:** Update during test execution
- **Architecture:** Update only when new ADRs are created
- **Implementation Status:** Update at end of each development phase
- **Guides:** Update when tooling or processes change

### Version Control
All documentation is version-controlled in Git. Major updates should be committed with descriptive messages.

---

## 📞 Support

For questions about documentation:
- **Email:** dev@bookmyjuice.co.in
- **Slack:** #bookmyjuice-dev
- **Next Review:** April 25, 2026 (Post-Beta Review)

---

**Documentation Status:** ✅ Complete & Organized
**Next Review:** April 25, 2026
