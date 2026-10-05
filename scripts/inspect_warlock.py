import numpy as np
from PIL import Image
from scipy import ndimage

p = 'assets/high-res/final-native2k/rig-source-parts-warlock.png'
arr = np.array(Image.open(p))
corners = np.array([arr[5, 5], arr[5, -6], arr[-6, 5], arr[-6, -6]])
bg = np.median(corners, axis=0)
diff = np.sqrt(np.sum((arr.astype(float) - bg)**2, axis=-1))

# What is comp 2: bbox=[80, 86, 972, 1043]?
# The audit says: "02 contains six faces and a label"
# Let's inspect comp 2:
c2 = arr[86:1043, 80:972]
Image.fromarray(c2).save('qa/image-v3-repair-20261004/rig_inspect/warlock_c2.png')

# What is comp 1: bbox=[1042, 108, 1999, 962]?
c1 = arr[108:962, 1042:1999]
Image.fromarray(c1).save('qa/image-v3-repair-20261004/rig_inspect/warlock_c1.png')

# What is comp 3: bbox=[1088, 1087, 1890, 1890]?
c3 = arr[1087:1890, 1088:1890]
Image.fromarray(c3).save('qa/image-v3-repair-20261004/rig_inspect/warlock_c3.png')

# What is comp 4: bbox=[48, 824, 962, 2045]?
c4 = arr[824:2045, 48:962]
Image.fromarray(c4).save('qa/image-v3-repair-20261004/rig_inspect/warlock_c4.png')

# Inside c2, how many distinct faces are there?
# Let's inspect sub-regions of c2:
c2_diff = diff[86:1043, 80:972]
labeled, num = ndimage.label(c2_diff > 30)
sizes = ndimage.sum(c2_diff > 30, labeled, range(1, num + 1))
print("Warlock c2 sub-components > 1000px:")
for i, sz in enumerate(sizes):
    if sz > 1000:
        ys, xs = np.where(labeled == (i+1))
        print(f"  sub {i+1}: sz={sz:.0f}, bbox=[{xs.min()}, {ys.min()}, {xs.max()}, {ys.max()}] w={xs.max()-xs.min()} h={ys.max()-ys.min()}")
