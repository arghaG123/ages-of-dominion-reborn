import test from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import crypto from 'node:crypto';
import data from '../src/data/reference-data.json' with { type: 'json' };
import contract from '../src/data/implementation-contract.json' with { type: 'json' };
import ageBuildings from '../src/data/age-buildings.json' with { type: 'json' };
import { newCampaign, command, advance, cost, futureConclusion } from '../src/core/campaign.js';
import { encode, decode, save, load } from '../src/core/save.js';
import { forgeOffer, gearBonus, heroStats, GEAR_SLOTS } from '../src/core/rules.js';
import { kingdomPainting, kingdomWallTrace, plotPresentation, wallPhase, KINGDOM_AGES, WALL_KIND } from '../src/client/kingdom-view.js';
import { resourceBarLayout, resourceChipLabel, boxesSeparate } from '../src/client/resource-bar.js';
import { heroBody, heroKitCaption, kitEra, wornMarks, selectGearIcon } from '../src/client/hero-room.js';
import { WORN_ANCHORS } from '../src/client/actor.js';
import { storyScreen, storyChamberLine } from '../src/client/story-view.js';
import gearIcons from '../src/data/gear-icons-20261007.json' with { type: 'json' };

const fresh = () => newCampaign(contract, data, 1_000);
const act = (state, id, type, payload = {}) => command(state, { id, type, payload }, state.clock, data);
const finish = (state, plotId) => advance(state, state.buildJobs.find(job => job.plotId === plotId).completesAt, data);

function memory() {
  const map = new Map();
  return {
    getItem: key => (map.has(key) ? map.get(key) : null),
    setItem: (key, value) => map.set(key, String(value)),
    removeItem: key => map.delete(key),
  };
}

function reload(state) {
  const storage = memory();
  save(storage, state, data);
  const loaded = load(storage, data);
  assert.equal(loaded.status, 'VALID');
  return loaded.state;
}

test('a fresh campaign shows open ground and one tutorial outline', () => {
  const state = fresh();
  assert.equal(state.walls.level, 0);
  assert.equal(state.buildJobs.length, 0);
  assert.equal(state.plots.filter(plot => plot.level === 0).length, 17);
  const painting = kingdomPainting(state);
  assert.equal(painting.phase, 'none');
  assert.equal(painting.stamps.length, 0);
  assert.equal(painting.file, 'assets/derivatives/kingdom-stone-populated-20261021/stone-ground.png');
  assert.equal(wallPhase(state), 'none');
  const tutorial = contract.geometry.kingdom.sites.find(site => site.id !== 'townhall').id;
  let dashed = 0;
  for (const site of contract.geometry.kingdom.sites) {
    const plot = state.plots.find(item => item.id === site.id);
    const view = plotPresentation({ plot, job: null, measured: null, tutorialSiteId: tutorial, selected: false });
    assert.equal(view.pad, false);
    if (plot.level === 0 && plot.id !== tutorial) {
      assert.equal(view.state, 'empty');
      assert.equal(view.outline, null);
      assert.equal(view.clearing, 'ground');
    }
    if (view.outline === 'tutorial') dashed += 1;
  }
  assert.equal(dashed, 1);
});

