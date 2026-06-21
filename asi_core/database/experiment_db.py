from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any, Callable, List, Optional

from asi_core.database import sampling


@dataclass
class Candidate:
    """One trial: its motivation, spec, measured result and analysis."""

    id: int
    spec: Any
    motivation: str = ""
    parent_id: Optional[int] = None
    round: int = 0
    metrics: dict = field(default_factory=dict)
    score: float = 0.0
    analysis: str = ""
    n_selected: int = 0  # times chosen as a parent (used by ucb1)

    def summary(self) -> str:
        return (
            f"#{self.id} (r{self.round}, parent={self.parent_id}) "
            f"score={self.score:.4f} :: {self.motivation}"
        )


class ExperimentDB:
    """In-memory store of every candidate, with parent sampling."""

    def __init__(self):
        self._nodes: List[Candidate] = []
        self._next_id = 0

    def add(
        self,
        spec,
        motivation: str = "",
        parent_id: Optional[int] = None,
        round: int = 0,
        metrics: Optional[dict] = None,
        score: float = 0.0,
        analysis: str = "",
    ) -> Candidate:
        cand = Candidate(
            id=self._next_id,
            spec=spec,
            motivation=motivation,
            parent_id=parent_id,
            round=round,
            metrics=metrics or {},
            score=score,
            analysis=analysis,
        )
        self._nodes.append(cand)
        self._next_id += 1
        return cand

    def all(self) -> List[Candidate]:
        return list(self._nodes)

    def get(self, cid: int) -> Candidate:
        return self._nodes[cid]

    def best(self) -> Optional[Candidate]:
        return max(self._nodes, key=lambda c: c.score) if self._nodes else None

    def select_parent(
        self,
        strategy: str,
        rng,
        descriptor: Optional[Callable] = None,
        ucb_c: float = 1.4,
    ) -> Candidate:
        chosen = sampling.select(strategy, self._nodes, rng, descriptor=descriptor, ucb_c=ucb_c)
        chosen.n_selected += 1
        return chosen

    def to_json(self) -> str:
        rows = [
            {k: v for k, v in asdict(c).items() if k != "spec"} for c in self._nodes
        ]
        return json.dumps(rows, indent=2)

    def __len__(self) -> int:
        return len(self._nodes)
