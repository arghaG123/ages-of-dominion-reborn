import json
from pathlib import Path

ROOT = Path(".")
inv = json.loads((ROOT / "docs/plan/image-production/full-purchase-inventory.json").read_text(encoding="utf-8"))

print("=== INVENTORY BATCHES MAPPING ===")
for b in inv.get("batches", []):
    print(f"Batch {b.get('batch', b.get('id'))}: {list(b.keys())}")
    if "itemIds" in b:
        print(f"  Count: {len(b['itemIds'])}")
    if "summary" in b or "categorySummary" in b or "categories" in b:
        print(f"  Summary: {b.get('summary') or b.get('categorySummary') or b.get('categories')}")


print("\n=== BATCH 04 MANIFEST ===")
m4 = json.loads((ROOT / "docs/plan/image-production/batch-04-manifest.json").read_text(encoding="utf-8"))
for i, item in enumerate(m4["items"]):
    print(f"{i+1:02d}: {item['id']} (guide: {item.get('guide')}, style: {item.get('styleReference')})")

print("\n=== TOTAL UNIQUE REQUESTED ACROSS 01-04 ===")
requested = {}
for b in range(1, 5):
    p = ROOT / f"docs/plan/image-production/batch-{b:02d}-manifest.json"
    if p.exists():
        data = json.loads(p.read_text(encoding="utf-8"))
        for it in data["items"]:
            requested.setdefault(it["id"], []).append(b)

print("\n=== INVENTORY BATCH ALLOCATIONS ===")
items = inv["items"]
for b in range(1, 17):
    b_items = [it for it in items if it.get("batch") == b]
    ids = [it["id"] for it in b_items]
    print(f"Batch {b:02d}: {len(b_items)} items: {ids[:3]} ... {ids[-3:] if len(ids)>3 else []}")

# Check which items from inventory have NOT been requested in batches 1-4
all_requested_ids = set(requested.keys())
unrequested_items = [it for it in items if it["id"] not in all_requested_ids]
print(f"\nTotal inventory items: {len(items)}")
print(f"Total unrequested items from baseline: {len(unrequested_items)}")

# Count unrequested items by category
unreq_cats = {}
for it in unrequested_items:
    unreq_cats[it["category"]] = unreq_cats.get(it["category"], 0) + 1
print("Unrequested by category:", unreq_cats)

print("\n=== ALL BUILDINGS IN INVENTORY ===")
buildings = [it for it in items if it["category"] == "buildings"]
print("\n=== BATCHES 5-8 IN INVENTORY ===")
for b in [5, 6, 7, 8]:
    b_items = [it for it in items if it.get('batch') == b]
    print(f"\n--- Batch {b} ({len(b_items)} items) ---")
    for it in b_items:
        print(f"  {it['position']:02d}: {it['id']:30s} ({it['category']})")





