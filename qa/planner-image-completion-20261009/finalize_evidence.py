import sys,json,collections,datetime
from pathlib import Path
from PIL import Image
import PIL,numpy,cv2,scipy
ROOT=Path('C:/dev/ages-of-dominion-reborn');QA=Path(__file__).resolve().parent
sys.path.insert(0,str(QA));from audit_common import read,sha,dump
protected=read('qa/planner-image-completion-20261009/input-hashes.json')['files']; changes=[]
for p,h in protected.items():
    actual=sha(ROOT/p) if (ROOT/p).is_file() else None
    if actual!=h:changes.append({'path':p,'before':h,'after':actual})
snap=[]
for owner in ['environment','actors']:
    s=read(f'qa/image-vertex-repair-20261009/{owner}/input_snapshot.json');files=s['files'];items=[dict(v,path=k) for k,v in files.items()] if isinstance(files,dict) else files
    check=[]
    for item in items:
        p=ROOT/item['path'];h=sha(p) if p.is_file() else None
        check.append({'path':item['path'],'match':h==item.get('sha256'),'expectedSHA256':item.get('sha256'),'actualSHA256':h})
    snap.append({'owner':owner,'capturedAt':s.get('capturedAt',s.get('recordedAt')),'checked':len(check),'mismatches':[x for x in check if not x['match']]})
dump('producer-snapshot-preservation.json',snap)
pixels=read('qa/planner-image-completion-20261009/independent-matte-candidates.json');mattebad={p['id'] for p in pixels if p['role'] in ['attacker','creature'] and p['lowerMagentaPixels']>40}
greens={'armory-stone','barracks-stone','farm-bronze','workshop-iron','townhall-industrial','mine-industrial','hall-industrial','adventure-site-town'}
warnings=read('qa/planner-image-completion-20261009/transform-checks.json');warnings={x['id'] for x in warnings}
status=[]
for owner in ['environment','actors']:
    for r in read(f'qa/planner-image-completion-20261009/{owner}-per-id.json'):
        reasons=[]
        if r['id'] in mattebad:reasons.append('Visible magenta lower ground/edge; independently measured and overview inspected')
        if r['id'] in greens:reasons.append('Visible flat green geometric base remains; candidate-only color count paired with pixel review')
        if r['id'] in warnings:reasons.append('Recipe crop origin is nonzero but sourceToOutput is identity')
        if r['geometryWarnings']:reasons.append('Contact point probes do not land on visible paint; point applicability/semantic grounding must be reviewed')
        result='FAIL' if r['status']=='FAIL' or (reasons[:1] and (r['id'] in mattebad or r['id'] in greens or r['id'] in warnings)) else ('PARTIAL' if r['status']=='PARTIAL' else 'UNVERIFIED')
        if r['id'] in ['troop-stone-ranged','troop-stone-melee','troop-industrial-ranged','troop-industrial-heavy','healer-boot'] and not (r['id'] in mattebad or r['id'] in greens or r['id'] in warnings):result='PASS_BOUNDED_STATIC_PIXELS'
        status.append({'id':r['id'],'owner':owner,'producerStatus':r['status'],'independentResult':result,'reasons':reasons,'scope':'Declared art use only; no runtime, complete gait, owner, or device acceptance'})
dump('independent-per-id-status.json',status)
geo=read('qa/planner-image-completion-20261009/independent-clearance.json');scopes=[]
for mode in ['kingdom','adventure','tactical','defense']:
    x=[r for r in geo if r['mode']==mode];scopes.append({'family':mode,'ages':8,'result':'FAIL' if any(r['spatial']=='FAIL' for r in x) else 'PARTIAL','ids':[r['id'] for r in x],'remaining':'Full physical footprint/entrance/height/Wall, banks/decks/approaches/walkable and reference appearance evidence; Code integration separate'})
for name,result,remaining in [('8 class bodies','PARTIAL','7 candidates collected, zero AI2 processed; healer not generated; rigs/sides/sockets/gait incomplete'),('24 troops','PARTIAL','3 Code crops reused + Slinger local crop; remaining sheet/role/matte rows unresolved'),('40 attackers','FAIL','39 measured lower-magenta rows including one PARTIAL; 38 incorrectly READY; Bronze runner HUD, Medieval archer damage'),('8 creatures','FAIL','All 8 lower-magenta/edge defects; drone is a multi-pose sheet'),('6 slots x 8 ages','PARTIAL','48 base icons present; 4 quality/class-kit states not established; 32 recipe affine warnings across actor outputs'),('10 artifacts','PARTIAL','10 rows present; art/use integrity and explicit Code screen bindings open'),('mounts/transports','PARTIAL','4 mount rows plus mounted master; scenery/base, transport identity, sockets and gait unresolved'),('projectile/impact and other FX','PARTIAL','7 effect sheets remain partial; component ROIs alone do not prove semantics, timing or sequences'),('Forge/Inventory/Market/Army/Hero Hall','UNVERIFIED','Asset composites and Code-native dispositions; no current integrated screen acceptance'),('Story/Rival/Quests/Milestones/Tutorial','UNVERIFIED','Reference/Code-native dispositions do not prove connected content or live states'),('music/SFX/settings/help/credits/privacy','UNVERIFIED','Code/audio content and ordinary usable screens are separate gates'),('save/import/export/slots/backup/recovery','UNVERIFIED','No fresh runtime or durability claim tested in this art audit'),('5 War flows','UNVERIFIED','Siege/Duel/Endless/Skirmish/Challenge runtime completion not claimed by Image'),('all30 approved mock screens/four viewports','UNVERIFIED','Current ASSET_COMPOSITE plates are not actual gameplay or owner composition approval')]:scopes.append({'family':name,'result':result,'remaining':remaining})
dump('whole-scope-status.json',scopes)
dump('final-verification.json',{'atUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protectedFilesChecked':len(protected),'protectedChanges':changes,'libraries':{'python':sys.version,'pillow':PIL.__version__,'numpy':numpy.__version__,'opencv':cv2.__version__,'scipy':scipy.__version__},'producerSnapshotChecks':snap,'matteAffectedAttackerCreatureRows':len(mattebad),'greenBaseVisualRows':len(greens),'transformWarnings':len(warnings),'wholeGame':'INCOMPLETE','device':'STOPPED','runtime':'UNVERIFIED','providerLiveState':'UNVERIFIED','billedTotal':'UNKNOWN'})
print('protected checked',len(protected),'changes',len(changes),'snapshots',[(s['owner'],s['checked'],len(s['mismatches'])) for s in snap],'matte',len(mattebad),'affine',len(warnings))
for s in snap:
    print(s['owner'],'snapshot discrepancies',json.dumps(s['mismatches'])[:2400])
