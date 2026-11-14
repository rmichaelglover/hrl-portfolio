from pathlib import Path
import json,csv,html,shutil,zipfile
from collections import Counter
O=Path(__file__).parent;G=json.loads((O/'games.json').read_text());M=json.loads((O/'metadata.json').read_text());S=json.loads((O/'summary.json').read_text());byid={g['id']:g for g in G}
assert len(G)==76 and sum(x['chapters'] for x in M['studies'])==77
esc=html.escape
manual={
'df4AKckV':"A particularly clear realization of controlled provocation. Your queen on h5 was attacked by 10.Bf3. Instead of retreating, 10…g4 blocked the bishop’s line and attacked that bishop. After 11.Be4 hxg3 12.fxg3, 12…Qxh2# completed the attack. The observable gain is the counterattack and mating geometry; the opponent’s private impression of you is not recorded.",
'2nJxcpYA':"A mixed but instructive test. 3.Nc3 and 4.Nf3 developed fresh knights with threats against your queen, so those were productive development tempi. Later, 10.Nd5 attacked the queen on f6 but allowed 10…Qxa1. The deeper check confirms a major tactical concession there. The practical lesson is to distinguish sound developing threats from a later overextension.",
'475976ig':"A queen-to-queen confrontation rather than simply a development race. After …Qg4 and …Qxg2, White tried 8.Qf3 and 9.Qg2. Your 9…Qxg2 won their queen. This supports readiness to exploit a mistaken attack; it does not by itself show that you induced underestimation.",
'TaC6RghC':"White’s 7.Bg5 developed a bishop while threatening your queen. The later 9.Nh4 moved an already-active knight to attack the queen on f5. Your 9…Qxg5 10.Qxg5 fxg5 traded queens and removed White’s bishop. The distinction between a sound first developing threat and an exploitable follow-up is central to your thesis.",
'i0W1q3IX':"Your 2.Qd2 and unusual setup met Black’s queen-and-bishop pressure. 5.e3 Qxe3+ 6.Qxe3 Bxe3 7.Bxe3 left you a bishop ahead for a pawn. That is an opening tactical payoff. The later game was a separate comeback: your first c-pawn eliminated a rook, the second promoted, and after the opponent’s responses you captured both their queens. 85.Qg2# converted the final queen ending. The opening payoff and the eventual win should be credited separately.",
'AOYgpFzW':"A counterexample to treating unfamiliarity as sufficient protection. 2.Qd2, 3.Kd1 and 4.Qe1 combined early queen play with an uncastled king relocation. Black’s central invasion culminated in 18…Qxd2#. The practical checkpoint is whether your king and defenders remain coordinated while you introduce the unusual feature.",
'fjFuElbw':"The clearest local piece-safety issue is 17.Qxe4 Bxe4: the bishop on h7 defended e4 along the diagonal. Your queen was lost when it captured the knight there. There was no qualifying early queen-chase episode in this chapter. This is a calculation/safety lesson rather than evidence that the provocation mechanism failed merely because an opening was unusual.",
'zoMm9deu':"A successful unconventional opening without an early queen outing: your queen first moved on move 19. The early story is pawn commitments and bishop activity, including Bxc7 and Bxb8. This belongs to the broader controlled-unfamiliarity programme, but should not be counted as evidence for a specifically early-queen psychological mechanism.",
'DItWyjG9':"Your Qb1–Qb2 arrangement was unconventional, but there was no qualifying queen-chase episode in the first twenty moves. The recorded result is a win on time after 26.Rg6+. The engine screen flags substantial tactical difficulties along the way. The win is real; a clock result and an objectively established opening advantage are different measurements.",
'pjvMqQeJ':"This is Crazyhouse, won on time against tixupixu. Captured pieces can return as drops: 17…B@e6 is a drop-based queen threat, not ordinary bishop development. Its subsequent tactics are legally replayed under Crazyhouse rules. Standard Stockfish scores are deliberately absent, so this chapter is kept separate from standard-chess evaluation claims.",
'OGrU8gpH':"Only one ply is recorded. The result is a White win, but the chapter contains no developed queen-chase or tactical sequence with which to test the theory. It belongs in the inventory, not among substantive supporting examples."
}

def move_number(m):return int(m['move'].split('.')[0])
def score(ev):
 if ev.get('terminal'):return 'recorded terminal outcome'
 s=ev.get('display','')
 if ev.get('unsupported_variant'):return 'not scored for this variant'
 if s=='terminal':return 'terminal outcome'
 if s.startswith('#'):
  n=int(s[1:]);return f"{'White' if n>0 else 'Black'} searched mate in {abs(n)}"
 try:return f"White {int(s)/100:+.2f}"
 except ValueError:return s