test('empty-site footprints on every age ground match the surrounding earth', () => {
  const probe = spawnSync('python', ['-c', `
import json, sys
import cv2
import numpy as np
contract = json.load(open(r"src/data/implementation-contract.json", encoding="utf-8"))
geo = contract["geometry"]["kingdom"]
a,b,c,d,e,f = geo["worldToSource"]
def proj(x, y):
    return [a*x + c*y + e, b*x + d*y + f]
ages = ["stone","bronze","iron","medieval","gunpowder","industrial","modern","future"]
report = {}
for age in ages:
    path = f"assets/derivatives/mock-led-20261016/kingdom/kingdom-{age}-ground.png"
    gray = cv2.cvtColor(cv2.imread(path), cv2.COLOR_BGR2GRAY)
    gy, gx = np.gradient(gray)
    mag = np.hypot(gx, gy)
    h, w = gray.shape
    peaks = []
    for site in geo["sites"]:
        if site["id"] == "townhall":
            continue
        x, y, rw, rh = site["rect"]
        corners = np.array([proj(x, y), proj(x+rw, y), proj(x+rw, y+rh), proj(x, y+rh)], dtype=float)
        center = np.mean(corners, axis=0)
        site_peaks = []
        for i in range(4):
            p0 = corners[i]
            p1 = corners[(i + 1) % 4]
            edge = p1 - p0
            length = float(np.hypot(edge[0], edge[1]) or 1)
            tangent = edge / length
            normal = np.array([-tangent[1], tangent[0]])
            mid = (p0 + p1) / 2
            if np.dot(normal, center - mid) > 0:
                normal = -normal
            profile = []
            for offset in range(8, 56, 2):
                samples = []
                for t in np.linspace(0.2, 0.8, 10):
                    pt = p0 + edge * t + normal * offset
                    ix, iy = int(round(pt[0])), int(round(pt[1]))
                    if 1 <= ix < w - 1 and 1 <= iy < h - 1:
                        samples.append(mag[iy, ix])
                profile.append(float(np.mean(samples)) if samples else 0)
            profile = np.array(profile)
            med = float(np.median(profile)) + 1
            site_peaks.append((float(profile.max()) - med) / med)
        peaks.append(float(np.mean(site_peaks)))
    report[age] = {"mean": float(np.mean(peaks)), "max": float(np.max(peaks))}
print(json.dumps(report))
`], { encoding: 'utf8' });
  assert.equal(probe.status, 0, probe.stderr);
  const report = JSON.parse(probe.stdout);
  // Ceilings sit under the straight-edge peaks measured on the rectangle paintings.
  const ceiling = {
    stone: 1.5, bronze: 1.5, iron: 1.5, medieval: 1.5,
    gunpowder: 2.0, industrial: 2.0, modern: 2.5, future: 2.0,
  };
  for (const age of KINGDOM_AGES) {
    assert.ok(report[age].mean < ceiling[age], `${age} empty sites still show a pad edge (${report[age].mean})`);
  }
});

test('all ages route all four wall phases to their own reviewed source family', () => {
  const stone = fresh();
  assert.equal(kingdomPainting(stone).file, 'assets/derivatives/kingdom-stone-populated-20261021/stone-ground.png');
  const stoneFiles = [
    'stone-ground.png',
    'stone-scaffold.png',
    'stone-wall.png',
    'stone-wall-tall.png',
  ].map(name => fs.readFileSync(`assets/derivatives/kingdom-stone-populated-20261021/${name}`));
  for (const bytes of stoneFiles) {
    const width = bytes.readUInt32BE(16);
    const height = bytes.readUInt32BE(20);
    const aspectError = Math.abs(width / height - 1376 / 768) / (1376 / 768);
    assert.ok(aspectError < 0.001, 'generated family aspect ratio must stay within 0.1% of the registered scene');
  }
  let job = act(stone, 'wall-job', 'BUILD', { plotId: 'walls', building: 'walls' });
  const scaffold = kingdomPainting(job);
  assert.equal(scaffold.phase, 'scaffold');
  assert.equal(scaffold.stamps.length, 0);
  assert.equal(scaffold.file, 'assets/derivatives/kingdom-stone-populated-20261021/stone-scaffold.png');
  job = finish(job, 'walls');
  const built = kingdomPainting(job);
  assert.equal(built.phase, 'built');
  assert.equal(built.wallKind, 'timber-palisade');
  assert.equal(built.file, 'assets/derivatives/kingdom-stone-populated-20261021/stone-wall.png');
  job.resources.wood += 5000;
  job.resources.stone += 5000;
  job = act(job, 'wall-tall', 'BUILD', { plotId: 'walls', building: 'walls' });
  assert.equal(kingdomPainting(job).phase, 'scaffold');
  job = finish(job, 'walls');
  const tall = kingdomPainting(job);
  assert.equal(tall.phase, 'tall');
  assert.equal(tall.wallKind, 'timber-palisade');
  assert.equal(tall.file, 'assets/derivatives/kingdom-stone-populated-20261021/stone-wall-tall.png');
  const files = new Set();
  for (const ageName of KINGDOM_AGES) {
    const age = KINGDOM_AGES.indexOf(ageName);
    const state = fresh();
    state.age = age;
    state.walls.level = 1;
    const painting = kingdomPainting(state);
    assert.equal(painting.wallKind, WALL_KIND[ageName]);
    assert.equal(painting.stamps.length, 0);
    if (ageName === 'stone') assert.equal(painting.file, 'assets/derivatives/kingdom-stone-populated-20261021/stone-wall.png');
    else assert.equal(painting.file, `assets/derivatives/kingdom-families-20261018/${ageName}/wall.webp`);
    assert.equal(fs.existsSync(painting.file), true);
    const bytes = fs.readFileSync(painting.file);
    files.add(crypto.createHash('sha256').update(bytes).digest('hex'));
    if (ageName !== 'stone') assert.notEqual(painting.file, 'assets/derivatives/mock-led-20261016/kingdom/kingdom-stone-wall.png');

    const expected = ageName === 'stone'
      ? ['stone-ground.png', 'stone-scaffold.png', 'stone-wall.png', 'stone-wall-tall.png'].map(name => `assets/derivatives/kingdom-stone-populated-20261021/${name}`)
      : ['ground.webp', 'scaffold.webp', 'wall.webp', 'wall-tall.webp'].map(name => `assets/derivatives/kingdom-families-20261018/${ageName}/${name}`);
    const states = [
      { walls: { level: 0 }, buildJobs: [] },
      { walls: { level: 0 }, buildJobs: [{ plotId: 'walls' }] },
      { walls: { level: 1 }, buildJobs: [] },
      { walls: { level: 2 }, buildJobs: [] },
    ];
    states.forEach((wallState, phaseIndex) => {
      const phaseState = fresh();
      phaseState.age = age;
      Object.assign(phaseState, wallState);
      assert.equal(kingdomPainting(phaseState).file, expected[phaseIndex]);
      assert.equal(fs.existsSync(expected[phaseIndex]), true);
    });
  }
  assert.equal(files.size, 8);
  const wall = kingdomWallTrace(contract.geometry.kingdom);
  assert.equal(wall.opening, 1);
  assert.equal(wall.version, 'walls-isometric-v4');
  const lumber = ageBuildings.ages.stone.lumber;
  const builtPlot = plotPresentation({
    plot: { id: 'P01', type: 'lumber', level: 1 },
    job: null,
    measured: lumber,
    tutorialSiteId: '',
    selected: false,
  });
  assert.equal(builtPlot.pad, false);
  assert.equal(builtPlot.state, 'built');
  assert.equal(builtPlot.art, lumber.file);
});

