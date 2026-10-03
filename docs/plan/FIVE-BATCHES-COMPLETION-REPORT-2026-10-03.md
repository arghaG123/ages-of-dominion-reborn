# Five-Batch Production Execution Completion Report (Batches 09–13)
**Date**: 3 October 2026  
**Project**: `project-eaa4c1cc-8f19-4d24-9e6`  
**Account**: `arghawork3@gmail.com`  
**Model**: `gemini-3.1-flash-image` (Vertex AI Global Batch Prediction, 1K)  
**Branch**: `codex/rebuild` (independent repo at `C:\dev\ages-of-dominion-reborn`)

---

## 1. Executive Summary

Under the explicit owner authorization to execute the next **five** batches (`production-09` through `production-13`, exactly 30 useful requests each, 150 requests maximum), all five batches were executed sequentially, monitored to terminal state, and collected to local storage.

- **Completed Batches**: 5 (`production-09`, `production-10`, `production-11`, `production-12`, `production-13`)
- **Total Requests Executed**: 150 requests (30 per batch)
- **Terminal Provider States**: 5/5 `JOB_STATE_SUCCEEDED` (0 failed, 0 active, 0 unknown)
- **Collected Originals**: 150 verified PNG originals in `assets/production/production-{09..13}-20261003/images/`
- **Technical Validation Status**: **PASS** for all 5 batches (0 decode errors, 0 dimension errors, 100% prompt SHA256 and payload matches)
- **Visual Review Status**: **UNVERIFIED** (pixel fidelity, matte, and runtime integration await section/runtime review)
- **Sequential Pipeline Enforced**:
  - `production-09` completed terminal -> `production-10` submitted **before** `production-09` collected.
  - `production-10` completed terminal -> `production-11` submitted **before** `production-10` collected.
  - `production-11` completed terminal -> `production-12` submitted **before** `production-11` collected.
  - `production-12` completed terminal -> `production-13` submitted **before** `production-12` collected.
  - `production-13` completed terminal -> `production-13` collected; **Batch 14 was NOT submitted**.
- **Single Active/Unknown Job Rule**: Strictly maintained across all 48 project locations throughout the entire sequence.
- **Provider Collection Parser Fix**: Repaired `scripts/vertex-production.py` to support multi-part candidate responses from Gemini 3.1 Flash Image (selecting the final generated image part `found[-1]`), resolving a collection error where `attacker-future-runner` produced two parts.

---

## 2. Batch Execution Registry (Batches 09–13)

| Batch ID | Provider Job Resource Name | Submitted (UTC) | Completed (UTC) | Provider State | Outputs | Technical Status | Reconciled Liability |
|---|---|---|---|---|---|---|---|
| `production-09-20261003` | `projects/186933974004/locations/global/batchPredictionJobs/7989419961254674432` | 11:28:00 | 11:33:27 | `JOB_STATE_SUCCEEDED` | 30/30 | **PASS** | $2.39 USD |
| `production-10-20261003` | `projects/186933974004/locations/global/batchPredictionJobs/6595555876583505920` | 11:35:25 | 12:08:26 | `JOB_STATE_SUCCEEDED` | 30/30 | **PASS** | $2.45 USD |
| `production-11-20261003` | `projects/186933974004/locations/global/batchPredictionJobs/7177646128421142528` | 12:10:36 | 12:24:31 | `JOB_STATE_SUCCEEDED` | 30/30 | **PASS** | $2.36 USD |
| `production-12-20261003` | `projects/186933974004/locations/global/batchPredictionJobs/1629211387500691456` | 12:26:28 | 12:29:53 | `JOB_STATE_SUCCEEDED` | 30/30 | **PASS** | $2.36 USD |
| `production-13-20261003` | `projects/186933974004/locations/global/batchPredictionJobs/2619440355568779264` | 13:01:50 | 13:07:42 | `JOB_STATE_SUCCEEDED` | 30/30 | **PASS** | $2.35 USD |

---

## 3. Inventory Gap Coverage (Batches 09–13)

Exactly 150 distinct unrequested baseline inventory positions were fulfilled:

### Batch 09: 30 Era Attackers (Stone through early Modern)
- `attacker-stone-archer`, `attacker-stone-sapper`, `attacker-stone-shaman`
- `attacker-bronze-brute`, `attacker-bronze-runner`, `attacker-bronze-archer`, `attacker-bronze-sapper`, `attacker-bronze-shaman`
- `attacker-iron-brute`, `attacker-iron-runner`, `attacker-iron-archer`, `attacker-iron-sapper`, `attacker-iron-shaman`
- `attacker-medieval-brute`, `attacker-medieval-runner`, `attacker-medieval-archer`, `attacker-medieval-sapper`, `attacker-medieval-shaman`
- `attacker-gunpowder-brute`, `attacker-gunpowder-runner`, `attacker-gunpowder-archer`, `attacker-gunpowder-sapper`, `attacker-gunpowder-shaman`
- `attacker-industrial-brute`, `attacker-industrial-runner`, `attacker-industrial-archer`, `attacker-industrial-sapper`, `attacker-industrial-shaman`
- `attacker-modern-brute`, `attacker-modern-runner`

