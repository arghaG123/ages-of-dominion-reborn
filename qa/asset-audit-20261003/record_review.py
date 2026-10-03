"""Persist the verifier's manual findings, never infer them from decoding or filenames."""
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
import json
from inspect import ROOT, OUT, read, sha

SNAPSHOT=read(OUT/'local-snapshot.json')
FAIL={
 ('01','townhall-stone'):'Strong illustration outlines and simplified materials differ from the approved rendered landscape. Superseded by the photoreal hall in batch 03; do not repurchase.',
 ('02','portrait-ancient-warlock'):'The entire output is a village painting; no full-body Warlock or identity master exists to extract.',
 ('03','kingdom-terrain-medieval'):'Dense houses and actors occupy most required dynamic plots. Converting this into bare terrain requires rebuilding the central town; use the less obstructed batch 01 source.',
 ('03','tactical-terrain-desert'):'Only one crossing, engraved deployment grids and canyon geometry replace the required two-crossing arena. Reject as a complete registered Tactical terrain.',
 ('03','tactical-terrain-snow'):'A new transverse river intersects the intended river; decks run across the wrong water geometry and square lawn markers remain. This changes navigable topology.',
 ('03','tactical-terrain-waste'):'Only one crossing and visible square grids. The second lane and terrain topology require major reconstruction; not accepted as the complete arena.',
 ('03','tactical-terrain-ruins'):'Only one crossing, raised masonry squares and obstructed approaches. Reject as a complete two-crossing Tactical arena.',
 ('03','defense-terrain-waste'):'A populated Medieval city surrounds and occupies the defense scene, rather than an ash/broken-ground biome with separate mutable town layers.',
}
NOTES={
 ('01','kingdom-terrain-stone'):'Stone materials and right river are usable; outlined pads, scattered objects and actors are baked. Keep outskirts material; clean plot/road/perimeter regions and verify every reserved footprint.',
 ('01','kingdom-terrain-bronze'):'Earth/mudbrick settlement material is usable; huts, debris, borders and actor-like details remain. Remove baked dynamic details and rebuild empty registered pads.',
 ('01','kingdom-terrain-iron'):'Ordered masonry settlement and empty-looking rectangular plots closely follow the guide. Remove engraved plot borders and baked dynamic details; verify period decoration separately.',
 ('01','kingdom-terrain-medieval'):'Slate/timber outskirts and mostly empty pads are usable. A second right-hand bridge and plot outlines are baked; remove the extra crossing and separate the mutable perimeter.',
 ('01','kingdom-terrain-gunpowder'):'Bastioned town terrain is recognizable. Permanent walls/gate, plot outlines and extra crossings cannot represent mutable Walls0; separate or remove those layers.',
 ('01','kingdom-terrain-industrial'):'Industrial outskirts/roads are useful; trains, vehicles, stockpiles and site edges are painted into the central area. Remove those dynamic details without changing the contract geography.',
 ('01','kingdom-terrain-modern'):'Modern buildings outside the plots are useful. Construction materials, vehicles and hard pad outlines remain in the selectable area; erase those and validate pad clearance.',
 ('01','kingdom-terrain-future'):'Futuristic outskirts differ visibly from earlier eras. Empty lawn islands, baked gate and two crossings still require correction to the single-crossing/shared-pad map.',
 ('01','townhall-bronze'):'One mudbrick/thatch civic compound is visible with detailed material finish. Recover the isolated structure, remove backdrop/shadow and measure the actual base; do not retain proposed pivot blindly.',
 ('01','townhall-iron'):'A mechanical clock tower makes this unsuitable as the declared Iron civic hall. Preserve as a possible later-era civic/decoration source; the original Iron requirement remains open.',
 ('01','townhall-medieval'):'One timber/stone/slate civic building is visible. Recover backdrop and exterior shadow; its ground axes/base differ from the proposed guide and need measured registration.',
 ('01','townhall-gunpowder'):'Detailed slate/masonry civic compound is usable source material, with era reuse dependent on the final town kit. It includes boundary walls/sheds; exclude independent perimeter from the Hall layer.',
 ('01','townhall-industrial'):'Brick/steel civic-industrial compound is legible. Decide which courtyard stockpiles belong to the Hall; matte and measure the remaining base before scene assembly.',
 ('01','townhall-modern'):'One concrete/glass civic block has a clean identity. Its visible square apron and exterior shadow need separate handling, then actual base registration.',
 ('01','townhall-future'):'One curved futuristic civic structure has readable architecture. Recover exterior key color, internal negative spaces and ramps; measure ground plane and silhouette scale.',
 ('01','adventure-terrain'):'Forested valley, one bridge and six clearings are present. Red guide dots, circular markers, borders and schematic paths remain. These are edits/registration work, not proof that the scenery is worthless.',
 ('01','tactical-terrain'):'Natural rocky/wooded arena, two detailed stone bridges, no baked units or HUD. Raw scene content passes. Registration overlay puts L3 into the river/bridge side and R1 on rock; banks/deployment clearances still fail as delivered.',
 ('01','defense-terrain'):'Rocky wooded lane is usable. Tower-pad borders and red guide-like marks remain; lane/gate/pad positions must be checked against the contract before acceptance.',
 ('01','adventure-site-town'):'One walled town cluster is suitable as a single Adventure site, not a Kingdom building. A green triangular guide remnant remains under its lower-right base; remove it and measure approach/pivot.',
 ('01','adventure-site-ruin'):'One broken masonry ruin is readable. Recover openings/windows separately from stone; retain actual rubble footprint, measure base and site entrance.',
 ('01','adventure-site-mill'):'One waterwheel mill has detailed timber/stone. Recover gaps around wheel/supports; wheel projection and ground approach require a scene comparison.',
 ('01','adventure-site-mine'):'One mine-working compound is readable, with ramps/crane/ore. Recover rope/support openings and apron; register the full compound rather than only its tallest roof.',
 ('01','adventure-site-dwelling'):'One thatch dwelling compound is readable. Retain shelter/ground contact and remove keyed exterior floor; measure footprint and approach.',
 ('01','adventure-site-shrine'):'One small stone shrine is legible. Recover backdrop, shadow and entrance space; keep this as the shrine identity rather than adding a new building type.',
 ('01','resource-food'):'Basket, grain and provisions communicate Food. Source content passes; remove magenta from basket/rope openings and check legibility at the 18px resource exception.',
 ('01','resource-wood'):'Bound logs communicate Wood with good cut-grain detail. The background is muted rose rather than pure magenta; use segmentation, not an exact FF00FF key.',
 ('01','resource-stone'):'Grey rocks clearly communicate Stone. Preserve rock silhouette and small detached rock; remove exterior shadow and magenta contamination before UI/pickup crops.',
 ('01','resource-gold'):'Gold coin stack clearly communicates Gold. Remove reflected magenta along coin rims and exterior shadow; verify contrast at 18px.',
 ('01','knight-mounted-master'):'Helmet, scale/plate-like armor, barding and heraldic shield fail the requested Stone hide/timber kit. Face/horse artwork can be a later-era reference candidate; it does not fill ancient Knight or supply an articulated gait.',
 ('02','gear-stone-weapon'):'Two crossed wooden implements appear where one flint club was requested. The stone-head/haft motif is useful, but isolating one needs reconstruction at the overlap; prefer batch 03 club segmentation first.',
 ('02','portrait-ancient-ranger'):'Full human body, bow and hide/fur clothing communicate Ranger. Paved floor is outside the required isolated source; remove floor/shadow and preserve quiver, bowstring and fine fur.',
 ('03','kingdom-terrain-stone'):'Early timber/thatch outskirts are useful, but timber pad borders, extra lower plots, actors and shifted crossing remain. Prefer batch 01 topology unless this source wins a measured comparison.',
 ('03','townhall-stone'):'Detailed thatch/timber/hide Hall is usable and improves the earlier cartoon. Dirt island is a removable apron, not a reason to repurchase. Edge-connected soil and oversized footprint need crop/registration work.',
 ('03','skill-offense'):'Front-facing square plaque, crossed blades, legible material and no HUD/text. Raw content passes; keep the plaque as the required square silhouette. Only exterior backdrop/shadow and edge QA remain.',
 ('03','gear-stone-weapon'):'One fully visible flint club lies over a village. Isolate the complete club, discarding all village pixels/shadow; a simple chroma key cannot work. Source scene fails, but the requested object is recoverable by segmentation.',
 ('03','adventure-terrain-plains'):'Grassland, six clearings and one prominent stone bridge are useful. Red dots remain; crossing is displaced from the guide despite several clearings aligning. Preserve land/road material and re-register the crossing/corridor.',
 ('03','adventure-terrain-hills'):'Rocky valley includes an extra lower-left crossing, green pad borders, red dots and a mounted actor. Local removal is plausible, but compare the remaining bridge/pads before choosing it as a registered terrain.',
 ('03','adventure-terrain-swamp'):'Wet reeds/pools read as swamp. Clearings, borders and paths are still schematic; recover them and verify that pools never invade legal corridors.',
 ('03','adventure-terrain-desert'):'Desert material is useful, but drawn ring markers and schematic rectangular pads/roads remain. Remove rings/borders; register bridge and site entrances without deleting desert identity.',
 ('03','adventure-terrain-snow'):'Snow and evergreens are convincing; exposed rectangular lawn pads and ring markers are guide leakage. Restore snow/soil naturally at reserved sites and register one crossing.',
 ('03','adventure-terrain-waste'):'Ash/broken terrain material is useful, with a single visible crossing. Plot rectangles/edges and exposed path diagram need repair; preserve navigable source/world corridor registration.',
 ('03','adventure-terrain-ruins'):'Ruin material is usable outside clearings; loose stone details and stumps appear in/near pads. Remove intrusive props and verify the same six source footprints/crossing.',
 ('03','tactical-terrain-plains'):'Two bridges survive, but broad rectangular lawn/deployment regions and schematic paths leak the guide. Remove lawn boundaries and inspect legal deployments before reuse.',
 ('03','tactical-terrain-hills'):'Natural rocky highland arena with two stone crossings, no obvious baked actors/HUD. Raw content passes at contact-sheet scale. Rocks and banks still need full registration/deployment review.',
 ('03','tactical-terrain-swamp'):'Wet deadwood arena with two stone crossings, no obvious baked actors/HUD. Raw content passes at contact-sheet scale. Verify every slot/path against pools, stumps and bridge approaches.',
 ('03','defense-terrain-plains'):'Grassland winding lane and open pads are useful. Pad borders, a castle/gate and an extra river crossing remain; gate/river differ from the contract. Separate dynamic gate and restore exact lane/pads.',
 ('03','defense-terrain-hills'):'Highland rocks and winding path are useful. Castle/gate, tower-pad outlines and bridge are baked; move mutable gate to its own layer and clear every legal lane/pad.',
 ('03','defense-terrain-swamp'):'Marsh material is useful, but causeway edges and square pads remain. Pools must remain outside the full legal lane and tower footprints; verify sparse source detail at phone size.',
 ('03','defense-terrain-desert'):'Detailed desert material is useful. Two red dots, circles, a large bridge and castle/gate are baked; recover those areas and rebuild the contract lane/gate geometry.',
 ('03','defense-terrain-snow'):'Snowfield/evergreens are useful; circular bare pads, bridge and castle/gate remain. Clear pad diagrams and separate gate; restore contract lane without introducing a new crossing rule.',
 ('03','defense-terrain-ruins'):'Broken walls/rock vegetation outside the winding lane are useful. Ruin props, source bounds and pad clearance need checking; derive the gate from a separate registered layer.',
 ('03','farm-stone'):'One farm-plot compound with thatch sheds and crops, no visible people/animals. Multiple sheds form one requested farm yard; source content passes. Retain the farm patch, remove keyed floor/shadow and fit its real footprint.',
 ('03','lumber-stone'):'One timber-yard compound with logs, shelters and axe rack reads as Lumber Camp. Source content passes; remove exterior shadow/backdrop and measure the compound base.',
 ('03','quarry-stone'):'One flint face and timber-crane working reads as Quarry. Source content passes; recover crane/rope openings and stone ground island, then measure actual base.',
 ('03','mine-stone'):'One shallow timber gold-working pit reads as the requested Stone mine source. Source content passes; it is a ground feature, so test legibility and footprint at town scale after matte.',
}
MOTIFS={'offense':'crossed melee blades','archery':'bow and arrow','armorer':'armor plates','wisdom':'open book','leadership':'banner','luck':'clover','tactics':'formation/weapon arrangement','logistics':'boot with route','firstaid':'supporting hands', 'arrow':'magic arrow','bless':'raised blessed weapon','haste':'winged boot','cure':'healing hand','slow':'binding chains','bolt':'lightning','fireball':'fire sphere','resurrect':'rising human figure'}
GEAR={'helm':'bone circlet','offhand':'hide shield','armor':'hide vest','boots':'hide boot pair','accessory':'bone ring'}
PORTRAITS={'warlock':'', 'mage':'staff, antlers and caster robes','paladin':'shield and bone/stone mace','barbarian':'fur and stone axe','necromancer':'skull/bone staff and headdress','healer':'herb basket and staff'}
DETAIL={('03','townhall-stone'),('03','skill-offense'),('02','portrait-ancient-warlock'),('03','gear-stone-weapon'),('01','townhall-iron'),('01','knight-mounted-master'),('01','tactical-terrain'),('03','farm-stone'),('02','portrait-ancient-ranger'),('03','defense-terrain-desert'),('03','tactical-terrain-desert'),('03','tactical-terrain-snow'),('03','kingdom-terrain-medieval'),('01','townhall-gunpowder')}
CONTENTFAIL={('01','townhall-stone'),('01','townhall-iron'),('01','knight-mounted-master'),('02','portrait-ancient-warlock'),('02','gear-stone-weapon'),('03','gear-stone-weapon')}
TERRAINPASS={('01','tactical-terrain'),('03','tactical-terrain-hills'),('03','tactical-terrain-swamp')}
ALTERNATIVE={('01','townhall-iron'):'Later-era civic/clock-tower decorative reference only; Iron Hall remains missing.',('01','knight-mounted-master'):'Later-era mounted Knight/face/horse reference candidate only; ancient Knight remains missing.'}

