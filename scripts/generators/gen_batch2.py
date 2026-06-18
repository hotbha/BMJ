import json

families = ["delight", "signature", "premium"]
sizes = ["200ml", "300ml", "500ml"]
juices = {
    "delight": ["mix-punch", "carrot-juice", "colon-cleanser", "beat-the-heat", "winter-special"],
    "signature": ["abc-juice", "pineapple", "amla-juice", "ashguard-juice", "citrus-juice"],
    "premium": ["black-grapes", "antioxidant-juice", "wheatgrass-juice", "coconut-milk", "detox-smoothie"]
}
prices_paise = {
    ("delight", "200ml"): (46100, 169700),
    ("delight", "300ml"): (60900, 218900),
    ("delight", "500ml"): (103900, 366500),
    ("signature", "200ml"): (49200, 184500),
    ("signature", "300ml"): (64600, 233700),
    ("signature", "500ml"): (106400, 415700),
    ("premium", "200ml"): (55400, 204200),
    ("premium", "300ml"): (67000, 243500),
    ("premium", "500ml"): (112500, 440300),
}
juice_names = {
    "mix-punch": "Mix Punch", "carrot-juice": "Carrot Juice", "colon-cleanser": "Colon Cleanser",
    "beat-the-heat": "Beat the Heat", "winter-special": "Winter Special",
    "abc-juice": "ABC Juice", "pineapple": "Pineapple", "amla-juice": "Amla Juice",
    "ashguard-juice": "Ashguard Juice", "citrus-juice": "Citrus Juice",
    "black-grapes": "Black Grapes", "antioxidant-juice": "Antioxidant Juice",
    "wheatgrass-juice": "Wheatgrass Juice", "coconut-milk": "Coconut Milk",
    "detox-smoothie": "Detox Smoothie"
}
family_names = {"delight": "Delight", "signature": "Signature", "premium": "Premium"}

items = []
item_prices = []

for family in families:
    for size in sizes:
        for juice in juices[family]:
            item_id = f"bmj-{family}-{juice}-{size}"
            name = f"{family_names[family]} {juice_names[juice]} {size}"
            desc = f"{family_names[family]} - {juice_names[juice]} - {size}"
            items.append({
                "id": item_id, "name": name, "description": desc,
                "type": "plan", "item_family_id": family, "metered": False,
                "metadata": {
                    "plan_type": "juice_specific", "family": family, "size": size,
                    "default_juice": juice, "has_bottle_deposit": True,
                    "bottle_count_weekly": 6, "bottle_count_monthly": 24
                }
            })
            w_price, m_price = prices_paise[(family, size)]
            item_prices.append({
                "id": f"{item_id}-weekly", "name": f"{name} Weekly",
                "description": f"{desc} - Weekly", "pricing_model": "flat_fee",
                "item_id": item_id, "item_family_id": family,
                "price": w_price, "currency_code": "INR",
                "period": 1, "period_unit": "week", "trial_period": 0, "trial_period_unit": "day", "tiers": []
            })
            item_prices.append({
                "id": f"{item_id}-monthly", "name": f"{name} Monthly",
                "description": f"{desc} - Monthly", "pricing_model": "flat_fee",
                "item_id": item_id, "item_family_id": family,
                "price": m_price, "currency_code": "INR",
                "period": 1, "period_unit": "month", "trial_period": 0, "trial_period_unit": "day", "tiers": []
            })

payload = {
    "items": items,
    "itemFamilies": [
        {"id": "delight", "name": "Delight", "description": "Entry-level juice subscription category"},
        {"id": "signature", "name": "Signature", "description": "Mid-range juice subscription category"},
        {"id": "premium", "name": "Premium", "description": "Premium juice subscription category"}
    ],
    "itemPrices": item_prices,
    "currencies": [{"currency_code": "INR"}]
}

with open("batch2_juice_plans.json", "w") as f:
    json.dump(payload, f, indent=2)

print(f"Generated: {len(items)} items, {len(item_prices)} item prices")