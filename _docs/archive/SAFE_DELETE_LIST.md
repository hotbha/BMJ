# SAFE_DELETE_LIST.md — evidence-backed deletions (REVIEW FIRST — nothing deleted yet)

> **STATUS: NOT EXECUTED.** Do not run any command below until `CLEANUP_CANDIDATES.md` has been
> reviewed and this list approved. Every row carries its proof of no references.
> Classification rationale: [`CLEANUP_CANDIDATES.md`](CLEANUP_CANDIDATES.md).
> History-preserving moves live in [`ARCHIVE_LIST.md`](ARCHIVE_LIST.md) instead.

## 0. How to execute (after approval)

```powershell
# Root repo (tracked scratch)
cd x:\BMJ
git rm -q -- <files...>
git rm -q --  '$null' Document 'nul)' query x      # quote the weird names

# Nested repos are separate repositories
cd x:\BMJ\bmjServer ; git rm -q -- app.jar startup.log fix_bom.py Java.gitignore logs
cd x:\BMJ\lush      ; git rm -q -- lib/widgets/app_drawer.dart   # etc.

# Ignored on-disk junk (§E) — no commit needed
cd x:\BMJ ; Remove-Item -Force AppiumServer.log, backend.log, server.log, 'Redis-x64-5.0.14.1.msi'
```

**Mandatory verification battery (must match the pre-cleanup baseline):**

| Check | Command | Expected |
| :--- | :--- | :--- |
| Backend compiles | `bmjServer\mvnw.cmd -o -DskipTests compile` | `BUILD SUCCESS` |
| Flutter static analysis | `lush\dart analyze lib test integration_test` | **0 errors** |
| Flutter tests | `lush\flutter test` | **351 passed, 12 failed** (identical to baseline at `e1d11e6`) |
| No `/api/test` caller was orphaned | `rg -n -F '/api/test' lush/lib lush/test lush/integration_test scripts ops` | only `run_e2e_tests.py:273,275`, `fullstack_auth_and_pricing_test.dart:56,63`, 1 comment |
| Diff is exactly the intended set | `git status --porcelain` in all three repos | matches this list |

## A. Root repo — tracked scratch (66 files, `git rm`)

A1–A7 = 44 scratch artefacts · A8 = 22 Chargebee MCP session files (coupled doc edit).

### A1. Broken-redirect junk (5) — shell-redirect accidents, never created on purpose

| File | Size | Content | Evidence |
| :--- | ---: | :--- | :--- |
| `$null` | 0 B | empty | 0 bytes (nothing can depend on it); no script path reference in any repo |
| `Document` | 0 B | empty | 0 bytes; `git grep -n -F -e 'Document'` → prose hits only, never this path |
| `nul)` | 16 B | `File Not Found` | `git grep -n -F -e 'nul)'` → **NO-MATCH** |
| `query` | 7 B | `MySQL` | `git grep -n -F -e 'query'` → prose hits only, never this path |
| `x` | 9,649 B | stray copy of `BottleTrackingController.java` (`@RequestMapping("/api/bottles")`); hash `E3A86C68…53A3` matches **no** file under `bmjServer/src` | `git grep -n -F -e 'x'` → letter `x` only |

### A2. Credential-bearing UAT scratch (6) — **rotate the tokens after deleting**

| File | Why it is dead | Evidence |
| :--- | :--- | :--- |
| `uat_token.txt` | UAT bearer token captured for a manual call | `git grep -n -F -e 'uat_token.txt'` → **NO-MATCH** |
| `uat_signin.json`, `uat_signup.json` | Hand-made request bodies | `git grep -n -F -e 'uat_signin.json'` → **NO-MATCH** |
| `signin.json` | Same | `git grep -n -F -e 'signin.json'` → **NO-MATCH** |
| `temp_signin.json`, `temp_search.txt` | Same; currently only *mentioned* in the launch docs as evidence of findings I4/I7 | `git grep -n -F -e 'temp_signin.json'` → **NO-MATCH** |

### A3. Generic scratch text/json (23) — `git grep` NO-MATCH per name

`b64.txt` · `c1.txt` · `data1.json` · `f1_b64.txt` · `f1_data.json` · `fd.json` ·
`file1.json` · `gen_test.txt` · `nodetest.txt` · `out_test.txt` · `root_test.txt` ·
`script_b64.txt` · `tc1.json` · `tcdata.json` · `tcs.json` · `test_decode.txt` ·
`test_out.txt` · `test_simple.txt` · `test_write.txt` · `test123.txt` · `_data_b64.txt` ·
`build_out.md` · `_mcp_init.json`

