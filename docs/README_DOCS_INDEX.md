# BookMyJuice - Documentation Index

**Last Updated:** March 27, 2026  
**Location:** x:\BMJ\docs  

---

## 📚 Complete Documentation List

All official BookMyJuice documentation is now centralized in the `docs/` folder for better tracking and version control.

---

## 🎯 Core Documentation (NEW - March 27, 2026)

### 1. Business Requirements Document
**File:** `BRD_Business_Requirements.md`  
**Size:** 500+ lines  
**Purpose:** Complete business & functional requirements with traceability matrix

**Contents:**
- 6 Business Requirements (BR-001 to BR-006)
- 14 Functional Requirements (FR-AUTH-001 to FR-ORD-002)
- 10 Non-Functional Requirements (NFR-001 to NFR-010)
- Requirements Traceability Matrix
- 14 Use Case Specifications
- Risk Assessment
- Development Phases (9 phases over 30 days)

**Linked To:** Test Cases, Implementation Plan

---

### 2. Detailed Test Cases
**File:** `Test_Cases_Detailed.md`  
**Size:** 600+ lines  
**Purpose:** Professional test cases with pass/fail criteria

**Contents:**
- 30 Test Cases across 7 sections
- Authentication Tests (TC-AUTH-001 to TC-AUTH-008)
- Product Catalog Tests (TC-PROD-001 to TC-PROD-003)
- Shopping Cart Tests (TC-CART-001 to TC-CART-007)
- Checkout Tests (TC-CHK-001 to TC-CHK-004)
- Order Management Tests (TC-ORD-001 to TC-ORD-003)
- Performance Tests (TC-PERF-001 to TC-PERF-002)
- Security Tests (TC-SEC-001 to TC-SEC-003)

**Test Status:** ⏳ All Pending (Ready for Execution)

---

### 3. Development Tools Configuration
**File:** `Development_Tools_Configuration.md`  
**Size:** 400+ lines  
**Purpose:** Complete setup guide for professional development environment

**Contents:**
- 15+ VS Code Extensions (installation commands)
- MCP Servers Configuration (GitHub, Filesystem, PostgreSQL)
- Flutter Test Dependencies (mockito, bloc_test, patrol)
- Backend Test Dependencies (JUnit 5, Mockito, Testcontainers)
- Test Directory Structure (complete hierarchy)
- CI/CD Pipeline Configuration (GitHub Actions)
- Database Tools (SQLTools, Flyway)
- API Development Tools (REST Client, Swagger)
- Code Quality Tools (linting, coverage)
- Development Environment Checklist

**Status:** ✅ All External Support Resolved

---

### 4. SDLC Implementation Plan
**File:** `SDLC_Implementation_Plan.md`  
**Size:** 300+ lines  
**Purpose:** 9-phase implementation roadmap following professional SDLC

**Contents:**
- Phase 1: Environment Setup (Days 1-2)
- Phase 2: Authentication Module (Days 3-7)
- Phase 3: Product Catalog (Days 8-10)
- Phase 4: Shopping Cart (Days 11-13)
- Phase 5: Checkout Module (Days 14-17)
- Phase 6: Order Management (Days 18-20)
- Phase 7: Integration Testing (Days 21-23)
- Phase 8: Beta Preparation (Days 24-25)
- Phase 9: Beta Launch (Days 26-30)

**Discrete Tasks:** 50+ tasks with duration estimates

---

### 5. External Support Complete
**File:** `EXTERNAL_SUPPORT_COMPLETE.md`  
**Purpose:** Summary of all external dependencies and tools configured

**Contents:**
- ✅ VS Code Extensions (configuration provided)
- ✅ Flutter Test Dependencies (INSTALLED)
- ✅ Backend Test Dependencies (INSTALLED)
- ✅ Test Directory Structure (CREATED)
- ✅ CI/CD Pipeline (CONFIGURED)
- ✅ Test Helper Files (CREATED)
- ✅ Analysis Options (CONFIGURED)
- ✅ First Unit Test Files (CREATED)

**Next Steps:** Run `flutter pub get` and `mvnw clean install`

