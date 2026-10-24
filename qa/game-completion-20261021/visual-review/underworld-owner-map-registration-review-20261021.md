# Underworld owner-map correction and natural Shrine route — 21 October 2026

**Classification: bounded source-grid correction, Town start, Shrine visit, and reload source/position check PASS; natural crossing, full Adventure, and the whole game remain INCOMPLETE.** Four of twelve campaign worlds currently bind their matching owner-selected paintings in live play: Grasslands, Feywild, Jade Karst, and Crystal Underworld.

## Source registration and corrected sites

src/data/adventure-worlds.json selects this same owner image for Underworld file and runtimeFile:

assets/mocks/owner-approved-vast-adventure-maps-20261020/05_Vast_Map_Subterranean_Underworld_Cavern.png

The current flat source transform is [86, 0, 0, 76.8, 0, 0]. A source-grid review found that the former Underworld site rectangles did not consistently cover their painted landmarks. The geometry was corrected to:

- Town [13,2,3,4], approach [12,5]: eastern stone city.
- Ruin [4,6,2,1], approach [4,7]: western purple obelisk.
- Mill [3,5,2,1], approach [5,5]: waterwheel.
- Mine [0,3,2,2], approach [2,4]: western mining works.
- Dwelling [10,1,3,2], approach [10,3]: floating citadel.
- Shrine [10,7,1,1], approach [9,7]: blue runic altar.

The hero start is [12.5,5.5] at the Town approach. The regenerated source grid and inspected 1280×720 live view support the Town and Shrine alignment. The existing river blockers remain [6,4], [6,5], [6,6], and [6,8]; the serpent obstacle remains [7,6]; bridge deck cells remain [6,7] and [7,7]. The grid is diagnostic evidence, not full map or hazard acceptance. See the [owner-map grid report](owner-map-source-grid-audit-20261021/report.json) and [Underworld coordinate grid](owner-map-source-grid-audit-20261021/underworld-owner-source-16x10-grid.png).

## Fresh visible-control Shrine journey after the correction

On isolated http://127.0.0.1:4201/, a fresh campaign selected Crystal Underworld, entered Adventure, and left Town using the visible controls. Five legal one-cell moves reached the Shrine approach [9,7]. The Shrine interaction offered Wisdom and the player selected Wisdom 1/3. The hero was visibly adjacent to the blue altar.

Saving returned “Saved locally.” After reload and Continue, the world still selected the Underworld owner painting, the Shrine approach remained selected, and the hero marker returned to the saved position with zero moves left. The post-reload skill ledger was not independently reopened, so persistence of the Wisdom lesson is not claimed here. Browser error and warning logs were empty.

The earlier note about a Town-to-Shrine bridge journey and Tactics 1/3 used the superseded site geometry. It is historical and is not current natural-crossing evidence. The post-correction natural bridge route, other Underworld sites/rewards, and complete hazard classification remain OPEN.

## Viewport and verification

The earlier 826×375 view showed the Adventure map field fitting with a 280px details panel that scrolls internally. That is layout-only evidence and does not close post-correction map fidelity. Unexplored fog still substantially darkens the painting.

- Focused Adventure-world suite after the geometry and assertion edits: 18/18 passed.
- Full bounded Node suite: not rerun after those edits. The previously recorded 249/249 result belongs to the earlier source snapshot.
- Main/navigation syntax checks and the current browser error/warning query: passed/empty.
- The source-grid diagnostic counts 4/12 owner paintings bound at runtime.

Remaining work includes natural bridge verification against the corrected sites, classification of all painted hazards, the other eight owner-map bindings, all-world visual fidelity, complete natural journeys, independent desktop review, final APK parity, device QA, and owner acceptance. Whole-game status remains INCOMPLETE.