RECIPES={
 'MATTE': {'operation':'Executor: create a separate RGBA derivative with original SHA256 provenance. Segment the subject and all internal holes; use a spatially varying background model for rose/gradient backdrops, remove chroma spill, keep own-material colors and put ground shadow in a separate layer. No global FF00FF deletion.', 'evidence':'Subject/alpha on black, white and neutral green; 1:1 edge crops; inspect fur/rope/window/wheel/ring holes and shadow. These operations have NOT been executed by this verifier.'},
 'ICON': {'operation':'Executor: keep one required square skill plaque or round spell disc; rectify oblique view using measured face corners before extracting. Normalize family scale/rim/light. UI background and plaque material stay opaque; only the exterior becomes alpha. The batch 03 Offense plaque already faces front.', 'evidence':'All 9 skill motifs and 8 spell motifs together at actual intended UI sizes; isolated individual exports; no new symbols or generated statistics.'},
 'REGISTRATION': {'operation':'Executor: after matte measure ground control points q00,q10,q01,q11 and base-centre pivot, not silhouette centre. Derive object axes B=[(q10-q00)/fw,(q01-q00)/fh]. Place using terrain camera A and D=A*inverse(B), anchored at the target world footprint. Compare q11 to the affine prediction; if perspective or silhouette distortion is unacceptable, reproject/rebuild the derivative rather than forcing CSS width/height. Never copy the proposed [512,790] as measured.', 'evidence':'Measured control points/pivot/footprint, facing/light/shadow, derivative hash and 1:1 composite. The requested 12px pivot tolerance applies to registration; raw non-key bounding boxes are NOT pivots.'},
 'TERRAIN': {'operation':'Executor: preserve original; edit a 1376x768 derivative to the fixed contract geography. Remove all baked markers/actors/dynamic buildings in reserved areas; preserve material outside them. Contract guide is geometry only, never final visible pad art. One Kingdom crossing, one Adventure crossing, TWO Tactical crossings; Defense has no bridge in its current navigation contract. Correct land/water geometry rather than assigning hotspots to arbitrary pixels.', 'evidence':'Contract overlay plus clean derivative, all required pads/approaches/lane/bridge cells and legal deployment positions at source size and landscape 825x375, 933x424, 1180x820, 1280x720. Reuse the same camera/landmarks across Kingdom ages; no per-age logical rearrangement.'},
 'CLUB': {'operation':'Executor: preferentially segment batch 03 club using the fully visible flint head and haft. Exclude every village/actor/road pixel and exterior cast shadow, decontaminate edges, then export ONE isolated club. Batch 02 requires reconstructing the crossed-handle overlap; do not call two crossed implements one weapon.', 'evidence':'Single-object crop, mask/alpha and black/white/green edge comparison at 1:1 and forge/inventory scale. No new paid generation is prescribed.'},
 'ALTERNATIVE': {'operation':'Executor: preserve the original identity and hash, attach a separate proposed alternative-use mapping, and review era/camera/kit compatibility. Never rename it to claim that the declared ancient/Iron requirement passed; record the original gap.', 'evidence':'Compare with later-era kit/scene before accepting alternative use. Face/horse crops are references, not complete unmounted ancient class masters or animation.'},
}

