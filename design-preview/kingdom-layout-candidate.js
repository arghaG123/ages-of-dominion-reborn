const pack = globalThis.KINGDOM_CANDIDATE;
const candidate = pack.candidate;
const current = pack.current;
const frames = document.querySelector('#frames');
const panel = document.querySelector('#panel');
const pickOut = document.querySelector('#pick');
const siteList = document.querySelector('#sites');
const params = new URLSearchParams(location.search);
let view = params.get('view') || 'proposed';
const layers = {
  terrain: true,
  hall: true,
  sites: true,
  roads: true,
  missing: true,
  fixture: params.get('fixture') === '1',
  contact: params.get('contact') !== '0',
  safe: true,
};
if (params.get('panel') === '1') panel.classList.add('open');
document.querySelector('#status').textContent = `${candidate.id} · ${candidate.status} · ${candidate.ownerAcceptance}`;

function project(cam, x, y) {
  const [a, b, c, d, e, f] = cam;
  return [a * x + c * y + e, b * x + d * y + f];
}
function inverse(cam, x, y) {
  const [a, b, c, d, e, f] = cam;
  const det = a * d - b * c;
  return [(d * (x - e) - c * (y - f)) / det, (-b * (x - e) + a * (y - f)) / det];
}
function ns(name, attrs) {
  const node = document.createElementNS('http://www.w3.org/2000/svg', name);
  for (const [key, value] of Object.entries(attrs)) node.setAttribute(key, value);
  return node;
}
function poly(cam, rect) {
  const [x, y, w, h] = rect;
  return [[x, y], [x + w, y], [x + w, y + h], [x, y + h]].map(p => project(cam, p[0], p[1]).join(',')).join(' ');
}
function imageToSource(point) {
  const m = candidate.hall.matrix;
  return [m[0][0] * point[0] + m[0][2], m[1][1] * point[1] + m[1][2]];
}

function draw(host, model, label) {
  host.replaceChildren();
  const terrain = document.createElement('img');
  terrain.alt = '';
  terrain.src = '../' + (model.image || current.terrain);
  terrain.hidden = !layers.terrain;
  const svg = ns('svg', { viewBox: '0 0 1376 768', preserveAspectRatio: 'xMidYMid meet' });
  svg.dataset.model = model.name;
  if (layers.missing && model.missing) {
    const [x, y, x2, y2] = model.missing;
    const hatch = ns('g', {});
    for (let i = x; i < x2; i += 8) hatch.append(ns('line', { x1: i, y1: y, x2: i + 4, y2: y2, stroke: '#c83e38', 'stroke-width': 1 }));
    hatch.append(ns('rect', { x, y, width: x2 - x, height: y2 - y, fill: 'none', stroke: '#c83e38', 'stroke-width': 3 }));
    svg.append(hatch);
  }
  if (layers.roads) {
    for (const road of model.roads || []) {
      svg.append(ns('polyline', { points: road.map(p => project(model.camera, p[0], p[1]).join(',')).join(' '), fill: 'none', stroke: '#9c8870', 'stroke-width': 10 }));
    }
    for (const [x, y] of model.blocked || []) svg.append(ns('polygon', { points: poly(model.camera, [x, y, 1, 1]), fill: '#3d6d8866' }));
  }
  if (layers.hall && model.hall) {
    const m = model.hall.matrix;
    svg.append(ns('image', { href: '../' + model.hall.file, x: 0, y: 0, width: model.hall.width, height: model.hall.height, transform: `matrix(${m[0][0]} ${m[1][0]} ${m[0][1]} ${m[1][1]} ${m[0][2]} ${m[1][2]})` }));
  }
  if (layers.contact && model.contact?.sourceSamples?.length) {
    svg.append(ns('polyline', {
      points: model.contact.sourceSamples.map(p => p.join(',')).join(' '),
      fill: 'none', stroke: '#70b9c5', 'stroke-width': 3, 'pointer-events': 'none',
    }));
    for (const gap of model.contact.gaps || []) {
      const from = imageToSource(gap.from);
      const to = imageToSource(gap.to);
      svg.append(ns('line', { x1: from[0], y1: from[1], x2: to[0], y2: to[1], stroke: '#c83e38', 'stroke-dasharray': '6 4', 'stroke-width': 2, 'pointer-events': 'none' }));
    }
  }
  if (layers.sites) {
    for (const site of model.sites) {
      const group = ns('g', { class: 'site', 'data-site': site.id });
      const focused = window.candidateFocus?.site === site.id && model.name !== 'current';
      group.append(ns('polygon', {
        points: poly(model.camera, site.rect),
        fill: site.id === 'townhall' ? '#77655299' : '#40544a66',
        stroke: focused ? '#f1e9d9' : '#d5b573',
        'stroke-width': focused ? 5 : 2,
        'pointer-events': 'none',
      }));
      svg.append(group);
    }
  }
  if (layers.fixture && model.mature) {
    const blocking = new Set((model.mature.relations || []).filter(item => item.class === 'blocking').map(item => item.far));
    for (const item of model.mature.structures) {
      const [x, y, w, h] = item.body;
      svg.append(ns('rect', { x, y, width: w, height: h, fill: '#c9a35b33', stroke: '#f1e9d9', 'stroke-width': 2, 'pointer-events': 'none' }));
      svg.append(ns('circle', { cx: item.door[0], cy: item.door[1], r: 5, fill: blocking.has(item.id) ? '#c83e38' : '#70b9c5', 'pointer-events': 'none' }));
    }
  }
  if (layers.safe) svg.append(ns('rect', { x: 24, y: 24, width: 1328, height: 720, fill: 'none', stroke: '#70b9c5', 'stroke-width': 2, 'pointer-events': 'none' }));
  const caption = document.createElement('div');
  caption.className = 'caption';
  caption.textContent = label;
  host.append(terrain, svg, caption);
  svg.addEventListener('click', event => {
    const rect = svg.getBoundingClientRect();
    const scale = Math.min(rect.width / 1376, rect.height / 768);
    const sx = (event.clientX - rect.left - (rect.width - 1376 * scale) / 2) / scale;
    const sy = (event.clientY - rect.top - (rect.height - 768 * scale) / 2) / scale;
    let site = null;
    if (sx >= 0 && sy >= 0 && sx <= 1376 && sy <= 768) {
      const point = inverse(model.camera, sx, sy);
      site = model.sites.find(item => {
        const [x, y, w, h] = item.rect;
        return point[0] >= x && point[0] <= x + w && point[1] >= y && point[1] <= y + h;
      })?.id ?? null;
      window.candidatePick = { view: model.name, source: [sx, sy], world: point, site };
    } else window.candidatePick = { view: model.name, source: [sx, sy], site: null };
    pickOut.textContent = (window.candidatePick.site || 'none') + ' · map · ' + model.name;
  });
}

