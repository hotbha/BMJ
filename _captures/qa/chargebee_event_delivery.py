"""Webhook delivery + retry evidence from the live events API (read-only)."""
import json
import sys

from chargebee_live_audit import get, load_env


def main():
    load_env()
    status, body = get("/events", {"limit": 30})
    print(f"GET /events -> {status}")
    if status != 200 or not isinstance(body, dict):
        print(str(body)[:300])
        return 1

    rows = []
    for wrap in body.get("list", []):
        e = wrap.get("event", {})
        hooks = e.get("webhooks") or []
        rows.append({
            "id": e.get("id"),
            "type": e.get("event_type"),
            "occurred_at": e.get("occurred_at"),
            "webhooks": [{"id": w.get("id"), "status": w.get("webhook_status"),
                          "reason": w.get("webhook_failure_reason")} for w in hooks],
        })

    print(f"events sampled: {len(rows)}")
    with_hooks = [r for r in rows if r["webhooks"]]
    print(f"events carrying delivery records: {len(with_hooks)}")
    for r in rows[:12]:
        hook_desc = ", ".join(f"{h['status']}({h['reason'] or '-'})" for h in r["webhooks"]) or "no delivery record"
        print(f"  {r['type']:<34} {r['occurred_at']}  -> {hook_desc}")

    statuses = {}
    for r in with_hooks:
        for h in r["webhooks"]:
            statuses[h["status"]] = statuses.get(h["status"], 0) + 1
    print("\ndelivery status tally:", statuses or "(none recorded)")

    with open(r"X:\BMJ\_captures\qa\chargebee_event_delivery.json", "w", encoding="utf-8") as fh:
        json.dump(rows, fh, indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
