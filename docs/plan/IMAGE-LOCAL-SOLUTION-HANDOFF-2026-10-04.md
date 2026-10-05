# Image local solution handoff — 4 October 2026

Local execution of `docs/plan/IMAGE-AI-CONSOLIDATED-LOCAL-SOLUTION-2026-10-04.txt`. No provider call, no native overwrite, no game edit. `codeAIHandoffReady` stays false. Interface: `docs/plan/IMAGE-DELIVERY-INTERFACE-V6-2026-10-04.json`. Checkpoint: `qa/image-local-solution-20261004/checkpoint.json`.

## Ready for Code now

Static plates already reviewed, plus:

- Stone heavy stays `assets/derivatives/actors/v5/troop-stone-heavy.png`.
- Industrial melee cast shadow is a separate optional layer. Default actor: `assets/derivatives/actors/v6/troop-industrial-melee.png` (`3a17f25a9df60d18b24df30afa1911ecaa4eb5ce51e146986b0878e1f5717579`). Boots kept. Usable at 64px and 130px as a static plate.
- Ranger sleeve `assets/derivatives/rigs/v5/ranger/sleeve_upper_arm.png` over vambrace `vambrace_hand_open.png`. Native crops `[76,1094,230,1397]` and `[61,1404,211,1784]`. Placement is 0.30 cuff insertion and +0.05 cuff transverse, child behind the sleeve, shared pivot. Demonstrated only at -25°, 0°, and +25°. The vambrace already has 547 interior transparent pixels; they were not filled.

## Partial

- Modern heavy halo is gone on a grey composite and the helmet core was protected. The ground slab under the tracks is still there at 64px. Output `assets/derivatives/actors/v6/troop-modern-heavy.png`. v4 remains.
- Modern ranged bright mound `[836,1210,1211,1389]` was removed. The grey sheet under the body and the bipod-foot snow caps stay. This is still a snow-scene illustration, not a general actor.
- Bronze heavy stays the Charioteer: two horses, two crew, one vehicle. The dirt patch remains. It is not in the three-role draft.
- Healer v6 parts are real arms, a greave, a boot, torso, and skirt. `arm_upper_left.png` is waist armor. `boot_leg_left.png` and `boot_leg_right.png` are upper-leg armor. Historical v4 files were not edited. Sides are UNKNOWN. Joints were not run.
- Paladin v6 is one coherent set, including a combined sword and hand. No mirror. Sides are UNKNOWN. Joints were not run.

## Failed and stopped

- Medieval melee: two shadow attempts. The long cast shadow remains. Keep v5. Do not use the v6 file.
- Knight thigh to greave: 12 placements plus one deeper correction still show a hairline gap. `qa/image-local-solution-20261004/joints/knight_thigh_greave_correction_0.png`. Not an articulated leg.
- Stone Clubman and Stone Slinger: the three ledger copies of each are the same platform painting. Draft stays unsubmitted.
- Industrial ranged: the three ledger copies are the prone sheet. Standing anatomy is absent.
- Mage, Warlock, Necromancer, and Barbarian components were cut into `qa/image-local-solution-20261004/components/`. The Mage torso component includes the painted TORSO/PELVIS labels and leader lines, so those files were not promoted.

## Draft

`docs/plan/REPLACEMENT-DRAFT-THREE-ROLES-V6-CLARIFICATION-2026-10-04.json` is `DRAFT_NOT_SUBMITTED` / `OWNER_BUDGET_AUTHORIZATION_REQUIRED`. Stone ranged is a Slinger with a sling, not a bow or spear. The recorded 0.3108 USD figure is an unverified planning estimate.

Terrain survey `qa/image-v4-repair-20261004/terrain/clearance-v4.json` is unchanged. Roads and rivers are still unlabeled. Nothing was promoted.

Matte, static size, joint, scene, runtime, and owner acceptance are separate. Device QA stays stopped.
