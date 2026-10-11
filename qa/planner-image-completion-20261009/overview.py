import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));from gallery import sheet,ROOT,QA
for owner,prefix in [('environment','ENVIRONMENT-ART'),('actors','ACTORS-EQUIPMENT')]:
    j=json.loads((ROOT/f'docs/plan/{prefix}-VERTEX-REPAIR-INTERFACE-2026-10-09.json').read_text(encoding='utf-8-sig'))
    rows=[r for r in j['rows'] if r.get('output') and not r['id'].startswith(('state-','support-'))]
    for z in range(0,len(rows),30):
        sheet(f'{owner}-overview-{z//30+1}.jpg',[(r['id']+' '+r['status'],r['output']['path']) for r in rows[z:z+30]],w=240,h=240,cols=6)
    print(owner,'overview rows',len(rows))
# Exact current guide and candidate versus approved appearance, fixed inputs unmodified.
ref=ROOT/'design-preview/generated/landscape-mocks-20261003-efcd7a7e/images/03-kingdom-stone.jpg'
sheet('stone-reference-guide-candidates.jpg',[('Approved composition reference',ref.relative_to(ROOT).as_posix()),('Legal guide v2','qa/image-vertex-repair-20261009/environment/geography/guides/kingdom-terrain-stone-legal-guide-v2.png'),('Rejected Stone A','assets/derivatives/image-vertex-repair-20261009/environment/native/kingdom-terrain-stone-candidate-a.png'),('Rejected Stone B','assets/derivatives/image-vertex-repair-20261009/environment/native/kingdom-terrain-stone-candidate-b.png')],w=650,h=420,cols=2)
