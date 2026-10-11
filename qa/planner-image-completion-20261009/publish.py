import sys,json,re,datetime,html,collections
from pathlib import Path
ROOT=Path('C:/dev/ages-of-dominion-reborn');QA=Path(__file__).resolve().parent
sys.path.insert(0,str(QA));from audit_common import sha,read,dump
refs=[]
for p in sorted((ROOT/'design-preview/generated/landscape-mocks-20261003-efcd7a7e/images').glob('*.jpg')):
    name=p.stem;gate='UNVERIFIED';art='PARTIAL'
    if 'kingdom' in name:art='FAIL'
    elif 'adventure' in name or 'defense' in name:art='FAIL'
    refs.append({'reference':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'screen':name,'imageGate':art,'runtimeReferenceFidelity':gate,'ownerAcceptance':gate,'evidence':'Current whole-scope-status.json and per-ID results; no new live integrated screen capture'})
dump('30-reference-coverage.json',refs)
packchecks=[]
for owner in ['actors','environment']:
    base=ROOT/f'qa/image-vertex-repair-20261009/{owner}/regeneration';index=json.loads((base/'ready-index.json').read_text(encoding='utf-8-sig'))
    for entry in index['packs']:
        p=ROOT/entry['path'];j=json.loads(p.read_text(encoding='utf-8-sig'));wire=ROOT/j['wireBodyPath'];body=json.loads(wire.read_text(encoding='utf-8-sig'));parts=[p for c in body.get('contents',[]) for p in c.get('parts',[])]
        packchecks.append({'owner':owner,'id':entry['id'],'packPinMatch':sha(p)==entry['sha256'],'wirePinMatch':sha(wire)==j['wireBodySHA256'],'guideDeclared':bool(j.get('guide')),'wireImageParts':sum('inlineData' in p or 'fileData' in p for p in parts),'packHasDefectEvidence':bool(j.get('defect'))})
