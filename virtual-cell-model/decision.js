(function () {
  'use strict';
  function compare(weights) {
    if (weights.length !== 3 || weights.some(w => !Number.isFinite(w) || w < 0)) throw new Error('Invalid weights');
    const total = weights.reduce((a, b) => a + b, 0);
    if (!total) return null;
    const score = values => values.reduce((sum, value, i) => sum + value * weights[i] / total, 0);
    const c = score([8, 7, 3]), d = score([6, 5, 9]);
    return { c, d, selection: Math.abs(c - d) < 1e-12 ? 'Tie' : c > d ? 'C' : 'D' };
  }
  if (typeof module !== 'undefined') module.exports = { compare };
  if (typeof document === 'undefined') return;
  const ids = ['health', 'relationships', 'resources'];
  function update() {
    const weights = ids.map(id => Number(document.getElementById(id).value));
    ids.forEach((id, i) => { document.getElementById(id + '-value').textContent = weights[i]; });
    const result = compare(weights), output = document.getElementById('result');
    output.textContent = result ? `${result.selection === 'Tie' ? 'Equal scores' : 'Selected: ' + result.selection} · C: ${result.c.toFixed(2)} / D: ${result.d.toFixed(2)}` : 'Choose at least one positive weight.';
    output.className = 'result';
  }
  ids.forEach(id => document.getElementById(id).addEventListener('input', update));
  update();
})();
