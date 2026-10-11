// Isolated visual capture for the landscape shell. Does not touch port 4173.
import { chromium } from 'file:///C:/Users/TechnoExponent/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import { spawn } from 'node:child_process';
import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';

const root = 'C:/dev/ages-of-dominion-reborn';
const qa = path.join(root, 'qa/visual-playable-20261005');
const shots = path.join(qa, 'shots');
const port = 4317;
const liveUrl = `http://127.0.0.1:${port}`;
await mkdir(shots, { recursive: true });
const server = spawn(process.execPath, ['scripts/serve.mjs', '--port', String(port)], { cwd: root, stdio: ['ignore', 'pipe', 'pipe'] });
let log = '';
server.stdout.on('data', chunk => { log += chunk; });
server.stderr.on('data', chunk => { log += chunk; });
process.on('exit', () => server.kill());
await new Promise(resolve => setTimeout(resolve, 400));
const browser = await chromium.launch({ headless: true, executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe' });
const report = { liveUrl, port, log: log.trim(), errors: [], shots: [], checks: [] };

function check(id, pass, detail = {}) {
  report.checks.push({ id, pass: Boolean(pass), ...detail });
  if (!pass) report.errors.push(id);
}

async function shot(page, name) {
  const file = path.join(shots, name + '.png');
  await page.screenshot({ path: file });
  const bytes = await readFile(file);
  report.shots.push({ name, file: path.relative(root, file).replaceAll('\\', '/'), sha256: createHash('sha256').update(bytes).digest('hex'), bytes: bytes.length });
}

async function boot(width, height) {
  const context = await browser.newContext({ viewport: { width, height } });
  const page = await context.newPage();
  page.on('pageerror', error => report.errors.push(String(error)));
  await page.goto(liveUrl);
  return { context, page };
}

const home = await boot(1280, 720);
await home.page.waitForSelector('#gate-title');
check('home-title', (await home.page.locator('#gate-title').innerText()) === 'Ages of Dominion');
check('home-no-schematic', await home.page.evaluate(() => !document.querySelector('[data-articulation="schematic"]')));
check('home-actions', await home.page.evaluate(() => ['new-campaign', 'open-load', 'open-settings'].every(id => document.querySelector(`#gate-actions [data-choice="${id}"]`))));
await shot(home.page, 'home-1280x720');
await home.context.close();

for (const [width, height] of [[825, 375], [933, 424], [1180, 820]]) {
  const sized = await boot(width, height);
  await sized.page.waitForSelector('#gate-title');
  await shot(sized.page, `home-${width}x${height}`);
  await sized.context.close();
}

const play = await boot(1280, 720);
await play.page.locator('#gate-actions [data-choice="new-campaign"]').click();
try {
  await play.page.waitForSelector('[data-class-card]', { timeout: 8000 });
} catch (error) {
  const info = await play.page.evaluate(() => ({
    view: document.querySelector('#app')?.dataset.view,
    status: document.querySelector('#status')?.textContent,
    message: document.querySelector('#message')?.textContent,
    selected: document.querySelector('#selected')?.textContent,
    cards: document.querySelectorAll('[data-class-card]').length,
    html: document.querySelector('#world')?.innerHTML.slice(0, 500) || '',
  }));
  console.log('HERO-DEBUG ' + JSON.stringify(info));
  await shot(play.page, 'debug-hero');
  throw error;
}
check('class-cards', await play.page.locator('[data-class-card]').count() >= 8);
check('hero-no-schematic', await play.page.evaluate(() => !document.querySelector('[data-articulation="schematic"]')));
await shot(play.page, 'hero-class-1280x720');
await play.page.locator('[data-choice="class:knight"]').first().click();
await play.page.locator('[data-choice="enter-valley"]').first().click();
await play.page.waitForSelector('[data-pad-state]');
check('kingdom-pads', await play.page.evaluate(() => document.querySelector('[data-presentation="kingdom-pad-state-v2"]') && document.querySelector('#terrain')?.dataset.terrainStatus === 'baked-unaccepted'));
await shot(play.page, 'kingdom-stone-1280x720');
async function openNav(page, name) {
  const node = page.locator(`[data-choice="nav:${name}"]`);
  if (await node.getAttribute('data-nav') === 'more') {
    const more = page.locator('[data-choice="nav-more"]');
    if ((await more.innerText()) !== 'Fewer') await more.click();
  }
  await node.click();
}
await openNav(play.page, 'adventure');
await play.page.waitForTimeout(200);
check('adventure-painted', await play.page.evaluate(() => document.querySelector('#world')?.dataset.board === 'adventure-painted-v1'));
await shot(play.page, 'adventure-1280x720');
await openNav(play.page, 'army');
check('army-still', await play.page.evaluate(() => ![...document.querySelectorAll('[data-plate-motion]')].some(node => node.dataset.plateMotion === 'walk')));
await shot(play.page, 'army-1280x720');
await openNav(play.page, 'forge');
check('forge-slots', await play.page.evaluate(() => document.querySelectorAll('[data-slot]').length === 6 && document.querySelector('[data-slot-icon]')));
await shot(play.page, 'forge-1280x720');
await openNav(play.page, 'story');
await shot(play.page, 'story-1280x720');
await openNav(play.page, 'market');
await shot(play.page, 'market-1280x720');
await openNav(play.page, 'settings');
await shot(play.page, 'settings-1280x720');
await openNav(play.page, 'defense');
check('defense-painted', await play.page.evaluate(() => document.querySelector('#world')?.dataset.board === 'defense-painted-v1'));
await shot(play.page, 'defense-1280x720');
await openNav(play.page, 'war');
await shot(play.page, 'war-1280x720');
if (!(await play.page.locator('#panel').evaluate(node => node.classList.contains('open')))) await play.page.locator('#context').click();
await play.page.getByRole('button', { name: 'Skirmish', exact: true }).click();
await play.page.waitForTimeout(400);
check('tactical-painted', await play.page.evaluate(() => document.querySelector('#world')?.dataset.board === 'tactical-painted-v1'));
await shot(play.page, 'tactical-1280x720');
await play.page.locator('[data-choice="retreat"]').first().click();
await play.page.waitForSelector('#retreat:not([hidden])');
const modal = await play.page.evaluate(() => ({
  dockInert: document.querySelector('#dock').inert,
  worldInert: document.querySelector('#world').inert,
  focus: document.activeElement?.id || '',
}));
check('retreat-inert', modal.dockInert && modal.worldInert && modal.focus === 'retreat-cancel', modal);
await play.page.keyboard.press('Tab');
check('retreat-tab', await play.page.evaluate(() => document.activeElement?.id === 'retreat-confirm'));
await play.page.keyboard.press('Shift+Tab');
check('retreat-shift-tab', await play.page.evaluate(() => document.activeElement?.id === 'retreat-cancel'));
await shot(play.page, 'retreat-1280x720');
await play.page.keyboard.press('Escape');
check('retreat-escape', await play.page.evaluate(() => document.querySelector('#retreat').hidden && document.querySelector('#dock').inert === false));
await play.context.close();

const phone = await boot(500, 900);
check('portrait-rotate', await phone.page.evaluate(() => getComputedStyle(document.querySelector('#app')).display === 'none' && getComputedStyle(document.querySelector('#rotate')).display !== 'none'));
await shot(phone.page, 'portrait-500x900');
await phone.context.close();

await browser.close();
server.kill();
const gallery = `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Visual playable review</title>
<style>body{font-family:Segoe UI,sans-serif;background:#14110e;color:#f4ecdf;margin:24px}figure{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:0 0 28px}img{width:100%;background:#000}h1,h2{font-family:Palatino,Georgia,serif}</style></head>
<body>
<h1>Ages of Dominion — runtime review</h1>
<p>Live game: <a href="${liveUrl}">${liveUrl}</a>. Launch: <code>node scripts/serve.mjs --port ${port}</code> with the verified Node 24 executable. This page is a local gallery. It is not the game.</p>
<p>Registration of the painted grounds remains UNVERIFIED. Empty kingdom sites are outlines, not accepted geometry.</p>
${[
  ['Home', 'design-preview/generated/landscape-mocks-20261003-efcd7a7e/images/01-home.jpg', 'home-1280x720'],
  ['Hero and class', 'design-preview/generated/landscape-mocks-20261003-efcd7a7e/images/19-hero-equipment.jpg', 'hero-class-1280x720'],
  ['Kingdom', 'design-preview/generated/landscape-mocks-20261003-efcd7a7e/images/02-kingdom-day1.jpg', 'kingdom-stone-1280x720'],
  ['Adventure', 'design-preview/generated/landscape-mocks-20261003-efcd7a7e/images/11-adventure-overview.jpg', 'adventure-1280x720'],
  ['Army', 'design-preview/generated/landscape-mocks-20261003-efcd7a7e/images/24-army.jpg', 'army-1280x720'],
  ['Forge', 'design-preview/generated/landscape-mocks-20261003-efcd7a7e/images/22-forge.jpg', 'forge-1280x720'],
  ['Tactical', 'design-preview/generated/landscape-mocks-20261003-efcd7a7e/images/15-tactical-action.jpg', 'tactical-1280x720'],
  ['Defense', 'design-preview/generated/landscape-mocks-20261003-efcd7a7e/images/17-defense-preparation.jpg', 'defense-1280x720'],
  ['Story', 'design-preview/generated/landscape-mocks-20261003-efcd7a7e/images/25-story.jpg', 'story-1280x720'],
  ['Settings', 'design-preview/generated/landscape-mocks-20261003-efcd7a7e/images/28-settings.jpg', 'settings-1280x720'],
].map(([title, reference, name]) => `<h2>${title}</h2><figure><img src="../../${reference}" alt="Approved landscape reference"><img src="shots/${name}.png" alt="Runtime ${title}"></figure>`).join('\n')}
</body></html>`;
await writeFile(path.join(qa, 'gallery.html'), gallery);
await writeFile(path.join(qa, 'report.json'), JSON.stringify(report, null, 2));
console.log(JSON.stringify({ errors: report.errors, checks: report.checks.map(item => item.id + ':' + item.pass), shots: report.shots.length, log: report.log }, null, 2));
if (report.errors.length) process.exit(1);