test('aging to Medieval then building the wall paints that age, including the taller upgrade', () => {
  // The balance is a fixture so the age price cannot block the wall. It is not a natural journey.
  let state = fresh();
  state.resources = { food: 1e12, wood: 1e12, stone: 1e12, gold: 1e12 };
  for (let step = 0; step < 3; step += 1) {
    state = act(state, `hall-${step}`, 'BUILD', { plotId: 'townhall', building: 'townhall' });
    state = finish(state, 'townhall');
    state = act(state, `age-${step}`, 'AGE_UP');
  }
  assert.equal(state.age, 3);
  assert.equal(state.walls.level, 0);
  assert.equal(kingdomPainting(state).phase, 'none');
  assert.equal(kingdomPainting(state).file, 'assets/derivatives/kingdom-families-20261018/medieval/ground.webp');
  state = act(state, 'med-job', 'BUILD', { plotId: 'walls', building: 'walls' });
  assert.equal(kingdomPainting(state).phase, 'scaffold');
  assert.equal(kingdomPainting(state).stamps.length, 0);
  assert.equal(kingdomPainting(state).file, 'assets/derivatives/kingdom-families-20261018/medieval/scaffold.webp');
  state = finish(state, 'walls');
  const built = kingdomPainting(state);
  assert.equal(built.phase, 'built');
  assert.equal(built.wallKind, 'stone-curtain');
  assert.equal(built.stamps.length, 0);
  assert.equal(built.file, 'assets/derivatives/kingdom-families-20261018/medieval/wall.webp');
  state = act(state, 'med-tall', 'BUILD', { plotId: 'walls', building: 'walls' });
  assert.equal(kingdomPainting(state).phase, 'scaffold');
  assert.equal(kingdomPainting(state).file, 'assets/derivatives/kingdom-families-20261018/medieval/scaffold.webp');
  state = finish(state, 'walls');
  const tall = kingdomPainting(state);
  assert.equal(tall.phase, 'tall');
  assert.equal(tall.wallKind, 'stone-curtain');
  assert.equal(tall.stamps.length, 0);
  assert.equal(tall.file, 'assets/derivatives/kingdom-families-20261018/medieval/wall-tall.webp');
});

