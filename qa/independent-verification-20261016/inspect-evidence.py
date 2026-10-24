"""Independent read-only source/pixel/package evidence, 16 October 2026."""
from pathlib import Path
import hashlib, json, importlib.util, subprocess, zipfile
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def load(p): return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
snapshot={"head":subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
 "dirty":subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).splitlines(),
 "files":{str(p.relative_to(ROOT)).replace('\\','/'):{'bytes':p.stat().st_size,'sha256':sha(p)} for p in (ROOT/'src').rglob('*') if p.is_file()}}
(OUT/'source-snapshot.json').write_text(json.dumps(snapshot,indent=2))
spec=importlib.util.spec_from_file_location('trace',ROOT/'qa/game-completion-20261013/physical_trace.py')
trace=importlib.util.module_from_spec(spec); spec.loader.exec_module(trace)
manifest=load('assets/derivatives/scene-edges-20261013/manifest.json')
rows=[]
for r in manifest['rows']:
 mode=r['mode']; geo=trace.CONTRACT['geometry'][mode]; results={}
 arrays=[]
 for label,path in [('before',r['source']),('displayed',r['file'])]:
  im=Image.open(ROOT/path).convert('RGB'); rgb=np.array(im); arrays.append(rgb)
  f=trace.trace_features(geo,geo['worldToSource'],im.width/geo['sourceSize'][0],im.height/geo['sourceSize'][1],rgb,np.array(im.convert('L')))
  accepted,reason=trace.agrees(f)
  results[label]={'path':path,'sha256':sha(ROOT/path),'heuristicPass':accepted,'reason':reason,'roads':f['roads']['edge'],'lane':f['lanes']['edge'],'banks':f['banks']['edge']}
 changed=np.any(arrays[0]!=arrays[1],axis=2)
 rows.append({'mode':mode,'age':r['age'],'changedPixels':int(changed.sum()),'totalPixels':int(changed.size),'changedPercent':round(float(changed.mean()*100),5),**results})
report={'method':'Recompute the producer edge heuristic on BOTH original and runtime copy. This heuristic is not physical or visual acceptance.',
 'beforePass':sum(r['before']['heuristicPass'] for r in rows),'displayPass':sum(r['displayed']['heuristicPass'] for r in rows),'rows':rows}
(OUT/'scene-heuristic-countercheck.json').write_text(json.dumps(report,indent=2))
bodies=load('src/data/hero-bodies-20261011.json')['bodies']; atlas=load('src/data/actor-atlas.json')
kits={k:{'file':v['file'],'depictedKitEra':v.get('depictedKitEra'),'status':v.get('status'),'hashMatches':sha(ROOT/v['file'])==v['sha256']} for k,v in bodies.items()}
(OUT/'art-coverage.json').write_text(json.dumps({'standingBodies':kits,'classCount':len(atlas['classes']),'worldReady':atlas['worldReady'],'mountReady':atlas.get('mountReady'),'requiredEraCount':4,'note':'Class atlas has one specification per class. Distinct hashes do not prove anatomy, contact, clips, roles or four era coverage.'},indent=2))
apks=[]
for p in [ROOT/'android/app/build/outputs/apk/release/ages-of-dominion-reborn-preview-release-unsigned-20261011.apk',ROOT/'delivery/ages-of-dominion-reborn-preview-48b6b93c.apk']:
 if p.exists():
  with zipfile.ZipFile(p) as z:
   native={n:hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if n.endswith('.dex') or n=='AndroidManifest.xml'}
  apks.append({'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p),'nativeEntries':native})
(OUT/'package-identities.json').write_text(json.dumps(apks,indent=2))
print(json.dumps({'head':snapshot['head'],'sourceFiles':len(snapshot['files']),'sceneBeforePass':report['beforePass'],'sceneAfterPass':report['displayPass'],'changedPercentRange':[min(r['changedPercent'] for r in rows),max(r['changedPercent'] for r in rows)],'bodies':kits,'packages':apks},indent=2))
