import base64
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "qa/professional-art-20261018/tactical-stone-registered-v1"
PACK = ROOT / "qa/professional-art-20261018/tactical-stone-ground-edit-v2"
CONTRACT = ROOT / "src/data/implementation-contract.json"
geometry = json.loads(CONTRACT.read_text())["geometry"]["tactical"]
matrix = geometry["worldToSource"]


def point(column, row):
    return (matrix[0] * column + matrix[2] * row + matrix[4], matrix[1] * column + matrix[3] * row + matrix[5])


if (PACK / "write_ahead_request.json").exists():
    raise RuntimeError("Sent pack is immutable")
PACK.mkdir(parents=True, exist_ok=True)
mask = Image.new("RGB", tuple(geometry["sourceSize"]), "black")
draw = ImageDraw.Draw(mask)
draw.polygon([point(-.3, -.3), point(7.3, -.3), point(7.3, 10.3), point(-.3, 10.3)], fill="white")
mask.save(PACK / "repair-region-mask.png")
prompt = (
    "EDIT the first image, do not invent a different composition. The second image is its frozen "
    "geometry guide and the third is the repair-region mask: white is the game board that MUST be "
    "corrected, black is existing scenery to preserve. Keep original high-quality natural realistic "
    "rendering, lighting, camera and Stone Age materials. Critical defect: the riverbank cliffs and "
    "rocks obstruct legal ground and figures. REMOVE every raised cliff, large boulder and tree from "
    "all green guide cells. Replace with FLAT DRY WALKABLE DIRT AND SHORT GRASS, seamlessly continuous "
    "to neighboring green cells. The dry green ground must go ALL THE WAY to the blue river's exact "
    "edges. No inset cliff escarpments or slippery slopes on that ground. The river can be shallow "
    "with low pebbly banks; its narrow blue guide footprint alone is impassable. White line envelopes "
    "on the guide must be clear of scenery and cliffs. The two bridges are overlong: replace them "
    "with simple flat primitive timber footbridges whose DECK outlines are EXACTLY the tan guide "
    "parallelograms, with no additional stone bridge piers or abutments beyond them. They need no "
    "railings. Dry paths reach each bridge end with no ledge/drop. The guide's brown cells may have "
    "rocks but they may not intrude on green cells. River and deck at source1376x768: river edges "
    "x=501..578,y=74..62 at row0; x=771..848,y=534..522 at row10. Bridge1 corners "
    "(565.45,219.6),(680.95,201.6),(702.55,238.4),(587.05,256.4). Bridge2 corners "
    "(673.45,403.6),(788.95,385.6),(810.55,422.4),(695.05,440.4). Scale coordinates by four "
    "for the full native 5504x3072 image. No grid, colors, text, masks, symbols, figures, UI or "
    "baked figure shadows in output. Ground must be open first, decorative cliffs remain outside "
    "the entire playable board. No whole-image blur. One full 4K16:9 image, no collage."
)
paths = [SOURCE / "native-1.png", SOURCE / "geometry-guide.png", PACK / "repair-region-mask.png"]
parts = [{"text": prompt}]
manifest = []
for path in paths:
    raw = path.read_bytes()
    parts.append({"inlineData": {"mimeType": "image/png", "data": base64.b64encode(raw).decode()}})
    manifest.append({"path": path.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(raw).hexdigest(), "size": list(Image.open(path).size)})
wire = json.dumps({"contents": [{"role": "user", "parts": parts}], "generationConfig": {"responseModalities": ["IMAGE"], "candidateCount": 1, "imageConfig": {"aspectRatio": "16:9", "imageSize": "4K"}}}, separators=(",", ":")).encode()
(PACK / "prepared-wire.json").write_bytes(wire)
metadata = {"id": "tactical-stone-ground-edit-v2", "attemptId": "professional-tactical-stone-ground-edit-v2-a1", "owner": "ENVIRONMENT", "resolution": "4K", "inputImages": 3, "promptChars": len(prompt), "reservationUSD": .4, "wireBodySHA256": hashlib.sha256(wire).hexdigest(), "contractSHA256": hashlib.sha256(CONTRACT.read_bytes()).hexdigest(), "inputs": manifest, "status": "PREPARED_NOT_SENT", "visualAcceptance": "NOT_TESTED", "materialDifference": "Registered local-region native edit; explicit flat legal ground and shortened primitive bridge decks, no defective medieval prior or UI mock conditioning."}
(PACK / "prepared.json").write_text(json.dumps(metadata, indent=2))
print(json.dumps({"status": metadata["status"], "pack": str(PACK), "reservationUSD": .4}))
