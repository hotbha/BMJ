# CLEANUP_CANDIDATES.md — SAFE V1 Cleanup (classification only)

> **STATUS: REVIEW REQUIRED — NOTHING HAS BEEN DELETED, MOVED OR COMMITTED.**
> **Date:** 2026-10-16 · **Scope:** `x:\BMJ` root repo + nested `lush` + nested `bmjServer`
> **Owner sign-off needed before any action.** Pair documents:
> [`SAFE_DELETE_LIST.md`](SAFE_DELETE_LIST.md) · [`ARCHIVE_LIST.md`](ARCHIVE_LIST.md)

## 1. What this document is

A file-by-file classification of the repository into **KEEP / ARCHIVE / DELETE**, driven by
one rule set:

| Class | Rule |
| :--- | :--- |
| **KEEP** | Reachable from a V1 launch path (customer flow, deploy, CI, health check) **or** referenced by a launch document. |
| **ARCHIVE** | Old docs, old SRS, legacy reports, deprecated design docs, one-off generators — value as history, no launch role. Move, never delete. |
| **DELETE** | Temp/scratch artefacts, confirmed dead code, unused routes, old test endpoints — after proof of no references. |

Everything below is evidence-backed. No file is removed by this document.

## 2. Method and evidence protocol

Every candidate was checked with **two independent tools** and, for the risky sets, **two
passes**:

1. `git ls-files` — is the file tracked, and in which repo?
2. `git grep -n -F -e '<name>'` — per-repo reference search (note: `git grep` does **not**
   cross nested repos).
3. `rg -F -l --no-ignore --hidden -e '<name>' <root>` — workspace-wide search across all
   three repos, excluding `.git/`, `node_modules/`, `target/`, `build/`, `.dart_tool/`,
   `.venv*/`, `.pytest_cache/`, `**/*.log`, `.gradle/`, `.kotlin/`, `Stitch/`.
4. **Case-insensitive second pass** (`--ignore-case`) for the Flutter tree. *This mattered:*
   `lib/views/models/User.dart` and `Order.dart` are referenced with different casing than
   the git index (`user.dart`), so a case-sensitive-only sweep would have produced two
   **false** dead-code verdicts. They are **KEEP**.
5. `git status --porcelain --ignored=matching` — separates tracked junk from ignored/untracked
   on-disk junk (which needs no commit, only a local delete).

Reproducible harness used for the multi-file sweeps (created by this review, untracked, listed
for deletion in `SAFE_DELETE_LIST.md` §E):

```powershell
powershell -NoProfile -File x:\BMJ\_cleanup_refcheck.ps1 `
  -Root x:\BMJ -Names x:\BMJ\_cleanup_names_root.txt -Out x:\BMJ\_cleanup_refs_root.txt