```powershell
cd x:\BMJ
foreach ($p in @('c1.txt','b64.txt','tcdata.json','_mcp_init.json','build_out.md')) { git grep -n -F -e $p }  # → NO-MATCH x5
```

### A4. Appium / UI dumps (3)
`ui.xml`, `ui2.xml`, `ui3.xml` — Appium page-source dumps (`git grep` **NO-MATCH**). `ui2.xml`
and `ui3.xml` are the same size (12,729 B), i.e. the same dump captured twice.

### A5. One-off python scratch (2)
| File | Evidence |
| :--- | :--- |
| `_analyze_catalog.py` | `git grep -n -F -e '_analyze_catalog.py'` → **NO-MATCH** (it *reads* `chargebee_catalog.json`, which stays) |
| `_extract_fails.py` | `git grep -n -F -e '_extract_fails.py'` → **NO-MATCH** |

### A6. Regenerable harness outputs (4) — proven write-only targets

| File | Evidence it is an output, not an input |
| :--- | :--- |
| `import_result.json` | `scripts/chargebee/import_catalog.py:148` → `with open("import_result.json", "w") as f:` |
| `e2e_test_report_v3.json` | `scripts/tools/run_e2e_tests.py:343` → `with open('e2e_test_report_v3.json', 'w') as f:` |
| `e2e_test_report.json`, `e2e_test_report_v2.json` | Superseded generations of the same output; `git grep -n -F -e 'e2e_test_report_v2.json'` → **NO-MATCH** |

### A7. Backup (1)
`dbdiagram.mwb.bak` — `git grep -n -F -e 'dbdiagram.mwb.bak'` → **NO-MATCH** (the live
`dbdiagram.mwb` is ARCHIVEd, not deleted — see `ARCHIVE_LIST.md`).

## B. `bmjServer` — tracked junk (34 files, `git rm` in that repo)

| # | File(s) | Proof of no references | Note |
| :--- | :--- | :--- | :--- |
| B1 | `logs/application.log`, `logs/auth.log`, `logs/chargebee.log`, `logs/error.log`, `logs/webhook.log` + `logs/archive/**` (25) = **30 tracked runtime logs** | `git ls-files logs \| wc` = 30; `git check-ignore -v --no-index logs/application.log` → **no output** (never ignored). 20 are *already deleted* in the working tree: `git status --porcelain -- logs` = 48 dirty entries | Add `logs/` + `*.log` to `bmjServer/.gitignore` in the same commit |
| B2 | `startup.log` (16.3 KB) | `git grep -n -F -e 'startup.log'` → **NO-MATCH** | Captured console output |
| B3 | `fix_bom.py` (1.2 KB) | `git grep -n -F -e 'fix_bom.py'` → **NO-MATCH** | One-off BOM fixer |
| B4 | `Java.gitignore` | `git grep -n -F -e 'Java.gitignore'` → **NO-MATCH**; git never reads it — which is *why* B1's logs got committed | Merge its `*.log` rule into `.gitignore` |
| B5 | `app.jar` (**61 MB committed binary**) | `git grep -n -F -e 'app.jar'` → `Dockerfile:37 COPY --from=builder /app/target/*.jar app.jar` and `application-{dev,prod}.properties:2` **comments only** | **Precondition:** confirm no manual `java -jar app.jar` deploy on the VPS (`CLEANUP_CANDIDATES.md` §6 row 3) |

## C. `lush` — dead Dart, safe set (13 files, `git rm`)

Proof: two independent passes agree these have **zero references** in `lush` —
(1) basename sweep, (2) **case-insensitive** sweep, plus
`git grep -n -F -e '<name>'` → `NO-MATCH for all 24 patterns` for the widget/screen set.

### C1. Three-byte stubs (3) — empty placeholders

| File | Size | Content |
| :--- | ---: | :--- |
| `lib/views/models/juices_view.dart` | 3 B | empty |
| `lib/views/models/juice_list_view.dart` | 3 B | empty |
| `lib/views/models/plan_service.dart` | 3 B | empty (not the real `PlanService`) |

### C2. Already deleted in the working tree — formalise them (2)

| File | Evidence |
| :--- | :--- |
| `lib/services/subscription_service_v2.dart` | `git status --porcelain` → ` D` (deleted, unstaged, **still tracked**) |
| `lib/views/screens/subscription/modify_schedule_screen.dart` | ` D` — and `docs/BMJ_V1_SCOPE.md` §3 already records the day-wise schedule feature as **Removed** |

