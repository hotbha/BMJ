"""Read-only probe: are Chargebee price variants available on this site?

Variant pricing is the only way to hold more than one INR price point on a
single `charge` item (see CHARGEBEE_CANARY_EXECUTION.md §3 and the Chargebee
docs agent run on 2026-10-29), so the rollout needs to know whether variants
already exist before any further price is created.

Usage: python cb_variants.py
"""

import json
import sys

from chargebee_price_rollout import Mcp


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:  # pragma: no cover
        pass

    data = Mcp("data")
    for tool, arguments in (
        ("list_price_variants", {"limit": 100}),
        ("list_product_variants", {"limit": 100}),
    ):
        try:
            payload = data.call(tool, arguments)
        except Exception as error:  # noqa: BLE001 - probe reports, never raises
            print(f"{tool}: ERROR {error}")
            continue
        print(f"{tool}: {json.dumps(payload)[:1500]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
