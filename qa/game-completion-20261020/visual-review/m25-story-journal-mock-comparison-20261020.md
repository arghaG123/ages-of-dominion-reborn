# M25 story and journal mock comparison — 20 October 2026

**Status: PARTIAL.** Focused layout repairs are now in the runtime, and the rival portrait is fully visible at both tested landscape sizes. The first-chapter run does not yet establish the approved M25 Chapter IV encounter scene or full visual parity.

## Reference and evidence

- Approved reference: `design-preview/generated/landscape-mocks-20261003-efcd7a7e/images/25-story.jpg`.
- Fresh natural-browser runner: `qa/game-completion-20261020/visual-review/story-live-20261020.mjs`.
- Machine-readable run: `qa/game-completion-20261020/visual-review/story-live-20261020/report.json`.
- Captures: `qa/game-completion-20261020/visual-review/story-live-20261020/`.
- Tested at 825×375 and 1280×720 in isolated new campaigns. No page errors, console errors, or failed HTTP responses were recorded.

## What passed

- New campaign opened Story, selected the saved rival Varek Iron-Eye, and exposed both real Chapter I choices.
- The Quests tab showed six distinct quest cards.
- The expanded chapter archive showed all seven adopted chapter subjects, each with chapter art; Chapter I was open and later chapters remained correctly locked at Stone.
- Choosing “Share the fire” set the saved `generous` branch, awarded 120 food, and opened Chapter II. The same rival, branch, chapter, and 370-food balance remained after reload, so the reward did not repeat.
- These mechanics were reproduced at both tested viewports.

## Visual comparison and open defect

The approved M25 image depicts Chapter IV “The Divided Gate”: a large medieval gate and two characters facing one another, with a compact choice plate. The fresh natural capture is Chapter I “The First Fire,” so it does not prove a like-for-like Chapter IV scene match. The updated Chronicle now keeps the full chapter painting unobstructed, moves the narrative and choices into a compact centered lower plate, and puts the archive in the upper-right corner. The selected rival portrait sits in the upper-left story header. The measured portrait/panel overlap is now 0% at both sizes, and its center hit resolves to the portrait image.

The updated Quests page uses a scrollable left journal over the chapter art instead of stretching cards across the full scene. Quest progress, exact rewards, destinations and eight age records are exposed in the UI. The first chapter art is a camp rather than the approved Chapter IV gate, so this is a layout repair and a partial comparison, not acceptance of the requested scene art.

## Acceptance boundary

This is a bounded Story/Journaling mechanics and visual repair, not M25 acceptance. Chapter IV’s naturally earned gate composition, two-character confrontation, locked/cancel paths, all chapter subjects in their earned states, and the Future conclusion “The Valley We Keep” remain open. Source changes are in `src/client/main.js` and `src/client/polish.css`; the natural-browser runner was updated to review the live scene without opening the redundant side panel. No image provider, package, device, or Git action was performed.
