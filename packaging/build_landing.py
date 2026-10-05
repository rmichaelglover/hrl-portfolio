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
maestro=maestro[:start]+maestro[end:]
mast='''<a class="home-skip" href="#board">Skip to chess board</a><div class="home-mast"><h1>♟ Maestro · colorful, musical chess</h1><nav aria-label="Main navigation"><a href="chess-music/">Listen &amp; mix</a><a href="chess-lessons/">Lecture One</a><a href="community/">Players &amp; profiles</a><a href="linux/">Linux downloads</a><a href="#site-extras">All worlds ↓</a></nav></div>'''
maestro=maestro.replace('<body class="maestro-home" data-maestro-landing="1">','<body class="maestro-home" data-maestro-landing="1">'+mast+app,1)
maestro=maestro.replace('<h1>🎼 Chess Maestro <span>·</span> <small style="font-weight:500;color:var(--mut)">Phase 4 — key &amp; harmony from the game</small></h1>','<h2 style="font-size:18px;margin:0">Maestro controls · play, customize &amp; export</h2>',1)
maestro=maestro.replace('<a href="./">← Home</a>', '<a href="#site-extras">All worlds ↓</a>',1)
maestro=maestro.replace("if (maestroParams.get('play') === '1') {", "if (maestroParams.get('play') === '1' || document.body.dataset.maestroLanding === '1') {")
maestro=maestro.replace("if (maestroParams.get('embed') === '1') {", "if(document.body.dataset.maestroLanding==='1'){for(const [id,value] of [['selTheme','blue'],['selPieceW','woodland'],['selPieceB','classic']]){const select=document.getElementById(id);select.value=value;select.dispatchEvent(new Event('change'));}}\nif (maestroParams.get('embed') === '1') {")
maestro=re.sub(r'<script defer src="assets/day-visuals/gallery.js"[^>]*></script>','',maestro)
maestro=maestro.replace('</head>', '''<style>
.home-mast{max-width:980px;margin:auto;padding:10px 16px 4px}.home-mast h1{font:700 clamp(18px,3vw,24px)/1.2 system-ui;margin:0 0 6px}.home-mast nav{display:flex;flex-wrap:wrap;gap:6px 16px;font-size:13px}.home-mast a{color:#1560a3;text-decoration:none}.maestro-home .app{padding-bottom:10px}.maestro-home .top{padding-top:16px}.home-skip{position:absolute;top:-100px;left:10px;z-index:20;padding:10px;background:#fff}.home-skip:focus{top:10px}#site-extras{display:block;margin-top:26px}#board{scroll-margin-top:8px}.home-mast a:focus-visible{outline:3px solid #c060ff;outline-offset:3px}
</style></head>''',1)
maestro=maestro.replace('</body>',extras+'</body>',1)
maestro=maestro.replace('<title>Chess Maestro — relaxation-labeling chess, scored as music</title>','<title>Maestro — play colorful, musical chess | Manny Glover</title>')
(ROOT/'index.html').write_text(maestro)
print('Homepage built: native full Maestro first; preserved site directory below.')
