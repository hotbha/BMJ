#!/usr/bin/env python3
"""
BookMyJuice E2E Preflight Checker
Implements Phase 0 checks — human checklist + automated environment validation.
Exit code 0 = all checks passed, 1 = any failure.
"""
import os
import sys
import json
import base64
import subprocess
import urllib.request
import urllib.error


def print_header(title: str):
    print(f"\n{'=' * 60}")
    print(f" {title}")
    print(f"{'=' * 60}")


def print_fail(message: str):
    print(f"  ❌ {message}")


def print_pass(message: str):
    print(f"  ✅ {message}")


def check_url(url: str, timeout: int = 10) -> bool:
    try:
        req = urllib.request.Request(url, method='GET')
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status == 200
    except Exception:
        return False


def human_checklist() -> None:
    """Print human checklist and wait for confirmation."""
    checklist = """
╔══════════════════════════════════════════╗
║   HUMAN ACTIONS REQUIRED BEFORE START   ║
╠══════════════════════════════════════════╣
║                                          ║
║  1. DEVICE                               ║
║     Connect Android phone via USB        ║
║     Enable USB Debugging:                ║
║       Settings → Developer Options       ║
║       → USB Debugging ON                 ║
║     Run: adb devices                     ║
║     Confirm device appears (not empty)   ║
║                                          ║
║  2. SERVER                               ║
║     Start bmjServer:                     ║
║       cd bmjServer                       ║
║       mvn spring-boot:run                ║
║     Confirm: "Started Application" log   ║
║     Note your machine's local IP:        ║
║       Windows:     ipconfig              ║
║     Update appium_test/.env:             ║
║       BMJ_SERVER_URL=http://192.168.x.x:8080 ║
║     Confirm phone + server on same WiFi  ║
║                                          ║
║  3. TEST ACCOUNT                         ║
║     Ensure this account exists in        ║
║     Firebase Auth (TEST project):        ║
║       Email:    tester@bookmyjuice.com   ║
║       Password: Test@1234                ║
║     If not: create it manually in        ║
║     Firebase Console → Authentication    ║
║                                          ║
║  4. CHARGEBEE TEST SITE                  ║
║     Confirm TEST site is active:         ║
║       bookmyjuice-test.chargebee.com     ║
║     Confirm at least 1 active plan       ║
║     exists (subscription test needs it)  ║
║                                          ║
║  5. NOTIFICATIONS PERMISSION             ║
║     On the phone:                        ║
║       Settings → Apps → BookMyJuice      ║
║       → Notifications → Allow ALL        ║
║                                          ║
║  6. APK INSTALLED                        ║
║     Run:                                 ║
║       cd lush                            ║
║       flutter build apk --debug          ║
║       adb install -r build/app/outputs/  ║
║         apk/debug/app-debug.apk          ║
║     Confirm app icon appears on phone    ║
║                                          ║
╠══════════════════════════════════════════╣
║  Type YES and press Enter when ALL       ║
║  6 items above are confirmed.            ║
╚══════════════════════════════════════════╝
"""
    print(checklist)
    response = input("All checklist items confirmed? (YES): ").strip()
    if response != "YES":
        print("\nChecklist not confirmed. Exiting.")
        print("Run preflight again after completing all items.")
        sys.exit(1)
    print("  ✅ Human checklist confirmed.\n")


def check_appium_server() -> bool:
    print_header("Check 1 — Appium Server")
    print("  Checking http://127.0.0.1:4723/status ...")
    try:
        req = urllib.request.Request('http://127.0.0.1:4723/status', method='GET')
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            if data.get('value', {}).get('ready'):
                print_pass("Appium server is ready.")
                return True
            else:
                print_fail("Appium server not ready.")
    except Exception as e:
        print_fail(f"Appium server unreachable: {e}")
    print("\n  Fix: Run in a separate terminal: appium --port 4723")
    print("  Then re-run this script.")
    return False


def check_device_connected() -> bool:
    print_header("Check 2 — Device Connected")
    try:
        result = subprocess.run(
            ['adb', 'devices'],
            capture_output=True, text=True, timeout=10
        )
        lines = [l for l in result.stdout.strip().split('\n') if l and 'List of devices' not in l]
        if lines and 'device' in lines[0] and 'offline' not in lines[0]:
            device_id = lines[0].split('\t')[0]
            print_pass(f"Device connected: {device_id}")
            return True
        elif any('offline' in l for l in lines):
            print_fail("Device found but OFFLINE. Unlock phone and check USB Debugging.")
        else:
            print_fail("No device found.")
    except FileNotFoundError:
        print_fail("adb not found. Install Android SDK platform-tools.")
    except Exception as e:
        print_fail(f"adb error: {e}")
    print("\n  Fix: Check USB cable and USB Debugging setting. Run: adb devices")
    return False


def check_bmj_server_reachable() -> bool:
    from config.test_config import TestConfig
    print_header("Check 3 — bmjServer Reachable (from machine)")
    server_url = TestConfig.SERVER_URL
    print(f"  Checking {server_url}/api/products ...")
    try:
        req = urllib.request.Request(f"{server_url}/api/products", method='GET')
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status == 200:
                print_pass(f"bmjServer reachable at {server_url}")
                return True
    except Exception as e:
        print_fail(f"bmjServer not reachable: {e}")
    print(f"\n  Fix: Confirm mvn spring-boot:run is running in bmjServer/")
    print(f"       Server URL: {server_url}")
    return False


