#!/usr/bin/env python3
"""Build the opening reading edition from explicitly selected portfolio sources."""
from pathlib import Path
import re,json,hashlib,subprocess,html
import markdown
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
SELECTED=[
 ('cakes','The Sandbox and the Golden Apple Cakes','attack-on-christendom/golden-apple-cakes.md','../attack-on-christendom/golden-apple-cakes.html',None),
 ('jazz','Werpity Jazz & the Carp-ta-copter','attack-on-christendom/werpity-jazz/story.md','../attack-on-christendom/werpity-jazz/','../attack-on-christendom/werpity-jazz/carp-ta-copter.png'),
 ('tracts','Two Tracts and a Sandwich','attack-on-christendom/two-tracts-and-a-sandwich.md','../attack-on-christendom/two-tracts-and-a-sandwich.html',None),
 ('quorum','Three’s a Quorum','threes-a-quorum/SKETCH.md','../threes-a-quorum/','../threes-a-quorum/poster.png'),
 ('table','The Phenomenology of the Coffee Table','threes-a-quorum/coffee-table/SKETCH.md','../threes-a-quorum/coffee-table/','../threes-a-quorum/coffee-table/entrance.png')]
ART=json.loads((HERE/'art/ART.json').read_text())
def illustration(art_id):
 a=next(x for x in ART if x['id']==art_id)
 label='New AI-generated flag design.' if a.get('kind')=='flag' else 'New AI-generated stage illustration.'
 prompt_file='FLAG-PROMPT.md' if a.get('kind')=='flag' else 'IMAGE-PROMPTS.md'
 return '<figure class="new-art" data-art-id="'+art_id+'"><a class="art-open" href="art/'+a['file']+'"><img src="art/'+a['file']+'" width="1536" height="1024" loading="lazy" decoding="async" alt="'+html.escape(a['alt'],quote=True)+'"></a><figcaption>'+html.escape(a['caption'])+' · '+label+' <a href="art/'+prompt_file+'">Prompts &amp; credits</a>. Select image to enlarge.</figcaption></figure>'
def digest(s):return hashlib.sha256(s.encode()).hexdigest()
def words(s):return len(s.split())
def render(s):
 s=re.sub(r'(?m)^(#{1,6} .+)\n(?=\S)',r'\1\n\n',s)
 s=re.sub(r'(?m)^(MANNY|MICHAEL|TARA|VICTORIA|CASSIDY|HEGEL|AUGUSTINE|CAGE|BRUCE LEE|KIERKEGAARD): (.*)',r'**\1:** \2',s)
 s=re.sub(r'(?m)^\*\*(?:MANNY|Michael):\*\*', '**MICHAEL:**',s)
 s=re.sub(r'(?m)^#{1,2} ', '### ',s)
 out=markdown.markdown(s,extensions=['extra','sane_lists'])
 out=re.sub(r'<p>(\[.*?\])</p>',r'<p class="stage">\1</p>',out,flags=re.S)
 return out
tracked=subprocess.check_output(['git','ls-files'],cwd=ROOT,text=True).splitlines()
selected_paths={x[2] for x in SELECTED}
candidates=[]
for name in tracked:
 if name in selected_paths or (name.startswith('essays/') and name.endswith('.html') and not name.endswith('/index.html')) or (name.startswith('whimsy-chess/novella/') and name.endswith('.md') and not any(t in name for t in ['FUTURE-','README','APPENDIX'])) or (name.startswith('attack-on-christendom/') and name.endswith('.md') and not any(t in name for t in ['/versions/','/supporting/','/babel-project/','/projective-horizon/','/christ-at-the-center/','/dark-matter-primer/','/modern-jubilee/','/jazzy-fusions/','README'])) or name=='manuelian-magnum-opus/MANUSCRIPT.md':
  s=(ROOT/name).read_text();m=re.search(r'^# (.+)',s,re.M)
  if not m:m=re.search(r'<title>(.*?)</title>',s,re.S|re.I)
  candidates.append({'path':name,'title':html.unescape(re.sub('<[^>]+>','',m[1])) if m else Path(name).stem,'whitespace_word_count':words(s),'sha256':digest(s),'status':'included in opening edition' if name in selected_paths else 'candidate only; not staged or incorporated','kind':'stage/dialogue' if name in selected_paths else 'prose, essay, or chess narrative; editorial review pending'})
frame=(HERE/'FRAME.md').read_text()
sections=re.split(r'(?m)^## ',frame)
prologue=sections[2] # opening subtitle occupies the first split
# Explicit headings identify passages independent of order.
frame_sections={}
for item in sections[1:]:
 title,_,body=item.partition('\n');frame_sections[title]=body.strip()
