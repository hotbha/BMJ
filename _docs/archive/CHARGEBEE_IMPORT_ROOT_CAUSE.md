# Chargebee Import Root Cause — why the 45 one-time item prices never landed

> **Site:** `bookmyjuice-test` (TEST) · **Task:** `T3`
> **Status:** 🔒 **READ-ONLY ANALYSIS — NO WRITE WAS PERFORMED. NOTHING WAS CREATED, MODIFIED OR DELETED.**
> **Hypothesis under test:** *"The previous import failed because charge item prices were created with `period = 1` / `period_unit = day`, while existing charge prices on the site use `period = null` / `period_unit = null`."*
> **Verdict:** 🟡 **SUPPORTED — the best available explanation. Confidence: MEDIUM-HIGH that the payload is invalid by construction; MEDIUM that this specific field is the trigger.** It is **not** yet proven; §3 defines the one-row canary that proves or kills it, and that canary is a **write** requiring `G1`.

---

## 0. Verdict, claim by claim

| # | Claim embedded in the hypothesis | Verdict | Evidence |
| :-: | :--- | :-- | :--- |
| C1 | The previous payload really does set `period: 1`, `period_unit: "day"` on the one-time prices | ✅ **CONFIRMED** | `chargebee_items_payload.json` → **45/45** rows · §1 `E1` |
| C2 | Existing charge prices use `period: null`, `period_unit: null` | ✅ **CONFIRMED — and stronger than the hypothesis states:** the fields are **absent from the API response entirely**, not merely `null` | field-presence audit of all 314 prices · §1 `E2` |
| C3 | `period` is a *recurring-only* concept in Chargebee Product Catalog 2.0 | ✅ **CONFIRMED by the vendor's own API reference** | §1 `E4`, `E5` |
| C4 | This field is what made the import fail | 🟡 **SUPPORTED, NOT PROVEN** — no error artefact from the failed import survives, and producing one requires a write | §3 |
| C5 | It is the *only* possible cause | ❌ **NO** — 7 alternatives, 4 ruled out, 3 open | §4 |
| C6 | The failure was correctly diagnosed at the time | ❌ **NO** — the opposite explanation was written into the record, and it is false | §1 `E9` |

**One-line answer:** it is the **best-supported explanation available without a write**, it is **not yet a proven root cause**, and it is **cheap to prove** with a single canary row (§3).

---

## 1. Evidence

### `E1` The prepared payload sets a billing period on a one-time product

Full audit of `chargebee_items_payload.json` (45 rows; all `pricing_model: flat_fee`; all `currency_code: INR`):

| Field | Value | Rows |
| :--- | :--- | :--- |
| `period` | `1` | **45 / 45** |
| `period_unit` | `"day"` | **45 / 45** |
| `trial_period` | `0` | 45 / 45 |
| `trial_period_unit` | `"day"` | 45 / 45 |
| `tiers` | `[]` | 45 / 45 |

Sample row (verbatim):

```json
{"id":"bmj-item-mix-punch-200ml","name":"Mix Punch 200ml","description":"Mix Punch - 200ml",
 "pricing_model":"flat_fee","item_id":"bmj-item-mix-punch","item_family_id":"delight",
 "price":12900,"currency_code":"INR","period":1,"period_unit":"day",
 "trial_period":0,"trial_period_unit":"day","tiers":[]}
```

A **one-time bottle purchase** was therefore described to Chargebee as a **daily recurring** price. That is a category error before it is a syntax error — the payload models a subscription, on an object whose entire purpose is to *not* recur.

### `E2` Every charge price that *does* exist carries **no** `period` field at all

All 314 item prices were walked and their response fields inventoried. For the 5 `charge`-type prices, these fields are **absent from the object entirely**: `period`, `period_unit`, `trial_period`, `trial_period_unit`.

| Field group | present on charge prices |
| :--- | :-- |
| `id`, `item_id`, `item_family_id`, `item_type`, `price`, `currency_code`, `pricing_model`, `status`, `is_taxable`, `free_quantity`, `created_at`, `resource_version`, … | ✅ 5 / 5 |
| `period` · `period_unit` · `trial_period` · `trial_period_unit` | ❌ **0 / 5** |

| working charge price | `pricing_model` | `is_taxable` | `period` / `period_unit` |
| :--- | :--- | :-- | :--- |
| `abc200-INR` | `per_unit` | `true` | **absent** |
| `carrot300-INR` | `per_unit` | `true` | **absent** |
| `pineapple300-INR` | `per_unit` | `true` | **absent** |
| `ABC-INR` | **`flat_fee`** | `true` | **absent** |
| `cbdemo_one-time-setup-fee` | **`flat_fee`** | `true` | **absent** |

