"""Retire completed raw payloads using an EXISTING ZIP and a verified loose backup.

Creates no ZIP, contacts no provider and changes no provider control files.
Run prepare first, inspect its index, then retire. Restore rehydrates exact bytes.
"""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[2]
META = ROOT / 'docs/asset-provenance'
INDEX = META / 'raw-response-archive-index.json'
BACKUP = ROOT.parent / 'ages-of-dominion-reborn-cleanup-backup-2026-10-04/raw-generation-responses'
EXTERNAL = Path('E:/Ages-of-Dominion-Reborn-Migration-2026-10-04/ages-of-dominion-reborn-worktree-2026-10-04-handoff-final6.zip')


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.pending')
    temporary.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    os.replace(temporary, path)


def response_paths():
    return sorted([
        *ROOT.glob('assets/high-res/**/response.json'),
        *ROOT.glob('assets/production/**/predictions.jsonl'),
        *ROOT.glob('design-preview/generated/**/predictions.jsonl'),
    ])


def image_catalog():
    images = {}
    for directory in ('assets', 'design-preview', 'docs/plan/references', 'qa'):
        for path in (ROOT / directory).rglob('*'):
            if path.is_file() and path.suffix.lower() in ('.png', '.jpg', '.jpeg', '.webp'):
                images.setdefault(digest(path), path.relative_to(ROOT).as_posix())
    return images


def compact(value, images, refs, opaque, source_path, record_number, pointer=''):
    if isinstance(value, list):
        return [compact(child, images, refs, opaque, source_path, record_number, pointer + '/' + str(number))
                for number, child in enumerate(value)]
    if not isinstance(value, dict):
        return value
    mime = value.get('mimeType', value.get('mime_type', ''))
    result = {}
    for key, child in value.items():
        child_pointer = pointer + '/' + key.replace('~', '~0').replace('/', '~1')
        if key == 'data' and isinstance(child, str) and str(mime).startswith('image/'):
            blob = base64.b64decode(child, validate=True)
            # Preserve exact base64 representation, not only approximate decoded content.
            if base64.b64encode(blob).decode('ascii') != child:
                raise ValueError('Noncanonical base64: preserve raw instead of silently normalizing')
            sha = hashlib.sha256(blob).hexdigest()
            if sha not in images:
                extension = {'image/png': '.png', 'image/jpeg': '.jpg', 'image/webp': '.webp'}.get(mime)
                if not extension:
                    raise ValueError(f'Unknown image MIME {mime}')
                target = ROOT / 'assets/provenance/extracted-response-images' / (sha + extension)
                target.parent.mkdir(parents=True, exist_ok=True)
                if target.exists() and digest(target) != sha:
                    raise ValueError('Unlike extracted-image destination')
                if not target.exists():
                    target.write_bytes(blob)
                from PIL import Image
                with Image.open(target) as image:
                    image.verify()
                images[sha] = target.relative_to(ROOT).as_posix()
            if digest(ROOT / images[sha]) != sha:
                raise ValueError('Retained image changed')
            ref = {'path': images[sha], 'sha256': sha, 'bytes': len(blob), 'mimeType': mime}
            refs.append(ref)
            result[key] = {'_archived_image_reference': ref}
        elif key == 'thoughtSignature' and isinstance(child, str) and len(child) > 4096:
            ref = {'originalPath': source_path, 'record': record_number,
                   'jsonPointer': child_pointer, 'characters': len(child),
                   'utf8SHA256': hashlib.sha256(child.encode('utf-8')).hexdigest()}
            opaque.append(ref)
            result[key] = {'_archived_exact_text_reference': ref}
        else:
            result[key] = compact(child, images, refs, opaque, source_path, record_number, child_pointer)
    return result


def expand(value, original):
    if isinstance(value, list):
        return [expand(child, original) for child in value]
    if not isinstance(value, dict):
        return value
    if set(value) == {'_archived_image_reference'}:
        ref = value['_archived_image_reference']
        blob = (ROOT / ref['path']).read_bytes()
        if hashlib.sha256(blob).hexdigest() != ref['sha256']:
            raise ValueError('Image reference failed reconstruction')
        return base64.b64encode(blob).decode('ascii')
    if set(value) == {'_archived_exact_text_reference'}:
        ref = value['_archived_exact_text_reference']
        text = original
        for component in ref['jsonPointer'].split('/')[1:]:
            component = component.replace('~1', '/').replace('~0', '~')
            text = text[int(component)] if isinstance(text, list) else text[component]
        if len(text) != ref['characters'] or hashlib.sha256(text.encode('utf-8')).hexdigest() != ref['utf8SHA256']:
            raise ValueError('Opaque signature reference mismatch')
        return text
    return {key: expand(child, original) for key, child in value.items()}