rows=[]
for item in SNAPSHOT['assets']:
    b=item['batch'].split('-')[1]; id=item['id']; key=(b,id); kind=item['kind']
    reason=FAIL.get(key) or NOTES.get(key)
    if not reason and kind in ['skill','spell']:
        motif=MOTIFS[id.split('-',1)[1]]; shape='square plaque' if kind=='skill' else 'round disc'
        reason=f'One {shape} with readable {motif}; motif/material source content passes. Oblique view, rose backdrop and exterior cast shadow require rectification/matte and family normalization.'
    if not reason and kind=='gear':
        reason=f'One {GEAR[id.rsplit("-",1)[1]]} communicates the six-slot Stone item in hide/bone materials. Source content passes; recover backdrop/internal holes and test small-size silhouette. A boot pair is one Boots slot, not an extra weapon.'
    if not reason and kind=='portrait':
        role=id.rsplit('-',1)[1];reason=f'Full human body with {PORTRAITS[role]} communicates {role}. Source content passes at contact-sheet scale; recover gradient floor/shadow, hair and attachments. Detail anatomy and scene/kit continuity remain unverified.'
    assert reason, key
    content='FAIL' if key in CONTENTFAIL or (kind=='terrain' and key not in TERRAINPASS) else 'PASS'
    status='FAIL' if key in FAIL else 'RECOVERABLE'
    recipes=[]
    if status=='RECOVERABLE':
        if key in ALTERNATIVE:recipes=['ALTERNATIVE']
        elif id=='gear-stone-weapon':recipes=['CLUB','MATTE']
        elif kind=='terrain':recipes=['TERRAIN']
        else:
            recipes=['MATTE']
            if kind in ['skill','spell']:recipes.append('ICON')
            if kind in ['building','site','actor']:recipes.append('REGISTRATION')
    category=kind if kind!='terrain' else item['mode']+'-terrain'
    if b=='03' and kind in ['building','skill','gear']:category='objects'
    proof={'contactSheet':SNAPSHOT['sheets'][b+'-'+category], 'original':item['file'], 'reviewLevel':'FULL_ORIGINAL_PLUS_CONTACT_SHEET' if key in DETAIL else 'CONTACT_SHEET_SOURCE_CONTENT_ONLY', 'limitations':'Alpha edges, measured pivots, registered composite, motion, interactive states and owner acceptance are UNVERIFIED.'}
    row={'key':item['batch']+':'+id+':'+item['sha256'], 'batch':item['batch'],'position':item['position'],'id':id,'sourceFile':item['file'],'sourceSHA256':item['sha256'], 'kind':kind,'attempt':item['attempt'],'intendedRole':id, 'classification':status,'technicalStatus':'PASS','sourceContentStatus':content, 'verifierAcceptanceScope':'Raw identity/motif/material/silhouette only; excludes matte, camera registration, composites, runtime and owner acceptance.' if content=='PASS' else 'No acceptance of original intended source content.', 'reason':reason,'requiredAlpha':item['requiredAlpha'], 'alphaStatus':'PROCESSING_REQUIRED' if item['requiredAlpha'] else 'NOT_REQUIRED','registrationStatus':'UNVERIFIED','compositeStatus':'UNVERIFIED','ownerAcceptance':'UNVERIFIED','runtimeApproved':False,'recoveryRecipes':recipes,'remainingOperation':' + '.join(recipes) if recipes else 'Keep original; not suitable as complete intended asset. No replacement submission authorized by this audit.', 'evidence':proof}
    if key in ALTERNATIVE:row['alternativeUse']=ALTERNATIVE[key];row['originalRequirementRemainsOpen']=True
    if kind=='terrain':row['recoveryConfidence']='CONDITIONAL_COMPLEX_REPAIR' if status!='FAIL' else 'NOT_ACCEPTED_AS_COMPLETE_TERRAIN'
    if key==('03','skill-offense'):row['measuredNonKeyBoundsPx']=[158,163,866,865];row['boundsMeasurementNote']='Read-only approximate chroma exclusion, includes subject/shadow. Not an alpha matte or pivot.'
    if key==('03','townhall-stone'):row['measuredNonKeyBoundsPx']=[0,20,1024,1010];row['boundsMeasurementNote']='Read-only approximate chroma exclusion; edge-connected dirt apron, roof top y20. Not the ground pivot.'
    rows.append(row)

