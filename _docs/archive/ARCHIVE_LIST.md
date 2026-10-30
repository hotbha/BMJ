# ARCHIVE_LIST.md — move, never delete (REVIEW FIRST — nothing moved yet)

> **STATUS: NOT EXECUTED.** History-preserving relocation of old docs, old SRS, legacy reports,
> deprecated design docs and one-off generators. Nothing here affects a V1 launch path.
> Rationale: [`CLEANUP_CANDIDATES.md`](CLEANUP_CANDIDATES.md) · deletions:
> [`SAFE_DELETE_LIST.md`](SAFE_DELETE_LIST.md).

## 1. Mechanism (recommended)

```powershell
cd x:\BMJ
git mv docs/business-requirements docs/archive/business-requirements        # per area
git mv docs/functional-specs     docs/archive/functional-specs
... (see the per-group commands below)
git commit -m "chore(docs): archive superseded V0 docs (no content change)"
```

Rules:

1. **`git mv` only** — the content stays in history *and* in the tree, at `archive/…`.
2. **Never fold this into the launch freeze commit.** It rewrites 20 doc paths and the links
   inside `BMJ_LAUNCH_CHECKLIST.md`, `PRODUCT_ALIGNMENT_REPORT.md` and `docs/README.md`.
3. Add `archive/README.md` (one paragraph: what this folder is, who owns it, "not a launch
   input").
4. Sequence: **after** the `v1.0.0-launch` tag (see `CLEANUP_CANDIDATES.md` §7).

## A. Old SRS / requirements (5 tracked + 1 root)

| Item | Why it is archive, not delete | Notes |
| :--- | :--- | :--- |
| `docs/business-requirements/BRD_Business_Requirements.md` | The V0 business-requirement baseline (June 2026); superseded by `docs/BMJ_V1_SCOPE.md`. Referenced by `PRODUCT_ALIGNMENT_REPORT.md` as *audited input*. | Keep for traceability of the audit |
| `docs/business-requirements/pricing-table.xlsx` | Pricing baseline behind that BRD; live pricing is Chargebee + `docs/PRICING_STRUCTURE.md` | Binary; move as-is |
| `docs/functional-specs/FUNCTIONAL_SPEC.md` | V0 functional spec (describes endpoints/flows since retired: portal, pricing pages, modify-schedule) | Actively misleading for V1 → must not stay in the live doc set |
| `docs/use-cases/USE_CASES.md`, `docs/use-cases/UC-BOTTLE-TRACKING.md` | V0 use cases incl. bottle tracking (out of V1 scope) | |
| `requirements.yaml` (root, 52 KB) | MVP requirement/guardrail dump dated 2026-03-27 (`version: 2.2.0-MVP`). Referenced only by `docs/architecture/ADR-004-unified-signup-flow.md` | Root clutter; archive under `archive/requirements.yaml` |

## B. Legacy reports (8 docs + 1 root report + generated output)

| Item | Why archived | Coupling |
| :--- | :--- | :--- |
| `E2E_BLACK_BOX_TEST_REPORT.md` (root) | Superseded black-box run; its own body is pre-freeze | `docs/TESTING_GUIDE.md:61` links it → move **both** in one commit |
| `docs/TESTING_GUIDE.md` | Describes the retired report location + pre-freeze flows | ← move with the report |
| `docs/test-cases/TEST_CASES.md` | V0 manual/automated test catalogue (~22 files worth of specs) | Superseded by the runnable suites + `BMJ_LAUNCH_CHECKLIST.md` §4 |
| `docs/test-registry/{TEST_REGISTRY,BUG_REGISTRY,COVERAGE_REPORT}.md` | V0 bug/coverage registries | `BMJ_LAUNCH_CHECKLIST.md` links `COVERAGE_REPORT.md` → repoint |
| `docs/test-baselines/TEST_BASELINE.md` | **The 12-failure baseline of record** — keep the *fact*, archive the *file* after repointing the link | `BMJ_LAUNCH_CHECKLIST.md` links it → repoint |
| `docs/QUALITY_MANAGEMENT.md` | V0 SDLC/QC process doc; entry/exit criteria superseded by the checklist | `BMJ_LAUNCH_CHECKLIST.md` links it → repoint |
| `docs/guides/RELEASE_NOTES.md` | Historically a "known issues" dumping ground, now stale | `docs/README.md` links it 4× |
| `test-output/{e2e_api_test_results.json,e2e_test_execution_report.md,e2e_test_summary.md}` | Generated run output | **Ignored by git** → DELETE instead (`SAFE_DELETE_LIST.md` §E), not archive |

## C. Deprecated design docs (7 tracked)

| Item | Why deprecated | Still-useful content? |
| :--- | :--- | :--- |
| `docs/DESIGN_SYSTEM.md` (42 KB) | Documents the pre-launch UI system; the shipped UI diverged (see the Flow-1..10 screens in `docs/BMJ_V1_SCOPE.md`) | Colour/typography tokens may still be quoted |
| `docs/DELIVERY.md` (17 KB) | Delivery domain spec incl. pincode serviceability tables | Live behaviour is in `DeliveryController` + `address_repository` |
| `docs/SUBSCRIPTIONS.md` (21 KB) | Describes pause/resume/cancel *screens and services* — precisely the capability blocked by **B6** | The 9-PM-cutoff rules are still business-relevant → archive, do not delete |
| `docs/PRICING_STRUCTURE.md` | Local pricing description; Chargebee is the pricing source of truth | |
| `docs/data_models_map.md` (36 KB) | V0 Dart↔Chargebee↔DB field map; the D-2/D-6 fixes changed the id mapping | Valuable for the next schema change → archive |
| `docs/ARCHITECTURE_OVERVIEW.md` (3 KB) | Brief V0 component overview; `ADR-001..004` + `docs/API.md` supersede it | |
| `docs/CACHING_STRATEGY.md` (1.7 KB) | **Self-declared not implemented**: *"PLANNED — Redis Cache Infrastructure … Status: Not implemented"* | Archive or delete; it is an aspiration, not a system |
| `dbdiagram.mwb` (root, 37 KB MySQL Workbench model) | Zero references; the schema of record is the JPA entities + migrations | Archive (keep for future ERD work) |

## D. One-off generators, ops harnesses and unreferenced assets

### D1. `scripts/generators/**` — 34 tracked files, all generating already-archived docs/tests

Evidence: the group is unreferenced by the launch set; representative `git grep` → **NO-MATCH**:
`gen7.py`, `gen7_final.py`, `gentc.py`, `gentc2.py`, `genfiles.py`, `genfull.py`, `gentest.py`,
`generate_tests.py`, `build_all.js`, `build_all.py`, `build_tcs1.js`, `gen_hash.py`.
Full list: `_brd_full.py`, `_cb_list.py`, `_g13.py`, `_gen.py`, `build_all.js`, `build_all.py`,
`build_doc.py`, `build_tcs1.js`, `gen_batch2.py`, `gen_e2e.js`, `gen_e2e_auth.py`,
`gen_e2e_cart.py`, `gen_e2e_catalog.py`, `gen_e2e_checkout.py`, `gen_hash.py`, `gen_not.py`,
`gen_notifications.py`, `gen_rtm.py`, `gen_tc.py`, `gen_tc_base.py`, `gen_tc1.py`, `gen_tcs.py`,
`gen7.py`, `gen7_final.py`, `generate_all.ps1`, `generate_catalog.py`, `generate_e2e_auth.py`,
`generate_tcs.js`, `generate_tests.py`, `genfiles.py`, `genfull.py`, `gentc.py`, `gentc2.py`,
`gentest.py`.

> The four `_`-prefixed files and the `gen7*/gentc*` family are scratch iterations of the same
> generator. If you prefer a smaller archive, these 12 can be **deleted** instead — the docs they
> produced are the artefacts that matter. `gen_batch2.py` must **stay** (it consumes
> `batch2_juice_plans.json`, a live import payload).

### D2. `scripts/tools/**` scratch (17 of 18 files)

`_write_files.ps1`, `_write_gaps.ps1`, `create_files.ps1`, `create_files.py`, `decode_run.py`,
`f1.py`, `final7.py`, `g.py`, `go.py`, `make_f7.py`, `makefiles.py`, `s1.py`, `s1_temp.py`,
`write_file.ps1`, `write_notif.py`, `write_test.ps1` — single-letter/near-empty helper scripts
(`g.py`, `go.py`, `s1.py`), all **NO-MATCH**.
**Keep:** `scripts/tools/run_e2e_tests.py` (live E2E harness).
Also `scripts/GenHash.java` → archive (one-off hash helper; `scripts/generators/gen_hash.py` is
its Python twin).

### D3. `ops/**` — 5 of 10 files superseded

Archive: `ops/test_fullstack.ps1`, `ops/test_fullstack_v2.ps1`, `ops/test_fullstack_final.ps1`,
`ops/test_signin.ps1`, `ops/test_debug.ps1` — five generations of the same ad-hoc full-stack
probe, all **NO-MATCH**.
**Keep:** `ops/find_active_ip.ps1` (7 refs), `ops/build_flutter_for_phone.ps1` (doc +
`package.json`), `ops/bootstrap.sh`, `ops/provision-vps.sh`, and **`ops/test_fullstack_dynamic.ps1`**
(linked from `docs/HUMAN_INTERVENTION_REQUIRED.md` — archiving it breaks a launch doc).

### D4. Unreferenced assets and scripts in `bmjServer`

| Item | Evidence | Recommendation |
| :--- | :--- | :--- |
| `bmjServer/spring-boot-jwt-authentication-spring-security-{architecture,flow}.png`, `bmjServer/spring-boot-refresh-token-jwt-example-flow.png` (82 KB total) | `git grep -n -F -e 'spring-boot-jwt'` → **NO-MATCH**; no image reference in `bmjServer/README.md` | Archive (generic Spring-tutorial diagrams, not BMJ assets) |
| `bmjServer/create-admin-user.sql` | `git grep -n -F -e 'create-admin-user.sql'` → **NO-MATCH** | Archive **and keep one copy handy for launch ops** — it is likely the admin bootstrap |
| `bmjServer/scripts/setup_chargebee_catalog.py` | `git grep` → **NO-MATCH** | Archive (superseded by root `scripts/chargebee/*`) |

## E. Design exports — `Stitch/**` (65 untracked files)

Google Stitch HTML/PNG screen exports, **completely untracked** (`git status` shows 33 unignored
entries + 32 ignored PNGs). Zero references from any code or launch doc; the mobile screens are
implemented in `lush/lib/views`.

Recommendation: move to `archive/design/stitch/` (or leave in place) — it costs nothing to keep
and is the only record of the design exploration. **Never** add it to the freeze commit; if you
would rather not carry it, it is untracked, so it is *already* excluded from the launch.

## F. Recommended archive-instead-of-delete (the 14 unreferenced Flutter feature screens)

These have **zero references** (verified by a case-insensitive sweep + `git grep`, all
`NO-MATCH`), so they are technically dead code. I recommend **archiving rather than deleting**
because each is the only implementation of a capability that Product may re-wire after launch —
most notably pause/cancel, which blocker **B6** leaves unresolved:

`lib/views/screens/subscription/{active,cancel,pause,resume}_subscription_screen.dart` ·
`lib/views/screens/subscription/subscription_plans_screen.dart` ·
`lib/views/screens/notification_centre_screen.dart` ·
`lib/views/screens/profile/address_screen.dart` ·
`lib/views/screens/orders/{order_catalog,order_checkout,order_item}_screen.dart` ·
`lib/views/widgets/my_bottles_widget.dart` ·
`lib/views/widgets/{subscription_card,subscription_plan_card,shimmer_subscription_card}.dart`

```powershell
cd x:\BMJ\lush
git mv lib/views/screens/subscription lib/archive/screens/subscription   # etc.
```

If Product confirms in writing that pause/cancel is a **support-process-only** fallback (B6
sign-off), promote these 14 into `SAFE_DELETE_LIST.md` §C instead.

## G. Explicitly NOT archived (do not move these)

| Item | Why |
| :--- | :--- |
| `docs/architecture/ADR-001..004` | Decision records of record; `ADR-003` is cited by `docs/BMJ_V1_SCOPE.md`, `ADR-004` by `PRODUCT_ALIGNMENT_REPORT.md`. Archiving drops the audit trail for the V1 decisions. |
| `docs/API.md`, `docs/BMJ_V1_SCOPE.md`, `BMJ_LAUNCH_CHECKLIST.md`, `PRODUCT_ALIGNMENT_REPORT.md`, `docs/HUMAN_INTERVENTION_REQUIRED.md` | The launch set itself. |
| `docs/DEPLOYMENT.md`, `docs/CICD_PIPELINE.md`, `docs/QUICKSTART.md`, `docs/guides/DEVELOPMENT_SETUP.md`, `docs/guides/DEVELOPMENT_TOOLS.md` | Deploy + onboarding for whoever runs tomorrow. |
| `docs/KNOWN_ISSUES.md`, `docs/WEBHOOK_RELIABILITY.md`, `docs/chargebee_final_state.md`, `docs/CHARGEBEE_MCP.md` | Live operational knowledge (webhooks + Chargebee state + MCP tooling). |
| `docs/README.md` | The index — it must be **edited** to reflect any archive, never moved silently. |
| `CHANGELOG.md`, `docker-compose.yml`, `Makefile`, `package.json`, `chargebee_catalog.json`, `batch1_generic_plans.json`, `batch2_juice_plans.json`, `scripts/chargebee/**`, `scripts/tools/run_e2e_tests.py` | Live launch/deploy/tooling paths (see `CLEANUP_CANDIDATES.md` §4.2). |

## H. Link-fix checklist that must accompany the archive commit

| File | Change |
| :--- | :--- |
| `docs/README.md` | Rewrite the Document Catalog: 20 entries move to `archive/…`; keep the KEEP list; note "🆕 V1 launch set: `BMJ_LAUNCH_CHECKLIST.md`, `PRODUCT_ALIGNMENT_REPORT.md`, `BMJ_V1_SCOPE.md`, `API.md`" |
| `BMJ_LAUNCH_CHECKLIST.md` | 3 links → `archive/…`: `docs/QUALITY_MANAGEMENT.md`, `docs/test-baselines/TEST_BASELINE.md`, `docs/test-registry/COVERAGE_REPORT.md` |
| `PRODUCT_ALIGNMENT_REPORT.md` | 10 audit references point into the archive (add one line in §1: *"linked paths refer to `archive/…` after the post-launch doc move"*) |
| `docs/TESTING_GUIDE.md` | Moves to the archive together with `E2E_BLACK_BOX_TEST_REPORT.md` (no link fix needed if moved as a pair) |
| `docs/HUMAN_INTERVENTION_REQUIRED.md` | **Pre-existing broken link** `auth_flows.md` → fix or drop; also avoid archiving `ops/test_fullstack_dynamic.ps1` |
| `docs/ADR-004-unified-signup-flow.md` | References `requirements.yaml` → repoint to `archive/requirements.yaml` |
| `docs/KNOWN_ISSUES.md`, `docs/CICD_PIPELINE.md` | Reference `docker-compose.yml` (not archived — no change) |

**Verification after the move:** no tracked file may reference a moved path. Re-run the §2.2
harness with the archived filenames as the names list and expect 0 hits outside `archive/`:

```powershell
rg -F -l --no-ignore -e 'BRD_Business_Requirements.md' -e 'FUNCTIONAL_SPEC.md' `
   -e 'USE_CASES.md' -e 'DESIGN_SYSTEM.md' -e 'data_models_map.md' -e 'TEST_BASELINE.md' `
   x:\BMJ --glob '!**/archive/**' --glob '!**/.git/**'      # expect only the two launch docs, then fix them
```

## I. Summary

| Group | Items | Mechanism |
| :--- | ---: | :--- |
| A — Old SRS / requirements | 6 | `git mv` → `docs/archive/`, `archive/requirements.yaml` |
| B — Legacy reports | 9 (1 ignored output → DELETE) | `git mv` → `docs/archive/`, `archive/reports/` |
| C — Deprecated design docs | 8 (incl. `dbdiagram.mwb`) | `git mv` → `docs/archive/design/`, `archive/` |
| D — Generators / ops / assets | 34 + 17 + 5 + 1 + 3 + 1 = 61 | `git mv` → `archive/scripts/`, `archive/ops/`, `archive/assets/` |
| E — Stitch design exports | 65 untracked | Move or leave; never committed |
| F — Flutter feature screens (sign-off pending) | 14 | `git mv` inside `lush` → `lush/archive/` |
| **Total archived artefacts** | **~163** | Zero runtime impact · 1 dedicated commit · after the freeze tag |

> Reminder: archiving is a **post-launch** action (`CLEANUP_CANDIDATES.md` §7). Nothing in this
> document is required to launch, and nothing here has been executed.


