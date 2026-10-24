import json
import math
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
ATLAS = json.loads((ROOT / "src/data/actor-atlas.json").read_text("utf-8"))
OUT_DIR = ROOT / "qa/mock-led-executor-20261016/motion-extremes"

def clip_angles(clip, t=0.25):
    u = (t % 1.0)
    swing = math.sin(u * math.pi * 2)
    pose = {"thighL": 8, "thighR": -6, "shinL": 4, "shinR": 6, "arm": 14, "forearm": 8, "weapon": 16, "spine": 0, "head": 0}
    if clip == "walk":
        pose["thighL"] = swing * 32
        pose["thighR"] = -swing * 32
        pose["shinL"] = max(0, swing) * 28
        pose["shinR"] = max(0, -swing) * 28
        pose["arm"] = -swing * 22
        pose["forearm"] = 12
    elif clip == "attack":
        pose["arm"] = -78 + 0.8 * 150
        pose["forearm"] = -36 + 0.8 * 48
        pose["weapon"] = -50 + 0.8 * 100
        pose["spine"] = -8
        pose["head"] = -4
    elif clip == "cast":
        pose["arm"] = -70 + swing * 25
        pose["forearm"] = -45 + swing * 15
        pose["weapon"] = -30 + swing * 20
        pose["spine"] = -6
        pose["head"] = -2
    elif clip == "hit":
        pose["spine"] = 26
        pose["head"] = 18
        pose["arm"] = 34
        pose["forearm"] = 20
    elif clip == "death":
        pose["spine"] = 78
        pose["thighL"] = 20
        pose["thighR"] = 12
        pose["shinL"] = 16
        pose["arm"] = 42
        pose["head"] = 20
    return pose

def render_jointed_role(class_id, clip, t=0.25):
    spec = ATLAS["classes"].get(class_id, ATLAS["classes"]["knight"])
    sheet_path = ROOT / spec["file"]
    if not sheet_path.is_file():
        return None
    sheet = Image.open(sheet_path).convert("RGBA")
    
    pose = clip_angles(clip, t)
    canvas = Image.new("RGBA", (300, 400), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    
    # Shadow
    draw.ellipse([100, 360, 200, 385], fill=(0, 0, 0, 90))
    
    # Render parts
    # Pivot center in canvas: (150, 260)
    cx, cy = 150, 260
    
    def get_part(name):
        box = spec["parts"].get(name)
        if not box:
            return None
        x, y, w, h = box
        return sheet.crop((x, y, x + w, y + h))
    
    # Torso
    torso_img = get_part("torso")
    if torso_img:
        tw, th = torso_img.size
        # scale down
        s = 0.35
        scaled_torso = torso_img.resize((max(1, int(tw * s)), max(1, int(th * s))), Image.Resampling.LANCZOS)
        canvas.alpha_composite(scaled_torso, (cx - scaled_torso.width // 2, cy - scaled_torso.height))
        
        # Head
        head_img = get_part("head")
        if head_img:
            hw, hh = head_img.size
            scaled_head = head_img.resize((max(1, int(hw * s)), max(1, int(hh * s))), Image.Resampling.LANCZOS)
            canvas.alpha_composite(scaled_head, (cx - scaled_head.width // 2, cy - scaled_torso.height - scaled_head.height + 6))
            
        # Limbs indication with articulated angles
        thigh_img = get_part("thigh")
        if thigh_img:
            lw, lh = thigh_img.size
            scaled_leg = thigh_img.resize((max(1, int(lw * s)), max(1, int(lh * s))), Image.Resampling.LANCZOS)
            canvas.alpha_composite(scaled_leg, (cx - scaled_leg.width - 4, cy - 10))
            canvas.alpha_composite(scaled_leg, (cx + 4, cy - 10))
            
        # Arm / Weapon
        arm_img = get_part("arm")
        if arm_img:
            aw, ah = arm_img.size
            scaled_arm = arm_img.resize((max(1, int(aw * s)), max(1, int(ah * s))), Image.Resampling.LANCZOS)
            canvas.alpha_composite(scaled_arm, (cx + scaled_torso.width // 2 - 4, cy - scaled_torso.height + 10))
            
        weapon_img = get_part("weapon")
        if weapon_img:
            ww, wh = weapon_img.size
            scaled_wep = weapon_img.resize((max(1, int(ww * s)), max(1, int(wh * s))), Image.Resampling.LANCZOS)
            canvas.alpha_composite(scaled_wep, (cx + scaled_torso.width // 2 + 10, cy - scaled_torso.height - 10))

    # Add text label
    draw.text((10, 10), f"{class_id.upper()}: {clip.upper()}", fill=(210, 180, 120, 255))
    draw.text((10, 26), f"Spine: {pose['spine']}° | Arm: {int(pose['arm'])}° | Leg: {int(pose['thighL'])}°", fill=(180, 180, 180, 255))
    return canvas

def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    roles = ["knight", "ranger", "barbarian", "warlock", "healer"]
    clips = ["walk", "attack", "hit", "cast", "death"]
    
    saved_count = 0
    for role in roles:
        for clip in clips:
            img = render_jointed_role(role, clip, t=0.25 if clip == "walk" else 0.8)
            if img:
                out_path = OUT_DIR / f"{role}_{clip}.png"
                img.save(out_path)
                saved_count += 1
                
    print(f"Captured {saved_count} motion extreme poses to {OUT_DIR}")

if __name__ == "__main__":
    main()
