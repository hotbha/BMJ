# Chargebee Execution Plan — populating the 45 one-time item prices

> **Site:** `bookmyjuice-test` (TEST environment) · **Currency:** INR, stored in **paise**
> **Prepared:** 2026-10-16 · **Authority:** the architecture decision recorded in [`docs/architecture/ADR-005-chargebee-sole-pricing-source.md`](docs/architecture/ADR-005-chargebee-sole-pricing-source.md)
> **Status:** 📋 **PLAN ONLY — NOTHING HAS BEEN CREATED.** The existence of this document authorises **no** write to Chargebee.
> **Scope:** a **data-only** change. Zero application code changes.

## 0. Objective and binding constraints

Create **45 `ItemPrice` objects** — one per `(bmj-item-*, size)` pair — so the 15 one-time products become purchasable. Nothing else is created, modified or deleted.

The four constraints of the approved decision, and the machine check that proves compliance:

| # | Constraint | How this plan proves it |
| :-: | :--- | :--- |
| `C-A` | **Charge-based catalog confirmed** | the created objects are `ItemPrice` records attached to existing `type: charge` items — no plan, add-on, family or customer object is created (§7 `V-5`) |
| `C-B` | **Chargebee is the sole pricing source** | the payload is generated *from* `docs/business-requirements/pricing-table.xlsx` and written *to* Chargebee; no price is stored anywhere else (§5, §7 `V-5`) |
| `C-C` | **Do NOT modify Flutter pricing logic** | `git status --porcelain -- lush/` must be empty before, during and after (§4 `P0-8`, §7 `V-5`) |
| `C-D` | **Do NOT add hardcoded prices** | static scan of `lush/lib/**` for price literals must return 0 hits (§7 `V-5`) |
| `C-E` | **Do NOT create alternate pricing sources** | no new file, service, table, asset or doc introduces a price table; the two stale ones are marked non-authoritative (§11) |

---

## 1. Success criteria

| Metric | Before | After | Source |
| :--- | :-: | :-: | :--- |
| `ItemPrice` objects on the site | 314 | **359** | live census |
| `price`-bearing prices (`pricing_model` charge items) | 5 | **50** | live census |
| `bmj-item-*` items with **zero** prices | 15 | **0** | live census |
| Storefront items rendering 3 sizes | 0 / 15 | **15 / 15** | `GET /api/v1/catalog/charge-items` |
| Flutter files changed | — | **0** | `git status -- porcelain -- lush/` |

---

## 2. The mechanism — and what it forces

From `docs/CHARGEBEE_MCP.md` §5 and a live `tools/list` of both agents:

| Agent | Tools | Catalog write capability |
| :--- | :-: | :--- |
| `data_lookup_agent` | 40 | **none** — read-only (`retrieve_item_price`, `list_item_prices`, `retrieve_item`) |
| `onboarding_agent` | 10 | **`import_product_catalog` only** — *"Import items, families, prices, currencies"* |

Three consequences drive the whole plan:

1. **There is no granular create.** A single `ItemPrice` cannot be created by name; the only write is a **bulk import**. Therefore the "canary" is a *minimal import payload containing exactly one price* (§6 `S-1`).
2. **There is no delete tool.** Rollback cannot be tool-driven — it is dashboard or REST (§8).
3. **The import is not transactional** (vendor-documented; consistent with the 2026-05-28 run that created 15 items and **0** of the 45 prices). A partial result is a *normal* failure mode, so every step reads back what it created.

### 2.1 The read path is frozen — these lines must not change

| Line | Behaviour the payload must satisfy |
| :--- | :--- |
| `ItemService.java:929` | only `type: charge` items are candidates |
| `:951-958` | category from `metadata.category`, else `item_family_id`; invalid → **skipped** |
| `:1109-1113` | prices from the pre-fetch map, else the per-item `ItemPrice.list().itemId().is(...)` call |
| `:1144-1146` | `price` (paise) → ₹ via `movePointLeft(2)` |
| `:1165-1177` | size = `name`/`description` containing `200ml` / `300ml` / `500ml` |

> The pre-fetch is currently **dead** (it requests `limit(200)` against a vendor maximum of 100, so it throws on every request) and the per-item path serves the prices instead. This is why populating the catalog needs **no code change** — see `CATALOG_PRICE_LOADING_VERDICT.md`. `PR-17` remains performance debt, **not** part of this plan.

