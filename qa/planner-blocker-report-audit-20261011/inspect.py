from pathlib import Path
import hashlib,json,re,zipfile
from PIL import Image,ImageDraw
root=Path('C:/dev/ages-of-dominion-reborn'); out=root/'qa/planner-blocker-report-audit-20261011'
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()
primary=['AGENTS.md','START-HERE.md','CURRENT-STATUS.md','DECISIONS.md','docs/SESSION-HANDOFF.md','docs/BUILD-PROGRESS.md','docs/plan/README.md']
readme=(root/'docs/plan/README.md').read_text(encoding='utf-8-sig')
files=set(root/p for p in primary)
for match in re.findall(r'\]\(([^)]+)\)',readme):
    link=match.split('#')[0]
    if link and not re.match(r'^[a-z]+:',link):files.add((root/'docs/plan'/link).resolve())
for name in ['FULL-IMPLEMENTATION-SPEC.md','MASTER-PLAN.md','REQUIREMENTS-TRACEABILITY.md','REQUIREMENTS-MATRIX-CANONICAL-2026-10-04.md','IMPLEMENTATION-CONTRACT.json','GAME-DATA-REFERENCE.json','DATA-ADOPTION-LEDGER.json','SOURCE-EQUATIONS-ADDENDUM-2026-10-03.md']:files.add(root/'docs/plan'/name)
inventory=[]
for p in sorted(files):
    if p.is_file() and p.suffix in ['.md','.json','.txt']:
        t=p.read_text(encoding='utf-8-sig');inventory.append({'file':str(p.relative_to(root)),'sha256':sha(p),'chars':len(t),'headings':re.findall(r'^#{1,4} .+$',t,re.M),'currentKeywords':{k:t.lower().count(k.lower()) for k in ['morale','resurrection','dwelling','20seconds','INCOMPLETE']}})
    else:inventory.append({'file':str(p),'exists':p.exists(),'textDocument':False})
(out/'document-inventory.json').write_text(json.dumps(inventory,indent=2),encoding='utf-8')
iface=json.loads((root/'docs/plan/IMAGE-COMPLETE-INTERFACE-2026-10-11.json').read_text()); rows=iface['rows']; scenes=iface['scenes']
art={'interfaceSHA256':sha(root/'docs/plan/IMAGE-COMPLETE-INTERFACE-2026-10-11.json'),'sceneRows':len(scenes),'sceneSpatial':{},'sceneRecordHashes':{r['id']:hashlib.sha256(json.dumps(r,sort_keys=True).encode()).hexdigest() for r in scenes}}
for r in scenes:
    spatial=r.get('gates',{}).get('spatial',r.get('qa',{}).get('spatial','UNKNOWN'));art['sceneSpatial'][spatial]=art['sceneSpatial'].get(spatial,0)+1
bodies=json.loads((root/'src/data/hero-bodies-20261011.json').read_text());art['bodies']=len(bodies['bodies']);art['healerPresent']='healer' in bodies['bodies'];art['bodyNote']=bodies['note']
classification=json.loads((root/'qa/code-image-repair-20261011/plate-classification.json').read_text());art['classifiedRows']=len(classification['rows']);art['unreviewedRows']=sum(r['review'].startswith('UNREVIEWED') for r in classification['rows'])
art['bodyNativeChecks']=[{'id':k,'exists':(root/v['native']).exists(),'hashMatch':(root/v['native']).exists() and sha(root/v['native'])==v['nativeSHA256']} for k,v in bodies['bodies'].items()]
(out/'art-status.json').write_text(json.dumps(art,indent=2),encoding='utf-8')
apks=list((root/'android/app/build/outputs/apk').rglob('*.apk'));packages=[]
sample=['src/client/main.js','src/client/hero-room.js','src/client/game.css','src/data/plate-overrides-20261007.json','src/core/battle.js','src/core/campaign.js','src/core/defense.js','src/core/mechanics.js','src/core/rules.js']
for apk in apks:
    row={'path':str(apk.relative_to(root)),'bytes':apk.stat().st_size,'sha256':sha(apk),'samples':[]}
    with zipfile.ZipFile(apk) as z:
        for name in sample:
            key='assets/www/'+name
            if key not in z.namelist():key='assets/'+name
            h=hashlib.sha256(z.read(key)).hexdigest() if key in z.namelist() else None
            row['samples'].append({'file':name,'match':h==sha(root/name),'apkSHA256':h,'sourceSHA256':sha(root/name)})
    packages.append(row)
(out/'package.json').write_text(json.dumps(packages,indent=2),encoding='utf-8')
protected={str(p.relative_to(root)):sha(p) for p in list((root/'src').rglob('*'))+list((root/'tests').rglob('*')) if p.is_file()};protected['qa/blocker-repair-20261011/adoption.json']=sha(root/'qa/blocker-repair-20261011/adoption.json');(out/'protected.json').write_text(json.dumps(protected,indent=2),encoding='utf-8')
plate=root/'assets/derivatives/image-repair-20261011/actors/plates/tower-industrial-support.png';im=Image.open(plate).convert('RGBA');im.thumbnail((350,650));sheet=Image.new('RGB',(700,680),(34,40,42))
for n,bg in enumerate([(34,40,42),(208,208,196)]):
    panel=Image.new('RGBA',(350,650),bg+(255,));panel.alpha_composite(im,((350-im.width)//2,650-im.height));sheet.paste(panel.convert('RGB'),(n*350,30))
ImageDraw.Draw(sheet).text((12,8),'Industrial support: actual alpha over dark and light backgrounds',fill='white');sheet.save(out/'support-composite.jpg',quality=86)
helper=(root/'qa/planner-blocker-solutions-20261011/layout-probe.mjs').read_text()
helper=helper.replace("const port = Number(process.env.AOD_PORT || 4619)","const port = Number(process.env.AOD_PORT || 4627)").replace("const debugPort = Number(process.env.AOD_DEBUG_PORT || 9419)","const debugPort = Number(process.env.AOD_DEBUG_PORT || 9427)").replace("'planner-blocker-solutions-20261011'","'planner-blocker-report-audit-20261011'")
helper=helper.replace("for (const name of ['hero', 'forge'])", "for (const name of ['hero', 'forge', 'kingdom', 'adventure'])")
helper=helper.replace("const row = await evaluate(measure);", "if (width === 825) { const shot = await send('Page.captureScreenshot', { format: 'png' }); await writeFile(path.join(outDir, name + '-825x375.png'), Buffer.from(shot.data, 'base64')); }\n      const row = await evaluate(measure);")
helper=re.sub(r'\s*if \(checked.startsWith[^\n]+', '', helper)
helper=helper.replace('|| row.svgButtons ||', "|| (['hero','forge'].includes(row.name) && row.svgButtons) ||")
(out/'layout.mjs').write_text(helper,encoding='utf-8')
print(json.dumps({'documents':len(inventory),'art':{k:v for k,v in art.items() if k not in ['sceneRecordHashes','bodyNote','bodyNativeChecks']},'packages':[{'bytes':p['bytes'],'sha256':p['sha256'],'sampleMismatches':sum(not s['match'] for s in p['samples'])} for p in packages]},indent=2))
