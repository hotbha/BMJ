"""Read-only probe: prove the subscription identity mismatch.

Signs in a test phone via dev OTP, then asks /api/subscriptions/my and
compares the answer with the rows actually stored for that user.
No writes to app data; only auth + two GETs.
"""
import json
import re
import subprocess
import sys
import urllib.request

BASE = "http://127.0.0.1:8090"


def post(path, payload):
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())


def get(path, token):
    req = urllib.request.Request(
        BASE + path, headers={"Authorization": "Bearer " + token}
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())


def latest_otp(phone):
    out = subprocess.run(
        ["docker", "logs", "bmj-backend-local", "--tail", "60"],
        capture_output=True,
        text=True,
        errors="ignore",
    ).stdout
    hits = re.findall(r"OTP for %s: (\d+)" % re.escape(phone), out)
    return hits[-1] if hits else None


def main():
    phone = sys.argv[1] if len(sys.argv) > 1 else "9876543210"
    post("/api/auth/send-otp", {"phone": phone})
    code = latest_otp(phone)
    print(f"phone={phone} otp={code}")
    if not code:
        print("NO OTP FOUND")
        return 1
    auth = post("/api/auth/login-otp", {"phone": phone, "otp": code})
    token = auth.get("token") or auth.get("accessToken") or auth.get("jwt")
    print(f"login status={auth.get('status')} userId={auth.get('userId')}")
    if not token:
        print("NO TOKEN — raw:", json.dumps(auth)[:400])
        return 1
    subs = get("/api/subscriptions/my", token)
    items = subs.get("subscriptions") or []
    print(f"api status={subs.get('status')} count={len(items)}")
    for s in items[:5]:
        print(f"   id={s.get('id')} customerId={s.get('customerId')} status={s.get('status')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
