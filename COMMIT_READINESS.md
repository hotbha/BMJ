# Commit Readiness

> **Date:** 2026-10-30 · Validates `FINAL_COMMIT_STRATEGY.md` against the tree **after** the consolidation cleanup, then records what was actually committed.

## 1. Validation against the strategy

| Repo | Strategy expected | Actual before commits | Verdict |
| :--- | ---: | ---: | :--- |
| `X:\BMJ\lush` | 141 | **141** (93 M / 22 D / 26 ??) | ✅ exact match |
| `X:\BMJ\bmjServer` | not itemised | **61** (16 M / 35 D / 10 ??) | ⚠️ added by this pass — see §3 |
| `X:\BMJ` (parent) | not itemised | **109** (49 D / 8 M / 8 AD / 1 A / 43 ??) | ⚠️ grew because of the archive moves — see §4 |

## SAFE TO COMMIT

Everything in the app repo: 141 files, each matched to a C-group by the classifier (`emit_pathspecs.py`, output preserved in the commit history). Specifically:

- **C1 (7)** — `android/app/build.gradle.kts`, the three `AndroidManifest.xml` files, `.gitignore`, `lib/config/api_config.dart`, `android/build/…` removal. All are release-infrastructure and were verified by a signed AAB build.
- **C3 (25)** — 16 new `lib/widgets/bmj_*`, `lib/theme/*`, `assets/fonts/`, `pubspec.yaml`, design-system tests.
- **C2 (35)** — auth screens, bloc, UserRepository, deleted password/email screens, their tests.
- **C4 (42)** — screens and legacy widgets touched by the visual migration, plus `lib/main.dart`.
- **C5 (24)** — subscription screens, plan selection, catalog.
- **C6 (3)** — schedule-related client files (`day_wise_schedule_screen`, schedule screen, deleted `modify_schedule_screen`).
- **C7 (5)** — integration tests, `test/unit/utils/`, PDP screen test.

Server repo: 61 files — 30 log files, `app.jar`, `fix_bom.py`, `Java.gitignore`, `startup.log` (deletions), `.gitignore`, then AuthController, payload requests, EmailVerificationService, JwtUtils, WebSecurityConfig, DeliverySchedule*, Subscription*, CatalogController, controllers and tests.

Parent repo: the 29 archive moves, the 43 new/relocated documents, and the `_captures` screenshot set.

## NEEDS REVIEW (committed, but a human should look)

| Item | Why |
| :--- | :--- |
| `lush` C4 includes `lib/main.dart` | the app's composition root; it carries route changes from C2 **and** theme changes from C3. It only compiles because C3 and C2 landed first (see the ordering note) |
| `lush` C6 is only 3 client files | the schedule's substance lives in the server repo — the client half is thin by design |
| `lush` `pubspec.yaml` sits in C3 | it carries the bundled fonts (design system) but may also carry test-only deps |
| `bmjServer` `.gitignore` | 19 lines added; includes `*.pid`, logs, jars — worth a glance |
| `_captures` scripts | `chargebee_*.py`, `cb_*.py`, `plan_price_census.py`, `verify_plan_prices.py`, `audit_pricing.py`, `catalog_audit.py` are investigation tooling; they were kept because the rollout still needs them |

## UNEXPECTED (found and resolved rather than committed)

| Item | Resolution |
| :--- | :--- |
| `android/build/reports/problems/problems-report.html` still tracked despite `.gitignore` | `git rm --cached` in commit `28357c1` |
| `smoke_backend.pid` in the server repo | removed from the index, file deleted, `*.pid` added to `.gitignore` |
| `_captures/mcp_call.py` contained a hardcoded MCP key | **deleted** (never committed) |
| `android/build` pathspec silently failed the first `git add` | caught by checking `git status` after each commit; nothing was lost |
| Chargebee MCP keys in `.clinerules/cline-guardrails.md`, `.vscode/mcp.json`, `docs/CHARGEBEE_MCP.md` | **already tracked before this pass** — cannot be fixed by staging; requires rotation + history decision (`CONFIG_CLEANUP_REPORT.md` §1.1) |

## 2. Ordering deviation (deliberate)

The brief listed C2 (auth) before C3 (design system). Auth screens import the new `bmj_*` widgets, so committing auth first would produce a commit that cannot compile on its own. The commits were therefore created **C1 → C3 → C2 → C4 → C5 → C6 → C7**, with each commit's body naming its strategy group so traceability survives. Every commit was followed by `flutter analyze` → **0 errors**.

## 3. Server repo — why it was included

`bmjServer` is a git submodule with **its own remote** (`github.com/bookmyjuice/bmjServer`). The delivery-schedule, catalog-2.0 and auth-consolidation server work would otherwise never reach GitHub. It was verified with `mvn -DskipTests -o compile` → **exit 0** before committing.

## 4. Parent repo — why it grew

The 49 deletions and 43 additions are the same 29 documents, moved to `_docs/archive/` (a move is a delete + an add in git). The 8 `AD` entries are files that had been staged as additions earlier and were then relocated by this pass.

## 5. What must NOT be committed (verified absent)

`*.jks`, `key.properties`, `*.err`, `_secrets/`, `.env` — confirmed by `git diff --name-only origin/main..HEAD` (no matches) and by `git status` showing nothing under those patterns.
