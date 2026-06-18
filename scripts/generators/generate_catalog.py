#!/usr/bin/env python3
"""
Step 1: Call generate_product_catalog with pricing summary
Step 2: Import the generated catalog into Chargebee
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

# Pricing summary based on Excel data from user
PRICING_SUMMARY = """
BookMyJuice Juice Subscription Plans

Three product families: Delight, Signature, Premium

Delight (Entry-level family):
- Juices: Mix Punch (200ml, 300ml, 500ml), Carrot Juice (200ml, 300ml, 500ml), Colon Cleanser (200ml, 300ml, 500ml), Beat the heat (200ml, 300ml, 500ml), Winter Special (200ml, 300ml, 500ml)
- Weekly subscription: 6 days, Daily delivery
- Monthly subscription: 4 weeks (24 days), Daily delivery
- Juice names within Delight family: Mix Punch, Carrot Juice, Colon Cleanser, Beat the heat, Winter Special

Signature (Mid-range family):
- Juices: ABC Juice (200ml, 300ml, 500ml), Pineapple (200ml, 300ml, 500ml), Amla Juice (200ml, 300ml, 500ml), Ashguard Juice (200ml, 300ml, 500ml), Citrus Juice (200ml, 300ml, 500ml)
- Weekly subscription: 6 days, Daily delivery
- Monthly subscription: 4 weeks (24 days), Daily delivery
- Juice names within Signature family: ABC Juice, Pineapple, Amla Juice, Ashguard Juice, Citrus Juice

Premium (Highest family):
- Juices: Bloody Red (200ml, 300ml, 500ml), Antioxidant Juice (200ml, 300ml, 500ml), Wheatgrass Juice (200ml, 300ml, 500ml), Coconut Milk (200ml, 300ml, 500ml), Detox Smoothie (200ml, 300ml, 500ml)
- Weekly subscription: 6 days, Daily delivery
- Monthly subscription: 4 weeks (24 days), Daily delivery
- Juice names within Premium family: Bloody Red, Antioxidant Juice, Wheatgrass Juice, Coconut Milk, Detox Smoothie

