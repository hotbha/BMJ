import sys, json
from collections import Counter

with open('chargebee_catalog.json') as f:
    data = json.load(f)

print('=== Item Families ===')
for fam in data['itemFamilies']:
    print(f'  {fam["id"]}: {fam["name"]} - {fam.get("description","")}')

print()
print('=== Items per Family ===')
fam_counts = Counter(i['item_family_id'] for i in data['items'])
for k, v in fam_counts.items():
    print(f'  {k}: {v} items')
print(f'  Total: {len(data["items"])} items')

print()
print('=== Items per Category (sample IDs) ===')
for fam_id in ['delight', 'signature', 'premium']:
    items = [i for i in data['items'] if i['item_family_id'] == fam_id]
    print(f'  {fam_id}:')
    for item in items[:3]:
        print(f'    {item["id"]} - {item["name"]}')
    if len(items) > 3:
        print(f'    ... and {len(items)-3} more')

prices = data.get('itemPrices', data.get('item_prices', []))
print()
print(f'=== Item Prices: {len(prices)} total ===')
price_fam_counts = Counter(p.get('item_family_id', 'unknown') for p in prices)
for k, v in price_fam_counts.items():
    print(f'  {k}: {v} prices')

print()
print('=== Sample Prices ===')
for p in prices[:3]:
    print(json.dumps(p, indent=2))
    print()