### 2.2 How a call is made (Windows)

Per `docs/CHARGEBEE_MCP.md` §4: **never** inline JSON in PowerShell. Use `.bat` files with caret continuation, payloads in separate `.json` files, and `-d @payload.json`.

```batch
:: _cb_import.bat  — one write call
curl.exe -s --max-time 120 ^
  -H "Authorization: Bearer <ONBOARDING_TOKEN>" ^
  -H "mcp-session-id: <SESSION_ID>" ^
  -H "Content-Type: application/json" ^
  -H "Accept: text/event-stream" ^
  -d @payload_import_item_prices.json ^
  https://bookmyjuice-test.mcp.chargebee.com/onboarding_agent > import_result.json 2>&1
```

`--max-time 120` (not 15) for writes: an import streams and can legitimately take longer than a lookup. Sessions come from the `initialize` handshake; re-initialise if a write returns a session error.

---

## 3. Authorisation gates (blocking — none may be waived silently)

| Gate | State | Owner | What it must say | Blocks |
| :-: | :--- | :--- | :--- | :--- |
| `G1` write authorisation | ⛔ **open** | Product / Release | in writing: *create the 45 item prices in `bookmyjuice-test`* | every step from `S-1` |
| `G5` rollback owner | ⛔ **open** | Engineering lead | a **named person** + the chosen mechanism (dashboard or REST key) — §8 | `S-1` |
| `P-4` GST / `is_taxable` | ✅ **resolved by live read, 2026-10-16** | Finance | confirm the paise are **GST-inclusive** (a question about *values*, not fields) | not blocking |
| `G4` mechanism agreed | ✅ **resolved by this plan** | — | `import_product_catalog`, canary-first (§2, §6) | — |

**`P-4` note — measured, not assumed.** A live `list_item_prices` filtered on `item_type[is]=charge` returns **exactly 5** prices, and **all 5 carry `is_taxable: true`** and `status: active` (`abc200-INR`, `carrot300-INR`, `pineapple300-INR`, `ABC-INR`, `cbdemo_one-time-setup-fee`).

- **Decision:** the 45 include **`is_taxable: true`** (`C-5`) — identical tax treatment to every working charge price on the site. Omitting it would make these the **only** non-taxable prices on the site: a silent behavioural divergence that would surface on an *invoice*, not on the storefront, i.e. the worst place to discover it.
- **Residual — Finance only:** confirm the approved paise values are **GST-inclusive** (₹129.00 is the customer-facing price). This does not block `S-1`; it validates the numbers already in `CHARGEBEE_FINAL_PRICE_MATRIX.md`.

---

## 4. Pre-flight — read-only assertions (no writes)

All via `data_lookup_agent`. Every row is **archived as raw JSON** in the evidence pack (`V-6`).

| id | Assertion | Tool / command | Expected |
| :-: | :--- | :--- | :--- |
| `P0-1` | both agents reachable | `initialize` on both URLs | two `mcp-session-id` values |
| `P0-2` | the 15 items exist and are charge items | `retrieve_item` × 15 | 15/15 `type: charge`, not deleted |
| `P0-3` | they carry **zero** prices today | `list_item_prices` × 15 | 15 × `[]` |
| `P0-4` | site census | full price census | **314** prices, **5** charge-type |
| `P0-5` | **id collision check** | `retrieve_item_price` × 45 | 45 × not-found |
| `P0-6` | payload integrity | local assertions `A-1`…`A-7` (§5.3) | 45 entries, 0 defects |
| `P0-7` | legacy guard unchanged | census | legacy items still `metadata.category = "juice"` |
| `P0-8` | **code freeze — capture the baseline** | `git -C lush status --porcelain` and `git -C bmjServer status --porcelain` (hash both outputs); `git -C lush rev-parse HEAD`; `git -C bmjServer rev-parse HEAD`; hash `lush/lib/bloc/ProductCatalogBloc/product_catalog_bloc.dart` and `lush/lib/UserRepository/user_repository.dart` | baseline **stored** — `V-5a` compares against it |
| `P0-9` | storefront baseline | `GET /api/v1/catalog/charge-items` | 15 items, **all** `"prices":[]` — archived verbatim |

> **If `P0-5` returns any hit, stop.** A pre-existing id means the id space is already claimed and the payload must be re-derived *before* any write.
>
> `P0-9` is the "before" half of the proof. Without it, a green storefront afterwards cannot be attributed to this change.

