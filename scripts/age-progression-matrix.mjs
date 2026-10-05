import fs from 'node:fs';
import data from '../src/data/reference-data.json' with { type: 'json' };
import { agePrice, forgeOffer, recruitCost, towerPurchaseCost } from '../src/core/rules.js';

const ages = data.AGES.map(age => age.n);
const lines = ['# Eight-age progression matrix — 4 October 2026', '', 'Computed from the live rules. This is not a played eight-age journey and it does not change a save.', ''];
lines.push('| Age | Advance cost | Melee recruit x5 | Heavy recruit x5 | Arrow tower | Forge quality 0 at Armory 1 |');
lines.push('|---|---|---|---|---|---|');
for (let age = 0; age <= 7; age++) {
  const advance = age < 7 ? agePrice(age) : null;
  const melee = recruitCost(data, 'melee', age);
  const heavy = recruitCost(data, 'heavy', age);
  const tower = towerPurchaseCost(data, 'arrow', age);
  const forge = forgeOffer(age, 1);
  const money = value => Object.entries(value).map(([key, amount]) => `${amount} ${key}`).join(', ');
  lines.push(`| ${ages[age]} | ${advance ? money(advance) : 'Future has no further age'} | ${money(melee)} | ${money(heavy)} | ${money(tower)} | ${money(forge.cost)} |`);
}
lines.push('', 'Armory level 1 caps forge quality at 0. Quality rises by one at Armory levels 3, 5, and 7, and it never passes 3. Positive morale remains an owner decision and is not applied here.');
fs.mkdirSync('docs/plan', { recursive: true });
fs.writeFileSync('docs/plan/AGE-PROGRESSION-MATRIX-2026-10-04.md', lines.join('\n') + '\n');
console.log('wrote age matrix');
