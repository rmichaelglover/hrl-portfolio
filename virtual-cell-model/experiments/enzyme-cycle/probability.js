'use strict';
const rate = document.getElementById('rate');
const time = document.getElementById('time');
function updateProbability() {
  const k = Number(rate.value);
  const dt = Number(time.value);
  document.getElementById('rate-value').textContent = k.toFixed(2);
  document.getElementById('time-value').textContent = dt.toFixed(2);
  document.getElementById('probability').textContent = (-Math.expm1(-k * dt) * 100).toFixed(1) + '%';
}
rate.addEventListener('input', updateProbability);
time.addEventListener('input', updateProbability);
updateProbability();
