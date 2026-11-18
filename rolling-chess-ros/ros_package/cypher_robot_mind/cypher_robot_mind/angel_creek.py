"""Artificial Angel and Virtual Person coupled to a creek-powered sensor model."""
import argparse
import csv
import json
import math
import random
from pathlib import Path

from .artificial_angel import Angel, Expert
from .peaceful import Garden

DT = 1.0                 # seconds per sample
AREA = 0.004             # channel cross-section, m²
HEAD = 0.12              # metres of hydraulic head
EFFICIENCY = 0.25
CAPACITANCE = 0.1        # farads
CAPACITY = 0.5           # joules
PULSE = 0.05             # joules per requested sensor pulse
RESISTANCE = 2         # ohms in model discharge path
K_B = 1.380649e-23
TRACER_RADIUS = 0.5e-6   # metres, suspended tracer particle


def samples(path):
    if path is None:
        for i in range(60):
            yield (0.18 + 0.14 * math.sin(i * 0.53), 20.0,
                   0.18 + 0.11 * math.sin((i - 2) * 0.53))
        return
    with path.open(newline="") as stream:
        for row in csv.DictReader(stream):
            flow = float(row["flow_lps"])
            temperature = float(row["temperature_c"])
            if not math.isfinite(flow) or flow < 0 or not 5 <= temperature <= 35:
                raise ValueError("Expected nonnegative finite flow and temperature of 5–35 °C")
            reading = row.get("downstream_flow_lps", "")
            downstream = float(reading) if reading else None
            if downstream is not None and (not math.isfinite(downstream) or downstream < 0):
                raise ValueError("Downstream flow must be finite and nonnegative")
            yield flow, temperature, downstream


class CreekWorld:
    """Values visible to the Angel before it makes the next-sample forecast."""

    def __init__(self, flow, trend, energy):
        self.flow = flow
        self.trend = trend
        self.energy = energy
        self.regime = int(energy >= 2 * PULSE)


def run(path=None, seed=7):
    agent = Angel(seed)
    agent.experts = [
        Expert("persistence", lambda w: int(w.flow >= 0.18)),
        Expert("trend", lambda w: int(w.flow + w.trend >= 0.18)),
        Expert("conservative", lambda w: int(w.flow >= 0.24)),
    ]
    agent.weights = {expert.name: 1.0 for expert in agent.experts}
    for context in agent.context.values():
        for name in agent.weights:
            context.setdefault(name, {"success": 1.0, "failure": 1.0})
    garden = Garden({"weights": {"progress": 1.0, "anticipation": 1.0, "roses": 0.7}})
    tracer_rng = random.Random(seed + 1)
    energy = position = previous_flow = 0.0
    pending = None
    for tick, (flow, celsius, downstream) in enumerate(samples(path)):
        q = flow / 1000
        velocity = q / AREA
        kelvin = celsius + 273.15
        # Approximate liquid-water viscosity in Pa·s over the input range.
        viscosity = 2.414e-5 * 10 ** (247.8 / (kelvin - 140))
        diffusion = K_B * kelvin / (6 * math.pi * viscosity * TRACER_RADIUS)
        brownian = tracer_rng.gauss(0.0, math.sqrt(2 * diffusion * DT))
        position += velocity * DT + brownian

        harvest = EFFICIENCY * 998 * 9.81 * q * HEAD * DT
        charged = min(CAPACITY, energy + harvest)
        spill = energy + harvest - charged
        target = None
        clock = False
        if pending is not None:
            world, clock = pending
            if clock and downstream is not None:
                target = int(downstream >= 0.18)
                for expert in agent.experts:
                    counts = agent.context[world.regime][expert.name]
                    key = "success" if expert.propose(world) == target else "failure"
                    counts[key] += 1
        world = CreekWorld(flow, flow - previous_flow if tick else 0.0, charged)
        action, disagreement, _ = agent.choose(world, train=False)
        # A high-flow forecast requests verification. The energy gate can deny it.
        discharge_limit = charged * -math.expm1(-2 * DT / (RESISTANCE * CAPACITANCE))
        delivered = PULSE if action == 1 and discharge_limit >= PULSE else 0.0
        energy = charged - delivered
        voltage = math.sqrt(2 * charged / CAPACITANCE)
        end_voltage = math.sqrt(2 * energy / CAPACITANCE)
        # The switch opens at the end of the RC discharge interval.
        duration = (RESISTANCE * CAPACITANCE * math.log(voltage / end_voltage)
                    if delivered else None)
        if delivered:
            garden.step()
        yield {
            "sample": tick, "source": "csv" if path else "synthetic",
            "flow_lps": flow, "temperature_c": celsius,
            "velocity_m_s": velocity, "diffusion_m2_s": diffusion,
            "brownian_increment_m": brownian, "tracer_x_m": position,
            "harvest_j": harvest, "spill_j": spill, "stored_j": energy,
            "pulse_j": delivered, "pulse_initial_a": voltage / RESISTANCE if delivered else 0,
            "rc_duration_s": duration,
            "forecast_high_flow": bool(action), "vote_entropy": disagreement,
            "sampled_outcome_high_flow": (
                bool(target) if target is not None else None
            ),
            "garden_tick": garden.tick_count,
            "garden": garden.snapshot(),
            "expert_trust": {e.name: agent.trust(world.regime, e.name) for e in agent.experts},
        }
        pending = world, bool(delivered)
        previous_flow = flow


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, help="1 Hz rows of flow_lps,temperature_c and optional downstream_flow_lps")
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args()
    for record in run(args.csv, args.seed):
        print(json.dumps(record))


if __name__ == "__main__":
    main()
