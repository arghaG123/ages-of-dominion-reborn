"""Owner-authorized specification/prompt changes only; no game/provider/build work."""
import hashlib,json,re
from pathlib import Path
R=Path(__file__).resolve().parents[2]
decision='OWNER-REVIEW-SEQUENCE-AND-MORALE-DECISION-2026-10-11.md'
protected=['src/core/battle.js','src/core/mechanics.js','src/core/rules.js','src/core/campaign.js','src/core/save.js','src/client/main.js']
before={p:hashlib.sha256((R/p).read_bytes()).hexdigest() for p in protected}
p=R/'docs/plan/ONE-WORKABLE-CODE-IMAGE-BLOCKER-SOLUTIONS-PROMPT-2026-10-11.txt'
t=p.read_text(encoding='utf-8-sig')
replacements={
'Whole product stays INCOMPLETE until all mandatory gates close; physical device STOPPED, positive morale PENDING_OWNER_DECISION and owner acceptance UNVERIFIED remain separate. These gates do not prevent unrelated local completion.':'Complete the implementation and final build first, then deliver them for this planner\'s independent visual/mock and previous-game functionality verification. Owner review follows the complete verified build. Device verification is authorized for the later stage after full planned implementation/build and independent desktop verification; perform no device work now. Positive morale is DECIDED below, implementation UNVERIFIED. Report implementation/build completion separately from deferred device and owner review; continue all ready work.',
'Read this prompt, docs/plan/BLOCKER-SOLUTIONS-INDEPENDENT-VERIFICATION-2026-10-11.md and qa/planner-blocker-solutions-20261011/ first.':'Read this prompt, docs/plan/'+decision+', docs/plan/BLOCKER-SOLUTIONS-INDEPENDENT-VERIFICATION-2026-10-11.md and qa/planner-blocker-solutions-20261011/ first. The owner\'s latest 11 October review sequence and delegated morale decision supersede historical STOPPED/repeat-permission/morale-choice/preview-approval requirements. No further owner morale choice is needed.',
'Positive morale remains pending with no invented extra turns.':'Implement the decided bounded positive-morale rule in J2, with no chains or negative turn-skip addition.',
'Single agent, no subagents/messages/executor dispatch/new chats/automations. No account/cloud/server/store/release work, global CLI/IAM/billing changes or provider switching. Runtime completely local with zero declared/granted permissions. Device STOPPED until renewed explicit permission; do not probe/install/reset/test physical hardware. Owner acceptance and positive morale require genuine owner decisions only for dependent gates.':'Single agent, no subagents/messages/executor dispatch/new chats/automations. No account/cloud/server/store/release work, global CLI/IAM/billing changes or provider switching. Runtime completely local with zero declared/granted permissions. Device verification is DEFERRED until full planned implementation/build and independent desktop verification; the owner has authorized that later verification, with no device action now. Owner review follows the finished independently verified build and never blocks its preparation. Positive morale is already decided by owner-delegated planner authority; implement J2 without asking for another choice.',
'No install/device/performance acceptance claim.':'This execution handoff performs no device installation/test now; report the complete verified build for the planner\'s later authorized device stage. Do not claim native performance before that evidence.',
'Owner acceptance remains separate until given.':'The planner independently verifies actual visuals and adopted previous-game functionality first; owner review occurs on the complete verified build, with no earlier preview-approval dependency.',
'Device/runtime performance/owner approval stillUNVERIFIED until actual authorized evidence.':'Device verification remains DEFERRED until the full implementation/build and independent desktop audit close; later device performance and owner review require actual results, separately from completed build status.',
'forceoutcomes/reseed/reroll or invent freeRankUp/extraTurns/currency/sites.':'forceoutcomes/reseed/reroll or invent freeRankUp/unbounded morale chains/currency/sites.',
'Do not dispatch/delegate/message,mutate Git,install/test devices,publish releases or ask the owner to repeat recorded settings/authorization.':'Do not dispatch/delegate/message,mutate Git,install/test devices before the deferred verification stage,publish releases or ask the owner to repeat recorded settings/authorization or the now-decided morale choice.'
}
for old,new in replacements.items():
    if t.count(old)!=1:raise ValueError('Unexpected replacement count: '+old[:90])
    t=t.replace(old,new)