test('medieval through future walls are textured paintings and the future scaffold is not timber', () => {
  const probe = spawnSync('python', ['-c', `
import json, cv2, numpy as np
from pathlib import Path
root = Path("assets/derivatives/mock-led-20261016/kingdom")
contract = json.loads(Path("src/data/implementation-contract.json").read_text(encoding="utf-8"))
geo = contract["geometry"]["kingdom"]
A, B, C, D, E, F = geo["worldToSource"]
gx, gy = geo["anchors"]["gate"]
sx, sy = int(round(A * gx + C * gy + E)), int(round(B * gx + D * gy + F))

def added(ground, wall):
    diff = np.abs(wall.astype(np.int16) - ground.astype(np.int16)).sum(2)
    inner = cv2.erode((diff > 40).astype(np.uint8) * 255, np.ones((9, 9), np.uint8))
    sel = inner > 0
    def horizontal(image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY).astype(np.float32)
        return np.abs(cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3))
    if not np.any(sel):
        return -999.0
    return float((horizontal(wall) - horizontal(ground))[sel].mean())

def median(ground, image):
    diff = np.abs(image.astype(np.int16) - ground.astype(np.int16)).sum(2)
    bright = (diff > 40) & (image.mean(2) > 90)
    if not np.any(bright):
        return [0.0, 0.0, 0.0]
    return [float(v) for v in np.median(image[bright], axis=0)]

report = {}
for age in ["medieval", "gunpowder", "industrial", "modern", "future"]:
    ground = cv2.imread(str(root / f"kingdom-{age}-ground.png"), cv2.IMREAD_COLOR)
    wall = cv2.imread(str(root / f"kingdom-{age}-wall.png"), cv2.IMREAD_COLOR)
    tall = cv2.imread(str(root / f"kingdom-{age}-wall-tall.png"), cv2.IMREAD_COLOR)
    gate = wall[sy - 6:sy + 6, sx - 6:sx + 6].astype(np.int16) - ground[sy - 6:sy + 6, sx - 6:sx + 6].astype(np.int16)
    report[age] = {
        "built": added(ground, wall),
        "tall": added(ground, tall),
        "gate": float(np.abs(gate).mean()),
        "shape": list(wall.shape),
    }
report["stoneScaffold"] = median(
    cv2.imread(str(root / "kingdom-stone-ground.png"), cv2.IMREAD_COLOR),
    cv2.imread(str(root / "kingdom-stone-scaffold.png"), cv2.IMREAD_COLOR),
)
report["futureScaffold"] = median(
    cv2.imread(str(root / "kingdom-future-ground.png"), cv2.IMREAD_COLOR),
    cv2.imread(str(root / "kingdom-future-scaffold.png"), cv2.IMREAD_COLOR),
)
print(json.dumps(report))
`], { encoding: 'utf8' });
  assert.equal(probe.status, 0, probe.stderr);
  const report = JSON.parse(probe.stdout);
  for (const age of ['medieval', 'gunpowder', 'industrial', 'modern', 'future']) {
    assert.deepEqual(report[age].shape, [768, 1376, 3]);
    assert.ok(report[age].built > 3, `${age} finished wall is still a flat slab (${report[age].built})`);
    assert.ok(report[age].tall > 3, `${age} taller wall is still a flat slab (${report[age].tall})`);
    assert.ok(report[age].gate < 8, `${age} gate is painted shut (${report[age].gate})`);
  }
  const stone = report.stoneScaffold;
  const future = report.futureScaffold;
  assert.ok(stone[2] > stone[0] + 20, `stone scaffold is not timber ${stone}`);
  assert.ok(future[0] > future[2] + 12, `future scaffold still matches stone timber ${future}`);
});