# same harness with -Root x:\BMJ\lush -IgnoreCase , -Root x:\BMJ\bmjServer , -Root x:\BMJ
```

Reference sweep results are archived as `_cleanup_refs_root.txt`, `_cleanup_refs_lush_ic.txt`,
`_cleanup_refs_java.txt`, `_cleanup_refs_server.txt`, `_cleanup_refs_tool.txt`.

### 2.1 A warning about the server sweep

A reference-count sweep on Java returned **27 classes with no reference outside their own
file**, including `HealthController`, `AddressController`, `CartController`, `InvoiceController`
and every `*WebhookController`. **This is not dead code.** Spring wires controllers, repositories,
`@Component`s and `@RestControllerAdvice` by annotation scanning / reflection, so static
reference counting is *invalid* for them. Proof:

```powershell
rg -n -i 'health' docker-compose.yml ops .github .vscode bmjServer/Dockerfile
# docker-compose.yml:129:      test: ["CMD","curl","-f","http://localhost:8080/api/health"]
# bmjServer/Dockerfile:50:    CMD curl -f http://localhost:8080/api/health || exit 1
# ops/provision-vps.sh:86:    location /api/health {
```

`HealthController` has zero Java references yet is the **container and nginx liveness probe**.
Deleting it would break deploys that currently look healthy. **Therefore: no Java class is
proposed for deletion on reference-count evidence alone** — only the explicitly non-production
`/api/test/**` routes are proposed (see §5 D).

## 3. Inventory

| Area | Tracked files | Verdict split |
| :--- | ---: | :--- |
| Root repo (`x:\BMJ`, excl. nested repos) | 204 entries (incl. 2 nested-repo gitlinks) | 66 DELETE (§5 A + F) · ~85 ARCHIVE (mostly `scripts/`, `Stitch/` untracked) · rest KEEP |
| `docs/` | 36 tracked + 1 untracked (`BMJ_V1_SCOPE.md`) | 20 ARCHIVE · 17 KEEP |
| `lush` | 374 | 13 DELETE now · 14 DELETE-with-sign-off · rest KEEP |
| `bmjServer` | src + 34 root/log junk files | 34 DELETE · 4 DELETE (route classes) · rest KEEP |
| On-disk ignored junk | ~330 paths | DELETE (no commit needed) |

## 4. KEEP — reachable from a V1 launch path

### 4.1 Application and service code

| Item | Why it must stay |
| :--- | :--- |
| `lush/**` (except §5 C) | The V1 client. Every file in the 10 in-scope flows is reachable: `login_page.dart`, `google_signup_screen.dart`, `phone_signup_screen.dart`, `phone_otp_verification_screen.dart`, `phone_login_screen.dart`, `dashboard.dart`, `home_tab.dart`, `menu_tab.dart`, `menu.dart`, `product_catalog_screen.dart`, `cart_screen.dart`, `order_history_page.dart`, `subscription_management_screen.dart`, `welcome_header.dart`, blocs, repositories, services, `main.dart` route table. |
| `bmjServer/src/**` | The V1 backend. Includes **`HealthController`** (`/api/health` is the Docker + nginx health probe, `bmjServer/Dockerfile:50`, `docker-compose.yml:129`, `ops/provision-vps.sh:86`) — zero Java references, fully live by HTTP. |
| `bmjServer/src/main/java/.../controllers/CheckoutController.java` | **Non-production, but a live dependency**: `scripts/tools/run_e2e_tests.py:273,275` calls `/api/test/oneTimeCheckoutPageUrl` and `/api/test/cartCheckout`. |
| `.../SelfServePageController.java`, `.../PricingPageController.java` | The **410 Gone regression guard** depends on them: `lush/integration_test/fullstack_auth_and_pricing_test.dart:56,63`. Deleting the route flips 410 → 404 and **fails the guard**. |
| `bmjServer/pom.xml`, `mvnw`, `mvnw.cmd`, `.mvn/**`, `Dockerfile`, `Dockerfile.dev`, `.github/workflows/ci.yml`, `.env.example`, `.gitignore` | Build, container, CI. `maven-wrapper.jar` is referenced by `mvnw`, `mvnw.cmd`, `MavenWrapperDownloader.java` and un-ignored in `.gitignore:3`. |

### 4.2 Root tooling that is live (even though nothing greps its name)

| Item | Evidence |
| :--- | :--- |
| `Makefile`, `package.json`, `package-lock.json` | `.vscode/tasks.json:168-273` runs `npm run e2e`, `e2e:physical`, `e2e:emulator`, `e2e:video`, `e2e:report`, `e2e:clean`, `e2e:full`, `e2e:checkout`; `package.json` defines them plus `phone:debug` → `ops/build_flutter_for_phone.ps1` and `phone:ip` → `ops/find_active_ip.ps1`. `Makefile` mirrors the same Patrol targets. **Not deletable.** |
| `docker-compose.yml` | Deployment topology; referenced by `docs/CICD_PIPELINE.md`, `docs/KNOWN_ISSUES.md`; hosts the `/api/health` healthcheck. |
| `.mcp.json`, `.vscode/mcp.json`, `.clinerules/cline-guardrails.md` | Tooling policy (Chargebee MCP guardrails). Zero code references = expected for config. |
| `.vscode/**`, `.github/**`, `.devcontainer/**` | Editor tasks, 4 CI workflows, devcontainer. |
| `ops/find_active_ip.ps1`, `ops/build_flutter_for_phone.ps1`, `ops/bootstrap.sh`, `ops/provision-vps.sh`, `ops/test_fullstack_dynamic.ps1` | Referenced by `.vscode/launch.json`, `package.json`, `docker-compose.yml`, `docs/HUMAN_INTERVENTION_REQUIRED.md`. |
| `CHANGELOG.md` | Referenced by `docs/guides/DEVELOPMENT_SETUP.md`. |
| `scripts/tools/run_e2e_tests.py` | The black-box E2E harness; the only code caller of the legacy checkout routes. |
| `scripts/chargebee/**` (9 files) | Live Chargebee tooling (`chargebee_mcp_client.py`, `chargebee_session.ps1`, `import_catalog.py`, `import_chg.ps1`, `chargebee_setup_catalog.py`, `chargebee_import_full.py`, `list_tools.py`); referenced by `docs/CHARGEBEE_MCP.md`. Note `_fix_mcp_config.py` is scratch (see §5 A). |
| `chargebee_catalog.json` (44 KB), `batch1_generic_plans.json`, `batch2_juice_plans.json` | **Not scratch: these are the catalog snapshot and the import payloads.** Referenced by `scripts/chargebee/import_chg.ps1`, `scripts/chargebee/chargebee_setup_catalog.py`, `scripts/chargebee/chargebee_import_full.py`, `scripts/generators/gen_batch2.py` and three docs. KEEP (or archive as catalog provenance — never blind-delete). |

### 4.3 Documentation of record

| Item | Why |
| :--- | :--- |
| `BMJ_LAUNCH_CHECKLIST.md`, `PRODUCT_ALIGNMENT_REPORT.md`, `docs/BMJ_V1_SCOPE.md` | The launch decision set (2 untracked deliverables + 1 untracked scope doc — see blocker **B1**). |
| `docs/API.md` | Frozen API contract incl. the Non-Production Endpoint inventory. |
| `docs/HUMAN_INTERVENTION_REQUIRED.md` | Manual steps the launch depends on. |
| `docs/DEPLOYMENT.md`, `docs/CICD_PIPELINE.md`, `docs/QUICKSTART.md`, `docs/guides/DEVELOPMENT_SETUP.md`, `docs/guides/DEVELOPMENT_TOOLS.md` | Deploy + onboarding. |
| `docs/architecture/ADR-001..004` | Decision record of record; `ADR-003` is cited by `docs/BMJ_V1_SCOPE.md`, `ADR-004` by `PRODUCT_ALIGNMENT_REPORT.md`. ADRs are immutable history — archive only if you intend to drop the audit trail. |
| `docs/chargebee_final_state.md`, `docs/CHARGEBEE_MCP.md`, `docs/KNOWN_ISSUES.md`, `docs/WEBHOOK_RELIABILITY.md` | Chargebee state + MCP tooling + live issues + webhook behaviour. `chargebee_final_state.md` is cited by `docs/BMJ_V1_SCOPE.md`. |
| `docs/README.md` | Documentation index — **must be edited** as part of any archive move (§7). |

## 5. DELETE — summary of the four delete sets

Full per-file evidence lives in [`SAFE_DELETE_LIST.md`](SAFE_DELETE_LIST.md).

| Set | Count | Contents | Risk |
| :--- | ---: | :--- | :--- |
| **A — Root scratch (tracked)** | 44 | Broken-redirect junk (`$null`, `Document`, `nul)`, `query`, `x`), credential-bearing UAT scratch (`uat_signin.json`, `uat_signup.json`, `uat_token.txt`, `signin.json`, `temp_signin.json`, `temp_search.txt`), 23 generic scratch txt/json, Appium `ui*.xml`, 2 one-off `.py`, 4 regenerable harness outputs, `dbdiagram.mwb.bak` | **Zero** — all report `NO-MATCH` under `git grep`. |
| **F — Chargebee MCP session batch files** | 22 | `_cb_*`, `_chargebee_*`, `chargebee_init.json`, `chargebee_items_payload.json`, `chargebee_mcp_generated_catalog.json` | **Low** — requires marking the batch workflow retired in `docs/CHARGEBEE_MCP.md` (§6 row 2). Live tooling (`scripts/chargebee/**`) is untouched. |
| **B — `bmjServer` junk (tracked)** | 34 | 30 `logs/**` files (5 top-level + 25 archived), `startup.log`, `fix_bom.py`, `Java.gitignore`, `app.jar` (61 MB) | **Low** — `app.jar` needs one confirmation (§6 row 3). |
| **C — `lush` dead Dart** | 13 now / 14 with sign-off | 3 three-byte stubs, 2 already-deleted-on-disk files, 8 unreferenced helpers; 14 feature screens need Product sign-off | **Low for the 13**, see §5.1 warning. |
| **D — Server non-production routes** | 4 classes | `TestController` (8 routes), `MetadataTestController` (8 routes), `MetadataTestService` (orphaned by it), `OrdersController` (2 routes) | **Low** — no callers anywhere; **closes blocker B2**. |
| **E — On-disk ignored junk (no commit)** | ~330 paths / ~21 MB | `AppiumServer.log` 12.6 MB, `Redis-x64-5.0.14.1.msi` 6.8 MB, 6 `hs_err_pid*.log`, 2 `replay_pid*.log`, `backend.log`, `server.log`, `chargebee-java-3.29.0.jar`, `chargebee-object-relationship.png`, `logs/**` (10), `test-output/**` (3), empty `.e2e-reports/`, `.pytest_cache/**` (5), `fix_accounts.sql`, `seed_accounts.sql`, `.venv-1/` (duplicate venv), `lush/android/**/.kotlin/errors/*.log` (~295) | **Zero** — all proven ignored via `git check-ignore -v`. |

### 5.1 The three traps this review found (read before approving)

1. **Basename casing hides references.** `User.dart`/`Order.dart` look dead under a
   case-sensitive sweep but are imported as `user.dart`/`order.dart` (`Order.dart` ←
   `lib/views/screens/order_history_page.dart`; `User.dart` ← 15 files incl.
   `lib/bloc/AuthBloc/auth_state.dart`, `lib/bloc/UserBloc/user_state.dart`). **Both are KEEP.**
2. **`lush/README.md` lists filenames, so it "references" files that are otherwise dead** — a
   docs mention is not a code dependency, but it does mean the README needs a refresh if you
   delete the widgets it lists.
3. **"Non-production" ≠ "unreferenced".** `CheckoutController`, `SelfServePageController` and
   `PricingPageController` are marked `@Deprecated`/NON-PRODUCTION yet are load-bearing for the
   E2E harness and the 410 regression guard. Only `TestController`, `MetadataTestController`
   (+ `MetadataTestService`) and `OrdersController` have **zero** callers.

## 6. Coupled decisions — deleting X requires editing Y

| # | Candidate | Coupled artefact that must change in the same commit | Evidence |
| :--- | :--- | :--- | :--- |
| 1 | `E2E_BLACK_BOX_TEST_REPORT.md` (root) | `docs/TESTING_GUIDE.md:61` links to it → archive both together | `git grep -n -F E2E_BLACK_BOX_TEST_REPORT.md` → 1 hit |
| 2 | `_cb_*.bat` / `_chargebee_*.bat` / `*_payload.json` / `*_tools.json` (16 files) | `docs/CHARGEBEE_MCP.md` documents this whole batch-file workflow → mark the section retired, or keep the files | the only doc hit is `docs/CHARGEBEE_MCP.md` |
| 3 | `bmjServer/app.jar` (tracked, 61 MB) | `Dockerfile:37` copies `/app/target/*.jar`, so the file is only named in build *comments* (`application-dev/prod.properties:2`). Confirm nobody runs `java -jar app.jar` by hand on the VPS | `git grep -n -F app.jar` |
| 4 | `bmjServer/logs/**` (30 files) | Add `logs/` + `*.log` to `bmjServer/.gitignore`; `Java.gitignore` (which intends exactly that) is **not** read by git — that is the root cause. 20 of the 30 are already deleted in the working tree, so the freeze commit will carry it | `git check-ignore -v --no-index logs/application.log` → **no output** |
| 5 | `TestController` + `MetadataTestController` + `MetadataTestService` + `OrdersController` | `docs/API.md` Non-Production table, `docs/BMJ_V1_SCOPE.md` §5 controller list, and the `TestController` javadoc that points `/api/test/user` → `/api/v1/user/profile` | `rg -n -F 'api/test'` over freeze docs |
| 6 | 20 archived `docs/*.md` | `docs/README.md` catalog + 4 links: `BMJ_LAUNCH_CHECKLIST.md` → `docs/QUALITY_MANAGEMENT.md`, `docs/test-baselines/TEST_BASELINE.md`, `docs/test-registry/COVERAGE_REPORT.md`; `PRODUCT_ALIGNMENT_REPORT.md` → 10 archived docs (audit references) | `.md` link extraction (§2 harness) |
| 7 | `ops/test_fullstack*.ps1` (4 of 5) | **Do not archive `test_fullstack_dynamic.ps1`** — `docs/HUMAN_INTERVENTION_REQUIRED.md` links it | `.md` link extraction |
| 8 | `docs/HUMAN_INTERVENTION_REQUIRED.md` | Pre-existing **dangling link** to `auth_flows.md` — fix while touching docs; unrelated to this cleanup | `Test-Path x:\BMJ\docs\auth_flows.md` → `False` |

## 7. Recommended sequencing

**Pre-launch (inside the freeze commit, blockers B1/B7):** §5 E (disk junk, no commit impact),
§5 B, §5 A, §5 D. Mechanical and low-risk — and §5 D removes the **B2** PII leak as a side effect.

**Immediately after, before tagging:** the verification battery, so the deletions provably did
not regress anything —
`bmjServer\mvnw.cmd -o -DskipTests compile` · `lush\dart analyze lib test integration_test` ·
`lush\flutter test` (**must stay at 351 passed / 12 failed**) · E2E smoke (`npm run e2e` or
`make test-e2e`).

**Post-launch (separate, reviewable commit):** all ARCHIVE moves. A pure file move with zero
runtime impact, but it rewrites 20 doc paths and the links inside the launch docs, so it must
not be folded into the frozen commit.

## 8. Open questions — need your call

| # | Question | Why it matters |
| :--- | :--- | :--- |
| Q1 | The 14 unreferenced **feature screens** (`pause_/cancel_/resume_/active_subscription`, `subscription_plans_screen`, `notification_centre_screen`, `address_screen`, `order_*_screen`, `my_bottles_widget`, `subscription(_plan)_card`, `shimmer_subscription_card`): DELETE or ARCHIVE? | They are the **only** implementation of pause/cancel, and blocker **B6** says subscribers cannot pause/cancel in-app. If Product wants that after launch, these files are the head start. Recommendation: **ARCHIVE, do not delete.** |
| Q2 | Credential-bearing UAT files (`uat_token.txt`, `uat_signin.json`, `uat_signup.json`, `signin.json`, `temp_signin.json`): DELETE, or move to `archive/evidence/` first? | They are cited as evidence in `BMJ_LAUNCH_CHECKLIST.md` (findings I4/I7). Deleting is better for secrets; keeping a copy preserves the audit trail. Either way **rotate the credentials**. |
| Q3 | `chargebee_catalog.json` + `batch1/batch2` payloads: KEEP at root, or ARCHIVE under `archive/chargebee/`? | They are live inputs to `scripts/chargebee/*`; moving them changes those scripts' relative paths. Cheapest safe answer: **KEEP**. |

## 9. What this cleanup does **not** do

- It does not touch the **B2** route differently from §5 D (deleting `OrdersController` closes it;
  if you prefer a one-line fix, add `@PreAuthorize("hasRole('ADMIN')")` to `getAllOrders` instead
  and move `OrdersController` to the Q1-style archive set).
- It does not resolve **B1** (freeze/commit), **B3/B4/B5** (the D-6/D-2 verifications and the live
  smoke), **B6** (pause/cancel product decision), **B7** (`home_tab.dart`/`menu_tab.dart` inside
  the freeze tree), or **I5** (log churn) — but §5 B/I5 and §7 are the mechanical part of I5.
- It does not delete anything. **Approve, then run.**

---

*Produced by the SAFE V1 cleanup review, 2026-10-16. Companion files: `SAFE_DELETE_LIST.md`,
`ARCHIVE_LIST.md`. Evidence harness: `_cleanup_refcheck.ps1` (+ `_cleanup_refs_*.txt`).*



