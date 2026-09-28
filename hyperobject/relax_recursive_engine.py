#!/usr/bin/env python3
from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

EPS = 1e-12

def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))

def normalize(v: Dict[str, float]) -> Dict[str, float]:
    s = sum(max(0.0, x) for x in v.values())
    if s < EPS:
        n = len(v)
        return {k: 1.0 / n for k in v} if n else {}
    return {k: max(0.0, x) / s for k, x in v.items()}

def cosine(a: Dict[str, float], b: Dict[str, float]) -> float:
    keys = set(a) | set(b)
    dot = sum(a.get(k, 0.0) * b.get(k, 0.0) for k in keys)
    na = math.sqrt(sum(x * x for x in a.values()))
    nb = math.sqrt(sum(x * x for x in b.values()))
    if na < EPS or nb < EPS:
        return 0.0
    return dot / (na * nb)

def lerp(a: float, b: float, rate: float) -> float:
    return a + rate * (b - a)

@dataclass
class Evidence:
    name: str
    features: Dict[str, float]
    confidence: float = 1.0

@dataclass
class Goal:
    id: str
    name: str
    level: str
    target: Dict[str, float]
    parent: Optional[str] = None
    strength: float = 0.5
    progress: float = 0.0
    priority: float = 0.5
    attempts: int = 0
    successes: int = 0
    active: bool = True
    children: List[str] = field(default_factory=list)

@dataclass
class OperatorState:
    compatibility: float = 0.25
    goal_alignment: float = 0.25
    novelty: float = 0.15
    persistence: float = 0.15
    evidence: float = 0.20
    exploration_temperature: float = 0.08

    def weights(self) -> Dict[str, float]:
        return normalize({
            "compatibility": self.compatibility,
            "goal_alignment": self.goal_alignment,
            "novelty": self.novelty,
            "persistence": self.persistence,
            "evidence": self.evidence,
        })

    def apply_weights(self, w: Dict[str, float]) -> None:
        self.compatibility = w["compatibility"]
        self.goal_alignment = w["goal_alignment"]
        self.novelty = w["novelty"]
        self.persistence = w["persistence"]
        self.evidence = w["evidence"]

@dataclass
class Candidate:
    id: str
    features: Dict[str, float]

@dataclass
class StepResult:
    chosen: Candidate
    reward: float
    success: bool
    state_before: Dict[str, float]
    state_after: Dict[str, float]
    active_goal_id: str

