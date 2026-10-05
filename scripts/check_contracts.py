import json

c1 = json.load(open('docs/plan/IMPLEMENTATION-CONTRACT.json'))['geometry']['kingdom']
c2 = json.load(open('qa/recovery-executor-20261003/kingdom-layout-candidate-v2.json'))['geometry']

print("Active contract sites count:", len(c1['sites']))
print("Active contract worldToSource:", c1['worldToSource'])
print("Active contract roads count:", len(c1.get('roads', [])))
print("Active contract bridges count:", len(c1.get('bridges', [])))

print("\nCandidate-v2 sites count:", len(c2.get('sites', [])))
print("Candidate-v2 worldToSource:", c2.get('worldToSource'))
print("Candidate-v2 roads count:", len(c2.get('roads', [])))
print("Candidate-v2 bridges count:", len(c2.get('bridges', [])))
