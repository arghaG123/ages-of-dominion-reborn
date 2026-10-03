# Continue in this chat — 3 October 2026

You are the executor for Ages of Dominion Reborn. Same model: grok-4.7 with reasoning. Do not ask about orientation, account, or project.

Workspace: `C:/dev/ages-of-dominion-reborn`. Old game `C:/dev/ages-of-dominion` and raw art `C:/dev/aod-art-src` stay read-only. Do not publish, deploy, change IAM, or install on a device.

## Already submitted — do not resubmit

Batch `production-03-20261003` is the active job:

`projects/186933974004/locations/global/batchPredictionJobs/3389643852779356160`

Model `gemini-3.1-flash-image`, global batch, exactly 30 requests, 6 USD hold. It contains five revised replacements (kingdom-terrain-stone, kingdom-terrain-medieval, townhall-stone, skill-offense, gear-stone-weapon) plus 21 empty-pad biome terrains and four Stone buildings. Five carried buildings are listed in `docs/plan/image-production/carried-buildings.json` and must be bought before new building identities.

Batches 01 and 02 are collected. Do not repurchase them. An active or unknown job blocks any new paid call.

## When this job becomes terminal

Prepare the next genuinely useful 30, including the five carried buildings, and submit that batch BEFORE collecting batch 03. If it is not ready or the budget check fails, write a deferral and then collect. Hard cap 80 USD. Keep the existing holds. Unknown billing is not zero.

Review outputs against `assets/production/VISUAL-REVIEW-2026-10-03.md`. A technical decode is not a visual pass. Missing alpha is a matte task, not an automatic repurchase. At most two paid attempts per identity.

## Game

Combat damage, defense waves, loot, hero XP, and End Day weather/mana are still blocked. Do not invent those equations. Continue the implemented campaign, tests, and landscape client. Update CURRENT-STATUS.md, docs/SESSION-HANDOFF.md, and docs/BUILD-PROGRESS.md.

Commands: `python scripts/vertex-production.py status 3`, then `submit` only for a prepared later batch, then `collect 3`.
