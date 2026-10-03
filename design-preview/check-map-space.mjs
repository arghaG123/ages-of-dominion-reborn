import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {runInNewContext} from 'node:vm';
import assert from 'node:assert/strict';
import {chromium} from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
const root='C:/dev/ages-of-dominion-reborn/design-preview/';
const maps=runInNewContext((await readFile(root+'map-space-data.js','utf8'))+';JSON.parse(JSON.stringify(MAP_SPACE));');
const key=p=>p.join(','),eq=(a,b)=>key(a)===key(b),has=(a,p)=>a.some(q=>eq(q,p));
const inside=(p,r)=>p[0]>=r[0]&&p[0]<r[0]+r[2]&&p[1]>=r[1]&&p[1]<r[1]+r[3];
const geometry=[];
for(const[id,m]of Object.entries(maps)){
  const deck=m.bridges.flatMap(b=>b.cells),siteCells=m.sites.flatMap(s=>{const[x,y,w,h]=s.rect;return Array.from({length:w*h},(_,i)=>[x+i%w,y+Math.floor(i/w)]);});
  const inBounds=p=>p[0]>=0&&p[0]<m.cols&&p[1]>=0&&p[1]<m.rows;
  const blocked=p=>has(m.obstacles,p)||(has(m.river,p)&&!has(deck,p))||has(siteCells,p);
  for(const s of m.sites){const[x,y,w,h]=s.rect;assert(x>=0&&y>=0&&x+w<=m.cols&&y+h<=m.rows,`${id} ${s.id} bounds`);for(let r=y;r<y+h;r++)for(let c=x;c<x+w;c++)assert(!has(m.obstacles,[c,r])&&!has(m.river,[c,r]),`${id} ${s.id} clearing exclusion`);assert(!blocked(s.approach),`${s.id} approach blocked`);const[c,r]=s.approach;assert((c===x-1||c===x+w)&&r>=y&&r<y+h||(r===y-1||r===y+h)&&c>=x&&c<x+w,`${s.id} detached approach`);}
  assert.equal(new Set(siteCells.map(key)).size,siteCells.length,`${id} site overlap`);
  const allPaths=[...m.roads.map(r=>r.cells),m.route];
  for(const path of allPaths)for(let i=0;i<path.length;i++){const p=path[i];assert(inBounds(p)&&!blocked(p),`${id} path blocked at ${p}`);if(i)assert.equal(Math.abs(p[0]-path[i-1][0])+Math.abs(p[1]-path[i-1][1]),1,`${id} disconnected step`);}
  for(const b of m.bridges){for(const p of b.cells){assert(has(m.river,p),`${b.id} deck not on water`);assert(inside([p[0]+.5,p[1]+.5],b.rect),`${b.id} route centre not on deck`);}for(const p of b.approaches)assert(inBounds(p)&&!blocked(p)&&!has(m.river,p),`${b.id} invalid land approach`);}
  const contacts=[...m.actors,...m.guards,...m.resources];contacts.forEach(a=>assert(inBounds(a.cell)&&!blocked(a.cell),`${id} ${a.id} footprint blocked`));assert.equal(new Set(contacts.map(a=>key(a.cell))).size,contacts.length,`${id} duplicate actor/pickup position`);
  if(id==='adventure'){
    const roadCells=new Set(m.roads.flatMap(r=>r.cells.map(key))),reached=new Set(),pending=[key(m.actors[0].cell)];
    while(pending.length){const k=pending.pop();if(reached.has(k))continue;reached.add(k);const[c,r]=k.split(',').map(Number);for(const p of [[c+1,r],[c-1,r],[c,r+1],[c,r-1]])if(roadCells.has(key(p))&&!reached.has(key(p)))pending.push(key(p));}
    const goals=[...m.sites.map(s=>s.approach),...m.resources.map(r=>r.cell),...m.guards.map(g=>g.cell)];goals.forEach(p=>assert(reached.has(key(p)),`adventure disconnected goal ${p}`));m.route.forEach(p=>assert(!has(m.guards.map(g=>g.cell),p),'sample legal preview crosses guard'));
  }else{assert.equal(m.cols,7);assert.equal(m.rows,10);assert(eq(m.actors.find(a=>a.commander).cell,[0,9]));assert.equal(m.resources.length,0);}
  geometry.push({mode:id,cols:m.cols,rows:m.rows,sites:m.sites.length,bridges:m.bridges.length,contacts:contacts.length,roadCorridors:m.roads.length,result:'PASS'});
}
const out=root+'evidence/map-space/';await mkdir(out,{recursive:true});
const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
const page=await browser.newPage({viewport:{width:1280,height:1024},deviceScaleFactor:1});
const errors=[];page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.status()>=400)errors.push(`${r.status()} ${r.url()}`)});
const checks=[];
try{
  await page.goto('http://127.0.0.1:8765/design-preview/review-map-space.html');
  for(const mode of ['adventure','tactical']){
    await page.locator(`button[data-mode=${mode}]`).click();
    for(const[width,height]of [[375,825],[825,375],[768,1024],[1280,1024]]){
      await page.setViewportSize({width,height});await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
      const result=await page.evaluate(()=>{
        const svg=document.querySelector('#map'),plane=document.querySelector('#world-plane'),matrix=svg.getScreenCTM(),stage=document.querySelector('#map-stage').getBoundingClientRect();
        const projected=(x,y)=>new DOMPoint(x,y).matrixTransform(matrix);
        const registered=[...svg.querySelectorAll('[data-anchor]')].map(el=>{const a=projected(+el.getAttribute('cx'),+el.getAttribute('cy'));const rect=el.getBoundingClientRect();const slot=svg.querySelector(`[data-slot="${el.dataset.anchor}"]`).getBoundingClientRect();return{id:el.dataset.anchor,delta:Math.hypot(a.x-(rect.x+rect.width/2),a.y-(rect.y+rect.height/2)),slotDelta:Math.hypot(a.x-(slot.x+slot.width/2),a.y-(slot.y+slot.height/2)),inside:a.x>=stage.left&&a.x<=stage.right&&a.y>=stage.top&&a.y<=stage.bottom};});
        const badButtons=[...document.querySelectorAll('button,nav a')].filter(el=>{const r=el.getBoundingClientRect();return r.width<48||r.height<48}).map(el=>el.textContent);
        const bounds=[...svg.querySelectorAll('[data-site],[data-slot]')].map(el=>{const b=el.getBoundingClientRect();return b.left>=stage.left-.1&&b.right<=stage.right+.1&&b.top>=stage.top-.1&&b.bottom<=stage.bottom+.1;});
        return{width:innerWidth,height:innerHeight,mode:svg.dataset.mode,viewBox:svg.getAttribute('viewBox'),overflow:document.documentElement.scrollWidth>innerWidth,registered,badButtons,allFootprintsInside:bounds.every(Boolean),singleWorldPlane:plane.children.length>0&&[...svg.querySelectorAll('[data-world-layer]')].every(el=>plane.contains(el)),gridCells:svg.querySelectorAll('[data-cell]').length,brokenImages:[...document.images].filter(i=>i.complete&&!i.naturalWidth).map(i=>i.src)};
      });
      assert(!result.overflow);assert.equal(result.badButtons.length,0);assert(result.singleWorldPlane&&result.allFootprintsInside);assert.equal(result.gridCells,mode==='tactical'?70:160);result.registered.forEach(a=>assert(a.delta<.01&&a.slotDelta<.01&&a.inside));assert.equal(result.brokenImages.length,0);checks.push(result);
      if(width===375||width===825)await page.locator('.blueprint').screenshot({path:out+`${mode}-${width}.png`});
    }
  }
  await page.setViewportSize({width:1280,height:1024});await page.evaluate(async()=>{await Promise.all([...document.images].map(i=>i.decode()))});await page.screenshot({path:out+'comparison-tactical-1280.png',fullPage:true});
  await page.locator('button[data-mode=adventure]').click();await page.locator('#reference').evaluate(i=>i.decode());await page.screenshot({path:out+'comparison-adventure-1280.png',fullPage:true});
  await page.locator('#focus').click();const detailBefore=await page.locator('#map').getAttribute('viewBox');await page.setViewportSize({width:375,height:825});assert.equal(await page.locator('#map').getAttribute('viewBox'),detailBefore,'detail camera reset on resize');await page.locator('.blueprint').screenshot({path:out+'adventure-detail-375.png'});
  for(const layer of ['grid','footprints','routes','marks']){const before=await page.locator('#map').getAttribute('viewBox');await page.locator(`[data-layer=${layer}]`).click();assert.equal(await page.locator('#map').getAttribute('viewBox'),before);const hidden=await page.locator(`[data-toggle=${layer}]`).first().getAttribute('data-hidden');assert.equal(hidden,layer==='grid'?'false':'true');await page.locator(`[data-layer=${layer}]`).click();}
  await page.locator('#overview').click();assert.equal(await page.locator('#map').getAttribute('data-camera'),'overview');
  const colour=(a,b)=>{const lum=h=>{const cs=h.match(/../g).map(c=>parseInt(c,16)/255).map(c=>c<=.04045?c/12.92:((c+.055)/1.055)**2.4);return .2126*cs[0]+.7152*cs[1]+.0722*cs[2]};const l1=lum(a),l2=lum(b);return(Math.max(l1,l2)+.05)/(Math.min(l1,l2)+.05);};
  const contrast={body:colour('f0e7d4','111a1f'),muted:colour('d1c5ad','111a1f'),button:colour('f0e7d4','243139'),pressed:colour('f0e7d4','5b4b2c')};Object.values(contrast).forEach(c=>assert(c>=4.5));
  assert.equal(errors.length,0);
  const report={date:'2026-10-03',scope:'Static blueprint only; no game/physical-device/finished-art acceptance',geometry,checks,errors,contrast,controls:'Mode, layer and detail switches verified; detail camera preserved through resize',visualStatus:'Automated stage only; manual findings are recorded separately in MAP-SPACE-BLUEPRINT-2026-10-03.md; owner feedback pending'};
  await writeFile(out+'checks.json',JSON.stringify(report,null,2));console.log(JSON.stringify({geometry,browserCases:checks.length,errors,contrast,controls:report.controls}));
}finally{await browser.close();}
