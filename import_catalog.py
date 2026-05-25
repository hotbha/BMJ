#!/usr/bin/env python3
"""
Import product catalog into Chargebee using MCP.
Sends items, item families, item prices, and currencies.
"""
import json
import requests
import sys

BASE_URL = "https://bookmyjuice-test.mcp.chargebee.com/onboarding_agent"
TOKEN = "test_ai_-ZFEjZ3qiK2mW3k7C9M2Q60OK2QmLslRdSnNWt61z4E"
SESSION_ID = "019e5c40-f05d-77ea-820e-037d0cc7a7fc"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
    "Accept": "text/event-stream",
    "mcp-session-id": SESSION_ID
}

def call_tool(method_name, arguments):
    """Call an MCP tool"""
    body = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": method_name,
            "arguments": arguments
        }
    }
    resp = requests.post(BASE_URL, json=body, headers=headers, timeout=30)
    content = resp.text
    return content

# Build items for each juice in each family with each size (200ml, 300ml, 500ml)
# Total: 3 families * 5 juices * 3 sizes = 45 items
items = []

item_families = [
    {"id": "delight", "name": "Delight", "description": "Entry-level refreshing juice collection"},
    {"id": "signature", "name": "Signature", "description": "Mid-range exclusive juice collection"},
    {"id": "premium", "name": "Premium", "description": "Premium cold-pressed juice collection"},
]

juice_config = {
    "delight": {
        "juices": ["MixPunch", "CarrotJuice", "ColonCleanser", "BeatTheHeat", "WinterSpecial"],
        "juice_display": ["Mix Punch", "Carrot Juice", "Colon Cleanser", "Beat the heat", "Winter Special"],
        "base_prices": {"200": 12900, "300": 15900, "500": 22900}
    },
    "signature": {
        "juices": ["ABCJuice", "Pineapple", "AmlaJuice", "AshguardJuice", "CitrusJuice"],
        "juice_display": ["ABC Juice", "Pineapple", "Amla Juice", "Ashguard Juice", "Citrus Juice"],
        "base_prices": {"200": 19900, "300": 24900, "500": 34900}
    },
    "premium": {
        "juices": ["BloodyRed", "Antioxidant", "WheatgrassJuice", "CoconutMilk", "DetoxSmoothie"],
        "juice_display": ["Bloody Red", "Antioxidant Juice", "Wheatgrass Juice", "Coconut Milk", "Detox Smoothie"],
        "base_prices": {"200": 29900, "300": 34900, "500": 44900}
    }
}

for family, config in juice_config.items():
    for i, juice_id in enumerate(config["juices"]):
        juice_display = config["juice_display"][i]
        for size, base_price_cents in config["base_prices"].items():
            item_id = f"{family}-{juice_id}-{size}"
            item_name = f"{juice_display} ({size}ml)"
            item_desc = f"{family.capitalize()} {juice_display} {size}ml"
            items.append({
                "id": item_id,
                "name": item_name,
                "description": item_desc,
                "type": "plan",
                "item_family_id": family,
                "metered": False,
                "metadata": {"is_custom_pricing": False}
            })

# Build item prices - 2 per item (Weekly and Monthly) = 90 prices
item_prices = []
price_idx = 1

for family, config in juice_config.items():
    for i, juice_id in enumerate(config["juices"]):
        juice_display = config["juice_display"][i]
        for size, base_price_cents in config["base_prices"].items():
            item_id = f"{family}-{juice_id}-{size}"
            weekly_price = base_price_cents * 6  # 6 days
            monthly_price = base_price_cents * 24  # 4 weeks = 24 days

            # Weekly price
            item_prices.append({
                "id": f"ip-{price_idx:04d}",
                "name": f"{juice_display} {size}ml Weekly",
                "description": f"{family.capitalize()} {juice_display} {size}ml - Weekly (6 days)",
                "pricing_model": "flat_fee",
                "item_id": item_id,
                "item_family_id": family,
                "price": weekly_price,
                "currency_code": "INR",
                "period": 6,
                "period_unit": "day",
                "trial_period": 0,
                "trial_period_unit": "day",
                "tiers": []
            })
            price_idx += 1

            # Monthly price
            item_prices.append({
                "id": f"ip-{price_idx:04d}",
                "name": f"{juice_display} {size}ml Monthly",
                "description": f"{family.capitalize()} {juice_display} {size}ml - Monthly (4 weeks)",
                "pricing_model": "flat_fee",
                "item_id": item_id,
                "item_family_id": family,
                "price": monthly_price,
                "currency_code": "INR",
                "period": 1,
                "period_unit": "month",
                "trial_period": 0,
                "trial_period_unit": "day",
                "tiers": []
            })
            price_idx += 1

# Currencies with correct field name
currencies = [{"currency_code": "INR", "prefix": "₹", "exchange_rate": 1.0}]

print(f"Items: {len(items)}")
print(f"Item Families: {len(item_families)}")
print(f"Item Prices: {len(item_prices)}")
print(f"Currencies: {len(currencies)}")

# Call import
result = call_tool("import_product_catalog", {
    "items": items,
    "itemFamilies": item_families,
    "itemPrices": item_prices,
    "currencies": currencies
})
print("\n=== IMPORT RESULT ===")
print(result)

# Save result to file
with open("import_result.json", "w") as f:
    f.write(result)
