from audit import *
names=['AGENTS.md','START-HERE.md','CURRENT-STATUS.md','DECISIONS.md','docs/SESSION-HANDOFF.md','docs/BUILD-PROGRESS.md','docs/plan/README.md','docs/PLANNER-VERIFIER-HANDOFF.md','RESUME-HERE.md','README.md']
report='docs/plan/PROJECT-DEVICE-HANDOFF-AUDIT-2026-10-09.md';prompt='docs/plan/NEXT-DEVICE-COMPLETE-CONTINUATION-PROMPT-2026-10-09.txt';transfer='docs/migration/device-handoff-20261009/README.md'
history={}
for name in names:
    p=ROOT/name;t=p.read_text(encoding='utf-8-sig')
    if '> **Latest owner device continuation / independent audit' in t[:500]:t=t.split('\n\n',2)[2]
    history[name]={'sha256':sha(p),'bytes':p.stat().st_size,'contentHash':hashlib.sha256(t.encode()).hexdigest()}
    def link(n):return os.path.relpath(ROOT/n,p.parent).replace('\\','/')
    banner=f'''Language/framework/version: JavaScript ES modules, HTML/CSS/SVG; Node24.19.0 and Python3.13.7/image tooling verified9October2026. Task: independent verification/device handoff; product remains INCOMPLETE.

> **Latest owner device continuation / independent audit — 9 October 2026:** Owner requested a new chat FIRST, whole Code/Image verification, one portable continuation prompt, removal of unneeded old QA and commit/push. This prospectively authorizes those precise audit/cleanup/Git actions, superseding earlier planner no-Git/no-cleanup statements for this task. Read [the fresh report]({link(report)}), [the single seven-section continuation prompt]({link(prompt)}) and [copy/restore instructions]({link(transfer)}). Fresh107tests105PASS/2missingexactguides; ordinarymodal/naturalstarter/373APKwebfiles PASSbounded, programmaticRetreatnavigation and9.593pxArmycopy/phonecomposition FAIL. NewunifiedImage work exists:7standingcandidates/123PNGs,3bodystalecontracts/46of55staleplatehashes,32sceneFAIL;24source-missingflags contradicted by presentbiomecatalogsources. Croptranslation197PASS does not prove contacts/rigs/scene acceptance. Reserveoverride recordedONCE/effectivereserve0/priorliability64.8327/capacity15.1673beforelaterliabilities/hard80/invoicesUNKNOWN; no provider call or accounting change by this audit. LocalassetZIP+QAlineage+finalcaptures are hash/readback verified and excluded fromGit; newdevicecopy/restore UNVERIFIED,124historicalrawbackupfiles and2guides stillmissing. OldQAbytecodecleanup removed20684bytes/3files, no tracked deletions; current/referenced art/QA/history/browserstate preserved. Main/ownerremote verified at base73fdfc3ad4568a2f668dbbcc0aa65acf567f8b07; publication is the normal pushed commit containing this report, inspect Git for its SHA. WholegameINCOMPLETE/runtime-ownerUNVERIFIED/deviceSTOPPED. No game/art repair, paid generation, device or executor dispatch performed here. Historical banners below remain evidence, not current completion claims.

'''
    p.write_text(banner+t,encoding='utf-8')
    assert p.read_text(encoding='utf-8').endswith(t)
write('pointer-update.json',{'preservedHistory':history,'files':names,'links':[report,prompt,transfer]})
print('Updated pointers',len(names),'history preserved')
