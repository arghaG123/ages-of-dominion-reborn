import json
opens = json.load(open("open-leaves-to-check.json", encoding="utf-8"))
for leaf in opens:
    if leaf["type"] in ("REQUIREMENT", "G_CONTRACT", "MASTER_PLAN_STEP"):
        outcome = (leaf.get("outcome") or "").replace("\n", " ")[:120]
        print(f"{leaf['id']}\t{leaf['name']}\t{outcome}")
