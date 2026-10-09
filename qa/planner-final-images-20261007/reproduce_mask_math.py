"""Read-only independent mask reproduction; no producer imports or output mutation."""
import json,pathlib
import numpy as np,cv2
from PIL import Image
R=pathlib.Path(__file__).resolve().parents[2];rows=json.loads((R/'docs/plan/ACTORS-EQUIPMENT-RESIDUAL-INTERFACE-2026-10-07.json').read_text())['rows'];result=[]
for r in rows:
 if r['id'] not in ['troop-stone-melee','troop-stone-ranged','troop-industrial-ranged','troop-industrial-heavy']:continue
 im=Image.open(R/r['source']['path']).convert('RGBA');arr=np.array(im,dtype=np.uint8);h,w=arr.shape[:2]
 mask=np.zeros((h+2,w+2),dtype=np.uint8);rgb=np.ascontiguousarray(arr[:,:,:3])
 for p in [(0,0),(w-1,0),(0,h-1),(w-1,h-1),(w//2,0),(w//2,h-1)]:cv2.floodFill(rgb,mask,p,(0,0,0),(25,25,25),(25,25,25),flags=8|(255<<8)|cv2.FLOODFILL_MASK_ONLY)
 bg=mask[1:-1,1:-1]==255;distance=cv2.distanceTransform(bg.astype(np.uint8),cv2.DIST_L2,3);alpha=np.clip(1-distance/2,0,1);alpha[~bg]=1;calc=arr.copy();calc[:,:,3]=(alpha*255).astype(np.uint8);image=Image.fromarray(calc);box=image.getbbox();crop=[max(0,box[0]-10),max(0,box[1]-10),min(w,box[2]+10),min(h,box[3]+10)]
 actual=np.array(Image.open(R/r['output']['path']).convert('RGBA'));predicted=np.array(image.crop(crop));same=predicted.shape==actual.shape and np.array_equal(predicted,actual)
 result.append({'id':r['id'],'independentlyReproducedDeliveredPixels':same,'floatingFloodMaskFraction':float(bg.mean()),'actualCropXYXY':crop,'sourceToOutput':[1,0,0,1,-crop[0],-crop[1]],'claimedSourceToOutput':r['sourceToOutput'],'scope':'reproduces damaged output only; no corrected production output written'})
(R/'qa/planner-final-images-20261007/mask-causality.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
