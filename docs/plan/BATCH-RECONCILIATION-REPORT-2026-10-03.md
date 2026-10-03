# Batch Reconciliation and Next Batch Preparation Report — 3 October 2026

## 1. Executive Summary

As the image-batch executor in `C:\dev\ages-of-dominion-reborn`, live job records, local collections, durable locks, budget ledgers, and inventory gaps have been completely reconciled in project `project-eaa4c1cc-8f19-4d24-9e6` using authorized account `arghawork3@gmail.com`.

- **Live Provider Jobs**: 48 discoverable Vertex locations scanned. Exactly 11 jobs discovered across the project, all in `global`. **All 11 jobs are terminal** (10 `JOB_STATE_SUCCEEDED`, 1 `JOB_STATE_FAILED`). **Zero active, pending, or unknown jobs exist.**
- **Local Collections**: Batches 01–08 contain **240 verified original images**; all 240 source/prompt/payload associations PASS. Zero duplicates. Zero missing. Batch 08 is completely collected locally; no resubmission or recollecting of batches 01–08 will occur.
- **Durable Locks**: Both local (`docs/plan/image-production/active-batch.lock.json`) and cloud (`gs://project-eaa4c1cc-8f19-4d24-9e6-aod-batch/design-mocks/active-batch.lock.json`) bind to terminal job `6249288878671265792` (`production-08-20261003`).
- **Budget Reconciliation**: Holds protect **$65 USD** ($48 for 8 batches @ $6 + $2 historical mock + $15 safety reserve). Actual invoices remain unknown (`billedTotal: null`); holds are retained without resetting. Remaining headroom under the $80 hard cap is **$15 USD**.
- **Corrected Batch 07 Draft**: Executed manifests are preserved. Created `docs/plan/image-production/batch-07-manifest-corrected-draft.json` correcting the 6 heavy prompts to the frozen roster (Charioteer, War Elephant, Siege Knight, Cannon Crew, Steam Walker, Battle Tank, Hover Tank) and removing contradictory boilerplate.
- **Draft Batch 09 Prepared**: Created `docs/plan/image-production/batch-09-manifest-draft.json` containing **exactly 30 useful requests** addressing demonstrated baseline inventory gaps (30 unrequested siege attackers: 3 Stone, 5 Bronze, 5 Iron, 5 Medieval, 5 Gunpowder, 5 Industrial, 2 Modern). All 30 spatial guides generated deterministically.
- **Affordability Verified**: $65 committed + $6 proposed = $71 USD <= $80 USD hard cap ($9 USD remaining headroom).
- **Current Submission Status**: **DEFERRED PENDING OWNER AUTHORIZATION**. In accordance with strict instructions, no batch 09+ submission has been made. Submission is blocked solely on explicit owner authorization.

---

## 2. Reconciled Provider Jobs Across All Locations

A full pagination scan of Vertex AI across 48 discoverable regions for project `project-eaa4c1cc-8f19-4d24-9e6` was executed:

| Job Name | Display Name | State | Outputs |
|---|---|---|---|
| `projects/186933974004/locations/global/batchPredictionJobs/6249288878671265792` | `production-08-20261003` | `JOB_STATE_SUCCEEDED` | 30/30 |
| `projects/186933974004/locations/global/batchPredictionJobs/1624373536338477056` | `production-07-20261003` | `JOB_STATE_SUCCEEDED` | 30/30 |
| `projects/186933974004/locations/global/batchPredictionJobs/6618865523092357120` | `production-06-20261003` | `JOB_STATE_SUCCEEDED` | 30/30 |
| `projects/186933974004/locations/global/batchPredictionJobs/3746131910783401984` | `production-05-20261003` | `JOB_STATE_SUCCEEDED` | 30/30 |
| `projects/186933974004/locations/global/batchPredictionJobs/6905547786872160256` | `production-04-20261003` | `JOB_STATE_SUCCEEDED` | 30/30 |
| `projects/186933974004/locations/global/batchPredictionJobs/3389643852779356160` | `production-03-20261003` | `JOB_STATE_SUCCEEDED` | 30/30 |
| `projects/186933974004/locations/global/batchPredictionJobs/2260718089937092608` | `production-02-20261003` | `JOB_STATE_SUCCEEDED` | 30/30 |
| `projects/186933974004/locations/global/batchPredictionJobs/7379059066443661312` | `production-01-20261003` | `JOB_STATE_SUCCEEDED` | 30/30 |
| `projects/186933974004/locations/global/batchPredictionJobs/410583068017950720` | `landscape-mocks-20261003-efcd7a7e` | `JOB_STATE_SUCCEEDED` | 30/30 |
| `projects/186933974004/locations/global/batchPredictionJobs/6248299318206267392` | `aod-batch-job_1790607031713_w8pd5` | `JOB_STATE_FAILED` | 0 |
| `projects/186933974004/locations/global/batchPredictionJobs/2392655087223701504` | `aod-batch-job_1790603410818_zk2kj` | `JOB_STATE_SUCCEEDED` | - |

