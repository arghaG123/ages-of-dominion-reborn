"""Read-only original checks and annotated registration evidence; no production art processing."""
import base64, hashlib, json, re
from pathlib import Path
from PIL import Image, ImageDraw
from inspect import ROOT, OUT, read, sha, sheet

snapshot=read(OUT/'local-snapshot.json')
associations=[]
for b in ['01','02','03']:
    folder=ROOT/f'assets/production/production-{b}-20261003'
    manifest=read(folder/'manifest.json'); byhash={i['promptSHA256']:i for i in manifest['items']}
    report=read(folder/'collection-report.json'); outputs={o['id']:o for o in report['outputs']}
    seen=set()
    for raw in (folder/'provider-output').glob('predictions.jsonl'):
        for line in raw.open(encoding='utf-8'):
            row=json.loads(line); texts=[p['text'] for c in row['request']['contents'] for p in c.get('parts',[]) if p.get('text')]; assert len(texts)==1; text=texts[0]
            matches=[h for h in byhash if h==hashlib.sha256(text.encode()).hexdigest()]
            if len(matches)!=1: raise ValueError('Ambiguous prompt hash association')
            spec=byhash[matches[0]]; blobs=[]
            for candidate in row['response'].get('candidates',[]):
                for part in candidate.get('content',{}).get('parts',[]):
                    inline=part.get('inlineData',{})
                    if inline.get('mimeType','').startswith('image/'): blobs.append(base64.b64decode(inline['data']))
            assert len(blobs)==1 and spec['id'] not in seen
            seen.add(spec['id']); output=outputs[spec['id']]
            associations.append({'batch':folder.name,'id':spec['id'],'promptHashFound':True,'promptTextFound':spec['prompt'] in text,'rawImageMatchesSaved':hashlib.sha256(blobs[0]).hexdigest()==sha(ROOT/output['file'])})
    assert len(seen)==30

contract=read(ROOT/'docs/plan/IMPLEMENTATION-CONTRACT.json')
pairs=[]
for b,id in [('01','tactical-terrain'),('01','kingdom-terrain-iron'),('03','kingdom-terrain-stone'),('03','adventure-terrain-plains'),('03','defense-terrain-plains')]:
    output=next(x for x in snapshot['assets'] if x['batch'].split('-')[1]==b and x['id']==id)
    g=contract['geometry'][output['mode']]; a,bm,c,d,e,f=g['worldToSource']
    def p(x,y):return(a*x+c*y+e,bm*x+d*y+f)
    with Image.open(ROOT/output['file']) as original: im=original.convert('RGB')
    draw=ImageDraw.Draw(im)
    for site in g['sites']:
        x,y,w,h=site['rect']; draw.line([p(x,y),p(x+w,y),p(x+w,y+h),p(x,y+h),p(x,y)],fill='#00ffff',width=3)
    for bridge in g['bridges']:
        x,y,w,h=bridge['rect'];draw.line([p(x,y),p(x+w,y),p(x+w,y+h),p(x,y+h),p(x,y)],fill='#ffff00',width=4)
    for label,(x,y) in g['anchors'].items():
        sx,sy=p(x,y);draw.line([(sx-8,sy),(sx+8,sy)],fill='#ff00ff',width=3);draw.line([(sx,sy-8),(sx,sy+8)],fill='#ff00ff',width=3);draw.text((sx+8,sy),label,fill='white',stroke_width=1,stroke_fill='black')
    name=output['batch'].split('-')[1]+'-'+id+'-registration'; target=OUT/(name+'.png'); im.save(target)
    pairs.extend([(name,target),(output['mode']+' contract guide',ROOT/g['guide'])])
sheet('registration-pairs',pairs,640,370,2)
result={'associations':associations,'all90PromptAndRawMatches':all(x['promptTextFound'] and x['rawImageMatchesSaved'] for x in associations),'diagnosticNote':'Annotations show proposed contract positions over original pixels. They are not approved composites or edits to source art.'}
(OUT/'association-check.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'associations':len(associations),'all90PromptAndRawMatches':result['all90PromptAndRawMatches']}))
