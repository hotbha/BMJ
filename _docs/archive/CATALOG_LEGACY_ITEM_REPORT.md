# Catalog Legacy Item Report — the `PR-19` leak question

> **Site:** `bookmyjuice-test` (TEST) · **Task:** `T5` · **Investigated:** 2026-10-16
> **Question under test:** *"Legacy items `abc200`, `carrot300`, `pineapple300` are leaking into the storefront."*
> **Status:** 🔒 **READ-ONLY INVESTIGATION — NOTHING WAS DELETED, ARCHIVED, RENAMED OR MODIFIED.**
> **Verdict:** ❌ **FALSIFIED as a *present* leak.** They are **not** served today — proven by the runtime log, not by reading code. They remain a 🟠 **LATENT** leak: one metadata edit on those items would make them appear, and `abc200` would appear **with a working ₹99 price**.

---

## 0. Verdict at a glance

| Claim | Verdict | Proof |
| :--- | :-- | :--- |
| `abc200`, `carrot300`, `pineapple300` are **served** by `GET /api/v1/catalog/charge-items` today | ❌ **FALSE** | live log: each is logged `Skipping item … - invalid category: juice`; the response is `Returning 15 filtered items` |
| They **would** pass the category filter if it were evaluated on family id | ✅ **TRUE** | families `Premium-Juices` / `Delight-Juices` satisfy `contains("premium")` / `contains("delight")` |
| They **do** pass the filter today | ❌ **FALSE** | their `metadata.category` is `"juice"`, and the metadata branch runs **first** |
| How many leak today | **0** | 20 charge items − 5 skipped = **15** returned (the arithmetic closes exactly) |
| How many could leak | **3** (latent) | `abc200` → premium · `carrot300` → delight · `pineapple300` → delight. (`ABC` would **not** leak even then: family `Juices` holds no token.) |
| Would a leaked item be purchasable? | 🟠 **`abc200` yes — ₹99** | `abc200-INR` description is `"Apple, Beetroot, Carrot (ABC) Juice (200ml)"` → contains `200ml` → survives the size filter |
| Anything deleted or changed? | **No** | read-only census + runtime log + source reading only |

---

## 1. Where the concern came from — and why it was a reasonable reading

The category filter is a **substring test**, and **three of the eight families on the site contain a category token**:

| family id | family name | satisfies the `contains()` test? |
| :--- | :--- | :--- |
| `delight` | Delight | `delight` ✓ — the intended family |
| `signature` | Signature | `signature` ✓ — the intended family |
| `premium` | Premium | `premium` ✓ — the intended family |
| `Delight-Juices` | Delight Juices | ⚠️ **`delight` ✓** — legacy family |
| `Signature-Juices` | Signature Juices | ⚠️ **`signature` ✓** — legacy family |
| `Premium-Juices` | Premium Juices | ⚠️ **`premium` ✓** — legacy family |
| `Juices` | *(displayed as "Premium-Juices" — see §7)* | ✗ no token |
| `cbdemo_omnisupport-solutions` | OmniSupport Solutions | ✗ no token |

Read `extractCategoryFromFamilyId` (`ItemService.java:985-994`) in isolation and the conclusion is inescapable: those three legacy families **pass**, therefore the legacy items must be leaking.

**That reading is wrong — but only because of an earlier branch that a static reading typically skips.** The items pass the *family* test; they never reach it.

---

## 2. What actually happens — the runtime log settles it

`bmjServer/smoke_backend.out.log`, **2026-10-16 12:56:17 → 12:56:24**, one request to `GET /api/v1/catalog/charge-items` (verbatim, elided):

```text
12:56:17.484 INFO  ItemService - Filtered to 20 CHARGE items out of 176 total items
12:56:17.890 WARN  ItemService - Failed to batch-fetch ItemPrices: limit : It should not be more than 100
12:56:24.719 DEBUG ItemService - Skipping item abc200                     - invalid category: juice
12:56:24.722 DEBUG ItemService - Skipping item carrot300                  - invalid category: juice
12:56:24.724 DEBUG ItemService - Skipping item pineapple300               - invalid category: juice
12:56:24.725 DEBUG ItemService - Skipping item ABC                       - invalid category: juice
12:56:24.725 DEBUG ItemService - Skipping item cbdemo_one-time-setup-fee  - invalid category: null
12:56:24.726 INFO  ItemService - Caching 15 items to local database
12:56:24.726 INFO  ItemService - Returning 15 filtered items with categories: Delight, Signature, Premium
```

**The arithmetic closes exactly: `20 − 5 = 15`.** Every non-`bmj-item-*` charge item is rejected **by name, in the log**, and the endpoint returns 15 items. This is not a matter of opinion: the served set is *measured*, and the legacy items are not in it.

**Why `juice`?** Because their `metadata.category` is literally `"juice"`:

| item | family | `metadata.category` | category actually evaluated | result |
| :--- | :--- | :--- | :--- | :--- |
| `abc200` | `Premium-Juices` | **`"juice"`** | `juice` | ❌ skipped |
| `carrot300` | `Delight-Juices` | **`"juice"`** | `juice` | ❌ skipped |
| `pineapple300` | `Delight-Juices` | **`"juice"`** | `juice` | ❌ skipped |
| `ABC` | `Juices` | **`"juice"`** | `juice` | ❌ skipped |
| `cbdemo_one-time-setup-fee` | `cbdemo_omnisupport-solutions` | *(none)* | `null`; family holds no token | ❌ skipped |

---

## 3. The exact filter condition

Resolution happens in **three ordered steps** in `bmjServer/src/main/java/com/bookmyjuice/services/ItemService.java`:

**Step 1 — metadata wins (`:951-955`):**

```java
String category = extractCategoryFromMetadata(chargebeeItem.metadata());
// Fall back to itemFamilyId if metadata category is null/blank
if (category == null || category.trim().isEmpty()) {
    category = extractCategoryFromFamilyId(chargebeeItem.itemFamilyId());
}
```

**Step 2 — the family fallback *is* the substring test (`:985-994`)** — reached **only** when step 1 yields `null`/blank:

```java
private String extractCategoryFromFamilyId(String familyId) {
    if (familyId == null || familyId.trim().isEmpty()) return null;
    String lower = familyId.toLowerCase().trim();
    if (lower.contains("delight"))   return "delight";
    if (lower.contains("signature")) return "signature";
    if (lower.contains("premium"))   return "premium";
    return null;
}
```

**Step 3 — the gate (`:956-959`):**

```java
if (!isValidCategory(category)) {   // accepts only delight | signature | premium
    logger.debug("Skipping item {} - invalid category: {}", chargebeeItem.id(), category);
    continue;
}
```

> ### The exact filter condition that decides `PR-19`
> **`metadata.category`, if present and non-blank, is used verbatim. The `contains()` family test is consulted only when that is absent.**
>
> - The 15 real products carry `metadata = {"is_custom_pricing": false}` → **no `category`** → they take the family path and resolve correctly.
> - The legacy items **do** carry `category: "juice"` → rejected at step 3, **before** the family path can pull them in.

### 3.1 Why the metadata is the safety net and the family test is the hazard

| | 15 `bmj-item-*` products | `abc200` / `carrot300` / `pineapple300` |
| :--- | :--- | :--- |
| `metadata` | `{"is_custom_pricing": false}` | `{… , "category": "juice", "subcategory": "green_juice", …}` |
| category used | family id → `delight` / `signature` / `premium` ✅ | metadata → `"juice"` ❌ |
| family | `delight` / `signature` / `premium` (exact ids) | `Premium-Juices` / `Delight-Juices` |
| outcome | **served** | **skipped** |

**Nothing in the code guarantees this safety.** It holds only because someone once put `"category": "juice"` into those items' metadata. Remove or rename that key and the legacy items fall through to `contains()` — and two of the three legacy families satisfy it.

---

## 4. How many — 0 today, 3 latent

| State | Count | Which |
| :--- | :-: | :--- |
| Leaking **today** | **0** | measured: the endpoint returns exactly the 15 `bmj-item-*` products |
| **Latent** (would leak if `metadata.category` were removed or renamed) | **3** | `abc200`, `carrot300`, `pineapple300` |
| Cannot leak even then | 2 | `ABC` (family `Juices` — no token) · `cbdemo_one-time-setup-fee` (family `cbdemo_omnisupport-solutions`, no metadata) |
| Charge items total (the candidate set) | 20 | 15 real + 5 legacy/demo |

All three latent items are `active`, `type: charge`, `enabled_for_checkout: true`, `enabled_in_portal: true`, `channel: web` — **nothing on the item itself would stop them.** The `metadata.category` key is the only thing doing so.

---

## 5. What exactly would happen if the guard were removed

| item | family → resolved category | its price | size-token test | what would render |
| :--- | :--- | :--- | :--- | :--- |
| `abc200` | `Premium-Juices` → **premium** | `abc200-INR` · **₹99.00** · desc `"Apple, Beetroot, Carrot (ABC) Juice (200ml)"` | ✅ contains `(200ml)` | 🔴 **a purchasable ₹99.00 product in the Premium category** |
| `carrot300` | `Delight-Juices` → **delight** | `carrot300-INR` · ₹89.00 · desc `"Customer facing info…… for Carrot 300 ml Charge item"` | ❌ `"300 ml"` has a **space** — not `"300ml"` | 🟠 appears in Delight with `prices: []` (no size resolves) |
| `pineapple300` | `Delight-Juices` → **delight** | `pineapple300-INR` · ₹99.00 · desc `"customer facing info"` | ❌ no token | 🟠 appears in Delight with `prices: []` |