> ⚠️ **Do not use `git status --porcelain -- lush/` as the freeze check.** `lush` is a **submodule**: from the superproject that command prints only `M lush` — a dirty gitlink — and says nothing about *what* changed inside. Worse, `lush` is **already dirty today** (20 entries, including `lib/bloc/ProductCatalogBloc/product_catalog_bloc.dart` and `lib/UserRepository/user_repository.dart`), so an "empty diff" criterion could never pass and would be quietly waived. `bmjServer` is a nested repo with **no `.gitmodules` mapping**, so `git -C bmjServer` is the only reliable way to inspect it. Hence `P0-8` captures a **baseline** and `V-5a` asserts **no delta from it**.

---

## 5. The artefact — corrected payload

### 5.1 Corrections required (`C-1`…`C-5`)

`chargebee_items_payload.json` (repo root) already holds the 45 target prices, but each row also carries fields that are **plan/addon-only** in Chargebee Product Catalog 2.0 (vendor-confirmed) — the leading hypothesis for why the 2026-05-28 import created the items and skipped the prices.

| # | Field(s) | Action | Why |
| :-: | :--- | :--- | :--- |
| `C-1` | `period`, `period_unit` (`1 day`) | **delete** | recurring-only; asserts a one-time bottle is a daily subscription — a category error |
| `C-2` | `trial_period`, `trial_period_unit` (`0 day`) | **delete** | recurring-only; a zero-day trial is still a subscription concept |
| `C-3` | `tiers: []` | **delete** | valid only for `tiered` / `volume` / `stairstep` pricing models |
| `C-4` | — | **keep** `id`, `name`, `description`, `pricing_model: flat_fee`, `item_id`, `item_family_id`, `price`, `currency_code` | the documented minimal shape for a flat fee |
| `C-5` | `is_taxable` | **add `true`** | all **5** existing charge prices are taxable (§3); omitting it would make these 45 the only non-taxable prices on the site |

### 5.2 Resulting object (exact shape — one of 45)

```json
{"itemPrices":[
  {"id":"bmj-item-mix-punch-200ml","name":"Mix Punch 200ml","description":"Mix Punch - 200ml",
   "pricing_model":"flat_fee","item_id":"bmj-item-mix-punch","item_family_id":"delight",
   "price":12900,"currency_code":"INR","is_taxable":true}
]}
```

> The `id`, `name` and `description` are **not** cosmetic: `ItemService.java:1165-1177` matches `200ml`/`300ml`/`500ml` against `name` **or** `description`. A price with the right amount but no size token is created successfully, billed correctly, and **never rendered**.

### 5.3 Assertions on the payload — all must pass before it is used

| # | Assertion |
| :-: | :--- |
| `A-1` | exactly **45** objects; ids unique |
| `A-2` | **45/45** `name` contains the size token — and it agrees with `description` |
| `A-3` | 15 distinct `item_id`s, each with exactly **3** sizes (200 / 300 / 500ml) |
| `A-4` | every `item_id` resolves to a live `charge` item from `P0-2` |
| `A-5` | every `price` is an integer in **paise**, equal to the workbook value |
| `A-6` | `item_family_id` matches the item's real family; values ∈ {`delight`,`signature`,`premium`} |
| `A-7` | exactly the **9** keys of §5.2 — no `period`, `period_unit`, `trial_*`, `tiers`, no other extra key |
| `A-8` | every object has `"is_taxable": true` (`C-5`) |

> `A-2` is the one that fails *silently* in production: a price without its size token is created successfully, is billed correctly, and **never appears** on the storefront (`ItemService.java:1165-1177`). Assert it on the payload **and** on the read-back.

**Verified against the current file — 2026-10-16** (`chargebee_items_payload.json`, 45 rows):

| Assertion | Result |
| :--- | :--- |
| `A-1` | ✅ 45 rows, 45 unique ids, no duplicates |
| `A-2` | ✅ 0 rows missing a size token |
| `A-3` | ✅ 15 distinct `item_id`s, exactly 3 sizes each |
| `A-5` | ✅ 45/45 integer paise |
| `A-6` | ✅ families = {`delight`, `premium`, `signature`}; `pricing_model` = `flat_fee` ×45 |
| `A-7` | ❌ **all 45 rows still carry** `period`, `period_unit`, `trial_period`, `trial_period_unit`, `tiers` |
| `A-8` | ❌ `is_taxable` **absent from all 45** |

