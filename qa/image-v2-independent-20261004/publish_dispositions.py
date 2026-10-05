import json
from pathlib import Path
ROOT=Path('C:/dev/ages-of-dominion-reborn');OUT=Path(__file__).parent
m=json.loads((ROOT/'docs/plan/IMAGE-DELIVERY-MANIFEST-2026-10-04.json').read_text())
failactors=['troop-stone-melee','troop-stone-ranged','troop-bronze-ranged','troop-bronze-heavy','troop-iron-ranged','troop-iron-heavy','troop-medieval-melee','troop-medieval-heavy','troop-gunpowder-melee','troop-gunpowder-ranged','troop-gunpowder-heavy','troop-industrial-melee','troop-industrial-ranged','troop-modern-melee','troop-modern-ranged','troop-modern-heavy','troop-future-melee','troop-future-ranged','troop-future-heavy']
rows=[]
for r in m['cleanUsableRows']+m['failedUnrecoverableRows']:
 c=r['category'];iid=r['id'];status='UNVERIFIED';note=''
 if c=='portrait_card':
  status='PASS_BOUNDED_CARD_FRAMING' if iid!='knight-mounted-master' else 'FAIL_STONE_ERA';note='Opaque card only; likeness/owner/live cropping not accepted.'
 if c=='army_actor':
  status='FAIL_WORLD_CONTENT_MATTE' if iid in failactors else ('FAIL_ROLE_USE_SUBSTITUTION' if iid in ['troop-iron-melee','troop-industrial-heavy'] else ('UNVERIFIED_SHADOW_CONTACT' if iid=='troop-bronze-melee' else 'CANDIDATE_BOUNDED_SINGLE_POSE'))
 if c=='hero_mount':status='FAIL_STONE_ERA_SCENIC' if iid=='knight-mounted-master' else 'FAIL_FLOOR_BACKDROP_CONTACT'
 if c=='rig_anatomy_sheet':status='FAIL_COMPLETE_SEMANTIC_ANATOMY_LANDMARK_INTERFACE';note='Local separated-source recovery worth attempting; do not equate delivered crop grouping with irrecoverability.'
 if c=='authentic_substitution':status='CANDIDATE_BOUNDED_IDENTITY_MATTE';note='Authentic1K provenance; registration/live/owner acceptance open.'
 rows.append({'id':iid,'category':c,'technical':'PASS_BINDINGS_DECODE','independentContentMatteDisposition':status,'notes':note,'spatial':'UNVERIFIED','runtime':'UNVERIFIED','owner':'UNVERIFIED','source':r.get('source'),'derivative':r.get('derivative')})
(OUT/'independent-role-dispositions.json').write_text(json.dumps({'manifestSHA256':'9811801550aa82e198f61833b24f83f3a4d34babfba1314f2860e07193033545','scope':'Bounded overview/consumer-size plus named detail evidence; not exhaustive native-edge approval','rows':rows},indent=2))
print('independent rows',len(rows),'confirmed current matte failures',len(failactors))
