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
spotlight = (ROOT/'packaging/homepage/discoveries.html').read_text()
app=app.replace('<div class="boardcol">', '<div class="boardcol"><p class="home-board-hint">Your move. Click a piece, pick a square, make it sing.</p>', 1)
app=app.replace('<div class="meta" id="meta"></div>', '<div class="meta" id="meta"></div>'+spotlight, 1)
maestro=maestro[:start]+maestro[end:]
mast='''<a class="home-skip" href="#board">Skip to chess board</a><div class="home-mast"><h1>♟ Maestro+++ <small>Chess. Music. A little magic.</small></h1><nav aria-label="Main navigation"><a href="chess-music/">Music</a><a href="chess-lessons/">Learn chess</a><a href="community/">Meet the players</a><a href="linux/">Get the app</a><a href="#site-extras">All worlds ↓</a></nav></div>'''
maestro=maestro.replace('<body class="maestro-home" data-maestro-landing="1">','<body class="maestro-home" data-maestro-landing="1">'+mast+app,1)
maestro=maestro.replace('<h1>🎼 Chess Maestro <span>·</span> <small style="font-weight:500;color:var(--mut)">Phase 4 — key &amp; harmony from the game</small></h1>','<h2 style="font-size:18px;margin:0">Maestro controls · play, customize &amp; export</h2>',1)
maestro=maestro.replace('<a href="./">← Home</a>', '<a href="#site-extras">All worlds ↓</a>',1)
maestro=maestro.replace("if (maestroParams.get('play') === '1') {", "if (maestroParams.get('play') === '1' || document.body.dataset.maestroLanding === '1') {")
maestro=maestro.replace("if (maestroParams.get('embed') === '1') {", "if(document.body.dataset.maestroLanding==='1'){for(const [id,value] of [['selTheme','brown'],['selPieceW','woodland'],['selPieceB','classic']]){const select=document.getElementById(id);select.value=value;select.dispatchEvent(new Event('change'));}}\nif (maestroParams.get('embed') === '1') {")
maestro=re.sub(r'<script defer src="assets/day-visuals/gallery.js"[^>]*></script>','',maestro)
maestro=maestro.replace('</head>', '<style>'+ (ROOT/'packaging/homepage/style.css').read_text()+'</style></head>', 1)
quick_actions = '''<script>
const quick=document.createElement('div');quick.className='home-quick-actions';quick.setAttribute('aria-label','Play and listen');
for(const id of ['btnMusic','btnNewGame'])quick.append(document.getElementById(id));
document.getElementById('narr').after(quick);
const story=document.querySelector('.storybook-commentary');if(story)story.open=false;
for(const [id,label] of [['first','⏮ Start'],['prev','◀ Back'],['play','▶ Replay'],['next','Next ▶'],['last','End ⏭']])document.getElementById(id).textContent=label;
</script>'''
maestro=maestro.replace('</body>',quick_actions+extras+'</body>',1)
maestro=maestro.replace('<title>Chess Maestro — relaxation-labeling chess, scored as music</title>','<title>Maestro+++ — play colorful, musical chess | Manny Glover</title>')
(ROOT/'index.html').write_text(maestro)
print('Homepage built: native full Maestro first; preserved site directory below.')
