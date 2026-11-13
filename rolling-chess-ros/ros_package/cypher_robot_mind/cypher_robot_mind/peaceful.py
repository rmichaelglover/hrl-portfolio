"""Michael Emanuel Glover's peaceful joint-preference world; no ROS dependency.
Chess observations inform planning weights; household values are explicitly authored.
"""
from dataclasses import dataclass, asdict
from itertools import product
from collections import deque
from math import hypot
import hashlib
import io


def chess_profile(text):
    import chess.pgn
    stream = io.StringIO(text)
    records, quiet, anticipation = [], [], []
    while (game := chess.pgn.read_game(stream)) is not None:
        if game.errors:
            raise ValueError("Malformed PGN")
        board = game.board()
        count = 0
        for move in game.mainline_moves():
            if move not in board.legal_moves:
                raise ValueError("Illegal recorded move")
            is_quiet = not board.is_capture(move)
            quiet.append(int(is_quiet))
            board.push(move)
            # Fraction of legal replies landing on squares attacked by the mover.
            # This is a board-geometric observation, not a person's social preference.
            replies = list(board.legal_moves)
            anticipation.append(sum(board.is_attacked_by(not board.turn, m.to_square)
                                    for m in replies) / max(1, len(replies)))
            count += 1
        records.append({"white": game.headers.get("White"),
                        "black": game.headers.get("Black"),
                        "site": game.headers.get("Site"), "plies": count})
    if not quiet:
        raise ValueError("PGN contains no moves")
    q, a = sum(quiet)/len(quiet), sum(anticipation)/len(anticipation)
    return {"sha256": hashlib.sha256(text.encode()).hexdigest(), "games": records,
            "plies": len(quiet), "quiet_fraction": q, "reply_exposure": a,
            "weights": {"progress": 1 + q, "anticipation": 1 + a, "roses": .7},
            "interpretation": "Designed transfer of recorded chess geometry to planning weights; not learned human preferences."}


@dataclass
class Person:
    name: str
    position: tuple
    goal: tuple
    rose_interest: float = .7
    wants_prosthetic_support: bool = False
    rose_pauses: int = 0
    total_progress: float = 0.


def separation(a, b, c, d):
    """Minimum distance of two simultaneous linear moves, including endpoints."""
    x, y = a[0]-c[0], a[1]-c[1]
    vx, vy = b[0]-a[0]-d[0]+c[0], b[1]-a[1]-d[1]+c[1]
    vv = vx*vx + vy*vy
    t = max(0., min(1., -(x*vx+y*vy)/vv)) if vv else 0.
    return hypot(x+t*vx, y+t*vy)


class Garden:
    """Enumerate five actions per person jointly; no captures or occupancy swaps.

    The preference score includes others' preferred replies, rather than treating
    them as stationary obstacles. This is one-step joint coordination, not minimax.
    """
    roses = ((2, 2), (6, 2))
    walls = frozenset({(4, 0), (4, 1), (4, 3), (4, 4)})
    names = ("Alex", "Rosy", "Mama", "Papa", "Cypher")

    def __init__(self, profile):
        self.profile = profile
        self.tick_count = 0
        self.people = [Person(n, p, g, r, n == "Alex") for n, p, g, r in zip(
            self.names, [(1,2),(7,2),(2,4),(6,4),(4,6)],
            [(7,2),(1,2),(6,4),(2,4),(4,2)], [.9,.6,.8,.7,.5])]
        self.last = {"reason": "Everyone has a destination and a preference of their own."}

    def frog(self, tick):
        # A known scripted neighbor; reserve its complete swept hop this turn.
        return (3, 5 + (tick//3)%2)

    def valid(self, p):
        return 0 <= p[0] <= 8 and 0 <= p[1] <= 6 and p not in self.walls

    def candidates(self, person):
        x,y = person.position
        return [(x+dx,y+dy) for dx,dy in [(0,0),(1,0),(-1,0),(0,1),(0,-1)]
                if self.valid((x+dx,y+dy)) and separation(person.position,(x+dx,y+dy),
                    self.frog(self.tick_count),self.frog(self.tick_count+1)) >= .65]

    def distances(self, person):
        # Anticipate residents who may prefer to stay put: route around their space.
        occupied = {q.position for q in self.people if q is not person and q.position != person.goal}
        distances = {person.goal: 0}
        queue = deque([person.goal])
        while queue:
            x,y = queue.popleft()
            for q in [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]:
                if self.valid(q) and q not in occupied and q not in distances:
                    distances[q] = distances[(x,y)] + 1
                    queue.append(q)
        return distances

    def utility(self, p, target):
        distances = self.distance_cache[p.name]
        gain = distances.get(p.position, 100)-distances.get(target, 100)
        w = self.profile["weights"]
        # Pausing once near roses is a positive preference; remaining there forever is not.
        rose = (target == p.position and p.position in self.roses and p.rose_pauses < 2)
        return w["progress"]*gain + (2*w["progress"]*p.rose_interest + w["roses"] if rose else 0) - (.04 if target == p.position and not rose and target != p.goal else 0)

    def step(self):
        self.distance_cache = {p.name: self.distances(p) for p in self.people}
        options = [self.candidates(p) for p in self.people]
        preferred = [max(v, key=lambda q:self.utility(p,q)) if v else p.position
                     for p,v in zip(self.people,options)]
        best = None
        for joint in product(*options):
            if any(separation(self.people[i].position,joint[i],self.people[j].position,joint[j]) < .75
                   for i in range(len(joint)) for j in range(i)):
                continue
            u = [self.utility(p,q) for p,q in zip(self.people,joint)]
            # Avoid obstructing another person's predicted first-choice destination.
            obstruction = sum(q == preferred[j] and q != preferred[i]
                              for i,q in enumerate(joint) for j in range(len(joint)) if i != j)
            # Rotate tie priority to avoid always giving Alex the first equal claim.
            priority = sum((len(u)-k)*u[(self.tick_count+k)%len(u)] for k in range(len(u)))
            score = (sum(u) + .2*min(u) - self.profile["weights"]["anticipation"]*obstruction, priority)
            if best is None or score > best[0]: best = score,joint,u
        if best is None:
            raise RuntimeError("No safe joint action; no movement committed")
        _, joint, utilities = best
        before = [p.position for p in self.people]
        for p,q in zip(self.people,joint):
            if q == p.position and q in self.roses and p.rose_pauses < 2: p.rose_pauses += 1
            p.total_progress += abs(p.position[0]-p.goal[0])+abs(p.position[1]-p.goal[1])-abs(q[0]-p.goal[0])-abs(q[1]-p.goal[1])
            p.position = q
        self.tick_count += 1
        self.last = {"from": before, "preferred": preferred, "chosen": joint,
                     "utilities": utilities, "reason": "A joint choice respects people, swept frog paths, and time by the roses."}
        return self.snapshot()

    def snapshot(self):
        return {"tick": self.tick_count, "people": [asdict(p) for p in self.people],
                "frog": self.frog(self.tick_count), "roses": self.roses,
                "walls": sorted(self.walls), "decision": self.last}
