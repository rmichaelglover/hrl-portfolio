"""ROS-independent world estimation and planning. No simulator truth inputs."""
import heapq
import math
import numpy as np
from .relaxation import RelaxationLabeler

SIZE, RESOLUTION = 20, 0.5
LABELS = ['clear', 'danger', 'opportunity', 'unknown']


class KalmanTrack:
    """2D constant-velocity Kalman filter, independent x/y axes."""
    def __init__(self, position, variance=0.04):
        self.x = np.array([[position[0], 0.0], [position[1], 0.0]])
        self.p = np.repeat(np.diag([variance, 1.0])[None, :, :], 2, axis=0)

    def predict(self, dt):
        f = np.array([[1.0, dt], [0.0, 1.0]])
        q = 0.2 * np.array([[dt**4/4, dt**3/2], [dt**3/2, dt**2]])
        self.x = self.x @ f.T
        self.p = np.array([f @ p @ f.T + q for p in self.p])

    def correct(self, position, variance):
        innovation = np.array(position) - self.x[:, 0]
        for axis in range(2):
            p = self.p[axis]
            k = p[:, 0] / (p[0, 0] + variance)
            self.x[axis] += k * innovation[axis]
            # Joseph form keeps covariance symmetric and positive semidefinite.
            a = np.eye(2) - np.outer(k, [1.0, 0.0])
            self.p[axis] = a @ p @ a.T + variance * np.outer(k, k)
        return float(np.linalg.norm(innovation))

    @property
    def position(self):
        return self.x[:, 0].copy()

    def future(self, seconds=1.0):
        return self.x[:, 0] + seconds * self.x[:, 1]


def cell(position):
    return tuple(np.clip(np.floor(np.asarray(position) / RESOLUTION).astype(int), 0, SIZE-1))


def center(point):
    return (np.asarray(point) + 0.5) * RESOLUTION


class BeliefMap:
    def __init__(self):
        self.log_odds = np.zeros((SIZE, SIZE))  # indexed [y, x]
        self.observations = np.zeros((SIZE, SIZE), dtype=int)

    @property
    def occupancy(self):
        return 1.0 / (1.0 + np.exp(-self.log_odds))

    def scan(self, origin, ranges, angle_min, angle_increment, range_max):
        """Bayesian inverse range-sensor model; each cell updated once per scan.

        Maximum-range returns mean free space, not a wall at the sensor limit.
        """
        free, occupied = set(), set()
        for i, distance in enumerate(ranges):
            if math.isnan(distance) or distance <= 0:
                continue
            distance = min(float(distance), range_max)
            angle = angle_min + i * angle_increment
            direction = np.array([math.cos(angle), math.sin(angle)])
            endpoint = np.asarray(origin) + direction * distance
            for t in np.arange(0, max(0, distance - RESOLUTION * 0.35), RESOLUTION * .3):
                xy = np.asarray(origin) + direction * t
                if np.all(xy >= 0) and np.all(xy < SIZE * RESOLUTION):
                    free.add(cell(xy))
            if distance < range_max - .05 and np.all(endpoint >= 0) and np.all(endpoint < SIZE * RESOLUTION):
                occupied.add(cell(endpoint))
        for x, y in free - occupied:
            self.log_odds[y, x] -= .7
            self.observations[y, x] += 1
        for x, y in occupied:
            self.log_odds[y, x] += 1.0
            self.observations[y, x] += 1
        np.clip(self.log_odds, -5, 5, out=self.log_odds)