def critical(g,key,heading):
 m=g.get(key)
 if not m or not g['engine_supported'] or g['plies']<3:return ''
 deep=g.get('refinements',{}).get(str(m['ply']))
 before=deep['before'] if deep else g['evaluations'][m['ply']-1];after=deep['after'] if deep else g['evaluations'][m['ply']]
 pref=before.get('pv','');budget='200,000-node recheck' if deep else '20,000-node screen'
 t=f"**{heading}: {m['move']}.** {budget}: {score(before)} → {score(after)}."
 if pref:t+=f" Pre-move candidate line: `{pref}`."
 if deep:
  delta=deep['swing_for_michael']
  if key=='largest_own_setback' and delta>=-75:t+=' The deeper check does not reproduce a substantial adverse swing; do not label this move a demonstrated blunder from the initial screen alone.'
  if key=='largest_opponent_concession' and delta<=75:t+=' The deeper check does not confirm a substantial concession; the initial screening signal is not treated as a proven opportunity.'
 return t

studyrows=[]
for study in M['studies']:
 a=[byid[i] for i in study['ids']];c=Counter(g['outcome'] for g in a)
 studyrows.append((study['name'],study['chapters'],c['Win'],c['Draw'],c['Loss'],sum(g['early_queen'] for g in a)))
