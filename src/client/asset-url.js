// Source development uses original art. The build writes only its own URL table.
import assets from '../data/build-assets.json' with { type: 'json' };

export function resolveAssetUrl(value, mapping = assets) {
  if (typeof value !== 'string') return value;
  const suffixAt = value.search(/[?#]/);
  const file = suffixAt < 0 ? value : value.slice(0, suffixAt);
  const suffix = suffixAt < 0 ? '' : value.slice(suffixAt);
  const relative = file.startsWith('./') ? file.slice(2) : file;
  if (mapping[relative]) return mapping[relative] + suffix;
  // Sprite-sheet crops may resolve against import.meta.url before reaching the renderer.
  // Android's appassets URL has both /assets/www/ and the game's /assets/ prefix.
  for (let start = file.indexOf('/assets/'); start >= 0; start = file.indexOf('/assets/', start + 1)) {
    const absoluteAsset = file.slice(start + 1);
    if (mapping[absoluteAsset]) return file.slice(0, start + 1) + mapping[absoluteAsset] + suffix;
  }
  return value;
}
