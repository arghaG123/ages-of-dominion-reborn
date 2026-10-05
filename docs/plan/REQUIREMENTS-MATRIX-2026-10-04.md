# Requirements matrix — 4 October 2026

Status: **INCOMPLETE**. Functional PASS is not owner acceptance, art acceptance, or device proof. Missing owner review does not block the next independent code row.

Evidence: `node --test tests/*.test.mjs` → **67 PASS / 0 FAIL**; `qa/code-art-next-verification-20261004/probes.mjs` PASS after save-boundary repairs; `qa/code-art-consumers-20261004/processing.json`. Dirty tree on `cff552880ae15c892b736ac7847f6753787ca58f`. No commit/push. Preservation destinations null.

## OWN rows (owner-facing scope)

| ID | Spec | Implementation | Technical | Source | Derivative | Spatial | Runtime | Owner | Native/device | Storage/Git | Remaining | Next |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| OWN-01 | Eight ages transform homeland | age command + terrain pointers | PARTIAL | 1K terrain bound | none new for ages | FAIL baked content | PARTIAL | UNVERIFIED | STOPPED | blocked | age kits/workers | pad-fit stone plots |
| OWN-02 | Day1 Hall L1 + 17 empty + Walls 0 | campaign bootstrap | PASS | n/a | n/a | Hall FAIL reg | PASS rules | UNVERIFIED | STOPPED | open | accepted Hall | keep proposal |
| OWN-03 | Mutable scaffolds/workers/buildings | jobs + pad-fit plates | PARTIAL | 1K buildings | v2 plates + barracks | pad-fit-v1 PROPOSAL | PARTIAL | UNVERIFIED | STOPPED | open | workers/routes/fields | journey |
| OWN-04 | Adventure 8 biomes | rules + board | PARTIAL | 8×4K tech PASS | not integrated | UNVERIFIED | PARTIAL | UNVERIFIED | STOPPED | open | fog/sites/guards | travel journey |
| OWN-05 | Tactical 7×10 legality | battle.js | PASS rules | maps tech | stick figures | UNVERIFIED | PARTIAL | UNVERIFIED | STOPPED | open | textured 3–7 | clips |
| OWN-06 | Defense 5 roles + bosses | defense.js roles/boss/army | PASS bounded | 1K unused for actors | shapes+projectiles | UNVERIFIED | PARTIAL | UNVERIFIED | STOPPED | open | painted actors | atlases |
| OWN-07 | Four tower families | stats+projectiles+HP | PASS | age forms open | markers | UNVERIFIED | PARTIAL | UNVERIFIED | STOPPED | open | age silhouettes | consumers |
| OWN-08 | Hero 8 classes / 6 slots | core+UI stage | PARTIAL | rig-knight extracted | plate+pose | UNVERIFIED | PARTIAL | UNVERIFIED | STOPPED | open | class kits/compare | forge UI |
| OWN-09 | Army 3 roles × 8 ages + creatures | recruit+stackTitle | PARTIAL | wolf extracted | wolf plate | UNVERIFIED | PARTIAL | UNVERIFIED | STOPPED | open | role plates | dwellings |
| OWN-10 | Forge/loot/equip/compare | forge commands | PASS rules | gear 1K | partial UI | UNVERIFIED | PARTIAL | UNVERIFIED | STOPPED | open | visible compare | inventory |
| OWN-11 | 9 skills / 8 spells | mechanics | PASS | offense UI | v4-ui | UNVERIFIED | PARTIAL | UNVERIFIED | STOPPED | open | spell FX | keep |
| OWN-12 | Story 7 chapters + Future | age-gated | PASS | n/a | n/a | n/a | PASS tests | UNVERIFIED | STOPPED | open | natural ages | journey |
| OWN-13 | Quests/milestones | once-only | PASS | n/a | n/a | n/a | PASS | UNVERIFIED | STOPPED | open | natural clears | journey |
| OWN-14 | War five options | siege/duel/endless/skirmish/challenge | PASS start | n/a | n/a | UNVERIFIED | PASS isolation | UNVERIFIED | STOPPED | open | Challenge UX | seed/file |
| OWN-15 | Skirmish isolation | no campaign writes | PASS | n/a | n/a | n/a | PASS | UNVERIFIED | STOPPED | open | keep | — |
| OWN-16 | Tutorial/help/credits/privacy | screens | PASS partial | n/a | n/a | UNVERIFIED | PASS browser | UNVERIFIED | STOPPED | open | polish | — |
| OWN-17 | Landscape whole game | cameras | PASS framing | mocks | n/a | PARTIAL | PARTIAL | UNVERIFIED | STOPPED | open | mature scenes | — |
| OWN-18 | Positive morale | undecided | BLOCKED effect only | n/a | n/a | n/a | BLOCKED | PENDING | STOPPED | open | owner choice | unrelated OK |
| OWN-19 | Offline local zero permissions | WebView source | PASS source | n/a | n/a | n/a | UNVERIFIED pkg | UNVERIFIED | STOPPED | open | preview APK rebuild | static |

