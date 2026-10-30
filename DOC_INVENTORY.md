# Document Inventory

> **Date:** 2026-10-30 · Consolidation pass. **Executed:** the ARCHIVE moves and DELETE removals in this document are already applied.

Result: **12 markdown files remain in the repository root** (was 40), **29 documents archived**, **4 cleanup-scratch documents archived**, zero root-level duplicates.

## KEEP — release-critical, current (12 in root)

| File | Why it survives |
| :--- | :--- |
| `RELEASE_CANDIDATE_CHECKLIST.md` | **Single source of truth** for release status |
| `FINAL_COMMIT_STRATEGY.md` | The commit plan C1–C7 with exact file lists |
| `LAUNCH_HARDENING_SPRINT.md` | Device matrix definition, Chargebee gates, orphan analysis |
| `RELEASE_SIGNING_CHECK.md` | Signing setup, certificates, human actions |
| `AAB_RELEASE_REPORT.md` | Bundle evidence: size, signature, installability, permissions |
| `PRODUCTION_ENDPOINT_AUDIT.md` | Every localhost/staging hit + the `API_BASE_URL` decision |
| `DEVICE_QA_RESULTS.md` | T1–T10 matrix, what passed, what is blocked and why |
| `CHARGEBEE_BETA_STATUS.md` | Gate state, census, the rollout sequence |
| `CHARGEBEE_PRICE_VARIANTS_MAPPING.md` | The 45-row runbook — needed the moment variants unlock |
| `CHARGEBEE_VARIANT_PRICING_SUPPORT_REQUEST.md` | What to send Chargebee support |
| `ORPHAN_SCHEDULE_REMEDIATION.md` | Option A recommendation + sequencing |
| `DEPLOYMENT_RUNBOOK.md`, `CHANGELOG.md` | Operations and release history |
| `DOC_INVENTORY.md`, `SCREENSHOT_INDEX.md`, `CONFIG_CLEANUP_REPORT.md`, `COMMIT_READINESS.md`, `GITHUB_PUSH_REPORT.md` | This consolidation's index documents |

`docs/**` (38 files: API, architecture ADRs, BRD, functional spec, test registry, guides) is untouched — it is the living project documentation, not migration history.

## ARCHIVE — moved to `_docs/archive/` (29 files)

Historical migration records. Kept, not deleted, per instruction.

| Group | Files |
| :--- | :--- |
| Auth migration | `AUTH_SIMPLIFICATION_PLAN.md`, `AUTH_SIMPLIFICATION_IMPLEMENTATION_PLAN.md` |
| Stitch / visual migration | `STITCH_ALIGNMENT_REPORT.md`, `STITCH_IMPLEMENTATION_STATUS.md`, `STITCH_V2_UI_MIGRATION.md`, `VISUAL_ALIGNMENT_AUDIT.md`, `VISUAL_REVIEW.md`, `PRODUCT_ALIGNMENT_REPORT.md`, `BMJ_UX_REHAUL_PLAN.md` |
| Chargebee investigation | `CHARGEBEE_EXECUTION_PLAN.md`, `CHARGEBEE_FINAL_PRICE_MATRIX.md`, `CHARGEBEE_GO_LIVE_RECOMMENDATION.md`, `CHARGEBEE_IMPORT_ROOT_CAUSE.md`, `CHARGEBEE_PRICE_CREATION_PLAN.md`, `CHARGEBEE_CANARY_EXECUTION.md`, `CHARGEBEE_ONE_TIME_PRICE_MODELLING_DECISION.md`, `chargebee_final_state.md` (was `docs/`) |
| Catalog census | `CATALOG_PRICE_MATRIX.md`, `CATALOG_PRICE_LOADING_VERDICT.md`, `CATALOG_LEGACY_ITEM_REPORT.md` |
| Superseded launch/quality reports | `BMJ_LAUNCH_CHECKLIST.md` (superseded by the RC checklist), `PRODUCTION_READINESS_REPORT.md`, `B5_SMOKE_TEST_PLAN.md`, `B6_DECISION_REPORT.md`, `E2E_BLACK_BOX_TEST_REPORT.md` |
| Cleanup history | `ARCHIVE_LIST.md`, `CLEANUP_CANDIDATES.md`, `CLEANUP_PHASE_1.md`, `SAFE_DELETE_LIST.md` |

## DELETE — removed (disposable, no archival value)

| Removed | Count | Why |
| :--- | ---: | :--- |
| `hs_err_pid*.log`, `replay_pid*.log` | 8 | JVM crash dumps (~2.3 MB) from Gradle/JDK failures |
| `_chargebee_init.bat`, `_chargebee_tools.bat`, `_chargebee_tools_payload.json` | 3 | one-off MCP bootstrap scripts |
| `chargebee_mcp_generated_catalog.json` | 1 | 0-byte artifact |
| `_captures/shots/` | 37 images + text dumps | old probe screenshots and widget-tree dumps |
| `_captures/__pycache__/` | 2 | bytecode |
| `_captures/_*.json` | 8 | one-off API probe responses (`_signin.json`, `_cb_spec_out.json` 146 KB, …) |
| `_captures/mcp_call.py` | 1 | contained a **hardcoded Chargebee MCP key**; superseded by the key-less rollout scripts |
| `_captures/measure_*.py`, `classify_commits.py`, `write_commit_strategy.py`, `*.txt` | 5 | one-off generators already consumed |
| `_captures/lush_before`, `_captures/lush_after` | 1,060 files / **648 MB** | throwaway worktree copies; regenerable exactly per `_captures/README.md` |
| `lush/build_*.err` | 4 | build noise (now also gitignored) |

The `lush_before` git worktree was removed properly (`git worktree remove`), so `git worktree list` is clean again.

## Verification

| Check | Result |
| :--- | :--- |
| Root markdown files | 12 (was 40) |
| Archived | 29 in `_docs/archive/` |
| Duplicate migration reports in root | 0 |
| `_captures` size | **648 MB → ~17 MB** |
| Registered worktrees | 1 (`X:/BMJ/lush`) |