### C3. Unreferenced helpers / widgets / models (8)

| File | Primary class | Reference proof |
| :--- | :--- | :--- |
| `lib/widgets/app_drawer.dart` | `AppDrawer` | `git grep -n -F -e 'app_drawer'` → **NO-MATCH** (it *imports* `User.dart`; nothing imports it) |
| `lib/widgets/hero_header.dart` | `HeroHeader` | **NO-MATCH** |
| `lib/widgets/stats_strip.dart` | `StatsStrip` | **NO-MATCH** |
| `lib/views/models/detailed_juice_card.dart` | `DetailedJuiceCard` | **NO-MATCH** |
| `lib/views/models/signup_request.dart` | `SignupRequest` | **NO-MATCH** (the live signup payload is inline in `AuthBloc`) |
| `lib/utils/font_utils.dart` | `FontUtils` | **NO-MATCH** |
| `lib/utils/text_utils.dart` | `TextUtils` | **NO-MATCH** |
| `lib/theme/app_icons.dart` | `AppIcons` | **NO-MATCH** |

> ⚠️ `lush/README.md` lists several of these filenames in its file-tree — that is a docs
> mention, not a code dependency. If you delete them, refresh the README in the same commit.

## D. Server — non-production route classes (4 files, requires the compile check)

| File | Routes removed | Proof of zero callers |
| :--- | :--- | :--- |
| `bmjServer/.../controllers/OrdersController.java` | `GET /api/test/orders`, `GET /api/test/ordersByCustomerId` | `rg -n -F '/api/test'` across `lush/lib`, `lush/test`, `lush/integration_test`, `scripts`, `ops`, `bmjServer/src/test` → **no hit for either route**. **Deleting this file closes blocker B2** (the anonymous all-customer-order + address PII leak). |
| `bmjServer/.../controllers/TestController.java` | 8 routes (`/all`, `/user`, `/mod`, `/admin`, `/chargebeeItems`, `/databaseItems`, `/health`, `/charge-items`) | Same sweep → **no caller**. `git grep -n -F -e 'TestController' -- '*.java'` → only `TestController.java` itself. Production replacements exist: `CatalogController` (`/api/v1/catalog/charge-items`) and `UserProfileController` (`/api/v1/user/profile`). |
| `bmjServer/.../controllers/MetadataTestController.java` | 8 routes (`/api/test/metadata/**`) | Same sweep → **no caller** (already `@PreAuthorize("hasRole('ADMIN')")`) |
| `bmjServer/.../services/MetadataTestService.java` | — (service) | Only referenced from `MetadataTestController.java:24,46`; **orphaned by the deletion above** (verify with `mvn compile`) |

**Explicitly NOT deletable (live dependencies, despite being non-production):**
`CheckoutController` (`scripts/tools/run_e2e_tests.py:273,275`), `SelfServePageController`
(`/api/test/portal` 410 guard), `PricingPageController` (`fullstack_auth_and_pricing_test.dart:56`).
`ItemService.getChargeItemsWithCategoriesAndSizes()` stays — `CatalogController:58` uses it.

**Coupled doc edits for §D:** `docs/API.md` Non-Production table · `docs/BMJ_V1_SCOPE.md` §5
controller list · `TestController` javadoc pointers to the production replacements.

### A8. Chargebee MCP session batch cluster (22) — delete **only** with the coupled doc edit

These are ad-hoc `curl` session files from the Chargebee MCP onboarding sessions. Their only
references are **each other** and `docs/CHARGEBEE_MCP.md` (which documents the workflow), so
the deletion requires that doc section to be marked retired in the same commit
(`CLEANUP_CANDIDATES.md` §6 row 2). The live equivalents remain: `scripts/chargebee/**` +
`.vscode/mcp.json`.

`_cb_data_lookup_call.bat` · `_cb_data_lookup_init.bat` · `_cb_data_lookup_init_payload.json` ·
`_cb_data_lookup_tools.bat` · `_cb_data_lookup_tools_payload.json` · `_cb_generate_catalog.bat` ·
`_cb_generate_catalog_payload.json` · `_cb_onboarding_tools.bat` · `_cb_retrieve_item.bat` ·
`_cb_retrieve_item_payload.json` · `_cb_search_addons.bat` · `_cb_search_addons_payload.json` ·
`_cb_search_generics_payload.json` · `_cb_search_plans.bat` · `_cb_search_plans_p2_payload.json` ·
`_cb_search_plans_payload.json` · `_chargebee_init.bat` · `_chargebee_tools.bat` ·
`_chargebee_tools_payload.json` · `chargebee_init.json` · `chargebee_items_payload.json` ·
`chargebee_mcp_generated_catalog.json` (0 bytes)

