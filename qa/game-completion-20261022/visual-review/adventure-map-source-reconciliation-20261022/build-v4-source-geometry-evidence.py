from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[4]
FOLDER = ROOT / 'qa/game-completion-20261022/visual-review/adventure-map-source-reconciliation-20261022'
WORLDS = json.loads((ROOT / 'src/data/adventure-worlds.json').read_text(encoding='utf-8'))
MANIFEST = json.loads((FOLDER / 'source-manifest.json').read_text(encoding='utf-8'))
OLD = json.loads((FOLDER / 'per-world-map-source-geometry-20261022.json').read_text(encoding='utf-8'))
V2 = json.loads((FOLDER / 'production-geometry-v2-preserved.json').read_text(encoding='utf-8'))
OLD_BY_ID = {row['id']: row for row in OLD['worlds']}
V2_BY_ID = {row['id']: row for row in V2['worlds']}
SOURCES = {(row['worldId'], row['role']): row for row in MANIFEST['sources']}
OVERLAY_DIR = 'qa/game-completion-20261022/visual-review/adventure-map-source-reconciliation-20261022/production-geometry-v4-overlays'
rows = []
for world in WORLDS:
    world_id = world['id']
    old = OLD_BY_ID[world_id]
    v2 = V2_BY_ID[world_id]
    reference = SOURCES[(world_id, 'reference')]
    generated = SOURCES[(world_id, 'generated-game-map')]
    terrain = SOURCES[(world_id, 'generated-terrain')]
    geometry = world['geometry']
    versions = [
        {'version': 1, 'sourceImage': reference['path'], 'sourceSha256': reference['sha256'], 'runtimeActive': False, 'role': 'reference-example-geometry', 'geometry': world['referenceGeometry']['geometry']},
        {'version': 2, 'sourceImage': v2['productionMapFile'], 'sourceSha256': v2['geometry']['sourceSha256'], 'runtimeActive': False, 'role': 'pre-correction-generated-map-geometry', 'geometry': v2['geometry']},
        {'version': 3, 'sourceImage': old['independentGeneratedMap']['path'], 'sourceSha256': old['runtimeGeometryV3']['sourceSha256'], 'runtimeActive': False, 'role': 'pre-overlap-fix-generated-map-geometry', 'supersededReason': 'Haunted Marsh dwelling/ruin and Astral Peaks ruin/shrine hitboxes overlapped.', 'geometry': old['runtimeGeometryV3']},
        {'version': 4, 'sourceImage': generated['path'], 'sourceSha256': generated['sha256'], 'runtimeActive': True, 'role': 'current-game-specific-production-geometry', 'geometry': geometry},
    ]
    rows.append({
        'stableWorldId': world_id,
        'title': world['title'],
        'referencePicture': {**reference, 'role': 'visual-direction-only'},
        'independentlyGeneratedProductionMap': {**generated, 'role': 'current-runtime-background'},
        'retainedGeneratedTerrain': {**terrain, 'role': 'separate-retained-asset-not-selected-by-campaign-world-runtime'},
        'runtimeUses': {
            'image': world['productionMapFile'],
            'geometryVersion': geometry['version'],
            'geometrySource': geometry['sourceFile'],
            'geometrySha256': geometry['sourceSha256'],
            'sourceBindingRole': world['sourceBindings']['production']['role'],
            'referenceImageUsed': False,
            'activeGeometry': geometry,
        },
        'geometryHistory': versions,
        'mapFeatures': world['mapFeatures'],
        'layoutCoverage': {
            'deterministicLayoutsPerWorld': 20,
            'allLayoutsPass': True,
            'siteCount': len(geometry['sites']),
            'resourceAndGuardAnchors': len([key for key in geometry['anchors'] if key != 'hero']),
            'crossingCount': len(geometry['bridges']),
            'roadCount': len(geometry['roads']),
            'evidence': 'tests/adventure-worlds.test.mjs: all twenty deterministic layouts per world; safe starts, anchors, sites, guards and approaches reachable.'
        },
        'visualEvidence': {
            'geometryOverlay': f'{OVERLAY_DIR}/{world_id}-production-geometry-v4.png',
            'mapContactSheet': 'qa/game-completion-20261022/visual-review/adventure-map-source-reconciliation-20261022/adventure-map-production-geometry-v4-contact.png',
            'comparison': 'Generated production map reviewed against owner examples for landscape quality and composition; geometry reviewed against the production artwork and gameplay requirements.',
            'ownerAcceptance': 'pending'
        },
        'naturalVisibleJourney': 'Sunlit Riverlands visible-controls journey recorded; no complete new visible-controls journey claimed for this world.' if world_id != 'grasslands' else 'Visible-controls journey covered travel, Shrine offer, bridge crossing, cache/site rewards, guard victory, settlement, save/reload, and retained XP/resources/army. Rechecked after v4 migration on isolated origin.',
        'remainingGaps': ['owner visual acceptance pending', 'no new full natural journey claimed for this world' if world_id != 'grasslands' else 'none for the scoped natural journey', 'per-map prompt/provider receipt provenance not found']
    })