---

### 6. Release Notes
**File:** `RELEASE_NOTES.md`  
**Purpose:** Release history and launch documentation

**Contents:**
- March 27, 2026 - Professional SDLC Setup
- March 27, 2026 - MVP Launch Preparation
- February 26, 2026 - E2E Signup Testing
- MVP Feature Status
- Known Issues
- Deployment Options
- Beta Launch Schedule
- Success Metrics

---

## 📐 Architecture Decision Records (ADR)

### ADR-001: Database Selection
**File:** `architecture/ADR-001-database-selection.md`  
**Status:** ACCEPTED  
**Decision:** MySQL 8.0 as primary database

**Rationale:**
- Team expertise
- Spring Boot integration
- Cost-effective
- Chargebee compatibility

---

### ADR-002: State Management Pattern
**File:** `architecture/ADR-002-state-management-pattern.md`  
**Status:** ACCEPTED  
**Decision:** BLoC Pattern with flutter_bloc

**Rationale:**
- Separation of concerns
- Testability
- Scalability
- Team familiarity

---

## 🎨 Design & API Documentation

### Design System
**File:** `DESIGN_SYSTEM.md`  
**Size:** 800+ lines  
**Purpose:** Complete UI/UX design system

**Contents:**
- Design Principles (6 principles)
- Color Palette (brand colors, semantic colors)
- Typography (type scale, font families)
- Spacing & Layout (8pt grid system)
- Icons (guidelines, library)
- Components (buttons, inputs, cards, dialogs)
- Patterns (navigation, authentication flow)
- Accessibility (WCAG 2.1 AA compliance)
- Resources & Tools

---

### API Documentation
**File:** `API.md`  
**Size:** 600+ lines  
**Purpose:** Complete API reference with examples

**Contents:**
- Overview & Base URLs
- Authentication (JWT, token lifecycle)
- API Endpoints:
  - Authentication (signin, signup, refresh, Google, OTP)
  - User Management (profile, addresses)
  - Subscription Management (plans, checkout, pause, cancel)
  - Order Management (history, details, one-time checkout)
  - Cart Management (add, update, remove, total)
  - Products (list, details)
  - Health Check
- Error Handling (standard format, status codes)
- Rate Limiting (backend & frontend limits)
- Webhooks (Chargebee integration)
- SDKs & Examples (Flutter, cURL)

**Interactive Docs:** Available at `/swagger-ui.html`

---

## 📋 Contributing Guidelines

**File:** `CONTRIBUTING.md` (Root Level)  
**Size:** 600+ lines  
**Purpose:** Development guidelines and coding standards

**Contents:**
- Code of Conduct
- Development Setup (prerequisites, quick start)
- Git Workflow (branch naming, commit conventions)
- Coding Standards (Java/Spring Boot, Flutter/Dart)
- Testing Guidelines (unit, widget, E2E)
- Pull Request Process (checklist, template)
- Architecture Decisions (ADR template)

---

## 🤖 AI Agent Instructions

**File:** `.github/copilot-instructions.md` (Root Level)  
**Purpose:** Instructions for AI coding assistants

**Contents:**
- Project structure overview
- Key build & test commands
- Critical patterns & conventions
- Common developer workflows
- Important notes about Chargebee integration

---

## 📁 Legacy Documentation (Pre-March 27, 2026)

### Backend README
**File:** `bmjServer/README.md` & `bmjServer/README_COMBINED.md`  
**Status:** Historical reference  
**Note:** Superseded by new API.md and BRD

### Frontend README
**File:** `lush/README.md` & `lush/README_COMBINED.md`  
**Status:** Historical reference  
**Note:** Superseded by new DESIGN_SYSTEM.md and API.md

### iOS Assets README
**File:** `lush/ios/Runner/Assets.xcassets/LaunchImage.imageset/README.md`  
**Status:** System-generated  
**Note:** Keep as-is (Xcode asset documentation)

---

## 🗂️ Document Organization

