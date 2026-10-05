import numpy as np
from PIL import Image
from scipy import ndimage

# Let's inspect Knight, Warlock, Mage, Necromancer, Barbarian, Ranger, Paladin, Healer
# to find exact boxes and identify each part

def inspect_knight():
    print("=== INSPECT KNIGHT ===")
    p = 'assets/high-res/final-native2k/rig-source-parts-knight.png'
    arr = np.array(Image.open(p))
    mag = (arr[:,:,0] > 180) & (arr[:,:,1] < 70) & (arr[:,:,2] > 180)
    # Let's inspect the top half vs bottom half
    # In top half (y < 1000):
    top_mask = (~mag) & (np.arange(2048)[:, None] < 1000)
    labeled, num = ndimage.label(top_mask)
    sizes = ndimage.sum(top_mask, labeled, range(1, num + 1))
    for i, sz in enumerate(sizes):
        if sz > 5000:
            ys, xs = np.where(labeled == (i+1))
            print(f"Top piece {i+1}: sz={sz:.0f}, bbox=[{xs.min()}, {ys.min()}, {xs.max()}, {ys.max()}] w={xs.max()-xs.min()} h={ys.max()-ys.min()}")

inspect_knight()
