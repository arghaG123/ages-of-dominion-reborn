from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "qa/mock-led-executor-20261016/healer-comparison.png"

def main():
    ground_path = ROOT / "assets/derivatives/mock-led-20261016/kingdom/kingdom-stone-ground.png"
    ground = Image.open(ground_path).convert("RGBA")
    
    # Crop a 1000x500 section around the settlement
    comp = ground.crop((200, 200, 1200, 700))
    draw = ImageDraw.Draw(comp)
    
    # Bodies to compare at game size (height = 140px)
    target_h = 140
    bodies = [
        ("knight", ROOT / "assets/derivatives/mock-led-20261016/bodies/class-knight-standing-body.png"),
        ("healer", ROOT / "assets/derivatives/mock-led-20261016/bodies/class-healer-standing-body.png"),
        ("ranger", ROOT / "assets/derivatives/mock-led-20261016/bodies/class-ranger-standing-body.png"),
        ("barbarian", ROOT / "assets/derivatives/mock-led-20261016/bodies/class-barbarian-standing-body.png"),
    ]
    
    base_y = 400
    x_positions = [150, 350, 550, 750]
    
    for (name, path), x in zip(bodies, x_positions):
        if not path.is_file():
            continue
        img = Image.open(path).convert("RGBA")
        scale = target_h / img.height
        w = int(round(img.width * scale))
        h = int(round(img.height * scale))
        resized = img.resize((w, h), Image.Resampling.LANCZOS)
        
        # Ground shadow
        draw.ellipse([x - w//3, base_y - 6, x + w//3, base_y + 10], fill=(0, 0, 0, 110))
        
        # Paste body with feet at base_y
        comp.alpha_composite(resized, (x - w//2, base_y - h + (8 if name == 'healer' else 0)))
        
        # Text label
        draw.text((x - 20, base_y + 14), name.upper(), fill=(240, 230, 210, 255))
        
    OUT.parent.mkdir(parents=True, exist_ok=True)
    comp.save(OUT)
    print(f"Saved healer comparison to {OUT}")

if __name__ == "__main__":
    main()
