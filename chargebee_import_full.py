#!/usr/bin/env python3
"""
Import BMJ product catalog into Chargebee test site.
Creates 3 families, 45 items (plans), 90 item prices.
"""
import json
import os
import requests

BASE_URL = "https://bookmyjuice-test.mcp.chargebee.com/onboarding_agent"
TOKEN = "test_ai_-ZFEjZ3qiK2mW3k7C9M2Q60OK2QmLslRdSnNWt61z4E"

SESSION = "019e6559-4a55-7192-9fba-cd8d8f70327b"

def call_tool(method, args, timeout=120):
    body = {
        "jsonrpc": "2.0", "id": 3,
        "method": "tools/call",
        "params": {"name": method, "arguments": args}
    }
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
        "mcp-session-id": SESSION,
    }
    resp = requests.post(BASE_URL, json=body, headers=headers, timeout=timeout, stream=True)
    
    full_text = ""
    for chunk in resp.iter_content(chunk_size=None, decode_unicode=True):
        if chunk:
            full_text += chunk
            for line in chunk.split('\n'):
                if line.startswith('data: '):
                    try:
                        return json.loads(line[6:])
                    except:
                        pass
    for line in full_text.split('\n'):
        if line.startswith('data: '):
            try:
                return json.loads(line[6:])
            except:
                pass
    return {"raw": full_text[:3000]}


def build_full_catalog():
    """Build complete BMJ catalog: 3 families, 45 items, 90 item prices"""
    
    # Price per bottle (in paise) per category+size
    # Per PRICING_STRUCTURE.md
    prices_per_bottle = {
        ("delight", "200ml"): 12900,
        ("delight", "300ml"): 15900,
        ("delight", "500ml"): 22900,
        ("signature", "200ml"): 19900,
        ("signature", "300ml"): 24900,
        ("signature", "500ml"): 34900,
        ("premium", "200ml"): 29900,
        ("premium", "300ml"): 34900,
        ("premium", "500ml"): 44900,
    }
    
    # 5 juice flavors per category
    flavor_slugs = ["orange", "apple", "mango", "mixed", "black-grapes"]
    flavor_names = ["Orange", "Apple", "Mango", "Mixed", "Black Grapes"]
    sizes = ["200ml", "300ml", "500ml"]
    categories = ["delight", "signature", "premium"]
    cat_names = {"delight": "Delight", "signature": "Signature", "premium": "Premium"}
    
    # Durations for prices
    durations = [
        ("weekly", 6, "day", "Weekly"),
        ("monthly", 1, "month", "Monthly"),
    ]
    
    # === ITEM FAMILIES (3) ===
    item_families = [
        {"id": "delight", "name": "Delight", "description": "Entry-level juice subscription category"},
        {"id": "signature", "name": "Signature", "description": "Mid-range juice subscription category"},
        {"id": "premium", "name": "Premium", "description": "Premium juice subscription category"},
    ]
    
    # === ITEMS (45 plans) ===
    # Each plan = category + juice + size
    items = []
    item_id_map = {}  # track item ids
    
    for cat in categories:
        for fi, flavor in enumerate(flavor_slugs):
            for size in sizes:
                item_id = f"{cat}-{flavor}-{size}"
                item_name = f"{cat_names[cat]} {flavor_names[fi]} {size}"
                items.append({
                    "id": item_id,
                    "name": item_name,
                    "description": f"{cat_names[cat]} - {flavor_names[fi]} - {size}",
                    "type": "plan",
                    "item_family_id": cat,
                    "metered": False,
                    "metadata": {"is_custom_pricing": False}
                })
                item_id_map[(cat, flavor, size)] = item_id
    
    # === ITEM PRICES (90 = 45 items x 2 durations) ===
    item_prices = []
    
    for cat in categories:
        for fi, flavor in enumerate(flavor_slugs):
            for size in sizes:
                base_price = prices_per_bottle[(cat, size)]
                item_id = item_id_map[(cat, flavor, size)]
                
                for dur_slug, period, period_unit, dur_name in durations:
                    # Weekly = 6 bottles, Monthly = 24 bottles
                    if dur_slug == "weekly":
                        quantity = 6
                        total_paise = base_price * 6  # 6 bottles
                    else:
                        quantity = 24
                        total_paise = base_price * 24  # 24 bottles
                    
                    price_id = f"{item_id}-{dur_slug}"
                    
                    item_prices.append({
                        "id": price_id,
                        "name": f"{cat_names[cat]} {flavor_names[fi]} {size} ({dur_name})",
                        "description": f"{cat_names[cat]} - {flavor_names[fi]} - {size} - {dur_name}",
                        "pricing_model": "flat_fee",
                        "item_id": item_id,
                        "item_family_id": cat,
                        "price": total_paise,
                        "currency_code": "INR",
                        "period": period,
                        "period_unit": period_unit,
                        "trial_period": 0,
                        "trial_period_unit": "day",
                        "tiers": []
                    })
    
    print(f"\n=== BUILT CATALOG ===")
    print(f"Item Families: {len(item_families)}")
    print(f"Items (plans): {len(items)}")
    print(f"Item Prices:   {len(item_prices)}")
    print(f"Total: {len(item_families) + len(items) + len(item_prices)} objects")
    
    # Verify item_family_id references
    family_ids = {f["id"] for f in item_families}
    item_family_refs = {i["item_family_id"] for i in items}
    price_family_refs = {p["item_family_id"] for p in item_prices}
    print(f"\nFamily IDs in families: {family_ids}")
    print(f"Family refs in items:   {item_family_refs}")
    print(f"Family refs in prices:  {price_family_refs}")
    assert family_ids == item_family_refs, "Item family refs don't match!"
    assert family_ids == price_family_refs, "Price family refs don't match!"
    
    # Verify item_id references
    item_ids = {i["id"] for i in items}
    price_item_refs = {p["item_id"] for p in item_prices}
    print(f"Item IDs count:  {len(item_ids)}")
    print(f"Price item refs: {len(price_item_refs)}")
    
    return {
        "itemFamilies": item_families,
        "items": items,
        "itemPrices": item_prices,
        "currencies": [{"currency_code": "INR"}]
    }


# Build and validate
catalog = build_full_catalog()

# Save catalog for reference
with open("chargebee_catalog.json", "w") as f:
    json.dump(catalog, f, indent=2)
print(f"\nSaved chargebee_catalog.json ({os.path.getsize('chargebee_catalog.json')} bytes)")

# Import step
print("\n=== IMPORTING TO CHARGEBEE ===")
print("Press Ctrl+C if you want to abort, or wait 5s...")
import time as _time
# No wait - proceed directly
# _time.sleep(5)

result = call_tool("import_product_catalog", catalog, timeout=180)

print(f"\nImport result type: {type(result).__name__}")
if "result" in result:
    data = result["result"]
    if isinstance(data, dict):
        print(f"Result keys: {list(data.keys())}")
        print(json.dumps(data, indent=2)[:3000])
    else:
        print(f"Result: {str(data)[:3000]}")
elif "error" in result:
    err = result["error"]
    print(f"Error: {json.dumps(err, indent=2)}")
else:
    print(f"Raw result: {json.dumps(result, indent=2)[:3000]}")
