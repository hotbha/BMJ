#!/usr/bin/env python3
"""
Comprehensive E2E Black-Box Test Suite for BookMyJuice Backend V3
- Phase 2: Execute all tests against live server
- Phase 3: Fix and verify all bugs
"""
import json
import urllib.request
import urllib.error
import sys
import traceback
import time

BASE_URL = "http://localhost:8080"

results = []
test_accounts = {}

def test(name, method, path, body=None, expected_status=200, headers=None, raw_body=False):
    """Execute a single API test and record result"""
    url = f"{BASE_URL}{path}"
    data = json.dumps(body).encode('utf-8') if body and not raw_body else (body.encode('utf-8') if raw_body else None)
    
    if headers is None:
        headers = {}
    if 'Content-Type' not in headers and not raw_body:
        headers['Content-Type'] = 'application/json'
    
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print(f"{method} {url}")
    if body:
        print(f"Body: {json.dumps(body, indent=2) if not raw_body else body[:200]}")
    
    try:
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        with urllib.request.urlopen(req, timeout=15) as resp:
            status = resp.status
            raw = resp.read().decode('utf-8')
            try:
                response_json = json.loads(raw)
                print(f"Response ({status}): {json.dumps(response_json, indent=2)}")
            except:
                response_json = raw
                print(f"Response ({status}): {raw[:200]}")
            
            passed = status == expected_status
            results.append({"name": name, "passed": passed, "status": status, 
                          "expected": expected_status, "response": response_json,
                          "path": path, "method": method})
            if passed:
                print(f"✅ PASSED")
            else:
                print(f"❌ FAILED - Expected status {expected_status}, got {status}")
            return response_json, None
    except urllib.error.HTTPError as e:
        status = e.code
        try:
            raw = e.read().decode('utf-8')
            response_json = json.loads(raw)
            print(f"Response ({status}): {json.dumps(response_json, indent=2)}")
        except:
            response_json = raw = e.read().decode('utf-8')
            print(f"Response ({status}): {raw[:200]}")
        
        passed = status == expected_status
        results.append({"name": name, "passed": passed, "status": status,
                      "expected": expected_status, "response": response_json,
                      "path": path, "method": method})
        if passed:
            print(f"✅ PASSED")
        else:
            print(f"❌ FAILED - Expected status {expected_status}, got {status}")
        return response_json, None
    except Exception as e:
        print(f"💥 ERROR: {e}")
        traceback.print_exc()
        results.append({"name": name, "passed": False, "status": 0,
                      "expected": expected_status, "response": str(e),
                      "path": path, "method": method})
        print(f"❌ FAILED - Exception: {e}")
        return None, str(e)

def print_summary():
    """Print test summary with categorized results"""
    passed = sum(1 for r in results if r['passed'])
    failed = sum(1 for r in results if not r['passed'])
    total = len(results)
    
    print(f"\n\n{'='*60}")
    print(f"TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Total:  {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Pass%:  {passed/total*100 if total else 0:.1f}%")
    
    if failed > 0:
        print(f"\n--- FAILURES ---")
        for r in results:
            if not r['passed']:
                print(f"  ❌ {r['name']} ({r['method']} {r['path']})")
                print(f"     Expected: {r['expected']}, Got: {r['status']}")
                if isinstance(r['response'], dict):
                    err = r['response'].get('error') or r['response'].get('message') or json.dumps(r['response'])[:100]
                    print(f"     Info: {err}")
                else:
                    print(f"     Response: {str(r['response'])[:100]}")

# ============================================================
# TEST EXECUTION
# ============================================================
print("="*60)
print("BOOKMYJUICE E2E BLACK-BOX TEST SUITE V3")
print("Phase 2: Execution + Phase 3: Fix Verification")
print("="*60)

# ============================================================
# AUTH TEST SUITE
# ============================================================
print("\n\n--- AUTH TEST SUITE ---")

# Health check
test("Health Check", "GET", "/api/health", expected_status=200)

# --- SIGNUP & SIGNIN FLOW (creates live account for subsequent tests) ---
ts = str(int(time.time()))
# Ensure 10-digit phone: prefix 99 + last 8 digits of timestamp
test_phone = f"99{ts[-8:]}"
test_email = f"e2e_{ts[-8:]}@example.com"

print(f"\n[SETUP] Using test phone: {test_phone}, email: {test_email}")

