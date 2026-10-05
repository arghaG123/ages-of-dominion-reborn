import numpy as np
from PIL import Image

p = 'assets/high-res/final-native2k/rig-source-parts-knight.png'
arr = np.array(Image.open(p))

# In the bottom half (y >= 1000), let's inspect the colors and find why they merged
bot = arr[1000:, :]
# Let's see rows and columns of bottom half
# Is there a grid separating the pieces?
# Let's look at horizontal and vertical projections of non-magenta pixels
mag = (bot[:,:,0] > 180) & (bot[:,:,1] < 70) & (bot[:,:,2] > 180)
print("Bottom half fraction non-magenta:", 1.0 - np.mean(mag))

# Let's save an image of bottom half where non-magenta is shown and magenta is black
viz = np.zeros_like(bot)
viz[~mag] = bot[~mag]
Image.fromarray(viz).resize((512, 256)).save('qa/image-v3-repair-20261004/rig_inspect/knight_bot_nonmag.png')
print("Saved knight_bot_nonmag.png")
