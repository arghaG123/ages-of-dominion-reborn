import os
from PIL import Image
import numpy as np

p1 = 'assets/production/production-07-20261003/images/09-troop-iron-melee.png'
p2 = 'assets/production/production-17-20261003/images/10-attacker-industrial-heavy.png'

for name, path in [('legionary', p1), ('steam_walker', p2)]:
    im = Image.open(path).convert('RGB')
    arr = np.array(im, dtype=float)
    # Check magenta background: where r > 200, g < 60, b > 200
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    # Standard chroma key for magenta
    # Foreground has low magenta similarity
    mag_dist = np.sqrt((r - 255)**2 + g**2 + (b - 255)**2)
    # Check bottom 200 rows for sole pixels
    bot = arr[-200:, :]
    print(f"\n=== {name} ({im.size}) ===")
    print(f"Min magenta dist: {mag_dist.min():.1f}, max: {mag_dist.max():.1f}")
    # Inspect pixels with magenta fringe (where r > g + 30 and b > g + 30)
    pinkish = (r > g + 30) & (b > g + 30)
    print(f"Pinkish pixels total: {np.sum(pinkish)}")
