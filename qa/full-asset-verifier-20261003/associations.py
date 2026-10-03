import base64,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows=[]
for folder in sorted((ROOT/'assets/production').glob('production-*-20261003')):
    manifest=read(folder/'manifest.json');items={i['promptSHA256']:i for i in manifest['items']};report=read(folder/'collection-report.json');outputs={o['id']:o for o in report['outputs']};seen=set()
    for line in (folder/'provider-output/predictions.jsonl').open(encoding='utf-8'):
        row=json.loads(line);texts=[p['text'] for c in row['request']['contents'] for p in c.get('parts',[]) if p.get('text')]
        assert len(texts)==1
        promptHash=hashlib.sha256(texts[0].encode()).hexdigest();spec=items[promptHash];blobs=[]
        for candidate in row['response'].get('candidates',[]):
            for part in candidate.get('content',{}).get('parts',[]):
                inline=part.get('inlineData',{})
                if inline.get('mimeType','').startswith('image/'):blobs.append(base64.b64decode(inline['data']))
        assert len(blobs)==1 and spec['id'] not in seen
        seen.add(spec['id']);output=outputs[spec['id']]
        rows.append(dict(batch=folder.name,id=spec['id'],promptSHA256=promptHash,sourceSHA256=output['sha256'],echoPromptMatch=texts[0]==spec['prompt'],rawImageMatchesSaved=hashlib.sha256(blobs[0]).hexdigest()==sha(ROOT/output['file']),responseStatus=row.get('status')))
    assert len(seen)==30
    print(folder.name+' 30 checked',flush=True)
result=dict(rows=rows,count=len(rows),allPass=all(r['echoPromptMatch'] and r['rawImageMatchesSaved'] for r in rows))
(OUT/'associations.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'count':len(rows),'allPass':result['allPass']}))
