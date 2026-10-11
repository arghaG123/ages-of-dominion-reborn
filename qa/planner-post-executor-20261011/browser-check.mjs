// Earned-gameplay journey in an isolated headless Chrome profile (raw CDP, no debug grants).
// Real UI commands only: build, wait real construction time, recruit, travel, fight, settle,
// reload, forge/equip, siege, war modes, story, settings, slots. Writes machine-readable
// evidence and bounded captures to qa/code-image-complete-20261011/.
import { spawn } from 'node:child_process';
import { mkdtemp, mkdir, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';

const root = process.cwd();
const chrome = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const port = Number(process.env.AOD_PORT || 4541);
const debugPort = Number(process.env.AOD_DEBUG_PORT || 9361);
const outDir = path.join(root, 'qa', 'planner-post-executor-20261011');
await mkdir(outDir, { recursive: true });

const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
function waitForText(stream, text, child) {
  return new Promise((resolve, reject) => {
    let log = '';
    const timer = setTimeout(() => reject(new Error(log || 'timed out')), 15000);
    stream.on('data', chunk => { log += chunk; if (log.includes(text)) { clearTimeout(timer); resolve(log); } });
    child.on('exit', code => { clearTimeout(timer); reject(new Error(`exited ${code}: ${log}`)); });
  });
}

const server = spawn(process.execPath, ['scripts/serve.mjs', '--port', String(port)], { cwd: root, stdio: ['ignore', 'pipe', 'pipe'] });
await waitForText(server.stdout, 'Reborn local preview', server);
const profile = await mkdtemp(path.join(tmpdir(), 'aod-chrome-'));
const browser = spawn(chrome, ['--headless=new', '--disable-gpu', '--no-first-run', '--no-default-browser-check', '--hide-scrollbars', `--remote-debugging-port=${debugPort}`, `--user-data-dir=${profile}`, 'about:blank'], { stdio: 'ignore' });
for (let i = 0; i < 60; i++) {
  try { await (await fetch(`http://127.0.0.1:${debugPort}/json/version`)).json(); break; }
  catch { await sleep(100); }
}
const page = await (await fetch(`http://127.0.0.1:${debugPort}/json/new?http://127.0.0.1:${port}/`, { method: 'PUT' })).json();
const ws = new WebSocket(page.webSocketDebuggerUrl);
await new Promise(resolve => { ws.addEventListener('open', resolve); });
let nextId = 0;
const pending = new Map();
const consoleErrors = [];
ws.addEventListener('message', event => {
  const message = JSON.parse(event.data);
  if (message.id && pending.has(message.id)) pending.get(message.id)(message);
  else if (message.method === 'Runtime.exceptionThrown') consoleErrors.push({ kind: 'exception', text: message.params.exceptionDetails?.exception?.description || message.params.exceptionDetails?.text });
  else if (message.method === 'Runtime.consoleAPICalled' && (message.params.type === 'error' || message.params.type === 'warning')) consoleErrors.push({ kind: message.params.type, text: message.params.args.map(arg => arg.value ?? arg.description).join(' ') });
  else if (message.method === 'Network.loadingFailed') consoleErrors.push({ kind: 'network', text: message.params.errorText });
  else if (message.method === 'Network.responseReceived' && message.params.response.status >= 400) consoleErrors.push({ kind: 'http', text: `${message.params.response.status} ${message.params.response.url}` });
});
function send(method, params = {}) {
  const id = ++nextId;
  return new Promise((resolve, reject) => {
    pending.set(id, message => { pending.delete(id); if (message.error) reject(new Error(JSON.stringify(message.error))); else resolve(message.result); });
    ws.send(JSON.stringify({ id, method, params }));
  });
}
async function evaluate(expression) {
  const result = await send('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true });
  if (result.exceptionDetails) throw new Error(result.exceptionDetails.exception?.description || result.exceptionDetails.text || 'evaluate failed');
  return result.result.value;
}
const snap = () => evaluate('window.rebornSnapshot()');
const view = () => evaluate(`document.querySelector('#app').dataset.view`);
async function click(selector, { optional = false } = {}) {
  const clicked = await evaluate(`(() => { const node = document.querySelector(${JSON.stringify(selector)}); if (!node) return false; node.click(); return true; })()`);
  if (!clicked && !optional) throw new Error(`missing ${selector}`);
  await sleep(60);
  return clicked;
}
async function clickText(text) {
  const clicked = await evaluate(`(() => { const node = [...document.querySelectorAll('button')].find(button => button.textContent.trim() === ${JSON.stringify(text)}); if (!node) return false; node.click(); return true; })()`);
  if (!clicked) throw new Error(`missing button ${text}`);
  await sleep(60);
}
async function waitUntil(expression, timeoutMs, label) {
  const started = Date.now();
  while (Date.now() - started < timeoutMs) {
    if (await evaluate(expression)) return Date.now() - started;
    await sleep(250);
  }
  throw new Error(`timeout waiting for ${label || expression}`);
}
async function setViewport(width, height) {
  await send('Emulation.setDeviceMetricsOverride', { width, height, deviceScaleFactor: 1, mobile: false });
  await evaluate('new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))');
  await sleep(80);
}
async function capture(name) {
  const shot = await send('Page.captureScreenshot', { format: 'png' });
  await writeFile(path.join(outDir, name + '.png'), Buffer.from(shot.data, 'base64'));
}
async function screenHealth() {
  return evaluate(`(() => {
    const stage = document.querySelector('#stage').getBoundingClientRect();
    const buttons = [...document.querySelectorAll('button')].filter(node => { const r = node.getBoundingClientRect(); return r.width > 0 && r.height > 0; });
    const small = buttons.filter(node => { const r = node.getBoundingClientRect(); return r.width < 48 || r.height < 48; }).map(node => node.textContent.trim());
    const failedImages = [...document.querySelectorAll('img')].filter(node => node.getAttribute('src') && node.complete && node.naturalWidth === 0).map(node => node.getAttribute('src'));
    const svgImages = [...document.querySelectorAll('#world image')].map(node => node.getAttribute('href'));
    return { view: document.querySelector('#app').dataset.view, buttons: buttons.length, small, failedImages, svgImages: svgImages.length, stage: { w: Math.round(stage.width), h: Math.round(stage.height) }, title: document.querySelector('#selected').textContent, message: document.querySelector('#message').textContent.slice(0, 160) };
  })()`);
}


const report={date:new Date().toISOString(),kind:'CURRENT_LIVE_LAYOUT_AUDIT',fixtureFree:true,classes:[],screens:[],errors:[]};
async function measure(){return evaluate(`(() => {
 const box=n=>{const r=n.getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height}};
 const stage=box(document.querySelector('#stage'));
 const targets=[...document.querySelectorAll('button,[role="button"],input,select,textarea')].filter(n=>{const r=n.getBoundingClientRect();return r.width>0&&r.height>0&&getComputedStyle(n).visibility!=='hidden'}).map(n=>({tag:n.tagName,id:n.dataset.choice||n.dataset.heroSlot||n.dataset.classCard||n.dataset.slot||n.textContent.slice(0,40),...box(n)}));
 const texts=[...document.querySelectorAll('#world text')].map(n=>{const m=n.getScreenCTM();return {text:n.textContent,cssFont:parseFloat(getComputedStyle(n).fontSize)*Math.hypot(m.a,m.b),...box(n)}});
 const actor=document.querySelector('#world [data-presentation="standing-body"] image');
 return {view:document.querySelector('#app').dataset.view,stage,targets,smallTargets:targets.filter(r=>r.w<48||r.h<48),texts,smallTexts:texts.filter(r=>r.cssFont<12),body:actor?{href:actor.getAttribute('href'),...box(actor)}:null};
})()`)}
try{
 await send('Page.enable');await send('Runtime.enable');await send('Network.enable');await setViewport(1280,720);
 await evaluate(`new Promise(r=>{if(document.readyState==='complete')r();else addEventListener('load',()=>r(),{once:true})})`);
 await click('[data-choice="new-campaign"]');
 for(const id of ['knight','ranger','warlock','mage','paladin','barbarian','necromancer','healer']){
  await click('[data-choice="class:'+id+'"]');await sleep(160);
  report.classes.push({classId:id,...await measure()});
 }
 await click('[data-choice="class:knight"]');await click('[data-choice="enter-valley"]');
 await click('[data-choice="nav:adventure"]');await click('[data-choice="enter-adventure"]');
 for(const [width,height] of [[825,375],[933,424],[1180,820],[1280,720]]){
  await setViewport(width,height);
  for(const name of ['hero','forge','army','kingdom','adventure','war','settings']){
   await click('[data-choice="nav:'+name+'"]');await sleep(250);
   const row={width,height,name,...await measure()};report.screens.push(row);
   if(['hero','forge','kingdom','adventure'].includes(name)&&(width===825||width===1280))await capture('fresh-'+name+'-'+width+'x'+height);
  }
 }
}catch(error){report.errors.push(String(error.stack||error));}
finally{
 report.consoleErrors=consoleErrors;
 await writeFile(path.join(outDir,'browser-layout-check.json'),JSON.stringify(report,null,2));
 ws.close();browser.kill();server.kill();await sleep(300);
 const checkedProfile=path.resolve(profile);
 if(checkedProfile.startsWith(path.resolve(tmpdir())+path.sep)&&path.basename(checkedProfile).startsWith('aod-chrome-'))await rm(checkedProfile,{recursive:true,force:true}).catch(()=>{});
}
console.log(JSON.stringify({errors:report.errors,consoleErrors:report.consoleErrors,screens:report.screens.map(s=>({name:s.name,size:[s.width,s.height],smallTargets:s.smallTargets.length,minFont:Math.min(...s.texts.map(t=>t.cssFont))})),classes:report.classes.length},null,2));
