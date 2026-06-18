"""Parent-selection strategies for the experiment database.

Each strategy chooses which prior candidate to evolve next, trading off
exploitation (use the best so far) against exploration (try elsewhere).
"""

from __future__ import annotations

import math
from typing import Callable, List, Optional


def random_select(cands, rng, **_):
    return rng.choice(cands)


def greedy_select(cands, rng, **_):
    best = max(c.score for c in cands)
    return rng.choice([c for c in cands if c.score == best])


def ucb1_select(cands, rng, ucb_c: float = 1.4, **_):
    unseen = [c for c in cands if c.n_selected == 0]
    if unseen:
        return rng.choice(unseen)
    total = sum(c.n_selected for c in cands)
    log_n = math.log(total)
    return max(cands, key=lambda c: c.score + ucb_c * math.sqrt(log_n / c.n_selected))


def map_elites_select(cands, rng, descriptor: Optional[Callable] = None, **_):
    """Keep the best candidate per behavior cell, then pick a random elite."""
    if descriptor is None:
        return greedy_select(cands, rng)
    elites: dict = {}
    for c in cands:
        cell = descriptor(c)
        if cell not in elites or c.score > elites[cell].score:
            elites[cell] = c
    return rng.choice(list(elites.values()))


STRATEGIES = {
    "random": random_select,
    "greedy": greedy_select,
    "ucb1": ucb1_select,
    "map_elites": map_elites_select,
}


def select(name: str, cands: List, rng, descriptor=None, ucb_c: float = 1.4):
    if not cands:
        raise ValueError("no candidates to select from")
    try:
        fn = STRATEGIES[name]
    except KeyError:
        raise ValueError(f"unknown strategy '{name}'. options: {list(STRATEGIES)}")
    return fn(cands, rng, descriptor=descriptor, ucb_c=ucb_c)
