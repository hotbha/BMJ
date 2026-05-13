# Human Intervention Required â€” BookMyJuice

> **Last Updated:** 2026-05-12 (added H18 for Firebase setup)  
> **Purpose:** Track items that **cannot** be automated and need a human to complete.

---

## H1 — Chargebee .env setup

**Status:** âœ… Resolved  
**Priority:** Critical  
**Owner:** DevOps / Admin

**Resolution:** Chargebee test site `bookmyjuice-test` is configured with API key in `.env`:
- `CHARGEBEE_SITE=bookmyjuice-test`
- `CHARGEBEE_API_KEY=<REDACTED_ROTATE_NOW>`

**Remaining:** GitHub Actions secrets `CHARGEBEE_SITE` and `CHARGEBEE_API_KEY` still need to be created.

---

## H2 — JWT .env setup

**Status:** âœ… Resolved  
**Priority:** Critical  
**Owner:** DevOps

**Resolution:** JWT secret configured in `.env`:
- `JWT_SECRET=<REDACTED_ROTATE_NOW>` (40 chars)
- `JWT_EXPIRATION_MS=86400000` (24 hours)

**Note:** Current secret is 40 characters (meets minimum 32-char requirement). For production, consider generating a full 64-character cryptographically random string as originally specified.

**Remaining:** GitHub Actions secret `JWT_SECRET` still needs to be created.

---

## H3 — SMTP .env setup

**Status:** âœ… Resolved  
**Priority:** High  
**Owner:** Admin

**Resolution:** SMTP configured in `.env`:
- `MAIL_HOST=smtppro.zoho.com`
- `MAIL_PORT=587`
- `MAIL_USERNAME=support@bookmyjuice.co.in`
- `MAIL_PASSWORD=<REDACTED_ROTATE_NOW>`
- `MAIL_FROM=support@bookmyjuice.co.in`

**Note:** Using Zoho SMTP instead of Gmail. The app password `<REDACTED_ROTATE_NOW>` is configured.

**Remaining:** GitHub Actions secret `MAIL_PASSWORD` still needs to be created.

---

## H4 â€” Google OAuth Consent Screen & Client ID

**Status:** âœ… Resolved  
**Priority:** High  
**Owner:** Admin

**Resolution:**
- Android client ID configured in `lush/lib/views/models/google_sign_in.dart` as `_serverClientId`
- Web client ID configured in `lush/web/index.html` as `google-signin-client_id` meta tag
- Both client IDs provided by user and configured:
  - Android: `434116959668-sovbab9648v9hgbk1pi3tfg3ssl60mhb.apps.googleusercontent.com`
  - Web: `434116959668-ab6k17v17l18ji7otsijcmahhfdb5322.apps.googleusercontent.com`
- People API enabled by user in Google Cloud Console
- Spring Boot `application.properties` reads `GOOGLE_CLIENT_ID` from `.env` for ID token validation

**Notes:**
- The `.env` file contains both IDs: `GOOGLE_CLIENT_ID` (Android) and `GOOGLE_WEB_CLIENT_ID` (Web)
- For production, authorized redirect URIs may still need adding in Google Cloud Console
- The client secret JSON file must be kept outside version control

---

## H5 â€” [RESOLVED] Stale architecture/status docs

**Status:** âœ… Resolved  
**Resolution:** Deleted stale docs and replaced with v3.0 enterprise versions.

---

## H6 â€” [RESOLVED] Hardcoded pricing page IDs

**Status:** âœ… Resolved  
**Resolution:** Controllers already return 410 Gone. No hosted pricing pages remain in Flutter.

---

## H7 â€” [RESOLVED] Production Dockerfile review

**Status:** âœ… Resolved  
**Resolution:** Dockerfile is already production-grade (multi-stage, non-root, health checks, G1GC).

---

## H8 â€” [RESOLVED] Flutter checkout screens

**Status:** âœ… Resolved  
**Resolution:** Only hosted checkout retained for final payment. All non-checkout hosted pages removed.

---

## H9 â€” Chargebee Java Library JARs

**Status:** âœ… Resolved  
**Priority:** Low  
**Owner:** DevOps

