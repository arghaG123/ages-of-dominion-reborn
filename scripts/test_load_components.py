import os, json, hashlib
from pathlib import Path
from PIL import Image

ROOT = Path('C:/dev/ages-of-dominion-reborn')

def compute_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

# Load v3 components
actors_mounts = json.load(open(ROOT / 'docs/plan/ACTORS-MOUNTS-V3-RESULTS.json'))
rigs = json.load(open(ROOT / 'assets/derivatives/rigs/v3/parts_manifest_v3.json'))
terrain_survey = json.load(open(ROOT / 'docs/plan/KINGDOM-TERRAIN-SURVEY-V3-2026-10-04.json'))
accounting = json.load(open(ROOT / 'docs/plan/ACCOUNTING-CONSISTENCY-V3-2026-10-04.json'))
isolated_controls = json.load(open(ROOT / 'qa/image-v3-isolated-controls-20261004/isolated-reuse-binding-results.json'))

print("All components loaded successfully.")
