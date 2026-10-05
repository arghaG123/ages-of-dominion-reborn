import {chromium} from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
try{
 const context=await browser.newContext();const page=await context.newPage();
 await page.addInitScript(()=>{
  const Native=window.AudioContext;window.qaAudioStarts=0;
  window.AudioContext=class extends Native {createOscillator(){const osc=super.createOscillator();const start=osc.start.bind(osc);osc.start=(...args)=>{window.qaAudioStarts++;return start(...args);};return osc;}};
 });
 await page.goto('http://127.0.0.1:4173');await page.waitForFunction(()=>typeof window.rebornSnapshot==='function');
 await page.getByRole('button',{name:'Settings',exact:true}).click();await page.locator('#context').click();await page.getByRole('button',{name:'Arm local audio',exact:true}).click();
 await page.waitForTimeout(500);await page.evaluate(()=>window.rebornBackground(true));
 const before=await page.evaluate(()=>window.qaAudioStarts);await page.waitForTimeout(1000);const after=await page.evaluate(()=>window.qaAudioStarts);
 const result={at:new Date().toISOString(),before,after,status:after===before?'PASS':'FAIL',scope:'Browser oscillator-start instrumentation proves scheduled motif continues after explicit app background; listening/native hearing UNVERIFIED'};
 await fs.writeFile(new URL('./audio.json',import.meta.url),JSON.stringify(result,null,2));console.log(JSON.stringify(result));await context.close();
}finally{await browser.close();}
