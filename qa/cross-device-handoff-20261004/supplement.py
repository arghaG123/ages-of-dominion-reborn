"""Read-only collection/alpha/archive inspection, new QA diagnostics only."""
from pathlib import Path
import hashlib,json,zipfile,csv,subprocess
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]; OUT=Path(__file__).resolve().parent
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
def load(p):return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
def save(n,x):(OUT/n).write_text(json.dumps(x,indent=2),encoding='utf-8')
rows=[]
for p in sorted((ROOT/'assets/production').glob('production-*/collection-report.json')):
 d=json.loads(p.read_text()); out=d.get('outputs',[])
 for r in out:
  f=ROOT/r['file']; im=Image.open(f); im.load()
  rows.append({'batch':d.get('batch',p.parent.name),'id':r['id'],'path':r['file'],'hashPass':sha(f)==r['sha256'],'size':im.size})
save('production-originals.json',{'collections':len(set(r['batch'] for r in rows)),'outputs':len(rows),'distinctIDs':len(set(r['id'] for r in rows)),'allHashesPass':all(r['hashPass'] for r in rows),'rows':rows})
hi=[]
for r in load('docs/plan/image-production/final-native4k-manifest.json')['items']:
 f=ROOT/r['sourceFile']; im=Image.open(f);im.load()
 hi.append({'id':r['canonicalID'],'path':r['sourceFile'],'sha256':sha(f),'hashPass':sha(f)==r['sourceSHA256'],'size':im.size,'gates':r['gates']})
j=load('docs/plan/image-production/interactive-2k-later73-journal.json'); expected={r['id']:r['sha256'] for r in j['attempts'] if r.get('status')=='SUCCEEDED'}
two=[]
for p in sorted((ROOT/'assets/high-res/final-native2k').glob('*.png')):
 im=Image.open(p); im.load(); two.append({'id':p.stem,'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'journalMatch':sha(p)==expected.get(p.stem),'size':im.size})
save('native-collections.json',{'native4K':hi,'native2K':two,'native2KJournalUniqueSuccessIDs':len(expected)})

paths=['assets/derivatives/actors/v6/troop-industrial-melee.png','assets/derivatives/actors/v6/troop-modern-heavy.png','assets/derivatives/actors/v6/troop-modern-ranged-snow-mound-trimmed.png','assets/derivatives/rigs/v6/healer/boot.png','assets/derivatives/rigs/v6/paladin/head_three_quarter.png']
alpha=[]
for k,p in enumerate(paths):
 im=Image.open(ROOT/p).convert('RGBA'); a=im.getchannel('A'); box=a.getbbox();hist=a.histogram()
 alpha.append({'path':p,'sha256':sha(ROOT/p),'size':im.size,'alphaRange':a.getextrema(),'transparentPixels':hist[0],'visibleAlphaBounds':box,'displayWarning':'Raw RGB in transparent pixels may be shown by a viewer. Judge alpha-composited diagnostics.'})
 crop=im.crop(box);crop.thumbnail((480,600)); sheet=Image.new('RGB',(1440,640),(25,25,25)); dr=ImageDraw.Draw(sheet)
 for i,color in enumerate([(255,255,255),(0,0,0),(110,132,104)]):
  bg=Image.new('RGB',(480,600),color);bg.paste(crop,((480-crop.width)//2,0),crop.getchannel('A'));sheet.paste(bg,(i*480,40))
 dr.text((8,8),p,fill='white');sheet.save(OUT/f'alpha-diagnostic-{k+1}.png')
save('alpha-inspection.json',alpha)

catalogs={}
for name in ['src/data/plate-catalog.json','src/data/anatomy-binding-v1.json','src/data/static-mounts-v1.json','src/data/portrait-cards.json']:
 d=load(name);bound=[]
 def walk(obj):
  if isinstance(obj,dict):
   path=obj.get('file'); digest=obj.get('sha256')
   if path and isinstance(path,str) and (ROOT/path).is_file():bound.append({'path':path,'sha256':sha(ROOT/path),'recorded':digest,'hashPass':sha(ROOT/path)==digest if digest else None})
   for v in obj.values():walk(v)
  elif isinstance(obj,list):
   for v in obj:walk(v)
 walk(d);catalogs[name]=bound
save('consumer-bindings.json',catalogs)

archive=Path('E:/Ages-of-Dominion-Reborn-Migration-2026-10-04/ages-of-dominion-reborn-worktree-2026-10-04-handoff-final6.zip')
backup=Path('C:/dev/ages-of-dominion-reborn-cleanup-backup-2026-10-04/raw-generation-responses')
result={'externalFinal6Exists':archive.exists(),'looseRawBackupExists':backup.exists(),'archiveStatus':'LOCAL_READ_ONLY_COMPARISON_NOT_NEW_DEVICE_RESTORE','latestDeliveryRows':[]}
if archive.exists():
 with zipfile.ZipFile(archive) as z:
  names=set(z.namelist()); result['entryCount']=len(names)
  for name in ['src/client/main.js','src/core/defense.js','scripts/capture-playable-20261004.mjs','docs/plan/IMAGE-DELIVERY-INTERFACE-V6-2026-10-04.json','assets/derivatives/actors/v6/troop-industrial-melee.png','qa/code-playable-20261004/report.json']:
   variants=[n for n in names if n==name or n.endswith('/'+name)]
   entry=variants[0] if variants else None
   result['latestDeliveryRows'].append({'path':name,'entry':entry,'matchesCurrent':hashlib.sha256(z.read(entry)).hexdigest()==sha(ROOT/name) if entry else False})
save('archive-current-check.json',result)

files=[]
for name in ['docs/plan/image-production/budget-ledger.json','docs/plan/image-production/UNIFIED-ACCOUNTING-RECONCILIATION-2026-10-04.json','docs/plan/image-production/reconciled-accounting-ledger.json','docs/plan/image-production/submission.mutex.json','docs/plan/image-production/active-batch.lock.json','docs/plan/image-production/pacing_state.json']:
 files.append({'path':name,'sha256':sha(ROOT/name),'data':load(name)})
save('local-controls-snapshot.json',files)
print(json.dumps({'originals':len(rows),'originalHashesPass':all(r['hashPass'] for r in rows),'native4K':len(hi),'native4KHashesPass':all(r['hashPass'] for r in hi),'native2K':len(two),'native2KJournalPass':all(r['journalMatch'] for r in two),'archive':result,'consumerMismatches':[r for group in catalogs.values() for r in group if r['hashPass'] is False]},indent=2))
