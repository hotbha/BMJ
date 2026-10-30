# Config Cleanup Report

> **Date:** 2026-10-30 · **Report only — nothing in this document was changed** (except the one deletion noted in §1.4).
> Scan: `localhost`, `127.0.0.1`, `0.0.0.0`, `10.0.2.2`, `:8080`, `:8099`, `staging`, `dev.`, `test_ai_`, `live_ai_`, `AIza…`, `BEGIN PRIVATE KEY` across Flutter, backend, scripts, CI and configs (`.venv`, `node_modules`, `build`, `_docs/archive` excluded).

## 1. Secrets

### 1.1 🔴 Chargebee MCP keys in **tracked** files

| File | Lines | Exposure |
| :--- | :--- | :--- |
| `.clinerules/cline-guardrails.md` | 10, 15, 17 | two `test_ai_…` keys, one per MCP agent |
| `.vscode/mcp.json` | 20, 27 | same two keys |
| `docs/CHARGEBEE_MCP.md` | 15, 16 | same two keys |

Evidence: a regex scan for `test_ai_` matches all three files, and `git ls-files --error-unmatch` confirms all three are **tracked**. These keys are in git history and must be treated as compromised.

**Remediation (requires the owner):** rotate both MCP keys in Chargebee → move them to a local `.env`/secret store → replace the literals with placeholders → `git rm --cached .vscode/mcp.json` (or commit a `${env:CHARGEBEE_MCP_KEY}` version). History rewrite is a separate decision.

### 1.2 🟠 Firebase client keys in tracked files (informational)

`lush/lib/services/firebase_options.dart` (4 `AIza…` keys) and `lush/android/app/google-services.json` are tracked. These are **client identifiers, not secrets** under Firebase's model (protected by bundle-id/package restrictions + security rules). No action required for beta; they are routinely committed in Flutter apps. Flagged so the choice is deliberate.

### 1.3 🟡 Removed in this pass

`_captures/mcp_call.py` contained a hardcoded MCP key and was **deleted** (untracked helper, superseded by `chargebee_price_rollout.py` / `chargebee_catalog_check.py`, which read credentials from the environment).

### 1.4 ✅ Clean

- `.env` and `.env.*` are **not tracked** (only `.env.example` is); verified with `git ls-files`.
- No private keys, no `sk_live`, no PEM blocks anywhere outside third-party plugin symlinks.
- `android/key.properties` and `X:\BMJ\_secrets\bmj-upload.jks` are outside git and matched by `.gitignore` (`*.jks`, `key.properties`).

## 2. Endpoints

| File:line | Value | Class | Note |
| :--- | :--- | :--- | :--- |
| `lush/lib/config/api_config.dart:34-35` | `http://127.0.0.1:8080` (web), `http://localhost:8080` | 🔴 **blocker** | default when `API_BASE_URL` is not defined |
| `lush/lib/services/firebase_notification_service.dart:154` | `http://10.0.2.2:8080` | 🟠 dev default | only used when the flag is missing |
| `lush/android/app/src/debug/AndroidManifest.xml:7-9` | cleartext enabled (debug only) | ✅ intended | release manifest has no cleartext |
| `bmjServer/src/main/resources/application.properties:5` | `${CHARGEBEE_SITE:bookmyjuice-test}` | 🟠 defaults to TEST | prod must set `bookmyjuice` |
| `bmjServer/.../application-prod.properties:13` | `${DB_HOSTNAME:localhost}`, `useSSL=true` | 🟡 | require the env var in prod |
| `bmjServer/.../security/WebSecurityConfig.java:149` | `addAllowedOriginPattern("*")` | 🟡 | open CORS, `allowCredentials=false` |
| `.github/workflows/ci-cd.yml:222` | builds a **debug** APK with `localhost` | 🔴 release-pipeline gap | CI has no release build |
| `.github/workflows/ci-cd.yml:241,268` | `staging.bookmyjuice.co.in`, `bookmyjuice.co.in` | ℹ️ environment map | confirm which is the API host |
| `.github/workflows/deploy-vps.yml:118` | `http://localhost:8080/api/health` | ✅ server-local | |
| `_captures/stub_server.py`, `chargebee_*.py` | `127.0.0.1:8099` | ✅ tooling only | never shipped |

## 3. Dead code / stale switches

| Item | Evidence | Impact |
| :--- | :--- | :--- |
| `ChargebeeConfig` (site names + `apiKey` getter) | zero references in `lib/`, `test/`, `integration_test/` | dead; its hardcoded key default was already removed |
| `keystore_name.jks` (alias `your_alias`) and `clientkeystore` (alias `client`) | both tracked; both open with password `android` | tracked secrets — remove + rotate |
| `signingConfig = debug` fallback in `build.gradle.kts` | intentional contributor fallback, active only when `key.properties` is absent | keep, but CI must fail if it triggers |
| `test/widgets/signup_screen_test.dart` | deleted along with its screen — no dangling references (418 tests pass) | clean |
| Patrol plugin assets in `lush/windows/flutter/ephemeral/` | build symlinks, gitignored | no action |

## 4. Summary

| Severity | Count | Items |
| :--- | ---: | :--- |
| 🔴 Must fix before public release | 3 | MCP keys in tracked files; `API_BASE_URL` default; CI builds debug only |
| 🟠 Should fix before beta | 2 | `CHARGEBEE_SITE` default, `10.0.2.2` default |
| 🟡 Acceptable with a decision | 2 | CORS `*`, prod DB host default |
| ✅ Verified clean | 3 | `.env` untracked, signing material untracked, no PEM/private keys |
