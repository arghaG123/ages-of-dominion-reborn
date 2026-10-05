from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,subprocess
root=Path(__file__).resolve().parents[2];out=Path(__file__).resolve().parent
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
before=json.loads((out/'snapshot-start.json').read_text())
changed=[r['file'] for r in before['sources'] if sha(root/r['file'])!=r['sha256']]
remote=subprocess.check_output(['git','ls-remote','--heads','origin','main'],cwd=root,text=True).strip()
checks={'at':datetime.now(timezone.utc).isoformat(),'sourceChangedSinceStart':changed,'sourcePreservation':'PASS' if not changed else 'CONCURRENT_CHANGE_REVIEW_REQUIRED','tests':{'command':'node --test tests/*.test.mjs','observedPass':50,'observedFail':0,'runCount':1,'scope':'Observed once in this planner turn; not full product acceptance'},'remoteMainFresh':remote,'buildByPlanner':False,'providerQueryByPlanner':False,'productionMutationByPlanner':False,'deviceTesting':'STOPPED_UNAUTHORIZED','executorMessageOrDelegation':False,'notes':['Initial browser harness import corrected to file URL; later tactical fixture moved to isolated context to avoid pagehide autosave restoring state. Successful final browser run is authoritative.','Desktop file-scheme failure is not Android runtime proof.','QA viewing plates are local evidence, not processed production assets.']}
(out/'checks.json').write_text(json.dumps(checks,indent=2))
for name in ['CURRENT-STATUS.md','START-HERE.md','docs/SESSION-HANDOFF.md','docs/BUILD-PROGRESS.md','docs/PLANNER-VERIFIER-HANDOFF.md','docs/plan/README.md']:
    p=root/name;prefix='' if name.startswith('docs/plan/') else ('plan/' if name.startswith('docs/') else 'docs/plan/')
    text=f'> **Independent code/art verification — 4 October 2026:** Read [the fresh audit]({prefix}CODE-ART-INDEPENDENT-VERIFICATION-2026-10-04.md) and [the complete remaining-work prompt]({prefix}CODE-ART-COMPLETE-REMAINING-WORK-PROMPT-2026-10-04.txt). Fresh50 tests and the earlier5Defense-save probes PASS; sustained Endless fixture PASS. Hall/P03–P05 phone repair verified, but P14/P15 target clipping, valid-backup loss and audio background scheduling FAIL. Existing APK is stale against6current web files; native/device and owner acceptance UNVERIFIED/device STOPPED.510original hashes match;22native-size outputs hash/decode PASS, inspected Defense forest/hills spatial FAIL. Full game/art/support/journeys remain INCOMPLETE; continue all ready scoped executor work. Local/remote main cff5528,67tracked assets, saved restore destination null/0verified rows. Planner wrote QA/docs only; no code/art production/provider/build/device/storage/Git mutation, executor messaging or delegation. Concurrent image records preserved; historical text follows.\n\n'
    current=p.read_text(encoding='utf-8')
    if text not in current:p.write_text(text+current,encoding='utf-8')
storage=root/'docs/plan/GIT-ASSET-STORAGE-PLAN-2026-10-03.md'
addition='> **Concrete preservation refresh — 4 October 2026:** New local [hash/size catalog](../../qa/code-art-verification-20261004/asset-preservation-catalog.json), closing snapshot1186assets files/4,621,872,706bytes, supplies a reviewable scope. Refresh later concurrent additions before copying; also retain unique QA/reference/provenance evidence. Exact external archive and independent durable second destination/access/retention/cost scope remain unresolved in the saved proof; null destination/0verified rows and67tracked assets persist. No copy/upload/ignore/untracking/Git change by planner. Missing destinations block those steps only. Read [the fresh audit](CODE-ART-INDEPENDENT-VERIFICATION-2026-10-04.md). Older sizes/no-commit facts below are history.\n\n'
current=storage.read_text(encoding='utf-8')
if addition not in current:storage.write_text(addition+current,encoding='utf-8')
print(json.dumps(checks))
