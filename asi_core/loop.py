from __future__ import annotations

import random
from typing import Callable, Optional

from asi_core.cognition.store import CognitionStore
from asi_core.config import EvolveConfig
from asi_core.database.experiment_db import Candidate, ExperimentDB
from asi_core.pipeline.base import Analyzer, Engineer, Researcher


class EvolveLoop:
    """The LEARN -> DESIGN -> EXPERIMENT -> ANALYZE engine.

    Domain-agnostic: supply a Researcher, Engineer and Analyzer for any task
    with a measurable objective and the loop iterates toward better candidates.
    """

    def __init__(
        self,
        researcher: Researcher,
        engineer: Engineer,
        analyzer: Analyzer,
        config: Optional[EvolveConfig] = None,
        cognition: Optional[CognitionStore] = None,
        db: Optional[ExperimentDB] = None,
        behavior_descriptor: Optional[Callable[[Candidate], tuple]] = None,
        on_round: Optional[Callable[[Candidate], None]] = None,
    ):
        self.researcher = researcher
        self.engineer = engineer
        self.analyzer = analyzer
        self.config = config or EvolveConfig()
        self.cognition = cognition or CognitionStore()
        self.db = db or ExperimentDB()
        self.behavior_descriptor = behavior_descriptor
        self.on_round = on_round
        self.rng = random.Random(self.config.seed)

    def _experiment_and_analyze(self, spec, motivation, parent_id, rnd) -> Candidate:
        metrics, score = self.engineer.evaluate(spec)  # EXPERIMENT
        cand = self.db.add(
            spec=spec,
            motivation=motivation,
            parent_id=parent_id,
            round=rnd,
            metrics=metrics,
            score=score,
        )
        insight = self.analyzer.analyze(cand, self.db.all())  # ANALYZE
        cand.analysis = insight
        self.cognition.add(insight, meta={"candidate_id": cand.id, "score": score})
        if self.on_round:
            self.on_round(cand)
        return cand

    def run(self, seed_spec, seed_motivation: str = "seed") -> Optional[Candidate]:
        parent = self._experiment_and_analyze(seed_spec, seed_motivation, None, 0)
        for rnd in range(1, self.config.rounds + 1):
            context = self.cognition.query(  # LEARN
                parent.analysis or parent.motivation, k=self.config.retrieval_k
            )
            spec, motivation = self.researcher.propose(  # DESIGN
                parent, context, self.db.all()
            )
            self._experiment_and_analyze(spec, motivation, parent.id, rnd)
            parent = self.db.select_parent(  # pick whom to evolve next
                self.config.strategy,
                self.rng,
                descriptor=self.behavior_descriptor,
                ucb_c=self.config.ucb_c,
            )
        return self.db.best()
