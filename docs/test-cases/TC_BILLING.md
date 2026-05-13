# BILLING Module — Detailed Test Cases

> **Document Version:** 1.0
> **Last Updated:** 2026-05-11

---

## TC-BILL-001: Checkout with valid items

| Field | Value |
|-------|-------|
| **ID** | TC-BILL-001 |
| **Module** | BILLING |
| **Type** | Unit |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Preconditions** | Mock SecurityContext |
| **Steps** | POST /api/checkout with valid itemPriceIds |
| **Expected** | 400 (CB not mocked) |
| **Auto** | ✅ Automated |

## TC-BILL-002: Checkout with empty cart

| Field | Value |
|-------|-------|
| **ID** | TC-BILL-002 |
| **Module** | BILLING |
| **Type** | Unit |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Preconditions** | Mock SecurityContext |
| **Steps** | POST /api/checkout with empty list |
| **Expected** | 400 BAD_REQUEST |
| **Auto** | ✅ Automated |

## TC-BILL-003: Checkout with invalid item data

| Field | Value |
|-------|-------|
| **ID** | TC-BILL-003 |
| **Module** | BILLING |
| **Type** | Unit |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Preconditions** | Mock SecurityContext |
| **Steps** | POST /api/checkout with missing itemPriceId |
| **Expected** | 400 BAD_REQUEST |
| **Auto** | ✅ Automated |

## TC-BILL-004: Checkout with single item

| Field | Value |
|-------|-------|
| **ID** | TC-BILL-004 |
| **Module** | BILLING |
| **Type** | Unit |
| **Priority** | P2-Medium |
| **Severity** | S2-Minor |
| **Preconditions** | Mock SecurityContext |
| **Steps** | POST /api/checkout with one item |
| **Expected** | 400 (CB not mocked) |
| **Auto** | ✅ Automated |

## TC-BILL-005: Checkout defaults quantity

| Field | Value |
|-------|-------|
| **ID** | TC-BILL-005 |
| **Module** | BILLING |
| **Type** | Unit |
| **Priority** | P2-Medium |
| **Severity** | S2-Minor |
| **Preconditions** | Mock SecurityContext |
| **Steps** | POST /api/checkout without quantity field |
| **Expected** | 400 (CB not mocked) |
| **Auto** | ✅ Automated |

## Total: 5 test cases
