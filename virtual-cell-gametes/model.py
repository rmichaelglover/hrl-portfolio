"""Externally driven human fertilization bookkeeping; no fitted kinetics.

Boundary: euploid MII oocyte and acrosome-reacted, fusion-ready sperm
already at the oolemma. Event indices are NOT biological time.
"""
from dataclasses import asdict, dataclass, field
import json


@dataclass
class Fertilization:
    fused_sperm: list[str] = field(default_factory=list)
    activated: bool = False
    block_established: bool = False
    meiosis_complete: bool = False
    pronuclei: bool = False
    history: list[dict] = field(default_factory=list)

    def snapshot(self):
        # DNA units count haploid unreplicated nuclear genome equivalents (C).
        # The first polar body and all unfused sperm are outside this boundary.
        maternal_c = 1 if self.meiosis_complete else 2
        return {
            "fused_sperm": list(self.fused_sperm),
            "activated": self.activated,
            "block_established": self.block_established,
            "meiosis_complete": self.meiosis_complete,
            "pronuclei": self.pronuclei,
            "maternal_nuclear_dna_C": maternal_c,
            "paternal_nuclear_dna_C": len(self.fused_sperm),
            "second_polar_body_dna_C": int(self.meiosis_complete),
            "total_accounted_nuclear_dna_C": 2 + len(self.fused_sperm),
            "status": "polyspermy" if len(self.fused_sperm) > 1 else (
                "two_pronuclei" if self.pronuclei else "in_progress"),
        }

    def apply(self, event, sperm_id=None):
        """Supply an observed/assumed event, rejecting inconsistent ordering.

        Activation and effective block establishment are distinct supplied events.
        Multiple fusions before an effective block remain possible in this model.
        """
        if event == "fusion":
            if not isinstance(sperm_id, str) or not sperm_id.strip():
                raise ValueError("fusion requires a nonempty sperm_id")
            if sperm_id in self.fused_sperm:
                raise ValueError("the same sperm cannot fuse twice")
            if self.block_established or self.pronuclei:
                raise ValueError("fusion is outside the current permitted state")
            self.fused_sperm.append(sperm_id)
        elif event == "activation":
            if not self.fused_sperm or self.activated:
                raise ValueError("activation requires fusion and occurs once")
            self.activated = True
        elif event == "block_established":
            if not self.activated or self.block_established:
                raise ValueError("effective block requires activation and occurs once")
            self.block_established = True
        elif event == "meiosis_II_completion":
            if not self.activated or self.meiosis_complete:
                raise ValueError("meiosis completion requires activation and occurs once")
            self.meiosis_complete = True
        elif event == "pronuclear_formation":
            if not self.meiosis_complete or len(self.fused_sperm) != 1 or self.pronuclei:
                raise ValueError("normal two-pronucleus endpoint requires meiosis II and one sperm")
            self.pronuclei = True
        else:
            raise ValueError(f"unknown event: {event}")
        result = self.snapshot()
        self.history.append({"event_index": len(self.history), "event": event,
                             "sperm_id": sperm_id, "state": result})
        return result


def demonstration():
    normal = Fertilization()
    initial = normal.snapshot()
    for event in ("fusion", "activation", "block_established",
                  "meiosis_II_completion", "pronuclear_formation"):
        normal.apply(event, "sperm-1" if event == "fusion" else None)
    polyspermy = Fertilization()
    polyspermy.apply("fusion", "sperm-1")
    polyspermy.apply("fusion", "sperm-2")
    return {"evidence_status": "synthetic externally supplied events; no prediction",
            "initial": initial, "normal": asdict(normal),
            "polyspermy": asdict(polyspermy)}


if __name__ == "__main__":
    print(json.dumps(demonstration(), indent=2))