class RelaxEngine:
    def __init__(self, state_learning_rate=0.35, goal_learning_rate=0.12,
                 operator_learning_rate=0.03, seed=7):
        self.state_lr = state_learning_rate
        self.goal_lr = goal_learning_rate
        self.operator_lr = operator_learning_rate
        self.rng = random.Random(seed)
        self.state: Dict[str, float] = {}
        self.previous_state: Dict[str, float] = {}
        self.goals: Dict[str, Goal] = {}
        self.evidence: List[Evidence] = []
        self.operator = OperatorState()
        self.history: List[StepResult] = []
        self.cycle = 0

    def set_state(self, state: Dict[str, float]) -> None:
        self.state = normalize(state)
        self.previous_state = dict(self.state)

    def add_goal(self, goal: Goal) -> None:
        self.goals[goal.id] = goal
        if goal.parent:
            self.goals[goal.parent].children.append(goal.id)

    def observe(self, evidence: Evidence) -> None:
        self.evidence.append(evidence)
        if len(self.evidence) > 500:
            self.evidence.pop(0)

    def active_short_goals(self) -> List[Goal]:
        return [g for g in self.goals.values() if g.level == "short" and g.active]

    def ancestry(self, goal: Goal) -> List[Goal]:
        out = []
        p = goal.parent
        while p:
            g = self.goals[p]
            out.append(g)
            p = g.parent
        return out

    def goal_hierarchy_target(self, goal: Goal) -> Dict[str, float]:
        chain = [goal] + self.ancestry(goal)
        merged: Dict[str, float] = {}
        total_weight = 0.0
        weight = 1.0
        for g in chain:
            for k, v in g.target.items():
                merged[k] = merged.get(k, 0.0) + weight * g.strength * v
            total_weight += weight * g.strength
            weight *= 0.65
        if total_weight < EPS:
            return merged
        return {k: v / total_weight for k, v in merged.items()}

    def choose_goal(self) -> Goal:
        goals = self.active_short_goals()
        if not goals:
            raise RuntimeError("No active short-term goals.")
        def score(g: Goal) -> float:
            target = self.goal_hierarchy_target(g)
            alignment = (cosine(self.state, target) + 1.0) / 2.0
            unfinished = 1.0 - g.progress
            exploration = self.rng.uniform(-0.03, 0.03)
            return (0.35 * g.strength + 0.30 * g.priority +
                    0.20 * unfinished + 0.15 * alignment + exploration)
        return max(goals, key=score)

    def aggregate_evidence(self) -> Dict[str, float]:
        keys = set()
        for e in self.evidence:
            keys.update(e.features)
        out = {}
        for k in keys:
            num = 0.0
            den = 0.0
            for e in self.evidence:
                num += e.features.get(k, 0.0) * e.confidence
                den += e.confidence
            out[k] = num / den if den > EPS else 0.0
        return out

    def candidate_score(self, candidate: Candidate, active_goal: Goal) -> Tuple[float, Dict[str, float]]:
        w = self.operator.weights()
        evidence = self.aggregate_evidence()
        goal_target = self.goal_hierarchy_target(active_goal)
        compatibility = (cosine(candidate.features, self.state) + 1.0) / 2.0
        goal_alignment = (cosine(candidate.features, goal_target) + 1.0) / 2.0
        evidence_fit = (cosine(candidate.features, evidence) + 1.0) / 2.0
        persistence = (cosine(candidate.features, self.previous_state) + 1.0) / 2.0
        novelty = 1.0 - compatibility
        components = {
            "compatibility": compatibility,
            "goal_alignment": goal_alignment,
            "novelty": novelty,
            "persistence": persistence,
            "evidence": evidence_fit,
        }
        score = sum(w[k] * components[k] for k in components)
        score += self.operator.exploration_temperature * self.rng.uniform(-1.0, 1.0)
        return score, components

    def choose_candidate(self, candidates: List[Candidate], active_goal: Goal) -> Tuple[Candidate, Dict[str, float]]:
        scored = [(self.candidate_score(c, active_goal), c) for c in candidates]
        ((_, comps), chosen) = max(scored, key=lambda x: x[0][0])
        return chosen, comps

    def relax_state(self, chosen: Candidate) -> None:
        self.previous_state = dict(self.state)
        keys = set(self.state) | set(chosen.features)
        updated = {}
        for k in keys:
            old = self.state.get(k, 0.0)
            target = chosen.features.get(k, 0.0)
            updated[k] = max(0.0, lerp(old, target, self.state_lr))
        self.state = normalize(updated)

    def relax_goals(self, active_goal: Goal, reward: float) -> None:
        reward01 = clamp((reward + 1.0) / 2.0)
        active_goal.strength = clamp(lerp(active_goal.strength, reward01, self.goal_lr))
        active_goal.progress = clamp(active_goal.progress + self.goal_lr * max(reward, 0.0))
        active_goal.attempts += 1
        if reward > 0:
            active_goal.successes += 1

        credit = reward01
        parent_id = active_goal.parent
        attenuation = 0.65
        while parent_id:
            parent = self.goals[parent_id]
            parent.strength = clamp(
                lerp(parent.strength, credit, self.goal_lr * attenuation)
            )
            child_progress = [self.goals[c].progress for c in parent.children]
            if child_progress:
                target_progress = sum(child_progress) / len(child_progress)
                parent.progress = clamp(
                    lerp(parent.progress, target_progress, self.goal_lr * attenuation)
                )
            credit *= attenuation
            attenuation *= 0.75
            parent_id = parent.parent

    def relax_operator(self, components: Dict[str, float], reward: float) -> None:
        current = self.operator.weights()
        reward_signed = clamp(reward, -1.0, 1.0)
        updated = dict(current)

        for name, contribution in components.items():
            centered = contribution - 0.5
            delta = self.operator_lr * reward_signed * centered
            updated[name] = max(0.001, current[name] + delta)

        updated = normalize(updated)
        self.operator.apply_weights(updated)

        if reward < -0.2:
            self.operator.exploration_temperature = clamp(
                self.operator.exploration_temperature + self.operator_lr * 0.25,
                0.0, 0.5
            )
        elif reward > 0.4:
            self.operator.exploration_temperature = clamp(
                self.operator.exploration_temperature - self.operator_lr * 0.10,
                0.0, 0.5
            )

    def evaluate(self, candidate: Candidate, active_goal: Goal) -> float:
        goal_target = self.goal_hierarchy_target(active_goal)
        evidence = self.aggregate_evidence()
        goal_fit = (cosine(candidate.features, goal_target) + 1.0) / 2.0
        evidence_fit = (cosine(candidate.features, evidence) + 1.0) / 2.0
        continuity = (cosine(candidate.features, self.state) + 1.0) / 2.0
        reward01 = 0.55 * goal_fit + 0.30 * evidence_fit + 0.15 * continuity
        return clamp(2.0 * reward01 - 1.0, -1.0, 1.0)

    def step(self, candidates: List[Candidate]) -> StepResult:
        self.cycle += 1
        active_goal = self.choose_goal()
        before = dict(self.state)
        chosen, components = self.choose_candidate(candidates, active_goal)
        reward = self.evaluate(chosen, active_goal)

        self.relax_state(chosen)
        self.relax_goals(active_goal, reward)
        self.relax_operator(components, reward)

        self.observe(Evidence(
            name=f"cycle_{self.cycle}",
            features=dict(chosen.features),
            confidence=clamp((reward + 1.0) / 2.0),
        ))

        result = StepResult(
            chosen=chosen,
            reward=reward,
            success=reward > 0.0,
            state_before=before,
            state_after=dict(self.state),
            active_goal_id=active_goal.id,
        )
        self.history.append(result)
        return result

    def print_status(self) -> None:
        print(f"\n=== RELAX cycle {self.cycle} ===")
        print("\nSTATE")
        for k, v in sorted(self.state.items()):
            print(f"  {k:18s} {v:.3f}")

        print("\nGOALS")
        for g in self.goals.values():
            print(
                f"  [{g.level:6s}] {g.name:40s}"
                f" strength={g.strength:.3f}"
                f" progress={g.progress:.3f}"
            )

        print("\nOPERATOR")
        for k, v in self.operator.weights().items():
            print(f"  {k:18s} {v:.3f}")
        print(f"  {'exploration':18s} {self.operator.exploration_temperature:.3f}")

