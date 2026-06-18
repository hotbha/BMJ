# Quality Management — BookMyJuice

**Document Version:** 1.2  
**Last Updated:** 2026-06-10

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
| Flutter Widget | Frontend Dev | flutter_test | `lush/test/widget/` |
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

---

## 4. Bug Tracking

| Tool | Location |
|------|----------|
| Bug Registry | `docs/test-registry/BUG_REGISTRY.md` |
| Bug Lifecycle | NEW → TRIAGED → FIXING → VERIFIED → CLOSED |
| Severity Labels | S0 (Critical) → S3 (Trivial) |
| Priority Labels | P0 (Critical) → P3 (Low) |

---

## 5. Escalation Matrix

| Role | Person | Responsibility |
|------|--------|----------------|
| QA Lead | TBD | Test strategy, test review, bug triage |
| Frontend Dev Lead | TBD | Flutter test implementation, code review |
| Backend Dev Lead | TBD | Backend test implementation, code review |
| DevOps | TBD | CI/CD pipeline, environment management |

---

## 6. Severity & Priority

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
| `test/unit/bloc/auth_bloc_test.dart` | Unit | 21 | ✅ All passed |
| `test/unit/bloc/cart_bloc_test.dart` | Unit | 14 | ✅ All passed |
| `test/unit/bloc/products_bloc_test.dart` | Unit | 4 | ✅ All passed |
| `test/unit/bloc/product_catalog_bloc_test.dart` | Unit | 6 | ✅ All passed |
| `test/unit/bloc/notification_bloc_test.dart` | Unit | 12 | ✅ All passed |
| `test/unit/bloc/user_bloc_test.dart` | Unit | 6 | ✅ All passed |
| `test/unit/models/notification_model_test.dart` | Unit | 9 | ✅ All passed |
| `test/unit/models/order_model_test.dart` | Unit | 17 | ✅ All passed |
| `test/unit/models/products_model_test.dart` | Unit | 3 | ✅ All passed |
| `test/unit/models/referral_info_test.dart` | Unit | 7 | ✅ All passed |
| `test/unit/services/order_service_test.dart` | Unit | 13 | ✅ All passed |
| `test/unit/services/cart_service_test.dart` | Unit | 19 | ✅ All passed |
| `test/unit/services/subscription_service_test.dart` | Unit | 23 | ✅ All passed |
| `test/unit/repositories/products_repository_test.dart` | Unit | 17 | ✅ All passed |
| `test/unit/repositories/referral_repository_test.dart` | Unit | 7 | ✅ All passed |
| `test/subscription_bloc_test.dart` | Unit | 17 | ✅ All passed |
| `test/subscription_screens_test.dart` | Widget | 14 | ✅ All passed |
| `test/order_flow_test.dart` | Integration | 6 | ✅ All passed |
| `test/bloc/order_history_test.dart` | Unit | 2 | ✅ All passed |
| `test/bloc/referral_bloc_test.dart` | Unit | 1 | ✅ All passed |
| `test/widget/screens/login_page_test.dart` | Widget | 21 | ✅ All passed |
| `test/widgets/signup_screen_test.dart` | Widget | 10 | ✅ All passed |
| `test/widgets/signup_validation_test.dart` | Unit | 19 | ✅ All passed |
| `test/widget/order_history_widget_test.dart` | Widget | 2 | ✅ All passed |
| `test/screens/referral_screen_test.dart` | Widget | 5 | ✅ All passed |
| `test/widget_test.dart` | Widget | 1 | ✅ All passed |
| **Flutter Total** | | **368** | ✅ All passed |
| **Backend (Java)** | Unit + Integration | **185** | ⚠️ 27 failures (environment-dependent) |
| **Grand Total** | | **553** | ⚠️ |

> **Note:** Flutter test count (368) confirmed via `flutter test` — "00:24 +368: All tests passed!" (2026-06-10).
> Backend test failures are environment-dependent (missing DB, mail config, etc.).
> Run with a fully provisioned Docker environment (`docker-compose up`) for 100% pass.

---

### 13.1 Test Documentation

| Document | Path | Status |
|----------|------|--------|
| Test Case Catalog | `docs/test-cases/TEST_CASES.md` | ✅ Created v1.0 |
| Test-to-Requirement Registry | `docs/test-registry/TEST_REGISTRY.md` | ✅ Created v1.0 |
| Baseline Report | `docs/test-baselines/TEST_BASELINE.md` | ✅ Created v1.0 |

---

**Document Maintained By:** QA Team  
**Last Review:** 2026-06-10  
**Next Review:** 2026-07-10