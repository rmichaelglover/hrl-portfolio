"""Author one portable PGN study and derive the Maestro presentation from it."""
import json
from pathlib import Path
import chess
import chess.pgn

HERE = Path(__file__).resolve().parent
SOURCE = HERE / 'source-game.pgn'
with SOURCE.open() as stream:
    original = chess.pgn.read_game(stream)
chapters = []

def chapter(title, fen, intro, kind='analysis', hint='', answers=()):
    game = chess.pgn.Game()
    game.setup(chess.Board(fen))
    game.headers.update(Event=title, StudyName='The Stalemate Gambit Explained', Site='Chess Maestro',
                        White='Woodland Kingdom', Black='The visiting army',
                        Result='*', ChapterName=title)
    game.comment = intro
    chapters.append(dict(game=game, kind=kind, hint=hint, answers=list(answers)))
    return game

def line(root, moves, comments):
    node = root
    for san, comment in zip(moves.split(), comments):
        move = node.board().parse_san(san)
        node = node.add_variation(move)
        node.comment = comment
    return node

end = original.end()
g = chapter('01 · The king who refused to die', end.parent.board().fen(),
    'You have taken my army. You have surrounded my king. Before you take your victory: check whether I can still move. Black to move. Explore the historical finish first, then the three checkmates that were available. A practical rescue, not a forced draw.')
line(g, 'Qee6', ['The final door closes without a check. White has no legal move: stalemate! King Ethelheim lives to tell the tale. [%csl Gh5]'])
for san in ['Qf5#', 'Qg5#', 'Qe2#']:
    line(g, san, ['Checkmate. The difference is one check: the king is attacked and has no escape. Black could have chosen this instead of the historical stalemate.'])

g = chapter('02 · Build your own cage', end.board().fen(),
    'White to move. Try to find any legal move. There are none! Three questions explain the cage: Is the king in check? No. Can the king move safely? No. Can another white piece move? There are no others. A safe king with no legal move means stalemate, whatever the material count. Inspect g4, g5, g6, h4 and h6: Black controls every neighboring square. [%csl Gh5,Rg4,Rg5,Rg6,Rh4,Rh6]')
g.headers['Result'] = '1/2-1/2'

g = chapter('03 · The last piece must go', '8/8/8/8/8/5k2/5qR1/7K w - - 0 1',
    'White to move. King Ethelheim is nearly boxed in, but his rook can still move. Offer that last piece with check. This composed position teaches a trap: both captures draw, but Black may decline the gift by moving the king.',
    'practice', 'Put the rook on g3 with check. If Black captures it, who can still move?', ['g2g3'])
n = line(g, 'Rg3+ Kxg3', ['Castle Hessenbach offers himself on g3 with check. Ask what changes if he disappears.', 'The king takes the gift. White is not in check and has no legal move: stalemate.'])
offer = g.variations[0]
line(offer, 'Qxg3', ['The queen takes instead. The cage is complete again: stalemate. Both captures fall for the same trick.'])
line(offer, 'Ke4', ['Black declines the gift. White still has a movable rook; this is not stalemate. The sacrifice sets a trap rather than forcing a draw.'])

g = chapter('04 · The dangerous gift: promotion', '8/k1P5/2K5/8/8/8/8/8 w - - 0 1',
    'White to move. The little c-pawn is ready for a crown. Promote to a piece that avoids immediate stalemate and keeps enough material to checkmate a bare king. A queen can control too much!',
    'practice', 'A rook guards ranks and files but leaves a6 available. Which crown lets Black keep moving?', ['c7c8r'])
line(g, 'c8=R', ['A castle instead of a dragon! Black can play Ka6. The game continues with king and rook against king.'])
line(g, 'c8=Q', ['The queen controls a6 as well as the eighth rank. Black has no safe move, yet a7 is not checked: stalemate. More power has bought only half a point.'])
line(g, 'c8=B', ['Black can move, but king and bishop alone cannot checkmate a bare king. This promotion also draws.'])
line(g, 'c8=N', ['Black can move, but king and knight alone cannot checkmate a bare king. Choose the rook to retain winning material.'])

g = chapter('05 · The royal walking tour', chess.STARTING_FEN,
    'The founding game: mannyfresher against EmilioAsoXela, 3+0 blitz, 27 August 2026. Follow the king from his castle into the wilderness. The chapter pauses at story beats; the full legal game is here for replay. This is resourceful survival against missed wins, not a proven drawing opening.')
g.headers.update(White='mannyfresher', Black='EmilioAsoXela', Date='2026.08.27',
                 TimeControl='180+0', Result='1/2-1/2', Source='https://lichess.org/rdt2NZGH')
