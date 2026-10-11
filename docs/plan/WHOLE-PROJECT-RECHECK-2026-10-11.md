# Whole-project recheck - 11 October 2026

**Overall: INCOMPLETE.** Checked current source at `790629dec96226021182c8ab5c03bc4e474b8db9`, the canonical full plan, its requirements traceability and 109 linked/current planning documents. This is an independent verification pass, with fresh Node tests, isolated headless browser checks, file/hash checks and static APK inspection. No game/art repairs, paid/provider calls, accounting changes, builds, device work, backups, ZIPs, commit or push were performed.

## Fresh findings

| Area | Current finding | Meaning and remaining work |
|---|---|---|
| Core tests | **PASS bounded: 108/108**, no failures/skips | Core/system assertions pass. This does not complete full gameplay, visuals or physical-device acceptance. |
| Source asset availability | **PASS: 3,647/3,647** transfer-manifest assets match size/SHA256 | Current game art files are present. No need to repurchase assets solely because QA paths are missing. |
| Consumer file contracts | **PASS bounded:** 353 rows, 645 source/output references, zero hash/dimension errors | Eligibility is still 68 PASS / 272 BLOCKED / 13 PARTIAL. File integrity is distinct from clean art, correct geometry and actual live use. |
| Current web closure | **PASS bounded:** 333 declared assets / 373 expected web files; zero missing source files or external network references | Checked without creating a dist copy. No new web build was run. |
| Navigation screens | **PASS bounded:** 12 navigation views load without broken image elements; Home also captured | Rendering a view is not proof that every action, state or earned progression is complete. |
| Retreat navigation | **PASS:** background programmatic Kingdom click leaves Tactical/modal/action count unchanged; Cancel works | Supersedes the 9 October scoped failure. Full battle/action/input coverage remains separate. |
| Army layout | **PASS bounded:** captions/plates inside stage at 825x375, 933x424, 1180x820, 1280x720 | Fresh Stone review checks. Does not establish all eight ages, all screens, touch ergonomics or device performance. |
| Exact v4/v5 guides | **PASS:** present with required original hashes | Both are ignored and untracked. Track these two small essential exceptions for reproducible clones. Recoverable in Git commit `7af55b7`; no old-device request is necessary for these guides. |
| Reconciled Image references | 70 reference checks PASS; seven named receipt PNG paths MISSING | **All seven exact native images have hash-identical existing copies** under `assets/derivatives/image-unified-reserve-20261009/actors/natives/`. Publish corrected source-path contracts; no new render, purchase or duplicate copy is needed to fix these bindings. |
| Scene gates | **32 binding PASS; 32 spatial FAIL** | The source-discovery problem is resolved. Roads, banks, bridge approaches, building footprints/entrances/heights and the physical scene still need registration and visual acceptance. |
| Class art/rigs | Standing bodies and partial derivatives present; complete gait/rig/atlas delivery **FAIL/INCOMPLETE** | Correct mattes, sides, joints, equipment attachments and timing. A standing plate is not an articulated character. Unity knight remains an unreviewed possible trial, not approved production art. |
| Local APK | **FAIL current-source parity:** 319,425,603 bytes, SHA256 `02f85e52c5c1aab755e42374bfd2c166f7ba0d5e23519314830de0e00b5694bd` | CRC passes, but it lacks 107 expected current files and differs on seven more. This laptop retains an older APK, not the 509,502,836-byte package recorded by the 9 October audit. Rebuild/reverify after current changes. |
| Full play/owner/device | **UNVERIFIED; device STOPPED** | Earned eight-age progression, natural prepared Siege victory with settlement/reload, full six-slot Forge/equipment journey, all five War round-trips, final visual review and actual Android performance remain open. |
| Historical QA/provenance transfer | 2,019 lineage and four capture manifest files absent; three old ZIP payloads absent | Recover only required existing lineage/evidence from the previous device if needed. This does not negate the verified current asset tree. The 124 retired historical raw responses are still external and were not recovered here. No new backups were made. |

Evidence is in `qa/whole-project-audit-20261011/`: `node-tests.txt`, `browser-retreat-army.json`, `transfer-check.json`, `consumer-file-check.json`, `image-interface-check.json`, `native-source-alternatives.json`, `package-check.json`, `guide-check.json` and current captures.

## Actual pixels versus the approved direction