### `E3` Where `period` *does* appear, the item is recurring

Distribution across all 314 prices, by `item_type`:

| `item_type` | `period` / `period_unit` observed | count |
| :--- | :--- | --: |
| `charge` | **no period fields at all** | 5 |
| `addon` | `1/day`, `1/month` ×4, `1/year` ×4 | 9 |
| `plan` | `1/month` ×149, `1/week` ×56, `6/day` ×90, `1/day`, `1/year` | 300 |

`period` tracks **recurrence**, exactly as the vendor documents: nothing recurring is a `charge`, and no `charge` carries a period. The one item price on the site whose model is *closest* to the failed payload — a one-time `flat_fee` — is `ABC-INR`, and it carries no period.

### `E4`–`E6` The vendor's API reference agrees, in writing

| # | Field (Create an Item Price) | Quote from the API reference |
| :-: | :--- | :--- |
| `E4` | `period` / `period_unit` | *"The `period_unit` is **mandatory when the item `type` is `plan` or `addon`**."* · *"The billing period of an item price (**applicable only to plan-item prices and addon-item prices**) is the `period` of the item price in `period_unit`s."* — **`charge` appears in neither list.** |
| `E5` | `trial_period` / `trial_period_unit` | *"The trial period of the plan in `trial_period_unit`s. You can also set trial periods for addons; contact Support to enable that feature."* — **no `charge` case.** |
| `E6` | `tiers` | *"Applicable only for `tiered`, `volume`, and `stairstep` `pricing_models`."* → `tiers: []` on a `flat_fee` row is out of contract too. |

The vendor's own canonical example of a **charge** item price omits all of them:

```bash
curl https://<site>.chargebee.com/api/v2/item_prices -u {site_api_key}: \
  -d id="implementation-fee-usd" -d item_id="implementation-fee" \
  -d name="Implementation Fee USD" -d currency_code="USD" \
  -d pricing_model="FLAT_FEE" -d price=5000     # no period, no period_unit, no trial, no tiers
```

> **Caveat, stated plainly:** the reference proves these fields are **not applicable** to charge prices. It does **not** publish the exact error text for sending them anyway. *"Not applicable" ≠ "it was proven to throw."* That distinction is the entire reason §3 exists.

### `E7` A bulk import is **not** transactional — so "items exist, prices don't" needs no exotic explanation

Chargebee bulk operations validate **row by row**, report `cb_validation_errors` and `cb_operation_status` per row, and let the operator *"skip rows with errors and continue"*. **Valid rows are created; invalid rows are skipped; nothing rolls back.**

This is the single most important structural fact for this investigation: the exact shape of the damage — **15 items created, 45 prices absent** — is *documented* bulk-import behaviour once one price-row field is invalid. It removes the need for any "the whole call silently failed" theory (§4 `A1`).

### `E8` Counter-evidence that kills the obvious wrong answer: `flat_fee` is fine

`ABC-INR` is a **charge** item price with `pricing_model: flat_fee`, `price: 8900`, `status: active`, `is_taxable: true`. The payload's `pricing_model`, `currency_code` and one-time intent are therefore **proven usable on this very site**. Any explanation built on `flat_fee` or `INR` is dead on arrival — the difference between the rows that worked and the rows that vanished is **not** the pricing model.

### `E9` The "explanation of record" is false — which is why this went undiagnosed

`docs/chargebee_final_state.md:79-80` states:

> *"Created 2026-05-28 via MCP. Type: `charge`. IDs: `bmj-item-*` pattern.*
> *Charge types use flat pricing via `item.price` field, not separate `item_prices`."*

**The second sentence is false, twice over** (`CATALOG_PRICE_MATRIX.md` §1.1): `retrieve_item` on all 15 items returns **no `price` field at all** (`Item` in PC 2.0 has no price), and **5 charge items on this same site do carry item prices**. The shortfall was recorded in that document as `⚠️ One-time item prices 0/45` and rationalised away with a false premise instead of being investigated — which is how the defect reached a launch gate.

---

## 2. The differential: failed payload vs. every working charge price

| Field | Failed payload (45 rows) | All 5 working charge prices | Verdict |
| :--- | :--- | :--- | :--- |
| `item_type` | `charge` | `charge` | same |
| `pricing_model` | `flat_fee` | `flat_fee` (2) · `per_unit` (3) | same class — `flat_fee` proven (`E8`) |
| `currency_code` | `INR` | `INR` | same |
| `price` | integer paise | integer paise | same |
| `item_family_id` | `delight` / `signature` / `premium` | present on 5/5 | same |
| **`period` / `period_unit`** | **`1` / `"day"` on 45/45** | **absent on 5/5** | ⛔ **the only material difference** |
| **`trial_period` / `trial_period_unit`** | **`0` / `"day"` on 45/45** | **absent on 5/5** | ⛔ second out-of-contract pair |
| **`tiers`** | **`[]` on 45/45** | absent on 5/5 | ⚠️ out of contract for `flat_fee` |
| **`is_taxable`** | **absent** | **`true` on 5/5** | ⚠️ GST-relevant omission (§6) |

