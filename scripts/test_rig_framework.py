import os, json, hashlib
from PIL import Image
import numpy as np
from scipy import ndimage

ROOT = 'C:/dev/ages-of-dominion-reborn'
RIG_DIR = f'{ROOT}/assets/derivatives/rigs'
QA_DIR = f'{ROOT}/qa/offline-controls-repair-20261004/rigs_qa'
os.makedirs(RIG_DIR, exist_ok=True)
os.makedirs(QA_DIR, exist_ok=True)

def compute_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def despill_magenta_rgba(arr):
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    mag_dist = np.sqrt((r - 255.0)**2 + g**2 + (b - 255.0)**2)
    alpha = np.clip((mag_dist - 65.0) / 75.0, 0.0, 1.0)
    
    # Despill
    spill = np.maximum(0.0, np.minimum(r - g, b - g))
    clean_r = np.clip(r - spill * 0.95, 0, 255)
    clean_b = np.clip(b - spill * 0.95, 0, 255)
    clean_g = np.clip(g, 0, 255)
    
    rgba = np.dstack([
        clean_r.astype(np.uint8),
        clean_g.astype(np.uint8),
        clean_b.astype(np.uint8),
        (alpha * 255.0).astype(np.uint8)
    ])
    return rgba

# Topology templates for structured rig sheets:
# 6 major panels:
# Top row: Torso/Head assembly, Armor plate / Cloak, Side profile
# Mid row: Arms / Legs / Weapons
ANATOMY_ROLES = {
    'head_and_helm': 'Head / Helmet with neck pivot',
    'torso_chest': 'Main Torso and chest plate',
    'arm_upper_left': 'Upper Left Arm with shoulder and elbow joints',
    'arm_lower_left': 'Lower Left Arm with elbow and wrist joints',
    'arm_upper_right': 'Upper Right Arm with shoulder and elbow joints',
    'arm_lower_right': 'Lower Right Arm with elbow and wrist joints',
    'leg_upper_left': 'Upper Left Thigh with hip and knee joints',
    'leg_lower_left': 'Lower Left Shin/Foot with knee and ankle contact',
    'leg_upper_right': 'Upper Right Thigh with hip and knee joints',
    'leg_lower_right': 'Lower Right Shin/Foot with knee and ankle contact',
    'weapon_primary': 'Primary Class Weapon',
    'shield_or_secondary': 'Secondary Weapon / Shield'
}

print("Rig anatomy extraction framework initialized.")
