import numpy as np
from PIL import Image
from scipy import ndimage

p = 'assets/high-res/final-native2k/rig-source-parts-knight.png'
im = Image.open(p)
arr = np.array(im)

# What are the parts in knight?
# The audit specifically says:
# "Knight 01 is multiple greaves, 02 arms/weapons on a floor, 05 a shield misnamed head, 08 a shoulder misnamed head."
# Let's inspect the bboxes of the original components that were extracted:
# comp 1 was bbox=[1097, 1100, 2027, 2027] (the old part 01: multiple greaves)
# comp 2 was bbox=[37, 1084, 984, 2027] (the old part 02: arms/weapons on a floor)
# comp 3 was bbox=[1329, 130, 1775, 971] (the old part 05: shield misnamed head)
# comp 9 was bbox=[1683, 130, 1929, 425] (the old part 08: shoulder misnamed head)

print("Original part 01: [1097, 1100, 2027, 2027]")
print("Original part 02: [37, 1084, 984, 2027]")

# Let's see what is inside [1097:2027, 1100:2027]!
# Why did it merge? Is there a grey floor connecting them?
part1_crop = arr[1100:2027, 1097:2027]
part2_crop = arr[1084:2027, 37:984]

Image.fromarray(part1_crop).save('qa/image-v3-repair-20261004/rig_inspect/knight_old_p01.png')
Image.fromarray(part2_crop).save('qa/image-v3-repair-20261004/rig_inspect/knight_old_p02.png')

# Let's inspect the connected components inside part1_crop if we remove the floor or find components:
# What colors are in part1_crop?
# Let's find out what the floor color is!
print("knight_old_p01.png and p02 saved")