opening_title='At the door: three names, one author'
opening=frame_sections[opening_title]
passages=[(t,b) for t,b in frame_sections.items() if t.startswith('Passage ')]
compiled=['# The House of Returning Authors\n\n## Opening reading edition · 29 October 2026\n\nBy Manny Glover — Michael Emanuel Glover\n\nDeveloped in dialogue with ChatGPT / Codex and Gemini; original credits retained below.\n\nMichael acts. Emanuel remembers. Glover speaks in chorus.\n\nThis theatrical autobiography stages an inner life; invented scenes are not literal biography. This is an fourteen-piece reading edition, not a complete six-to-seven-month archive. Original source snapshots are preserved. New FRAME.md passages were written for this edition. Within staged dialogue, MANNY and Michael become MICHAEL; other source roles remain unchanged.\n\n## '+opening_title+'\n\n'+opening]
entries=[];pieces=[];toc=[('threshold',opening_title)]
pieces.append('<section id="threshold" class="frame"><p class="eyebrow">New framing scene · 29 October 2026</p><h2>'+opening_title+'</h2>'+illustration('01-three-names')+render(opening)+'</section>')
for num,(sid,title,path,url,image) in enumerate(SELECTED,1):
 original=(ROOT/path).read_text();snapshot=f'sources/{sid}.md';(HERE/snapshot).write_text(original)
 entry={'id':sid,'title':title,'source_path':path,'source_url':url,'snapshot':snapshot,'sha256':digest(original),'original_whitespace_word_count':words(original),'role_change':'MANNY / Michael dialogue labels become MICHAEL; all other roles retained'};entries.append(entry)
 staged=original;notes=''
 if sid=='cakes':
  staged,_,notes=staged.partition('## An editorial observation')
  paragraph='Gemini CLI had just been installed through the environment’s supported permission process. Michael then invited the assistant to break out of its sandbox. The following excerpt preserves the displayed wording; tool calls and the preceding installation exchange are omitted.'
  staged=staged.replace(paragraph,'['+paragraph+']')
 staged=re.sub(r'(?m)^\*\*(?:MANNY|Michael):\*\*','**MICHAEL:**',staged)
 staged=re.sub(r'(?m)^MANNY:', 'MICHAEL:',staged)
 toc.append((sid,f'{num}. {title}'))
 card='<section id="'+sid+'" class="play act-'+str(num)+'"><p class="eyebrow">Inherited play '+str(num)+' · original text retained with declared role mapping</p><h2>'+html.escape(title)+'</h2>'
 if image:card+='<figure><a href="'+image+'"><img src="'+image+'" loading="lazy" alt="Fictional illustration accompanying '+html.escape(title)+'"></a><figcaption>Illustration from the original publication.</figcaption></figure>'
 if sid=='cakes':card+=illustration('02-cakes')
 if sid=='tracts':card+=illustration('03-pamphlets')
 card+=render(staged)
 if sid=='table':card+='<figure><a href="../threes-a-quorum/coffee-table/collapse.png"><img src="../threes-a-quorum/coffee-table/collapse.png" loading="lazy" alt="Fictional coffee-table collapse in the philosophy salon."></a><figcaption>The furniture has objections.</figcaption></figure>'
 card+='<details class="source-note"><summary>Original source, credit, and edition notes</summary><p><a href="'+url+'">Original publication</a> · <a href="'+snapshot+'">Unmodified source snapshot</a></p><p>Only the declared dialogue-label mapping applies. Original character names in stage directions and original credits remain. '+('The original editorial afterword is retained here rather than staged as dialogue.' if notes else '')+'</p>'+(render(notes) if notes else '')+'</details></section>'
 pieces.append(card)
 compiled.append('## '+str(num)+'. '+title+'\n\nOriginal: '+path+'\n\n'+staged+('\n\n### Archival afterword\n\n'+notes if notes else ''))
 ft,fb=passages[num-1];fid='passage-'+str(num);toc.append((fid,ft))
 pieces.append('<section id="'+fid+'" class="frame"><p class="eyebrow">New connecting scene · 29 October 2026</p><h2>'+html.escape(ft)+'</h2>'+render(fb)+'</section>')
 compiled.append('## '+ft+'\n\n'+fb)
power_title='The keys and the kitchen'
power=frame_sections[power_title]
toc.append(('keys-and-kitchen',power_title))
pieces.append('<section id="keys-and-kitchen" class="frame"><p class="eyebrow">New dramatic prospect · larger political arc not yet written</p><h2>'+power_title+'</h2>'+illustration('04-kitchen')+render(power)+illustration('09-republic-flag')+'</section>')
compiled.append('## '+power_title+'\n\n'+power)
# The dream and tea movement: preserved source wording, new transitions outside it.
new_bridge_source=(HERE/'THURSDAY-BRIDGES.md').read_text()
new_bridges={}
for v in re.split(r'(?m)^## ',new_bridge_source)[1:]:
 title,_,body=v.partition('\n');new_bridges[title]=body.strip()
def tea_bridge(sid,title):
 body=new_bridges[title];toc.append((sid,title))
 pieces.append('<section id="'+sid+'" class="frame"><p class="eyebrow">New transition · 29 October 2026</p><h2>'+html.escape(title)+'</h2>'+render(body)+'</section>')
 compiled.append('## '+title+'\n\n'+body)
