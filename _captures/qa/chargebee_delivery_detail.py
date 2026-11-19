"""Dump the full webhook delivery record for the most recent event, read-only.

Shows every field Chargebee exposes about the delivery attempt (status, reason,
attempt times) so a failure can be diagnosed from Chargebee's own data.
"""
import json
import sys

from chargebee_live_audit import load_env
from chargebee_live_audit import get


def main():
    load_env()
    status, body = get("/events", {"limit": 5})
    if status != 200 or not isinstance(body, dict):
        print(f"GET /events -> {status}")
        return 1

    for wrap in body.get("list", []):
        e = wrap.get("event", {})
        hooks = e.get("webhooks") or []
        if not any(h.get("webhook_status") not in ("not_applicable", None) for h in hooks):
            continue
        print(f"event {e.get('id')} type={e.get('event_type')} occurred_at={e.get('occurred_at')}")
        for h in hooks:
            print(f"  webhook_id={h.get('id')}")
            print(f"    fields present: {sorted(h.keys())}")
            print(json.dumps(h, indent=2, default=str)[:1200])
        return 0

    print("no event in the sample had a delivery attempt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
