# BookMyJuice - Unified Signup Flow Use Cases

**Document Version:** 1.0  
**Last Updated:** 2026-03-29  
**Author:** Development Team

---

## Table of Contents

1. [Overview](#overview)
2. [Actors](#actors)
3. [Use Case Diagram](#use-case-diagram)
4. [Use Cases](#use-cases)
5. [Activity Flows](#activity-flows)
6. [Exception Handling](#exception-handling)

---

## Overview

The Unified Signup Flow provides three entry points for new users to create accounts:
- **Email-First:** Start with email verification
- **Phone-First:** Start with phone verification  
- **Google:** Use Google account (email pre-verified)

All flows converge to collect:
- Verified email address
- Verified phone number
- Complete delivery address
- Secure password

---

## Actors

### Primary Actors

| Actor | Description |
|-------|-------------|
| **New User** | First-time user creating an account |
| **Returning User** | Existing user logging in |
| **Google User** | User signing up with Google account |

### Secondary Actors

| Actor | Description |
|-------|-------------|
| **Email Service** | Sends verification codes (future: SendGrid, SES) |
| **SMS Service** | Sends OTP via SMS (future: Twilio, MSG91) |
| **Google Auth** | Provides OAuth authentication |
| **bmjServer** | Backend API handling signup logic |
| **Chargebee** | Customer management system |
| **Database** | MySQL storing user data |

---

## Use Case Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     BookMyJuice Signup System                    │
│                                                                  │
│  ┌──────────────┐                                               │
│  │  New User    │                                               │
│  └──────┬───────┘                                               │
│         │                                                        │
│         ├───────────────────────────────────────────┐           │
│         │                                           │           │
│         ▼                                           ▼           │
│  ┌─────────────────┐                     ┌──────────────────┐  │
│  │ Select Signup   │                     │  View Error      │  │
│  │ Method          │                     │  Messages        │  │
│  └────────┬────────┘                     └──────────────────┘  │
│           │                                                     │
│    ┌──────┼──────┐                                             │
│    │      │      │                                             │
│    ▼      ▼      ▼                                             │
│ ┌─────┐ ┌─────┐ ┌──────────┐                                  │
│ │Email│ │Phone│ │  Google  │                                  │
│ │Flow │ │Flow │ │   Flow   │                                  │
│ └──┬──┘ └──┬──┘ └────┬─────┘                                  │
│    │        │         │                                        │
│    │        │         ▼                                        │
│    │        │    ┌──────────┐                                 │
│    │        │    │ Google   │                                 │
│    │        │    │ Auth     │                                 │
│    │        │    └──────────┘                                 │
│    │        │         │                                        │
│    ▼        ▼         ▼                                        │
│ ┌────────────────────────────┐                                │
│ │  Verify Email & Phone      │                                │
│ └─────────────┬──────────────┘                                │
│               │                                                │
│               ▼                                                │
│ ┌────────────────────────────┐                                │
│ │  Enter Address Details     │                                │
│ └─────────────┬──────────────┘                                │
│               │                                                │
│               ▼                                                │
│ ┌────────────────────────────┐                                │
│ │  Create Password           │                                │
│ └─────────────┬──────────────┘                                │
│               │                                                │
│               ▼                                                │
│ ┌────────────────────────────┐                                │
│ │  Account Created           │                                │
│ │  → Chargebee Customer      │                                │
│ │  → Auto Login              │                                │
│ └────────────────────────────┘                                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Use Cases

### UC-AUTH-001: Email-First Signup

**Goal:** Create account starting with email verification

**Scope:** BookMyJuice Authentication System

**Level:** User Goal

**Primary Actor:** New User with email preference

**Stakeholders and Interests:**
- **User:** Wants quick, secure account creation
- **BookMyJuice:** Needs verified contact info for delivery
- **Chargebee:** Requires customer record for billing

**Preconditions:**
- User has valid email address
- User has valid 10-digit phone number
- User is not already registered

**Success Guarantee (Postconditions):**
- User account created
- Email verified
- Phone verified
- Address saved
- User logged in
- Chargebee customer created

**Main Success Scenario:**

1. User opens app and sees login/signup screen
2. User taps "Sign up with Email"
3. System displays email entry screen
4. User enters email address
5. User taps "Continue"
6. System sends 6-digit verification code to email
7. System displays code entry screen
8. User enters 6-digit code
9. User taps "Verify Email"
10. System validates code
11. System displays phone entry screen
12. User enters 10-digit phone number
13. User taps "Send OTP"
14. System sends 6-digit OTP to phone
15. System displays OTP entry screen
16. User enters 6-digit OTP
17. User taps "Verify OTP"
18. System validates OTP
19. System displays address entry screen
20. User enters first name
21. User enters last name
22. User enters flat/house number
23. User enters society/locality
24. User enters sector/area
25. User enters city
26. User enters state
27. User enters ZIP code
28. User enters country code
29. User taps "Continue"
30. System displays password creation screen
31. User enters password
32. User confirms password
33. User taps "Create Account"
34. System validates all data
35. System creates user in database
36. System creates Chargebee customer
37. System generates JWT token
38. System logs user in
39. System navigates to dashboard
40. System displays welcome message

**Extensions (Alternate Flows):**

- **3a. Invalid email format:**
  - 3a1. System shows error: "Please enter a valid email"
  - 3a2. User re-enters email
  - 3a3. Resume at step 5

- **5a. Email already registered:**
  - 5a1. System shows error: "Email is already registered"
  - 5a2. System offers "Login" button
  - 5a3. User can navigate to login or try different email

- **9a. Wrong verification code:**
  - 9a1. System shows error: "Invalid or expired verification code"
  - 9a2. User can retry or resend
  - 9a3. Resume at step 8

- **9b. Code expired (10 minutes):**
  - 9b1. System shows error: "Code expired"
  - 9b2. User taps "Resend Code" (available after 30 seconds)
  - 9b3. System sends new code
  - 9b4. Old code invalidated
  - 9b5. Resume at step 8

- **13a. Invalid phone format:**
  - 13a1. System shows error: "Please enter a valid 10-digit phone number"
  - 13a2. User re-enters phone
  - 13a3. Resume at step 13

- **17a. Wrong OTP:**
  - 17a1. System shows error: "Invalid or expired OTP"
  - 17a2. User can retry or resend
  - 17a3. Resume at step 16

- **29a. Missing required address field:**
  - 29a1. System highlights empty field
  - 29a2. System shows error: "[Field] is required"
  - 29a3. User fills field
  - 29a4. Resume at step 29

- **33a. Password doesn't meet requirements:**
  - 33a1. Password validator shows failed requirements in red
  - 33a2. User cannot submit
  - 33a3. User modifies password
  - 33a4. Resume at step 31

- **33b. Passwords don't match:**
  - 33b1. System shows error: "Passwords do not match"
  - 33b2. User re-enters confirm password
  - 33b3. Resume at step 32

- **35a. Database error:**
  - 35a1. System logs error
  - 35a2. System shows error: "Failed to create account. Please try again."
  - 35a3. User can retry

- **36a. Chargebee customer creation fails:**
  - 36a1. System rolls back user creation
  - 36a2. System shows error: "Failed to create customer record"
  - 36a3. User can retry

**Special Requirements:**
- Email verification code: 6 digits, 10-minute expiry
- Phone OTP: 6 digits, 10-minute expiry
- Resend available after 30 seconds
- Password: 8+ chars, uppercase, lowercase, 2 numbers, special char
- All data transmitted over HTTPS
- Password stored as BCrypt hash

**Technology & Data Variations:**
- Email service: Currently console log (dev), future: SendGrid/SES
- SMS service: Currently console log (dev), future: Twilio/MSG91
- Database: MySQL
- Cache: Redis (future)

---

### UC-AUTH-002: Phone-First Signup

**Goal:** Create account starting with phone verification

**Primary Actor:** New User with phone preference

**Preconditions:**
- User has valid 10-digit phone number
- User has valid email address
- User is not already registered

**Main Success Scenario:**

1. User opens app and sees login/signup screen
2. User taps "Sign up with Phone"
3. System displays phone entry screen
4. User enters 10-digit phone number
5. User taps "Send OTP"
6. System sends 6-digit OTP to phone
7. System displays OTP entry screen
8. User enters 6-digit OTP
9. User taps "Verify OTP"
10. System validates OTP
11. System displays email entry screen
12. User enters email address
13. User taps "Continue"
14. System sends 6-digit verification code to email
15. System displays code entry screen
16. User enters 6-digit code
17. User taps "Verify Email"
18. System validates code
19. System displays address entry screen
20. User enters all address fields (steps 20-29 as in UC-AUTH-001)
21. User enters password and confirms (steps 30-33 as in UC-AUTH-001)
22. System creates account (steps 34-40 as in UC-AUTH-001)

**Extensions:** (Similar to UC-AUTH-001, with phone/email order reversed)

---

### UC-AUTH-003: Google Signup

**Goal:** Create account using Google authentication

**Primary Actor:** New User with Google account

**Preconditions:**
- User has valid Google account
- User has valid 10-digit phone number
- User is not already registered with this email

**Main Success Scenario:**

1. User opens app and sees login/signup screen
2. User taps "Sign up with Google"
3. System opens Google authentication
4. User selects Google account
5. Google returns verified email, name, and picture
6. System displays phone entry screen
7. System shows pre-filled email (read-only)
8. System shows pre-filled first name (editable)
9. System shows pre-filled last name (editable)
10. User enters 10-digit phone number
11. User taps "Send OTP"
12. System sends 6-digit OTP to phone
13. System displays OTP entry screen
14. User enters 6-digit OTP
15. User taps "Verify OTP"
16. System validates OTP
17. System displays address entry screen
18. User enters all address fields
19. User enters password and confirms
20. User taps "Create Account"
21. System creates account with Google email
22. System creates Chargebee customer
23. System generates JWT token
24. System logs user in
25. System navigates to dashboard

**Extensions:**

- **2a. Google auth cancelled:**
  - 2a1. User cancels Google authentication
  - 2a2. System returns to signup method selection
  - 2a3. User can try again or choose different method

- **4a. No Google account on device:**
  - 4a1. User adds Google account
  - 4a2. Resume at step 4

- **10a. Phone already registered:**
  - 10a1. System shows error: "This phone number is already registered"
  - 10a2. System offers "Login" button
  - 10a3. User can login or use different phone

**Special Requirements:**
- Google Sign-In plugin configured
- Email from Google is pre-verified (no email verification needed)
- Phone verification still required
- Name from Google is pre-filled but editable

---

### UC-AUTH-004: Resend Verification Code

**Goal:** Request new verification code when original is lost/expired

**Primary Actor:** User in signup flow

**Preconditions:**
- User has requested verification code
- 30 seconds have elapsed since last code sent

**Main Success Scenario:**

1. User is on verification code entry screen
2. User waits for code (doesn't arrive)
3. User sees "Resend Code" button (enabled after 30 seconds)
4. User taps "Resend Code"
5. System invalidates old code
6. System generates new 6-digit code
7. System sends new code to email/phone
8. System shows success message: "Verification code resent"
9. User enters new code
10. User taps "Verify"
11. System validates new code
12. User proceeds to next step

**Extensions:**

- **4a. User taps resend before 30 seconds:**
  - 4a1. Button is disabled
  - 4a2. Countdown timer shows remaining seconds
  - 4a3. User must wait

- **11a. New code also fails:**
  - 11a1. System shows error
  - 11a2. User can retry or contact support
  - 11a3. After 3 failed attempts, suggest different email/phone

**Special Requirements:**
- Countdown timer: 30 seconds
- Old code must be invalidated
- Maximum 5 resend attempts per email/phone

---

### UC-AUTH-005: Password Creation

**Goal:** Create secure password meeting all requirements

**Primary Actor:** User in signup flow

**Preconditions:**
- User has completed email verification
- User has completed phone verification
- User has entered address details

**Main Success Scenario:**

1. System displays password creation screen
2. System shows password requirements
3. User enters password in first field
4. Password validator shows real-time feedback
5. All requirements turn green as met
6. User enters same password in confirm field
7. User taps "Create Account"
8. System validates password meets all requirements
9. System validates passwords match
10. System proceeds with account creation

**Password Requirements:**
- Minimum 8 characters
- At least 1 uppercase letter (A-Z)
- At least 1 lowercase letter (a-z)
- At least 2 numbers (0-9)
- At least 1 special character (!@#$%^&* etc.)
- No spaces
- No control characters

**Extensions:**

- **7a. Password too short:**
  - 7a1. Validator shows "Minimum 8 characters" in red
  - 7a2. Submit button disabled
  - 7a3. User extends password

- **7b. Missing uppercase:**
  - 7b1. Validator shows requirement in red
  - 7b2. Submit button disabled
  - 7b3. User adds uppercase letter

- **7c. Missing lowercase:**
  - 7c1. Validator shows requirement in red
  - 7c2. Submit button disabled
  - 7c3. User adds lowercase letter

- **7d. Insufficient numbers:**
  - 7d1. Validator shows "At least 2 numbers" in red
  - 7d2. Submit button disabled
  - 7d3. User adds another number

- **7e. Missing special character:**
  - 7e1. Validator shows requirement in red
  - 7e2. Submit button disabled
  - 7e3. User adds special character

- **7f. Password contains space:**
  - 7f1. Validator shows "No spaces allowed" in red
  - 7f2. Submit button disabled
  - 7f3. User removes space

- **8a. Passwords don't match:**
  - 8a1. System shows error: "Passwords do not match"
  - 8a2. User re-enters confirm password
  - 8a3. Resume at step 7

---

## Activity Flows

### Email-First Flow Activity Diagram

```
┌─────────────┐
│   Start     │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ Select Email    │
│ Signup          │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Enter Email     │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Send Email Code │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Verify Code     │───[Invalid]───┐
└──────┬──────────┘               │
       │ [Valid]                   │
       ▼                           ▼
┌─────────────────┐       ┌─────────────────┐
│ Enter Phone     │       │ Show Error      │
└──────┬──────────┘       └─────────────────┘
       │
       ▼
┌─────────────────┐
│ Send OTP        │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Verify OTP      │───[Invalid]───┐
└──────┬──────────┘               │
       │ [Valid]                   │
       ▼                           ▼
┌─────────────────┐       ┌─────────────────┐
│ Enter Address   │       │ Show Error      │
└──────┬──────────┘       └─────────────────┘
       │
       ▼
┌─────────────────┐
│ Create Password │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Create Account  │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Auto Login      │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│    Dashboard    │
└─────────────────┘
```

---

## Exception Handling

### System Exceptions

| Exception | User Message | System Action |
|-----------|--------------|---------------|
| NetworkError | "Network error. Please check your connection." | Retry with exponential backoff |
| DatabaseError | "Failed to create account. Please try again." | Log error, alert admin |
| ChargebeeError | "Failed to create customer record." | Rollback user creation |
| EmailServiceError | "Failed to send verification code." | Log error, retry with fallback |
| SMSServiceError | "Failed to send OTP." | Log error, retry with fallback |
| JWTGenerationError | "Failed to create session." | Log error, manual login required |

### Validation Exceptions

| Validation | User Message | Recovery |
|------------|--------------|----------|
| InvalidEmail | "Please enter a valid email address" | Re-enter email |
| DuplicateEmail | "This email is already registered" | Login or use different email |
| InvalidPhone | "Please enter a valid 10-digit phone number" | Re-enter phone |
| DuplicatePhone | "This phone number is already registered" | Login or use different phone |
| InvalidCode | "Invalid or expired verification code" | Retry or resend |
| InvalidOTP | "Invalid or expired OTP" | Retry or resend |
| WeakPassword | Password validator shows failed requirements | Modify password |
| PasswordMismatch | "Passwords do not match" | Re-enter confirm password |
| MissingAddress | "[Field] is required" | Fill required field |

### Rate Limiting

| Action | Limit | Response |
|--------|-------|----------|
| Send Email Code | 5 per hour per email | "Too many attempts. Try again later." |
| Send OTP | 5 per hour per phone | "Too many attempts. Try again later." |
| Verify Code | 3 attempts per code | "Maximum attempts reached. Please request new code." |
| Verify OTP | 3 attempts per OTP | "Maximum attempts reached. Please request new OTP." |
| Signup Attempts | 3 per hour per IP | "Too many signup attempts. Please try again later." |

---

## Appendix A: Screen Flow Map

```
┌─────────────────────┐
│  Splash Screen      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Login / Signup     │
│  Selection Screen   │
└──────────┬──────────┘
           │
    ┌──────┼──────┬──────────┐
    │      │      │          │
    ▼      ▼      ▼          ▼
┌──────┐ ┌──────┐ ┌────────┐ │
│ Email│ │ Phone│ │ Google │ │
│Signup│ │Signup│ │ Signup │ │
└──┬───┘ └──┬───┘ └───┬────┘ │
   │        │         │      │
   │        │         │      │
   ▼        ▼         ▼      │
   ┌────────────────┐       │
   │ Email Verified │◄──────┘
   └───────┬────────┘
           │
           ▼
   ┌────────────────┐
   │ Phone Verified │
   └───────┬────────┘
           │
           ▼
   ┌────────────────┐
   │ Address Entry  │
   └───────┬────────┘
           │
           ▼
   ┌────────────────┐
   │ Create Password│
   └───────┬────────┘
           │
           ▼
   ┌────────────────┐
   │  Dashboard     │
   └────────────────┘
```

---

## Appendix B: Data Schema

### User Entity

```sql
CREATE TABLE users (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(100) UNIQUE NOT NULL,  -- Email for email-based auth
  email VARCHAR(100) UNIQUE NOT NULL,
  phone VARCHAR(20) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL,  -- BCrypt hash
  first_name VARCHAR(50) NOT NULL,
  last_name VARCHAR(50) NOT NULL,
  address VARCHAR(120) NOT NULL,
  extended_addr VARCHAR(120),
  extended_addr2 VARCHAR(120),
  city VARCHAR(120) NOT NULL,
  state VARCHAR(120) NOT NULL,
  zip VARCHAR(10) NOT NULL,
  country VARCHAR(2) NOT NULL DEFAULT 'IN',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### Verification Code Store (In-Memory)

```java
Map<String, VerificationCodeData> {
  key: "email@example.com" or "9876543210",
  value: {
    code: "123456",
    expiryTime: 1234567890000,  // 10 minutes from creation
    isUsed: false
  }
}
```

---

**Document End**