addition='''J2. Implement the decided positive-morale rule; close final independent verification
Owner delegates the decision to the planner; the design is now adopted, implementation unverified. Tactical campaign/Duel and isolated practice scenarios with declared morale use effective commander Leadership+supported equipped/stack bonuses-documented weather penalty, clamped[-3,3]. No fabricated enemy commander, racial penalty or class immunity. Preserve source coefficient: chance=max(0,morale)*.042, giving4.2/8.4/12.6percent at1/2/3. Real-time Defense/Endless has no bonus turns; explain Tactical-only applicability there rather than invent firing/income buffs.

After the first eligible completed ordinary Move/Melee/Shoot activation per stack/round, resolve damage/retaliation/outcome first. If actor alive and battleACTIVE and morale>0, consume exactly one persisted battle RNG roll. On success grant the same stack ONE immediate bonus activation ahead of the next ordinary stack. No roll from Wait, Defend, commanderSpell, retaliation, rejected action, bonus action or resolved battle; Wait merely delays the ordinary eligible activation. Bonus permits ordinary legal Move/Melee/Shoot/Defend or explicit Skip; no Wait or chain. No reset of ammo,mana,once-per-roundspell,retaliation,Wait,buffs/casualties/stats/rewards. Existing applicable effect decay still happens per completed activation. Preserve unique queueIDs with validated activation bookkeeping, not duplicated queue entries. Persist/log check,roll,outcome,currentbonus,granted/used flags and round; reset only on real nextRound. Legacy acted stacks get no retroactive bonus; unacted stacks remain eligible. Render/preview/reload/replayed command never rerolls. Snapshot actual commander morale (currently omitted), side ownership and isolated practice RNG.

Require boundary/exclusion/no-chain/RNG/queue/actor-death/final-kill/Wait/bonus-Skip tests, saved activebonus/reload/idempotence/legacy/corrupt-state checks, manual/Auto controlled-action parity and full practice isolation. Reverify seeded earned progression/balance after new RNG draws; historical124Duels/Wisdom42 recipe is not a promised post-change count. Replace PENDING_OWNER_DECISION runtime constant/comments/UI only during verified implementation. Full details and research are in docs/plan/OWNER-REVIEW-SEQUENCE-AND-MORALE-DECISION-2026-10-11.md.

Finish all planned game/art/build scope, then deliver the actual current build to this planner for independent verification before owner review. The planner must compare all30mock/state rows plus every additional screen/state,8ages/8classes/fourkits/32worlds, actual geometry/contacts/gear/motion/mattes,4viewports/portrait and usable UI. A complete previous-game functionality matrix must cite read-only old source/data, adopted canonical changes, reborn behavior and real runtime/earned/regression evidence for every system/control/mode/state. Independently authored parity excludes deliberate documented improvements and obsolete prototype bugs. Repair every unexplained discrepancy before reporting verified completion. Device verification is deferred to after those completion conditions; no premature owner-review or repeat-morale-decision pause.

'''
anchor='K. Deliver a fresh lean package without deleting referenced bytes\n'
if t.count(anchor)!=1:raise ValueError('Missing unique K anchor')
t=t.replace(anchor,addition+anchor)
accept='- Morale: decided functional positive effect implemented with exact .042 coefficient, one eligible seeded roll/one bonus maximum per stack/round, no chains or extra commander casts; valid unique queue, Auto, save/migration/reload/idempotence and isolated practice tests PASS. Design adoption is not implementation PASS.\n'
t=t.replace('6. Acceptance criteria\n\n','6. Acceptance criteria\n\n'+accept)
p.write_text(t,encoding='utf-8')
prefixes={
'AGENTS.md':'docs/plan/', 'START-HERE.md':'docs/plan/', 'CURRENT-STATUS.md':'docs/plan/', 'DECISIONS.md':'docs/plan/',
'docs/SESSION-HANDOFF.md':'plan/', 'docs/BUILD-PROGRESS.md':'plan/', 'docs/plan/README.md':'',
'docs/plan/FULL-IMPLEMENTATION-SPEC.md':'', 'docs/plan/MASTER-PLAN.md':'', 'docs/plan/SOURCE-EQUATIONS-ADDENDUM-2026-10-03.md':''}
for rel,link in prefixes.items():
    dest=R/rel
    body=dest.read_bytes()
    notice=('> **Latest owner review sequence and delegated morale decision - 11 October 2026:** ['
      'Authoritative decision and research]('+link+decision+'); [updated ONE executor prompt]('+link+'ONE-WORKABLE-CODE-IMAGE-BLOCKER-SOLUTIONS-PROMPT-2026-10-11.txt). Complete the whole planned game/art/final build first; this planner independently verifies all actual visuals against mocks and adopted previous-game functionality before owner review. Device verification is authorized for the later completed-plan/build/independent-desktop-verification stage, with no device action now or repeat permission prerequisite. Positive morale DESIGN DECIDED: source-compatible4.2percent per positive morale point,capped12.6percent,one immediate Tactical bonus action per stack/round,no chains; implementation/test status UNVERIFIED. No further owner morale choice or interim owner-preview approval blocks existing execution scope. Product remains INCOMPLETE while required work is open. Planner docs/research only; no production/provider/build/device/Git/backup/dispatch action. Earlier pending/STOPPED banners are historical.\r\n\r\n')
    dest.write_bytes(notice.encode('utf-8')+body)