test('food, wood, stone, gold, Menu and Save stay in separate bounds', () => {
  for (const width of [825, 1280]) {
    const layout = resourceBarLayout(width);
    const boxes = [...layout.chips, layout.menu, layout.save, layout.title, layout.status];
    assert.equal(boxesSeparate(boxes), true, `overlap at ${width}`);
    assert.ok(layout.save.x + layout.save.w <= layout.inner + 0.5);
    assert.ok(layout.chips[3].x + layout.chips[3].w <= layout.menu.x - 1);
  }
  const huge = 1_000_000_000_000;
  const chip = resourceChipLabel('food', huge);
  assert.notEqual(chip.text, String(huge));
  assert.equal(chip.full, String(huge));
  assert.equal(chip.title, `food ${huge}`);
  assert.equal(chip.accessible, `food ${huge}`);
  assert.ok(chip.text.length <= 8);
  assert.deepEqual(cost(data, 'lumber', 0), { wood: 25, stone: 15 });
  assert.deepEqual(forgeOffer(0, 1).cost, { wood: 80, stone: 60, gold: 70 });
  let state = fresh();
  state.resources.wood += 100;
  state.resources.stone += 100;
  const before = state.resources.wood;
  state = act(state, 'camp', 'BUILD', { plotId: 'P01', building: 'lumber' });
  state = finish(state, 'P01');
  const produced = advance(state, state.clock + 10_000, data);
  assert.equal(produced.resources.wood - state.resources.wood, 4.5);
  assert.equal(before - 25, state.resources.wood);
});

test('forge equip and unequip preserve item identity and only draw a supported body attachment', () => {
  let state = fresh();
  state.resources = { food: 1e12, wood: 1e12, stone: 1e12, gold: 1e12 };
  const layoutBalance = reload(state);
  assert.equal(layoutBalance.resources.food, 1e12);
  assert.equal(resourceChipLabel('wood', layoutBalance.resources.wood).full, '1000000000000');
  state = layoutBalance;
  state = act(state, 'armory', 'BUILD', { plotId: 'P02', building: 'armory' });
  state = finish(state, 'P02');
  const start = heroStats(state, data);
  for (const slot of GEAR_SLOTS) {
    state = act(state, `forge-${slot}`, 'FORGE', { slot, quality: 0 });
    const bagItem = state.inventory.find(item => item.slot === slot);
    assert.ok(bagItem);
    assert.equal(wornMarks(state).find(mark => mark.slot === slot).worn, false);
    assert.equal(wornMarks(state).some(mark => mark.id === bagItem.id), false);
    const bonus = gearBonus(bagItem);
    state = act(state, `equip-${slot}`, 'EQUIP', { itemId: bagItem.id });
    assert.equal(state.inventory.some(item => item.id === bagItem.id), false);
    assert.equal(state.hero.equip[slot].id, bagItem.id);
    const stats = heroStats(state, data);
    for (const [key, amount] of Object.entries(bonus)) assert.equal(stats[key] - start[key], amount);
    const mark = wornMarks(state).find(item => item.slot === slot);
    assert.equal(mark.worn, true);
    assert.equal(mark.id, bagItem.id);
    assert.ok(mark.socketIcon);
    const inventoryIcon = selectGearIcon(gearIcons.icons, slot, state.hero.equip[slot])?.file;
    assert.ok(inventoryIcon, `${slot} needs an age-matched inventory icon`);
    if (slot === 'weapon' && state.age === 0) {
      assert.equal(mark.appearance, 'attached-asset');
      assert.equal(mark.appearanceFile, 'assets/derivatives/worn-gear-20261018/flint-club-stone.png');
      assert.deepEqual(mark.anchor, WORN_ANCHORS.weapon);
      assert.notEqual(mark.appearanceFile, inventoryIcon, 'the inventory plate is not used as the held prop');
    } else {
      assert.equal(mark.appearance, 'socket-only', `${slot} has no source-backed wearable layer`);
      assert.equal(mark.appearanceFile, '');
      assert.equal(mark.socketIcon, inventoryIcon, 'equipped item remains visible in its socket');
    }
    if (slot === 'weapon') {
      const wornSave = reload(state);
      assert.equal(wornSave.hero.equip.weapon.id, bagItem.id);
      assert.equal(wornMarks(wornSave).find(item => item.slot === 'weapon').worn, true);
      state = wornSave;
    }
    state = act(state, `unequip-${slot}`, 'UNEQUIP', { slot });
    assert.equal(state.hero.equip[slot], null);
    assert.equal(state.inventory.some(item => item.id === bagItem.id), true);
    const restored = heroStats(state, data);
    for (const key of Object.keys(bonus)) assert.equal(restored[key], start[key]);
    assert.equal(wornMarks(state).find(item => item.slot === slot).worn, false);
    if (slot === 'weapon') {
      const removed = reload(state);
      assert.equal(removed.hero.equip.weapon, null);
      assert.equal(wornMarks(removed).find(item => item.slot === 'weapon').worn, false);
      state = removed;
    }
  }
  const caption = heroKitCaption(state);
  assert.equal(caption.includes('static pose'), false);
  assert.equal(caption.includes('unverified'), false);
  assert.equal(caption.includes('not a worn attachment'), false);
  assert.match(caption, /ancient kit/);
});

