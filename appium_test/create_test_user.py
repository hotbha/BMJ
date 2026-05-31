"""
Create or sign in a test user in Firebase Auth for E2E testing.
Also validates if existing account works.
"""
import requests
import sys
import os

def main():
    api_key = 'AIzaSyAYGWyGFM5c52O-1vHRjOlX7hI2bynf0p0'
    
    # Try existing account first
    existing_creds = [
        ('tester@bookmyjuice.com', 'Test@1234'),
        ('tester@bookmyjuice.com', 'Test@123'),
        ('e2etester@bookmyjuice.com', 'E2ETest@1234'),
    ]
    
    for email, password in existing_creds:
        r = requests.post(
            f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}',
            json={'email': email, 'password': password, 'returnSecureToken': True},
            timeout=15
        )
        if r.status_code == 200:
            data = r.json()
            print(f"VALID ACCOUNT: email={email} password={password}")
            print(f"  localId={data.get('localId')}")
            print(f"  idToken={data.get('idToken', '')[:50]}...")
            return
        else:
            err = r.json().get('error', {}).get('message', '')
            print(f"  INVALID: {email}/{password} -> {err}")
    
    # No existing account worked — create a new one
    print("\nCreating new test user...")
    new_email = 'e2etester@bookmyjuice.com'
    new_pwd = 'E2ETest@1234'
    
    r = requests.post(
        f'https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={api_key}',
        json={'email': new_email, 'password': new_pwd, 'returnSecureToken': True},
        timeout=15
    )
    if r.status_code == 200:
        data = r.json()
        print(f"CREATED: email={data.get('email')} password={new_pwd}")
        print(f"  localId={data.get('localId')}")
        print(f"\nUpdate .env with:")
        print(f"  TEST_EMAIL={new_email}")
        print(f"  TEST_PASSWORD={new_pwd}")
    else:
        err = r.json().get('error', {}).get('message', '')
        print(f"  CREATE FAILED: {err}")
        print(f"  Full error: {r.text}")

if __name__ == '__main__':
    main()