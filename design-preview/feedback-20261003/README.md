# Section feedback gallery — 3 October 2026

Open http://127.0.0.1:4186/design-preview/feedback-20261003/ while the local review server is running.

This review artifact contains 43 samples: 23 existing landscape appearance references and 20 layout or recovered-derivative studies. The original 41 sections and their local feedback keys are unchanged. Two added sections show the recovered Stone placement and the resource/Offense sample. Owner feedback is still pending unless an exported file is supplied. It covers Home, eight classes, New Campaign, Day 1 Kingdom, all eight ages, construction, offline return, Market, Adventure overview/crossing/foot travel, Tactical deployment/action/results, Defense preparation/waves, Hero, skills, spells, Forge, inventory, army, Codex, War selection, story, quests, tutorial, settings, saves, recovery, help, privacy, rotation guidance and the material board. The classes share one sample; the eight age views each have their own sample.

Choose a section, inspect the sample and its remaining-work note, then select **Keep direction** or **Needs changes** and add notes. Feedback saves in this browser's local storage. **Export feedback** downloads every section decision and comment as JSON. To share it with the verifier, provide the exported file or paste the relevant notes in chat. The gallery does not send feedback to a service or automatically update approval ledgers. **Open large sample** opens the chosen landscape sample without the review sidebar.

## Verification

- The catalogue check loads every section, including the original 41 and the two recovered samples. The latest run reported 43 samples, 23 appearance references and 20 layout studies, with export retaining both recovered section ids.
- Representative views include the recovered Stone placement and the resource/Offense sample at 1280×720, plus those two samples at 825×375, 933×424, 1180×820 and 1280×720. A loaded image without stage overflow is not visual fidelity.
- Feedback survived reload and the export contained one entry per section in an isolated QA browser. QA feedback is not owner feedback. No owner decision was supplied for the new sections.
- Evidence: `../../qa/section-preview-20261003/checks.json` and the `contract-*.png` captures. `preview-manifest.json` binds the catalogue and 23 unchanged raster references by SHA-256.

## Limits

These samples support visual feedback. They are not playable game sections. Existing references retain their original title/text, camera, geography, age-material and icon defects; each section calls out relevant remaining work. New layouts use unchanged source artwork. Knight/Warlock paintings remain pending; class and skill backgrounds require matte recovery. Day 1 is a site-centre placement study, with final hall, clearings, actor placement, pad borders and registered world composition still pending. Final source recovery, composite fidelity, readable game controls on hardware, runtime behavior and owner approval remain separate gates.

The original game at `C:\dev\ages-of-dominion` and the raw art at `C:\dev\aod-art-src` were not edited. This gallery change made no provider calls, did not delete originals, and did not install or publish a build. Owner acceptance of the recovered samples is still pending.

If the local server has stopped, start a review-only static server from PowerShell:

```powershell
python -m http.server 4186 --bind 127.0.0.1 --directory 'C:\dev\ages-of-dominion-reborn'
```