### Before Cleanup (March 27, 2026)
```
x:\BMJ\
├── MVP_LAUNCH_READY.md          ❌ Redundant
├── MVP_LAUNCH_PLAN.md           ❌ Redundant
├── MVP_BUILD_STATUS.md          ❌ Redundant
├── MVP_BUILD_STATUS_UPDATE.md   ❌ Redundant
├── MVP_LAUNCH_SUMMARY.md        ❌ Redundant
├── INTEGRATION_ISSUES.md        ❌ Redundant
├── BETA_TESTING_GUIDE.md        ❌ Redundant
├── README_WORKSPACE.md          ❌ Redundant
├── SETUP_COMPLETE.md            ❌ Redundant
├── E2E_SIGNUP_TEST_REPORT.md    ❌ Redundant
├── E2E_SIGNUP_TEST_SUCCESS.md   ❌ Redundant
├── E2E_TEST_FINDINGS.md         ❌ Redundant
└── docs/                        ✅ Organized
```

### After Cleanup
```
x:\BMJ\
├── docs/
│   ├── BRD_Business_Requirements.md      ✅ NEW
│   ├── Test_Cases_Detailed.md            ✅ NEW
│   ├── Development_Tools_Configuration.md ✅ NEW
│   ├── SDLC_Implementation_Plan.md       ✅ NEW
│   ├── EXTERNAL_SUPPORT_COMPLETE.md      ✅ NEW
│   ├── RELEASE_NOTES.md                  ✅ NEW
│   ├── DESIGN_SYSTEM.md                  ✅ Existing
│   ├── API.md                            ✅ Existing
│   └── architecture/
│       ├── ADR-001-database-selection.md ✅ Existing
│       └── ADR-002-state-management-pattern.md ✅ Existing
├── CONTRIBUTING.md                       ✅ Existing (Root level - keep)
└── .github/copilot-instructions.md       ✅ Existing (Root level - keep)
```

---

## 📊 Documentation Statistics

| Category | Count | Total Lines |
|----------|-------|-------------|
| New Documentation (March 27) | 6 | 2,500+ |
| Architecture Decision Records | 2 | 400+ |
| Design & API Docs | 2 | 1,400+ |
| Contributing Guidelines | 1 | 600+ |
| AI Instructions | 1 | 200+ |
| **TOTAL** | **12** | **5,100+** |

---

## 🔍 Quick Reference

### For New Developers
1. Start with `CONTRIBUTING.md` - Development setup & guidelines
2. Read `BRD_Business_Requirements.md` - Understand what to build
3. Review `Test_Cases_Detailed.md` - Understand testing requirements
4. Follow `SDLC_Implementation_Plan.md` - Step-by-step implementation

### For Developers
1. `DESIGN_SYSTEM.md` - UI/UX guidelines
2. `API.md` - API reference
3. `Development_Tools_Configuration.md` - Tooling setup
4. `architecture/ADR-*.md` - Architecture decisions

### For QA/Testers
1. `Test_Cases_Detailed.md` - Complete test cases
2. `BRD_Business_Requirements.md` - Requirements traceability
3. `RELEASE_NOTES.md` - Known issues

### For Project Managers
1. `SDLC_Implementation_Plan.md` - Timeline & phases
2. `BRD_Business_Requirements.md` - Scope & requirements
3. `RELEASE_NOTES.md` - Release history & metrics

---

## ✅ Document Control

| Action | Date | Performed By | Result |
|--------|------|--------------|--------|
| Initial Documentation | 2026-02-26 | Development Team | E2E Test Reports |
| MVP Launch Docs | 2026-03-27 | Development Team | MVP Status Reports |
| **Professional SDLC Docs** | **2026-03-27** | **Development Team** | **✅ Complete** |
| Documentation Cleanup | 2026-03-27 | Development Team | ✅ 11 files consolidated |
| External Support Setup | 2026-03-27 | Development Team | ✅ Complete |

---

## 📞 Support

For questions about documentation:
- Email: dev@bookmyjuice.co.in
- Slack: #bookmyjuice-dev
- Review Meeting: April 4, 2026

---

**Documentation Status:** ✅ Complete & Centralized  
**Next Review:** April 4, 2026 (Post-Beta Review)