def prepare():
    if INDEX.exists():
        raise RuntimeError('Index exists; inspect it or run retire/verify/restore. Never overwrite history.')
    sources = response_paths()
    images = image_catalog()
    records = []
    document = {'version': 1, 'status': 'PREPARING', 'externalArchive': str(EXTERNAL),
                'independentBackupRoot': str(BACKUP), 'records': records,
                'policy': 'All non-image fields preserved; exact raw bytes retained in two verified copies.'}
    save(INDEX, document)
    with zipfile.ZipFile(EXTERNAL) as archive:
        for number, source in enumerate(sources, 1):
            relative = source.relative_to(ROOT).as_posix()
            source_sha = digest(source)
            info = archive.getinfo(relative)
            if info.file_size != source.stat().st_size:
                raise ValueError(f'External archive size mismatch: {relative}')
            backup = BACKUP / relative
            backup.parent.mkdir(parents=True, exist_ok=True)
            if not backup.exists():
                pending = backup.with_name(backup.name + '.pending')
                with archive.open(info) as stream, pending.open('wb') as output:
                    shutil.copyfileobj(stream, output, 1024 * 1024)
                if digest(pending) != source_sha:
                    raise ValueError(f'Clean external restore SHA mismatch: {relative}')
                os.replace(pending, backup)
            else:
                with archive.open(info) as stream:
                    external_sha = hashlib.file_digest(stream, 'sha256').hexdigest()
                if external_sha != source_sha or digest(backup) != source_sha:
                    raise ValueError(f'Existing backup mismatch: {relative}')
            refs, opaque = [], []
            target = META / 'raw-response-metadata' / (relative + '.metadata')
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                raise ValueError(f'Metadata already exists: {target}')
            with source.open('r', encoding='utf-8-sig') as stream, target.open('w', encoding='utf-8') as output:
                values = (json.loads(line) for line in stream if line.strip()) if source.suffix == '.jsonl' else [json.load(stream)]
                count = 0
                for original in values:
                    reduced = compact(original, images, refs, opaque, relative, count)
                    if expand(reduced, original) != original:
                        raise ValueError('Semantic reconstruction lost a field')
                    output.write(json.dumps(reduced, ensure_ascii=False, separators=(',', ':')) + '\n')
                    count += 1
            if digest(source) != source_sha:
                raise ValueError('Source changed during preparation')
            records.append({'originalPath': relative, 'sha256': source_sha,
                            'bytes': source.stat().st_size, 'externalZipEntry': relative,
                            'independentBackupRelativePath': relative,
                            'metadataPath': target.relative_to(ROOT).as_posix(),
                            'metadataSHA256': digest(target), 'recordCount': count,
                            'imageReferences': refs, 'opaqueFieldReferences': opaque,
                            'status': 'VERIFIED_READY_FOR_RETIREMENT'})
            save(INDEX, document)
            print(f'Prepared {number}/{len(sources)}: {relative}', flush=True)
    document['status'] = 'ALL_RAW_AND_IMAGE_REFERENCES_VERIFIED'
    document['originalBytes'] = sum(record['bytes'] for record in records)
    document['metadataBytes'] = sum((ROOT / record['metadataPath']).stat().st_size for record in records)
    save(INDEX, document)
    shutil.copy2(INDEX, BACKUP / 'raw-response-archive-index.json')
    print(json.dumps({key: document[key] for key in ('status', 'originalBytes', 'metadataBytes')}), flush=True)


def verify_record(record):
    if digest(BACKUP / record['independentBackupRelativePath']) != record['sha256']:
        raise ValueError('Backup mismatch')
    if digest(ROOT / record['metadataPath']) != record['metadataSHA256']:
        raise ValueError('Metadata mismatch')
    for ref in record['imageReferences']:
        path = ROOT / ref['path']
        if path.stat().st_size != ref['bytes'] or digest(path) != ref['sha256']:
            raise ValueError('Image reference mismatch')


