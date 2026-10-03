"""Join verifier reviews to collected files by (batch, id, source SHA256).

Collection reports stay technical provenance. Source-content, matte, registration,
composite, runtime and owner acceptance stay separate. A hash mismatch rejects the
review instead of inheriting it.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / 'docs/plan/image-production/VERIFIER-REVIEW-20261003.json'
REGISTRY = ROOT / 'docs/plan/image-production/RECOVERY-SOURCE-REGISTRY-20261003.json'
DELIVERY = ROOT / 'assets/delivery/stone-starter-20261003/gate-ledger.json'
VISUAL = ROOT / 'qa/delivery-20261003/visual-gates.json'
VISUAL_CURRENT = ROOT / 'qa/delivery-20261003/visual-gates-current.json'
GATES = ('technical', 'sourceContent', 'matte', 'registration', 'composite', 'runtime', 'ownerAcceptance')
ALLOWED = ('PASS', 'FAIL', 'UNVERIFIED', 'NOT_APPLICABLE')
ARTWORK_SIZES = {'resource-symbol': [18], 'resource-detail': [18, 36], 'skill-emblem': [36, 64]}


def authoritative(root: Path) -> dict:
    """Fresh hashes of the geometry contract and the review policy. Matching stale strings do not count."""
    contract_path = root / 'docs/plan/IMPLEMENTATION-CONTRACT.json'
    contract = load_json(contract_path)
    camera = hashlib.sha256(json.dumps(contract['geometry']['kingdom']['worldToSource']).encode()).hexdigest()
    policy_path = root / 'docs/plan/ASSET-ACCEPTANCE-CLARIFICATION-2026-10-03.md'
    return {
        'camera': camera,
        'contract': hashlib.sha256(contract_path.read_bytes()).hexdigest(),
        'policy': hashlib.sha256(policy_path.read_bytes()).hexdigest() if policy_path.exists() else '',
    }


def required_scene_members(scene_note: dict, scene_file: str) -> dict:
    use = scene_note.get('use') or ('stone-kingdom-day1' if 'hall-only-day1' in scene_file.replace('\\', '/') else '')
    if use == 'stone-kingdom-day1':
        return {'use': use, 'constituents': {'townhall-stone', 'kingdom-terrain-stone'}, 'registrations': {'townhall-stone'}}
    return {'use': use, 'constituents': set(), 'registrations': set()}


def bind_artwork(artwork, row, policy, matches) -> dict:
    if not isinstance(artwork, dict):
        return {'status': 'UNVERIFIED', 'bound': False}
    status = artwork.get('status')
    if status != 'PASS':
        return {'status': status if status in ALLOWED else 'UNVERIFIED', 'bound': False}
    evidence = artwork.get('evidence') or []
    use = artwork.get('use')
    bound = (
        artwork.get('policyRevision') == policy
        and artwork.get('derivativeSHA256') == row.get('derivativeSHA256')
        and row.get('derivativeHashMatch') is True
        and use in ARTWORK_SIZES
        and artwork.get('sizes') == ARTWORK_SIZES[use]
        and bool(evidence)
        and all(isinstance(item, dict) and matches(item.get('file'), item.get('sha256')) for item in evidence)
    )
    if not bound:
        return {'status': 'UNVERIFIED', 'bound': False, 'reason': 'artwork verdict is not bound to policy, evidence, use and size'}
    return {**artwork, 'status': 'PASS', 'bound': True}


def published_artwork(root: Path, extra: dict):
    path = root / 'qa/recovery-executor-20261003/bound-reviews.json'
    if not path.exists():
        return None
    record = load_json(path)
    for item in record.get('assets', []):
        if item.get('batch') == extra.get('batch') and item.get('id') == extra.get('id') and item.get('sourceSHA256') == extra.get('sourceSHA256') and item.get('derivativeSHA256') == extra.get('derivativeSHA256'):
            return item.get('artworkReadyForUse')
    return None


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def _status(value, default='UNVERIFIED'):
    if value in (None, ''):
        return default
    if value is True:
        return 'PASS'
    if value is False:
        return 'FAIL'
    return str(value)


def _discover(root: Path):
    found = []
    production = root / 'assets/production'
    if not production.exists():
        return found
    for report_path in sorted(production.glob('production-*/collection-report.json')):
        report = load_json(report_path)
        for output in report.get('outputs', []):
            found.append({'batch': report['batch'], 'id': output['id'], 'sourceFile': output['file'], 'sourceSHA256': output['sha256']})
    return found


def evaluate(root: Path | None = None, review_items=None, registry_items=None, delivery=None, visual=None, file_hash=None):
    root = root or ROOT
    review = load_json(root / 'docs/plan/image-production/VERIFIER-REVIEW-20261003.json') if review_items is None else {'assets': review_items}
    registry = load_json(root / 'docs/plan/image-production/RECOVERY-SOURCE-REGISTRY-20261003.json') if registry_items is None else {'sources': registry_items}
    if delivery is None and (root / 'assets/delivery/stone-starter-20261003/gate-ledger.json').exists():
        delivery = load_json(root / 'assets/delivery/stone-starter-20261003/gate-ledger.json')
    delivery = delivery or {'assets': []}
    if visual is None and (root / 'qa/delivery-20261003/visual-gates-current.json').exists():
        visual = load_json(root / 'qa/delivery-20261003/visual-gates-current.json')
    elif visual is None and (root / 'qa/delivery-20261003/visual-gates.json').exists():
        visual = load_json(root / 'qa/delivery-20261003/visual-gates.json')
    visual = visual or {'assets': []}
    file_hash = file_hash or (lambda path: digest(root / path))

    by_key = {}
    stale = []
    rows = []
    for item in review['assets']:
        path = root / item['sourceFile']
        actual = file_hash(item['sourceFile']) if path.exists() else None
        fresh = actual == item['sourceSHA256']
        key = (item['batch'], item['id'], item['sourceSHA256'])
        if not fresh:
            stale.append({'batch': item['batch'], 'id': item['id'], 'expected': item['sourceSHA256'], 'actual': actual})
        technical = 'REJECTED_STALE_HASH' if not fresh else _status(item.get('technicalStatus'), 'UNVERIFIED')
        source = 'REJECTED_STALE_HASH' if not fresh else _status(item.get('sourceContentStatus'), 'UNVERIFIED')
        row = {
            'key': item.get('key'),
            'batch': item['batch'],
            'id': item['id'],
            'sourceFile': item['sourceFile'],
            'sourceSHA256': item['sourceSHA256'],
            'actualSHA256': actual,
            'hashMatch': fresh,
            'classification': item.get('classification') if fresh else 'REJECTED_STALE_HASH',
            'gates': {
                'technical': technical,
                'sourceContent': source,
                'matte': 'UNVERIFIED',
                'registration': 'UNVERIFIED',
                'composite': 'UNVERIFIED',
                'runtime': 'UNVERIFIED',
                'ownerAcceptance': 'REJECTED_STALE_HASH' if not fresh else _status(item.get('ownerAcceptance'), 'UNVERIFIED'),
            },
            'runtimeApproved': False,
            'ownerAccepted': False,
            'reviewSource': 'HISTORICAL',
        }
        if item.get('runtimeApproved') is True:
            row['runtimeClaim'] = 'REJECTED_SELF_APPROVAL'
            row['gates']['runtime'] = 'UNVERIFIED'
        by_key[key] = row
        rows.append(row)

    if review_items is None:
        for output in _discover(root):
            key = (output['batch'], output['id'], output['sourceSHA256'])
            if key in by_key:
                continue
            path = root / output['sourceFile']
            actual = file_hash(output['sourceFile']) if path.exists() else None
            fresh = actual == output['sourceSHA256']
            row = {
                'batch': output['batch'],
                'id': output['id'],
                'sourceFile': output['sourceFile'],
                'sourceSHA256': output['sourceSHA256'],
                'actualSHA256': actual,
                'hashMatch': fresh,
                'classification': 'UNVERIFIED' if fresh else 'REJECTED_STALE_HASH',
                'gates': {name: ('PASS' if name == 'technical' and fresh else 'UNVERIFIED') for name in GATES},
                'runtimeApproved': False,
                'ownerAccepted': False,
                'reviewSource': 'COLLECTION_ONLY',
            }
            if not fresh:
                row['gates'] = {name: 'REJECTED_STALE_HASH' for name in GATES}
                stale.append({'batch': output['batch'], 'id': output['id'], 'expected': output['sourceSHA256'], 'actual': actual})
            by_key[key] = row
            rows.append(row)

    output_stale = []

    def output_matches(path, expected):
        if not path or not expected:
            return False
        file = root / path
        if not file.exists():
            return False
        try:
            return file_hash(path) == expected
        except OSError:
            return False

    for extra in delivery.get('assets', []):
        key = (extra['batch'], extra['id'], extra['sourceSHA256'])
        row = by_key.get(key)
        if row is None or not row['hashMatch']:
            stale.append({'batch': extra['batch'], 'id': extra['id'], 'reason': 'delivery record has no fresh review row'})
            continue
        if extra.get('sourceSHA256') != row['sourceSHA256']:
            continue
        derivative_ok = output_matches(extra.get('derivative'), extra.get('derivativeSHA256'))
        row['derivative'] = extra.get('derivative')
        row['derivativeSHA256'] = extra.get('derivativeSHA256')
        row['derivativeHashMatch'] = derivative_ok
        if not derivative_ok:
            output_stale.append({'batch': extra['batch'], 'id': extra['id'], 'reason': 'missing or stale derivative', 'derivative': extra.get('derivative')})
            for gate in ('matte', 'registration', 'composite'):
                claimed = extra.get('gates', {}).get(gate, {}).get('status')
                if claimed == 'PASS':
                    row['gates'][gate] = 'REJECTED_STALE_HASH'
            continue
        for gate in ('matte', 'registration', 'composite'):
            if gate in extra.get('gates', {}):
                status = extra['gates'][gate]['status']
                if status in ALLOWED:
                    row['gates'][gate] = status
                    row.setdefault('delivery', {})[gate] = extra['gates'][gate]
        published = published_artwork(root, extra)
        row['artworkReadyForUse'] = bind_artwork(published or extra.get('artworkReadyForUse'), row, authoritative(root)['policy'], output_matches)
        # Delivery evidence cannot promote runtime or owner gates.
        row['gates']['runtime'] = 'UNVERIFIED'
        row['gates']['ownerAcceptance'] = 'UNVERIFIED'
        row['runtimeApproved'] = False
        row['ownerAccepted'] = False

    for note in visual.get('assets', []):
        key = (note['batch'], note['id'], note['sourceSHA256'])
        row = by_key.get(key)
        if row is None or not row['hashMatch']:
            continue
        bound = note.get('derivativeSHA256')
        if not bound or bound != row.get('derivativeSHA256') or not row.get('derivativeHashMatch'):
            output_stale.append({'batch': note['batch'], 'id': note['id'], 'reason': 'visual note is not bound to the current derivative hash'})
            continue
        for gate, status in note.get('gates', {}).items():
            if gate in ('runtime', 'ownerAcceptance'):
                continue
            if gate in row['gates'] and status in ALLOWED:
                automated = row['gates'][gate]
                if automated == 'FAIL' or automated == 'REJECTED_STALE_HASH':
                    continue
                row['gates'][gate] = status
                row.setdefault('visual', {})[gate] = status

    scene_note = visual.get('scene') or {}
    composite = delivery.get('composite') or {}
    scene_ok = False
    if scene_note:
        bindings = authoritative(root)
        constituent = scene_note.get('constituentSHA256') or {}
        revisions = scene_note.get('registrationRevision') or {}
        delivery_hashes = {item['id']: item.get('derivativeSHA256') for item in delivery.get('assets', [])}
        delivery_revisions = {item['id']: (item.get('registration') or {}).get('revision') for item in delivery.get('assets', []) if item.get('registration')}
        scene_file = composite.get('file') or scene_note.get('file') or ''
        required = required_scene_members(scene_note, scene_file)
        evidence = scene_note.get('evidence') or []
        evidence_ok = bool(evidence) and all(isinstance(item, dict) and output_matches(item.get('file'), item.get('sha256')) for item in evidence)
        scene_ok = (
            bool(constituent) and bool(revisions)
            and required['constituents'] <= set(constituent)
            and required['registrations'] <= set(revisions)
            and scene_note.get('sha256') == composite.get('sha256')
            and output_matches(scene_file, composite.get('sha256'))
            and scene_note.get('cameraHash') == delivery.get('cameraHash') == bindings['camera']
            and scene_note.get('contractHash') == delivery.get('contractHash') == bindings['contract']
            and all(delivery_hashes.get(key) == value for key, value in constituent.items())
            and all(delivery_revisions.get(key) == value for key, value in revisions.items())
            and (scene_note.get('composite') != 'PASS' or evidence_ok)
            and (scene_note.get('composite') != 'PASS' or scene_note.get('use') == required['use'])
        )
        if not scene_ok:
            output_stale.append({'reason': 'scene review is not bound to the current composite, constituents, registration, camera, contract and evidence'})
    scene_gate = {
        'status': scene_note.get('composite', 'UNVERIFIED') if scene_ok else ('REJECTED_STALE_HASH' if scene_note else 'UNVERIFIED'),
        'bound': scene_ok,
    }

    selected = []
    for source in registry.get('sources', []):
        key_text = source['preferredReviewCandidateKey']
        parts = key_text.split(':')
        batch, ident, sha = parts[0], parts[1], parts[2]
        row = by_key.get((batch, ident, sha))
        path_ok = bool(row and source.get('sourceFile') == row['sourceFile'] and source.get('id') == row['id'] and source.get('batch', batch) == row['batch'] and output_matches(source.get('sourceFile'), source.get('sourceSHA256')))
        ok = bool(row and row['hashMatch'] and row['sourceSHA256'] == source['sourceSHA256'] == sha and path_ok)
        if source.get('sourceFile') and not path_ok:
            output_stale.append({'id': source.get('id'), 'reason': 'registry sourceFile does not match the selected row'})
        selected.append({
            'id': source['id'],
            'preferredReviewCandidateKey': key_text,
            'sourceFile': source['sourceFile'],
            'sourceSHA256': source['sourceSHA256'],
            'acceptedForRecovery': ok,
            'runtimeApproved': False,
            'ownerAcceptance': 'UNVERIFIED',
            'sourceContent': row['gates']['sourceContent'] if ok else 'REJECTED_STALE_HASH',
            'reason': source.get('selectionReason'),
        })
    grouped = {}
    for row in rows:
        grouped.setdefault((row['batch'], row['id']), []).append(row)
    for group in grouped.values():
        if len(group) > 1:
            for row in group:
                row['duplicate'] = True
                row['hashMatch'] = False
                row['gates'] = {name: 'REJECTED_STALE_HASH' for name in GATES}
                row['artworkReadyForUse'] = {'status': 'UNVERIFIED', 'bound': False}
    return {'rows': rows, 'stale': stale, 'outputStale': output_stale, 'scene': scene_gate, 'selected': selected}


def stale_fixture():
    item = {
        'key': 'production-01-20261003:resource-food:deadbeef',
        'batch': 'production-01-20261003',
        'id': 'resource-food',
        'sourceFile': 'assets/production/production-01-20261003/images/26-resource-food.png',
        'sourceSHA256': 'deadbeef',
        'technicalStatus': 'PASS',
        'sourceContentStatus': 'PASS',
        'ownerAcceptance': 'PASS',
        'runtimeApproved': True,
        'classification': 'RECOVERABLE',
    }
    registry = [{
        'id': 'resource-food',
        'preferredReviewCandidateKey': 'production-01-20261003:resource-food:deadbeef',
        'sourceFile': item['sourceFile'],
        'sourceSHA256': 'deadbeef',
        'selectionReason': 'fixture',
    }]
    result = evaluate(
        review_items=[item],
        registry_items=registry,
        delivery={'assets': []},
        visual={'assets': []},
        file_hash=lambda _path: 'not-the-recorded-hash',
    )
    row = result['rows'][0]
    return row['gates']['sourceContent'] == 'REJECTED_STALE_HASH' and row['runtimeApproved'] is False and result['selected'][0]['acceptedForRecovery'] is False


def safety_fixtures():
    """The three audit failures plus the added negative cases must stay rejected."""
    item = {
        'key': 'production-03-20261003:skill-offense:594fc35135244184a2c685ff6ac243dfe4b5ff9c846e8e0a92ea60b816cf11cf',
        'batch': 'production-03-20261003', 'id': 'skill-offense',
        'sourceFile': 'assets/production/production-03-20261003/images/04-skill-offense.png',
        'sourceSHA256': '594fc35135244184a2c685ff6ac243dfe4b5ff9c846e8e0a92ea60b816cf11cf',
        'technicalStatus': 'PASS', 'sourceContentStatus': 'PASS', 'classification': 'RECOVERABLE',
    }
    real = 'a1454dfb7cc41a97aa63c6f6b3b0095d8d7a381e2c48725dc487268821c162f5'
    extra = {
        'batch': item['batch'], 'id': item['id'], 'sourceSHA256': item['sourceSHA256'],
        'derivative': 'assets/delivery/stone-starter-20261003/derivatives/skill-offense.png',
        'derivativeSHA256': real,
        'gates': {'matte': {'status': 'PASS'}, 'registration': {'status': 'UNVERIFIED'}, 'composite': {'status': 'UNVERIFIED'}},
    }
    def fake_hash(path):
        if path.endswith('04-skill-offense.png'):
            return item['sourceSHA256']
        if path.endswith('derivatives/skill-offense.png'):
            return real
        return 'absent'
    def run(delivery_assets, visual, sources):
        return evaluate(review_items=[item], registry_items=sources, delivery={'assets': delivery_assets, 'composite': {'file': 'missing.png', 'sha256': 'abc'}, 'cameraHash': 'camera', 'contractHash': 'contract'}, visual=visual, file_hash=fake_hash)
    missing = dict(extra)
    missing['derivative'] = 'qa/recovery-verifier-20261003/does-not-exist.png'
    missing['derivativeSHA256'] = '0' * 64
    missing_row = run([missing], {'assets': []}, [])['rows'][0]
    stale_visual = run([extra], {'assets': [{'batch': item['batch'], 'id': item['id'], 'sourceSHA256': item['sourceSHA256'], 'derivativeSHA256': '0' * 64, 'gates': {'matte': 'FAIL'}}]}, [])['rows'][0]
    changed_output = run([dict(extra, derivativeSHA256='f' * 64)], {'assets': [{'batch': item['batch'], 'id': item['id'], 'sourceSHA256': item['sourceSHA256'], 'derivativeSHA256': real, 'gates': {'matte': 'PASS'}}]}, [])['rows'][0]
    wrong_path = run([extra], {'assets': []}, [{'id': 'skill-offense', 'preferredReviewCandidateKey': item['key'], 'sourceFile': 'qa/recovery-verifier-20261003/does-not-exist.png', 'sourceSHA256': item['sourceSHA256']}])['selected'][0]
    wrong_batch = run([extra], {'assets': []}, [{'id': 'skill-offense', 'batch': 'production-01-20261003', 'preferredReviewCandidateKey': 'production-01-20261003:skill-offense:' + item['sourceSHA256'], 'sourceFile': item['sourceFile'], 'sourceSHA256': item['sourceSHA256']}])['selected'][0]
    stale_scene = run([extra], {'assets': [], 'scene': {'composite': 'PASS', 'sha256': '0' * 64, 'file': 'missing.png', 'cameraHash': 'old', 'contractHash': 'old', 'constituentSHA256': {'skill-offense': '0' * 64}, 'registrationRevision': {}}}, [])
    return {
        'missingDerivativePassRejected': missing_row['gates']['matte'] == 'REJECTED_STALE_HASH',
        'staleVisualNotApplied': stale_visual['gates']['matte'] == 'PASS' and 'visual' not in stale_visual,
        'changedOutputDoesNotKeepOldVisual': changed_output['gates']['matte'] != 'PASS',
        'registryMissingPathRejected': wrong_path['acceptedForRecovery'] is False,
        'wrongBatchRejected': wrong_batch['acceptedForRecovery'] is False,
        'staleSceneRejected': stale_scene['scene']['bound'] is False and stale_scene['scene']['status'] == 'REJECTED_STALE_HASH',
    }


def interior_integrity(root: Path | None = None) -> dict:
    """Roof and wall pixels that are deep inside v1 must stay opaque in v3."""
    root = root or ROOT
    import cv2
    import numpy as np
    from PIL import Image
    v1 = np.array(Image.open(root / 'assets/delivery/stone-starter-20261003/derivatives/townhall-stone.png').convert('RGBA'))
    v3 = np.array(Image.open(root / 'assets/delivery/stone-starter-20261003/derivatives/v3/townhall-stone.png').convert('RGBA'))
    distance = cv2.distanceTransform((v1[:, :, 3] > 16).astype(np.uint8), cv2.DIST_L2, 5)
    red = v1[:, :, 0].astype(np.int16)
    green = v1[:, :, 1].astype(np.int16)
    blue = v1[:, :, 2].astype(np.int16)
    protected = (distance > 12) & (v1[:, :, 3] > 200) & (green + 10 > blue) & (red > 50)
    lost = int((protected & (v3[:, :, 3] <= 16)).sum())
    return {'protected': int(protected.sum()), 'lost': lost, 'pass': lost == 0 and int(protected.sum()) > 1000}


def preserved_ui(root: Path | None = None) -> dict:
    root = root or ROOT
    expected = {
        'resource-food': 'af2ef872598b99d5457793551c8297c3d136ab6e1113edb19da73fd3f7a635ef',
        'resource-wood': '98124471d8d7c8055a73d1c62dce1e5ed4c0fb329d6fa5a77a1e9eb5bcebede8',
        'resource-stone': 'fe3eb2bf114243f5053c9ce5d8834e85646e4e710a7aad40ec51b9f426e540b3',
        'skill-offense': 'cb71c50e6c1f5bdd208e0ab45c3cfc2acecc70372210bbe0ac1d18ec54a91922',
    }
    ok = all(digest(root / 'assets/delivery/stone-starter-20261003/derivatives/v2' / f'{name}.png') == sha for name, sha in expected.items())
    return {'pass': ok, 'ids': list(expected)}


def adversarial_fixtures():
    """The four verifier probes, plus use/size and duplicate coverage, must not accept a PASS."""
    item = {
        'key': 'production-01-20261003:resource-gold:e8cb7967df838fd84168e87dff6ac98c66c1bdfaab0dfbac84f81d978468f168',
        'batch': 'production-01-20261003', 'id': 'resource-gold',
        'sourceFile': 'assets/production/production-01-20261003/images/29-resource-gold.png',
        'sourceSHA256': 'e8cb7967df838fd84168e87dff6ac98c66c1bdfaab0dfbac84f81d978468f168',
        'technicalStatus': 'PASS', 'sourceContentStatus': 'UNVERIFIED', 'runtimeApproved': False,
    }
    real = 'fd1d293143ab7d08312fc6a435bfc8d1c437792616b5f56edf97f050584b27c9'
    def fake_hash(path):
        name = str(path).replace('\\', '/')
        if name.endswith('images/29-resource-gold.png'):
            return item['sourceSHA256']
        if name.endswith('derivatives/v3/resource-gold.png'):
            return real
        return 'absent'
    delivery = {'assets': [{'batch': item['batch'], 'id': item['id'], 'sourceSHA256': item['sourceSHA256'], 'derivative': 'assets/delivery/stone-starter-20261003/derivatives/v3/resource-gold.png', 'derivativeSHA256': real, 'gates': {}}], 'composite': {'file': 'assets/delivery/stone-starter-20261003/composites/stone-kingdom-hall-only-day1-v3.png', 'sha256': '66e20d9d00ea651f383d9a09d3585b15580702adb4505793b1b10c5ceab3854f'}, 'cameraHash': 'obsolete-camera', 'contractHash': 'obsolete-contract'}
    scene = {'composite': 'PASS', 'sha256': delivery['composite']['sha256'], 'file': delivery['composite']['file'], 'cameraHash': 'obsolete-camera', 'contractHash': 'obsolete-contract', 'constituentSHA256': {}, 'registrationRevision': {}, 'evidence': [{'file': 'missing-verifier-evidence.png', 'sha256': '0' * 64}]}
    omitted = evaluate(review_items=[item], registry_items=[], delivery=delivery, visual={'assets': [], 'scene': scene}, file_hash=fake_hash)
    wrong = dict(delivery['assets'][0])
    wrong_art = {'status': 'PASS', 'evidence': [{'file': 'missing.png', 'sha256': '0' * 64}], 'policyRevision': 'stale', 'sizes': [18, 36], 'use': 'skill-emblem', 'derivativeSHA256': real}
    wrong_delivery = {'assets': [{**delivery['assets'][0], 'artworkReadyForUse': wrong_art}], 'cameraHash': delivery['cameraHash'], 'contractHash': delivery['contractHash'], 'composite': delivery['composite']}
    artwork = evaluate(review_items=[item], registry_items=[], delivery=wrong_delivery, visual={'assets': []}, file_hash=fake_hash)
    duplicate = evaluate(review_items=[item, dict(item)], registry_items=[], delivery={'assets': []}, visual={'assets': []}, file_hash=fake_hash)
    return {
        'omittedMembersRejected': omitted['scene']['status'] != 'PASS' and omitted['scene']['bound'] is False,
        'staleCameraRejected': omitted['scene']['status'] != 'PASS',
        'missingEvidenceRejected': omitted['scene']['bound'] is False,
        'wrongUseRejected': artwork['rows'][0]['artworkReadyForUse']['status'] != 'PASS',
        'duplicateRowsRejected': all(row.get('duplicate') and row['gates']['sourceContent'] == 'REJECTED_STALE_HASH' for row in duplicate['rows']),
    }


def main():
    result = evaluate()
    fresh = [r for r in result['rows'] if r['hashMatch']]
    summary = {
        'rows': len(result['rows']),
        'fresh': len(fresh),
        'stale': len(result['stale']),
        'selected': len(result['selected']),
        'selectedFresh': sum(1 for s in result['selected'] if s['acceptedForRecovery']),
        'runtimeApproved': sum(1 for r in result['rows'] if r['runtimeApproved']),
        'ownerAccepted': sum(1 for r in result['rows'] if r['ownerAccepted']),
        'sourceContentPass': sum(1 for r in fresh if r['gates']['sourceContent'] == 'PASS'),
        'staleFixtureRejected': stale_fixture(),
        'safetyFixtures': safety_fixtures(),
        'collectionRows': sum(1 for r in result['rows'] if r.get('reviewSource') == 'COLLECTION_ONLY'),
        'missingReviewUnverified': all(r['gates']['sourceContent'] == 'UNVERIFIED' for r in result['rows'] if r.get('reviewSource') == 'COLLECTION_ONLY'),
        'interior': interior_integrity(),
        'preservedUi': preserved_ui(),
        'adversarialFixtures': adversarial_fixtures(),
    }
    published_path = ROOT / 'qa/recovery-executor-20261003/per-asset-reviews.json'
    published_path.parent.mkdir(parents=True, exist_ok=True)
    body = {
        'serialization': 'json.dumps sort_keys true, separators comma and colon',
        'policySHA256': authoritative(ROOT)['policy'],
        'cameraHash': authoritative(ROOT)['camera'],
        'contractHash': authoritative(ROOT)['contract'],
        'scene': result['scene'],
        'assets': [
            {
                'batch': row['batch'],
                'id': row['id'],
                'sourceFile': row['sourceFile'],
                'sourceSHA256': row['sourceSHA256'],
                'derivative': row.get('derivative'),
                'derivativeSHA256': row.get('derivativeSHA256'),
                'derivativeHashMatch': row.get('derivativeHashMatch'),
                'reviewSource': row.get('reviewSource'),
                'gates': row['gates'],
                'artworkReadyForUse': row.get('artworkReadyForUse', {'status': 'UNVERIFIED', 'bound': False}),
                'runtimeApproved': False,
                'ownerAccepted': False,
            }
            for row in result['rows']
        ],
    }
    encoded = json.dumps(body, sort_keys=True, separators=(',', ':')).encode()
    published_path.write_text(json.dumps({'canonicalSHA256': hashlib.sha256(encoded).hexdigest(), 'body': body}, indent=2) + '\n', encoding='utf-8')
    summary['publishedAssets'] = len(body['assets'])
    summary['publishedSHA256'] = hashlib.sha256(encoded).hexdigest()
    summary['sceneBound'] = result['scene']['bound']
    summary['artworkPass'] = sum(1 for row in result['rows'] if (row.get('artworkReadyForUse') or {}).get('status') == 'PASS' and (row.get('artworkReadyForUse') or {}).get('bound') is True)
    print(json.dumps(summary))
    return summary


if __name__ == '__main__':
    main()
