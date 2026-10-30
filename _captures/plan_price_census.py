"""Census of subscription plan item prices on the Chargebee test site.

Read-only. The migration to catalog 2.0 checkout needs the real
`item_price_id` of every plan the app offers, so this prints the actual matrix
(category x size x cadence) instead of trusting the id naming convention:

    delight / signature / premium  x  200ml / 300ml / 500ml  x  day/week/month/year

Anything missing from the matrix is reported explicitly — a missing combination
is a catalog gap, not something the checkout code can paper over.

Usage
    python plan_price_census.py
    python plan_price_census.py --ids      # just the ids, one per line
"""

import json
import re
import sys

from mcp_call import AGENTS, _post

PAGE_LIMIT = 100
MAX_PAGES = 40

CATEGORIES = ("delight", "signature", "premium")
SIZES = ("200ml", "300ml", "500ml")
CADENCES = ("day", "week", "month", "year")


def fetch_prices():
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
                "clientInfo": {"name": "bmj-plan-census", "version": "1.0.0"},
            },
        },
    )
    if "error" in init:
        raise SystemExit(f"initialize failed: {init['error']}")

    prices = []
    offset = None
    for _ in range(MAX_PAGES):
        arguments = {"limit": PAGE_LIMIT}
        if offset:
            arguments["offset"] = offset
        response, _ = _post(
            url,
            key,
            {
                "jsonrpc": "2.0",
                "id": "page",
                "method": "tools/call",
                "params": {"name": "list_item_prices", "arguments": arguments},
            },
            session,
        )
        result = response.get("result", {})
        if result.get("isError"):
            raise SystemExit(f"list_item_prices failed: {result}")
        payload = json.loads(result["content"][0]["text"])
        prices.extend(entry["item_price"] for entry in payload.get("list", []))
        offset = payload.get("next_offset")
        if not offset:
            break
    return prices


def cadence_of(price):
    unit = (price.get("period_unit") or "").lower()
    return {"week": "week", "month": "month", "day": "day", "year": "year"}.get(unit, unit or "-")


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:  # pragma: no cover
        pass

    prices = [p for p in fetch_prices() if p.get("item_type") == "plan"]
    if "--ids" in sys.argv:
        for price in sorted(prices, key=lambda p: p["id"]):
            print(price["id"])
        return 0

    by_cadence = {}
    for price in prices:
        by_cadence[cadence_of(price)] = by_cadence.get(cadence_of(price), 0) + 1
    print("plan item prices by billing period: " + ", ".join(
        f"{unit}={count}" for unit, count in sorted(by_cadence.items())
    ))
    print(f"total plan item prices: {len(prices)}\n")

    # index: (category, size, cadence) -> id
    matrix = {}
    for price in prices:
        price_id = price["id"]
        match = re.match(
            r"^bmj-(delight|signature|premium)-.+?-(200ml|300ml|500ml)-(daily|weekly|monthly|yearly)$",
            price_id,
        )
        if not match:
            continue
        category, size, cadence = match.groups()
        cadence = {"daily": "day", "weekly": "week", "monthly": "month", "yearly": "year"}[cadence]
        matrix[(category, size, cadence)] = price

    print(f"{'category':<11}{'size':<8}" + "".join(f"{c:<10}" for c in CADENCES))
    for category in CATEGORIES:
        for size in SIZES:
            row = f"{category:<11}{size:<8}"
            for cadence in CADENCES:
                price = matrix.get((category, size, cadence))
                row += f"{'ok' if price else 'MISSING':<10}"
            print(row)

    print("\nresolved ids:")
    for key in sorted(matrix):
        price = matrix[key]
        print(
            f"  {price['id']:<48} INR {price['price'] / 100:>9.2f} "
            f"{price.get('period')} {price.get('period_unit'):<6} {price.get('status')}"
        )

    missing = [
        f"{category}-{size}-{cadence}"
        for category in CATEGORIES
        for size in SIZES
        for cadence in CADENCES
        if (category, size, cadence) not in matrix
    ]
    print(f"\nmissing combinations: {len(missing)}")
    for gap in missing:
        print(f"  {gap}")

    # ids that carry the bmj- prefix but no recognised size/cadence shape
    odd = sorted(p["id"] for p in prices
                 if p["id"].startswith("bmj-") and not any(p["id"] == m["id"] for m in matrix.values()))
    print(f"\nother bmj- plan prices (unrecognised shape): {len(odd)}")
    for price_id in odd[:20]:
        print(f"  {price_id}")
    if len(odd) > 20:
        print(f"  ... {len(odd) - 20} more")
    return 0


if __name__ == "__main__":
    sys.exit(main())
