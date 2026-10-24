// Presentation mirror of BUILD's existing job duration. Core timing remains authoritative.
export function constructionDurationMs(building, level, payment) {
  const total = Object.values(payment || {}).reduce((sum, amount) => sum + amount, 0);
  return building === 'quarry' && level === 0
    ? 3000
    : Math.round(3000 + Math.min(1, Math.max(0, (total - 300) / 2200)) * 5000);
}

export function formatConstructionDuration(durationMs) {
  const seconds = Number((Math.ceil(durationMs / 100) / 10).toFixed(1));
  const value = Number.isInteger(seconds) ? String(seconds) : seconds.toFixed(1);
  return value + ' ' + (seconds === 1 ? 'second' : 'seconds');
}

export function plotProduction(state, plotId, rateFor) {
  const plot = state?.plots?.find(item => item.id === plotId);
  if (!plot?.type || plot.level < 1 || typeof rateFor !== 'function') return null;

  const total = rateFor(state);
  const withoutPlot = rateFor({ ...state, plots: state.plots.filter(item => item.id !== plotId) });
  for (const [resource, amount] of Object.entries(total || {})) {
    const rate = amount - (withoutPlot?.[resource] || 0);
    if (rate > 0.000001) return { resource, rate };
  }
  return null;
}
