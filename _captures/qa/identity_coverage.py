"""Identity-link coverage: BMJ users vs live Chargebee customers (read-only)."""
import json
import sys

from chargebee_live_audit import ENV, get, load_env
import sub_census
from sub_census import q


def main():
    load_env()
    sub_census.load_env()
    status, body = get("/customers", {"limit": 100})
    cb_customers = []
    if status == 200 and isinstance(body, dict):
        cb_customers = [c.get("customer", {}) for c in body.get("list", [])]
    print(f"chargebee customers fetched: {len(cb_customers)}")

    rows = q("select id, username, ifnull(email,''), ifnull(chargebee_customer_id,'') from users")
    users = [{"id": r[0], "phone": r[1], "email": r[2], "link": r[3]} for r in rows]
    print(f"bmj users: {len(users)}")

    linked = [u for u in users if u["link"]]
    unlinked = [u for u in users if not u["link"]]
    print(f"linked: {len(linked)}   unlinked: {len(unlinked)}")

    # users who own subscription rows
    owned = q("select customer_id, count(*) from subscription_entity group by customer_id")
    owner_keys = {r[0] for r in owned}
    users_with_rows = []
    for u in users:
        if u["id"] in owner_keys:
            users_with_rows.append(u)
    reachable = [u for u in users_with_rows if u["link"] and u["link"] in {c.get("id") for c in cb_customers}]
    print(f"users owning subscription rows: {len(users_with_rows)}")
    print(f"  of which API-reachable: {len(reachable)}")

    # Chargebee customers that correspond to a BMJ user (phone or email)
    by_phone = {}
    for u in users:
        if u["phone"]:
            by_phone[u["phone"]] = u
    cb_matched = 0
    for c in cb_customers:
        if c.get("phone") in by_phone:
            cb_matched += 1
    print(f"chargebee customers matching a BMJ user phone: {cb_matched}")

    summary = {
        "chargebee_customers": len(cb_customers),
        "bmj_users": len(users),
        "linked": len(linked),
        "unlinked": len(unlinked),
        "users_owning_rows": len(users_with_rows),
        "users_reachable": len(reachable),
        "cb_customers_matched_by_phone": cb_matched,
        "unlinked_users": [{"id": u["id"], "phone": u["phone"]} for u in unlinked],
    }
    print(json.dumps(summary, indent=2))
    with open(r"X:\BMJ\_captures\qa\identity_coverage.json", "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
