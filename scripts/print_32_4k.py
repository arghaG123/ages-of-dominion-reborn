import json

data = json.load(open('docs/plan/image-production/native4k-first32-delivery-manifest.json'))
for it in data['items']:
    cid = it.get('canonicalID')
    p = it.get('nativePath')
    dim = it.get('dimensions')
    print(f"{cid}: {p} ({dim})")