def relax_scene(belief, position, goal, hazard=None, max_iterations=8):
    """Local cells + their nine world regions share one HRL field.

    Regional evidence comes from sensed occupancy. Parent-child and spatial
    compatibility allow support in both directions. Strengths are contextual
    interpretations, not calibrated Bayesian posterior probabilities.
    """
    cx, cy = cell(position)
    cells = [(x, y) for y in range(max(0, cy-2), min(SIZE, cy+3))
             for x in range(max(0, cx-2), min(SIZE, cx+3))]
    occupancy = belief.occupancy

    def prior(x, y):
        p = occupancy[y, x]
        unknown = 1.0 if belief.observations[y, x] == 0 else max(.03, 1-2*abs(p-.5))
        progress = max(0.0, np.linalg.norm(np.asarray(position)-goal) - np.linalg.norm(center((x,y))-goal))
        threat = 0.0 if hazard is None else math.exp(-np.linalg.norm(center((x,y))-hazard)**2 / 1.2)
        row = np.array([.03+(1-p)*(1-unknown), .03+p*(1-unknown)+2*threat,
                        .03+progress*(1-p)*(1-unknown), .03+unknown])
        return row / row.sum()

    local = [prior(x,y) for x,y in cells]
    regions = []
    for ry in range(3):
        for rx in range(3):
            regions.append(np.mean([prior(x,y) for y in range(SIZE) for x in range(SIZE)
                                    if min(2,x*3//SIZE)==rx and min(2,y*3//SIZE)==ry],axis=0))
    priors = np.array(local + regions)
    n = len(priors)
    compat = np.zeros((n,4,n,4))
    agreement = np.diag([.7, .9, .7, .15])
    for i,(x,y) in enumerate(cells):
        parent = len(cells) + min(2,y*3//SIZE)*3 + min(2,x*3//SIZE)
        compat[i,:,parent,:] = agreement * .6
        compat[parent,:,i,:] = agreement * .6
        for j,(xx,yy) in enumerate(cells):
            if abs(xx-x)+abs(yy-y)==1:
                compat[i,:,j,:] = agreement
    engine = RelaxationLabeler(compat, priors, prior_strength=.75,
                              max_iterations=max_iterations, tol=1e-4)
    result = engine.run()
    return {'cells': cells, 'strengths': result.strengths[:len(cells)].tolist(),
            'regions': result.strengths[len(cells):].tolist(),
            'iterations': result.iterations, 'converged': result.converged}


class Attention:
    """Bounded, deterministic excitation experiment, not a proof of SOC."""
    def __init__(self):
        self.gain = .75
        self.activity = np.zeros(9)
        self.history = []

    def update(self, surprise, region):
        previous = self.activity.copy()
        seeds = np.zeros(9)
        seeds[region] = min(1., max(0., surprise))
        activity = seeds.copy()
        for _ in range(5):
            field = np.zeros(9)
            for i in range(9):
                for j in range(9):
                    if abs(i%3-j%3)+abs(i//3-j//3)==1:
                        field[i] += activity[j]/4
            activity = np.clip(seeds + self.gain * field, 0, 1)
        # Homeostatic gain tunes mean activity toward an illustrative setpoint.
        # This is not an inferred branching ratio or criticality measurement.
        self.gain = float(np.clip(self.gain + .02*(.18-activity.mean()), .25, 1.5))
        self.activity = activity
        cascade = int(np.count_nonzero(activity > .1))
        self.history = (self.history + [cascade])[-80:]
        return {'gain': self.gain, 'active_regions': cascade,
                'activity': activity.tolist(), 'history': self.history,
                'change': float(np.linalg.norm(activity-previous))}


def plan(belief, position, goal, hazard=None, scene=None):
    start, end = cell(position), cell(goal)
    occupancy = belief.occupancy
    blocked = occupancy > .72
    # At 0.5 m resolution, adjacent cell centres are already 0.25 m from
    # the occupied cell's square. Inflate by geometric robot clearance,
    # rather than a full cell that would erase traversable corridors.
    inflated = blocked.copy()
    for y,x in np.argwhere(blocked):
        for yy in range(max(0,y-1),min(SIZE,y+2)):
            for xx in range(max(0,x-1),min(SIZE,x+2)):
                dx=max(0,abs(xx-x)*RESOLUTION-RESOLUTION/2)
                dy=max(0,abs(yy-y)*RESOLUTION-RESOLUTION/2)
                if math.hypot(dx,dy)<.22: inflated[yy,xx]=True
    risk = {}
    if scene:
        risk = {tuple(c): s[1] for c,s in zip(scene['cells'], scene['strengths'])}
    queue, costs, parent = [(0.,start)], {start:0.}, {}
    while queue:
        _, point = heapq.heappop(queue)
        if point == end:
            route = [point]
            while point in parent:
                point = parent[point]; route.append(point)
            return list(reversed(route))
        for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
            nxt = (point[0]+dx,point[1]+dy)
            x,y = nxt
            if not (1 <= x < SIZE-1 and 1 <= y < SIZE-1) or inflated[y,x]:
                continue
            distance = float('inf') if hazard is None else np.linalg.norm(center(nxt)-hazard)
            if distance < .8:
                continue
            proximity=float(np.max(occupancy[max(0,y-1):min(SIZE,y+2),max(0,x-1):min(SIZE,x+2)]))
            new = costs[point] + 1 + 2*occupancy[y,x] + 2*proximity + 3*risk.get(nxt,0) + 2*math.exp(-distance)
            if new < costs.get(nxt,float('inf')):
                costs[nxt], parent[nxt] = new, point
                heuristic = abs(x-end[0])+abs(y-end[1])
                heapq.heappush(queue,(new+heuristic,nxt))
    return []
