// Normalizes producer residual rows into the Code consumer contract.
// Producer READY labels and spatial PASS flags are not copied through.

export const OUTLINE_DERIVATIVE_IDS = new Set([
  'troop-stone-melee',
  'troop-stone-ranged',
  'troop-industrial-ranged',
  'troop-industrial-heavy',
]);

export const SHEET_OR_SILHOUETTE_IDS = new Set([
  'attacker-bronze-runner',
  'attacker-medieval-archer',
  'troop-iron-melee',
  'troop-medieval-ranged',
  'troop-gunpowder-heavy',
  'troop-future-ranged',
]);

export const PARTIAL_SPRITE_IDS = new Set([
  'troop-industrial-melee',
  'troop-modern-ranged',
  'troop-modern-heavy',
]);

export const JOINT_FAIL_IDS = new Set([
  'healer-head-to-torso',
  'healer-skirt-to-leg',
  'knight-thigh-greave',
  'paladin-greave-boot',
  'paladin-head-raster',
  'paladin-thigh-knee',
]);

export const MAGENTA_GEAR_IDS = new Set([
  'gear-stone-helm',
  'gear-stone-boots',
]);

const SOURCE_FRAMES = new Set([
  'ORIGIN_TOP_LEFT_NATIVE',
  'SOURCE_NATIVE',
  'source',
]);

export function positiveInt(value) {
  return typeof value === 'number' && Number.isInteger(value) && value > 0;
}

export function asWH(dimensions) {
  if (!dimensions) return null;
  if (Array.isArray(dimensions)) {
    if (dimensions.length !== 2 || !positiveInt(dimensions[0]) || !positiveInt(dimensions[1])) return null;
    return { width: dimensions[0], height: dimensions[1] };
  }
  if (typeof dimensions === 'object' && positiveInt(dimensions.width) && positiveInt(dimensions.height)) {
    return { width: dimensions.width, height: dimensions.height };
  }
  return null;
}

export function asVec2(value) {
  if (Array.isArray(value) && value.length === 2 && value.every(item => typeof item === 'number' && Number.isFinite(item))) return [value[0], value[1]];
  if (value && typeof value === 'object' && typeof value.x === 'number' && typeof value.y === 'number' && Number.isFinite(value.x) && Number.isFinite(value.y)) return [value.x, value.y];
  return null;
}

export function asAffine(value) {
  if (!Array.isArray(value) || value.length !== 6) return null;
  if (!value.every(item => typeof item === 'number' && Number.isFinite(item))) return null;
  return value.slice();
}

export function applyAffine(affine, point) {
  return [
    affine[0] * point[0] + affine[2] * point[1] + affine[4],
    affine[1] * point[0] + affine[3] * point[1] + affine[5],
  ];
}

function insideHalfOpen(point, width, height) {
  return point[0] >= 0 && point[1] >= 0 && point[0] < width && point[1] < height;
}

function boxInside(box, width, height) {
  return box[0] >= 0 && box[1] >= 0 && box[2] <= width && box[3] <= height && box[2] > box[0] && box[3] > box[1];
}

function pointsOf(row) {
  const ground = [];
  const footprint = [];
  if (Array.isArray(row.groundContact)) {
    for (const point of row.groundContact) {
      const next = asVec2(point);
      if (!next) return { error: 'groundContact' };
      ground.push(next);
    }
  } else if (row.groundContact != null) return { error: 'groundContact' };
  if (Array.isArray(row.footprint)) {
    for (const point of row.footprint) {
      const next = asVec2(point);
      if (!next) return { error: 'footprint' };
      footprint.push(next);
    }
  } else if (row.footprint != null) return { error: 'footprint' };
  const entrance = row.entrance == null ? null : asVec2(row.entrance);
  if (row.entrance != null && !entrance) return { error: 'entrance' };
  let envelope = null;
  if (Array.isArray(row.heightEnvelope)) {
    if (row.heightEnvelope.length !== 4 || !row.heightEnvelope.every(item => typeof item === 'number' && Number.isFinite(item))) return { error: 'heightEnvelope' };
    envelope = row.heightEnvelope.slice();
  } else if (row.heightEnvelope != null) return { error: 'heightEnvelope' };
  return { ground, footprint, entrance, envelope };
}

function mapPoints(points, affine) {
  return points.map(point => applyAffine(affine, point));
}

