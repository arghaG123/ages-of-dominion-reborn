import numpy as np
from PIL import Image

p = 'assets/high-res/final-native2k/rig-source-parts-knight.png'
arr = np.array(Image.open(p))

# Let's save crops of various sub-regions in knight
crops = {
    'knight_top_left': arr[0:1024, 0:1024],
    'knight_top_right': arr[0:1024, 1024:2048],
    'knight_bot_left': arr[1024:2048, 0:1024],
    'knight_bot_right': arr[1024:2048, 1024:2048]
}

for name, crop in crops.items():
    Image.fromarray(crop).resize((512, 512)).save(f'qa/image-v3-repair-20261004/rig_inspect/{name}.png')

print("Saved knight quadrant crops")
