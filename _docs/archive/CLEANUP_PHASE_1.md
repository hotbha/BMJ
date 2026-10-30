# CLEANUP_PHASE_1.md — Zero-risk V1 cleanup: execution record

**Executed:** 16 October 2026
**Scope approved:** the **zero-risk set only** — (1) the `/api/test/orders` PII leak, (2) logs,
(3) generated artifacts, (4) tracked build outputs, (5) `.gitignore`. Nothing else.
**Status:** ✅ **executed and verified.** All three repositories compile/analyse/test exactly as before.
**Companion documents:** `SAFE_DELETE_LIST.md` (the per-file evidence), `B6_DECISION_REPORT.md`,
`STITCH_ALIGNMENT_REPORT.md`.

---

## 1. Scope — what was executed, and what was deliberately left alone

| # | Approved item | Executed | Detail |
| :--- | :--- | :--- | :--- |
| 1 | PII leak fix — `/api/test/orders` | ✅ | `OrdersController` deleted (closes **B2**) — §2.1 |
| 2 | Logs | ✅ | 30 tracked runtime logs untracked; 1 deleted; rules added — §2.2 |
| 3 | Generated artifacts | ✅ | 44 root scratch/harness outputs + ignored on-disk junk — §2.5, §2.6 |
| 4 | Tracked build outputs | ✅ | 61 MB `app.jar` untracked (kept on disk); `lush` build report already handled — §2.3 |
| 5 | `.gitignore` | ✅ | `bmjServer` +14 rules, root +9 rules, `Java.gitignore` decoy deleted — §2.4 |

**Deliberately NOT touched (unchanged, verified):**

| Item | Why it stayed |
| :--- | :--- |
| **The 14 unreferenced Flutter screens** | Explicit instruction. Not archived, not deleted, not edited. Classified in `B6_DECISION_REPORT.md` §5. |
| `lush` dead Dart set (`SAFE_DELETE_LIST.md` §C, 13 files) | Not in the approved five. Still available. |
| 22 Chargebee MCP session batch files (§A8/§5 F) | Not zero-risk: retiring them requires a `docs/CHARGEBEE_MCP.md` edit. |
| The ARCHIVE set (`ARCHIVE_LIST.md`) | Post-launch, separate reviewable commit. |
| `chargebee_catalog.json`, `batch1/2_*.json` | Live inputs to `scripts/chargebee/*`. |
| `fix_accounts.sql`, `seed_accounts.sql` | Possible UAT seeding input; untracked-file deletion is irreversible. |
| `chargebee-java-3.29.0.jar`, `chargebee-object-relationship.png`, `.venv-1/` | Same reason: ignored, but their deletion could not be proven valueless. |
| `Stitch/**` contents | Only the `.gitignore` rule that governs them was changed (§2.4). Not staged — that is task **B1**. |

## 2. Change log

### 2.1 The PII leak — `OrdersController` deleted (closes blocker **B2**)

```powershell
cd x:\BMJ\bmjServer
git rm -f -- src/main/java/com/bookmyjuice/controllers/OrdersController.java   # -f: freeze line-ending normalisation
```

**What it removed.** `GET /api/test/orders` → `orderService.fetchOrders()` = **every customer's orders**,
including the `shippingAddress` / `billingAddress` maps, amounts, dates and customer ids — served to an
**unauthenticated** caller, because `/api/test/**` is `permitAll` (`WebSecurityConfig.java:93`) and the
handler carried no `@PreAuthorize`. Its sibling `GET /api/test/ordersByCustomerId` went with it; that one was
**not** a leak (it resolves the id from the security context), but it had zero callers.

**Why delete rather than the one-line `@PreAuthorize("hasRole('ADMIN')")`:**

1. **Zero callers anywhere.** `rg -F 'OrdersController'` across all three repos returned only the class
   declaration and one javadoc `@link` — no configuration, no test, no tooling.
2. **Both routes already have production replacements** — `GET /api/orders/admin/all-orders` (ADMIN-only)
   and `GET /api/orders/by-customer`.
3. Deleting removes the surface **permanently** instead of guarding it, and shrinks the `/api/test` namespace
   (finding **T3**) by two routes and one `@Deprecated` class.

