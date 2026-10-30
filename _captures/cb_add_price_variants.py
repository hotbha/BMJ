"""Prepare the 45-row payload for Chargebee Price Variants (approved Option A).

Chargebee stores only **one INR price per `charge` item** unless each price point
carries a distinct price variant, so every one-time row needs
`price_variant_id` before it can be created. This script adds it, derived from
the size token already present in the price id:

    bmj-item-bloody-red-300ml  ->  price_variant_id = bmj-300ml

Nothing else changes: the 45 prices stay on the same 15 `charge` items, so the
storefront contract (one product row, `prices[]` = 200/300/500 ml) is untouched.
See CHARGEBEE_PRICE_VARIANTS_MAPPING.md for the full mapping.

Idempotent: re-running rewrites nothing once every row carries the key.

Usage
    python cb_add_price_variants.py           # apply
    python cb_add_price_variants.py --check   # report only, exit 1 if not ready
"""

import io
import re
import sys

PAYLOAD = r"X:\BMJ\chargebee_items_payload.json"
ROW_PREFIX = '    {"id":"bmj-item-'
VARIANT_FOR_SIZE = {"200ml": "bmj-200ml", "300ml": "bmj-300ml", "500ml": "bmj-500ml"}
EXPECTED_ROWS = 45


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:  # pragma: no cover
        pass

    raw = io.open(PAYLOAD, encoding="utf-8", newline="").read()
    newline = "\r\n" if "\r\n" in raw else "\n"
    lines = raw.split(newline)

    changed = 0
    prepared = 0
    out = []
    for line in lines:
        if line.startswith(ROW_PREFIX) and '"pricing_model":"flat_fee"' in line:
            match = re.search(r'"id":"([^"]+)"', line)
            if not match:
                print(f"cannot read the id of: {line[:80]}")
                return 1
            price_id = match.group(1)
            size = price_id.rsplit("-", 1)[-1]
            variant = VARIANT_FOR_SIZE.get(size)
            if variant is None:
                print(f"{price_id}: no known size token ({size})")
                return 1
            if '"price_variant_id"' in line:
                prepared += 1
            else:
                line = line.replace(
                    '"currency_code":"INR",',
                    f'"currency_code":"INR","price_variant_id":"{variant}",',
                    1,
                )
                changed += 1
                prepared += 1
        out.append(line)

    if prepared != EXPECTED_ROWS:
        print(f"{prepared} price rows prepared, expected {EXPECTED_ROWS}")
        return 1

    if "--check" in sys.argv:
        state = "prepared" if changed == 0 else f"{changed} row(s) still to add"
        print(f"{prepared}/{EXPECTED_ROWS} rows carry price_variant_id — {state}")
        return 0 if changed == 0 else 1

    if changed:
        io.open(PAYLOAD, "w", encoding="utf-8", newline="").write(newline.join(out))
        print(f"{PAYLOAD}: added price_variant_id to {changed} row(s)")
    else:
        print(f"{PAYLOAD}: already prepared ({prepared} rows) — nothing written")

    for size, variant in VARIANT_FOR_SIZE.items():
        print(f"  {size:<6} -> {variant}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
