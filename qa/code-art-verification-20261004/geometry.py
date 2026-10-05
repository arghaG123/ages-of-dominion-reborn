from pathlib import Path
import json,math
from PIL import Image
root=Path(__file__).resolve().parents[2];out=Path(__file__).resolve().parent
contract=json.loads((root/'src/data/implementation-contract.json').read_text(encoding='utf-8'))
scene=json.loads((root/'src/data/stone-scene.json').read_text())
validation=json.loads((root/'assets/high-res/interactive-4k-first32-20261003/run-02-20261004-010239/packs/kingdom-terrain-stone/validation.json').read_text())
hall=scene['hall'];m=hall['matrix']
with Image.open(root/hall['file']) as im:alpha=im.getchannel('A').getbbox()
def p(g,pt):a,b,c,d,e,f=g;return[a*pt[0]+c*pt[1]+e,b*pt[0]+d*pt[1]+f]
geo=contract['geometry']['defense']
result={'activeHallRasterEnvelope':{'scale':m[0][0],'width':hall['width']*m[0][0],'height':hall['height']*m[1][1],'alphaBBox':alpha},'kingdomValidationScope':'Mixes active contract coordinates with prior proposed framing/contact/rectangle fixture. Rectangle overlap does not prove an actual door obstruction. Distance between chosen centre points does not prove an apron gap. Physical registration remains UNVERIFIED; observed scene mismatch remains FAIL.','reportedGapRecomputed':math.dist([640,291.26],[644.6,297.4]),'nativeAspect':{'width':5504,'height':3072,'ratio':5504/3072,'exactRatio':'43:24','logicalFourfold':True},'defenseAnchors':{k:p(geo['worldToSource'],v) for k,v in geo['anchors'].items()},'defenseSpatialReview':{'defense-terrain':'FAIL for active contract: source gate (670,65.5) lies in output sky; winding road/pads do not follow source guide','defense-terrain-hills':'FAIL for active contract: source gate (670,65.5) lies in output sky; winding road/pads do not follow source guide','other20Outputs':'UNVERIFIED fine spatial survey; overview does not establish all polygons/corridors/bridge approaches'}}
(out/'geometry-claims.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
