"""Verifies the 11 October web/APK package: dist == www == APK bytes for every expected current file,
APK CRC, application id, zero declared permissions, no remote URLs. Writes
qa/code-image-complete-20261011/package-check.json. Read-only apart from that report."""
import hashlib, json, re, struct, sys, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APK = ROOT / 'android/app/build/outputs/apk/release/ages-of-dominion-reborn-preview-release-unsigned-20261011.apk'
DIST = ROOT / 'dist'
WWW = ROOT / 'android/app/src/main/assets/www'
OUT = ROOT / 'qa/code-image-complete-20261011/package-check.json'
load = lambda rel: json.loads((ROOT / rel).read_text(encoding='utf-8-sig'))
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def closure():
    files = set()
    def visit(v):
        if isinstance(v, dict):
            for k, x in v.items():
                if isinstance(x, str) and (k in ['file', 'terrain', 'uiFile', 'sourceFile', 'displayFile'] or k.endswith('File')): files.add(x)
                else: visit(x)
        elif isinstance(v, list):
            for x in v: visit(x)
    for name in ['reviewed-source-selection', 'stone-scene', 'actor-atlas', 'plate-catalog', 'age-buildings', 'portrait-cards', 'plate-overrides-20261007', 'gear-icons-20261007', 'hero-bodies-20261011']:
        visit(load('src/data/' + name + '.json'))
    for r in load('src/data/consumer-catalog-20261007.json').get('assets', []):
        if r.get('gates', {}).get('runtime') == 'PASS' and isinstance(r.get('outputPath'), str): files.add(r['outputPath'])
    mode = load('src/data/mode-scenes.json')
    for name in ['adventure', 'tactical', 'defense']: files.update(mode.get(name, []))
    expected = ['index.html'] + [p.relative_to(ROOT).as_posix() for p in (ROOT / 'src').rglob('*') if p.is_file()] + sorted(files)
    return expected


def manifest_strings(blob):
    """Extracts the UTF-16 string pool from a binary AndroidManifest.xml."""
    if len(blob) < 8 or struct.unpack('<H', blob[:2])[0] != 0x0003: return []
    pool_off = 8
    if struct.unpack('<H', blob[pool_off:pool_off + 2])[0] != 0x0001: return []
    chunk_size, count, _, flags, strings_start = struct.unpack('<IIIII', blob[pool_off + 4:pool_off + 24])
    utf8 = bool(flags & (1 << 8))
    offsets = struct.unpack('<%dI' % count, blob[pool_off + 28:pool_off + 28 + 4 * count])
    out = []
    base = pool_off + strings_start
    for off in offsets:
        p = base + off
        if utf8:
            n = blob[p]; p += 1
            if n & 0x80: p += 1
            n = blob[p]; p += 1
            if n & 0x80: n = ((n & 0x7f) << 8) | blob[p]; p += 1
            out.append(blob[p:p + n].decode('utf-8', 'replace'))
        else:
            n = struct.unpack('<H', blob[p:p + 2])[0]; p += 2
            if n & 0x8000: n = ((n & 0x7fff) << 16) | struct.unpack('<H', blob[p:p + 2])[0]; p += 2
            out.append(blob[p:p + 2 * n].decode('utf-16-le', 'replace'))
    return out


expected = closure()
report = {'version': 'package-check-20261011', 'apk': APK.relative_to(ROOT).as_posix(), 'expectedFiles': len(expected)}
report['missingCurrentFiles'] = [x for x in expected if not (ROOT / x).is_file()]
network = []
for name in ['index.html'] + [p.relative_to(ROOT).as_posix() for p in (ROOT / 'src').rglob('*') if p.is_file() and p.suffix in ['.html', '.js', '.css', '.json', '.mjs']]:
    for url in re.findall(r'https?://[^\s"\x27`)<>]+', (ROOT / name).read_text(encoding='utf-8-sig')):
        if url != 'http://www.w3.org/2000/svg': network.append({'path': name, 'url': url})
report['networkReferences'] = network
dist_diff = [x for x in expected if not (DIST / x).is_file() or sha(DIST / x) != sha(ROOT / x)]
www_diff = [x for x in expected if not (WWW / x).is_file() or sha(WWW / x) != sha(ROOT / x)]
report['distDiffers'] = dist_diff
report['wwwDiffers'] = www_diff
report['distFiles'] = sum(1 for p in DIST.rglob('*') if p.is_file())
report['wwwFiles'] = sum(1 for p in WWW.rglob('*') if p.is_file())
report['apkPresent'] = APK.is_file()
if APK.is_file():
    report['apkBytes'] = APK.stat().st_size
    report['apkSHA256'] = sha(APK)
    with zipfile.ZipFile(APK) as z:
        names = set(z.namelist())
        absent, different = [], []
        for name in expected:
            entry = 'assets/www/' + name
            if entry not in names: absent.append(name)
            elif hashlib.sha256(z.read(entry)).hexdigest() != sha(ROOT / name): different.append(name)
        report['apkMissingCurrentFiles'] = absent
        report['apkDifferentCurrentFiles'] = different
        report['apkCrcBadEntry'] = z.testzip()
        report['apkWwwEntries'] = sum(1 for n in names if n.startswith('assets/www/') and not n.endswith('/'))
        strings = manifest_strings(z.read('AndroidManifest.xml'))
        ids = [s for s in strings if s.startswith('com.agesofdominion.') and not s.endswith('Activity')]
        report['manifestPackageStrings'] = ids
        report['manifestApplicationId'] = 'com.agesofdominion.game.reborn.preview' if 'com.agesofdominion.game.reborn.preview' in ids else (ids[0] if ids else None)
        report['manifestPermissions'] = [s for s in strings if s.startswith('android.permission.')]
        report['manifestMentionsInternet'] = any('INTERNET' in s for s in strings)
        report['signed'] = any(n.startswith('META-INF/') and n.endswith(('.RSA', '.DSA', '.EC')) for n in names)
report['pass'] = bool(APK.is_file() and not report['missingCurrentFiles'] and not network and not dist_diff and not www_diff
                      and not report.get('apkMissingCurrentFiles') and not report.get('apkDifferentCurrentFiles')
                      and report.get('apkCrcBadEntry') is None and report.get('manifestApplicationId') == 'com.agesofdominion.game.reborn.preview'
                      and report.get('manifestPermissions') == [] and not report.get('manifestMentionsInternet'))
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print(json.dumps({k: v for k, v in report.items() if not isinstance(v, list) or len(v) < 6}, indent=2))
sys.exit(0 if report['pass'] else 1)
