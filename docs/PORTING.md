# Porting asi-core to the other projects

`asi-core` is the reusable distillation of the ASI-Evolve loop. To adopt it in
another repo you implement **one domain** = three agents + a score. The engine
(loop, cognition store, experiment DB, sampling) stays untouched.

| ASI-Evolve concept | asi-core class      | What you implement per project |
|--------------------|---------------------|--------------------------------|
| LEARN              | `CognitionStore`    | seed it with your domain knowledge |
| DESIGN             | `Researcher`        | propose the next candidate from a parent |
| EXPERIMENT         | `Engineer`          | run the candidate, return `(metrics, score)` |
| ANALYZE            | `Analyzer`          | distill a reusable insight |
| parent selection   | `database.sampling` | pick a strategy in `config.yaml` |

---

## 1. `oncology` — full loop (best fit)

This is the same shape as ASI-Evolve's biomedical track, so the **complete**
LEARN→DESIGN→EXPERIMENT→ANALYZE loop applies.

- **Cognition** = literature (the bioRxiv / ChEMBL / ClinicalTrials sources).
- **Researcher** = propose the next therapeutic hypothesis / target from a
  parent hypothesis + retrieved papers (an LLM-backed `propose`).
- **Engineer** = query the evidence sources, score plausibility / support
  (e.g. bioactivity, trial signal). Returns `metrics + score`.
- **Analyzer** = summarise what the evidence implies; feed it back to cognition
  so the next round is better informed.
- **Sampling** = `ucb1` or `map_elites` to keep exploring distinct mechanisms
  rather than over-fitting one promising lead.

## 2. The arbitrage scanners — partial fit (self-tuning, not the full loop)

For the scanners (`liga-cards`, `card-trader`, `sealed`, `scanner-comc`,
`ebay`, `integrated`, ...) the candidate is **not a new invention each round**;
it is a **search configuration**. Port only two pieces:

- **Engineer** = run a scan with a given config (sources, margin threshold, FX
  rate, condition/fraud filters) and score it by **realised net ROI** of the
  opportunities it surfaced — not gross margin.
- **Experiment DB + sampling (`map_elites`/`ucb1`)** = let the system converge
  on the configs that actually make money, treating each config as a candidate.
- **Analyzer** = turn opportunity history into rules ("set X from source Y is
  always phantom margin after shipping") that prune future configs.

Skip the *creative* `Researcher` here — inventing brand-new strategies from
scratch has low payoff for a scanner. Start with `integrated-scanner` (it
already aggregates the others) as the second pilot.

---

## Minimal template

```python
from asi_core import EvolveLoop, EvolveConfig, Researcher, Engineer, Analyzer

class MyResearcher(Researcher):
    def propose(self, parent, context, history): ...   # -> (spec, motivation)

class MyEngineer(Engineer):
    def evaluate(self, spec): ...                      # -> (metrics, score)

class MyAnalyzer(Analyzer):
    def analyze(self, candidate, history): ...         # -> insight str

loop = EvolveLoop(MyResearcher(), MyEngineer(), MyAnalyzer(),
                  config=EvolveConfig(rounds=200, strategy="ucb1"))
best = loop.run(seed_spec)
```