Two details make this worse than it first appears:

1. **The item names are the raw ids** — `abc200`, `carrot300`, `pineapple300` — because the legacy items were never given product names. They would surface *as products* under Delight/Premium, labelled with internal ids.
2. **`abc200` would be fully purchasable** at ₹99.00, because its price description happens to carry a well-formed `(200ml)` token. The leak is therefore not cosmetic: it is a stray SKU a customer could buy and pay for.

> **Correction to an earlier claim.** `CATALOG_PRICE_MATRIX.md` §0/§4 previously described the storefront as serving *"18 items · 1 with a price — the legacy `abc200` at ₹99"*. That figure came from evaluating the filter **statically** and was **wrong**. Measured reality (live log): **15 items served · 0 with a price · 0 legacy items**. The matrix has been corrected accordingly.

---

## 6. Secondary findings (data hygiene — recorded, nothing changed)

| # | Finding | Impact |
| :-: | :--- | :--- |
| `H-1` | Family id `Juices` carries the **display name "Premium-Juices"** — id and name disagree | None functionally (the code matches the **id**), but actively misleading during triage: it looks like a Premium family that is not one |
| `H-2` | Three legacy `*-Juices` families plus a stray `Juices` family sit alongside the three canonical ones | These are the source of the substring hazard — remnants of the retired catalog |
| `H-3` | The 3 legacy charge items hold prices named with internal ids (`abc200 INR`) and described with operator notes (`"customer facing info"`) | Any future import that attaches size tokens to them instantly creates purchasable junk SKUs |
| `H-4` | The legacy items carry full marketing metadata (`category: juice`, `subcategory`, `nutritionalInfo`, …) while the 15 real products carry only `{"is_custom_pricing": false}` | The real products depend on the **fallback** path; the legacy ones block it. The opposite of what a reader would expect — see `T5` §3.1 |

---

## 7. Recommended hardening — **no deletions**

**Nothing was deleted, archived, renamed or modified in this task**, and nothing should be as a *reaction* to it. Note two facts: `abc200-INR` is one of only five working charge prices on the site (removing it removes evidence), and removing legacy catalog objects is a **Product/owner decision**, not an incident response.

The code-side fix, by contrast, is cheap and fully within engineering's control:

| # | Change | Why |
| :-: | :--- | :--- |
| `R-1` | Replace the `contains()` family test with an **exact allow-list** (`Set.of("delight","signature","premium")`) | Removes the substring hazard permanently: `Delight-Juices` etc. can never match |
| `R-2` | Require a **positive** marker for BMJ products (e.g. `id.startsWith("bmj-item-")`, or explicit `metadata.is_bmj_item == true`) instead of relying on the *absence* of a `category` key | Today's safety rests on negative evidence held in **someone else's** metadata; a single edit elsewhere silently disables it |
| `R-3` | Add a regression test: *an item in family `Delight-Juices` with no `category` metadata must not be served* | No test covers this today; the bug cannot be locked out without one |
| `R-4` | Raise the `Skipping item … invalid category` log from `debug` to `info`/`warn` for non-`bmj-item-*` ids | The evidence that resolved this question was emitted at **`debug`** and survived only because the log happened to retain DEBUG |

---

## 8. Evidence appendix (reproduce)

| Claim | Source |
| :--- | :--- |
| 20 charge items considered → 15 served → 5 skipped **by name**, with the resolved category | `bmjServer/smoke_backend.out.log`, 2026-10-16 12:56:17 → 12:56:24 |
| the same behaviour on a second, later request | same log, 13:06:55 → `Skipping item abc200 …` |
| families present (8): `premium`, `signature`, `delight`, `Premium-Juices`, `Delight-Juices`, `Signature-Juices`, `Juices`, `cbdemo_omnisupport-solutions` | `list_item_families` (read-only) |
| the 3 legacy items' `metadata.category == "juice"`, families, `active` status, checkout/portal flags | `list_items` (read-only) |
| their prices, names and descriptions (`abc200-INR` desc contains `(200ml)`; `carrot300-INR` desc says `300 ml` with a space) | `list_item_prices` (read-only), 314 rows |
| filter precedence and the exact test | `ItemService.java:951-959`, `:985-994`, `:956-959`, `:1165-1177` |
| nothing was changed | this task issued **only** read calls (`list_items`, `list_item_prices`, `list_item_families`, `retrieve_item`) against the read-only `data_lookup_agent` |

---

**End of report.** **Zero** objects were deleted, archived, renamed or modified; no metadata was touched. Verdict: **not leaking now (falsified as a present defect), latent for the future** — fixed in code (`R-1`–`R-4`), not by deletion.