### Batch 10: 8 Attackers + 8 Creatures + 14 Hero Paintings
- 8 Attackers: `attacker-modern-archer`, `attacker-modern-sapper`, `attacker-modern-shaman`, `attacker-future-brute`, `attacker-future-runner`, `attacker-future-archer`, `attacker-future-sapper`, `attacker-future-shaman`
- 8 Neutral Creatures: `creature-wolf-pack`, `creature-bandit-outlaw`, `creature-wild-bear`, `creature-harpy-scout`, `creature-stone-golem`, `creature-griffin-sentinel`, `creature-swamp-wyvern`, `creature-renegade-drone`
- 14 Hero Paintings: `hero-warrior-medieval`, `hero-ranger-medieval`, `hero-mage-medieval`, `hero-cleric-medieval`, `hero-rogue-medieval`, `hero-paladin-medieval`, `hero-necromancer-medieval`, `hero-monk-medieval`, `hero-warrior-gunpowder`, `hero-ranger-gunpowder`, `hero-mage-gunpowder`, `hero-cleric-gunpowder`, `hero-rogue-gunpowder`, `hero-paladin-gunpowder`

### Batch 11: 10 Hero Paintings + 6 Sites + 10 Artifacts + 3 Mounts + 1 Title Background
- 10 Hero Paintings: `hero-necromancer-gunpowder`, `hero-monk-gunpowder`, `hero-warrior-modern`, `hero-ranger-modern`, `hero-mage-modern`, `hero-cleric-modern`, `hero-rogue-modern`, `hero-paladin-modern`, `hero-necromancer-modern`, `hero-monk-modern`
- 6 Adventure Sites: `adventure-site-treasure-vault`, `adventure-site-sanctuary-rest`, `adventure-site-passage-exit`, `adventure-site-rival-camp`, `adventure-site-ancient-dwelling`, `adventure-site-guardian-post`
- 10 Artifact Relics: `artifact-chalice-of-vitality`, `artifact-orb-of-storms`, `artifact-crown-of-dominion`, `artifact-tome-of-arcana`, `artifact-banner-of-valor`, `artifact-horn-of-calling`, `artifact-mirror-of-truth`, `artifact-compass-of-epochs`, `artifact-ring-of-eternity`, `artifact-aegis-of-protection`
- 3 Mount Masters: `mount-horse-master`, `mount-motor-master`, `mount-future-master`
- 1 Title Background: `title-background-panoramic` (16:9)

### Batch 12: 8 Chapters + 6 Rivals + 1 UI Material + 8 Class Rig Plates + 7 Spell Effects
- 8 Chapter Artworks (16:9): `chapter-artwork-01` through `chapter-artwork-08`
- 6 Persistent Rivals: `rival-aldric-ironclad`, `rival-valeria-sunblade`, `rival-corvus-nightveil`, `rival-theron-stormcaller`, `rival-morgana-shadowweaver`, `rival-kane-dreadnought`
- 1 UI Material: `ui-material-texture-sheet`
- 8 Class Rig Plates: `rig-sheet-warrior`, `rig-sheet-ranger`, `rig-sheet-mage`, `rig-sheet-cleric`, `rig-sheet-rogue`, `rig-sheet-paladin`, `rig-sheet-necromancer`, `rig-sheet-monk`
- 7 Spell Effects: `effect-fireball-impact`, `effect-lightning-strike`, `effect-frost-nova`, `effect-healing-radiance`, `effect-shadow-bolt`, `effect-meteor-strike`, `effect-shield-barrier`

