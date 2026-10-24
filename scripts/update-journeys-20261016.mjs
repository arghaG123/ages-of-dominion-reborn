import fs from 'node:fs';
import path from 'node:path';

const journeysPath = path.resolve('qa/mock-led-executor-20261016/journeys.json');
const raw = JSON.parse(fs.readFileSync(journeysPath, 'utf8'));

const verifiedBrowserSubcases = {
  'J01.1': { result: 'PASS', evidence: 'qa/mock-led-executor-20261016/browser-play-trace.json:J01.1' },
  'J01.2': { result: 'PASS', evidence: 'qa/mock-led-executor-20261016/browser-shots/j01-kingdom-day1.png' },
  'J02.1': { result: 'PASS', evidence: 'qa/mock-led-executor-20261016/browser-play-trace.json:J02.1' },
  'J02.2': { result: 'PASS', evidence: 'qa/mock-led-executor-20261016/browser-shots/j02-lumber-scaffold.png' },
  'J03.1': { result: 'PASS', evidence: 'qa/mock-led-executor-20261016/browser-play-trace.json:J03.1' },
  'J05.1': { result: 'PASS', evidence: 'qa/mock-led-executor-20261016/browser-play-trace.json:J05.1' },
  'J05.2': { result: 'PASS', evidence: 'qa/mock-led-executor-20261016/browser-shots/j05-adventure-travel.png' },
  'J07.1': { result: 'PASS', evidence: 'qa/mock-led-executor-20261016/browser-shots/j07-tactical-duel.png' },
  'J08.1': { result: 'PASS', evidence: 'qa/mock-led-executor-20261016/browser-play-trace.json:retreat-cancel' },
  'J08.2': { result: 'PASS', evidence: 'qa/mock-led-executor-20261016/browser-play-trace.json:retreat-confirm' },
  'J09.1': { result: 'PASS', evidence: 'qa/mock-led-executor-20261016/browser-shots/j09-defense-siege.png' },
  'J11.1': { result: 'PASS', evidence: 'qa/mock-led-executor-20261016/browser-shots/j11-hero-room.png' },
  'J12.1': { result: 'PASS', evidence: 'qa/mock-led-executor-20261016/browser-play-trace.json:J12.1' },
  'J15.1': { result: 'PASS', evidence: 'qa/mock-led-executor-20261016/browser-play-trace.json:J15.1' },
  'J16.2': { result: 'PASS', evidence: 'qa/mock-led-executor-20261016/browser-play-trace.json:J16.2' },
  'J18.1': { result: 'PASS', evidence: 'qa/mock-led-executor-20261016/browser-play-trace.json:J18.1' },
};

let passedCount = 0;
let unverifiedCount = 0;

for (const journey of raw.journeys) {
  journey.classification = 'simulation';
  for (const sub of journey.mandatorySubcases) {
    if (verifiedBrowserSubcases[sub.subcaseId]) {
      sub.result = verifiedBrowserSubcases[sub.subcaseId].result;
      sub.evidence = verifiedBrowserSubcases[sub.subcaseId].evidence;
      passedCount++;
    } else {
      sub.result = 'UNVERIFIED';
      sub.evidence = 'UNVERIFIED: Not played in browser session. Node test exists as simulation only.';
      unverifiedCount++;
    }
  }
}

raw.evaluatedAt = new Date().toISOString();
raw.summary = {
  totalJourneys: raw.journeys.length,
  passedJourneys: 0,
  failedJourneys: 0,
  passedSubcases: passedCount,
  unverifiedSubcases: unverifiedCount,
};

fs.writeFileSync(journeysPath, JSON.stringify(raw, null, 2), 'utf8');
console.log(`Updated journeys.json: passedSubcases=${passedCount}, unverifiedSubcases=${unverifiedCount}`);
