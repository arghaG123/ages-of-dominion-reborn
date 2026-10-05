import json
import os
import glob
from PIL import Image

manifest_path = "docs/plan/IMAGE-LATER73-EXECUTION-MANIFEST-2026-10-04.json"
with open(manifest_path, "r", encoding="utf-8") as f:
    manifest = json.load(f)

print(f"Total manifest items: {len(manifest['items'])}")

# Check mapping to files in assets/high-res/final-native2k
final_dir = "assets/high-res/final-native2k"
for idx, item in enumerate(manifest['items']):
    # Find matching file in final_dir
    item_id = item['id']
    # Candidate filenames could be {item_id}.png
    expected_file = os.path.join(final_dir, f"{item_id}.png")
    exists = os.path.exists(expected_file)
    print(f"[{idx+1:02d}] {item['group']} | ID: {item_id} | File exists: {exists}")
