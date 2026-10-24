import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';

const root = process.cwd();
const out = path.join(root, 'qa/game-completion-20261020/visual-review/equipment-live');
await fs.mkdir(out, { recursive: true });
const report = {
  recordedAt: new Date().toISOString(),
  classification: 'FRESH_UI_JOURNEY_CONTROLLED_BROWSER_CLOCK',
  journey: 'new campaign -> build Quarry and Armory -> advance the browser clock for legal production -> forge weapon -> compare and equip -> reload -> verify equipped weapon on the Adventure rider',
  url: 'http://127.0.0.1:4179/?audit=1',
  errors: [],
  checks: {},
  screenshots: {},
};
const browser = await chromium.launch({
  executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe',
  headless: true,
});
const context = await browser.newContext({ viewport: { width: 825, height: 375 }, deviceScaleFactor: 1 });
const page = await context.newPage();
await page.clock.install();
page.on('pageerror', error => report.errors.push(String(error)));
page.on('console', message => { if (message.type() === 'error') report.errors.push(message.text()); });

const read = () => page.evaluate(() => JSON.parse(document.querySelector('#audit-snapshot')?.textContent || 'null'));
async function clickChoice(id) {
  const control = page.locator(`[data-choice="${id}"]`).first();
  await control.waitFor({ state: 'visible', timeout: 10000 });
  assert.equal(await control.isDisabled(), false, `${id} is enabled`);
  await control.click();
}
async function waitForState(predicate, label, timeout = 20000, args = []) {
  for (let elapsed = 0; elapsed <= timeout; elapsed += 250) {
    const snapshot = await read();
    if (snapshot?.state && predicate(snapshot, ...args)) return snapshot.state;
    await page.clock.runFor(250);
  }
  throw new Error(`Timed out waiting for ${label}`);
}
async function capture(name, viewport = '825x375') {
  const file = path.join(out, `${name}-${viewport}.png`);
  await page.screenshot({ path: file });
  return path.relative(root, file);
}
async function openSite(siteId, building) {
  await page.locator('#context').click();
  await clickChoice('site-list');
  await clickChoice(`choose-site:${siteId}`);
  await clickChoice(`build:${siteId}:${building}`);
  await page.locator('#build-commit').click();
  const started = await waitForState(
    (snapshot, site, type) => snapshot?.state?.buildJobs?.some(job => job.plotId === site && job.type === type),
    `${building} construction starts`,
    20000,
    [siteId, building],
  );
  assert.ok(started.buildJobs.some(job => job.plotId === siteId && job.type === building));
  return waitForState(
    (snapshot, site, type) => snapshot?.state?.plots?.some(plot => plot.id === site && plot.type === type && plot.level === 1)
      && !snapshot.state.buildJobs.some(job => job.plotId === site),
    `${building} construction completes`,
    20000,
    [siteId, building],
  );
}

