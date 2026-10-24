import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.interpolate import RBFInterpolator

ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / "qa/professional-art-20261018/tactical-stone-ground-edit-v2"
SOURCE = PACK / "native-1.png"
geometry = json.loads((ROOT / "src/data/implementation-contract.json").read_text())["geometry"]["tactical"]
matrix = geometry["worldToSource"]
native = Image.open(SOURCE).convert("RGB")
pixels = np.asarray(native)
native_scale = native.width / geometry["sourceSize"][0]
targets = []
sources = []
traces = []


def point(column, row):
    return np.array((matrix[0] * column + matrix[2] * row + matrix[4], matrix[1] * column + matrix[3] * row + matrix[5]))


def control(target, source, role):
    targets.append(list(target))
    sources.append(list(source))
    traces.append({"target": list(target), "source": list(source), "role": role})


for horizontal in np.linspace(0, 1376, 10):
    for vertical in (0, 768):
        control((horizontal, vertical), (horizontal, vertical), "fixed-native-boundary")
for vertical in np.linspace(0, 768, 7)[1:-1]:
    for horizontal in (0, 1376):
        control((horizontal, vertical), (horizontal, vertical), "fixed-native-boundary")
for row in np.linspace(.1, 9.9, 26):
    if 2.3 < row < 4.7 or 6.4 < row < 9.2:
        continue
    columns = np.linspace(1.5, 5.5, 801)
    locations = np.array([point(column, row) for column in columns]) * native_scale
    samples = pixels[np.rint(locations[:, 1]).astype(int), np.rint(locations[:, 0]).astype(int)].astype(float)
    water = (samples[:, 2] - samples[:, 0] > 5) & (samples[:, 2] - samples[:, 1] > -8)
    edges = np.flatnonzero(np.diff(np.r_[False, water, False]))
    runs = [(start, end) for start, end in zip(edges[::2], edges[1::2]) if end - start > 15]
    if not runs:
        raise ValueError(f"Cannot identify actual water span at logical row {row}")
    start, end = max(runs, key=lambda pair: pair[1] - pair[0])
    for target_column, observed_column in ((3, columns[start]), (4, columns[end - 1])):
        control(point(target_column, row), point(observed_column, row), "observed-water-span")
bridge_traces = [
    [[495, 222], [746, 187], [762, 230], [519, 267]],
    [[591, 405], [896, 356], [934, 420], [620, 480]],
]
for bridge, observed in zip(geometry["bridges"], bridge_traces):
    column, row, width, height = bridge["rect"]
    corners = [point(column, row), point(column + width, row), point(column + width, row + height), point(column, row + height)]
    for target, source in zip(corners, observed):
        control(target, source, "manually-traced-native-deck-corner")
transform = RBFInterpolator(np.asarray(targets), np.asarray(sources), kernel="thin_plate_spline", smoothing=0)
cells = []
step = 24
minimum_jacobian = float("inf")
for top in range(0, native.height, step):
    bottom = min(top + step, native.height)
    for left in range(0, native.width, step):
        right = min(left + step, native.width)
        destination = np.array([[left, top], [left, bottom], [right, bottom], [right, top]], dtype=float)
        mapped = transform(destination / native_scale) * native_scale
        horizontal = (mapped[3] - mapped[0]) / (right - left)
        vertical = (mapped[1] - mapped[0]) / (bottom - top)
        jacobian = float(horizontal[0] * vertical[1] - horizontal[1] * vertical[0])
        minimum_jacobian = min(minimum_jacobian, jacobian)
        cells.append(((left, top, right, bottom), tuple(mapped.flatten())))
if minimum_jacobian <= .05:
    raise ValueError(f"Registration would fold or collapse native terrain: {minimum_jacobian}")
destination = PACK / "source-bound-registered-candidate.png"
native.transform(native.size, Image.Transform.MESH, cells, Image.Resampling.BICUBIC).save(destination)
report = {"status": "CANDIDATE_NOT_BOUND", "source": str(SOURCE.relative_to(ROOT)), "sourceSHA256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(), "output": str(destination.relative_to(ROOT)), "outputSHA256": hashlib.sha256(destination.read_bytes()).hexdigest(), "dimensions": list(native.size), "method": "Continuous inverse native-pixel thin-plate registration; no generated line stamps, pasted bridge assets, repeated ground tiles, or whole-image blur.", "minimumSampledJacobian": minimum_jacobian, "controls": traces, "visualAcceptance": "NOT_TESTED", "frozenGameGeometryChanged": False}
(PACK / "source-bound-registration.json").write_text(json.dumps(report, indent=2))
print(json.dumps({"status": report["status"], "output": str(destination), "minimumSampledJacobian": minimum_jacobian}))
