# BookMyJuice - Unified Signup Flow Test Cases

**Document Version:** 1.0  
**Last Updated:** 2026-03-29  
**Device:** 25053PC47I  
**Base URL:** http://192.168.1.6:8080

---

## Table of Contents

1. [Test Overview](#test-overview)
2. [Email-First Flow Tests](#email-first-flow-tests)
3. [Phone-First Flow Tests](#phone-first-flow-tests)
4. [Google Signup Tests](#google-signup-tests)
5. [Address Entry Tests](#address-entry-tests)
6. [Password Creation Tests](#password-creation-tests)
7. [API Tests](#api-tests)
8. [Integration Tests](#integration-tests)
9. [Test Execution Status](#test-execution-status)

---

## Test Overview

### Test Environment
- **Physical Device:** 25053PC47I
- **Base URL:** http://192.168.1.6:8080
- **Test Framework:** Flutter Integration Test
- **Test File:** `integration_test/physical_device_template_test.dart`

### Test Data Requirements
- Valid email addresses (new and existing)
- Valid 10-digit phone numbers
- Valid passwords meeting all requirements
- Complete address data

### Test Execution Commands

```bash
# Run all integration tests
flutter test integration_test/physical_device_template_test.dart \
  --dart-define=E2E=true \
  --dart-define=API_BASE_URL=http://192.168.1.6:8080 \
  --dart-define=E2E_USER=test@example.com \
  --dart-define=E2E_PASS=SecurePass123!

# Run specific test by name
flutter test integration_test/physical_device_template_test.dart \
  --dart-define=E2E=true \
  --name "Email-first Signup Flow"
```

---

## Email-First Flow Tests

### TC-AUTH-EF-001: Email-First Successful Signup

| Field | Value |
|-------|-------|
| **Type** | Positive |
| **Priority** | P0 |
| **Status** | Automated |
| **Automated In** | `physical_device_template_test.dart` |

**Preconditions:**
- App is installed and launched
- User is on login/signup screen
- Email `newuser@example.com` is not registered

**Test Steps:**

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Tap "Sign up with Email" | Navigate to email entry screen |
| 2 | Enter email: `newuser@example.com` | Email displayed in field |
| 3 | Tap "Continue" | System sends verification code, navigate to code entry |
| 4 | Enter code: `123456` | Code displayed as 6 dots |
| 5 | Tap "Verify Email" | Email verified, navigate to phone entry |
| 6 | Enter phone: `9999999999` | Phone displayed in field |
| 7 | Tap "Send OTP" | System sends OTP, navigate to OTP entry |
| 8 | Enter OTP: `123456` | OTP displayed as 6 dots |
| 9 | Tap "Verify OTP" | Phone verified, navigate to address entry |
| 10 | Enter First Name: `John` | Name displayed |
| 11 | Enter Last Name: `Doe` | Name displayed |
| 12 | Enter Address: `123 Main St` | Address displayed |
| 13 | Enter Society: `Sunshine Society` | Society displayed |
| 14 | Enter Sector: `Sector 15` | Sector displayed |
| 15 | Enter City: `Mumbai` | City displayed |
| 16 | Enter State: `Maharashtra` | State displayed |
| 17 | Enter ZIP: `400001` | ZIP displayed |
| 18 | Enter Country: `IN` | Country displayed |
| 19 | Tap "Continue" | Navigate to password creation |
| 20 | Enter Password: `SecurePass123!` | Password validator shows all green |
| 21 | Enter Confirm Password: `SecurePass123!` | Confirm password displayed |
| 22 | Tap "Create Account" | Account created, navigate to dashboard |

**Expected Result:**
- Account created successfully
- User logged in automatically
- Dashboard displayed
- Welcome message shown

**Post-Test Cleanup:**
- Delete test account from database (if needed for rerun)

---

### TC-AUTH-EF-002: Email-First Invalid Email Format

| Field | Value |
|-------|-------|
| **Type** | Negative |
| **Priority** | P1 |
| **Status** | Manual |

**Test Steps:**

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Tap "Sign up with Email" | Navigate to email entry |
| 2 | Enter email: `invalid-email` | Email displayed |
| 3 | Tap "Continue" | Error message displayed |

**Expected Result:**
- Error message: "Please enter a valid email"
- User remains on email entry screen

---

### TC-AUTH-EF-003: Email-First Duplicate Email

| Field | Value |
|-------|-------|
| **Type** | Negative |
| **Priority** | P1 |
| **Status** | Manual |

**Preconditions:**
- Email `existing@example.com` is already registered

**Test Steps:**

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Tap "Sign up with Email" | Navigate to email entry |
| 2 | Enter email: `existing@example.com` | Email displayed |
| 3 | Tap "Continue" | Error message displayed |

**Expected Result:**
- Error message: "Email is already registered"
- Option to navigate to login screen

---

### TC-AUTH-EF-004: Email-First Wrong Verification Code

| Field | Value |
|-------|-------|
| **Type** | Negative |
| **Priority** | P1 |
| **Status** | Manual |

**Test Steps:**

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Enter valid email | Email accepted |
| 2 | Tap "Continue" | Code sent, code entry screen |
| 3 | Enter wrong code: `000000` | Code displayed |
| 4 | Tap "Verify Email" | Error message displayed |

**Expected Result:**
- Error message: "Invalid or expired verification code"
- User can retry with correct code

---

### TC-AUTH-EF-005: Email-First Expired Code

| Field | Value |
|-------|-------|
| **Type** | Negative |
| **Priority** | P2 |
| **Status** | Manual |

**Test Steps:**

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Enter valid email | Email accepted |
| 2 | Tap "Continue" | Code sent |
| 3 | Wait 11 minutes | Time elapsed |
| 4 | Enter correct code: `123456` | Code displayed |
| 5 | Tap "Verify Email" | Error message displayed |

**Expected Result:**
- Error message: "Invalid or expired verification code"
- Option to resend code

---

### TC-AUTH-EF-006: Email-First Resend Code

| Field | Value |
|-------|-------|
| **Type** | Positive |
| **Priority** | P2 |
| **Status** | Manual |

**Test Steps:**

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Enter valid email | Email accepted |
| 2 | Tap "Continue" | Code sent |
| 3 | Wait 30 seconds | Countdown completes |
| 4 | Tap "Resend Code" | New code sent, success message |

**Expected Result:**
- Message: "Verification code resent"
- New 6-digit code logged to console (dev mode)
- Old code becomes invalid

---

## Phone-First Flow Tests

### TC-AUTH-PF-001: Phone-First Successful Signup

| Field | Value |
|-------|-------|
| **Type** | Positive |
| **Priority** | P0 |
| **Status** | Automated |

**Test Steps:** (Similar structure to TC-AUTH-EF-001, starting with phone)

**Expected Result:**
- Account created successfully
- User logged in automatically

---

### TC-AUTH-PF-002: Phone-First Invalid Phone Format

| Field | Value |
|-------|-------|
| **Type** | Negative |
| **Priority** | P1 |
| **Status** | Manual |

**Test Steps:**

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Tap "Sign up with Phone" | Navigate to phone entry |
| 2 | Enter phone: `12345` | Phone displayed |
| 3 | Tap "Send OTP" | Error message displayed |

**Expected Result:**
- Error message: "Please enter a valid 10-digit phone number"

---

### TC-AUTH-PF-003: Phone-First Wrong OTP

| Field | Value |
|-------|-------|
| **Type** | Negative |
| **Priority** | P1 |
| **Status** | Manual |

**Test Steps:**

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Enter valid phone | Phone accepted |
| 2 | Tap "Send OTP" | OTP sent |
| 3 | Enter wrong OTP: `000000` | OTP displayed |
| 4 | Tap "Verify OTP" | Error message displayed |

**Expected Result:**
- Error message: "Invalid or expired OTP"

---

## Google Signup Tests

### TC-AUTH-GS-001: Google Signup Successful Flow

| Field | Value |
|-------|-------|
| **Type** | Positive |
| **Priority** | P0 |
| **Status** | Manual |

**Preconditions:**
- Google account available on device

**Test Steps:**

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Tap "Sign up with Google" | Google auth opens |
| 2 | Select Google account | Auth completes |
| 3 | Verify email is pre-filled | Email shown (read-only) |
| 4 | Enter phone: `9876543210` | Phone displayed |
| 5 | Tap "Send OTP" | OTP sent |
| 6 | Enter OTP: `123456` | OTP displayed |
| 7 | Tap "Verify OTP" | Navigate to address entry |
| 8 | Enter complete address | All fields filled |
| 9 | Tap "Continue" | Navigate to password creation |
| 10 | Create password | Account created |

**Expected Result:**
- Account created with Google email
- Phone verified
- Address saved

---

### TC-AUTH-GS-002: Google Signup Cancelled Auth

| Field | Value |
|-------|-------|
| **Type** | Negative |
| **Priority** | P2 |
| **Status** | Manual |

**Test Steps:**

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Tap "Sign up with Google" | Google auth opens |
| 2 | Cancel/Back button | Auth cancelled |

**Expected Result:**
- User returns to signup method selection
- No account created

---

## Address Entry Tests

### TC-AUTH-AE-001: Address Entry All Fields Valid

| Field | Value |
|-------|-------|
| **Type** | Positive |
| **Priority** | P0 |
| **Status** | Manual |

**Test Steps:**

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Enter First Name: `John` | Valid |
| 2 | Enter Last Name: `Doe` | Valid |
| 3 | Enter Address: `123 Main St` | Valid |
| 4 | Enter Society: `Sunshine Society` | Valid |
| 5 | Enter Sector: `Sector 15` | Valid |
| 6 | Enter City: `Mumbai` | Valid |
| 7 | Enter State: `Maharashtra` | Valid |
| 8 | Enter ZIP: `400001` | Valid |
| 9 | Enter Country: `IN` | Valid |
| 10 | Tap "Continue" | Navigate to password creation |

---

### TC-AUTH-AE-002: Address Entry Missing First Name

| Field | Value |
|-------|-------|
| **Type** | Negative |
| **Priority** | P1 |
| **Status** | Manual |

**Test Steps:**

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Leave First Name empty | Field blank |
| 2 | Fill all other fields | Fields filled |
| 3 | Tap "Continue" | Error message displayed |

**Expected Result:**
- Error message: "First name is required"

---

### TC-AUTH-AE-003: Address Entry Invalid ZIP Code

| Field | Value |
|-------|-------|
| **Type** | Negative |
| **Priority** | P1 |
| **Status** | Manual |

**Test Steps:**

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Enter ZIP: `12345` | 5 digits entered |
| 2 | Tap "Continue" | Error message displayed |

**Expected Result:**
- Error message: "Enter valid 6-digit ZIP code"

---

## Password Creation Tests

### TC-AUTH-PC-001: Password Meets All Requirements

| Field | Value |
|-------|-------|
| **Type** | Positive |
| **Priority** | P0 |
| **Status** | Manual |

**Test Steps:**

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Enter Password: `SecurePass123!` | All validator items green |
| 2 | Enter Confirm: `SecurePass123!` | Match confirmed |
| 3 | Tap "Create Account" | Account created |

**Password Requirements Verified:**
- [x] Minimum 8 characters
- [x] At least 1 uppercase letter
- [x] At least 1 lowercase letter
- [x] At least 2 numbers
- [x] At least 1 special character
- [x] No spaces

---

### TC-AUTH-PC-002: Password Too Short

| Field | Value |
|-------|-------|
| **Type** | Negative |
| **Priority** | P1 |
| **Status** | Manual |

**Test Steps:**

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Enter Password: `Pass1!` | Validator shows red for length |
| 2 | Check validator | "Minimum 8 characters" failed |

---

### TC-AUTH-PC-003: Password No Special Character

| Field | Value |
|-------|-------|
| **Type** | Negative |
| **Priority** | P1 |
| **Status** | Manual |

**Test Steps:**

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Enter Password: `SecurePass123` | Validator shows red for special char |
| 2 | Check validator | "Special character" requirement failed |

---

### TC-AUTH-PC-004: Password Mismatch

| Field | Value |
|-------|-------|
| **Type** | Negative |
| **Priority** | P1 |
| **Status** | Manual |

**Test Steps:**

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Enter Password: `SecurePass123!` | Password displayed |
| 2 | Enter Confirm: `SecurePass456!` | Confirm displayed |
| 3 | Tap "Create Account" | Error message displayed |

**Expected Result:**
- Error message: "Passwords do not match"

---

## API Tests

### TC-AUTH-API-001: API Send Email Verification

| Field | Value |
|-------|-------|
| **Type** | Positive |
| **Priority** | P0 |
| **Status** | Automated |

**Request:**
```http
POST /api/auth/send-email-verification
Content-Type: application/json

{
  "email": "test@example.com"
}
```

**Expected Response:**
```json
{
  "message": "Success: Verification code sent to test@example.com"
}
```
**Status Code:** 200 OK

---

### TC-AUTH-API-002: API Verify Email Code

| Field | Value |
|-------|-------|
| **Type** | Positive |
| **Priority** | P0 |
| **Status** | Manual |

**Request:**
```http
POST /api/auth/verify-email-code
Content-Type: application/json

{
  "email": "test@example.com",
  "verificationCode": "123456"
}
```

**Expected Response:**
```json
{
  "message": "Success: Email verified!"
}
```
**Status Code:** 200 OK

---

### TC-AUTH-API-003: API Unified Signup

| Field | Value |
|-------|-------|
| **Type** | Positive |
| **Priority** | P0 |
| **Status** | Manual |

**Request:**
```http
POST /api/auth/unified-signup
Content-Type: application/json

{
  "email": "newuser@example.com",
  "phone": "9876543210",
  "password": "SecurePass123!",
  "firstName": "John",
  "lastName": "Doe",
  "address": "123 Main St",
  "extendedAddr": "Sunshine Society",
  "extendedAddr2": "Sector 15",
  "city": "Mumbai",
  "state": "Maharashtra",
  "zip": "400001",
  "country": "IN"
}
```

**Expected Response:**
```json
{
  "message": "User registered successfully!"
}
```
**Status Code:** 200 OK

---

### TC-AUTH-API-004: API Unified Signup Duplicate Email

| Field | Value |
|-------|-------|
| **Type** | Negative |
| **Priority** | P1 |
| **Status** | Manual |

**Request:** (Same as TC-AUTH-API-003 with existing email)

**Expected Response:**
```json
{
  "message": "Error: Email is already registered!"
}
```
**Status Code:** 400 Bad Request

---

## Integration Tests

### TC-AUTH-INT-001: Complete Email-First Flow with Backend

| Field | Value |
|-------|-------|
| **Type** | Integration |
| **Priority** | P0 |
| **Status** | Automated |

**Automated in:** `physical_device_template_test.dart`

**Test verifies:**
- Frontend UI flow
- Backend API calls
- Database user creation
- Chargebee customer creation
- JWT token generation
- Auto-login after signup

---

### TC-AUTH-INT-002: Complete Phone-First Flow with Backend

| Field | Value |
|-------|-------|
| **Type** | Integration |
| **Priority** | P0 |
| **Status** | Automated |

**Automated in:** `physical_device_template_test.dart`

---

### TC-AUTH-INT-003: Login → Browse → Logout Flow

| Field | Value |
|-------|-------|
| **Type** | Integration |
| **Priority** | P0 |
| **Status** | Automated |

**Automated in:** `physical_device_template_test.dart`

---

## Test Execution Status

### Automated Tests

| Test ID | Test Name | Status | Last Run | Notes |
|---------|-----------|--------|----------|-------|
| TC-AUTH-EF-001 | Email-First Successful | ⏳ Not Run | - | In `physical_device_template_test.dart` |
| TC-AUTH-PF-001 | Phone-First Successful | ⏳ Not Run | - | In `physical_device_template_test.dart` |
| TC-AUTH-INT-003 | Login → Logout | ⏳ Not Run | - | In `physical_device_template_test.dart` |
| TC-AUTH-API-001 | API Send Email Verification | ⏳ Not Run | - | In `physical_device_template_test.dart` |

### Manual Tests Pending

| Test ID | Test Name | Assigned To | Due Date | Status |
|---------|-----------|-------------|----------|--------|
| TC-AUTH-EF-002 | Invalid Email Format | QA Team | 2026-04-01 | ⏳ Pending |
| TC-AUTH-EF-003 | Duplicate Email | QA Team | 2026-04-01 | ⏳ Pending |
| TC-AUTH-EF-004 | Wrong Verification Code | QA Team | 2026-04-01 | ⏳ Pending |
| TC-AUTH-PF-002 | Invalid Phone Format | QA Team | 2026-04-01 | ⏳ Pending |
| TC-AUTH-GS-001 | Google Signup Successful | QA Team | 2026-04-01 | ⏳ Pending |
| TC-AUTH-AE-001 | Address All Valid | QA Team | 2026-04-01 | ⏳ Pending |
| TC-AUTH-PC-001 | Password Valid | QA Team | 2026-04-01 | ⏳ Pending |

---

## Defect Log

| Defect ID | Related Test | Severity | Status | Description |
|-----------|--------------|----------|--------|-------------|
| - | - | - | - | No defects logged yet |

---

## Sign-Off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| QA Lead | | | |
| Development Lead | | | |
| Product Owner | | | |
