import json, pathlib, collections
R=pathlib.Path(__file__).resolve().parents[2]
def read(p): return json.loads((R/p).read_text(encoding='utf-8-sig'))
for name in ('ENVIRONMENT-ART','ACTORS-EQUIPMENT'):
 p=f'docs/plan/{name}-RESIDUAL-INTERFACE-2026-10-07.json'; d=read(p)
 print('\nINTERFACE',p,'keys',list(d))
 print('counts',len(d['rows']),collections.Counter(x['status'] for x in d['rows']))
 print('meta',{k:v for k,v in d.items() if k not in ('rows','readySubset','inputSnapshot')})
 print('snapshot',str(d.get('inputSnapshot'))[:1800])
 ids=['armory-stone','skill-offense','support-home','townhall-stone','troop-stone-ranged','troop-industrial-heavy','healer-leg-greave','healer-leg-subchain','knight-chain-diagram']
 for row in d['rows']:
  if row['id'] in ids: print(json.dumps(row))
 sibling='environment' if name=='ENVIRONMENT-ART' else 'actors'
 cp=read(f'qa/image-residual-executor-20261007/{sibling}/checkpoint.json')
 print('CHECKPOINT',{k:v for k,v in cp.items() if k not in ('completedIds','sourceHashes','evidencePaths')})
 print('FILES',[(x.name,x.stat().st_size) for x in (R/f'qa/image-residual-executor-20261007/{sibling}').glob('*') if x.is_file()])
d=read('qa/image-residual-executor-20261007/environment/scenes.json')
print('\nSCENES type',type(d).__name__,'keys',list(d)[:20] if isinstance(d,dict) else 'list')
rows=d.get('scenes',d.get('rows',[])) if isinstance(d,dict) else d
print('count',len(rows))
for row in rows[:1]: print(json.dumps(row))
for p in ['qa/image-residual-executor-20261007/actors/regeneration-manifest.json','qa/planner-three-ai-20261006/source-preservation.json']:
 d=read(p);print('\nMANIFEST',p,'type',type(d).__name__,'keys',list(d)[:20] if isinstance(d,dict) else 'list'); print(str(d)[:5000] if 'regeneration' in p else str(d)[:1200])
