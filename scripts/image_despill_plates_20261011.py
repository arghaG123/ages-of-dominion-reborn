"""Source-preserving magenta-key despill for the live plates the game actually draws.

The 3 October live plates (attackers, creatures, troops, towers, projectile sheets) still carry
magenta key residue: ground shadows, glows and anti-aliased edges were blended with the magenta
backdrop before the matte was cut. This script re-separates those pixels with a key-unmix model
(observed = (1-k)*foreground + k*key) and writes repaired copies under the image-complete-20261011
namespace. Originals are never modified. Projectile families additionally receive one explicit
frame crop from their effect sheet, because the runtime draws a single projectile, not a sheet.

Outputs
  assets/derivatives/image-complete-20261011/actors/plates/<basename>.png
  qa/image-complete-20261011/plate-despill.json      per-ID before/after measurements
  src/data/plate-overrides-20261007.json             file/width/height/sha256 for repaired keys
"""
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / 'src/data/plate-catalog.json'
OVERRIDES = ROOT / 'src/data/plate-overrides-20261007.json'
OUT_DIR = ROOT / 'assets/derivatives/image-complete-20261011/actors/plates'
QA = ROOT / 'qa/image-complete-20261011/plate-despill.json'
GROUPS = ('attackers', 'creatures', 'troops', 'towers', 'projectiles')
# Explicit single-frame ROIs (x0, y0, x1, y1) in sheet pixels, chosen by inspection of each sheet.
PROJECTILE_ROI = {
    'arrow': lambda w, h: (w // 2, 0, w, h // 2),           # top-right bolt
    'splash': lambda w, h: (0, 0, 104, 104),                # first fireball tile
    'slow': lambda w, h: (0, 118, 132, 258),                # one frost spiral tile
    'support': lambda w, h: (w // 2, 0, w, h // 2),         # top-right blessing comet
}
MIN_FRACTION = 0.001  # below this measured magenta share the original is kept as-is


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def magenta_stats(arr):
    r, g, b, a = (arr[..., i].astype(int) for i in range(4))
    vis = a > 16
    m = np.minimum(r, b) - g
    mag = vis & (m > 60)
    n = int(vis.sum())
    return {'visible': n, 'magenta': int(mag.sum()), 'fraction': round(float(mag.sum()) / max(1, n), 5)}


def despill(arr):
    rgb = arr[..., :3].astype(np.float64)
    alpha = arr[..., 3].astype(np.float64)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    m = np.minimum(r, b) - g
    # Key colour: the dominant strongly-magenta opaque colour; sheets keep a darker key than sprites.
    strong = (alpha > 200) & (m > 120)
    candidates = (alpha > 200) & (m > 40)
    if strong.sum() > 50 and strong.sum() >= 0.2 * candidates.sum():
        key = np.median(rgb[strong], axis=0)
    elif candidates.sum() > 50:
        # Brightest 5% of the magenta candidates approximate the unshadowed key.
        cand = rgb[candidates]
        lum = cand[:, 0] + cand[:, 2]
        key = np.median(cand[lum >= np.percentile(lum, 95)], axis=0)
    else:
        key = np.array([235.0, 20.0, 235.0])
    key_m = max(40.0, min(key[0], key[2]) - key[1])
    hue_ok = np.abs(r - b) <= 0.35 * np.maximum(m, 0) + 12
    k = np.clip(m / key_m, 0, 1) * hue_ok
    k = np.where(m > 8, k, 0.0)
    keep = 1.0 - k
    fg = np.where(keep[..., None] > 0.03, (rgb - k[..., None] * key) / np.maximum(keep[..., None], 0.03), 0.0)
    fg = np.clip(fg, 0, 255)
    out = np.empty_like(arr)
    out[..., :3] = np.round(fg).astype(np.uint8)
    out[..., 3] = np.round(np.where(keep > 0.03, alpha * keep, 0.0)).astype(np.uint8)
    return out, [round(float(v), 1) for v in key]


def drop_detached_markers(arr):
    """Removes tiny detached saturated blobs (generation markers such as a stray red dot)."""
    from scipy import ndimage
    alpha = arr[..., 3] > 8
    labels, count = ndimage.label(alpha)
    if count < 2:
        return arr, 0
    sizes = ndimage.sum(alpha, labels, range(1, count + 1))
    main = int(np.argmax(sizes)) + 1
    rgb = arr[..., :3].astype(int)
    sat = rgb.max(axis=2) - rgb.min(axis=2)
    dropped = 0
    for index in range(1, count + 1):
        if index == main or sizes[index - 1] > 400:
            continue
        mask = labels == index
        if sat[mask].mean() > 120:
            arr[mask] = 0
            dropped += 1
    return arr, dropped


def trim(arr):
    a = arr[..., 3] > 8
    ys, xs = np.where(a)
    if not len(ys):
        return arr, (0, 0)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    return arr[y0:y1, x0:x1], (int(x0), int(y0))


def main():
    catalog = json.loads(CATALOG.read_text(encoding='utf-8'))
    overrides = json.loads(OVERRIDES.read_text(encoding='utf-8'))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = {'version': 'plate-despill-20261011', 'method': 'per-image key unmix: observed=(1-k)fg+k*key, k=min(r,b)-g over key chroma, hue-gated; alpha scaled by 1-k; originals untouched', 'rows': []}
    for group in GROUPS:
        for key_id, row in catalog[group].items():
            extra = overrides.get(group, {}).get(key_id, {})
            if extra.get('matteRepair') == 'despill-20261011':
                extra = {k: v for k, v in extra.items() if k not in ('file', 'width', 'height', 'sha256', 'matteRepair', 'sourceToOutput', 'sourceFile', 'sourceSHA256')}
            effective = {**row, **extra}
            src = ROOT / effective['file']
            arr = np.asarray(Image.open(src).convert('RGBA'))
            before = magenta_stats(arr)
            roi = None
            if group == 'projectiles':
                w, h = arr.shape[1], arr.shape[0]
                roi = PROJECTILE_ROI[key_id](w, h)
                arr = arr[roi[1]:roi[3], roi[0]:roi[2]]
            if before['fraction'] < MIN_FRACTION and roi is None:
                report['rows'].append({'group': group, 'id': key_id, 'file': effective['file'], 'action': 'KEEP_ORIGINAL', 'before': before})
                continue
            fixed, key_rgb = despill(arr)
            fixed, markers = drop_detached_markers(fixed)
            offset = (0, 0)
            if roi is not None:
                fixed, offset = trim(fixed)
            after = magenta_stats(fixed)
            out = OUT_DIR / Path(effective['file']).name
            Image.fromarray(fixed, 'RGBA').save(out, optimize=True)
            x0 = (roi[0] if roi else 0) + offset[0]
            y0 = (roi[1] if roi else 0) + offset[1]
            entry = overrides.setdefault(group, {}).setdefault(key_id, {})
            entry.update({
                'file': out.relative_to(ROOT).as_posix(),
                'width': int(fixed.shape[1]),
                'height': int(fixed.shape[0]),
                'sha256': sha256(out),
                'sourceFile': effective['file'],
                'sourceSHA256': sha256(src),
                'sourceToOutput': [1, 0, 0, 1, -x0, -y0],
                'matteRepair': 'despill-20261011',
            })
            report['rows'].append({'group': group, 'id': key_id, 'file': entry['file'], 'source': effective['file'], 'action': 'DESPILL_FRAME' if roi else 'DESPILL', 'keyRGB': key_rgb, 'markersDropped': markers, 'roi': list(roi) if roi else None, 'offset': [x0, y0], 'before': before, 'after': after, 'bytes': out.stat().st_size, 'sha256': entry['sha256']})
            print(group, key_id, before['fraction'], '->', after['fraction'])
    report['summary'] = {
        'rows': len(report['rows']),
        'repaired': sum(1 for r in report['rows'] if r['action'] != 'KEEP_ORIGINAL'),
        'kept': sum(1 for r in report['rows'] if r['action'] == 'KEEP_ORIGINAL'),
        'residualAbove1pct': [r['id'] for r in report['rows'] if r.get('after') and r['after']['fraction'] > 0.01],
    }
    overrides['note'] = overrides.get('note', '') + ' 11 October 2026: despill-20261011 entries replace the magenta-key live plates with source-preserving despilled copies (identity affine, same frame) and crop one frame from each projectile effect sheet.'
    OVERRIDES.write_text(json.dumps(overrides, indent=2) + '\n', encoding='utf-8')
    QA.parent.mkdir(parents=True, exist_ok=True)
    QA.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report['summary']))


if __name__ == '__main__':
    main()