# Sign up with complete valid data
resp, _ = test("Sign Up (complete)", "POST", "/api/auth/signup",
    {"firstName": "E2E", "lastName": "Tester", "email": test_email, 
     "phone": test_phone, "password": "Test@1234"},
    expected_status=200)
if resp:
    test_accounts["phone"] = test_phone
    test_accounts["password"] = "Test@1234"

# Sign in with the created account
resp, _ = test("Sign In (existing user)", "POST", "/api/auth/signin",
    {"username": test_phone, "password": "Test@1234"},
    expected_status=200)
jwt_token = None
if resp and isinstance(resp, dict):
    if "token" in resp:
        jwt_token = resp["token"]
    elif "jwt" in resp:
        jwt_token = resp["jwt"]
    elif "accessToken" in resp:
        jwt_token = resp["accessToken"]
    test_accounts["jwt"] = jwt_token
    if jwt_token:
        print(f"[SETUP] JWT token obtained: {jwt_token[:50]}...")

# Sign in with invalid credentials
test("Sign In (wrong password)", "POST", "/api/auth/signin",
    {"username": test_phone, "password": "WrongPass@1"},
    expected_status=400)

# Auth header for authenticated tests
auth_header = {"Authorization": f"Bearer {jwt_token}"} if jwt_token else {}

# --- UNIFIED SIGNUP ---
ts2 = str(int(time.time()))
unified_phone = f"88{ts2[-8:]}"
# Full unified signup - country must be 2-letter code!
resp, _ = test("Unified Signup (complete)", "POST", "/api/auth/unified-signup",
    {"phone": unified_phone, "email": f"unified_{ts2[-8:]}@example.com", 
     "password": "Test@1234", "fullName": "Unified User",
     "firstName": "Unified", "lastName": "User",
     "address": "123 Test Street", "extendedAddr": "Apt 4B",
     "extendedAddr2": "", "city": "Mumbai", "state": "Maharashtra",
     "zip": "400001", "country": "IN"},  # 2-letter code required
    expected_status=200)

# --- AUTO LOGIN ---
# autologin is @GetMapping, so POST should 404 via RouteExistenceFilter
test("Auto Login (POST - wrong method)", "POST", "/api/auth/autologin",
    {}, expected_status=404)

# Auto login with valid JWT
if jwt_token:
    test("Auto Login (valid JWT)", "GET", "/api/auth/autologin",
        headers={"Authorization": f"Bearer {jwt_token}"},
        expected_status=200)

# Auto login without auth header
test("Auto Login (no auth header)", "GET", "/api/auth/autologin",
    expected_status=400)

# --- GOOGLE SIGN-IN ---
# Needs real Google token - test with invalid token
test("Google Sign-In (invalid token)", "POST", "/api/auth/google",
    {"idToken": "test_invalid_google_token"},
    expected_status=400)

# --- SEND & VERIFY EMAIL ---
ts3 = str(int(time.time()))
verify_email = f"verify_{ts3[-8:]}@example.com"
resp, _ = test("Send Email Verification", "POST", "/api/auth/send-email-verification",
    {"email": verify_email},
    expected_status=200)

# Verify with wrong code (hardcoded won't match server-generated code)
test("Verify Email Code (wrong code)", "POST", "/api/auth/verify-email-code",
    {"email": verify_email, "verificationCode": "000000"},
    expected_status=400)

# --- ACCOUNT ENDPOINTS ---
# GET /api/auth/account doesn't exist (only DELETE does)
test("Get Account (route check - no auth)", "GET", "/api/auth/account",
    expected_status=404)

# DELETE requires auth - without auth returns 403 (AccessDeniedException → Forbidden)
test("Delete Account (no auth)", "DELETE", "/api/auth/account",
    expected_status=403)

# ============================================================
# PRODUCTS / CATALOG
# ============================================================
print("\n\n--- PRODUCTS/CATALOG TEST SUITE ---")

# Products endpoint requires auth
test("Get Products (no auth)", "GET", "/api/v1/products",
    expected_status=401)

# Pricing plans are public (permitAll in B-05 fix)
test("Get Pricing Plans (no auth)", "GET", "/api/subscriptions/pricing/plans",
    expected_status=200)


# ============================================================
# SUBSCRIPTION
# ============================================================
print("\n\n--- SUBSCRIPTION TEST SUITE ---")

