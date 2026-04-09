# Architecture Documentation Updates - Unified Signup Flow

**Date:** March 29, 2026  
**Version:** 1.0  
**Status:** Complete

---

## Summary

This document summarizes all architecture and documentation updates made to support the Unified Signup Flow implementation.

---

## New Documents Created

### 1. ADR-004: Unified Signup Flow Architecture

**Location:** `docs/architecture/ADR-004-unified-signup-flow.md`

**Contents:**
- Context and business requirements (BR-AUTH-001 to BR-AUTH-008)
- Multi-step signup architecture decision
- State management pattern (BLoC)
- API endpoint design
- Verification code architecture
- Database schema (no changes required)
- Security architecture (password, JWT, rate limiting)
- Chargebee integration flow
- Frontend screen architecture
- Consequences (positive/negative)
- Risks and mitigations
- Implementation status
- Compliance (RBI, GDPR, OWASP)

**Key Decisions:**
- 3 entry points (Email, Phone, Google)
- 6-digit verification codes (10-min expiry)
- 15-minute JWT expiration
- BCrypt password hashing
- Rate limiting (5/hour per email/phone)
- Unified signup API endpoint

---

### 2. ARCHITECTURE_OVERVIEW.md

**Location:** `docs/ARCHITECTURE_OVERVIEW.md`

**Contents:**
- System architecture diagram
- Application architecture (Flutter + Spring Boot)
- Data architecture (MySQL schema, data flow)
- Security architecture (authentication flow, security measures)
- Integration architecture (Chargebee boundaries, API endpoints)
- ADR index (all 4 ADRs)
- Deployment architecture (dev + production)
- Monitoring & observability

**Updates from v1.0:**
- Added unified signup flow to authentication section
- Updated ADR index with ADR-004
- Added 11 new signup screens to Flutter structure
- Added email verification service to backend structure
- Updated security measures table

---

### 3. UNIFIED_SIGNUP_TEST_CASES.md

**Location:** `UNIFIED_SIGNUP_TEST_CASES.md` (root directory)

**Contents:**
- Test environment setup
- 25 detailed test cases:
  - Email-First Flow (6 tests)
  - Phone-First Flow (3 tests)
  - Google Signup (2 tests)
  - Address Entry (3 tests)
  - Password Creation (4 tests)
  - API Tests (4 tests)
  - Integration Tests (3 tests)
- Test execution commands
- Manual test assignments
- Defect log template
- Sign-off section

**Automated Tests:**
- TC-AUTH-EF-001: Email-First Successful Signup
- TC-AUTH-PF-001: Phone-First Successful Signup
- TC-AUTH-API-001: Send Email Verification
- TC-AUTH-INT-003: Login → Logout

---

### 4. UNIFIED_SIGNUP_USE_CASES.md

**Location:** `UNIFIED_SIGNUP_USE_CASES.md` (root directory)

**Contents:**
- Actor definitions (primary and secondary)
- Use case diagram (ASCII art)
- 5 detailed use cases:
  - UC-AUTH-001: Email-First Signup
  - UC-AUTH-002: Phone-First Signup
  - UC-AUTH-003: Google Signup
  - UC-AUTH-004: Resend Verification Code
  - UC-AUTH-005: Password Creation
- Activity flow diagrams
- Exception handling
- Error messages catalog
- Data schema appendix

**Use Case Structure:**
- Goal, scope, level
- Primary actor
- Stakeholders and interests
- Preconditions
- Success guarantee (postconditions)
- Main success scenario (step-by-step)
- Extensions (alternate flows)
- Special requirements
- Technology & data variations

---

### 5. UNIFIED_SIGNUP_IMPLEMENTATION_SUMMARY.md

**Location:** `UNIFIED_SIGNUP_IMPLEMENTATION_SUMMARY.md` (root directory)

**Contents:**
- Executive summary
- Key changes overview (files created/modified)
- API endpoints (new and enhanced)
- Signup flows (3 flow diagrams)
- Data validation rules
- Security features
- Integration points (Chargebee, Google, Email, SMS)
- Testing status (automated and manual)
- Migration notes
- Known limitations
- Success metrics
- Rollout plan
- Support & maintenance

