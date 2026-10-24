import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
import assert from 'node:assert/strict';

const root = process.cwd();
const out = `${root}/qa/game-completion-20261019/visual-review/hero-details`;
await fs.mkdir(out, { recursive: true });
const browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
const report = { recordedAt: new Date().toISOString(), url: 'http://127.0.0.1:4179/', viewports: [], errors: [] };
for (const viewport of [{ name: '1280x720', width: 1280, height: 720 }, { name: '825x375', width: 825, height: 375 }]) {
  const context = await browser.newContext({ viewport: { width: viewport.width, height: viewport.height } });
  const page = await context.newPage();
  page.on('pageerror', error => report.errors.push({ viewport: viewport.name, error: String(error) }));
  page.on('console', message => { if (message.type() === 'error') report.errors.push({ viewport: viewport.name, error: message.text() }); });
  await page.goto(report.url, { waitUntil: 'networkidle' });
  async function click(choice) {
    const node = page.locator(`[data-choice="${choice}"]`).first();
    await node.waitFor({ state: 'visible', timeout: 5000 }).catch(() => {
      throw new Error(`Unavailable control ${choice} at ${viewport.name}; no visible control appeared`);
    });
    if (await node.isDisabled()) throw new Error(`Disabled control ${choice} at ${viewport.name}`);
    await node.click();
  }
  async function capture(name) {
    await page.waitForTimeout(100);
    const file = `${out}/${name}-${viewport.name}.png`;
    await page.screenshot({ path: file });
    return file.slice(root.length + 1);
  }
  await click('new-campaign');
  await click('scene-class:paladin');
  await click('scene-enter-valley');
  await click('nav:hero');
  const base = await capture('hero-standing');
  await click('inspect:hero');
  const skills = await capture('hero-skills');
  const skillReport = await page.locator('#choices .hero-sigil-grid button.sigil').evaluateAll(nodes => nodes.map(node => ({ label: node.getAttribute('aria-label'), width: node.getBoundingClientRect().width, height: node.getBoundingClientRect().height, imageLoaded: node.querySelector('img')?.naturalWidth > 0 })));
  assert.equal(skillReport.length, 9, `all nine skills are present at ${viewport.name}`);
  const skillsBeforeScroll = await page.locator('#panel').evaluate(node => ({ top: node.scrollTop, max: node.scrollHeight - node.clientHeight }));
  await page.locator('#choices .hero-sigil-grid button.sigil:last-child').scrollIntoViewIfNeeded();
  const skillsAfterScroll = await page.locator('#panel').evaluate(node => {
    const last = node.querySelector('#choices .hero-sigil-grid button.sigil:last-child').getBoundingClientRect();
    const view = node.getBoundingClientRect();
    return { top: node.scrollTop, max: node.scrollHeight - node.clientHeight, viewport: [view.top, view.bottom], last: [last.top, last.bottom], lastSkillVisible: last.top >= view.top && last.bottom <= view.bottom };
  });
  assert.equal(skillsAfterScroll.lastSkillVisible, true, `last skill stays reachable by scrolling at ${viewport.name}`);
  const skillsScrolled = await capture('hero-skills-scrolled');
  await click('hero-tab:spells');
  await page.locator('#panel').evaluate(node => { node.scrollTop = 0; });
  const spells = await capture('hero-spells');
  const spellReport = await page.locator('#choices .hero-spell-grid button.sigil').evaluateAll(nodes => nodes.map(node => ({ label: node.getAttribute('aria-label'), disabled: node.getAttribute('aria-disabled') === 'true', width: node.getBoundingClientRect().width, height: node.getBoundingClientRect().height, imageLoaded: node.querySelector('img')?.naturalWidth > 0 })));
  assert.equal(spellReport.length, 8, `all eight spells are present at ${viewport.name}`);
  const spellsBeforeScroll = await page.locator('#panel').evaluate(node => ({ top: node.scrollTop, max: node.scrollHeight - node.clientHeight }));
  await page.locator('#choices .hero-spell-grid button.sigil:last-child').scrollIntoViewIfNeeded();
  const spellsAfterScroll = await page.locator('#panel').evaluate(node => {
    const last = node.querySelector('#choices .hero-spell-grid button.sigil:last-child').getBoundingClientRect();
    const view = node.getBoundingClientRect();
    return { top: node.scrollTop, max: node.scrollHeight - node.clientHeight, viewport: [view.top, view.bottom], last: [last.top, last.bottom], lastSpellVisible: last.top >= view.top && last.bottom <= view.bottom };
  });
  assert.equal(spellsAfterScroll.lastSpellVisible, true, `last spell stays reachable by scrolling at ${viewport.name}`);
  const spellsScrolled = await capture('hero-spells-scrolled');
  await page.locator('#panel').evaluate(node => { node.scrollTop = 0; });
  const slotChoices = await page.locator('#scene-ui.hero button[data-hero-slot]').evaluateAll(nodes => nodes.map(node => node.dataset.choice));
  assert.equal(slotChoices.length, 6, 'all six equipment sockets are present');
  await click(slotChoices.find(choice => choice.endsWith(':weapon')));
  const weaponDetail = await capture('hero-weapon-empty-detail');
  const menuActions = await page.locator('#choices button[data-choice]').evaluateAll(nodes => nodes.map(node => ({ choice: node.dataset.choice, label: node.getAttribute('aria-label') || node.innerText.trim(), disabled: node.disabled, rect: (() => { const r = node.getBoundingClientRect(); return [Math.round(r.x), Math.round(r.y), Math.round(r.width), Math.round(r.height)]; })() })));
  report.viewports.push({ name: viewport.name, captures: { base, skills, skillsScrolled, spells, spellsScrolled, weaponDetail }, sixSlots: slotChoices, skills: skillReport, spells: spellReport, skillsBeforeScroll, skillsAfterScroll, spellsBeforeScroll, spellsAfterScroll, weaponActions: menuActions, panel: await page.locator('#panel').evaluate(node => ({ scrollHeight: node.scrollHeight, clientHeight: node.clientHeight, scrollWidth: node.scrollWidth, clientWidth: node.clientWidth })) });
  await context.close();
}
await fs.writeFile(`${out}/hero-details.json`, JSON.stringify(report, null, 2));
console.log(JSON.stringify({ viewports: report.viewports.map(item => ({ name: item.name, skillCount: item.skills.length, spellCount: item.spells.length, brokenSkillArt: item.skills.filter(skill => !skill.imageLoaded).length, brokenSpellArt: item.spells.filter(spell => !spell.imageLoaded).length, actionCount: item.weaponActions.length })), errors: report.errors }, null, 2));
await browser.close();
