"""A tiny, dependency-free domain that proves the loop end to end.

Objective: place N points in the unit square so the *minimum* pairwise
distance is as large as possible (a circle-packing proxy). It needs no LLM and
no GPU, so the engine can be verified in seconds.
"""

from __future__ import annotations

import math

from asi_core.pipeline.base import Analyzer, Engineer, Researcher

N_POINTS = 10


def seed_spec(rng):
    return [(rng.random(), rng.random()) for _ in range(N_POINTS)]


def _min_pairwise(pts) -> float:
    m = float("inf")
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            m = min(m, math.hypot(pts[i][0] - pts[j][0], pts[i][1] - pts[j][1]))
    return m


class PackResearcher(Researcher):
    """DESIGN: perturb one point of the parent layout (guided local search)."""

    def __init__(self, rng, sigma: float = 0.08):
        self.rng = rng
        self.sigma = sigma

    def propose(self, parent, context, history):
        pts = list(parent.spec)
        i = self.rng.randrange(len(pts))
        x, y = pts[i]
        nx = min(1.0, max(0.0, x + self.rng.gauss(0, self.sigma)))
        ny = min(1.0, max(0.0, y + self.rng.gauss(0, self.sigma)))
        pts[i] = (nx, ny)
        return pts, f"perturb point {i} of #{parent.id}"


class PackEngineer(Engineer):
    """EXPERIMENT: score = minimum pairwise distance (spread the points out)."""

    def evaluate(self, spec):
        score = _min_pairwise(spec)
        return {"min_dist": score}, score


class PackAnalyzer(Analyzer):
    """ANALYZE: note progress relative to the best result so far."""

    def analyze(self, candidate, history):
        best = max(h.score for h in history)
        verdict = "new best" if candidate.score >= best else "no improvement"
        return f"r{candidate.round}: min_dist={candidate.score:.4f} ({verdict}; best={best:.4f})"


def behavior_descriptor(candidate):
    """MAP-Elites cell = quantized centroid of the layout."""
    pts = candidate.spec
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    return (round(cx, 1), round(cy, 1))
