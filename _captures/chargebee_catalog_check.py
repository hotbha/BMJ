"""Chargebee → catalog sanity check for the test site.

Pulls every item price from the Chargebee test account through the data-lookup
MCP and reports the shape the app depends on:

* how many `charge` prices (per-bottle, the PDP / cart path) vs `plan` prices
  (weekly/monthly subscriptions) exist,
* the INR range of each, and any price that is zero or negative (the app must
  never render those),
* the exact per-200ml charge price for the juices used in the capture harness,
  so a UI capture can be compared against Chargebee.

Usage: python chargebee_catalog_check.py
"""

import json
import sys

from mcp_call import AGENTS, _post

PAGE_LIMIT = 100
MAX_PAGES = 30

# 200ml charge items the Flutter catalog/PDP shows first (cheapest size).
WATCHED = [
    "bmj-delight-pineapple-200ml",
    "bmj-signature-abc-200ml",
    "bmj-premium-carrot-200ml",
]


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
                "clientInfo": {"name": "bmj-catalog-check", "version": "1.0.0"},
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


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:  # pragma: no cover
        pass

    prices = fetch_prices()
    print(f"{len(prices)} item price(s) on the test site\n")

    by_type = {}
    for price in prices:
        by_type.setdefault(price.get("item_type"), []).append(price)

    for item_type, entries in sorted(by_type.items()):
        rupees = [entry["price"] / 100 for entry in entries]
        print(
            f"{item_type:<8} count={len(entries):<5} "
            f"min=₹{min(rupees):.0f} max=₹{max(rupees):.0f}"
        )

    bad = [p for p in prices if not p.get("price") or p["price"] <= 0]
    print(f"\nzero/negative prices: {len(bad)}")

    inr = [p for p in prices if p.get("currency_code") != "INR"]
    print(f"non-INR prices: {len(inr)}")

    print("\nper-bottle charge prices for the capture juices:")
    for price in sorted(prices, key=lambda p: (p.get("item_id") or "", p.get("name") or "")):
        item_id = price.get("item_id") or ""
        if price.get("item_type") != "charge":
            continue
        if not any(item_id.startswith(prefix) for prefix in WATCHED):
            continue
        print(
            f"  {price['id']:<44} {price['price_formatted']:<14} "
            f"{price.get('period')} {price.get('period_unit')}"
        )

    print("\nall charge (one-time) prices:")
    for price in sorted(
        (p for p in prices if p.get("item_type") == "charge"),
        key=lambda p: p.get("id") or "",
    ):
        print(
            f"  {price['id']:<46} {price['price_formatted']:<13} "
            f"{price.get('period')} {str(price.get('period_unit') or '-'):<6} "
            f"{(price.get('item_id') or '')}"
        )

    periods = {}
    for price in prices:
        if price.get("item_type") != "plan":
            continue
        periods[price.get("period_unit")] = periods.get(price.get("period_unit"), 0) + 1
    print("\nplan prices by period unit: " + ", ".join(
        f"{unit}={count}" for unit, count in sorted(periods.items())
    ))

    print("\n200ml plan prices (sample):")
    sample = [
        p for p in prices
        if p.get("item_type") == "plan" and "200ml" in (p.get("id") or "")
    ]
    sample.sort(key=lambda p: p.get("id") or "")
    for price in sample[:8]:
        print(
            f"  {price['id']:<46} {price['price_formatted']:<13} "
            f"{price.get('period')} {price.get('period_unit')}"
        )
    print(f"  ... {len(sample)} 200ml plan prices in total")

    return 0


if __name__ == "__main__":
    sys.exit(main())
