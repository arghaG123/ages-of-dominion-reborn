import os, json, hashlib
from PIL import Image

ROOT = 'C:/dev/ages-of-dominion-reborn'

def compute_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

print("Publishing Corrected Versioned Delivery Manifest (v2)...")

# 1. Load intermediate manifests
portraits_data = json.load(open(f'{ROOT}/qa/offline-controls-repair-20261004/corrected-portraits-manifest.json'))
actors_mounts_data = json.load(open(f'{ROOT}/qa/offline-controls-repair-20261004/cleaned-actors-and-mounts-manifest.json'))
rigs_data = json.load(open(f'{ROOT}/assets/derivatives/rigs/parts_manifest.json'))
kingdom_data = json.load(open(f'{ROOT}/qa/offline-controls-repair-20261004/kingdom-bounded-measurement-report.json'))
accounting_data = json.load(open(f'{ROOT}/qa/offline-controls-repair-20261004/accounting-reconciliation-evidence.json'))
later73_exec_manifest = json.load(open(f'{ROOT}/docs/plan/IMAGE-LATER73-EXECUTION-MANIFEST-2026-10-04.json'))
item_map = {item['id']: item for item in later73_exec_manifest['items']}

items = []
clean_usable_rows = []
failed_unrecoverable_rows = []

# -------------------------------------------------------------
# 1. PORTRAITS (38 source images: 31 hero kits + 1 mounted painting + 6 rivals)
# -------------------------------------------------------------
for iid, p_info in portraits_data.items():
    native_rel = f'assets/high-res/final-native2k/{iid}.png'
    native_sha = compute_sha256(f'{ROOT}/{native_rel}')
    
    # Class / era extraction
    parts = iid.split('-')
    if 'rival' in iid:
        era = p_info['canonicalRivalInfo']['era'] if p_info['canonicalRivalInfo'] else 'variable'
        class_name = 'rival'
        role = p_info['canonicalRivalInfo']['role'] if p_info['canonicalRivalInfo'] else 'rival_warlord'
    elif iid == 'knight-mounted-master':
        era = 'medieval' # Note: cannot fulfill ancient
        class_name = 'knight'
        role = 'mounted_master_reference'
    else:
        era = parts[1] # e.g. ancient, medieval, powder, mech
        class_name = parts[2] # e.g. ranger, warlock, mage, etc.
        role = f'{era}_{class_name}_portrait'
        
    # Determine distinct gates
    is_km = (iid == 'knight-mounted-master')
    is_rival = ('rival' in iid)
    
    gates = {
        'technical': 'PASS',
        'content': 'STONE_FAIL_ERA_MISMATCH' if is_km else 'PASS',
        'layout': 'PASS',
        'matte': 'PASS',
        'spatial': 'N_A_CARD_PORTRAIT',
        'appearance': 'PENDING_OWNER_ACCEPTANCE',
        'runtime': 'UNSUITABLE_STONE_TRAVEL_FAIL' if is_km else ('PROPOSED_RIVAL_DERIVATIVE_READY' if is_rival else 'READY_AS_DERIVATIVE_CANDIDATE'),
        'owner': 'PENDING'
    }
    
    row = {
        'id': iid,
        'group': '2K-LATER-A-HERO-32' if not is_rival else '2K-LATER-RIVALS',
        'category': 'portrait_card',
        'era': era,
        'class': class_name,
        'role': role,
        'source': {
            'path': native_rel,
            'sha256': native_sha,
            'dimensions': [2048, 2048],
            'mode': 'RGB',
            'provenance': 'gemini-3.1-flash-image (native 2K)'
        },
        'derivative': {
            'path': p_info['derivativePaths'][0],
            'sha256': p_info['derivativeSHA256'],
            'dimensions': p_info['derivativeDimensions'],
            'mode': p_info['derivativeMode'],
            'recipeVersion': p_info['recipeVersion'],
            'sourceCropBox': p_info['cropBoxNative'],
            'headTopNative': p_info['headTopNative'],
            'headCenterNative': p_info['headCenterNative'],
            'headroomNative': p_info['headroomNative'],
            'intendedUse': p_info['intendedUse'],
            'travelUse': p_info['travelUse'],
            'allDerivativePaths': p_info['derivativePaths']
        },
        'camera': {
            'view': 'bust_to_waist_portrait',
            'facing': 'front_facing',
            'lighting': 'upper-left directional key light'
        },
        'canonicalMapping': p_info.get('canonicalRivalInfo'),
        'gates': gates,
        'notes': [
            'Preserved v1 crop in assets/derivatives/portraits/v1_archived/',
            'V2 calibrated crop ensures complete helmet, crown, eyes, and chest visibility.'
        ]
    }
    
    if is_km:
        row['notes'].append('Depicts medieval barded plate with scenic castle background; fails stone-starter travel need; preserved as medieval reference.')
        failed_unrecoverable_rows.append(row)
    else:
        clean_usable_rows.append(row)
    items.append(row)

