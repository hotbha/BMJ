# Task Continuation Prompt — E2E Test Suite + Backend Fixes

## Current State Summary

### ✅ COMPLETED (22/26 items)

**Backend Fixes (Chargebee + Google Sign-In):**
1. ✅ Added `googleId` and `photoUrl` fields to `UnifiedSignupRequest.java`
2. ✅ Modified `unifiedSignup()` in `AuthController.java` to store Google fields on User entity
3. ✅ Modified `googleSignIn()` to create Chargebee customers for returning Google users who lack one
4. ✅ Modified `linkGoogleAccount()` to create Chargebee customers for users who lack one
5. ✅ Compiled Maven build successfully
6. ✅ Deployed new JAR to Docker container + restarted backend (healthy)
7. ✅ Created e2etester user (9000000001) in MySQL via `/api/auth/unified-signup`
8. ✅ Verified login API works: `POST /api/auth/signin` with `username=e2etester@bookmyjuice.com`, `password=E2ETest@1234` returns JWT token (200)

**Appium Testing Infrastructure:**
9. ✅ Fixed `debug_post_login.py` package name from `com.bookmyjuice.lush` to `com.bookmyjuice.app`
10. ✅ Confirmed actual app packages: `com.example.lush` AND `com.bookmyjuice.app` both installed
11. ✅ `adb reverse tcp:8080 tcp:8080` set up (shows as UsbFfs)
12. ✅ API config uses `http://localhost:8080`
13. ✅ All page objects and test suite files exist

### ❌ PENDING (4 items)

**Critical Issue — Login via Appium fails:**
- `debug_post_login.py` successfully navigates to login page, enters credentials, taps "Sign In", but **the app stays on the login page** (button becomes disabled, no error shown, no navigation)
- The API works correctly via curl/Python — `POST /api/auth/signin` with `username` + `password` returns 200 + JWT
- **Root cause likely**: The app on the device (`com.bookmyjuice.app`) was **last updated at 2026-05-30 16:50:53** — it may have been built with an old API URL. The app needs to be REBUILT and REINSTALLED with `--dart-define=API_BASE_URL=http://localhost:8080` and the backend Docker was ALSO rebuilt with new JAR at the same time.

### Key Technical Details

| Item | Value |
|------|-------|
| Backend container | `bmj-backend` — healthy, port 8080 |
| MySQL container | `bmj-mysql` — healthy, port 3307 |
| Redis container | `bmj-redis` — healthy, port 6379 |
| App package (device) | `com.bookmyjuice.app` (MainActivity) |
| Test user email | `e2etester@bookmyjuice.com` |
| Test user phone | `9000000001` |
| Test user password | `E2ETest@1234` |
| API signin endpoint | `POST /api/auth/signin` with `{"username":"...", "password":"..."}` |
| adb reverse | `tcp:8080 tcp:8080` active |
| Python venv | `X:\BMJ\.venv\Scripts\python` |
| Appium | Running on `http://127.0.0.1:4723` |

### Pending Steps (in priority order)

1. **Rebuild & reinstall Flutter app** with `--dart-define=API_BASE_URL=http://localhost:8080` and `--release` flag:
   ```
   cd X:\BMJ\lush && flutter build apk --release --dart-define=API_BASE_URL=http://localhost:8080
   ```
   Then install via `adb install -r build/app/outputs/flutter-apk/app-release.apk`

2. **Re-run debug_post_login.py** to verify Appium login flow works end-to-end

3. **Run all auth tests** (13/13 passing):
   ```
   .venv\Scripts\python -m pytest appium_test/tests/suite_1_auth/ -v
   ```

4. **Run all remaining test suites** (address, catalog, cart, checkout, subscription, notifications, profile, navigation, edge cases)

5. **Update E2E_BUG_TRACKER.md** with any bugs found

### Relevant Files

| File | Description |
|------|-------------|
| `appium_test/debug_post_login.py` | Login flow debug script (package fixed to `com.bookmyjuice.app`) |
| `appium_test/conftest.py` | Test fixtures with `logged_in()` fixture |
| `appium_test/pages/login_page.py` | Login page object (EditText[0]=email, EditText[1]=password) |
| `appium_test/config/device_config.json` | Appium device config (appPackage: `com.bookmyjuice.app`) |
| `appium_test/tests/suite_1_auth/test_auth.py` | 13 auth tests |
| `bmjServer/src/.../AuthController.java` | Modified with Chargebee customer creation for Google flows |
| `bmjServer/src/.../UnifiedSignupRequest.java` | Added googleId/photoUrl fields |
| `lush/lib/config/api_config.dart` | API base URL: `localhost:8080` (physical device issue) |
| `lush/lib/UserRepository/user_repository.dart` | Login sends `{'username': ..., 'password': ...}` |
| `appium_test/.env` | `TEST_EMAIL`, `TEST_PASSWORD`, `TEST_PHONE` |
| `bmjServer/target/` | Compiled JAR already deployed to Docker |

### Script to resume work

When resuming, first check if backend is healthy:
```
docker ps | findstr bmj-backend
curl.exe http://localhost:8080/actuator/health
```

Check if Appium is running:
```
curl.exe http://127.0.0.1:4723/status
```

Verify test user login:
```
python -c "import requests; r=requests.post('http://localhost:8080/api/auth/signin', json={'username':'e2etester@bookmyjuice.com','password':'E2ETest@1234'}); print(r.status_code, r.text[:100])"
```

Then rebuild Flutter app and proceed with the pending items above.