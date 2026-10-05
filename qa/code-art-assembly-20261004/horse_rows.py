import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.assemble_live_art import find_token, load_rgba, matte, foreground
fg = foreground(matte(load_rgba(find_token("mount-horse"))))
ys, xs = __import__("numpy").where(fg)
y0, y1, x0, x1 = int(ys.min()), int(ys.max()), int(xs.min()), int(xs.max())
print("bounds", x0, y0, x1, y1)
for y in range(360, y1, 40):
    row = fg[y, x0:x1 + 1]
    runs, start = [], None
    for i, value in enumerate(row):
        if value and start is None:
            start = i
        elif not value and start is not None:
            runs.append((start, i - start))
            start = None
    if start is not None:
        runs.append((start, len(row) - start))
    print(y, [(a, w) for a, w in runs if w > 6])
