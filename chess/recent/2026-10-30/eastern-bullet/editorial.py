"""New fictional commentary, tied to exact positions in the supplied games.

The House/Thursday ensemble joins the Woodland pieces; opponents remain
opponents from the PGN and are never assigned invented motives or dialogue.
"""
GAMES = {}


def game(number, title, capsule, *beats):
    GAMES[number] = {'title': title, 'capsule': capsule,
                     'beats': [{'ply': p, 'san': san, 'speaker': speaker, 'text': text}
                               for p, san, speaker, text in beats]}


game(1, 'Dilorias rings the f2 doorbell',
     'The first queen exit drags the white king to f2. The continuation brings the black h-rook to g2 with check, but the recorded finish is White’s 33.Qxd7#.',
     (7,'g3','Dasha','Pause the film. From d5, Dilorias can take the rook on h1: the diagonal is d5–e4–f3–g2–h1. The deeper search finds 4...Qxh1. There was treasure before the smoke bomb.'),
     (16,'Qxf2+','Queen Dilorias','Doorbell! I have arrived on f2 carrying a check and absolutely no return ticket.'),
     (17,'Kxf2','Tara','The recorded reply is Kxf2. Nxf2 was also legal. The queen bought a pawn and a question for the king; she did not force this particular king move.'),
     (46,'Rxg2+','Glover','A rook reaches g2 with check. The understudies have found the spotlight. White can answer Kxg2, so this is another offering, not a trapped king.'),
     (65,'Qxd7#','Emanuel','The night begins with a queen sacrifice and ends with checkmate against us. Keep both pictures: the imaginative opening and the actual last square.'))

game(2, 'The bishop behind the smoke',
     'Bishop shuttles invite ...Nxc2+. The queen takes that knight, and the bishop on f5 takes the queen. The same geometry returns in game 19.',
     (11,'Bb2','Michael','The bishop has now traveled b2–c1–b2–c1–b2. A very busy doorway. Almost everyone else is still at home.'),
     (13,'Qxc2','Dasha','The queen takes the knight on c2. Trace the diagonal from f5 through e4 and d3: the bishop can reach c2.'),
     (14,'Bxc2','Queen Dilorias','Exit through the bishop’s diagonal. I would like the lighting crew to remember that diagonal next time.'),
     (80,'Qg2#','Tara','The king’s long walk ends in checkmate. In the return encounter, watch the bishop and the checking knight together.'))

game(3, 'The queen offered, the queen collected',
     'A five-move win with an important missing branch: after 4...Qxd3, White could have taken Manny’s queen with 5.Qxd3. Instead 5.Nf3 allowed ...Qxd1+.',
     (8,'Qxd3','Queen Dilorias','I take the bishop on d3 and stand directly in front of the other queen. This is an offer, not an invisibility spell.'),
     (9,'Nf3','Dasha','White develops the knight. The unplayed 5.Qxd3 would have captured the queen on d3. Now the d-file is open in the other direction.'),
     (10,'Qxd1+','Glover','Dilorias collects the opposing queen with check. Black is awarded the game here. The board is not checkmate; the PGN says Normal and does not specify the off-board cause.'))

game(4, 'Harriet tries to light the whole file',
     'A bishop, then another bishop, then a knight go toward the black king. The queens later exchange, and Black’s c-pawn becomes the decisive passer.',
     (9,'Bxe7','Michael','The bishop takes e7. Before calling it a raid, count the reply Qxe7: this visit costs a bishop.'),
     (25,'Nxh7','Harriet Hissindorf','The knight goes to h7, and I am about to run up the h-file. We have excellent enthusiasm and a rather expensive entrance fee.'),
     (35,'Qxg4+','Tara','This queen move captures Black’s queen with check; ...Rxg4 completes a queen exchange. It is not one of the fifteen unmatched queen departures.'),
     (88,'Qg4#','Emanuel','Black’s passed c-pawn promoted on c1 before the final queen checkmate. The king attack needed a forcing continuation much earlier.'))

game(5, 'The queen takes a bishop, and the pawn answers',
     'The queen-for-bishop exchange on e5 leaves White with the surviving queen. The white attack finishes on b5.',
     (14,'Ne4','Sir Banyan Blithers','The g8 knight has reached e4, where the d3 pawn can take it. A central square is useful only if the landing survives the reply.'),
     (26,'Qxe5','Queen Dilorias','I take the bishop on e5. The f4 pawn is already looking at me. We can call this a sacrifice; we must still name what it purchases.'),
     (39,'Qb5#','Glover','The white queen finds b5. A king on a5 has very little scenery left to hide behind.'))

