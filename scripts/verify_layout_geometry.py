import json

cam = (60.0, -10.0, 25.0, 35.0, 170.0, 165.0)


def project(x, y):
  a, b, c, d, e, f = cam
  return (a * x + c * y + e, b * x + d * y + f)


def overlap_rect(r1, r2):
  return not (
      r1[0] + r1[2] <= r2[0]
      or r2[0] + r2[2] <= r1[0]
      or r1[1] + r1[3] <= r2[1]
      or r2[1] + r2[3] <= r1[1]
  )


# Adjusted sites:
# P05..P08 at x=8.3, width=1.3
# P09..P11 at x=9.8, width=1.3 -> right edge = 11.1
# At [11.1, 7.5]: source X = 60*11.1 + 25*7.5 + 170 = 1023.5 < 1040.16 (panel clearance PASS)
sites = [
    {"id": "townhall", "rect": [2.914, 3.809, 4.636, 2.413]},
    {"id": "P01", "rect": [0.3, 2.3, 1.4, 1.2], "region": "upper"},
    {"id": "P02", "rect": [0.3, 3.7, 1.4, 1.2], "region": "upper"},
    {"id": "P03", "rect": [0.3, 6.45, 1.4, 1.2], "region": "upper"},
    {"id": "P04", "rect": [0.3, 8.55, 1.4, 1.2], "region": "lower"},
    {"id": "P05", "rect": [8.3, 2.45, 1.3, 1.2], "region": "upper"},
    {"id": "P06", "rect": [8.3, 4.3, 1.3, 1.2], "region": "upper"},
    {"id": "P07", "rect": [8.3, 6.15, 1.3, 1.2], "region": "upper"},
    {"id": "P08", "rect": [8.3, 8.55, 1.3, 1.2], "region": "lower"},
    {"id": "P09", "rect": [9.8, 2.45, 1.3, 1.2], "region": "upper"},
    {"id": "P10", "rect": [9.8, 4.4, 1.3, 1.2], "region": "upper"},
    {"id": "P11", "rect": [9.8, 6.3, 1.3, 1.2], "region": "upper"},
    {"id": "P12", "rect": [8.35, 9.8, 1.4, 1.2], "region": "lower"},
    {"id": "P13", "rect": [2.05, 8.55, 1.4, 1.2], "region": "lower"},
    {"id": "P14", "rect": [3.65, 8.55, 1.4, 1.2], "region": "lower"},
    {"id": "P15", "rect": [6.75, 8.55, 1.4, 1.2], "region": "lower"},
    {"id": "P16", "rect": [2.05, 9.8, 1.4, 1.2], "region": "lower"},
    {"id": "P17", "rect": [6.2, 9.8, 1.4, 1.2], "region": "lower"},
]

overlaps = []
for i in range(len(sites)):
  for j in range(i + 1, len(sites)):
    if overlap_rect(sites[i]["rect"], sites[j]["rect"]):
      overlaps.append((sites[i]["id"], sites[j]["id"]))

print("Overlaps count:", len(overlaps), overlaps)

panel_max_x = 1040.16
exceed_panel = []
for s in sites:
  x, y, w, h = s["rect"]
  corners = [
      project(x, y),
      project(x + w, y),
      project(x + w, y + h),
      project(x, y + h),
  ]
  max_sx = max(p[0] for p in corners)
  min_sx = min(p[0] for p in corners)
  max_sy = max(p[1] for p in corners)
  min_sy = min(p[1] for p in corners)
  if max_sx > panel_max_x:
    exceed_panel.append((s["id"], max_sx))

print("Exceed panel count:", len(exceed_panel), exceed_panel)

# Check river cells (col 13)
river_overlaps = []
for s in sites:
  x, y, w, h = s["rect"]
  if x + w > 13.0:
    river_overlaps.append((s["id"], x + w))
print("River overlaps count:", len(river_overlaps), river_overlaps)