**Coupled edits made in the same change** (required by `CLEANUP_CANDIDATES.md` §6 row 5):

| File | Edit |
| :--- | :--- |
| `bmjServer/.../OrderController.java:53-56` | The javadoc `{@link OrdersController}` would have become a dangling reference → rewritten to prose |
| `docs/API.md:1786-1787` | Both Non-Production table rows marked **REMOVED 2026-10-16 (`B2`)** with the reason and the replacement |
| `docs/API.md:1063-1072` | `/api/orders/by-customer` section gains the removal note |
| `docs/BMJ_V1_SCOPE.md:96-103` | Controller list updated; new paragraph on why this route leaked and its siblings do not |
| `docs/BMJ_V1_SCOPE.md:205` | The freeze-change table row for `OrdersController` updated to "DELETED" |

**Proof:** `.\\mvnw.cmd -o -DskipTests compile` → **BUILD SUCCESS**, `Compiling 171 source files`
(the freeze compiled **172** — exactly one file fewer). No orphaned reference remains.

**What is still true of the namespace (unchanged, POST-LAUNCH):** `/api/test/**` remains `permitAll`
(findings **T3** / `G-8`). No unauthorised route in it returns another customer's PII any more:
`TestController` guards `/user`, `/mod`, `/admin`, `/chargebeeItems`, `/databaseItems` with `@PreAuthorize`
(only `/health`, `/all`, `/charge-items` are open, all non-PII); `MetadataTestController` is class-level
ADMIN-guarded (`:29`); the rest are the retired `410 Gone` probes. **B2 is closed.**

### 2.2 Logs — the `I5` churn

```powershell
cd x:\BMJ\bmjServer
git rm -r -f --cached -- logs   # 30 tracked runtime logs → untracked, KEPT ON DISK
git rm -f -- startup.log        # 16.3 KB captured console output, NO-MATCH → deleted
```

| Decision | Reason |
| :--- | :--- |
| Logs **untracked, not deleted** | They are the live runtime output of a running service. The goal was to stop repository churn, not to destroy operational history — `logs/archive/*.log` hold Feb–Aug 2026 entries that would otherwise be unrecoverable. **All 37 log files are still on disk.** |
| `startup.log` deleted outright | One-off captured console output (`git grep` NO-MATCH). Recoverable from git history. |

### 2.3 Tracked build outputs

```powershell
git rm -f --cached -- app.jar    # 61 MB fat jar → untracked, KEPT ON DISK
```

* `Dockerfile:37` is `COPY --from=builder /app/target/*.jar app.jar` — the container builds its own jar, so
  the committed 61 MB binary was pure churn and is **not** an input to any build.
* ⚠️ **Precondition before physically deleting the file** (`SAFE_DELETE_LIST.md` §B5): confirm nobody runs
  `java -jar app.jar` by hand on the VPS. The untrack alone is safe and reversible; the file is still on disk.
* `lush/android/build/reports/problems/problems-report.html` — **already handled by the freeze**: it is staged
  as deleted and `/android/build/` is in `lush/.gitignore:49`. Verified, no action needed.

### 2.4 `.gitignore` — the root cause of `I5` and a Stitch-freeze trap

**`bmjServer/.gitignore` (+14 rules, verified ignored):**

```
logs/
*.log
hs_err_pid*
replay_pid*
/app.jar            → git check-ignore -v logs/application.log  ⇒ .gitignore:39:logs/
                      git check-ignore -v app.jar               ⇒ .gitignore:51:/app.jar
```

* ⛔ **Never add a bare `*.jar` here.** It would override the `!.mvn/wrapper/maven-wrapper.jar` negation on
  line 3 and break `mvnw` on a fresh clone. That near-miss is exactly why the decoy below was dangerous.
* **`Java.gitignore` was deleted.** Git never reads a file with that name — its `*.log` rule had *no effect*,
  which is the verified root cause of the 30 committed logs. Its intent now lives in the real `.gitignore`.
  (`git ls-files Java.gitignore` before deletion: tracked; `git grep -F Java.gitignore`: NO-MATCH.)