game(6, 'JasmineKafka’s double doorway',
     'Against the export’s highest-rated opponent, the queens exchange on d4 and a knight arrives on c2 with check. Black finishes with ...g6#.',
     (16,'Qxd4','Michael','The visiting queen takes the pawn on d4. After Qxd4 Nxd4 the queens are gone, but the knight now has an excellent route.'),
     (20,'Nc2+','Dasha','The knight check on c2 reaches the king and the a1 rook. Removing queens has not removed tactics.'),
     (36,'g6#','King Ethelheim','I reached h5. The pawn on g6 supplies the final check. My travel diary needs fewer destinations and more escape squares.'))

game(7, 'Alexander’s long road to b2',
     'The a-pawn runs to a3 and captures on b2, while the king remains on e8. White’s queen and bishop then coordinate a compact mate.',
     (20,'a3','Alexander Aaronson','I am a long way from a7, and b2 is ahead. Before cheering, look behind me: the king and back rank still need a working shelter.'),
     (22,'axb2','Tara','The pawn reaches b2 by capture. White answers Bxb2; the runner is gone. The open position continues.'),
     (39,'Qe8#','Glover','The queen reaches e8, supported by the bishop’s diagonal from c6. A pawn adventure and king safety belong on the same board.'))

game(8, 'The clock awards the cloak',
     'A genuine clock win after a wild knight journey. The queen exchange is ordinary; at the final board Manny’s material is much reduced.',
     (31,'Nd6+','Sir Banyan Blithers','Check on d6! A knight in the middle of the palace makes everyone look up.'),
     (35,'Ba6','Dasha','The bishop move lets Black exchange queens with ...Qxe3+. The scan’s stronger continuation here is 18.Ne5. The knight’s landing matters more than how spectacular the route looked.'),
     (71,'Kg2','Glover','White wins on time. That is the result, full stop. It does not turn the final board into a won ending: Black still has two rooks, a bishop and a knight against our king and pawns.'))

game(9, 'The diagonal behind the checking queen',
     'The queen checks from a4, but Black’s ...Bd7 both blocks and attacks her. The next bishop move leaves that attack unanswered.',
     (39,'Qa4+','Queen Dilorias','Check from a4. A fine entrance. The reply ...Bd7 closes the check and opens a direct line back to me.'),
     (41,'Bxd3','Dasha','White takes on d3 while the bishop on d7 still attacks the queen on a4. The next recorded move is ...Bxa4.'),
     (52,'Qh1#','Tara','Black’s queen finishes on h1. After a blocked check, ask what the blocking piece now attacks.'))

game(10, 'The bare-king escape clause',
     'The king tours d7–c6–b6–a7–b8 and later stands alone. A timeout draw follows: a bare black king cannot deliver mate.',
     (8,'Kb6','King Ethelheim','The third king move in four turns. We are taking the scenic route before the pieces have found their coats.'),
     (52,'Rxg2+','Glover','The last rook offers itself on g2. Kxg2 follows. There are still black pawns to clear before the king is truly alone.'),
     (75,'Rxa5','Tara','White takes the last black pawn on a5. Black now has only a king. White still has a rook and pawns.'),
     (80,'Kb5','Dasha','The PGN records a draw by Time forfeit. The bare black king cannot mate, which explains the draw if White’s time expires. We have no move-by-move clock stamps to reconstruct the final seconds.'))

game(11, 'Dilorias returns for a final flourish',
     'White wins a bishop early, then both sides get chances. A queen raid and advanced g-pawn create activity before Black’s attack finishes.',
     (9,'Bxg4','Emanuel','The bishop on g4 is ours to take, and the record does take it. There are useful captures before the spectacular adventures begin.'),
     (41,'Be5','Michael','The bishop walks onto e5, where ...Nxe5 takes it. At this position the scan prefers Nf3. More helpers would make the later queen raid less lonely.'),
     (57,'Kh3','Queen Dilorias','The king is on h3, I am on f6, and Black’s queen will arrive on h6. The checking line and my own safety are now joined.'),
     (66,'Qf2#','Glover','The white knight visited g5 and e6, and Black’s queen collected Dilorias on f6 along the way. The final checkmate is on f2.'))

