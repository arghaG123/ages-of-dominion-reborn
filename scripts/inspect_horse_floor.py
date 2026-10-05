import os
from PIL import Image
import numpy as np

p = 'assets/high-res/final-native2k/hero-mount-horse.png'
im = Image.open(p).convert('RGB')
arr = np.array(im)

# Look at y from 1600 to 2048, and inspect horizontal strips
for y in range(1600, 2040, 40):
    row_rgb = arr[y, 400:1600, :]
    print(f"y={y}: mean RGB={row_rgb.mean(axis=0).astype(int).tolist()} std={row_rgb.std(axis=0).mean():.1f}")

# Look at hooves vs floor
# In hero-mount-horse, where are the hooves?
print("\nHooves search in hero-mount-horse:")
for y in range(1500, 2000, 25):
    # dark hoof pixels (hooves are usually dark, floor is light grey)
    dark_pixels = np.sum(arr[y, :, :].mean(axis=1) < 100)
    print(f"y={y}: dark_pixels (<100) = {dark_pixels}")
