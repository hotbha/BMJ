# Chargebee Go-Live Recommendation

> **Site:** `bookmyjuice-test` (TEST) · **Task:** `T6` · **Date:** 2026-10-16
> **Status:** 🔒 **READ-ONLY. This document authorises nothing by itself.**
> **Inputs:** `T1`–`T5` — [`CHARGEBEE_FINAL_PRICE_MATRIX.md`](CHARGEBEE_FINAL_PRICE_MATRIX.md) · [`CHARGEBEE_IMPORT_ROOT_CAUSE.md`](CHARGEBEE_IMPORT_ROOT_CAUSE.md) · [`CATALOG_PRICE_LOADING_VERDICT.md`](CATALOG_PRICE_LOADING_VERDICT.md) · [`CATALOG_LEGACY_ITEM_REPORT.md`](CATALOG_LEGACY_ITEM_REPORT.md)

---

# ✅ RECOMMENDATION: **A — Chargebee data creation MAY proceed**

**Subject to five mandatory conditions (§2.2).** Recommendation **B — *additional engineering work required first* — is not warranted**, and §2.1 explains why every argument for B fails against measured evidence.

**In one sentence:** the price values are now *proven approved* (workbook = payload, 45/45), the target ids are *proven free*, the prices would be *served* by the existing code the moment they exist, and the one remaining unknown — the historical import failure — is neutralised by creating **one** row before the other 44.

---

## 1. Evidence summary — what each task produced

| Task | Deliverable | Question answered | Result | Weight |
| :-- | :--- | :--- | :--- | :-- |
| `T1` | `CHARGEBEE_FINAL_PRICE_MATRIX.md` | join workbook ↔ Chargebee ↔ payload into 45 priced rows | ✅ **45 rows, 15 items, 0 mismatches, 0 id collisions** | 🟢 decisive |
| `T2` | (same document, §3) | do the 45 planned prices match the approved table? | ✅ **45/45 exact** — workbook, approved table and payload all agree | 🟢 decisive |
| `T3` | `CHARGEBEE_IMPORT_ROOT_CAUSE.md` | why did the previous import fail? | 🟡 **payload invalid by construction (HIGH)**; `period: 1 day` the specific trigger (**MEDIUM — unproven**); canary defined | 🟡 managed by canary |
| `T4` | `CATALOG_PRICE_LOADING_VERDICT.md` | if all 45 existed, would the catalog return them? | ✅ **YES** — the dead batch pre-fetch is bypassed by a working per-item fallback (`PR-17` is **not** a blocker) | 🟢 decisive |
| `T5` | `CATALOG_LEGACY_ITEM_REPORT.md` | are legacy items leaking into the storefront? | ❌ **falsified** — 15 items served, 0 legacy items; latent risk only | 🟢 removes a blocker |
| — | `CATALOG_PRICE_MATRIX.md` | the census underpinning all of the above | ✅ 15 items / 314 prices / **0** `bmj-item-*` prices | 🟢 baseline |

**Net position:** this is a **pure data creation** of 45 rows on 15 existing, healthy `charge` items. No repair, no migration, no re-pointing, no schema change, no subscription impact, and no existing Chargebee object has to be modified.

**What the change delivers when it lands:** every one of the 15 storefront products stops returning `"prices":[]` and instead returns **3 sizes with real prices** — i.e. the V1 catalog becomes commercially usable, which is exactly what `PR-18` / `B14` records as missing.

**What remains true after the change:** the 45 rows are the *entire* delta. `abc200` stays excluded, the plans are untouched, and the subscriptions are unaffected.

---

## 2.1 Recommendation B is not warranted — argument by argument

