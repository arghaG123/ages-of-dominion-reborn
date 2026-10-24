import fs from 'node:fs';

const contract = JSON.parse(fs.readFileSync('qa/mock-led-executor-20261016/completion-contract.json', 'utf8'));
const passed = contract.leaves.filter(l => l.result === 'PASS');
console.log('Passed leaves count:', passed.length);

for (const leaf of passed) {
  console.log(`\nLeaf ${leaf.leafId}: ${leaf.name}`);
  const text = `${leaf.evidence || ''} ${leaf.recheckedEvidence || ''}`;
  const tokens = text.match(/[a-zA-Z0-9_\-\.\/]+\.[a-zA-Z0-9]+/g) || [];
  for (const token of tokens) {
    const exists = fs.existsSync(token);
    console.log(`  ${token}: ${exists ? 'EXISTS' : '>>> MISSING <<<'}`);
  }
}