**Outcome**: There are zero active, queued, or unknown jobs. The single-active-batch rule is completely clear to proceed upon authorization.

---

## 3. Local Collections and Locks

All 8 production batches are locally stored in `assets/production/`:
- `production-01-20261003`: 30 outputs (Terrain, Buildings, Sites, Resources, Hero Master)
- `production-02-20261003`: 30 outputs (Skills, Spells, Gear, Hero Portraits)
- `production-03-20261003`: 30 outputs (Terrains, Buildings, Skills, Gear)
- `production-04-20261003`: 30 outputs (Carried Buildings & Era Buildings)
- `production-05-20261003`: 30 outputs (Era Buildings)
- `production-06-20261003`: 30 outputs (Town Sheets, Buildings, Troops)
- `production-07-20261003`: 30 outputs (Town Sheets, Troops, Stone Towers)
- `production-08-20261003`: 30 outputs (Towers, Stone Brute/Runner Attackers)

Total collected: **240 PNG originals**. All raw response JSONL files and provenance are preserved.

### Lock Status
- Local Lock: `docs/plan/image-production/active-batch.lock.json`
- Cloud Lock: `gs://project-eaa4c1cc-8f19-4d24-9e6-aod-batch/design-mocks/active-batch.lock.json`
- Bound Job: `projects/186933974004/locations/global/batchPredictionJobs/6249288878671265792` (`production-08-20261003`).
- Verified State: Terminal `JOB_STATE_SUCCEEDED`.

---

## 4. Budget Reconciliation and Affordability

| Item | Amount | Status |
|---|---:|---|
| Batches 01–08 Reservations (8 × $6.00) | $48.00 USD | Protected holds retained |
| Historical Mock Conservative Reservation | $2.00 USD | Protected hold retained |
| Global Safety Reserve | $15.00 USD | Protected minimum |
| **Total Currently Protected** | **$65.00 USD** | Exceeds $60 target by $5; invoices unknown |
| Hard Cap | $80.00 USD | Enforced hard limit |
| **Remaining Hard Cap Headroom** | **$15.00 USD** | Available before reaching $80 |
| Proposed Batch 09 Reservation | $6.00 USD | Draft prepared |
| **Projected Committed with Batch 09** | **$71.00 USD** | **Affordable: $71.00 <= $80.00** ($9.00 headroom) |

Actual invoices remain unbilled / unknown (`billedTotal: null`). Holds are strictly preserved.

---

## 5. Demonstrated Inventory Gaps & Identity Accounting

- **Total Baseline Purchase Inventory**: 480 outputs across 16 batches.
- **Executed Attempts**: 240 attempts across 235 distinct requested IDs (5 intentional duplicates in Batch 03).
- **Unrequested Baseline Items**: 245 items remain unrequested:
  - `attackers`: 38 unrequested (40 total − 2 in Batch 08)
  - `creatures`: 8 unrequested (8 total neutral creatures)
  - `hero-paintings`: 24 unrequested (32 total − 8 in Batches 01/02)
  - `gear`: 122 unrequested (128 total − 6 in Batch 02)
  - `artifacts`: 10 unrequested
  - `sites`: 6 unrequested
  - `supporting`: 16 unrequested
  - `mounts`: 3 unrequested
  - `rig-sheets`: 8 unrequested
  - `effects`: 10 unrequested

Detailed ledger saved at: `docs/plan/image-production/IDENTITY-GAP-LEDGER-20261003.json` and `.md`.

---

## 6. Batch 07 Prompt Corrections (Heavy Units)

In executed `batch-07-manifest.json`, 6 heavy troop prompts mistakenly requested human infantry instead of the vehicle/beast/crew identities mandated by the frozen roster. Those originals are preserved as crew and visual reference fragments. 

The corrected draft is saved at `docs/plan/image-production/batch-07-manifest-corrected-draft.json` with immutable links to the Batch 07 attempts:
1. `troop-bronze-heavy` -> **Charioteer**: horse-drawn two-wheeled bronze war chariot with spoked wheels, bronze driver and warrior with spear/bow.
2. `troop-iron-heavy` -> **War Elephant**: Asian war elephant with iron head barding/tusk caps and iron-reinforced fighting howdah.
3. `troop-medieval-heavy` -> **Siege Knight**: heavy knight mounted on a destrier warhorse with full steel plate barding/caparison and couched siege lance.
4. `troop-gunpowder-heavy` -> **Cannon Crew**: field artillery wheeled bronze cannon with 2-man gunner crew (linstock, ramrod, powder cask); contradictory boilerplate removed.
5. `troop-industrial-heavy` -> **Steam Walker**: steam-powered bipedal armored combat walker with iron boiler, smoking chimney, and rotary autocannon.
6. `troop-modern-heavy` -> **Battle Tank**: modern tracked main battle tank with rotating turret, smoothbore tank cannon, and reactive armor.
7. `troop-future-heavy` -> **Hover Tank**: sci-fi combat hover tank with glowing repulsor pads, sleek composite chassis, and twin plasma railguns.

