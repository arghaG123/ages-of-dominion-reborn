import numpy as np
from PIL import Image
from scipy import ndimage

im1 = Image.open('qa/image-v3-repair-20261004/rig_inspect/knight_old_p01.png')
arr1 = np.array(im1)
print('arr1 shape:', arr1.shape)
# Sample corners
print('corners arr1:', arr1[5,5], arr1[5,-6], arr1[-6,5], arr1[-6,-6])
# Let's see if there is magenta or grey floor
# Is there magenta between pieces?
r, g, b = arr1[:,:,0], arr1[:,:,1], arr1[:,:,2]
mag = (r > 180) & (g < 60) & (b > 180)
print('fraction magenta in p01:', np.mean(mag))

# What is connecting the pieces? Let's check non-magenta areas:
# In knight, the background is magenta [255, 0, 255] or grey?
# Earlier we saw Knight bg: [252.5, 2.5, 250.] which IS magenta!
# Why did comp 1 merge?
# Let's see if there's a grey floor connecting them:
# A grey floor would have r approx g approx b.
grey_floor = (np.abs(r.astype(int) - g.astype(int)) < 30) & (np.abs(r.astype(int) - b.astype(int)) < 30) & (r > 50) & (r < 210)
print('fraction grey in p01:', np.mean(grey_floor))

# If we treat both magenta and grey floor as background, how many components are there?
fg1 = (~mag) & (~grey_floor)
labeled, num = ndimage.label(fg1)
sizes = ndimage.sum(fg1, labeled, range(1, num + 1))
big = [(i+1, sz) for i, sz in enumerate(sizes) if sz > 1500]
big.sort(key=lambda x: x[1], reverse=True)
print(f'p01 components without grey floor (>1500px): {len(big)}')
for comp_idx, sz in big:
    mask = (labeled == comp_idx)
    ys, xs = np.where(mask)
    print(f'  comp {comp_idx}: size={sz}, bbox=[{xs.min()},{ys.min()},{xs.max()},{ys.max()}], w={xs.max()-xs.min()}, h={ys.max()-ys.min()}')
