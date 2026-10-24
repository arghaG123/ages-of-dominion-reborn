# M01 home gate follow-up — 23 October 2026

**Status: PARTIAL.** The two targeted M01 defects are repaired: the compact home scene now uses a centered cover fit, and Continue no longer resumes to Settings after a Settings → Back round trip. Live browser checks returned to the saved Stone Kingdom.

At both compact captures, the scene fills the stage without side gutters and all four gate actions remain inside the panel. The in-app viewport tool reports 826×375 for the 825×375 request and 934×424 for the 933×424 request; its retained raster files are 824×375 and 932×424. A fractional override was rejected. Its 1280×720 request produced a 1166×530 screenshot, so that file is not treated as an exact desktop capture.

New Campaign opened the world picker and returned to the gate without starting a campaign. Save/Load and Settings opened; no save slot was stored or loaded. Continue after Settings returned to Kingdom at Stone Age, day 1. No-save, damaged-save, and active battle/defense resume states remain unreviewed. M01 therefore remains partial.

The temporary browser reset to its host 403×716 portrait viewport logged repeated `Art foot is above the visible scene area` errors from Kingdom painting. They stopped after restoring the compact landscape viewport and did not recur there; retain this as a separate runtime follow-up.

**Verification:** focused responsive file 39/39 PASS; full Node suite 279/279 PASS. The screenshot files and machine-readable details are in this folder.