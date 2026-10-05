"""Local-only image audit, full decode and bounded visual review sheets."""
from pathlib import Path
import json,hashlib,base64,re,collections,sys
from datetime import datetime,timezone
from PIL import Image,ImageDraw
R=Path('C:/dev/ages-of-dominion-reborn'); Q=R/'qa/later71-independent-audit-20261004'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def digest(b):return hashlib.sha256(b).hexdigest()
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
prefix='closing-' if '--closing' in sys.argv else ''
def put(n,v):(Q/(prefix+n)).write_text(json.dumps(v,indent=2),encoding='utf-8')
m=read(R/'docs/plan/IMAGE-LATER73-EXECUTION-MANIFEST-2026-10-04.json');j=read(R/'docs/plan/image-production/interactive-2k-later73-journal.json')
rows=[];usage=[];protected=[]
for v in m['items']:
 id=v['id'];p=R/v['localPackDir'];wa=read(p/'write_ahead_request.json') if (p/'write_ahead_request.json').exists() else {}
 row={'id':id,'group':v['group'],'status':wa.get('status'),'writeAhead':wa,'bodyHashMatch':sha(p/'request_body.json')==wa.get('bodySHA256') if (p/'request_body.json').exists() else False}
 if (p/'request_body.json').exists():
  body=read(p/'request_body.json');parts=body.get('contents',[{}])[0].get('parts',[]);cfg=body.get('generationConfig',{})
  row['config']=cfg;row['requestTextMatchesManifest']=parts[0].get('text')==v['prompt'];row['attachedImageCount']=sum('inlineData' in x for x in parts)
  refs=[]
  for part in parts:
   if 'inlineData' in part:refs.append(digest(base64.b64decode(part['inlineData']['data'])))
  row['attachedReferenceHashes']=refs;row['selectedSourceHashes']=[x.get('sha256') for x in v.get('sources',[])];row['referencesMatchSelected']=refs==row['selectedSourceHashes'][:len(refs)]
 final=R/'assets/high-res/final-native2k'/f'{id}.png'
 if final.exists():
  with Image.open(final) as im:im.load();row['dimensions']=im.size;row['mode']=im.mode;row['format']=im.format
  row['finalFile']=final.relative_to(R).as_posix();row['sha256']=sha(final);row['bytes']=final.stat().st_size
  row['packOutputMatch']=sha(p/'output.png')==row['sha256'];row['writeAheadOutputMatch']=wa.get('sha256')==row['sha256']
  resp=read(p/'response.json');imgparts=[x for c in resp.get('candidates',[]) for x in c.get('content',{}).get('parts',[]) if 'inlineData' in x]
  row['responseImageCount']=len(imgparts);row['responseImageHashMatches']=[digest(base64.b64decode(x['inlineData']['data']))==row['sha256'] for x in imgparts]
  row['rawResponseSHA256']=sha(p/'response.json');row['responseIdPresent']=bool(resp.get('responseId'));row['createTime']=resp.get('createTime');row['finishReasons']=[c.get('finishReason') for c in resp.get('candidates',[])];row['usage']=resp.get('usageMetadata',{})
  usage.append({'id':id,'usage':row['usage'],'journalCost':next((x.get('costUSD') for x in j['attempts'] if x['id']==id and x['status']=='SUCCEEDED'),None)})
  protected.extend([{'file':final.relative_to(R).as_posix(),'sha256':row['sha256']},{'file':(p/'response.json').relative_to(R).as_posix(),'sha256':row['rawResponseSHA256']}])
 rows.append(row)
success=[r for r in rows if r.get('finalFile')];unknown=[r for r in rows if str(r['status']).startswith('UNKNOWN')]
summary={'at':datetime.now(timezone.utc).isoformat(),'selected':len(rows),'uniqueIDs':len({r['id'] for r in rows}),'finalFiles':len(success),'groups':dict(collections.Counter(r['group'] for r in success)),'native2048PNGFullDecode':sum(r.get('dimensions')==(2048,2048) and r.get('format')=='PNG' for r in success),'modes':dict(collections.Counter(r.get('mode') for r in success)),'uniqueImageHashes':len({r['sha256'] for r in success}),'unknownIDs':[r['id'] for r in unknown],'technicalFailures':[r['id'] for r in success if not(r['packOutputMatch'] and r['writeAheadOutputMatch'] and all(r['responseImageHashMatches']) and r['bodyHashMatch'] and r['requestTextMatchesManifest'] and r['referencesMatchSelected'])],'journalStatusCounts':dict(collections.Counter(x['status'] for x in j['attempts'])),'journalSummary':j['summary'],'sumUniqueSucceededCost':sum(u['journalCost'] for u in usage),'unknownBoundUSD':len(unknown)*.143612,'retainedExposureEstimateUSD':62.8496+sum(u['journalCost'] for u in usage)+len(unknown)*.143612,'invoice':'UNKNOWN','finalPNGBytes':sum(r['bytes'] for r in success)}
put('audit.json',{'summary':summary,'rows':rows});put('usage.json',usage);put('protected-start.json',protected)
# No asset mutation: overview thumbnails and explicit labels in this QA directory.
groups=[('heroes',[r for r in success if '-A-' in r['group']]),('mount-rig-rival',[r for r in success if '-B-' in r['group']]),('army',[r for r in success if '-C-' in r['group']])]
for name,items in groups:
 for k in range(0,len(items),16):
  subset=items[k:k+16];sheet=Image.new('RGB',(1200,340*((len(subset)+3)//4)),(225,225,225));d=ImageDraw.Draw(sheet)
  for t,r in enumerate(subset):
   with Image.open(R/r['finalFile']) as im:thumb=im.convert('RGB');thumb.thumbnail((288,288))
   x=(t%4)*300;y=(t//4)*340;sheet.paste(thumb,(x+6,y+6));d.text((x+6,y+300),r['id'],fill=(0,0,0))
  sheet.save(Q/f'{prefix}{name}-{k//16+1}.jpg',quality=91)
print(json.dumps(summary,indent=2));print(json.dumps(usage[:1],indent=2))
