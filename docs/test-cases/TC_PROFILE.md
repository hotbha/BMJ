# PROFILE / CHARGEBEE SYNC Module — Detailed Test Cases

> **Document Version:** 1.0
> **Last Updated:** 2026-05-11

---

## TC-PROF-001: ChargebeeSyncService — startup sync disabled (NEW)

| Field | Value |
|-------|-------|
| **ID** | TC-PROF-001 |
| **Module** | PROFILE |
| **Type** | Unit |
| **Priority** | P2-Medium |
| **Severity** | S2-Minor |
| **Preconditions** | Mock syncConfig.isEnableStartupSync=false |
| **Steps** | syncChargebeeDataOnStartup() |
| **Expected** | Logs disabled message, returns without syncing |
| **Auto** | ✅ Automated |

## TC-PROF-002: ChargebeeSyncService — getSyncStatus (NEW)

| Field | Value |
|-------|-------|
| **ID** | TC-PROF-002 |
| **Module** | PROFILE |
| **Type** | Unit |
| **Priority** | P2-Medium |
| **Severity** | S2-Minor |
| **Preconditions** | Mock repositories return counts |
| **Steps** | getSyncStatus() |
| **Expected** | Returns formatted string with counts |
| **Auto** | ✅ Automated |

## TC-PROF-003: ChargebeeSyncService — shutdown does not throw (NEW)

| Field | Value |
|-------|-------|
| **ID** | TC-PROF-003 |
| **Module** | PROFILE |
| **Type** | Unit |
| **Priority** | P3-Low |
| **Severity** | S3-Trivial |
| **Preconditions** | Fresh ChargebeeSyncService |
| **Steps** | shutdown() |
| **Expected** | Does not throw (executor may be null) |
| **Auto** | ✅ Automated |

## Total: 3 test cases (all new)