**Stays (live or documented):** `chargebee_tools_full.json` ← `scripts/chargebee/list_tools.py`;
`chargebee_data_lookup_tools.json` + `chargebee_init_payload.json` ← `docs/CHARGEBEE_MCP.md`;
`chargebee_catalog.json` + `batch1_generic_plans.json` + `batch2_juice_plans.json` ← import scripts.

## E. On-disk ignored junk (no commit impact, ~21 MB) — delete freely

All proven ignored, so removing them changes **no** git state:

| Path | Evidence |
| :--- | :--- |
| `AppiumServer.log` (12.61 MB), `backend.log`, `server.log` | `.gitignore:265 *.log` |
| `hs_err_pid{12480,14360,26472,27920,42756,48924}.log` | `.gitignore:322 hs_err_pid*.log` |
| `replay_pid{12480,27920}.log` | `.gitignore:323 replay_pid*.log` |
| `Redis-x64-5.0.14.1.msi` (6.79 MB) | `.gitignore:330 Redis-*.msi` |
| `chargebee-java-3.29.0.jar` | `.gitignore:334 *.jar` |
| `chargebee-object-relationship.png` | `.gitignore:10 *.png` |
| `logs/**` (10 files incl. Feb-2026 archive) | `.gitignore:266 logs/` |
| `.e2e-reports/` (empty dir), `test-output/**` (3 files) | `.gitignore:230 test-output/`, `.gitignore:7 .e2e-reports/` |
| `.pytest_cache/**` (5 files) | `.pytest_cache/.gitignore:2 *` |
| `fix_accounts.sql`, `seed_accounts.sql` | `.gitignore:212 *.sql` |
| `.venv-1/` (duplicate virtualenv) | `.venv-1/.gitignore:1 *` |
| `lush/android/**/.kotlin/errors/*.log` (~295 files) | ignored; pure Gradle/Kotlin noise |

> `fix_accounts.sql` / `seed_accounts.sql` may be useful UAT seeding input — review before
> deleting if you want to keep the ability to re-seed.

## F. Audit artefacts created by this review (12) — delete once this list is approved

Untracked helper files, not part of the product:
`_cleanup_refcheck.ps1`, `_cleanup_names_{root,lush,java,server,tool}.txt`,
`_cleanup_refs_{root,lush,lush_ic,java,server,tool}.txt`.
Keep them only while the three reports are being reviewed (they are the raw evidence).

## G. NOT in this list — needs an explicit decision (do not delete silently)

| Item | Why it is held back |
| :--- | :--- |
| 14 unreferenced **feature screens** in `lush` (`active_subscription_screen`, `cancel_subscription_screen`, `pause_subscription_screen`, `resume_subscription_screen`, `subscription_plans_screen`, `notification_centre_screen`, `address_screen`, `order_catalog_screen`, `order_checkout_screen`, `order_item_screen`, `my_bottles_widget`, `subscription_card`, `subscription_plan_card`, `shimmer_subscription_card`) | Zero references (verified twice), **but** they are the only implementation of pause/cancel/resume and of order-detail UI — blocker **B6** may want them. Recommendation: **ARCHIVE** (`ARCHIVE_LIST.md` §D). |
| Credential-bearing UAT files | Listed for DELETE in §A2, but preserved-as-evidence is a legitimate alternative (`CLEANUP_CANDIDATES.md` §8 Q2). |
| `chargebee_catalog.json`, `batch1_generic_plans.json`, `batch2_juice_plans.json` | Live inputs to `scripts/chargebee/*`. KEEP. |
| `bmjServer/app.jar` | DELETE only after the VPS deploy check (§B5 precondition). |
| `lush/lib/main.dart` route entries for retired screens (`/email-signup`, `/signup-method-selection`, …) | Deleting the screens without deleting their routes is safe; deleting the **routes** is finding **I6** and is POST-LAUNCH. |

---

*Nothing in this file has been executed. Approve `CLEANUP_CANDIDATES.md` first, then run the
sections you approve. Re-verify with the battery in §0.*