intro=[
'# Controlled Provocation: A Review of Six Recent Public Chess Studies',
'**Michael Emanuel Glover’s opening theory · 13 November 2026**',
'Originating theory, playing style, study curation and games: **Michael Emanuel Glover (mannyfresher)**. Assistant contribution: legal replay, operational definitions, engine screening and rechecks, aggregation, and explanatory writing.',
'## Finding',
'Your controlled-provocation idea has concrete tactical realizations in these studies. Its strongest examples do more than survive a queen threat: they answer it with a counter-threat, interposition, material gain, or mating attack. Fermathemate’s 10.Bf3 met …g4 and a mating finish; No_More_Bans_Pls’s later Nd5 allowed …Qxa1; A-Roy2025’s Nh4 allowed a favorable queen liquidation. These are observable commitments and consequences.',
'The same record also distinguishes productive queen threats from wasted moves. A fresh knight or bishop can develop well while attacking your queen. Repeated-piece moves are not automatically wasted either; their value depends on what they accomplish. The useful test is the position after your answer, including your own queen tempi, king safety, and available tactics.',
'## Your theory, made testable',
'> Make the position look inviting to attack, while preparing to exploit the attack’s commitments. Keep a functional structure, introduce deliberate unfamiliarity, and judge the opponent’s response rather than treating an unusual appearance as a defect.',
'The board-level hypothesis is that selected queen provocations elicit exploitable commitments. The psychological hypothesis is that opponents underestimate an unconventional player. The move records can test tactical consequences, development, and queen displacement; they do not record an opponent’s private beliefs. A successful counterattack is credited without inventing those beliefs.',
'## Complete inventory',
'All **77 chapters** in the six recent files were reviewed. They contain **76 unique games**, with **4,856 recorded plies** after deduplication. The unique results are **41 wins, 10 draws, 25 losses** from your side. The duplicate is the Svenjamin94 game `1ET6rM28`, appearing in two study chapters; both chapter locations remain indexed below.',
'There are **75 standard-rule chapters/games** eligible for standard Stockfish evaluation, including two chapters beginning from supplied positions, and **one Crazyhouse game**. Study membership totals below count the duplicate in each study where it appears.',
'| Study | Chapters | Wins | Draws | Losses | Queen moved by move 10 |',
'|---|---:|---:|---:|---:|---:|']
intro += ['| '+' | '.join(map(str,r))+' |' for r in studyrows]
intro += [
'## What the queen-pressure audit found',
'An “early queen” means your queen first moved by recorded fullmove 10; **44 games** qualify, including **27 by move 5**. Those 44 games ended **26 wins, 6 draws, 12 losses**. This is a description of your selected studies, not an estimate of what early queen play causes against matched opponents.',
'After your queen had moved, **43 games** contained a qualifying newly available legal queen-capture threat in the first twenty recorded full moves. **30 of the 44 early-queen games** had such an episode. Across the complete sample there were **93 episodes**:',
'| Opponent action producing queen pressure | Episodes | Interpretation |',
'|---|---:|---|',
'| Repeated move with an already-active piece | 41 | A candidate commitment to examine; not automatically a wasted tempo. |',
'| First move of a knight or bishop | 22 | Developing with a threat; ordinarily a useful tempo unless concretely refuted. |',
'| Pawn commitment | 20 | Changes squares, lines or pawn structure; its actual costs require calculation. |',
'| Other first piece move | 9 | Includes queen/rook/king activity; examine the concrete purpose. |',
'| Crazyhouse piece drop | 1 | A variant-specific threat, treated separately from ordinary development. |',
'Of these 93 episodes, **70 were answered by a queen move**; **33 of those queen answers captured or gave check**, while **37 did neither**. There were **7 checking opponent moves** among the queen-pressure episodes. Those can be forks or forcing combinations rather than simple harassment. This ledger makes the cost on both sides visible; it is not a net-tempo or causal-gain calculation.',
'In **22 games**, you also made a non-castling king move within the first ten recorded full moves. That is another commitment to assess alongside early queen play. Your “one deliberate exception” idea is most demanding when several exceptions accumulate: queen moves, king relocation, pawn commitments, or delayed development. The report identifies those combinations without assuming that every one is unsound.',
'## Practical conclusions',
'1. **Best-supported mechanism: a forcing answer to the queen threat.** The clearest case is …g4 against Bf3: it both shields the queen’s line and attacks the threatening bishop. The queen is not just running away.',
'2. **Count developing threats honestly.** Nc3 and Nf3 against No_More_Bans_Pls were useful development, even though a later knight chase failed tactically. Different episodes in the same game deserve different judgments.',
'3. **Keep piece safety symmetric.** The opponent’s exposed attacker and your exposed queen obey the same capture geometry. Against pietro_atlas, Qxe4 entered the h7-bishop’s diagonal.',
'4. **Separate opening success, later recovery, and final result.** The kusal2022 game contains an opening gain and a later comeback. A win on time records successful practical play, but does not establish that the final position or opening was theoretically winning.',
'5. **Keep the broader theory broader than the queen.** The Justinnn09 win used an unconventional setup and active bishops before your queen first moved on move 19. That supports studying unfamiliar structures, not attributing every success to early queen psychology.',
'## Method and reading the game notes',
'Every supplied mainline was replayed with python-chess and the appropriate rules. Standard positions were screened with **Stockfish 14.1, one thread, 64 MB hash, 20,000 nodes per position**. Each eligible game’s largest screened personal setback and opponent concession, plus the strongest screened early queen-pressure episode where present, received a **200,000-node before/after recheck**. Candidate lines are legal continuations generated during those searches. Positions retain their replayed histories.',
'Engine figures are always **from White’s perspective**, in pawn units. They are finite-search assessments, not proofs of optimal play. Mate-search scores are printed as searched mates rather than being interpreted as ordinary centipawn changes. A changed evaluation can be a search-horizon effect; the notes explicitly flag important screening signals not reproduced by the deeper check.',
'A queen-pressure episode requires a newly available **legal** capture of your queen after an opposing move and after your queen has already moved. Pinned geometric attacks that cannot legally capture it are excluded. Threats can include checking forks and offers to trade queens. A queen actually captured on that move is separately recorded, rather than counted as an ensuing chase. In Crazyhouse, drops are labeled explicitly. “Repeat-piece” is based on the recorded piece’s prior moves; it is not a claim that its latest move lacked value.',
'The two “From Position” chapters are evaluated from their supplied FENs. Their numbering describes the supplied record, not unseen earlier play. No opponent intention, preparation, emotional state, or deliberate trap is inferred solely from the result.',
'## Selected examples in detail']
for id in ['df4AKckV','2nJxcpYA','TaC6RghC','i0W1q3IX','AOYgpFzW','fjFuElbw','zoMm9deu']:
 g=byid[id];opp=g['headers']['Black'] if g['michael_color']=='White' else g['headers']['White']
 intro += [f"### {opp} — {g['outcome']}, you played {g['michael_color']}",manual[id],f"[Public study chapter]({g['references'][0]['chapter_url']})"]
intro += ['## All 77 chapter locations','The index includes every chapter. Repeated game IDs link to the single deduplicated analysis.','| Study | Chapter | Opponent | Your side | Result | Game |','|---|---:|---|---|---|---|']
for study in M['studies']:
 for number,id in enumerate(study['ids'],1):
  g=byid[id];opp=g['headers']['Black'] if g['michael_color']=='White' else g['headers']['White']
  intro.append(f"| {study['name']} | {number} | {opp} | {g['michael_color']} | {g['outcome']} | [{id}](#game-{id.lower()}) |")
