# GitHub Push Report

> **Date:** 2026-10-30 · Three repositories, all pushed.

## 1. `lush` (Flutter app) — `github.com/bookmyjuice/lush`

**Branch:** `main` · **Range:** `e1d11e6..28357c1` · **Status:** ✅ pushed, `origin/main` = `28357c1`

| Hash | Commit | Group |
| :--- | :--- | :--- |
| `a8908e6` | chore(release): harden release signing, manifest and android config | C1 |
| `4265f30` | feat(design-system): vibrant_zest tokens, widgets and typography | C3 |
| `9822927` | feat(auth): consolidate to Google + phone OTP | C2 |
| `e281be1` | feat(ui): Stitch visual migration across Home, PDP, Cart and Subscription | C4 |
| `04c0bf1` | feat(subscription): catalog 2.0, plans and management flows | C5 |
| `b4f694a` | feat(subscription): day-wise delivery schedule and nextDeliveryAt | C6 |
| `9146410` | test(qa): extend widget, integration and device coverage | C7 |
| `28357c1` | chore(build): untrack generated Gradle report artifact | cleanup |

**Files changed:** 142 · **+17,218 / −16,258**

Commit order is C1 → C3 → C2 → … (design system before auth) so that **every commit compiles on its own**; the brief's suggested order would have made C2 reference untracked widgets. Each commit's body names its strategy group.

**Verification at each commit:** `flutter analyze --no-pub lib` → **0 errors** (8/8 commits). After the final commit: `flutter test` → **418/418 passing**.

**Excluded from the push (verified):** `*.jks`, `keystore_name.jks`, `clientkeystore`, `key.properties`, `*.err`, `.env`, `_secrets/`. `git diff --name-only origin/main..HEAD` contains no signing material. The only secret-shaped line in the diff is a **removal** (the deleted hardcoded Chargebee key in `lib/config/api_config.dart`).

## 2. `bmjServer` (Spring backend) — `github.com/bookmyjuice/bmjServer`

**Branch:** `main` · **Range:** `fa34ca9..1f17048` · **Status:** ✅ pushed, `origin/main` = `1f17048`

| Hash | Commit |
| :--- | :--- |
| `2118797` | chore(repo): stop tracking build artifacts and runtime logs |
| `054963f` | feat(auth): Google + phone OTP consolidation on the server |
| `9a04038` | feat(catalog): catalog 2.0 endpoints and day-wise delivery schedule |
| `cad691e` | chore(repo): ignore runtime logs, jars and pid files |
| `1f17048` | chore(repo): drop stale smoke-test pid and ignore pid files |

**Files changed:** 60 · **+2,689 / −139,536** (the deletions are 30 committed log files and `app.jar`).

**Verification:** `mvn -DskipTests -o compile` → **exit 0** after the build-artifact commit and again after the final commit. (`mvn test` was not run — the server has its own CI and needs its test database.)

## 3. `BMJ` (parent: docs, tooling, submodules) — `github.com/hotbha/BMJ`

**Branch:** `feat/v1-launch-freeze` · **Status:** ✅ pushed as a **new remote branch** (GitHub returned the PR-creation link)

| Hash | Commit |
| :--- | :--- |
| `ccb338e` | chore(repo): consolidate docs, prune captures, remove build junk |
| `e96af0b` | docs(release): add release-candidate documentation |
| `305020b` | chore(submodule): bump lush and bmjServer to release-candidate commits |

The branch was local-only before this pass; it now exists on the remote with the consolidation work. A pull request into `main` is the natural next step if you want it merged.

## 4. Secret scan before push

| Pattern | Result |
| :--- | :--- |
| `test_ai_…` in the app diff | one match — the **removed** literal in `api_config.dart` (good) |
| `BEGIN PRIVATE KEY`, `sk_live` | none |
| `*.jks`, `key.properties` in the diff | none |

**Still exposed in history (not introduced by this pass):** Chargebee MCP keys in `.clinerules/cline-guardrails.md`, `.vscode/mcp.json`, `docs/CHARGEBEE_MCP.md`, and the two `android`-password keystores. Both are recorded as H1/H2 in `RELEASE_CANDIDATE_CHECKLIST.md`; rotation is a human step and history rewriting is a separate decision.

## 5. Post-push state

| Check | Value |
| :--- | :--- |
| `lush` working tree | clean, `main` == `origin/main` |
| `bmjServer` working tree | clean, `main` == `origin/main` |
| `BMJ` working tree | clean, `feat/v1-launch-freeze` == `origin/feat/v1-launch-freeze` |
| Tests | 418/418 |
| Analyze errors | 0 |
| Root documents | 12 (single checklist + supporting audits + operations + changelog) |
| Archive | `_docs/archive/` — 29 documents |
| Screenshots | 29 images indexed in `SCREENSHOT_INDEX.md` |
