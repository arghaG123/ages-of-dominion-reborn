from PIL import Image
import numpy as np

for cname in ['warlock_c1', 'warlock_c3', 'warlock_c4']:
    im = Image.open(f'qa/image-v3-repair-20261004/rig_inspect/{cname}.png')
    print(f"{cname}: size={im.size}")

# Let's inspect what is in c1, c3, c4:
# c1: [108:962, 1042:1999] (w=957, h=854)
# c3: [1087:1890, 1088:1890] (w=802, h=803)
# c4: [824:2045, 48:962] (w=914, h=1221)
