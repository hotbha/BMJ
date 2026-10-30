"""Create the 45 approved one-time (charge) item prices in Chargebee test.

Implements the approved rollout process from CHARGEBEE_EXECUTION_PLAN.md §6 and
CHARGEBEE_CANARY_EXECUTION.md, using the granular `create_an_item_price` tool
that the onboarding MCP now exposes (the plan was written when the only write
tool was the non-transactional bulk import):

    canary (1 row)  ->  delight (15)  ->  signature (15)  ->  premium (14)

Every step is: read back -> assert -> continue or stop. No step runs on an
unverified predecessor, and a row that already exists is never touched.

Usage
    python chargebee_price_rollout.py plan          # validate payload, print
    python chargebee_price_rollout.py preflight     # is variant pricing ready?
    python chargebee_price_rollout.py canary
    python chargebee_price_rollout.py batch delight
    python chargebee_price_rollout.py batch signature
    python chargebee_price_rollout.py batch premium
    python chargebee_price_rollout.py verify
    python chargebee_price_rollout.py census

Payload shape (9 keys): id, name, description, pricing_model, item_id, price,
currency_code, price_variant_id, is_taxable. `price_variant_id` is what makes a
second INR price on the same `charge` item legal (bmj-200ml / bmj-300ml /
bmj-500ml) — see CHARGEBEE_PRICE_VARIANTS_MAPPING.md. `item_family_id` is
deliberately not sent (C-6: derived from item_id), and period/trial/tiers are
removed (C-1..C-3: recurring-only fields, the suspected cause of the 2026-05-28
silent skip).

`preflight` is the gate for the variant rollout: it proves price variants are
enabled on the site and that the three required variants exist, before any price
is written.
"""

import json
import sys
import uuid

from mcp_call import AGENTS, _post

PAYLOAD_SOURCE = r"X:\BMJ\chargebee_items_payload.json"
CANARY_ID = "bmj-item-bloody-red-200ml"
SIZES = ("200ml", "300ml", "500ml")
# size -> the Chargebee price variant that owns that price point
VARIANTS = {"200ml": "bmj-200ml", "300ml": "bmj-300ml", "500ml": "bmj-500ml"}
ALLOWED_KEYS = {
    "id",
    "name",
    "description",
    "pricing_model",
    "item_id",
    "price",
    "currency_code",
    "price_variant_id",
    "is_taxable",
}
FORBIDDEN_KEYS = ("period", "period_unit", "trial_period", "trial_period_unit", "tiers")
FAMILIES = ("delight", "signature", "premium")


# --------------------------------------------------------------------------- MCP


class Mcp:
    """One MCP session per agent, reused across calls."""

    def __init__(self, agent):
        self.agent = agent
        self.url, self.key = AGENTS[agent]
        _, self.session = self._post(
            {
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "bmj-price-rollout", "version": "1.0.0"},
                },
            }
        )

    def _post(self, payload):
        return _post(self.url, self.key, payload, getattr(self, "session", None))

    def call(self, tool, arguments):
        response, _ = self._post(
            {
                "jsonrpc": "2.0",
                "id": tool,
                "method": "tools/call",
                "params": {"name": tool, "arguments": arguments},
            }
        )
        result = response.get("result")
        if result is None:
            raise RuntimeError(f"{self.agent}.{tool}: {json.dumps(response)[:600]}")
        text = (result.get("content") or [{}])[0].get("text", "")
        if result.get("isError"):
            raise RuntimeError(f"{self.agent}.{tool} failed: {text[:600]}")
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {"raw": text}


def existing_prices():
    """Every item price on the site, keyed by id (read-only agent)."""
    mcp = Mcp("data")
    prices = {}
    offset = None
    for _ in range(40):
        arguments = {"limit": 100}
        if offset:
            arguments["offset"] = offset
        page = mcp.call("list_item_prices", arguments)
        for entry in page.get("list", []):
            price = entry["item_price"]
            prices[price["id"]] = price
        offset = page.get("next_offset")
        if not offset:
            break
    return prices


