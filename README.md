# github.com-GAIR-NLP-ASI-Evolve

**`asi-core`** — a small, reusable distillation of the
[ASI-Evolve](https://github.com/GAIR-NLP/ASI-Evolve) loop (GAIR-NLP), meant to
be shared across projects. ASI-Evolve replaces manual experimentation with a
continuous, AI-driven cycle:

> **LEARN** (retrieve knowledge) → **DESIGN** (propose a candidate) →
> **EXPERIMENT** (run + measure) → **ANALYZE** (extract a lesson) → repeat.

This repo is the **domain-agnostic engine**. Plug in three agents for any task
with a measurable objective and it iterates autonomously toward better
candidates.

## Layout

```
asi_core/
  loop.py                 # EvolveLoop: the LEARN->DESIGN->EXPERIMENT->ANALYZE engine
  config.py               # EvolveConfig (mirrors ASI-Evolve's config.yaml)
  pipeline/base.py        # Researcher, Engineer, Analyzer (the three agents)
  cognition/store.py      # CognitionStore (keyword backend; swap in FAISS)
  database/
    experiment_db.py      # ExperimentDB + Candidate (full trial history)
    sampling.py           # parent selection: random | greedy | ucb1 | map_elites
examples/circle_packing/  # a runnable, dependency-free proof of the loop
docs/PORTING.md           # how to adopt it in oncology and the scanners
```

## Run the demo

No dependencies required (Python 3.10+):

```bash
python -m examples.circle_packing.run --rounds 300 --strategy greedy
python -m examples.circle_packing.run --rounds 300 --strategy ucb1
```

You should see the best score climb as the loop evolves layouts.

## Using it for a real domain

Implement a `Researcher`, `Engineer` and `Analyzer`, then:

```python
from asi_core import EvolveLoop, EvolveConfig
loop = EvolveLoop(researcher, engineer, analyzer,
                  config=EvolveConfig(rounds=200, strategy="ucb1"))
best = loop.run(seed_spec)
```

See [`docs/PORTING.md`](docs/PORTING.md) for the mapping to the `oncology`
research agent (full loop) and the arbitrage scanners (self-tuning sub-loop).
