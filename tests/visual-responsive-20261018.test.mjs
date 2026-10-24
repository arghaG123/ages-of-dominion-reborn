import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import contract from '../src/data/implementation-contract.json' with { type: 'json' };
import data from '../src/data/reference-data.json' with { type: 'json' };
import { camera, coverCamera, focusPointCamera, project, wideBoardCamera, worldViewportWidth } from '../src/client/projection.js';

const main = fs.readFileSync(new URL('../src/client/main.js', import.meta.url), 'utf8');
const polish = fs.readFileSync(new URL('../src/client/polish.css', import.meta.url), 'utf8');
const game = fs.readFileSync(new URL('../src/client/game.css', import.meta.url), 'utf8');
const defense = main.slice(main.indexOf('function defense()'), main.indexOf('function story()'));

test('Adventure map image labels describe the selected campaign world without a stale generated-source claim', () => {
  assert.match(main, /campaignWorld\.title\} campaign world map/);
  assert.doesNotMatch(main, /campaignWorld\.title\} generated campaign world map/);
});

test('class choices prefer reviewed portraits and crop the age-correct body fallback', () => {
  assert.match(main, /const reviewedPortrait = portraitCard\(id, state\.age\);\s*const card = reviewedPortrait \|\| heroBody\(id, state\.age\) \|\| pendingPortrait\(id, state\.age\);/);
  assert.match(main, /if \(!reviewedPortrait\) img\.className = 'portrait-body-crop';/);
  assert.match(main, /label\.className = 'portrait-choice-label';[\s\S]*?label\.textContent = data\.CLASSES\[id\]\.n;/);
  assert.match(polish, /button\.portrait-choice img \{[^}]*object-fit: cover/);
  assert.match(polish, /button\.portrait-choice \{[^}]*height: 56px; min-width: 48px; min-height: 48px/);
  assert.match(polish, /button\.portrait-choice \.portrait-choice-label \{[^}]*font: 600 12px/);
  assert.match(polish, /img\.portrait-body-crop \{ object-position: center 8%; \}/);
  assert.match(polish, /button\.portrait-choice \.portrait-choice-label \{ font-size: 12px/);
});

test('context panel starts at the top when its screen, item or mode changes', () => {
  assert.match(main, /const panelContentKey = JSON\.stringify\(\[[\s\S]*?selectedHeroSlot, forgeSlot, forgePreview, tacticalIntent, defenseTowerId/);
  assert.match(main, /const panelContentChanged = panelContentKey !== lastPanelContentKey;/);
  assert.match(main, /const scroll = viewChanged \|\| panelContentChanged \? 0 : panel\.scrollTop;/);
});

test('resume notice is kept inside the campaign gate and never floats over play controls', () => {
  const html = fs.readFileSync(new URL('../index.html', import.meta.url), 'utf8');
  assert.match(html, /<details id="gate-report" hidden>[\s\S]*?<summary role="status">Away-time report<\/summary>[\s\S]*?<button type="button" id="gate-report-dismiss">Dismiss report<\/button>/);
  assert.match(main, /if \(resumeNote && !state\.battle && !state\.defense\) view = 'home';/);
  assert.match(polish, /#gate-report \{ margin-top: 14px;[\s\S]*?\}/);
  assert.match(polish, /#gate-report \{ margin-top: 6px; padding: 6px 8px; \}/);
  assert.doesNotMatch(html, /id="resume"/);
  assert.doesNotMatch(polish, /#resume\b/);
});

test('title backdrop stays at native frame scale for sharp raster detail', () => {
  const home = main.slice(main.indexOf('function home()'), main.indexOf("$('world').setAttribute('data-screen', 'home-gate')"));
  assert.match(home, /href: TITLE_BACKDROP,[\s\S]*?x: 0,[\s\S]*?y: 0,[\s\S]*?width: 1376,[\s\S]*?height: 768,[\s\S]*?preserveAspectRatio: 'xMidYMid meet'/);
  assert.doesNotMatch(home, /x: -260,[\s\S]*?width: 1896,[\s\S]*?height: 848/);
});

test('M01 title gate covers the compact landscape viewports without side gutters', () => {
  const frame = main.slice(main.indexOf('function measureFrame()'), main.indexOf('function fitScene()'));
  assert.match(frame, /view === 'home'[\s\S]*?coverCamera\(\[1376, 768\], worldWidth, height\)/);
  for (const [width, height] of [[825, 375], [933, 424]]) {
    const fit = coverCamera([1376, 768], width, height);
    assert.equal(fit.mode, 'cover');
    assert.ok(Math.abs(fit.offset[0]) < 1e-6, `cover is horizontally registered at ${width}x${height}`);
    assert.ok(Math.abs(fit.offset[1] + (768 * fit.scale - height) / 2) < 1e-6, `crop is centered at ${width}x${height}`);
    assert.ok(fit.offset[0] <= 0 && fit.offset[0] + 1376 * fit.scale >= width - 1e-6, `art covers width ${width}`);
    assert.ok(fit.offset[1] <= 0 && fit.offset[1] + 768 * fit.scale >= height - 1e-6, `art covers height ${height}`);
    assert.ok(fit.window[1] > 0 && fit.window[1] + fit.window[3] < 768, `top and bottom crop at ${width}x${height}`);
  }
});
test('M01 gate overlays preserve a playable Continue destination', () => {
  assert.match(main, /const RESUMABLE_SCREENS = new Set\(screens\.filter\(name => !\['home', 'settings', 'help'\]\.includes\(name\)\)\);/);
  assert.match(main, /let lastSavedView = isResumableView\(initial\.view\) \? initial\.view : 'kingdom';/);
  assert.match(main, /const destination = isResumableView\(view\) \? view : lastSavedView;/);
  assert.match(main, /return isResumableView\(lastSavedView\) \? lastSavedView : 'kingdom';/);
  assert.match(main, /if \(state && isResumableView\(view\)\) lastSavedView = view;/);
  assert.match(main, /initial\.view === 'home' \|\| isResumableView\(initial\.view\) \? initial\.view : 'home'/);
});
test('campaign gate title copy keeps restrained shadows for readable lettering', () => {
  assert.match(game, /#gate-kicker \{[\s\S]*?text-shadow: 0 1px 1px rgba\(0, 0, 0, 0\.9\);/);
  assert.match(game, /#gate-title \{[\s\S]*?text-shadow: 0 1px 2px rgba\(0, 0, 0, 0\.9\);/);
  assert.doesNotMatch(game, /0 0 24px rgba\(201, 163, 91, 0\.45\)/);
});

test('Hero equipment labels stay semantic and appear only on focus or hover', () => {
  assert.match(main, /node\.setAttribute\('aria-label', `\$\{slotName\[slot\]\}: \$\{item \? itemTitle\(item\) : 'Empty'\}`\);/);
  assert.match(polish, /#scene-ui\.hero \.hero-slot-label \{ display: none; \}/);
  assert.match(polish, /button\[data-hero-slot\]:focus-visible \.hero-slot-label,[\s\S]*?button\[data-hero-slot\]:hover \.hero-slot-label \{ display: block; \}/);
});

test('Hero summary occupies the side inspector at desktop and stays readable below the equipment on short views', () => {
  assert.match(polish, /#scene-ui\.hero \.copy \{ position: absolute; right: 18px; bottom: 112px; left: auto; transform: none; width: min\(254px, 25vw\)/);
  assert.match(polish, /#stage-field\.panel-open #scene-ui\.hero \.copy \{ display: none; \}/);
  assert.match(polish, /#scene-ui\.hero \.copy \{ right: 10px; bottom: 8px; left: auto; transform: none; width: 240px; max-width: calc\(100% - 24px\); display: block; padding: 8px 10px; \}/);
  assert.match(polish, /#scene-ui\.hero \.copy p\[data-kit-note\]::after \{[^}]*font: 600 12px\/1\.2 "Segoe UI", sans-serif/);
  assert.match(polish, /#scene-ui\.hero \.copy p\[data-kit-note\]::after \{[^}]*white-space: pre-line/);
  assert.match(main, /dataset\.mobileSummary = `\$\{data\.CLASSES\[classId\]\.n\} · Lv \$\{state\.hero\.level\}\\nATK[\s\S]*?\\nMP/);
});

test('short landscape Settings keeps every control visible below the game header', () => {
  assert.match(polish, /@media \(max-height: 500px\) \{[\s\S]*?#scene-ui\.support:has\(\[data-level\]\) \{ inset: 56px auto auto 50%; transform: translateX\(-50%\); max-height: calc\(100% - 114px\); padding: 8px; gap: 2px; \}/);
  assert.match(polish, /#scene-ui\.support:has\(\[data-level\]\) \.support-grid \{ gap: 4px; \}/);
  assert.match(polish, /#scene-ui\.support:has\(\[data-level\]\) article \{ padding: 6px 10px; \}/);
  assert.match(main, /'settings-audio'/);
  assert.match(main, /'settings-motion'/);
});

test('Settings exposes local graphics quality, honest language support, save state and a return action', () => {
  assert.match(main, /const GRAPHICS_QUALITY_KEY = 'aod\.reborn\.graphics-quality\.v1';/);
  assert.match(main, /graphicsSelect\.addEventListener\('change', \(\) => setGraphicsQuality\(graphicsSelect\.value\)\);/);
  assert.match(main, /GRAPHICS_QUALITY_VALUES\.includes\(value\)/);
  assert.match(main, /languageSelect\.disabled = true;/);
  assert.match(main, /English is the only in-game language currently available\./);
  assert.match(main, /localSave\.dataset\.saveState = saveKind;/);
  assert.match(main, /'settings-open-saves'/);
  assert.match(main, /'settings-back'/);
  assert.match(main, /settingsReturnView = screens\.includes\(returnTo\) && returnTo !== 'settings' \? returnTo : 'kingdom';/);
  assert.match(main, /view = screens\.includes\(settingsReturnView\) && settingsReturnView !== 'settings' \? settingsReturnView : 'kingdom';/);
  assert.match(main, /if \(name === 'settings'\) openSettings\(view\)/);
  assert.match(main, /openSettings\('home'\)/);
  assert.match(polish, /html\[data-graphics-quality="medium"\] #world image/);
  assert.match(polish, /html\[data-graphics-quality="low"\] #world image \{ image-rendering: crisp-edges; \}/);
  assert.match(polish, /#scene-ui\.support\.settings \.settings-options \{ grid-template-columns: repeat\(3, minmax\(0, 1fr\)\)/);
});

test('army formation cards show rank once as stars and keep the full unit label visible', () => {
  assert.ok(main.includes("const caption = fullCaption.replace(/ rank \\d+$/, '');"));
  assert.match(main, /card\.setAttribute\('aria-label', `\$\{caption\}\. Rank \$\{stack\.rank\} of 4 stars\.`\);/);
  assert.match(main, /if \(attrs\['data-stack-caption'\]\) span\.className = 'roster-unit-label';/);
  assert.match(polish, /\.roster-unit-label \{[^}]*overflow-wrap: anywhere; text-overflow: clip; white-space: normal; line-height: 1\.05/);
  assert.match(polish, /#board \.board-row\[data-army-row="roster"\] \{[^}]*justify-content: flex-start;[^}]*overscroll-behavior-x: contain;/);
  assert.match(polish, /#board \.board-row\[data-army-row="roster"\]::-webkit-scrollbar-thumb \{[^}]*background: #bfa779/);
});

test('class-selection portraits keep their hit areas clear of the Hero inspector shortcut', () => {
  assert.match(main, /detailActions\[view\] && !\(view === 'hero' && classChoiceOpen\(\)\)/);
});

test('Defense removes completed deployment actions and never labels an undeployed stack as deployed', () => {
  assert.match(defense, /if \(!session\.heroDeployed\) \{\s*\$\('choices'\)\.append\(button\(defensePad \?/);
  assert.match(defense, /if \(!session\.armyDeployed\) \{\s*for \(const stack of state\.army\)/);
  assert.doesNotMatch(defense, /session\.armyDeployed \? 'Deployed — '/);
  assert.doesNotMatch(defense, /Deploy hero — already on the field/);
});

test('Tactical setup shows the real two-sided force while only allied stacks can be moved', () => {
  assert.match(main, /for \(const stack of battle\.stacks\.filter\(item => !item\.dead && item\.count > 0\)\)/);
  assert.match(main, /const isAlly = alliedIds\.has\(stack\.id\);/);
  assert.match(main, /: document\.createElement\('div'\);/);
  assert.match(main, /Opponent formation: \$\{name\}\. Fixed at/);
  assert.match(main, /isAlly \? \(isPlaced \? 'Placed' : 'Ready'\) : 'Opponent'/);
  assert.match(polish, /\.deployment-card\[data-side="e"\] \{ border-color: #b97865; border-bottom-color: #b97865; \}/);
});

test('short-landscape deployment keeps its roster strip and 48px actions in separate rows', () => {
  assert.match(polish, /#app\[data-view="tactical"\] #scene-ui\.game-status\.battle-deployment \{ inset: auto 8px 8px auto; width: min\(340px, 36vw\); max-width: 36vw; grid-template-columns: minmax\(0, 1fr\) auto; grid-template-rows: 48px auto auto;/);
  assert.match(polish, /\.deployment-card-copy strong \{ font-size: 10px; white-space: normal; text-overflow: clip; \}/);
  assert.match(polish, /\.deployment-instructions \{ grid-column: 1 \/ -1; grid-row: 2; font-size: 9px; \}/);
  assert.match(polish, /\.deployment-roster \{ grid-column: 1 \/ -1; grid-row: 3; \}/);
  assert.match(polish, /\.deployment-actions \{ grid-column: 2; grid-row: 1; display: flex; align-items: center;/);
  assert.match(polish, /\.deployment-actions button \{ min-height: 48px; padding: 6px 8px; font-size: 10px; \}/);
});

test('Hero skills and spellbook have separate, compact and accessible workspaces', () => {
  assert.match(main, /let heroDetailTab = 'skills';/);
  assert.match(main, /tabs\.setAttribute\('aria-label', 'Hero details'\)/);
  assert.match(main, /node\.setAttribute\('aria-pressed', String\(heroDetailTab === id\)\)/);
  assert.match(main, /skills\.className = 'sigil-grid hero-sigil-grid';/);
  assert.match(main, /spells\.className = 'sigil-grid hero-sigil-grid hero-spell-grid';/);
  assert.match(main, /node\.dataset\.skillOffer = offered \? 'available' : 'not-offered';/);
  assert.match(main, /offerBadge\.textContent = 'OFFER';/);
  assert.match(main, /stateBadge\.textContent = eligible \? 'LOW MP' : 'WIS ' \+ \(spell\.lv - 1\);/);
  assert.match(main, /node\.setAttribute\('aria-label', spell\.n \+ '\. ' \+ spell\.d \+ ' ' \+ availability \+ ' Current mana '/);
  assert.match(polish, /#choices \.hero-sigil-grid \{ grid-template-columns: repeat\(3, minmax\(0, 1fr\)\)/);
  assert.match(polish, /#choices \.hero-spell-grid \{ grid-template-columns: repeat\(4, minmax\(0, 1fr\)\)/);
  assert.match(polish, /#choices \.hero-stat-grid \{ display: grid; grid-template-columns: repeat\(2, minmax\(0, 1fr\)\)/);
  assert.match(polish, /\.hero-spell-grid button\.sigil img \{[^}]*border-radius: 50%/);
  assert.match(polish, /button\.sigil\[data-skill-offer="available"\] \{[^}]*#edcd77/);
  assert.match(polish, /hero-spell-grid button\.sigil \.sigil-name \{[^}]*-webkit-line-clamp: 2[^}]*white-space: normal/);
  assert.match(polish, /hero-spell-grid button\.sigil \.sigil-lock-badge \{/);
});

test('Forge opens its M22 recipe panel with four quality tiers and a reachable six-slot rail', () => {
  assert.match(polish, /#scene-ui\.support:has\(\[data-war-mode\]\) \.support-grid \{[^}]*grid-template-columns: repeat\(5, minmax\(0, 1fr\)\)/);
  assert.match(main, /choiceHeading\('Forge menu'\)/);
  assert.match(main, /for \(let qualityIndex = 0; qualityIndex <= 3; qualityIndex \+= 1\)/);
  assert.match(main, /choice\.dataset\.forgeQualityLocked = 'true'/);
  assert.match(main, /Requires Armory level \$\{requiredArmory\}/);
  assert.match(main, /if \(view === 'forge' && \(forgePreview \|\| viewChanged\)\) setPanel\(true\);/);
  assert.match(polish, /#app\[data-view="forge"\] #panel \{\s*top: 78px;\s*right: 162px;\s*bottom: 78px;/);
  assert.match(polish, /#scene-ui\.forge \.forge-slots \{[^}]*grid-template-columns: repeat\(2, 62px\)/);
  assert.match(polish, /#app\[data-view="forge"\] #choices > button\[data-forge-quality-current="true"\]/);
  assert.match(polish, /#app\[data-view="forge"\] #choices > button\[data-forge-quality-locked="true"\]/);
  assert.match(main, /dock && !\$\('panel'\)\.classList\.contains\('open'\)/);
  assert.match(main, /forge-return-kingdom/);
  assert.match(main, /dataset\.forgeActionOnly = String\(forgeActionOnly\)/);
  for (const width of [825, 933, 1280]) {
    const panelWidth = Math.min(304, width * 0.27);
    const panelLeft = width - 162 - panelWidth;
    const railLeft = width - 12 - 142;
    assert.ok(panelLeft + panelWidth < railLeft, `Forge recipe panel clears gear-slot rail at ${width}px`);
  }
});
test('short landscape keeps home actions at 48px and fits the menu destination grid', () => {
  assert.match(polish, /#gate-actions \{ display: grid; grid-template-columns: repeat\(2, minmax\(0, 1fr\)\); gap: 8px; \}/);
  assert.match(polish, /#gate-actions button \{ min-height: 48px;/);
  assert.match(main, /panel\.dataset\.sheet = menuSheet \? 'menu' : resourceSheet \? 'resources' : siteChoices \? 'sites' : kingdomActionSheet \? 'kingdom-actions' : kingdomBuildSite \? 'kingdom-build' : view === 'market' \? 'market-inspector' : view === 'kingdom' && state\?\.plots\.some\(plot => plot\.id === selected\) \? 'kingdom-building' : view === 'defense' \? \(state\?\.defense \? 'defense-session' : 'defense-preparation'\) : 'content';/);
  assert.match(main, /startChoice\.classList\.add\('defense-start-action'\)/);
  assert.match(polish, /#panel\[data-sheet="defense-preparation"\] #panel-close \{ position: absolute; top: 8px; right: 8px; z-index: 11; margin: 0; \}/);
  assert.match(polish, /#panel\[data-sheet="defense-preparation"\] \{ display: flex; flex-direction: column; overflow: hidden; \}/);
  assert.match(polish, /#panel\[data-sheet="defense-preparation"\] #choices \{ flex: 1 1 auto; min-height: 0; overflow-y: auto;/);
  assert.match(polish, /#panel\[data-sheet="defense-preparation"\] #choices > \.defense-start-action \{ position: sticky; top: 0;/);
  assert.match(polish, /#panel\[data-sheet="defense-preparation"\] #choices > \.defense-start-action \{[^}]*background-image: linear-gradient\(#58482b, #2c2419\)/);
  assert.match(polish, /#panel\[data-sheet="defense-preparation"\] #choices > \[data-choice="tutorial-toggle"\] \{ display: none; \}/);
  assert.match(polish, /#panel\[data-sheet="menu"\] #choices \{ grid-template-columns: repeat\(2, minmax\(0, 1fr\)\)/);
  assert.match(polish, /#panel\[data-sheet="menu"\] #choices > button \{ min-width: 0; min-height: 48px;/);
  assert.match(polish, /#scene-ui\.support:has\(\[data-market-good\]\) \.support-grid \{ grid-template-columns: repeat\(4, minmax\(0, 1fr\)\)/);
  assert.match(polish, /#scene-ui\.support:has\(\[data-market-good\]\) article > button \{ min-width: 0; min-height: 48px;/);
});

test('saved campaign gate groups its M01 primary and secondary actions', () => {
  assert.match(polish, /#gate \{ width: clamp\(260px, 30vw, 400px\); \}/);
  assert.match(polish, /#gate\[data-campaign-state="saved"\] #gate-actions \{[\s\S]*?grid-template-columns: repeat\(2, minmax\(0, 1fr\)\);[\s\S]*?margin-top: clamp\(16px, 4vh, 30px\);/);
  assert.match(polish, /\[data-choice="continue"\],\s*#gate\[data-campaign-state="saved"\] #gate-actions \[data-choice="new-campaign"\] \{ grid-column: 1 \/ -1;/);
  assert.match(polish, /#gate\[data-campaign-state="saved"\] #gate-actions \[data-choice="open-load"\] \{ grid-column: 2; grid-row: 3; \}/);
  assert.match(polish, /#gate\[data-campaign-state="saved"\] #gate-actions \[data-choice="open-settings"\] \{ grid-column: 1; grid-row: 3; \}/);
  assert.match(main, /add\('Save\/Load', 'open-load'/);
  assert.match(polish, /#gate\[data-campaign-state="saved"\] \{ justify-content: space-between; padding-top: 12px; \}/);
});

test('Defense preparation opens one inspector start action without cloning it into the dock', () => {
  assert.match(defense, /const startChoice = button\(defensePlan === 'endless' \? 'Start Endless' : 'Start Campaign Siege',[\s\S]*?defensePlan === 'endless' \? 'start-endless' : 'start-siege'\);/);
  const prepare = main.slice(main.indexOf('function prepareDefense('), main.indexOf('function startDefense('));
  assert.match(prepare, /setPanel\(true\);/);
});

test('Forge workpiece has an anvil-aligned pose, six accessible slots and a compact action inspector', () => {
  const paint = main.slice(main.indexOf('function paintForge('), main.indexOf('function mountForgeChrome('));
  assert.match(paint, /'data-forge-preview': previewRole/);
  assert.match(paint, /Crafting preview; this weapon is not owned yet/);
  assert.match(paint, /forgeWeaponPreviewPose\(previewItem\.age\)/);
  assert.ok(paint.includes('transform: `rotate(${pose.rotation} ${pose.x + pose.width / 2} ${pose.y + pose.height / 2})`'));
  assert.doesNotMatch(paint, /data-forge-hero|data-ground.*forge-hero-shadow/);
  assert.match(polish, /#scene-ui\.forge \.copy \{\s*left: 72px;\s*right: auto;\s*top: 72px;\s*width: min\(320px, calc\(100% - 760px\)\)/);
  assert.match(polish, /#scene-ui\.forge \.forge-slots \{[^}]*left: clamp\(400px, 31vw, 460px\);/);
  assert.match(polish, /#scene-ui\.forge \.forge-inventory\[data-empty="true"\] \{ display: none; \}/);
  assert.match(polish, /#scene-ui\.forge \.forge-inventory \{[\s\S]*?height: auto;\s*max-height: min\(190px, calc\(100% - 240px\)\);[\s\S]*?grid-template-rows: auto auto;/);
  assert.match(polish, /#scene-ui\.forge:has\(\.forge-inventory\[data-empty="false"\]\) \.copy \{ display: none; \}/);
  assert.match(polish, /#scene-ui\.forge \.forge-inventory-grid \{[\s\S]*?max-height: 120px;/);
  assert.match(polish, /#app\[data-view="forge"\] #dock \{\s*inset: 72px 12px auto auto;[^}]*height: auto;[^}]*max-height: calc\(100% - 140px\);/);
  assert.match(polish, /#scene-ui\.forge \.copy p\[data-forge-inventory-status\] \{ display: none; \}/);
});

test('compact Story rival choices stay above navigation and remain scrollable if text grows', () => {
  assert.match(polish, /#scene-ui\.support:has\(\.journal-tabs\):not\(:has\(\.journal-objectives\)\) > \.journal-rival-chooser \{[\s\S]*?top: 136px;[\s\S]*?bottom: 72px;[\s\S]*?overflow-y: auto;/);
  assert.match(polish, /\.journal-rival-chooser \.journal-rival-choices button \{\s*min-height: 52px;\s*padding: 4px 3px;\s*font-size: 12\.5px;\s*line-height: 1\.1;\s*white-space: normal;/);
  const contentAndCardChrome = 2 * 52 + 6 + 24 + 22 + 8;
  for (const height of [375, 424, 720]) {
    assert.ok(contentAndCardChrome <= height - 136 - 72, `all six rival choices fit above navigation at 825/933/1280-class height ${height}`);
  }
});

test('M25 Story HUD uses saved chapter progress, reachable controls and split compact framing', () => {
  assert.match(main, /storyHeaderTitle\(state, data\)/);
  assert.match(main, /\['quests', 'Objectives'\]/);
  assert.match(main, /tabs\.append\(button\('Settings',[\s\S]*?head\.append\(tabs\);/);
  assert.match(main, /button\('Settings',\s*\(\) => openSettings\(view\)/);
  assert.match(polish, /#app\[data-view="story"\] > header h1 \{[^}]*left: 50%;[^}]*transform: translateX\(-50%\)/);
  assert.match(polish, /#app\[data-view="story"\] > header #resources \{[^}]*position: absolute;[^}]*left: 0;/);
  assert.match(polish, /#app\[data-view="story"\] #scene-ui\.support:has\(\.journal-tabs\) > header\.story-header \{[^}]*position: fixed;[^}]*top: 8px;/);
  assert.match(polish, /#app\[data-view="story"\] #scene-ui\.support:has\(\.journal-tabs\) \.journal-tabs \{[^}]*position: fixed;[^}]*top: 56px;[^}]*right: 18px;/);
  assert.match(polish, /:has\(\.journal-tabs\):has\(\.journal-objectives\) \.journal-rival-chooser \{\s*display: none;/);
  assert.match(polish, /@media \(max-width: 1000px\) \{[\s\S]*?#app\[data-view="story"\] #scene-ui\.support:has\(\.journal-tabs\) > header\.story-header \{\s*top: 58px;/);
  assert.match(polish, /\.journal-tabs \{[^}]*position: fixed;[^}]*top: 56px;[^}]*right: 18px;/);
});

test('opening a side panel keeps the scene fitted to the whole stage', () => {
  assert.equal(worldViewportWidth(1280, 920, true), 1280);
  assert.equal(worldViewportWidth(920, 560, true, 1280), 1280);
  assert.equal(worldViewportWidth(1280, 1280, false), 1280);
});

test('Chapter IV story background uses its generated Divided Gate scene asset', () => {
  assert.match(main, /'assets\/production\/production-12-20261003\/images\/03-supporting-chapter-3\.png',\s*'assets\/derivatives\/visual-repair-20261020\/scenes\/story-chapter-4-divided-gate-v2\.png',\s*'assets\/production\/production-12-20261003\/images\/05-supporting-chapter-5\.png'/);
  assert.equal(fs.existsSync(new URL('../assets/derivatives/visual-repair-20261020/scenes/story-chapter-4-divided-gate-v2.png', import.meta.url)), true);
});

test('Adventure camera fits the full map and clears obsolete edge darkening', () => {
  const frame = main.slice(main.indexOf('function measureFrame()'), main.indexOf('function fitScene()'));
  assert.match(frame, /const cameraWidth = view === 'adventure' && panelOpen \? width : worldWidth;/);
  assert.match(frame, /wideBoardCamera\(sourceSize, cameraWidth, height, boardTop, boardBottom\)/);
  assert.match(frame, /stage\.style\.backgroundImage = '';/);
  assert.match(frame, /terrain\.style\.maskImage = '';/);
  assert.match(frame, /delete stage\.dataset\.adventureEdgeBackdrop;/);
  assert.doesNotMatch(frame, /northEdgeSafe|safeOffsetY/);
  assert.match(main, /class: 'fog',[\s\S]*?fill: '#10171b',[\s\S]*?opacity: 0\.32/);
});

test('Adventure camera follows the hero without exposing blank space beside an open inspector', () => {
  const source = contract.geometry.adventure.sourceSize;
  const geometry = contract.geometry.adventure;
  const hero = project(geometry.worldToSource, [8.5, 8.5]);
  for (const [stageWidth, height, visibleWidth] of [[825, 375, 545], [933, 424, 600], [1280, 720, 922]]) {
    const fit = focusPointCamera(source, stageWidth, height, visibleWidth, hero, 0.5);
    const right = fit.offset[0] + source[0] * fit.scale;
    const bottom = fit.offset[1] + source[1] * fit.scale;
    const heroX = hero[0] * fit.scale + fit.offset[0];
    assert.ok(fit.offset[0] <= 0 && fit.offset[0] + 1e-6 >= stageWidth - source[0] * fit.scale);
    assert.ok(fit.offset[1] <= 0 && fit.offset[1] + 1e-6 >= height - source[1] * fit.scale);
    assert.ok(right >= stageWidth - 1e-6, `right edge covers ${stageWidth}px stage`);
    assert.ok(bottom >= height - 1e-6, `bottom edge covers ${height}px stage`);
    assert.ok(Math.abs(heroX - visibleWidth * 0.7) < 1e-6, `hero stays in the visible 70% play area for ${visibleWidth}px field`);
  }
});

test('short Adventure inspector keeps its movement actions inside the visible panel', () => {
  assert.match(polish, /@media \(max-height: 400px\) \{[\s\S]*?#app\[data-view="adventure"\] #stage-field\.panel-open #panel \{ bottom: 40px; \}/);
});

test('Kingdom inspector and navigation follow the M06 focused scene composition', () => {
  assert.match(polish, /#app\[data-view="kingdom"\] #nav \{[\s\S]*?position: fixed;[\s\S]*?inset: 50% auto auto 12px;[\s\S]*?flex-direction: column/);
  assert.match(polish, /#app\[data-view="kingdom"\] #nav button\.icon-medallion \{[\s\S]*?min-height: 48px/);
  assert.match(polish, /#app\[data-view="kingdom"\] #nav button\.icon-medallion::after \{[\s\S]*?content: attr\(aria-label\)/);
  assert.match(polish, /#app\[data-view="kingdom"\] #panel \{[\s\S]*?bottom: 12px;[\s\S]*?left: 50%;[\s\S]*?width: min\(560px, calc\(100vw - 96px\)\)/);
  assert.match(polish, /#app\[data-view="kingdom"\] #choices \{[\s\S]*?grid-template-columns: repeat\(2, minmax\(0, 1fr\)\)/);
  assert.match(polish, /@media \(max-height: 500px\) \{[\s\S]*?#app\[data-view="kingdom"\] #nav \{ top: 52px; transform: none; \}/);
});

test('Kingdom bottom inspector does not reserve a false side-panel inset for scene labels', () => {
  const frame = main.slice(main.indexOf('function measureFrame()'), main.indexOf('function fitScene()'));
  assert.match(frame, /const sidePanelOpen = panelOpen && view !== 'kingdom';/);
  assert.match(frame, /const inset = sidePanelOpen \? panel\.getBoundingClientRect\(\)\.width \+ 8 : 0;/);
  assert.match(frame, /worldViewportWidth\(rect\.width, width, sidePanelOpen, window\.innerWidth\)/);
  assert.match(frame, /const cameraWidth = view === 'adventure' && panelOpen \? width : worldWidth;/);
});

test('short-wide map scenes keep all Adventure, Tactical and Defense board corners in view', () => {
  for (const mode of ['adventure', 'tactical', 'defense']) {
    const geometry = contract.geometry[mode];
    const corners = [[0, 0], [geometry.cols, 0], [geometry.cols, geometry.rows], [0, geometry.rows]];
    const boardYs = corners.map(point => project(geometry.worldToSource, point)[1]);
    const boardTop = Math.min(...boardYs);
    const boardBottom = Math.max(...boardYs);
    for (const [width, height] of [[825, 375], [933, 424]]) {
      const fit = wideBoardCamera(geometry.sourceSize, width, height, boardTop, boardBottom);
      assert.ok(Math.abs(geometry.sourceSize[0] * fit.scale - width) < 1e-6, `${mode} ${width}x${height} scene fills the width without side gutters`);
      assert.ok(Math.abs(fit.offset[0]) < 1e-6, `${mode} ${width}x${height} remains horizontally registered to the terrain`);
      for (const [x, y] of corners) {
        const [sourceX, sourceY] = project(geometry.worldToSource, [x, y]);
        const screenX = sourceX * fit.scale + fit.offset[0];
        const screenY = sourceY * fit.scale + fit.offset[1];
        assert.ok(screenX >= 0 && screenX <= width, `${mode} ${width}x${height} x corner ${x},${y} remains visible`);
        assert.ok(screenY >= 0 && screenY <= height, `${mode} ${width}x${height} y corner ${x},${y} remains visible`);
      }
    }
    assert.deepEqual(wideBoardCamera(geometry.sourceSize, 1280, 720, boardTop, boardBottom), camera(geometry.sourceSize, 1280, 720));
  }
});

test('Adventure town guidance sits in the left field away from the town landmark', () => {
  assert.match(main, /sceneStatus\(campaignWorld\?\.title \|\| 'Beyond the gates',[\s\S]*?'adventure-town'\);/);
  assert.match(polish, /#app\[data-view="adventure"\] #scene-ui\.game-status\.adventure-town \{ left: 18px; width: min\(340px, calc\(100vw - 36px\)\);/);
  assert.match(polish, /#app\[data-view="adventure"\] #scene-ui\.game-status\.adventure-town \{ left: 12px; width: min\(340px, calc\(100vw - 24px\)\);/);
});

test('settlement results clear floating battle labels behind the result card', () => {
  assert.match(polish, /#stage-field:has\(#scene-ui\.combat-result\) #labels \{ visibility: hidden; \}/);
});

test('Army Codex gives all eight creatures legible, age-gated, informational choices', () => {
  const paint = main.slice(main.indexOf('function paintArmy()'), main.indexOf('function army()'));
  assert.equal(Object.keys(data.CREATURES).length, 8);
  assert.match(paint, /for \(const \[type, creature\] of Object\.entries\(data\.CREATURES\)\)/);
  assert.match(paint, /const earliestAge = data\.AGES\.findIndex\(\(_, age\) => dwellingPool\(data, age\)\.includes\(type\)\);/);
  assert.match(paint, /recruitment remains at eligible dwellings\./);
  assert.match(paint, /if \(subject\.kind === 'role' && subject\.age === state\.age\) \{/);
  assert.match(paint, /name\.textContent = codexCompactNames\[creature\.n\] \|\| creature\.n;/);
  assert.match(paint, /name\.title = creature\.n;/);
  assert.match(polish, /army-codex-creature img \{[^}]*border-radius: 50%; background: radial-gradient/);
  assert.match(polish, /#board \.army-codex-creature \{[^}]*min-width: 48px; min-height: 48px/);
  assert.match(polish, /#board \.army-codex-creature span \{[^}]*font-size: 10px/);
});

test('Army desktop layout follows the M24 scene-and-overlay composition while short landscape reflows panels', () => {
  assert.match(polish, /#board\[data-army-layout="screen"\] \{[^}]*grid-template-columns: minmax\(0, 1fr\); grid-template-rows: minmax\(0, 1fr\)/);
  assert.match(polish, /#board \.army-showcase-units \{[^}]*width: min\(100%, 400px\);[^}]*margin: 0 auto/);
  assert.match(polish, /#board \.army-showcase-unit img \{[^}]*max-height: 210px/);
  assert.match(polish, /\.army-creature-codex \{ position: absolute; z-index: 5; top: 68px; right: 12px;[^}]*width: min\(176px, 13vw\); height: min\(380px, calc\(100% - 68px - min\(292px, 38vh\) - 24px\)\)/);
  assert.match(polish, /\.roster-inspector \{ position: absolute; z-index: 5; right: 12px; bottom: 12px; width: min\(308px, 22\.5vw\); height: min\(292px, 38vh\)/);
  assert.match(polish, /#board \.army-roster-shelf \{ position: absolute; z-index: 4; left: 72px; bottom: 80px;/);
  assert.match(polish, /@media \(min-height: 501px\) \{\s*#board \.army-roster-shelf::after \{ display: none; \}\s*#board \.army-roster-shelf \.board-row\[data-army-row="roster"\] \{ gap: 4px; padding-left: 0; \}\s*#board \.army-roster-shelf \.board-row\[data-army-row="roster"\] \.board-card \{ flex-basis: clamp\(72px, 6\.4vw, 88px\); \}/);
  assert.match(polish, /#board \.army-roster-shelf \.board-row\[data-army-row="roster"\] \.board-card img \{[^}]*border-radius: 50%;[^}]*object-fit: contain/);
  assert.match(polish, /@media \(max-height: 500px\) \{[\s\S]*?#board \.army-roster-shelf \{ position: relative; left: auto; bottom: auto; width: auto; height: auto;/);
  assert.match(polish, /#board \.army-creature-codex \{ position: static; right: auto; top: auto;/);
  assert.match(polish, /#board \.roster-inspector \{ position: static; right: auto; bottom: auto;/);
});

test('Army roster shelf has room for four actual formations at desktop size', () => {
  assert.match(polish, /#board \.army-roster-shelf \{[^}]*width: min\(372px, calc\(100vw - 90px\)\)/);
  const shelfWidth = 372;
  const innerWidth = shelfWidth - 20;
  const cardWidth = Math.min(88, Math.max(72, 1280 * 0.064));
  const fourCardsWidth = cardWidth * 4 + 4 * 3;
  assert.ok(fourCardsWidth <= innerWidth, `${fourCardsWidth}px of cards must fit inside ${innerWidth}px of shelf content`);
});

test('M23 Hero inventory binds real carried items to six equipment slots and item actions', () => {
  assert.match(main, /heroDetailTab === 'inventory' && !classOpen/);
  assert.match(main, /GEAR_SLOTS\.forEach\(\(slot, index\) =>/);
  assert.match(main, /socket\.dataset\.slotNumber = String\(index \+ 1\)/);
  assert.match(main, /back\.setAttribute\('aria-label', 'Back to Hero details'\)/);
  assert.match(main, /for \(const item of state\.inventory\)/);
  assert.match(main, /selectGearIcon\(gearIcons\.icons, item\.slot, item\)/);
  assert.match(main, /aria-label', `\$\{itemTitle\(item\)\}\. \$\{bonusText\(item\)\}\. \$\{statProjection\(item\)\}\./);
  assert.match(main, /button\('Equip', \(\) => act\('EQUIP', \{ itemId: item\.id \}\)/);
  assert.match(main, /button\(`Unequip \$\{slotName\[item\.slot\]\}`/);
  assert.match(main, /button\('Compare in Forge'/);
  assert.match(polish, /#scene-ui\.hero \.hero-inventory-slots \{[\s\S]*?grid-template-columns: repeat\(6, minmax\(0, 1fr\)\)/);
  assert.match(polish, /#scene-ui\.hero \.hero-inventory-panel \{[\s\S]*?grid-template-columns: minmax\(0, 1\.25fr\) minmax\(280px, \.9fr\)/);
  assert.match(polish, /#scene-ui\.hero \.hero-inventory-panel \{[\s\S]*?left: 9\.5%;[\s\S]*?bottom: 24px;[\s\S]*?width: min\(1045px, calc\(100% - 19%\)\);[\s\S]*?height: min\(388px, 54vh\)/);
  assert.match(polish, /#scene-ui\.hero \.hero-inventory-detail \{[\s\S]*?grid-template-columns: 110px minmax\(0, 1fr\)/);
  assert.match(polish, /\.hero-inventory-slots button\[data-hero-slot\]::after \{[\s\S]*?attr\(data-slot-number\)[\s\S]*?attr\(data-slot-name\)/);
  assert.match(polish, /body:has\(#scene-ui\.hero\[data-hero-detail-tab="inventory"\]\) #nav/);
  assert.match(polish, /#scene-ui\.hero \.hero-inventory-back \{[\s\S]*?top: 58px;[\s\S]*?width: 48px/);
  assert.match(polish, /@media \(max-height: 500px\) \{\s*#scene-ui\.hero \.hero-inventory-slots/);
});