Current pixels were viewed directly, including Kingdom, Adventure, Tactical/Skirmish, Hero, Army and Forge. Kingdom was compared with generated mock02 and the Hero/equipment direction with mock19. This is scoped sampling; the complete thirty-screen/state reference comparison was not performed or claimed.

- **Kingdom:** a realistic terrain painting and seventeen functional plot overlays exist. The active arrangement, overlays, Hall placement/size, river crossings and chrome differ substantially from the approved composition. The painting still contains extra structures; the large blank upper strip and schematic boundaries remain visible.
- **Adventure:** realistic terrain is present, but the broad drawn route strips, circular markers and labelled flat site pads remain provisional instead of finished registered world content.
- **Tactical:** the fresh Skirmish screen has an action interface and projected board, but visible unit presentation is incomplete and the map is small within the phone frame. A loaded board does not establish the promised finished battle scene.
- **Hero:** the captured current view presents portrait/class choices rather than the full realistic character/equipment-room composition. Full body/kit integration remains open.
- **Army/Forge:** readable captions and functioning panels exist; bare backgrounds, provisional cutouts, placeholder slot symbols and incomplete figure integration still differ from the promised visual finish. The small-layout check does not make these finished screens.

All final production artwork must remain **semi-realistic or realistic**, matching the approved direction. Structural SVG controls/geometry do not count as completed production artwork. No new owner acceptance was inferred.

## Full requirements crosswalk

These are scoped dispositions, not a completion percentage. PASS means only the named bounded requirement; most product rows remain PARTIAL until complete workflows and visuals are demonstrated.

| ID | Present / verified | Remaining work / disposition |
|---|---|---|
| OWN-01 section acceptance | Direction/reference galleries retained; implementation authorized | Finished section owner acceptance UNVERIFIED |
| OWN-02 independent rebuild | Current repository/source baseline; local core/client modules | PASS bounded; no exhaustive originality/ancestry audit |
| OWN-03 existing-art reuse | 3,647 asset hashes and 353 consumer contracts pass | PARTIAL: promote only individually validated runtime uses |
| OWN-04 connected genres/campaign | Campaign, Adventure, Tactical and Defense core; bounded starter journey saved | PARTIAL: full natural connected journey/wins/reloads |
| OWN-05 approved composition | Existing realistic paintings and registered legal contract | FAIL: current pixels and 32 scene spatial gates |
| OWN-06 realistic finish | Realistic portraits/terrain/partial plates | FAIL final finish; complete assembly, mattes and UI presentation |
| OWN-07 Day1 sites | Sparse-start and plot rules pass suite;17 pads plus separate Hall | PARTIAL: artwork footprint/entrance/framing acceptance |
| OWN-08 eight ages | Eight-age data/building/terrain support | PARTIAL: earned complete progression and all-age rendered workflows |
| OWN-09 terrain/sites | Navigation/source catalogs present;32 source bindings pass | PARTIAL: actual routes, contacts, crossings and per-scene clearance |
| OWN-10 mounted motion | Single-pose mount/limited assembly inputs | FAIL full supported gait/sides/attachments |
| OWN-11 eight classes/kits | Eight class records/cards, seven body natives available | FAIL complete class rigs/kits/animation delivery |
| OWN-12 Defense role behavior | Causal role/wave/fixed-step tests pass | PARTIAL: natural victory settlement/reload and dense live behavior |
| OWN-13 Tactical controls | Core/redraw tests and fresh modal regression pass | PARTIAL: all action/results/manual workflows and final figures |
| OWN-14 era identity | Eight-age names/art associations/substitutions exist | PARTIAL: usable era-correct art across all live consumers |
| OWN-15 return quality | Rival/story/quest systems in source | PARTIAL: balanced natural play and owner experience review |
| OWN-16 complete handoff | Current report, canonical scope and scoped next work documented | PASS bounded documentation |
| OWN-17 environment reuse | Existing Node24.19.0/Python3.13.15/tools available | PASS bounded; no installs/account changes |
| OWN-18 image/provider policy | Reserve-release authority/control history present | PARTIAL: live availability/unknown operations/invoice reconciliation belongs to executor before paid calls |
| OWN-19 offline/publishing boundary | Current source closure has zero external network references | PARTIAL: refreshed packaged/native proof; no device/store activity |
| SYS-01 economy/buildings | Cost/production/instance/payment assertions pass | PARTIAL: full eight-age economy/balance and building-state UI |
| SYS-02 Army/creatures | Recruitment/capacity/roles/ranks/creature rules and current Army view | PARTIAL: all live figures, creature flows and persistent losses |
| SYS-03 six equipment slots | Slot validation/craft/equip/unequip source and tests | PARTIAL: six naturally earned slots through actual UI and reload |
| SYS-04 Forge/Market | Current layouts/commands/tests present | PARTIAL: complete real previews, quality/cost/exchange/result workflows |
| SYS-05 Hero/skills/spells | Stats, nine skills/eight spells and eligibility rules | PARTIAL: full rendered kit/offer/spell journey; positive morale owner decision pending |
| SYS-06 Adventure | Map/path/fog/encounter core; current view loads | PARTIAL: all site/pickup/recovery flows and finished registered presentation |
| SYS-07 Tactical | Turn/action/legal-target core and modal guard pass | PARTIAL: all control vectors/actions/animations/result/reload journey |
| SYS-08 Defense | Four tower/five attacker/fixed-step/pause/speed/casualty rules | PARTIAL: real deploy/telegraph/ability/dense rendering and natural win |
| SYS-09 story/objectives | Chapters/Future, six quests, milestones/rival in source | PARTIAL: full natural unlock/branch/reward/claim/read-through proof |
| SYS-10 support/audio | Settings/help/audio/privacy support source; screens load | PARTIAL: heard audio and all options/content/native lifecycle verification |
| SYS-11 tutorial | Sparse affordable starter and tutorial rules | PARTIAL: complete natural Build/Recruit/Travel/Battle/Defense tutorial |
| SYS-12 saves | Schema/checksum/domain/corruption/slot/import-export rules pass | PARTIAL: complete actual file/quota/corrupt-backup UI flows and device storage |
| SYS-12a save boundaries | Fault/domain guards retained and suite passes | PASS bounded automated checks; preserve when integrating |
| SYS-13 shared progression | Shared campaign state/idempotence/practice-isolation tests | PARTIAL: all natural mode return/reload consequences |
| SYS-14 native package | Old APK exists and its CRC passes | FAIL current local package parity; rebuild and verify permissions/closure |
| SYS-15 mobile/performance | Four-size Stone Army/modal regression passes | PARTIAL: every screen/eight ages/touch/insets/dense-device frame/memory evidence |
| SYS-16 five War flows | All five start; practice-isolation and causal tests pass | PARTIAL: complete natural setup/result/return/replay/save/reload for each |
| GIT-01 portability/Git | Main and origin/main match checked790629d; all current asset bytes present | PARTIAL: guide ignore exceptions; required lineage/raw recovery; future transfer verification |