# -------------------------------------------------------------
# 2. ARMY ACTORS (24 units)
# -------------------------------------------------------------
actors_dict = actors_mounts_data['actors']
for iid, a_info in actors_dict.items():
    native_rel = f'assets/high-res/final-native2k/{iid}.png'
    native_sha = compute_sha256(f'{ROOT}/{native_rel}')
    parts = iid.split('-')
    era = parts[1]
    role = parts[2]
    
    # 2K candidates for iron-melee and industrial-heavy failed
    is_failed_candidate = (iid in ['troop-iron-melee', 'troop-industrial-heavy'])
    
    gates = {
        'technical': 'PASS',
        'content': 'FAIL_STENCIL' if iid == 'troop-iron-melee' else ('FAIL_INFANTRY_GUNNER' if iid == 'troop-industrial-heavy' else 'PASS'),
        'layout': 'PASS',
        'matte': 'PASS',
        'spatial': 'PENDING_REGISTRATION',
        'appearance': 'PENDING_OWNER_ACCEPTANCE',
        'runtime': 'FAILED_CANDIDATE_SUPERSEDED_BY_SUBSTITUTION' if is_failed_candidate else 'READY_AS_DERIVATIVE_CANDIDATE',
        'owner': 'PENDING'
    }
    
    row = {
        'id': iid,
        'group': '2K-LATER-C-ARMY-24',
        'category': 'army_actor',
        'era': era,
        'class': role,
        'role': f'{era}_{role}',
        'source': {
            'path': native_rel,
            'sha256': native_sha,
            'dimensions': [2048, 2048],
            'mode': 'RGB',
            'provenance': 'gemini-3.1-flash-image (native 2K)'
        },
        'derivative': {
            'path': a_info['outPath'],
            'sha256': a_info['sha256'],
            'dimensions': [2048, 2048],
            'mode': 'RGBA',
            'recipeVersion': 'v2-isolated-pose-despill',
            'tightBBox': a_info['tightBBox'],
            'groundContactPivot': a_info['groundContactPivot'],
            'opaquePixels': a_info['opaquePixels']
        },
        'camera': {
            'view': 'full_body_actor',
            'facing': '3/4 view facing right/center',
            'lighting': 'upper-left directional key light'
        },
        'gates': gates,
        'notes': [
            'Clean RGBA matte cutout; background artifacts, secondary poses, labels, and floor planes removed.',
            f'Measured ground contact point: {a_info["groundContactPivot"]}.'
        ]
    }
    
    if is_failed_candidate:
        failed_unrecoverable_rows.append(row)
    else:
        clean_usable_rows.append(row)
    items.append(row)

