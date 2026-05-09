# Quality Management — BookMyJuice

**Document Version:** 1.1  
**Last Updated:** 2026-05-09

---

## 1. Test Pyramid

```
         ╱  E2E  ╲              ← 5-10 flows (Patrol / integration_test)
        ╱─────────╲
       ╱───────────╲
      ╱ Integration ╲           ← 20-40 tests (Spring Boot + TestContainers)
     ╱───────────────╲
    ╱─────────────────╲
   ╱   Unit Tests    ╲         ← 100+ tests (JUnit5/Mockito + flutter_test/bloc_test)
  ╱─────────────────────╲
```

## 2. Test Ownership

| Layer | Owner | Tools | Location |
|-------|-------|-------|----------|
| Backend Unit | Backend Dev | JUnit5, Mockito | `bmjServer/src/test/java/` |
| Backend Integration | Backend Dev | Spring Boot Test, TestContainers | `bmjServer/src/test/java/` (IT suffix) |
| Flutter Unit | Frontend Dev | flutter_test, bloc_test | `lush/test/` |
| Flutter Widget | Frontend Dev | flutter_test | `lush/test/widgets/` |
| E2E | QA | Patrol, integration_test | `lush/integration_test/`, `lush/patrol_test/` |
| API Performance | QA/Dev | k6 | `bmjServer/scripts/k6/` |
| Security | Security/Dev | OWASP, dependency-check | CI pipeline |

---

## 3. Entry / Exit Criteria

### PR Entry Criteria
- [ ] Code compiles without errors
- [ ] `flutter analyze` passes (no errors)
- [ ] New code includes corresponding tests
- [ ] All existing tests pass locally
- [ ] No hardcoded secrets in code
- [ ] API changes are documented

### PR Exit Criteria
- [ ] All CI checks pass
- [ ] Code coverage ≥ 80% for modified modules
- [ ] No critical security vulnerabilities introduced
- [ ] Tests added for new/changed functionality
- [ ] Documentation updated (if applicable)
- [ ] At least one reviewer approved

### Release Readiness Checklist
- [ ] All quality gates pass
- [ ] No open P0 or P1 bugs
- [ ] E2E tests pass on staging environment
- [ ] Performance tests within thresholds
- [ ] Security scan passed
- [ ] API documentation updated
- [ ] Migration scripts verified
- [ ] Rollback plan documented
- [ ] Monitoring and alerting configured

---

## 4. Regression Policy

- **Full regression** on every release to production
- **Smoke regression** (critical paths only) on every merge to main
- **Automated regression** runs nightly on staging
- **Manual regression** performed by QA for major releases

### Critical Regression Paths
1. User signup → login → browse plans → subscribe → payment → confirmation
2. User login → view subscription → pause → resume → cancel
3. User login → browse one-time products → add to cart → checkout → payment
4. User login → manage address → select delivery slot
5. Admin webhook ingestion → data sync verification

---

## 5. Defect Triage Workflow

```
Bug Reported → Triage (daily)
  ├── P0 Critical → Immediate fix (within 4h)
  ├── P1 Major → Next sprint (within 1 week)
  ├── P2 Minor → Scheduled (within 2 sprints)
  └── P3 Trivial → Backlog
```

### Triage Committee
- QA Lead (owner)
- Engineering Lead
- Product Manager (for priority decisions)

---

## 6. Severity / Priority Definitions

### Severity

| Level | Label | Meaning |
|-------|-------|---------|
| 🔴 Critical | S0 | Security breach, app crash, auth bypass, data corruption, production outage |
| 🟠 Major | S1 | Core feature broken, checkout blocked, slot booking broken, subscription command broken |
| 🟡 Minor | S2 | Partial feature issue, incorrect message, non-blocking UX issue |
| 🟢 Trivial | S3 | Typo, spacing, cosmetic-only issue |

### Priority