---

## 7. Concrete Next Batch: Draft Batch 09

Manifest: `docs/plan/image-production/batch-09-manifest-draft.json`
Readiness: `docs/plan/image-production/batch-09-readiness-draft.json`

### 30 Exact Unrequested Inventory Gap Positions:
1. `attacker-stone-archer` (tribal slinger hunter with hide pouch and flint stones)
2. `attacker-stone-sapper` (primitive demolition breacher with firebrands and digging pick)
3. `attacker-stone-shaman` (tribal shaman with feathered stag skull headdress and bone rattle staff)
4. `attacker-bronze-brute` (hulking bronze-armored champion with horned helm and bronze war club)
5. `attacker-bronze-runner` (agile bronze skirmisher with linen tunic and dual bronze daggers)
6. `attacker-bronze-archer` (composite bow raider with bronze-tipped arrows and hip quiver)
7. `attacker-bronze-sapper` (siege sapper with bronze-tipped ladder and battering log)
8. `attacker-bronze-shaman` (sun mystic with bronze sun mask and solar staff)
9. `attacker-iron-brute` (armored barbarian vanguard with iron chain shirt and spiked iron mace)
10. `attacker-iron-runner` (swift hill raider in studded leather with dual iron short swords)
11. `attacker-iron-archer` (iron arbalest crossbowman with heavy iron-spanned crossbow)
12. `attacker-iron-sapper` (fortress sapper with iron pickaxe and entrenching shovel)
13. `attacker-iron-shaman` (druidic bone-seer with carved oak staff and raven skull)
14. `attacker-medieval-brute` (mercenary shock trooper in blackened half-plate with spiked flail)
15. `attacker-medieval-runner` (hooded rogue assassin in dark leather brigandine with stiletto daggers)
16. `attacker-medieval-archer` (heavy yeoman archer with heavy yew warbow and bodkin arrows)
17. `attacker-medieval-sapper` (siege engineer with wooden mantlet shield and heavy sledgehammer)
18. `attacker-medieval-shaman` (heretic blood-cultist with cowled vestments and occult runic tome)
19. `attacker-gunpowder-brute` (grenadier assault trooper with iron breastplate and bomb satchel)
20. `attacker-gunpowder-runner` (saboteur raider in dark coat with dual flintlock pistols and cutlass)
21. `attacker-gunpowder-archer` (sharpshooter skirmisher with long-barrel flintlock rifle and powder horn)
22. `attacker-gunpowder-sapper` (field pioneer sapper carrying fused gunpowder keg and shovel)
23. `attacker-gunpowder-shaman` (dark alchemist in leather coat and plague doctor mask with alembic flask)
24. `attacker-industrial-brute` (steam-augmented riot shock trooper with hydraulic arm brace and trench maul)
25. `attacker-industrial-runner` (stealth trench raider in gas mask with trench daggers and smoke canister)
26. `attacker-industrial-archer` (designated marksman with bolt-action scoped rifle and bandolier)
27. `attacker-industrial-sapper` (combat demolition pioneer carrying dynamite bundles and plunger detonator)
28. `attacker-industrial-shaman` (galvanic tesla-technician with sparking induction coils and conduction rod)
29. `attacker-modern-brute` (heavily armored tactical juggernaut in EOD bomb suit with riot shield)
30. `attacker-modern-runner` (covert operative in night-ops tactical suit with suppressed SMG)

*(The remaining 8 attackers—Modern Archer/Sapper/Shaman + all 5 Future attackers—naturally form the start of Batch 10 alongside Creatures and Hero paintings).*

- **Spatial Guides**: All 30 spatial guides created deterministically in `docs/plan/image-production/guides/attacker-*.png` using Defense mode geometry ([1.0, 1.0] ground footprint, pivot 512,790).
- **Validation**: Passed all checks in `validate_paid(m, b)`.

---

## 8. Remaining Authorization Blocker

Record of deferral: `docs/plan/image-production/next-batch-deferred.json`.

**The executor has NOT submitted Batch 09.**
Technical preparation, deterministic guides, prompt audits, and financial affordability checks are complete. However, the planner's report does not authorize batch 09+. In strict accordance with the owner's policy, the executor requires **explicit owner authorization** before submitting `production-09-20261003` to Vertex AI.
