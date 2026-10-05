import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.assemble_live_art import find_token, load_rgba, matte, foreground, components
fg = foreground(matte(load_rgba(find_token("rig-knight"))))
boxes = components(fg, 700)
for b in boxes[:18]:
    sol = b["area"] / (b["w"] * b["h"])
    print(f"sol={sol:.2f} a={b['area']:6d} x={b['x']:4d} y={b['y']:4d} w={b['w']:4d} h={b['h']:4d}")
