"""Publish the owner-required documentation contract; no production operations."""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[2]; OUT=Path(__file__).resolve().parent
PLAN=ROOT/'docs/plan'; OLD=ROOT/'qa/plan-semantic-audit-20261016'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,v):(OUT/n).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
if not (OUT/'previous-document-identities.json').exists():
    previous=json.loads((OLD/'verification.json').read_text(encoding='utf-8'))
    write('previous-document-identities.json',previous['artifacts'])

paths=['AGENTS.md','START-HERE.md','CURRENT-STATUS.md','DECISIONS.md','docs/SESSION-HANDOFF.md','docs/BUILD-PROGRESS.md','docs/plan/README.md','docs/plan/COMPLETE-GAME-DESIGN-AND-INTERACTION-EXECUTOR-PLAN-2026-10-12.md']
for name in paths:
    p=ROOT/name; body=p.read_text(encoding='utf-8')
    if body.startswith('> **Authoritative execution contract'):
        body=body.split('\n\n',1)[1]
    prefix='docs/plan/' if p.parent==ROOT else 'plan/' if p.parent==ROOT/'docs' else ''
    banner=('> **Authoritative execution contract - owner clarification, 16 October 2026:** The owner uses the plan as the complete source of truth for the other implementation AI. Read the [binding manual sections 0 and 10]('+prefix+'MOCK-LED-IMPLEMENTATION-SOLUTIONS-MANUAL-2026-10-16.md) and give that AI [ONE authoritative complete executor file]('+prefix+'ONE-COMPLETE-EXECUTOR-CONTINUATION-2026-10-16.txt). All 18 owner-concern groups have mandatory outcomes, repair routes and evidence obligations; all original requirements, 30 mocks, 18 journeys, 16 G contracts and 96 steps remain required. Resolve/implement/verify/repair until every required current assertion passes; a checkpoint, blocked row or test count is not completion. The earlier semantic audit describes corrected prior wording. Planner remains documentation/verifier only; no production/provider/build/device/Git/cleanup/dispatch. Budget and later review sequence remain unchanged. **The specification is authoritative; implementation acceptance remains INCOMPLETE.**\n\n')
    p.write_text(banner+body,encoding='utf-8')

report=PLAN/'INDEPENDENT-PLAN-SEMANTIC-AUDIT-2026-10-16.md'
body=report.read_text(encoding='utf-8')
if not body.startswith('> **Current owner clarification'):
    report.write_text('> **Current owner clarification - 16 October 2026:** The findings below describe the preceding plan wording and its corrections. The owner requires the plan to be the complete execution source of truth. [Manual sections 0 and 10](MOCK-LED-IMPLEMENTATION-SOLUTIONS-MANUAL-2026-10-16.md) now bind every concern to implementation, repair and current evidence, including deterministic fit/storage decisions and final completion rules. Use [ONE authoritative executor file](ONE-COMPLETE-EXECUTOR-CONTINUATION-2026-10-16.txt). This adds documentation requirements, not an implementation PASS or budget expansion.\n\n'+body,encoding='utf-8')

