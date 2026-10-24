# Stone Kingdom terrain family candidate review — 20 October 2026

Status: **candidate only; not bound to runtime.** The active `kingdom-stone-family-20261018` files and runtime catalog remain unchanged. Four non-destructive image-generation candidates live under `assets/derivatives/visual-repair-20261020/kingdom/`:

| Phase | Candidate | Dimensions | SHA256 | ORB/RANSAC registration vs active phase |
|---|---|---:|---|---|
| Empty ground | `stone-ground-candidate-v1.png` | 1678×937 | `0327EC7A0D4EAD9E9F6DA54B86D26400C83B8B57D189124B430CE84BC0BD38DD` | 2,667 inliers; median 0.103 px; p95 1.533 px |
| Scaffold | `stone-scaffold-candidate-v1.png` | 1678×937 | `873D54CC10002D09349E192D3A1555E809FF80DE65CD960AD266B4B6C4C0DCAF` | 5,271 inliers; median 0.048 px; p95 1.431 px |
| Built wall | `stone-wall-candidate-v1.png` | 1678×937 | `3DC17056A1D9769BAEAFF575E8DFED2DC0A81599A88E8889C62013ED4BE45D7A` | 4,003 inliers; median 0.137 px; p95 1.485 px |
| Taller wall | `stone-wall-tall-candidate-v1.png` | 1678×937 | `7963EB9BE4D64AD6263FCD49627603819621FD89097B8B73A9B39897BFCCD199` | 4,381 inliers; median 0.132 px; p95 1.470 px |

Generation used the built-in image generation tool. Prompt set: refine natural ground material and local integration to match the approved Stone Kingdom mock's sharp semi-realistic quality; retain the 1678×937 source camera, roads, river, crossings, camps, huts and each phase's wall/scaffold silhouette and gate; leave gameplay building sites open; add no UI or unrelated structures.

Visual review shows the same river, crossings, camps and central layout, with richer terrain detail. ORB/RANSAC estimates show near-identity alignment. This screening does **not** prove pixel-exact road/bank traces, contact geometry, distinct phase legality or full live compositing. Do not bind these assets until those checks pass across the real consumers and all ages. The approved isometric placement contract was not changed. Full suite last passed 228/228 before this candidate work; no code/tests were changed in this image-only pass.
