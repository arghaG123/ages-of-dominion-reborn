import numpy as np
from PIL import Image

p = 'assets/high-res/final-native2k/rig-source-parts-knight.png'
im = Image.open(p)
arr = np.array(im)

# Let's inspect where parts are by dividing into a 4x4 or 5x5 grid and seeing what is in each cell
# Native is 2048x2048.
# Let's tile into 512x512 blocks (4x4 = 16 blocks):
for r in range(4):
    for c in range(4):
        block = arr[r*512:(r+1)*512, c*512:(c+1)*512]
        mag = (block[:,:,0] > 180) & (block[:,:,1] < 60) & (block[:,:,2] > 180)
        fg_ratio = 1.0 - np.mean(mag)
        print(f"Block ({r},{c}) [y={r*512}:{(r+1)*512}, x={c*512}:{(c+1)*512}]: fg_ratio={fg_ratio:.2f}")
