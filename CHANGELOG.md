# Changelog

## [2026-06-09] Password Strength Upgrade: 1 → 2 Numbers (FLAG-010)
- **Scope**: BRD §4.6, USE_CASES.md, FUNCTIONAL_SPEC.md, app_text_field.dart, sign_up_screen.dart,
  google_signup_screen.dart, create_password_screen.dart, TC_AUTH.md
- **Change**: Password requirement changed from "at least 1 number" → "at least 2 numbers"
- **Regex**: Updated from `(?=.*\d)` to `(?=(?:.*\d){2})` in Flutter validators
- **Documents**: BRD regex updated to `(?=(?:.*\d){2})`, USE_CASES.md "2 numbers" confirmed, FUNCTIONAL_SPEC §3.4 line 215 confirmed
- **Backend**: No regex validation exists on backend (uses @Size(min=8, max=40) only). Backend already accepts any 8+ char password, so this is purely a frontend validation change.
- **Test Cases**: TC-AUTH-037 (special char check) and TC-AUTH-054 (buffer overflow) unaffected.
  TC-AUTH-038 updated description to explicitly mention "2 numbers" requirement.
  TC-AUTH-051 (login) unaffected — server validates credentials, not password format.
  TC-AUTH-052 (forgot password) unaffected — queries by email, not password.
- **UI labels**: All Flutter password requirement lists updated: "1 number" → "2 numbers"