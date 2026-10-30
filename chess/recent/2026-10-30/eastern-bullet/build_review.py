"""Build the public review, exact replay frames, annotated PGN and diagrams."""
from pathlib import Path
from html import escape
import collections,hashlib,json,re
import chess,chess.pgn,chess.svg
from editorial import GAMES,FEATURED

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
CAST = {
 'Ra':('🏰','Castle Andora'),'Nb':('🦄','Sir Banyan Blithers'),
 'Bc':('🛕','Popette Christiana Carolina'),'Qd':('🐲','Queen Dilorias'),
 'Ke':('🦁','King Ethelheim'),'Bf':('🧙','Pope Francisco Finochitti'),
 'Ng':('🐎','Dame Gertrude Goethe'),'Rh':('🧱','Castle Hessenbach'),
 'Pa':('🦊','Alexander Aaronson'),'Pb':('🦡','Bartholomew Bogerson'),
 'Pc':('🦝','Cais Christianson'),'Pd':('🦌','Dorothy Dryers'),
 'Pe':('🦉','Ella Elouise'),'Pf':('🐸','Frank Fassenbecher'),
 'Pg':('🦎','Georgiana Gina'),'Ph':('🦔','Harriet Hissindorf'),
}
CHECKPOINTS=[
 {'game':29,'ply':31,'title':'The c-file opens','question':'Black to move. Which checking move collects the queen on c3?',
  'options':['Rxc3+','Nf6','a5'],'answer':'Rxc3+','line':['c8c3','b2c3'],
  'explanation':'Rxc3+ takes White’s queen with check. The c-file is clear. White can answer bxc3, so the rook is part of the price; this is a real recovery, not a free queen.'},
 {'game':12,'ply':25,'title':'Use the knight-shaped Force','question':'Black to move. Which knight check forks the king and queen?',
  'options':['Nxf3+','Qxf3','Ng6'],'answer':'Nxf3+','line':['e5f3','e1e2','f3d4'],
  'explanation':'The knight lands on f3 with check against e1 and attacks the queen on d4. Ke2 Nxd4+ is one legal illustration, not the only possible king response. This is an unplayed analysis branch.'},
 {'game':3,'ply':8,'title':'A queen offer can be accepted','question':'White to move. Which move directly captures Black’s offered queen?',
  'options':['Qxd3','Nf3','Nc3'],'answer':'Qxd3','line':['d1d3'],
  'explanation':'White’s queen can take the black queen on d3 along the open d-file. The recorded game instead continued Nf3 Qxd1+, and Manny won. This is an unplayed analysis branch.'},
]


def replay_frames(game, hero):
    b=game.board();identities={}
    for square,piece in b.piece_map().items():
        if piece.color==hero:
            identities[square]=piece.symbol().upper()+chess.square_name(square)[0]
    frames=[];queen_episodes=[];moves=list(game.mainline_moves())
    for ply in range(len(moves)+1):
        frames.append({'fen':b.fen(),'wood':{chess.square_name(sq):key for sq,key in identities.items()},
                       'last':moves[ply-1].uci() if ply else None,'check':chess.square_name(b.king(b.turn)) if b.is_check() else None})
        if ply==len(moves):break
        move=moves[ply];moving=b.piece_at(move.from_square);captured=b.piece_at(move.to_square)
        if captured and captured.color==hero and captured.piece_type==chess.QUEEN:
            after=b.copy();after.push(move)
            if ply+1<len(moves):after.push(moves[ply+1])
            if after.pieces(chess.QUEEN,not hero):queen_episodes.append(ply+1)
        identity=identities.pop(move.from_square,None)
        identities.pop(move.to_square,None)
        if b.is_en_passant(move):identities.pop(move.to_square-8 if b.turn else move.to_square+8,None)
        if b.is_castling(move) and moving.color==hero:
            rank=chess.square_rank(move.from_square)
            rook_from=chess.square(7 if chess.square_file(move.to_square)>4 else 0,rank)
            rook_to=chess.square(5 if chess.square_file(move.to_square)>4 else 3,rank)
            identities[rook_to]=identities.pop(rook_from)
        if identity:identities[move.to_square]=identity
        b.push(move)
        assert all(b.piece_at(sq) and b.piece_at(sq).color==hero for sq in identities)
    return frames,queen_episodes


