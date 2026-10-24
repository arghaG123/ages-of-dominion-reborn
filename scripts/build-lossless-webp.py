"""Generate build-only WebP derivatives; never write in the original asset tree."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from PIL import Image
import argparse
import hashlib
import io
import json

parser = argparse.ArgumentParser()
parser.add_argument('--root', required=True)
parser.add_argument('--dist', required=True)
parser.add_argument('--inputs', required=True)
parser.add_argument('--workers', type=int, default=4)
parser.add_argument('--resume', action='store_true', help='Reuse only previously pixel-verified output whose source/output hashes still match')
args = parser.parse_args()
root, dist = Path(args.root).resolve(), Path(args.dist).resolve()
assert dist == root / 'dist', 'Only the generated dist directory is writable'
inputs = json.loads(Path(args.inputs).read_text())
previous = {}
if args.resume and (dist / 'asset-encoding.json').is_file():
    previous = {row['source']: row for row in json.loads((dist / 'asset-encoding.json').read_text())['assets']}

def sha(data):
    return hashlib.sha256(data).hexdigest()

def convert(relative):
    source = (root / relative).resolve()
    assert source.is_relative_to(root / 'assets')
    original = source.read_bytes()
    cached = previous.get(relative)
    if cached and cached['sourceSha256'] == sha(original) and (not cached['converted'] or cached.get('rgbaExact') is True):
        built = (dist / cached['file']).resolve()
        if built.is_relative_to(dist / 'assets') and built.is_file() and sha(built.read_bytes()) == cached['sha256']:
            return {**cached, 'reusedVerifiedEncoding': True}
    output, data = relative, original
    result = {'source': relative, 'sourceBytes': len(original), 'sourceSha256': sha(original), 'converted': False}
    if source.suffix.lower() == '.png':
        with Image.open(io.BytesIO(original)) as image:
            result['dimensions'] = list(image.size)
            # Do not flatten animation, reduce bit depth, or change non-ICC gamma handling.
            supported = image.mode in {'RGB', 'RGBA', 'P', 'L', 'LA'} and getattr(image, 'n_frames', 1) == 1
            custom_color = ('gamma' in image.info or 'chromaticity' in image.info) and not image.info.get('icc_profile')
            if supported and not custom_color:
                rgba = image.convert('RGBA')
                buffer = io.BytesIO()
                metadata = {key: image.info[key] for key in ['icc_profile', 'exif'] if image.info.get(key)}
                rgba.save(buffer, format='WEBP', lossless=True, quality=100, method=4, exact=True, **metadata)
                candidate = buffer.getvalue()
                with Image.open(io.BytesIO(candidate)) as decoded:
                    assert decoded.size == image.size, relative
                    assert decoded.convert('RGBA').tobytes() == rgba.tobytes(), f'RGBA mismatch: {relative}'
                    assert decoded.info.get('icc_profile') == image.info.get('icc_profile'), f'ICC mismatch: {relative}'
                    assert dict(decoded.getexif()) == dict(image.getexif()), f'EXIF mismatch: {relative}'
                result['rgbaExact'] = True
                result['iccExact'] = True
                result['candidateBytes'] = len(candidate)
                if len(candidate) < len(original):
                    output = str(Path(relative).with_suffix('.lossless.webp')).replace('\\', '/')
                    assert output not in inputs, f'Output collides with a source asset: {output}'
                    data = candidate
                    result['converted'] = True
            else:
                result['keptReason'] = 'Preserve original animation, depth or color interpretation'
    target = (dist / output).resolve()
    assert target.is_relative_to(dist / 'assets')
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    result.update(file=output, bytes=len(data), sha256=sha(data))
    return result

rows = []
with ThreadPoolExecutor(max_workers=max(1, min(args.workers, 4))) as pool:
    futures = [pool.submit(convert, relative) for relative in inputs]
    for future in as_completed(futures):
        rows.append(future.result())
        if len(rows) % 20 == 0 or len(rows) == len(inputs):
            print(f'Lossless assets verified: {len(rows)}/{len(inputs)}', flush=True)
rows.sort(key=lambda row: row['source'])
mapping = {row['source']: row['file'] for row in rows if row['converted']}
report = {'files': len(rows), 'converted': len(mapping), 'sourceBytes': sum(r['sourceBytes'] for r in rows),
          'assetBytes': sum(r['bytes'] for r in rows), 'assets': rows, 'mapping': mapping,
          'lossless': True, 'originalAssetsModified': False}
(dist / 'asset-encoding.json').write_text(json.dumps(report, indent=2) + '\n')
(dist / 'src/data/build-assets.json').write_text(json.dumps(mapping, indent=2) + '\n')
print(json.dumps({k: v for k, v in report.items() if k not in {'assets', 'mapping'}}), flush=True)
