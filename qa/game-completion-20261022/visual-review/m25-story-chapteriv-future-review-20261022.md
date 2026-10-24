# M25 Story and Future review — 22 October 2026

**Status: PARTIAL; whole game remains INCOMPLETE.** This review compares the current live Story state with M25 and follows the ordinary campaign controls through all seven adopted chapter choices and the Future acknowledgement. It is not full branch or quest acceptance.

## Current evidence

- Reference: `design-preview/generated/landscape-mocks-20261003-efcd7a7e/images/25-story.jpg` (M25, Chapter IV “The Divided Gate”). The mock index records a parchment chronicle, selected rival dossier, seven chapter choices, and branch flags.
- Fresh natural run: [report.json](natural-story-all-chapters-live-20261022-run01/report.json) from an isolated Chromium context on the current local preview. New campaign, selected Astral Cloudpeaks, visible tutorial skip, lawful building and age costs, then story/rival interactions through the earned campaign. The browser clock was fast-forwarded only across idle elapsed time to cover legal production/build waits; no campaign state or resources were injected.
- The Astral Adventure image used to support that age progression is one of the current illustrative references. Its scene, sites, bridge geometry and appearance are not accepted as game-specific production-map content by this Story review.
- All eight ages were reached naturally. The Hero chose rival Varek Iron-Eye and the first visible branch in each of the seven chapters. Chapter IV was reached at Medieval age (age index 3); all seven saved flags and the same campaign identity survived reload. The save action showed `Saved locally.` before reload.
- The Future page displayed “The Valley We Keep.” The user-facing “Keep the valley” action changed `futureSeen` without an unexplained resource gain after subtracting the exact passive production over the 1,270 ms state-clock interval. The Future acknowledgement and all seven choices persisted after reload.
- Page errors, console errors, and failed HTTP responses: **0**.

## M25 pixel comparison

The live Chapter IV image is a close composition match to M25 at 1280×720: a large medieval gate dominates the scene, two characters face each other, the narrative occupies a centered lower plate, and the two branch controls sit below it. The chapter archive is at upper right. The matched state was reached through earned play, rather than substituting a Stone-age Story screen for the Medieval mock.

Differences in the live capture: the title and current-age label sit at upper left; compact resource chips, Menu/Save, and Chronicle/Quests controls replace the mock’s centered “IRONHEART” header and Settings/Objectives pair; the current right-side challenger model has a different silhouette from the pictured challenger. These are observed differences, not yet owner acceptance decisions. At 825×375 the gate scene remains recognizable, while the lower dialogue panel takes a much larger share of the visible scene.

Visual captures:

- [M25 comparison reference](../../../design-preview/generated/landscape-mocks-20261003-efcd7a7e/images/25-story.jpg)
- [Chapter IV at 1280×720](natural-story-all-chapters-live-20261022-run01/story-chapter-iv-divided-gate-before-choice-1280x720.png)
- [Chapter IV at 825×375](natural-story-all-chapters-live-20261022-run01/story-chapter-iv-divided-gate-before-choice-825x375.png)
- [Future conclusion at 1280×720](natural-story-all-chapters-live-20261022-run01/story-future-conclusion-open-1280x720.png)
- [Future conclusion acknowledged at 1280×720](natural-story-all-chapters-live-20261022-run01/story-future-conclusion-kept-1280x720.png)

## Still open

- Only the first of each chapter’s two story choices was selected; the alternate branch effects and their natural reload paths remain unverified.
- The six-rival alternatives, quest claims/destinations, all eight milestone claims, and the broader M25/M26/J14/J18 assertions are not closed by this run.
- Compact first-entry Story layout has a separate unresolved measurement discrepancy: one fresh 825×375 menu-to-Story run measured overlapping rival/navigation hit areas; another same-day audit measured 2.25 px clearance for the same source hashes. See the [responsive follow-up](story-choice-natural-live-20261022-run03/report.json) and [independent status audit](../../independent-status-20261022/VERIFICATION.md). Keep the Story fit open until browser scale/font conditions are reconciled.

No production source, package, phone/device, provider, or Git state was changed in this review.
