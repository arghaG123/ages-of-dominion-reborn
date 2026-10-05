import numpy as np
from PIL import Image

im = Image.open('qa/image-v3-repair-20261004/rig_inspect/warlock_c2.png')
arr = np.array(im)
h, w, _ = arr.shape
print(f"warlock_c2 shape: {w}x{h}")

# The 6 faces in c2: are they in 2 rows x 3 cols or 3 rows x 2 cols?
# Let's inspect horizontal and vertical cuts:
# Let's see row sums of difference from grey bg:
bg = np.array([126.5, 126.5, 126.5])
diff = np.sqrt(np.sum((arr.astype(float) - bg)**2, axis=-1))

# Let's divide c2 into a 2x3 or 3x2 grid:
# Let's test 2 rows x 3 cols:
row_h = h // 2
col_w = w // 3
for r in range(2):
    for c in range(3):
        face_block = arr[r*row_h:(r+1)*row_h, c*col_w:(c+1)*col_w]
        Image.fromarray(face_block).save(f'qa/image-v3-repair-20261004/rig_inspect/warlock_face_r{r}_c{c}.png')
print("Saved 6 face blocks of warlock_c2")