**Conclusion: the existing file is not a usable payload.** The `C-1`…`C-3` and `C-5` corrections are required and **not yet applied**; producing the corrected `chargebee_item_prices_payload.json` is the first build task, and its output is what the `A-*` gate runs against.

### 5.4 Files

| File | Purpose |
| :--- | :--- |
| `chargebee_item_prices_payload.json` | the 45-row corrected payload — **the only write artefact** |
| `chargebee_item_prices_canary_payload.json` | 1-row payload (`bmj-item-mix-punch-200ml`) for `S-1` |
| `scripts/chargebee/` generation script | derives both from `chargebee_items_payload.json` + the workbook, printing `A-1`…`A-7` |

> **Variant B** — only if `import_product_catalog` rejects a prices-only payload: send the same corrected payload **plus** the pre-existing `items` / `itemFamilies` arrays. Expect duplicate-name errors on objects that already exist (the 3 `premium-black-grapes` failures of 2026-05-28 are the precedent). The A/B decision is taken **once**, at the canary, and recorded (`S-1b`).

---

## 6. Execution sequence

Every step: **import → read back → assert → continue or stop.** No step runs on an unverified predecessor.

| Step | Payload | Scope | Expected | Verification | Abort if |
| :-: | :--- | :--- | :--- | :--- | :--- |
| `S-1` | canary, 1 row | `bmj-item-mix-punch-200ml` = `12900` | exactly 1 price created; other 44 untouched | `retrieve_item_price` + `list_item_prices(bmj-item-mix-punch)` = 1 + endpoint probe | any error other than a known duplicate; **any** other object created |
| `S-1b` | — | record the A/B payload decision | decision logged with rationale | evidence pack | — |
| `S-2` | batch 1, 14 rows | remaining **delight** sizes | 15 delight prices in total | read-back × 14 + census | census ≠ expected |
| `S-3` | batch 2, 15 rows | all **signature** sizes | +15 | read-back × 15 + census | census ≠ expected |
| `S-4` | batch 3, 15 rows | all **premium** sizes | +15 → **359** | read-back × 15 + census | census ≠ expected |

**Why batches follow families:** a partially populated family is not sellable *as a family*, so a halt is commercially meaningful and cheap to diagnose. Each batch is ≤ 15 rows — a small, readable result set.

**Between batches:** re-run the census **before** the next import. A batch that reports success but does not move the census halts the run (§9).

---

## 7. Verification

| id | Check | Method | Pass condition |
| :-: | :--- | :--- | :--- |
| `V-1` | per-object read-back | `retrieve_item_price` × 45 | 45/45: `item_id`, `price` (paise), `currency_code: INR`, `pricing_model: flat_fee`, `name` carries the size token, `status: active`, `deleted: false` |
| `V-2` | census closure | full price census | **314 → 359**, charge-type **5 → 50**, `bmj-item-*` with zero prices **15 → 0** |
| `V-3` | contract probe | `GET /api/v1/catalog/charge-items` | 15 items; each `prices` has **3** entries; sizes ⊂ {`200ml`,`300ml`,`500ml`}; every ₹ value = `price / 100`; **45/45** vs the workbook |
| `V-4` | **commercial** probe (QA, manual) | storefront → 3 products → 3 sizes → add to cart → Chargebee hosted page | the amount shown on the storefront **equals** the amount on the hosted page — this is the operational definition of *"Chargebee is the sole pricing source"* |
| `V-5` | negative checks | see below | all five must hold |
| `V-6` | evidence pack | archive raw JSON | every `P0-*`, `S-*`, `V-*` artefact retained |

**`V-5` negative checks — the ones that catch a "fix" that broke a rule:**

| # | Check | Command | Must be |
| :-: | :--- | :--- | :--- |
| `V-5a` | no Flutter change | `git -C lush status --porcelain` + the two file hashes, compared to the `P0-8` baseline | **identical to baseline** — zero new entries, both hashes unchanged |
| `V-5b` | no hardcoded price added | `git -C lush diff -U0 -- lib/` — scan **added lines only** for price literals (`129`, `₹129`, `129.0`, …) | **0 hits** in added lines |
| `V-5c` | legacy items still unserved | endpoint payload | the legacy `metadata.category = "juice"` items are **absent** |
| `V-5d` | pre-existing data untouched | price-id set before vs after | the original **314** ids are all still present, unchanged |
| `V-5e` | no collateral objects | census of items / families / plans / add-ons / customers | items **15 → 15**, families **3 → 3**, plans / add-ons / customers **unchanged** |

