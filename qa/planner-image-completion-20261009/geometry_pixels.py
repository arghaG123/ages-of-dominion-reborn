import sys,json,math,collections
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path('C:/dev/ages-of-dominion-reborn');QA=Path(__file__).resolve().parent
sys.path.insert(0,str(QA));from audit_common import read,dump
def pointseg(p,a,b):
    x,y=p;u,v=a;s,t=b;dx=s-u;dy=t-v;q=((x-u)*dx+(y-v)*dy)/(dx*dx+dy*dy) if dx*dx+dy*dy else 0;q=max(0,min(1,q));return math.hypot(x-u-q*dx,y-v-q*dy)
def orient(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def segdist(a,b,c,d):
    if orient(a,b,c)*orient(a,b,d)<=0 and orient(c,d,a)*orient(c,d,b)<=0 and max(min(a[0],b[0]),min(c[0],d[0]))<=min(max(a[0],b[0]),max(c[0],d[0])) and max(min(a[1],b[1]),min(c[1],d[1]))<=min(max(a[1],b[1]),max(c[1],d[1])):return 0
    return min(pointseg(a,c,d),pointseg(b,c,d),pointseg(c,a,b),pointseg(d,a,b))
def inside(p,poly):
    n=False
    for a,b in zip(poly,poly[1:]+poly[:1]):
        if (a[1]>p[1])!=(b[1]>p[1]) and p[0]<(b[0]-a[0])*(p[1]-a[1])/(b[1]-a[1])+a[0]:n=not n
    return n
def distance(line,poly):
    if any(inside(p,poly) for p in line):return 0
    return min(segdist(a,b,c,d) for a,b in zip(line,line[1:]) for c,d in zip(poly,poly[1:]+poly[:1]))
j=read('docs/plan/ENVIRONMENT-ART-VERTEX-REPAIR-INTERFACE-2026-10-09.json');geo=[]
for s in j['scenes']:
    conflicts=[]
    for pad in s['fullFootprints']:
        for road in s['roads']:
            ds=distance(road['polyline'],pad['polygon']);require=road['halfWidth']+road['uncertainty']
            if ds<=require:conflicts.append({'road':road['id'],'site':pad['id'],'distance':round(ds,3),'required':require})
    geo.append({'id':s['id'],'mode':s['mode'],'conflicts':conflicts,'producerCount':len(s['clearanceResults']),'reproducedCount':len(conflicts),'countMatches':len(conflicts)==len(s['clearanceResults']),'spatial':s['gates']['spatial'],'untraced':{k:not bool(s.get(k)) for k in ['banks','decks','approaches','walkable','obstacles']}})
dump('independent-clearance.json',geo)
pixels=[]
for owner,prefix in [('environment','ENVIRONMENT-ART'),('actors','ACTORS-EQUIPMENT')]:
    for r in read(f'docs/plan/{prefix}-VERTEX-REPAIR-INTERFACE-2026-10-09.json')['rows']:
        if not r.get('output') or r['id'].startswith(('state-','support-')):continue
        im=Image.open(ROOT/r['output']['path']).convert('RGBA'); a=np.asarray(im);rgb=a[:,:,:3].astype(np.int16);vis=a[:,:,3]>16;mag=vis&(rgb[:,:,0]>170)&(rgb[:,:,2]>150)&(rgb[:,:,1]<100)&(abs(rgb[:,:,0]-rgb[:,:,2])<90);bottom=mag.copy();bottom[:int(im.height*.65)]=False
        green=vis&(rgb[:,:,1]>rgb[:,:,0]+20)&(rgb[:,:,1]>rgb[:,:,2]+15)&(rgb[:,:,1]>90);green[:int(im.height*.55)]=False
        pixels.append({'id':r['id'],'role':r['role'],'status':r['status'],'path':r['output']['path'],'magentaPixels':int(mag.sum()),'lowerMagentaPixels':int(bottom.sum()),'lowerGreenCandidatePixels':int(green.sum()),'candidateOnly':True})
dump('independent-matte-candidates.json',pixels)
print('clearance',collections.Counter((x['mode'],x['spatial']) for x in geo),'arithmetic mismatches',sum(not x['countMatches'] for x in geo))
print('attacker magenta',[(p['id'],p['lowerMagentaPixels']) for p in pixels if p['role']=='attacker' and p['lowerMagentaPixels']>40])
print('creature magenta',[(p['id'],p['lowerMagentaPixels']) for p in pixels if p['role']=='creature' and p['lowerMagentaPixels']>40])
print('green',[(p['id'],p['lowerGreenCandidatePixels']) for p in pixels if p['id'] in ['armory-stone','barracks-stone','farm-bronze','workshop-iron','townhall-industrial','mine-industrial','hall-industrial','adventure-site-town']])
print('null READY',collections.Counter(r['intendedUse'] for r in j['rows'] if r['status']=='READY' and not r.get('output')))
