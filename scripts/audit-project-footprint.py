"""Read-only audit and exact proposed cleanup manifest. Never deletes files."""
from pathlib import Path
import collections
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/maintenance/footprint-20261024'
OUT.mkdir(parents=True, exist_ok=True)
deps = json.loads(subprocess.check_output(['node', str(ROOT / 'scripts/asset-dependencies.mjs')], cwd=ROOT))
keep = set(deps['files'])
references = collections.defaultdict(list)
pattern = re.compile(r'(?:assets|qa)/[^\s\"\'`<>]+')

for folder in ['src', 'tests', 'scripts', 'design-preview']:
    for p in (ROOT / folder).rglob('*'):
        if p.is_file() and p.suffix.lower() in {'.json', '.js', '.mjs', '.py', '.html', '.css'} and p.stat().st_size < 8_000_000:
            text = p.read_text(encoding='utf-8', errors='replace').replace('\\\\', '/').replace('\\', '/')
            for value in pattern.findall(text):
                value = value.rstrip('.,;)')
                if (ROOT / value).is_file() and (value.startswith('assets/') or folder in {'src', 'tests'}):
                    keep.add(value)
                    references[value].append(p.relative_to(ROOT).as_posix())

# Retain the actual screenshot files cited by the current independent dossier and
# latest repair reports, even when those captures live under an older run folder.
for folder in ['qa/independent-status-20261022', 'qa/priority-repair-20261023', 'qa/game-completion-20261023']:
    for p in (ROOT / folder).rglob('*'):
        if p.is_file() and p.suffix.lower() in {'.json', '.md', '.html'} and p.stat().st_size < 8_000_000:
            for value in pattern.findall(p.read_text(encoding='utf-8', errors='replace').replace('\\', '/')):
                value = value.rstrip('.,;)')
                if (ROOT / value).is_file():
                    keep.add(value)

media = {'.png', '.jpg', '.jpeg', '.webp', '.gif', '.avif', '.bmp', '.mp4', '.webm'}
inventory = []
remove = []
retained = []
folders = collections.Counter()
for top in ROOT.iterdir():
    paths = top.rglob('*') if top.is_dir() else [top]
    for p in paths:
        if not p.is_file():
            continue
        rel = p.relative_to(ROOT).as_posix()
        size = p.stat().st_size
        folders[top.name] += size
        reason = None
        # Owner chose "Keep assets; remove only listed QA captures" on 24 October.
        # Keep the dependency inventory for packaging, but never propose asset deletion.
        if rel.startswith('qa/') and p.suffix.lower() in media:
            protected = (rel in keep or '/guides/' in rel or rel.startswith((
                'qa/independent-status-20261022/', 'qa/game-completion-20261023/',
                'qa/priority-repair-20261023/', 'qa/plan-semantic-audit-',
            )))
            if not protected:
                reason = 'Regenerable QA capture; retain structured findings and current independent/23 October evidence'
        if reason:
            remove.append({'path': rel, 'bytes': size, 'sha256': hashlib.file_digest(p.open('rb'), 'sha256').hexdigest(), 'reason': reason})
        elif rel.startswith('assets/'):
            retained.append({'path': rel, 'bytes': size, 'sha256': hashlib.file_digest(p.open('rb'), 'sha256').hexdigest(), 'consumers': references.get(rel, deps['consumers'].get(rel, []))})

result = {'root': str(ROOT), 'beforeBytes': sum(folders.values()), 'beforeFolders': dict(folders),
          'removeBytes': sum(x['bytes'] for x in remove), 'removeFiles': len(remove), 'remove': remove,
          'retainedAssetBytes': sum(x['bytes'] for x in retained), 'retainedAssets': retained,
          'scope': 'Owner-requested sub-8GB project; keep ALL assets, propose regenerable QA captures only. No APKs or Git objects in this manifest.'}
(OUT / 'current-cleanup-proposal.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({k: v for k, v in result.items() if k not in {'remove', 'retainedAssets'}}, indent=2))
