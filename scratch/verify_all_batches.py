import json
from pathlib import Path

ROOT = Path('.')
for b in range(1, 9):
    b_id = f'production-{b:02d}-20261003'
    p = ROOT / 'assets/production' / b_id
    rep_file = p / 'collection-report.json'
    if not rep_file.exists():
        print(f'{b_id}: NO collection report!')
        continue
    rep = json.loads(rep_file.read_text(encoding='utf-8'))
    images = list((p / 'images').glob('*.*'))
    tech = rep.get('technicalStatus')
    out_cnt = len(rep.get('outputs', []))
    err_cnt = len(rep.get('errors', []))
    print(f'{b_id}: technicalStatus={tech}, outputs={out_cnt}, errors={err_cnt}, imagesOnDisk={len(images)}')