handoff=PLAN/'ONE-COMPLETE-EXECUTOR-CONTINUATION-2026-10-16.txt'
tail=handoff.read_bytes().split('===== FULL G01–G16 PRODUCT CONTRACT ====='.encode(),1)[1]
header='''ONE AUTHORITATIVE COMPLETE EXECUTOR FILE - 16 OCTOBER 2026

The owner uses this file as the complete source of truth for the other implementation AI. Work in C:/dev/ages-of-dominion-reborn. Implement and resolve every required owner concern and deliver the finished required game and exact candidate package. The planner remains documentation/verifier only; do not ask it to execute or dispatch implementation.

Read the embedded manual sections 0 and 10 first for binding scope, precedence, definite repair decisions and completion rules. Then execute its detailed recipes, sections 9 and 1-8, the complete G01-G16 contracts and the preserved original 96 steps. The earlier plan-audit wording describes defects that were corrected, not optional outcomes or permission to deliver partial work. Inherited section references are resolved in A01. Semantic audit revision: A01-A08 remain binding under the latest sections 0 and 10.

Advanced landscape mocks define the finished look; adopted source-backed rules define mechanics; current owner decisions control conflicts. Game appearance comes first. Preserve dirty work, old/raw read-only sources and required evidence. Another theme, dashboard, plot grid, box-wall stroke, malformed Healer, static plate gait, injected natural journey, untested save backend or passing test count is not the required result.

Current financial authority remains prior $80 plus at most $20 additional solely for identified style/Healer fixes, absolute exposure ceiling $100, released $15 counted once. Reconcile all liabilities/UNKNOWN and preserve one active/inflight UNKNOWN, owned mutex/CAS/write-ahead/reservations/receipts, success-completion plus >=20 seconds, and definite 429 >=60 seconds or longer Retry-After. No repeat permission for affordable prepared authorized repairs; no filler, blind replay or unrelated use of the extra allowance.

Complete -> verify actual consumers -> repair every failed required leaf -> recheck current evidence -> build and deliver exact final candidate -> independent desktop verification -> later authorized device and owner sequence. Continue independent ready work through scoped blockers. A genuine external limit requires an exact INCOMPLETE exception, never false completion or budget expansion. Do not self-award independent/device/owner acceptance.

===== DETAILED MOCK-LED SOLUTIONS MANUAL =====

'''
handoff.write_bytes(header.encode('utf-8')+(PLAN/'MOCK-LED-IMPLEMENTATION-SOLUTIONS-MANUAL-2026-10-16.md').read_bytes()+'\n\n===== FULL G01–G16 PRODUCT CONTRACT ====='.encode()+tail)

specs=[
('OC01','Finished game appearance',['OWN-05','OWN-06','OWN-15'],['G01','G08','G10','G15']),
('OC02','Natural sparse Stone start',['OWN-07','SYS-01'],['G02','G03']),
('OC03','Physical walls',['OWN-07','SYS-01'],['G03']),
('OC04','Physical scene registration',['OWN-09','OWN-13','OWN-14'],['G01','G04','G05','G06']),
('OC05','Coherent realistic style',['OWN-03','OWN-06','OWN-14'],['G01','G08','G10']),
('OC06','Complete usable Healer',['OWN-11'],['G08']),
('OC07','All class and era kits',['OWN-08','OWN-11','OWN-14'],['G01','G08']),
('OC08','Six functional worn slots',['SYS-03','SYS-04'],['G10']),
('OC09','Real role and mount motion',['OWN-10','OWN-12','OWN-13'],['G04','G05','G06','G08','G11']),
('OC10','Adventure world and transitions',['OWN-09','SYS-06'],['G04']),
('OC11','Complete Tactical control',['OWN-13','SYS-07'],['G05','G09']),
('OC12','Defense and five War modes',['OWN-12','SYS-08','SYS-16'],['G06','G07']),
('OC13','Economy and progression',['OWN-08','OWN-15','SYS-01','SYS-02','SYS-05'],['G02','G03','G08','G11']),
('OC14','Supporting experiences',['OWN-17','SYS-04','SYS-05','SYS-10'],['G08','G09','G10','G11','G13','G15']),
('OC15','Story objectives tutorial',['SYS-09','SYS-11'],['G12','G14']),
('OC16','Durable saves and recovery',['SYS-12','SYS-13'],['G15','G16']),
('OC17','Mobile accessibility offline native',['OWN-19','SYS-14','SYS-15'],['G15']),
('OC18','Whole final connected delivery',['OWN-01','OWN-02','OWN-04','OWN-16','OWN-17','OWN-18','SYS-13'],['G15','G16'])]
manual=(PLAN/'MOCK-LED-IMPLEMENTATION-SOLUTIONS-MANUAL-2026-10-16.md').read_text(encoding='utf-8')
rows=[]
for ident,title,req,g in specs:
    contract=next(x for x in manual.splitlines() if x.startswith('| '+ident+' '))
    cells=[x.strip() for x in contract.split('|')[1:-1]]
    rows.append({'id':ident,'concern':title,'originalRequirements':req,'G':g,'requiredOutcome':cells[1],'repairRoute':cells[2],'manualLine':manual[:manual.index(contract)].count('\n')+1,'implementationAcceptance':'NOT_TESTED_BY_PLANNER'})
write('owner-concern-index.json',rows)
print(json.dumps({'concerns':len(rows),'originalRequirementsMapped':len({i for x in rows for i in x['originalRequirements']}),'Gmapped':len({i for x in rows for i in x['G']})}))
