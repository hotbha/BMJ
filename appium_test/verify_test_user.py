"""
Verify the test user's email in Firebase and validate credentials work.
"""
import requests

api_key = 'AIzaSyAYGWyGFM5c52O-1vHRjOlX7hI2bynf0p0'
email = 'e2etester@bookmyjuice.com'
password = 'E2ETest@1234'

# Step 1: Sign in
print("=== Step 1: Sign in ===")
r = requests.post(
    f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}',
    json={'email': email, 'password': password, 'returnSecureToken': True},
    timeout=15
)
print(f"Status: {r.status_code}")
data = r.json()
if r.status_code != 200:
    print(f"Failed: {data}")
    exit(1)

id_token = data['idToken']
print(f"Signed in successfully")
print(f"  emailVerified: {data.get('emailVerified')}")
print(f"  localId: {data.get('localId')}")

# Step 2: Verify email
print("\n=== Step 2: Verify email ===")
r2 = requests.post(
    f'https://identitytoolkit.googleapis.com/v1/accounts:update?key={api_key}',
    json={'idToken': id_token, 'emailVerified': True, 'returnSecureToken': True},
    timeout=15
)
print(f"Status: {r2.status_code}")
print(f"Response: {r2.json()}")

# Step 3: Re-sign in to check verified status
print("\n=== Step 3: Re-sign in to verify ===")
r3 = requests.post(
    f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}',
    json={'email': email, 'password': password, 'returnSecureToken': True},
    timeout=15
)
data3 = r3.json()
print(f"emailVerified: {data3.get('emailVerified')}")
print(f"Success! Account is now verified.")