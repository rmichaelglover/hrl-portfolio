" chess_emoji.vim — Manny's emoji chess study board for Vim (legacy Vimscript, Vim 8+)
"
" Woodland Agents = YOU (Manny), whichever color you played that game.
" Misfit Squad = the opponent.  (Set per game by the 'hero' color.)
" Empty squares are white/black square emojis; occupied squares show each
" piece's unique character emoji, which follows the piece by IDENTITY (its
" starting square) the whole game -- so Castle Andora stays Castle Andora even
" after it roams the board.
"
"   :ChessEmoji [queendab|kadas|roundup|carr|schroflag|crab|goldsmith|fathersday|houdini|daisies]   open a game
"   In the board:  l / <Right> / <Space> = next   h / <Left> = prev
"                  < = start    > = end    q = quit
"
" Alignment: emoji widths vary by terminal/font.  We use setcellwidths() to
" force every glyph to 2 cells and render with no separators, which keeps the
" grid locked.  Use a modern terminal (gnome-terminal, kitty, wezterm...) with
" a monospace font that has emoji for the best result.

if exists('g:loaded_chess_emoji') | finish | endif
let g:loaded_chess_emoji = 1

" ============================================================ the cast
" Two side-relative casts keyed by TYPE+startfile (e.g. 'Ra','Pa').
" Your side (the 'hero' color) is always the Woodland Agents; the opponent is
" always the Misfit Squad -- so the woodland creatures are always YOU.
let s:WOOD = {
\ 'Ra':['🏰','Castle Andora'],       'Nb':['🦄','Sir Banyan Blithers'],
\ 'Bc':['🛕','Popette Christiana Carolina'], 'Qd':['🐲','Queen Dilorias'],
\ 'Ke':['🦁','King Ethelheim'],      'Bf':['🧙','Pope Francisco Finochitti'],
\ 'Ng':['🐎','Dame Gertrude Goethe'], 'Rh':['🧱','Castle Hessenbach'],
\ 'Pa':['🦊','Alexander Aaronson'],  'Pb':['🦡','Bartholomew Bogerson'],
\ 'Pc':['🦝','Cais Christianson'],   'Pd':['🦌','Dorothy Dryers'],
\ 'Pe':['🦉','Ella Elouise'],        'Pf':['🐸','Frank Fassenbecher'],
\ 'Pg':['🦎','Georgiana Gina'],      'Ph':['🦔','Harriet Hissindorf'],
\ }
let s:MISFIT = {
\ 'Ra':['🏯','Akira the Keep'],      'Nb':['🦏','Bruno the Rhino'],
\ 'Bc':['🔮','Cassandra the Oracle'], 'Qd':['👸','Queen Daria'],
\ 'Ke':['🤴','King Edmund'],         'Bf':['💎','Felix the Jewel'],
\ 'Ng':['🐘','Ganesh the Elephant'], 'Rh':['🗼','Helga the Tower'],
\ 'Pa':['🤠','Annie Apple'],         'Pb':['🥳','Boomer Bash'],
\ 'Pc':['🧔','Cyrus Cobb'],          'Pd':['🔺','Delta Dot'],
\ 'Pe':['📢','Echo Edwards'],        'Pf':['💃','Fiona Fizz'],
\ 'Pg':['🏁','Gio Grand'],           'Ph':['🏨','Hank Hollis'],
\ }
" s:hero is the color (w/b) that YOU played this game; set per game on open.
let s:hero = 'b'
function! s:char(id) abort
  let suffix = strpart(a:id, 1)
  return (a:id[0] ==# s:hero) ? s:WOOD[suffix] : s:MISFIT[suffix]
endfunction
function! s:cname(id) abort
  let c = s:char(a:id)
  return c[1] . ' ' . c[0]
endfunction

" Classic chess figurines, for an uncluttered review board.
let s:GLYPH_W = {'p':'♙','n':'♘','b':'♗','r':'♖','q':'♕','k':'♔'}
let s:GLYPH_B = {'p':'♟','n':'♞','b':'♝','r':'♜','q':'♛','k':'♚'}
" Display style: 'emoji' (the cast) or 'classic' (chess figurines). Toggle with 't'.
let s:style = exists('g:chess_emoji_style') ? g:chess_emoji_style : 'emoji'
function! s:toggle_style() abort
  let s:style = (s:style ==# 'emoji') ? 'classic' : 'emoji'
  call s:render()
endfunction

" ============================================================ geometry
function! s:sign(n) abort
  return a:n > 0 ? 1 : (a:n < 0 ? -1 : 0)
endfunction
function! s:fi(sq) abort
  return char2nr(a:sq[0]) - char2nr('a')
endfunction
function! s:ri(sq) abort
  return str2nr(a:sq[1])
endfunction
function! s:sq(f, r) abort
  return nr2char(char2nr('a') + a:f) . a:r
endfunction

" ============================================================ engine (identity)
function! s:start_pos() abort
  let p = {}
  let back = {'a':'R','b':'N','c':'B','d':'Q','e':'K','f':'B','g':'N','h':'R'}
  let f = 0
  while f < 8
    let fl = nr2char(char2nr('a') + f)
    let p[fl . '2'] = 'wP' . fl
    let p[fl . '7'] = 'bP' . fl
    let p[fl . '1'] = 'w' . back[fl] . fl
    let p[fl . '8'] = 'b' . back[fl] . fl
    let f += 1
  endwhile
  return p
endfunction
function! s:fresh_pieces(pos) abort
  let pc = {}
  for sq in keys(a:pos)
    let id = a:pos[sq]
    let pc[id] = {'type': tolower(id[1]), 'color': id[0], 'promoted': ''}
  endfor
  return pc
endfunction

function! s:clear_path(pos, from, to) abort
  let df = s:sign(s:fi(a:to) - s:fi(a:from))
  let dr = s:sign(s:ri(a:to) - s:ri(a:from))
  let f = s:fi(a:from) + df
  let r = s:ri(a:from) + dr
  while f != s:fi(a:to) || r != s:ri(a:to)
    if has_key(a:pos, s:sq(f, r)) | return 0 | endif
    let f += df | let r += dr
  endwhile
  return 1
endfunction

function! s:reach(pos, pieces, from, to, iscap, ep) abort
  let id = get(a:pos, a:from, '')
  if id ==# '' | return 0 | endif
  let color = id[0]
  let type = a:pieces[id].type
  let df = s:fi(a:to) - s:fi(a:from)
  let dr = s:ri(a:to) - s:ri(a:from)
  let af = abs(df) | let ar = abs(dr)
  if type ==# 'p'
    let dir = color ==# 'w' ? 1 : -1
    let start = color ==# 'w' ? 2 : 7
    if !a:iscap
      if df != 0 | return 0 | endif
      if dr == dir && !has_key(a:pos, a:to) | return 1 | endif
      if dr == 2*dir && s:ri(a:from) == start && !has_key(a:pos, a:to)
            \ && !has_key(a:pos, s:sq(s:fi(a:from), s:ri(a:from)+dir))
        return 1
      endif
      return 0
    else
      if af == 1 && dr == dir
        if has_key(a:pos, a:to) && a:pos[a:to][0] !=# color | return 1 | endif
        if a:ep !=# '' && a:to ==# a:ep | return 1 | endif
      endif
      return 0
    endif
  elseif type ==# 'n'
    return (af==1 && ar==2) || (af==2 && ar==1)
  elseif type ==# 'b'
    return af==ar && af>0 && s:clear_path(a:pos, a:from, a:to)
  elseif type ==# 'r'
    return ((df==0) != (dr==0)) && s:clear_path(a:pos, a:from, a:to)
  elseif type ==# 'q'
    return ((af==ar && af>0) || ((df==0) != (dr==0))) && s:clear_path(a:pos, a:from, a:to)
  elseif type ==# 'k'
    return max([af, ar]) == 1
  endif
  return 0
endfunction

function! s:find_king(pos, color) abort
  let kid = a:color . 'Ke'
  for sq in keys(a:pos)
    if a:pos[sq] ==# kid | return sq | endif
  endfor
  return ''
endfunction
function! s:attacked(pos, pieces, target, by) abort
  for sq in keys(a:pos)
    if a:pos[sq][0] !=# a:by | continue | endif
    if s:reach(a:pos, a:pieces, sq, a:target, 1, '') | return 1 | endif
  endfor
  return 0
endfunction
function! s:legal_after(pos, pieces, from, to, epcap) abort
  let np = copy(a:pos)
  let color = a:pos[a:from][0]
  if a:epcap !=# '' && has_key(np, a:epcap) | call remove(np, a:epcap) | endif
  if has_key(np, a:to) | call remove(np, a:to) | endif
  let np[a:to] = np[a:from]
  call remove(np, a:from)
  let ksq = s:find_king(np, color)
  return !s:attacked(np, a:pieces, ksq, color ==# 'w' ? 'b' : 'w')
endfunction

let s:errors = []
function! s:apply_san(state, san, suffix) abort
  let pos = a:state.pos
  let pieces = a:state.pieces
  let color = a:state.turn
  let note = {'from':'','to':'','captured':'','moverId':'','promo':'','castle':''}
  let san = a:san

  if san ==# 'O-O' || san ==# 'O-O-O'
    let r = color ==# 'w' ? 1 : 8
    let ks = san ==# 'O-O'
    let kfrom = 'e' . r
    let kto = (ks ? 'g' : 'c') . r
    let rfrom = (ks ? 'h' : 'a') . r
    let rto = (ks ? 'f' : 'd') . r
    let note.moverId = pos[kfrom] | let note.from = kfrom | let note.to = kto
    let note.castle = ks ? 'K' : 'Q'
    call remove(pos, kfrom) | let pos[kto] = note.moverId
    let rid = pos[rfrom] | call remove(pos, rfrom) | let pos[rto] = rid
    let a:state.ep = ''
    let a:state.turn = color ==# 'w' ? 'b' : 'w'
    return note
  endif

  let promo = ''
  let m = matchlist(san, '=\([QRBNqrbn]\)$')
  if !empty(m)
    let promo = tolower(m[1])
    let san = substitute(san, '=[QRBNqrbn]$', '', '')
  endif

  let iscap = san =~# 'x'
  let clean = substitute(san, 'x', '', '')
  let dest = strpart(clean, len(clean)-2)
  let head = strpart(clean, 0, len(clean)-2)
  let type = 'p' | let disf = '' | let disr = 0
  if head !=# ''
    let h = head
    if h[0] =~# '[KQRBN]'
      let type = tolower(h[0]) | let h = strpart(h, 1)
    endif
    for ch in split(h, '\zs')
      if ch =~# '[a-h]' | let disf = ch
      elseif ch =~# '[1-8]' | let disr = str2nr(ch) | endif
    endfor
  endif

  let epcap = ''
  if type ==# 'p' && iscap && !has_key(pos, dest) && dest ==# a:state.ep
    let epcap = s:sq(s:fi(dest), s:ri(dest) + (color ==# 'w' ? -1 : 1))
  endif

  let cands = []
  for sq in keys(pos)
    let id = pos[sq]
    if id[0] !=# color | continue | endif
    if pieces[id].type !=# type | continue | endif
    if disf !=# '' && sq[0] !=# disf | continue | endif
    if disr && s:ri(sq) != disr | continue | endif
    if !s:reach(pos, pieces, sq, dest, iscap, a:state.ep) | continue | endif
    if !s:legal_after(pos, pieces, sq, dest, epcap) | continue | endif
    call add(cands, sq)
  endfor
  if empty(cands)
    call add(s:errors, 'no source for ' . a:san . ' (' . color . ')')
    return note
  endif
  let from = cands[0]

  let note.moverId = pos[from] | let note.from = from | let note.to = dest
  let capsq = iscap ? (epcap !=# '' ? epcap : dest) : ''
  if capsq !=# '' && has_key(pos, capsq)
    let note.captured = pos[capsq] | call remove(pos, capsq)
  endif
  call remove(pos, from) | let pos[dest] = note.moverId

  let a:state.ep = ''
  if type ==# 'p' && abs(s:ri(dest) - s:ri(from)) == 2
    let a:state.ep = s:sq(s:fi(from), (s:ri(from) + s:ri(dest)) / 2)
  endif
  if promo !=# ''
    let pieces[note.moverId].type = promo
    let pieces[note.moverId].promoted = promo
    let note.promo = promo
  endif

  let a:state.turn = color ==# 'w' ? 'b' : 'w'
  return note
endfunction

function! s:build_frames(movestr) abort
  let s:errors = []
  let pos = s:start_pos()
  let state = {'pos': pos, 'pieces': s:fresh_pieces(pos), 'turn': 'w', 'ep': ''}
  let promos = {}
  let frames = [{'pos': copy(state.pos), 'note': {}, 'suffix': '', 'san': '', 'promos': {}}]
  for tok in split(a:movestr, '\s\+')
    if tok ==# '' | continue | endif
    let suffix = matchstr(tok, '[+#]$')
    let san = substitute(tok, '[+#]$', '', '')
    let note = s:apply_san(state, san, suffix)
    if note.promo !=# '' | let promos[note.moverId] = note.promo | endif
    call add(frames, {'pos': copy(state.pos), 'note': note, 'suffix': suffix, 'san': tok, 'promos': copy(promos)})
  endfor
  return frames
endfunction

" ============================================================ narration
let s:MOVV = {
\ 'p':['advances to','marches up to','steps to','presses on to'],
\ 'n':['leaps to','bounds to','prances to','springs to'],
\ 'b':['glides to','sweeps to','slips to','sails to'],
\ 'r':['rumbles to','rolls to','swings to','charges to'],
\ 'q':['sweeps to','sails to','strides to','glides to'],
\ 'k':['steps to','strides to','shuffles to','marches to'],
\ }
let s:CAPV = ['captures','strikes down','seizes','overpowers','vanquishes','swallows']
function! s:pick(list, seed) abort
  return a:list[((a:seed % len(a:list)) + len(a:list)) % len(a:list)]
endfunction

function! s:narrate(game, i, frame) abort
  if a:i == 0
    return 'The Woodland Agents (you) take the board against the Misfit Squad. A tale of daring and creativity -- not memorizing what the machine calls "best." Step with  l / ->  and  h / <-'
  endif
  if has_key(a:game.special, string(a:i))
    return a:game.special[string(a:i)]
  endif
  let note = a:frame.note
  let mover = note.moverId
  let type = tolower(mover[1])
  let s = ''
  if note.castle !=# ''
    let s = s:cname(mover) . ' castles ' . (note.castle ==# 'K' ? 'kingside' : 'queenside') . '.'
  elseif note.captured !=# ''
    let s = s:cname(mover) . ' ' . s:pick(s:CAPV, a:i) . ' ' . s:cname(note.captured) . ' on ' . note.to . '!'
  elseif type ==# 'p'
    let s = s:cname(mover) . ' ' . s:pick(s:MOVV.p, a:i) . ' ' . note.to . '.'
  else
    let s = s:cname(mover) . ' ' . s:pick(s:MOVV[type], a:i) . ' ' . note.to . '.'
  endif
  if note.promo !=# '' | let s .= ' Crowned at last -- now a Queen! 👑' | endif
  if a:frame.suffix ==# '#' | let s .= '  Checkmate! 🏆'
  elseif a:frame.suffix ==# '+' | let s .= '  Check!' | endif
  return s
endfunction

" ============================================================ rendering
function! s:render() abort
  let game = b:chess_game
  let i = b:chess_cur
  let frame = b:chess_frames[i]
  let pos = frame.pos
  let nmoves = len(b:chess_frames) - 1

  let wtag = (s:hero ==# 'w') ? 'Woodland Agents (you)' : 'Misfit Squad'
  let btag = (s:hero ==# 'b') ? 'Woodland Agents (you)' : 'Misfit Squad'
  let lines = []
  call add(lines, '  🌲  ' . game.white . '  -- ' . wtag)
  call add(lines, '      ' . game.black . '  -- ' . btag)
  call add(lines, '      ' . game.opening . '   ·   ' . game.result)
  call add(lines, '      "Daring & creativity over the engine''s book."')
  call add(lines, '')
  let r = 8
  while r >= 1
    let row = ' ' . r . ' '
    let f = 0
    while f < 8
      let id = get(pos, s:sq(f, r), '')
      if id !=# ''
        if s:style ==# 'classic'
          let type = get(frame.promos, id, tolower(id[1]))
          let row .= (id[0] ==# 'w' ? s:GLYPH_W : s:GLYPH_B)[type] . ' '
        else
          let row .= s:char(id)[0]
        endif
      else
        let row .= ((f + r) % 2 == 0) ? '⬛' : '⬜'
      endif
      let f += 1
    endwhile
    call add(lines, row)
    let r -= 1
  endwhile
  call add(lines, '   a b c d e f g h')
  call add(lines, '')

  if i == 0
    call add(lines, '  Start position   (0 / ' . nmoves . ')')
  else
    let num = (i - 1) / 2 + 1
    let dots = ((i - 1) % 2 == 0) ? '.' : '...'
    call add(lines, '  Move ' . i . ' / ' . nmoves . '    ' . num . dots . ' ' . frame.san)
  endif
  call add(lines, '')
  for wl in s:wrap('  ' . s:narrate(game, i, frame), 58)
    call add(lines, wl)
  endfor
  call add(lines, '')
  call add(lines, '  l/->/spc next  h/<- prev  < start  > end  t style[' . s:style . ']  q quit')

  setlocal modifiable
  silent! %delete _
  call setline(1, lines)
  setlocal nomodifiable nomodified
endfunction

function! s:wrap(text, width) abort
  let words = split(a:text, ' ')
  let out = [] | let line = ''
  for w in words
    if line ==# ''
      let line = w
    elseif strchars(line) + 1 + strchars(w) > a:width
      call add(out, '  ' . line) | let line = w
    else
      let line .= ' ' . w
    endif
  endfor
  if line !=# '' | call add(out, '  ' . line) | endif
  return out
endfunction

" ============================================================ stepping & open
function! s:step(d) abort
  let last = len(b:chess_frames) - 1
  let n = b:chess_cur + a:d
  let b:chess_cur = n < 0 ? 0 : (n > last ? last : n)
  call s:render()
endfunction
function! s:jump(n) abort
  let last = len(b:chess_frames) - 1
  let b:chess_cur = a:n < 0 ? last : (a:n > last ? last : a:n)
  call s:render()
endfunction

function! s:open(name) abort
  if !has_key(g:chess_emoji_games, a:name)
    echohl ErrorMsg | echo 'No such game: ' . a:name . '  (try: ' . join(keys(g:chess_emoji_games), ', ') . ')' | echohl NONE
    return
  endif
  if exists('*setcellwidths')
    silent! call setcellwidths([[0x2B1B, 0x2B1C, 2], [0x1F300, 0x1FAFF, 2]])
  endif
  let game = g:chess_emoji_games[a:name]
  let s:hero = get(game, 'hero', 'b')
  let frames = s:build_frames(game.moves)
  if !empty(s:errors)
    echohl ErrorMsg | echo 'Engine errors: ' . join(s:errors, '; ') | echohl NONE
  endif

  let bn = bufnr('[ChessEmoji]')
  if bn > 0 && bufexists(bn)
    execute 'buffer' bn
  else
    silent enew
    silent! file [ChessEmoji]
  endif
  setlocal buftype=nofile bufhidden=hide noswapfile nowrap nonumber norelativenumber nolist nocursorline

  " colour classic figurines by side (no effect in emoji style)
  if !exists('g:syntax_on') | silent! syntax enable | endif
  syntax clear
  syntax match ceWhitePiece /[♔♕♖♗♘♙]/
  syntax match ceBlackPiece /[♚♛♜♝♞♟]/
  highlight default ceWhitePiece ctermfg=231 cterm=bold guifg=#ffffff gui=bold
  highlight default ceBlackPiece ctermfg=111 cterm=bold guifg=#88aaff gui=bold

  let b:chess_game = game
  let b:chess_frames = frames
  let b:chess_cur = 0

  nnoremap <buffer><silent> l       :call <SID>step(1)<CR>
  nnoremap <buffer><silent> <Right> :call <SID>step(1)<CR>
  nnoremap <buffer><silent> <Space> :call <SID>step(1)<CR>
  nnoremap <buffer><silent> h       :call <SID>step(-1)<CR>
  nnoremap <buffer><silent> <Left>  :call <SID>step(-1)<CR>
  nnoremap <buffer><silent> <       :call <SID>jump(0)<CR>
  nnoremap <buffer><silent> >       :call <SID>jump(-1)<CR>
  nnoremap <buffer><silent> t       :call <SID>toggle_style()<CR>
  nnoremap <buffer><silent> q       :bdelete!<CR>

  call s:render()
endfunction

function! s:complete(A, L, P) abort
  return filter(keys(g:chess_emoji_games), 'v:val =~ "^" . a:A')
endfunction
command! -nargs=? -complete=customlist,s:complete ChessEmoji
      \ call s:open(empty(<q-args>) ? 'queendab' : <q-args>)
command! -bar ChessNext call s:step(1)
command! -bar ChessPrev call s:step(-1)

function! s:selftest() abort
  let out = []
  for [name, wp, wsuf, wmover] in [['queendab',63,'#','wQd'],['kadas',33,'#','wQd'],['roundup',45,'#','wQd'],['carr',44,'#','bRh'],['schroflag',58,'','bQd'],['horsey',42,'','bQd'],['crabblack',52,'#','bRa'],['crab',87,'#','wNb'],['goldsmith',80,'#','bBc'],['fathersday',60,'#','bNb'],['houdini',39,'#','wQd'],['daisies',135,'','wKe']]
    let s:hero = get(g:chess_emoji_games[name], 'hero', 'b')
    let fr = s:build_frames(g:chess_emoji_games[name].moves)
    let plies = len(fr) - 1
    let last = fr[-1]
    call add(out, name . ': plies=' . plies . (plies==wp?' OK':' BAD(want '.wp.')')
          \ . ' errors=' . len(s:errors)
          \ . ' last=' . last.san . ' mover=' . last.note.moverId
          \ . ((last.suffix==#wsuf && last.note.moverId==#wmover) ? ' OK' : ' BAD'))
    call add(out, '   -> ' . s:narrate(g:chess_emoji_games[name], plies, last))
  endfor
  return out
endfunction
function! g:ChessEmojiSelfTest() abort
  return s:selftest()
endfunction

" ============================================================ games
let g:chess_emoji_games = {}

" The flagship Queen Dab: Manny (1104, White) dabs on Arya864 (1586).
let g:chess_emoji_games['queendab'] = {
\ 'white':'mannyfresher (1104)', 'black':'Arya864 (1586)', 'hero':'w',
\ 'opening':'The Queen Dab  (vs +482 Elo!)', 'result':'White wins! 1-0',
\ 'moves':'d3 e5 e4 Nf6 f4 Nc6 g4 d6 h3 h6 g5 hxg5 fxg5 Nh5 Nc3 Nf4 h4 Be7 Nd5 Bxg5 Nf3 Bxh4+ Nxh4 Rxh4 Rg1 g5 Bxf4 exf4 Nxc7+ Qxc7 Rxg5 Ke7 Qd2 Nd4 O-O-O Nf3 Qg2 Nd4 Rg8 Ne6 Be2 Qc5 Bg4 Qe3+ Kb1 a5 Bxe6 Kxe6 d4 d5 Qg5 Qxe4 Qxh4 Kd6 Qh6+ Kc7 Rg7 b6 Rxf7+ Kb8 Qxb6+ Bb7 Qxb7#',
\ 'special':{
\   '1':'🕺 The QUEEN DAB begins! 1.d3 -- King Ethelheim''s 🦁 pawns will fling out like a dabbing arm (d3-e4-f4-g4) while Queen Dilorias 🐲 tucks in snug behind them. And ''dab'' is also what you do to a much stronger opponent: 1104 vs 1586. The book says this is dubious. The book is about to lose.',
\   '7':'g4! The pawn-arm fully extends -- d3, e4, f4, g4 -- the unmistakable Queen Dab pose. Her Majesty waits, coiled, behind the wall. No engine would play this. That is the point.',
\   '19':'Nd5?? A wild lurch -- but the Queen Dab THRIVES in chaos. Both armies trade blunders for the next twenty dizzy moves while Queen Dilorias 🐲 bides her time.',
\   '33':'Qd2. Queen Dilorias 🐲 finally stirs, still tucked behind her pawns -- patient, coiled, waiting to spring out and dab.',
\   '50':'d5?? The last crack, played on the increment. Queen Dilorias 🐲 smells blood and uncoils.',
\   '60':'Kb8?? -- straight into the net. The dab is now unstoppable.',
\   '63':'Qxb7# -- Queen Dilorias 🐲 DABS on b7! Checkmate. An 1104 just dabbed on a 1586 -- daring beat the database. 🕺🏆',
\ }}

" Kádas Stampede: Manny (1108, White) sends the queen on a lone rampage to mate.
let g:chess_emoji_games['kadas'] = {
\ 'white':'mannyfresher (1108)', 'black':'CTKCRONOS (1207)', 'hero':'w',
\ 'opening':'Kádas Stampede  (1.h4)', 'result':'White wins! 1-0',
\ 'moves':'h4 e5 g3 Bc5 a4 Qf6 e3 a5 b3 Nh6 Qh5 O-O Bc4 e4 Ra2 d6 Nh3 Bg4 Qd5 c6 Qg5 Qf3 Nf4 Qxh1+ Bf1 Bc8 Nh5 g6 Qxh6 Bd4 exd4 Bh3 Qg7#',
\ 'special':{
\   '1':'🐎 The KÁDAS STAMPEDE! 1.h4 -- Harriet Hissindorf 🦔 trots out on the rim, an offbeat first hoofbeat. No centre, no theory, just a strange little shove that says: we are doing this MY way.',
\   '11':'Qh5! Where the Queen Dab tucks Her Majesty BEHIND the pawns, the Stampede does the opposite -- Queen Dilorias 🐲 breaks ranks on move 6 and rides OUT, alone, into the open. The book gasps. The dragon does not care.',
\   '19':'Qd5. h5 to d5 -- Queen Dilorias 🐲 gallops clear across the board, a one-dragon cavalry charge. Develop your pieces, says the book. She IS the pieces.',
\   '21':'Qg5. And back again -- d5 to g5. She will not sit still, she will not come home. The whole enemy camp is now within a single furious hoofbeat.',
\   '24':'Qxh1+ -- Black snatches Castle Hessenbach 🧱 in the corner, WITH CHECK. "Take the free rook back!" howls the book. A whole rook, just sitting there. Watch what Manny does next.',
\   '25':'Bf1. Pope Francisco 🧙 quietly steps in front, and Queen Dilorias 🐲 does not so much as glance over her shoulder at the lost rook. Material is for accountants. The stampede only goes forward.',
\   '29':'Qxh6 -- she crashes through and devours the knight. The net draws tight; the enemy king feels the ground shaking.',
\   '33':'Qg7# -- Queen Dilorias 🐲 STAMPEDES onto g7. Checkmate. One queen, end to end, never once retreating, a whole rook left on the table behind her. She never wanted it. She wanted the king. 🐲🏆',
\ }}

" The Kádas Roundup: Manny (1086, White) herds the enemy king clear across the board into a mating net.
let g:chess_emoji_games['roundup'] = {
\ 'white':'mannyfresher (1086)', 'black':'mostafa272727 (1086)', 'hero':'w',
\ 'opening':'Kádas Roundup  (1.h4)', 'result':'White wins! 1-0',
\ 'moves':'h4 d5 h5 g5 hxg6 fxg6 a4 e5 a5 b5 axb6 cxb6 d4 e4 f3 exf3 Nxf3 Bf5 e3 Nc6 Bb5 Qc7 Ne5 O-O-O Nxc6 Qg3+ Kf1 Rd6 Nxa7+ Kb7 Be8 Ne7 Qe2 Bg7 Qa6+ Kb8 Nc6+ Rxc6 Qa8+ Kc7 Ra7+ Kd6 Qd8+ Ke6 Qxe7#',
\ 'special':{
\   '1':'🤠 THE KÁDAS ROUNDUP! 1.h4 -- Harriet Hissindorf 🦔 trots out on the rim again, the same offbeat Kádas hoofbeat that opened the Stampede. But where the Stampede sent one lone queen charging, today the whole posse rides. Saddle up.',
\   '9':'a5! Now BOTH rook-pawns are riding -- the h-file and the a-file, two outriders fanning out wide across the prairie. Where the Crab pinches, the Roundup encircles. The herd doesn''t know it yet, but the fences are going up.',
\   '29':'Nxa7+ -- Dame Gertrude Goethe 🐎 gallops deep behind the lines and snaps up the a7 pawn with check, kicking the corral gate wide open. The open a-file is now a chute, and the enemy king is standing right in it.',
\   '35':'Qa6+ -- and the ROUNDUP is on. Queen Dilorias 🐲 swings out to a6 and starts driving. From here the black king will be herded clear across the board -- b8, c7, d6 -- with nowhere to bolt but forward, into the open.',
\   '37':'Nc6+! Dame Gertrude Goethe 🐎 throws herself square in front of the king -- take her (Rxc6), it only spooks the herd onward. Every check is another crack of the whip, moving the king exactly where Manny wants him.',
\   '41':'Ra7+ -- Castle Andora 🏰 thunders up the open a-file to join the drive. Queen, knight, and now rook: the whole posse is on horseback, and the king is fully surrounded, stampeding into the centre against his will.',
\   '43':'Qd8+ -- the gate swings shut behind him. The king is roped, the prairie has run out. One square left, and it is not a safe one.',
\   '45':'Qxe7# -- Queen Dilorias 🐲 ropes the king at e7. Checkmate. From b8 to e6, driven the whole width of the board and penned. The Kádas Roundup: you do not chase the king, you herd him. 🐲🤠🏆',
\ }}

" The Carr Crash: Manny (1096, Black) wins a blunder-strewn brawl by doubling rooks down the h-file.
let g:chess_emoji_games['carr'] = {
\ 'white':'gzl1zz13 (1094)', 'black':'mannyfresher (1096)', 'hero':'b',
\ 'opening':'Carr Defence  (1.e4 h6)', 'result':'Black wins! 0-1',
\ 'moves':'e4 h6 f4 g6 Nf3 f6 c4 e6 Bd3 d6 O-O c6 Nc3 b6 b3 a6 g3 e5 Qe2 Bh3 Re1 Qd7 Bb2 Qg4 Na4 h5 Nxb6 Ra7 Nc8 Rah7 fxe5 h4 exd6 hxg3 d7+ Nxd7 hxg3 Qxg3+ Kh1 Bf1+ Nh2 Rxh2+ Qxh2 Rxh2#',
\ 'special':{
\   '2':'h6 -- the CARR DEFENCE. Harriet Hissindorf 🦔 pokes out one shy little pawn and the engine just shrugs. No centre, no theory, only a quiet "we do this our way." The book calls it dubious; Manny calls it Tuesday.',
\   '6':'f6. Harriet 🦔, then Georgiana Gina 🦎, now Frank Fassenbecher 🐸 -- h6, g6, f6, a crooked little wall the textbooks would faint at. It looks like nonsense. It is about to become a launch ramp.',
\   '24':'Qg4. Queen Dilorias 🐲 slides out to g4 and fixes one yellow eye on the white king. The dragon has found where he sleeps.',
\   '28':'Ra7. Castle Andora 🏰 steps off the back rank -- a rook lift. Not forward. Sideways. Curious.',
\   '30':'Rah7! Castle Andora 🏰 swings the whole way across to h7. Now the idea bares its teeth: the h-file Harriet pried open is an open highway, and a castle is rolling down it.',
\   '38':'Qxg3+. The dam breaks -- Queen Dilorias 🐲 smashes onto g3 with check. Suddenly the white king is very, very alone.',
\   '40':'Bf1+! Popette Christiana Carolina 🛕 tiptoes behind the lines to f1, check -- and quietly bolts the g2 escape hatch shut. The net pulls tight.',
\   '42':'Rxh2+. Castle Andora 🏰 crashes down onto h2 and offers herself to the queen. Take her. Please.',
\   '44':'Rxh2# -- and here comes the SECOND castle! Castle Hessenbach 🧱 thunders down the very same h-file. Checkmate. The Carr Crash: two rooks, one lane, no survivors. 🧱🏆',
\ }}

" Schrödinger's Flag: Manny (1084, Black) wins on time after a wild never-collapsing brawl -- the woodland glitches into its quantum form.
let g:chess_emoji_games['schroflag'] = {
\ 'white':'lifewavepr (1083)', 'black':'mannyfresher (1084)', 'hero':'b',
\ 'opening':'Schrödinger''s Flag  (1...h5, Zukertort)', 'result':'Black wins on time! 0-1',
\ 'moves':'Nf3 h5 e4 h4 h3 a5 a4 d5 exd5 Qxd5 Nc3 Qe6+ Be2 Qg6 O-O Bxh3 Nxh4 Rxh4 g3 Rf4 d3 Rxf2 Kxf2 Bxf1 Bxf1 Qb6+ d4 Nc6 Bb5 Rd8 Kg2 Rxd4 Bd2 e5 Qf3 Rxd2+ Kh3 g5 Re1 f6 Qf5 Qd4 Qe6+ Ne7 Qxf6 g4+ Kh4 Rh2+ Kg5 Bh6+ Qxh6 Rxh6 Kxh6 Ng8+ Kg6 Kf8 Rg1 Qxg1',
\ 'special':{
\   '2':'1...h5 -- and the woodland glitches. Harriet Hissindorf 🦔 flickers at the edge of the board, half hedgehog, half edge-quantum, and flings herself to h5. We are not opening a game; we are perturbing the lattice. Off-book, off-grid -- the eval bar begins to shimmer like a qubit that refuses to be measured.',
\   '16':'8...Bxh3 -- White castles into the storm and the whole field inverts. Popette Christiana Carolina 🛕, pixelating into a beam of violet amplitude, phases through to h3 and takes the pawn. The advantage tunnels from White to Black in a single flicker.',
\   '22':'11...Rxf2 -- Castle Hessenbach 🧱 stops being a castle. It smears down the f-file as pure probability current and crashes into f2. White swallows it, but it barely matters: the position is now a standing wave, winning and losing at once.',
\   '28':'14...Nc6 -- Sir Banyan Blithers 🦄 leaps out and is pinned to the king by the b5 bishop: a particle frozen in a potential well, present but unable to act for the rest of the game. Even the glitches have their trapped states.',
\   '36':'18...Rxd2+ -- Castle Andora 🏰, now a glowing strand of charge, tears across to d2 with check. Watch the eval breathe: zero, then minus five, the board oscillating like a time crystal that will not come to rest.',
\   '54':'27...Ng8+ -- mate was RIGHT THERE. A clean collapse to checkmate, the wave finally breaking -- and instead Dame Gertrude Goethe 🐎, glitching between horse and hologram, phases back to g8. The superposition holds. The kingdom flickers. Nothing resolves.',
\   '58':'29...Qxg1 -- and with the board still shimmering between every possible future, White''s clock hits zero. Decoherence. Queen Dilorias 🐲, dragon and eigenstate at once, scoops the final rook as time -- not a mating net -- collapses the wave. Black wins on the flag, and the woodland reassembles, victorious, in a world made of light. 🐲⚡🏆',
\ }}

" Horsey Surprise: Manny (Black) wins with knight-first Nimzowitsch chaos.
let g:chess_emoji_games['horsey'] = {
\ 'white':'steveagustin123games (1106)', 'black':'mannyfresher (1105)', 'hero':'b',
\ 'opening':'Horsey Surprise (Nimzowitsch Defense)', 'result':'Black wins! 0-1 (resign)',
\ 'moves':'e4 Nc6 d4 Nf6 e5 Ne4 Nf3 d5 Qd3 Qd7 c4 Qg4 h3 Qg6 cxd5 Bf5 Qe3 Nb4 Na3 O-O-O Nh4 Qh5 Nxf5 Qxf5 d6 exd6 exd6 Bxd6 Bd2 Rhe8 Be2 Bf4 g4 Qf6 Qxf4 Qxd4 O-O Nxd2 Rfd1 Rxe2 Nc2 Qxf4',
\ 'special':{
\   '1':'The HORSEY SURPRISE! 1...Nc6 -- the Nimzowitsch Defense. The horses come out FIRST, before the pawns are sorted, daring White to make sense of the chaos.',
\   '6':'Ne4! Dame Gertrude Goethe 🐎 gallops smack into the middle of the board on move 3. The book clutches its pearls.',
\   '18':'Nb4! Sir Banyan Blithers 🦄 leaps to the rim, eyeing c2 and d3. Suddenly horses are everywhere.',
\   '38':'Nxd2! Sir Banyan Blithers 🦄 crashes in and grabs a piece. The surprise is paying off.',
\   '42':'Qxf4 -- Queen Dilorias 🐲 scoops up the enemy queen, and White RESIGNS. The Horsey Surprise rides home. 🐴🏆',
\ }}

" The former 'queendab' -- correctly a Crab (Manny as Black).
let g:chess_emoji_games['crabblack'] = {
\ 'white':'chessnegi (1044)', 'black':'mannyfresher (1071)', 'hero':'b',
\ 'opening':'The Crab  (as Black)', 'result':'Black wins! 0-1',
\ 'moves':'d4 h5 Bf4 h4 h3 d6 Nf3 a5 e3 a4 c3 e6 Bd3 d5 Nbd2 a3 b3 c5 e4 dxe4 Nxe4 b6 dxc5 Bb7 Bb5+ Nc6 Bxc6+ Bxc6 Qxd8+ Rxd8 Nfd2 bxc5 O-O-O Rh5 Rhe1 Rhd5 f3 Rd3 Kc2 Nf6 Nc4 Nxe4 fxe4 Bxe4 Nd6+ Bxd6 Bxd6 R8xd6 Rxe4 Rxd1 Rxh4 R6d2#',
\ 'special':{
\   '2':'The Crab begins! Harriet Hissindorf 🦔 lunges to h5 -- one claw of the Crab, the rook-pawns reaching out wide.',
\   '8':'Alexander Aaronson 🦊 sets off up the a-file -- the second claw extends.',
\   '16':'...a3! Alexander Aaronson 🦊 plants himself deep in White''s camp. Both rook-pawns advanced -- the Crab''s pincers are fully set.',
\   '27':'Bxc6+?? A slip by White''s bishop. The advantage leaks toward the Woodland Agents.',
\   '42':'Nxe4?? Sir Banyan Blithers 🦄 grabs a pawn but blunders! For a moment, White is winning...',
\   '43':'fxe4?? ...but White blunders right back! An eight-point swing in two half-moves.',
\   '51':'Rxh4?? The fatal grab. White''s rook walks into the trap...',
\   '52':'R6d2# -- Castle Andora 🏰 crashes to d2 for checkmate! The Crab pinches shut. 🏆',
\ }}

let g:chess_emoji_games['crab'] = {
\ 'white':'mannyfresher (1081)', 'black':'Bandapallijeshwanth (1073)', 'hero':'w',
\ 'opening':'Kadas Opening (the Crab)', 'result':'White wins! 1-0',
\ 'moves':'h4 d5 h5 h6 a4 Nf6 a5 Bg4 f3 Bxh5 g4 Bg6 Bh3 Nc6 f4 Be4 Rh2 Qd7 g5 Bf5 gxf6 Bxh3 fxg7 Bxg7 Rxh3 O-O d3 Nd4 f5 Nxf5 e4 dxe4 Qg4 e6 a6 bxa6 Ra5 Qd4 Bxh6 Qb4+ c3 Qxa5 Bxg7 Nxg7 Qh4 Nh5 Qxh5 Qxh5 Rxh5 Rab8 b4 a5 Nd2 axb4 Nxe4 b3 Rg5+ Kh7 Nf6+ Kh6 Nf3 b2 Ng4+ Kh7 Nf6+ Kh6 Ng4+ Kh7 Rh5+ Kg6 Rh6+ Kg7 Kf2 b1=Q Kg3 Qxd3 Kf4 Qd6+ Kg5 Qc5+ Kh4 Qe7+ Ng5 Rb1 Rh7+ Kg8 Nh6#',
\ 'special':{} }

let g:chess_emoji_games['goldsmith'] = {
\ 'white':'Joe-Fouche (1092)', 'black':'mannyfresher (1099)', 'hero':'b',
\ 'opening':'Goldsmith Defense', 'result':'Black wins! 0-1',
\ 'moves':'e4 h5 Bc4 h4 Qf3 e6 e5 Qg5 Nh3 Qxe5+ Kf1 Nc6 d3 Nd4 Qf4 Qxf4 Nxf4 Nxc2 Nc3 Nxa1 Ke2 b6 Be3 Nc2 a3 Bb7 Bd2 h3 gxh3 Bxh1 Kd1 Nd4 Be3 Nf3 Ne4 e5 Nd5 O-O-O Ba6+ Kb8 b4 Rxh3 a4 Rxh2 a5 Bg2 axb6 Rh1+ Kc2 c6 b7 cxd5 Nd6 Bxd6 b5 Ba3 b6 axb6 Bxb6 Re8 Kb3 Ra1 d4 Nd2+ Kc2 Bb4 Kb2 Rxa6 Kc2 Rxb6 f4 Be4+ Kd1 Kxb7 dxe5 Rc8 e6 Rxe6 f5 Bf3#',
\ 'special':{} }

" Father's Day Surprise: Manny (pappymagee, 1066, Black) marches the a-pawn a5->a1=Q amid a queen melee, then mates with the surviving knight.
let g:chess_emoji_games['fathersday'] = {
\ 'white':'vonEdeurn (1118)', 'black':'pappymagee (1066)', 'hero':'b',
\ 'opening':'Father''s Day Surprise  (Goldsmith Defense)', 'result':'Black wins! 0-1',
\ 'moves':'e4 h5 g4 h4 h3 e5 f3 d5 Nc3 d4 Nd5 Be6 Bc4 c6 Nb6 Qxb6 Bxe6 fxe6 d3 Bb4+ Bd2 Bxd2+ Qxd2 Qxb2 Rd1 Qxa2 Ne2 a5 Rc1 a4 Qg5 Rh7 Kd2 a3 Qg6+ Kd7 Qxh7 Qb2 Qxg8 a2 Qxg7+ Kc8 Qxe5 a1=Q Rxa1 Rxa1 Rxa1 Qxa1 Qxe6+ Nd7 Qe8+ Kc7 Qe5+ Nxe5 f4 Qa5+ Kd1 Qa1+ Kd2 Nf3#',
\ 'special':{
\   '2':'🎁 THE FATHER''S DAY SURPRISE! 1...h5 -- the Goldsmith Defence. Harriet Hissindorf 🦔 flips the rook-pawn up the board on move one, the cheeky shove the engine scolds and Manny adores. Unwrap it slowly: we are not here for the book today, we are here for the fun.',
\   '28':'a5 -- and watch the edge of the board. Alexander Aaronson 🦊, the smallest fox in the kingdom, sets off alone up the a-file. No one is guarding him. No one thinks he matters. Remember his name.',
\   '34':'a3 -- the little fox is now THREE squares deep in White''s camp, tiptoeing past sleeping giants. The whole centre is a brawl of queens and bishops; nobody is watching the quiet pawn on the rim.',
\   '40':'a2 -- one step from glory. Alexander Aaronson 🦊 stands on the doorstep of the back rank while White''s queen goes greedily rampaging on the far wing, snatching rook and knight and pawn. Let her feast. The fox has somewhere to be.',
\   '44':'a1=Q!! Alexander Aaronson 🦊 reaches the end of his long walk and stands up a QUEEN. The littlest pawn, crowned -- a whole new dragon born on the back rank. This is the surprise inside the box.',
\   '48':'...Qxa1 -- and just like that the newborn queen is traded off in a flurry, a1 changing hands again and again. White has hoarded an avalanche of material. On paper she is winning. On the board her king is naked, and it is Black to dream.',
\   '54':'27.Qe5+?? Nxe5 -- the last greedy check walks straight into Sir Banyan Blithers 🦄. White''s queen, fat with plunder, vanishes. All those captured pieces meant nothing; the bare king means everything.',
\   '60':'30...Nf3# -- Sir Banyan Blithers 🦄 springs to f3 and the trap snaps shut. Checkmate! Just as the first Goldsmith ended on f3, so does this one -- a bishop there, a knight here. The fox marched, the queens fell, and the quiet knight delivered the Father''s Day Surprise. 🦄🎁🏆',
\ }}

" The Kádas Houdini: Manny (pappymagee, 923, White) is dead lost (Black missed mate-in-12 AND mate-in-1), then swindles the win as the h-pawn sets up Qxg7#.
let g:chess_emoji_games['houdini'] = {
\ 'white':'pappymagee (923)', 'black':'ryhilism (903)', 'hero':'w',
\ 'opening':'Kádas Houdini  (1.h4)', 'result':'White wins! 1-0',
\ 'moves':'h4 e5 h5 d5 e4 dxe4 d4 exd4 f4 Nc6 c4 Nf6 g3 Bg4 Be2 Bb4+ Bd2 d3 Bxg4 Qd4 Bc3 Qe3+ Ne2 Nxg4 Qd2 Qf2+ Kd1 Ne3+ Kc1 O-O h6 dxe2 Bxb4 Nxc4 Qc3 e1=Q+ Rxe1 e3 Qxg7#',
\ 'special':{
\   '1':'🎩 THE KÁDAS HOUDINI! 1.h4 -- Harriet Hissindorf 🦔 hops out on the rim once more. The engine frowns from move one and keeps frowning: this game is about to go very, very wrong for the Woodland Agents... and then, impossibly, right.',
\   '28':'Ne3+ -- King Ethelheim 🦁 is hounded into the corner, a knight on e3, a black queen on f2, the eval bar a ten-point cliff. By every honest measure the Woodland Agents are lost. Houdini, too, always began the trick already locked inside the box.',
\   '31':'31.h6. Amid the wreckage, one tiny thing goes right: Harriet Hissindorf 🦔 inches to h6. Nobody notices the hedgehog on the sixth rank. Nobody ever does. Remember her.',
\   '34':'34...Nxc4?? The first miracle. The Misfits had a forced mate in TWELVE on the board -- and reached for a free pawn instead. The chains are still locked, but a hand is fumbling for the key on the wrong side.',
\   '36':'36...e1=Q+?? A second new queen for Black, a second wrong turn -- the check leads nowhere and hands the spark back. Houdini is halfway out of the irons and the crowd doesn''t know it yet.',
\   '38':'38...e3?? The final gift. Black had mate in ONE with a simple check -- and pushed a quiet pawn instead. The door swings wide. One move for the Woodland Agents now. Just one.',
\   '39':'39.Qxg7# -- Queen Dilorias 🐲 crashes onto g7, guarded by little Harriet 🦔 on h6, and it is CHECKMATE. From dead lost -- mate-in-twelve and mate-in-one both against her -- the dragon slips the box and takes a bow. The Kádas Houdini: never count out a player who thrives in chaos. 🎩🐲🏆',
\ }}

" We're No Daisies: Manny (pappymagee, 981, Black) is winning all game, misses forced mates, gets out-blundered, and it ends in stalemate -- narrated as Doc Holliday (Tombstone, 1993).
let g:chess_emoji_games['daisies'] = {
\ 'white':'lastonefastone (1104)', 'black':'pappymagee (981)', 'hero':'b',
\ 'opening':'We''re No Daisies  (Goldsmith Defense)', 'result':'Draw by stalemate  ½-½',
\ 'moves':'e4 h5 Nf3 h4 g3 hxg3 fxg3 e5 Nxe5 d6 Nc4 Qg5 d3 Bg4 Be2 Bxe2 Kxe2 Qh5+ Ke1 Qxd1+ Kxd1 c6 e5 d5 Nd6+ Bxd6 exd6 Kd7 Bf4 f6 c4 g5 c5 gxf4 gxf4 Na6 b4 Nxb4 Nc3 Nxd3 Rb1 Nf2+ Ke2 Nxh1 Rxb7+ Ke6 d7 Rxh2+ Kd3 Nf2+ Ke3 Ng4+ Kf3 N8h6 Kg3 Rg8 Kf3 Rf2+ Kg3 Nh2+ Kxf2 N6g4+ Ke2 d4 Ne4 Kd5 Nd6 Ne3 Kd3 Nhf1 Nf7 Kxc5 d8=Q Rxd8 Nxd8 a5 Ne6+ Kd5 Nxd4 c5 Rb5 a4 Nc2 Nc4 Kc3 f5 Rb1 Ng3 Rd1+ Kc6 Kxc4 Ne4 Rd5 Nd6+ Rxd6+ Kxd6 Ne3 Ke6 Kxc5 a3 Kb5 Kf6 Kb4 Ke6 Kxa3 Kf6 Kb4 Ke6 a4 Kf6 a5 Ke6 a6 Kf6 a7 Ke6 a8=Q Kf6 Qa5 Ke6 Qxf5+ Kd6 Kc4 Kc6 Qd5+ Kb6 Qc5+ Kb7 Kb5 Kb8 Qc6 Ka7 Qb6+ Ka8 Ka6',
\ 'special':{
\   '2':'🤠 “I''m your huckleberry.” 1...h5 -- the Goldsmith again, that crooked rim-pawn Manny flicks out like a card skimmed across a saloon table. The book frowns; Doc Holliday just smiles through the fever. We did not come to play correct. We came to play.',
\   '15':'8.Be2?? -- now here is a thing of beauty. Black hangs the queen with 7...Bg4, plain as a tin star in the sun -- and White, with the shot lined up (8.Bxg5!), looks clean the other way and plays Be2. Two gunfighters, both with the draw, both studyin'' their boots. Forgive me: neither of us is a daisy.',
\   '44':'22...Nxh1 -- the horses are loose in the streets now, Sir Banyan 🦄 and Dame Gertrude 🐎 kickin'' in doors and helpin'' themselves to a rook in the corner. Black is winning by a wagonload; the eval bar reads like a death warrant for White. It is not revenge he''s after. It''s a reckonin''.',
\   '60':'30...Nh2+?? -- and the reckonin'' slips through our fingers. 30...Nf5+ was mate in two, sittin'' there pretty as a daisy in a gun barrel, and we checked sideways instead and let the man breathe. Doc coughs into his handkerchief and says not one word.',
\   '117':'59.a8=Q -- well now. While our horses pranced and fumbled their mates, one lonesome white pawn walked the whole length of Tombstone and strolled back a queen. The board turns clean over. Manny -- a piece up since the first act -- is suddenly the one starin'' down the barrel. My hypocrisy, it seems, knows no bounds.',
\   '135':'68.Ka6 -- stalemate. After 135 moves of missed mates on BOTH sides, forced wins tossed away like losing cards, the white king backs himself into a corner and Black hasn''t a legal move left. A draw nobody earned and nobody deserved. “You''re no daisy. You''re no daisy at all.” Neither of us was -- not today. 🤠🃏 ½',
\ }}
