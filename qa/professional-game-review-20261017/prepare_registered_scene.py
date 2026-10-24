import base64
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / "qa/professional-art-20261018/tactical-stone-registered-v1"
CONTRACT = ROOT / "src/data/implementation-contract.json"
BASE = ROOT / "assets/derivatives/scene-edges-20261013/tactical-stone.png"
STYLE = ROOT / "design-preview/generated/landscape-mocks-20261003-efcd7a7e/images/15-tactical-action.jpg"


def prepare():
    if (PACK / "write_ahead_request.json").exists():
        raise RuntimeError("Sent pack is immutable")
    contract = json.loads(CONTRACT.read_text())
    geometry = contract["geometry"]["tactical"]
    matrix = geometry["worldToSource"]

    def point(column, row):
        return (matrix[0] * column + matrix[2] * row + matrix[4], matrix[1] * column + matrix[3] * row + matrix[5])

    def polygon(column, row, width=1, height=1):
        return [point(column, row), point(column + width, row), point(column + width, row + height), point(column, row + height)]

    guide = Image.new("RGB", tuple(geometry["sourceSize"]), "#756951")
    draw = ImageDraw.Draw(guide)
    draw.polygon([point(3, -4), point(4, -4), point(4, 16), point(3, 16)], fill="#227eaa")
    for column in range(geometry["cols"]):
        for row in range(geometry["rows"]):
            if column != 3:
                draw.polygon(polygon(column, row), fill="#89965d", outline="#a4af7b")
    for bridge in geometry["bridges"]:
        draw.polygon(polygon(*bridge["rect"]), fill="#d8b16b", outline="#ffe3a4", width=2)
    for column, row in geometry.get("obstacles", []):
        draw.polygon(polygon(column, row), fill="#594a43")
    for name, anchor in geometry["anchors"].items():
        horizontal, vertical = point(*anchor)
        draw.ellipse((horizontal - 13, vertical - 9, horizontal + 13, vertical + 9), outline="#ffffff", width=2)
        draw.line((horizontal, vertical, horizontal, vertical - 60), fill="#ffffff", width=2)
    PACK.mkdir(parents=True, exist_ok=True)
    guide_path = PACK / "geometry-guide.png"
    guide.save(guide_path)
    prompt = (
        "Create one finished realistic/semi-realistic Stone Age tactical battlefield background, "
        "wide 16:9, production game art with sharp natural ground texture and believable depth. "
        "INPUT ORDER: first image is the STRICT geometry guide, second is the defective prior terrain "
        "for materials only, third is an approved game-screen mock for overall rendering quality only. "
        "The guide determines the camera and exact physical layout. Do NOT copy the prior terrain's "
        "river or bridges: they are misplaced. Green guide tiles are dry continuous walkable ground; "
        "the narrow blue diagonal strip is the river, tan parallelograms are two flat usable crossings. "
        "Reconstruct the scenery at precisely these image-space coordinates. At source 1376x768 the "
        "river top at logical row0 runs from (501,74) to (578,62), and bottom at row10 from "
        "(771,534) to (848,522). Extend it naturally offscreen in the SAME direction. Bridge 1 "
        "corners (565.45,219.6),(680.95,201.6),(702.55,238.4),(587.05,256.4); bridge 2 "
        "corners (673.45,403.6),(788.95,385.6),(810.55,422.4),(695.05,440.4). Use low, "
        "flat rough wooden or stone-slab prehistoric crossings, NOT high arched medieval bridges. "
        "Both ends must touch dry accessible banks at those exact corners. All green regions remain "
        "dry, open and unobstructed, including white foot-anchor locations and the empty 60px vertical "
        "figure envelopes above them. Decorative rocks and trees ONLY outside the board perimeter "
        "or inside brown blocked corner tiles. Keep useful foreground and distant terrain natural, "
        "no town, no castle, no figures or baked shadows for figures. Warm sun from upper left, "
        "naturally shaded cliff edges, coherent realistic materials. REMOVE all guide colours, grid "
        "lines, marks, white anchor lines, text, labels, UI, logos and borders in the finished image. "
        "No blur, diagram stamping, oversized formations or separate pasted wall pieces. Geometry "
        "is more important than decorative fidelity. Output one full 4K image, no collage."
    )
    inputs = [guide_path, BASE, STYLE]
    parts = [{"text": prompt}]
    manifest = []
    for path in inputs:
        raw = path.read_bytes()
        parts.append({"inlineData": {"mimeType": "image/jpeg" if path.suffix == ".jpg" else "image/png", "data": base64.b64encode(raw).decode()}})
        manifest.append({"path": path.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(raw).hexdigest(), "size": list(Image.open(path).size)})
    body = {"contents": [{"role": "user", "parts": parts}], "generationConfig": {"responseModalities": ["IMAGE"], "candidateCount": 1, "imageConfig": {"aspectRatio": "16:9", "imageSize": "4K"}}}
    wire = json.dumps(body, separators=(",", ":")).encode()
    (PACK / "prepared-wire.json").write_bytes(wire)
    meta = {"id": "tactical-stone-registered-v1", "attemptId": "professional-tactical-stone-registered-v1-a1", "owner": "ENVIRONMENT", "resolution": "4K", "inputImages": len(inputs), "promptChars": len(prompt), "reservationUSD": .4, "wireBodySHA256": hashlib.sha256(wire).hexdigest(), "contractSHA256": hashlib.sha256(CONTRACT.read_bytes()).hexdigest(), "inputs": manifest, "status": "PREPARED_NOT_SENT", "visualAcceptance": "NOT_TESTED"}
    (PACK / "prepared.json").write_text(json.dumps(meta, indent=2))
    print(json.dumps({"pack": str(PACK), "status": meta["status"], "inputs": manifest, "wireBodySHA256": meta["wireBodySHA256"]}))


if __name__ == "__main__":
    prepare()
