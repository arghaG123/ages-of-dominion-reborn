# M14–M15 live mock update — 22 October 2026

**Whole game: INCOMPLETE.** This current recheck supersedes the older M14 unmatched-state and M15 two-formation/swamp classifications only for the Medieval Skirmish deployment and active-battle presentation. It does not accept either mock, close J07–J08, or verify compact layouts, campaign result presentation, release, device, or owner gates.

## M14 — deployment

The approved local route `http://localhost:4174/?audit` reached a real pending Skirmish deployment at exactly 1280×720. The Medieval scene resolved to the registered `assets/high-res/interactive-4k-first32-20261003/run-05-tactical-retry-20261004-015857/packs/tactical-terrain/output.png` wooded river gorge.

The lower roster now contains all six actual formations, with clear side and function: Clubman ×12, Slinger ×8, and Bone Crusher ×5 are selectable allies; Dire Wolf ×4, Bandit ×3, and Cave Bear ×2 are fixed opponents. No provisional initiative order is shown before combat starts. The opposing cards are informational, and only the three allied cards have placement controls. Measured at 1280×720, the roster spans 840.4×67.2px and all six cards fit in one row; Start Battle and Cancel setup occupy the separate right column.

All three allies were placed on legal cells `[0,6]`, `[2,7]`, and `[1,9]`; the view enabled Start Battle only after all three were placed. This is a state-matched live deployment review, so M14 advances from OPEN to **PARTIAL**. It remains short of the mock's denser troop presentation and fine visual match. Exact compact-size rendering and a retained screenshot are still open.

## M15 — active battle

After Start Battle, the real turn order showed six living formations and the registered gorge. The first enemy action struck Clubman, reducing its practice stack from 12 to 11 before the player's first turn; the other counts remained Slinger ×8, Bone Crusher ×5, Dire Wolf ×4, Bandit ×3, and Cave Bear ×2. The active screen showed six initiative entries, the upper-left hero plaque, upper-right Round 1 / Medieval Age / Day 4 badge, and the four context-sensitive actions at lower right.

Measured at 1280×720: hero plaque `[18,84,278,92.3]`; round badge `[1024.4,62,123.6,43.7]`; action dock `[904,579.4,356,122.6]`; each of four action buttons was 164.7×48px. Available actions were Attack (1 legal target), Defend, Wait, and Spell (12 casts). The run rendered 26 figure plates across the six real stacks. M15 advances from the old direct FAIL to **PARTIAL** because the fresh state uses the correct gorge, all six real stacks, initiative, hero context and command hierarchy. The mock's field density and actor detail still exceed this six-stack scene; the source contract caps a battle at six stack slots, so additional mock cards were not fabricated.

The earlier practice review described the old swamp / two-formation screen. That finding is superseded for this current route: the current DOM identified the registered Medieval wooded river gorge and all six formations. This is a bounded in-session visual observation; the approved browser path did not retain the new screenshot as a file. Console warning/error query was empty.

## Practice isolation and verification

The practice retreat confirmation stated that no victory reward, campaign resources, items, casualties, experience, mana, or story would change. Confirmed retreat returned to the War screen, and the save control settled to “Save campaign.” The game’s passive resource counters advanced while the page remained open; no tactical reward or campaign purchase was made. The existing local preview campaign already contains the previously documented Knight’s Longsword. No campaign Duel was started.

- `node --test tests/*.test.mjs`: **267/267 PASS**, including the 10,000-command save-stress horizon.
- `node --test tests/visual-responsive-20261018.test.mjs`: **30/30 PASS**.
- `node --check src/client/main.js` and `node --check tests/visual-responsive-20261018.test.mjs`: passed.
- Approved route live viewport: exact 1280×720 only. The route's exposed controls do not provide a viewport-resize operation, so 825×375 and 933×424 remain unverified live; CSS regression coverage is not a substitute for those captures.

Source changes: `src/client/main.js` renders every real pending-battle formation while preserving ally-only movement; `src/client/polish.css` fits six roster cards and keeps short-landscape deployment actions on their own 48px row; `tests/visual-responsive-20261018.test.mjs` adds roster semantics and compact-layout assertions.

M14 and M15 remain **PARTIAL**; M16 remains **PARTIAL** from the prior practice-result comparison. Whole-game desktop acceptance, the remaining M01–M30/J01–J18 reviews, final package, device QA and owner acceptance remain open. No build/APK, device, provider, Git, cleanup or publication action occurred.