**Files Created/Modified:**
- Flutter: 11 screens, 3 BLoC files, 1 main.dart, 1 userRepository.dart
- Backend: 3 DTOs, 1 service, 1 controller, 1 config
- Documentation: 4 new documents, 1 updated (requirements.yaml)

---

## Updated Documents

### 1. requirements.yaml

**Location:** `requirements.yaml` (root directory)

**Updates:**
- Added `unified_signup_flow` section with:
  - 8 Business Requirements (BR-AUTH-001 to BR-AUTH-008)
  - 9 Functional Requirements (FR-AUTH-001 to FR-AUTH-009)
  - 3 Use Cases (UC-AUTH-001 to UC-AUTH-003)
  - 25 Test Cases (TC-AUTH-EF-001 to TC-AUTH-API-004)
  - 5 User Stories (US-AUTH-001 to US-AUTH-005)
  - Data validation rules for all fields
  - Error messages catalog

**MVP-AUTH Items Updated:**
- MVP-AUTH-001: Email Login/Signup (status: implemented, notes updated)
- MVP-AUTH-002: Google Sign-In (status: implemented, notes updated)
- MVP-AUTH-003: Auto-login with JWT (status: implemented)
- MVP-AUTH-004: Logout (status: implemented)
- MVP-AUTH-005: Phone OTP Verification (status: implemented, NEW)
- MVP-AUTH-006: Email Verification Code (status: implemented, NEW)
- MVP-AUTH-007: Unified Signup Flow (status: implemented, NEW)

---

### 2. docs/Test_Cases_Detailed.md

**Location:** `docs/Test_Cases_Detailed.md`

**Updates:**
- Version bumped to 3.0
- Added ADR-004 reference
- Added Unified Signup Flow section
- Updated test case naming convention with suffixes:
  - `-EF` (Email-First)
  - `-PF` (Phone-First)
  - `-GS` (Google Signup)
  - `-AE` (Address Entry)
  - `-PC` (Password Creation)
- Added reference to `../UNIFIED_SIGNUP_TEST_CASES.md`

---

### 3. docs/architecture/ (Directory)

**New File:**
- `ADR-004-unified-signup-flow.md`

**Existing Files (unchanged):**
- `ADR-001-database-selection.md`
- `ADR-002-state-management-pattern.md`
- `ADR-003-chargebee-integration-strategy.md`

---

## Documentation Cross-References

```
requirements.yaml
    ├── References: ADR-004, UNIFIED_SIGNUP_TEST_CASES.md, UNIFIED_SIGNUP_USE_CASES.md
    └── Contains: Business requirements, functional requirements, test cases (summary)

ADR-004-unified-signup-flow.md
    ├── References: requirements.yaml, ADR-003, UNIFIED_SIGNUP_IMPLEMENTATION_SUMMARY.md
    └── Contains: Architecture decision, technical design, security, compliance

ARCHITECTURE_OVERVIEW.md
    ├── References: All 4 ADRs, API.md, BACKEND_FRONTEND_STATUS.md
    └── Contains: System overview, component architecture, deployment

UNIFIED_SIGNUP_TEST_CASES.md
    ├── References: requirements.yaml, ADR-004, physical_device_template_test.dart
    └── Contains: 25 detailed test cases, execution commands

UNIFIED_SIGNUP_USE_CASES.md
    ├── References: requirements.yaml, ADR-004
    └── Contains: Actor definitions, use cases, activity flows, error messages

UNIFIED_SIGNUP_IMPLEMENTATION_SUMMARY.md
    ├── References: All above documents
    └── Contains: Implementation status, files changed, rollout plan

Test_Cases_Detailed.md
    ├── References: ADR-004, UNIFIED_SIGNUP_TEST_CASES.md
    └── Contains: Legacy test cases + unified signup test references
```

---

## Architecture Decision Records Summary

| ADR | Title | Key Decision | Status |
|-----|-------|--------------|--------|
| ADR-001 | Database Selection | MySQL 8.0 | ACCEPTED |
| ADR-002 | State Management | BLoC Pattern | ACCEPTED |
| ADR-003 | Chargebee Integration | Webhooks + Local Cache | ACCEPTED |
| ADR-004 | Unified Signup Flow | Multi-step with 3 entry points | ACCEPTED |

