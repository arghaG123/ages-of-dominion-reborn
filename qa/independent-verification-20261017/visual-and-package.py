from pathlib import Path
from PIL import Image,ImageDraw,ImageOps
import json,hashlib,zipfile,ast,struct,sys,re
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(n,x):(OUT/n).write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf8')
def board(rows,name,cols=5,w=320,h=220):
    im=Image.new('RGB',(cols*w,((len(rows)+cols-1)//cols)*h),'#24272b');d=ImageDraw.Draw(im)
    for i,(label,file) in enumerate(rows):
        x=i%cols*w;y=i//cols*h
        try:
            src=Image.open(ROOT/file).convert('RGBA');src.thumbnail((w-10,h-36))
            bg=Image.new('RGBA',src.size,'#74777b');bg.alpha_composite(src)
            im.paste(bg.convert('RGB'),(x+(w-src.width)//2,y+22))
            d.text((x+5,y+3),label,fill='white')
        except Exception as e:d.text((x+5,y+3),str(e)[:40],fill='red')
    im.save(OUT/name)
def visuals():
    ref=ROOT/'design-preview/generated/landscape-mocks-20261003-efcd7a7e/images'
    refs=sorted(ref.glob('*.jpg'));put('mock-identities.json',[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'size':Image.open(p).size} for p in refs])
    for start in [0,15]:board([(p.name,p.relative_to(ROOT).as_posix()) for p in refs[start:start+15]],f'mocks-{start+1}-{min(start+15,len(refs))}.jpg')
    kits=json.loads((ROOT/'src/data/hero-kit-eras-20261017.json').read_text())
    rows=[];identity=[]
    for c,eras in kits['classes'].items():
        for era in ['ancient','medieval','powder','mech']:
            r=eras[era];p=ROOT/r['file'];identity.append({'class':c,'era':era,**r,'actualSHA256':sha(p),'hashMatch':sha(p)==r['sha256']});rows.append((f'{c} {era}',r['file']))
    board(rows,'class-kits-32.jpg',4,250,370);put('kit-identity.json',identity)
    ages=['stone','bronze','iron','medieval','gunpowder','industrial','modern','future']
    for start in [0,4]:
        rows=[(f'{a} {phase}',f'assets/derivatives/mock-led-20261016/kingdom/kingdom-{a}-{phase}.png') for a in ages[start:start+4] for phase in ['ground','scaffold','wall','wall-tall']]
        board(rows,f'walls-{start+1}-{start+4}.jpg',4,420,260)
    native=[(p.parent.name,p.relative_to(ROOT).as_posix()) for p in (ROOT/'qa/mock-led-executor-20261016/style-repair').glob('*/preview-gray.jpg')]
    board(native,'latest-body-native-overview.jpg',5,240,350)
    motion=[(p.name,p.relative_to(ROOT).as_posix()) for p in (ROOT/'qa/mock-led-executor-20261016/motion-extremes').glob('*.png')]
    board(motion,'motion-extremes-25.jpg',5,300,240)
    modes=json.loads((ROOT/'src/data/mode-scenes.json').read_text(encoding='utf8'))
    for mode in ['adventure','tactical','defense']:
        board([(f'{mode} {ages[i]}',p) for i,p in enumerate(modes[mode])],f'{mode}-8-current.jpg',4,420,260)
    # Exclude label rows to compare the actual rendered pose pixels.
    poseComparisons=[]
    for role in ['knight','ranger','barbarian','warlock','healer']:
        parts=[]
        for clip in ['walk','attack','hit','cast','death']:
            p=ROOT/f'qa/mock-led-executor-20261016/motion-extremes/{role}_{clip}.png'
            im=Image.open(p).convert('RGBA');parts.append(hashlib.sha256(im.crop((0,55,im.width,im.height)).tobytes()).hexdigest())
        poseComparisons.append({'role':role,'distinctPosePixelHashesIgnoringLabels':len(set(parts)),'clipsCompared':5})
    put('motion-evidence-pixel-comparison.json',poseComparisons)
    # Decode every cited executor raster; existence is separate from relevance/currentness.
    rows=[]
    for p in (ROOT/'qa/mock-led-executor-20261016').rglob('*'):
        if p.suffix.lower() in ['.png','.jpg','.jpeg']:
            try:
                with Image.open(p) as im:im.load();rows.append({'path':p.relative_to(ROOT).as_posix(),'size':im.size,'decode':True})
            except Exception as e:rows.append({'path':p.relative_to(ROOT).as_posix(),'decode':False,'error':str(e)})
    put('executor-image-decode.json',rows)
def package():
    original=ROOT/'scripts/verify-package-20261011.py';tree=ast.parse(original.read_text())
    funcs=ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[])
    ns={'ROOT':ROOT,'hashlib':hashlib,'json':json,'struct':struct,'Path':Path,'re':re,'load':lambda p:json.loads((ROOT/p).read_text(encoding='utf-8-sig'))}
    exec(compile(funcs,str(original),'exec'),ns)
    expected=set(ns['closure']());baseCount=len(expected)
    kits=json.loads((ROOT/'src/data/hero-kit-eras-20261017.json').read_text())
    for eras in kits['classes'].values():
        for v in eras.values():expected.add(v['file'])
    for age in ['stone','bronze','iron','medieval','gunpowder','industrial','modern','future']:
        for phase in ['ground','scaffold','wall','wall-tall']:expected.add(f'assets/derivatives/mock-led-20261016/kingdom/kingdom-{age}-{phase}.png')
    hashes={p:sha(ROOT/p) for p in expected if (ROOT/p).is_file()}
    result={'scope':'Read-only existing package; all current src/catalog closure plus dynamic Kingdom state paintings and class-kit variants','legacyCheckerExpected':baseCount,'expected':len(expected),'missingSource':sorted(expected-hashes.keys())}
    for name,root in [('dist',ROOT/'dist'),('www',ROOT/'android/app/src/main/assets/www')]:
        result[name]={'missing':[p for p in sorted(expected) if not (root/p).is_file()], 'different':[p for p in sorted(hashes) if (root/p).is_file() and sha(root/p)!=hashes[p]]}
    apk=ROOT/'android/app/build/outputs/apk/release/ages-of-dominion-reborn-preview-release-unsigned-20261011.apk'
    result['apk']={'path':apk.relative_to(ROOT).as_posix(),'bytes':apk.stat().st_size,'sha256':sha(apk)}
    with zipfile.ZipFile(apk) as z:
        names=set(z.namelist());result['apk']['missing']=[p for p in sorted(expected) if 'assets/www/'+p not in names]
        result['apk']['different']=[p for p in sorted(hashes) if 'assets/www/'+p in names and hashlib.sha256(z.read('assets/www/'+p)).hexdigest()!=hashes[p]]
        result['apk']['crcBadEntry']=z.testzip()
        strings=ns['manifest_strings'](z.read('AndroidManifest.xml'))
        result['apk']['permissions']=[s for s in strings if s.startswith('android.permission.')]
        result['apk']['applicationIds']=[s for s in strings if s.startswith('com.agesofdominion.')]
        result['apk']['nativeEntryHashes']={n:hashlib.sha256(z.read(n)).hexdigest() for n in sorted(names) if n in ['classes.dex','AndroidManifest.xml','resources.arsc']}
    put('package-current.json',result)
    print(json.dumps({**{k:v for k,v in result.items() if k not in ['dist','www','apk']},'dist':{k:len(v) for k,v in result['dist'].items()},'www':{k:len(v) for k,v in result['www'].items()},'apk':{k:v if k not in ['missing','different'] else len(v) for k,v in result['apk'].items()}},indent=2))
if __name__=='__main__':
    if sys.argv[1]=='visuals':visuals()
    if sys.argv[1]=='package':package()
