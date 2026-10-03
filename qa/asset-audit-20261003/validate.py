"""Focused verification of audit records and original preservation. No runtime or network actions."""
from collections import Counter
from pathlib import Path
from datetime import datetime, timezone
import json, re
from inspect import ROOT, OUT, read, sha

review=read(ROOT/'docs/plan/image-production/VERIFIER-REVIEW-20261003.json')
snapshot=read(OUT/'local-snapshot.json'); assoc=read(OUT/'association-check.json');rows=review['assets']
checks=[]
def check(name,condition,details=''):
    checks.append({'name':name,'status':'PASS' if condition else 'FAIL','details':details})
check('90-unique-batch-hash-bindings',len(rows)==90 and len({r['key'] for r in rows})==90)
check('85-original-identities-5-repeat-attempts',len({r['id'] for r in rows})==85)
check('classifications-reconcile',Counter(r['classification'] for r in rows)==Counter({'RECOVERABLE':82,'FAIL':8}))
check('source-assessment-counts-reconcile',Counter(r['sourceContentStatus'] for r in rows)==Counter({'PASS':53,'FAIL':37}))
check('runtime-owner-gates-not-promoted',all(r['runtimeApproved'] is False and r['ownerAcceptance']=='UNVERIFIED' and r['compositeStatus']=='UNVERIFIED' for r in rows))
check('all-90-raw-response-associations',len(assoc['associations'])==90 and assoc['all90PromptAndRawMatches'])
check('every-source-hash-still-exact',all(sha(ROOT/r['sourceFile'])==r['sourceSHA256'] for r in rows))
changed=[v['path'] for v in snapshot['protectedMetadata'] if sha(ROOT/v['path'])!=v['sha256']]
check('preexisting-production-records-budget-source-unchanged',not changed,str(changed))
check('required-alpha-count',sum(r['requiredAlpha'] for r in rows)==56)
check('evidence-files-exist',all((ROOT/r['evidence']['contactSheet']).exists() and (ROOT/r['evidence']['original']).exists() for r in rows))
check('recovery-candidates-have-specific-recipes',all(r['recoveryRecipes'] and all(k in review['recipes'] for k in r['recoveryRecipes']) for r in rows if r['classification']=='RECOVERABLE'))
check('rejected-complete-roles-not-in-recovery-queue',all(not r['recoveryRecipes'] for r in rows if r['classification']=='FAIL'))
check('14-detail-originals-rest-overview-scope',sum(r['evidence']['reviewLevel']=='FULL_ORIGINAL_PLUS_CONTACT_SHEET' for r in rows)==14)
for batch in snapshot['batches'][:3]:
    b=read(ROOT/'assets/production'/batch['batch']/'verifier-review-20261003.json')
    check(batch['batch']+'-ledger-reconciles',len(b['assets'])==30 and b['assets']==[r for r in rows if r['batch']==batch['batch']])
registry=read(ROOT/'docs/plan/image-production/RECOVERY-SOURCE-REGISTRY-20261003.json')
keymap={r['key']:r for r in rows}
check('85-source-candidates-resolve-to-reviewed-hashes',len(registry['sources'])==85 and all(x['preferredReviewCandidateKey'] in keymap and x['sourceSHA256']==keymap[x['preferredReviewCandidateKey']]['sourceSHA256'] for x in registry['sources']))
check('alternative-candidates-leave-original-gaps',sum(x['alternativeOnly'] for x in registry['sources'])==2 and all(x['runtimeApproved'] is False for x in registry['sources']))
report=ROOT/'docs/plan/GENERATED-ASSET-RECOVERY-REVIEW-2026-10-03.md'
missing=[]
for link in re.findall(r'\]\(([^)]+)\)',report.read_text(encoding='utf-8')):
    if '://' not in link and not (report.parent/link).resolve().exists():missing.append(link)
check('human-report-local-links-resolve',not missing,str(missing))
lock=ROOT/'docs/plan/image-production/active-batch.lock.json'
check('fourth-job-has-no-new-local-collection',not (ROOT/'assets/production/production-04-20261003/collection-report.json').exists())
result={'checkedAt':datetime.now(timezone.utc).isoformat(),'status':'PASS' if all(c['status']=='PASS' for c in checks) else 'FAIL','checks':checks,'notRun':['game tests','game builds','provider actions','production image processing','browser/device runtime acceptance'],'activeLockSHA256':sha(lock),'note':'Technical integrity of the review artifacts only; visual findings are separately authored by the verifier.'}
(OUT/'validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':result['status'],'checks':len(checks),'failures':[c for c in checks if c['status']=='FAIL'],'batchClassifications':{b['batch']:dict(Counter(r['classification'] for r in rows if r['batch']==b['batch'])) for b in snapshot['batches'][:3]}}))
assert result['status']=='PASS'