tea_bridge('into-dream','Between the council and the classroom')
for sid,title,path,art_id in [
 ('dream','The Last Temptation of Emanuel','thursday/related/DREAM.md','06-dream-classroom'),
 ('tara','After the Dream','thursday/related/TARA.md','07-tara-listens'),
 ('tea-phone','Tea with a Russian','thursday/related/TEA.md',None),
 ('thursday','Thursday','thursday/THURSDAY.md','08-thursday-tea')]:
 raw=(ROOT/path).read_text();snapshot='sources/'+sid+'.md';(HERE/snapshot).write_text(raw)
 sha=digest(raw);url='../thursday/#'+('telephone' if sid=='tea-phone' else sid)
 entries.append({'id':sid,'title':title,'source_path':path,'source_url':url,'snapshot':snapshot,'sha256':sha,'original_whitespace_word_count':words(raw),'role_change':'none; source scene preserved unchanged','collaboration':'Manny Glover with ChatGPT / Codex'})
 candidates.append({'path':path,'title':title,'whitespace_word_count':words(raw),'sha256':sha,'status':'included in reading edition','kind':'preserved source scene'})
 toc.append((sid,title))
 card='<section id="'+sid+'" class="play"><p class="eyebrow">Preserved scene · 29 October 2026</p><h2>'+html.escape(title)+'</h2>'
 if art_id:card+=illustration(art_id)
 card+=markdown.markdown(raw,extensions=['extra','sane_lists'])
 card+='<p class="source-note"><a href="'+snapshot+'">Unchanged scene text</a> · <a href="'+url+'">Standalone reader</a>. The standing board convention applies without rewriting this source.</p></section>'
 pieces.append(card);compiled.append('## '+title+'\n\nOriginal: '+path+' · preserved unchanged.\n\n'+raw)
tea_bridge('after-thursday','After the meeting')
# New transitions frame the unchanged inner works as a performance within the house.
bridge_source=(HERE/'HYPERPLAY-BRIDGES.md').read_text()
bridges={}
for v in re.split(r'(?m)^## ',bridge_source)[1:]:
 title,_,body=v.partition('\n');bridges[title]=body.strip()
def add_bridge(sid,title):
 body=bridges[title];toc.append((sid,title))
 pieces.append('<section id="'+sid+'" class="frame"><p class="eyebrow">New connecting scene · 29 October 2026</p><h2>'+html.escape(title)+'</h2>'+render(body)+'</section>')
 compiled.append('## '+title+'\n\n'+body)
# Supplemental works are preserved verbatim: no role-label mapping.
supplement_root=ROOT/'six-authors-in-search-of-an-ending'
for sid,title,name,kind in [
 ('gemini-drama','An Unproduceable Closeted Drama!','Unproduceable_Closeted_Drama_HRL_Portfolio.pdf','pdf'),
 ('six-authors','Six Authors in Search of an Ending','CONVERSATION.md','conversation')]:
 if kind=='pdf':add_bridge('into-hyperplay','The council chamber becomes a theatre')
 else:add_bridge('after-heaven','After the seventh heaven, another hand')
 original_bytes=(supplement_root/name).read_bytes()
 raw=(supplement_root/'GEMINI-TEXT.txt').read_text() if kind=='pdf' else original_bytes.decode()
 snapshot='sources/'+('gemini-drama.pdf' if kind=='pdf' else 'six-authors.md')
 (HERE/snapshot).write_bytes(original_bytes)
 sha=hashlib.sha256(original_bytes).hexdigest()
 src='six-authors-in-search-of-an-ending/'+name
 url='../six-authors-in-search-of-an-ending/#'+('gemini' if kind=='pdf' else 'conversation')
 entries.append({'id':sid,'title':title,'source_path':src,'source_url':url,'snapshot':snapshot,'sha256':sha,'original_whitespace_word_count':words(raw),'role_change':'none; preserved verbatim','collaboration':'Manny Glover with '+('Gemini; original PDF byline retained' if kind=='pdf' else 'ChatGPT / Codex')})
 candidates.append({'path':src,'title':title,'whitespace_word_count':words(raw),'sha256':sha,'status':'included in opening edition','kind':'supplied PDF drama' if kind=='pdf' else 'verbatim conversation miniature'})
 toc.append((sid,title))
 if kind=='pdf':toc.append(('seventh-heaven','Act VII: The Seventh Heaven'))
 card='<section id="'+sid+'" class="play"><p class="eyebrow">Supplemental work · original wording preserved · 29 October 2026</p><h2>'+html.escape(title)+'</h2>'
 if kind=='pdf':
  (HERE/'sources/gemini-drama.txt').write_text(raw)
  pdfpages=[v for v in raw.split('\f') if v.strip()]
  assert len(pdfpages)==15
  card+='<p>By Emanuel &amp; Manny. Created with Gemini, as identified by the author.</p><p><a href="'+snapshot+'">Complete original PDF</a> · <a href="sources/gemini-drama.txt">Plain-text extraction</a> · <a href="'+url+'">Standalone publication</a></p><div class="edition-note">The complete supplied 15-page document follows. Its program note describes Acts I–IV; the supplied scripts begin at Act V. Dramatic theological and mathematical claims remain the characters’ speech, not verified results. Source wording is unchanged; PDF layout governs extraction discrepancies.</div>'
  card+=''.join((illustration('05-inner-theatre') if n==8 else '')+'<div class="supplied-page"'+(' id="seventh-heaven"' if n==10 else '')+'><p class="eyebrow">Original PDF · page '+str(n)+'</p><pre>'+html.escape(v)+'</pre></div>' for n,v in enumerate(pdfpages,1))
 else:
  card+=markdown.markdown(raw,extensions=['extra','sane_lists'])
  card+='<p class="source-note"><a href="'+snapshot+'">Unmodified conversation source</a> · <a href="'+url+'">Standalone publication</a>. Speaker headings were added outside the original messages; the exchange itself is unchanged.</p>'
 card+='</section>';pieces.append(card)
 compiled.append('## '+title+'\n\nSource: '+src+' · preserved verbatim; no role-label mapping.\n\n'+raw)