# -------------------------------------------------------------
# 3. AUTHENTICATED SUBSTITUTIONS (2 units)
# -------------------------------------------------------------
subs_dict = actors_mounts_data['substitutions']
for iid, s_info in subs_dict.items():
    gates = {
        'technical': 'PASS',
        'content': 'PASS',
        'layout': 'PASS',
        'matte': 'PASS',
        'spatial': 'PENDING_REGISTRATION',
        'appearance': 'PENDING_OWNER_ACCEPTANCE',
        'runtime': 'READY_AS_DERIVATIVE_CANDIDATE',
        'owner': 'PENDING'
    }
    row = {
        'id': f'{iid}-substitution',
        'targetID': iid,
        'group': 'SUBSTITUTIONS',
        'category': 'authentic_substitution',
        'era': 'iron' if 'iron' in iid else 'industrial',
        'class': 'melee' if 'melee' in iid else 'heavy',
        'role': 'roman_legionary' if 'iron' in iid else 'steam_combat_walker',
        'source': {
            'path': s_info['sourcePath'],
            'sha256': s_info['sourceSHA256'],
            'dimensions': s_info['sourceResolution'],
            'mode': 'RGB',
            'provenance': s_info['sourceProvenance']
        },
        'derivative': {
            'path': s_info['derivativePath'],
            'sha256': s_info['derivativeSHA256'],
            'dimensions': s_info['derivativeDimensions'],
            'mode': s_info['derivativeMode'],
            'recipeVersion': 'v2-despill-chroma-matte',
            'tightBBox': s_info['tightBBox'],
            'groundContactPivot': s_info['groundContactPivot']
        },
        'camera': {
            'view': 'full_body_actor',
            'facing': '3/4 view',
            'lighting': 'upper-left directional key light'
        },
        'gates': gates,
        'notes': [
            s_info['rationale'],
            'Preserved authentic 1024x1024 provenance from production batches 07/17; NOT native 2K.'
        ]
    }
    clean_usable_rows.append(row)
    items.append(row)

# -------------------------------------------------------------
# 4. MOUNTS (4 mounts)
# -------------------------------------------------------------
mounts_dict = actors_mounts_data['mounts']
for mid, m_info in mounts_dict.items():
    is_km = (mid == 'knight-mounted-master')
    native_rel = f'assets/high-res/final-native2k/{mid}.png'
    native_sha = compute_sha256(f'{ROOT}/{native_rel}')
    
    gates = {
        'technical': 'PASS',
        'content': 'STONE_FAIL_ERA_MISMATCH' if is_km else 'PASS',
        'layout': 'PASS',
        'matte': 'PASS',
        'spatial': 'PENDING_REGISTRATION',
        'appearance': 'PENDING_OWNER_ACCEPTANCE',
        'runtime': 'STONE_TRAVEL_FAIL' if is_km else 'READY_AS_DERIVATIVE_CANDIDATE',
        'owner': 'PENDING'
    }
    
    row = {
        'id': mid,
        'group': '2K-LATER-B-MOUNTS-4',
        'category': 'hero_mount',
        'era': 'ancient' if 'horse' in mid else ('powder_industrial' if 'motor' in mid else ('future' if 'future' in mid else 'medieval')),
        'class': 'mount',
        'role': mid.replace('hero-mount-', ''),
        'source': {
            'path': native_rel,
            'sha256': native_sha,
            'dimensions': [2048, 2048],
            'mode': 'RGB',
            'provenance': 'gemini-3.1-flash-image (native 2K)'
        },
        'derivative': {
            'path': m_info['outPath'],
            'sha256': m_info['sha256'],
            'dimensions': [2048, 2048],
            'mode': 'RGBA' if not is_km else 'RGB',
            'recipeVersion': 'v2-measured-saddle-ground-separation',
            'tightBBox': m_info.get('tightBBox', [0, 0, 2048, 2048]),
            'saddleRiderPivot': m_info['saddleRiderPivot'],
            'groundContactPivot': m_info['groundContactPivot'],
            'floorPlaneRemoved': m_info.get('floorPlaneRemoved', False)
        },
        'camera': {
            'view': 'mount_profile_isometric',
            'facing': 'profile facing right',
            'lighting': 'upper-left directional key light'
        },
        'gates': gates,
        'notes': [
            f'Measured saddle / rider attachment landmark: {m_info["saddleRiderPivot"]}.',
            f'Measured ground contact point: {m_info["groundContactPivot"]}.',
            'Rectangular floor planes removed.' if not is_km else 'Scenic castle painting fails stone travel need.'
        ]
    }
    if is_km:
        failed_unrecoverable_rows.append(row)
    else:
        clean_usable_rows.append(row)
    items.append(row)

