"""Prepends Image AI completion banner to status and handoff documents."""

from pathlib import Path

ROOT = Path("c:/dev/ages-of-dominion-reborn")

banner_template = (
    "> **Image AI — 32 verified, 8 Kingdom recovery candidates prepared, 73 request packs completed, "
    "runner continuity repaired with offline mocks, redundant staging cleaned (253.11 MiB reclaimed) — 4 October 2026:** "
    "Read [{report_label}]({report_path}). All 32 native 4K outputs verified intact (5504×3072, SHA256 match, 100% decode). "
    "Per-ID delivery manifest bound: 0 promoted to final-native4k (Kingdom 8 bare-content FAIL, 24 Adventure/Tactical/Defense "
    "pending independent asset/owner review). Coherent local recovery candidates (v4 bare bases, removal masks, extended bridge guides) "
    "prepared for all 8 Kingdom terrains in qa/image-next-task-20261004/recovery-candidates/. 8 Hall visible foundations and doorways surveyed. "
    "Focused-camera viewport diagnostics (825×375, 933×424, 1180×820, 1280×720 panel open/closed) evaluated. All 73 later 2K request packs "
    "locally prepared with role-specific prompts and layout specs; purchase status strictly INACTIVE_OWNER_SCHEDULING_REQUIRED (0 calls); "
    "Code AI handoff saved with immediate 1K source reuse. New continuity runner scripts/interactive_runner_continuity.py implements measured "
    "geometry checks, atomic owned mutex, write-ahead persistence, 20s post-success gap (per user directive), 60s 429 backoff, and unknown-outcome "
    "liability retention; 7/7 offline mock tests PASS. Reconciled protected exposure $62.8346 USD ($17.1654 headroom under $80 cap, $15 reserve intact, "
    "Run 1 NO_IMAGE reconciled at text tariff $0.001416). Eligible redundant comparisons/viewports and aborted duplicate PNGs cleaned "
    "(224 files, 253.11 MiB reclaimed, C: free 50.24 GiB); raw response.json deletion deferred pending archive. Zero provider calls, zero purchases. "
    "Concurrent banners and history preserved.\n\n"
)

targets = [
    ("CURRENT-STATUS.md", "the execution report", "docs/plan/IMAGE-AI-EXECUTION-AND-RECOVERY-REPORT-2026-10-04.md"),
    ("docs/SESSION-HANDOFF.md", "the execution report", "plan/IMAGE-AI-EXECUTION-AND-RECOVERY-REPORT-2026-10-04.md"),
    ("docs/BUILD-PROGRESS.md", "the execution report", "plan/IMAGE-AI-EXECUTION-AND-RECOVERY-REPORT-2026-10-04.md")
]

for filename, label, path in targets:
    fpath = ROOT / filename
    if fpath.exists():
        content = fpath.read_text(encoding="utf-8")
        banner = banner_template.format(report_label=label, report_path=path)
        fpath.write_text(banner + content, encoding="utf-8")
        print(f"Updated {filename}")
