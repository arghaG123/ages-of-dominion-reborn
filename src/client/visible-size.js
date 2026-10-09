// Visible size is CSS pixels after the camera scale. A world-unit cap and a CSS cap
// both apply, and the smaller one limits the longer visible side and the shorter side.

export function visibleBox(plate, requestedHeight, cssPerWorld) {
  const scale = Number.isFinite(cssPerWorld) && cssPerWorld > 0 ? cssPerWorld : 1;
  const height0 = Number.isFinite(requestedHeight) && requestedHeight > 0 ? requestedHeight : 0;
  const srcW = Number(plate?.width) > 0 ? Number(plate.width) : height0;
  const srcH = Number(plate?.height) > 0 ? Number(plate.height) : height0;
  const aspect = srcH > 0 ? srcW / srcH : 1;
  let height = height0;
  let width = height * aspect;
  const caps = [];
  if (Number.isFinite(plate?.maxVisibleCssPx) && plate.maxVisibleCssPx > 0) caps.push(plate.maxVisibleCssPx);
  if (Number.isFinite(plate?.staticMaxHeight) && plate.staticMaxHeight > 0) {
    caps.push(plate.staticMaxHeight);
    caps.push(plate.staticMaxHeight * scale);
  }
  if (!caps.length && Number.isFinite(plate?.defaultVisibleCssPx) && plate.defaultVisibleCssPx > 0) caps.push(plate.defaultVisibleCssPx);
  let capCss = null;
  if (caps.length && height > 0) {
    capCss = Math.min(...caps);
    const longest = Math.max(width * scale, height * scale);
    if (longest > capCss) {
      const fitted = capCss / longest;
      width *= fitted;
      height *= fitted;
    }
  }
  return {
    width,
    height,
    cssWidth: width * scale,
    cssHeight: height * scale,
    capCss,
  };
}