## Next work, in order

1. **Correct metadata source paths for the seven native bodies** using the already-present exact-hash files. Keep historical receipts intact; publish one consistent current interface/diagnostic/gallery revision. No duplicate image purchase or backup is needed.
2. **Finish Image content and scene registration:** source-preserving matte repairs, complete supported rigs/sides/animation timing, all32 scene roads/banks/bridges/entrances/heights/clearance. Continue local ready work; use paid corrections only under the existing per-ID authority and fresh budget/unknown-operation checks.
3. **Code integrates each verified output** while finishing realistic Kingdom/Hero/Adventure/Tactical/Defense and supporting layouts. Preserve geometry and good existing crops. The new reconciled/unified namespace currently has no references in `src/`; the Slinger still displays its older provisional plate.
4. **Demonstrate remaining natural product flows:** Siege win and once-only settlement/reload; six Forge/equipment slots; five War round-trips; earned eight-age progression; complete tutorial/story/saves/support behavior. Label fixtures separately.
5. **Compare all required screens/states against the thirty mocks**, at all four landscape sizes with meaningful readable/touch targets. Keep the semi-realistic/realistic requirement; do not call generic panels or diagrams final art.
6. **Track the two essential small guides as exact ignore exceptions**, and rebuild/reverify the final web/APK package after integration. Current local APK is stale. No rebuild was performed by this audit.
7. **Owner decisions/gates:** positive morale effect remains pending; physical-device testing requires renewed owner permission and remains STOPPED; final visual/product acceptance remains owner-controlled. Existing reserve release is already authorized; additional money is needed only if fresh verified requests exceed the hard-cap capacity.

Missing historical lineage affects its own verification/reuse actions. Source binding, guide absence, device pause and a pending morale choice must not halt unrelated ready implementation. This audit creates no backups or transfer ZIPs, in line with the owner's storage instruction.