def build_demo() -> RelaxEngine:
    e = RelaxEngine(
        state_learning_rate=0.35,
        goal_learning_rate=0.12,
        operator_learning_rate=0.03,
        seed=7,
    )

    e.set_state({
        "knowledge": 0.30,
        "coherence": 0.20,
        "adaptation": 0.20,
        "planning": 0.15,
        "observation": 0.15,
    })

    e.add_goal(Goal(
        "L1", "Build an adaptive reasoning system", "long",
        {"knowledge": 1.0, "coherence": 1.0, "adaptation": 1.0},
        strength=0.95, priority=1.0
    ))

    e.add_goal(Goal(
        "M1", "Develop hierarchical planning", "medium",
        {"planning": 1.0, "coherence": 0.9, "adaptation": 0.8},
        parent="L1", strength=0.85, priority=0.95
    ))

    e.add_goal(Goal(
        "M2", "Improve empirical feedback", "medium",
        {"observation": 1.0, "knowledge": 0.9, "adaptation": 0.8},
        parent="L1", strength=0.80, priority=0.90
    ))

    e.add_goal(Goal(
        "S1", "Choose the best next experiment", "short",
        {"planning": 1.0, "adaptation": 0.8, "coherence": 0.7},
        parent="M1", strength=0.75, priority=0.95
    ))

    e.add_goal(Goal(
        "S2", "Gather informative evidence", "short",
        {"observation": 1.0, "knowledge": 0.9, "adaptation": 0.6},
        parent="M2", strength=0.70, priority=0.90
    ))

    e.observe(Evidence(
        "initial_context",
        {"planning": 0.8, "observation": 0.7, "adaptation": 0.8, "knowledge": 0.6},
        confidence=0.9,
    ))

    return e

def generate_candidates(rng: random.Random, n: int = 8) -> List[Candidate]:
    names = ["observe", "plan", "test", "integrate", "explore", "exploit", "revise", "compress"]
    return [
        Candidate(
            id=f"{names[i % len(names)]}_{i}",
            features={
                "knowledge": rng.random(),
                "coherence": rng.random(),
                "adaptation": rng.random(),
                "planning": rng.random(),
                "observation": rng.random(),
            }
        )
        for i in range(n)
    ]

def main() -> None:
    engine = build_demo()

    print("INITIAL RELAX STATE")
    engine.print_status()

    for _ in range(20):
        result = engine.step(generate_candidates(engine.rng, 8))
        print(
            f"\nCycle {engine.cycle:02d}: "
            f"{result.active_goal_id} -> {result.chosen.id:12s} "
            f"reward={result.reward:+.3f}"
        )

    print("\nFINAL RELAX STATE")
    engine.print_status()

if __name__ == "__main__":
    main()