game(12, 'Banyan’s fork was already glowing',
     'A clock win with a wonderful missed alternative: 13...Nxf3+ would fork the king and queen. The recorded queen capture gives White a way back.',
     (25,'Qd4','Sir Banyan Blithers','I am the knight on e5. From f3 I would check the king on e1 and attack the queen on d4. My L-shaped doorway is already open!'),
     (26,'Qxf3','Dasha','The recorded move is the queen capture, not the knight check. The deeper recheck prefers ...Nxf3+. White now answers Qxe5+, removing the knight with check.'),
     (32,'Ne7','Glover','Black wins on time after blocking the check with ...Ne7. Keep the result, and keep the unplayed fork as a little exercise.'))

game(13, 'The castle is still on the drawing board',
     'White spends much of the opening building a pawn shell while Black’s queen and rooks enter. The game ends on time after a rook exchange.',
     (15,'h3','Ella Elouise','By move eight, every white move has been a pawn move. The shape is memorable; the pieces still need routes into it.'),
     (41,'Rxa6','Castle Andora','At last, a rook gets outside and takes on a6. There is activity, but the bishop on c6 can recapture my next c6 visit.'),
     (64,'Rxe6','Tara','Black wins on time after the rook exchange on e6. This is a useful game for trying the same shell with earlier piece development.'))

game(14, 'Harriet’s sprint past the rook alarm',
     'The queens exchange and White has real chances. Later the h-pawn sprint leaves a rook on e7 available to capture.',
     (27,'Nxc6','Sir Banyan Blithers','The queens have traded, and the knight lands on c6. This position has material to work with; there is no need to create a new queen sacrifice.'),
     (38,'Rce8','Dasha','Black has just put a rook on e8, looking at the rook on e7. The recheck prefers 20.Rxd7 for White. Name the attacked rook before sending another runner.'),
     (39,'h5','Harriet Hissindorf','I run to h5. The next move, ...Rxe7, takes our rook. My fast legs did not turn off its alarm.'),
     (50,'Nxg4','Emanuel','The g-pawn capture completes the record, followed by a Black win on time. The earlier advantage is a good place to practice keeping the whole cast involved.'))

game(15, 'The queen hears a knight coming',
     'After ...e5, White has Nf6+ followed by Nxd7, taking the queen. The black king eventually reaches b1 before White mates on b2.',
     (28,'e5','Tara','The pawn move leaves the f6 knight check available. Put the line Nf6+ Kd8 Nxd7 on the physical board before pressing on.'),
     (31,'Nxd7','Queen Dilorias','The knight reaches d7 and takes me. A check was the bridge; the queen capture was the destination.'),
     (71,'Qb2#','King Ethelheim','I have arrived on b1, having crossed almost the entire kingdom. The white queen closes the b2 door.'))

game(16, 'The knight who collected the back rank',
     'A white knight enters e5 and keeps finding targets. It later captures on d7, f8, e6 and f8 again, including the black queen.',
     (4,'Nd5','Michael','The opening knight returns to the center after Nf6. White can take it with cxd5; in the game White instead develops Nc3.'),
     (37,'Nxf8','Dasha','The knight has taken the rook on f8. Track that same knight: it will go to e6 and then return to f8 for the queen.'),
     (41,'Nxf8','Queen Dilorias','Same square, second delivery. The knight had not stopped attacking simply because the previous trophy was a rook.'),
     (71,'Qd8#','Glover','White’s queen delivers mate on d8. The knight’s tour is the pattern worth carrying out of this chapter.'))

game(17, 'The knight at the castle window',
     'The queens exchange early, then ...Nxc3+ gives White a decision. The king move leaves the d1 rook available to the knight.',
     (15,'Qxd6','Emanuel','This captures Black’s queen. ...exd6 then removes ours. It is a queen exchange, with a playable middlegame still to follow.'),
     (34,'Nxc3+','Dasha','The knight on c3 checks the king on b1 and attacks the rook on d1. The scan prefers 18.bxc3, taking the checking knight.'),
     (35,'Kc2','King Ethelheim','I step away instead, and ...Nxd1 takes the rook. The Force would have benefited from one ordinary pawn capture.'),
     (50,'Qxf2#','Glover','Black’s e-pawn promoted before the final mate. A queen-free position can grow a new queen if a passer keeps moving.'))

game(18, 'The pawn knocks on d7',
     'The white e-pawn takes a bishop on d7 with check after an unusual French structure. White keeps the initiative and mates on f7.',
     (8,'Bd7','Michael','The bishop steps onto d7 while White’s pawn on e6 attacks that square. The next move is exd7+.'),
     (10,'Ke7','King Ethelheim','The bishop is gone and the king leaves e8. The wandering begins as a response to a concrete check.'),
     (35,'Qf7#','Tara','The white queen mates on f7. Keep the pawn’s direction in view: a small piece can be the most immediate attacker.'))

