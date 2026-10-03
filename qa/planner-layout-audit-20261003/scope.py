from pathlib import Path
import json,hashlib,re
R=Path(__file__).resolve().parents[2]; O=Path(__file__).resolve().parent
def rd(p):return json.loads((R/p).read_text(encoding='utf-8-sig'))
files=['asset-manifest.json','reviewed-art-ledger.json','raw-inventory.json','public-art-inventory.json','GAME-DATA-REFERENCE.json','references/visual-targets/index.json']
summ={}
for p in files:
 d=rd('docs/plan/'+p);summ[p]={'type':type(d).__name__,'keys':list(d) if isinstance(d,dict) else None,'arrayCounts':{k:len(v) for k,v in d.items() if isinstance(v,list)} if isinstance(d,dict) else len(d)}
benchmark=rd('qa/benchmark/report.json'); summ['benchmarkKeys']=list(benchmark)
checks=benchmark.get('automated',[]);summ['benchmarkCheckStatusCounts']={s:sum(r.get('status')==s for r in checks) for s in ['PASS','FAIL','UNVERIFIED']};summ['benchmarkFailureRows']=[r for r in checks if r.get('status')=='FAIL'];summ['benchmarkAt']=benchmark['at'];summ['savedBenchmarkAssets']=len(benchmark['assets'])
rows=[json.loads(x) for x in (R/'assets/production/production-14-20261003/input.jsonl').read_text().splitlines()]
row=next((r for r in rows if 'kingdom-stone-day1-composition-v4' in json.dumps(r)),rows[-1]); summ['submittedKingdomInput']=row
summ['testsDeclared']=sum(len(re.findall(r"\btest\(",p.read_text())) for p in (R/'tests').glob('*.test.mjs'))
summ['distSourceMatches']={str(p.relative_to(R)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest()==hashlib.sha256((R/'dist'/p.relative_to(R)).read_bytes()).hexdigest() if (R/'dist'/p.relative_to(R)).exists() else False for p in (R/'src').rglob('*') if p.is_file()}
c=rd('qa/recovery-executor-20261003/kingdom-layout-candidate.json');b=rd('qa/planner-layout-audit-20261003/browser-checks.json');cam=c['camera']
def proj(x,y):a,b,d,e,tx,ty=cam;return[a*x+d*y+tx,b*x+e*y+ty]
summ['partialSitePanelCoverage']=[]
for view in b:
 if 'viewport' not in view:continue
 cut=view['dims']['panelSourceX']; ids=[]
 for site in c['geometry']['sites']:
  x,y,w,h=site['rect'];right=max(proj(a,d)[0] for a,d in [(x,y),(x+w,y),(x+w,y+h),(x,y+h)])
  if right>cut:ids.append({'id':site['id'],'sourcePixelsBeyondPanelLeft':round(right-cut,2)})
 summ['partialSitePanelCoverage'].append({'viewport':view['viewport'],'sites':ids})
(O/'scope-checks.json').write_text(json.dumps(summ,indent=2)+'\n')
print(json.dumps(summ,indent=2))
