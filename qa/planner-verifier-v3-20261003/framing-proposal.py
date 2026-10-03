"""QA counterfactual only: show clipping and the cost of a common translation."""
from pathlib import Path
import json
import numpy as np, cv2
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
terrain=np.array(Image.open(ROOT/'assets/production/production-01-20261003/images/01-kingdom-terrain-stone.png').convert('RGB'))
hall=np.array(Image.open(ROOT/'assets/delivery/stone-starter-20261003/derivatives/v3/townhall-stone.png').convert('RGBA'))
report=json.loads((ROOT/'qa/recovery-v3-20261003/report.json').read_text());reg=report['hall']['registration'];s=reg['footprintScale'];cx,cy=reg['centroid'];dx,dy=reg['destination']
def blit(canvas,shift):
    matrix=np.array([[s,0,dx-s*cx],[0,s,dy-s*cy+shift]],dtype=float)
    w=cv2.warpAffine(hall,matrix,(1376,768));a=w[:,:,3:4].astype(float)/255
    return np.clip(canvas*(1-a)+w[:,:,:3]*a,0,255).astype('uint8')
current=blit(terrain,0)
translated=np.full_like(terrain,(68,75,84));translated[193:]=terrain[:-193]
translated=blit(translated,193)
sheet=Image.new('RGB',(1376,1640),(20,20,20));draw=ImageDraw.Draw(sheet)
draw.text((15,8),'QA ONLY: footprint heuristic scale 0.3288 / current source frame: roof clips',fill='white');sheet.paste(Image.fromarray(current),(0,34))
draw.text((15,821),'QA ONLY: shared +193px translation. Missing upper terrain is grey; lower193px scenery cropped. NOT ACCEPTED.',fill='white');sheet.paste(Image.fromarray(translated),(0,855))
sheet.save(OUT/'framing-counterfactual.png')
