"""Extract barracks-stone and rig-knight derivatives for live Kingdom/Hero consumers.

Uses the same border-connected matte as the first Stone delivery recovery.
Does not modify originals, locks, provider records or the 66 prior delivery hashes.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from recover_first_delivery import matte, read_rgb, save_rgba, sha256  # noqa: E402

OUT = ROOT / 'assets/delivery/stone-starter-20261003/derivatives/v2'
RECORD = ROOT / 'qa/code-art-consumers-20261004/processing.json'
TARGETS = {
    'barracks-stone': {
        'batch': 'production-04-20261003',
        'sourceFile': 'assets/production/production-04-20261003/images/01-barracks-stone.png',
        'sourceSHA256': '80cff15590affe872fe15956aa11c044851a20014835dfe7555c5d7b84421365',
        'out': OUT / 'barracks-stone.png',
    },
    'rig-knight': {
        'batch': 'production-12-20261003',
        'sourceFile': 'assets/production/production-12-20261003/images/16-rig-knight.png',
        'sourceSHA256': None,
        'out': OUT / 'rig-knight.png',
    },
    'creature-wolf': {
        'batch': 'production-10-20261003',
        'sourceFile': 'assets/production/production-10-20261003/images/09-creature-wolf.png',
        'sourceSHA256': None,
        'out': OUT / 'creature-wolf.png',
    },
}


def main() -> int:
    rows = []
    for asset_id, spec in TARGETS.items():
        source = ROOT / spec['sourceFile']
        digest = sha256(source)
        if spec['sourceSHA256'] and digest != spec['sourceSHA256']:
            raise SystemExit(f'{asset_id} source hash mismatch: {digest}')
        if spec['sourceSHA256'] is None:
            spec['sourceSHA256'] = digest
        rgba, info = matte(read_rgb(source))
        out_hash = save_rgba(spec['out'], rgba)
        rows.append({
            'id': asset_id,
            'batch': spec['batch'],
            'sourceFile': spec['sourceFile'],
            'sourceSHA256': digest,
            'derivative': str(spec['out'].relative_to(ROOT)).replace('\\', '/'),
            'derivativeSHA256': out_hash,
            'width': int(rgba.shape[1]),
            'height': int(rgba.shape[0]),
            'recipe': 'border-connected-matte-v1',
            'processing': info,
            'runtimeApproved': False,
            'ownerAcceptance': 'UNVERIFIED',
            'intendedConsumer': 'kingdom' if 'barracks' in asset_id else 'hero-army',
        })
        print(asset_id, out_hash, info['opaqueFraction'])
    RECORD.parent.mkdir(parents=True, exist_ok=True)
    RECORD.write_text(json.dumps({'at': __import__('datetime').datetime.utcnow().isoformat() + 'Z', 'assets': rows}, indent=2), encoding='utf-8')
    print('wrote', RECORD)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
