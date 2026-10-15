import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
atlas = json.loads((ROOT / "src/data/actor-atlas.json").read_text(encoding="utf-8"))


def dump(class_id):
    image = Image.open(ROOT / atlas["classes"][class_id]["file"]).convert("RGB")
    rgb = np.asarray(image)
    height, width = rgb.shape[:2]
    corners = np.concatenate([
        rgb[2:8, 2:8].reshape(-1, 3),
        rgb[2:8, -8:-2].reshape(-1, 3),
        rgb[-8:-2, 2:8].reshape(-1, 3),
        rgb[-8:-2, -8:-2].reshape(-1, 3),
    ])
    background = np.median(corners, axis=0)
    distance = np.linalg.norm(rgb.astype(np.float32) - background.astype(np.float32), axis=2)
    red, green, blue = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    magenta = (red > 185) & (blue > 185) & (green < 120)
    mask = ((distance > 36) & ~magenta).astype(np.uint8) * 255
    count, _labels, stats, centroids = cv2.connectedComponentsWithStats(mask, 8)
    rows = []
    for index in range(1, count):
        x, y, w, h, area = [int(value) for value in stats[index]]
        if area < 400:
            continue
        rows.append((area, x, y, w, h, round(float(centroids[index][0]), 1), round(float(centroids[index][1]), 1)))
    rows.sort(reverse=True)
    samples = [(200, 200), (300, 300), (700, 200), (200, 700), (512, 512)]
    picked = {f"{x},{y}": rgb[y, x].tolist() for x, y in samples}
    print(class_id, image.size, "bg", background.tolist(), "kept", len(rows), "raw", count - 1, "samples", picked)
    for row in rows[:12]:
        print(" ", row)


for class_id in ("healer", "knight", "warlock", "mage"):
    dump(class_id)
    print()