sections=[];records=[]
for g in G:
 h=g['headers'];opp=h['Black'] if g['michael_color']=='White' else h['White'];refs=g['references']
 lines=[f"<a id=\"game-{g['id'].lower()}\"></a>",f"### {g['index']:02d}. {opp} — {g['outcome']} as {g['michael_color']}",f"**{h.get('Date','?')} · {h.get('White')}–{h.get('Black')} · {h.get('Result')} · {g['plies']} plies · {h.get('Termination','termination unspecified')}. [Study chapter]({refs[0]['chapter_url']}) · [Game]({h['Site']})."]
 if g.get('custom_start'):lines.append('**Supplied-position chapter:** review begins from its PGN FEN, not an assumed standard initial position.')
 if not g['engine_supported']:lines.append('**Crazyhouse:** drop-aware legal replay; no standard-chess engine assessment.')
 if g['id'] in manual:lines.append(manual[g['id']])
 if g['queen_moves']:
  first=g['queen_moves'][0];q=g['queen_moves_first10'];forcing=sum(x['forcing'] for x in q)
  lines.append(f"**Queen plan:** first queen move `{first['move']}`; {len(q)} queen moves in the first ten recorded full moves, {forcing} capturing or checking. "+('This is an early-queen test under the stated definition.' if g['early_queen'] else 'This is not an early-queen test under the stated definition.'))
 else:lines.append('**Queen plan:** your queen did not move in the supplied mainline; this is not a test of your early-queen mechanism.')
 cs=g['early_chases']
 if cs:
  detail=[]
  for c in cs:
   qualifier='; also check' if c['checking_move'] else ''
   detail.append(f"`{c['move']}` ({c['kind']}{qualifier}) → `{c['response'] or 'record ends'}`")
  lines.append('**Queen-pressure ledger, through move 20:** '+'; '.join(detail)+'.')
  counts=Counter(c['kind'] for c in cs)
  developed=counts['minor-piece development'];repeated=counts['repeat-piece move']
  text=f"**Theory assessment:** {developed} developing minor-piece threat(s), {repeated} repeated-piece threat(s). "
  text+=('The record directly tests your response to queen pressure. Judge each episode by its concrete follow-up; neither the threat count nor the final result identifies wasted tempi by itself.' if g['early_queen'] else 'The threats occurred after a later queen move, so they illuminate queen handling without directly testing early deployment.')
  lines.append(text)
 else:lines.append('**Theory assessment:** no qualifying queen-pressure episode after your queen moved and within the first twenty recorded full moves. This game can illuminate your setup and tactics, but supplies no direct opening chase episode under this definition.')
 ownminor=', '.join(g['own_minor_development_first10']) or 'none recorded';otherminor=', '.join(g['opponent_minor_development_first10']) or 'none recorded'
 lines.append(f"**Development and king commitments:** your first minor-piece moves through move 10: `{ownminor}`; opponent: `{otherminor}`. "+('Your non-castling early king moves: `'+', '.join(g['early_uncastled_king_moves'])+'`.' if g['early_uncastled_king_moves'] else 'No non-castling early king move is recorded.'))
 for key,title in [('largest_own_setback','Your screened critical decision'),('largest_opponent_concession','Opponent’s screened critical decision')]:
  t=critical(g,key,title)
  if t:lines.append(t)
 end=' '.join(m['move'] for m in g['moves'][-6:])
 lines.append('**Recorded finish:** `'+end+'`. '+('The final position is checkmate.' if g['checkmate'] else 'The supplied record does not end in a checkmated position; its header result and termination are retained.'))
 lines.append('**Opening record:** `'+' '.join(m['move'] for m in g['moves'][:20])+'`.')
 if len(refs)>1:lines.append('**Duplicate preserved:** '+ '; '.join(f"{r['study']} chapter {r['chapter']}" for r in refs)+'.')
 sections.append((g,opp,lines))
 records.append({'game_id':g['id'],'studies':'; '.join(r['study'] for r in refs),'opponent':opp,'your_color':g['michael_color'],'result':g['outcome'],'date':h.get('Date'),'plies':g['plies'],'variant':h.get('Variant','Standard'),'early_queen':g['early_queen'],'first_queen_move':g['queen_moves'][0]['move'] if g['queen_moves'] else '', 'queen_moves_first10':len(g['queen_moves_first10']),'queen_pressure_episodes_first20':len(cs),'minor_development_threats':sum(c['kind']=='minor-piece development' for c in cs),'repeat_piece_threats':sum(c['kind']=='repeat-piece move' for c in cs),'public_chapter':refs[0]['chapter_url']})
