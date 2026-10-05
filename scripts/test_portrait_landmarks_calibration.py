import os, json
from pathlib import Path
from PIL import Image
import numpy as np

ROOT = Path('C:/dev/ages-of-dominion-reborn')
m = json.load(open(ROOT / 'docs/plan/IMAGE-LATER73-EXECUTION-MANIFEST-2026-10-04.json'))
hero_items = [i for i in m['items'] if i['group'] == '2K-LATER-A-HERO-32']
rival_items = [i for i in m['items'] if 'rival' in i['id']]
all_portraits = hero_items + rival_items

def measure_portrait(iid):
    p = ROOT / f'assets/high-res/final-native2k/{iid}.png'
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
        'cropBox': [x1, y1, x2, y2]
    }

crops = [measure_portrait(item['id']) for item in all_portraits]
for c in crops:
    print(f"{c['id']:30}: headTop={c['headTopY']:3d}, cx={c['headCenterX']:4d}, crop={c['cropBox']}")
