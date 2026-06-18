# Bug Registry — BookMyJuice

**Document Version:** 1.0  
**Last Updated:** 2026-06-12  
**Status:** ✅ Active  
**Document Maintained By:** QA Team  

---

## Bug Lifecycle

```
NEW → TRIAGED → FIXING → VERIFIED → CLOSED
```

- **NEW**: Bug reported, awaiting triage
- **TRIAGED**: Reviewed and severity/priority assigned
- **FIXING**: Developer working on fix
- **VERIFIED**: Fix deployed to staging, awaiting QA confirmation
- **CLOSED**: Fix confirmed, ready for production

---

## Severity & Priority

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

## Active Bugs

| ID | Summary | Module | Severity | Priority | Status | Reported | Assigned | Notes |
|----|---------|--------|----------|----------|--------|----------|----------|-------|
| — | No active bugs | — | — | — | — | — | — | — |

---

## Resolved Bugs

| ID | Summary | Module | Severity | Priority | Status | Reported | Resolved | Fix Version | Notes |
|----|---------|--------|----------|----------|--------|----------|----------|-------------|-------|
| — | No resolved bugs yet | — | — | — | — | — | — | — | — |

---

## Bug Report Template

Use the following template when filing a new bug:

```markdown
### BUG-{NEXT_ID}: {Short Description}

**Module:** {Auth / Cart / Billing / Subscription / Profile / Products / Orders / Notifications / General}  
**Environment:** {Staging / Production / Local}  
**Device/OS:** {e.g. Pixel 7 / Android 14, iPhone 15 / iOS 18}  
**App Version:** {e.g. 1.0.0-beta.1}  

**Steps to Reproduce:**
1. Go to '...'
2. Tap on '...'
3. See error

**Expected Behavior:**
{What should happen}

**Actual Behavior:**
{What actually happens}

**Severity:** {S0 / S1 / S2 / S3}  
**Priority:** {P0 / P1 / P2 / P3}  

**Attachments:**
- Screenshot / Screen recording: {link}
- Logs: {link}
- Network trace: {link}

**Additional Context:**
{Any other relevant information}
```

---

## Escalation Contacts

| Role | Contact |
|------|---------|
| QA Lead | TBD |
| Frontend Dev Lead | TBD |
| Backend Dev Lead | TBD |
| DevOps | TBD |

---

**Document Control:**
- **Created:** 2026-06-12
- **Last Updated:** 2026-06-12
- **Version:** 1.0
- **Status:** ✅ Active