| Level | Label | Response Time | Fix Time |
|-------|-------|---------------|----------|
| 🔴 P0 | Critical | 1 hour | 4 hours |
| 🟠 P1 | High | 4 hours | 1 week |
| 🟡 P2 | Medium | 1 day | 2 sprints |
| 🟢 P3 | Low | 1 week | Backlog |

---

## 7. Coverage Thresholds

| Module | Unit Coverage | Integration Coverage | Gate |
|--------|---------------|---------------------|------|
| Auth | ≥ 85% | ≥ 80% | ✅ CI |
| Delivery | ≥ 80% | ≥ 80% | ✅ CI |
| Billing | ≥ 80% | ≥ 80% | ✅ CI |
| Webhooks | ≥ 85% | ≥ 85% | ✅ CI |
| Cache | ≥ 80% | ≥ 80% | ✅ CI |
| Theme | ≥ 90% | N/A | ✅ CI |
| General | ≥ 80% (project-wide) | ≥ 75% | ✅ CI |

---

## 8. Quality Gates (CI Enforced)

| Gate | Condition | Action |
|------|-----------|--------|
| Backend Unit Tests | 100% pass | ❌ Fail build |
| Backend Integration Tests | 100% pass | ❌ Fail build |
| Backend Coverage | ≥ 80% line coverage | ❌ Fail build |
| Flutter Analyze | No errors | ❌ Fail build |
| Flutter Unit Tests | 100% pass | ❌ Fail build |
| Flutter Coverage | ≥ 80% | ❌ Fail build |
| Dependency Check | No critical vulns | ⚠️ Warning |
| API Contract | No breaking changes | ❌ Fail build (if contract testing enabled) |

---

## 9. Environments

| Environment | Purpose | URL | Deploy |
|-------------|---------|-----|--------|
| `local` | Developer testing | `localhost:8080` | `docker-compose up` |
| `ci` | Pipeline verification | Ephemeral | GitHub Actions |
| `staging` | Pre-production validation | `staging.api.bookmyjuice.co.in` | CI on merge to develop |
| `production` | Live user traffic | `api.bookmyjuice.co.in` | CI + manual approval |

---

## 10. Test Cadence

| Cadence | Tests | Environment |
|---------|-------|-------------|
| Per PR | Unit + Integration + Coverage | CI |
| Nightly (12 AM) | Full regression + Performance | Staging |
| Pre-release | Full regression + E2E + Security + Performance | Staging |
| Post-release | Smoke (5 min, 30 min, 2h) | Production |

---

## 11. Traceability

```
Requirements (docs/functional-specs/)
    ↓ maps to
Test Cases (docs/test-registry/TEST_REGISTRY.md)
    ↓ linked to
Bug Reports (docs/test-registry/BUG_REGISTRY.md)
    ↓ tracked via
Coverage Report (docs/test-registry/COVERAGE_REPORT.md)
```

---

## 12. Tools & Integration

| Tool | Use | Integration |
|------|-----|-------------|
| GitHub Actions | CI/CD | Pipeline |
| JaCoCo | Backend coverage | Maven plugin |
| `flutter test --coverage` | Flutter coverage | Flutter CLI |
| TestContainers | Backend integration tests | Maven plugin |
| Patrol | E2E testing | Flutter package |
| k6 | API performance testing | CLI / CI |
| OWASP DC | Dependency security | Maven plugin |
| Flutter Analyze | Dart code quality | CI step |

---

## 13. Flutter Test Status (Current Baseline)

| Test File | Type | Count | Status |
|-----------|------|-------|--------|
| `test/theme/app_theme_test.dart` | Unit | 26 | ✅ All passed |
| `test/theme/theme_cubit_test.dart` | Unit | 12 | ✅ All passed |
| `test/widgets/signup_screen_test.dart` | Widget | 9 | ✅ All passed |
| **Total** | | **68** | ✅ All passed |

---

**Document Maintained By:** QA Team  
**Last Review:** 2026-05-09  
**Next Review:** 2026-06-09