try {
  await page.goto(report.url, { waitUntil: 'networkidle' });
  await clickChoice('new-campaign');
  await clickChoice('scene-class:knight');
  await clickChoice('scene-enter-valley');
  await waitForState(snapshot => snapshot?.state?.story?.flags?.enteredValley === true, 'fresh Valley entry');

  let state = await openSite('P01', 'quarry');
  report.checks.quarry = {
    level: state.plots.find(plot => plot.id === 'P01')?.level,
    resources: { ...state.resources },
    rate: 0.35,
  };
  state = await openSite('P02', 'armory');
  report.checks.armory = {
    level: state.plots.find(plot => plot.id === 'P02')?.level,
    resources: { ...state.resources },
  };

  // Keep all game actions on the visible UI; advance only idle production time.
  await page.clock.runFor(100000);
  state = (await read()).state;
  report.checks.production = {
    stoneAvailable: state.resources.stone,
    sufficientForForge: state.resources.stone >= 60,
    controlledClockAdvanceMs: 100000,
  };
  assert.ok(report.checks.production.sufficientForForge, 'Quarry production supplies the legal forge cost');

  await page.locator('#context').click();
  await clickChoice('menu:forge');
  await clickChoice('scene-forge-slot:weapon');
  report.screenshots.forgeWeapon = await capture('forge-weapon');
  await clickChoice('inspect:forge');
  await clickChoice('forge-confirm');
  await page.locator('#build-commit').click();
  state = await waitForState(snapshot => snapshot?.state?.inventory?.some(item => item.slot === 'weapon'), 'forged weapon enters inventory');
  const item = state.inventory.find(entry => entry.slot === 'weapon');
  assert.equal(item?.age, 0, 'forged weapon belongs to the current Stone age');
  report.checks.forged = { item: { ...item }, resources: { ...state.resources } };

  await clickChoice(`equip:${item.id}`);
  await clickChoice(`equip-confirm:${item.id}`);
  state = await waitForState(
    (snapshot, id) => snapshot?.state?.hero?.equip?.weapon?.id === id,
    'weapon equips on the Hero',
    20000,
    [item.id],
  );
  assert.ok(!state.inventory.some(entry => entry.id === item.id), 'equipped item leaves the inventory');
  await clickChoice('nav:hero');
  const wearLayer = await page.locator('[data-worn-slot="weapon"]').getAttribute('data-worn-appearance');
  const wearLayerProbe = await page.locator('[data-slot-layer="weapon"] image').evaluate(node => {
    const rect = node.getBoundingClientRect();
    const box = node.getBBox();
    return {
      href: node.getAttribute('href'),
      localBox: [box.x, box.y, box.width, box.height].map(value => Math.round(value * 100) / 100),
      screenRect: [rect.x, rect.y, rect.width, rect.height].map(value => Math.round(value * 100) / 100),
      opacity: getComputedStyle(node).opacity,
      visibility: getComputedStyle(node).visibility,
    };
  });
  report.checks.equipped = {
    itemId: item.id,
    slot: state.hero.equip.weapon.slot,
    quality: state.hero.equip.weapon.quality,
    inventoryNoLongerContainsItem: !state.inventory.some(entry => entry.id === item.id),
    bodyWearAppearance: wearLayer,
    itemLayerCount: await page.locator('[data-slot-layer="weapon"]').count(),
    wearLayerProbe,
  };
  report.screenshots.heroWeaponPhone = await capture('hero-weapon-equipped');

  await page.locator('#save').click();
  await page.waitForTimeout(150);
  await page.reload({ waitUntil: 'networkidle' });
  state = await waitForState(
    (snapshot, id) => snapshot?.state?.hero?.equip?.weapon?.id === id,
    'equipped weapon survives reload',
    20000,
    [item.id],
  );
  report.checks.reload = {
    view: (await read()).view,
    equippedWeapon: state.hero.equip.weapon.id,
    slot: state.hero.equip.weapon.slot,
    inventoryCount: state.inventory.length,
  };

  if ((await read()).view === 'home' && await page.locator('[data-choice="continue"]').isVisible()) {
    await clickChoice('continue');
  }
  if ((await read()).view !== 'hero') await clickChoice('nav:hero');
  await clickChoice('nav:adventure');
  await clickChoice('enter-adventure');
  await page.locator('#world [data-worn-slot="weapon"]').waitFor({ state: 'attached', timeout: 10000 });
  const adventureWeaponAppearance = await page.locator('#world [data-worn-slot="weapon"]').getAttribute('data-worn-appearance');
  const adventureWeaponLayers = page.locator('#world [data-slot-layer="weapon"] image');
  const adventureWeaponHref = await adventureWeaponLayers.first().getAttribute('href');
  report.checks.adventureRider = {
    view: (await read()).view,
    appearance: adventureWeaponAppearance,
    layerCount: await adventureWeaponLayers.count(),
    genericWeaponJointCount: await page.locator('#world [data-actor="knight"] [data-joint="weapon"]').count(),
    href: adventureWeaponHref,
  };
  report.screenshots.adventureRider = await capture('hero-mounted-weapon');
  assert.equal(adventureWeaponAppearance, 'attached-asset', 'Adventure rider shows the equipped reviewed held prop');
  assert.equal(report.checks.adventureRider.layerCount, 1, 'Adventure rider uses one worn weapon layer');
  assert.equal(report.checks.adventureRider.genericWeaponJointCount, 0, 'Adventure rider has no duplicate generic rig weapon');
  assert.match(adventureWeaponHref || '', /flint-club-stone\.png$/, 'Adventure rider uses the reviewed Stone club art');
  await clickChoice('nav:hero');

  await page.setViewportSize({ width: 1280, height: 720 });
  await page.waitForTimeout(300);
  report.screenshots.heroWeaponDesktop = await capture('hero-weapon-equipped', '1280x720');
  report.checks.desktop = {
    viewport: [page.viewportSize().width, page.viewportSize().height],
    wornLayerCount: await page.locator('[data-slot-layer="weapon"]').count(),
    bodyRect: await page.locator('[data-presentation="standing-body"] image[data-body]').boundingBox(),
  };
} catch (error) {
  report.error = String(error);
} finally {
  report.errors = [...new Set(report.errors)];
  report.passed = !report.error
    && report.errors.length === 0
    && report.checks.quarry?.level === 1
    && report.checks.armory?.level === 1
    && report.checks.production?.sufficientForForge === true
    && report.checks.equipped?.slot === 'weapon'
    && report.checks.equipped?.inventoryNoLongerContainsItem === true
    && report.checks.reload?.equippedWeapon === report.checks.equipped?.itemId
    && report.checks.adventureRider?.appearance === 'attached-asset'
    && report.checks.adventureRider?.layerCount === 1
    && report.checks.adventureRider?.genericWeaponJointCount === 0
    && /flint-club-stone\.png$/.test(report.checks.adventureRider?.href || '')
    && report.checks.desktop?.wornLayerCount === 1;
  await fs.writeFile(path.join(out, 'natural-equipment-live-20261020.json'), JSON.stringify(report, null, 2));
  await context.close();
  await browser.close();
}
console.log(JSON.stringify({ passed: report.passed, report, output: path.join(out, 'natural-equipment-live-20261020.json') }, null, 2));
if (!report.passed) process.exitCode = 1;
