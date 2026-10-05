import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from PIL import Image
from scripts.assemble_live_art import ROOT, find_token, load_rgba, matte, foreground, horse_parts
from scripts.assemble_live_art import save_sheet
horse = matte(load_rgba(find_token("mount-horse")))
split = horse_parts(foreground(horse))
atlas_path = ROOT / "src/data/actor-atlas.json"
atlas = json.loads(atlas_path.read_text(encoding="utf-8"))
mount = atlas["mounts"]["horse"]
body_px = horse.copy()
for leg in split["legs"]:
    body_px[leg["y"]:leg["y"] + leg["h"], leg["x"]:leg["x"] + leg["w"], 3] = 0
mount["bodyFile"] = save_sheet(body_px, "mounts/horse-body.png")
save_sheet(horse, "mounts/horse.png")
mount["body"] = [split["body"]["x"], split["body"]["y"], split["body"]["w"], split["body"]["h"]]
mount["legs"] = [[leg["x"], leg["y"], leg["w"], leg["h"]] for leg in split["legs"]]
atlas_path.write_text(json.dumps(atlas, indent=2) + "\n", encoding="utf-8")
preview = Image.new("RGBA", (720, 520), (20, 28, 24, 255))
bx, by, bw, bh = mount["body"]
body = Image.fromarray(body_px[by:by + bh, bx:bx + bw])
body.thumbnail((460, 260))
preview.alpha_composite(body, (20, 16))
for index, leg in enumerate(mount["legs"]):
    crop = Image.fromarray(horse[leg[1]:leg[1] + leg[3], leg[0]:leg[0] + leg[2]])
    crop.thumbnail((80, 200))
    preview.alpha_composite(crop, (40 + index * 90, 300))
preview.save(ROOT / "qa/code-art-assembly-20261004/preview-horse.png")
print("legs", len(mount["legs"]), "body", mount["body"], "boxes", mount["legs"])