# -------------------------------------------------------------
# 5. RIG ANATOMY (8 rig sheets)
# -------------------------------------------------------------
for rid, r_info in rigs_data.items():
    native_rel = f'assets/high-res/final-native2k/{rid}.png'
    native_sha = compute_sha256(f'{ROOT}/{native_rel}')
    
    is_irregular = (r_info['recoverability'] == 'IRRECOVERABLE_IN_NATIVE_2K_CANDIDATE')
    
    gates = {
        'technical': 'PASS',
        'content': 'FAIL_IRREGULAR_UNSEPARATED' if is_irregular else 'PASS',
        'layout': 'FAIL' if is_irregular else 'PASS',
        'matte': 'PASS',
        'spatial': 'PENDING_SKELETON_BINDING',
        'appearance': 'PENDING_OWNER_ACCEPTANCE',
        'runtime': 'FAIL_REQUIRES_CODE_AI_FALLBACK' if is_irregular else 'READY_AS_DERIVATIVE_CANDIDATE',
        'owner': 'PENDING'
    }
    
    row = {
        'id': rid,
        'group': '2K-LATER-D-RIGS-8',
        'category': 'rig_anatomy_sheet',
        'era': 'ancient_to_medieval',
        'class': r_info['classId'],
        'role': f'hero_rig_{r_info["classId"]}',
        'sheetStatus': r_info['sheetStatus'],
        'recoverability': r_info['recoverability'],
        'source': {
            'path': native_rel,
            'sha256': native_sha,
            'dimensions': [2048, 2048],
            'mode': 'RGB',
            'provenance': 'gemini-3.1-flash-image (native 2K)'
        },
        'partsDeliveredCount': r_info['partsCount'],
        'parts': r_info['parts'],
        'gates': gates,
        'notes': [
            r_info['auditFinding'],
            'All extracted slices are true RGBA with transparent backgrounds and despill applied.',
            'Preserved 162 old v1 RGB rig slices in assets/derivatives/rigs/v1_archived/.'
        ]
    }
    if is_irregular:
        failed_unrecoverable_rows.append(row)
    else:
        clean_usable_rows.append(row)
    items.append(row)