counts=dict(Counter(r['classification'] for r in rows)); contentcounts=dict(Counter(r['sourceContentStatus'] for r in rows))
review={'version':1,'reviewedAt':datetime.now(timezone.utc).isoformat(),'authority':'Owner requested scoped visual validation/recovery of existing collected results; planner/verifier only. No provider actions, image generation, production art edits or game implementation.', 'classificationMeaning':{'PASS':'All intended delivery checks passed; none in this audit because derived/composite gates remain open.','RECOVERABLE':'Specific existing artwork can serve intended or explicitly stated alternative role after listed operations. Conditional candidate, not a completed recovered asset.','FAIL':'Demonstrably unsuitable as the complete intended asset; preserve original for reference/material salvage.','UNVERIFIED':'Not visually assessed at all; none at overview/source-content scope. Finer delivery gates remain unverified for all.'}, 'batches':SNAPSHOT['batches'],'counts':{'collectedOutputs':len(rows),'distinctOriginalIDs':len(set(r['id'] for r in rows)),'classification':{s:counts.get(s,0) for s in ['PASS','RECOVERABLE','FAIL','UNVERIFIED']},'sourceContent':contentcounts,'ownerAccepted':0,'runtimeApproved':0}, 'recipes':RECIPES, 'assets':rows,'localEvidence':'qa/asset-audit-20261003/local-snapshot.json','associationEvidence':'qa/asset-audit-20261003/association-check.json', 'registrationEvidence':'qa/asset-audit-20261003/registration-pairs.jpg'}
target=ROOT/'docs/plan/image-production/VERIFIER-REVIEW-20261003.json';target.write_text(json.dumps(review,indent=2)+'\n',encoding='utf-8')
for batch in SNAPSHOT['batches'][:3]:
    subset=[r for r in rows if r['batch']==batch['batch']]
    body={'version':1,'reviewedAt':review['reviewedAt'],'canonicalReview':'docs/plan/image-production/VERIFIER-REVIEW-20261003.json','batch':batch['batch'],'counts':dict(Counter(r['classification'] for r in subset)), 'note':'Separate verifier ledger. Original collection/provider/manifests remain unchanged. No owner or runtime approval.', 'assets':subset}
    (ROOT/'assets/production'/batch['batch']/'verifier-review-20261003.json').write_text(json.dumps(body,indent=2)+'\n',encoding='utf-8')
    lines=['# Scoped source review: '+batch['batch'],'','Overview/content findings only. No finished matte/composite, owner or runtime approval.','', '|Position|Asset|Classification|Source content|Reason|Recovery|','|---|---|---|---|---|---|']
    for row in subset:lines.append(f'|{row["position"]}|[{row["id"]}](images/{Path(row["sourceFile"]).name})|{row["classification"]}|{row["sourceContentStatus"]}|{row["reason"]}|{row["remainingOperation"]}|')
    (ROOT/'assets/production'/batch['batch']/'VERIFIER-REVIEW-20261003.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')

