#!/usr/bin/env python3
"""Artificial Angel v0.1 — a bounded, inspectable meta-agent.

Standard-library-only demonstration of heterogeneous specialists,
self-representation, epistemic curiosity, and reversible policy mutation.
This is a toy game-learning system, not an AGI or a chess engine.
"""
from __future__ import annotations
import argparse
import json
import math
import random
from dataclasses import dataclass, asdict

ACTIONS = (-1, 0, 1)

@dataclass(frozen=True)
class World:
    x: float
    y: float
    regime: int

    def payoff(self, action: int) -> float:
        # Hidden target: linear in one regime, nonlinear in another.
        z = (1.8 * self.x - 0.65 * self.y) if self.regime == 0 else (2.4 * self.x * self.y + 0.35 * self.y)
        target = 1 if z > 0.38 else (-1 if z < -0.38 else 0)
        return 1.0 if action == target else 0.0

class Expert:
    def __init__(self, name, fn): self.name, self.fn = name, fn
    def propose(self, w: World) -> int: return self.fn(w)

def sign(z, thresh=.35): return 1 if z > thresh else (-1 if z < -thresh else 0)

EXPERTS = [
    Expert('linear', lambda w: sign(1.6*w.x - .5*w.y)),
    Expert('interaction', lambda w: sign(2.2*w.x*w.y + .35*w.y)),
    Expert('x_only', lambda w: sign(w.x, .2)),
    Expert('y_only', lambda w: sign(w.y, .2)),
    Expert('contrarian', lambda w: -sign(w.x, .2)),
]

class Angel:
    def __init__(self, seed: int = 7, curiosity: float = .35):
        self.rng = random.Random(seed)
        self.curiosity = curiosity
        self.experts = EXPERTS
        self.weights = {e.name: 1.0 for e in EXPERTS}
        self.context = {r: {e.name: {'success': 1., 'failure': 1.} for e in EXPERTS} for r in (0,1)}
        self.regime_count = {0: 0, 1: 0}
        self.experiments = []
        self.steps = 0
        self.reward = 0.
        self.mutations_accepted = 0
        self.mutations_rejected = 0

    def trust(self, regime, name):
        d = self.context[regime][name]
        return d['success']/(d['success'] + d['failure'])

    def probabilities(self, w):
        scores = {a: 0.0 for a in ACTIONS}
        for e in self.experts:
            pred = e.propose(w)
            scores[pred] += self.weights[e.name] * (0.05 + self.trust(w.regime, e.name))
        total = sum(scores.values())
        return {a: scores[a]/total for a in ACTIONS}

    def choose(self, w, train=True):
        probs = self.probabilities(w)
        # An explicit model of uncertainty (normalized entropy).
        h = -sum(p*math.log(p) for p in probs.values() if p > 0)/math.log(3)
        # Curiosity is conditional: higher uncertainty encourages experimentation.
        explore = train and self.rng.random() < self.curiosity*h
        if explore:
            # Prefer less-supported alternatives; every action remains possible.
            weights = [1.01-probs[a] for a in ACTIONS]
            action = self.rng.choices(ACTIONS, weights=weights, k=1)[0]
        else:
            action = max(ACTIONS, key=lambda a: (probs[a], -abs(a), -a))
        return action, h, explore

    def observe(self, w, action, reward):
        self.steps += 1
        self.reward += reward
        self.regime_count[w.regime] += 1
        # All specialists are evaluated counterfactually in this transparent toy environment.
        for e in self.experts:
            s = self.context[w.regime][e.name]
            correct = w.payoff(e.propose(w))
            s['success'] += correct
            s['failure'] += 1-correct

    def self_model(self):
        return {'identity': 'Artificial Angel v0.1',
                'steps': self.steps,
                'observed_accuracy': round(self.reward/max(self.steps,1),4),
                'curiosity': round(self.curiosity,4),
                'weights': {k: round(v,3) for k,v in self.weights.items()},
                'regime_exposure': self.regime_count.copy(),
                'conditional_competence': {str(r): {n: round(self.trust(r,n),3) for n in self.weights} for r in (0,1)},
                'mutations_accepted': self.mutations_accepted,
                'mutations_rejected': self.mutations_rejected}

    def mutate_and_validate(self, validation):
        """Explore alternative weights, accept only if fixed validation improves.
        Deliberate constraints: no arbitrary code editing, no file/network permissions,
        bounded weight values, and explicit rollback on rejection.
        """
        old = self.weights.copy()
        old_score = self.evaluate(validation)
        name = self.rng.choice(list(self.weights))
        factor = self.rng.choice([.65, .8, 1.25, 1.5])
        self.weights[name] = min(4.,max(.2, self.weights[name]*factor))
        new_score = self.evaluate(validation)
        accepted = new_score > old_score + 1e-12
        if accepted: self.mutations_accepted += 1
        else:
            self.weights = old
            self.mutations_rejected += 1
        self.experiments.append({'expert': name, 'factor': factor,
                                 'before': round(old_score,4),
                                 'after': round(new_score,4), 'accepted': accepted})

    def evaluate(self, worlds):
        return sum(w.payoff(self.choose(w, train=False)[0]) for w in worlds)/len(worlds)

def sample_world(rng): return World(rng.uniform(-1,1), rng.uniform(-1,1), rng.randrange(2))

def run(seed=7, episodes=1200, curiosity=.35):
    rng = random.Random(seed+100)
    agent = Angel(seed, curiosity)
    validation = [sample_world(random.Random(seed+200+i)) for i in range(180)]
    test = [sample_world(random.Random(seed+6000+i)) for i in range(300)]
    history = []
    for t in range(episodes):
        w = sample_world(rng)
        move, uncertainty, explore = agent.choose(w)
        agent.observe(w, move, w.payoff(move))
        if (t+1)%100 == 0:
            agent.mutate_and_validate(validation)
            history.append({'episode': t+1,
                            'rolling_accuracy': round(agent.reward/agent.steps,4),
                            'heldout_accuracy': round(agent.evaluate(test),4),
                            'uncertainty': round(uncertainty,3),
                            'exploratory_move': explore})
    baselines = {e.name: round(sum(w.payoff(e.propose(w)) for w in test)/len(test),4) for e in EXPERTS}
    result = {'self_model': agent.self_model(),
              'heldout_accuracy': round(agent.evaluate(test),4),
              'expert_baselines': baselines,
              'history': history,
              'mutation_log': agent.experiments,
              'caveat': 'Toy contextual decision task with known simulator rewards; not a chess engine, self-awareness, or superintelligence.'}
    return result

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--seed', type=int, default=7)
    parser.add_argument('--episodes', type=int, default=1200)
    parser.add_argument('--curiosity', type=float, default=.35)
    parser.add_argument('--output', default='angel_results.json')
    args=parser.parse_args()
    if args.episodes < 100 or not 0 <= args.curiosity <= 1: parser.error('episodes >= 100 and curiosity in [0,1] required')
    result=run(args.seed,args.episodes,args.curiosity)
    with open(args.output,'w') as f: json.dump(result,f,indent=2)
    print(json.dumps({'self_model':result['self_model'], 'heldout_accuracy':result['heldout_accuracy'], 'expert_baselines':result['expert_baselines']},indent=2))
    print('Saved:',args.output)
