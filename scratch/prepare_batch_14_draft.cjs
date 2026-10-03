const fs = require("fs");
const crypto = require("crypto");

function sha256(str) {
  return crypto.createHash("sha256").update(str, "utf8").digest("hex");
}

const gearPrompts = [
  {
    id: "gear-industrial-armor-field",
    age: "industrial",
    name: "Industrial Age Field Armor (armor)",
    desc: "heavy canvas and steel-reinforced trench vest with leather straps and cartridge loops."
  },
  {
    id: "gear-industrial-armor-robe",
    age: "industrial",
    name: "Industrial Age Heavy Overcoat (armor)",
    desc: "thick wool trench greatcoat with reinforced brass buttons and shoulder epaulettes."
  },
  {
    id: "gear-industrial-boots-soft",
    age: "industrial",
    name: "Industrial Age Riding Boots (boots)",
    desc: "polished knee-high calfskin officer boots with brass spur mounts."
  },
  {
    id: "gear-industrial-accessory",
    age: "industrial",
    name: "Industrial Age Officer Watch (accessory)",
    desc: "ornate brass pocket watch with mechanical gearing and linked gold chain."
  },
  {
    id: "gear-modern-helm",
    age: "modern",
    name: "Modern Age Tactical Helmet (helm)",
    desc: "ballistic composite combat helmet with night-vision mount and tactical headset rails."
  },
  {
    id: "gear-modern-helm-hood",
    age: "modern",
    name: "Modern Age Recon Balaclava (helm)",
    desc: "flame-resistant tactical balaclava with protective ballistic eye goggles."
  },
  {
    id: "gear-modern-helm-circlet",
    age: "modern",
    name: "Modern Age Tactical Headset (helm)",
    desc: "active electronic noise-cancelling communications headset with boom microphone."
  },
  {
    id: "gear-modern-weapon",
    age: "modern",
    name: "Modern Age Tactical Assault Carbine (weapon)",
    desc: "polymer tactical assault rifle with holographic reflex sight and picatinny accessory rails."
  },
  {
    id: "gear-modern-weapon-ranger",
    age: "modern",
    name: "Modern Age Precision Sniper Rifle (weapon)",
    desc: "bolt-action anti-materiel sniper rifle with heavy bipod and variable high-power optical scope."
  },
  {
    id: "gear-modern-weapon-caster",
    age: "modern",
    name: "Modern Age EMP Emitter (weapon)",
    desc: "high-energy directional electromagnetic pulse weapon with glowing blue battery coils."
  },
  {
    id: "gear-modern-weapon-barbarian",
    age: "modern",
    name: "Modern Age Tactical Breaching Axe (weapon)",
    desc: "hardened carbon-steel tactical tomahawk with textured rubberized grip and pry spike."
  },
  {
    id: "gear-modern-offhand",
    age: "modern",
    name: "Modern Age Ballistic Riot Shield (offhand)",
    desc: "heavy transparent polycarbonate and kevlar tactical shield with armored view port."
  },
  {
    id: "gear-modern-offhand-codex",
    age: "modern",
    name: "Modern Age Military Tactical Tablet (offhand)",
    desc: "ruggedized military battlefield command tablet displaying encrypted digital satellite maps."
  },
  {
    id: "gear-modern-offhand-focus",
    age: "modern",
    name: "Modern Age Target Designator (offhand)",
    desc: "handheld laser target designator optic with digital rangefinder display."
  },
  {
    id: "gear-modern-armor",
    age: "modern",
    name: "Modern Age Ballistic Plate Carrier (armor)",
    desc: "heavy multicam tactical plate carrier with ceramic armor inserts and MOLLE magazine pouches."
  },
  {
    id: "gear-modern-armor-field",
    age: "modern",
    name: "Modern Age Combat Uniform (armor)",
    desc: "ripstop tactical combat shirt and pants with integrated hard-shell elbow and knee pads."
  },
  {
    id: "gear-modern-armor-robe",
    age: "modern",
    name: "Modern Age Ghillie Camouflage Suit (armor)",
    desc: "dense woodland camouflage ghillie concealment poncho with synthetic foliage burlap strips."
  },
  {
    id: "gear-modern-boots",
    age: "modern",
    name: "Modern Age Combat Assault Boots (boots)",
    desc: "waterproof tactical combat assault boots with vibram high-traction lug soles."
  },
  {
    id: "gear-modern-boots-soft",
    age: "modern",
    name: "Modern Age Stealth Recon Shoes (boots)",
    desc: "lightweight silent-tread tactical recon footwear with reinforced synthetic toe caps."
  },
  {
    id: "gear-modern-accessory",
    age: "modern",
    name: "Modern Age GPS Tactical Wrist Unit (accessory)",
    desc: "ruggedized tactical digital navigation smartwatch displaying encrypted compass telemetry."
  },
  {
    id: "gear-future-helm",
    age: "future",
    name: "Future Age Cybernetic Full-Face Helm (helm)",
    desc: "sleek carbon-nanotube full enclosure helmet with integrated gold holographic visor display."
  },
  {
    id: "gear-future-helm-hood",
    age: "future",
    name: "Future Age Stealth Nano-Cowl (helm)",
    desc: "matte black hexagonal optical camouflage cowl with glowing cyan ocular implants."
  },
  {
    id: "gear-future-helm-circlet",
    age: "future",
    name: "Future Age Neural Interface Crown (helm)",
    desc: "sculpted titanium cranial interface ring with pulsing fiber-optic synapse connectors."
  },
  {
    id: "gear-future-weapon",
    age: "future",
    name: "Future Age Plasma Rifle (weapon)",
    desc: "sleek magnetic acceleration plasma rifle with glowing ion containment coils."
  },
  {
    id: "gear-future-weapon-ranger",
    age: "future",
    name: "Future Age Particle Beam Sniper (weapon)",
    desc: "long-barrel magnetic particle accelerator with quantum targeting lens and energy heatsinks."
  },
  {
    id: "gear-future-weapon-caster",
    age: "future",
    name: "Future Age Graviton Projector (weapon)",
    desc: "floating gyroscopic singularity wand with spinning magnetic containment rings."
  },
  {
    id: "gear-future-weapon-barbarian",
    age: "future",
    name: "Future Age Thermal Energy Claymore (weapon)",
    desc: "high-frequency superheated vibro-greatsword with glowing amber plasma cutting edge."
  },
  {
    id: "gear-future-offhand",
    age: "future",
    name: "Future Age Energy Force Barrier (offhand)",
    desc: "forearm-mounted emitter generating an iridescent hexagonal hard-light energy shield."
  },
  {
    id: "gear-future-offhand-codex",
    age: "future",
    name: "Future Age Quantum Data Holocron (offhand)",
    desc: "floating geometric quantum crystalline data matrix projecting rotating holographic glyphs."
  }
];

