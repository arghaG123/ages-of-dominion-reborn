import numpy as np
from PIL import Image

for cname in ['warlock_c1', 'warlock_c3', 'warlock_c4']:
    im = Image.open(f'qa/image-v3-repair-20261004/rig_inspect/{cname}.png')
    arr = np.array(im)
    # Check dimensions and colors
    print(f"=== {cname} ===")
    print("Dimensions:", arr.shape)
    # Let's inspect sub-regions or what is visible
    # Save a half-size thumbnail
    im.resize((im.width // 2, im.height // 2)).save(f'qa/image-v3-repair-20261004/rig_inspect/{cname}_thumb.png')