**The differential isolates exactly two fields that describe recurrence — `period`/`period_unit` and `trial_period`/`trial_period_unit` — plus the empty `tiers` array.** Of these, the hypothesis names the first. That is why it is the leading explanation: it is the *only* difference that conceptually invalidates a one-time price.

---

## 3. Proof — the canary that settles it (⚠️ this step is a **WRITE**, requires `G1`)

The missing artefact is unambiguous: **no import response or Chargebee validation file was retained**, so the failure cannot be *read* out of history. It can only be **reproduced** deliberately. Two canaries, run in this order:

| # | Canary | Object | Payload | Interpretation |
| :-: | :--- | :--- | :--- | :--- |
| `K-1` | **Positive canary (the first of the 45)** | `bmj-item-mix-punch-200ml` on `bmj-item-mix-punch` | the **corrected** row: `flat_fee`, `price: 12900`, `INR`, **no `period` / `period_unit` / `trial_*` / `tiers`** | **2xx** → the documented-correct shape works; proceed to the remaining 44. **Rejected** → the root cause is *not* `period`; inspect the error text before writing anything else. |
| `K-2` | **Negative canary (causal proof)** | a throwaway price id on a disposable charge item (never a `bmj-*` id) | the **historical** shape: `period: 1`, `period_unit: "day"` | **Rejected naming `period`** → hypothesis **PROVEN**. **Accepted** → hypothesis **FALSIFIED**; `A5`/`A6`/`A7` become the prime suspects. |

**Two rules for the canaries** (both learned from `E7`):
1. **Capture the raw response verbatim** — the tool result, status and any validation/error text. Retaining it is the difference between a diagnosis and another guess.
2. **Never run `K-2` in production**, and delete or unpublish the throwaway object afterwards (itself a write, needing its own authorisation).

> **The honest position:** `K-1` alone is enough to *proceed safely*. `K-2` is what converts "likely cause" into "known cause". If `K-2` is not authorised, this document keeps its 🟡 verdict — the fix is still the right fix, but the root cause stays **probable, not proven**.

---

## 4. Alternative explanations

| # | Alternative | State | Reasoning |
| :-: | :--- | :-- | :--- |
| `A1` | The import never reached the price step / a rollback undid it | ❌ **RULED OUT** | Bulk operations are **not transactional** (`E7`): rows are created/skipped individually. And 15 items *did* land — the call executed. |
| `A2` | `flat_fee` is invalid for a charge item price | ❌ **RULED OUT** | `ABC-INR` is `charge` + `flat_fee` + `active` (`E8`). |
| `A3` | The prices were sent to the wrong site/account | ❌ **RULED OUT** | The same payload's 15 items exist on **this** site; the target `item_id`s all resolve here. |
| `A4` | Duplicate-id conflict ("already exists") caused a skip | ❌ **RULED OUT** | None of the 45 ids exist now — and a pre-existing price would still be present, not absent. |
| `A5` | `tiers: []` is rejected on a `flat_fee` price | 🟠 **OPEN — plausible co-cause** | `tiers` is documented as applicable only to `tiered`/`volume`/`stairstep` (`E6`); an empty array on `flat_fee` is out of contract. **Mitigation: omit the key entirely.** |
| `A6` | `trial_period: 0` / `trial_period_unit: "day"` is rejected on a charge price | 🟠 **OPEN — same family as the hypothesis** | Trials are documented for `plan` (and `addon`, on request) — not `charge` (`E5`). **Mitigation: omit.** |
| `A7` | The bulk MCP tool silently ignored the `itemPrices` array (key/schema mismatch, or a partial-success path reported as success) | 🟠 **OPEN — not ruleable-out from artefacts** | No tool response was retained. This is a **tool-contract** risk, and it is the reason `K-1` must be observed **per row** rather than assumed. |
| `A8` | The omitted `is_taxable` caused the rejection | 🟢 **LOW** | Optional field with a default; every live row sets `true`. Set it anyway (GST clarity). |

**Why this matters:** `A5`, `A6` and `A7` all predict the *same* observed damage as the hypothesis. That is precisely why the confidence is **MEDIUM**, not HIGH, and why `K-1`/`K-2` exist.

---

## 5. What this is **not** — do not conflate it with `PR-17`