def recompact():
    """Shrink this script's own metadata while preserving opaque fields by exact archive reference."""
    document = json.loads(INDEX.read_text(encoding='utf-8'))
    if document['status'] != 'ALL_RAW_AND_IMAGE_REFERENCES_VERIFIED':
        raise ValueError('Recompaction requires fully prepared, unretired sources')
    images = image_catalog()
    for number, record in enumerate(document['records'], 1):
        verify_record(record)
        source = ROOT / record['originalPath']
        if digest(source) != record['sha256']:
            raise ValueError('Source changed before recompaction')
        target = ROOT / record['metadataPath']
        pending = target.with_name(target.name + '.pending')
        refs, opaque = [], []
        with source.open('r', encoding='utf-8-sig') as stream, pending.open('w', encoding='utf-8') as output:
            values = (json.loads(line) for line in stream if line.strip()) if source.suffix == '.jsonl' else [json.load(stream)]
            count = 0
            for original in values:
                reduced = compact(original, images, refs, opaque, record['originalPath'], count)
                if expand(reduced, original) != original:
                    raise ValueError('Recompaction semantic reconstruction mismatch')
                output.write(json.dumps(reduced, ensure_ascii=False, separators=(',', ':')) + '\n')
                count += 1
        os.replace(pending, target)
        record.update(metadataSHA256=digest(target), imageReferences=refs,
                      opaqueFieldReferences=opaque, recordCount=count)
        save(INDEX, document)
        if number % 20 == 0:
            print(f'Recompacted {number}/{len(document["records"])}', flush=True)
    document['metadataBytes'] = sum((ROOT / row['metadataPath']).stat().st_size for row in document['records'])
    save(INDEX, document)
    shutil.copy2(INDEX, BACKUP / 'raw-response-archive-index.json')
    print(f"Metadata now {document['metadataBytes']} bytes", flush=True)


def retire():
    document = json.loads(INDEX.read_text(encoding='utf-8'))
    if document['status'] != 'ALL_RAW_AND_IMAGE_REFERENCES_VERIFIED':
        raise ValueError('Preparation incomplete')
    archive_root = EXTERNAL.parent
    with zipfile.ZipFile(EXTERNAL) as archive:
        # Complete validation precedes the first removal.
        for record in document['records']:
            verify_record(record)
            with archive.open(record['externalZipEntry']) as stream:
                if hashlib.file_digest(stream, 'sha256').hexdigest() != record['sha256']:
                    raise ValueError('External archive mismatch before retirement')
            source = (ROOT / record['originalPath']).resolve(strict=True)
            source.relative_to(ROOT.resolve())
            if source.name not in ('response.json', 'predictions.jsonl') or digest(source) != record['sha256']:
                raise ValueError('Unexpected or changed removal target')
    journal = META / 'raw-response-retirement-journal.jsonl'
    with journal.open('a', encoding='utf-8') as output:
        for record in document['records']:
            source = (ROOT / record['originalPath']).resolve(strict=True)
            source.relative_to(ROOT.resolve())
            if digest(source) != record['sha256']:
                raise ValueError('Source changed before removal')
            source.unlink()
            record['status'] = 'ARCHIVED_WORKING_COPY_REMOVED'
            output.write(json.dumps({'path': record['originalPath'], 'sha256': record['sha256'], 'bytes': record['bytes']}) + '\n')
            output.flush()
    document['status'] = 'RAW_WORKING_COPIES_RETIRED'
    save(INDEX, document)
    shutil.copy2(INDEX, BACKUP / 'raw-response-archive-index.json')
    shutil.copy2(INDEX, archive_root / 'raw-response-archive-index.json')
    print(f"Retired {len(document['records'])} files / {document['originalBytes']} bytes", flush=True)


def restore(selected):
    document = json.loads(INDEX.read_text(encoding='utf-8'))
    records = [record for record in document['records'] if selected == 'all' or record['originalPath'] == selected]
    if not records:
        raise ValueError('No matching archived path')
    for record in records:
        target = (ROOT / record['originalPath']).resolve()
        target.relative_to(ROOT.resolve())
        if target.exists():
            if digest(target) != record['sha256']:
                raise ValueError('Refusing to overwrite an unlike restored target')
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        source = BACKUP / record['independentBackupRelativePath']
        if source.exists():
            if digest(source) != record['sha256']:
                raise ValueError('Backup hash mismatch')
            shutil.copy2(source, target)
        else:
            with zipfile.ZipFile(EXTERNAL) as archive, archive.open(record['externalZipEntry']) as input_stream, target.open('xb') as output:
                shutil.copyfileobj(input_stream, output)
        if digest(target) != record['sha256']:
            raise ValueError('Restored raw hash mismatch')
        print('Restored ' + record['originalPath'], flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=('prepare', 'recompact', 'retire', 'verify', 'restore'))
    parser.add_argument('--path', default='all')
    parser.add_argument('--backup-root', type=Path)
    parser.add_argument('--external-zip', type=Path)
    args = parser.parse_args()
    if args.backup_root:
        BACKUP = args.backup_root.resolve()
    if args.external_zip:
        EXTERNAL = args.external_zip.resolve()
    if args.action == 'prepare':
        prepare()
    elif args.action == 'recompact':
        recompact()
    elif args.action == 'retire':
        retire()
    elif args.action == 'restore':
        restore(args.path)
    else:
        document = json.loads(INDEX.read_text(encoding='utf-8'))
        for record in document['records']:
            verify_record(record)
        print(f"PASS: {len(document['records'])} backups, metadata records and all image references")
