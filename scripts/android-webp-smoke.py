"""Preview-only Android UI inspection/taps. Never targets the production package."""
from pathlib import Path
import argparse
import json
import re
import subprocess
import time
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ADB = Path.home() / 'AppData/Local/Android/Sdk/platform-tools/adb.exe'
PACKAGE = 'com.agesofdominion.game.reborn.preview'
parser = argparse.ArgumentParser()
parser.add_argument('--serial', required=True)
parser.add_argument('--name', required=True)
parser.add_argument('--tap-label')
parser.add_argument('--screenshot', action='store_true', help='Retain only selected visual evidence, not duplicate captures at every tap')
args = parser.parse_args()
assert re.fullmatch(r'[a-zA-Z0-9_-]+', args.name)
OUT = ROOT / 'qa/lossless-webp-20261024/android'
OUT.mkdir(parents=True, exist_ok=True)

def adb(*command):
    return subprocess.check_output([str(ADB), '-s', args.serial, *command])

def assert_preview_focus():
    for attempt in range(20):
        focus = adb('shell', 'dumpsys', 'window').decode(errors='replace')
        current = next((line.strip() for line in focus.splitlines() if 'mCurrentFocus=' in line), '')
        if 'mCurrentFocus=null' not in current:
            break
        time.sleep(0.1)  # Window transition only; never repeat a touchscreen tap.
    if PACKAGE + '/' not in current:
        raise RuntimeError('Preview is not foreground; refuse to inspect or tap another application: ' + current)

def inspect():
    assert_preview_focus()
    adb('shell', 'uiautomator', 'dump', '--compressed', '/sdcard/aod-webp-ui.xml')
    raw = adb('shell', 'cat', '/sdcard/aod-webp-ui.xml')
    adb('shell', 'rm', '-f', '/sdcard/aod-webp-ui.xml')
    tree = ET.fromstring(raw)
    assert_preview_focus()
    nodes = [dict(node.attrib) for node in tree.iter('node') if node.get('text') or node.get('content-desc')]
    return raw, nodes

raw, nodes = inspect()
if args.tap_label:
    matches = [node for node in nodes if args.tap_label in {node.get('text'),node.get('content-desc')} and node.get('enabled') == 'true']
    if len(matches) != 1:
        raise RuntimeError('Need one exact fresh UI label; matches=' + json.dumps(matches))
    x1,y1,x2,y2 = map(int,re.findall(r'\d+',matches[0]['bounds']))
    if x2 <= x1 or y2 <= y1:
        raise RuntimeError('Requested control is offscreen; refuse a zero-bounds tap')
    assert_preview_focus()
    adb('shell','input','touchscreen','tap',str((x1+x2)//2),str((y1+y2)//2))
    raw,nodes=inspect()
(OUT/(args.name+'.xml')).write_bytes(raw)
if args.screenshot:
    (OUT/(args.name+'.png')).write_bytes(adb('exec-out','screencap','-p'))
summary=[{key:node[key] for key in ['text','content-desc','class','bounds','clickable','enabled'] if key in node} for node in nodes]
(OUT/(args.name+'.json')).write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