**Root `.gitignore` (+9 rules) — the Stitch freeze trap:**

```
!Stitch/**/*.png
```

Line 10 of the root ignore file is a blanket `*.png`. `git check-ignore -v 'Stitch/…/screen.png'` matched it,
so **`git add Stitch/` would have committed 31 `code.html` + 3 `DESIGN.md` and silently dropped all 31
`screen.png` mockups.** A negation must follow the rule it overrides, so the new block is last.

| Proof | Before | After |
| :--- | :--- | :--- |
| `git add -n Stitch` (dry run) | **34 files** | **65 files** (31 html + 31 png + 3 md) |
| `git check-ignore -v Stitch/**/screen.png` | `.gitignore:10:*.png` | prints the **negation** (i.e. *not* ignored) |

### 2.5 Generated artifacts — 44 root files (43 tracked + 1 untracked)

Executed in `SAFE_DELETE_LIST.md` §A1–A7 order. All were previously proven `NO-MATCH` under `git grep`.

| Set | N | Files |
| :--- | ---: | :--- |
| A1 broken-redirect junk | 5 | `$null`, `Document`, `nul)`, `query`, `x` |
| A2 credential-bearing UAT scratch ⚠️ | 6 | `uat_token.txt`, `uat_signin.json`, `uat_signup.json`, `signin.json`, `temp_signin.json`, `temp_search.txt` |
| A3 generic scratch txt/json | 23 | `b64.txt`, `c1.txt`, `data1.json`, `f1_b64.txt`, `f1_data.json`, `fd.json`, `file1.json`, `gen_test.txt`, `nodetest.txt`, `out_test.txt`, `root_test.txt`, `script_b64.txt`, `tc1.json`, `tcdata.json`, `tcs.json`, `test_decode.txt`, `test_out.txt`, `test_simple.txt`, `test_write.txt`, `test123.txt`, `_data_b64.txt`, `build_out.md`, `_mcp_init.json` |
| A4 Appium page-source dumps | 3 | `ui.xml`, `ui2.xml`, `ui3.xml` |
| A5 one-off Python scratch | 2 | `_analyze_catalog.py`, `_extract_fails.py` |
| A6 regenerable harness outputs | 4 | `import_result.json`, `e2e_test_report.json`, `e2e_test_report_v2.json`, `e2e_test_report_v3.json` |
| A7 backup | 1 | `dbdiagram.mwb.bak` |

**Mechanism note (transparency).** `git rm -- $files` aborted on `dbdiagram.mwb.bak`, which turned out **never
to have been tracked**. The 43 tracked files are therefore staged with `git add -A -- $files` and show as
staged deletions (**`D` ×43**, verified); none is left unstaged.

⚠️ **The only irreversible deletion in this pass:** `dbdiagram.mwb.bak` was an untracked, ignored file, so no
git history holds it. Disclosed in full. (The live `dbdiagram.mwb` is untouched — it is an ARCHIVE candidate.)

⚠️ **Credential follow-up (`I4`).** `temp_signin.json` carried a UAT username/password pair. Deleting the file
does **not** purge it from history (`git log --all -- temp_signin.json` still reaches it). **Rotate that UAT
account and the `uat_token.txt` token.** While doing so I also **redacted the password that my own
`BMJ_LAUNCH_CHECKLIST.md:43` had reproduced in plaintext** — otherwise the freeze commit would have re-committed
the same secret inside a deliverable. `I4` now reads as a history-purge task.

**Regeneration check (no broken tooling):** the only remaining references to deleted outputs are their
**writers** — `scripts/tools/run_e2e_tests.py:343` writes `e2e_test_report_v3.json` and
`scripts/chargebee/import_catalog.py:148` writes `import_result.json`. Both recreate the file on the next run.

### 2.6 On-disk ignored junk (~21 MB, zero git impact)

