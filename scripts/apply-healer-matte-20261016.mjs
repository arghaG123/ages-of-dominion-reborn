import fs from 'node:fs';
import crypto from 'node:crypto';
import path from 'node:path';

const src = path.resolve('assets/derivatives/mock-led-20261016/bodies/healer_fixed_matte.png');
const dst = path.resolve('assets/derivatives/mock-led-20261016/bodies/class-healer-standing-body.png');

fs.copyFileSync(src, dst);
const buf = fs.readFileSync(dst);
const sha = crypto.createHash('sha256').update(buf).digest('hex');
console.log('Copied to', dst);
console.log('Size:', buf.length);
console.log('SHA256:', sha);

const bodiesPath = path.resolve('src/data/hero-bodies-20261011.json');
const bodies = JSON.parse(fs.readFileSync(bodiesPath, 'utf8'));
const healer = bodies.bodies && bodies.bodies.healer;
if (healer) {
  healer.bytes = buf.length;
  healer.sha256 = sha;
  healer.matteRepair.paperWhiteBackdropClearedRemnantsRemoved = true;
  healer.matteRepair.whiteRemnantBelowStaffCleaned = true;
  fs.writeFileSync(bodiesPath, JSON.stringify(bodies, null, 2));
  console.log('Updated hero-bodies-20261011.json for healer');
}