## SYS rows

| ID | Spec | Implementation | Technical | Source | Derivative | Spatial | Runtime | Owner | Native/device | Storage/Git | Remaining | Next |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SYS-01 | Idempotent commands | campaign.command | PASS | n/a | n/a | n/a | PASS | UNVERIFIED | STOPPED | open | keep | — |
| SYS-02 | Chronological producers | settle/advance | PASS | n/a | n/a | n/a | PASS | UNVERIFIED | STOPPED | open | keep | — |
| SYS-03 | Save envelope+checksum | save.js | PASS | n/a | n/a | n/a | PASS | UNVERIFIED | STOPPED | open | native proof | — |
| SYS-04 | Staged replace+revision floor | replaceCampaign | PASS | n/a | n/a | n/a | PASS probes | UNVERIFIED | STOPPED | open | keep | — |
| SYS-05 | Live-write failure recovery | keep latest backup/staged | PASS fault | n/a | n/a | n/a | PASS injection | UNVERIFIED | STOPPED | open | keep | — |
| SYS-06 | Cleanup debt ≠ commit failure | clearStaged | PASS | n/a | n/a | n/a | PASS | UNVERIFIED | STOPPED | open | keep | — |
| SYS-07 | Strict present-null migration | adoptProgress missing() | PASS | n/a | n/a | n/a | PASS | UNVERIFIED | STOPPED | open | keep | — |
| SYS-08 | Damaged Home import/restore | main home | PASS | n/a | n/a | n/a | PASS browser | UNVERIFIED | STOPPED | open | keep | — |
| SYS-09 | Story validation strict | chapter/flags | PASS | n/a | n/a | n/a | PASS | UNVERIFIED | STOPPED | open | natural | — |
| SYS-10 | Audio Music/SFX + background | audio.js | PASS sched | n/a | n/a | n/a | PASS | UNVERIFIED | UNVERIFIED heard | open | heard audio | — |
| SYS-11 | Support screens | help/settings/home | PASS partial | n/a | n/a | UNVERIFIED | PASS | UNVERIFIED | STOPPED | open | journeys | — |
| SYS-12 | Slots import/export/backup | save slots | PASS | n/a | n/a | n/a | PASS | UNVERIFIED | STOPPED | open | keep | — |
| SYS-13 | Defense fixed step/pause/2x | defense.js | PASS | n/a | n/a | UNVERIFIED | PASS | UNVERIFIED | STOPPED | open | dense waves | sessions |
| SYS-14 | Native DOM storage/origin/pause | MainActivity | PASS source | n/a | n/a | n/a | UNVERIFIED APK | UNVERIFIED | STOPPED | open | rebuild preview | static |
| SYS-15 | Dist asset closure | build.mjs | PARTIAL | selection | new derivatives | n/a | UNVERIFIED | UNVERIFIED | STOPPED | open | rebuild dist | packaging |
| SYS-16 | Git asset preservation | destinations null | FAIL | 67 tracked | n/a | n/a | n/a | UNVERIFIED | n/a | BLOCKED | two durable copies | ask destinations |

Ordered ready queue: connected recruit→travel→tactical→defense→story journey evidence; remaining OWN art/atlas work; preview APK static rebuild; OWN-18/device/Git stay blocked only for their rows.

Positive morale remains pending and blocks only that effect. Image-provider retries, batch 18+, and device installation stay out of this executor.
