import json
import cv2
import numpy as np
from pathlib import Path

root = Path("assets/derivatives/mock-led-20261016/kingdom")
contract = json.loads(Path("src/data/implementation-contract.json").read_text(encoding="utf-8"))
geo = contract["geometry"]["kingdom"]
A, B, C, D, E, F = geo["worldToSource"]
gx, gy = geo["anchors"]["gate"]
sx, sy = int(round(A * gx + C * gy + E)), int(round(B * gx + D * gy + F))

def proj(x, y):
    return (int(round(A * x + C * y + E)), int(round(B * x + D * y + F)))

# Segments from wallPresentation
nw = proj(0.7, 0.15)
ne = proj(12.6, 0.15)
sw = proj(0.7, 9.45)
se = proj(12.6, 9.45)
gw = proj(7.2, 9.45)
ge = proj(8.2, 9.45)

segments = [
    (nw, ne),          # back
    (nw, sw),          # west
    (ne, se),          # east
    (sw, gw),          # front-west (stops before gate)
    (ge, se),          # front-east (starts after gate)
]

def render_wall_on_image(base_img, era, height=18, is_tall=False, is_scaffold=False):
    canvas = base_img.copy()
    h_canvas, w_canvas = canvas.shape[:2]
    
    # We will draw textured quads along each segment
    for p0, p1 in segments:
        dx = p1[0] - p0[0]
        dy = p1[1] - p0[1]
        length = int(np.hypot(dx, dy))
        if length == 0:
            continue
        
        # Wall rises upwards (-y in screen space)
        wall_h = int(height * 1.55) if is_tall else height
        
        # Generate wall texture
        if is_scaffold:
            # Scaffold: periodic upright posts
            np.random.seed(p0[0] + p0[1])
            step = 14
            for s in range(0, length, step):
                t = s / length
                bx = int(p0[0] + dx * t)
                by = int(p0[1] + dy * t)
                # Keep away from gate
                if np.hypot(bx - sx, by - sy) < 22:
                    continue
                post_h = wall_h + int(np.random.uniform(-2, 4))
                if era == 'future':
                    # Cyan/blue energy pylons: B > R + 12
                    color = (245, 210, 45) # BGR: Blue=245, Green=210, Red=45
                    cv2.line(canvas, (bx, by), (bx, by - post_h), color, 4)
                    cv2.circle(canvas, (bx, by - post_h), 3, (255, 230, 80), -1)
                else:
                    color = (70, 115, 165) # warm sunlit timber post (mean > 90, R > B + 20)
                    cv2.line(canvas, (bx, by), (bx, by - post_h), color, 4)
                    # Crossbeam
                    if s + step < length:
                        nbx = int(p0[0] + dx * (s + step) / length)
                        nby = int(p0[1] + dy * (s + step) / length)
                        if np.hypot(nbx - sx, nby - sy) >= 22:
                            cv2.line(canvas, (bx, by - post_h + 4), (nbx, nby - post_h + 4), (65, 105, 155), 2)
        else:
            # Built or tall wall: solid textured wall polygon
            # For each pixel step along the segment, draw vertical textured column
            np.random.seed(p0[0] + p0[1] + (100 if is_tall else 0))
            
            # Base color palette per era
            if era == 'stone':
                base_color = np.array([58, 96, 142], dtype=float) # warm timber palisade
            elif era == 'medieval':
                base_color = np.array([125, 130, 135], dtype=float) # grey stone
            elif era == 'gunpowder':
                base_color = np.array([55, 75, 130], dtype=float) # red brick
            elif era == 'industrial':
                base_color = np.array([80, 85, 90], dtype=float) # steel
            elif era == 'modern':
                base_color = np.array([135, 140, 142], dtype=float) # concrete
            elif era == 'future':
                base_color = np.array([75, 70, 65], dtype=float) # composite
            elif era == 'bronze':
                base_color = np.array([45, 90, 145], dtype=float) # bronze
            elif era == 'iron':
                base_color = np.array([65, 70, 75], dtype=float) # dark iron
            else:
                base_color = np.array([100, 100, 100], dtype=float)

            # Draw vertical strip for each point along the line
            for s in range(length):
                t = s / length
                bx = int(round(p0[0] + dx * t))
                by = int(round(p0[1] + dy * t))
                
                # Leave gate open: window around sx, sy
                if np.hypot(bx - sx, by - sy) < 18:
                    continue
                if not (0 <= bx < w_canvas):
                    continue
                
                # Texture pattern across length: vertical courses every 6-10 px
                joint = (s % 8 == 0)
                crenel = (s % 16 < 8)
                current_h = wall_h
                if crenel and not is_tall:
                    current_h = int(wall_h * 0.75) # crenellation gap
                
                for y_off in range(current_h):
                    py = by - y_off
                    if not (0 <= py < h_canvas):
                        continue
                    
                    # Compute pixel color with texture and depth shading
                    noise = np.random.uniform(-6, 6)
                    col = base_color + noise
                    
                    # Horizontal courses
                    if y_off % 6 == 0:
                        col -= 30
                    if joint:
                        col -= 35
                    
                    # Era specific accents
                    if era == 'future' and (y_off == current_h // 2 or (s % 16 == 4)):
                        col = np.array([235, 195, 45], dtype=float) # cyan glow line
                    elif era == 'industrial' and (y_off % 8 == 3) and (s % 10 == 3):
                        col += 45 # rivet
                    elif era == 'gunpowder' and y_off >= current_h - 2:
                        col = np.array([130, 135, 140], dtype=float) # stone coping
                    
                    # Top highlight, bottom shadow
                    if y_off == current_h - 1:
                        col += 25
                    elif y_off == 0:
                        col -= 40
                    
                    # Apply to canvas (3px width along normal for thickness)
                    canvas[py, bx] = np.clip(col, 0, 255)
                    if bx + 1 < w_canvas:
                        canvas[py, bx + 1] = np.clip(col * 0.95, 0, 255)
                    if bx - 1 >= 0:
                        canvas[py, bx - 1] = np.clip(col * 0.95, 0, 255)
                    if py + 1 < h_canvas and y_off == 0:
                        # Ground contact shadow
                        canvas[py + 1, bx] = (canvas[py + 1, bx] * 0.6).astype(np.uint8)
                        
    return canvas

def added(ground, wall):
    diff = np.abs(wall.astype(np.int16) - ground.astype(np.int16)).sum(2)
    inner = cv2.erode((diff > 40).astype(np.uint8) * 255, np.ones((9, 9), np.uint8))
    sel = inner > 0
    def horizontal(image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY).astype(np.float32)
        return np.abs(cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3))
    if not np.any(sel):
        return -999.0
    return float((horizontal(wall) - horizontal(ground))[sel].mean())

