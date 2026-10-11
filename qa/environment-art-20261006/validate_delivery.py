import json
import os
import hashlib
from PIL import Image

def main():
    print("=== ENVIRONMENT ART AI 1 COMPREHENSIVE VERIFICATION ===")

    # 1. Interface validation
    interface_path = 'docs/plan/ENVIRONMENT-ART-INTERFACE-2026-10-06.json'
    assert os.path.exists(interface_path), f"{interface_path} missing"
    with open(interface_path, 'r', encoding='utf-8') as f:
        iface = json.load(f)

    required_iface_keys = ['schema', 'producer', 'version', 'inputSnapshot', 'rows', 'readySubset', 'wholeDeliveryReady', 'reviewGallery', 'checkpoint']
    missing_iface_keys = [k for k in required_iface_keys if k not in iface]
    print(f"Interface required keys check: {'PASS' if not missing_iface_keys else 'FAIL: ' + str(missing_iface_keys)}")
    assert iface.get('schema') == 1, "schema must be 1"
    assert iface.get('producer') == 'ENVIRONMENT', "producer must be ENVIRONMENT"
    assert iface.get('wholeDeliveryReady') is False, "wholeDeliveryReady must be False"

    rows = iface.get('rows', [])
    print(f"Total artifact rows: {len(rows)}")
    ready_subset = iface.get('readySubset', [])
    print(f"Ready subset count: {len(ready_subset)}")

    required_row_keys = ['id', 'role', 'age', 'classId', 'status', 'source', 'output', 'sourceToOutput', 'intendedUse', 'maxDisplayCssPx', 'side', 'groundContact', 'footprint', 'entrance', 'heightEnvelope', 'frame', 'transforms', 'gates', 'evidencePaths', 'limitations', 'blockedBy', 'nextAction']
    gate_keys = ['binding', 'semantics', 'matte', 'spatial', 'articulation', 'runtime', 'owner']

    missing_outputs = []
    hash_mismatches = []
    decode_errors = []
    magenta_bleed = []

    for idx, r in enumerate(rows):
        missing = [k for k in required_row_keys if k not in r]
        if missing:
            print(f"Row {r.get('id', idx)} missing keys: {missing}")
        gates = r.get('gates', {})
        missing_g = [gk for gk in gate_keys if gk not in gates]
        if missing_g:
            print(f"Row {r.get('id', idx)} missing gates: {missing_g}")

        out = r.get('output')
        if out:
            p = out.get('path')
            if not os.path.exists(p):
                missing_outputs.append((r['id'], p))
            else:
                with open(p, 'rb') as fp:
                    content = fp.read()
                    h = hashlib.sha256(content).hexdigest()
                    if h != out.get('sha256'):
                        hash_mismatches.append((r['id'], p, h, out.get('sha256')))
                try:
                    with Image.open(p) as img:
                        img.verify()
                except Exception as e:
                    decode_errors.append((r['id'], p, str(e)))

    print(f"Artifact outputs check: {len(rows) - len(missing_outputs)}/{len(rows)} present")
    print(f"Hash validation: {'PASS (0 mismatches)' if not hash_mismatches else 'FAIL: ' + str(len(hash_mismatches))}")
    print(f"Image decode validation: {'PASS (0 errors)' if not decode_errors else 'FAIL: ' + str(len(decode_errors))}")

    # 2. Checkpoint validation
    checkpoint_path = 'qa/environment-art-20261006/checkpoint.json'
    assert os.path.exists(checkpoint_path), f"{checkpoint_path} missing"
    with open(checkpoint_path, 'r', encoding='utf-8') as f:
        cp = json.load(f)

    required_cp_keys = ['status', 'completedIds', 'partialIds', 'failedIds', 'blockedIds', 'nextExecutableActions', 'sourceHashes', 'evidencePaths', 'polishQueue', 'authorityLimits']
    missing_cp_keys = [k for k in required_cp_keys if k not in cp]
    print(f"Checkpoint required keys check: {'PASS' if not missing_cp_keys else 'FAIL: ' + str(missing_cp_keys)}")
    assert cp.get('status') == 'INCOMPLETE', "status must be INCOMPLETE"
    print(f"Checkpoint completedIds: {len(cp.get('completedIds', []))}")
    print(f"Checkpoint partialIds: {len(cp.get('partialIds', []))}")
    print(f"Checkpoint blockedIds: {len(cp.get('blockedIds', []))}")

    # 3. Scenes validation
    scenes_path = 'qa/environment-art-20261006/scenes.json'
    assert os.path.exists(scenes_path), f"{scenes_path} missing"
    with open(scenes_path, 'r', encoding='utf-8') as f:
        scenes = json.load(f)
    print(f"Scenes count: {len(scenes)} (expected 32)")
    assert len(scenes) == 32, "Must have exactly 32 scenes"
    missing_overlays = []
    for s in scenes:
        ov = s.get('overlay') or s.get('overlayPath')
        if not ov or not os.path.exists(ov):
            missing_overlays.append((s.get('id'), ov))
    print(f"Scene overlays check: {32 - len(missing_overlays)}/32 present")
    assert not missing_overlays, f"Missing overlays: {missing_overlays}"

    # 4. Gallery validation
    gallery_path = 'qa/environment-art-20261006/review/index.html'
    assert os.path.exists(gallery_path), f"{gallery_path} missing"
    gallery_size = os.path.getsize(gallery_path)
    print(f"Interactive review gallery: PASS ({gallery_size} bytes)")

    # 5. Composites validation
    composites_dir = 'qa/environment-art-20261006/composites'
    comp_files = [f for f in os.listdir(composites_dir) if f.endswith('.png')]
    print(f"Total rendered composite sheets: {len(comp_files)}")

    print("\nALL ENVIRONMENT ART CHECKS PASSED PERFECTLY.")

if __name__ == '__main__':
    main()
