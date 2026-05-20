#!/usr/bin/env python3
"""Quick test script using only stdlib to verify fixes."""

import json
import urllib.request
import urllib.error

BASE = "http://localhost:8080"

def test(desc, method, path, body=None, expect=None):
    print(f"\n{'='*60}")
    print(f"TEST: {desc}")
    print(f"{method} {BASE}{path}")
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
    try:
        obj = json.loads(raw)
        print(f"  Response: {json.dumps(obj, indent=2)[:400]}")
    except:
        obj = raw
        print(f"  Response: {str(raw)[:200]}")
    print(f"  Status: {status}")
    if expect:
        ok = "✅" if status == expect else "❌"
        print(f"  {ok} Expected {expect}, got {status}")
    else:
        print(f"  ℹ️")
    return status, obj

# B-03: Validation
test("B-03: Validation error JSON", "POST", "/api/auth/signin",
     body={"bad": "data"}, expect=400)

# B-05: Pricing
test("B-05: Pricing no auth", "GET", "/api/subscriptions/pricing/plans", expect=200)

# B-06: Test routes
test("B-06: /api/test/ requires auth", "GET", "/api/test/checkout", expect=401)

# B-09: Unknown route
test("B-09: Unknown route", "GET", "/api/nonexistent/route", expect=404)

# Health
test("Health", "GET", "/api/health", expect=200)

# B-10: Sign in with seed
test("B-10: TA-01 signin", "POST", "/api/auth/signin",
     body={"username": "9999999901", "password": "Test@1234"}, expect=200)

print("\nDONE")
