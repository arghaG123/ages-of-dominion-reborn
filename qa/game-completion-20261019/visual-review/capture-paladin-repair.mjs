import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
for(const size of [{width:1280,height:720},{width:825,height:375}]){
 const page=await browser.newPage({viewport:size});
 const errors=[];page.on('pageerror',e=>errors.push(String(e)));
 await page.goto('http://127.0.0.1:4179/',{waitUntil:'networkidle'});
 await page.locator('[data-choice="new-campaign"]').click();
 await page.locator('[data-choice="scene-class:paladin"]').click();
 await page.locator('[data-choice="scene-enter-valley"]').click();
 await page.waitForTimeout(250);
 await page.locator('[data-choice="nav:hero"]').click();
 await page.waitForTimeout(150);
 const data=await page.evaluate(()=>({snapshot:window.rebornSnapshot?.(),body:[...document.querySelectorAll('#world [data-body]')].map(n=>({id:n.dataset.body,src:n.getAttribute('href'),bounds:[n.getAttribute('x'),n.getAttribute('y'),n.getAttribute('width'),n.getAttribute('height')]}))}));
 const name=size.width+'x'+size.height+'.png';
 await page.screenshot({path:'qa/game-completion-20261019/visual-review/paladin-ancient-hero-'+name});
 console.log(JSON.stringify({size,errors,data:{age:data.snapshot.age,class:data.snapshot.hero.class,body:data.body}}));
 await page.close();
}
await browser.close();