function models() {
  const proposed = {
    name: 'proposed',
    camera: candidate.camera,
    sites: candidate.geometry.sites,
    roads: candidate.geometry.roads,
    blocked: candidate.geometry.blocked,
    hall: candidate.hall,
    contact: candidate.contact,
    mature: candidate.mature,
    missing: candidate.missingTerrain.sourceRect,
  };
  return {
    current: {
      name: 'current',
      camera: current.camera,
      sites: current.sites,
      roads: current.roads,
      blocked: current.blocked,
      hall: current.hall,
      contact: null,
      mature: null,
      missing: null,
    },
    proposed,
    collected: {
      ...proposed,
      name: 'collected',
      hall: null,
      image: candidate.painting.file,
    },
  };
}

function fillSites() {
  siteList.replaceChildren();
  for (const site of candidate.geometry.sites) {
    const button = document.createElement('button');
    button.type = 'button';
    button.dataset.site = site.id;
    button.textContent = site.id;
    button.setAttribute('aria-current', window.candidateFocus?.site === site.id ? 'true' : 'false');
    button.onclick = () => {
      window.candidateFocus = { view: 'proposed', site: site.id, source: 'list' };
      pickOut.textContent = site.id + ' · list';
      render();
    };
    siteList.append(button);
  }
}

function measure() {
  const header = document.querySelector('header').getBoundingClientRect();
  const footer = document.querySelector('footer').getBoundingClientRect();
  const stage = document.querySelector('#stage').getBoundingClientRect();
  const open = panel.classList.contains('open') ? panel.getBoundingClientRect() : null;
  window.candidateMetrics = {
    viewport: [window.innerWidth, window.innerHeight],
    chromePx: Math.round(header.height + footer.height),
    headerPx: Math.round(header.height),
    footerPx: Math.round(footer.height),
    stageHeight: Math.round(stage.height),
    stageWidth: Math.round(stage.width),
    panelWidth: open ? Math.round(open.width) : 0,
    reviewChromeRecorded: candidate.viewport.reviewChromePx,
    runtimeChromeBudgetPx: candidate.viewport.runtimeChromeBudgetPx,
    paintingFidelity: candidate.painting.spatialFidelity,
  };
}

function render() {
  const all = models();
  frames.classList.toggle('compare', view === 'compare');
  frames.replaceChildren();
  const shown = view === 'compare' ? ['current', 'proposed'] : [view];
  const labels = {
    current: 'Current contract',
    proposed: 'Proposed v2 · contact is the stone foot, not a finished terrace',
    collected: 'Collected batch 14 · spatial fidelity FAIL · not adopted',
  };
  for (const name of shown) {
    const pane = document.createElement('div');
    pane.className = 'pane';
    frames.append(pane);
    draw(pane, all[name], labels[name]);
  }
  fillSites();
  for (const button of document.querySelectorAll('#nav button')) button.setAttribute('aria-current', button.dataset.view === view ? 'true' : 'false');
  document.querySelector('#context').setAttribute('aria-expanded', panel.classList.contains('open') ? 'true' : 'false');
  measure();
}

document.querySelector('#context').onclick = () => { panel.classList.toggle('open'); render(); };
for (const input of document.querySelectorAll('[data-layer]')) {
  input.checked = Boolean(layers[input.dataset.layer]);
  input.onchange = () => { layers[input.dataset.layer] = input.checked; render(); };
}
for (const button of document.querySelectorAll('#nav button')) button.onclick = () => { view = button.dataset.view; render(); };
window.addEventListener('resize', measure);
window.candidateState = () => ({ view, layers, open: panel.classList.contains('open'), focus: window.candidateFocus || null });
render();
