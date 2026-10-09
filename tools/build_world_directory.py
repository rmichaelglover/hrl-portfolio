"""Inventory public entry pages and keep the front-page directory complete."""
from pathlib import Path
from html.parser import HTMLParser
from html import escape
import json
import re
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parents[1]
GROUPS = ['Worlds & Nature','Chess & Games','Music & Art','Science & Tools','Words & Faith','Writing & Research','Community']
MAP = {
 'Worlds & Nature': 'tiny-creek-world tiny-creek-chess worlds-of-kings worlds-of-kings-earth worlds-of-kings-fusion worlds-of-kings-wildlife fair-oaks lion-and-the-lamb genesis emoji-life humanity-atlas st-james atlanta',
 'Chess & Games': 'chess whimsy-chess capture-tutor chess-biometric chess-brain chess-mind chess-lessons chess-logic chess-premove chess-relaxation ultrabullet-lessons open-chess-brain relaxed-chess-brain relaxfish magnum-chessicus super-monkey-chessballs lichess-emulator catfish-lane',
 'Music & Art': 'we-follows chess-music hrlized wave-worlds mk-ultrabullet cover-songs floating-guitar elbies-world',
 'Words & Faith': 'bible-hrl easy-bible-reader ecc-plus wikimrgrele gospel mother-god-shrine',
 'Community': 'community fair-oaks education-pathways gay-georgia chronology cv linux terms licensing',
 'Writing & Research': 'all-in-a-days-work attack-on-christendom chesshustlagaard drugs-are-good el-cuento essays hrl-cybersecurity hyperspace i-am-what-i-am magnum-economicus magnum-quantreleviathone manuelian-magnum-opus mother-god-bomb no-panzer numerological-speculations perfect-union political-economy-paper projective-horizon-bipolar red-thread relax-relabel research-whitepapers spreadsheet-dissertation the-wall three-white-papers ujewhale-macro-report virtual-body-cancer white-hat-hackers',
}
OVERRIDES = {
 'oort-halo/': ('Oort Cloud & Galactic Halo','Compare three gravitational toy models: central mass, outer shell, and extended halo. Plots, assumptions, and reproducible Python code.','Science & Tools'),
 'whimsy-chess/stalemate-gambit/': ('The Stalemate Gambit Explained','Seven playful chapters, four interactive lessons, a wandering king, and a portable study PGN.','Chess & Games'),
 'tiny-creek-world/': ('Tiny Creek World','Travel a peaceful world garden, meet wildlife neighbors, make gifts, and collect little welcomes.','Worlds & Nature'),
 'tiny-creek-chess/': ('Tiny Creek Chess','Learn chess with nature councils, animal friends, country flags, and classical figurines.','Worlds & Nature'),
 'worlds-of-kings/': ('Worlds of Kings · Original','Play the three-country local hotseat game: ocean crossings, alliances, and vanishing armies.','Worlds & Nature'),
 'worlds-of-kings-earth/': ('Worlds of Kings · Earth Atlas','Explore real countries, provinces, cities, ocean spaces, and candidate chess routes.','Worlds & Nature'),
 'worlds-of-kings-fusion/': ('Worlds of Kings · Fusion','Play experimental local hotseat matches across real geography, with ocean promotion and a separate saved game.','Worlds & Nature'),
 'worlds-of-kings-wildlife/': ('Worlds of Kings · Emoji Wilds','A separate playable Earth edition with wildlife pieces, country palettes, and optional classical figurines.','Worlds & Nature'),
 'fair-oaks/world/': ('Fair Oaks World','Walk a first-person voxel landscape of oak rings, micro-schools, and groves.','Worlds & Nature'),
 'lion-and-the-lamb/': ('The Lion and the Lamb','Explore an imagined coexistence landscape of human places, living buffers, and wildlife.','Worlds & Nature'),
 'lion-and-the-lamb/world/': ('The Lion and the Lamb · World Atlas','Explore mapped geography and population averages beneath an imagined coexistence scenario.','Worlds & Nature'),
 'genesis/isles/': ('Floating Isles','Watch a levitating archipelago grow through skyfalls, groves, lanterns, and a festival.','Worlds & Nature'),
 'genesis/reef/': ('The Deep Reef','Descend into an ASCII voxel ocean of coral, kelp, jellyfolk, and bioluminescent life.','Worlds & Nature'),
 'genesis/terraform/': ('Terraformer','Grow a cold rock into a world with seas, twin suns, blooms, and wandering creatures.','Worlds & Nature'),
 'genesis/maestro/playworld.html': ('Maestro · Playworld','Enter the chess game as a playable voxel landscape.','Chess & Games'),
 'genesis/maestro/': ('Maestro · Voxel Chess','Replay chess as a three-dimensional world, with Minecraft and Roblox exports.','Chess & Games'),
 'whimsy-chess/riverbank/': ('The Last Ferry','Solve a three-jump riverbank chess puzzle.','Chess & Games'),
 'whimsy-chess/storybook/': ('Chess Storybook','Two narrated chess adventures with the Woodland cast.','Chess & Games'),
 'elbies-world/music.html': ("Elbie’s World · Music",'Explore music in Elbie’s world.','Music & Art'),
 'formula-time-v2.html': ('Formula Time','Explore chess, relaxation, and silver-marble equations.','Science & Tools'),
 'relaxed-chess-brain/arena.html': ('Relaxed Chess Brain · Arena','Visit the chess brain’s interactive arena.','Chess & Games'),
}
EXTRA = ['genesis/critter/conway.html','genesis/critter/chess-life.html','genesis/maestro/playworld.html','genesis/maestro/emoji.html','genesis/maestro/cyber.html','whimsy-chess/maestro.html','whimsy-chess/novella/reader.html','elbies-world/music.html','formula-time-v2.html','relaxed-chess-brain/arena.html','bible-hrl/explorer.html','bible-hrl/relaxation.html','bible-hrl/scatter.html','bible-hrl/tensor.html','bible-hrl/simplex.html','bible-hrl/trajectories.html','ujewhale-macro-report/interactive.html']

