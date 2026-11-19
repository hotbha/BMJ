"""Full inventory of the site's webhook endpoints (read-only)."""
import json
import sys

from chargebee_live_audit import get, load_env


def main():
    load_env()
    status, body = get("/webhook_endpoints", {"limit": 100})
    if status != 200 or not isinstance(body, dict):
        print(f"status={status}")
        return 1

    items = body.get("list", [])
    print(f"webhook endpoints: {len(items)}\n")
    rows = []
    all_events = set()
    for it in items:
        ep = it.get("webhook_endpoint", it)
        events = ep.get("enabled_events", []) or []
        all_events.update(events)
        rows.append({
            "id": ep.get("id"),
            "name": ep.get("name"),
            "disabled": ep.get("disabled"),
            "primary_url": ep.get("primary_url"),
            "api_version": ep.get("api_version"),
            "url": ep.get("url"),
            "send_card_resource": ep.get("send_card_resource"),
            "enabled_events": events,
            "event_count": len(events),
        })

    for r in rows:
        print(f"- {r['name']}  [{r['id']}]")
        print(f"    url        : {r['url']}")
        print(f"    disabled   : {r['disabled']}   primary={r['primary_url']}  api={r['api_version']}")
        print(f"    events({r['event_count']}): {', '.join(r['enabled_events']) or '(none)'}")
        print()

    print("union of subscribed events:", len(all_events))
    for e in sorted(all_events):
        print("   ", e)

    enabled = [r for r in rows if not r["disabled"]]
    disabled = [r for r in rows if r["disabled"]]
    print(f"\nACTIVE endpoints: {len(enabled)}   DISABLED: {len(disabled)}")
    for r in enabled:
        print(f"   ACTIVE  -> {r['url']}")
    for r in disabled:
        print(f"   DISABLED-> {r['url']}")

    hosts = sorted({(r["url"] or "").split("//")[-1].split("/")[0] for r in rows if r["url"]})
    print("\ndistinct hosts:", hosts)
    return 0


if __name__ == "__main__":
    sys.exit(main())
