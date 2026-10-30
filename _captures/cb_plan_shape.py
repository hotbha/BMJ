"""Read-only: how the live catalog models sizes for plan (subscription) prices.

The one-time path needs one price per (product, size). Chargebee rejects a
second INR price on the same `charge` item, so this probe records the modelling
the site already uses for plans before any restructuring decision is taken.

Usage: python cb_plan_shape.py
"""

import sys

from chargebee_price_rollout import existing_prices


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:  # pragma: no cover
        pass

    prices = existing_prices().values()
    plans = [p for p in prices if p.get("item_type") == "plan"]
    print(f"plan prices: {len(plans)}")

    sample = sorted(p["id"] for p in plans if "200ml" in p["id"])[:15]
    print("sample 200ml plan price ids:")
    for price_id in sample:
        print(f"  {price_id}")

    items = sorted({p["item_id"] for p in plans if "200ml" in p["id"]})
    print(f"distinct items behind those ids: {len(items)}")
    for item_id in items[:15]:
        matching = sorted(p["id"] for p in plans if p["item_id"] == item_id)
        print(f"  {item_id}: {len(matching)} prices -> {matching[:6]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
