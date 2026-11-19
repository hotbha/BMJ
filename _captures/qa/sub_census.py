"""Subscription identity census (read-only).

Classifies every subscription row by the id space its customer_id belongs to,
then simulates SubscriptionController.getCustomerIdFromSecurityContext() to
count users who own subscriptions the API cannot reach.

Read-only: SELECTs only. No writes, no DDL.
"""
import subprocess
import sys
from collections import Counter, defaultdict

CONTAINER = "bmj-smoke-mysql"
ENV = {}


def load_env(path=r"X:\BMJ\.env"):
    with open(path, encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            ENV[k.strip()] = v.strip()
    return ENV


def q(sql):
    cmd = [
        "docker", "exec", "-i", CONTAINER, "mysql",
        "-u", ENV["DB_USERNAME"], "-p" + ENV["DB_PASSWORD"],
        ENV["DB_NAME"], "-N", "-B", "-e", sql,
    ]
    out = subprocess.run(cmd, capture_output=True, text=True, errors="ignore")
    if out.returncode != 0 and "Warning" not in out.stderr:
        print("SQL failed:", out.stderr[:300], file=sys.stderr)
        return []
    rows = []
    for line in out.stdout.splitlines():
        if not line.strip():
            continue
        rows.append(line.split("\t"))
    return rows


def num(v):
    """mysql -B prints SQL NULL as the literal 'NULL'."""
    try:
        return int(v)
    except (TypeError, ValueError):
        return 0


def main():
    load_env()

    total = int(q("select count(*) from subscription_entity")[0][0])
    by_status = q("select status, count(*) from subscription_entity group by status order by 2 desc")
    rows_by_cid = q(
        "select customer_id, count(*), sum(status='ACTIVE') "
        "from subscription_entity group by customer_id order by 2 desc"
    )
    users = q("select id, username, ifnull(chargebee_customer_id,'') from users order by id")
    customers = {r[0] for r in q("select customer_id from customer_entity")}
    user_ids = {r[0] for r in users}

    local_rows, cb_rows, orphan_rows, both_rows = 0, 0, 0, 0
    orphan_rows_customer = 0
    orphans = []
    for cid, n, active in rows_by_cid:
        n = int(n)
        in_local = cid in user_ids
        in_cb = cid in customers
        numeric = cid.isdigit()
        if in_local and in_cb:
            both_rows += n          # numeric key that is BOTH a user id and a customer id
        elif in_local:
            local_rows += n
        elif in_cb and numeric:
            orphan_rows_customer += n  # numeric customer record with no owning user
        elif in_cb:
            cb_rows += n
        else:
            orphan_rows += n
            orphans.append((cid, n, active))

    # Simulate the resolver per user.
    affected, healthy, no_rows = [], [], []
    for uid, phone, cb in users:
        owned = q(f"select count(*), sum(status='ACTIVE') from subscription_entity "
                  f"where customer_id='{uid}'")
        owned_n = num(owned[0][0]) if owned else 0
        owned_active = num(owned[0][1]) if owned else 0
        if owned_n == 0:
            no_rows.append((uid, phone, cb, 0, 0))
            continue
        # resolver: chargebee id if set, else customer_entity row keyed by local id
        if cb:
            key = cb
            how = "users.chargebee_customer_id"
        elif str(uid) in customers:
            key = str(uid)
            how = "customer_entity fallback"
        else:
            key = None
            how = "none (returns null)"
        reachable = 0
        if key:
            got = q(f"select count(*) from subscription_entity where customer_id='{key}'")
            reachable = num(got[0][0]) if got else 0
        rec = (uid, phone, cb or "(null)", owned_n, owned_active, key or "(null)", how, reachable)
        (healthy if reachable else affected).append(rec)

    print("=" * 72)
    print("SUBSCRIPTION IDENTITY CENSUS")
    print("=" * 72)
    print(f"total subscription rows ............ {total}")
    for st, n in by_status:
        print(f"   status {st:<12} ............... {n}")
    print()
    print(f"rows keyed by LOCAL user id only ..... {local_rows}")
    print(f"rows keyed by CHARGEBEE id only ..... {cb_rows}")
    print(f"rows on a DUAL-SPACE numeric key .. {both_rows}")
    print(f"rows on a customer with no user . {orphan_rows_customer}")
    print(f"rows keyed by NEITHER (true orphan) {orphan_rows}")
    print(f"distinct customer_id values ........ {len(rows_by_cid)}")
    print()
    print(f"users with subscription rows ....... {len(healthy) + len(affected)}")
    print(f"AFFECTED (own rows, API returns 0) . {len(affected)}")
    print(f"HEALTHY  (own rows, API returns n) . {len(healthy)}")
    print(f"users with no rows (correct empty) . {len(no_rows)}")
    print()
    print("--- affected users: has subscription, API says none ---")
    if affected:
        print(f"{'user':>5} {'phone':<12} {'cb id':<20} {'rows':>4} {'active':>6} "
              f"{'resolver key':<20} {'via':<26} {'reachable':>9}")
        for r in affected:
            print(f"{r[0]:>5} {r[1]:<12} {r[2]:<20} {r[3]:>4} {r[4]:>6} "
                  f"{r[5]:<20} {r[6]:<26} {r[7]:>9}")
    else:
        print("   (none)")
    print()
    print("--- healthy users (for contrast) ---")
    for r in healthy:
        print(f"{r[0]:>5} {r[1]:<12} {r[2]:<20} rows={r[3]:<3} active={r[4]:<3} "
              f"key={r[5]:<20} reachable={r[7]}")
    if orphans:
        print()
        print("--- orphan customer_ids (no matching user, no matching customer) ---")
        for cid, n, active in orphans:
            print(f"   {cid:<24} rows={n:<3} active={active}")
    return 0


if __name__ == "__main__":
    sys.exit(main())