def build():
    audit=json.loads((HERE/'analysis.json').read_text())
    deeper=json.loads((HERE/'selected-analysis.json').read_text())
    by_id={g['id']:g for g in audit['games']}
    originals=[]
    with (HERE/'original.pgn').open() as f:
        while (g:=chess.pgn.read_game(f)) is not None:originals.append(g)
    originals.sort(key=lambda g:g.headers['UTCTime'])
    games=[];annotated=[];dialogues=[];rows=[];md=[]
    md.append('''# Bullet Manninja & the Queen-Sac Force
## Eastern Bullet Arena · 30 October 2026

A new fictional review with Tara, Dasha, Michael, Emanuel and Glover from the House/Thursday ensemble, joined by Queen Dilorias, King Ethelheim and the Woodland crew. A physical whiteboard stands beside their chessboard throughout. The characters may diagram and revise; the recorded moves remain the record.

Manny’s brief: bullet, ninja powers, using the Force, sacking the queen. We follow the resulting imbalance: open files, exposed kings, checking chances and the other pieces taking over the scene.

The export contains 29 Manny games at 60+0: 4 wins, 1 draw, 24 losses. These are game results, not arena points or a tournament rank. Fifteen games contain a queen-for-material departure under the definition below; all fifteen ended in losses. That does not erase the interesting resources they contain. The final game’s 16...Rxc3+ is a real queen recovery, and the unplayed ...Nxf3+ in game 12 is an excellent tactical checkpoint.

TARA: Put the square on the board. I want everyone to be able to check the story.

DASHA: A sacrifice gives the remaining pieces a job. Let’s name it before adding another attacker.

QUEEN DILORIAS: I am available for dramatic exits. Kindly tell the rook when its entrance is due.

## The review lens

For each queen offer, ask what it buys: a forcing reply, an exposed king, a clear file, or a concrete material recovery. Then examine the opponent’s simplest answer. In one-minute chess the clock is part of the result; this export has no per-move clock annotations, so it cannot show which moves were premoves or how many seconds a sacrifice consumed.

''')
    for number,game in enumerate(originals,1):
        h=dict(game.headers);g=by_id[h['GameId']];editor=GAMES[number]
        frames,episodes=replay_frames(game,g['side']=='white')
        for beat in editor['beats']:
            assert g['moves'][beat['ply']-1]['san']==beat['san'],(number,beat)
        item={'number':number,'id':g['id'],'title':editor['title'],'capsule':editor['capsule'],
              'headers':h,'side':g['side'],'opponent':g['opponent'],'outcome':g['outcome'],
              'moves':[m['san'] for m in g['moves']],'uci':[m['uci'] for m in g['moves']],
              'frames':frames,'beats':editor['beats'],'queen_departures':episodes,
              'evaluations':[{'cp_white':p['cp_white'],'mate_white':p['mate_white'],
                              'mate_winner':p['mate_winner'],'depth':p['depth']} for p in g['positions']]}
        games.append(item)
        # Annotations are new comments; the original move sequence and headers stay intact.
        game.comment='Bullet Manninja review. '+editor['title']+'. '+editor['capsule']
        nodes=list(game.mainline())
        for beat in editor['beats']:
            node=nodes[beat['ply']-1]
            node.comment=(node.comment+' '+beat['speaker']+': '+beat['text']).strip()
        annotated.append(game.accept(chess.pgn.StringExporter(headers=True,variations=False,comments=True)))
        result=h['Result'].replace('1/2','½')
        rows.append(f'<tr><td>{number:02}</td><th scope="row"><button type="button" data-game="{number}" data-ply="0">{escape(g["opponent"])}</button><span>{escape(editor["title"])}</span></th><td>{g["side"].title()}</td><td class="result-{g["outcome"]}">{result}</td><td>{escape(h["Termination"])}'+(' · mate' if g['ending']['is_checkmate'] else '')+'</td></tr>')
        beat_html=[];md.append(f'## {number:02}. {editor["title"]}\n\n{h["White"]} ({h["WhiteElo"]}) — {h["Black"]} ({h["BlackElo"]}) · {h["Result"]} · {h["Termination"]} · [{g["id"]}](https://lichess.org/{g["id"]})\n\n{editor["capsule"]}\n')
        for beat in editor['beats']:
            ply=beat['ply'];prefix=str((ply+1)//2)+('.' if ply%2 else '...');label=prefix+beat['san']
            beat_html.append(f'<div class="dialogue"><span class="speaker">{escape(beat["speaker"])}</span><p><button type="button" class="move-link" data-game="{number}" data-ply="{ply}">{escape(label)}</button> {escape(beat["text"])}</p></div>')
            md.append(f'**{beat["speaker"]} — {label}:** {beat["text"]}\n')
        if number in FEATURED:
            dialogues.append((number,f'<article class="act" id="act-{number}"><div class="act-heading"><p class="eyebrow">GAME {number:02} · {escape(g["outcome"].upper())}</p><a href="#replay" data-game="{number}" data-ply="{editor["beats"][0]["ply"]}">Replay this chapter ↗</a></div><h3>{escape(editor["title"])}</h3><p class="act-intro">{escape(editor["capsule"])}</p>'+''.join(beat_html)+'</article>'))
    departure_total=sum(len(g['queen_departures']) for g in games)
    assert departure_total==15
    assert len(games)==29 and len(GAMES)==29
    method='''## Method and provenance

The original PGN is retained byte for byte. Games are arranged chronologically by UTC start time; the supplied file was newest first. All 1,621 plies parsed legally with python-chess. Stockfish 14.1 searched each non-terminal position at 40,000 nodes, one thread, 64 MiB hash, no configured tablebases. Nine selected positions were rechecked at 500,000 nodes with three candidate lines. Finite searches are estimates, not proofs of optimal play. The detailed outputs retain depths, scores, PVs and settings.

A queen-for-material departure means the player’s queen is captured and the opponent still has a queen after the player’s immediately following reply, if one was recorded. This structural count separates nine immediate queen exchanges from fifteen unmatched queen losses; it cannot determine the intention behind each move. Later queen recovery, such as game 29’s ...Rxc3+, remains part of the story.

The time-forfeit draw is supported by the final board (Black has only a king; White has a rook and pawns) and the recorded draw/termination tags. Lichess explains that a timeout is drawn when the opponent cannot mate by any legal sequence: https://lichess.org/faq#timeout. There are no per-move clock stamps in this file. No premove, remaining-time, intent, arena-rank or opponent-motive claims have been inferred.

New dialogue uses the House/Thursday fictional ensemble and existing Woodland cast. The opponents’ names and ratings are PGN metadata. Manny’s pieces remain Woodland on either board color; opponents remain classical figurines. The original source stories and scripts are unchanged.
'''
    md.append(method)
    (HERE/'REVIEW.md').write_text('\n'.join(md)+'\n')
    (HERE/'reviewed.pgn').write_text('\n\n'.join(annotated)+'\n')
    for checkpoint in CHECKPOINTS:
        g=games[checkpoint['game']-1];b=chess.Board(g['frames'][checkpoint['ply']]['fen']);line=[]
        for uci in checkpoint['line']:
            move=chess.Move.from_uci(uci);assert move in b.legal_moves
            line.append(b.san(move));b.push(move)
        checkpoint['line_san']=line
        checkpoint['fen']=g['frames'][checkpoint['ply']]['fen']
    data={'summary':audit['summary'],'queen_departures':departure_total,'cast':CAST,
          'games':games,'checkpoints':CHECKPOINTS,'default_game':29,'default_ply':32}
    (HERE/'review.json').write_text(json.dumps(data,separators=(',',':'),ensure_ascii=False)+'\n')
    diagrams=HERE/'diagrams';diagrams.mkdir(exist_ok=True)
    puzzles=[]
    for i,c in enumerate(CHECKPOINTS):
        b=chess.Board(c['fen']);side=chess.WHITE if b.turn else chess.BLACK
        svg=chess.svg.board(b,orientation=side,size=480,colors={'square light':'#eadbb9','square dark':'#689186','margin':'#122b35','coord light':'#ddd6be','coord dark':'#b7d2c1'})
        (diagrams/f'checkpoint-{i+1}.svg').write_text(svg)
        puzzles.append(f'<article class="checkpoint"><img src="diagrams/checkpoint-{i+1}.svg" alt="{escape(c["question"],quote=True)}" width="480" height="480" loading="lazy"><div class="checkpoint-copy"><p class="eyebrow">CHECKPOINT {i+1:02} · GAME {c["game"]:02}</p><h3>{escape(c["title"])}</h3><p>{escape(c["question"])}</p><div class="answers" role="group" aria-label="Answer checkpoint {i+1}">'+''.join(f'<button type="button" data-puzzle="{i}" data-answer="{escape(option,quote=True)}">{escape(option)}</button>' for option in c['options'])+f'</div><p class="puzzle-feedback" id="puzzle-feedback-{i}" role="status">Take a look. No clock running here.</p><button type="button" class="text-button" data-game="{c["game"]}" data-ply="{c["ply"]}">See the recorded position ↑</button></div></article>')
    template=(HERE/'page-template.html').read_text()
    template=template.replace('<!-- ACTS -->','\n'.join(dict(dialogues)[n] for n in FEATURED))
    template=template.replace('<!-- SCORE_ROWS -->','\n'.join(rows)).replace('<!-- CHECKPOINTS -->','\n'.join(puzzles))
    (HERE/'index.html').write_text(template)
    manifest={'source_file':'original.pgn','sha256':audit['source_sha256'],'games':len(games),'plies':sum(len(g['moves']) for g in games),
              'outcomes':dict(collections.Counter(g['outcome'] for g in games)),
              'queen_departures':departure_total,'engine':audit['engine'],'files':['index.html','REVIEW.md','original.pgn','reviewed.pgn','review.json','analysis.json','selected-analysis.json'],
              'cast_sources':['../../../../house-of-returning-authors/CAST.md','../../../../thursday/THURSDAY.md','../../../../whimsy-chess/CAST-POLICY.md']}
    (HERE/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(f'Built {len(games)} games, {len(dialogues)} featured chapters, {sum(len(g["beats"]) for g in games)} checked story beats, 3 legal checkpoints.')


if __name__=='__main__':build()
