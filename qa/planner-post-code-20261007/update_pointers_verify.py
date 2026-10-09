import pathlib,json,hashlib,re,posixpath,html
R=pathlib.Path(__file__).resolve().parents[2];Q=pathlib.Path(__file__).parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(Q/n).write_text(json.dumps(v,indent=2),encoding='utf-8')
audit='docs/plan/CODE-DELIVERY-AND-NEXT-TWO-IMAGE-AUDIT-2026-10-07.md';env='docs/plan/ENVIRONMENT-IMAGE-AI-AFTER-CODE-EXECUTION-2026-10-07.txt';actors='docs/plan/ACTORS-EQUIPMENT-IMAGE-AI-AFTER-CODE-EXECUTION-2026-10-07.txt'
files=['START-HERE.md','CURRENT-STATUS.md','docs/SESSION-HANDOFF.md','docs/BUILD-PROGRESS.md','docs/PLANNER-VERIFIER-HANDOFF.md','docs/plan/README.md','docs/plan/AUDIT-UPDATE.md'];updates=[]
for rel in files:
 p=R/rel;text=p.read_text(encoding='utf-8-sig');base=posixpath.dirname(rel) or '.'
 def link(target):return posixpath.relpath(target,base)
 marker='**Latest AFTER-Code audit and TWO parallel Image prompts — 7 October 2026, INCOMPLETE:**'
 if marker in text:continue
 prefix='Language/framework/version: JavaScript ES modules, HTML/CSS/SVG; independently verified Node24.19.0/Python3.12.14 and systemPython3.13.7 on7October2026. Custom serve/build scripts; static Android preview min24/compile-target36, deviceSTOPPED. Task: Code Review/Testing then Image execution handoff planning.\n\n'
 prefix+='> '+marker+' Code\'s newest whole-build checkpoint explicitly says `localCodeWorkComplete:false`; completion is not established. [Independent audit]('+link(audit)+'), [actual reference/current gallery]('+link('qa/planner-post-code-20261007/gallery.html')+'), [361per-ID outcomes]('+link('qa/planner-post-code-20261007/per-id-status.json')+'), [37requirements]('+link('qa/planner-post-code-20261007/requirements-status.json')+'). Fresh107tests/105PASS/2exactguideENOENT; three subject-preserving Code troop crops and46gear actualbindings; ordinary HTMLinert/modal Cancel-Escape focus/onceconfirm PASS, programmaticnavigation isolation FAIL;64all8age/fourviewport fixtures and192alpha-size checks PASS, Armycaptions9.593CSSpx/clipping FAIL. StaticAPK333assetclosure/CRC/previewID/SDK24-36/zero-permissions PASS; no new build/device. All32scenes remain partial/unpromoted/fullclassgaits incomplete; actual old runtime TownHall magenta differs from cleaner residual candidates. Give owner-selected AIs exactly [Environment whole-local execution]('+link(env)+') and [Actors/Equipment whole-local execution]('+link(actors)+'). NEW exclusive sibling namespaces/interfaces; separate queues/helpers/outputs; no shared runtime/pointer writes. After both deliveries, owner instructs Code to finish listed runtime integration, allscreen/layout/mechanics/naturaljourney and package dependencies. NO_NEW_PAID_CALLS/deviceSTOPPED/geometryfrozen/historypreserved. Planner QA/docs only; no product/image/provider/lock/budget/device/build/Git/storage mutation, executor message or agents. Earlier same-date banners describe historical stages.\n\n'
 before=sha(p);p.write_text(prefix+text,encoding='utf-8');updates.append({'path':rel,'beforeSHA256':before,'afterSHA256':sha(p),'historicalTextPreservedAsSuffix':p.read_text(encoding='utf-8').endswith(text)})
if updates or not (Q/'pointer-update.json').exists():save('pointer-update.json',updates)
else:updates=json.loads((Q/'pointer-update.json').read_text(encoding='utf-8'))
snapshot=json.loads((Q/'input-hashes.json').read_text(encoding='utf-8'));changed=[]
for rel,v in snapshot.items():
 p=R/rel
 if not p.is_file() or sha(p)!=v['sha256']:changed.append({'path':rel,'exists':p.is_file(),'expected':v['sha256'],'actual':sha(p) if p.is_file() else None})
sections=['Task Summary','Environment','Inputs & Outputs','Step-by-Step Instructions','Edge Cases & Failure Modes','Acceptance Criteria','Do NOT'];prompts=[]
for rel in [env,actors]:
 p=R/rel;text=p.read_text(encoding='utf-8');heads=re.findall(r'^([1-7])\. ('+'|'.join(re.escape(s) for s in sections)+r')$',text,re.M);body=text.split('4. Step-by-Step Instructions\n',1)[1].split('5. Edge Cases & Failure Modes\n',1)[0];steps=re.findall(r'^(\d+)\. (.+)$',body,re.M)
 prompts.append({'path':rel,'sha256':sha(p),'sevenSectionsPass':heads==[(str(i),s) for i,s in enumerate(sections,1)],'steps':len(steps),'sequentialAtomicNumbering':list(map(lambda x:int(x[0]),steps))==list(range(1,len(steps)+1)),'firstLineLanguageVersion':text.startswith('Language/framework/version:')})
links=[]
for rel in [audit,'qa/planner-post-code-20261007/gallery.html',*files]:
 p=R/rel;text=p.read_text(encoding='utf-8');targets=re.findall(r'(?:href|src)="([^"]+)"',text) if p.suffix=='.html' else re.findall(r'\]\(([^)]+)\)',text.split('Earlier same-date banners describe historical stages.')[0])
 for target in targets:
  if re.match(r'^[a-z]+://',target) or target.startswith('#'):continue
  f=p.parent/target.split('#')[0];links.append({'from':rel,'target':target,'exists':f.exists()})
report={'protectedInputFiles':len(snapshot),'protectedInputsUnchanged':not changed,'changes':changed,'prompts':prompts,'exactlyTwoNewImagePrompts':len(prompts)==2,'newCodeExecutionPrompt':False,'pointerHistoryPreserved':all(x['historicalTextPreservedAsSuffix'] for x in updates),'galleryAndLatestLinksPass':all(x['exists'] for x in links),'brokenLinks':[x for x in links if not x['exists']],'executorDispatched':False,'productionMutation':False,'gitIndexHeadSnapshotsPreserved':not any(x['path'].startswith('.git/') for x in changed)}
save('final-verification.json',report);print(json.dumps(report,indent=2))
