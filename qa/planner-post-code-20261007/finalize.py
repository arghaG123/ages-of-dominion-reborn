import pathlib,json,hashlib,collections,re,html,math
from PIL import Image,ImageDraw
import numpy as np
R=pathlib.Path(__file__).resolve().parents[2];Q=pathlib.Path(__file__).parent
def read(p):return json.loads((R/p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(Q/n).write_text(json.dumps(v,indent=2),encoding='utf-8')
delivery=read('qa/planner-post-code-20261007/delivery-checks.json');consumer=read('qa/planner-post-code-20261007/code-consumer-checks.json');old=read('qa/planner-final-images-20261007/per-id-status.json');snapshot=read('qa/planner-post-code-20261007/input-hashes.json');cat=read('src/data/consumer-catalog-20261007.json');by={x['id']:x for x in cat['assets']};binding={r['id']:r for r in consumer['checks']};rows=[]
actualBuildings={r['id']:r for r in read('qa/planner-post-code-20261007/actual-building-bindings.json')['rows']}
for r in old['rows']:
 r=dict(r);id=r['id'];r['date']='2026-10-07';r['priorPixelEvidence']='qa/planner-final-images-20261007/gallery.html';r['pixelEvidenceScope']='Previous native/overview findings retained only for unchanged producer/source bytes; current binding rechecked.'
 if id in actualBuildings:r['actualBuildingConsumer']=actualBuildings[id]
 if id in {'townhall-iron','townhall-medieval','townhall-modern'}:r['nextAction']='Current old v2 runtime has obvious magenta patch. Validate/reuse adequate newer residual output with corrected metadata; later Code must rebind it. No mandatory reprocessing of clean residual.'
 if id in by:
  a=by[id];r['codeConsumer']={k:a.get(k) for k in ['outputPath','outputSha256','use','producer','gates','sourceToOutput','coordinateFrame','groundContact','heightEnvelope','limitations','blockedBy']};r['currentBindingCheck']=binding[id]
 if id in {'troop-stone-melee','troop-industrial-ranged','troop-industrial-heavy'}:
  r.update(decision='REUSE_VALIDATED_CODE_CROP_BOUNDED',currentConsumerPixel='PASS_BOUNDED',nextAction='Recheck native edges/actual contact/declared static role; reuse unchanged Code crop where adequate. No repeat extraction by default.',reason=['Current Code crop preserves substantial painted body/kit; RGB matches native crop exactly and hashes/dimensions/translations pass. Prior damaged producer remains a separate historical/output identity.']);r['newPixelEvidence']='qa/planner-post-code-20261007/code-repaired-troops.jpg'
 elif id=='troop-stone-ranged':r.update(decision='LOCAL_CHECKER_AWARE_EXTRACTION_REQUIRED',nextAction='Existing native Slinger WITH SLING is useful; painted RGB checker still defeats current Code crop. New bounded checker-aware local sourceROI baseline/correction, no purchase.')
 if id.startswith('hero-') and id.endswith('complete-body-and-gait'):r['nextAction']='AI2 assess genuinely new compatible painted anatomy only; preserve exact missing/failed links, publish full matrices or honest bounded cards. Code integrates after both deliveries.'
 if r.get('producer')=='ENVIRONMENT' and 'terrain-' not in id:r['imageOwner']='ENVIRONMENT'
 elif r.get('producer')=='ACTORS' or id.startswith('hero-'):r['imageOwner']='ACTORS'
 else:r['imageOwner']='ENVIRONMENT'
 if id.startswith('support-env-'):r['nextAction']='AI1 extract feasible clean separable scenery/material or report exact absence/no-new-image-needed; Code authors live support UI.'
 rows.append(r)
save('per-id-status.json',{'status':'INCOMPLETE','date':'2026-10-07','rows':rows,'scope':'Fresh binding/consumer audits and unchanged-content historical pixel findings. Not blanket native-edge or full-art acceptance.'})
vp=read('qa/planner-post-code-20261007/viewport-report.json');alphaCache={};sizes=[];fonts=[]
for row in vp['rows']:
 row['screen']='army' if row['id'].startswith('army-') else 'kingdom'
 for p in row['plates']:
  f=R/p['path']
  if p['path'] not in alphaCache:
   with Image.open(f) as im:
    a=np.asarray(im.convert('RGBA'))[:,:,3];ys,xs=np.where(a>128);alphaCache[p['path']]={'dims':list(im.size),'bbox':[int(xs.min()),int(ys.min()),int(xs.max())+1,int(ys.max())+1] if len(xs) else None,'sha256':sha(f)}
  a=alphaCache[p['path']];bb=a['bbox'];w,h=a['dims'];vw=p['width']*(bb[2]-bb[0])/w if bb else 0;vh=p['height']*(bb[3]-bb[1])/h if bb else 0
  sizes.append({'id':row['id'],'age':row['age'],'viewport':row['viewport'],'path':p['path'],'sha256':a['sha256'],'alpha128BBox':bb,'visibleCssWidth':vw,'visibleCssHeight':vh,'capCss':p['cap'],'pass':max(vw,vh)<=p['cap']+.05,'scope':'Alpha128 visible extents. Canvas bounds also fit. Actual layout clipping remains separate.'})
 for t in row['text']:fonts.append({'id':row['id'],**t})
save('viewport-report-normalized.json',vp);save('visible-alpha-size-checks.json',{'rows':sizes,'allPassing':all(x['pass'] for x in sizes),'fonts':fonts,'minArmyFont':min(t['cssFont'] for t in fonts if t['id'].startswith('army-')),'instrumentation':'Original browser-audit age sizes included stale zero-bounds before layout; replaced by64fresh after-layout fixtures. Original viewport screen number is normalized separately by file ID.'})
requirements=read('qa/planner-final-images-20261007/requirements-status.json')['rows']
for r in requirements:
 r.update(coreTests='107tests/105PASS/2exactguideENOENT',evidencePaths=['qa/planner-post-code-20261007/node-tests.txt','qa/planner-post-code-20261007/browser-report.json','qa/planner-post-code-20261007/viewport-report-normalized.json','qa/planner-post-code-20261007/per-id-status.json'],fresh=True)
 if r['id']=='SYS-07':r.update(status='PARTIAL',scope='Ordinary inertHTML/Tab/Cancel/Escape/onceconfirm PASS; programmatic navigation dismisses modal. Map action counter guard passes; complete event-path isolation FAIL.',nextAction='Code guard programmatic navigation/toolbar/action callbacks while modal open; retest each vector independently.')
 elif r['id']=='SYS-14':r.update(status='PASS',scope='Read-only static package only:333asset source/dist/www/APK matches; all currentsrc/index matches; ZIPCRC valid; previewID/min24/target-compile36/zeropermissions. No device/install/build by planner.',evidencePaths=['qa/planner-post-code-20261007/package-checks.json','qa/planner-post-code-20261007/apk-badging.txt','qa/planner-post-code-20261007/apk-permissions.txt'],nextAction='Rebuild and reverify only after later Code integration changes; device remains stopped.')
 elif r['id'] in ['OWN-03','OWN-14']:r.update(status='PARTIAL',scope='Three subject-preserving Code troop crops +46gear actualadapterconsumers;68catalogeligible entries are not68actualwiring proofs. Source hashes/declaredfiles pass; residual mattes/scenes/fullbodies still fail.',nextAction='Both Image AIs finish owned local scope; laterCode validates and binds each passinguse.')
 elif r['id']=='OWN-08':r.update(status='PARTIAL',scope='Fresh32Army+32Kingdom accelerated age/viewport fixtures. Not earned8age play or developedallbuildingstates.',nextAction='Image8agecoverage; laterCode actual allscreen/state/runtime and earnedprogression evidence.')
 elif r['id']=='SYS-15':r.update(status='FAIL',scope='All32Armyfixtures cap checksPASS; ArmySVGcaptionsmin9.593CSSpx and topfiguresclipunderheader. Freshphone/portrait/modal ordinary evidence bounded; physicalfps/deviceUNVERIFIED.',nextAction='Code fit allscreens into actualchrome safearea and make labels readable atsmallviewports.')
 elif r['id'] in ['OWN-10','OWN-11']:r.update(status='FAIL',scope='Delivered class diagrams/cards/subchains are not complete8classbodies or articulatedmountedgait.',nextAction='AI2 allfeasible anatomy/assembly evidence; Code boundedfallback and later verifiedintegration.')
 elif r['id'] in ['OWN-01','OWN-18','GIT-01']:r['fresh']=False
save('requirements-status.json',{'date':'2026-10-07','status':'INCOMPLETE','rows':requirements,'scope':'37canonical requirements with bounded current source/test/browser/staticpackage and explicit unverified natural/device/owner gates.'})
refs=sorted((R/'design-preview/generated/landscape-mocks-20261003-efcd7a7e/images').glob('*.jpg'))
actual={1:'pixels/home-1280.png',2:'pixels/kingdom-day1.png',3:'viewports/kingdom-age-0-1280x720.png',4:'viewports/kingdom-age-1-1280x720.png',5:'viewports/kingdom-age-2-1280x720.png',6:'viewports/kingdom-age-3-1280x720.png',7:'viewports/kingdom-age-4-1280x720.png',8:'viewports/kingdom-age-5-1280x720.png',9:'viewports/kingdom-age-6-1280x720.png',10:'viewports/kingdom-age-7-1280x720.png',11:'pixels/adventure.png',19:'pixels/hero.png',22:'pixels/forge.png',24:'pixels/army.png',25:'pixels/story.png',28:'pixels/settings.png'}
visual=[]
for i,p in enumerate(refs,1):
 result=Q/actual[i] if i in actual else None;visual.append({'id':f'MOCK-{i:02}','referencePath':p.relative_to(R).as_posix(),'referenceSha256':sha(p),'actualPath':result.relative_to(R).as_posix() if result else None,'actualSha256':sha(result) if result else None,'stateKind':'FIXTURE_SPARSE_AGE' if 3<=i<=10 else 'NATURAL_CURRENT_VISIBLE_STATE' if result else 'NOT_FRESHLY_CAPTURED','composition':'FAIL' if result else 'UNVERIFIED','reason':'Current native UI/terrain/cards visibly differ from primary composition; not owner accepted. Sparse agefixtures are not developedtown targetstates.' if result else 'Required dedicated composition/state not independently captured. Screenshots/tests from otherstates do not close this row.','imageOwners':['ENVIRONMENT','ACTORS'],'codeRemaining':'Build state-aware live composition, not fullmockJPEG; integrate validated clean layers.','owner':'UNVERIFIED'})
save('reference-coverage.json',{'rows':visual,'note':'30canonical targets; exact missing currentstates remain explicit. Tactical freshSkirmish exists separately but is notdeployment/action/result acceptance.'})
coverage=[]
for p in refs:
 text=p.stem;coverage.append({'id':text,'environment':'Clean scenery/material/state-layer coverage; explicit no-new-image-needed ifCode-nativeUI adequate.','actors':'Subject/item/effect coverage where present; explicitNOT_APPLICABLE otherwise.','code':'Live stateful layout/controls/mechanics/integration and actualreferencecomparison.'})
save('two-image-ownership.json',{'status':'INCOMPLETE','environment':{'assets':'assets/derivatives/image-after-code-20261007/environment/','qa':'qa/image-after-code-20261007/environment/','interface':'docs/plan/ENVIRONMENT-ART-AFTER-CODE-INTERFACE-2026-10-07.json'},'actors':{'assets':'assets/derivatives/image-after-code-20261007/actors/','qa':'qa/image-after-code-20261007/actors/','interface':'docs/plan/ACTORS-EQUIPMENT-AFTER-CODE-INTERFACE-2026-10-07.json'},'overlap':'NONE: AI1stationarytower/staticworldeffects;AI2people/gear/projectile/impacteffects. Sharedinputsreadonly; no sharedhelpers/catalog/pointers. Each uses existing counterpartinputs or declaredmissinglayer.','coverage':coverage,'codeAfterBoth':['Validate typed rows/transforms and integrate passingdeclareduses into exactcatalogs','Connect artifact/effect/material/mount/assembly adapters where currentcatalogonly declares eligibility','Complete all8age/all30reference/livestate screen compositions and readable-safearea layouts','Guard allmodal eventpaths including programmaticnav/toolbar','Resolve inactivegeometry/camera proposals only with recorded authority','Demonstrate ordinary build/recruit/travel/fight/loot/equip/return/Siegewin/once-settle/reload and6slots/5Warflowroundtrips; earned8age separate','Preserve sourcedmechanics/save/idempotency/practiceisolation; moralescopedpending','Reverify tests/exactguidegaps; rebuild web/APKclosure only after actualintegration changes'],'paid':'NO_NEW_PAID_CALLS','device':'STOPPED','executorDispatch':False})
def sheet(items,name,cols=4,tw=360,th=250):
 canvas=Image.new('RGB',(cols*tw,math.ceil(len(items)/cols)*th),(32,33,38));dr=ImageDraw.Draw(canvas)
 for i,(label,p) in enumerate(items):
  x,y=i%cols*tw,i//cols*th;dr.text((x+5,y+4),label[:48],fill='white')
  with Image.open(p) as im:im=im.convert('RGB');im.thumbnail((tw-10,th-30));canvas.paste(im,(x+(tw-im.width)//2,y+28))
 canvas.save(Q/name)
sheet([(p.stem,p) for p in sorted((Q/'pixels').glob('*.png')) if 'army-age' not in p.stem],'current-runtime-overview.jpg')
sheet([(r['id'],R/r['path']) for r in vp['rows'] if r['viewport']==[1280,720]],'eight-age-runtime-overview.jpg')
parts=[]
for r in visual:
 ref=R/r['referencePath'];res=R/r['actualPath'] if r['actualPath'] else None
 parts.append(f'<article><h2>{r["id"]} {html.escape(ref.stem)}</h2><p>{html.escape(r["reason"])}</p><div class="pair"><figure><img loading="lazy" src="../../{r["referencePath"]}"><figcaption>Approved appearance reference</figcaption></figure>'+(f'<figure><img loading="lazy" src="{res.relative_to(Q).as_posix()}"><figcaption>{r["stateKind"]}</figcaption></figure>' if res else '<p>Dedicated fresh result missing; UNVERIFIED</p>')+'</div></article>')
extra=[]
for p in sorted(Q.glob('*.jpg')):extra.append(f'<article><h2>{p.name}</h2><a href="{p.name}"><img loading="lazy" src="{p.name}"></a></article>')
(Q/'gallery.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>Post-Code independent audit 7 October2026</title><style>body{background:#171a20;color:#eee;font:16px system-ui;margin:24px}article{padding:16px;border:1px solid #756440;margin:25px 0}img{display:block;width:100%;height:auto}a{color:#e3c679}.pair{display:grid;grid-template-columns:1fr 1fr;gap:12px}figure{margin:0}figcaption{padding:8px}article>img{max-width:1600px}@media(max-width:800px){.pair{grid-template-columns:1fr}}</style><h1>Code delivery and next two Image AIs — INCOMPLETE</h1><p>JavaScript ES modules/HTML/CSS/SVG; Node24.19.0; Python3.12.14.105/107testsPASS; exact2guideENOENT. Current3Codecrops verified;32Army+32Kingdom fixtures; ordinarymodalfocusPASS/programmaticnavgap. StaticAPK333closurePASS/zero permissions; deviceSTOPPED/ownerUNVERIFIED. Thumbnail overview is not fineedgeacceptance. Sparse agefixtures are not earned/developed towns. Allimages retainaspect.</p><p><a href="../../docs/plan/CODE-DELIVERY-AND-NEXT-TWO-IMAGE-AUDIT-2026-10-07.md">Audit</a> · <a href="../../docs/plan/ENVIRONMENT-IMAGE-AI-AFTER-CODE-EXECUTION-2026-10-07.txt">Environment prompt</a> · <a href="../../docs/plan/ACTORS-EQUIPMENT-IMAGE-AI-AFTER-CODE-EXECUTION-2026-10-07.txt">Actors prompt</a> · <a href="per-id-status.json">361per-IDdecisions</a> · <a href="requirements-status.json">37requirements</a> · <a href="two-image-ownership.json">Ownership/Code dependencies</a></p>'+''.join(parts+extra),encoding='utf-8')
docs=['AGENTS.md','START-HERE.md','CURRENT-STATUS.md','DECISIONS.md','docs/SESSION-HANDOFF.md','docs/BUILD-PROGRESS.md','docs/plan/README.md']+['docs/plan/'+n for n in ['INSTALLED-ENVIRONMENT.md','AUDIT-UPDATE.md','MASTER-PLAN.md','REQUIREMENTS-TRACEABILITY.md','VISUAL-DESIGN.md','MOCK-FIDELITY-AUDIT.md','ART-REUSE.md','asset-manifest.json','reviewed-art-ledger.json','raw-inventory.json','public-art-inventory.json','GAME-DATA-REFERENCE.json','INSTALLATION-TRANSFER.md','REVIEW-AND-STATUS.md','NEXT-AI-PROMPT.md','FULL-IMPLEMENTATION-SPEC.md','DATA-ADOPTION-LEDGER.json','SOURCE-EQUATIONS-ADDENDUM-2026-10-03.md','WHOLE-PLAN-INDEPENDENT-AUDIT-2026-10-04.md']]
index=[]
for rel in docs:
 p=R/rel
 if p.exists():
  text=p.read_text(encoding='utf-8-sig');index.append({'path':rel,'sha256':sha(p),'bytes':p.stat().st_size,'headings':re.findall(r'^#{1,4} .+$',text,re.M),'scopeClauses':[line for line in text.splitlines() if re.search(r'17.*pad|7.*10|9.*15|16.*10|six.*slot|eight.*age|four.*qual|permission|48.*px',line,re.I)][:30]})
 else:index.append({'path':rel,'missing':True})
save('reading-index.json',index)
for rel in ['index.html','package.json','.git/index','.git/HEAD','android/app/build.gradle','android/app/src/main/AndroidManifest.xml']:
 p=R/rel
 if p.exists():snapshot[rel]={'sha256':sha(p),'bytes':p.stat().st_size}
save('input-hashes.json',snapshot)
save('summary.json',{'status':'INCOMPLETE','tests':{'total':107,'passed':105,'failed':2,'scope':'exactguideENOENT'},'producerRows':312,'perIdRows':len(rows),'requirements':len(requirements),'consumerCounts':consumer['runtimeCounts'],'consumerFileErrors':[c['id'] for c in consumer['checks'] if any(not f['exists'] or not f['hashMatch'] or f.get('dimensionMatch') is False for f in c['files'])],'codeRepairs':consumer['repairs'],'browserCaptures':22,'viewportCaptures':64,'visibleAlphaChecks':len(sizes),'visibleAlphaPass':all(x['pass'] for x in sizes),'minArmyCaptionCss':min(t['cssFont'] for t in fonts if t['id'].startswith('army-')),'package':'333assetsstaticPASS/noinstalleddevice','noProductOrProductionEdits':True,'noExecutorDispatched':True})
print(json.dumps({'perId':len(rows),'requirements':len(requirements),'alphaChecks':len(sizes),'alphaFailures':[x for x in sizes if not x['pass']],'minArmyFont':min(t['cssFont'] for t in fonts if t['id'].startswith('army-')),'protectedFiles':len(snapshot),'readingMissing':[x for x in index if x.get('missing')]},indent=2))
