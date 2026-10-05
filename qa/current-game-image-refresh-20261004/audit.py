"""Read-only local QA. Writes only this new QA folder; no imports of executors."""
import hashlib, json, pathlib, re, zipfile
from datetime import datetime, timezone
from PIL import Image

ROOT=pathlib.Path('C:/dev/ages-of-dominion-reborn')
OUT=ROOT/'qa/current-game-image-refresh-20261004'
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''): h.update(block)
    return h.hexdigest()
def save(name,value): (OUT/name).write_text(json.dumps(value,indent=2,ensure_ascii=False),encoding='utf-8')
def meta(p):
    row={'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p),'mtimeUTC':datetime.fromtimestamp(p.stat().st_mtime,timezone.utc).isoformat()}
    if p.suffix.lower() in ('.png','.jpg','.webp'):
        with Image.open(p) as im:
            im.load(); row.update(size=list(im.size),mode=im.mode)
            if 'A' in im.getbands(): row['alphaBBox']=im.getchannel('A').getbbox()
    return row

if __name__=='__main__':
    protected=[]
    for folder in ['assets','src','scripts','android','dist','www']:
        for p in (ROOT/folder).rglob('*'):
            if p.is_file() and not any(v in p.parts for v in ['.gradle','intermediates','node_modules']):
                protected.append({'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)})
    if not (OUT/'protected-before.json').exists(): save('protected-before.json',protected)
    latest=ROOT/'docs/plan/IMAGE-DELIVERY-INTERFACE-V5-2026-10-04.json'
    interface=json.loads(latest.read_text(encoding='utf-8-sig'))
    ledger=json.loads((ROOT/interface['hashLedger']).read_text(encoding='utf-8-sig'))
    bindings=[]
    def walk(o):
        if isinstance(o,dict):
            if 'path' in o and 'sha256' in o:
                p=ROOT/o['path']; row=meta(p) if p.is_file() else {'path':o['path'],'missing':True}
                row['expectedSHA256']=o['sha256']; row['hashMatches']=row.get('sha256')==o['sha256'];bindings.append(row)
            for v in o.values():walk(v)
        elif isinstance(o,list):
            for v in o:walk(v)
    walk(ledger); save('image-v5-bindings.json',bindings)
    decisions=[]
    for row in interface['decisions']:
        p=ROOT/row['output']; current=meta(p); current.update(id=row['id'],decision=row['decision'],recordedHash=row.get('sha256'))
        if row.get('sha256'): current['recordedHashMatches']=row['sha256']==current['sha256']
        decisions.append(current)
    save('image-decisions-current.json',decisions)
    native=[meta(ROOT/f'assets/high-res/final-native2k/rig-source-parts-{c}.png') for c in ['ranger','knight','healer','paladin']]
    save('rig-native-sources.json',native)
    report=json.loads((ROOT/'qa/code-matte-journey-20261004/report.json').read_text(encoding='utf-8-sig'))
    screenshots=[]
    for p in (ROOT/'qa/code-matte-journey-20261004').glob('*.png'):screenshots.append(meta(p))
    save('code-screenshot-bindings.json',screenshots)
    apk=ROOT/'android/app/build/outputs/apk/release/app-release-unsigned.apk'
    package=meta(apk); rows=[]
    with zipfile.ZipFile(apk) as z:
        for name in z.namelist():
            if name.startswith('assets/www/') and not name.endswith('/'):
                rel=name[len('assets/www/'):]; packaged=hashlib.sha256(z.read(name)).hexdigest()
                row={'path':rel,'packageSHA256':packaged}
                for label,base in [('root',ROOT),('dist',ROOT/'dist'),('www',ROOT/'android/app/src/main/assets/www')]:
                    p=base/rel; row[label+'Matches']=p.is_file() and sha(p)==packaged
                rows.append(row)
    package['closure']=rows; save('apk-current.json',package)
    docs=['AGENTS.md','START-HERE.md','CURRENT-STATUS.md','DECISIONS.md','docs/SESSION-HANDOFF.md','docs/BUILD-PROGRESS.md','docs/PLANNER-VERIFIER-HANDOFF.md','docs/plan/README.md']
    for name in ['INSTALLED-ENVIRONMENT.md','AUDIT-UPDATE.md','MASTER-PLAN.md','REQUIREMENTS-TRACEABILITY.md','VISUAL-DESIGN.md','MOCK-FIDELITY-AUDIT.md','ART-REUSE.md','asset-manifest.json','reviewed-art-ledger.json','raw-inventory.json','public-art-inventory.json','GAME-DATA-REFERENCE.json','INSTALLATION-TRANSFER.md','REVIEW-AND-STATUS.md','NEXT-AI-PROMPT.md','FULL-IMPLEMENTATION-SPEC.md','REQUIREMENTS-MATRIX-CANONICAL-2026-10-04.md','CODE-READY-WORK-MATRIX-2026-10-04.md','CODE-AI-RESUME-2026-10-04.md']:
        docs.append('docs/plan/'+name)
    save('required-reading-inventory.json',[meta(ROOT/p) for p in docs])
    sessions=pathlib.Path('C:/Users/pupan/.codex/sessions/2026/10/04')
    narratives=[]
    for p in sessions.glob('*.jsonl'):
        if not any(s in p.name for s in ['ab66','ab6b','ab6e']):continue
        messages=[]
        for line in p.open(encoding='utf-8'):
            o=json.loads(line); q=o.get('payload',{})
            if o.get('type')=='response_item' and q.get('type')=='message' and q.get('role')=='assistant':
                for c in q.get('content',[]):
                    if c.get('type')=='output_text' and '[external_agent_tool_call:' not in c.get('text',''):messages.append(c['text'])
        narratives.append({'session':p.name,'lastNarrative':messages[-1] if messages else None})
    save('executor-local-narratives.json',narratives)
    summary={'atUTC':datetime.now(timezone.utc).isoformat(),'protectedFiles':len(protected),'imageV5LedgerRows':len(bindings),'v5HashFailures':[r['path'] for r in bindings if not r['hashMatches']],'decisionHashFailures':[r['id'] for r in decisions if r.get('recordedHashMatches') is False],'apkSHA256':package['sha256'],'apkBytes':package['bytes'],'packageEntries':len(rows),'closureFailures':[r for r in rows if not all(r[k] for k in ['rootMatches','distMatches','wwwMatches'])]}
    save('summary.json',summary);print(json.dumps(summary,indent=2))