ledger=R/'docs/plan/DATA-ADOPTION-LEDGER.json'
lt=ledger.read_text(encoding='utf-8-sig')
old='"status": "DOCUMENTED_PARTIAL_TURNS_MORALE_DECISION_PENDING",'
new='''"status": "DOCUMENTED_TURNS_MORALE_DESIGN_DECIDED_IMPLEMENTATION_UNVERIFIED",
      "moraleDecision20261011": {
        "authority": "Owner delegates positive morale design to planner after research",
        "specification": "docs/plan/OWNER-REVIEW-SEQUENCE-AND-MORALE-DECISION-2026-10-11.md",
        "priorStatus": "DOCUMENTED_PARTIAL_TURNS_MORALE_DECISION_PENDING",
        "probabilityPerPositivePoint": 0.042,
        "moraleCap": 3,
        "maximumBonusActivationsPerStackRound": 1,
        "chains": false,
        "implementationStatus": "UNVERIFIED"
      },'''
if lt.count(old)!=1:raise ValueError('Ledger row status drift')
lt=lt.replace(old,new).replace('"moraleDecision": "PENDING_OWNER_CHOICE_EXTRA_TURN_VS_COSMETIC"','"moraleDecision": "DECIDED_OWNER_DELEGATED_PLANNER_EXTRA_ACTION_20261011",\n    "priorMoraleDecision": "PENDING_OWNER_CHOICE_EXTRA_TURN_VS_COSMETIC"')
json.loads(lt)
ledger.write_text(lt,encoding='utf-8')
checks={'sevenSections':re.findall(r'^([1-7])\. (.+)$',t,re.M),'sourcePreserved':{s:hashlib.sha256((R/s).read_bytes()).hexdigest()==h for s,h in before.items()},'promptSHA256':hashlib.sha256(p.read_bytes()).hexdigest(),'moraleDesignDecided':True,'implementationVerified':False,'noProductionProviderBuildDeviceGitBackupDispatch':True}
assert len(checks['sevenSections'])==7 and all(checks['sourcePreserved'].values())
(R/'qa/planner-owner-sequence-morale-20261011/checks.json').write_text(json.dumps(checks,indent=2))
print(json.dumps(checks,indent=2))