Two **independent** defects live in this area. They are routinely merged, and merging them produces the wrong fix:

| | **Import defect** (this document) | **`PR-17`** (the code defect) |
| :--- | :--- | :--- |
| Where | Chargebee **data** layer | `bmjServer/.../services/ItemService.java:937` |
| When it bites | once, at import time (2026-05-28) | **every** catalog request |
| Symptom | **45 price rows absent** (measured: 0 `bmj-item-*` prices exist) | the batch price pre-fetch **throws**: `limit : It should not be more than 100` |
| Evidence | the price census + the field differential (§2) | runtime log, **15+ occurrences** on 2026-10-16 (`smoke_backend.out.log`) |
| Effect on the storefront | **none directly** — the per-item fallback path still reads prices (see `CATALOG_PRICE_LOADING_VERDICT.md`) | extra API calls + a `WARN` that hides real failures |
| Fix | corrected payload + canary (§6) | `limit(100)` + paginate like `:910-923` already does for items |

**The log proves the app-side failure. It says nothing about the import failure** — the runtime log is 5 months newer than the import and cannot observe it. Anyone who "fixes `PR-17`" expecting the prices to appear will find the store empty of price rows for a different reason.

---

## 6. The corrected creation payload (the fix this analysis supports)

```json
{
  "id":             "bmj-item-mix-punch-200ml",
  "name":           "Mix Punch 200ml",
  "description":    "Mix Punch - 200ml",
  "pricing_model":  "flat_fee",
  "item_id":        "bmj-item-mix-punch",
  "item_family_id": "delight",
  "price":          12900,
  "currency_code":  "INR",
  "is_taxable":     true
}
```

| # | Correction vs the historical payload | Rationale |
| :-: | :--- | :--- |
| `C-1` | **omit** `period` / `period_unit` (do not send `1` / `"day"`) | `E2`+`E4`: no working charge price carries them; the reference scopes them to `plan`/`addon` |
| `C-2` | **omit** `trial_period` / `trial_period_unit` | `E5`: trials are a `plan` (optionally `addon`) concept |
| `C-3` | **omit** `tiers` | `E6`: `tiers` applies only to `tiered`/`volume`/`stairstep`; an empty array on `flat_fee` is out of contract |
| `C-4` | **add** `is_taxable: true` | all 5 working charge prices set it; GST must be an explicit decision, not a default (open item `P-4`) |

Omitting rather than sending `null` is deliberate: `null` still transmits the key, and `A5`/`A6` are open. The `name`/`description` **must** keep the literal `200ml` token (`ItemService.java:1165-1177`) — verified 45/45 in `CHARGEBEE_FINAL_PRICE_MATRIX.md` §2 `A3`.

---

## 7. What would confirm or falsify this analysis

| Outcome | Meaning |
| :--- | :--- |
| `K-1` (corrected row) returns 2xx | ✅ the documented-correct shape is proven on this site — **proceed**, and the remaining 44 are de-risked |
| `K-1` is rejected naming a **different** field | ⛔ this analysis is **wrong** — read the error, re-open §4 with the new fact |
| `K-2` (with `period: 1` / `day`) is rejected naming `period` | ✅ hypothesis **PROVEN** — root cause becomes HIGH confidence |
| `K-2` is accepted | ❌ hypothesis **FALSIFIED** — the cause is `A5`, `A6` or `A7`; the corrected payload is still correct, but the historical failure remains unexplained |
| A retained Chargebee validation/error file is found naming another field | overrides everything above — that artefact outranks this inference |

---

## 8. Confidence summary and required actions

| Question | Answer | Confidence |
| :--- | :--- | :--- |
| Was the historical payload **invalid by construction** for a one-time price? | **Yes** | 🟢 **HIGH** (`E1`+`E2`+`E4`+`E5`+`E6`+differential) |
| Was `period: 1` / `period_unit: day` **the** trigger? | **Probably** | 🟡 **MEDIUM** (`A5`/`A6`/`A7` open) |
| Is the **corrected** payload the right thing to send? | **Yes** | 🟢 **HIGH** (mirrors every working charge price; vendor reference agrees) |
| Can the historical failure be proven **without a write**? | **No** | 🟢 **HIGH** — no artefact was retained; the canary is the proof |

**Required actions (in order):** obtain `G1` → run `K-1` and capture the raw response → if green, create the remaining 44 in batches → re-run the census (`314 → 359`) → re-run the storefront probe. Optional `K-2` converts the root cause from *probable* to *proven*; run it only with explicit permission and on a throwaway object.

---

**End of root-cause analysis.** No Chargebee object was created, modified or deleted in producing this document; the canaries in §3 are **proposed**, not executed.



