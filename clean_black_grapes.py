import json, re, sys, os

def count_matches(data_str):
    return len(re.findall(r'black.grapes', data_str, re.I))

def remove_black_grapes(obj):
    """Recursively traverse JSON and remove dicts whose id/name contains 'black-grapes'."""
    removed = 0
    if isinstance(obj, dict):
        skip = False
        if any('black-grapes' in str(v).lower() for k, v in obj.items() if k in ('id', 'name', 'item_id')):
            skip = True
        if not skip:
            new = {}
            for k, v in obj.items():
                new[k], r = remove_black_grapes(v)
                removed += r
            return new, removed
        else:
            return None, 1
    elif isinstance(obj, list):
        new_list = []
        for item in obj:
            cleaned, r = remove_black_grapes(item)
            removed += r
            if cleaned is not None:
                new_list.append(cleaned)
        return new_list, removed
    return obj, removed

files = [
    ('chargebee_catalog.json', True),
    ('batch1_generic_plans.json', True),
    ('batch2_juice_plans.json', True),
    ('chargebee_items_payload.json', True),
]

total = 0
for fn, rewrite in files:
    if not os.path.exists(fn):
        print(f"{fn}: NOT FOUND — skipping")
        continue
    with open(fn) as f:
        data = json.load(f)
    before = count_matches(json.dumps(data))
    if before == 0:
        print(f"{fn}: 0 matches — no changes needed")
        continue
    cleaned, removed = remove_black_grapes(data)
    total += removed
    with open(fn, 'w') as f:
        json.dump(cleaned, f, indent=2)
    print(f"{fn}: Removed {removed} entries with 'black-grapes'")

print(f"\nTotal: Removed {total} entries across all files")