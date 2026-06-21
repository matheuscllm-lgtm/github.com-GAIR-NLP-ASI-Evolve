from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, List, Tuple


class Researcher(ABC):
    """DESIGN step: propose the next candidate from a parent + retrieved knowledge."""

    @abstractmethod
    def propose(self, parent, context: List[str], history) -> Tuple[Any, str]:
        """Return ``(spec, motivation)`` for the next experiment.

        ``spec`` is whatever the Engineer knows how to evaluate (code, params,
        a hypothesis). ``context`` is the knowledge retrieved this round.
        """


class Engineer(ABC):
    """EXPERIMENT step: execute a spec and measure it."""

    @abstractmethod
    def evaluate(self, spec) -> Tuple[dict, float]:
        """Return ``(metrics, score)``. Higher score is better."""


class Analyzer(ABC):
    """ANALYZE step: distill a transferable insight from a finished candidate."""

    @abstractmethod
    def analyze(self, candidate, history) -> str:
        """Return an insight string; it is stored back into the Cognition Store."""