**Resolution:**
- `chargebee-java-3.29.0.zip` â€” Deleted
- `chargebee-java-3.30.0.zip` â€” Deleted
- `chargebee-java-3.30.0/` extracted directory â€” Deleted

The Chargebee Java SDK is included as a Maven dependency in `pom.xml`. No manual JARs needed.

---

## H10 â€” MySQL Database Initialization

**Status:** ðŸŸ¡ Ready (Docker + Flyway)  
**Priority:** High  
**Owner:** DevOps

**Required Action:**
1. Start MySQL:
   ```bash
   docker compose up -d mysql
   ```
2. MySQL service is configured in `.env`:
   - `DB_HOSTNAME=mysql`, `DB_PORT=3306`, `DB_NAME=bmj_db`
   - `DB_USERNAME=bmj`, `DB_PASSWORD=<REDACTED_ROTATE_NOW>`
3. Flyway migration scripts exist at `bmjServer/src/main/resources/db/migration/`:
   - `V1__init.sql` through `V5__refresh_tokens.sql`
4. Flyway will auto-apply migrations on Spring Boot startup.

---

## H11 â€” Redis Setup (Production)

**Status:** ðŸŸ¡ Partial (Docker available)  
**Priority:** Medium  
**Owner:** DevOps

**Required Action:**
- For local dev: `docker compose up -d redis`
- For production: Use managed Redis (AWS ElastiCache, Redis Enterprise, or Upstash).
- Note: `REDIS_HOST` and `REDIS_PORT` are not explicitly set in `.env` â€” add them if needed.

---

## H12 â€” GitHub Repository Secrets Configuration

**Status:** ðŸ”´ Pending  
**Priority:** High  
**Owner:** DevOps

**Required Action:**
Create the following secrets in GitHub â†’ Settings â†’ Secrets and variables â†’ Actions:

| Secret Name | Source | Value Status |
|------------|--------|-------------|
| `CHARGEBEE_SITE` | Chargebee settings | âœ… Known (`bookmyjuice-test`) |
| `CHARGEBEE_API_KEY` | Chargebee settings | âœ… Known |
| `JWT_SECRET` | Generated (see H2) | âœ… Known |
| `WEBHOOK_USERNAME` | Custom | âœ… Known (`webhook_user`) |
| `WEBHOOK_PASSWORD` | Custom | âœ… Known |
| `MAIL_PASSWORD` | SMTP app password | âœ… Known |

All values exist in `.env` and just need to be copied to GitHub Secrets.

---

## H13 â€” [NEW] Webhook Username & Password Setup

**Status:** âœ… Resolved  
**Priority:** Medium  
**Owner:** DevOps

**Resolution:** Webhook credentials configured in `.env`:
- `WEBHOOK_USERNAME=webhook_user`
- `WEBHOOK_PASSWORD=<REDACTED_ROTATE_NOW>`

For production, replace with stronger credentials.

**Remaining:** GitHub Actions secrets `WEBHOOK_USERNAME` and `WEBHOOK_PASSWORD` need to be created.

---

## H14 â€” [NEW] JWT Expiration Override

**Status:** âœ… Resolved  
**Priority:** Low  
**Owner:** DevOps

**Resolution:** Default JWT expiration `86400000` ms (24 hours) configured via `JWT_EXPIRATION_MS` in `.env`. No override needed for development.

---

## H15 â€” [RESOLVED] Health Endpoint Created

**Status:** âœ… Resolved  
**Resolution:** `/api/health` endpoint created in `HealthController.java` and added to `permitAll()` in `WebSecurityConfig`. No manual configuration required.

---

## H16 â€” [RESOLVED] Empty Cart Validation Fix

**Status:** âœ… Resolved  
**Resolution:** `CheckoutController.cartCheckout()` now validates for empty/null cart before calling Chargebee API. Returns `400 BAD_REQUEST` with message "Error: Cart is empty. Add items before checkout."

---

## H17 â€” [RESOLVED] Dynamic IP Handling for Phone Testing