> `V-5d` is the check that proves the import did not *replace* anything. `V-5e` is the check that proves it did not *invent* anything.

---

## 8. Rollback

**`R-1` — the target list.** The 45 ids are deterministic (`<item_id>-<size>ml`) and are read from the payload file, never from memory. **Only** ids confirmed created in `V-1` are eligible.

**`R-2` — the mechanism (must be proven before `S-1`, not after).** The onboarding agent has **no delete tool**, so rollback is:

| Option | How | Requirement |
| :--- | :--- | :--- |
| (a) dashboard | Chargebee UI → Product Catalog → Item Prices → delete by id | the named `G5` owner holds admin access |
| (b) REST | `DELETE /api/v2/item_prices/{item_price_id}` | a site API key with delete scope, held by the `G5` owner |

The `G5` owner chooses one **and confirms access works** before the canary. A rollback plan that has never been exercised is a hope, not a plan.

**`R-3` — blast radius.** This plan creates or modifies **no** item, family, plan, add-on, customer, subscription, invoice or order. Only the created prices are in scope; nothing else requires restoration.

**`R-4` — partial rollback.** If a batch fails mid-way, delete exactly the ids verified in `V-1` and re-run the census: it must return to **314 / 5 / 15**. Then diagnose before any retry.

**`R-5` — the rollback window closes.** A price that has been used on an invoice or a transaction cannot simply be deleted; Chargebee retains it for the record. So the safe window for a clean delete is **between creation and the first real purchase**. Consequence: verify and probe **before** the catalog is announced as live.

**`R-6` — what rollback does not fix.** Rolling back returns the site to today's state, in which **none of the 15 products is purchasable**. Rollback is a brake, not a remedy.

> **`S-1c` — recommended rollback rehearsal** (needs `G5` live): after the canary is verified, **delete it** via the chosen mechanism, confirm the census returns to `314`, then re-import it as `S-1d` and re-verify. Cost: one object, twice. Benefit: the rollback path is *proven* while the blast radius is exactly **1**. If the rehearsal fails, the run never proceeds to 44 more objects.

---

## 9. Abort criteria (hard stops)

| # | Trigger | Action |
| :-: | :--- | :--- |
| `X-1` | `G1` **or** `G5` is not recorded in writing | **do not start** |
| `X-2` | any object created outside the 45 (item / family / plan / add-on / customer / subscription) | stop, roll back created prices (§8) |
| `X-3` | a created price's `name` lacks its size token on read-back | stop, delete that price, re-derive the payload |
| `X-4` | the census moves by anything other than exactly the batch size | stop; no retry until diagnosed |
| `X-5` | any of the original **314** ids is absent or altered (`V-5d`) | stop, escalate — data integrity |
| `X-6` | any created `price` ≠ the workbook value | stop, delete, correct the payload |
| `X-7` | any Flutter or server file appears modified (`V-5a`) | stop — the change is no longer data-only |
| `X-8` | duplicate-name / duplicate-id errors on **prices** | stop — `P0-5` was wrong; re-derive ids before retrying |
| `X-9` | an import rejection you cannot explain in 15 minutes | stop **at the canary**; do not scale the payload up to find out |
| `X-10` | `V-4` shows the storefront amount ≠ the hosted-page amount | **stop and roll back** — the worst possible failure: customer-facing price mismatch |

> `X-9` is the reason the canary exists. The temptation at a bulk-import failure is to add fields until it works; that is how 45 wrong prices get created instead of 1.

---

## 10. Traceability — every step has a justification

