import os, json
from PIL import Image
import numpy as np
from scipy import ndimage

ROOT = 'C:/dev/ages-of-dominion-reborn'
m = json.load(open(f'{ROOT}/docs/plan/IMAGE-LATER73-EXECUTION-MANIFEST-2026-10-04.json'))
army_items = [i for i in m['items'] if i['group'] == '2K-LATER-C-ARMY-24']

def inspect_actor(item_id):
    p = f'{ROOT}/assets/high-res/final-native2k/{item_id}.png'
    im = Image.open(p).convert('RGB')
    arr = np.array(im, dtype=float)
    h, w, _ = arr.shape
    corners = np.array([arr[5, 5], arr[5, -6], arr[-6, 5], arr[-6, -6]])
    bg = np.median(corners, axis=0)
    
    # Check if magenta
    is_magenta = (bg[0] > 180 and bg[1] < 70 and bg[2] > 180)
    # Check if blue
    is_blue = (bg[0] < 70 and bg[1] < 100 and bg[2] > 80)
    # Check if pink
    is_pink = (bg[0] > 180 and bg[1] > 100 and bg[2] > 160 and bg[1] < bg[0])
    
    print(f"{item_id:25}: bg={bg.astype(int).tolist()} magenta={is_magenta} blue={is_blue} pink={is_pink}")

for a in army_items:
    inspect_actor(a['id'])

for m_id in ['hero-mount-horse', 'hero-mount-motor-transport', 'hero-mount-future-transport', 'knight-mounted-master']:
    inspect_actor(m_id)