test("Get My Subs (no auth)", "GET", "/api/subscriptions/my",
    expected_status=401)
test("Create Sub (no auth)", "POST", "/api/subscriptions/create",
    {"planId": "test-plan", "paymentMethodId": "pm_test"},
    expected_status=401)
test("Pause Sub (no auth)", "PUT", "/api/subscriptions/test-123/pause",
    expected_status=401)


# ============================================================
# CART
# ============================================================
print("\n\n--- CART TEST SUITE ---")

test("Get Cart (no auth)", "GET", "/api/v1/cart", expected_status=401)
test("Add to Cart (no auth)", "POST", "/api/v1/cart/items",
    {"priceId": "test-price", "quantity": 1}, expected_status=401)
test("Clear Cart (no auth)", "DELETE", "/api/v1/cart/clear", expected_status=401)

# Cart with auth
if jwt_token:
    test("Get Cart (with auth)", "GET", "/api/v1/cart", 
         headers=auth_header, expected_status=200)


# ============================================================
# CHECKOUT
# ============================================================
print("\n\n--- CHECKOUT TEST SUITE ---")

# Checkout test endpoints: /api/test/** now permitAll (B-11), but @PreAuthorize
# returns 403 (Forbidden) instead of 401 (Unauthorized) when no valid role
test("One-time Checkout URL (no auth)", "GET", "/api/test/oneTimeCheckoutPageUrl",
    expected_status=403)  # 403 because route is permitted but role check fails
test("Cart Checkout (no auth)", "POST", "/api/test/cartCheckout",
    [{"priceId": "test-price", "quantity": 1}], expected_status=403)  # same


# ============================================================
# ORDERS
# ============================================================
print("\n\n--- ORDERS TEST SUITE ---")

test("Get Orders (no auth)", "GET", "/api/orders/my", expected_status=401)
test("Get Order Detail (no auth)", "GET", "/api/orders/test-order-123", expected_status=401)


# ============================================================
# INVOICES
# ============================================================
print("\n\n--- INVOICES TEST SUITE ---")

test("Get Invoices (no auth)", "GET", "/api/invoices/my", expected_status=401)


# ============================================================
# ADDRESS
# ============================================================
print("\n\n--- ADDRESS TEST SUITE ---")

# Canonical address endpoint at /api/v1/address (NOT /api/delivery/addresses)
test("Get Addresses (no auth)", "GET", "/api/v1/address", expected_status=401)
test("Add Address (no auth)", "POST", "/api/v1/address",
    {"fullName": "Test", "phone": "9876543210", "addressLine1": "123 Test St",
     "city": "Mumbai", "state": "Maharashtra", "pincode": "400001"},
    expected_status=401)


# ============================================================
# WEBHOOK
# ============================================================
print("\n\n--- WEBHOOK TEST SUITE ---")

# Webhook requires HTTP Basic auth per separate filter chain
test("Webhook Chargebee (no auth)", "POST", "/api/webhooks/chargebee",
    {"event_type": "test.event", "content": {"id": "test"}},
    expected_status=401)


# ============================================================
# API CONSISTENCY
# ============================================================
print("\n\n--- API CONSISTENCY TEST SUITE ---")

# /api/v1/auth/signin now has permitAll (B-11 fix). Invalid creds → 400
test("v1 auth prefix (invalid creds)", "POST", "/api/v1/auth/signin",
    {"username": "invalid", "password": "invalid"},
    expected_status=400)  # Route exists, permitAll, invalid creds = 400

# v1 auth prefix with valid creds should work (signin with our test account)
if jwt_token:
    test("v1 auth prefix (signin with real creds)", "POST", "/api/v1/auth/signin",
        {"username": test_phone, "password": "Test@1234"},
        expected_status=200)


# ============================================================
# Print results
# ============================================================
print_summary()

# Write detailed report
with open('e2e_test_report_v3.json', 'w') as f:
    json.dump({
        "summary": {
            "total": len(results),
            "passed": sum(1 for r in results if r['passed']),
            "failed": sum(1 for r in results if not r['passed']),
            "pass_rate": f"{sum(1 for r in results if r['passed'])/len(results)*100 if results else 0:.1f}%"
        },
        "results": results,
        "failures": [r for r in results if not r['passed']],
        "test_account": test_accounts
    }, f, indent=2)

print(f"\n\nDetailed report written to e2e_test_report_v3.json")