def retrieve_price(price_id, mcp=None):
    client = mcp or Mcp("data")
    return client.call("retrieve_item_price", {"item_price_id": price_id})


# --------------------------------------------------------------------- payload


def load_rows():
    """The 45 approved rows, corrected to the 8-key create shape."""
    with open(PAYLOAD_SOURCE, encoding="utf-8") as handle:
        source = json.load(handle)

    items = {item["id"]: item for item in source["items"]}
    rows = []
    for raw in source["itemPrices"]:
        row = {key: value for key, value in raw.items() if key not in FORBIDDEN_KEYS}
        row.pop("item_family_id", None)
        row["is_taxable"] = True
        row["_family"] = items[row["item_id"]]["item_family_id"]
        row["_product"] = items[row["item_id"]]["name"]
        rows.append(row)
    return rows


def check_payload(rows):
    """A-1..A-8 of CHARGEBEE_EXECUTION_PLAN.md §5.3. Returns a failure list."""
    failures = []

    if len(rows) != 45:
        failures.append(f"A-1 row count {len(rows)} != 45")
    ids = [row["id"] for row in rows]
    if len(set(ids)) != len(ids):
        failures.append("A-1 duplicate price ids")

    for row in rows:
        size = row["id"].rsplit("-", 1)[-1]
        if size not in SIZES:
            failures.append(f"A-2 {row['id']}: no size token in id")
        if not row["name"].endswith(size):
            failures.append(f"A-2 {row['id']}: name lacks {size}")
        if not row["description"].endswith(size):
            failures.append(f"A-2 {row['id']}: description lacks {size}")

    by_item = {}
    for row in rows:
        by_item.setdefault(row["item_id"], []).append(row["id"].rsplit("-", 1)[-1])
    if len(by_item) != 15:
        failures.append(f"A-3 {len(by_item)} items != 15")
    for item_id, sizes in by_item.items():
        if sorted(sizes) != sorted(SIZES):
            failures.append(f"A-3 {item_id}: sizes {sorted(sizes)}")

    for row in rows:
        if row["_family"] not in FAMILIES:
            failures.append(f"A-6 {row['id']}: family {row['_family']!r}")
        if not isinstance(row["price"], int) or row["price"] <= 0:
            failures.append(f"A-5 {row['id']}: price {row['price']!r} not positive int")
        if row["currency_code"] != "INR":
            failures.append(f"A-5 {row['id']}: currency {row['currency_code']}")
        if row["pricing_model"] != "flat_fee":
            failures.append(f"A-7 {row['id']}: pricing_model {row['pricing_model']}")
        if set(row) - {"_family", "_product"} != ALLOWED_KEYS:
            failures.append(f"A-7 {row['id']}: keys {sorted(row)}")
        if row.get("is_taxable") is not True:
            failures.append(f"A-8 {row['id']}: is_taxable not True")

    # A-9/A-10: every row carries the price variant of its size, and no two rows
    # claim the same (item, currency, variant) price point.
    price_points = {}
    for row in rows:
        size = row["id"].rsplit("-", 1)[-1]
        expected_variant = VARIANTS.get(size)
        variant = row.get("price_variant_id")
        if variant != expected_variant:
            failures.append(
                f"A-9 {row['id']}: price_variant_id {variant!r} != {expected_variant!r}"
            )
        key = (row["item_id"], row["currency_code"], variant)
        if key in price_points:
            failures.append(
                f"A-10 {row['id']}: duplicate price point {key} (already {price_points[key]})"
            )
        price_points[key] = row["id"]
    if len(price_points) != len(rows):
        failures.append(f"A-10 {len(price_points)} distinct price points != {len(rows)}")

    return failures


def body_for(row):
    return {key: row[key] for key in ALLOWED_KEYS}


# ----------------------------------------------------------------------- steps