| Argument for "more engineering first" | Why it does not hold |
| :--- | :--- |
| *"The import already failed once; we don't know why."* | The historical payload is **invalid by construction** for a one-time price (it sends `period`, `period_unit`, `trial_*` and `tiers`, all documented as `plan`/`addon`-only — `T3` `E1`–`E6`), and the corrected shape **matches all 5 charge prices that already work on this site**. The residual unknown is answered by **`K-1`** — one row, observed, *before* the batch. Blocking 45 known-good rows on an unknown that a one-row canary resolves is disproportionate. |
| *"`PR-17` might hide the prices."* | Measured false. The pre-fetch fails on **100 %** of requests (`limit : It should not be more than 100`, 15+ log occurrences), so `preFetchedPrices` is always `null` and the **working** per-item path always runs (`T4` §4). The storefront is not blocked by code. |
| *"Legacy junk might surface."* | Measured false — `20 − 5 = 15` items returned, each legacy item logged as skipped (`T5` §2). The leak is **latent**, and its fix (`R-1`–`R-4`) is code-side and independent of this data change. |
| *"The prices were never approved."* | Resolved **by this validation**: the business workbook (`docs/business-requirements/pricing-table.xlsx`, the stated source of truth) agrees with the payload **45/45**; `P-1`, `P-2`, `P-3`, `P-5` are closed (`T1` §7). Only **`P-4` (GST)** remains, and it is a field-level decision (`is_taxable: true`), not a blocker. |
| *"The ids might collide."* | Asserted: **0** collisions with existing price ids and **0** with existing item ids (`T1` §2 `A4`). |

---

## 2.2 The five mandatory conditions (all must hold)

| # | Condition | Why |
| :-: | :--- | :--- |
| `M-1` | **Explicit human authorisation (`G1`)** to write, using the destructive `onboarding_agent`. Every measurement to date used the read-only `data_lookup_agent`. | No write is authorised by any document's existence — including this one |
| `M-2` | **Canary first (`K-1`)**: create **one** row (`bmj-item-mix-punch-200ml`, ₹129.00, corrected shape), **capture the raw response verbatim**, confirm it reads back — then batch the remaining **44**. | Converts the last unknown (`T3`) into a known fact before committing 45 rows; a bulk import's failure mode is **partial success** (`T3` `E7`) |
| `M-3` | **Corrected payload shape** — omit `period`, `period_unit`, `trial_period`, `trial_period_unit`, `tiers`; add `is_taxable: true`; keep the literal size token in `name`/`description` (`C-1`…`C-4`). | The historical shape is the prime suspect (`T3` §2); the token is required by the reader (`T4` `C-2`) |
| `M-4` | **Post-creation verification**: re-run the census — item prices `314 → 359`, `charge`-type prices `5 → 50`, items with zero prices `15 → 0`, **0** rows attached outside the 15 target ids — then re-run storefront probe `2b` and confirm each product returns **3** sizes. | Creation is not "done" until the reading side is **measured**, not assumed |
| `M-5` | **Rollback agreed before writing**: the only objects touched are the **45 new price ids**; rollback = delete/unpublish exactly those 45. Name the owner. | The only action that looks irreversible, made reversible on paper first |

### Recommended, **not** blocking

| # | Item | Note |
| :-: | :--- | :--- |
| `N-1` | `PR-17` — paginate the price pre-fetch (`T4` §7) | 🟡 Performance/observability. Fix by **paginating**, never by merely raising the bound (`T4` `F-4`) |
| `N-2` | `R-1`–`R-4` — exact family allow-list, positive BMJ marker, regression test, log levels (`T5` §7) | Removes the latent `PR-19` leak at its source |
| `N-3` | Correct `D-1`…`D-4` (`T1` §6): `docs/PRICING_STRUCTURE.md`, `scripts/chargebee/chargebee_setup_catalog.py`, `docs/chargebee_final_state.md:80`, and the `is_taxable` gap | Two of these are active traps for the next operator |
| `N-4` | Refresh `PRODUCTION_READINESS_REPORT.md` / `BMJ_LAUNCH_CHECKLIST.md` (`PR-18`, `B14`, `B10`) with the corrected `PR-17` severity and the price approval | Keeps the gate list truthful |
| `N-5` | **`git add` this document and its four companions** | They are **untracked** — the same failure class as `PR-1` / `B8`, where the artefact that closes a gate never reaches the repository |

---

## 3. What remains open after creation

