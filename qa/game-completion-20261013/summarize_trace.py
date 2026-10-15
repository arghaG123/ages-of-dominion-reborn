import json
from collections import Counter
from pathlib import Path

report = json.loads(Path("qa/game-completion-20261013/scene-trace.json").read_text(encoding="utf-8"))
print(report["acceptance"], report["pass"], report["fail"], report["blocked"])
notes = Counter(row["reviewNotes"] for row in report["rows"])
for note, count in notes.items():
    print(count, note)
print("---")
for row in report["rows"]:
    edge = row["features"]["roads"]["edge"]
    banks = row["features"]["banks"]["edge"]
    lanes = row["features"]["lanes"]["edge"]
    decks = row["features"]["decks"]
    deck_text = ",".join(str(deck["edge"]["agreement"]) for deck in decks) or "-"
    bank_text = None if banks is None else banks["agreement"]
    lane_text = None if lanes is None else lanes["agreement"]
    print(
        f"{row['scene']:10} {row['ageName']:12} {row['nativeWidth']}x{row['nativeHeight']} "
        f"road={edge['agreement']}/{edge['controlAgreement']} n={edge['samples']} "
        f"bank={bank_text} lane={lane_text} deck={deck_text} "
        f"obs={row['features']['roads']['obstacleIntersectionCount']} "
        f"blk={row['features']['roads']['blockedIntersectionCount']}"
    )