def create_one(onboarding, data, row, known):
    """Create one price, then read it back and assert what Chargebee stored."""
    price_id = row["id"]
    if price_id in known:
        print(f"  = {price_id:<44} already exists — left untouched")
        return verify_one(data, row, known[price_id])

    onboarding.call(
        "create_an_item_price",
        {
            "header_params": {
                "chargebee-idempotency-key": str(
                    uuid.uuid5(uuid.NAMESPACE_URL, f"bmj-price:{price_id}")
                )
            },
            "body_params": body_for(row),
        },
    )
    stored = retrieve_price(price_id, data)["item_price"]
    known[price_id] = stored
    return verify_one(data, row, stored)


def verify_one(data, row, stored):
    """Compare the stored price with the approved row."""
    expected = body_for(row)
    problems = []

    for key in ("name", "item_id", "pricing_model", "currency_code"):
        if stored.get(key) != expected[key]:
            problems.append(f"{key}={stored.get(key)!r} != {expected[key]!r}")
    if stored.get("price") != expected["price"]:
        problems.append(f"price={stored.get('price')} != {expected['price']}")
    if stored.get("is_taxable") is not True:
        problems.append(f"is_taxable={stored.get('is_taxable')!r}")
    if stored.get("status") != "active":
        problems.append(f"status={stored.get('status')!r}")
    if stored.get("item_type") != "charge":
        problems.append(f"item_type={stored.get('item_type')!r}")
    if stored.get("item_family_id") != row["_family"]:
        problems.append(
            f"item_family_id={stored.get('item_family_id')!r} != {row['_family']!r}"
        )
    if stored.get("price_variant_id") != expected.get("price_variant_id"):
        problems.append(
            f"price_variant_id={stored.get('price_variant_id')!r} != {expected.get('price_variant_id')!r}"
        )

    amount = f"₹{stored.get('price', 0) / 100:,.2f}"
    if problems:
        print(f"  ✗ {row['id']:<44} {amount:<12} {'; '.join(problems)}")
        return False
    print(f"  ✓ {row['id']:<44} {amount:<12} {row['_family']}")
    return True


# ------------------------------------------------------------------------- CLI


def preflight():
    """Is this site ready for variant pricing? Read-only: writes nothing."""
    data = Mcp("data")
    try:
        page = data.call("list_price_variants", {"limit": 100})
    except Exception as error:  # noqa: BLE001 - the probe reports, it never raises
        print("price variants: NOT AVAILABLE on this site")
        print(f"  Chargebee said: {str(error)[:400]}")
        print("\nRemediation — either, then rerun this command:")
        print("  1. Chargebee UI: Settings -> Configure Chargebee -> Product Catalog")
        print("     -> Price Variants -> Enable, then create the three variants below.")
        print("  2. Chargebee support (support@chargebee.com) quoting the message above.")
        print("\nNothing was written. The rollout stays paused.")
        return False

    found = {}
    for entry in page.get("list", []):
        variant = entry.get("price_variant", entry)
        if variant.get("id"):
            found[variant["id"]] = variant

    print(f"price variants on site: {len(found)}")
    for size, variant_id in VARIANTS.items():
        state = "present" if variant_id in found else "MISSING"
        print(f"  {size:<6} {variant_id:<12} {state}")

    missing = [v for v in VARIANTS.values() if v not in found]
    if missing:
        print("\nCreate the missing variants (Product Catalog -> Price Variants):")
        for variant_id in missing:
            size = next(s for s, v in VARIANTS.items() if v == variant_id)
            print(
                f"  id={variant_id:<12} name={size.replace('ml', ' ml'):<8} "
                f"description=One-time {size} bottle"
            )
        print("\nNot ready: create the variants above, then rerun preflight.")
        return False

    print("\nprice variants: READY — canary may run")
    return True


def run_batch(rows, known, label):
    onboarding = Mcp("onboarding")
    data = Mcp("data")
    print(f"\n== {label}: {len(rows)} price(s) ==")
    results = [create_one(onboarding, data, row, known) for row in rows]
    ok = sum(1 for passed in results if passed)
    print(f"  {ok}/{len(rows)} verified")
    return ok == len(rows)


