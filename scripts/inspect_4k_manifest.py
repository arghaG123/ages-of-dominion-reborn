import json

data = json.load(open('docs/plan/image-production/native4k-first32-delivery-manifest.json'))
print('Total entries in native4k-first32-delivery-manifest:', len(data.get('deliveries', [])))
for d in data.get('deliveries', []):
    rid = d.get('id', '')
    if 'kingdom' in rid:
        print(f"{rid}: path={d.get('targetFile')}, dimensions={d.get('dimensions')}, sha={d.get('outputSHA256')[:12]}")
