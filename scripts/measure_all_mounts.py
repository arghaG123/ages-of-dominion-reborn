import os
from PIL import Image
import numpy as np

def measure_mount(iid, bot_limit, rider_zone_x):
    p = f'assets/high-res/final-native2k/{iid}.png'
    im = Image.open(p).convert('RGB')
    arr = np.array(im)
    bg = arr[10, 10, :]
    diff = np.sqrt(np.sum((arr.astype(float) - bg)**2, axis=2))
    fg = diff > 28.0
    
    # Exclude rectangular floor plane below bot_limit
    fg[bot_limit:, :] = False
    
    # Top contour
    top_y = np.zeros(2048)
    for x in range(2048):
        ys = np.where(fg[:, x])[0]
        top_y[x] = ys.min() if len(ys) > 0 else 2048
        
    rider_tops = top_y[rider_zone_x[0]:rider_zone_x[1]]
    seat_idx = np.argmax(rider_tops) # lowest dip for seat/saddle
    seat_x = int(rider_zone_x[0] + seat_idx)
    seat_y = int(rider_tops[seat_idx])
    
    # Bottom contact
    bot_ys = []
    contact_xs = []
    for x in range(2048):
        ys = np.where(fg[:, x])[0]
        if len(ys) > 0:
            bot_ys.append(ys.max())
            contact_xs.append(x)
            
    contact_y = int(max(bot_ys)) if len(bot_ys) > 0 else 2048
    contact_x = int(contact_xs[np.argmax(bot_ys)]) if len(contact_xs) > 0 else 1024
    
    # Bbox
    ys, xs = np.where(fg)
    bbox = [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]
    
    print(f"\n{iid}:")
    print(f"  bbox = {bbox}")
    print(f"  Rider/Saddle Landmark: [{seat_x}, {seat_y}]")
    print(f"  Ground Contact Landmark: [{contact_x}, {contact_y}]")
    return bbox, [seat_x, seat_y], [contact_x, contact_y]

measure_mount('hero-mount-horse', 1875, (900, 1350))
measure_mount('hero-mount-motor-transport', 1840, (800, 1300))
measure_mount('hero-mount-future-transport', 1780, (700, 1300))
