/* Original conceptual illustrations. Static first; animation only on request. */
(() => {
  if(document.documentElement.classList.contains('maestro-embedded'))return;
  const script = document.currentScript;
  const theme = script.dataset.dayTheme || 'chess';
  const labels = {chess:'A knight takes the scenic route',language:'Words and their connections',quantum:'Two illustrated waves',economics:'An illustrated cycle of exchange',biology:'An illustrated cell community'};
  const base = new URL('.', script.src);
  const still = new URL(theme + '.png', base).href;
  const animation = new URL(theme + '.gif', base).href;
  const style = document.createElement('style');
  style.textContent = '.day-visual{box-sizing:border-box;max-width:520px;margin:20px 0;padding:0;font:13px/1.5 system-ui,sans-serif}.day-visual img{display:block;width:100%;height:auto;border-radius:10px}.day-visual figcaption{display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin-top:7px}.day-visual button{font:inherit;cursor:pointer;padding:5px 12px;border:1px solid #a7977f;border-radius:6px;background:#fffaf1;color:#27241d}.day-visual button:focus-visible{outline:3px solid #b89337;outline-offset:3px}';
  document.head.append(style);
  const figure = document.createElement('figure'); figure.className = 'day-visual';
  const img = document.createElement('img'); img.src = still; img.width = 640; img.height = 240; img.alt = labels[theme] + ' — conceptual illustration';
  const caption = document.createElement('figcaption');
  const label = document.createElement('span');label.textContent = labels[theme] + ' · Illustration';
  const button = document.createElement('button');button.type = 'button';button.textContent = 'Play GIF';button.setAttribute('aria-pressed','false');
  let playing = false;
  const stop = () => {playing=false;img.src=still;button.textContent='Play GIF';button.setAttribute('aria-pressed','false');};
  button.addEventListener('click',()=>{if(playing){stop();return;}playing=true;img.src=animation;button.textContent='Pause GIF';button.setAttribute('aria-pressed','true');});
  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  motion.addEventListener('change', e => {if(e.matches)stop();});
  document.addEventListener('visibilitychange',()=>{if(document.hidden)stop();});
  caption.append(label,button);figure.append(img,caption);
  const heading = document.querySelector(script.dataset.dayTarget || 'h1');
  if(heading)heading.after(figure);else (document.querySelector('main')||document.body).prepend(figure);
})();