| Removed | Size / count | Ignore rule |
| :--- | :--- | :--- |
| `AppiumServer.log` | 13.2 MB | `.gitignore:265 *.log` |
| `Redis-x64-5.0.14.1.msi` | 6.8 MB | `.gitignore:330 Redis-*.msi` |
| `logs/**` (root, incl. a Feb-2026 archive) | 10 files | `.gitignore:266 logs/` |
| `backend.log`, `server.log` | 160 KB + 5 KB | `*.log` |
| `lush/android/**/.kotlin/errors/*.log` | **295 files** | Gradle/Kotlin noise |
| `.pytest_cache/**`, `test-output/**`, `.e2e-reports/` | 9 paths | test-runner caches |

All were `Remove-Item`'d from disk only — they were never in the index, so **no commit is affected by this
section**. Confirmed gone afterwards; 5 items were deliberately kept (`fix_accounts.sql`, `seed_accounts.sql`,
`chargebee-java-3.29.0.jar`, `chargebee-object-relationship.png`, `.venv-1/`) — see §1.

---

## 3. Verification battery — all four green

| # | Check | Command | Expected | **Result** |
| :--- | :--- | :--- | :--- | :--- |
| 1 | Backend compiles | `cd bmjServer; .\\mvnw.cmd -o -DskipTests compile` | `BUILD SUCCESS` | ✅ **BUILD SUCCESS**, exit 0, `Compiling 171 source files` (freeze: 172 → exactly one fewer) |
| 2 | Flutter static analysis | `cd lush; dart analyze lib test integration_test` | **0 errors** | ✅ **0 errors** (38 warnings, 367 infos — both info-level against baseline) |
| 3 | Flutter tests | `cd lush; flutter test` | **351 passed / 12 failed** | ✅ **+351 −12** — byte-for-byte the baseline at `e1d11e6`; the 12 are the two known pre-existing suites (`subscription_screens_test.dart` ×11 ThemeCubit provider, `product_catalog_bloc_test.dart` ×1) |
| 4 | No `/api/test` caller orphaned | `rg -F '/api/test' lush/lib lush/test lush/integration_test scripts ops` | the known set only | ✅ Exactly the baseline: `run_e2e_tests.py:273,275` (CheckoutController routes, untouched), `fullstack_auth_and_pricing_test.dart:56,63` (410-Gone assertions), 1 comment in `welcome_header.dart:20` |
| 5 | No dangling reference to a deleted file | `rg -F` over `*.md`, `Makefile`, `*.ps1`, `*.py`, `*.json` | writers only | ✅ Only `run_e2e_tests.py:343` and `import_catalog.py:148` — both **write** those outputs |
| 6 | Ignore rules effective | `git check-ignore -v logs/application.log` / `app.jar` | matched | ✅ `.gitignore:39:logs/` and `.gitignore:51:/app.jar` |
| 7 | Stitch mockups committable | `git add -n Stitch` | 65 files | ✅ **65** (was 34) |

### 3.1 End state of the three repositories

| Repo | `git status --porcelain` | Interpretation |
| :--- | :--- | :--- |
| `bmjServer` | **`D` ×35**, `M` ×8, `??` ×2 | 35 = 30 logs + `startup.log` + `fix_bom.py` + `Java.gitignore` + `app.jar` + `OrdersController.java`; `??` ×2 = the freeze's new `CatalogController`/`UserProfileController` |
| root | **`D` ×43**, `M` ×4, `??` ×~22 | 43 = the §A deletions; the `??` are the deliverables + `Stitch/` + the audit harness |
| `lush` | `M` ×17, `D` ×3 | **Unchanged by this pass** — the 17 modified files are the freeze's own edits, the 3 deletions are pre-existing |

**Nothing in this cleanup is outside the approved five items**, and every changed path is accounted for above.

---

## 4. Revert instructions (everything except one file is reversible)

| Change | Revert |
| :--- | :--- |
| 43 root deletions | `git restore --staged --worktree -- <files>` (or `git checkout HEAD -- <file>` per file) |
| `OrdersController.java` | `git restore --staged --worktree -- src/main/java/com/bookmyjuice/controllers/OrdersController.java` (in `bmjServer`; restores the *committed* pre-deprecation version) |
| `logs/**`, `app.jar` untracked | `git restore --staged -- logs app.jar` (files never left the disk) |
| `startup.log`, `fix_bom.py`, `Java.gitignore` | `git restore --staged --worktree --` each path |
| `.gitignore` edits (both repos) | `git restore -- .gitignore` — but see §2.4: reverting the root rule re-hides all 31 Stitch mockups |
| `dbdiagram.mwb.bak` | ❌ **No revert** — untracked file, not in any history |

