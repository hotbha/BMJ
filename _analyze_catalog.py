import json

with open(r'x:\BMJ\chargebee_catalog.json') as f:
    data = json.load(f)

if isinstance(data, list):
    print(f"List with {len(data)} items")
    for i, item in enumerate(data):
        if isinstance(item, dict) and 'item' in item:
            it = item['item']
            fid = it.get('item_family_id', 'N/A')
            name = it.get('name', 'N/A')
            status = it.get('status', 'N/A')
            iid = it.get('id', 'N/A')
            metadata = it.get('meta_data', {})
            print(f"  [{i}] id={iid} | name={name} | family_id={fid} | status={status} | metadata={metadata}")
elif isinstance(data, dict):
    print("Dict with keys:", list(data.keys()))
    for k, v in data.items():
        if isinstance(v, list):
            print(f"  {k}: list with {len(v)} items")
            for i, item in enumerate(v[:5]):
                if isinstance(item, dict):
                    print(f"    [{i}] {json.dumps(item, indent=2)[:200]}")