| Step | Why it is shaped this way | Evidence |
| :--- | :--- | :--- |
| `S-1` canary (1 row) | the import is **not transactional**; a 1-row blast radius is the only way to learn the mechanism safely | `CHARGEBEE_IMPORT_ROOT_CAUSE.md` §0 |
| `C-1`…`C-3` (drop recurring fields) | `period` / `period_unit` / `trial_*` / `tiers` are plan/addon-only (vendor-confirmed) | `CHARGEBEE_IMPORT_ROOT_CAUSE.md` §1 `E4`, `E5` |
| `A-2` size token | a price without the token is created, billed, and **never rendered** | `ItemService.java:1165-1177` |
| `P0-9` / `V-3` | created prices *are* served — the pre-fetch is dead, the per-item path works | `CATALOG_PRICE_LOADING_VERDICT.md` §4 |
| `P0-7` / `V-5c` | legacy items are rejected by `metadata.category`, so no junk surfaces | `CATALOG_LEGACY_ITEM_REPORT.md` §2 |
| the 45 rows and their ids | approved values, no collisions | `CHARGEBEE_FINAL_PRICE_MATRIX.md` `A1`–`A7` |
| "proceed" | the catalog is ready to populate | `CHARGEBEE_GO_LIVE_RECOMMENDATION.md` — Recommendation A |
| `S-1c` / §8 | there is no delete tool, so the rollback path must be rehearsed | live `tools/list` of `onboarding_agent` (10 tools) |
| `C-5` `is_taxable` | all 5 live charge prices are taxable; mirroring them avoids creating the only non-taxable prices on the site | live `list_item_prices` (`item_type[is]=charge`), 2026-10-16 |
| `P0-8` baseline rather than "empty" | `lush` is a submodule and is **already** dirty, so an empty-diff gate would be waived on day one | `git -C lush status --porcelain` — 20 entries |

---

## 11. Explicitly out of scope — not authorised by this plan

| Not in scope | Why |
| :--- | :--- |
| **Any Flutter change** | `C-C`. Not needed: `product_catalog_screen.dart` already hides price-less items, and prices will now exist. Touching the client would also violate `C-D`/`C-E` risk surface for zero gain |
| **Any bmjServer change** — including `PR-17` (`limit(200)` → ≤100 + pagination) | real, but **performance/observability only**; the per-item path already works. Fix it as a separate PR with tests, never in the middle of a data change |
| **Price lists, currencies, tax config** | outside the decision; `P-4` is its own gate |
| **Plans, add-ons, coupons, customers, subscriptions** | untouched by design (`V-5e` proves it) |
| **Deleting the legacy `"juice"` items** | a separate code/ops decision (`R-1`…`R-4` of the legacy report). Deleting them is *not* required to make the catalog sellable |
| **Production writes** | TEST only. Production needs its own `G1` and its own census |
| **A new price file, constant, seed or fallback table** | `C-E` — that is the failure mode this whole plan exists to prevent |
| **Rewriting the stale price tables** | they get **marked non-authoritative and replaced by a pointer** to the approved workbook + Chargebee. Pasting a corrected table would create *another* copy that can go stale — the exact defect being fixed |

---

## 12. Open items carried forward

| id | Item | Owner |
| :-: | :--- | :--- |
| `N-5` | all planning documents are **untracked** in git — `git add` them in the freeze commit (same failure class as `PR-1`/`B8`) | Engineering |
| `G1`/`G5` | written authorisation + named rollback owner | Product / Eng lead |
| `P-4` | `is_taxable: true` **decided** (§3, `C-5`); residual = Finance confirms the paise are GST-inclusive | Finance |
| `PR-16` | an upstream failure must not present as `200 []` | Backend |
| `PR-17` | pre-fetch `limit(200)` is illegal → per-item path only | Backend (deferred) |
| `B8`/`B9` | untracked `CatalogController`; nothing activates the `prod` profile | Backend |

---

## 13. Definition of done and sign-off

**Done when:** `V-1`…`V-6` all pass, the census reads **359 / 50 / 0**, the contract probe returns **15 × 3** prices matching the workbook **45/45**, `V-5a`…`V-5e` hold, and `V-4` shows shown = charged.

| Role | Name | Confirms | Date |
| :--- | :--- | :--- | :--- |
| Product owner | ______ | `G1` — authorises the 45 creates | ______ |
| Engineering lead | ______ | `G5` — names the rollback owner and the mechanism | ______ |
| Executor | ______ | runs §4 → §6, records the evidence pack | ______ |
| QA | ______ | `V-3`, `V-4` (commercial probe) | ______ |
| Finance | ______ | `P-4` residual — the 45 paise values are GST-inclusive | ______ |

> **Nothing in this document has been executed.** The Chargebee site is unchanged: 314 prices, 5 charge-type, 15 products with zero prices.




