// Design viewer: all scene layers share a source projection and root SVG camera.
const NS='http://www.w3.org/2000/svg';
let mode='adventure',detail=false;
const visible={grid:false,footprints:true,routes:true,marks:true};
function project(map,x,y,z=0){const a=map.camera.yaw*Math.PI/180,e=map.camera.elevation*Math.PI/180,u=map.camera.unit;return [u*(Math.cos(a)*x+Math.sin(a)*y),u*(Math.sin(e)*(-Math.sin(a)*x+Math.cos(a)*y)-Math.cos(e)*z)];}
function node(tag,attrs={},parent=document.querySelector('#map')){const el=document.createElementNS(NS,tag);Object.entries(attrs).forEach(([k,v])=>el.setAttribute(k,v));parent.append(el);return el;}
function points(map,list){return list.map(p=>project(map,...p).join(',')).join(' ');}
function polygon(map,rect,cls,parent,attrs={}){const[x,y,w,h]=rect;return node('polygon',{points:points(map,[[x,y],[x+w,y],[x+w,y+h],[x,y+h]]),class:cls,...attrs},parent);}
function cell(map,p,cls,parent,inset=0,attrs={}){return polygon(map,[p[0]+inset,p[1]+inset,1-2*inset,1-2*inset],cls,parent,attrs);}
function centre(p){return[p[0]+.5,p[1]+.5];}
function label(map,p,text,parent,small=false){const[x,y]=project(map,...p);const el=node('text',{x,y,class:`world-label${small?' small-label':''}`},parent);el.textContent=text;}
function route(map,cells,cls,parent){node('polyline',{points:points(map,cells.map(centre)),class:cls},parent);}
function render(){
  const map=MAP_SPACE[mode],svg=document.querySelector('#map');svg.replaceChildren();
  node('title',{id:'map-title'}).textContent=map.title;
  node('desc',{id:'map-desc'}).textContent='Planning drawing of reserved clearings, bridge approaches, obstacles and separate route/selection layers. No finished terrain or actors.';
  const defs=node('defs'),pattern=node('pattern',{id:'exclusion',patternUnits:'userSpaceOnUse',width:10,height:10},defs);node('rect',{width:10,height:10,fill:'#343b38'},pattern);node('path',{d:'M0 10 L10 0',stroke:'#947d6b','stroke-width':2},pattern);
  const scene=node('g',{id:'world-plane'}),terrain=node('g',{'data-world-layer':'terrain'},scene);
  polygon(map,[0,0,map.cols,map.rows],'terrain',terrain);
  const grid=node('g',{'data-toggle':'grid','data-hidden':!visible.grid,'data-world-layer':'grid'},scene);
  for(let r=0;r<map.rows;r++)for(let c=0;c<map.cols;c++)cell(map,[c,r],'grid',grid,0,{'data-cell':`${c},${r}`});
  node('polygon',{points:points(map,map.banks),class:'river'},terrain);map.obstacles.forEach(p=>cell(map,p,'obstacle',terrain));
  const roads=node('g',{'data-toggle':'routes','data-hidden':!visible.routes,'data-world-layer':'roads'},scene);
  map.roads.forEach(r=>route(map,r.cells,'road',roads));
  // Decks render over the river and road. Route markings render later over decks.
  scene.append(terrain,grid,roads);
  const decks=node('g',{'data-world-layer':'bridge-decks'},scene);map.bridges.forEach(b=>polygon(map,b.rect,'bridge',decks,{'data-bridge':b.id}));
  const footprints=node('g',{'data-toggle':'footprints','data-hidden':!visible.footprints,'data-world-layer':'footprints'},scene);
  (map.deployment||[]).forEach(d=>{const[x,y,w,h]=d.rect;for(let r=y;r<y+h;r++)for(let c=x;c<x+w;c++){if(!map.obstacles.some(p=>p[0]===c&&p[1]===r))cell(map,[c,r],`deploy ${d.team}`,footprints,.04);}});
  map.sites.forEach(s=>{polygon(map,s.rect,'clearing',footprints,{'data-site':s.id});const[x,y,w,h]=s.rect;polygon(map,[x+.2,y+.2,w-.4,h-.4],'site-base',footprints);cell(map,s.approach,'approach',footprints,.18);label(map,[x+.15,y+.65],s.id,footprints);});
  map.bridges.forEach(b=>b.approaches.forEach(p=>cell(map,p,'approach',footprints,.12)));
  map.actors.forEach(a=>cell(map,a.cell,'site-base',footprints,.12,{'data-slot':a.id}));
  const routeLayer=node('g',{'data-toggle':'routes','data-hidden':!visible.routes,'data-world-layer':'route-markings'},scene);route(map,map.route,'route',routeLayer);
  const marks=node('g',{'data-toggle':'marks','data-hidden':!visible.marks,'data-world-layer':'marks'},scene);
  map.resources.forEach(r=>{cell(map,r.cell,'resource',marks,.25);label(map,centre(r.cell),r.id,marks);});
  map.guards.forEach(g=>{cell(map,g.cell,'guard',marks,.3);label(map,[g.cell[0]+.2,g.cell[1]+.18],g.id,marks);});
  map.actors.forEach(a=>{const[x,y]=project(map,...centre(a.cell));node('circle',{cx:x,cy:y,r:a.commander?8:6,class:`anchor ${a.team}`,'data-anchor':a.id,'data-world':centre(a.cell).join(',')},marks);if(a.id===map.selected)cell(map,a.cell,'selection',marks,.08);label(map,[a.cell[0]+.65,a.cell[1]+.6],a.id,marks);});
  const labels=node('g',{'data-world-layer':'labels'},scene);
  map.bridges.forEach(b=>label(map,[b.rect[0],b.rect[1]-.1],b.id,labels));
  map.labels.forEach(l=>label(map,l.at,l.text,labels,true));
  const rect=detail?map.focus:[0,0,map.cols,map.rows], [x,y,w,h]=rect;
  const corners=[[x,y],[x+w,y],[x+w,y+h],[x,y+h]].map(p=>project(map,...p));
  const xs=corners.map(p=>p[0]),ys=corners.map(p=>p[1]),pad=detail?32:64;
  const box=[Math.min(...xs)-pad,Math.min(...ys)-pad,Math.max(...xs)-Math.min(...xs)+pad*2,Math.max(...ys)-Math.min(...ys)+pad*2];
  svg.setAttribute('viewBox',box.join(' '));svg.dataset.mode=mode;svg.dataset.camera=detail?'detail':'overview';
  document.querySelector('#mode-title').textContent=map.title;document.querySelector('#comparison').textContent=map.comparison;
  const ref=document.querySelector('#reference');ref.src=map.reference;ref.alt=`Owner ${mode} reference · unchanged composition evidence`;
  document.querySelector('#camera-note').textContent=`${detail?'Crossing detail; Whole region restores all sites/slots.':'Whole region; every reserved site/slot is included.'} One ${map.camera.elevation}° proposed ground-camera elevation, ${map.camera.yaw}° yaw. Resize changes the root fit only. The camera angles are calibration proposals, not measured source-art facts.`;
  const rows=[...map.sites.map(s=>[s.id,s.label,`${s.rect[0]},${s.rect[1]} · ${s.rect[2]} × ${s.rect[3]}`,`(${s.approach}) · ${s.facing}`]),...map.bridges.map(b=>[b.id,b.label,`${b.rect.join(', ')}`,b.approaches.map(p=>`(${p})`).join(' ↔ ')]),...map.resources.map(r=>[r.id,`${r.label} pickup`,`${r.cell} · 1 × 1`,'Connected side clearing']),...map.guards.map(g=>[g.id,g.label,`${g.cell} · 1 × 1`,'Encounter anchor; stop before guard']),...map.actors.map(a=>[a.id,a.label,`${a.cell} · 0.76 × 0.76 reserved`,a.commander?'Fixed commander ground anchor':a.team==='enemy'?'Face toward allied bank':'Face toward route / enemy bank'])];
  const body=document.querySelector('#placement-list');body.replaceChildren();rows.forEach(row=>{const tr=document.createElement('tr');row.forEach(value=>{const td=document.createElement('td');td.textContent=value;tr.append(td)});body.append(tr)});
  document.querySelectorAll('button[data-mode]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.mode===mode)));
  document.querySelector('#overview').setAttribute('aria-pressed',String(!detail));document.querySelector('#focus').setAttribute('aria-pressed',String(detail));
  fitLabelSize();
}
function fitLabelSize(){const svg=document.querySelector('#map'),ctm=svg.getScreenCTM();if(!ctm)return;const scale=Math.hypot(ctm.a,ctm.b),pixels=innerWidth<480?11:13;svg.querySelectorAll('.world-label').forEach(el=>{el.style.fontSize=`${pixels/scale}px`;el.style.strokeWidth=`${3/scale}px`;});}
document.querySelectorAll('button[data-mode]').forEach(b=>b.addEventListener('click',()=>{mode=b.dataset.mode;detail=false;render()}));
document.querySelector('#overview').addEventListener('click',()=>{detail=false;render()});document.querySelector('#focus').addEventListener('click',()=>{detail=true;render()});
document.querySelectorAll('[data-layer]').forEach(b=>b.addEventListener('click',()=>{visible[b.dataset.layer]=!visible[b.dataset.layer];b.setAttribute('aria-pressed',String(visible[b.dataset.layer]));render()}));
render();
new ResizeObserver(fitLabelSize).observe(document.querySelector('#map-stage'));
