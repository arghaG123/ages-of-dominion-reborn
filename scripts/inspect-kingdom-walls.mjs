import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import path from 'node:path';
import fs from 'node:fs/promises';
import data from '../src/data/reference-data.json' with { type: 'json' };
import contract from '../src/data/implementation-contract.json' with { type: 'json' };
import { newCampaign } from '../src/core/campaign.js';
import { encode, SAVE_KEY } from '../src/core/save.js';

const outDir = path.resolve('qa/mock-led-executor-20261016/walls-overview');
await fs.mkdir(outDir, { recursive: true });

const browser = await chromium.launch({
  executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe',
  headless: true
});

const scenarios = [
  { name: '01-stone-walls-0-unbuilt', age: 0, wallLevel: 0, job: false },
  { name: '02-stone-walls-scaffold', age: 0, wallLevel: 0, job: true },
  { name: '03-stone-walls-1-built', age: 0, wallLevel: 1, job: false },
  { name: '04-stone-walls-2-upgraded', age: 0, wallLevel: 2, job: false },
  { name: '05-iron-walls-1-built', age: 2, wallLevel: 1, job: false },
  { name: '06-iron-walls-2-upgraded', age: 2, wallLevel: 2, job: false },
  { name: '07-medieval-walls-1-built', age: 3, wallLevel: 1, job: false },
  { name: '08-future-walls-1-built', age: 7, wallLevel: 1, job: false },
];

for (const sc of scenarios) {
  const page = await browser.newPage({ viewport: { width: 1376, height: 768 } });
  const campaign = newCampaign(contract, data, Date.now(), 42);
  campaign.age = sc.age;
  campaign.walls.level = sc.wallLevel;
  if (sc.job) {
    campaign.buildJobs.push({
      id: 'job-walls',
      plotId: 'walls',
      type: 'walls',
      targetLevel: sc.wallLevel + 1,
      completesAt: Date.now() + 60000,
    });
  }
  const encoded = encode(campaign, data);
  await page.goto('http://127.0.0.1:4173/', { waitUntil: 'domcontentloaded' });
  await page.evaluate(({ key, saveStr }) => {
    localStorage.clear();
    localStorage.setItem(key, saveStr);
    localStorage.setItem(key + '-view', 'kingdom');
  }, { key: SAVE_KEY, saveStr: encoded });

  await page.reload({ waitUntil: 'networkidle' });
  await page.waitForTimeout(400);

  // Ensure inspector/panel is closed
  const panelOpen = await page.evaluate(() => document.querySelector('#panel')?.classList.contains('open'));
  if (panelOpen) {
    await page.click('#context');
    await page.waitForTimeout(200);
  }

  const shotPath = path.join(outDir, `${sc.name}.png`);
  await page.screenshot({ path: shotPath });
  console.log(`Saved screenshot: ${shotPath}`);
  await page.close();
}

await browser.close();