const forgeStyleRefSHA = "f5253c7524352e1f57aff00d7623ada1d3858216cdc04296f9dae4bc3e9ba560";
const kingdomDay1StyleRefSHA = "629dff52e46e85741604a37f59453c072b22ecdf56f71d50937a549e32a677bf";

const items = [];

for (let i = 0; i < gearPrompts.length; i++) {
  const g = gearPrompts[i];
  const pText = `ONE production image for Ages of Dominion. Semi-realistic dense rendered strategy-game materials, warm upper-left daylight, short soft contact shadows. NO text, HUD, buttons, labels, numbers, device frame, watermark, or invented names. Isolated object on pure magenta #FF00FF background. No floor, no background shadow. ONE high-detail equipment icon for Ages of Dominion RPG: ${g.name}. ${g.desc} Centrally framed inventory object, crisp authentic period materials, warm studio lighting. Pure flat magenta #FF00FF backdrop, no floor, no shadows, no text.`;
  items.push({
    position: i + 1,
    id: g.id,
    kind: "gear",
    mode: null,
    age: g.age,
    aspect: "1:1",
    prompt: pText,
    styleReference: "22-forge.jpg",
    guide: null,
    requiredAlpha: true,
    reviewStatus: "UNVERIFIED",
    attempt: 1,
    requestedOutputs: 1,
    reviewCriteria: `${g.age} era, ${g.id} item identity, clean silhouette, rich materials, clean magenta background.`,
    styleReferenceSHA256: forgeStyleRefSHA,
    promptSHA256: sha256(pText),
    guideSHA256: null
  });
}

// Position 30: kingdom-stone-day1-composition-v4
const kingdomPrompt = "Create ONE landscape 16:9, high-detail strategy-game composition reference for Ages of Dominion: Stone Age Kingdom, Day 1. Use the corrected spatial guide for layout. Use the approved landscape Day 1 reference for composition and material finish only. Use the preserved Hall v3 for Stone architectural identity. Show exactly ONE completed building: a prominent Stone Town Hall made from timber, hide, thatch, flint and rough stone foundations. Place it naturally on the upper civic terrace. Preserve its proportions and show its complete roof, foundation and entrance approach. It must be visibly grounded, with coherent perspective and contact shadows—not tiny, floating, stretched or sitting on a pasted ground island. Show 17 empty, usable building clearings connected by natural soil paths. Keep their footprints and approaches free of buildings, actors, logs and material stacks. No outlined rectangles, signs, plus marks, labels or visible grid. The perimeter is unbuilt: no completed walls, defensive towers or built gate. Keep a readable perimeter route and future entrance area. Include a river on the right, an age-appropriate crossing, connected roads, rocky hills and richly textured forest margins, following the corrected guide. Decorative outskirts must stay outside reserved plots and routes. Use a coherent high aerial three-quarter camera, warm upper-left daylight and consistent short shadows. Render complete terrain around the Hall without clipping required sites or scenery. No medieval church, spires, cannon, steel architecture, mature city, extra active buildings, gameplay HUD, text, numbers, buttons, watermark or guide marks.";

