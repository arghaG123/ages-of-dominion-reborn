from pathlib import Path
import json,re,hashlib
ROOT=Path(__file__).resolve().parents[2]; OUT=Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
for r in json.loads((OUT/'prompt-structure-check.json').read_text()):
    p=ROOT/r['path']; s=p.read_text(encoding='utf-8')
    headers=re.findall(r'^([1-7])\. (Task Summary|Environment|Inputs & Outputs|Step-by-Step Instructions|Edge Cases & Failure Modes|Acceptance Criteria|Do NOT)$',s,re.M)
    nums=[int(n) for n in re.findall(r'^(\d+)\. ',s.split('4. Step-by-Step Instructions\n\n')[1].split('\n\n5. Edge Cases')[0],re.M)]
    checks.append({'id':r['path'],'pass':len(headers)==7 and nums==list(range(1,r['atomicSteps']+1)) and sha(p)==r['sha256']})
for rel in ['visual-loaded/gallery.html','reference-runtime-loaded.jpg','eight-age-overview.jpg','summary.json','per-id-status.json']:
    checks.append({'id':rel,'pass':(OUT/rel).exists()})
gallery=OUT/'visual-loaded/gallery.html'
links=re.findall(r'src="([^"]+)"',gallery.read_text(encoding='utf-8'))
checks.append({'id':'loaded-gallery-images-resolve','pass':all((gallery.parent/x).exists() for x in links),'imageLinks':len(links)})
before=json.loads((OUT/'source-before.json').read_text())
changed=[n for n,h in before.items() if not (ROOT/n).exists() or sha(ROOT/n)!=h]
checks.append({'id':'existing-src-tests-scripts-preserved','pass':not changed,'checked':len(before),'changed':changed})
guides=[ROOT/'qa/recovery-executor-20261003/guides'/f'kingdom-stone-day1-composition-v{i}-guide.png' for i in [4,5]]
result={'checks':checks,'allPass':all(r['pass'] for r in checks),'knownMissingGuides':[p.relative_to(ROOT).as_posix() for p in guides if not p.exists()],'wholeProduct':'INCOMPLETE','ownerAcceptance':'UNVERIFIED','device':'STOPPED'}
(OUT/'final-handoff-check.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
assert result['allPass']
