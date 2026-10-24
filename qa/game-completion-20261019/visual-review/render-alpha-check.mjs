import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
const files=[
['Ancient Paladin','C:/Users/pupan/.codex/generated_images/01a14d31-4376-7570-bde1-ae01df1f91de/exec-9fee4070-392c-4204-9f3f-18b30b3503a7.png'],
['Mech Paladin','C:/Users/pupan/.codex/generated_images/01a14d31-4376-7570-bde1-ae01df1f91de/exec-55e0266c-a458-467b-8e00-b19bf22ad353.png']
];
const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
const page=await browser.newPage({viewport:{width:1040,height:850},deviceScaleFactor:1});
const imgs=[];
for(const [name,file] of files){const b=await fs.readFile(file);imgs.push({name,data:'data:image/png;base64,'+b.toString('base64')});}
const panels=imgs.map(x=>'<section><h2>'+x.name+'</h2><img src="'+x.data+'"></section>').join('');
await page.setContent('<!doctype html><html><head><style>html,body{margin:0;background:#101820;color:#f4e6c8;font:16px Segoe UI, sans-serif}main{display:flex;gap:8px;padding:8px}section{width:512px;height:820px;text-align:center}h2{height:32px;margin:0}img{width:512px;height:768px;object-fit:contain;background-color:#777;background-image:linear-gradient(45deg,#999 25%,transparent 25%),linear-gradient(-45deg,#999 25%,transparent 25%),linear-gradient(45deg,transparent 75%,#999 75%),linear-gradient(-45deg,transparent 75%,#999 75%);background-size:32px 32px;background-position:0 0,0 16px,16px -16px,-16px 0}</style></head><body><main>'+panels+'</main></body></html>');
await page.waitForTimeout(100);
await page.screenshot({path:'qa/game-completion-20261019/visual-review/paladin-alpha-check.png'});
console.log('wrote alpha composite check');
await browser.close();