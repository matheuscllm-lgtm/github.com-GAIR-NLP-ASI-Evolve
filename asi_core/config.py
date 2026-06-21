from __future__ import annotations

from dataclasses import dataclass


@dataclass
class EvolveConfig:
    """Global knobs for a run. Mirrors ASI-Evolve's config.yaml defaults."""

    rounds: int = 100
    strategy: str = "greedy"      # random | greedy | ucb1 | map_elites
    retrieval_k: int = 3          # cognition entries pulled into each DESIGN step
    ucb_c: float = 1.4            # exploration constant for the ucb1 strategy
    seed: int = 0
    model: str = ""               # identifier for an LLM-backed agent (optional)

    @classmethod
    def from_yaml(cls, path: str) -> "EvolveConfig":
        import yaml  # optional dependency; see requirements.txt

        with open(path) as f:
            data = yaml.safe_load(f) or {}
        known = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}
        return cls(**known)
