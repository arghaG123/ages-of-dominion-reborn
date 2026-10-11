from audit import *
from PIL import Image
import shutil
# Persist the other authorized cleanup's small evidence and make its recovery tool portable.
external=Path('C:/Users/TechnoExponent/Documents/Codex/2026-10-09/reborn-storage-audit/outputs')
dest=ROOT/'docs/storage-cleanup/preview-retirement-20261009';dest.mkdir(parents=True,exist_ok=True)
for n in ['comparison-preview-restore-manifest.json','preview-cleanup-result.json','cleanup-result.json']:
    shutil.copy2(external/n,dest/n)
t=(external/'restore-comparison-previews.py').read_text()
assert 'ROOT = Path(r"C:\\dev\\ages-of-dominion-reborn")' in t
t=t.replace('ROOT = Path(r"C:\\dev\\ages-of-dominion-reborn")','ROOT = Path(__file__).resolve().parents[3]')
(dest/'restore-comparison-previews.py').write_text(t)
manifest=json.loads((dest/'comparison-preview-restore-manifest.json').read_text())
write('preview-recovery-portability.json',{'copiedFromOtherAuthorizedCleanup':True,'portableRoot':'Path(__file__).resolve().parents[3]','manifestHashMatches':sha(ROOT/'qa/image-vertex-repair-20261009/environment/composites/composites_manifest.json')==manifest['compositesManifestSha256'],'sceneHashMatches':sha(ROOT/'qa/image-vertex-repair-20261009/environment/scenes.json')==manifest['scenesSha256'],'historicalExactReadbackEntries':len(manifest['pngs']),'freshRendering':'NOT_REPEATED; root calculation only changed; historical exact reproduction evidence retained'})
catalog=read('src/data/consumer-catalog-20261007.json');rows=[]
for r in catalog['assets']:
    errors=[]
    for prefix in ['source','output']:
        n=r.get(prefix+'Path');h=r.get(prefix+'Sha256')
        if n:
            p=ROOT/n
            if not p.is_file():errors.append(prefix+':MISSING')
            elif h and sha(p)!=h:errors.append(prefix+':HASH')
    rows.append({'id':r['id'],'runtimeGate':r['gates']['runtime'],'errors':errors})
write('consumer-checks.json',{'rows':len(rows),'counts':dict(collections.Counter(r['runtimeGate'] for r in rows)),'checks':rows,'eligibilityDoesNotProveBinding':True,'slingerBoundInOverride':read('src/data/plate-overrides-20261007.json')['troops'].get('0-ranged') is not None,'newUnifiedPathsReferencedInSource':any('image-unified-reserve-20261009' in p.read_text(encoding='utf-8-sig') for p in (ROOT/'src').rglob('*') if p.is_file())})
# Correct the initial compressed-size API label: it does not prove disk allocation.
x=read('qa/planner-device-handoff-20261009/inventory.json')
for g in x['groups'].values():g['compressedFileSizeWBytes']=g.pop('allocatedBytes')
x['allocatedBytesStatus']='Initial GetCompressedFileSizeW is not a disk allocation proof. See storage-final.json for FILE_STANDARD_INFO.'
write('inventory.json',x)
print('Consumer',len(rows),'errors',sum(bool(r['errors']) for r in rows),'portable previews',len(manifest['pngs']),flush=True)
