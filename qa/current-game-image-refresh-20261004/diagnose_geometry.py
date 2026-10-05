"""Pure geometric analysis of saved data; does not execute gameplay or repair art."""
import json, math, pathlib
ROOT=pathlib.Path('C:/dev/ages-of-dominion-reborn')
OUT=ROOT/'qa/current-game-image-refresh-20261004'
load=lambda p: json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
geo=load('src/data/implementation-contract.json')['geometry']['defense']
data=load('src/data/reference-data.json')
def segment_distance(p,a,b):
    dx,dy=b[0]-a[0],b[1]-a[1]
    t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/(dx*dx+dy*dy)))
    return math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)
rows=[]
for s in geo['sites']:
    x,y,w,h=s['rect'];p=[x+w/2,y+h/2]
    d=min(segment_distance(p,a,b) for a,b in zip(geo['lane'],geo['lane'][1:]))
    rows.append({'site':s['id'],'worldCentre':p,'minDistanceToLane':d,'baseFamilyCoverage':{k:d<=v['rng'] for k,v in data['TOWERS'].items()}})
result={'method':'point-to-segment distance in world units, no source/gameplay execution','sites':rows,'limit':'Geometric potential coverage does not prove firing, survival, clearing or balance. Off-lane placement alone is not a no-coverage diagnosis.'}
(OUT/'defense-geometric-coverage.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(rows[:2],indent=2))
