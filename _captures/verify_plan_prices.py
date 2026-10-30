"""Prove the subscription plan item prices the migration depends on exist.

Read-only. Queries the Chargebee test site through the data-lookup MCP and
asserts, for every id given on the command line (default: the weekly + monthly
plan used for the hosted-page validation), that:

* the item price exists and can be retrieved by id (retrieve_item_price),
* item_type == "plan"   (catalog 2.0 recurring item, not a one-off charge),
* status == "active"    (an archived price cannot be checked out),
* price > 0 and currency == INR,
* period/period_unit match the plan cadence the id claims.

Usage
    python verify_plan_prices.py
    python verify_plan_prices.py bmj-delight-mix-punch-200ml-weekly ...
"""

import json
import sys

from mcp_call import AGENTS, _post

DEFAULT_IDS = [
    "bmj-delight-mix-punch-200ml-weekly",
    "bmj-delight-mix-punch-200ml-monthly",
]

# id suffix -> (period, period_unit) the plan cadence must match
CADENCE = {"weekly": (1, "week"), "monthly": (1, "month"), "yearly": (1, "year")}


def call(tool, arguments):
    url, key = AGENTS["data"]
    init, session = _post(
        url,
        key,
        {
            "jsonrpc": "2.0",
            "id": "init",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "bmj-plan-check", "version": "1.0.0"},
            },
        },
    )
    if "error" in init:
        raise SystemExit(f"initialize failed: {init['error']}")
    response, _ = _post(
        url,
        key,
        {
            "jsonrpc": "2.0",
            "id": tool,
            "method": "tools/call",
            "params": {"name": tool, "arguments": arguments},
        },
        session,
    )
    result = response.get("result", {})
    if result.get("isError"):
        return None, result
    return json.loads(result["content"][0]["text"]), None


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:  # pragma: no cover
        pass

    wanted = sys.argv[1:] or DEFAULT_IDS
    failures = 0

    for item_price_id in wanted:
        payload, error = call("retrieve_item_price", {"item_price_id": item_price_id})
        if error:
            print(f"FAIL {item_price_id}: not retrievable -> {error}")
            failures += 1
            continue

        price = payload.get("item_price", payload)
        item_type = price.get("item_type")
        status = price.get("status")
        amount = price.get("price") or 0
        currency = price.get("currency_code")
        period = price.get("period")
        period_unit = price.get("period_unit")

        problems = []
        if item_type != "plan":
            problems.append(f"item_type={item_type} (expected plan)")
        if status != "active":
            problems.append(f"status={status} (expected active)")
        if amount <= 0:
            problems.append(f"price={amount} (must be > 0)")
        if currency != "INR":
            problems.append(f"currency={currency} (expected INR)")

        for suffix, expected in CADENCE.items():
            if item_price_id.endswith(suffix) and (period, period_unit) != expected:
                problems.append(f"cadence={period} {period_unit} (expected {expected[0]} {expected[1]})")

        state = "OK  " if not problems else "FAIL"
        if problems:
            failures += 1
        print(
            f"{state} {item_price_id:<44} {currency} {amount / 100:>9.2f} "
            f"{period} {period_unit}  item_type={item_type} status={status}"
        )
        for problem in problems:
            print(f"       - {problem}")
        if price.get("item_id"):
            print(f"       item_id={price['item_id']}  name={price.get('name')!r}")

    print(f"\n{len(wanted) - failures}/{len(wanted)} plan price(s) verified")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
