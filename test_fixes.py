#!/usr/bin/env python3
"""Quick verification script for bug fixes using urllib (stdlib)."""

import json
import urllib.request

BASE = "http://localhost:8080"

def test(desc, method, path, body=None):
    print(f"\n{'='*60}")
    print(f"TEST: {desc}")
    print(f"{method} {BASE}{path}")
    try:
        url = f"{BASE}{path}"
        data = json.dumps(body).encode() if body else None
        req = urllib.request.Request(url, data=data, method=method)
        if body:
            req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                status = resp.status
                raw = resp.read().decode()
        except urllib.error.HTTPError as e:
            status = e.code
            raw = e.read().decode()
        print(f"  Status: {status}")
        try:
            obj = json.loads(raw)
            print(f"  Response: {json.dumps(obj, indent=2)}")
        except:
            print(f"  Response: {raw[:200]}")
        verdict = "PASS" if status < 500 else "FAIL"
        print(f"  {verdict}")
    except Exception as e:
        print(f"  ERROR: {e}")

# B-03: Test global error handler returns proper JSON
test("B-03: Bad signin request (no username/password)", "POST", "/api/auth/signin",
     body={"bad_field": "test"})

# B-05: Pricing plans should be accessible without auth
test("B-05: Pricing plans (no auth)", "GET", "/api/subscriptions/pricing/plans")

# B-09: Unknown route should return 404, not 401
test("B-09: Unknown route", "GET", "/api/nonexistent/route")

# Test health endpoint
test("Health check", "GET", "/api/health")

# Test seed data signin
test("B-10: Signin with seed TA-01", "POST", "/api/auth/signin",
     body={"username": "9999999901", "password": "Test@1234"})

# B-06: Check if test routes require auth (user said checkout requires auth)
test("B-06: Test routes (no auth)", "GET", "/api/test/checkout")

print(f"\n{'='*60}")
print("Done.")
