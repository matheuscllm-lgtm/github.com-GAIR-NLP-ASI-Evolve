"""asi-core: a domain-agnostic LEARN -> DESIGN -> EXPERIMENT -> ANALYZE engine.

A small, reusable distillation of the ASI-Evolve loop (GAIR-NLP) meant to be
shared across projects (e.g. the oncology research agent and the arbitrage
scanners). Plug in three agents (Researcher, Engineer, Analyzer) for a domain
and the loop autonomously iterates toward a measurable objective.
"""

from asi_core.config import EvolveConfig
from asi_core.loop import EvolveLoop
from asi_core.cognition.store import CognitionStore
from asi_core.database.experiment_db import ExperimentDB, Candidate
from asi_core.pipeline.base import Researcher, Engineer, Analyzer

__all__ = [
    "EvolveConfig",
    "EvolveLoop",
    "CognitionStore",
    "ExperimentDB",
    "Candidate",
    "Researcher",
    "Engineer",
    "Analyzer",
]
