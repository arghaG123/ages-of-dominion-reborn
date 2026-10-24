# M01 home gate follow-up — 23 October 2026, run 03

**Status: PARTIAL.** The prior pass fixed the cover framing and Continue-after-Settings route, but missed a visible compact-layout mismatch: the gate kept a 320px minimum and covered almost 40% of an 825px landscape view. This follow-up lowers the responsive minimum to 260px.

At the browser's 825×375 request, the observed inner viewport was 826×375 and the stage was 825.6×375.2. The gate measured 260px wide (31.5% of the stage). Continue and New Campaign measured 222.4×52px; Settings and Save/Load measured 106.2×48px. All four labels fit their buttons and all controls remained inside the gate. The panoramic scene continued to cover the remaining stage without side gutters. A compact screenshot was reviewed live through CUA but was not retained as a file.

The active-defense route was also observed in a temporary local preview: Menu → Campaign & saves → Continue returned to the paused defense at 0/5 waves and 400 gate HP. That preview unexpectedly opened a previously populated campaign, so this is supplemental evidence only; it does not close clean-origin or damaged-save review. No slot was loaded, exported, imported, replaced or saved manually.

No-save and damaged-save behavior remain open. Both temporary preview origins presented saved campaigns, so I stopped without clearing or modifying their stored bytes. The exact browser-size offsets remain: 825×375 requested became 826×375 CSS and 824×375 raster in the earlier capture; the 933×424 and exact desktop captures were not repeated in this run. Owner acceptance remains open.

**Verification after the width change:** `tests/visual-responsive-20261018.test.mjs` — 39/39 PASS. The earlier full Node suite result (279/279) predates this CSS-only change and is not reported as a post-change run.
