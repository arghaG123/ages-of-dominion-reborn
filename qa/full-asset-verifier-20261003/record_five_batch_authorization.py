"""Planner metadata/pointers only; no provider, production script or ledger changes."""
from pathlib import Path
import json,hashlib
from decimal import Decimal
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
usage=[]
for p in sorted((ROOT/'assets/production').glob('*/collection-report.json')):
    d=json.loads(p.read_text(encoding='utf-8-sig'));u=d['usage']
    usage.append({'batch':p.parent.name,'collectionReportSHA256':sha(p),'records':len(u),'input':sum(x.get('promptTokenCount',0) for x in u),'output':sum(x.get('candidatesTokenCount',0) for x in u),'thoughtsReported':sum(x.get('thoughtsTokenCount',0) for x in u),'total':sum(x.get('totalTokenCount',0) for x in u)})
totals={k:sum(x[k] for x in usage) for k in ['records','input','output','thoughtsReported','total']}
model=Decimal(totals['input'])*Decimal('.5')/Decimal(1000000)+Decimal(totals['output'])*60/Decimal(1000000)
assert model==Decimal('16.4939815')
records=[]
for rel,base in [('CURRENT-STATUS.md','docs/plan/'),('START-HERE.md','docs/plan/'),('RESUME-HERE.md','docs/plan/'),('DECISIONS.md','docs/plan/'),('docs/PLANNER-VERIFIER-HANDOFF.md','plan/'),('docs/SESSION-HANDOFF.md','plan/'),('docs/BUILD-PROGRESS.md','plan/'),('docs/plan/README.md',''),('docs/plan/FULL-IMPLEMENTATION-SPEC.md',''),('docs/plan/FULL-ASSET-PURCHASE-PLAN.md',''),('docs/plan/ALL-BATCHES-ASSET-AUDIT-2026-10-03.md','')]:
    prefix=(f'> **LATEST OWNER AUTHORIZATION — NEXT FIVE BATCHES, 3 October 2026:** The owner explicitly says "We need to submit next 5 batches." The batch executor is authorized to prepare/submit/monitor/collect production09–13, exactly30 useful requests each/150 maximum; old draft-only/no09+ permission blockers below are superseded for those five. No repeated per-batch approval is required. Read [the new execution prompt]({base}BATCHES-09-13-EXECUTION-PROMPT-2026-10-03.txt) and [authorization/budget reconciliation]({base}FIVE-BATCH-AUTHORIZATION-2026-10-03.md). One active/unknown in the supplied project, next prepared authorized submission before prior collection, stop-on-quota, target60/hard80 and reserve15 persist. Current unreconciled65 + five6USD holds =95USD, so evidence-backed cost reconciliation/accounting repair is required; affordability for09 alone does not cover all five. Preserve original reservation history and unknown bills; this authorization does not waive budget/access/readiness blockers. This chat remains planner/verifier only, with no submission, collection, provider query or delegation. Recovery/game ownership is unchanged;14+ is outside this authorization. Prior text below is retained as history.\r\n\r\n').encode('utf-8')
    p=ROOT/rel;old=p.read_bytes();p.write_bytes(prefix+old)
    records.append({'file':rel,'priorSHA256':hashlib.sha256(old).hexdigest(),'prefixBytes':len(prefix),'priorBytesPreserved':p.read_bytes()[len(prefix):]==old})
p=ROOT/'docs/plan/BATCH-GENERATION-AI-NEXT-PROMPT-2026-10-03.txt';old=p.read_bytes()
head=b'CURRENT OWNER AUTHORIZATION: Submit the next FIVE batches09-13, exactly30 useful requests each, within existing project/single-active/budget rules. Use docs/plan/BATCHES-09-13-EXECUTION-PROMPT-2026-10-03.txt as the current executable handoff. Historical absence-of-authorization/draft-only clauses below are superseded for09-13. Original text preserved; all other applicable safeguards persist.\r\n\r\n'
p.write_bytes(head+old);records.append({'file':p.relative_to(ROOT).as_posix(),'priorSHA256':hashlib.sha256(old).hexdigest(),'prefixBytes':len(head),'priorBytesPreserved':p.read_bytes()[len(head):]==old})
value={'ownerQuote':'We need to submit next 5 batches.','scope':'09-13; 5 batches x 30 useful positions; 150 maximum','plannerOnly':True,'providerCalled':False,'productionLedgerChanged':False,'actualInvoice':None,'source':'local collection metadata, not newly re-audited raw/provider usage','usage':usage,'totals':totals,'illustrativeStandardModelTokenUSD':str(model),'excludes':'other jobs, unreported usage, storage/operations/tax; not a final bill or automatic hold release','priorDocumentPreservation':records}
(OUT/'five-batch-authorization-checks.json').write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'records':totals['records'],'modelOnlyUpperIllustrationUSD':str(model),'planningFilesUpdated':len(records),'allPriorBytesPreserved':all(x['priorBytesPreserved'] for x in records)}))
