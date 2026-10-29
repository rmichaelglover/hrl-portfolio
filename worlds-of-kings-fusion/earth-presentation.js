/* Navigation and reversible presentation controls; no game state is changed. */
(() => {
  'use strict';
  const panel = document.querySelector('.map-panel, .atlas');
  if (!panel) return;
  const bar = document.createElement('div');
  bar.className = 'world-view-bar';
  const hint = document.createElement('p');
  const heading = document.createElement('strong');
  heading.textContent = 'Explore the globe';
  hint.append(heading, 'Drag to rotate or pan · use + / − to zoom · choose a projection in each view.');
  const focus = document.createElement('button');
  focus.type = 'button';
  focus.textContent = 'Expand world';
  focus.setAttribute('aria-pressed', 'false');
  focus.setAttribute('aria-controls', 'panes');
  function setExpanded(expanded) {
    document.body.classList.toggle('world-focus', expanded);
    focus.setAttribute('aria-pressed', String(expanded));
    focus.textContent = expanded ? 'Restore layout' : 'Expand world';
  }
  focus.addEventListener('click', () => setExpanded(!document.body.classList.contains('world-focus')));
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && document.body.classList.contains('world-focus')) {
      setExpanded(false);
      focus.focus();
    }
  });
  bar.append(hint, focus);
  panel.prepend(bar);
  const places = document.getElementById('place-navigation');
  if (places && !places.closest('details')) {
    const drawer = document.createElement('details');
    drawer.className = 'world-place-drawer';
    const summary = document.createElement('summary');
    summary.textContent = 'Jump to a region or city';
    places.before(drawer);
    drawer.append(summary, places);
  }
})();