All prices in INR (INR currency).
"""

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

def parse_sse_json(content):
    """Parse SSE JSON response"""
    for line in content.split("\n"):
        if line.startswith("data: "):
            return json.loads(line[6:])
    return None

if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "generate"
    
    if action == "generate":
        result = call_tool("generate_product_catalog", {
            "pricingSummary": PRICING_SUMMARY
        })
        print("=== GENERATE PRODUCT CATALOG RESULT ===")
        print(result[:5000])
        
        # Save for later use
        with open("catalog_result.json", "w") as f:
            f.write(result)
        
        # Try to parse and extract items, itemPrices, itemFamilies
        data = parse_sse_json(result)
        if data and "result" in data:
            result_data = data["result"]
            content = result_data.get("content", [])
            for c in content:
                if c.get("type") == "text":
                    text = c["text"]
                    print(f"\n=== TEXT CONTENT (first 3000 chars) ===")
                    print(text[:3000])
                    with open("catalog_text.txt", "w") as f:
                        f.write(text)
            
    elif action == "import":
        # Read the saved catalog and import
        with open("catalog_result.json", "r") as f:
            result = f.read()
        
        # Parse the catalog JSON
        data = parse_sse_json(result)
        if data:
            result_data = data["result"]
            content = result_data.get("content", [])
            for c in content:
                if c.get("type") == "text":
                    text = c["text"]
                    # Try to extract JSON from text
                    try:
                        catalog = json.loads(text)
                        items = catalog.get("items", [])
                        item_families = catalog.get("itemFamilies", [])
                        item_prices = catalog.get("itemPrices", [])
                        currencies = catalog.get("currencies", [])
                        
                        print(f"Items: {len(items)}")
                        print(f"Item Families: {len(item_families)}")
                        print(f"Item Prices: {len(item_prices)}")
                        print(f"Currencies: {len(currencies)}")
                        
                        import_result = call_tool("import_product_catalog", {
                            "items": items,
                            "itemFamilies": item_families,
                            "itemPrices": item_prices,
                            "currencies": currencies
                        })
                        print("\n=== IMPORT RESULT ===")
                        print(import_result)
                    except json.JSONDecodeError:
                        print(f"Could not parse as JSON: {text[:500]}")
    
    elif action == "manual":
        # Directly call import_product_catalog with manually constructed data
        items = [
            # Delight family - Mix Punch sizes
            {"id": "delight-mixpunch-200", "name": "Mix Punch (200ml)", "description": "Delight Mix Punch 200ml", "type": "plan", "item_family_id": "delight", "metered": False, "metadata": {"is_custom_pricing": False}},
            {"id": "delight-mixpunch-300", "name": "Mix Punch (300ml)", "description": "Delight Mix Punch 300ml", "type": "plan", "item_family_id": "delight", "metered": False, "metadata": {"is_custom_pricing": False}},
            {"id": "delight-mixpunch-500", "name": "Mix Punch (500ml)", "description": "Delight Mix Punch 500ml", "type": "plan", "item_family_id": "delight", "metered": False, "metadata": {"is_custom_pricing": False}},
            # Delight - Carrot Juice sizes
            {"id": "delight-carrot-200", "name": "Carrot Juice (200ml)", "description": "Delight Carrot Juice 200ml", "type": "plan", "item_family_id": "delight", "metered": False, "metadata": {"is_custom_pricing": False}},
            {"id": "delight-carrot-300", "name": "Carrot Juice (300ml)", "description": "Delight Carrot Juice 300ml", "type": "plan", "item_family_id": "delight", "metered": False, "metadata": {"is_custom_pricing": False}},
            {"id": "delight-carrot-500", "name": "Carrot Juice (500ml)", "description": "Delight Carrot Juice 500ml", "type": "plan", "item_family_id": "delight", "metered": False, "metadata": {"is_custom_pricing": False}},
            # Delight - Colon Cleanser sizes
            {"id": "delight-colon-200", "name": "Colon Cleanser (200ml)", "description": "Delight Colon Cleanser 200ml", "type": "plan", "item_family_id": "delight", "metered": False, "metadata": {"is_custom_pricing": False}},
            {"id": "delight-colon-300", "name": "Colon Cleanser (300ml)", "description": "Delight Colon Cleanser 300ml", "type": "plan", "item_family_id": "delight", "metered": False, "metadata": {"is_custom_pricing": False}},
            {"id": "delight-colon-500", "name": "Colon Cleanser (500ml)", "description": "Delight Colon Cleanser 500ml", "type": "plan", "item_family_id": "delight", "metered": False, "metadata": {"is_custom_pricing": False}},
            # Delight - Beat the heat sizes
            {"id": "delight-beatheat-200", "name": "Beat the heat (200ml)", "description": "Delight Beat the heat 200ml", "type": "plan", "item_family_id": "delight", "metered": False, "metadata": {"is_custom_pricing": False}},
            {"id": "delight-beatheat-300", "name": "Beat the heat (300ml)", "description": "Delight Beat the heat 300ml", "type": "plan", "item_family_id": "delight", "metered": False, "metadata": {"is_custom_pricing": False}},
            {"id": "delight-beatheat-500", "name": "Beat the heat (500ml)", "description": "Delight Beat the heat 500ml", "type": "plan", "item_family_id": "delight", "metered": False, "metadata": {"is_custom_pricing": False}},
            # Delight - Winter Special sizes
            {"id": "delight-winter-200", "name": "Winter Special (200ml)", "description": "Delight Winter Special 200ml", "type": "plan", "item_family_id": "delight", "metered": False, "metadata": {"is_custom_pricing": False}},
            {"id": "delight-winter-300", "name": "Winter Special (300ml)", "description": "Delight Winter Special 300ml", "type": "plan", "item_family_id": "delight", "metered": False, "metadata": {"is_custom_pricing": False}},
            {"id": "delight-winter-500", "name": "Winter Special (500ml)", "description": "Delight Winter Special 500ml", "type": "plan", "item_family_id": "delight", "metered": False, "metadata": {"is_custom_pricing": False}},
            # Signature family - ABC Juice sizes
            {"id": "signature-abc-200", "name": "ABC Juice (200ml)", "description": "Signature ABC Juice 200ml", "type": "plan", "item_family_id": "signature", "metered": False, "metadata": {"is_custom_pricing": False}},
            {"id": "signature-abc-300", "name": "ABC Juice (300ml)", "description": "Signature ABC Juice 300ml", "type": "plan", "item_family_id": "signature", "metered": False, "metadata": {"is_custom_pricing": False}},
            {"id": "signature-abc-500", "name": "ABC Juice (500ml)", "description": "Signature ABC Juice 500ml", "type": "plan", "item_family_id": "signature", "metered": False, "metadata": {"is_custom_pricing": False}},
            # Signature - Pineapple sizes
            {"id": "signature-pineapple-200", "name": "Pineapple (200ml)", "description": "Signature Pineapple 200ml", "type": "plan", "item_family_id": "signature", "metered": False, "metadata": {"is_custom_pricing": False}},
            {"id": "signature-pineapple-300", "name": "Pineapple (300ml)", "description": "Signature Pineapple 300ml", "type": "plan", "item_family_id": "signature", "metered": False, "metadata": {"is_custom_pricing": False}},
            {"id": "signature-pineapple-500", "name": "Pineapple (500ml)", "description": "Signature Pineapple 500ml", "type": "plan", "item_family_id": "signature", "metered": False, "metadata": {"is_custom_pricing": False}},
            # Signature - Amla Juice sizes
            {"id": "signature-amla-200", "name": "Amla Juice (200ml)", "description": "Signature Amla Juice 200ml", "type": "plan", "item_family_id": "signature", "metered": False, "metadata": {"is_custom_pricing": False}},
            {"id": "signature-amla-300", "name": "Amla Juice (300ml)", "description": "Signature Amla Juice 300ml", "type": "plan", "item_family_id": "signature", "metered": False, "metadata": {"is_custom_pricing": False}},
            {"id": "signature-amla-500", "name": "Amla Juice (500ml)", "description": "Signature Amla Juice 500ml", "type": "plan", "item_family_id": "signature", "metered": False, "metadata": {"is_custom_pricing": False}},
            # Signature - Ashguard Juice sizes
            {"id": "signature-ashguard-200", "name": "Ashguard Juice (200ml)", "description": "Signature Ashguard Juice 200ml", "type": "plan", "item_family_id": "signature", "metered": False, "metadata": {"is_custom_pricing": False}},
            {"id": "signature-ashguard-300", "name": "Ashguard Juice (300ml)", "description": "Signature Ashguard Juice 300ml", "type": "plan", "item_family_id": "signature", "metered": False, "metadata": {"is_custom_pricing": False}},
            {"id": "signature-ashguard-500", "name": "Ashguard Juice (500ml)", "description": "Signature Ashguard Juice 500ml", "type": "plan", "item_family_id": "signature", "metered": False, "metadata": {"is_custom_pricing": False}},
            # Signature - Citrus Juice sizes
            {"id": "signature-citrus-200", "name": "Citrus Juice (200ml)", "description": "Signature Citrus Juice 200ml", "type": "plan", "item_family_id": "signature", "metered": False, "metadata": {"is_custom_pricing": False}},
            {"id": "signature-citrus-300", "name": "Citrus Juice (300ml)", "description": "Signature Citrus Juice 300ml", "type": "plan", "item_family_id": "signature", "metered": False, "metadata": {"is_custom_pricing": False}},
            {"id": "signature-citrus-500", "name": "Citrus Juice (500ml)", "description": "Signature Citrus Juice 500ml", "type": "plan", "item_family_id": "signature", "metered": False, "metadata": {"is_custom_pricing": False}},
            # Premium family - Bloody Red sizes
            {"id": "premium-bloodyred-200", "name": "Bloody Red (200ml)", "description": "Premium Bloody Red 200ml", "type": "plan", "item_family_id": "premium", "metered": False, "metadata": {"is_custom_pricing": False}},
            {"id": "premium-bloodyred-300", "name": "Bloody Red (300ml)", "description": "Premium Bloody Red 300ml", "type": "plan", "item_family_id": "premium", "metered": False, "metadata": {"is_custom_pricing": False}},
            {"id": "premium-bloodyred-500", "name": "Bloody Red (500ml)", "description": "Premium Bloody Red 500ml", "type": "plan", "item_family_id": "premium", "metered": False, "metadata": {"is_custom_pricing": False}},
            # Premium - Antioxidant Juice sizes
            {"id": "premium-antioxidant-200", "name": "Antioxidant Juice (200ml)", "description": "Premium Antioxidant Juice 200ml", "type": "plan", "item_family_id": "premium", "metered": False, "metadata": {"is_custom_pricing": False}},
            {"id": "premium-antioxidant-300", "name": "Antioxidant Juice (300ml)", "description": "Premium Antioxidant Juice 300ml", "type": "plan", "item_family_id": "premium", "metered": False, "metadata": {"is_custom_pricing": False}},
            {"id": "premium-antioxidant-500", "name": "Antioxidant Juice (500ml)", "description": "Premium Antioxidant Juice 500ml", "type": "plan", "item_family_id": "premium", "metered": False, "metadata": {"is_custom_pricing": False}},
            # Premium - Wheatgrass Juice sizes
            {"id": "premium-wheatgrass-200", "name": "Wheatgrass Juice (200ml)", "description": "Premium Wheatgrass Juice 200ml", "type": "plan", "item_family_id": "premium", "metered": False, "metadata": {"is_custom_pricing": False}},
            {"id": "premium-wheatgrass-300", "name": "Wheatgrass Juice (300ml)", "description": "Premium Wheatgrass Juice 300ml", "type": "plan", "item_family_id": "premium", "metered": False, "metadata": {"is_custom_pricing": False}},
            {"id": "premium-wheatgrass-500", "name": "Wheatgrass Juice (500ml)", "description": "Premium Wheatgrass Juice 500ml", "type": "plan", "item_family_id": "premium", "metered": False, "metadata": {"is_custom_pricing": False}},
            # Premium - Coconut Milk sizes
            {"id": "premium-coconut-200", "name": "Coconut Milk (200ml)", "description": "Premium Coconut Milk 200ml", "type": "plan", "item_family_id": "premium", "metered": False, "metadata": {"is_custom_pricing": False}},
            {"id": "premium-coconut-300", "name": "Coconut Milk (300ml)", "description": "Premium Coconut Milk 300ml", "type": "plan", "item_family_id": "premium", "metered": False, "metadata": {"is_custom_pricing": False}},
            {"id": "premium-coconut-500", "name": "Coconut Milk (500ml)", "description": "Premium Coconut Milk 500ml", "type": "plan", "item_family_id": "premium", "metered": False, "metadata": {"is_custom_pricing": False}},
            # Premium - Detox Smoothie sizes
            {"id": "premium-detox-200", "name": "Detox Smoothie (200ml)", "description": "Premium Detox Smoothie 200ml", "type": "plan", "item_family_id": "premium", "metered": False, "metadata": {"is_custom_pricing": False}},
            {"id": "premium-detox-300", "name": "Detox Smoothie (300ml)", "description": "Premium Detox Smoothie 300ml", "type": "plan", "item_family_id": "premium", "metered": False, "metadata": {"is_custom_pricing": False}},
            {"id": "premium-detox-500", "name": "Detox Smoothie (500ml)", "description": "Premium Detox Smoothie 500ml", "type": "plan", "item_family_id": "premium", "metered": False, "metadata": {"is_custom_pricing": False}},
        ]
        
        item_families = [
            {"id": "delight", "name": "Delight", "description": "Entry-level refreshing juice collection"},
            {"id": "signature", "name": "Signature", "description": "Mid-range exclusive juice collection"},
            {"id": "premium", "name": "Premium", "description": "Premium cold-pressed juice collection"},
        ]
        
        # Item prices - Weekly (6 days) for each item
        item_prices = []
        
        # Pricing (in paise - INR * 100)
        # Delight: 200ml=12900, 300ml=15900, 500ml=22900 (per bottle)
        # Weekly = price * 6, Monthly = price * 24
        pricing = {
            "delight": {"200": 12900, "300": 15900, "500": 22900},
            "signature": {"200": 19900, "300": 24900, "500": 34900},
            "premium": {"200": 29900, "300": 34900, "500": 44900},
        }
        
        juice_names = {
            "delight": ["mixpunch", "carrot", "colon", "beatheat", "winter"],
            "signature": ["abc", "pineapple", "amla", "ashguard", "citrus"],
            "premium": ["bloodyred", "antioxidant", "wheatgrass", "coconut", "detox"],
        }
        
        price_id_counter = 1
        for family in ["delight", "signature", "premium"]:
            for juice in juice_names[family]:
                for size in ["200", "300", "500"]:
                    base_price = pricing[family][size]
                    
                    # Weekly (6 days): price * 6
                    weekly_price = base_price * 6
                    item_id = f"{family}-{juice}-{size}"
                    
                    ip_weekly = {
                        "id": f"ip-{price_id_counter:04d}",
                        "name": f"{juice.capitalize()} {size}ml Weekly",
                        "description": f"{family.capitalize()} {juice} {size}ml - Weekly (6 days)",
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
                    }
                    item_prices.append(ip_weekly)
                    price_id_counter += 1
                    
                    # Monthly (24 days aka 4 weeks): price * 24
                    monthly_price = base_price * 24
                    ip_monthly = {
                        "id": f"ip-{price_id_counter:04d}",
                        "name": f"{juice.capitalize()} {size}ml Monthly",
                        "description": f"{family.capitalize()} {juice} {size}ml - Monthly (4 weeks)",
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
                    }
                    item_prices.append(ip_monthly)
                    price_id_counter += 1
        
        currencies = [{"id": "INR", "prefix": "₹", "exchange_rate": 1.0}]
        
        print(f"Items: {len(items)}")
        print(f"Item Families: {len(item_families)}")
        print(f"Item Prices: {len(item_prices)}")
        print(f"Currencies: {len(currencies)}")
        
        import_result = call_tool("import_product_catalog", {
            "items": items,
            "itemFamilies": item_families,
            "itemPrices": item_prices,
            "currencies": currencies
        })
        print("\n=== IMPORT RESULT ===")
        print(import_result)

    else:
        print(f"Unknown action: {action}")
        print("Usage: python generate_catalog.py [generate|import|manual]")
