"""JavaScript ES modules/HTML/CSS/SVG project; Node 24.19.0.
Preview restoration tool: Python 3.12+, Pillow 12.3.0. No provider calls.
Rebuilds only the 256 historical comparison PNGs from retained inputs.
Usage: python restore-comparison-previews.py --verify-dir <scratch-directory>
       python restore-comparison-previews.py --restore
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
QA = ROOT / "qa/image-vertex-repair-20261009/environment"
TARGET = QA / "composites"

def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(4 * 1024 * 1024):
            h.update(block)
    return h.hexdigest()

def checked(path):
    path = Path(path).absolute()
    for parent in [path, *path.parents]:
        if parent.exists() and (parent.is_symlink() or parent.stat().st_file_attributes & 1024):
            raise RuntimeError(f"Reparse point is not permitted: {parent}")
    return path

def run():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--verify-dir", type=Path)
    group.add_argument("--restore", action="store_true")
    args = parser.parse_args()
    expected_path = Path(__file__).with_name("comparison-preview-restore-manifest.json")
    expected = json.loads(expected_path.read_text(encoding="utf-8"))
    manifest_path = checked(QA / "composites/composites_manifest.json")
    scene_path = checked(QA / "scenes.json")
    if digest(manifest_path) != expected["compositesManifestSha256"] or digest(scene_path) != expected["scenesSha256"]:
        raise RuntimeError("Retained scene/manifest bytes changed; review restoration inputs before proceeding.")
    rows = json.loads(manifest_path.read_text(encoding="utf-8"))
    scenes = {s["id"]: s for s in json.loads(scene_path.read_text(encoding="utf-8"))}
    destination = checked(TARGET if args.restore else args.verify_dir)
    if not args.restore and (destination == TARGET or ROOT in destination.parents):
        raise RuntimeError("Verification output must be outside the project.")
    destination.mkdir(parents=True, exist_ok=True)
    original = {Path(x["path"]).name: x for x in expected["pngs"]}
    grouped = {}
    for row in rows:
        grouped.setdefault(row["contributors"][0]["scene"], []).append(row)
    rendered = []
    for scene_id, scene_rows in grouped.items():
        source = checked(ROOT / scenes[scene_id]["source"]["path"])
        if digest(source) != scenes[scene_id]["source"]["sha256"]:
            raise RuntimeError(f"Source hash differs: {source}")
        with Image.open(source) as native:
            legal = native.resize((1376, 768), Image.Resampling.BOX)
        for row in scene_rows:
            width, height = row["viewport"]
            scale = min(width / 1376, height / 768)
            placed_w, placed_h = int(round(1376 * scale)), int(round(768 * scale))
            canvas = Image.new("RGB", (width, height), (12, 16, 18))
            canvas.paste(legal.resize((placed_w, placed_h), Image.Resampling.LANCZOS), ((width-placed_w)//2, (height-placed_h)//2))
            products = [(row["actual"]["path"], canvas)]
            if row.get("comparison"):
                reference_path = checked(ROOT / row["reference"]["path"])
                if digest(reference_path) != row["reference"]["sha256"]:
                    raise RuntimeError(f"Reference hash differs: {reference_path}")
                with Image.open(reference_path) as image:
                    reference = image.convert("RGB")
                ref_scale = min(width / reference.width, height / reference.height)
                ref_w, ref_h = int(round(reference.width * ref_scale)), int(round(reference.height * ref_scale))
                side = Image.new("RGB", (width*2+8, height), (12, 16, 18))
                side.paste(reference.resize((ref_w, ref_h), Image.Resampling.LANCZOS), ((width-ref_w)//2, (height-ref_h)//2))
                side.paste(canvas, (width+8, 0))
                products.append((row["comparison"], side))
            for relative, image in products:
                name = Path(relative).name
                if name not in original or Path(relative).parent.as_posix() != "qa/image-vertex-repair-20261009/environment/composites":
                    raise RuntimeError(f"Unexpected preview path: {relative}")
                output = checked(destination / name)
                if output.exists():
                    if digest(output) != original[name]["sha256"]:
                        raise RuntimeError(f"Existing output differs; refusing to replace: {output}")
                else:
                    temporary = checked(destination / (name + ".restore-tmp"))
                    if temporary.exists():
                        raise RuntimeError(f"Temporary output already exists: {temporary}")
                    image.save(temporary, format="PNG", compress_level=1)
                    if digest(temporary) != original[name]["sha256"]:
                        raise RuntimeError(f"Reproduced PNG differs: {name}; original not touched.")
                    os.replace(temporary, output)
                rendered.append({"path": relative, "sha256": digest(output), "bytes": output.stat().st_size})
            canvas.close()
        legal.close()
        print(f"Verified {scene_id}", flush=True)
    if len(rendered) != len(original) or {Path(x["path"]).name for x in rendered} != set(original):
        raise RuntimeError("Restoration did not cover the exact original file set.")
    print(json.dumps({"allExact": True, "files": len(rendered), "bytes": sum(x["bytes"] for x in rendered), "output": str(destination)}), flush=True)

if __name__ == "__main__":
    run()
