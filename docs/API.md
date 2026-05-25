# BookMyJuice API Documentation

> Comprehensive API documentation for the BookMyJuice backend services.

## Table of Contents

- [Overview](#overview)
- [Authentication](#authentication)
- [API Endpoints](#api-endpoints)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Webhooks](#webhooks)
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
| Access Token | 30 days (2592000000 ms) | No refresh — re-authenticate |

### Authentication Flow

```
1. User Login
   POST /api/v1/auth/signin   (canonical)
   ↓
2. Receive Token
   { accessToken, tokenType, id, username, email, roles }
   ↓
3. Use Access Token for API calls
   Authorization: Bearer <accessToken>
   ↓
4. When Access Token expires (30 days)
   Re-authenticate via /api/v1/auth/signin
   ↓
5. Receive new Access Token
```

> **Note:** No refresh token flow exists. The JWT is a single 30-day token. When it expires, the user must re-authenticate. The token version is tracked server-side for invalidation support (e.g., on password reset).

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
  "message": "Error: Invalid username or password!"
}
```

---

#### POST /api/v1/auth/signup

Register a new user account.

**Request:**
```json
{
  "name": "John Doe",
  "email": "user@example.com",
  "phone": "+919876543210",
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

---

> **Note:** No `/api/v1/auth/refresh` endpoint exists. JWT tokens are single 30-day tokens. When expired, re-authenticate via `/api/v1/auth/signin`.

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

---

#### POST /api/v1/auth/otp/request

Request OTP for phone authentication.

**Request:**
```json
{
  "phone": "+919876543210"
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

---

#### POST /api/v1/auth/otp/verify

Verify OTP and authenticate.

**Request:**
```json
{
  "phone": "+919876543210",
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
  "phone": "+919876543210",
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

---

#### PUT /api/v1/user/profile

Update user profile.

**Request:**
```json
{
  "name": "John Updated",
  "phone": "+919876543211"
}
```

**Response (200 OK):**
```json
{
  "message": "Profile updated successfully",
  "user": { ... }
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

#### GET /api/v1/subscriptions/plans

Get available subscription plans.

**Response (200 OK):**
```json
{
  "plans": [
    {
      "id": "plan_30_30",
      "name": "30:30 Plan",
      "description": "30 juices over 30 days",
      "price": 2999,
      "currency": "INR",
      "billingPeriod": "monthly",
      "juiceCount": 30,
      "duration": 30,
      "features": [
        "Daily delivery",
        "Flexible scheduling",
        "Flexible delivery"
      ]
    },
    {
      "id": "plan_15_30",
      "name": "15:30 Plan",
      "description": "15 juices over 30 days",
      "price": 1799,
      "currency": "INR",
      "billingPeriod": "monthly",
      "juiceCount": 15,
      "duration": 30,
      "features": [
        "Alternate day delivery",
        "Flexible scheduling",
        "Flexible delivery"
      ]
    }
  ]
}
```

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

---

#### GET /api/v1/subscriptions/active

Get active subscription details.

**Response (200 OK):**
```json
{
  "subscription": {
    "id": "sub_123",
    "planId": "plan_30_30",
    "planName": "30:30 Plan",
    "status": "active",
    "startDate": "2026-03-01T00:00:00Z",
    "currentPeriodStart": "2026-03-27T00:00:00Z",
    "currentPeriodEnd": "2026-04-26T23:59:59Z",
    "nextBillingDate": "2026-04-27T00:00:00Z",
    "amount": 2999,
    "currency": "INR",
    "autoRenew": true,
    "pausedAt": null,
    "cancelledAt": null
  }
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

---

### Order Management

#### GET /api/v1/orders

Get order history with pagination.

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 10)
- `status` (optional): Filter by status

**Response (200 OK):**
```json
{
  "orders": [
    {
      "id": "ord_123",
      "orderNumber": "BMJ-2026-001234",
      "status": "delivered",
      "type": "subscription",
      "items": [
        {
          "productId": "prod_orange",
          "name": "Fresh Orange Juice",
          "quantity": 1,
          "size": "250ml",
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
    "itemsPerPage": 10
  }
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
      "size": "250ml",
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

> **Note:** `deliveryFee` is NOT included in cart response. Delivery fee is sourced from Chargebee pricing data during checkout.

---

#### POST /api/v1/cart/items

Add item to cart.

**Request:**
```json
{
  "productId": "prod_orange",
  "quantity": 2,
  "priceId": "price_250ml"
}
```

**Response (200 OK):**
```json
{
  "message": "Item added to cart",
  "cart": { ... }
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
      "priceId": "price_250ml",
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
- `409 Conflict` — Mixed cart types detected (one-time and subscription items cannot coexist)

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
- `400 Bad Request` — Cart empty, mixed cart types, or user has no Chargebee customer ID
- `401 Unauthorized` — Authentication required

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

---

### Products

#### GET /api/v1/products

Get all available products (sourced from Chargebee).

**Query Parameters:**
- `category` (optional): Filter by category
- `search` (optional): Search query
- `sortBy` (optional): popularity, price_low_high, price_high_low
- `page` (optional): Page number
- `limit` (optional): Items per page

**Response (200 OK):**
```json
{
  "products": [
    {
      "id": "prod_orange",
      "name": "Fresh Orange Juice",
      "description": "100% fresh oranges, cold-pressed",
      "category": "citrus",
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
        "unit": "per 250ml"
      },
      "prices": [
        {
          "id": "price_250ml",
          "size": "250ml",
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
  "pagination": { ... }
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
  "category": "citrus",
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
      "label": "Morning"
    },
    {
      "id": 2,
      "startTime": "09:00",
      "endTime": "12:00",
      "label": "Mid-Morning"
    }
  ]
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
| `invoice.failed` | Payment failed |
| `payment.succeeded` | Payment successful |
| `payment.failed` | Payment failed |

### Webhook Signature Verification

```
X-Chargebee-Signature: t=<timestamp>,v1=<hmac_signature>
```

---

## Error Handling

### Standard Error Response Format

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
| 400 | Bad Request | Invalid request |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Resource conflict (e.g., mixed cart types) |
| 422 | Unprocessable Entity | Validation error |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 502 | Bad Gateway | Upstream error |
| 503 | Service Unavailable | Service down |

### Error Codes

| Error Code | Description | Resolution |
|------------|-------------|------------|
| `AUTH_001` | Invalid credentials | Check username/password |
| `AUTH_002` | Token expired | Re-authenticate via /api/v1/auth/signin |
| `AUTH_003` | Invalid token | Re-authenticate |
| `USER_001` | User not found | Register first |
| `USER_002` | Email already exists | Use different email |
| `SUB_001` | Subscription not found | Check subscription ID |
| `SUB_002` | Subscription already active | No action needed |
| `SUB_003` | Subscription already paused | Already paused |
| `ORD_001` | Order not found | Check order ID |
| `ORD_002` | Insufficient stock | Try different product |
| `PAY_001` | Payment failed | Retry payment |
| `PAY_002` | Payment pending | Wait for confirmation |
| `VAL_001` | Validation error | Fix request data |
| `SYS_001` | System error | Contact support |

---

## Rate Limiting

### Rate Limits

| Endpoint Category | Limit | Window |
|-------------------|-------|--------|
| Authentication | 10 requests | per minute |
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
  "message": "Rate limit exceeded",
  "errorCode": "RATE_LIMIT_EXCEEDED",
  "retryAfter": 60,
  "path": "/api/v1/endpoint"
}
```

---

## SDKs & Examples

### Flutter Example

```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

class ApiService {
  static const String baseUrl = 'http://localhost:8080/api/v1';
  String? _accessToken;
  
  // Login
  Future<Map<String, dynamic>> login(String email, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/signin'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'username': email,
        'password': password,
      }),
    );
    
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      _accessToken = data['accessToken'];
      return data;
    } else {
      throw ApiException('Login failed: ${response.body}');
    }
  }
  
  // Get Profile
  Future<Map<String, dynamic>> getProfile() async {
    final response = await http.get(
      Uri.parse('$baseUrl/user/profile'),
      headers: {
        'Authorization': 'Bearer $_accessToken',
        'Accept': 'application/json',
      },
    );
    
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw ApiException('Failed to get profile');
    }
  }
  
  // Get Products
  Future<List<dynamic>> getProducts() async {
    final response = await http.get(
      Uri.parse('$baseUrl/products'),
      headers: {'Accept': 'application/json'},
    );
    
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return data['products'];
    } else {
      throw ApiException('Failed to get products');
    }
  }
}

class ApiException implements Exception {
  final String message;
  ApiException(this.message);
  
  @override
  String toString() => message;
}
```

### cURL Examples

```bash
# Login (canonical endpoint)
curl -X POST http://localhost:8080/api/v1/auth/signin \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user@example.com",
    "password": "SecurePass123!"
  }'

# Get Profile
curl -X GET http://localhost:8080/api/v1/user/profile \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Accept: application/json"

# Get Products
curl -X GET http://localhost:8080/api/v1/products \
  -H "Accept: application/json"

# Initiate Checkout (V2 - cart-based)
curl -X POST http://localhost:8080/api/v2/checkout \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json"

# Add Address (canonical)
curl -X POST http://localhost:8080/api/v1/address \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "label": "Home",
    "fullName": "John Doe",
    "phone": "9876543210",
    "addressLine1": "123 Main St",
    "city": "Bangalore",
    "state": "Karnataka",
    "pincode": "560001"
  }'

# Check Pincode Serviceability
curl -X GET "http://localhost:8080/api/v1/serviceability?pincode=400001" \
  -H "Accept: application/json"
```

---

## Swagger/OpenAPI Documentation

Interactive API documentation is available at:

- **Development:** http://localhost:8080/swagger-ui.html
- **Staging:** https://staging-api.bookmyjuice.co.in/swagger-ui.html
- **Production:** https://api.bookmyjuice.co.in/swagger-ui.html

**OpenAPI JSON Spec:**
- http://localhost:8080/v3/api-docs

---

*Last Updated: May 20, 2026*
*API Version: 1.0.0*