**Recommended sequencing:** this pass is intended to be folded into the **B1 freeze commit** *in its own
commit* (so the cleanup is reviewable separately from the freeze), together with `git add Stitch` and the two
`logs`/`app.jar` untracks. Then re-run rows 1–3 of §3 from the tag.

---

## 5. Root cause of `I5` (recorded so it cannot recur)

> **`bmjServer` tracked 30 runtime logs because the rule that was meant to prevent it lived in a file called
> `Java.gitignore`. Git only reads files named exactly `.gitignore`.**

Consequences that were all visible in this pass:

1. `git check-ignore -v logs/application.log` returned **nothing** — the logs were never ignored.
2. `logs/` churned on every run: **48 dirty index entries** (19 deleted + 26 untracked + 3 modified) that would
   have polluted the freeze commit.
3. The decoy file also contained a bare `*.jar` rule. Had it ever been renamed to `.gitignore`, it would have
   overridden the `!.mvn/wrapper/maven-wrapper.jar` negation and broken `mvnw` on a fresh clone. The rules were
   therefore merged **selectively**, not copied.

## 6. What was NOT executed, and why

| Held back | Reason |
| :--- | :--- |
| `lush` dead-Dart set (13 files, `SAFE_DELETE_LIST.md` §C) | Outside the approved five. Includes the 3-byte stubs and the 8 unreferenced helpers — all still proven dead. |
| 22 Chargebee MCP batch files (§5 F) | "Low" risk, not zero: retiring them requires marking the batch workflow retired in `docs/CHARGEBEE_MCP.md`. |
| Every ARCHIVE move (`ARCHIVE_LIST.md`) | Post-launch, separate commit — it rewrites 20 doc paths. |
| The 14 unreferenced screens | Explicit instruction; classified in `B6_DECISION_REPORT.md` §5. |
| `bmjServer/app.jar` **physical** deletion | Waiting on the VPS `java -jar app.jar` check (§2.3). Untracked only — the safe half. |
| `fix_accounts.sql`, `seed_accounts.sql`, `.venv-1/`, `chargebee-java-3.29.0.jar`, `chargebee-object-relationship.png` | Ignored, but their deletion is irreversible and their value could not be disproven. |
| Rewriting `BMJ_V1_SCOPE.md` §2's two dead-file entry points | The flows are reachable by other means; a freeze document is not silently rewritten (note recorded in `B6_DECISION_REPORT.md` §5.1). |

## 7. Next steps

| # | Action | Owner |
| :--- | :--- | :--- |
| 1 | **Commit this cleanup as its own commit** inside the **B1** freeze work, then push and tag `v1.0.0-launch` in all three repos | Repo owner |
| 2 | `git add Stitch` (65 files) — **only works because of §2.4**; the folder is currently untracked | Repo owner |
| 3 | Commit/stash the unrelated `home_tab.dart` / `menu_tab.dart` work (**B7**) so it does not ride inside the freeze | Repo owner |
| 4 | **Rotate** the UAT token and the `9999999901` account password; purge `temp_signin.json` from history (`I4`) | Backend + Ops |
| 5 | Confirm the VPS deploy does not use a hand-placed `app.jar`, then delete the file from disk | Backend |
| 6 | Run the **B5** staging smoke — now including the **B6** step (pause → resume → cancel in `/manage-subscriptions`) | QA |
| 7 | Verify `B3` / `B4` (order history with real data; the `D-2` backfill) | Backend + QA |
| 8 | Take the `B6_DECISION_REPORT.md` §5 screen decisions, then the ARCHIVE set, as separate post-launch changes | Product + Flutter |

---

*Executed 16 October 2026 against `bmjServer` `main` (`fa34ca9`) and root `feat/v1-launch-freeze`
(`HEAD be41c89`), with `lush` untouched. Every claim above is reproducible with the command shown in the same
row.*

