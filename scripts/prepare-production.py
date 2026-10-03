"""Prepare useful requests and deterministic registration guides; never calls a provider."""
from pathlib import Path
import json, hashlib, math
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / 'docs/plan/image-production'
MOCKS = ROOT / 'design-preview/generated/landscape-mocks-20261003-efcd7a7e/images'
def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

ages = ['stone','bronze','iron','medieval','gunpowder','industrial','modern','future']
materials = ['timber,hide,thatch,flint,dirt; NO medieval church,towers,steel', 'earth,plaster,early stone,bronze,cultivated fields', 'masonry,tiled roofs,iron,ordered paving', 'coursed stone,timber,slate,terracotta,civic keep', 'bastion stone,period civic manor,powder yards', 'brick,iron,rails,pipes,factory yards', 'concrete,glass,asphalt,utilities,modern transport', 'advanced integrated architecture,power,technical transport; NO medieval rural village carryover']
slots = ['helm','weapon','offhand','armor','boots','accessory']
common = ('ONE production image for Ages of Dominion. Semi-realistic dense inhabited rendered strategy-game materials, '
          'warm upper-left daylight, short soft contact shadows, coherent camera, high aerial three-quarter elevation55 yaw15. '
          'NO text, HUD, buttons, labels, glyph numbers, device frame, watermark, invented names/currencies. '
          'First input is an exact spatial/shape guide when present; second image gives MATERIAL/FINISH only, never copy its UI or unwanted buildings. '
          'A guide is a registration specification, not final diagram art. Never shift camera, river, sites or geographic landmarks. ')

def guide(mode, cols, rows, sites, blocked, bridges, roads, anchors):
    width,height=1376,768
    image=Image.new('RGB',(width,height),'#d4d0ba'); draw=ImageDraw.Draw(image)
    # This same affine transform is recorded for rendering/benchmark; no screen-percentage cutouts.
    matrix=[60, -10, 25, 35, 170, 165] if mode=='kingdom' else ([53,-8,23,37,180,160] if mode=='adventure' else [77,-12,27,46,270,110])
    if mode=='defense': matrix=[60,-8,20,35,270,100]
    def point(x,y): a,b,c,d,e,f=matrix; return a*x+c*y+e,b*x+d*y+f
    def poly(rect): x,y,w,h=rect; return [point(x,y),point(x+w,y),point(x+w,y+h),point(x,y+h)]
    for cell in blocked: draw.polygon(poly([*cell,1,1]),fill='#597281')
    for road in roads:
        draw.line([point(x+(0 if mode=='kingdom' else .5),y+(0 if mode=='kingdom' else .5)) for x,y in road],fill='#ae9171',width=16)
    for bridge in bridges: draw.polygon(poly(bridge['rect']),fill='#c5b397',outline='#5a5349',width=3)
    for site in sites:
        draw.polygon(poly(site['rect']),fill='#91b76b',outline='#193d19',width=4)
        x,y,w,h=site['rect']; draw.text(point(x+w/2,y+h/2),site['id'],fill='black')
    for name,cell in anchors.items(): draw.ellipse((point(*cell)[0]-6,point(*cell)[1]-6,point(*cell)[0]+6,point(*cell)[1]+6),fill='#c83e38'); draw.text(point(*cell),name,fill='black')
    path=PLAN/'guides'/f'{mode}.png'; path.parent.mkdir(parents=True,exist_ok=True); image.save(path)
    return {'cols':cols,'rows':rows,'sourceSize':[width,height],'worldToSource':matrix,'sites':sites,'blocked':blocked,'bridges':bridges,'roads':roads,'anchors':anchors,'guide':str(path.relative_to(ROOT)).replace('\\','/'),'guide_sha256':sha(path)}

