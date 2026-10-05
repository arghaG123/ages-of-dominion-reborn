from PIL import Image
import numpy as np

# Inspect RGB dominant colors and bounding boxes of old rivals
for i in range(1, 7):
    old_p = f"c:/dev/ages-of-dominion/public/art/rival-{i}.webp"
    im = Image.open(old_p)
    arr = np.array(im)
    alpha = arr[:, :, 3]
    ys, xs = np.where(alpha > 20)
    rgb = arr[:, :, :3]
    fg_rgb = rgb[alpha > 20]
    mean_rgb = fg_rgb.mean(axis=0)
    print(f"Old rival-{i}: bbox=({xs.min()},{ys.min()},{xs.max()},{ys.max()}), mean_rgb=({mean_rgb[0]:.1f},{mean_rgb[1]:.1f},{mean_rgb[2]:.1f})")

print("\nNew rival candidates:")
for i in range(1, 7):
    new_p = f"assets/high-res/final-native2k/rival-identity-{i}.png"
    im = Image.open(new_p)
    arr = np.array(im)
    mean_rgb = arr.mean(axis=(0, 1))
    print(f"New rival-identity-{i}: mean_rgb=({mean_rgb[0]:.1f},{mean_rgb[1]:.1f},{mean_rgb[2]:.1f})")
