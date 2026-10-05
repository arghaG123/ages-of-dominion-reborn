import os, json
from PIL import Image
import numpy as np
from scipy import ndimage

ROOT = 'C:/dev/ages-of-dominion-reborn'
m = json.load(open(f'{ROOT}/docs/plan/IMAGE-LATER73-EXECUTION-MANIFEST-2026-10-04.json'))
army_items = [i for i in m['items'] if i['group'] == '2K-LATER-C-ARMY-24']
mount_items = [i for i in m['items'] if 'mount' in i['id'] or i['id'] == 'knight-mounted-master']

print(f"Army items: {len(army_items)}, Mount items: {len(mount_items)}")

for item in army_items + mount_items:
    iid = item['id']
    p = f'{ROOT}/assets/high-res/final-native2k/{iid}.png'
    if not os.path.exists(p):
        print(f"MISSING: {iid}")
        continue
    im = Image.open(p)
    arr = np.array(im)
    corners = np.array([arr[10, 10], arr[10, -11], arr[-11, 10], arr[-11, -11]])
    # check corner color
    c_mean = corners.mean(axis=0)
    print(f"{iid:28}: size={im.size}, cornerRGB={c_mean[:3].astype(int).tolist()}, mode={im.mode}")