def main():
    # Stable world sites authored from owner count/composition, never imported executable source.
    upper=[(2,2),(4,2),(6,2),(8,2),(10,2),(2,4),(4,4),(8,4),(10,4)]
    lower=[(1,6),(3,6),(9,6),(11,6),(2,8),(4,8),(8,8),(10,8)]
    pads=[{'id':f'P{i+1:02}','region':'upper' if i<9 else 'lower','rect':[x,y,1.4,1.2]} for i,(x,y) in enumerate(upper+lower)]
    kingdom=guide('kingdom',14,11,[{'id':'townhall','rect':[5,0,3,1.5]},*pads],[[13,r] for r in range(11)],[{'id':'right-crossing','rect':[12.5,7,1.5,.8],'cells':[[13,7]],'approaches':[[12,7]]}],[[[6.5,1.5],[7.7,1.6],[7.7,4],[7.7,6],[7.7,8],[7.7,10]]],{'gate':[7.7,10],'ridge':[6.5,0]})
    # Preserve reviewed site relationships; replace illegal tactical deployment examples.
    sites=[{'id':i,'rect':rect,'approach':ap} for i,rect,ap in [('town',[7,1,3,3],[8,4]),('ruin',[12,1,2,2],[12,3]),('mill',[1,4,2,2],[2,6]),('mine',[11,6,2,2],[10,6]),('dwelling',[11,8,2,2],[10,8]),('shrine',[1,8,2,2],[2,7])]]
    bridge={'id':'stone-crossing','rect':[3.75,6.05,2.5,.9],'cells':[[4,6],[5,6]],'approaches':[[3,6],[6,6]]}
    advroads=[[[8,4],[8,5],[8,6],[8,7],[8,8]],[[8,8],[8,7],[7,7],[7,6],[6,6],[5,6],[4,6],[3,6],[2,6],[2,7]],[[8,6],[9,6],[9,5],[9,4],[10,4],[11,4],[12,4],[12,3]],[[8,6],[9,6],[10,6]],[[8,8],[9,8],[10,8]],[[2,7],[3,7],[3,8]],[[8,8],[8,9],[7,9]],[[11,4],[11,5],[12,5],[13,5],[14,5]],[[10,6],[10,5]]]
    adventure=guide('adventure',16,10,sites,[[c,r] for c in [4,5] for r in range(10)], [bridge],advroads,{'hero':[8.5,8.5],'food':[3.5,8.5],'wood':[7.5,9.5],'stone':[14.5,5.5],'gold':[10.5,4.5],'guard-ruin':[12.5,4.5],'guard-mine':[10.5,5.5]})
    adventure['obstacles']=[[0,r] for r in range(4,10)]+[[14,8],[15,8],[14,9],[15,9]]+[[15,r] for r in range(6)]
    tactical=guide('tactical',7,10,[],[[3,r] for r in range(10)],[{'id':f'crossing-{r}','rect':[2.75,r+.1,1.5,.8],'cells':[[3,r]],'approaches':[[2,r],[4,r]]} for r in [3,7]],[[[1,r],[2,r],[3,r],[4,r],[5,r]] for r in [3,7]],{'commander':[.5,9.5],'L1':[1.5,8.5],'L2':[1.5,7.5],'L3':[2.5,8.5],'R1':[5.5,1.5],'R2':[5.5,2.5],'R3':[4.5,2.5]})
    tactical['deployment']={'allied':[0,6,3,4],'enemy':[4,0,3,4]}; tactical['obstacles']=[[0,0],[1,0],[0,1],[6,0],[6,1],[0,5],[6,5],[6,8],[6,9],[5,9]]
    lane=[[0,14],[1,14],[2,14],[2,13],[2,12],[3,12],[4,12],[4,11],[4,10],[5,10],[6,10],[6,9],[6,8],[5,8],[4,8],[4,7],[4,6],[3,6],[2,6],[2,5],[2,4],[3,4],[4,4],[4,3],[4,2],[5,2],[6,2],[6,1],[6,0]]
    defense=guide('defense',9,15,[{'id':f'D{i+1}','rect':[x,y,.8,.8]} for i,(x,y) in enumerate([(1,12),(3,10),(7,9),(3,8),(1,6),(5,5),(3,2),(7,2)])],[],[],[lane],{'gate':[6.5,.5],'spawn':[.5,14.5]}); defense['lane']=lane
    contract={'version':1,'landscapeOnly':True,'viewports':[[825,375],[933,424],[1180,820],[1280,720]],'ages':ages,'resources':['food','wood','stone','gold'],'classes':['knight','ranger','warlock','mage','paladin','barbarian','necromancer','healer'],'slots':slots,'slotUI':{'left':['helm','weapon','offhand'],'right':['armor','boots','accessory']},'skills':['offense','archery','armorer','wisdom','leadership','luck','tactics','logistics','firstaid'],'spells':['arrow','bless','haste','cure','slow','bolt','fireball','resurrect'],'creatures':['wolf','bandit','bear','harpy','golem','griffin','wyvern','drone'],'flyers':['harpy','griffin','wyvern','drone'],'modes':['kingdom','adventure','tactical','defense'],'geometry':{'kingdom':kingdom,'adventure':adventure,'tactical':tactical,'defense':defense},'hud':{'resourcesOnly':['kingdom','adventure'],'symbolPx':18,'railPx':28,'touchPx':48},'budget':{'hardCapUSD':80,'targetUSD':60,'safetyReserveUSD':15,'previousMockReserveUSD':2,'batchReservationUSD':6},'assetApproval':'TECHNICAL+CONTENT+REGISTERED_COMPOSITE+MANUAL_REFERENCE_REVIEW_REQUIRED','retryPolicy':{'maxAttemptsBeforeScriptRevision':2,'paidRetryMustBeUseful30':True}}
    write(ROOT/'docs/plan/IMPLEMENTATION-CONTRACT.json',contract)
    batch1=[]
    def add(target,id,prompt,kind,mode=None,age=None,aspect='1:1',ref=None):
        target.append({'position':len(target)+1,'id':id,'kind':kind,'mode':mode,'age':age,'aspect':aspect,'prompt':common+prompt,'styleReference':ref or '06-kingdom-medieval.jpg','guide':contract['geometry'][mode]['guide'] if mode and kind=='terrain' else None,'requiredAlpha':kind!='terrain','reviewStatus':'UNVERIFIED','attempt':1,'requestedOutputs':1})
    for age,mat in zip(ages,materials): add(batch1,f'kingdom-terrain-{age}',f'Bare wide Kingdom terrain for {age} age: {mat}. Match exact first-guide camera and geography; green P01-P17 rectangles and townhall terrace must become EMPTY buildable clearings at exact same positions. Nine upper and eight lower. No Hall or active buildings or walls baked in. Decorative outskirts at edge only. River remains right with one lower stone/age appropriate crossing; road spine and gate opening preserved. No plus marks/grid/labels from guide. Hills and inhabited outskirts outside reserved footprint.','terrain','kingdom',age,'16:9')
    for age,mat in zip(ages,materials): add(batch1,f'townhall-{age}',f'ONE upper Town Hall civic seat for {age}: {mat}. Object only, high aerial three-quarter camera matching terrain, ground footprint3 by1.5 world units; south entrance, grounded base. Empty plain pure magenta background for later reviewed matte processing. Whole silhouette fits with margin, no terrain scene or buildings surrounding it. No modern research lab name.','building','kingdom',age)
    for mode,ref,prompt in [('adventure','11-adventure-overview.jpg','Dense inhabited valley; EMPTY six guide clearings, four pickup and two guard pads, connected paths and western stone crossing. No sites/actors/loot painted onto pads. Woods, ridge, shore variation outside corridors.'),('tactical','14-tactical-deployment.jpg','Ground arena fills view; two stone decks across stream at exactly guide lanes3 and7; approaches empty, opposed banks, ruined cliffs outside legal board. No army/commander/grid baked in.'),('defense','17-defense-preparation.jpg','Winding valley lane from lower left spawn to upper right gate. Exact guide lane and eight empty tower pads; no towers/army/attackers/HUD; Stone era. Gate area remains empty for separate object.')]: add(batch1,f'{mode}-terrain',prompt,'terrain',mode,None,'16:9',ref)
    for site in sites: add(batch1,f'adventure-site-{site["id"]}',f'ONE {site["id"]} site object, medieval material calibration; footprint{site["rect"][2:]} world units with entrance facing approach{site["approach"]}. Match aerial camera. Fortified town if town; mine rock entrance if mine; no extra unidentified site. Pure magenta background, full silhouette and short contact shadow.','site','adventure',3,ref='11-adventure-overview.jpg')
    for id,motif in [('food','grain/provisions bundle'),('wood','cut log bundle'),('stone','rough grey quarry rock'),('gold','distinct stacked gold coins')]: add(batch1,f'resource-{id}',f'ONE clear modern realistic icon of {motif}; silhouette legible at18px. No rim/medallion/disc/frame/labels. Plain pure magenta backdrop; item fills central70% with isolated edges.','resource',ref='30-icon-material-board.jpg')
    add(batch1,'knight-mounted-master','ONE consistent Knight and horse identity master: high aerial full-body mounted idle pose, same recognizable face/cloth/gear as style input19, naturally grounded hooves and saddle attachments. Ancient Stone hide/timber equipment, not Medieval plate. Pure magenta backdrop. This is a static identity anchor, NOT an articulated animation atlas.','actor','adventure',0,ref='19-hero-equipment.jpg')
    batch2=[]
    skillMotifs=['crossed melee blade impact','bow with single aimed arrow','defensive chest plate','open scholarly tome','rally banner','four-leaf clover','planned formation pennants','walking boot with route','bandage and healing hand']
    spellMotifs=['single magic arrow','blessed raised weapon','swift motion boot','gentle cure hand','restraining chains','lightning strike','one fire sphere','rising restored silhouette']
    for id,motif in zip(contract['skills'],skillMotifs): add(batch2,'skill-'+id,f'ONE distinct square skill emblem: {id}, represented by {motif}. No text. Square silhouette; thin single material rim. Never duplicate another skill motif. Plain magenta backdrop.','skill',ref='30-icon-material-board.jpg')
    for id,motif in zip(contract['spells'],spellMotifs): add(batch2,'spell-'+id,f'ONE circular spell emblem: {id}, represented by {motif}. No text. Single thin circular rim and clear material/sorcery motif. Plain magenta backdrop.','spell',ref='30-icon-material-board.jpg')
    for slot,motif in zip(slots,['bone circlet','flint club','hide-covered wooden shield','hide chest wrap','hide leg wraps','bone ring']): add(batch2,'gear-stone-'+slot,f'ONE Stone era {motif} for six-slot {slot} equipment. Object alone, well lit material edges, pure magenta background. No Medieval metals or invented stats/labels.','gear',age=0,ref='22-forge.jpg')
    for cls in contract['classes'][1:]: add(batch2,'portrait-ancient-'+cls,f'ONE ancient era full-body {cls} identity portrait. Distinct class silhouette, Stone-compatible hide/textiles/timber/bone implements; recognizable consistent human face, no names/stats/HUD. Plain magenta backdrop. NO medieval plate/crossbow/firearms.','portrait',age=0,ref='19-hero-equipment.jpg')
    for index,items in enumerate([batch1,batch2],1):
        assert len(items)==30
        for item in items:
            if item['kind'] in ['building','site','actor']:
                footprint=[3,1.5] if item['kind']=='building' else next((x['rect'][2:] for x in sites if item['id']=='adventure-site-'+x['id']),[1,1])
                # Isolated object camera guide, never the full terrain layout for an object request.
                iw,ih=1024,1024; im=Image.new('RGB',(iw,ih),'#ff00ff'); d=ImageDraw.Draw(im)
                fw,fh=footprint; unit=170/max(fw,fh)
                source_matrix=contract['geometry'][item['mode']]['worldToSource']
                a,b,c,dd=[v*unit/source_matrix[0] for v in source_matrix[:4]]
                ox,oy=512-(a*fw+c*fh)/2,790-(b*fw+dd*fh)/2
                polygon=[(ox,oy),(ox+a*fw,oy+b*fw),(ox+a*fw+c*fh,oy+b*fw+dd*fh),(ox+c*fh,oy+dd*fh)]
                d.polygon(polygon,fill='#91b76b',outline='#193d19',width=4); d.ellipse((506,784,518,796),fill='red')
                gp=PLAN/'guides'/(item['id']+'.png'); im.save(gp)
                item['guide']=str(gp.relative_to(ROOT)).replace('\\','/')
                facing='+row'
                if item['kind']=='site':
                    site=next(s for s in sites if item['id']=='adventure-site-'+s['id']); x,y,w,h=site['rect']; ax,ay=site['approach']
                    facing='-column' if ax<x else '+column' if ax>=x+w else '-row' if ay<y else '+row'
                item['registration']={'sourceSize':[iw,ih],'sourcePivot':[512,790],'footprintWorld':footprint,'groundPolygonSource':polygon,'worldAxesSource':[a,b,c,dd],'camera':'mode:'+item['mode'],'facing':facing,'pivotTolerancePx':12,'status':'PROPOSED_REQUIRES_PIXEL_REVIEW'}
                item['prompt'] += ' Isolated guide green polygon is ONLY the required base footprint, red dot is ground-centre pivot(512,790) in1024square. Replace green with object grounded base; remove all guide marks. Keep full object top within y80. Do not copy a whole map. For site entrances honor its separately specified approach.'
            path=MOCKS/item['styleReference']
            if not path.exists(): raise RuntimeError(f'Missing style input {path}')
            item['styleReferenceSHA256']=sha(path); item['promptSHA256']=hashlib.sha256(item['prompt'].encode()).hexdigest()
            item['guideSHA256']=sha(ROOT/item['guide']) if item['guide'] else None
        write(PLAN/f'batch-{index:02}-manifest.json',{'id':f'production-{index:02}-20261003','model':'gemini-3.1-flash-image','project':'project-eaa4c1cc-8f19-4d24-9e6','region':'global','count':30,'status':'PREPARED_NOT_SUBMITTED','items':items,'maxOutputTokens':4096,'inputTokenUpperBoundPerRequest':12000,'reservedUSD':6,'pricingSources':['https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing','https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/capabilities/batch-inference','https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/gemini/3-1-flash-image']})
    if not (PLAN/'budget-ledger.json').exists(): write(PLAN/'budget-ledger.json',{'version':1,'currency':'USD','hardCap':80,'target':60,'safetyReserve':15,'historicalMock':{'outputOnlyEstimate':.504,'conservativeReservation':2,'billedTotal':None},'batches':[],'billedTotal':None,'billingStatus':'ESTIMATES_NOT_INVOICE'})
    print('Prepared contract, four guides, two useful30 manifests; zero provider calls.')
if __name__=='__main__': main()