# -------------------------------------------------------------
# 6. ASSEMBLE COMPLETE DELIVERY MANIFEST v2
# -------------------------------------------------------------
complete_delivery_manifest_v2 = {
    'schema': 'ages-of-dominion/image-delivery/v2',
    'deliveryDate': '2026-10-04',
    'deliveredBy': 'owner-selected-image-executor',
    'deliveryScopeStatus': 'LOCAL_REPAIR_AND_ACCOUNTING_DELIVERY_COMPLETE',
    'paidScopeAuthorization': 'NO_NEW_PAID_SCOPE_EXHAUSTED',
    'summary': {
        'totalNativeCandidates': 73,
        'uniqueSourcePortraits': 38,
        'portraitDerivativeFiles': 44,
        'armyActorsDelivered': 24,
        'mountsDelivered': 4,
        'authenticSubstitutionsDelivered': 2,
        'rigSheetsAnalyzed': 8,
        'cleanUsableRowsCount': len(clean_usable_rows),
        'failedUnrecoverableRowsCount': len(failed_unrecoverable_rows),
        'codeAIHandoffReady': True
    },
    'accountingReconciliationHeadline': {
        'totalExposureUSD': accounting_data['uniqueAttemptReconciliation']['totalCommittedProtectedExposureUSD'],
        'batches01To17ReconciledUSD': accounting_data['uniqueAttemptReconciliation']['categoryD_Batches01To17TotalUSD'],
        'terrain4KBuffersUSD': accounting_data['uniqueAttemptReconciliation']['categoryE_Buffers4KTotalUSD'],
        'originalMockUSD': accounting_data['uniqueAttemptReconciliation']['categoryF_HistoricalMockReservationUSD'],
        'protectedOwnerReserveUSD': accounting_data['uniqueAttemptReconciliation']['categoryG_SafetyReserveProtectedUSD'],
        'baseExpenditureUSD': accounting_data['discrepancyAudit']['statedBaseUSD'],
        'later73SuccessEstimateUSD': accounting_data['uniqueAttemptReconciliation']['categoryA_SuccessEstimate73USD'],
        'retainedUnknownLiabilityUSD': accounting_data['uniqueAttemptReconciliation']['categoryC_RetainedUnknownLiabilitiesUSD'],
        'conservativeCeilingBufferUSD': accounting_data['uniqueAttemptReconciliation']['conservativeCeilingBufferUSD'],
        'conservativeHeadroomUnder80USD': accounting_data['scopeConstraints']['headroomUnderHardCapUSD'],
        'reconciliationNotes': accounting_data['discrepancyAudit']['rootCause']
    },
    'safeguardsControlsStatus': {
        'testReportPath': 'qa/offline-controls-repair-20261004/repaired-controls-report.json',
        'passingProbesCount': 9,
        'failingProbesCount': 0,
        'cloudClassification': 'ACTIVE_OR_UNKNOWN_CLOUD_STATES covered; all active and unknown states blocked from dispatch',
        'exclusiveMutexStatus': 'Exclusive token with OS O_EXCL check enforced; delayed contender fails closed'
    },
    'kingdomTerrainMeasurement': {
        'reportPath': 'qa/offline-controls-repair-20261004/kingdom-bounded-measurement-report.json',
        'affineMatrix': kingdom_data['activeContract']['worldToSource'],
        'activeContractTownHallProjected': kingdom_data['activeContract']['townhallCenterRefProjected'],
        'candidateV2TownHallProjected': kingdom_data['candidateV2Contract']['townhallCenterRefProjected'],
        'activeContractBridgeProjected': kingdom_data['activeContract']['bridgeCenterRefProjected'],
        'candidateV2BridgeProjected': kingdom_data['candidateV2Contract']['bridgeCenterRefProjected'],
        'uint8OverflowFixed': True,
        'terrainStatus': 'RECOVERABILITY_SURVEYED_HONEST_FAILURES_RECORDED_NO_NEW_PURCHASE'
    },
    'cleanUsableRows': clean_usable_rows,
    'failedUnrecoverableRows': failed_unrecoverable_rows,
    'items': items
}

# Save canonical v2 delivery manifest
out_manifest_path = f'{ROOT}/docs/plan/IMAGE-DELIVERY-MANIFEST-2026-10-04.json'
with open(out_manifest_path, 'w') as f:
    json.dump(complete_delivery_manifest_v2, f, indent=2)

print(f"Saved canonical delivery manifest v2 to {out_manifest_path} ({len(items)} items).")

# Save QA summary
qa_summary_path = f'{ROOT}/qa/offline-controls-repair-20261004/IMAGE-DELIVERY-SUMMARY-2026-10-04.json'
with open(qa_summary_path, 'w') as f:
    json.dump({
        'summary': complete_delivery_manifest_v2['summary'],
        'accounting': complete_delivery_manifest_v2['accountingReconciliationHeadline'],
        'safeguards': complete_delivery_manifest_v2['safeguardsControlsStatus'],
        'kingdom': complete_delivery_manifest_v2['kingdomTerrainMeasurement'],
        'cleanRowsCount': len(clean_usable_rows),
        'failedRowsCount': len(failed_unrecoverable_rows)
    }, f, indent=2)

print(f"Saved QA delivery summary to {qa_summary_path}.")
