// Scoped enlarged-preview checks; this never opens the game.
const { chromium } = require('C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs = require('node:fs/promises');
const root='C:/dev/ages-of-dominion-reborn/qa/section-preview-20261003';
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'msedge'});
 const page=await browser.newPage();const errors=[];const results=[];
 page.on('pageerror',e=>errors.push(e.message));
 for(const [id,width,height] of [['home',1376,816],['classes',933,472],['kingdom-day1',1376,816],['tactical',1376,816]]){
  await page.setViewportSize({width,height});
  await page.goto('http://127.0.0.1:4186/design-preview/feedback-20261003/?focus=1#'+id,{waitUntil:'networkidle'});
  await page.waitForFunction(expected=>document.querySelector('#section').value===expected,id);
  await page.locator('#stage img').evaluateAll(imgs=>Promise.all(imgs.map(im=>im.complete?null:new Promise(r=>{im.onload=r;im.onerror=r}))));
  const result=await page.evaluate(()=>{
   const stage=document.querySelector('#stage').getBoundingClientRect();
   return {selected:document.querySelector('#section').value,width:stage.width,height:stage.height,ratio:stage.width/stage.height,overflow:document.documentElement.scrollWidth>innerWidth,badImages:[...document.querySelectorAll('#stage img')].filter(im=>!im.complete||!im.naturalWidth).map(im=>im.src)};
  });
  if(result.selected!==id||Math.abs(result.ratio-1376/768)>.01||result.overflow||result.badImages.length)errors.push(id+': '+JSON.stringify(result));
  await page.locator('#stage').screenshot({path:root+'/'+id+'-large.png'});
  results.push({id,viewport:{width,height},...result});
 }
 await fs.writeFile(root+'/focus-checks.json',JSON.stringify({status:errors.length?'FAIL':'PASS',results,errors},null,2)+'\n');
 await browser.close();console.log(JSON.stringify({status:errors.length?'FAIL':'PASS',results,errors}));if(errors.length)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1});