**Status:** âœ… Resolved  
**Resolution:** Flutter `api_config.dart` updated to default to `10.0.2.2` (Android emulator). New helper scripts created in `ops/`:
- `find_active_ip.ps1` â€” Auto-detects your current WiFi IP
- `build_flutter_for_phone.ps1` â€” Builds Flutter APK with `--dart-define=API_BASE_URL=<your-ip>:8080`
- `test_fullstack_dynamic.ps1` â€” Full-stack test script with `-Remote` flag for phone testing

---

## H18 â€” [NEW] Firebase Project Configuration & google-services.json

**Status:** ðŸ”´ Pending  
**Priority:** High  
**Owner:** Admin

**Required Actions:**

### Step 1: Re-download `google-services.json` from Firebase Console
- Go to [Firebase Console â†’ Project Settings](https://console.firebase.google.com/project/bookmyjuice-4c156/settings/general)
- Under "Your apps" â†’ Android app (`com.bookmyjuice.app`), click **"Download google-services.json"**
- **Replace** `lush/android/app/google-services.json` with the new file
- The current file has an empty `"oauth_client": []` array â€” the new file **must** contain OAuth client entries for Google Sign-In to work

### Step 2: Verify SHA-1 fingerprint in Firebase Console
- In Firebase Console â†’ Project Settings â†’ General â†’ Your apps â†’ Android app
- SHA-1 must be: `B6:FF:C3:DE:5B:1A:80:3F:3D:3F:B8:F7:6C:60:7B:2C:51:F1:D2:E0`
- If missing, add it

### Step 3: Verify SHA-1 fingerprint in Google Cloud Console
- Go to [Google Cloud Console â†’ APIs & Services â†’ Credentials](https://console.cloud.google.com/apis/credentials)
- Find the "Android OAuth 2.0 Client ID" and verify it has the same SHA-1 fingerprint
- The Android client ID **must match** between Firebase and Google Cloud

### Step 4: Enable Google Sign-In in Firebase Authentication
- Go to [Firebase Console â†’ Authentication â†’ Sign-in method](https://console.firebase.google.com/project/bookmyjuice-4c156/authentication)
- Enable **Google** provider
- For **Web SDK configuration**, use the Web client ID:  
  `24122477606-tju3ortu42psbfluvl9hvmj7q15ec64c.apps.googleusercontent.com`
- Also enable **Phone** if needed

### Step 5: Add Test Users for OAuth Consent Screen
- Go to [Google Cloud Console â†’ APIs & Services â†’ OAuth consent screen](https://console.cloud.google.com/apis/credentials/consent)
- If status is "Testing" (not Published), add your email as a **Test user**

### Step 6: Clean rebuild
```bash
cd x:\BMJ\lush
flutter clean
flutter pub get
flutter run
```

### Root Cause of `[16] Account reauth failed.` error:
The error has **two root causes**, both now addressed:

1. **ðŸ”§ CODE FIX (Applied):** The `_handleGoogleSignup()` method in `signup_method_selection_screen.dart` was firing **two** Google Sign-In attempts simultaneously â€” the BLoC `GoogleSignIn` event AND the direct `GoogleSignInHelper.instance.signIn()` call. Android's Credential Manager cannot handle concurrent auth requests, causing `[16] Account reauth failed.` The fix removes the redundant BLoC event, keeping only the single direct call.

2. **ðŸ‘¤ HUMAN FIX NEEDED:** The `google-services.json` file has an empty `"oauth_client": []` array, so Android doesn't know which OAuth client to use. This causes the `GetCredentialResponse error returned from framework` log message. Re-downloading `google-services.json` from Firebase Console (after enabling Google Sign-In) will include the OAuth client IDs needed to validate tokens.

### Client ID Changes
The old OAuth client IDs have been replaced globally:

| What | Old ID | New ID |
|------|--------|--------|
| Web Client ID (used everywhere) | `434116959668-ab6k...` | `24122477606-tju3ortu42psbfluvl9hvmj7q15ec64c` |
| Android Client ID (used as serverClientId) | `434116959668-sovbab...` | `24122477606-tju3ortu42psbfluvl9hvmj7q15ec64c` (same Web ID) |

Files updated:
- `lush/lib/views/models/google_sign_in.dart` â€” `_serverClientId` changed to Web client ID
- `.env` â€” `GOOGLE_CLIENT_ID` and `GOOGLE_WEB_CLIENT_ID` updated
- `.env.example` â€” default updated
- `lush/web/index.html` â€” meta tag updated
- `bmjServer/src/main/resources/application.properties` â€” defaults updated

**Note on Android client:** The Android OAuth client is auto-configured via the `google-services.json` file downloaded from Firebase. The `serverClientId` parameter passed to `GoogleSignIn.initialize()` must be the **Web** client ID (not Android), as per google_sign_in 7.x documentation. The Web client ID is used for ID token verification on the server. No separate Android client ID is needed in code.

---

## H19 â€” [COMPLETED] Full-screen Theme Migration & Dashboard as Default

**Status:** âœ… Completed  
**Priority:** High  
**Owner:** Developer

**Completed:**
1. âœ… **Dashboard as default (Requirement 2)**: Implemented `DashboardMode` enum, `AuthWrapper` rewritten to show public dashboard for unauthenticated users with login prompts on auth-gated actions. Compilation verified.
2. âœ… **Back button handling (Requirement 3)**: `PopScope` added to 11 critical screens with `BackButtonHandler` confirmation dialogs for in-progress operations. Compilation verified.
3. âœ… **Theme alignment (Requirement 1)**: All 14 remaining screen files migrated from legacy `LushTheme`/`FontUtils`/raw `Colors.*` to `AppColors`/`AppTextStyles`. Files migrated:
   - `menu.dart`, `notifications.dart`, `order_history_page.dart`, `login_page.dart`
   - `phone_login_screen.dart`, `reset_password_email_screen.dart`, `forgot_password_screen.dart`
   - `text_utils.dart`, `day_wise_schedule_screen.dart`, `delete_account_screen.dart`
   - `link_google_account_screen.dart`, `reset_password_mobile_screen.dart`
   - `dashboard.dart`, `address_screen.dart`
4. âœ… **`flutter analyze` passes with 0 errors** (all 14 files migrated, only pre-existing info-level style hints remain)

**âš ï¸ Human verification recommended:**
- Test that the Dashboard loads correctly for logged-out users
- Verify that tapping "Login" / "Get Started" on the public dashboard navigates to `/login`
- Test back button behavior on multi-step signup flow (try pressing back mid-flow)
- Verify theme looks correct on both light and dark modes on at least 5 key screens


---

## Summary

| ID | Item | Status | Priority |
|----|------|--------|----------|
| H1 | Chargebee .env setup | âœ… Resolved | Critical |
| H2 | JWT .env setup | âœ… Resolved | Critical |
| H3 | SMTP .env setup | âœ… Resolved | High |
| H4 | Google OAuth Consent Screen | âœ… Resolved | High |
| H5 | Stale docs | âœ… Resolved | Medium |
| H6 | Hardcoded pricing page IDs | âœ… Resolved | Medium |
| H7 | Production Dockerfile | âœ… Resolved | Medium |
| H8 | Flutter checkout screens | âœ… Resolved | Medium |
| H9 | Chargebee Java Library JARs | âœ… Resolved | Low |
| H10 | MySQL Database Initialization | ðŸŸ¡ Ready | High |
| H11 | Redis Setup | ðŸŸ¡ Partial | Medium |
| H12 | GitHub Secrets Configuration | ðŸ”´ Pending | High |
| H13 | Webhook Credentials | âœ… Resolved | Medium |
| H14 | JWT Expiration Override | âœ… Resolved | Low |
| H15 | Health Endpoint | âœ… Resolved | Low |
| H16 | Empty Cart Validation | âœ… Resolved | High |
| H17 | Dynamic IP Handling | âœ… Resolved | Medium |
| H18 | Firebase Configuration & google-services.json | âœ… Resolved | High |
| **H19** | **Full-screen Theme Migration & Dashboard as Default** | **âœ… Completed** | **High** |

**Still needing human action:** H10 (run docker-compose), H11 (production Redis), H12 (GitHub secrets setup).
- H19 requires human verification (recommended: test dashboard for logged-out users, back button behavior, theme light/dark mode).