dump('pack-index-checks.json',packchecks)
gallery=['stone-reference-guide-candidates.jpg','kingdom-candidates.jpg','actor-native-candidates.jpg','slinger-native-versus-result.jpg','actor-local-results.jpg']+[f'{o}-overview-{i}.jpg' for o in ['environment','actors'] for i in range(1,6)]
content='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Independent image audit — 9 October 2026</title><style>body{background:#1c232c;color:#eef2f5;font:16px system-ui;margin:24px;max-width:1600px}img{width:100%;height:auto}a{color:#b8d4ff}figure{margin:32px 0}figcaption{padding:12px}h1{font-size:26px}</style><h1>Independent image audit — PARTIAL / INCOMPLETE</h1><p>JavaScript ES modules / HTML / CSS / SVG; Node24.19.0. Actual source/candidate/derivative pixel comparisons. These images are planner QA, not playable game screenshots or owner approval.</p><p>12 Kingdom candidates fail fixed geometry; 7 actor candidates await processing; 39 attackers / 8 creatures retain magenta; 8 named environment bases retain green.</p><p><a href="../../docs/plan/IMAGE-COMPLETION-INDEPENDENT-AUDIT-2026-10-09.md">Full report and reserve explanation</a> · <a href="independent-per-id-status.json">Per-ID results</a> · <a href="whole-scope-status.json">Whole scope</a> · <a href="30-reference-coverage.json">30-screen coverage</a></p>'
for n in gallery:content+=f'<figure><figcaption>{html.escape(n)}</figcaption><a href="{n}"><img loading="lazy" src="{n}" alt="{html.escape(n)}"></a></figure>'
(QA/'gallery.html').write_text(content+'</html>',encoding='utf-8')
report='docs/plan/IMAGE-COMPLETION-INDEPENDENT-AUDIT-2026-10-09.md'
targets=['AGENTS.md','START-HERE.md','CURRENT-STATUS.md','DECISIONS.md','docs/SESSION-HANDOFF.md','docs/BUILD-PROGRESS.md','docs/PLANNER-VERIFIER-HANDOFF.md','docs/plan/README.md','docs/plan/AUDIT-UPDATE.md']
updates=[]
for path in targets:
    p=ROOT/path;original=p.read_text(encoding='utf-8-sig');before=sha(p)
    relative=('../../' if path.startswith('docs/plan/') else '../' if path.startswith('docs/') else '')+report
    if path.startswith('docs/plan/'):relative='IMAGE-COMPLETION-INDEPENDENT-AUDIT-2026-10-09.md'
    if path.startswith('docs/') and not path.startswith('docs/plan/'):relative='plan/IMAGE-COMPLETION-INDEPENDENT-AUDIT-2026-10-09.md'
    banner=f'> **Independent Image completion audit — 9 October 2026, 14:00 IST:** [Fresh verification and exact reserve explanation]({relative}). Actual19receipts/12native5504x3072Kingdom candidates +7native2048x2048actor bodies hash/raw-byte/decode PASS; allKingdom replacements geometryFAIL. Both producers say imageWorkComplete=false. AI2 has not consumed7collected bodies; localProcessingComplete is overstated while local repairs/metadata remain. Visible lower magenta39attackers/all8creatures (46incorrectREADY rows), eightnamedgreenbases and32cropaffine warnings remain;32scene clearance independently reproduces24FAIL/8PARTIAL. Producer78Environment/104ActorREADY claims are bounded and not visual acceptance. Currentprotected exposure79.8327USD =71.1156baseline +8.7171repairholds, including15reserve once; ordinaryheadroom0.1673USD/invoicesUNKNOWN. Reserve is a global protected budget allowance with no documented specific purchase/retry purpose; currentauthority does not release it. Local processing of collectedbytes cancontinue; morepaidcalls require exactaffordability reconciliation or ownerbudgetdecision. WholegameINCOMPLETE/runtime-ownerUNVERIFIED/deviceSTOPPED. Planner QA/docs/pointers only;3782protectedfiles unchanged, noprovider/paid/production/game/build/device/Git/storage/message/delegation action. Prior dated history follows.\n\n'
    if 'Independent Image completion audit — 9 October 2026, 14:00 IST' in original:continue
    if original.startswith('Language/framework/version:'):
        line,sep,rest=original.partition('\n');updated=line+'\n\n'+banner+rest.lstrip('\r\n')
    else:updated=banner+original
    p.write_text(updated,encoding='utf-8',newline='')
    updates.append({'path':path,'beforeSHA256':before,'afterSHA256':sha(p),'originalRetained':original in updated or (original.partition('\n')[2].lstrip('\r\n') in updated and original.splitlines()[0] in updated)})
dump('pointer-update.json',updates)
bad=[]
for p in [QA/'gallery.html',ROOT/report]+[ROOT/x for x in targets]:
    t=p.read_text(encoding='utf-8-sig')
    if p.suffix=='.html':links=re.findall(r'(?:src|href)="([^"]+)"',t)
    else:
        links=re.findall(r'\]\(([^)]+)\)',t)
        if p!=ROOT/report:links=[x for x in links if 'IMAGE-COMPLETION-INDEPENDENT-AUDIT' in x][:1]
    for link in links:
        if not link or '://' in link or link.startswith('#'):continue
        target=re.sub(r':\d+$','',link.split('#')[0]);actual=(p.parent/target).resolve()
        if not actual.exists():bad.append({'file':str(p),'link':link})
dump('publication-checks.json',{'reportExists':(ROOT/report).is_file(),'galleryImages':len(gallery),'screenReferences':len(refs),'pointerUpdates':len(updates),'historyRetained':all(x['originalRetained'] for x in updates),'missingLinks':bad,'indexedPacks':len(packchecks),'pinFailures':[p for p in packchecks if not p['packPinMatch'] or not p['wirePinMatch']]})
print(json.dumps({'pointerUpdates':len(updates),'missingLinks':bad,'pinFailures':[p for p in packchecks if not p['packPinMatch'] or not p['wirePinMatch']],'actorWireGuidesMissing':sum(p['owner']=='actors' and p['wireImageParts']==0 for p in packchecks)},indent=2))
