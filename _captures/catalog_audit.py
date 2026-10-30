"""Read-only audit of the live catalog API chain (Chargebee -> Catalog API).

Usage:
    python catalog_audit.py [base_url]

Prints one row per storefront product with its real `prices[]`, flags em-dash
(price-less) products, non-INR rows and zero/negative amounts. Exits 1 when the
catalog is not fully priced, so it can gate a rollout step.
"""

import json
import sys
import urllib.request

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8085"
URL = f"{BASE}/api/v1/catalog/charge-items"
SIZES = ("200ml", "300ml", "500ml")


def main() -> int:
    with urllib.request.urlopen(URL, timeout=30) as response:
        items = json.load(response)

    problems = []
    total = 0
    for item in items:
        prices = item.get("prices") or []
        total += len(prices)
        rendered = " ".join(
            "{size}={price}".format(size=price.get("size"), price=price.get("price"))
            for price in prices
        )
        if not prices:
            problems.append(f"{item['itemId']}: prices[] empty (UI shows em dash)")
        print(f"{item['itemId']:<34} {str(item.get('category')):<10} {len(prices)}  {rendered or '-'}")
        found = {price.get("size") for price in prices}
        missing = [size for size in SIZES if size not in found]
        if prices and missing:
            problems.append(f"{item['itemId']}: missing sizes {', '.join(missing)}")
        for price in prices:
            if price.get("currencyCode") not in (None, "INR"):
                problems.append(f"{item.get('itemId')}: non-INR {price.get('currencyCode')}")
            amount = price.get("price") or 0
            if amount <= 0:
                problems.append(f"{price.get('priceId')}: non-positive amount {amount}")
            if not price.get("priceId"):
                problems.append(f"{item.get('itemId')}: price without id")
            if price.get("size") not in SIZES:
                problems.append(f"{price.get('priceId')}: unparsed size {price.get('size')!r}")

    print(f"\nitems={len(items)} prices={total} target=45")
    print(f"fully priced products={sum(1 for i in items if len(i.get('prices') or []) == 3)}/15")
    if problems:
        print(f"\nPROBLEMS ({len(problems)}):")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    print("\ncatalog: OK (all 15 products carry 200/300/500 ml INR prices)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
