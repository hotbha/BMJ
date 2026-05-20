#!/usr/bin/env python3
"""Fix remaining issues: B-09 (404), B-10 (seed accounts), B-05 (pricing)."""

import subprocess, json, urllib.request, urllib.error

BASE = "http://localhost:8080"

def run(cmd):
    """Run a command inside the bmj-mysql container."""
    full = f"docker exec -i bmj-mysql sh -c \"{cmd}\""
    r = subprocess.run(full, capture_output=True, text=True, shell=True)
    return r.stdout, r.stderr

# Step 1: Check what's in the DB
print("="*60)
print("STEP 1: Check seed accounts in MySQL")
print("="*60)

# Generate a proper BCrypt hash using Java's output from the running backend
# Let's check the seed data first
out, err = run("mysql -u bmj -p'PASS@123' bmj_db -e 'SELECT id,username,email FROM users WHERE id IN (1,2,3)' 2>&1")
print(f"Users: {out}")
print(f"Errors: {err}")

out, err = run("mysql -u bmj -p'PASS@123' bmj_db -e 'SELECT id,name FROM roles' 2>&1")
print(f"Roles: {out}")

out, err = run("mysql -u bmj -p'PASS@123' bmj_db -e 'SELECT * FROM user_roles' 2>&1")
print(f"User-Roles: {out}")

# Step 2: Delete and re-seed with correct BCrypt hash
print("\n" + "="*60)
print("STEP 2: Re-seed test accounts")
print("="*60)

# First delete existing test accounts to avoid conflicts
run("mysql -u bmj -p'PASS@123' bmj_db -e 'DELETE FROM user_roles WHERE user_id IN (1,2,3)'")
run("mysql -u bmj -p'PASS@123' bmj_db -e 'DELETE FROM users WHERE id IN (1,2,3)'")

# Let's use the BCrypt hash from a known working hash
# We'll use Spring Boot's own PasswordEncoder to generate a hash by calling a test endpoint
# OR we can just let the application handle this through a registration

# Let's get a proper BCrypt hash by making a signup request with a known password
# First, let's check the signup endpoint to understand what's needed
print("\nTesting signup with simple password to get hash...")
signup_data = json.dumps({
    "firstName": "Seed",
    "lastName": "User",
    "email": "seedtest@bookmyjuice.co.in",
    "phone": "9999999999",
    "password": "TestPass@1234"
}).encode()

req = urllib.request.Request(
    f"{BASE}/api/auth/signup",
    data=signup_data,
    method="POST",
    headers={"Content-Type": "application/json"}
)
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        print(f"Signup status: {resp.status}")
        print(f"Signup response: {resp.read().decode()}")
except urllib.error.HTTPError as e:
    print(f"Signup error: {e.code} {e.read().decode()}")

# Get the hash from DB
out, err = run("mysql -u bmj -p'PASS@123' bmj_db -e \"SELECT password FROM users WHERE phone='9999999999'\"")
print(f"Hash from signup: {out.strip()}")

# Now let's check the AuthEntryPointJwt
print("\n" + "="*60)
print("STEP 3: Check AuthEntryPointJwt")
print("="*60)

try:
    with open("X:\\BMJ\\bmjServer\\src\\main\\java\\com\\bookmyjuice\\security\\jwt\\AuthEntryPointJwt.java", "r") as f:
        content = f.read()
        print(content[:500])
except:
    print("Could not read AuthEntryPointJwt.java")