beats = {0:g.comment, 21:'11.O-O-O: the king chooses the castle with the storm outside. Watch how quickly the shelter disappears.',
    27:'14.Kd2: King Ethelheim packs a sandwich and leaves home.',
    66:'33...fxg6: the last rook disappears. White now has a king, a bishop and pawns. The emergency plan is to stay in the game and make Black finish the job.',
    76:'38...b1=Q: a new dragon joins the chase. Black has a forced mate according to the source annotations, but must still execute it.',
    91:'46.Kb5: across the board again. Locate the checks and the escape squares before continuing.',
    126:'63...Qxa4: the final white pawn falls. From now on the king has no army to keep the game moving.',
    144:'72...g1=Q: Black now has two queens, not three. The original queen and two promotions did not all survive: White captured the original queen on move 16.',
    159:'80.Kh5: one last square. Black can checkmate with Qf5, Qg5 or Qe2. The historical choice is one step away.',
    160:'80...Qee6: safe, surrounded, immobile. Stalemate. The king has survived the entire expedition.'}
node = g
for ply, move in enumerate(original.mainline_moves(), 1):
    node = node.add_variation(move)
    if ply in beats: node.comment = beats[ply]

g = chapter('06 · One last square', end.parent.parent.board().fen(),
    'White to move in the real game. Two queens loom over the king. Find the only legal escape. Moving there keeps the game alive for Black to make one final decision.',
    'practice', 'The f-file is watched. Test h5: is it attacked?', ['g6h5'])
line(g, 'Kh5 Qee6', ['The only legal move! Survival gives the opponent another decision; it does not force the eventual mistake.', 'Black closes the cage without checking. The historical game ends in stalemate.'])
line(g.variations[0], 'Qf5#', ['Black chooses checkmate instead. Even a perfectly chosen escape cannot save a position when the opponent has a forced win.'])

g = chapter('07 · The stalemate laboratory', 'k7/8/2K5/1Q6/8/8/8/8 w - - 0 1',
    'White to move. Two neighboring queen moves write opposite endings. First deliberately build a stalemate with Qb6; then rewind and find checkmate. This laboratory asks you to understand the cage well enough to create it or avoid it.',
    'practice', 'b6 closes every escape without attacking a8. b7 attacks the king too.', ['b5b6'])
line(g, 'Qb6', ['No check, no legal move: stalemate. You have built the cage. [%csl Ga8,Rb8,Rb7,Ra7]'])
line(g, 'Qb7#', ['Check and no legal escape: checkmate! The white king protects the queen on b7. One square changes the ending.'])

def frame(board):
    placement, pieces, used = {}, {}, set()
    slots = {'k':['Ke'], 'q':['Qd'], 'r':['Ra','Rh'], 'b':['Bc','Bf'], 'n':['Nb','Ng'], 'p':['P'+f for f in 'abcdefgh']}
    for square, piece in sorted(board.piece_map().items(), key=lambda x: x[1].piece_type, reverse=True):
        color = 'w' if piece.color else 'b'
        typ = piece.symbol().lower()
        candidates = slots[typ] + (slots['p'] if typ != 'p' else [])
        ident = next(color+s for s in candidates if color+s not in used)
        used.add(ident)
        placement[chess.square_name(square)] = ident
        pieces[ident] = dict(type=typ, color=color, promoted=typ if ident[1]=='P' and typ!='p' else None)
    return dict(placement=placement, pieces=pieces, note=None)

payload = []
for item in chapters:
    game = item['game']
    nodes = []
    def visit(node, parent=None):
        board = node.board()
        assert board.is_valid(), board.fen()
        index = len(nodes)
        nodes.append(dict(id=index, parent=parent, san=node.parent.board().san(node.move) if node.parent else 'Start',
                          uci=node.move.uci() if node.move else '', comment=node.comment,
                          fen=board.fen(), turn='w' if board.turn else 'b',
                          fullmove=board.fullmove_number, frame=frame(board),
                          legal=[m.uci() for m in board.legal_moves],
                          outcome='Stalemate · ½–½' if board.is_stalemate() else 'Checkmate' if board.is_checkmate() else 'Dead position · ½–½' if board.is_insufficient_material() else 'Check' if board.is_check() else '', children=[]))
        for child in node.variations:
            nodes[index]['children'].append(visit(child, index))
        return index
    visit(game)
    payload.append(dict(title=game.headers['ChapterName'], mode=item['kind'], hint=item['hint'],
                        answers=item['answers'], nodes=nodes,
                        beats=[n['id'] for n in nodes if n['comment']],
                        pgn=str(game)))
text='\n\n'.join(str(c['game']) for c in chapters)+'\n'
(HERE/'study.pgn').write_text(text)
(HERE/'study.json').write_text(json.dumps(payload, ensure_ascii=False, separators=(',',':'))+'\n')
# Verify exported PGN, including every variation and all chapter start positions.
import io
stream=io.StringIO(text)
count=0
while (game := chess.pgn.read_game(stream)) is not None:
    assert not game.errors, game.errors
    count+=1
assert count == 7
print(f'Validated {count} PGN chapters and {sum(len(c["nodes"]) for c in payload)} legal positions.')