def join_blocks(blocks):
 out=''
 previous=''
 for block in blocks:
  out+=('\n' if block.startswith('|') and previous.startswith('|') else '\n\n' if out else '')+block
  previous=block
 return out

md=join_blocks(intro+['## Individual game reviews']+[line for _,_,ls in sections for line in ls])+'\n'
(O/'CONTROLLED-PROVOCATION-REVIEW.md').write_text(md)
with (O/'game-index.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
# Minimal local reader: all evidence and complete movetext stay available offline.
try:
 import markdown
 render=lambda x:markdown.markdown(x,extensions=['tables','fenced_code'])
except ImportError:
 render=lambda x:'<div style="white-space:pre-wrap">'+esc(x)+'</div>'
body=render(join_blocks(intro))
options=''.join(f'<option>{esc(st["name"])}</option>' for st in M['studies'])
body+='<section id="game-reviews"><h2>Individual game reviews — all 76 unique games</h2><div class="filters"><label>Search <input id="search" placeholder="Opponent, move, or game ID"></label><label>Study <select id="study"><option value="">All studies</option>'+options+'</select></label><label>Result <select id="result"><option value="">All results</option><option>Win</option><option>Draw</option><option>Loss</option></select></label><output id="shown">76 games</output></div>'
for g,opp,lines in sections:
 studies='|'.join(r['study'] for r in g['references']);details=render('\n\n'.join(lines[2:]))
 full=' '.join(m['move'] for m in g['moves'])
 body+=f'<article class="game" id="game-{g["id"].lower()}" data-study="{esc(studies,quote=True)}" data-result="{g["outcome"]}"><h3>{g["index"]:02d}. {esc(opp)} — {g["outcome"]} as {g["michael_color"]}</h3>{details}<details><summary>Complete recorded mainline</summary><p class="moves">{esc(full)}</p></details></article>'
body+='</section>'
css='''body{font:18px/1.65 Georgia,serif;color:#243d35;background:#f5f0e4;margin:0}main{max-width:1100px;margin:auto;padding:35px 24px 80px}h1{font-size:clamp(32px,6vw,60px);line-height:1.1}h2{margin-top:55px;border-top:1px solid #adbca8;padding-top:25px}h3{font-size:25px}a{color:#27624b}table{border-collapse:collapse;width:100%;font:14px/1.6 system-ui;display:block;overflow:auto}th,td{padding:9px 12px;border:1px solid #c2c9b7;text-align:left}code,.moves{font:14px/1.7 ui-monospace,monospace;overflow-wrap:anywhere;background:#e6e9da}blockquote{border-left:4px solid #aa8752;padding:8px 24px;font-size:21px}.game{border:1px solid #c3ccb8;border-radius:9px;padding:23px;margin:25px 0;background:#fffbf1;scroll-margin-top:20px}.filters{display:flex;flex-wrap:wrap;gap:15px;background:#dde5d4;padding:18px;border-radius:8px;font:14px system-ui}.filters label{display:grid;gap:6px}input,select{font:inherit;padding:9px;max-width:100%}details{padding:12px 0}summary{cursor:pointer}nav{font:14px system-ui;display:flex;gap:20px;flex-wrap:wrap}.game[hidden]{display:none}@media print{.filters,nav{display:none}.game{break-inside:avoid}body{background:white;color:black}}'''
js='''const search=document.querySelector('#search'),study=document.querySelector('#study'),result=document.querySelector('#result');function filter(){let count=0;document.querySelectorAll('.game').forEach(g=>{g.hidden=!(g.textContent.toLowerCase().includes(search.value.toLowerCase())&&(!study.value||g.dataset.study.split('|').includes(study.value))&&(!result.value||g.dataset.result===result.value));if(!g.hidden)count++;});document.querySelector('#shown').textContent=count+' games';}for(const el of [search,study,result])el.addEventListener('input',filter);'''
(O/'index.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Controlled Provocation · Michael Emanuel Glover</title><style>'+css+'</style><main><nav><a href="CONTROLLED-PROVOCATION-REVIEW.md">Full Markdown report</a><a href="game-index.csv">Spreadsheet index</a><a href="games.json">Analysis data</a><a href="metadata.json">Sources and settings</a></nav>'+body+'</main><script>'+js+'</script></html>')
inputs=O/'inputs';inputs.mkdir(exist_ok=True)
for src in M['source_files']:shutil.copy(src['file'],inputs/Path(src['file']).name)
print('Wrote full review:',len(G),'game sections;',len(md.split()),'words; all 77 chapter locations indexed.')
