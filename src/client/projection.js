export const TARGET_PX = 48;
export function targetSourceSize(scale) { return TARGET_PX / scale; }
export function project(matrix, [x, y]) { const [a,b,c,d,e,f] = matrix; return [a*x+c*y+e,b*x+d*y+f]; }
export function inverse(matrix, [x, y]) {
  const [a,b,c,d,e,f] = matrix, det = a*d-b*c;
  if (Math.abs(det) < 1e-8) throw new Error('Noninvertible camera');
  return [(d*(x-e)-c*(y-f))/det,(-b*(x-e)+a*(y-f))/det];
}
function clamp(value, min, max) { return Math.min(max, Math.max(min, value)); }

export function boundsOf(points) {
  let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
  for (const [x, y] of points) {
    minX = Math.min(minX, x); minY = Math.min(minY, y);
    maxX = Math.max(maxX, x); maxY = Math.max(maxY, y);
  }
  return { minX, minY, maxX, maxY };
}

export function unionBounds(a, b) {
  return { minX: Math.min(a.minX, b.minX), minY: Math.min(a.minY, b.minY), maxX: Math.max(a.maxX, b.maxX), maxY: Math.max(a.maxY, b.maxY) };
}

export function transformedBounds(matrix, width, height) {
  const [a, b, e] = matrix[0];
  const [c, d, f] = matrix[1];
  return boundsOf([[0, 0], [width, 0], [width, height], [0, height]].map(([x, y]) => [a * x + b * y + e, c * x + d * y + f]));
}

// One uniform scale. A focus box, plus hitPx of screen margin, stays inside the stage.
// Cover is used only when that box still fits; otherwise the scale drops and aspect stays.
export function camera(source, width, height, focus = null, hitPx = 0) {
  const contain = Math.min(width / source[0], height / source[1]);
  const cover = Math.max(width / source[0], height / source[1]);
  let scale = !focus && contain * source[0] < width * 0.8 ? cover : contain;
  if (focus) {
    const spanX = Math.max(1e-6, focus.maxX - focus.minX);
    const spanY = Math.max(1e-6, focus.maxY - focus.minY);
    const roomW = width - hitPx * 2;
    const roomH = height - hitPx * 2;
    const fit = roomW > 0 && roomH > 0 ? Math.min(roomW / spanX, roomH / spanY) : contain;
    scale = Math.min(cover, fit);
  }
  const viewW = width / scale;
  const viewH = height / scale;
  const pad = focus ? hitPx / scale : 0;
  const minX = focus ? focus.minX - pad : 0;
  const minY = focus ? focus.minY - pad : 0;
  const maxX = focus ? focus.maxX + pad : source[0];
  const maxY = focus ? focus.maxY + pad : source[1];
  let originX = focus ? minX + (maxX - minX - viewW) / 2 : (source[0] - viewW) / 2;
  let originY = focus ? minY + (maxY - minY - viewH) / 2 : (source[1] - viewH) / 2;
  originX = placeWindow(originX, viewW, source[0]);
  originY = placeWindow(originY, viewH, source[1]);
  const mode = Math.abs(scale - cover) < 1e-9 ? 'cover' : Math.abs(scale - contain) < 1e-9 ? 'contain' : 'fit';
  return { scale, offset: [-originX * scale, -originY * scale], mode, window: [originX, originY, viewW, viewH] };
}

export function coverCamera(source, width, height) {
  if (![...source, width, height].every(Number.isFinite) || source[0] <= 0 || source[1] <= 0 || width <= 0 || height <= 0) {
    throw new RangeError('A cover camera needs positive dimensions');
  }
  const scale = Math.max(width / source[0], height / source[1]);
  const viewWidth = width / scale;
  const viewHeight = height / scale;
  const originX = (source[0] - viewWidth) / 2;
  const originY = (source[1] - viewHeight) / 2;
  return {
    scale,
    offset: [-originX * scale, -originY * scale],
    mode: 'cover',
    window: [originX, originY, viewWidth, viewHeight],
  };
}
export function wideBoardCamera(source, width, height, boardTop, boardBottom) {
  if (width / height < 2) return camera(source, width, height);
  const scale = width / source[0];
  const windowHeight = height / scale;
  const boardSpan = boardBottom - boardTop;
  const edgeMargin = 12;
  if (windowHeight >= boardSpan + edgeMargin * 2) {
    const centerY = (boardTop + boardBottom) / 2;
    const originY = centerY - windowHeight / 2;
    return {
      scale,
      offset: [0, -originY * scale],
      mode: 'cover',
      window: [0, originY, source[0], windowHeight],
    };
  }
  const focus = { minX: 0, minY: boardTop, maxX: source[0], maxY: boardBottom };
  return camera(source, width, height, focus);
}

// Follow a board point while keeping the transformed world painting over the
// complete stage. Side inspectors reduce the useful play width, but they sit
// above the scene and must not expose a blank strip beside a panned map.
export function focusPointCamera(source, stageWidth, stageHeight, visibleWidth, point, minimumScale = 0) {
  const [sourceWidth, sourceHeight] = source;
  const [pointX, pointY] = point;
  if (![sourceWidth, sourceHeight, stageWidth, stageHeight, visibleWidth, pointX, pointY].every(Number.isFinite)
    || sourceWidth <= 0 || sourceHeight <= 0 || stageWidth <= 0 || stageHeight <= 0
    || visibleWidth <= 0 || pointX < 0 || pointX > sourceWidth || pointY < 0 || pointY > sourceHeight) {
    throw new RangeError('A focused camera needs positive dimensions and an in-frame point');
  }
  const targetX = clamp(visibleWidth * 0.7, 0, stageWidth);
  const scaleForFocusAndCoverage = pointX < sourceWidth
    ? (stageWidth - targetX) / (sourceWidth - pointX)
    : stageWidth / sourceWidth;
  const scale = Math.max(minimumScale, stageWidth / sourceWidth, stageHeight / sourceHeight, scaleForFocusAndCoverage);
  const left = stageWidth - sourceWidth * scale;
  const top = stageHeight - sourceHeight * scale;
  const offsetX = clamp(targetX - pointX * scale, left, 0);
  const targetY = stageHeight * 0.68;
  const offsetY = clamp(targetY - pointY * scale, top, 0);
  return {
    scale,
    offset: [offsetX, offsetY],
    mode: 'focus-cover',
    window: [-offsetX / scale, -offsetY / scale, stageWidth / scale, stageHeight / scale],
  };
}

// The side panel sits above the scene. Keep the world fitted to the complete
// stage so opening it does not create letterbox bands; callers still use the
// unobscured width when placing labels and other screen-space affordances.
export function worldViewportWidth(stageWidth, visibleWidth, panelOpen, viewportWidth = stageWidth) {
  return panelOpen ? Math.max(stageWidth, viewportWidth) : visibleWidth;
}

function placeWindow(origin, view, sourceSize) {
  // Keep the painting against the stage. Padding that falls outside the source
  // must not push the terrain down and leave a black band.
  if (view >= sourceSize) return (sourceSize - view) / 2;
  return clamp(origin, 0, sourceSize - view);
}
export function kingdomFocusBounds(geo, hall) {
  const centres = geo.sites.map(site => {
    const [x, y, w, h] = site.rect;
    return project(geo.worldToSource, [x + w / 2, y + h / 2]);
  });
  return unionBounds(boundsOf(centres), transformedBounds(hall.matrix, hall.width, hall.height));
}