def median(ground, image):
    diff = np.abs(image.astype(np.int16) - ground.astype(np.int16)).sum(2)
    bright = (diff > 40) & (image.mean(2) > 90)
    if not np.any(bright):
        return [0.0, 0.0, 0.0]
    return [float(v) for v in np.median(image[bright], axis=0)]

# Generate for all 8 ages
for age in ["stone", "bronze", "iron", "medieval", "gunpowder", "industrial", "modern", "future"]:
    g_path = root / f"kingdom-{age}-ground.png"
    ground = cv2.imread(str(g_path))
    
    # Generate scaffold, wall, tall
    scaffold = render_wall_on_image(ground, age, height=18, is_scaffold=True)
    wall = render_wall_on_image(ground, age, height=20, is_tall=False)
    tall = render_wall_on_image(ground, age, height=20, is_tall=True)
    
    # Save the files
    cv2.imwrite(str(root / f"kingdom-{age}-scaffold.png"), scaffold)
    cv2.imwrite(str(root / f"kingdom-{age}-wall.png"), wall)
    cv2.imwrite(str(root / f"kingdom-{age}-wall-tall.png"), tall)
    
    score_built = added(ground, wall)
    score_tall = added(ground, tall)
    gate = wall[sy - 6:sy + 6, sx - 6:sx + 6].astype(np.int16) - ground[sy - 6:sy + 6, sx - 6:sx + 6].astype(np.int16)
    gate_diff = float(np.abs(gate).mean())
    
    print(f"{age:10s} built score: {score_built:6.2f}, tall score: {score_tall:6.2f}, gate diff: {gate_diff:5.2f}")

med_stone = median(
    cv2.imread(str(root / "kingdom-stone-ground.png")),
    cv2.imread(str(root / "kingdom-stone-scaffold.png"))
)
med_fut = median(
    cv2.imread(str(root / "kingdom-future-ground.png")),
    cv2.imread(str(root / "kingdom-future-scaffold.png"))
)
print("Stone scaffold median BGR:", med_stone, "R > B + 20?", med_stone[2] > med_stone[0] + 20)
print("Future scaffold median BGR:", med_fut, "B > R + 12?", med_fut[0] > med_fut[2] + 12)

