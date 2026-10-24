from pathlib import Path
import os,json,hashlib,datetime
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent;PLAN=ROOT/'docs/plan'
prompt=PLAN/'ONE-COMPLETE-REPAIR-AFTER-VERIFICATION-2026-10-17.txt'
owner=PLAN/'OWNER-MOBILE-GAME-UI-KINGDOM-AND-RELEASE-GATES-2026-10-17.md'
original=PLAN/'ONE-COMPLETE-EXECUTOR-CONTINUATION-2026-10-16.txt'
delimiter=b'===== BEGIN UNMODIFIED ORIGINAL AUTHORITATIVE COMPLETE EXECUTOR FILE =====\n'
old=prompt.read_bytes();before_original=old.split(delimiter,1)[0]
retained_marker=b'===== RETAINED 17 OCTOBER INDEPENDENT REPAIR PREFACE =====\n'
if retained_marker in before_original:before_original=before_original.split(retained_marker,1)[1]
header='''ONE CURRENT COMPLETE EXECUTOR REPAIR HANDOFF — REVISED 17 OCTOBER 2026

You are the implementation AI. Finish Ages of Dominion Reborn in C:/dev/ages-of-dominion-reborn, including all required game/art/interaction/runtime/evidence and final package work. This is the ONE current handoff. A report, checkpoint, catalog, test count, repainted button or partially improved scene is not the finished game.

READING AND PRECEDENCE
1. Read and implement the latest owner contract U01–U16 embedded immediately below. It makes mobile game UI, icon-plus-amount resources, sharp registered Kingdom terrain/wall families, logical building/wall states and desktop→final-package→mobile review gates concrete. These latest directions override conflicting label-heavy layouts and the older APK-before-independent-desktop-content-review sequence. They add no interim owner-preview permission gate, engine migration, mechanics change or budget increase.
2. Read and implement the retained independent 17 October repair preface below it. Its fresh findings and bounded checks remain dated evidence; complete every still-required storage, class/kit/worn gear, motion, scene, mechanics, natural journey, layout and package repair.
3. Read the entire ORIGINAL authoritative complete executor file embedded byte-for-byte after the final delimiter, sections 0 and 10 first, then all R01–R10, M01–M30, J01–J18, A01–A08, G01–G16 and the original 96 steps. Preserve all original 35 requirements, 32 scenes, 32 class/kit rows, 192 slot decisions and every mechanics/role/viewport obligation. The latest owner directions control any inherited work-sequence or presentation conflict; they do not delete any required outcome.

The owner contract is also at docs/plan/OWNER-MOBILE-GAME-UI-KINGDOM-AND-RELEASE-GATES-2026-10-17.md. The prompt recheck is at docs/plan/REPAIR-PROMPT-ARCHITECTURE-AND-QA-REVIEW-2026-10-17.md. Actual implementation findings/coverage remain in INDEPENDENT-EXECUTOR-VERIFICATION-2026-10-17.md and INDEPENDENT-EXECUTOR-COVERAGE-2026-10-17.md, with source/QA paths inside them. This file supersedes all older remaining-work/four-live-failures repair entrypoints; give the implementation AI this file, not a selection of competing partial prompts.

The other AI implements and fixes. This planner acts as architect/verifier/advisor/senior QA, with docs/QA/isolated verification authority only. Do not ask it to execute production/generation/build/device/Git/cleanup/dispatch work. Preserve dirty/concurrent work, owner saves, originals/native/raw/QA/history/packages and read-only reference roots. Retain all provider/purpose/UNKNOWN/mutex/reservation/receipt/pacing controls and the absolute $100 ceiling; released $15 counts once and extra $20 remains targeted. No new spend occurs in this planner review.

Complete the actual game and its desktop assertions; obtain independent review of the completed browser/source candidate and fix returned defects; then build/verify the final exact APK from that snapshot; only then follow the already authorized later mobile QA/repair and owner sequence. Do not build an APK after each local visual/code checkpoint. Necessary packaging/native fixes may require corrected builds and relevant rechecks. Do not self-award independent/device/owner acceptance. Continue independent ready work through scoped blockers; a genuine external-limit handoff must identify exact attempted repair, dependency/reconciled shortfall and preserved artifacts, with product INCOMPLETE.

===== LATEST OWNER MOBILE GAME CONTRACT U01-U16 =====
'''
prompt.write_bytes(header.encode('utf8')+owner.read_bytes()+b'\n===== END LATEST OWNER MOBILE GAME CONTRACT =====\n\n'+retained_marker+before_original+delimiter+original.read_bytes())
prefix='> **Latest owner mobile-game/Kingdom/release correction — 17 October 2026: INCOMPLETE.** '
for rel in ['AGENTS.md','START-HERE.md','CURRENT-STATUS.md','DECISIONS.md','docs/SESSION-HANDOFF.md','docs/BUILD-PROGRESS.md','docs/plan/README.md']:
    p=ROOT/rel;text=p.read_text(encoding='utf-8-sig')
    if text.startswith(prefix):text=text.split('\n\n',1)[1]
    def link(q):return Path(os.path.relpath(PLAN/q,p.parent)).as_posix()
    banner=prefix+f"[Owner contract U01–U16]({link(owner.name)}), [architecture/QA recheck]({link('REPAIR-PROMPT-ARCHITECTURE-AND-QA-REVIEW-2026-10-17.md')}) and [ONE current complete repair file]({link(prompt.name)}). Default HUD uses real game icons, resource symbols plus amounts with names accessible in details, bounded equipment sockets and contextual information. Repair sharp registered Kingdom terrain and integrated same-family no-wall/scaffold/built/taller states; no broad blur or foreign fitted wall stamps, and all owned buildings remain truthful dynamic layers. Finish and independently verify the complete desktop game, then build/verify the final snapshot APK, then later mobile QA/repair and owner review. No routine checkpoint APKs or report-only completion. All original scope and budget/preservation controls remain. This revision is documentation/QA, not a new game-test PASS or production/provider/build/device/Git/cleanup/dispatch action. Earlier conflicting UI/release recipes are historical.\n\n"
    p.write_text(banner+text,encoding='utf8')
for name in ['INDEPENDENT-EXECUTOR-VERIFICATION-2026-10-17.md','INDEPENDENT-EXECUTOR-COVERAGE-2026-10-17.md']:
    p=PLAN/name;text=p.read_text(encoding='utf8')
    intro='> **Later owner correction, 17 October 2026:** '
    if text.startswith(intro):text=text.split('\n\n',1)[1]
    p.write_text(intro+f"[U01–U16](OWNER-MOBILE-GAME-UI-KINGDOM-AND-RELEASE-GATES-2026-10-17.md) now specifies icon-led mobile game presentation, sharp integrated Kingdom wall/ground families and complete desktop review before final packaging/mobile QA. [The same ONE repair file]({prompt.name}) is revised in place with those directions and the full unchanged original contract. Findings/test counts below are the earlier implementation audit, not a fresh rerun by this prompt review.\n\n"+text,encoding='utf8')
print('Updated ONE prompt',len(prompt.read_bytes()),hashlib.sha256(prompt.read_bytes()).hexdigest())