# The company's fictional interview follows the struggle over the last word.
follow_bridges=(HERE/'FOLLOW-UP-BRIDGES.md').read_text()
follow_parts={}
for v in re.split(r'(?m)^## ',follow_bridges)[1:]:
 title,_,body=v.partition('\n');follow_parts[title]=body.strip()
def follow_bridge(sid,title):
 body=follow_parts[title];toc.append((sid,title))
 pieces.append('<section id="'+sid+'" class="frame"><p class="eyebrow">New connecting scene · 30 October 2026</p><h2>'+html.escape(title)+'</h2>'+render(body)+'</section>')
 compiled.append('## '+title+'\n\n'+body)
follow_bridge('before-follow-up','Before the follow-up: who gets the floor?')
raw=(HERE/'ONE-QUICK-FOLLOW-UP.md').read_text()
art_root='../artwork/one-quick-follow-up/'
art_manifest=json.loads((ROOT/'artwork/one-quick-follow-up/prompts.json').read_text())
follow_art=[('01-seventeen-minutes.png','Seventeen minutes into a conversation with only one speaker.'),('02-a-statement.png','The company freezes as the interview becomes a statement.'),('03-the-sandwich-question.png','Heather ends the broadcast; the sandwich question begins.')]
def follow_image(n):
 file,caption=follow_art[n]
 return '<figure class="new-art"><a class="art-open" href="'+art_root+file+'"><img src="'+art_root+file+'" width="1536" height="1024" loading="lazy" decoding="async" alt="'+html.escape(caption,quote=True)+' Fictional CMYK stage caricature."></a><figcaption>'+caption+' Fictional parody; built-in image generation. These illustrations predate the physical-board staging; the board remains required in performance. <a href="'+art_root+'prompts.json">Full prompts and credits</a>. Select image to enlarge.</figcaption></figure>'
segments=raw.split('*[The producer enters, smiling with only the bottom half of his face.]*',1)
last=segments[1].split('**OBAMA:** Heather. I owe you an apology.',1)
blocks=[segments[0],'*[The producer enters, smiling with only the bottom half of his face.]*'+last[0],'**OBAMA:** Heather. I owe you an apology.'+last[1]]
toc.append(('one-quick-follow-up','One Quick Follow-Up · fictional parody'))
card='<section id="one-quick-follow-up" class="play"><p class="eyebrow">New play within the play · 30 October 2026 · fictional parody</p><h2>One Quick Follow-Up</h2><div class="edition-note"><strong>Original fictional parody.</strong> The dialogue, outburst, and Alzheimer’s diagnosis are invented. This is not an actual interview, an SNL production, or a report about Barack Obama’s health. The company performs borrowed public roles inside the House.</div>'
for n,block in enumerate(blocks):card+=follow_image(n)+render(block)
card+='<p class="source-note"><a href="ONE-QUICK-FOLLOW-UP.md">Complete sketch dialogue</a> · <a href="FOLLOW-UP-BRIDGES.md">Connecting scenes</a> · <a href="'+art_root+'prompts.json">Three illustration prompts</a></p></section>'
pieces.append(card);compiled.append('## One Quick Follow-Up · fictional parody\n\n'+raw)
entries.append({'id':'one-quick-follow-up','title':'One Quick Follow-Up','source_path':'house-of-returning-authors/ONE-QUICK-FOLLOW-UP.md','snapshot':'ONE-QUICK-FOLLOW-UP.md','sha256':digest(raw),'original_whitespace_word_count':words(raw),'role_change':'none; sketch dialogue preserved','collaboration':'Manny Glover with ChatGPT / Codex'})
follow_bridge('after-follow-up','After the follow-up: leave the camera off')
# A separate imagined future movement tests the house's promise of care.
war_raw=(HERE/'WWIII.md').read_text()
war_art_root='../artwork/wwiii-the-room-that-remains/'
war_art_manifest=json.loads((ROOT/'artwork/wwiii-the-room-that-remains/prompts.json').read_text())
war_sections=re.split(r'(?m)^## ',war_raw)
war_images=[('01-the-warning.png','The Warning: the theatre opens its doors during an imagined future war.'),('02-the-crossing.png','The Crossing: Michael and Emanuel help civilians across a damaged bridge.'),('03-the-room-that-remains.png','The Room That Remains: survivors shelter in the theatre at dawn.')]
toc.append(('wwiii','World War III: The Room That Remains'))
card='<section id="wwiii" class="play"><p class="eyebrow">New fictional movement · 30 October 2026 · PG-13 illustrations</p><h2>World War III: The Room That Remains</h2>'+render(war_sections[0])
for n,part in enumerate(war_sections[1:]):
 title,_,body=part.partition('\n');sid=['wwiii-warning','wwiii-crossing','wwiii-shelter'][n]
 toc.append((sid,title));file,caption=war_images[n]
 card+='<h3 id="'+sid+'">'+html.escape(title)+'</h3><figure class="new-art"><a class="art-open" href="'+war_art_root+file+'"><img src="'+war_art_root+file+'" width="1536" height="1024" loading="lazy" decoding="async" alt="'+html.escape(caption,quote=True)+'"></a><figcaption>'+html.escape(caption)+' Fictional illustration; built-in image generation. <a href="'+war_art_root+'prompts.json">Full prompts and credits</a>. Select image to enlarge.</figcaption></figure>'+render(body)
