import os, json, hashlib
from PIL import Image
import numpy as np
from scipy import ndimage

# Verify bounding boxes and coordinates for all 8 characters
p_knight = 'assets/high-res/final-native2k/rig-source-parts-knight.png'
p_ranger = 'assets/high-res/final-native2k/rig-source-parts-ranger.png'
p_warlock = 'assets/high-res/final-native2k/rig-source-parts-warlock.png'
p_mage = 'assets/high-res/final-native2k/rig-source-parts-mage.png'
p_necromancer = 'assets/high-res/final-native2k/rig-source-parts-necromancer.png'
p_barbarian = 'assets/high-res/final-native2k/rig-source-parts-barbarian.png'
p_paladin = 'assets/high-res/final-native2k/rig-source-parts-paladin.png'
p_healer = 'assets/high-res/final-native2k/rig-source-parts-healer.png'

print("All 8 native paths exist:", all(os.path.exists(p) for p in [
    p_knight, p_ranger, p_warlock, p_mage, p_necromancer, p_barbarian, p_paladin, p_healer
]))
