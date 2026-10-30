# Production Endpoint Audit

> **Date:** 2026-10-30 · Searched: Flutter (`lib/`, `android/`, `ios/`, `integration_test/`), backend (`bmjServer/src`), scripts and CI configs.
> **Patterns:** `localhost`, `127.0.0.1`, `0.0.0.0`, `10.0.2.2`, `:8080`, `:8099`, `staging`, `dev.`, `ngrok`.

## 1. Verdict

The **Flutter app contains no staging or development hostname** — good. But it has **one release blocker**: when `API_BASE_URL` is not supplied, the app points at `http://localhost:8080`, so a release build with no `--dart-define` can never reach production and will fail every request.

## 2. Flutter app (ships to users)

| File:line | Value | Classification | Action |
| :--- | :--- | :--- | :--- |
| `lib/config/api_config.dart:34` | `http://127.0.0.1:8080` (web fallback) | 🔴 **blocker** | release build must never take this branch |
| `lib/config/api_config.dart:35` | `http://localhost:8080` (default) | 🔴 **blocker** | see §5 |
| `lib/services/firebase_notification_service.dart:154` | `http://10.0.2.2:8080` (default for `API_BASE_URL`) | 🟠 dev default | harmless only if CI always injects the define |
| `android/app/src/debug/AndroidManifest.xml:7` | comment: local QA over HTTP | ✅ dev-only | keep |
| `integration_test/cart_test.dart:4,9` | `http://192.168.1.6:8080` (comment/example) | ✅ docs only | none |
| `integration_test/physical_device_template_test.dart:3,8` | `http://192.168.1.6:8080` (comment/example) | ✅ docs only | none |

**No `staging.`/`dev.`/`test.`/`ngrok` host appears anywhere in `lib/`.** The only staging references in the whole workspace are in CI (§4).

## 3. Backend (`bmjServer`)

| File:line | Value | Classification | Action |
| :--- | :--- | :--- | :--- |
| `application-dev.properties:11` | `jdbc:mysql://${DB_HOSTNAME:localhost}:3306/bmj_db` | ✅ dev profile | none |
| `application-test.properties:8` | `jdbc:mysql://127.0.0.1:3306/bmj_db` | ✅ test profile | none |
| `application-prod.properties:13` | `${DB_HOSTNAME:localhost}`, `useSSL=true`, `allowPublicKeyRetrieval=false` | 🟡 default is localhost but overridable by env; TLS on | require `DB_HOSTNAME` in the prod environment (fail fast) |
| `application.properties:5` | `chargebee.site=${CHARGEBEE_SITE:bookmyjuice-test}` | 🟠 defaults to **TEST** | prod must set `CHARGEBEE_SITE=bookmyjuice` |
| `security/WebSecurityConfig.java:149` | `config.addAllowedOriginPattern("*")` | 🟡 CORS open to any origin (`allowCredentials=false`, so no cookie theft) | restrict to the storefront/known hosts before public launch |
| `application.properties:43` | `spring.mail.username=${MAIL_USERNAME:support@bookmyjuice.co.in}` | ✅ real domain | none |

## 4. Scripts, tooling and CI

| File:line | Value | Classification |
| :--- | :--- | :--- |
| `_captures/stub_server.py`, `chargebee_*.py` | `127.0.0.1:8099` | ✅ local tooling, never shipped |
| `.github/workflows/ci-cd.yml:222` | builds a **debug** APK with `API_BASE_URL=http://localhost:8080` | 🔴 **release pipeline gap** — CI has no release build at all |
| `.github/workflows/ci-cd.yml:241` | `https://staging.bookmyjuice.co.in` | ℹ️ environment map (staging target) |
| `.github/workflows/ci-cd.yml:268` | `https://bookmyjuice.co.in` | ℹ️ production target |
| `.github/workflows/deploy-vps.yml:118` | `http://localhost:8080/api/health` | ✅ server-local health check |
| `.github/workflows/backend-ci.yml:48,58` | `DB_HOSTNAME: localhost`, `REDIS_HOST: localhost` | ✅ CI services |

## 5. The one thing that must be decided before beta

`ApiConfig.baseUrl` has no production default:

```dart
static String get baseUrl {
  if (_envApiBaseUrl.isNotEmpty) return _envApiBaseUrl;
  if (kIsWeb) return 'http://127.0.0.1:8080';
  return 'http://localhost:8080';
}
```

Three options, in order of preference:

| Option | Change | Risk |
| :--- | :--- | :--- |
| **1. CI injects the beta URL** (no code change) | `flutter build appbundle --release --dart-define=API_BASE_URL=https://<beta-api>` | none — but a build without the flag silently points at localhost |
| **2. Fail fast** | default to `''` and assert non-empty in release | build/runtime error if the flag is missed — safest, needs a code change |
| **3. Hardcode the beta host as the default** | `defaultValue` = the beta API | a wrong/rotated host ships in the binary |

**Recommendation:** option 1 now (no code change this sprint) **plus** option 2 as a follow-up ticket, and add a CI assertion that greps the release build for `localhost`.

The AAB built in this sprint used `--dart-define=API_BASE_URL=https://api.bookmyjuice.example` — a **placeholder** that must be replaced with the real beta host before upload.

## 6. Confirmed environment map (from CI)

| Environment | Host |
| :--- | :--- |
| Staging | `https://staging.bookmyjuice.co.in` |
| Production | `https://bookmyjuice.co.in` |
| Chargebee test site | `bookmyjuice-test` (app + server default) |
| Chargebee prod site | `bookmyjuice` (must be set explicitly) |

The two `.co.in` hosts are website deployments; the API prefix (`/api/...`) is served from the same host per `deploy-vps.yml`'s health check. Confirm with the owner before wiring `API_BASE_URL`.
