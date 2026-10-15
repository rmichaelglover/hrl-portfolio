"""Explicit fictional hole-merger rules; no gravitational or chess-value claims."""
import hashlib
import json
import copy
import chess

POLICIES={'record','imprison','constrain','release'}


class HoleTopology:
    def __init__(self,board):
        self.pieces={}
        self.at={}
        for square,piece in board.piece_map().items():
            identifier=f'{"w" if piece.color else "b"}-{piece.symbol().lower()}-{chess.square_name(square)}'
            self.pieces[identifier]={'id':identifier,'color':'white' if piece.color else 'black',
                'type':piece.symbol().lower(),'square':chess.square_name(square),'existence':'on-board',
                'mobility':'free','topology':'ordinary','basin':None,'allowed':[]}
            self.pieces[identifier]['horizon']='outside'
            self.at[square]=identifier
        self.groups={}  # same-role merger sets, stored canonically
        self.rules={}
        self.links=[]  # directed B -> W release relays
        self.events=[]
        self.enforced=False

    def _valid_node(self,node):
        if node.startswith('B:'):
            chess.parse_square(node[2:]);return
        if node.startswith('W:') and node[2:] in self.pieces and self.pieces[node[2:]]['existence']=='on-board':return
        raise ValueError('White nodes must refer to on-board piece identities; black nodes to valid squares.')

    def members(self,node):
        return next((list(group) for group in self.groups.values() if node in group),[node])

    def root(self,node):return min(self.members(node))

    def _apply(self,identifier,policy,basin,allowed):
        piece=self.pieces[identifier]
        if piece['existence']!='on-board':return
        piece['topology']='singularity-associated'
        piece['basin']=basin
        piece['horizon']='entered' if basin.startswith('B:') else 'white-source'
        if policy=='imprison':piece['mobility']='imprisoned';piece['allowed']=[]
        elif policy=='constrain':piece['mobility']='constrained';piece['allowed']=sorted(set(allowed))
        elif policy=='release':piece['mobility']='free';piece['allowed']=[]

    def merge(self,left,right,policy='imprison'):
        self._valid_node(left);self._valid_node(right)
        if left==right:raise ValueError('Choose two different fixtures.')
        if policy not in POLICIES:raise ValueError('Unknown merger policy.')
        if left[0]!=right[0]:
            black,white=(left,right) if left.startswith('B:') else (right,left)
            link={'black':black,'white':white,'policy':'release on entry'}
            if link not in self.links:self.links.append(link)
            event={'kind':'black-white','members':[black,white],'policy':'release on entry'}
        else:
            combined=sorted(set(self.members(left)+self.members(right)))
            for key in list(self.groups):
                if set(self.groups[key])&set(combined):self.groups.pop(key);self.rules.pop(key,None)
            root=combined[0];self.groups[root]=combined;self.rules[root]=policy
            event={'kind':'black-black' if left.startswith('B:') else 'white-white','members':combined,'policy':policy}
            if left.startswith('W:'):
                allowed=[self.pieces[node[2:]]['square'] for node in combined
                         if self.pieces[node[2:]]['existence']=='on-board']
                for node in combined:self._apply(node[2:],policy,root,allowed)
            else:
                # Re-merging an occupied basin updates existing prisoners explicitly.
                for piece in self.pieces.values():
                    if piece['basin'] in combined or piece['basin'] in {self.root(n) for n in combined}:
                        self._apply(piece['id'],policy,root,[node[2:] for node in combined])
        self.events.append(event)
        return event

    def release(self,identifier):
        if identifier not in self.pieces:raise ValueError('Unknown piece identity.')
        piece=self.pieces[identifier]
        if piece['existence']!='on-board':raise ValueError('Release cannot resurrect a captured piece.')
        piece['mobility']='free';piece['allowed']=[]
        piece['horizon']='released'
        self.events.append({'kind':'release','piece':identifier})

    def permitted(self,move):
        identifier=self.at.get(move.from_square)
        if identifier is None:return False
        piece=self.pieces[identifier]
        if piece['existence']!='on-board' or piece['mobility']=='imprisoned':return False
        if piece['mobility']=='constrained' and chess.square_name(move.to_square) not in piece['allowed']:return False
        # Castling also moves a rook; its lifecycle constraints count too.
        if piece['type']=='k' and abs(chess.square_file(move.to_square)-chess.square_file(move.from_square))==2:
            rook_square=chess.square(7 if move.to_square>move.from_square else 0,chess.square_rank(move.from_square))
            rook=self.pieces.get(self.at.get(rook_square),{})
            rook_target=chess.square_name((move.from_square+move.to_square)//2)
            if rook.get('mobility')=='imprisoned':return False
            if rook.get('mobility')=='constrained' and rook_target not in rook.get('allowed',[]):return False
        return True

    def moved(self,before,move):
        """Called after legality is checked, with the pre-move board."""
        identifier=self.at.pop(move.from_square)
        piece=self.pieces[identifier]
        capture_square=move.to_square
        if before.is_en_passant(move):capture_square=move.to_square+(-8 if before.turn else 8)
        captured=self.at.pop(capture_square,None)
        if captured:
            victim=self.pieces[captured]
            if victim['type']=='k':raise RuntimeError('A king cannot be captured.')
            victim['existence']='captured';victim['square']=None;victim['mobility']='not-applicable';victim['allowed']=[]
            victim['horizon']='capture-completed'
            victim['captured_by']=identifier
        rook_id=None
        if before.is_castling(move):
            rank=chess.square_rank(move.from_square)
            rook_from=chess.square(7 if move.to_square>move.from_square else 0,rank)
            rook_to=(move.from_square+move.to_square)//2
            rook_id=self.at.pop(rook_from);self.at[rook_to]=rook_id
            self.pieces[rook_id]['square']=chess.square_name(rook_to)
        self.at[move.to_square]=identifier;piece['square']=chess.square_name(move.to_square)
        if move.promotion:piece['type']=chess.piece_symbol(move.promotion)
        self.enter(identifier)
        if rook_id:self.enter(rook_id)
        return identifier,captured

    def enter(self,identifier):
        piece=self.pieces[identifier]
        destination='B:'+piece['square'];members=self.members(destination);root=min(members)
        if root in self.rules:
            self._apply(identifier,self.rules[root],root,[node[2:] for node in members])
        for link in self.links:
            if link['black'] in members:
                for source in self.members(link['white']):
                    self._apply(source[2:],'release',self.root(link['white']),[])

    def signature(self,board):
        """Canonical semantic state: no event history or merger-order dependence."""
        payload={'position':' '.join(board.fen(en_passant='legal').split()[:4]),
                 'pieces':sorted(self.pieces.values(),key=lambda p:p['id']),
                 'groups':sorted((key,sorted(value),self.rules[key]) for key,value in self.groups.items()),
                 'links':sorted(set((self.root(link['black']),self.root(link['white']),link['policy']) for link in self.links)),
                 'enforced':self.enforced}
        return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()

    def snapshot(self,board,holes):
        nodes=[{'id':'B:'+chess.square_name(square),'label':'Black well · '+chess.square_name(square)} for square in holes]
        nodes += [{'id':'W:'+p['id'],'label':'White source · '+p['square']+' · '+p['type'].upper()+' '+p['color']}
                  for p in sorted(self.pieces.values(),key=lambda p:p['id']) if p['existence']=='on-board']
        available={}
        for move in ([] if board.is_game_over() and not self.enforced else board.legal_moves):
            victim=move.to_square
            if board.is_en_passant(move):victim+=-8 if board.turn else 8
            victim_id=self.at.get(victim)
            if victim_id and board.is_capture(move) and (not self.enforced or self.permitted(move)):
                available.setdefault(victim_id,[]).append(move.uci())
        pieces=[]
        for piece in self.pieces.values():
            square=chess.parse_square(piece['square']) if piece['square'] else None
            exposed=False if square is None else board.is_attacked_by(piece['color']!='white',square)
            pieces.append({**piece,'attacked_now':exposed,'capture_available_now':available.get(piece['id'],[])})
        return {'nodes':nodes,'groups':[{'id':key,'members':value,'policy':self.rules[key]} for key,value in sorted(self.groups.items())],
                'links':self.links,'pieces':pieces,'enforced':self.enforced,
                'events':self.events[-20:],'signature':self.signature(board)}

    def forecast(self,board,identifier,depth=3,max_nodes=2000):
        """Bounded adversarial capture reachability, not a probability estimate.

        Attacker chooses a move; defender may choose any legal response or a
        claimable draw. Every branch must respect the selected symbolic rules.
        Physics controller success is outside this proof's scope.
        """
        if identifier not in self.pieces:raise ValueError('Unknown piece identity.')
        target=self.pieces[identifier]
        if target['existence']=='captured':
            return {'status':'captured','nodes':0,'depth':0,'probability':None}
        if target['type']=='k':
            return {'status':'royal: use check/checkmate, never king capture','nodes':0,'depth':0,'probability':None}
        depth=max(1,min(4,int(depth)));max_nodes=max(1,min(5000,int(max_nodes)))
        defender=target['color']=='white';attacker=not defender;nodes=0
        def visit(position,topology,remaining):
            nonlocal nodes
            if nodes>=max_nodes:return None
            nodes+=1
            if topology.pieces[identifier]['existence']=='captured':return True
            if topology.enforced:
                # Baseline repetition keys omit merger/mobility rights. Do not
                # silently adjudicate those as repetition draws in the variant.
                if position.is_checkmate() or position.is_stalemate():return False
            else:
                if position.is_game_over():return False
                if position.turn==defender and position.can_claim_draw():return False
            if remaining==0:return False
            moves=list(position.legal_moves)
            if topology.enforced:moves=[m for m in moves if topology.permitted(m)]
            if not moves:return False
            # Try captures first; this changes efficiency, not the quantifiers.
            moves.sort(key=lambda m:not position.is_capture(m))
            unknown=False
            attacker_turn=position.turn==attacker
            for move in moves:
                child=position.copy(stack=True);field=copy.deepcopy(topology)
                field.moved(position,move);child.push(move)
                result=visit(child,field,remaining-1)
                if attacker_turn and result is True:return True
                if not attacker_turn and result is False:return False
                unknown|=result is None
            return None if unknown else (False if attacker_turn else True)
        result=visit(board.copy(stack=True),copy.deepcopy(self),depth)
        return {'status':'forced within horizon' if result is True else 'not forced within horizon' if result is False else 'unresolved budget',
                'depth':depth,'nodes':nodes,'budget':max_nodes,'probability':None,
                'scope':'Symbolic legal chess plus enabled mobility rules; no claim of physical completion or almost-sure capture.'}