items.push({
  position: 30,
  id: "kingdom-stone-day1-composition-v4",
  kind: "kingdom-scene",
  mode: "kingdom",
  age: "stone",
  aspect: "16:9",
  prompt: kingdomPrompt,
  styleReference: "02-kingdom-day1.jpg",
  guide: "guides/kingdom-stone-day1-v4-pending.png",
  requiredAlpha: false,
  reviewStatus: "UNVERIFIED",
  attempt: 4,
  requestedOutputs: 1,
  reviewCriteria: "Inspect actual pixels for Stone identity, one Hall/17 empty plots/unbuilt walls, civic prominence, natural grounding, consistent camera, clear routes and full framing. Check proposed display framing at 825x375, 933x424, 1180x820, and 1280x720. Record PASS/FAIL/UNVERIFIED with evidence. Do not declare a pass from successful generation alone.",
  styleReferenceSHA256: kingdomDay1StyleRefSHA,
  promptSHA256: sha256(kingdomPrompt),
  guideSHA256: null,
  generationPrerequisiteStatus: "PENDING_ACCEPTED_SPATIAL_GUIDE"
});

const manifest = {
  id: "production-14-20261003",
  model: "gemini-3.1-flash-image",
  project: "project-eaa4c1cc-8f19-4d24-9e6",
  region: "global",
  count: 30,
  status: "DRAFT_NOT_SUBMITTED_HELD_PENDING_GUIDE_AND_OWNER_AUTHORIZATION",
  note: "Position 30 replaces gear-industrial-boots with kingdom-stone-day1-composition-v4 per owner instruction. Gear industrial boots was collected in Batch 13 position 30 and remains preserved in inventory tracking. Generation is held pending delivery of an accepted versioned spatial guide and explicit owner authorization for Batch 14.",
  items: items,
  maxOutputTokens: 4096,
  inputTokenUpperBoundPerRequest: 12000,
  reservedUSD: 6,
  pricingSources: [
    "https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing",
    "https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/capabilities/batch-inference",
    "https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/gemini/3-1-flash-image"
  ]
};

fs.writeFileSync("docs/plan/image-production/batch-14-manifest-draft.json", JSON.stringify(manifest, null, 2), "utf8");
console.log("Wrote batch-14-manifest-draft.json with count:", manifest.items.length);

const readiness = {
  checkedAt: new Date().toISOString(),
  batch: "production-14-20261003",
  status: "DRAFT_NOT_SUBMITTED_HELD_PENDING_GUIDE_AND_OWNER_AUTHORIZATION",
  requests: 30,
  locationsScanned: 48,
  activeOrUnknownJobs: 0,
  committedReservationUSD: 47.856,
  newReservationUSD: 6.0,
  safetyReserveUSD: 15.0,
  hardCapUSD: 80.0,
  targetUSD: 60.0,
  totalProjectedCommittedUSD: 53.856,
  affordableUnderTarget: true,
  affordableUnderHardCap: true,
  headroomRemainingUSD: 26.144,
  readyTechnicalPrerequisites: false,
  readyForSubmission: false,
  submissionBlockers: [
    {
      code: "CORRECTED_SPATIAL_GUIDE_NOT_AVAILABLE",
      detail: "An accepted, versioned spatial guide that integrates all 18 sites, 17 empty plots, river-right approach, and full vertical envelope without clipping or shrinking is not yet available on disk. Current proposal stone-framing-proposal.json remains PROPOSAL_NOT_ACCEPTED. Per owner directive (\"If the corrected guide is unavailable, keep this request pending\"), this request is held pending."
    },
    {
      code: "OWNER_AUTHORIZATION_REQUIRED_FOR_BATCH_14",
      detail: "The owner explicitly instructed: \"Never modify a submitted batch or start an additional batch14 under this instruction.\" Previous authorization covered batches 09-13 (150 requests) only."
    }
  ],
  backlogIntegrity: {
    displacedItem: "gear-industrial-boots",
    status: "COLLECTED_IN_BATCH_13_PRESERVED_IN_INVENTORY",
    collectedLocation: "assets/production/production-13-20261003/images/30-gear-industrial-boots.png"
  },
  costBound: {
    imageAndAnyOutputUpperUSD: 3.6864,
    inputUpperUSD: 0.09,
    batchReservationIncludesUSD: 6,
    actualInvoice: null
  }
};

fs.writeFileSync("docs/plan/image-production/batch-14-readiness-draft.json", JSON.stringify(readiness, null, 2), "utf8");
console.log("Wrote batch-14-readiness-draft.json");
