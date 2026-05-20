#!/usr/bin/env python3
"""
Comprehensive E2E Black-Box Test Suite for BookMyJuice Backend V2
Tests against actual API contracts discovered from source code
"""
import json
import urllib.request
import urllib.error
import sys
import traceback
import time

BASE_URL = "http://localhost:8080"

results = []

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
    """Print test summary"""
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
print("BOOKMYJUICE E2E BLACK-BOX TEST SUITE V2")
print("Using correct API field names from source code")
print("="*60)

# ----- 1. AUTH TESTS -----
print("\n\n--- AUTH TEST SUITE ---")

# Health check first
test("Health Check", "GET", "/api/health", expected_status=200)

# Signin with CORRECT field names (LoginRequest uses 'username' not 'mobileNumber')
# username can be phone number or email
resp, _ = test("Sign In (correct fields)", "POST", "/api/auth/signin", 
     {"username": "9876543210", "password": "Test@123"}, 
     expected_status=200)

# Actually, with correct field names but no user exists, it should get BadCredentials (400)
# But since there's no @ControllerAdvice, validation pass -> BadCredentials -> 400 JSON response
# The /error path issue only happens with validation failures (@Valid)
# Let's check what happens with just a 400 response

# Try signup with CORRECT field names (EmailSignupRequest uses firstName, lastName, email, phone, password)
resp, _ = test("Sign Up (correct fields)", "POST", "/api/auth/signup",
     {"firstName": "E2E", "lastName": "Test", "email": "e2etest_v2@example.com", 
      "phone": "9999999998", "password": "Test@1234"},
     expected_status=200)

# Send OTP
resp, _ = test("Send OTP", "POST", "/api/auth/send-otp",
     {"phone": "9876543210"},
     expected_status=200)

# Verify OTP
test("Verify OTP", "POST", "/api/auth/verify-otp",
     {"phone": "9876543210", "otp": "123456"},
     expected_status=200)

# Login with OTP  
test("Login with OTP (correct fields)", "POST", "/api/auth/login-otp",
     {"phone": "9876543210", "otp": "123456"},
     expected_status=200)

# Google sign-in
test("Google Sign-In", "POST", "/api/auth/google",
     {"idToken": "test_google_id_token"},
     expected_status=200)

# Unified signup (correct fields - uses phone, email, password, fullName)
test("Unified Signup (correct fields)", "POST", "/api/auth/unified-signup",
     {"phone": "9999999997", "email": "unified_v2@example.com", 
      "password": "Test@1234", "fullName": "Unified User"},
     expected_status=200)

# Auto login
test("Auto Login (no auth header)", "POST", "/api/auth/autologin",
     {}, expected_status=400)

# Reset password by mobile
test("Reset Password Mobile (correct fields)", "POST", "/api/auth/reset-password-mobile",
     {"phone": "9876543210", "otp": "123456", "password": "NewTest@123"},
     expected_status=200)

# Reset password by email
test("Reset Password Email", "POST", "/api/auth/reset-password-email",
     {"email": "user@example.com", "password": "NewTest@123", "verificationCode": "123456"},
     expected_status=200)

# Send email verification
test("Send Email Verification", "POST", "/api/auth/send-email-verification",
     {"email": "newuser_v2@example.com"},
     expected_status=200)

# Verify email code
test("Verify Email Code", "POST", "/api/auth/verify-email-code",
     {"email": "user@example.com", "verificationCode": "123456"},
     expected_status=200)

# Link Google account (no OTP - should fail validation)
test("Link Google Account (invalid params)", "POST", "/api/auth/link-google-account",
     {"phone": "", "otp": "", "googleId": ""},
     expected_status=400)

# Account endpoints - require auth
test("Get Account (no auth)", "GET", "/api/auth/account",
     expected_status=401)

test("Delete Account (no auth)", "DELETE", "/api/auth/account",
     expected_status=401)


# ----- 2. PRODUCTS / CATALOG -----
print("\n\n--- PRODUCTS/CATALOG TEST SUITE ---")

test("Get Products (no auth)", "GET", "/api/v1/products",
     expected_status=401)

test("Get Pricing Plans (no auth)", "GET", "/api/subscriptions/pricing/plans",
     expected_status=200)  # Should be public (no @PreAuthorize)


# ----- 3. SUBSCRIPTION -----
print("\n\n--- SUBSCRIPTION TEST SUITE ---")

test("Get My Subs (no auth)", "GET", "/api/subscriptions/my",
     expected_status=401)
