import os, json
from PIL import Image
import numpy as np

ROOT = 'C:/dev/ages-of-dominion-reborn'
m = json.load(open(f'{ROOT}/docs/plan/IMAGE-LATER73-EXECUTION-MANIFEST-2026-10-04.json'))
hero_items = [i for i in m['items'] if i['group'] == '2K-LATER-A-HERO-32']
rival_items = [i for i in m['items'] if 'rival' in i['id']]
all_portraits = hero_items + rival_items

print(f"Total portraits to check: {len(all_portraits)}")

def measure_portrait(iid):
    p = f'{ROOT}/assets/high-res/final-native2k/{iid}.png'
    im = Image.open(p).convert('RGB')
    arr = np.array(im, dtype=float)
    h, w, _ = arr.shape
    
    gray = np.array(im.convert('L'), dtype=float)
    gy, gx = np.gradient(gray)
    grad = np.sqrt(gx**2 + gy**2)
    
    # In upper 50% (first 1024 lines), find where subject head starts
    mid_grad = grad[:1024, 300:1748]
    row_energy = np.mean(mid_grad > 18.0, axis=1)
    
    head_top = 0
    for y in range(0, 1000):
        if row_energy[y] > 0.035:
            head_top = max(0, y - 20)
            break
            
    # Measure horizontal center of head between head_top and head_top + 600
    head_zone = grad[head_top:min(1024, head_top + 600), :]
    col_energy = np.mean(head_zone > 18.0, axis=0)
    sig_cols = np.where(col_energy > 0.05)[0]
    if len(sig_cols) > 0:
        head_cx = int(np.median(sig_cols))
    else:
        head_cx = 1024
        
    crop_size = 1400
    # Headroom of 50-60 pixels above head_top
    y1 = max(0, head_top - 60)
    if y1 + crop_size > 2048:
        y1 = 2048 - crop_size
    y2 = y1 + crop_size
    
    x1 = max(0, min(2048 - crop_size, head_cx - crop_size // 2))
    x2 = x1 + crop_size
    
    return {
        'id': iid,
        'headTopY': head_top,
        'headCenterX': head_cx,
        'cropBox': [int(x1), int(y1), int(x2), int(y2)],
        'headroom': int(head_top - y1)
    }

results = []
for item in all_portraits:
    res = measure_portrait(item['id'])
    results.append(res)
    print(f"{res['id']:30}: headTop={res['headTopY']:3d}, cx={res['headCenterX']:4d}, cropBox={res['cropBox']}, headroom={res['headroom']:2d}")

with open(f'{ROOT}/qa/offline-controls-repair-20261004/calibrated-portrait-landmarks.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\nSaved calibrated landmarks to qa/offline-controls-repair-20261004/calibrated-portrait-landmarks.json")