def census(rows):
    """Site-level totals before/after, plus per-family coverage."""
    prices = existing_prices()
    by_type = {}
    for price in prices.values():
        by_type.setdefault(price.get("item_type"), 0)
        by_type[price["item_type"]] += 1

    mine = {row["id"] for row in rows}
    present = mine & set(prices)
    missing = sorted(mine - set(prices))
    zero_priced_items = {}
    for price in prices.values():
        zero_priced_items.setdefault(price["item_id"], 0)

    print(f"item prices on site : {len(prices)}")
    print("by item_type        : " + ", ".join(f"{k}={v}" for k, v in sorted(by_type.items())))
    print(f"approved prices     : {len(present)}/{len(mine)}")
    if missing:
        print(f"missing             : {', '.join(missing)}")
    for family in FAMILIES:
        total = len([row for row in rows if row["_family"] == family])
        have = len([row for row in rows if row["_family"] == family and row["id"] in prices])
        print(f"  {family:<10} {have}/{total}")
    bad = [p for p in prices.values() if not p.get("price") or p["price"] <= 0]
    print(f"zero/negative prices: {len(bad)}")
    print(f"non-INR prices      : {len([p for p in prices.values() if p.get('currency_code') != 'INR'])}")
    with_variant = [row["id"] for row in rows if (prices.get(row["id"]) or {}).get("price_variant_id")]
    print(f"with price variant  : {len(with_variant)}/{len(rows)}")
    default_priced = [
        row["id"] for row in rows
        if row["id"] in prices and not prices[row["id"]].get("price_variant_id")
    ]
    if default_priced:
        print(f"no-variant prices   : {', '.join(default_priced)}")
    return len(missing) == 0 and len(bad) == 0


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:  # pragma: no cover
        pass

    rows = load_rows()
    failures = check_payload(rows)
    command = sys.argv[1] if len(sys.argv) > 1 else "plan"

    if command == "plan":
        print(f"{len(rows)} rows from {PAYLOAD_SOURCE}")
        for family in FAMILIES:
            family_rows = [row for row in rows if row["_family"] == family]
            print(f"  {family:<10} {len(family_rows)} rows")
            for row in family_rows:
                print(
                    f"    {row['id']:<44} {row['price']:>6} paise  "
                    f"₹{row['price'] / 100:>8,.2f}  {row['price_variant_id']:<10} "
                    f"{row['item_id']}"
                )
        if failures:
            print("\nPAYLOAD FAILURES:")
            for failure in failures:
                print(f"  - {failure}")
            return 1
        print("\nA-1..A-10: PASS (45 rows, 15 items x 3 price variants)")
        return 0

    if command == "preflight":
        return 0 if preflight() else 1

    if failures:
        print("refusing to run — payload assertions failed:")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    # No price is written until variant pricing is provably available.
    if command in ("canary", "batch") and not preflight():
        return 1

    if command == "canary":
        canary = [row for row in rows if row["id"] == CANARY_ID]
        if not canary:
            print(f"canary {CANARY_ID} not in payload")
            return 1
        known = existing_prices()
        return 0 if run_batch(canary, known, "canary") else 1

    if command == "batch":
        family = sys.argv[2] if len(sys.argv) > 2 else ""
        if family not in FAMILIES:
            print(f"family must be one of {FAMILIES}")
            return 1
        batch = [row for row in rows if row["_family"] == family]
        known = existing_prices()
        return 0 if run_batch(batch, known, f"{family} batch") else 1

    if command == "verify":
        known = existing_prices()
        data = Mcp("data")
        failed = [
            row["id"] for row in rows if row["id"] not in known
            or not verify_one(data, row, known[row["id"]])
        ]
        print(f"\n{len(rows) - len(failed)}/{len(rows)} approved prices verified")
        return 1 if failed else 0

    if command == "census":
        return 0 if census(rows) else 1

    print(f"unknown command {command!r}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