test("Create Sub (no auth)", "POST", "/api/subscriptions/create",
     {"planId": "test-plan", "paymentMethodId": "pm_test"},
     expected_status=401)
test("Pause Sub (no auth)", "PUT", "/api/subscriptions/test-123/pause",
     expected_status=401)


# ----- 4. CART -----
print("\n\n--- CART TEST SUITE ---")

test("Get Cart (no auth)", "GET", "/api/v1/cart", expected_status=401)
test("Add to Cart (no auth)", "POST", "/api/v1/cart/items",
     {"priceId": "test-price", "quantity": 1}, expected_status=401)
test("Clear Cart (no auth)", "DELETE", "/api/v1/cart/clear", expected_status=401)


# ----- 5. CHECKOUT -----
print("\n\n--- CHECKOUT TEST SUITE ---")

test("One-time Checkout URL (no auth)", "GET", "/api/test/oneTimeCheckoutPageUrl",
     expected_status=200)
test("Cart Checkout (no auth)", "POST", "/api/test/cartCheckout",
     [{"priceId": "test-price", "quantity": 1}], expected_status=200)


# ----- 6. ORDERS -----
print("\n\n--- ORDERS TEST SUITE ---")

test("Get Orders (no auth)", "GET", "/api/orders/my", expected_status=401)
test("Get Order Detail (no auth)", "GET", "/api/orders/test-order-123", expected_status=401)


# ----- 7. INVOICES -----
print("\n\n--- INVOICES TEST SUITE ---")

test("Get Invoices (no auth)", "GET", "/api/invoices/my", expected_status=401)


# ----- 8. DELIVERY -----
print("\n\n--- DELIVERY TEST SUITE ---")

test("Get Addresses (no auth)", "GET", "/api/delivery/addresses", expected_status=401)
test("Add Address (no auth)", "POST", "/api/delivery/addresses",
     {"fullName": "Test", "phone": "9876543210", "addressLine1": "123 Test St",
      "city": "City", "state": "State", "pincode": "123456", "isDefault": False},
     expected_status=401)


# ----- 9. WEBHOOK -----
print("\n\n--- WEBHOOK TEST SUITE ---")

test("Webhook Chargebee (no auth)", "POST", "/api/webhooks/chargebee",
     {"event_type": "test.event", "content": {"id": "test"}},
     expected_status=401)


# ----- 10. API CONSISTENCY -----
print("\n\n--- API CONSISTENCY TEST SUITE ---")

# Check if /api/v1/auth* also works (might be mapped despite code saying /api/auth)
test("v1 auth prefix check", "POST", "/api/v1/auth/signin",
     {"username": "test", "password": "test"},
     expected_status=404)  # Should 404 since AuthController uses /api/auth


# ============================================================
# PHONE CONNECTIVITY TEST
# ============================================================
print("\n\n--- PHONE CONNECTIVITY TEST ---")
print("\nChecking if phone can reach backend...")

# Phone has two IPs: 192.168.1.5 (WiFi) and 10.37.65.201 (USB)
# PC IPs: 10.37.65.113 (USB), 172.27.240.1 (Hyper-V)
# Backend is on 0.0.0.0:8080 inside Docker, mapped to host's 0.0.0.0:8080

# The phone should be able to reach the PC via:
# 1. USB tethering network: http://10.37.65.113:8080
# 2. WiFi network: http://192.168.1.x:8080 (where x is PC's WiFi IP - need to find)

print("Phone IP (WiFi): 192.168.1.5")
print("Phone IP (USB):  10.37.65.201")
print("PC IP (USB):     10.37.65.113")
print("Backend port:    8080")
print("")
print("The phone should access: http://10.37.65.113:8080/api/health")
print("Or via WiFi: http://<PC_WIFI_IP>:8080/api/health")
print("")

# Test from this machine (simulating phone)
test("Phone accessibility (via USB)", "GET", "http://10.37.65.113:8080/api/health",
     expected_status=200)


# Print results
print_summary()

# Write detailed report
with open('e2e_test_report_v2.json', 'w') as f:
    json.dump({
        "summary": {
            "total": len(results),
            "passed": sum(1 for r in results if r['passed']),
            "failed": sum(1 for r in results if not r['passed']),
            "pass_rate": f"{sum(1 for r in results if r['passed'])/len(results)*100 if results else 0:.1f}%"
        },
        "results": results,
        "failures": [r for r in results if not r['passed']]
    }, f, indent=2)

print(f"\n\nDetailed report written to e2e_test_report_v2.json")
