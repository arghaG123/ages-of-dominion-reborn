// Isolated capture of the two corrected gallery samples. Does not read or write owner browser data.
const { chromium } = require('C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs = require('node:fs/promises');
const path = require('node:path');
const out = __dirname;
const base = process.env.GALLERY_BASE;
(async () => {
  const browser = await chromium.launch({ headless: true, channel: 'msedge' });
  const context = await browser.newContext();
  const page = await context.newPage();
  const errors = [];
  page.on('pageerror', (e) => errors.push(e.message));
  page.on('response', (r) => { if (r.status() >= 400) errors.push(`${r.status()} ${r.url()}`); });
  await page.goto(base, { waitUntil: 'networkidle' });
  const catalogue = await page.evaluate(() => window.reviewCatalogue);
  const old = catalogue.filter((s) => !['kingdom-stone-recovered', 'ui-resources-offense'].includes(s.id));
  const feedback = Object.fromEntries(old.map((s, i) => [s.id, { decision: i % 2 ? 'revise' : 'keep', comment: `Isolated correction fixture ${s.id}`, updatedAt: '2026-10-03T00:00:00Z' }]));
  const key = 'aod-section-feedback-20261003-v1';
  await page.evaluate(({ key, feedback }) => localStorage.setItem(key, JSON.stringify(feedback)), { key, feedback });
  await page.reload({ waitUntil: 'networkidle' });
  await page.selectOption('#section', 'ui-resources-offense');
  await page.locator('#comment').fill('Isolated correction fixture new section');
  await page.reload({ waitUntil: 'networkidle' });
  const preserved = await page.evaluate(({ key, feedback }) => {
    const actual = JSON.parse(localStorage.getItem(key));
    return Object.keys(feedback).every((id) => JSON.stringify(actual[id]) === JSON.stringify(feedback[id]));
  }, { key, feedback });
  const results = [];
  for (const id of ['kingdom-stone-recovered', 'ui-resources-offense']) {
    for (const [width, height] of [[825, 375], [933, 424], [1180, 820], [1280, 720]]) {
      await page.setViewportSize({ width, height });
      await page.goto(`${base}?sample=1&size=${width}x${height}#${id}`, { waitUntil: 'networkidle' });
      await page.locator('#stage img').evaluateAll((imgs) => Promise.all(imgs.map((im) => im.decode())));
      const view = await page.evaluate(() => {
        const stage = document.querySelector('#stage');
        const rail = stage.querySelector('.hud-rail');
        const icon = rail ? rail.querySelector('img') : null;
        const rect = stage.getBoundingClientRect();
        const iconRect = icon ? icon.getBoundingClientRect() : null;
        const railRect = rail ? rail.getBoundingClientRect() : null;
        return {
          selected: document.querySelector('#section').value,
          stage: { width: rect.width, height: rect.height },
          icon: iconRect ? { width: iconRect.width, height: iconRect.height } : null,
          rail: railRect ? { height: railRect.height } : null,
          captionInsideStage: !!stage.querySelector('.caption'),
          overflow: document.documentElement.scrollWidth > window.innerWidth + 1 || document.documentElement.scrollHeight > window.innerHeight + 1,
        };
      });
      const file = `gallery-sample-${id}-${width}x${height}.png`;
      await page.screenshot({ path: path.join(out, file) });
      results.push({ id, width, height, file, ...view });
    }
  }
  const report = {
    scope: 'Two corrected sections, four contract sizes, isolated context',
    catalogueCount: catalogue.length,
    uniqueIds: new Set(catalogue.map((s) => s.id)).size,
    oldFixtureFeedbackPreserved: preserved,
    results,
    errors,
  };
  await fs.writeFile(path.join(out, 'gallery-capture.json'), JSON.stringify(report, null, 2) + '\n');
  console.log(JSON.stringify(report));
  await context.close();
  await browser.close();
})().catch((e) => { console.error(e); process.exitCode = 1; });