function classifyUse(row, support, scene) {
  if (support || scene) return 'REFERENCE_ONLY';
  const role = String(row.role || '');
  const id = String(row.id || '');
  if (/joint|diagram|chain|socket|subchain/i.test(role) || /joint|diagram|chain|subchain/.test(id)) return 'JOINT_METADATA';
  if (/effect|fx|sheet/i.test(role)) return 'ATLAS_FRAME';
  if (/mount|transport|card|portrait|scenic/i.test(role) || id === 'knight-mounted-master') return 'STATIC_CARD';
  if (/gear|artifact|resource|skill|spell|material|icon/i.test(role)) return 'MATERIAL';
  return 'SPRITE';
}

function sideOf(value) {
  if (value === 'LEFT' || value === 'RIGHT' || value === 'UNKNOWN' || value === 'NOT_APPLICABLE') return value;
  return 'UNKNOWN';
}

function gateWorse(current, next) {
  const rank = { PASS: 0, NOT_APPLICABLE: 0, UNVERIFIED: 1, PARTIAL: 2, BLOCKED: 3, FAIL: 4 };
  return (rank[next] ?? 3) > (rank[current] ?? 0) ? next : current;
}

export function adaptProducerRow(row, options = {}) {
  const producer = options.producer === 'ENVIRONMENT' ? 'ENVIRONMENT' : 'ACTORS';
  const support = Boolean(options.support);
  const scene = Boolean(options.scene);
  const limitations = Array.isArray(row?.limitations) ? row.limitations.slice() : [];
  const blockedBy = Array.isArray(row?.blockedBy) ? row.blockedBy.slice() : [];
  const id = typeof row?.id === 'string' ? row.id : '';
  const dimensions = asWH(row?.output?.dimensions);
  const sourceToOutput = asAffine(row?.sourceToOutput);
  const parsed = pointsOf(row || {});
  const use = classifyUse(row || {}, support, scene);
  const outputPath = row?.output?.path || null;
  const gates = {
    binding: 'UNVERIFIED',
    semantics: row?.gates?.semantics || 'UNVERIFIED',
    matte: 'UNVERIFIED',
    spatial: 'UNVERIFIED',
    articulation: use === 'JOINT_METADATA' ? 'PARTIAL' : 'NOT_APPLICABLE',
    runtime: 'UNVERIFIED',
    owner: 'UNVERIFIED',
  };
  if (!id) {
    gates.binding = 'FAIL';
    blockedBy.push('missing id');
  }
  if (parsed.error) {
    gates.spatial = 'FAIL';
    blockedBy.push(`malformed ${parsed.error}`);
  }
  if (row?.output?.dimensions != null && !dimensions) {
    gates.binding = 'FAIL';
    blockedBy.push('malformed dimensions');
  }
  if (row?.sourceToOutput != null && !sourceToOutput) {
    gates.binding = 'FAIL';
    blockedBy.push('malformed sourceToOutput');
  }
  if ((use === 'SPRITE' || use === 'MATERIAL' || use === 'STATIC_CARD' || use === 'ATLAS_FRAME') && !outputPath) {
    gates.binding = 'FAIL';
    blockedBy.push('image use has no output');
  }
  if (use === 'JOINT_METADATA') {
    limitations.push('Joint or diagram metadata is not a body and is not an image URL.');
    gates.runtime = 'BLOCKED';
    if (!outputPath) gates.binding = gates.binding === 'FAIL' ? 'FAIL' : 'PASS';
  }
  if (JOINT_FAIL_IDS.has(id) || row?.status === 'FAIL') {
    gates.semantics = 'FAIL';
    gates.articulation = 'FAIL';
    gates.runtime = 'BLOCKED';
    blockedBy.push('failed joint or producer FAIL');
  }
  if (OUTLINE_DERIVATIVE_IDS.has(id)) {
    gates.matte = 'FAIL';
    gates.runtime = 'BLOCKED';
    limitations.push('Producer derivative matte is an outline. The identity sourceToOutput is not a repaired crop.');
    blockedBy.push('outline derivative');
  }
  if (SHEET_OR_SILHOUETTE_IDS.has(id)) {
    gates.matte = 'FAIL';
    gates.semantics = 'FAIL';
    gates.runtime = 'BLOCKED';
    blockedBy.push('sheet, scenery, or damaged silhouette');
  }
  if (MAGENTA_GEAR_IDS.has(id)) {
    gates.matte = 'FAIL';
    gates.runtime = 'BLOCKED';
    blockedBy.push('magenta gear background');
  }
  if (PARTIAL_SPRITE_IDS.has(id) || row?.status === 'PARTIAL') {
    gates.matte = gateWorse(gates.matte, 'PARTIAL');
    gates.runtime = 'PARTIAL';
    limitations.push('Kept partial. Not promoted to a general sprite.');
  }
  if (support) {
    gates.semantics = 'FAIL';
    gates.runtime = 'BLOCKED';
    limitations.push('Full mock screenshot. Reference only. Not a runtime background.');
    blockedBy.push('support screenshot');
  }
  if (scene) {
    gates.spatial = 'PARTIAL';
    gates.runtime = 'BLOCKED';
    limitations.push('Scene proposal stays inactive.');
    blockedBy.push('scene not promoted');
  }
  if (use === 'ATLAS_FRAME' && !row?.frames && !row?.transforms?.frames) {
    gates.runtime = 'BLOCKED';
    limitations.push('Effect sheet has no per-frame ROI.');
    blockedBy.push('missing frame ROI');
  }
  const audit = options.audit;
  if (audit?.pixel === 'FAIL' || audit?.decision === 'HOLD_GENERAL_WORLD_PLACEMENT') {
    gates.matte = 'FAIL';
    gates.runtime = gateWorse(gates.runtime, 'BLOCKED');
    blockedBy.push(audit.decision || 'pixel FAIL');
  }

  let coordinateFrame = null;
  let groundContact = parsed.ground || null;
  let footprint = parsed.footprint || null;
  let entrance = parsed.entrance || null;
  let heightEnvelope = parsed.envelope || null;
  if (!parsed.error && dimensions && (groundContact?.length || footprint?.length || entrance || heightEnvelope)) {
    const declaredSource = SOURCE_FRAMES.has(row?.frame);
    const sample = [...(groundContact || []), ...(footprint || []), ...(entrance ? [entrance] : [])];
    const outputFits = sample.every(point => insideHalfOpen(point, dimensions.width, dimensions.height))
      && (!heightEnvelope || boxInside(heightEnvelope, dimensions.width, dimensions.height));
    if (outputFits && !declaredSource) {
      coordinateFrame = 'OUTPUT_CROP';
      gates.spatial = gates.spatial === 'FAIL' ? 'FAIL' : 'PARTIAL';
      limitations.push('Coordinates fit the output. Producer spatial PASS was not adopted.');
    } else if (sourceToOutput) {
      const mappedGround = groundContact ? mapPoints(groundContact, sourceToOutput) : null;
      const mappedFoot = footprint ? mapPoints(footprint, sourceToOutput) : null;
      const mappedEntrance = entrance ? applyAffine(sourceToOutput, entrance) : null;
      const mappedEnvelope = heightEnvelope ? [
        applyAffine(sourceToOutput, [heightEnvelope[0], heightEnvelope[1]]),
        applyAffine(sourceToOutput, [heightEnvelope[2], heightEnvelope[3]]),
      ] : null;
      const envelopeBox = mappedEnvelope ? [mappedEnvelope[0][0], mappedEnvelope[0][1], mappedEnvelope[1][0], mappedEnvelope[1][1]] : null;
      const mapped = [...(mappedGround || []), ...(mappedFoot || []), ...(mappedEntrance ? [mappedEntrance] : [])];
      const fits = mapped.every(point => insideHalfOpen(point, dimensions.width, dimensions.height))
        && (!envelopeBox || boxInside(envelopeBox, dimensions.width, dimensions.height));
      coordinateFrame = 'SOURCE_NATIVE';
      if (fits) {
        groundContact = mappedGround;
        footprint = mappedFoot;
        entrance = mappedEntrance;
        heightEnvelope = envelopeBox;
        coordinateFrame = 'OUTPUT_CROP';
        gates.spatial = 'PARTIAL';
        limitations.push('Source coordinates were mapped by the recorded affine. Ground pixels are not yet proof of contact.');
      } else {
        gates.spatial = 'FAIL';
        blockedBy.push('contact outside output after recorded affine');
      }
    } else {
      coordinateFrame = declaredSource ? 'SOURCE_NATIVE' : null;
      gates.spatial = 'BLOCKED';
      blockedBy.push('missing source frame or transform');
      groundContact = null;
      footprint = null;
      entrance = null;
      heightEnvelope = null;
    }
  } else if (!parsed.error) {
    gates.spatial = use === 'SPRITE' ? 'PARTIAL' : 'NOT_APPLICABLE';
    coordinateFrame = dimensions ? 'OUTPUT_CROP' : null;
  }

  const repair = options.repair;
  if (repair?.subjectPreserved === true && repair.outputPath && asWH(repair.dimensions) && asAffine(repair.sourceToOutput)) {
    gates.matte = 'PASS';
    gates.binding = 'PASS';
    gates.spatial = 'PARTIAL';
    gates.runtime = 'PASS';
    limitations.push('Code consumer crop replaced the outline derivative.');
    return asset({
      id, producer: 'CODE', row, outputPath: repair.outputPath, outputSha: repair.outputSha256 || null,
      dimensions: asWH(repair.dimensions), sourceToOutput: asAffine(repair.sourceToOutput),
      coordinateFrame: 'OUTPUT_CROP', groundContact: repair.groundContact || null, footprint: null,
      entrance: null, heightEnvelope: repair.heightEnvelope || null, use: 'SPRITE', gates, limitations, blockedBy: [],
      side: sideOf(row?.side),
    });
  }

  const promotable = gates.binding !== 'FAIL' && gates.matte !== 'FAIL' && gates.matte !== 'PARTIAL'
    && gates.runtime !== 'BLOCKED' && gates.runtime !== 'FAIL' && gates.runtime !== 'PARTIAL'
    && outputPath && dimensions && (use === 'MATERIAL' || use === 'STATIC_CARD') && !support && !scene
    && gates.spatial !== 'FAIL' && gates.spatial !== 'BLOCKED';
  if (promotable && options.hashOk === true && row?.status === 'READY') {
    gates.binding = 'PASS';
    gates.matte = 'PASS';
    gates.runtime = 'PASS';
  } else if (gates.runtime === 'BLOCKED' || gates.runtime === 'PARTIAL' || gates.runtime === 'FAIL') {
    // Keep the stronger gate.
  } else {
    gates.runtime = 'BLOCKED';
  }
  if (gates.binding === 'UNVERIFIED' && options.hashOk === true) gates.binding = 'PASS';
  if (gates.binding === 'UNVERIFIED' && options.hashOk === false) {
    gates.binding = 'FAIL';
    gates.runtime = 'BLOCKED';
    blockedBy.push('hash mismatch');
  }

  return asset({
    id, producer, row, outputPath: use === 'JOINT_METADATA' && !outputPath ? null : outputPath,
    outputSha: row?.output?.sha256 || null, dimensions, sourceToOutput, coordinateFrame,
    groundContact, footprint, entrance, heightEnvelope, use, gates, limitations, blockedBy, side: sideOf(row?.side),
  });
}

