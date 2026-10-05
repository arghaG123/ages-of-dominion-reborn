from PIL import Image
import numpy as np

# Let's inspect the visual features of old webp rivals and new 2K rivals
# For example, average colors, edge density, dominant colors, etc.
for i in range(1, 7):
    old_p = f"c:/dev/ages-of-dominion/public/art/rival-{i}.webp"
    im = Image.open(old_p)
    # Check if alpha has transparent areas
    arr = np.array(im)
    alpha = arr[:, :, 3]
    print(f"Old rival-{i}.webp: alpha min={alpha.min()}, max={alpha.max()}, non-transparent fraction={(alpha > 10).mean():.2f}")
