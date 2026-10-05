from PIL import Image
import numpy as np

for name in ['knight', 'ranger', 'warlock', 'mage', 'necromancer', 'barbarian', 'paladin', 'healer']:
    p = f'assets/high-res/final-native2k/rig-source-parts-{name}.png'
    im = Image.open(p)
    arr = np.array(im)
    for r in range(4):
        for c in range(4):
            block = arr[r*512:(r+1)*512, c*512:(c+1)*512]
            Image.fromarray(block).resize((256, 256)).save(
                f'qa/image-v3-repair-20261004/rig_inspect/{name}_b{r}_{c}.png'
            )
print("Saved all 16 blocks for all 8 characters")