test('every class standing body matches the age kit, and the healer staff ends at the feet', () => {
  const classes = Object.keys(data.CLASSES);
  for (const classId of classes) {
    for (const age of [0, 3, 4, 7]) {
      const body = heroBody(classId, age);
      assert.equal(body.depictedKitEra, kitEra(age), `${classId} at age ${age}`);
      assert.equal(fs.existsSync(body.file), true);
      const sha = crypto.createHash('sha256').update(fs.readFileSync(body.file)).digest('hex');
      assert.equal(sha, body.sha256);
    }
  }
  const healer = heroBody('healer', 0);
  const probe = spawnSync('python', ['-c', `
from PIL import Image
import sys
im = Image.open(sys.argv[1]).convert('RGBA')
w, h = im.size
px = im.load()
foot = int(round(float(sys.argv[2]) * h))
below = 0
for y in range(foot + 1, h):
    below += sum(1 for x in range(w) if px[x, y][3] > 20)
print(below)
`, healer.file, String(healer.foot[1])], { encoding: 'utf8' });
  assert.equal(probe.status, 0, probe.stderr);
  assert.equal(Number(probe.stdout.trim()), 0);
});

test('seven chapter choices then Keep the valley grants nothing and reloads', () => {
  let state = fresh();
  state.resources = { food: 1e12, wood: 1e12, stone: 1e12, gold: 1e12 };
  for (let step = 0; step < 7; step += 1) {
    state = act(state, `hall-${step}`, 'BUILD', { plotId: 'townhall', building: 'townhall' });
    state = finish(state, 'townhall');
    state = act(state, `age-${step}`, 'AGE_UP');
  }
  assert.equal(state.age, 7);
  assert.equal(state.walls.level, 0);
  assert.equal(kingdomPainting(state).phase, 'none');
  assert.equal(kingdomPainting(state).file, 'assets/derivatives/kingdom-families-20261018/future/ground.webp');
  assert.equal(state.story.chapter, 0);
  assert.equal(state.story.futureSeen, false);
  assert.equal(storyScreen(state, data).title, 'Chapter I — The First Fire');
  assert.equal(storyChamberLine(state, data).conclusion, 'closed');
  assert.equal(storyChamberLine(state, data).text.includes('Reading this conclusion grants nothing'), false);
  assert.equal(storyScreen(state, data).keepValley, false);
  assert.throws(() => act(state, 'too-soon', 'ACK_FUTURE'), /not open/);
  for (let chapter = 0; chapter < data.STORY.length; chapter += 1) {
    assert.equal(storyScreen(state, data).choices.length > 0, true);
    state = act(state, `choice-${chapter}`, 'STORY_CHOICE', { index: 0 });
  }
  assert.equal(state.story.choices.length, 7);
  assert.equal(state.story.futureSeen, false);
  const screen = storyScreen(state, data);
  assert.equal(screen.keepValley, true);
  assert.match(screen.text, /The Valley We Keep/);
  const before = { ...state.resources };
  state = act(state, 'keep', 'ACK_FUTURE');
  assert.deepEqual(state.resources, before);
  assert.equal(state.story.futureSeen, true);
  const done = storyScreen(state, data);
  assert.equal(done.concluded, true);
  assert.match(done.text, /The Valley We Keep/);
  assert.match(done.text, /grants nothing/);
  assert.equal(futureConclusion(state, data), done.text);
  const chamber = storyChamberLine(state, data);
  assert.equal(chamber.conclusion, 'kept');
  assert.equal(chamber.text, futureConclusion(state, data));
  assert.match(chamber.text, /Reading this conclusion grants nothing/);
  const kept = reload(state);
  assert.equal(kept.story.futureSeen, true);
  assert.equal(kept.story.choices.length, 7);
  assert.deepEqual(kept.resources, before);
  assert.match(storyScreen(kept, data).text, /The Valley We Keep/);
});
