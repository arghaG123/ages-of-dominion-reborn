import os
from PIL import Image
import numpy as np

p = 'assets/high-res/final-native2k/hero-mount-horse.png'
im = Image.open(p).convert('RGB')
arr = np.array(im)
bg = arr[10, 10, :]

# Find top edge of horse for each column x
diff = np.sqrt(np.sum((arr.astype(float) - bg)**2, axis=2))
is_horse = diff > 25.0

top_y = np.zeros(2048)
for x in range(2048):
    ys = np.where(is_horse[:, x])[0]
    top_y[x] = ys.min() if len(ys) > 0 else 2048

# Horse back is typically around x=800..1200
# The saddle is the local minimum in height (i.e. dip between head/neck/withers and rump)
mid_xs = np.arange(800, 1400)
mid_tops = top_y[mid_xs]
# Find the lowest dip (highest y value) on the horse back
saddle_idx = np.argmax(mid_tops)
saddle_x = int(mid_xs[saddle_idx])
saddle_y = int(mid_tops[saddle_idx])

# Hooves: bottom-most y where horse is present
bot_ys = []
for x in range(400, 1800):
    ys = np.where(is_horse[:1875, x])[0]
    if len(ys) > 0:
        bot_ys.append(ys.max())
hoof_y = max(bot_ys)

print(f"Measured Horse:")
print(f"  Saddle Landmark: [{saddle_x}, {saddle_y}]")
print(f"  Hoof Ground Contact Y: {hoof_y}")
