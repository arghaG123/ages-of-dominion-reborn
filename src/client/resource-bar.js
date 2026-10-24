// Header resource chips. The stored amount is unchanged. A long balance uses a
// compact label, and the full floored integer stays on the tooltip and the accessible name.

const CHIP_IDS = ['food', 'wood', 'stone', 'gold'];

export function resourceAmountText(value) {
  const floored = Math.floor(Number(value));
  const full = Number.isFinite(floored) && floored >= 0 ? String(floored) : '0';
  if (full.length <= 4) return { text: full, full };
  const amount = Number(full);
  const units = [[1e12, 'T'], [1e9, 'B'], [1e6, 'M'], [1e3, 'K']];
  for (const [scale, suffix] of units) {
    if (amount >= scale) {
      const scaled = amount / scale;
      const digits = scaled >= 100 ? 0 : 1;
      // Round down: 999,999 must never advertise one million before the
      // underlying balance can actually pay a one-million cost.
      const factor = 10 ** digits;
      let body = (Math.floor(scaled * factor) / factor).toFixed(digits).replace(/\.0$/, '');
      if (body.length > 4) {
        const exponent = Math.floor(Math.log10(amount));
        const mantissa = Math.floor(amount / 10 ** exponent * 10) / 10;
        return { text: `${mantissa}e${exponent}`, full };
      }
      return { text: `${body}${suffix}`, full };
    }
  }
  return { text: full, full };
}

// Boxes for the header contents at a landscape viewport width.
// Title, status, four chips, Menu and Save stay in separate bounds.
export function resourceBarLayout(viewportWidth) {
  const width = Math.max(480, viewportWidth);
  const inner = width - 32;
  const gap = 8;
  const titleW = Math.min(156, Math.round(inner * 0.2));
  const statusW = Math.min(96, Math.round(inner * 0.12));
  const menuW = 72;
  const saveW = 64;
  let x = 0;
  const title = { id: 'title', x, w: titleW, y: 0, h: 36 };
  x += titleW + gap;
  const status = { id: 'status', x, w: statusW, y: 0, h: 36 };
  x += statusW + gap;
  const save = { id: 'save', x: inner - saveW, w: saveW, y: 0, h: 36 };
  const menu = { id: 'menu', x: save.x - gap - menuW, w: menuW, y: 0, h: 36 };
  const resourcesX = x;
  const resourcesW = menu.x - gap - resourcesX;
  const chipGap = 4;
  const chipW = (resourcesW - chipGap * 3) / 4;
  const chips = CHIP_IDS.map((id, index) => ({
    id,
    x: resourcesX + index * (chipW + chipGap),
    w: chipW,
    y: 0,
    h: 28,
  }));
  return { inner, title, status, chips, menu, save };
}

export function boxesSeparate(boxes) {
  for (let i = 0; i < boxes.length; i += 1) {
    for (let j = i + 1; j < boxes.length; j += 1) {
      const a = boxes[i];
      const b = boxes[j];
      const overlap = a.x < b.x + b.w - 0.5 && b.x < a.x + a.w - 0.5 && a.y < b.y + b.h && b.y < a.y + a.h;
      if (overlap) return false;
    }
  }
  return boxes.every(box => box.w > 8 && box.x >= -0.5 && box.x + box.w <= boxes.reduce((max, item) => Math.max(max, item.x + item.w), 0) + 0.5);
}

export function resourceChipLabel(name, value) {
  const shown = resourceAmountText(value);
  return { name, text: shown.text, full: shown.full, title: `${name} ${shown.full}`, accessible: `${name} ${shown.full}` };
}