| # | Open item | Owner | Blocking? |
| :-: | :--- | :--- | :--- |
| `P-4` | Is GST included in the stored paise? (`is_taxable: true` is the recommendation) | Finance + Product | ❌ not blocking the create — but must be settled before **live** billing |
| `PR-17` | Paginate the price pre-fetch (`T4` §7) | Backend | ❌ not blocking visibility; recommended in the same window |
| `PR-19` | Latent legacy leak — exact family allow-list + regression test (`T5` `R-1`–`R-4`) | Backend | ❌ not blocking; the leak does not occur today |
| `D-1`…`D-4` | Stale/false documentation (`T1` §6) | Docs owner | ❌ not blocking; two are active traps |
| `B10` | `PR-17` row in the launch checklist | Release owner | ❌ severity updated, gate unchanged |
| `B14` | Closes **only** once the 45 rows exist **and** the post-creation census (`M-4`) is green | Release owner | ✅ the point of this exercise |

---

## 4. Scope discipline — what this recommendation does **not** authorise

To be unambiguous, Recommendation A permits **one** thing:

> **Create 45 one-time `charge` item prices on the 15 existing `bmj-item-*` items, using the corrected payload (`C-1`…`C-4`), canary-first, in the TEST site `bookmyjuice-test` — and nothing else.**

It explicitly does **not** authorise: creating or modifying items, item families or plans; touching the 5 existing charge prices; deleting or archiving any legacy object; creating customers, subscriptions, orders or invoices; changing the app's source; or performing any write in **production**. Those require separate, explicit approval — and the `PR-19` hygiene items are code changes, covered by `N-2`, not by this data action.

---

## 5. Decision, sign-off and how to proceed

| Gate | Requirement | State |
| :--- | :--- | :--- |
| `G1` | Explicit human authorisation to write to Chargebee (`M-1`) | ⛔ **not given** |
| `G2` | Product sign-off on the 45 prices | ✅ **SATISFIED BY THIS VALIDATION** — the business workbook (`pricing-table.xlsx`) matches the payload **45/45** (`T1` §7: `P-1`, `P-2`, `P-3`, `P-5` closed; `P-4` = field-level GST choice) |
| `G3` | `PR-17` shipped first | 🔄 **NO LONGER A GATE** — reclassified by `T4`; recommended via `N-1` |
| `G4` | Price-creation mechanism agreed | ✅ **RECOMMENDED: canary-first** (`M-2`) |
| `G5` | Rollback path agreed and owned | ⛔ **open** — name the owner for `M-5` |

**Sequence once `G1` and `G5` are in place:** `M-3` corrected payload → `M-2` create `bmj-item-mix-punch-200ml` and read it back → if green, create the remaining **44** in batches → `M-4` census (`314 → 359`, `5 → 50`, `15 → 0`) → storefront probe `2b` (3 sizes per product) → close `B14` → then the non-blocking items `N-1`–`N-5`.

### Cross-reference

| Document | Role in this decision |
| :--- | :--- |
| [`CHARGEBEE_FINAL_PRICE_MATRIX.md`](CHARGEBEE_FINAL_PRICE_MATRIX.md) | the 45 approved rows + the assertions (`T1`/`T2`) |
| [`CHARGEBEE_IMPORT_ROOT_CAUSE.md`](CHARGEBEE_IMPORT_ROOT_CAUSE.md) | why the previous attempt failed, and the canary (`T3`) |
| [`CATALOG_PRICE_LOADING_VERDICT.md`](CATALOG_PRICE_LOADING_VERDICT.md) | the **YES** that removes `PR-17` as a gate (`T4`) |
| [`CATALOG_LEGACY_ITEM_REPORT.md`](CATALOG_LEGACY_ITEM_REPORT.md) | the falsified leak + the latent fix (`T5`) |
| [`CATALOG_PRICE_MATRIX.md`](CATALOG_PRICE_MATRIX.md) | the census (§10 record of the corrections applied) |
| [`CHARGEBEE_PRICE_CREATION_PLAN.md`](CHARGEBEE_PRICE_CREATION_PLAN.md) | the operational payload/gates this recommendation triggers |

---

**End of recommendation.** **Recommendation A — Chargebee data creation may proceed**, subject to `M-1`…`M-5`. No Chargebee object was created, modified or deleted in producing this document.


