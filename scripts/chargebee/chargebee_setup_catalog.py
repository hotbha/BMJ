#!/usr/bin/env python3
"""
Chargebee Product Catalog Setup for BMJ
Builds catalog data manually and imports into Chargebee test site.
"""
import json
import requests
import sys
import os

BASE_URL = "https://bookmyjuice-test.mcp.chargebee.com/onboarding_agent"
TOKEN = "test_ai_-ZFEjZ3qiK2mW3k7C9M2Q60OK2QmLslRdSnNWt61z4E"

def make_headers(session_id=None):
    h = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
    }
    if session_id:
        h["mcp-session-id"] = session_id
    return h

def call_tool(session_id, method_name, arguments, timeout=120):
    """Call MCP tool with SSE streaming support"""
    body = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": method_name,
            "arguments": arguments
        }
    }
    print(f"Calling {method_name}... (timeout={timeout}s)")
    
    resp = requests.post(
        BASE_URL, 
        json=body, 
        headers=make_headers(session_id), 
        timeout=timeout,
        stream=True
    )
    
    full_text = ""
    for chunk in resp.iter_content(chunk_size=None, decode_unicode=True):
        if chunk:
            full_text += chunk
            for line in chunk.split('\n'):
                if line.startswith('data: '):
                    data_str = line[6:]
                    try:
                        return json.loads(data_str)
                    except json.JSONDecodeError:
                        pass
    
    for line in full_text.split('\n'):
        if line.startswith('data: '):
            data_str = line[6:]
            try:
                return json.loads(data_str)
            except json.JSONDecodeError:
                pass
    
    print(f"Raw response (1000 chars): {full_text[:1000]}")
    return {"raw": full_text[:5000]}

def build_catalog():
    """Build the complete BMJ product catalog manually"""
    
    # Pricing data: {category: {size: paise_price_per_bottle}}
    bottle_prices = {
        "delight":    {"200ml": 12900, "300ml": 15900, "500ml": 22900},
        "signature":  {"200ml": 19900, "300ml": 24900, "500ml": 34900},
        "premium":    {"200ml": 29900, "300ml": 34900, "500ml": 44900},
    }
    
    juices = ["Orange", "Apple", "Mango", "Mixed", "Black_Grapes"]
    sizes = ["200ml", "300ml", "500ml"]
    categories = ["delight", "signature", "premium"]
    durations = [("weekly", 6, "day"), ("monthly", 1, "month")]
    
    # Item Families (3)
    item_families = [
        {"id": "delight", "name": "Delight", "description": "Entry-level juice subscription"},
        {"id": "signature", "name": "Signature", "description": "Mid-range juice subscription"},
        {"id": "premium", "name": "Premium", "description": "Premium juice subscription"},
    ]
    
    # Items (Plans) - 18: 3 categories x 3 sizes x 2 durations
    items = []
    for cat in categories:
        for size in sizes:
            for dur_id, period, period_unit in durations:
                item_id = f"{cat}_{size.replace('ml','')}ml_{dur_id}"
                items.append({
                    "id": item_id,
                    "name": f"{cat.title()} {size} ({dur_id.title()})",
                    "description": f"{cat.title()} {size} subscription - {dur_id.title()}",
                    "type": "plan",
                    "item_family_id": cat,
                    "metered": False,
                    "metadata": {"is_custom_pricing": False}
                })
    
    # Item Prices (45): One per category+juice+size combination for individual purchases
    # These are one-time charge prices for individual bottles
    item_prices_charges = []
    for cat in categories:
        for juice in juices:
            for size in sizes:
                price_id = f"{cat}_{juice.lower()}_{size.replace('ml','')}ml"
                paise = bottle_prices[cat][size]
                item_prices_charges.append({
                    "id": price_id,
                    "name": f"{cat.title()} {juice.replace('_',' ')} {size}",
                    "description": f"{cat.title()} - {juice.replace('_',' ')} {size} - One-time",
                    "pricing_model": "flat_fee",
                    "item_id": f"{cat}_{size.replace('ml','')}ml_weekly",  # linked to weekly plan
                    "item_family_id": cat,
                    "price": paise,
                    "currency_code": "INR",
                    "period": None,
                    "period_unit": None,
                    "trial_period": 0,
                    "trial_period_unit": "day",
                    "tiers": []
                })
    
    print(f"\nBuilt catalog:")
    print(f"  Item Families: {len(item_families)}")
    print(f"  Items (Plans): {len(items)}")
    print(f"  Item Prices:   {len(item_prices_charges)}")
    
    return {
        "items": items,
        "itemFamilies": item_families,
        "itemPrices": item_prices_charges,
        "currencies": [{"currency_code": "INR"}]
    }

def main():
    session_id = sys.argv[1] if len(sys.argv) > 1 else input("Session ID: ")
    
    catalog = build_catalog()
    
    print("\n" + "=" * 60)
    print("STEP 1: Import product catalog to Chargebee...")
    print("=" * 60)
    
    # Save catalog for reference
    with open("chargebee_catalog.json", "w") as f:
        json.dump(catalog, f, indent=2)
    print("Saved catalog to chargebee_catalog.json")
    
    result = call_tool(session_id, "import_product_catalog", catalog, timeout=120)
    
    print(f"\nImport result keys: {list(result.keys())}")
    if "result" in result:
        print(f"Success! Result: {json.dumps(result['result'], indent=2)[:2000]}")
    elif "error" in result:
        print(f"Error: {json.dumps(result['error'], indent=2)}")
        err_msg = json.dumps(result['error']).lower()
        if "already exist" in err_msg or "conflict" in err_msg or "duplicate" in err_msg:
            print("\nItems may already exist. Trying to clear and re-import is not available via API.")
            print("You may need to manually clear data in Chargebee dashboard.")
    else:
        print(f"Raw: {json.dumps(result, indent=2)[:2000]}")

if __name__ == "__main__":
    main()