preferred=defaultdict(list)
for row in rows: preferred[row['id']].append(row)
choices=[]
priority={'townhall-stone':'03','skill-offense':'03','gear-stone-weapon':'03','kingdom-terrain-stone':'01','kingdom-terrain-medieval':'01'}
for id,candidates in preferred.items():
    selected=next((r for r in candidates if r['batch'].split('-')[1]==priority.get(id)),candidates[0])
    choices.append({'id':id,'preferredReviewCandidateKey':selected['key'],'sourceFile':selected['sourceFile'],'sourceSHA256':selected['sourceSHA256'],'classification':selected['classification'],'runtimeApproved':False,'ownerAcceptance':'UNVERIFIED','alternativeOnly':selected.get('originalRequirementRemainsOpen',False),'selectionReason':'Existing better content or closer topology; review/recovery candidate only.','allAttemptKeys':[r['key'] for r in candidates], 'proposedBiome':'forest' if id in ['adventure-terrain','tactical-terrain','defense-terrain'] else None,'biomeAssociation':'UNVERIFIED_REQUIRES_COMPLETE_BIOME_KIT_REVIEW' if id in ['adventure-terrain','tactical-terrain','defense-terrain'] else None})
(ROOT/'docs/plan/image-production/RECOVERY-SOURCE-REGISTRY-20261003.json').write_text(json.dumps({'version':1,'note':'85 original identities, 90 attempts. This registry resolves reviewed source selection, not runtime approval or the full purchase inventory. Alternative-only sources leave original requirements open. Do not silently apply these candidates to the game.','sources':choices},indent=2)+'\n',encoding='utf-8')
print(json.dumps(review['counts'],indent=2))
