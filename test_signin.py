import requests, json

# Test signin
r = requests.post("http://localhost:8080/api/auth/signin", 
                   json={"username": "9999999901", "password": "Test@1234"})
print(f"Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"Token: {data.get('accessToken', 'N/A')[:60]}...")
    print(f"User: {data.get('username', 'N/A')}")
else:
    print(f"Error: {r.text}")

# Also test TA-02
r2 = requests.post("http://localhost:8080/api/auth/signin", 
                    json={"username": "9999999902", "password": "Test@1234"})
print(f"\nTA-02 Status: {r2.status_code}")
if r2.status_code == 200:
    print(f"TA-02 login OK")
else:
    print(f"TA-02 Error: {r2.text}")

# Test admin (TA-03)
r3 = requests.post("http://localhost:8080/api/auth/signin", 
                    json={"username": "9999999903", "password": "Test@1234"})
print(f"\nTA-03 Status: {r3.status_code}")
if r3.status_code == 200:
    print(f"TA-03 login OK")
else:
    print(f"TA-03 Error: {r3.text}")
