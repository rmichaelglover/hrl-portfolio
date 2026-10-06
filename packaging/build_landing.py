#!/usr/bin/env python3
"""Compose the full Maestro app and the preserved site directory into the homepage."""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
maestro=(ROOT/'maestro.html').read_text()
directory=(ROOT/'explore.html').read_text()
styles=re.search(r'<style>(.*?)</style>',directory,re.S).group(1)
styles=styles.replace(':root',':host').replace('html{',':host{').replace('body{',':host{')
content=directory[directory.index('<header>'):directory.index('<script>')]
# The directory retains its own style inside a shadow root so its buttons and
# headings cannot alter the chess board's established layout.
extras='''<div id="site-extras"></div><template id="site-extras-template"><style>'''+styles+'''</style>'''+content+'''</template>
<script>
const extras=document.getElementById('site-extras').attachShadow({mode:'open'});
extras.append(document.getElementById('site-extras-template').content.cloneNode(true));
extras.addEventListener('click',event=>{const anchor=event.target.closest('a[href^="#"]');if(!anchor)return;const target=extras.querySelector(anchor.getAttribute('href'));if(target){event.preventDefault();target.scrollIntoView({behavior:matchMedia('(prefers-reduced-motion:reduce)').matches?'instant':'smooth'});}});
</script>'''
maestro=maestro.replace('<body>','<body class="maestro-home" data-maestro-landing="1">',1)
start=maestro.index('  <div class="app">');end=maestro.index('<!-- WorldKit',start)
app=maestro[start:end]
# Homepage-only discoveries occupy the space below the move list.
spotlight = """<aside class="home-discoveries" aria-labelledby="home-discoveries-title">
<h2 id="home-discoveries-title">From our laboratory</h2>
<a class="discovery discovery-lead" href="relaxfish/"><img src="relaxfish/figures/potential_3d.png" alt="Three-dimensional RelaxFish compatibility potential" width="1200" height="800"><span class="discovery-copy"><span class="discovery-kicker">FLAGSHIP · CHESS RESEARCH</span><strong>Solving chess: RelaxFish &amp; certified proofs</strong><span>Hierarchical relaxation, adversarial search, and reproducible experiments. Explore the 27-page research article, eight color figures, and full results.</span><span class="discovery-action">Enter the RelaxFish laboratory ↗</span></span></a>
<a class="discovery" href="magnum-chessicus/"><img src="magnum-chessicus/figures/outcome-gap.png" alt="The discrete win, draw, and loss outcomes behind the certified-draw theorem" width="1200" height="800" loading="lazy"><span class="discovery-copy"><strong>Magnum Chessicus · the proof</strong><span>A proved conditional draw theorem and replayable small-position certificates. The initial position remains unresolved.</span><span class="discovery-action">Read the proof &amp; inspect certificates ↗</span></span></a>
<a class="discovery discovery-world" href="genesis/worlds/"><span class="world-preview" aria-hidden="true">🌋 <span>🏝️</span> 🪸</span><span class="discovery-copy"><strong>Living Worlds</strong><span>Explore the Terraformer, Floating Isles, and Deep Reef: interactive worlds that grow and change.</span><span class="discovery-action">Step into the simulations ↗</span></span></a>
</aside>"""
app=app.replace('<div class="meta" id="meta"></div>', '<div class="meta" id="meta"></div>'+spotlight, 1)
maestro=maestro[:start]+maestro[end:]
mast='''<a class="home-skip" href="#board">Skip to chess board</a><div class="home-mast"><h1>♟ Maestro+++ · colorful, musical chess</h1><nav aria-label="Main navigation"><a href="chess-music/">Listen &amp; mix</a><a href="chess-lessons/">Lecture One</a><a href="community/">Players &amp; profiles</a><a href="linux/">Linux downloads</a><a href="#site-extras">All worlds ↓</a></nav></div>'''
maestro=maestro.replace('<body class="maestro-home" data-maestro-landing="1">','<body class="maestro-home" data-maestro-landing="1">'+mast+app,1)
maestro=maestro.replace('<h1>🎼 Chess Maestro <span>·</span> <small style="font-weight:500;color:var(--mut)">Phase 4 — key &amp; harmony from the game</small></h1>','<h2 style="font-size:18px;margin:0">Maestro controls · play, customize &amp; export</h2>',1)
maestro=maestro.replace('<a href="./">← Home</a>', '<a href="#site-extras">All worlds ↓</a>',1)
maestro=maestro.replace("if (maestroParams.get('play') === '1') {", "if (maestroParams.get('play') === '1' || document.body.dataset.maestroLanding === '1') {")
maestro=maestro.replace("if (maestroParams.get('embed') === '1') {", "if(document.body.dataset.maestroLanding==='1'){for(const [id,value] of [['selTheme','brown'],['selPieceW','woodland'],['selPieceB','classic']]){const select=document.getElementById(id);select.value=value;select.dispatchEvent(new Event('change'));}}\nif (maestroParams.get('embed') === '1') {")
maestro=re.sub(r'<script defer src="assets/day-visuals/gallery.js"[^>]*></script>','',maestro)
maestro=maestro.replace('</head>', '''<style>
.home-discoveries{margin-top:18px;display:grid;gap:12px}.home-discoveries h2{font-size:12px;text-transform:uppercase;letter-spacing:.14em;color:var(--mut);margin:0}.discovery{display:block;overflow:hidden;border:1px solid #293550;border-radius:12px;background:linear-gradient(135deg,#101d35,#0a1020);color:var(--ink);text-decoration:none;transition:border-color .15s}.discovery:hover{border-color:var(--accent)}.discovery:focus-visible{outline:3px solid var(--accent);outline-offset:3px}.discovery img{display:block;width:100%;height:132px;object-fit:cover;background:#fff}.discovery-copy{display:grid;gap:7px;padding:13px}.discovery-copy strong{font-size:18px;line-height:1.25}.discovery-copy>span{font-size:12px;line-height:1.5;color:#b9c7df}.discovery-copy .discovery-kicker{font-size:10px;letter-spacing:.09em;color:#e8c170}.discovery-copy .discovery-action{color:var(--accent);font-weight:700}.discovery-lead{border-color:#4b5475}.world-preview{display:flex;align-items:center;justify-content:space-evenly;height:100px;font-size:38px;background:radial-gradient(ellipse at 50% 100%,#23584d,transparent 65%),linear-gradient(135deg,#122943,#231440)}.world-preview span{font-size:55px}@media(max-width:820px){.home-discoveries{grid-template-columns:repeat(3,minmax(0,1fr))}.home-discoveries h2{grid-column:1/-1}.discovery img{height:110px}.discovery-copy strong{font-size:16px}}@media(max-width:560px){.home-discoveries{grid-template-columns:1fr}.discovery img{height:150px}}
.home-mast{max-width:980px;margin:auto;padding:10px 16px 4px}.home-mast h1{font:700 clamp(18px,3vw,24px)/1.2 system-ui;margin:0 0 6px}.home-mast nav{display:flex;flex-wrap:wrap;gap:6px 16px;font-size:13px}.home-mast a{color:var(--accent);text-decoration:none}.maestro-home .app{padding-bottom:10px}.maestro-home .top{padding-top:16px}.home-skip{position:absolute;top:-100px;left:10px;z-index:20;padding:10px;background:var(--panel);color:var(--ink)}.home-skip:focus{top:10px}#site-extras{display:block;margin-top:26px}#board{scroll-margin-top:8px}.home-mast a:focus-visible{outline:3px solid #c060ff;outline-offset:3px}
</style></head>''',1)
maestro=maestro.replace('</body>',extras+'</body>',1)
maestro=maestro.replace('<title>Chess Maestro — relaxation-labeling chess, scored as music</title>','<title>Maestro+++ — play colorful, musical chess | Manny Glover</title>')
(ROOT/'index.html').write_text(maestro)
print('Homepage built: native full Maestro first; preserved site directory below.')
