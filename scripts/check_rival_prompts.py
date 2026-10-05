import json

manifest = json.load(open('docs/plan/IMAGE-LATER73-EXECUTION-MANIFEST-2026-10-04.json'))
rivals = [item for item in manifest['items'] if 'rival' in item['id']]
for r in rivals:
    print("="*60)
    print(f"ID: {r['id']}")
    print(f"Prompt: {r['prompt'][:250]}...")
