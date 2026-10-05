import os, json

p = "assets/derivatives/rigs/parts_manifest.json"
if os.path.exists(p):
    with open(p) as f:
        data = json.load(f)
    print("Classes in parts_manifest.json:", list(data.keys()))
    for k, v in data.items():
        print(f"\n=== {k} (count={v.get('partsCount')}, status={v.get('sheetStatus')}) ===")
        for pinfo in v.get('parts', []):
            bbox = pinfo.get('tightBBoxNative') or pinfo.get('tightBBox')
            print(f"  part {pinfo.get('partIndex'):02d}: {pinfo.get('partName')} bbox={bbox} pivot={pinfo.get('jointPivotLocal')} ({pinfo.get('jointPivotName')})")
