import json

for fname in ['native4k-first32-delivery-manifest.json', 'final-native4k-manifest.json']:
    p = f'docs/plan/image-production/{fname}'
    data = json.load(open(p))
    print(f"=== {fname} ===")
    print("Keys:", list(data.keys()))
    if isinstance(data, dict):
        for k in data:
            if isinstance(data[k], list):
                print(f"  {k}: list of len {len(data[k])}")
                if len(data[k]) > 0 and isinstance(data[k][0], dict):
                    print("    sample item keys:", list(data[k][0].keys()))
                    # print first item id
                    print("    first item id:", data[k][0].get('id') or data[k][0].get('itemId'))
            elif isinstance(data[k], dict):
                print(f"  {k}: dict with keys {list(data[k].keys())[:5]}")
