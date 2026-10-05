import os
from PIL import Image
import numpy as np

os.makedirs('qa/image-v3-repair-20261004/rig_inspect', exist_ok=True)

# For each character, let's slice out the main regions and save labeled thumbnails
def inspect_sheet(name):
    p = f'assets/high-res/final-native2k/rig-source-parts-{name}.png'
    im = Image.open(p).convert('RGBA')
    arr = np.array(im)
    h, w, _ = arr.shape
    
    # Save a thumbnail of the entire sheet with grid
    thumb = im.resize((512, 512), Image.Resampling.LANCZOS)
    thumb.save(f'qa/image-v3-repair-20261004/rig_inspect/{name}_full.png')
    print(f"Saved {name}_full.png")

for name in ['knight', 'ranger', 'warlock', 'mage', 'necromancer', 'barbarian', 'paladin', 'healer']:
    inspect_sheet(name)
