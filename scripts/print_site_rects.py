import json

c1 = json.load(open('docs/plan/IMPLEMENTATION-CONTRACT.json'))['geometry']['kingdom']
c2 = json.load(open('qa/recovery-executor-20261003/kingdom-layout-candidate-v2.json'))['geometry']

print("Active sites:")
for s in c1['sites']:
    print(f"  {s['id']}: rect={s['rect']}")

print("\nCandidate-v2 sites:")
for s in c2['sites']:
    print(f"  {s['id']}: rect={s.get('rect') or s.get('bounds')}")
