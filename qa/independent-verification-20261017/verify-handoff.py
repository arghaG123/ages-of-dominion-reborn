from pathlib import Path
import json,re,hashlib,subprocess
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(n,x):(OUT/n).write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf8')
missing=[];links=[]
for name in ['INDEPENDENT-EXECUTOR-VERIFICATION-2026-10-17.md','INDEPENDENT-EXECUTOR-COVERAGE-2026-10-17.md']:
    p=ROOT/'docs/plan'/name;text=p.read_text(encoding='utf8')
    for link in re.findall(r'\]\(([^)]+)\)',text):
        if link.startswith(('https:','http:','#')):continue
        target=(p.parent/link.split('#')[0]).resolve();row={'document':name,'link':link,'exists':target.exists()};links.append(row)
        if not target.exists():missing.append(row)
put('document-link-check.json',{'links':len(links),'missing':missing,'rows':links})
before=json.loads((OUT/'executor-evidence-identity.json').read_text(encoding='utf8'))
changed=[p for p,v in before.items() if not (ROOT/p).is_file() or sha(ROOT/p)!=v['sha256']]
put('prior-executor-evidence-preservation.json',{'checkedFiles':len(before),'changedOrMissing':changed})
imports=[];suspects=[];referencePaths=[];linksToOld=[]
for p in (ROOT/'src').rglob('*'):
    if p.is_symlink():linksToOld.append(p.relative_to(ROOT).as_posix())
    if p.is_file() and p.suffix in ['.js','.mjs','.css','.json']:
        text=p.read_text(encoding='utf-8-sig')
        for i,line in enumerate(text.splitlines()):
            if re.search(r'\bimport\b|\bfrom\b',line) and p.suffix in ['.js','.mjs']:
                imports.append({'path':p.relative_to(ROOT).as_posix(),'line':i+1,'text':line})
            if re.search(r'ages-of-dominion[/\\](?:src|core|client)|(?:\.\./)+ages-of-dominion(?:[/\\]|[\x27"])',line):
                occurrence={'path':p.relative_to(ROOT).as_posix(),'line':i+1,'text':line}
                if p.suffix=='.json':referencePaths.append(occurrence)
                else:suspects.append(occurrence)
put('read-only-import-scan.json',{'imports':imports,'oldExecutablePathSuspects':suspects,'oldReferenceDataProvenancePaths':referencePaths,'sourceSymlinks':linksToOld,'limitation':'Text/import path scan only. JSON sourcePath metadata is reference provenance, not an executable import. Does not establish exhaustive authored-code ancestry.'})
verification=json.loads((OUT/'handoff-verification.json').read_text(encoding='utf8'))
protection=json.loads((OUT/'protection-result.json').read_text(encoding='utf8'))
verification.update({'protectedFilesBefore':protection['before'],'protectedFilesAfter':protection['after'],'protectedChanges':len(protection['changes']),'priorExecutorEvidenceFiles':len(before),'priorExecutorEvidenceChanges':changed,'newDocMissingLinks':missing,'currentProductVerdict':'INCOMPLETE','noProductionMutationVerified':len(protection['changes'])==0,'noOldExecutableImportPathDetected':not suspects and not linksToOld})
put('handoff-verification.json',verification)
put('git-after.json',{'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'status':subprocess.check_output(['git','status','--porcelain=v1'],cwd=ROOT,text=True)})
print(json.dumps({k:v for k,v in verification.items() if k not in ['coverageCounts']},indent=2))
assert not missing and not changed and not protection['changes'] and verification['originalEmbeddedByteExact']
