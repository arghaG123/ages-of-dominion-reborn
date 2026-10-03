"""Planner allocation only. Does not edit production manifests, guides or ledgers."""
from pathlib import Path
import json, hashlib, collections
ROOT=Path(__file__).resolve().parents[2]; OUT=Path(__file__).resolve().parent
rows=json.loads((OUT/'originals.json').read_text())
items=json.loads((ROOT/'docs/plan/HIGH-RESOLUTION-UPGRADE-COUNT-2026-10-03.json').read_text())['scenarios']['TERRAIN_BACKGROUNDS_ONLY']['items']
aliases={
'adventure-site-guard-post':'site-guard','adventure-site-human-encounter':'site-human','adventure-site-region-exit':'site-exit','adventure-site-rest-camp':'site-rest','adventure-site-rival-camp':'site-rival','adventure-site-treasure':'site-treasure',
'artifact-clover':'artifact-iron-clover','artifact-codex':'artifact-sages-codex','artifact-lens':'artifact-eagle-eye-lens','artifact-swiftboots':'artifact-winged-spurs','artifact-vitality':'artifact-ring-of-vitality','artifact-wolfamulet':'artifact-wolf-amulet',
'hero-mount-horse':'mount-horse','hero-mount-motor-transport':'mount-motor','hero-mount-future-transport':'mount-future','title-background':'supporting-title','ui-materials':'supporting-ui-materials'}
classes=['knight','ranger','warlock','mage','paladin','barbarian','necromancer','healer']
ages=['stone','bronze','iron','medieval','gunpowder','industrial','modern','future']
for c in classes: aliases['rig-source-parts-'+c]='rig-'+c
for n,name in enumerate(['aldric','corvus','kane','morgana','theron','valeria'],1): aliases['rival-identity-'+str(n)]='supporting-rival-'+name
for n,age in enumerate(ages,1): aliases['story-'+age]='supporting-chapter-'+str(n)
for fx in ['arrow','bless','bolt','cure','haste','resurrect','slow','fireball']: aliases['effect-material-'+fx]='effect-spell-'+fx if fx in ['fireball','slow'] else 'effect-'+fx
aliases.update({'effect-material-impact-hit-death':'effect-impact','effect-material-physical-projectiles':'effect-projectile'})
required={x['id'] for x in items}; available={r['id'] for r in rows}; missing=required-available
assert set(aliases)==missing
aliasRows=[{'canonicalId':k,'candidateId':v,'status':'CANDIDATE_MAPPING_REQUIRES_CONTENT_REVIEW','candidates':[{'file':r['file'],'sha256':r['sha256'],'batch':r['batch']} for r in rows if r['id']==v]} for k,v in aliases.items()]
(OUT/'alias-candidates.json').write_text(json.dumps({'literalMatches':len(required&available),'candidateAliasMappings':aliasRows,'warning':'Coverage candidates are not artwork acceptance. Rival numbers are proposed appearance slots only; generated names do not change the six canonical game names.'},indent=2)+'\n')
four=['kingdom-terrain-'+a for a in ages]
for mode in ['adventure','tactical','defense']:
    four += [mode+'-terrain']+[mode+'-terrain-'+b for b in ['plains','hills','swamp','desert','snow','waste','ruins']]
hero=['knight-mounted-master']+['portrait-ancient-'+c for c in classes if c!='knight']+[f'portrait-{kit}-{c}' for kit in ['medieval','powder','mech'] for c in classes]
parts=['hero-mount-horse','hero-mount-motor-transport','hero-mount-future-transport']+['rig-source-parts-'+c for c in classes]+['rival-identity-'+str(n) for n in range(1,7)]
army=[f'troop-{age}-{role}' for age in ages for role in ['melee','ranged','heavy']]
assert len(four)==32 and len(hero)==32 and len(parts)==17 and len(army)==24
assert set(four+hero+parts+army)=={x['id'] for x in items if x['plannedResolution'] in ['4K','2K']}
queue=[]
for group,res,ids in [('4K-FIRST-32','4K',four),('2K-LATER-A-HERO-32','2K',hero),('2K-LATER-B-MOUNTS-RIGS-RIVALS-17','2K',parts),('2K-LATER-C-ARMY-24','2K',army)]:
    for n,id in enumerate(ids,1):
        sourceIds=[id,aliases.get(id)]
        if id.endswith('-heavy') and id.startswith('troop-') and any(a in id for a in ['bronze','iron','gunpowder','industrial','modern','future']): sourceIds.append(id.replace('troop-','attacker-'))
        queue.append({'group':group,'order':n,'id':id,'imageSize':res,'status':'PLANNED_NEEDS_EXECUTOR_READINESS','candidateSourceIds':[x for x in sourceIds if x],'sources':[{'batch':r['batch'],'id':r['id'],'file':r['file'],'sha256':r['sha256'],'promptSHA256':r['promptSHA256']} for r in rows if r['id'] in sourceIds],'preferredSource':None,'guide':None,'guideAcceptance':'UNVERIFIED'})
plan={'date':'2026-10-03','role':'PLANNER_VERIFIER','providerCallsPerformed':False,'scope':'32 individual 4K first; later proposed 2K groups require owner scheduling','model':'gemini-3.1-flash-image','project':'project-eaa4c1cc-8f19-4d24-9e6','counts':{'4K':32,'2K':73,'1K':375},'items':queue,'aliasEvidence':'qa/whole-implementation-audit-20261003/alias-candidates.json','budget':{'targetUSD':60,'hardCapUSD':80,'reserveUSD':15,'savedProtectedExposureUSD':57.225,'billedTotal':None,'expectedImageOutput4KUSD':4.8384,'expectedImageOutput2KUSD':7.3584,'inputAndTextAndStorageAndTaxAdditional':True,'capProposal4KOutputTokens':4096,'capProposal2KOutputTokens':2048,'inputTokenCapPerRequest':4000,'conditional105CeilingWith15PercentBufferUSD':76.826244,'warning':'Conditional ceiling is not a bill or increased budget. Executor validates caps, all liabilities and current pricing before calls.'}}
(ROOT/'docs/plan/INTERACTIVE-HIGH-RES-QUEUE-2026-10-03.json').write_text(json.dumps(plan,indent=2)+'\n')
usage=[]
for p in sorted((ROOT/'assets/production').glob('production-*/collection-report.json')):
    d=json.loads(p.read_text());usage.append({'batch':d['batch'],'records':len(d['usage']),'input':sum(x.get('promptTokenCount',0) for x in d['usage']),'output':sum(x.get('candidatesTokenCount',0) for x in d['usage'])})
totals={'batches':usage,'input':sum(x['input'] for x in usage),'output':sum(x['output'] for x in usage),'standardRateCalculationUSD':sum(x['input']*.5/1e6+x['output']*60/1e6 for x in usage),'invoiceStatus':'UNKNOWN','rawJSONLPayloadsReparsed':False}
(OUT/'usage-reconciliation.json').write_text(json.dumps(totals,indent=2)+'\n')
print(json.dumps({'queued':len(queue),'aliases':len(aliasRows),'input':totals['input'],'output':totals['output']}))
