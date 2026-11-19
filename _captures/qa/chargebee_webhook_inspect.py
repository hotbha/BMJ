"""Inspect the live site's webhook endpoint configuration (read-only).

Prints structure only; any credential-shaped field is redacted before printing.
"""
import json
import sys

from chargebee_live_audit import get, load_env, paginate

SENSITIVE = ("password", "secret", "token", "auth", "credential", "key")


def redact(obj, depth=0):
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if any(s in k.lower() for s in SENSITIVE):
                out[k] = "<redacted present>" if v else v
            else:
                out[k] = redact(v, depth + 1)
        return out
    if isinstance(obj, list):
        return [redact(v, depth + 1) for v in obj[:5]]
    return obj


def main():
    load_env()

    status, body = get("/webhook_endpoints", {"limit": 100})
    print(f"GET /webhook_endpoints -> {status}")
    if status != 200 or not isinstance(body, dict):
        print(str(body)[:400])
        return 1

    print("top-level keys:", sorted(body.keys()))
    key = "list" if "list" in body else next(
        (k for k, v in body.items() if isinstance(v, list)), None)
    items = body.get(key, []) if key else []
    print(f"records: {len(items)}")
    if items:
        first = items[0]
        wrapper = first.get("webhook_endpoint", first) if isinstance(first, dict) else first
        print("\nfield names on a record:", sorted(wrapper.keys()))
        print("\nfirst record (credentials redacted):")
        print(json.dumps(redact(wrapper), indent=2)[:2500])

    # does the API describe signature support?
    for path in ("/webhook_endpoints/signature", "/webhook_endpoints/secret"):
        s, b = get(path, {"limit": 1})
        msg = ""
        if isinstance(b, dict):
            msg = b.get("message") or b.get("type") or ""
        print(f"\nGET {path} -> {s} {str(msg)[:120]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
