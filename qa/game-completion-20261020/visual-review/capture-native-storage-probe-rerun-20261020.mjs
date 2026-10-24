import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';

const root = process.cwd();
const output = path.join(root, 'qa/game-completion-20261020/visual-review/native-storage-probe-rerun-20261020.json');
const browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
const context = await browser.newContext({ viewport: { width: 1100, height: 800 } });
const page = await context.newPage();
const errors = [];
const notFound = [];
page.on('pageerror', error => errors.push(String(error)));
page.on('console', message => { if (message.type() === 'error') errors.push({ text: message.text(), location: message.location() }); });
page.on('response', response => { if (response.status() === 404) notFound.push({ status: response.status(), url: response.url() }); });
await page.route('**/favicon.ico', route => route.fulfill({ status: 204, body: '' }));
await page.goto('http://127.0.0.1:4179/qa/game-completion-20261018/native-storage-probes.html', { waitUntil: 'networkidle' });
await page.locator('#run').click();
await page.waitForFunction(() => document.querySelector('#result')?.textContent.includes('rows'));
const result = JSON.parse(await page.locator('#result').textContent());
const report = {
  recordedAt: new Date().toISOString(),
  classification: result.classification,
  isolation: 'fresh in-memory Playwright browser context; writes only the two named probe databases',
  rows: result.rows,
  errors,
  notFound,
};
await fs.writeFile(output, JSON.stringify(report, null, 2));
await context.close();
await browser.close();
const failures = result.rows.filter(row => row.verdict !== 'PASS_BOUNDED');
console.log(JSON.stringify({ rows: result.rows.length, passed: result.rows.length - failures.length, failed: failures, errors, notFound, report: path.relative(root, output) }, null, 2));
assert.deepEqual(errors, []);
assert.deepEqual(failures, []);
assert.deepEqual(notFound, []);
