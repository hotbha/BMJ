"""Read-only dry run of the subscription identity migration.

Simulates Phase 3 in SQL (SELECT only, wrapped so nothing can be written) and
prints, for every affected customer, the before -> after key mapping plus the
exact rows that would move, move-as-noop, or stay put.
"""
import subprocess
import sys

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
        print("SQL ERROR:", out.stderr.strip()[:400], file=sys.stderr)
        return []
    return [ln.split("\t") for ln in out.stdout.splitlines() if ln.strip()]


def table(headers, rows):
    if not rows:
        print("   (none)")
        return
    widths = [max(len(str(h)), max(len(str(r[i])) for r in rows))
              for i, h in enumerate(headers)]
    print("   " + "  ".join(h.ljust(widths[i]) for i, h in enumerate(headers)))
    print("   " + "  ".join("-" * w for w in widths))
    for r in rows:
        print("   " + "  ".join(str(r[i]).ljust(widths[i]) for i in range(len(headers))))


def main():
    load_env()

    print("=" * 78)
    print("MIGRATION DRY RUN  (read-only - every statement is a SELECT)")
    print("=" * 78)

    cols = q("select column_name from information_schema.columns "
             "where table_schema=database() and table_name='subscription_entity' "
             "order by ordinal_position")
    names = [c[0] for c in cols]
    print(f"\n[0] subscription_entity columns ({len(names)}): {', '.join(names[:10])} ...")
    print(f"    'id' present for rollback join: {'YES' if 'id' in names else 'NO'}")

    rows = q("""
        select s.id, s.customer_id, s.status, ifnull(u.id,'-'), ifnull(u.username,'-'),
               ifnull(u.chargebee_customer_id,'(null)'),
               case when u.id is null then 'C: no owner'
                    when u.chargebee_customer_id is null or u.chargebee_customer_id='' then 'B: unmigratable'
                    when u.chargebee_customer_id = s.customer_id then 'A: no-op (same key)'
                    else 'A: re-key' end as cohort,
               case when u.id is null then '-'
                    when u.chargebee_customer_id is null or u.chargebee_customer_id='' then '-'
                    else u.chargebee_customer_id end as proposed,
               case when u.id is not null and u.chargebee_customer_id is not null and u.chargebee_customer_id<>''
                    then (select count(*) from customer_entity c where c.customer_id=u.chargebee_customer_id)
                    else 0 end as target_exists
        from subscription_entity s
        left join users u on s.customer_id = cast(u.id as char)
        order by s.customer_id, s.id
    """)
    print(f"\n[1] ALL {len(rows)} SUBSCRIPTION ROWS - before -> after")
    table(["sub id", "cur key", "status", "user", "phone", "cb id", "cohort", "proposed", "tgt"],
          rows)

    print("\n[2] PER-CUSTOMER IMPACT")
    per = {}
    for r in rows:
        per.setdefault((r[1], r[6], r[7]), []).append(r)
    summ = []
    for (cur, cohort, proposed), items in sorted(per.items()):
        summ.append([cur, len(items), sum(1 for i in items if i[2] == "ACTIVE"),
                     cohort, proposed])
    table(["current key", "rows", "active", "cohort", "proposed key"], summ)

    movable = [r for r in rows if r[6] == "A: re-key"]
    noop = [r for r in rows if r[6] == "A: no-op (same key)"]
    stuck_b = [r for r in rows if r[6] == "B: unmigratable"]
    stuck_c = [r for r in rows if r[6] == "C: no owner"]
    print(f"\n[3] PHASE 3 EFFECT: {len(movable)} rows updated, {len(noop)} no-op, "
          f"{len(stuck_b)} blocked (B), {len(stuck_c)} blocked (C)")
    print(f"    active rows that become visible to an owner: "
          f"{sum(1 for r in movable if r[2] == 'ACTIVE')}")

    bad = q("""
        select u.id, u.chargebee_customer_id
        from users u
        left join customer_entity c on c.customer_id = u.chargebee_customer_id
        where u.chargebee_customer_id is not null and u.chargebee_customer_id <> ''
          and c.customer_id is null
    """)
    print(f"\n[4] FK GATE (Phase 1c): users whose target customer row is missing: {len(bad)}")
    if bad:
        table(["user", "chargebee id"], bad)
    else:
        print("   (none) -> gate PASSES")

    print("\n[5] IDENTITY TWIN CHECK - same person on both keys?")
    twins = q("""
        select u.id, u.username,
               ifnull((select phone from customer_entity c where c.customer_id = cast(u.id as char)),'-'),
               u.chargebee_customer_id,
               ifnull((select phone from customer_entity c where c.customer_id = u.chargebee_customer_id),'-')
        from users u
        where u.chargebee_customer_id is not null and u.chargebee_customer_id <> ''
          and u.chargebee_customer_id not regexp '^[0-9]+$'
    """)
    table(["user", "login phone", "numeric twin phone", "chargebee id", "cb twin phone"], twins)

    print("\n[6] POST-STATE (projected, not applied)")
    proj = q("""
        select
          (select count(*) from subscription_entity s join users u on s.customer_id=cast(u.id as char)
             where u.chargebee_customer_id is not null and u.chargebee_customer_id<>''
               and u.chargebee_customer_id <> s.customer_id),
          (select count(*) from subscription_entity s join users u on s.customer_id=cast(u.id as char)
             where u.chargebee_customer_id is not null and u.chargebee_customer_id<>''
               and u.chargebee_customer_id <> s.customer_id and s.status='ACTIVE'),
          (select count(*) from subscription_entity s left join users u on s.customer_id=cast(u.id as char)
             where u.id is null)
    """)
    if proj:
        print(f"   rows that would move ......... {proj[0][0]}")
        print(f"   of which ACTIVE .............. {proj[0][1]}")
        print(f"   ownerless rows (quarantine) .. {proj[0][2]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