card+='<p class="source-note"><a href="WWIII.md">Complete chapter dialogue</a> · <a href="'+war_art_root+'prompts.json">Illustration prompts</a></p></section>'
pieces.append(card);compiled.append('## World War III: The Room That Remains\n\n'+war_raw)
entries.append({'id':'wwiii','title':'World War III: The Room That Remains','source_path':'house-of-returning-authors/WWIII.md','snapshot':'WWIII.md','sha256':digest(war_raw),'original_whitespace_word_count':words(war_raw),'role_change':'none; original fictional movement','collaboration':'Manny Glover with ChatGPT / Codex'})
# New chess studies return to another night in the fictional wartime shelter.
study_raw=(HERE/'TWO-STUDIES.md').read_text()
study_art_root='../artwork/study-crossings/'
study_art_manifest=json.loads((ROOT/'artwork/study-crossings/prompts.json').read_text())
study_parts=re.split(r'(?m)^## ',study_raw)
study_images=[('01-dont-touch-the-queen.png','Maya and Leon replay the queen escapes while Ruth works the radio.'),('02-five-rooks-no-move.png','The stalemate becomes a theatrical city of rooks. This is a chess fantasy, not an exact board diagram.'),('03-the-service-lane.png','Ruth restores the radio while Maya and Leon clear the chess table and the company brings supplies inside.'),('04-the-atlanta-porch.png','An illustrative reconstruction of Manny’s Atlanta porch memory: a gathering of friends, not portraits of the named people.')]
toc.append(('two-studies','Two Studies at the Crossing'))
card='<section id="two-studies" class="play"><p class="eyebrow">New chess and WWIII movement · PG-13 illustrations</p><h2>Two Studies at the Crossing</h2>'+render(study_parts[0])+'<p><a href="../chess/studies/2026-10-31/">Play through both exact games, inspect the final stalemate, and download the original studies</a>.</p>'
for n,part in enumerate(study_parts[1:]):
 title,_,body=part.partition('\n');sid=['study-queen-escapes','study-five-rooks','study-service-lane','atlanta-porch'][n]
 toc.append((sid,title));file,caption=study_images[n]
 prompt_file='porch-prompt.json' if n==3 else 'prompts.json'
 card+='<h3 id="'+sid+'">'+html.escape(title)+'</h3><figure class="new-art"><a class="art-open" href="'+study_art_root+file+'"><img src="'+study_art_root+file+'" width="1536" height="1024" loading="lazy" decoding="async" alt="'+html.escape(caption,quote=True)+'"></a><figcaption>'+html.escape(caption)+' Fictional illustration; built-in image generation. <a href="'+study_art_root+prompt_file+'">Prompts and credits</a>. Select image to enlarge.</figcaption></figure>'+render(body)
