"""Run the circle-packing demo:  python -m examples.circle_packing.run"""

from __future__ import annotations

import argparse
import random

from asi_core.cognition.store import CognitionStore
from asi_core.config import EvolveConfig
from asi_core.loop import EvolveLoop
from examples.circle_packing.domain import (
    PackAnalyzer,
    PackEngineer,
    PackResearcher,
    behavior_descriptor,
    seed_spec,
)


def main():
    ap = argparse.ArgumentParser(description="asi-core demo: circle packing")
    ap.add_argument("--rounds", type=int, default=300)
    ap.add_argument(
        "--strategy",
        default="greedy",
        choices=["random", "greedy", "ucb1", "map_elites"],
    )
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    config = EvolveConfig(rounds=args.rounds, strategy=args.strategy, seed=args.seed)
    rng = random.Random(args.seed)

    cognition = CognitionStore()
    cognition.seed(
        [
            "spread points evenly to maximize the minimum pairwise distance",
            "points stuck near the border reduce the achievable spacing",
        ]
    )

    loop = EvolveLoop(
        researcher=PackResearcher(rng),
        engineer=PackEngineer(),
        analyzer=PackAnalyzer(),
        config=config,
        cognition=cognition,
        behavior_descriptor=behavior_descriptor,
    )

    seed = loop.db  # noqa: F841 (kept for clarity of the wiring)
    best = loop.run(seed_spec(rng), seed_motivation="random initial layout")

    print(f"\nstrategy = {args.strategy}   rounds = {args.rounds}")
    print(f"experiments run : {len(loop.db)}")
    print(f"best result     : {best.summary()}")


if __name__ == "__main__":
    main()
