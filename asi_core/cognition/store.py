from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable, List, Optional


def _tokens(text: str) -> set:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


@dataclass
class Entry:
    text: str
    meta: dict = field(default_factory=dict)


class CognitionStore:
    """The retrieval backend for the LEARN step.

    The default backend is a dependency-free keyword (Jaccard) retriever so the
    loop runs out of the box. For production, pass an ``embed`` callable and
    swap in a vector index (e.g. FAISS) by subclassing and overriding ``query``.
    """

    def __init__(self, embed: Optional[Callable[[str], list]] = None):
        self._entries: List[Entry] = []
        self._embed = embed

    def add(self, text: str, meta: Optional[dict] = None) -> None:
        self._entries.append(Entry(text=text, meta=meta or {}))

    def seed(self, texts) -> None:
        for t in texts:
            self.add(t)

    def query(self, text: str, k: int = 3) -> List[str]:
        if not self._entries:
            return []
        q = _tokens(text)

        def sim(e: Entry) -> float:
            t = _tokens(e.text)
            if not q or not t:
                return 0.0
            return len(q & t) / len(q | t)

        ranked = sorted(self._entries, key=sim, reverse=True)
        return [e.text for e in ranked[:k]]

    def __len__(self) -> int:
        return len(self._entries)