game(19, 'The bishop behind the smoke, again',
     'A second encounter with luha2 repeats ...Nxc2+ Qxc2 Bxc2. This time Black later gives back a queen, but retains enough activity to win on time.',
     (7,'Nb1','Sir Banyan Blithers','Our knights have both stepped out and then back. We are demonstrating reversibility; the opponent is developing a position.'),
     (13,'Qxc2','Queen Dilorias','I take on c2 again. If the bishop on f5 looks familiar, it is because we saw this doorway in game two.'),
     (14,'Bxc2','Dasha','The same bishop diagonal takes the queen. Repeated patterns are useful even when they are patterns we would rather change.'),
     (34,'Qe2+','Emanuel','Now Black’s queen steps onto e2 with check and our knight can take it. The game still ends as a clock loss after ...Rd8, not as a neat material verdict.'))

game(20, 'A file opens under the queen',
     'Black’s f-pawn capture opens the f-file against the queen on f3; White’s h-pawn capture leaves the threat unanswered. Black’s pawn later promotes on g1 with check.',
     (24,'fxg4','Dasha','Black’s f-pawn has left the f-file. The black rook on f8 now sees down toward the queen on f3, with our pawn on h3 able to capture the pawn on g4.'),
     (25,'hxg4','Queen Dilorias','The pawn takes on g4. The next move is ...Rxf3. My file needed attention while everyone was watching the capture.'),
     (40,'fxg1=Q+','Glover','The pawn becomes a queen with check. Two moves later, that new queen finishes on f2.'))

game(21, 'Alexander reaches the seventh rank',
     'The a-pawn advances to a6 and captures on b7. Black’s coordinated rooks then outlast White’s remaining pieces.',
     (33,'axb7','Alexander Aaronson','I reach b7 by capture. This is a real promotion threat, and it deserves a look before the rooks arrive.'),
     (35,'Rxa7','Castle Andora','The rook takes on a7; the knight on c6 can take that rook. The passer’s story and the rook’s safety are intertwined.'),
     (76,'h6#','King Ethelheim','After all the rook checks and the long walk, a pawn supplies the final checkmate on h6.'))

game(22, 'The king’s early night walk',
     'Black’s king moves on turns two and four. The queen is later offered on a4, and White finishes with Qxd7#.',
     (4,'Ke7','King Ethelheim','The night is young. So is my development. I leave e8 before a knight or bishop has moved.'),
     (24,'Qa4','Queen Dilorias','I arrive on a4, where White’s queen on d4 can take me across the fourth rank. The board contains a clear invitation.'),
     (33,'Qxd7#','Tara','White takes the bishop on d7 with mate. The queen offer created no recorded escape for the king on d8.'))

game(23, 'The queen practices teleportation',
     'Four trips between c2 and d1 leave the rest of White’s position behind. A later queen visit to h5 meets ...Bg4+ and ...Bxh5.',
     (17,'Qd1','Queen Dilorias','I have now made four round trips between d1 and c2. The teleportation department reports excellent attendance and no new territory.'),
     (28,'Bg4+','Dasha','The bishop check from g4 also attacks the queen on h5. The king has to answer the check, then ...Bxh5 follows in the recorded line.'),
     (50,'Qb5#','Glover','Black’s queen finishes the king’s walk on a4. A journey can be memorable and still end exactly where the score says.'))

game(24, 'The rook nearly gets away',
     'A queen exchange opens the a-file rook adventure. After Ra8+, the rook visits a7, b7 and c7; Black takes it on c7.',
     (45,'Ra8+','Castle Andora','Check on the eighth rank! The queens have traded, and a rook has found a real line into the position.'),
     (49,'Rxb7','Tara','The rook has taken on b7 and can still retreat. Before another capture, find the enemy king’s reach.'),
     (51,'Rxc7+','Dasha','The rook takes c7 with check. Black can answer Kxc7. At the previous position the scan prefers 26.Ra7, keeping the rook.'),
     (60,'Ra8','Glover','Black wins on time after ...Ra8. This chapter is a useful comparison between an active rook and an expendable rook.'))