function asset(input) {
  return {
    id: input.id,
    producer: input.producer,
    sourcePath: input.row?.source?.path || '',
    sourceSha256: input.row?.source?.sha256 || '',
    outputPath: input.outputPath,
    outputSha256: input.outputSha,
    dimensions: input.dimensions,
    sourceRoi: Array.isArray(input.row?.source?.roi) ? input.row.source.roi : null,
    sourceToOutput: input.sourceToOutput,
    coordinateFrame: input.coordinateFrame,
    groundContact: input.groundContact,
    footprint: input.footprint,
    entrance: input.entrance,
    heightEnvelope: input.heightEnvelope,
    role: input.row?.role || '',
    age: Number.isInteger(input.row?.age) ? input.row.age : null,
    classId: input.row?.classId || null,
    use: input.use,
    side: input.side,
    maxVisibleCssPx: typeof input.row?.maxDisplayCssPx === 'number' ? input.row.maxDisplayCssPx : null,
    gates: input.gates,
    evidencePaths: Array.isArray(input.row?.evidencePaths) ? input.row.evidencePaths.slice() : [],
    limitations: input.limitations,
    blockedBy: input.blockedBy,
    nextAction: input.gates.runtime === 'PASS' ? null : (input.row?.nextAction || 'Keep the prior validated consumer or a bounded card.'),
  };
}