def check_bmj_server_from_device() -> bool:
    from config.test_config import TestConfig
    print_header("Check 4 — bmjServer Reachable (from device)")
    server_url = TestConfig.SERVER_URL
    print(f"  Checking device can reach {server_url} ...")
    # Try curl on device first, then wget
    for cmd in [
        ['adb', 'shell', f'curl -s -o /dev/null -w "%{{http_code}}" --max-time 5 {server_url}/api/products'],
        ['adb', 'shell', f'wget -O- -q --timeout=5 {server_url}/api/products 2>/dev/null || echo FAIL'],
    ]:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            output = result.stdout.strip()
            if '200' in output or ('{' in output or '[' in output):
                print_pass("Device can reach bmjServer.")
                return True
        except Exception:
            continue
    print_fail("Phone cannot reach server.")
    print("\n  Fix: Confirm both phone and machine are on the same WiFi network.")
    print(f"       Server IP configured as: {server_url}")
    return False


def check_app_installed() -> bool:
    print_header("Check 5 — App Installed")
    try:
        result = subprocess.run(
            ['adb', 'shell', 'pm', 'list', 'packages', '|', 'grep', 'bookmyjuice'],
            capture_output=True, text=True, timeout=10, shell=True
        )
        if 'com.bookmyjuice.lush' in result.stdout:
            print_pass("App is installed.")
            return True
        # Try without shell
        result = subprocess.run(
            ['adb', 'shell', 'pm', 'list', 'packages', 'bookmyjuice'],
            capture_output=True, text=True, timeout=10
        )
        if 'com.bookmyjuice.lush' in result.stdout:
            print_pass("App is installed.")
            return True
    except Exception as e:
        print_fail(f"Check failed: {e}")
    print_fail("App not installed.")
    print("\n  Fix: Run:")
    print("       cd lush")
    print("       flutter build apk --debug")
    print("       adb install -r build/app/outputs/apk/debug/app-debug.apk")
    return False


def check_firebase_reachable() -> bool:
    from config.test_config import TestConfig
    print_header("Check 6 — Firebase Reachable")
    api_key = TestConfig.FIREBASE_API_KEY
    if not api_key:
        print_fail("FIREBASE_WEB_API_KEY not configured.")
        return False
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
    payload = json.dumps({
        "email": TestConfig.TEST_EMAIL,
        "password": TestConfig.TEST_PASSWORD,
        "returnSecureToken": True
    }).encode()
    try:
        req = urllib.request.Request(url, data=payload, method='POST')
        req.add_header('Content-Type', 'application/json')
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            if 'idToken' in data:
                print_pass("Firebase Auth reachable, test account verified.")
                return True
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        if 'EMAIL_NOT_FOUND' in body or 'INVALID_LOGIN_CREDENTIALS' in body:
            print_fail("Test account credentials invalid.")
        else:
            print_fail(f"Firebase error: {body[:200]}")
    except Exception as e:
        print_fail(f"Firebase unreachable: {e}")
    print("\n  Fix: Create test account in Firebase Console → Authentication")
    print(f"       Email: {TestConfig.TEST_EMAIL}")
    print(f"       Password: {TestConfig.TEST_PASSWORD}")
    return False


def check_chargebee_reachable() -> bool:
    from config.test_config import TestConfig
    print_header("Check 7 — Chargebee TEST Site Reachable")
    api_key = TestConfig.CHARGEBEE_API_KEY
    if not api_key:
        print_fail("CHARGEBEE_TEST_API_KEY not configured.")
        return False
    auth_str = base64.b64encode(f"{api_key}:".encode()).decode()
    url = f"https://{TestConfig.CHARGEBEE_SITE}.chargebee.com/api/v2/plans"
    try:
        req = urllib.request.Request(url, method='GET')
        req.add_header('Authorization', f'Basic {auth_str}')
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            if 'list' in data:
                plan_count = len(data['list'])
                print_pass(f"Chargebee TEST reachable. Plans found: {plan_count}")
                if plan_count == 0:
                    print("  ⚠️  No plans found — subscription tests may fail.")
                return True
    except Exception as e:
        print_fail(f"Chargebee unreachable: {e}")
    print("\n  Fix: Check CHARGEBEE_TEST_API_KEY in .env")
    print(f"       Site: {TestConfig.CHARGEBEE_SITE}.chargebee.com")
    return False


def main():
    print("╔═══════════════════════════════════════════╗")
    print("║   BookMyJuice E2E — Preflight Checker    ║")
    print("╚═══════════════════════════════════════════╝")

    # Phase 0a: Human checklist
    human_checklist()

    # Phase 0b: Automated checks
    checks = [
        ("Appium Server", check_appium_server),
        ("Device Connected", check_device_connected),
        ("bmjServer (machine)", check_bmj_server_reachable),
        ("bmjServer (device)", check_bmj_server_from_device),
        ("App Installed", check_app_installed),
        ("Firebase Reachable", check_firebase_reachable),
        ("Chargebee Reachable", check_chargebee_reachable),
    ]

    failures = []
    for name, check_fn in checks:
        if not check_fn():
            failures.append(name)

    print("\n" + "=" * 60)
    if failures:
        print(f" ❌ FAILED CHECKS: {', '.join(failures)}")
        print("    Fix the issues above and re-run preflight.py")
        sys.exit(1)
    else:
        print(" ✅ All environment checks passed.")
        print("    Starting E2E test suite...")
        sys.exit(0)


if __name__ == '__main__':
    main()