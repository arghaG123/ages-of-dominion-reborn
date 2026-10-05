import numpy as np
from PIL import Image
from scipy import ndimage

p = 'assets/high-res/final-native2k/rig-source-parts-knight.png'
arr = np.array(Image.open(p))

# Let's inspect parts in y in [1000:1700]
mid_y = arr[1000:1700, :]
mag = (mid_y[:,:,0] > 180) & (mid_y[:,:,1] < 70) & (mid_y[:,:,2] > 180)
labeled, num = ndimage.label(~mag)
sizes = ndimage.sum(~mag, labeled, range(1, num + 1))
for i, sz in enumerate(sizes):
    if sz > 5000:
        ys, xs = np.where(labeled == (i+1))
        print(f"Mid piece {i+1}: sz={sz:.0f}, bbox=[{xs.min()}, {ys.min()+1000}, {xs.max()}, {ys.max()+1000}] w={xs.max()-xs.min()} h={ys.max()-ys.min()}")