result = {
    'classification': 'ADVENTURE_MAP_SOURCE_AND_GEOMETRY_CORRECTION_V4',
    'date': '2026-10-22',
    'status': 'Adventure source interpretation and geometry repair implemented; whole game remains INCOMPLETE.',
    'ownerCorrection': 'The twelve supplied images are random visual examples. They guide quality and composition only; production maps must be independently authored for the game.',
    'runtimeContract': {
        'selectorModule': 'src/client/adventure-map-source.js',
        'selectorBehavior': 'campaignMapImage accepts only the current productionMapFile when source binding, geometry source path, image SHA, and v4 geometry version agree; no reference-file, file, or mapFile fallback.',
        'rendererModule': 'src/client/main.js',
        'activeGeometryVersion': 4,
        'referenceRuntimeCount': 0,
        'worldCount': 12
    },
    'geometryCorrection': [
        {'worldId': 'haunted-marsh', 'siteId': 'dwelling', 'v3Rect': [0, 1, 3, 2], 'v4Rect': [0, 1, 2, 2], 'approachPreserved': [3, 1], 'reason': 'Remove one-cell overlap with ruin while retaining the mapped village area and its route entrance.'},
        {'worldId': 'astral-peaks', 'siteId': 'ruin', 'v3Rect': [9, 4, 3, 2], 'v4Rect': [9, 4, 2, 2], 'approachPreserved': [8, 5], 'reason': 'Separate the broken moon arch from the lunar gate site.'},
        {'worldId': 'astral-peaks', 'siteId': 'shrine', 'v3Rect': [10, 3, 2, 3], 'v4Rect': [11, 4, 1, 2], 'approachPreserved': [12, 5], 'reason': 'Center the interaction area on the visible lunar portal and remove its four-cell overlap with the ruin.'}
    ],
    'migration': {
        'campaignGeometryVersion': 4,
        'acceptedInputVersions': [1, 2, 3],
        'v3Behavior': 'Preserve valid position, discoveries, claims, collected caches, resources, guard resolutions and a valid pending encounter exactly; recover an invalid/disconnected position or pending encounter safely; malformed present versions remain errors.',
        'v1v2Behavior': 'Retain the prior remapping and safe recovery rules, preserving campaign progress and encounter packs.',
        'stableWorldIds': True,
        'userSavePolicy': 'No production-origin save was opened or reset. Only isolated test origin 127.0.0.1:41837 was migrated, saved, and reloaded.'
    },
    'verification': {
        'deterministicLayoutsPerWorld': 20,
        'deterministicLayoutsTotal': 240,
        'astralPeaksGold': {'anchor': [13.5, 5.5], 'cell': [13, 5], 'openAndReachableInAllLayouts': True},
        'siteFootprints': {'allSixPerWorldPresent': True, 'overlapCount': 0, 'approachesPreservedForGeometryCorrections': True},
        'focusedAdventureSuite': {'command': 'node --test tests/adventure-worlds.test.mjs', 'tests': 21, 'passed': 21, 'failed': 0},
        'fullNodeSuite': {'command': 'node --test tests/*.test.mjs', 'tests': 254, 'passed': 254, 'failed': 0, 'durationMs': 30594.5171},
        'visibleControlsJourney': {
            'worldId': 'grasslands',
            'actions': ['natural travel', 'claim Shrine lesson', 'cross water bridge', 'collect cache and claim site reward', 'settle guard encounter and receive rewards', 'save campaign', 'reload and continue with resources, XP and 17 army units intact'],
            'v4Migration': 'Loaded the existing isolated v3 campaign in the v4 runtime, saved it, reloaded it, and confirmed the same world, 516 gold, 110 XP, and 17 units.',
            'browserOrigin': 'http://127.0.0.1:41837/'
        },
        'responsiveEvidence': [
            {'requested': [825, 375], 'documentClient': [826, 375], 'mapRect': [0, 36.48, 537.6, 302.24], 'inspectorRect': [537.6, 54, 280, 281.2], 'mountedActorRect': [340.34, 92.61, 87.89, 85.86], 'screenshot': 'qa/game-completion-20261022/visual-review/adventure-map-source-reconciliation-20261022/live-run-v4/evidence/sunlit-v4-inspector-825x375-settled.jpg'},
            {'requested': [933, 424], 'documentClient': [934, 424], 'mapRect': [0, 30.52, 645.6, 362.96], 'inspectorRect': [645.6, 54, 280, 306], 'mountedActorRect': [417.96, 113.97, 87.89, 85.86], 'screenshot': 'qa/game-completion-20261022/visual-review/adventure-map-source-reconciliation-20261022/live-run-v4/evidence/sunlit-v4-inspector-933x424-settled.jpg'},
            {'requested': [1280, 720], 'documentClient': [1280, 720], 'mapRect': [0, 100.83, 922, 518.35], 'inspectorRect': [922, 72, 350, 568], 'mountedActorRect': [616.63, 254.2, 87.89, 85.86], 'screenshot': 'qa/game-completion-20261022/visual-review/adventure-map-source-reconciliation-20261022/live-run-v4/evidence/sunlit-v4-inspector-1280x720-settled.jpg'}
        ],
        'mapEdges': 'Full production image aspect ratio fits within each map pane; all four edges are visible with the inspector open.',
        'fog': 'Rendered Sunlit scene remains readable and moderately lit; QA includes fog samples at 0.32 opacity from the prior correction.',
        'visualAcceptance': 'Agent review completed; owner acceptance pending.'
    },
    'provenance': {
        'productionAssetDirectory': 'assets/derivatives/adventure-world-maps-generated-20261020',
        'referenceDirectory': 'assets/mocks/owner-approved-vast-adventure-maps-20261020',
        'sourceManifest': 'qa/game-completion-20261022/visual-review/adventure-map-source-reconciliation-20261022/source-manifest.json',
        'sourceManifestVerifiesHashesAndDimensions': True,
        'generationPromptsReceiptsFound': False,
        'note': 'The generated map PNGs remain available and were reused. The source manifest records paths, dimensions, byte sizes and SHA256; no per-map prompt/provider receipt record was found with the assets. No replacement purchase or provider call was made.'
    },
    'supersededEvidence': {
        'previousReport': 'qa/game-completion-20261022/visual-review/adventure-map-source-reconciliation-20261022/adventure-map-source-correction-and-verification-20261022.md',
        'previousGeometryVersion': 3,
        'oldIndividualOverlayFiles': 'Preserved for history; individual PNGs depict reference geometry v1 and must not be treated as current production geometry overlays.',
        'newEvidence': 'Use v4ContactSheet and each world visualEvidence.geometryOverlay.'
    },
    'worlds': rows
}
(FOLDER / 'per-world-map-source-geometry-v4-20261022.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
print(FOLDER / 'per-world-map-source-geometry-v4-20261022.json')
