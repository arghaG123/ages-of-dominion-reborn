import numpy as np
from PIL import Image

p = 'assets/high-res/final-native2k/rig-source-parts-knight.png'
arr = np.array(Image.open(p))
bot = arr[1000:, :]

# Let's inspect sub-blocks of the bottom half:
# [1000:1500, 0:500], [1000:1500, 500:1000], [1000:1500, 1000:1500], [1000:1500, 1500:2000]
# [1500:2048, 0:500], [1500:2048, 500:1000], [1500:2048, 1000:1500], [1500:2048, 1500:2000]

coords = [
    ('b00', 1000, 1500, 0, 500),
    ('b01', 1000, 1500, 500, 1000),
    ('b02', 1000, 1500, 1000, 1500),
    ('b03', 1000, 1500, 1500, 2048),
    ('b10', 1500, 2048, 0, 500),
    ('b11', 1500, 2048, 500, 1000),
    ('b12', 1500, 2048, 1000, 1500),
    ('b13', 1500, 2048, 1500, 2048),
]

for label, y1, y2, x1, x2 in coords:
    sub = arr[y1:y2, x1:x2]
    # Check median color
    med = np.median(sub.reshape(-1, 3), axis=0)
    print(f"{label} [{y1}:{y2}, {x1}:{x2}]: median={med}")
