import numpy as np
from PIL import Image

def analyze_character(name):
    print(f"\n==================== {name.upper()} ====================")
    p = f'assets/high-res/final-native2k/rig-source-parts-{name}.png'
    im = Image.open(p)
    arr = np.array(im)
    corners = np.array([arr[5, 5], arr[5, -6], arr[-6, 5], arr[-6, -6]])
    bg = np.median(corners, axis=0)
    print("Background color:", bg)
    
    # Let's inspect each quadrant
    quads = {
        'top_left (0..1024, 0..1024)': arr[0:1024, 0:1024],
        'top_right (0..1024, 1024..2048)': arr[0:1024, 1024:2048],
        'bot_left (1024..2048, 0..1024)': arr[1024:2048, 0:1024],
        'bot_right (1024..2048, 1024..2048)': arr[1024:2048, 1024:2048],
    }
    for qname, qarr in quads.items():
        # Check mean colors
        r, g, b = qarr[:,:,0], qarr[:,:,1], qarr[:,:,2]
        is_mag = (r > 170) & (g < 80) & (b > 170)
        fg_ratio = 1.0 - np.mean(is_mag)
        print(f"  {qname}: fg_ratio={fg_ratio:.2f}")

for name in ['knight', 'ranger', 'warlock', 'mage', 'necromancer', 'barbarian', 'paladin', 'healer']:
    analyze_character(name)