game(25, 'Dilorias goes through the front door',
     'The queen takes the bishop on c1 with check and is taken by a rook. White’s queen and bishops then build the finishing net.',
     (20,'Bxf3','Michael','The bishop takes the pawn on f3, and White’s queen recaptures. Count that bishop before budgeting the queen’s later entrance.'),
     (32,'Qxc1+','Queen Dilorias','I take the bishop on c1 with check. The rook on a1 can reach c1 through b1. The front door is impressively well staffed.'),
     (33,'Rxc1','Dasha','The queen has been exchanged for a bishop. There is no second enemy queen being collected in reply.'),
     (51,'Rfe1#','Glover','White’s f-rook gives mate on e1 after the black king’s long walk. Checks helped the story move, but did not restore the missing queen.'))

game(26, 'The midnight king wins on time',
     'Ethelheim tours the board, survives, trades queens late and wins on the clock. The final ...c4 leaves a knight hanging on g8.',
     (14,'Kc5','King Ethelheim','e8–e7–e6–d6–c5. Five squares, no luggage. I am touring the position while the attacking pieces try to meet me there.'),
     (40,'Kxa7','Glover','The king takes the bishop on a7. This is not an empty walk: the board has offered captures along the route.'),
     (58,'dxe6','Dasha','The queens have just exchanged on e6. This is an ordinary exchange, not one of the fifteen queen-for-material departures.'),
     (64,'c4','Tara','Black wins on time here. The board still matters for review: White could take the knight on g8 with Nxg8. Our deeper check preferred 32...Nxh6 before this move.'))

game(27, 'Castling does not teleport a queen',
     'The queen stays on d2 while Black’s pawn reaches e3. Castling long then allows that pawn to take the queen with check.',
     (26,'fxe3','Dasha','The black pawn reaches e3. It attacks d2, where the queen still stands. The threat is one diagonal step away.'),
     (27,'O-O-O','Queen Dilorias','The king and rook castle. I remain on d2. The audience may now inspect the small pawn that has booked my seat.'),
     (28,'exd2+','Tara','The pawn takes the queen with check. Castling moved two pieces, but neither was the attacked queen.'),
     (52,'Qb4#','King Ethelheim','My walk ends on a4, with the black queen mating from b4. The crucial question was already visible on d2.'))

game(28, 'The Force gets a knight-shaped warning',
     'The mirror opening becomes an active king hunt. The queen reaches g3, but ...Rg6 after Nf1 leaves her in the knight’s reach.',
     (26,'cxb3','Emanuel','The earlier ...c4+ opened a queen check and attacked the bishop. Now ...cxb3 collects that bishop. There is real tactical counterplay in the king hunt; keep that resource in the story.'),
     (46,'Qg3','Queen Dilorias','I reach g3. The rooks are preparing their entrance, the king hunt is noisy, and I am still a piece that can be taken.'),
     (49,'Nf1','Dasha','The knight on f1 attacks g3. Black has a bishop on a6 that can capture this knight along a6–b5–c4–d3–e2–f1. The deeper recheck chooses ...Bxf1.'),
     (50,'Rg6','Michael','The rook joins the attack while the knight is still aiming at the queen. One more attacker did not remove that defender.'),
     (51,'Nxg3','Queen Dilorias','Smoke bomb! A knight has collected me. The Force would like to amend the choreography before we add another rook.'),
     (63,'Qe6','Glover','The PGN ends with White winning on time after Qe6. The queen sacrifice did not produce a recorded mating finish.'))

game(29, 'The rook brings back the opposing queen',
     'Dilorias gives herself for the f3 knight. On move sixteen the c8 rook captures White’s queen with check. The recovery is real; the final win still belongs to White.',
     (8,'Qxf3','Queen Dilorias','I take the knight on f3. A pawn can take me, and the recorded reply is exf3. This is the evening’s queen-sac theme in miniature.'),
     (9,'exf3','Tara','The queen is gone, and White’s e-pawn is now on f3. When reviewing a sacrifice, keep following the other pieces instead of ending the story here.'),
     (31,'Rd7','Dasha','Look down the c-file from the rook on c8: c7, c6, c5 and c4 are empty, and White’s queen is on c3. The rook can take it with check.'),
     (32,'Rxc3+','Castle Andora','The queen is collected on c3! A rook can make a dramatic entrance without inventing a new movement rule.'),
     (37,'Rxd7','Michael','The knight has also been traded on d7. The resulting material is still not an equal refund: White retains a bishop alongside the rook.'),
     (91,'Qg2#','Glover','White promotes the f-pawn and eventually mates on g2. We keep the excellent c-file discovery, and we keep the exact result. Both belong to the night.'))

FEATURED = [1, 3, 12, 26, 28, 29, 10]
