"""Read-only inventory; creates audit metadata, never art or provider state."""
from pathlib import Path
import hashlib, json, re, subprocess, zipfile, collections

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'qa/planner-device-handoff-20261011'
OUT.mkdir(parents=True, exist_ok=True)
def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(4*1024*1024), b''): h.update(b)
    return h.hexdigest()
def write(name, data):
    (OUT/name).write_text(json.dumps(data, indent=2)+'\n', encoding='utf-8')
baseline = json.loads((ROOT/'docs/migration/device-handoff-20261009/transfer-manifest.json').read_text())
prior = {r['path']: r for r in baseline['files']}
hashpaths = collections.defaultdict(list)
for r in baseline['files']: hashpaths[r['sha256']].append(r['path'])
media = {'.png','.jpg','.jpeg','.webp','.svg','.wav','.mp3','.ogg','.gif','.bmp','.avif'}
rows=[]; categories=collections.defaultdict(lambda: {'files':0,'bytes':0})
for top in ['assets','qa','design-preview','docs','src','scripts','tests','delivery','dist','android','.git','output']:
    base=ROOT/top
    if not base.exists(): continue
    for p in base.rglob('*'):
        if not p.is_file() or p.is_symlink(): continue
        rel=p.relative_to(ROOT).as_posix(); n=p.stat().st_size
        categories[top]['files']+=1; categories[top]['bytes']+=n
        raw = top=='qa' and ('vertex-coordinator' in rel) and p.name in {'request_body.json','response.json'}
        asset = top=='assets' or (top in {'qa','design-preview'} and p.suffix.lower() in media) or raw
        if not asset: continue
        digest=sha(p); old=prior.get(rel)
        state='UNCHANGED_BASELINE' if old and old['sha256']==digest else ('CHANGED_BASELINE_PATH' if old else ('BASELINE_BYTES_NEW_PATH' if digest in hashpaths else 'NEW_BYTES'))
        role='raw-provider-lineage' if raw else ('review-evidence' if top=='qa' else ('native' if '/natives/' in rel or '/high-res/' in rel or '/production/' in rel else ('derivative' if '/derivatives/' in rel or '/consumers/' in rel or '/runtime-code-' in rel else 'asset-metadata-or-reference')))
        rows.append({'path':rel,'bytes':n,'sha256':digest,'difference':state,'role':role,'baselineBytePaths':hashpaths.get(digest,[])[:3]})
write('asset-inventory.json', {'baseline':'docs/migration/device-handoff-20261009/transfer-manifest.json','baselineSHA256':sha(ROOT/'docs/migration/device-handoff-20261009/transfer-manifest.json'),'files':rows,'counts':dict(collections.Counter(r['difference'] for r in rows))})
write('sizes-before.json',dict(categories))
required=['AGENTS.md','START-HERE.md','CURRENT-STATUS.md','DECISIONS.md','docs/SESSION-HANDOFF.md','docs/BUILD-PROGRESS.md','docs/plan/README.md']
index=(ROOT/'docs/plan/README.md').read_text(encoding='utf-8-sig')
for link in re.findall(r'\]\(([^)]+)\)',index):
    if '://' not in link:
        p=(ROOT/'docs/plan'/link.split('#')[0]).resolve()
        if p.is_file() and p.suffix in {'.md','.txt','.json'} and p.is_relative_to(ROOT): required.append(p.relative_to(ROOT).as_posix())
docs=[]
for rel in sorted(set(required)):
    p=ROOT/rel
    if p.exists():
        data=p.read_text(encoding='utf-8-sig'); docs.append({'path':rel,'bytes':p.stat().st_size,'sha256':sha(p),'read':True})
    else: docs.append({'path':rel,'missing':True})
write('document-inventory.json',docs)
protected=json.loads((ROOT/'qa/planner-blocker-report-audit-20261011/protected.json').read_text())
write('changes-since-prior-audit.json', [{'path':k.replace('\\','/'),'priorSHA256':v,'currentSHA256':sha(ROOT/k) if (ROOT/k).is_file() else None} for k,v in protected.items() if not (ROOT/k).is_file() or sha(ROOT/k)!=v])
packages=[]
for p in list((ROOT/'delivery').glob('*.apk'))+list((ROOT/'android/app/build/outputs/apk').rglob('*.apk')):
    item={'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}
    with zipfile.ZipFile(p) as z:
        mismatches=[]; missing=[]; count=0
        for q in [ROOT/'index.html', *[x for x in (ROOT/'src').rglob('*') if x.is_file()]]:
            rel=q.relative_to(ROOT).as_posix(); name='assets/www/'+rel; count+=1
            try: digest=hashlib.sha256(z.read(name)).hexdigest()
            except KeyError: missing.append(rel); continue
            if digest!=sha(q): mismatches.append(rel)
        item.update(sourceFilesChecked=count,mismatches=mismatches,missing=missing)
        item['badCRCEntry']=z.testzip()
    packages.append(item)
write('packages.json',packages)
payloads=[]
for r in baseline['payloads']:
    p=ROOT/r['sourcePath']; payloads.append({**r,'presentAtRecordedPath':p.is_file()})
write('prior-payloads.json',payloads)
print(json.dumps({'assetCounts':dict(collections.Counter(r['difference'] for r in rows)),'newBytes':sum(r['bytes'] for r in rows if r['difference']!='UNCHANGED_BASELINE'),'packages':packages,'priorPayloads':payloads,'documentCount':len(docs),'sizes':dict(categories)},indent=2))