class Page(HTMLParser):
 def __init__(self):
  super().__init__(); self.title=''; self.description=''; self.in_title=False; self.links=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='title':self.in_title=True
  if tag=='meta' and a.get('name')=='description':self.description=a.get('content','')
  if tag=='a' and 'href' in a:self.links.append(a['href'])
 def handle_endtag(self,tag):
  if tag=='title':self.in_title=False
 def handle_data(self,text):
  if self.in_title:self.title+=text

home=ROOT/'index.html'
before=home.read_text()
old=Page(); old.feed(before)
old_paths={unquote(urlsplit(h).path).removeprefix('/hrl-portfolio/') for h in old.links}
paths=[]
for path in ROOT.rglob('index.html'):
 relative=path.relative_to(ROOT)
 if path==home or any(p in {'.git','assets','packaging','server','tests','_layouts'} for p in relative.parts):continue
 if relative.parts[0]=='king-me-bitch':continue # neutral archive notice, not a world
 paths.append((path,str(relative.parent)+'/'))
paths.extend((ROOT/h,h) for h in EXTRA)
entries=[]
for path,href in paths:
 assert path.is_file(),href
 page=Page();page.feed(path.read_text())
 title=re.sub(r'\s+',' ',page.title).strip()
 title=re.split(r'\s+[|·—]\s+',title)[0]
 category=next((g for g,roots in MAP.items() if href.split('/')[0] in roots.split()),'Science & Tools')
 description=re.sub(r'\s+',' ',page.description).strip()
 if not description:description=f'Open {title} and explore its pages, ideas, and interactive features.'
 if len(description)>230:description=description[:227].rsplit(' ',1)[0]+'…'
 title,description,category=OVERRIDES.get(href,(title,description,category))
 entries.append(dict(href=href,title=title,description=description,category=category))
priority=list(OVERRIDES)
entries.sort(key=lambda e:(priority.index(e['href']) if e['href'] in priority else len(priority),e['title'].lower()))
assert len({e['href'] for e in entries})==len(entries)
(ROOT/'world-directory.json').write_text(json.dumps(entries,ensure_ascii=False,indent=2)+'\n')
missing=[e for e in entries if e['href'] not in old_paths]

