const ACTIVE_ADVENTURE_GEOMETRY_VERSION = 4;

export function campaignMapImage(world) {
  // The supplied picture is a visual example only. Accept the production map
  // only when its current geometry and source binding point to the same asset.
  const production = world?.productionMapFile;
  const binding = world?.sourceBindings?.production;
  const geometry = world?.geometry;
  if (!production || binding?.role !== 'game-specific-runtime-map'
    || binding.file !== production || binding.geometryVersion !== ACTIVE_ADVENTURE_GEOMETRY_VERSION
    || geometry?.version !== ACTIVE_ADVENTURE_GEOMETRY_VERSION || geometry.sourceFile !== production
    || !binding.sha256 || geometry.sourceSha256 !== binding.sha256) return '';
  return production;
}

export function isIntegratedAdventureMap(world) {
  return Boolean(campaignMapImage(world));
}
