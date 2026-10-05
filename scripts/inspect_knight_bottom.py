import numpy as np
from PIL import Image
from scipy import ndimage

p = 'assets/high-res/final-native2k/rig-source-parts-knight.png'
arr = np.array(Image.open(p))

# Let's inspect bottom left [1080:2048, 0:1024] and bottom right [1080:2048, 1024:2048]
bl = arr[1080:2048, 0:1024]
br = arr[1080:2048, 1024:2048]

corners = np.array([arr[5, 5], arr[5, -6], arr[-6, 5], arr[-6, -6]])
bg = np.median(corners, axis=0)
print('Knight bg:', bg)

# In the bottom half, why did components merge? Is there a grey floor or shadow?
# Let's see the colors in bl:
diff_bl = np.sqrt(np.sum((bl.astype(float) - bg)**2, axis=-1))
print('bl diff min, median, max:', diff_bl.min(), np.median(diff_bl), diff_bl.max())

# Let's test with higher diff thresholds or inspect what is inside bl and br
for thresh in [30, 50, 70, 90]:
    labeled, num = ndimage.label(diff_bl > thresh)
    sizes = ndimage.sum(diff_bl > thresh, labeled, range(1, num + 1))
    big = [sz for sz in sizes if sz > 1500]
    print(f'bl threshold {thresh}: {len(big)} components > 1500px, max sz={max(sizes) if len(sizes) else 0}')

for thresh in [30, 50, 70, 90]:
    diff_br = np.sqrt(np.sum((br.astype(float) - bg)**2, axis=-1))
    labeled, num = ndimage.label(diff_br > thresh)
    sizes = ndimage.sum(diff_br > thresh, labeled, range(1, num + 1))
    big = [sz for sz in sizes if sz > 1500]
    print(f'br threshold {thresh}: {len(big)} components > 1500px, max sz={max(sizes) if len(sizes) else 0}')
