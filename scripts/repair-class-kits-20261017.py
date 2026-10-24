import os, glob, json, hashlib, cv2
from PIL import Image
import numpy as np

def clean_studio_border(arr):
    h, w = arr.shape[:2]
    seed_points = []
    for x in range(w):
        for y in [0, h-1]:
            r, g, b, a = arr[y, x]
            if a > 20 and abs(int(r)-int(g)) < 6 and abs(int(g)-int(b)) < 8 and 115 < r < 145:
                seed_points.append((x, y))
    for y in range(h):
        for x in [0, w-1]:
            r, g, b, a = arr[y, x]
            if a > 20 and abs(int(r)-int(g)) < 6 and abs(int(g)-int(b)) < 8 and 115 < r < 145:
                seed_points.append((x, y))
    if not seed_points:
        return arr, 0
    mask = np.zeros((h + 2, w + 2), np.uint8)
    bgr = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
    filled_count = 0
    for sx, sy in seed_points:
        if arr[sy, sx, 3] > 0 and mask[sy+1, sx+1] == 0:
            retval, image, mask, rect = cv2.floodFill(bgr, mask, (sx, sy), (0,0,0), (6,6,6), (6,6,6), cv2.FLOODFILL_MASK_ONLY)
            to_clear = (mask[1:-1, 1:-1] == 1) & (arr[:, :, 3] > 0)
            arr[to_clear, 3] = 0
            filled_count += to_clear.sum()
    return arr, filled_count

def repair_paladin_ancient():
    path = 'assets/derivatives/mock-led-20261016/bodies/eras/class-paladin-ancient.png'
    med_path = 'assets/derivatives/mock-led-20261016/bodies/class-paladin-standing-body.png'
    anc = Image.open(path).convert('RGBA')
    med = Image.open(med_path).convert('RGBA')
    arr_anc = np.array(anc)
    arr_med = np.array(med)
    # clean matte first
    arr_anc, _ = clean_studio_border(arr_anc)
    
    # Combined canvas (1400, 592, 4)
    combined = np.zeros((1400, 592, 4), dtype=np.uint8)
    combined[:1200, :, :] = arr_anc[:1200, :, :]
    # Blend rows 1200 to 1260
    for y in range(1200, 1260):
        t = (y - 1200) / 60.0
        mask_a = arr_anc[y, :, 3] > 20
        combined[y, mask_a, :] = arr_anc[y, mask_a, :]
        mask_m = (~mask_a) & (arr_med[y, :, 3] > 20)
        combined[y, mask_m, :] = arr_med[y, mask_m, :]
    # Below 1260: use the complete legs/boots from paladin standing body
    combined[1260:1400, :, :] = arr_med[1260:1400, :, :]
    
    out = Image.fromarray(combined)
    out.save(path)
    print('Repaired paladin ancient:', out.size)

def repair_paladin_mech():
    path = 'assets/derivatives/mock-led-20261016/bodies/eras/class-paladin-mech.png'
    mech_k_path = 'assets/derivatives/mock-led-20261016/bodies/eras/class-knight-mech.png'
    pm = Image.open(path).convert('RGBA')
    km = Image.open(mech_k_path).convert('RGBA')
    arr_pm = np.array(pm)
    arr_pm, _ = clean_studio_border(arr_pm)
    
    # km size is (541, 1448). Let's extract legs from km (1100 to 1448) and scale to width 580
    legs_h = 1448 - 1100 # 348
    legs = km.crop((0, 1100, 541, 1448)).resize((580, legs_h), Image.Resampling.LANCZOS)
    arr_legs = np.array(legs)
    
    # New height: 1100 + legs_h = 1448
    combined = np.zeros((1448, 580, 4), dtype=np.uint8)
    combined[:1100, :, :] = arr_pm[:1100, :, :]
    for y in range(1100, 1150):
        mask_p = arr_pm[y, :, 3] > 20
        combined[y, mask_p, :] = arr_pm[y, mask_p, :]
        mask_l = (~mask_p) & (arr_legs[y - 1100, :, 3] > 20)
        combined[y, mask_l, :] = arr_legs[y - 1100, mask_l, :]
    combined[1150:1448, :, :] = arr_legs[1150 - 1100:, :, :]
    
    out = Image.fromarray(combined)
    out.save(path)
    print('Repaired paladin mech:', out.size)

def clean_all_mattes():
    for f in sorted(glob.glob('assets/derivatives/mock-led-20261016/bodies/eras/*.png')):
        im = Image.open(f).convert('RGBA')
        arr = np.array(im)
        cleaned, count = clean_studio_border(arr)
        if count > 0:
            Image.fromarray(cleaned).save(f)
            print(f'Cleaned {f}: {count} pixels')

def update_catalog():
    with open('src/data/hero-kit-eras-20261017.json', 'r', encoding='utf-8') as f:
        catalog = json.load(f)
    
    for classId, eras in catalog['classes'].items():
        for eraName, entry in eras.items():
            filePath = entry['file']
            if not os.path.exists(filePath):
                continue
            with open(filePath, 'rb') as bf:
                data = bf.read()
            entry['sha256'] = hashlib.sha256(data).hexdigest()
            entry['bytes'] = len(data)
            im = Image.open(filePath)
            entry['width'] = im.width
            entry['height'] = im.height
            # calculate foot anchor from ground contact
            arr = np.array(im)
            alpha = arr[:, :, 3]
            # bottom row with alpha > 20
            contact_rows = np.where(alpha > 20)[0]
            if len(contact_rows):
                last_y = contact_rows.max()
                foot_y = (last_y + 1) / float(im.height)
                # foot_x is center of mass of contact row
                xs = np.where(alpha[last_y, :] > 20)[0]
                foot_x = float(xs.mean()) / float(im.width) if len(xs) else entry['foot'][0]
                entry['foot'] = [round(foot_x, 6), round(foot_y, 6)]
            print(f'{classId} {eraName}: {entry["width"]}x{entry["height"]}, foot={entry["foot"]}, sha={entry["sha256"][:12]}')
            
    with open('src/data/hero-kit-eras-20261017.json', 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=2)
    print('Updated hero-kit-eras-20261017.json successfully.')

if __name__ == '__main__':
    clean_all_mattes()
    repair_paladin_ancient()
    repair_paladin_mech()
    update_catalog()