### Batch 13: 3 Combat Effects + 27 Core Era Equipment Items
- 3 Combat Effects: `effect-holy-resurrection`, `effect-ballistic-projectiles`, `effect-kinetic-impacts`
- 27 Era Equipment Items:
  - Bronze (6): `gear-bronze-head-helmet`, `gear-bronze-chest-cuirass`, `gear-bronze-hands-bracers`, `gear-bronze-legs-greaves`, `gear-bronze-mainhand-kopesh`, `gear-bronze-offhand-shield`
  - Iron (6): `gear-iron-head-spangenhelm`, `gear-iron-chest-chainmail`, `gear-iron-hands-gauntlets`, `gear-iron-legs-chausses`, `gear-iron-mainhand-broadsword`, `gear-iron-offhand-targe`
  - Medieval (6): `gear-medieval-head-greathelm`, `gear-medieval-chest-plate`, `gear-medieval-hands-hourglass-gauntlets`, `gear-medieval-legs-plate-greaves`, `gear-medieval-mainhand-longsword`, `gear-medieval-offhand-heater-shield`
  - Gunpowder (6): `gear-gunpowder-head-morion`, `gear-gunpowder-chest-breastplate`, `gear-gunpowder-hands-leather-gloves`, `gear-gunpowder-legs-riding-boots`, `gear-gunpowder-mainhand-sabre`, `gear-gunpowder-offhand-buckler`
  - Industrial (3): `gear-industrial-head-pith-helmet`, `gear-industrial-chest-trench-tunic`, `gear-industrial-mainhand-cavalry-sword`

---

## 4. Reconciled Financial Ledger & Token Consumption

### Cumulative Across All 13 Batches (01–13):

| Batch | Outputs | Input Tokens | Output Tokens | Total Tokens | Standard Cost | Buffered Cost (15%) | Reconciled Exposure |
|---|---:|---:|---:|---:|---:|---:|---:|
| `production-01` | 30 | 69,669 | 33,600 | 103,269 | $2.0508 | $2.3585 | $2.37 USD |
| `production-02` | 30 | 38,320 | 34,147 | 72,467 | $2.0680 | $2.3782 | $2.37 USD |
| `production-03` | 30 | 73,707 | 33,600 | 107,307 | $2.0529 | $2.3608 | $2.37 USD |
| `production-04` | 30 | 74,165 | 33,600 | 107,765 | $2.0531 | $2.3610 | $2.37 USD |
| `production-05` | 30 | 74,772 | 33,600 | 108,372 | $2.0534 | $2.3614 | $2.37 USD |
| `production-06` | 30 | 74,738 | 33,600 | 108,338 | $2.0534 | $2.3614 | $2.37 USD |
| `production-07` | 30 | 75,101 | 34,524 | 109,625 | $2.1090 | $2.4253 | $2.37 USD |
| `production-08` | 30 | 74,971 | 33,600 | 108,571 | $2.0535 | $2.3615 | $2.37 USD |
| `production-09` | 30 | 75,218 | 34,038 | 109,256 | $2.0799 | $2.3919 | $2.39 USD |
| `production-10` | 30 | 57,368 | 34,960 | 92,328 | $2.1263 | $2.4452 | $2.45 USD |
| `production-11` | 30 | 48,617 | 33,716 | 82,333 | $2.0473 | $2.3544 | $2.36 USD |
| `production-12` | 30 | 55,623 | 33,655 | 89,278 | $2.0471 | $2.3542 | $2.36 USD |
| `production-13` | 30 | 41,046 | 33,600 | 74,646 | $2.0365 | $2.3420 | $2.35 USD |
| **Total (13 Batches)** | **390** | **833,315** | **440,240** | **1,273,555** | **$26.8311** | **$30.8557** | **$30.87 USD** |

### Budget Status vs Cap & Target:
- **Sum of Reconciled Batch Liabilities**: $30.87 USD ($30.856 USD buffered calculation)
- **Historical Mock Conservative Hold**: $2.00 USD
- **Safety Reserve Hold**: $15.00 USD
- **Total Protected Commitments**: **$47.856 USD** (rounded to $47.87 USD)
- **Target Budget**: **$60.00 USD**
  - **Remaining Target Headroom**: **$12.144 USD** (Committed is well within target!)
- **Hard Cap**: **$80.00 USD**
  - **Remaining Hard Cap Margin**: **$32.144 USD** (Zero risk of cap breach)
- **Provider Invoice Status**: `billedTotal: null` (holds retained, actual charges pending invoice).

---

## 5. Lock and Job Mutex State

- **Local Lock**: `docs/plan/image-production/active-batch.lock.json`
  - `batch_id`: `"production-13-20261003"`
  - `state`: `"JOB_STATE_SUCCEEDED"`
  - `workflow_state`: `"TERMINAL_COLLECTED"`
  - `provider_job_name`: `"projects/186933974004/locations/global/batchPredictionJobs/2619440355568779264"`
  - `cloud_lock_generation`: `"1791032965965985"`
- **Cloud Lock**: `gs://project-eaa4c1cc-8f19-4d24-9e6-aod-batch/design-mocks/active-batch.lock.json` (synchronized, matching generation).
- **Active/Unknown Jobs Across GCP**: **0 active, 0 unknown**. All 13 batches are in terminal state `JOB_STATE_SUCCEEDED`.
