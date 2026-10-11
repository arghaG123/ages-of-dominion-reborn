from audit import *
import importlib.util,ast,tempfile,uuid
spec=importlib.util.spec_from_file_location('transfer',ROOT/'docs/migration/device-handoff-20261009/transfer.py');tr=importlib.util.module_from_spec(spec);spec.loader.exec_module(tr)
prompt=ROOT/'docs/plan/NEXT-DEVICE-COMPLETE-CONTINUATION-PROMPT-2026-10-09.txt';t=prompt.read_text(encoding='utf-8');sections=re.findall(r'^[1-7]\. (?:Task Summary|Environment|Inputs & Outputs|Step-by-Step Instructions|Edge Cases & Failure Modes|Acceptance Criteria|Do NOT)$',t,re.M);steps=[int(n) for n in re.findall(r'^(\d+)\. ',t.split('4. Step-by-Step Instructions')[1].split('5. Edge Cases & Failure Modes')[0],re.M)]
assert len(sections)==7 and steps==list(range(1,62))
links=[]
for n in ['docs/plan/PROJECT-DEVICE-HANDOFF-AUDIT-2026-10-09.md','docs/migration/device-handoff-20261009/README.md']:
    p=ROOT/n
    for target_name in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
        if '://' not in target_name:links.append({'source':n,'target':target_name,'exists':(p.parent/target_name).exists()})
assert all(v['exists'] for v in links)
manifest=json.loads(tr.MANIFEST.read_text(encoding='utf-8'));files=manifest['files']
assert len(files)==5670
assert len({r['path'] for r in files})==len(files)
assert all(not tr.forbidden(r['path']) for r in files)
# Verify extraction and unlike-file rejection in a small, separate scratch root.
scratch=OUT/'restore-safety-fixture'/uuid.uuid4().hex;scratch.mkdir(parents=True,exist_ok=True);(scratch/'payloads').mkdir(exist_ok=True)
blob=b'portable fixture, no project data';zp=scratch/'payloads/check.zip'
with zipfile.ZipFile(zp,'w') as z:z.writestr('assets/check.txt',blob)
fixture={'payloads':[{'name':zp.name,'bytes':zp.stat().st_size,'sha256':sha(zp)}],'files':[{'path':'assets/check.txt','bytes':len(blob),'sha256':hashlib.sha256(blob).hexdigest(),'archive':zp.name}]}
fp=scratch/'manifest.json';fp.write_text(json.dumps(fixture));oldroot,oldmanifest=tr.ROOT,tr.MANIFEST;tr.ROOT=scratch/'checkout';tr.ROOT.mkdir(exist_ok=True);tr.MANIFEST=fp
tr.restore(scratch/'payloads',False);tr.restore(scratch/'payloads',True)
try:tr.target('../escape');raise AssertionError('Traversal accepted')
except ValueError:pass
try:tr.target('C:/escape');raise AssertionError('Absolute path accepted')
except ValueError:pass
(tr.ROOT/'assets/check.txt').write_bytes(b'unlike-existing')
try:tr.restore(scratch/'payloads',False);raise AssertionError('Unlike destination accepted')
except SystemExit as e:assert e.code==1
assert (tr.ROOT/'assets/check.txt').read_bytes()==b'unlike-existing'
tr.ROOT,tr.MANIFEST=oldroot,oldmanifest
security=[];parse_errors=[];credential_matches=[]
candidate_paths=[p for base in ['docs/migration/device-handoff-20261009','docs/storage-cleanup/preview-retirement-20261009','qa/image-unified-reserve-20261009','qa/planner-device-handoff-20261009'] for p in (ROOT/base).rglob('*') if p.is_file() and not any(s in p.parts for s in ['__pycache__','static-package','restore-safety-fixture']) and p.suffix in ['.py','.json','.mjs','.md','.txt','.html']]
candidate_paths += [ROOT/'docs/plan/IMAGE-UNIFIED-RESERVE-INTERFACE-2026-10-09.json',ROOT/'docs/plan/PROJECT-DEVICE-HANDOFF-AUDIT-2026-10-09.md',prompt,ROOT/'docs/plan/image-production/budget-ledger.json',ROOT/'docs/plan/image-production/submission.mutex.json']
asset_json=[p for p in (ROOT/'assets').rglob('*') if p.is_file() and p.suffix in ['.json','.jsonl']]
for p in [*candidate_paths,*asset_json]:
    n=p.relative_to(ROOT).as_posix();security.append(n)
    try:
        if p.suffix in ['.json','.jsonl']:tr.scan_json(p.read_bytes(),n)
        else:
            b=p.read_bytes()
            if any(re.search(pattern,b) for pattern in [rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',rb'ya29\.[A-Za-z0-9_-]{20,}',rb'gh[pousr]_[A-Za-z0-9]{30,}',rb'github_pat_[A-Za-z0-9_]{30,}',rb'AIza[0-9A-Za-z_-]{35}']):credential_matches.append(n)
        if p.suffix=='.py':ast.parse(p.read_text(encoding='utf-8-sig'))
    except ValueError as e:parse_errors.append({'path':n,'errorType':type(e).__name__})
assert not credential_matches and not parse_errors,(credential_matches,parse_errors)
before=read('qa/planner-device-handoff-20261009/protected-before.json');changes=[];missing=[]
for n,v in before.items():
    p=ROOT/n
    if not p.exists():missing.append(n)
    elif sha(p)!=v['sha256']:changes.append(n)
allowed={'docs/SESSION-HANDOFF.md','docs/BUILD-PROGRESS.md','docs/plan/README.md','docs/PLANNER-VERIFIER-HANDOFF.md'}
assert not missing and set(changes)<=allowed,(missing,changes)
raw=read('qa/planner-device-handoff-20261009/raw-native-checks.json');assert len(raw)==19 and all(len(r['images'])==1 and r['images'][0]['native'] for r in raw)
write('final-verification.json',{'status':'PASS_SCOPED_HANDOFF_CHECKS_PRODUCT_INCOMPLETE','sevenSections':sections,'atomicSteps':len(steps),'links':links,'protectedSnapshotFiles':len(before),'unchangedProtectedFiles':len(before)-len(changes),'changedProtectedFiles':changes,'missingProtectedFiles':missing,'sourceArtControlNoMutationsByAudit':True,'rawNativeAssociations':19,'transferPayloads':manifest['payloads'],'transferEntries':len(files),'localArchiveReadback':'PASS','restoreSafetyFixture':'PASS: extraction/hash, traversal/absolute rejection, unlike overwrite refusal','newDeviceRestore':'UNVERIFIED','missingHistoricalRawFiles':124,'missingGuides':2,'securityPathsChecked':len(security),'credentialPatternMatches':credential_matches,'jsonPythonParseErrors':parse_errors,'noUserSaveCredentialBundlePaths':True,'producerRecordsPreservedWithStaleClaimsReported':True,'cleanup':read('qa/planner-device-handoff-20261009/cleanup-result.json'),'gitPublication':'PENDING_NORMAL_COMMIT_AND_PUSH; see final terminal evidence and published Git revision'})
write('security-check.json',{'pathsChecked':security,'matches':credential_matches,'errors':parse_errors,'limits':'Pattern/structured-field scan; provider thought signatures and inline-image base64 are opaque provenance, not authentication fields; no secret values printed.'})
print('Final checks PASS; protected',len(before)-len(changes),'unchanged; transfer',len(files),'entries; sections',len(sections),flush=True)
