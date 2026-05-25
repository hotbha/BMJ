# Task Progress: Phase 2 (Execute) + Phase 3 (Fix)

- [ ] Phase 2: Start Docker server (docker-compose up -d)
- [ ] Phase 2: Wait for backend to be healthy
- [ ] Phase 2: Run E2E test suite
- [ ] Phase 2: Analyze results against previous 52.9% pass rate
- [ ] Phase 3: Fix B-04 (Chargebee API version mismatch - remove .id() call)
- [ ] Phase 3: Fix Unified Signup 401 (missing permitAll or /error handler)
- [ ] Phase 3: Fix Auto Login 401 (missing permitAll for /api/auth/autologin)
- [ ] Phase 3: Fix Link Google Account 401
- [ ] Phase 3: Fix Checkout endpoint 401 (make test endpoints public or fix @PreAuthorize)
- [ ] Phase 3: Fix Pricing Plans 401 (add permitAll for /api/subscriptions/pricing/plans)
- [ ] Phase 3: Fix v1 auth prefix test expectation (actually works)
- [ ] Phase 3: Re-run tests to verify fixes
- [ ] Phase 3: Update RTM and test report