featured=['tiny-creek-world/','worlds-of-kings-fusion/','fair-oaks/world/','lion-and-the-lamb/world/','genesis/isles/','genesis/reef/']
icons=['🌱','♜','🌳','🦁','🏝️','🪸']
parts=['<!-- world-directory:start -->', '<section class="home-worlds" id="world-directory" aria-labelledby="world-directory-title">',
 '<div class="world-section-heading"><div><p class="world-eyebrow">ONE PORTFOLIO · MANY OPEN DOORS</p><h2 id="world-directory-title">Find your next world.</h2><p>Walk a garden, cross an ocean, follow a king, or step into a laboratory.</p></div><a href="#world-search">Search all worlds ↓</a></div>',
 '<div class="world-featured">']
for href,icon in zip(featured,icons):
 e=next(e for e in entries if e['href']==href)
 parts.append(f'<a class="world-feature" href="{escape(href)}"><span class="world-art" aria-hidden="true">{icon}</span><span class="world-feature-copy"><strong>{escape(e["title"])}</strong><span>{escape(e["description"])}</span><b>Enter this world ↗</b></span></a>')
parts+=['</div>', '<div class="world-find"><label for="world-search">Search worlds, games &amp; projects</label><div class="world-search-row"><input id="world-search" type="search" placeholder="Try wildlife, chess, music, reef…" autocomplete="off"><button type="button" id="world-clear">Clear</button></div></div>',
 '<div class="world-filters" role="group" aria-label="Filter by interest"><button type="button" data-category="All" aria-pressed="true">All</button>']
for group in GROUPS:parts.append(f'<button type="button" data-category="{escape(group)}" aria-pressed="false">{escape(group)}</button>')
parts+=['</div>',f'<p id="world-count" role="status">{len(entries)} doors to explore.</p>', '<div id="world-links" class="world-links">']
for e in entries:
 parts.append(f'<a href="{escape(e["href"])}" data-category="{escape(e["category"])}"><span class="world-category">{escape(e["category"])}</span><strong>{escape(e["title"])}</strong><span class="world-description">{escape(e["description"])}</span><span class="world-go">Open ↗</span></a>')
parts+=['</div>','<p id="world-empty" hidden>No worlds match yet. Try another word or choose All.</p>', '<button type="button" id="world-more" hidden>Show more worlds</button>', '<p class="world-archive-link">Looking for the original portfolio showcases? <a href="#site-extras">Browse the full archive ↓</a></p>', '</section>', '<!-- world-directory:end -->']
block='\n'.join(parts)
if '<!-- world-directory:start -->' in before:
 after=re.sub(r'<!-- world-directory:start -->.*?<!-- world-directory:end -->',lambda _:block,before,flags=re.S)
else:
 marker='  <div class="top">\n    <h2 style="font-size:18px;margin:0">Maestro controls'
 assert marker in before
 after=before.replace(marker,block+'\n\n'+marker,1)
home.write_text(after)
report='# Front-page world access audit\n\n'
report+=f'{len(entries)} public entry pages are now directly linked from the landing page. '
report+='The directory includes independent worlds, individual Genesis biomes, study and game modes, laboratories, reading tools, and research portals. Archive notices, test harnesses, and alternate obsolete renderers are excluded.\n\n'
report+='Six featured world cards sit above the directory. The landing-page discovery column also features the Stalemate Gambit study and direct access to the Tiny Creek and Worlds of Kings families.\n\n'
report+='Run `python3 tools/build_world_directory.py` when adding an entry page. It scans public `index.html` pages, adds selected standalone experiences, validates destinations, and regenerates the static HTML and JSON inventory. Search and category controls progressively enhance those native links.\n\n'
report+='## Directory coverage\n\n'
for group in GROUPS:report+=f'- {group}: {sum(e["category"]==group for e in entries)} entries.\n'
report+='\nEvery inventory destination exists on disk. Live publication and browser interactions are checked separately.\n'
(ROOT/'tools/WORLD-ACCESS-AUDIT.md').write_text(report)
print(f'Linked {len(entries)} public entries; {len(missing)} lacked an exact front-page entry link before this generation.')
print('Previously missing:',', '.join(e['href'] for e in missing))