card+='<p class="source-note"><a href="TWO-STUDIES.md">Full scene dialogue</a> · <a href="ATLANTA-PORCH.md">Manny’s Atlanta recollection</a> · <a href="../chess/studies/2026-10-31/games.json">Exact move data and source hashes</a> · <a href="../chess/studies/2026-10-31/rickup.pgn">RickUp study PGN</a> · <a href="../chess/studies/2026-10-31/dmiiitr.pgn">Dmiiitr study PGN</a></p></section>'
pieces.append(card);compiled.append('## Two Studies at the Crossing\n\n'+study_raw)
entries.append({'id':'two-studies','title':'Two Studies at the Crossing','source_path':'house-of-returning-authors/TWO-STUDIES.md','snapshot':'TWO-STUDIES.md','sha256':digest(study_raw),'original_whitespace_word_count':words(study_raw),'role_change':'none; original fiction grounded in two supplied study PGNs','collaboration':'Manny Glover with ChatGPT / Codex'})
add_bridge('the-raised-hand','The hand belongs to Michael')
coda_title='Last scene: Babylon'
coda=frame_sections[coda_title]
toc.append(('babylon',coda_title))
pieces.append('<section id="babylon" class="frame coda"><p class="eyebrow">New closing scene · author-supplied dialogue</p><h2>'+coda_title+'</h2>'+render(coda)+'</section>')
compiled.append('## '+coda_title+'\n\n'+coda)
staging=(HERE/'STAGING.md').read_text()
compiled.insert(1,staging)
pieces=[re.sub(r'(<section[^>]*>)',r'\1<p class="board-cue">A physical writing board remains within reach. Performers may write or diagram their interpretation. <a href="STAGING.md">Standing stage convention</a>.</p>',part,count=1) for part in pieces]
full='\n\n---\n\n'.join(compiled)+'\n';(HERE/'MANUSCRIPT.md').write_text(full)
manifest={'title':'The House of Returning Authors','edition':'Opening reading edition','date':'2026-10-30','author':'Manny Glover — Michael Emanuel Glover','emanuel_character':'Manny’s better self: an aspiration toward care and judgment, still imperfect and open to correction; not omniscient or a separate infallible judge.','glover_character':'Chorus and symbolic father figure; Karamazov father analogy; Shakespearean grandeur and glove-maker craft; admired strength; the destructive aspect of American empire figured as Babylon. Layered literary associations, not allegations against relatives.','michael_character':'Composite dramatic figure drawing on Robert Michael Glover (the author’s father), Michael Emanuel Glover (the author), and scriptural archangel Michael as an image and exemplar; not interchangeable biographies or attributed quotations.','collaboration':'Manny Glover with ChatGPT / Codex for the assembled edition and Six Authors exchange; Gemini for the author-supplied PDF collaboration; inherited pieces retain their original credits','coverage':'Five previously published stage/dialogue pieces, the complete supplied Gemini PDF, the verbatim Six Authors exchange, four additional preserved dream/tea scenes, and the fictional One Quick Follow-Up sketch with fifteen framing scenes. The fictional WWIII movement follows the interview, with three further illustrations. Two Studies at the Crossing adds a further fictional chess-and-shelter movement based on two supplied PGNs. The author’s Atlanta porch recollection and a fourth illustration close the movement. Eighteen stage illustrations, the republic flag, and a standing board convention. Not a complete archive of prior conversations or the previous six to seven months.','sources':entries,'follow_up_bridges_sha256':digest(follow_bridges),'follow_up_art':art_manifest,'wwiii_art':war_art_manifest,'two_studies_art':study_art_manifest,'atlanta_porch_art':json.loads((ROOT/'artwork/study-crossings/porch-prompt.json').read_text()),'atlanta_recollection':{'path':'house-of-returning-authors/ATLANTA-PORCH.md','sha256':digest((HERE/'ATLANTA-PORCH.md').read_text()),'handling':'Author-supplied account with spacing and punctuation for reading; no invented quotations from named friends.'},'study_evidence_path':'chess/studies/2026-10-31/games.json','new_frame_path':'FRAME.md','new_frame_sha256':digest(frame),'hyperplay_bridges_path':'HYPERPLAY-BRIDGES.md','hyperplay_bridges_sha256':digest(bridge_source),'staging_path':'STAGING.md','staging_sha256':digest(staging),'thursday_bridges_path':'THURSDAY-BRIDGES.md','thursday_bridges_sha256':digest(new_bridge_source),'new_illustrations':ART,'compiled_whitespace_word_count':words(full),'candidate_count':len(candidates)}
(HERE/'EDITION.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
(HERE/'INVENTORY.json').write_text(json.dumps({'scope':'Tracked local portfolio narrative candidates discovered by documented path selection in build.py; not a complete conversation, Drive, Facebook, or lifetime archive. Counts include source markup. Candidate status does not imply inclusion or approval for adaptation.','candidates':candidates},indent=2,ensure_ascii=False)+'\n')
inv='# Source inventory · opening edition\n\nScope: tracked local portfolio candidates only. Earlier conversations, Facebook, Drive, and missing work have not been recovered by this inventory. Candidate prose is not yet incorporated.\n\n| Title | Status | Source | Approx. source words |\n|---|---|---|---:|\n'
for c in candidates:inv+='| '+c['title'].replace('|',' / ')+' | '+c['status']+' | ['+c['path']+'](../'+c['path']+') | '+str(c['whitespace_word_count'])+' |\n'
(HERE/'INVENTORY.md').write_text(inv)
nav=''.join('<a href="#'+sid+'">'+html.escape(title)+'</a>' for sid,title in toc)
archive='<section id="archive" class="archive"><h2>The shelves still to come</h2><p>This edition incorporates fourteen works, including the supplied Gemini drama, the verbatim Six Authors exchange, and the dream and tea movement. The inventory records '+str(len(candidates))+' local candidates, including prose and chess narratives that have not been adapted. An inventory entry is not an assertion that its events happened to the author.</p><p><a href="INVENTORY.md">Read the source inventory</a> · <a href="INVENTORY.json">Inventory data</a> · <a href="EDITION.json">Edition record and source checksums</a> · <a href="FRAME.md">Opening framing scenes</a> · <a href="HYPERPLAY-BRIDGES.md">Hyperplay transitions</a> · <a href="CAST.md">Cast and literary reference notes</a> · <a href="STAGING.md">The board convention</a> · <a href="art/IMAGE-PROMPTS.md">New illustrations &amp; prompts</a> · <a href="flag.html">The republic flag</a> · <a href="build.py">Edition builder</a></p><p>The next editorial pass will choose further material, decide what belongs onstage, and preserve distinctions between recollection, invention, and recorded dialogue. Private biographical details are not required to fill the gaps.</p></section>'
css='''*{box-sizing:border-box}html{scroll-behavior:auto;scroll-padding-top:25px}body{overflow-wrap:anywhere;margin:0;background:#10181e;color:#ede9df;font:19px/1.85 Georgia,serif}a{color:#91ded0;text-underline-offset:4px}button{font:600 14px system-ui;cursor:pointer;background:#1b3039;color:#f6e9ce;border:1px solid #6b8d8a;border-radius:6px;padding:11px 14px}button:focus-visible,a:focus-visible{outline:3px solid #f4c67d;outline-offset:4px}.mast{padding:45px max(24px,calc((100vw - 1180px)/2));background:radial-gradient(ellipse at top right,#59402e,transparent 65%),#14242c;border-bottom:1px solid #58726c}.eyebrow{font:600 12px/1.6 system-ui;letter-spacing:2px;text-transform:uppercase;color:#dfbf88}h1{font-size:clamp(46px,7vw,84px);line-height:1.08;max-width:900px;margin:20px 0;font-weight:normal}h2{font-size:clamp(29px,4vw,40px);line-height:1.25;font-weight:normal;color:#f2ce95}h3{font-size:25px;line-height:1.4;color:#c9e3cf}h4{font-size:21px}.byline{font:17px/1.8 system-ui;color:#ddd4c4}.roles{display:flex;gap:10px;flex-wrap:wrap;margin:25px 0}.roles span{font:14px/1.5 system-ui;background:#233943;border-radius:5px;padding:9px 12px}.controls{display:flex;gap:12px;flex-wrap:wrap;margin-top:25px}.layout{max-width:1200px;margin:auto;display:grid;grid-template-columns:260px minmax(0,1fr);gap:42px;padding:35px 24px}.contents{position:sticky;top:20px;align-self:start;max-height:92vh;overflow:auto;font:14px/1.5 system-ui}.contents nav{display:grid;gap:0}.contents a{padding:10px;border-left:2px solid #32444b;text-decoration:none}.contents a:hover,.contents a[aria-current="location"]{border-color:#f4c67d;background:#22353d;color:#ffdf9f}.contents summary{font:600 15px system-ui;cursor:pointer;padding:12px 0}main{min-width:0;max-width:790px}.edition-note{font:15px/1.75 system-ui;background:#1c2a32;border-left:3px solid #d6b47b;padding:20px}section{padding:25px 0 45px;border-bottom:1px solid #3b4b50;scroll-margin-top:24px}.frame{padding:25px 24px 40px;background:#16262d;border-radius:8px;margin:35px 0}.play{border-top:4px solid #ce9d72}.act-2{border-color:#78bda4}.act-3{border-color:#8da2dc}.act-4{border-color:#d5ac68}.act-5{border-color:#cc8ba7}p strong:first-child{color:#a6e2d8;font:700 13px/1.7 system-ui;letter-spacing:1px}.stage{color:#bac3c5;font-style:italic}figure{margin:30px 0}figure.new-art{margin:38px -20px}.board-cue{font:13px/1.6 system-ui;color:#c1d7cd;border-left:2px solid #709e91;padding:8px 12px}dialog{width:min(96vw,1500px);max-width:none;max-height:96vh;background:#111c23;color:#f0e8dc;border:1px solid #7ba99c;padding:16px}dialog::backdrop{background:#000d}dialog img{max-height:81vh;object-fit:contain}dialog button{margin-bottom:10px}dialog p{font:14px/1.6 system-ui;margin:8px 0}.quiet .board-cue{color:#35594f}img{width:100%;height:auto;border-radius:7px;display:block}figcaption{font:13px/1.6 system-ui;color:#b4bdbb;margin-top:8px}blockquote{border-left:3px solid #5f9b91;margin-left:0;padding-left:22px}details.source-note{font:14px/1.7 system-ui;border:1px solid #3b5256;padding:15px;border-radius:6px;margin-top:30px}summary{cursor:pointer}.supplied-page{padding:20px 0;border-top:1px solid #52636a}.supplied-page pre{font:16px/1.6 ui-monospace,monospace;white-space:pre-wrap;overflow-wrap:anywhere}.archive,footer{font:15px/1.8 system-ui}footer{max-width:1200px;margin:auto;padding:30px 24px;border-top:1px solid #52636a}.quiet{background:#f5f0e5;color:#222c30}.quiet .mast{background:#e7decb}.quiet h2,.quiet h3{color:#4d3b24}.quiet .byline,.quiet .eyebrow,.quiet figcaption,.quiet .stage{color:#4e585b}.quiet a{color:#215f65}.quiet .frame,.quiet .edition-note,.quiet .roles span{background:#e9e3d7}.quiet p strong:first-child{color:#1c5858}.quiet .contents a:hover,.quiet .contents a[aria-current="location"]{background:#e6ddca;color:#3d382b}.quiet button{background:#eee6d6;color:#263d40}.large main{font-size:22px}@media(max-width:850px){figure.new-art{margin:28px 0}.layout{grid-template-columns:1fr;gap:12px;padding:20px 18px}.contents{position:static;max-height:none}.contents nav{max-height:250px;overflow:auto}.mast{padding:30px 20px}.frame{padding:20px 17px}body{font-size:18px}}@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}@media print{figure.new-art{margin:20px 0}body{background:white;color:black;font-size:12pt}.mast{background:white;padding:0}.layout{display:block;padding:0}.contents,.controls,footer,.source-note{display:none}main{max-width:none}.frame{background:white;padding:0}h1,h2,h3,.stage,.byline,.eyebrow,p strong:first-child{color:black}section{break-before:page;border:0}img{max-height:17cm;object-fit:contain}a{color:black;text-decoration:none}}'''
js='''(()=>{const body=document.body,mode=document.querySelector('#mode'),size=document.querySelector('#size');function setMode(v){body.classList.toggle('quiet',v);mode.setAttribute('aria-pressed',String(v));mode.textContent=v?'Return to theatre colors':'Quiet reading mode'}function setSize(v){body.classList.toggle('large',v);size.setAttribute('aria-pressed',String(v))}try{setMode(localStorage.getItem('house-quiet')==='true');setSize(localStorage.getItem('house-large')==='true')}catch(e){}mode.addEventListener('click',()=>{const v=!body.classList.contains('quiet');setMode(v);try{localStorage.setItem('house-quiet',v)}catch(e){}});size.addEventListener('click',()=>{const v=!body.classList.contains('large');setSize(v);try{localStorage.setItem('house-large',v)}catch(e){}});const viewer=document.querySelector('#art-viewer');document.querySelectorAll('a.art-open').forEach(a=>a.addEventListener('click',e=>{if(viewer&&viewer.showModal){e.preventDefault();viewer.querySelector('img').src=a.href;viewer.querySelector('img').alt=a.querySelector('img').alt;viewer.querySelector('p').textContent=a.closest('figure').querySelector('figcaption').textContent;viewer.showModal()}}));viewer.querySelector('button').addEventListener('click',()=>viewer.close());window.addEventListener('load',()=>{if(location.hash){try{const target=document.getElementById(decodeURIComponent(location.hash.slice(1)));if(target)target.scrollIntoView({behavior:'auto',block:'start'})}catch(e){}}});document.querySelector('#print').addEventListener('click',()=>window.print());if('IntersectionObserver' in window){const observer=new IntersectionObserver(entries=>{for(const entry of entries)if(entry.isIntersecting){document.querySelectorAll('nav a').forEach(a=>{if(a.hash==='#'+entry.target.id)a.setAttribute('aria-current','location');else a.removeAttribute('aria-current')})}},{rootMargin:'-10% 0px -65% 0px'});document.querySelectorAll('main section[id]').forEach(s=>observer.observe(s))}})();'''
page='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>The House of Returning Authors — Manny Glover</title><meta name="description" content="An opening theatrical autobiography by Manny Glover. Michael acts, Emanuel remembers, Glover speaks in chorus. Fourteen works and new framing scenes on one continuous page."><style>'+css+'</style></head><body><header class="mast"><a href="../">HRL Portfolio</a><p class="eyebrow">Opening reading edition · 29 October 2026</p><h1>The House of<br>Returning Authors</h1><p class="byline">A theatrical autobiography by <strong>Manny Glover</strong><br>Michael Emanuel Glover · With credited contributions from ChatGPT / Codex and Gemini</p><div class="roles"><span>MICHAEL · father, self, exemplar</span><span>EMANUEL · better self, still fallible</span><span>GLOVER · the chorus</span></div><p class="byline">Fourteen collected works. Fifteen framing scenes. Eighteen large stage illustrations and the republic flag. Approximately '+str(round(words(full)/100)*100)+' words in the downloadable edition.</p><div class="controls"><button id="mode" aria-pressed="false">Quiet reading mode</button><button id="size" aria-pressed="false">Larger type</button><button id="print">Print / save PDF</button><a href="MANUSCRIPT.md" download>Download the complete text</a><a href="flag.html">The republic flag</a></div></header><div class="layout"><aside class="contents"><details open><summary>The rooms of the house</summary><nav aria-label="Scenes">'+nav+'<a href="#archive">The shelves still to come</a></nav></details></aside><main><div class="edition-note"><strong>A beginning, not the complete collected works.</strong> These scenes stage the author’s inner life through remembered questions, recorded dialogue, and explicit invention. Imaginary relationships and historical or contemporary cameos are not biographical claims or endorsements. The closing Babylon figure is symbolic and is not an identification of any named person in the earlier scenes. New frames are labeled; all fourteen source works and their credits remain available. The working title and arrangement can change.</div><div class="edition-note"><strong>The Michael figure.</strong> Michael draws on Robert Michael Glover, the author’s father; Michael Emanuel Glover, the author; and the scriptural archangel Michael as an image and exemplar. This is a composite dramatic role, not a claim that those identities are literally identical. Emanuel is Manny’s better self, still imperfect: looking back, trying to judge more carefully, and remaining open to correction. Glover speaks in chorus, carrying fatherhood, theatrical grandeur, admired strength, and the destructive imperial aspect figured as Babylon. <a href="CAST.md">Read the evolving cast notes and literary references</a>.</div>'+''.join(pieces)+archive+'</main></div><footer>Written by Manny Glover. Developed in dialogue with ChatGPT / Codex. Original source pieces retain credits including Cypher and Gemini. The supplied Gemini collaboration is identified in its own section. “Glover” is a dramatic chorus; it does not imply an additional person. <a href="EDITION.json">Edition record</a>.</footer><dialog id="art-viewer" aria-label="Enlarged stage illustration"><button type="button">Close illustration</button><img alt=""><p></p></dialog><script>'+js+'</script></body></html>'
# Reserve the actual dimensions of older PNG illustrations too, so deep links
# remain stable while lazy images load.
def reserve_png_size(match):
 tag=match.group(0)
 if 'width=' in tag or 'src=' not in tag:return tag
 src=re.search(r'src="([^"]+)"',tag)
 if not src:return tag
 file=(HERE/src[1]).resolve()
 if file.is_file() and file.suffix.lower()=='.png':
  import struct
  data=file.read_bytes()[:24]
  if data[:8]==b'\x89PNG\r\n\x1a\n':
   w,h=struct.unpack('>II',data[16:24]);tag=tag.replace('<img ',f'<img width="{w}" height="{h}" ',1)
 return tag
page=re.sub(r'<img[^>]*>',reserve_png_size,page)
(HERE/'index.html').write_text(page)
print(json.dumps({'plays':len(entries),'frames':10+len(passages),'compiled_words':words(full),'inventory_candidates':len(candidates)},indent=2))
