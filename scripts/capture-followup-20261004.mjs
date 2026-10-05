import { spawn } from 'node:child_process';
import { mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';

const port = 4182;
const base = `http://127.0.0.1:${port}`;
const outDir = fileURLToPath(new URL('../qa/code-ready-20261004/followup/', import.meta.url));
await mkdir(outDir, { recursive: true });
const server = spawn(process.execPath, ['scripts/serve.mjs', '--port', String(port)], { stdio: ['ignore', 'pipe', 'pipe'] });
process.on('exit', () => server.kill());
await new Promise((resolve, reject) => {
  const timer = setTimeout(() => reject(new Error('preview server did not start')), 5000);
  server.stdout.on('data', chunk => {
    if (String(chunk).includes(String(port))) {
      clearTimeout(timer);
      resolve();
    }
  });
  server.stderr.on('data', chunk => {
    if (String(chunk).includes('already in use')) {
      clearTimeout(timer);
      reject(new Error(String(chunk)));
    }
  });
});

const report = { started: new Date().toISOString(), base, failures: [], steps: [] };
const browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
const page = await browser.newPage({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1 });
page.on('dialog', dialog => dialog.accept());

async function shot(name) {
  const buffer = await page.screenshot({ type: 'png' });
  await writeFile(path.join(outDir, name), buffer);
  return crypto.createHash('sha256').update(buffer).digest('hex');
}
async function clickChoice(choice) {
  if (!await page.locator('#panel').evaluate(node => node.classList.contains('open'))) await page.click('#context');
  await page.evaluate(id => {
    const node = document.querySelector(`[data-choice="${id}"]`);
    if (!node) throw new Error('missing choice ' + id);
    node.click();
  }, choice);
}

await page.goto(base + '/', { waitUntil: 'networkidle' });
await page.evaluate(() => localStorage.clear());
await page.reload({ waitUntil: 'networkidle' });
await clickChoice('new-campaign');
await clickChoice('class:ranger');
await clickChoice('nav:army');
await clickChoice('plate-review-next');
await clickChoice('plate-review-next');
if (await page.locator('#panel').evaluate(node => node.classList.contains('open'))) await page.click('#context');
report.steps.push({ name: 'iron-captions', sha256: await shot('01-iron-captions.png'), reviews: await page.locator('[data-plate-review]').evaluateAll(nodes => nodes.map(node => node.getAttribute('data-plate-review'))) });
if (!report.steps[0].reviews.includes('2-melee')) report.failures.push('iron melee caption missing');

await clickChoice('nav:adventure');
await clickChoice('enter-adventure');
await page.waitForTimeout(400);
if (await page.locator('#panel').evaluate(node => node.classList.contains('open'))) await page.click('#context');
const mount = await page.locator('[data-mount-status]').evaluateAll(nodes => nodes.map(node => ({
  status: node.getAttribute('data-mount-status'),
  gait: node.getAttribute('data-gait'),
  hooves: node.getAttribute('data-hoof-articulation'),
})));
const rider = await page.locator('[data-rider="painted-partial"]').count();
report.steps.push({ name: 'mounted-review', sha256: await shot('02-mounted-review.png'), mount, rider });
if (!mount.some(row => row.status === 'BOUNDED_REVIEW_SAMPLE_RESIDUAL_HAIRLINE' && row.gait === 'single-pose')) report.failures.push('review horse missing');
if (!rider) report.failures.push('painted rider missing');

report.finished = new Date().toISOString();
await writeFile(path.join(outDir, 'report.json'), JSON.stringify(report, null, 2));
await browser.close();
server.kill();
if (report.failures.length) {
  console.error(JSON.stringify(report.failures));
  process.exit(1);
}
console.log('follow-up capture passed');
