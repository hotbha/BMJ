# BookMyJuice API Documentation

> Comprehensive API documentation for the BookMyJuice backend services.

## Table of Contents

- [Overview](#overview)
- [Authentication](#authentication)
- [API Endpoints](#api-endpoints)
- [Error Handling](#error-handling)
- [Timeout & Retry Behavior](#timeout--retry-behavior)
- [Rate Limiting](#rate-limiting)
- [Webhooks](#webhooks)
- [Bottle Tracking](#bottle-tracking)
- [SDKs & Examples](#sdks--examples)

---

## Overview

**Base URL:**
- Development: `http://localhost:8080`
- Staging: `https://staging-api.bookmyjuice.co.in`
- Production: `https://api.bookmyjuice.co.in`

**API Version:** All endpoints use the `/api/v1/` prefix (e.g., `/api/v1/auth/signin`). Some older endpoints at `/api/` root (e.g., `/api/auth/signin`) are kept for backward compatibility — prefer the versioned path.

**Content Type:** `application/json`

**Price Units:**
- All prices are stored and transmitted in **paise** (Indian paise / cents) from Chargebee APIs.
- The app divides by 100 for display purposes (e.g., `9900` paise → `₹99`).
- The backend never calculates prices locally; Chargebee is the sole pricing authority.

**Timestamp Format:** All timestamps are in ISO 8601 UTC (`yyyy-MM-dd'T'HH:mm:ss'Z'`). Mobile converts to local timezone for display.

---

## Authentication

### JWT Token Authentication

Most endpoints require authentication using JWT tokens.

**Header Format:**
```
Authorization: Bearer <access_token>
```

### Token Lifecycle

| Token Type | Expiry | Refresh |
|------------|--------|---------|
| Access Token | 30 days (2592000000 ms) | POST /api/auth/refresh — silent refresh with stored credentials |

### Authentication Flow

```
1. User Login
   POST /api/v1/auth/signin   (canonical)
   ↓
2. Receive Token
   { accessToken, tokenType, id, username, email, roles }
   ↓
3. Store JWT in FlutterSecureStorage
   Key: bmj_jwt
   ↓
4. Use Access Token for API calls
   Authorization: Bearer <accessToken>
   ↓
5. On app launch (AutoLogin):
   a. Read JWT from FlutterSecureStorage
   b. If valid → navigate to Dashboard
   c. If expired → POST /api/auth/refresh with stored credentials
   d. If refresh fails → show public Dashboard (guest mode) with toast
   ↓
6. When Access Token expires (30 days)
   Silent refresh via POST /api/auth/refresh
```

> **Note:** Refresh endpoint POST /api/auth/refresh exists. On expiry, the app silently attempts refresh with stored credentials. If refresh fails, the user sees public Dashboard (guest mode) with a toast message. The token version is tracked server-side for invalidation support (e.g., on password reset). Token storage MUST use FlutterSecureStorage — not SharedPreferences.

---

## API Endpoints

### Authentication

> **Canonical Auth Endpoint:** `/api/v1/auth/signin`
> Legacy: `/api/auth/signin` kept for backward compatibility.

#### POST /api/v1/auth/signin (canonical) | /api/auth/signin (legacy)

Sign in with email or phone and password.

**Request:**
```json
{
  "username": "user@example.com",
  "password": "SecurePass123!"
}
```
Note: `username` field accepts either email address or 10-digit phone number.

**Response (200 OK):**
```json
{
  "accessToken": "eyJhbGciOiJIUzI1NiIs...",
  "tokenType": "Bearer",
  "id": 500,
  "username": "9999999901",
  "email": "user@example.com",
  "roles": ["ROLE_USER"]
}
```

**Error Responses:**
```json
// 400 Bad Request - Invalid credentials
{
  "status": 400,
  "message": "Error: Invalid username or password!",
  "errorCode": "AUTH_001",
  "timestamp": "2026-03-27T10:30:00Z",
  "path": "/api/v1/auth/signin"
}

// 400 Bad Request - Missing fields
{
  "status": 400,
  "message": "Validation error",
  "errors": [
    { "field": "username", "message": "Username is required" },
    { "field": "password", "message": "Password is required" }
  ],
  "errorCode": "VAL_001",
  "timestamp": "2026-03-27T10:30:00Z",
  "path": "/api/v1/auth/signin"
}

// 429 Too Many Requests - Rate limit exceeded
{
  "status": 429,
  "message": "Rate limit exceeded. Please wait before retrying.",
  "errorCode": "RATE_LIMIT_EXCEEDED",
  "retryAfter": 60,
  "timestamp": "2026-03-27T10:30:00Z",
  "path": "/api/v1/auth/signin"
}
```

---

#### POST /api/v1/auth/refresh

Silently refresh an expired JWT token. Called by the app's AutoLogin flow when the stored JWT's `exp` claim is past-current time. Does NOT require a valid token — uses stored credentials.

**Request:**
```json
{
  "username": "9999999901",
  "password": "SecurePass123!"
}
```

Note: The `username` field is the **10-digit phone number** (stored as `username` in the DB during signup). The `password` is the user's stored password (saved in SharedPreferences/FlutterSecureStorage — only if the user chose "Remember Me" or equivalent on login).

**Response (200 OK):**
```json
{
  "accessToken": "eyJhbGciOiJIUzI1NiIs...",
  "tokenType": "Bearer",
  "id": 500,
  "username": "9999999901",
  "email": "user@example.com",
  "roles": ["ROLE_USER"]
}
```

**Error Responses:**
```json
// 401 Unauthorized - Invalid credentials (password changed, user deleted)
{
  "status": 401,
  "message": "Invalid credentials — token refresh failed",
  "errorCode": "AUTH_002",
  "timestamp": "2026-03-27T10:30:00Z",
  "path": "/api/auth/refresh"
}

// 401 Unauthorized - Token revoked (password reset invalidated token)
{
  "status": 401,
  "message": "Token has been revoked. Please sign in again.",
  "errorCode": "AUTH_003",
  "timestamp": "2026-03-27T10:30:00Z",
  "path": "/api/auth/refresh"
}
```

**Client Behavior on Refresh Failure:**
1. Clear stored JWT from FlutterSecureStorage
2. Clear stored credentials (password) if any
3. Navigate to Dashboard in **public mode** (no login screen forced)
4. Show toast: "Session expired. Please sign in again."

---

#### POST /api/v1/auth/signup

Register a new user account.

**Request:**
```json
{
  "name": "John Doe",
  "email": "user@example.com",
  "phone": "9876543210",
  "password": "SecurePass123!",
  "address": {
    "street": "123 Main St",
    "city": "Bangalore",
    "state": "Karnataka",
    "pincode": "560001",
    "country": "India"
  }
}
```

**Response (200 OK):**
```json
{
  "message": "User registered successfully",
  "userId": "usr_123"
}
```

**Error Responses:**
```json
// 400 Bad Request - Email already exists
{
  "status": 400,
  "message": "Email is already registered",
  "errorCode": "USER_002",
  "timestamp": "2026-03-27T10:30:00Z",
  "path": "/api/v1/auth/signup"
}

// 400 Bad Request - Validation errors
{
  "status": 400,
  "message": "Validation error",
  "errors": [
    { "field": "phone", "message": "Phone must be a valid 10-digit Indian number" },
    { "field": "password", "message": "Password must be at least 8 characters with uppercase, lowercase, number, and special character" }
  ],
  "errorCode": "VAL_001",
  "timestamp": "2026-03-27T10:30:00Z",
  "path": "/api/v1/auth/signup"
}

// 500 Internal Server Error - Chargebee failure
{
  "status": 500,
  "message": "Failed to create customer in billing system",
  "errorCode": "SYS_001",
  "timestamp": "2026-03-27T10:30:00Z",
  "path": "/api/v1/auth/signup"
}
```

---

#### POST /api/v1/auth/google

Sign in with Google.

**Request:**
```json
{
  "googleIdToken": "eyJhbGciOiJIUzI1NiIs...",
  "deviceInfo": {
    "platform": "android",
    "deviceId": "device_123"
  }
}
```

**Response (200 OK):**
```json
{
  "accessToken": "eyJhbGciOiJIUzI1NiIs...",
  "tokenType": "Bearer",
  "id": 500,
  "username": "9999999901",
  "email": "user@example.com",
  "roles": ["ROLE_USER"],
  "isNewUser": false
}
```

**Error Responses:**
```json
// 400 Bad Request - Invalid Google token
{
  "status": 400,
  "message": "Invalid Google ID token",
  "errorCode": "AUTH_001",
  "timestamp": "2026-03-27T10:30:00Z",
  "path": "/api/v1/auth/google"
}

// 400 Bad Request - Google email not verified
{
  "status": 400,
  "message": "Google account email is not verified",
  "errorCode": "AUTH_001",
  "timestamp": "2026-03-27T10:30:00Z",
  "path": "/api/v1/auth/google"
}

// 503 Service Unavailable - Google token verification failed (network)
{
  "status": 503,
  "message": "Unable to verify Google token. Please try again.",
  "errorCode": "SYS_001",
  "timestamp": "2026-03-27T10:30:00Z",
  "path": "/api/v1/auth/google"
}
```

---

#### POST /api/v1/auth/otp/request

Request OTP for phone authentication.

**Request:**
```json
{
  "phone": "9876543210"
}
```

**Response (200 OK):**
```json
{
  "message": "OTP sent successfully",
  "otpReference": "otp_ref_123",
  "expiresIn": 300
}
```

**Error Responses:**
```json
// 400 Bad Request - Invalid phone
{
  "status": 400,
  "message": "Invalid phone number format",
  "errors": [
    { "field": "phone", "message": "Phone must be a valid 10-digit Indian number starting with 6, 7, 8, or 9" }
  ],
  "errorCode": "VAL_001",
  "timestamp": "2026-03-27T10:30:00Z",
  "path": "/api/v1/auth/otp/request"
}

// 429 Too Many Requests - OTP limit exceeded
{
  "status": 429,
  "message": "Too many OTP requests. Please try again after 5 minutes.",
  "errorCode": "RATE_LIMIT_EXCEEDED",
  "retryAfter": 300,
  "timestamp": "2026-03-27T10:30:00Z",
  "path": "/api/v1/auth/otp/request"
}
```

---

#### POST /api/v1/auth/otp/verify

Verify OTP and authenticate.

**Request:**
```json
{
  "phone": "9876543210",
  "otp": "123456",
  "otpReference": "otp_ref_123"
}
```

**Response (200 OK):**
```json
{
  "accessToken": "eyJhbGciOiJIUzI1NiIs...",
  "tokenType": "Bearer",
  "id": 500,
  "username": "9999999901",
  "email": "user@example.com",
  "roles": ["ROLE_USER"]
}
```

**Error Responses:**
```json
// 400 Bad Request - Wrong OTP
{
  "status": 400,
  "message": "Invalid OTP",
  "errorCode": "AUTH_001",
  "timestamp": "2026-03-27T10:30:00Z",
  "path": "/api/v1/auth/otp/verify"
}

// 400 Bad Request - Expired OTP
{
  "status": 400,
  "message": "OTP has expired. Please request a new one.",
  "errorCode": "AUTH_001",
  "timestamp": "2026-03-27T10:30:00Z",
  "path": "/api/v1/auth/otp/verify"
}

// 404 Not Found - No OTP request found for this phone
{
  "status": 404,
  "message": "No OTP request found for this phone number",
  "errorCode": "USER_001",
  "timestamp": "2026-03-27T10:30:00Z",
  "path": "/api/v1/auth/otp/verify"
}
```

---

### User Management

#### GET /api/v1/user/profile

Get current user profile.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": "usr_123",
  "email": "user@example.com",
  "name": "John Doe",
  "phone": "9876543210",
  "addresses": [
    {
      "id": "addr_1",
      "type": "home",
      "isDefault": true,
      "street": "123 Main St",
      "city": "Bangalore",
      "state": "Karnataka",
      "pincode": "560001",
      "country": "India"
    }
  ],
  "subscriptions": {
    "active": 1,
    "paused": 0
  },
  "createdAt": "2026-01-15T10:00:00Z"
}
```

**Error Responses:**
```json
// 401 Unauthorized - Missing/invalid token
{
  "status": 401,
  "message": "Authentication required",
  "errorCode": "AUTH_002",
  "timestamp": "2026-03-27T10:30:00Z",
  "path": "/api/v1/user/profile"
}

// 404 Not Found - User not found
{
  "status": 404,
  "message": "User not found",
  "errorCode": "USER_001",
  "timestamp": "2026-03-27T10:30:00Z",
  "path": "/api/v1/user/profile"
}
```

---

#### PUT /api/v1/user/profile

Update user profile.

**Request:**
```json
{
  "name": "John Updated",
  "phone": "9876543211"
}
```

**Response (200 OK):**
```json
{
  "message": "Profile updated successfully",
  "user": { ... }
}
```

**Error Responses:**
```json
// 400 Bad Request - Invalid phone
{
  "status": 400,
  "message": "Validation error",
  "errors": [
    { "field": "phone", "message": "Phone must be a valid 10-digit Indian number" }
  ],
  "errorCode": "VAL_001",
  "timestamp": "2026-03-27T10:30:00Z",
  "path": "/api/v1/user/profile"
}

// 403 Forbidden - Insufficient permissions
{
  "status": 403,
  "message": "Access denied",
  "errorCode": "AUTH_003",
  "timestamp": "2026-03-27T10:30:00Z",
  "path": "/api/v1/user/profile"
}
```

---

### Address Management

> **Canonical Address Endpoint:** `/api/v1/address`
> Legacy: `/api/v1/user/addresses` kept for backward compatibility.

#### GET /api/v1/address

Get all saved addresses for the authenticated user.

**Response (200 OK):**
```json
{
  "status": "success",
  "count": 1,
  "data": [
    {
      "id": 1,
      "label": "Home",
      "fullName": "John Doe",
      "phone": "9876543210",
      "addressLine1": "123 Main St",
      "addressLine2": "Apartment 4B",
      "landmark": "Near City Park",
      "city": "Bangalore",
      "state": "Karnataka",
      "pincode": "560001",
      "isDefault": true,
      "latitude": null,
      "longitude": null,
      "deliveryInstructions": "Leave at door"
    }
  ]
}
```

**Error Responses:**
```json
// 200 OK with empty data (no addresses saved)
{
  "status": "success",
  "count": 0,
  "data": []
}

// 401 Unauthorized
{
  "status": 401,
  "message": "Authentication required",
  "errorCode": "AUTH_002",
  "timestamp": "2026-03-27T10:30:00Z",
  "path": "/api/v1/address"
}
```

---

#### POST /api/v1/address

Add a new delivery address.

**Request:**
```json
{
  "label": "Work",
  "fullName": "John Doe",
  "phone": "9876543210",
  "addressLine1": "456 Tech Park",
  "addressLine2": "Floor 3",
  "landmark": "Near Metro Station",
  "city": "Bangalore",
  "state": "Karnataka",
  "pincode": "560100",
  "latitude": null,
  "longitude": null,
  "deliveryInstructions": "Reception desk",
  "default": true
}
```

**Response (201 Created):**
```json
{
  "status": "success",
  "message": "Address added successfully",
  "data": {
    "id": 2,
    "label": "Work",
    ...
  }
}
```

**Error Responses:**
```json
// 400 Bad Request - Missing required fields
{
  "status": 400,
  "message": "Validation error",
  "errors": [
    { "field": "pincode", "message": "Pincode is required and must be 6 digits" },
    { "field": "city", "message": "City is required" }
  ],
  "errorCode": "VAL_001",
  "timestamp": "2026-03-27T10:30:00Z",
  "path": "/api/v1/address"
}
```

---

#### PUT /api/v1/address/{id}

Update an existing address.

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Address updated successfully",
  "data": { ... }
}
```

**Error Responses:**
```json
// 404 Not Found - Address does not exist or belongs to another user
{
  "status": 404,
  "message": "Address not found",
  "errorCode": "VAL_001",
  "timestamp": "2026-03-27T10:30:00Z",
  "path": "/api/v1/address/999"
}
```

---

#### DELETE /api/v1/address/{id}

Delete an address.

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Address deleted successfully"
}
```

**Error Responses:**
```json
// 404 Not Found
{
  "status": 404,
  "message": "Address not found",
  "errorCode": "VAL_001",
  "timestamp": "2026-03-27T10:30:00Z",
  "path": "/api/v1/address/999"
}
```

---

#### PATCH /api/v1/address/{id}/default

Set an address as the default delivery address.

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Default address updated successfully"
}
```

---

### Subscription Management

#### GET /api/subscriptions/my

Get all subscriptions for the authenticated user.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "subscriptions": [
    {
      "id": "sub_123",
      "planId": "plan_30_30",
      "planName": "30:30 Plan",
      "status": "active",
      "startDate": "2026-03-01T00:00:00Z",
      "currentPeriodStart": "2026-03-27T00:00:00Z",
      "currentPeriodEnd": "2026-04-26T23:59:59Z",
      "nextBillingDate": "2026-04-27T00:00:00Z",
      "amount": 2999,
      "currency": "INR"
    }
  ]
}
```

**Error Responses:**
```json
// 401 Unauthorized
{
  "status": 401,
  "message": "Authentication required",
  "errorCode": "AUTH_002",
  "timestamp": "2026-03-27T10:30:00Z",
  "path": "/api/subscriptions/my"
}

// 200 OK - No subscriptions
{
  "subscriptions": []
}
```

**Notes:** Token is read internally by the service via `SecureStorageService`; the caller does not pass it explicitly.

---

#### GET /api/v1/subscriptions/plans

Get available subscription plans.

**Response (200 OK):**
```json
{
  "plans": [
    {
      "id": "plan_delight_200_weekly",
      "name": "Delight 200ml Weekly",
      "description": "6 bottles of our Delight range every week",
      "price": 59900,
      "currency": "INR",
      "billingPeriod": "weekly",
      "juiceCount": 6,
      "duration": 7,
      "features": [
        "6 bottles per week",
        "Choose from Delight juices",
        "Flexible scheduling",
        "Free delivery"
      ]
    },
    {
      "id": "plan_delight_200_monthly",
      "name": "Delight 200ml Monthly",
      "description": "24 bottles of our Delight range every month",
      "price": 199900,
      "currency": "INR",
      "billingPeriod": "monthly",
      "juiceCount": 24,
      "duration": 30,
      "features": [
        "24 bottles per month",
        "Choose from Delight juices",
        "Flexible scheduling",
        "Free delivery"
      ]
    }
  ]
}
```

> **Note:** The plans shown above are examples. Actual plan IDs and names follow the convention `plan_{category}_{size}_{frequency}` (e.g., `plan_delight_200_weekly`, `plan_signature_300_monthly`). There are 18 plans total: 3 categories (Delight, Signature, Premium) × 3 sizes (200ml, 300ml, 500ml) × 2 frequencies (weekly, monthly).

---

#### GET /api/v1/subscriptions/checkout-url

Get Chargebee hosted page URL for subscription.

**Query Parameters:**
- `planId` (required): Plan identifier

**Response (200 OK):**
```json
{
  "url": "https://bookmyjuice-test.chargebee.com/hosted_pages/new_subscription?...",
  "expiresAt": "2026-03-27T11:30:00Z"
}
```

**Error Responses:**
```json
// 400 Bad Request - Missing planId
{
  "status": 400,
  "message": "Plan ID is required",
  "errorCode": "VAL_001",
  "timestamp": "2026-03-27T10:30:00Z",
  "path": "/api/v1/subscriptions/checkout-url"
}

// 404 Not Found - Invalid planId
{
  "status": 404,
  "message": "Subscription plan not found",
  "errorCode": "SUB_001",
  "timestamp": "2026-03-27T10:30:00Z",
  "path": "/api/v1/subscriptions/checkout-url"
}
```

---

#### GET /api/v1/subscriptions/active

Get active subscription details.

**Response (200 OK):**
```json
{
  "subscription": {
    "id": "sub_123",
    "planId": "plan_delight_200_weekly",
    "planName": "Delight 200ml Weekly",
    "status": "active",
    "startDate": "2026-03-01T00:00:00Z",
    "currentPeriodStart": "2026-03-27T00:00:00Z",
    "currentPeriodEnd": "2026-04-26T23:59:59Z",
    "nextBillingDate": "2026-04-27T00:00:00Z",
    "amount": 59900,
    "currency": "INR",
    "autoRenew": true,
    "pausedAt": null,
    "cancelledAt": null
  }
}
```

**Error Responses:**
```json
// 200 OK - No active subscription
{
  "subscription": null
}

// 401 Unauthorized
{
  "status": 401,
  "message": "Authentication required",
  "errorCode": "AUTH_002",
  "timestamp": "2026-03-27T10:30:00Z",
  "path": "/api/v1/subscriptions/active"
}
```

---

#### POST /api/v1/subscriptions/{id}/pause

Pause active subscription.

**Path Parameters:**
- `id`: Subscription ID

**Request:**
```json
{
  "reason": "Going on vacation",
  "pauseUntil": "2026-04-15T00:00:00Z"
}
```

**Response (200 OK):**
```json
{
  "message": "Subscription paused successfully",
  "resumesAt": "2026-04-15T00:00:00Z"
}
```

**Error Responses:**
```json
// 400 Bad Request - After 9 PM IST cutoff
{
  "status": 400,
  "message": "Subscription pause is not available after 9 PM IST. Please try again tomorrow.",
  "errorCode": "SUB_002",
  "timestamp": "2026-03-27T20:30:00Z",
  "path": "/api/v1/subscriptions/sub_123/pause"
}

// 400 Bad Request - Already paused
{
  "status": 400,
  "message": "Subscription is already paused",
  "errorCode": "SUB_003",
  "timestamp": "2026-03-27T10:30:00Z",
  "path": "/api/v1/subscriptions/sub_123/pause"
}

// 404 Not Found - Subscription not found
{
  "status": 404,
  "message": "Subscription not found",
  "errorCode": "SUB_001",
  "timestamp": "2026-03-27T10:30:00Z",
  "path": "/api/v1/subscriptions/sub_999/pause"
}
```

---

#### POST /api/v1/subscriptions/{id}/resume

Resume paused subscription.

**Response (200 OK):**
```json
{
  "message": "Subscription resumed successfully",
  "nextDeliveryDate": "2026-04-16T00:00:00Z"
}
```

**Error Responses:**
```json
// 400 Bad Request - After 9 PM IST cutoff
{
  "status": 400,
  "message": "Subscription resume is not available after 9 PM IST. Please try again tomorrow.",
  "errorCode": "SUB_002",
  "timestamp": "2026-03-27T20:30:00Z",
  "path": "/api/v1/subscriptions/sub_123/resume"
}

// 400 Bad Request - Not paused
{
  "status": 400,
  "message": "Subscription is not currently paused",
  "errorCode": "SUB_003",
  "timestamp": "2026-03-27T10:30:00Z",
  "path": "/api/v1/subscriptions/sub_123/resume"
}
```

---

#### POST /api/v1/subscriptions/{id}/cancel

Cancel subscription.

**Request:**
```json
{
  "reason": "Too expensive",
  "cancelAtPeriodEnd": true
}
```

**Response (200 OK):**
```json
{
  "message": "Subscription cancelled successfully",
  "accessUntil": "2026-04-26T23:59:59Z"
}
```

**Error Responses:**
```json
// 400 Bad Request - After 9 PM IST cutoff
{
  "status": 400,
  "message": "Subscription cancellation is not available after 9 PM IST. Please try again tomorrow.",
  "errorCode": "SUB_002",
  "timestamp": "2026-03-27T20:30:00Z",
  "path": "/api/v1/subscriptions/sub_123/cancel"
}

// 400 Bad Request - Already cancelled
{
  "status": 400,
  "message": "Subscription is already cancelled",
  "errorCode": "SUB_003",
  "timestamp": "2026-03-27T10:30:00Z",
  "path": "/api/v1/subscriptions/sub_123/cancel"
}
```

---

### Order Management

#### GET /api/v1/orders

Get order history with pagination.

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 20)
- `status` (optional): Filter by status
- `sortBy` (optional): Sort field (`date`, `amount`) — default: `date`
- `sortOrder` (optional): `asc` or `desc` — default: `desc`

**Response (200 OK):**
```json
{
  "orders": [
    {
      "id": "ord_123",
      "orderNumber": "BMJ-2026-001234",
      "status": "delivered",
      "type": "one-time",
      "items": [
        {
          "productId": "prod_orange",
          "name": "Fresh Orange Juice",
          "quantity": 1,
          "size": "200ml",
          "price": 120
        }
      ],
      "subtotal": 120,
      "tax": 21.6,
      "discount": 0,
      "total": 141.6,
      "currency": "INR",
      "deliveryAddress": { ... },
      "createdAt": "2026-03-26T08:00:00Z",
      "deliveredAt": "2026-03-26T10:30:00Z"
    }
  ],
  "pagination": {
    "currentPage": 1,
    "totalPages": 5,
    "totalItems": 50,
    "itemsPerPage": 20
  }
}
```

**Error Responses:**
```json
// 200 OK - No orders
{
  "orders": [],
  "pagination": {
    "currentPage": 1,
    "totalPages": 0,
    "totalItems": 0,
    "itemsPerPage": 20
  }
}

// 401 Unauthorized
{
  "status": 401,
  "message": "Authentication required",
  "errorCode": "AUTH_002",
  "timestamp": "2026-03-27T10:30:00Z",
  "path": "/api/v1/orders"
}
```

> **Note:** `deliveryFee` is not returned by the API. Delivery fee is sourced from Chargebee pricing data.

---

#### GET /api/v1/orders/{id}

Get order details.

**Response (200 OK):**
```json
{
  "id": "ord_123",
  "orderNumber": "BMJ-2026-001234",
  "status": "delivered",
  "statusHistory": [
    {
      "status": "pending",
      "timestamp": "2026-03-26T08:00:00Z"
    },
    {
      "status": "confirmed",
      "timestamp": "2026-03-26T08:15:00Z"
    },
    {
      "status": "preparing",
      "timestamp": "2026-03-26T08:30:00Z"
    },
    {
      "status": "out_for_delivery",
      "timestamp": "2026-03-26T09:30:00Z"
    },
    {
      "status": "delivered",
      "timestamp": "2026-03-26T10:30:00Z"
    }
  ],
  "items": [ ... ],
  "payment": {
    "method": "card",
    "status": "paid",
    "transactionId": "txn_123"
  },
  "delivery": {
    "address": { ... },
    "scheduledTime": "2026-03-26T10:00:00Z - 11:00:00Z",
    "actualTime": "2026-03-26T10:30:00Z"
  }
}
```

**Error Responses:**
```json
// 404 Not Found
{
  "status": 404,
  "message": "Order not found",
  "errorCode": "ORD_001",
  "timestamp": "2026-03-27T10:30:00Z",
  "path": "/api/v1/orders/ord_999"
}
```

---

### Cart Management

#### GET /api/v1/cart

Get current user's cart.

**Response (200 OK):**
```json
{
  "items": [
    {
      "productId": "prod_orange",
      "name": "Fresh Orange Juice",
      "quantity": 2,
      "size": "200ml",
      "price": 120,
      "imageUrl": "https://..."
    },
    {
      "productId": "prod_apple",
      "name": "Apple Beet Carrot",
      "quantity": 1,
      "size": "300ml",
      "price": 150,
      "imageUrl": "https://..."
    }
  ],
  "summary": {
    "itemCount": 3,
    "subtotal": 390,
    "tax": 70.2,
    "discount": 0,
    "total": 460.2,
    "currency": "INR"
  }
}
```

**Error Responses:**
```json
// 200 OK - Empty cart
{
  "items": [],
  "summary": {
    "itemCount": 0,
    "subtotal": 0,
    "tax": 0,
    "discount": 0,
    "total": 0,
    "currency": "INR"
  }
}

// 401 Unauthorized
{
  "status": 401,
  "message": "Authentication required",
  "errorCode": "AUTH_002",
  "timestamp": "2026-03-27T10:30:00Z",
  "path": "/api/v1/cart"
}
```

> **Note:** `deliveryFee` is NOT included in cart response. Delivery fee is managed entirely through Chargebee pricing.

---

#### POST /api/v1/cart/items

Add item to cart.

**Request:**
```json
{
  "productId": "prod_orange",
  "quantity": 2,
  "priceId": "price_200ml"
}
```

**Response (200 OK):**
```json
{
  "message": "Item added to cart",
  "cart": { ... }
}
```

**Error Responses:**
```json
// 409 Conflict - Mixed cart types (one-time + subscription)
{
  "status": 409,
  "message": "Cart type conflict. Your cart contains one-time items. Please clear cart before adding subscription items.",
  "errorCode": "CART_TYPE_CONFLICT",
  "timestamp": "2026-03-27T10:30:00Z",
  "path": "/api/v1/cart/items"
}

// 400 Bad Request - Missing productId
{
  "status": 400,
  "message": "Validation error",
  "errors": [
    { "field": "productId", "message": "Product ID is required" }
  ],
  "errorCode": "VAL_001",
  "timestamp": "2026-03-27T10:30:00Z",
  "path": "/api/v1/cart/items"
}
```

---

#### PUT /api/v1/cart/items/{productId}

Update item quantity.

**Request:**
```json
{
  "quantity": 3
}
```

**Response (200 OK):**
```json
{
  "message": "Cart updated",
  "cart": { ... }
}
```

**Error Responses:**
```json
// 400 Bad Request - Quantity must be positive
{
  "status": 400,
  "message": "Validation error",
  "errors": [
    { "field": "quantity", "message": "Quantity must be at least 1" }
  ],
  "errorCode": "VAL_001",
  "timestamp": "2026-03-27T10:30:00Z",
  "path": "/api/v1/cart/items/prod_orange"
}

// 404 Not Found - Item not in cart
{
  "status": 404,
  "message": "Item not found in cart",
  "errorCode": "ORD_001",
  "timestamp": "2026-03-27T10:30:00Z",
  "path": "/api/v1/cart/items/prod_unknown"
}
```

---

#### DELETE /api/v1/cart/items/{productId}

Remove item from cart.

**Response (200 OK):**
```json
{
  "message": "Item removed from cart",
  "cart": { ... }
}
```

---

#### POST /api/v1/cart/merge

Merge guest cart items into user's cart on login. Handles conflict resolution for mixed cart types (one-time vs. subscription).

**Request:**
```json
{
  "items": [
    {
      "productId": "prod_orange",
      "quantity": 2,
      "priceId": "price_200ml",
      "itemType": "charge"
    }
  ]
}
```

**Response (200 OK):**
```json
{
  "message": "Cart merged successfully",
  "cart": { ... }
}
```

**Error Responses:**
```json
// 409 Conflict - Mixed cart types detected
{
  "status": 409,
  "message": "Cart merge conflict: guest cart contains different item type than server cart. Please clear one cart first.",
  "errorCode": "CART_TYPE_CONFLICT",
  "timestamp": "2026-03-27T10:30:00Z",
  "path": "/api/v1/cart/merge"
}
```

---

### Checkout

> **Canonical Checkout Endpoint:** `POST /api/v2/checkout`
> Per FUNCTIONAL_SPEC, cart-based checkout creates a Chargebee Hosted Page URL for payment.

#### POST /api/v2/checkout

Initiate one-time checkout from authenticated user's cart. Returns a Chargebee Hosted Page URL for payment processing.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Checkout session created successfully",
  "data": {
    "url": "https://bookmyjuice-test.chargebee.com/hosted_pages/checkout?...",
    "orderId": "ord_temp_123",
    "expiresAt": "2026-03-27T11:30:00Z"
  }
}
```

**Error Responses:**
```json
// 400 Bad Request - Cart empty
{
  "status": 400,
  "message": "Cart is empty. Add items before checkout.",
  "errorCode": "ORD_002",
  "timestamp": "2026-03-27T10:30:00Z",
  "path": "/api/v2/checkout"
}

// 400 Bad Request - Mixed cart types
{
  "status": 400,
  "message": "Cart contains mixed item types. Please clear cart and try again.",
  "errorCode": "CART_TYPE_CONFLICT",
  "timestamp": "2026-03-27T10:30:00Z",
  "path": "/api/v2/checkout"
}

// 400 Bad Request - No Chargebee customer ID
{
  "status": 400,
  "message": "Billing account not set up. Please contact support.",
  "errorCode": "PAY_002",
  "timestamp": "2026-03-27T10:30:00Z",
  "path": "/api/v2/checkout"
}

// 401 Unauthorized
{
  "status": 401,
  "message": "Authentication required",
  "errorCode": "AUTH_002",
  "timestamp": "2026-03-27T10:30:00Z",
  "path": "/api/v2/checkout"
}
```

---

#### POST /api/v2/checkout/with-items

Create a one-time checkout with specific items without using the cart system.

**Request:**
```json
{
  "items": [
    { "price_id": "charge_xxx", "quantity": 2 },
    { "price_id": "charge_yyy", "quantity": 1 }
  ]
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Checkout session created successfully",
  "data": {
    "url": "https://bookmyjuice-test.chargebee.com/hosted_pages/checkout?...",
    "orderId": "ord_temp_123",
    "expiresAt": "2026-03-27T11:30:00Z"
  }
}
```

**Error Responses:**
```json
// 400 Bad Request - Invalid items
{
  "status": 400,
  "message": "One or more items are invalid or unavailable",
  "errors": [
    { "field": "items[0].price_id", "message": "Invalid price ID: charge_xxx" }
  ],
  "errorCode": "VAL_001",
  "timestamp": "2026-03-27T10:30:00Z",
  "path": "/api/v2/checkout/with-items"
}
```

---

### Products

#### GET /api/v1/products

Get all available products (sourced from Chargebee).

**Query Parameters:**
- `category` (optional): Filter by category (`delight`, `signature`, `premium`)
- `search` (optional): Search query
- `sortBy` (optional): `popularity`, `price_low_high`, `price_high_low`
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 20, max: 100)

**Response (200 OK):**
```json
{
  "products": [
    {
      "id": "prod_orange",
      "name": "Fresh Orange Juice",
      "description": "100% fresh oranges, cold-pressed",
      "category": "delight",
      "images": [
        "https://...",
        "https://..."
      ],
      "nutritionalInfo": {
        "calories": 112,
        "protein": 1.7,
        "carbs": 25.8,
        "sugar": 20.8,
        "fiber": 0.5,
        "fat": 0.5,
        "unit": "per 200ml"
      },
      "prices": [
        {
          "id": "price_200ml",
          "size": "200ml",
          "price": 120,
          "currency": "INR"
        },
        {
          "id": "price_500ml",
          "size": "500ml",
          "price": 200,
          "currency": "INR"
        }
      ],
      "availability": {
        "inStock": true,
        "quantity": 50
      },
      "rating": {
        "average": 4.5,
        "count": 128
      }
    }
  ],
  "pagination": {
    "currentPage": 1,
    "totalPages": 3,
    "totalItems": 50,
    "itemsPerPage": 20
  }
}
```

**Error Responses:**
```json
// 200 OK - Empty results (no products match filter)
{
  "products": [],
  "pagination": {
    "currentPage": 1,
    "totalPages": 0,
    "totalItems": 0,
    "itemsPerPage": 20
  }
}

// 400 Bad Request - Invalid category
{
  "status": 400,
  "message": "Validation error",
  "errors": [
    { "field": "category", "message": "Invalid category. Must be one of: delight, signature, premium" }
  ],
  "errorCode": "VAL_001",
  "timestamp": "2026-03-27T10:30:00Z",
  "path": "/api/v1/products"
}
```

> **Note:** Product IDs are sourced from Chargebee and are not hardcoded. The products endpoint serves as a cache of Chargebee item data synced to the local database.

---

#### GET /api/v1/products/{id}

Get product details.

**Response (200 OK):**
```json
{
  "id": "prod_orange",
  "name": "Fresh Orange Juice",
  "description": "100% fresh oranges, cold-pressed",
  "longDescription": "Our signature orange juice is made from hand-picked Nagpur oranges, cold-pressed to retain maximum nutrients...",
  "category": "delight",
  "tags": ["fresh", "vitamin-c", "popular"],
  "images": [ ... ],
  "nutritionalInfo": { ... },
  "prices": [ ... ],
  "availability": { ... },
  "rating": { ... },
  "reviews": [
    {
      "userId": "usr_456",
      "userName": "Jane D.",
      "rating": 5,
      "comment": "Best orange juice I've ever had!",
      "date": "2026-03-20T00:00:00Z"
    }
  ]
}
```

**Error Responses:**
```json
// 404 Not Found
{
  "status": 404,
  "message": "Product not found",
  "errorCode": "ORD_001",
  "timestamp": "2026-03-27T10:30:00Z",
  "path": "/api/v1/products/prod_unknown"
}
```

---

### Health Check

#### GET /api/health

Check API health status.

**Response (200 OK):**
```json
{
  "status": "UP",
  "timestamp": "2026-03-27T10:30:00Z",
  "version": "1.0.0",
  "database": "UP",
  "chargebee": "UP",
  "redis": "UP"
}
```

**Response (503 Service Unavailable):**
```json
{
  "status": "DOWN",
  "timestamp": "2026-03-27T10:30:00Z",
  "version": "1.0.0",
  "database": "UP",
  "chargebee": "DOWN",
  "redis": "UP"
}
```

---

### Serviceability

#### GET /api/v1/serviceability

Check if delivery is available for a given pincode.

**Query Parameters:**
- `pincode` (required): 6-digit pincode

**Response (200 OK):**
```json
{
  "serviceable": true,
  "message": "Delivery available in your area"
}
```

**Error Responses:**
```json
// 200 OK - Not serviceable
{
  "serviceable": false,
  "message": "Sorry, we do not deliver to this pincode yet"
}

// 400 Bad Request - Invalid pincode
{
  "status": 400,
  "message": "Pincode must be a 6-digit number",
  "errorCode": "VAL_001",
  "timestamp": "2026-03-27T10:30:00Z",
  "path": "/api/v1/serviceability"
}
```

---

### Delivery Slots

#### GET /api/v1/delivery/slots

Get available delivery time slots.

**Query Parameters:**
- `serviceAreaId` (required): Service area ID
- `date` (required): Date in YYYY-MM-DD format

**Response (200 OK):**
```json
{
  "slots": [
    {
      "id": 1,
      "startTime": "07:00",
      "endTime": "09:00",
      "label": "Morning",
      "available": true,
      "remaining": 15
    },
    {
      "id": 2,
      "startTime": "09:00",
      "endTime": "12:00",
      "label": "Mid-Morning",
      "available": true,
      "remaining": 8
    },
    {
      "id": 3,
      "startTime": "12:00",
      "endTime": "15:00",
      "label": "Afternoon",
      "available": false,
      "remaining": 0
    }
  ]
}
```

**Error Responses:**
```json
// 200 OK - No slots available for date
{
  "slots": []
}

// 400 Bad Request - Missing parameters
{
  "status": 400,
  "message": "Validation error",
  "errors": [
    { "field": "serviceAreaId", "message": "Service area ID is required" },
    { "field": "date", "message": "Date is required in YYYY-MM-DD format" }
  ],
  "errorCode": "VAL_001",
  "timestamp": "2026-03-27T10:30:00Z",
  "path": "/api/v1/delivery/slots"
}
```

---

### Webhooks

#### Chargebee Webhooks

The backend processes Chargebee webhooks for real-time updates.

**Webhook Endpoint:**
```
POST /api/v1/webhooks/chargebee
```

### Supported Events

| Event | Description |
|-------|-------------|
| `customer.created` | New customer registered |
| `customer.updated` | Customer details updated |
| `subscription.created` | New subscription |
| `subscription.updated` | Subscription modified |
| `subscription.cancelled` | Subscription cancelled |
| `invoice.created` | Invoice generated |
| `invoice.paid` | Payment received |
| `payment.succeeded` | Payment successful |
| `payment.failed` | Payment failed |

### Webhook Signature Verification

```
X-Chargebee-Signature: t=<timestamp>,v1=<hmac_signature>
```

**Error Responses:**
```json
// 401 Unauthorized - Invalid signature
{
  "status": 401,
  "message": "Invalid webhook signature",
  "errorCode": "AUTH_003",
  "timestamp": "2026-03-27T10:30:00Z",
  "path": "/api/v1/webhooks/chargebee"
}

// 200 OK - Duplicate event (idempotent)
{
  "status": "skipped",
  "message": "Event already processed"
}
```

> **Note:** Webhook processing is **idempotent**. Duplicate events are detected by `event.id` and silently skipped with a 200 OK response. All webhook processing is non-blocking and best-effort.

---

### Bottle Tracking

Bottle Tracking endpoints manage the lifecycle of reusable juice bottles. The system records issuance (auto-dispatched on payment), returns, and breakage/loss reports.

#### GET /api/bottles/ledger

Get the computed bottle ledger for the authenticated user. Returns per-bottle-type balances (issued, returned, broken, outstanding).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "status": "success",
  "data": [
    {
      "customerId": "cb_cus_xxx",
      "bottleType": "glass_500ml",
      "totalIssued": 15,
      "totalReturned": 8,
      "totalBroken": 1,
      "outstanding": 6,
      "lastTransactionAt": "2026-05-25T14:30:00Z"
    }
  ]
}
```

**Error Responses:**
```json
// 200 OK - No bottle data
{
  "status": "success",
  "data": []
}

// 401 Unauthorized — User not authenticated
{
  "status": 401,
  "message": "Authentication required",
  "errorCode": "AUTH_002",
  "timestamp": "2026-03-27T10:30:00Z",
  "path": "/api/bottles/ledger"
}

// 400 Bad Request — Chargebee customer ID not found
{
  "status": 400,
  "message": "Billing account not found. Please contact support.",
  "errorCode": "PAY_002",
  "timestamp": "2026-03-27T10:30:00Z",
  "path": "/api/bottles/ledger"
}
```

**cURL Example:**
```bash
curl -X GET http://localhost:8080/api/bottles/ledger \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Accept: application/json"
```

---

#### GET /api/bottles/transactions

Get the raw bottle transaction history for the authenticated user. Optionally filter by order ID.

**Query Parameters:**
- `orderId` (optional): Filter by Chargebee order ID

**Response (200 OK):**
```json
{
  "status": "success",
  "count": 5,
  "data": [
    {
      "id": 1,
      "orderId": "cb_order_xxx",
      "customerId": "cb_cus_xxx",
      "bottleType": "glass_500ml",
      "quantity": 5,
      "action": "ISSUED",
      "referenceId": null,
      "notes": "Auto-dispatched on payment",
      "createdAt": "2026-05-25T10:00:00Z",
      "updatedAt": "2026-05-25T10:00:00Z"
    }
  ]
}
```

**Error Responses:**
```json
// 200 OK - No transactions
{
  "status": "success",
  "count": 0,
  "data": []
}
```

**cURL Example:**
```bash
# All transactions
curl -X GET http://localhost:8080/api/bottles/transactions \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Filter by order ID
curl -X GET "http://localhost:8080/api/bottles/transactions?orderId=cb_order_xxx" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

#### POST /api/bottles/return

Record bottles returned by the customer.

**Request:**
```json
{
  "orderId": "cb_order_xxx",
  "bottleType": "glass_500ml",
  "quantity": 5
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Bottle return recorded successfully",
  "data": {
    "id": 10,
    "orderId": "cb_order_xxx",
    "customerId": "cb_cus_xxx",
    "bottleType": "glass_500ml",
    "quantity": 5,
    "action": "RETURNED",
    "notes": "Customer-reported return",
    "createdAt": "2026-05-25T14:30:00Z",
    "updatedAt": "2026-05-25T14:30:00Z"
  }
}
```

**Error Responses:**
```json
// 400 Bad Request - Invalid quantity
{
  "status": 400,
  "message": "Validation error",
  "errors": [
    { "field": "quantity", "message": "Quantity must be positive" }
  ],
  "errorCode": "VAL_001",
  "timestamp": "2026-03-27T10:30:00Z",
  "path": "/api/bottles/return"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8080/api/bottles/return \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"orderId": "cb_order_xxx", "bottleType": "glass_500ml", "quantity": 5}'
```

---

#### POST /api/bottles/broken

Report bottles as broken or lost.

**Request:**
```json
{
  "orderId": "cb_order_xxx",
  "bottleType": "glass_500ml",
  "quantity": 2
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Bottle broken/lost reported successfully",
  "data": {
    "id": 10,
    "orderId": "cb_order_xxx",
    "customerId": "cb_cus_xxx",
    "bottleType": "glass_500ml",
    "quantity": 2,
    "action": "BROKEN",
    "notes": "Customer-reported broken/lost",
    "createdAt": "2026-05-25T15:00:00Z",
    "updatedAt": "2026-05-25T15:00:00Z"
  }
}
```

---

## Timeout & Retry Behavior

### Default Timeouts

| Layer | Default Timeout | Configurable? | Location |
|-------|----------------|---------------|----------|
| Flutter HTTP client | 30 seconds | Yes | `UserRepository` in `lush/lib` |
| bmjServer API | 10 seconds (inbound) | Yes | `application.properties` (`server.servlet.session.timeout`) |
| bmjServer → Chargebee | 15 seconds | Yes | `ChargebeeClient` configuration |
| ADB Exec (Appium) | 20 seconds | Yes | `appium_test/conftest.py` |

### Retry Strategy

| Scenario | Retry Count | Backoff | Notes |
|----------|-------------|---------|-------|
| Network timeout (Flutter → bmjServer) | 2 retries | 1s, 3s exponential | Only for idempotent GET requests |
| bmjServer → Chargebee timeout | 1 retry | 2s | For critical operations only (checkout, subscription actions) |
| Webhook processing failure | 3 retries | 5s, 30s, 5min exponential | Chargebee retries webhooks automatically |
| Appium element not found | Implicit: 10s | — | Set in `WebDriverWait` |
| OTP verification | No retry | — | User must manually request new OTP |

### Client-Side Error Handling

| HTTP Status | Flutter Behavior |
|-------------|------------------|
| 400 | Show validation error message from `errors[]` array. Do NOT navigate. |
| 401 | Attempt silent refresh via `/api/auth/refresh`. If fails → show public Dashboard with toast. |
| 403 | Show "Access denied" dialog. Do NOT retry. |
| 404 | Show "Not found" message. Offer navigation back. |
| 409 | Show conflict resolution dialog (e.g., "Your cart has subscription items. Clear cart to add one-time items?"). |
| 429 | Show "Too many requests. Please wait." with retry-after countdown. |
| 500+ | Show "Something went wrong. Please try again." with retry button. |

---

## Error Handling

### Standard Error Response Format

All error responses follow this standard format:

```json
{
  "timestamp": "2026-03-27T10:30:00Z",
  "status": 400,
  "message": "Error message",
  "errors": [
    {
      "field": "email",
      "message": "Invalid email format"
    }
  ],
  "path": "/api/v1/endpoint",
  "errorCode": "VALIDATION_ERROR"
}
```

### HTTP Status Codes

| Code | Status | Description |
|------|--------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created |
| 204 | No Content | Successful, no content |
| 400 | Bad Request | Invalid request (validation, missing fields, invalid credentials) |
| 401 | Unauthorized | Authentication required (missing, expired, or invalid token) |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Resource conflict (e.g., mixed cart types) |
| 422 | Unprocessable Entity | Validation error (alternative to 400 for some endpoints) |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error (unhandled exception) |
| 502 | Bad Gateway | Upstream error (e.g., Chargebee unreachable) |
| 503 | Service Unavailable | Service down (e.g., database connection lost) |

### Error Codes

| Error Code | Description | Resolution |
|------------|-------------|------------|
| `AUTH_001` | Invalid credentials | Check username/password |
| `AUTH_002` | Token expired | Re-authenticate via /api/v1/auth/signin or /api/auth/refresh |
| `AUTH_003` | Invalid token / Insufficient permissions | Re-authenticate |
| `USER_001` | User not found | Register first |
| `USER_002` | Email already exists | Use different email |
| `SUB_001` | Subscription not found | Check subscription ID |
| `SUB_002` | Subscription state error (e.g., after 9 PM cutoff) | Try again tomorrow |
| `SUB_003` | Subscription already in target state (paused/cancelled) | No action needed |
| `ORD_001` | Order/product not found | Check order/product ID |
| `ORD_002` | Insufficient stock / Cart empty | Try different product or add items |
| `PAY_001` | Payment failed | Retry payment |
| `PAY_002` | Payment pending / No Chargebee customer ID | Wait for confirmation or contact support |
| `VAL_001` | Validation error | Fix request data per errors[] array |
| `CART_TYPE_CONFLICT` | Mixed cart types (one-time + subscription) | Clear one cart type first |
| `RATE_LIMIT_EXCEEDED` | Rate limit hit | Wait for retryAfter seconds |
| `SYS_001` | System error (generic) | Contact support |

---

## Rate Limiting

### Rate Limits

| Endpoint Category | Limit | Window |
|-------------------|-------|--------|
| Authentication (signin, signup) | 10 requests | per minute |
| OTP (request, verify) | 5 requests | per 5 minutes per IP |
| General API | 100 requests | per minute |
| Order Placement | 5 requests | per minute |
| Chargebee Endpoints | Based on plan | per minute |

### Rate Limit Headers

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1679912400
Retry-After: 60
```

### Rate Limit Exceeded Response

```json
{
  "timestamp": "2026-03-27T10:30:00Z",
  "status": 429,
  "message": "Rate limit exceeded. Please wait before retrying.",
  "errorCode": "RATE_LIMIT_EXCEEDED",
  "retryAfter": 60,
  "path": "/api/v1/endpoint"
}
```

---

*Last Updated: June 8, 2026*
*API Version: 1.0.0*