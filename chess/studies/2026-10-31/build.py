"""Build exact replays and source evidence for the two user-selected studies."""
from pathlib import Path
import hashlib,json,html,shutil
import chess,chess.pgn,chess.svg

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
SOURCES=[('rickup','lichess_study_van-mieses_mannyfresher-1235-rickup-1255_by_mannyfresher_2026.10.31.pgn'),('dmiiitr','lichess_study_vant-kruijsing_mannyfresher-1086-dmiiitr-1679_by_mannyfresher_2026.10.31.pgn')]
NOTES={
'rickup':{8:'4...Bf5 leaves Black’s queen on d5 available to Qxd5.',9:'5.Qxd5 captures the black queen.',17:'9.Bb2 leaves White’s queen on f5 available to the e6-pawn. This is a missed opportunity, not an actual capture.',18:'9...O-O-O misses exf5; White’s queen survives.',33:'17.Bxh8 takes a rook but leaves the queen on b5 available to cxb5.',34:'17...Nxd3 misses cxb5.',35:'18.Qxd3+ is check, not mate. The source records 1–0 by time forfeit, while the last clock annotations still show Black 35 seconds and White 15 seconds. The export does not resolve that discrepancy.'},
'dmiiitr':{30:'15...Qxe4+ captures White’s queen with check.',39:'20.Rad1 puts the a-rook on d1; Black takes it with Qxd1.',42:'21...Rad8: White has recaptured the black queen, but has paid heavily in pieces.',44:'22...Rxd7 takes White’s last rook, after Rxd7 captured a bishop.',84:'42...Nxg5 removes White’s final pawn. White has only a king.',94:'47...a1=R is the first rook underpromotion.',112:'56...h1=R is the second rook underpromotion.',120:'60...g1=R is the third: Black now has five rooks.',135:'68.Kf5: the white king reaches f5.',136:'68...Re8 is stalemate: White to move, not in check, zero legal moves. Black still has five rooks, a bishop, a knight, and two pawns.'}}

def variations(node):
    for child in node.variations:
        assert child.move in node.board().legal_moves
        variations(child)

games=[]
for sid,name in SOURCES:
    source=Path('/home/rmichaelglover/Documents')/name
    dest=HERE/(sid+'.pgn')
    if source.exists():shutil.copy2(source,dest)
    with dest.open() as f:game=chess.pgn.read_game(f)
    assert game and not game.errors
    variations(game)
    board=game.board();frames=[{'fen':board.fen(),'san':'Start','label':'Start','note':'','clock':None}]
    for node in game.mainline():
        label=str(board.fullmove_number)+('. ' if board.turn else '... ')+board.san(node.move)
        board.push(node.move)
        frames.append({'fen':board.fen(),'san':node.san(),'label':label,'note':NOTES[sid].get(node.ply(),''),'clock':node.clock()})
    game_data={'id':sid,'headers':dict(game.headers),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'frames':frames,'legal_plies':len(frames)-1,'final_stalemate':board.is_stalemate(),'final_check':board.is_check(),'final_legal_moves':len(list(board.legal_moves)),'final_piece_count':len(board.piece_map()),'source':sid+'.pgn'}
    if sid=='dmiiitr':
        assert board.is_stalemate() and len(board.pieces(chess.ROOK,chess.BLACK))==5
        k=board.king(chess.WHITE)
        game_data['king_neighbours']=[{'square':chess.square_name(s),'occupied':str(board.piece_at(s)) if board.piece_at(s) else None,'attackers':[chess.square_name(a) for a in board.attackers(chess.BLACK,s)]} for s in chess.SquareSet(chess.BB_KING_ATTACKS[k])]
    for ply in ([8,17,33,35] if sid=='rickup' else [30,120,136]):
        b=chess.Board(frames[ply]['fen'])
        (HERE/f'{sid}-{ply}.svg').write_text(chess.svg.board(b,size=520,coordinates=True))
    games.append(game_data)
(HERE/'games.json').write_text(json.dumps({'scope':'Exact PGN mainlines; imported source comments and analysis variations retained in original PGNs. No new engine evaluations claimed.','games':games},indent=2)+'\n')
cards=[]
for g in games:
    hd=g['headers'];sid=g['id']
    cards.append('<section id="'+sid+'"><h2>'+html.escape(hd['White']+' – '+hd['Black'])+'</h2><p>'+html.escape(hd['Result']+' · '+hd['TimeControl']+' · '+hd['Opening'])+'</p><p><a href="'+g['source']+'">Original study PGN, including variations</a> · <a href="'+html.escape(hd['ChapterURL'])+'">Lichess study</a></p><div class="replay" data-game="'+sid+'"><div class="board" role="img" aria-label="Chess position"></div><div class="controls"><button data-step="start">Start</button><button data-step="prev">Previous</button><button data-step="next">Next</button><button data-step="end">End</button></div><label>Move <input type="range" min="0" max="'+str(g['legal_plies'])+'" value="0"></label><p class="status" aria-live="polite"></p><p class="note" aria-live="polite"></p><div class="jumps">'+''.join('<button data-ply="'+str(i)+'">'+html.escape(fr['label'])+'</button>' for i,fr in enumerate(g['frames']) if fr['note'])+'</div></div><details><summary>Complete mainline</summary><p>'+html.escape(' '.join(fr['label'] for fr in g['frames'][1:]))+'</p></details></section>')
body='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Two Studies at the Crossing — exact chess replays</title><link rel="stylesheet" href="style.css"><header><a href="../../../house-of-returning-authors/#two-studies">Read the illustrated story in the Megaplay</a><h1>Two Studies at the Crossing</h1><p>A queen that gets away twice. A bare king and five rooks. Two exact study replays.</p></header><main><aside>The games are real records supplied by Manny; the WWIII shelter and cast dialogue are fiction. PGN headers date both games 31 October 2026. The RickUp export records a time-forfeit win although its last clock marks show time remaining. The Dmiiitr position verifies as stalemate. Imported engine comments belong to the supplied source; no new engine scores are presented here.</aside>'''+''.join(cards)+'''<section><h2>The final cage</h2><img src="dmiiitr-136.svg" width="520" height="520" alt="Exact final stalemate: white king f5; black rooks e8 e1 f1 g1 h1, king g8, bishop g7, knight h7, pawns e3 f4."><p>White is not in check. Every adjacent square is attacked, and White has no other pieces. Five rooks cannot make this position a win: the game is already drawn.</p></section></main><footer><a href="games.json">Replay data, source hashes, and final king-square attacks</a> · <a href="../../../house-of-returning-authors/TWO-STUDIES.md">Full dialogue</a></footer><script src="replay.js"></script></html>'''
(HERE/'index.html').write_text(body)
print('Built two exact replays:',[(g['id'],g['legal_plies'],g['final_stalemate']) for g in games])
