"""Read-only audit of the live Chargebee site.

Never prints the API key. Only GET requests: nothing is created, updated or deleted.
Writes a JSON summary next to this script for the audit document.
"""
import base64
import json
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

ENV = {}
OUT = r"X:\BMJ\_captures\qa\chargebee_live_audit.json"
MAX_PAGES = 60
PAGE_SIZE = 100


def load_env(path=r"X:\BMJ\.env"):
    with open(path, encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            ENV[k.strip()] = v.strip()
    return ENV


def site_base():
    site = ENV["CHARGEBEE_SITE"]
    return f"https://{site}.chargebee.com/api/v2"


def get(path, params=None, timeout=30):
    """GET a Chargebee API path. Returns (status, json_or_text)."""
    url = site_base() + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    token = base64.b64encode((ENV["CHARGEBEE_API_KEY"] + ":").encode()).decode()
    req = urllib.request.Request(url, headers={
        "Authorization": "Basic " + token,
        "Accept": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="ignore")
            return resp.status, json.loads(body) if body.strip() else {}
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, body[:300]
    except Exception as e:  # noqa: BLE001 - network failures are data here
        return -1, str(e)


def paginate(path):
    """Walk a list endpoint. Returns (records, pages, truncated, error)."""
    records, pages, offset, truncated = [], 0, None, False
    while True:
        params = {"limit": PAGE_SIZE}
        if offset:
            params["offset"] = offset
        status, body = get(path, params)
        if status != 200 or not isinstance(body, dict):
            return records, pages, truncated, f"status={status} body={str(body)[:200]}"
        pages += 1
        key = "list" if "list" in body else next(
            (k for k, v in body.items() if isinstance(v, list)), None)
        batch = body.get(key, []) if key else []
        records.extend(batch)
        offset = body.get("next_offset")
        if not offset:
            break
        if pages >= MAX_PAGES:
            truncated = True
            break
    return records, pages, truncated, None


def probe(path):
    status, body = get(path, {"limit": 1})
    detail = ""
    if isinstance(body, dict):
        detail = body.get("message") or body.get("error_msg") or body.get("type") or ""
    return {"path": path, "status": status, "detail": str(detail)[:120]}


def main():
    load_env()
    if not ENV.get("CHARGEBEE_SITE") or not ENV.get("CHARGEBEE_API_KEY"):
        print("missing CHARGEBEE_SITE / CHARGEBEE_API_KEY")
        return 1
    print(f"site={ENV['CHARGEBEE_SITE']} (api key loaded, not printed)")

    result = {"site": ENV["CHARGEBEE_SITE"]}

    # connectivity + account identity
    status, body = get("/customers", {"limit": 1})
    print(f"\n[customers probe] status={status}")
    if status != 200:
        print("cannot continue:", str(body)[:300])
        return 1

    # customers
    customers, pages, truncated, err = paginate("/customers")
    result["customers"] = {"count": len(customers), "pages": pages, "truncated": truncated, "error": err}
    print(f"[customers] count={len(customers)} pages={pages} truncated={truncated} err={err}")

    # subscriptions + status tally
    subs, pages_s, truncated_s, err_s = paginate("/subscriptions")
    tally = {}
    for s in subs:
        sub = s.get("subscription", {})
        st = sub.get("status", "UNKNOWN")
        tally[st] = tally.get(st, 0) + 1
    result["subscriptions"] = {"count": len(subs), "pages": pages_s,
                               "truncated": truncated_s, "error": err_s, "by_status": tally}
    print(f"[subscriptions] count={len(subs)} by_status={tally}")

    # items / plans (context for the site)
    items, _, _, err_i = paginate("/items")
    plans = [i for i in items if i.get("item", {}).get("type") == "plan"]
    result["items"] = {"count": len(items), "plans": len(plans), "error": err_i}
    print(f"[items] count={len(items)} plans={len(plans)}")

    # sample events (what the site actually emits)
    status_e, body_e = get("/events", {"limit": 20})
    event_types = []
    if status_e == 200 and isinstance(body_e, dict):
        for e in body_e.get("list", []):
            et = e.get("event", {}).get("event_type")
            if et:
                event_types.append(et)
    result["events_sample"] = {"status": status_e, "types": sorted(set(event_types)),
                               "sampled": len(event_types)}
    print(f"[events] status={status_e} distinct_types={sorted(set(event_types))}")

    # webhook configuration surface
    probes = [probe(p) for p in (
        "/webhooks",
        "/webhook_endpoints",
        "/webhook",
        "/settings/webhooks",
        "/integrations/webhooks",
    )]
    result["webhook_probes"] = probes
    print("\n[webhook endpoint probes]")
    for p in probes:
        print(f"   {p['path']:<24} status={p['status']} {p['detail']}")

    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2)
    print(f"\nwrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