---

## Document Maintenance

### Review Schedule

| Document | Review Frequency | Next Review |
|----------|-----------------|-------------|
| ADR-004 | Monthly (until beta launch) | 2026-04-29 |
| ARCHITECTURE_OVERVIEW.md | Monthly | 2026-04-29 |
| UNIFIED_SIGNUP_TEST_CASES.md | Weekly (during testing) | 2026-04-05 |
| UNIFIED_SIGNUP_USE_CASES.md | Monthly | 2026-04-29 |
| UNIFIED_SIGNUP_IMPLEMENTATION_SUMMARY.md | Weekly (until production) | 2026-04-05 |
| requirements.yaml | Bi-weekly | 2026-04-12 |

### Change Log

| Date | Document | Change | Author |
|------|----------|--------|--------|
| 2026-03-29 | All | Initial creation for unified signup flow | Engineering Team |

---

## Access Paths

### For Developers

1. **Start Here:** `UNIFIED_SIGNUP_IMPLEMENTATION_SUMMARY.md` (technical overview)
2. **Architecture:** `ADR-004-unified-signup-flow.md` (design decisions)
3. **Testing:** `UNIFIED_SIGNUP_TEST_CASES.md` (test cases)
4. **Code:** See implementation summary file list

### For QA

1. **Start Here:** `UNIFIED_SIGNUP_TEST_CASES.md` (test execution)
2. **Requirements:** `requirements.yaml` (unified_signup_flow section)
3. **Use Cases:** `UNIFIED_SIGNUP_USE_CASES.md` (user flows)
4. **Test Script:** `lush/integration_test/physical_device_template_test.dart`

### For Product Managers

1. **Start Here:** `requirements.yaml` (business requirements)
2. **User Flows:** `UNIFIED_SIGNUP_USE_CASES.md` (use cases)
3. **Status:** `UNIFIED_SIGNUP_IMPLEMENTATION_SUMMARY.md` (implementation status)

### For Stakeholders

1. **Start Here:** `UNIFIED_SIGNUP_IMPLEMENTATION_SUMMARY.md` (executive summary)
2. **Architecture:** `ARCHITECTURE_OVERVIEW.md` (system overview)

---

## Compliance Mapping

| Requirement | ADR-004 Section | Test Case | Status |
|-------------|-----------------|-----------|--------|
| BR-AUTH-001 (Email required) | Section 1 | TC-AUTH-EF-001 | ✅ Implemented |
| BR-AUTH-002 (Phone required) | Section 1 | TC-AUTH-PF-001 | ✅ Implemented |
| BR-AUTH-003 (Address required) | Section 1 | TC-AUTH-AE-001 | ✅ Implemented |
| BR-AUTH-004 (Multiple entry points) | Section 1 | TC-AUTH-EF-001, PF-001, GS-001 | ✅ Implemented |
| BR-AUTH-005 (Email verification) | Section 4 | TC-AUTH-API-001 | ✅ Implemented |
| BR-AUTH-006 (Phone verification) | Section 4 | TC-AUTH-PF-001 | ✅ Implemented |
| BR-AUTH-007 (Google signup) | Section 7 | TC-AUTH-GS-001 | ✅ Implemented |
| BR-AUTH-008 (Strong password) | Section 6 | TC-AUTH-PC-001 | ✅ Implemented |

---

## Next Steps

### Documentation

- [ ] Add sequence diagrams to ADR-004
- [ ] Add performance benchmarks to implementation summary
- [ ] Add user analytics plan to requirements
- [ ] Create video demo of signup flow

### Testing

- [ ] Execute all 25 manual test cases
- [ ] Achieve 90%+ test automation coverage
- [ ] Performance test (signup completion < 3 seconds)
- [ ] Security audit (OWASP compliance)

### Deployment

- [ ] Update API documentation (Swagger)
- [ ] Create release notes
- [ ] Update user guide
- [ ] Train support team on new flow

---

**Document Prepared By:** Engineering Team  
**Review Status:** Complete  
**Approved For:** Development, QA, Stakeholder Review
