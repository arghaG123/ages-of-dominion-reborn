import { command } from '../src/core/campaign.js';
import { legalDeploymentCells } from '../src/core/battle.js';

export function completeSkirmishDeployment(state, data, prefix = 'test-skirmish') {
  let next = state;
  let index = 0;
  const send = (type, payload = {}) => {
    next = command(next, { id: `${prefix}-${index++}`, type, payload }, next.clock, data);
  };
  send('START_SKIRMISH');
  for (const stackId of next.battle.deployment.movableIds) {
    const cell = legalDeploymentCells(next.battle, stackId)[0];
    if (!cell) throw new Error(`No legal deployment cell for ${stackId}`);
    send('DEPLOY_BATTLE_STACK', { stackId, cell });
  }
  send('START_DEPLOYED_BATTLE');
  return next;
}
