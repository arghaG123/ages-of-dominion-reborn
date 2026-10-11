"""Rebind the seven class standing-body native pointers to existing exact-hash files.

The 9 October receipts named natives under
qa/image-vertex-repair-20261009/.../receipts/ACTORS/natives/, which are absent on
this device. Hash-identical copies exist under
assets/derivatives/image-unified-reserve-20261009/actors/natives/. This script
publishes a successor interface revision whose source pointers refer to those
existing files. Receipt history is preserved in `receiptPath`; nothing is copied,
restored, regenerated or purchased.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRIOR = ROOT / "docs" / "plan" / "IMAGE-RECONCILE-INTERFACE-2026-10-11.json"
ALTERNATIVES = ROOT / "qa" / "whole-project-audit-20261011" / "native-source-alternatives.json"
DEST = ROOT / "docs" / "plan" / "IMAGE-COMPLETE-INTERFACE-2026-10-11.json"
OUT = ROOT / "qa" / "image-complete-20261011"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    interface = json.loads(PRIOR.read_text(encoding="utf-8"))
    alternatives = json.loads(ALTERNATIVES.read_text(encoding="utf-8"))
    rebind: dict[str, dict] = {}
    report = []
    for alt in alternatives:
        missing = alt["missingPath"]
        expected = alt["expectedSHA256"]
        chosen = None
        for candidate in alt["existingManifestHashMatches"]:
            path = ROOT / candidate
            if path.is_file() and sha256_file(path) == expected:
                chosen = {"path": candidate, "sha256": expected, "bytes": path.stat().st_size}
                break
        report.append({
            "receiptPath": missing,
            "expectedSHA256": expected,
            "boundPath": chosen["path"] if chosen else None,
            "status": "PASS" if chosen else "BLOCKED",
        })
        if chosen:
            rebind[missing] = chosen

    touched = 0

    def walk(node):
        nonlocal touched
        if isinstance(node, dict):
            path = node.get("path")
            if isinstance(path, str) and path in rebind:
                chosen = rebind[path]
                node["receiptPath"] = path
                node["path"] = chosen["path"]
                node["sha256"] = chosen["sha256"]
                node["bytes"] = chosen["bytes"]
                touched += 1
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(interface)
    interface["schema"] = 5
    interface["version"] = "image-complete-20261011"
    interface["priorInterface"] = "docs/plan/IMAGE-RECONCILE-INTERFACE-2026-10-11.json"
    interface["imageWorkComplete"] = False
    interface["localProcessingComplete"] = False
    interface["note"] = (
        "Seven class standing-body native pointers now reference the existing hash-identical files under "
        "assets/derivatives/image-unified-reserve-20261009/actors/natives/. Original receipt paths are kept in "
        "receiptPath. 124 retired historical raw provider responses remain external and unavailable on this device. "
        "Standing bodies remain candidates, not rigs. Scene spatial gates remain FAIL until repaired."
    )
    DEST.write_text(json.dumps(interface, indent=2), encoding="utf-8")
    summary = {
        "status": "PASS" if all(r["status"] == "PASS" for r in report) and touched == len(report) else "PARTIAL",
        "pointersRebound": touched,
        "rows": report,
        "interface": str(DEST.relative_to(ROOT)).replace("\\", "/"),
    }
    (OUT / "native-rebind.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
