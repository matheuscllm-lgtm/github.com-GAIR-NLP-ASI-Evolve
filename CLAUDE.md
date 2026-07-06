# CLAUDE.md — github.com-GAIR-NLP-ASI-Evolve

Instruções para qualquer sessão Claude Code (local ou nuvem) que trabalhe neste repo.
O operador (Matheus) é médico, não-programador: explique termos técnicos em
linguagem simples na primeira ocorrência, mantendo precisão.

> **O que é isto, em uma frase:** o **`asi-core`** — uma destilação pequena e
> reutilizável do loop do [ASI-Evolve](https://github.com/GAIR-NLP/ASI-Evolve)
> (framework do grupo GAIR-NLP) que substitui experimentação manual por um ciclo
> contínuo dirigido por IA: **LEARN** (recuperar conhecimento) → **DESIGN**
> (propor um candidato) → **EXPERIMENT** (rodar + medir) → **ANALYZE** (extrair
> lição) → repetir. Este repo é o **motor genérico** ("domain-agnostic": não
> sabe nada do problema); pluga-se três agentes para qualquer tarefa com
> objetivo mensurável e o loop itera sozinho rumo a candidatos melhores.

Glossário mínimo: **loop** = ciclo que se repete; **candidato** = uma tentativa
de solução (código, parâmetros, uma hipótese); **score** = a nota numérica que
mede quão boa a tentativa foi (maior = melhor); **agente** = um componente com
papel fixo dentro do ciclo (aqui são classes Python, com ou sem LLM por trás);
**LLM** = modelo de linguagem grande (a IA que gera texto/código).

## Relação com os repos irmãos (3 repos, papéis diferentes)

| Repo (GitHub `matheuscllm-lgtm/…`) | Pasta local (nuvem) | O que é |
|---|---|---|
| `github.com-GAIR-NLP-ASI-Evolve` (**ESTE**) | `/home/user/github.com-GAIR-NLP-ASI-Evolve` | **Port/reimplementação enxuta**: só o motor (`asi_core/`), um exemplo executável sem dependências e o guia de adoção (`docs/PORTING.md`). Não contém código de LLM — é a versão limpa pra ser compartilhada entre projetos. |
| `asi-evolve` | `/home/user/asi-evolve` | O código **original completo** do ASI-Evolve (main.py, pipeline, cognition, database, skills, utils) **com os experimentos da frota de scanners Pokémon** (`experiments/`: `cardtrader_vintage`, `comc_tiers`, `liga_match`, `myp_match`, além de `best` e `circle_packing_demo`) e o `HANDOFF-self-evolving-integration.md` (estado dos runs ao vivo). É onde os experimentos com LLM de verdade rodaram. |
| `asi-main` | `/home/user/asi-main` | A mesma base original, **sem** os experimentos da frota (só `best` e `circle_packing_demo`) — cópia "limpa" do upstream. |

**Papel DESTE repo** (racional em `docs/PORTING.md`): extrair do ASI-Evolve o
que é reutilizável — loop, cognition store, experiment DB, amostragem de
parent — num pacote mínimo, pra ser adotado nos outros projetos do operador:
o agente de pesquisa `oncology` (loop completo) e os scanners de arbitragem
(sub-loop de auto-ajuste). Ver a seção "Como portar um domínio novo" abaixo.

> Lição da frota vinda dos runs ao vivo no repo `asi-evolve` (registrada nos
> CLAUDE.md dos scanners): aliases de set deduzidos por LLM saíram
> **alucinados** — ganho descoberto pelo loop foi **portado à mão** para
> produção após validação, nunca copiado cego.

## Como rodar

**Sem dependências** — o motor roda só com a biblioteca padrão do Python
(3.10+; verificado funcionando com o 3.11 deste container). O
`requirements.txt` só lista opcionais (ver "Configuração").

```bash
cd /home/user/github.com-GAIR-NLP-ASI-Evolve   # rode da RAIZ do repo (execução por módulo)
python -m examples.circle_packing.run --rounds 300 --strategy greedy
python -m examples.circle_packing.run --rounds 300 --strategy ucb1
```

O demo **circle packing** ("empacotamento de círculos": espalhar 10 pontos num
quadrado maximizando a menor distância entre eles) é um domínio de brinquedo,
sem LLM e sem GPU, que prova o motor ponta a ponta em segundos. Saída esperada:
número de experimentos + o melhor resultado (o score sobe conforme o loop
evolui os layouts).

Flags do demo (verificadas no `argparse` de `examples/circle_packing/run.py`):

- `--rounds` (default `300`) — quantas rodadas do ciclo rodar.
- `--strategy` (default `greedy`) — estratégia de seleção de parent; opções:
  `random` | `greedy` | `ucb1` | `map_elites` (ver "Configuração").
- `--seed` (default `0`) — semente do gerador aleatório (mesma seed = mesmo
  resultado, reprodutível).

Setup opcional (só se for usar `EvolveConfig.from_yaml`):

```bash
pip install -r requirements.txt   # instala pyyaml (único item não comentado)
```

## Configuração (`config.yaml` + `asi_core/config.py`)

O `config.yaml` da raiz é um **arquivo de exemplo** dos knobs de um run,
consumível via `EvolveConfig.from_yaml("config.yaml")` (exige `pyyaml`;
chaves desconhecidas são ignoradas). ⚠️ **O demo NÃO lê o `config.yaml`** —
`run.py` monta o `EvolveConfig` direto das flags do CLI. Campos (defaults do
dataclass em `asi_core/config.py`; o yaml da raiz sobrescreve `rounds: 300`):

| Campo | Default (código) | O que controla |
|---|---|---|
| `rounds` | `100` | nº de rodadas do loop |
| `strategy` | `greedy` | como escolher o **parent** (o candidato-base da próxima rodada): `random` (sorteio), `greedy` (sempre o melhor score), `ucb1` (equilibra explorar novidade × aproveitar o melhor, com bônus pra quem foi pouco tentado), `map_elites` (guarda o melhor por "célula de comportamento" e sorteia entre esses elites — exige passar um `behavior_descriptor` ao loop) |
| `retrieval_k` | `3` | quantas entradas do cognition store alimentam cada passo DESIGN |
| `ucb_c` | `1.4` | constante de exploração do `ucb1` (maior = explora mais) |
| `seed` | `0` | semente aleatória (reprodutibilidade) |
| `model` | `""` | identificador de LLM para um agente apoiado em modelo — **opcional e hoje não consumido por nenhum código do motor** (é um placeholder pra implementações futuras de Researcher/Analyzer com LLM) |

**Chaves de API / env vars:** nenhum código deste repo lê variável de ambiente
ou chave de API hoje (verificado por busca: zero ocorrências de
`environ`/`getenv`/`api_key`). O `requirements.txt` comenta os opcionais de
produção — `numpy` (engineers vetorizados), `faiss-cpu` (backend de embeddings
do CognitionStore) e o SDK `anthropic` (agentes Researcher/Analyzer apoiados em
LLM). Se um dia agentes com LLM entrarem aqui: chave **só** em env var ou
`.env` local (já está no `.gitignore`) — **nunca versionada**.

## Arquitetura

```
asi_core/                        o motor (domain-agnostic, stdlib pura)
  __init__.py                    exporta a API pública: EvolveLoop, EvolveConfig,
                                 CognitionStore, ExperimentDB, Candidate,
                                 Researcher, Engineer, Analyzer
  loop.py                        EvolveLoop: o ciclo LEARN->DESIGN->EXPERIMENT->ANALYZE;
                                 aceita cognition/db/behavior_descriptor/on_round opcionais
  config.py                      EvolveConfig (dataclass) + from_yaml (pyyaml opcional)
  pipeline/base.py               as 3 classes abstratas ("contratos" a implementar):
                                 Researcher.propose -> (spec, motivation)
                                 Engineer.evaluate  -> (metrics, score)  # score: maior = melhor
                                 Analyzer.analyze   -> insight (string, volta pro cognition)
  cognition/store.py             CognitionStore: memória de insights do passo LEARN.
                                 Backend default = retrieval por palavra-chave (Jaccard),
                                 sem dependências; p/ produção, subclasse com índice
                                 vetorial (ex. FAISS)
  database/
    experiment_db.py             ExperimentDB (histórico em memória de todo candidato,
                                 com to_json) + Candidate (spec, parent_id, metrics,
                                 score, analysis, n_selected)
    sampling.py                  estratégias de seleção de parent:
                                 random | greedy | ucb1 | map_elites
examples/circle_packing/         prova executável do loop (sem dependências)
  domain.py                      PackResearcher/PackEngineer/PackAnalyzer + seed_spec
                                 + behavior_descriptor (célula MAP-Elites = centroide)
  run.py                         CLI do demo (--rounds/--strategy/--seed)
docs/PORTING.md                  guia de adoção nos outros projetos (oncology + scanners)
config.yaml                      exemplo de configuração de run (ver seção acima)
requirements.txt                 pyyaml (opcional) + opcionais comentados
.claude/commands/auto.md         skill /auto (ver seção no fim)
```

Fluxo de um round (em `loop.py`): consulta o cognition store com a análise do
parent (LEARN) → `Researcher.propose` gera o próximo spec (DESIGN) →
`Engineer.evaluate` roda e pontua (EXPERIMENT) → `Analyzer.analyze` destila um
insight que volta pro cognition store (ANALYZE) → `db.select_parent` escolhe de
quem evoluir na próxima rodada. `loop.run(seed_spec)` retorna o melhor
`Candidate` ao final.

## Como portar/criar um domínio novo (resumo de `docs/PORTING.md` — leia-o)

Um domínio = **3 agentes + um score**. O motor (loop, cognition, DB, sampling)
fica intocado. Mapeamento:

| Conceito ASI-Evolve | Classe asi-core | Você implementa |
|---|---|---|
| LEARN | `CognitionStore` | semeie com o conhecimento do domínio (`.seed([...])`) |
| DESIGN | `Researcher` | propor o próximo candidato a partir de um parent |
| EXPERIMENT | `Engineer` | rodar o candidato, devolver `(metrics, score)` |
| ANALYZE | `Analyzer` | destilar um insight reutilizável |
| seleção de parent | `database.sampling` | escolher a estratégia no config |

Os dois alvos previstos no PORTING.md:

1. **`oncology` — loop completo (melhor encaixe):** cognition = literatura
   (bioRxiv/ChEMBL/ClinicalTrials); Researcher = propor a próxima hipótese
   terapêutica (LLM-backed); Engineer = consultar as fontes de evidência e
   pontuar plausibilidade; Analyzer = resumir o que a evidência implica;
   sampling `ucb1`/`map_elites` pra explorar mecanismos distintos.
2. **Scanners de arbitragem — encaixe parcial (auto-ajuste, não o loop
   inteiro):** o candidato é uma **configuração de busca** (fontes, threshold,
   FX, filtros), não uma invenção nova a cada rodada. Porta-se só Engineer
   (rodar um scan com a config e pontuar por **ROI líquido realizado**) +
   ExperimentDB/sampling; **pula-se o Researcher criativo** (baixo payoff).
   Segundo piloto sugerido: `integrated-scanner`.

Template mínimo de código: seção "Minimal template" do `docs/PORTING.md`
(subclasses de `Researcher`/`Engineer`/`Analyzer` + `EvolveLoop(...).run(seed)`).

## Testes

**Não há suíte de testes neste repo** (não existe pasta `tests/` nem config de
pytest — honestamente: nada a rodar). A verificação prática do motor é o
próprio demo, que é determinístico por seed:

```bash
python -m examples.circle_packing.run --rounds 50 --strategy greedy
```

Se um dia entrar uma suíte, atualize esta seção.

## Fluxo de desenvolvimento e segurança

- **Branch + PR, nunca push direto na `main`** — é como todo o histórico do
  repo foi construído (asi-core #1, skill /auto #2, melhoria do /auto #3),
  padrão da frota.
- **Gitignored:** `__pycache__/`, `*.py[cod]`, `.venv/`/`venv/`, `.env`,
  `*.egg-info/`, `.pytest_cache/`.
- **Segredos:** o repo não tem nenhum e nenhum código lê chave. Se agentes
  LLM-backed forem adicionados, chave só em env var / `.env` local — nunca em
  arquivo versionado (cuidado com a família de erro nº 1 da frota: BOM/
  zero-width ao setar chave).
- Dados/saídas de experimento não têm pasta própria aqui (o demo só imprime no
  terminal); se um port gerar artefatos, mantenha-os fora do versionamento.

## Skill `/auto` (`.claude/commands/auto.md`)

O repo tem uma única skill/command: **`/auto`** — o modo autônomo genérico da
frota (mesmo contrato sincronizado nos outros repos, na **versão genérica**,
não a variante "agente master de arbitragem"). Executa a tarefa ponta a ponta
(corrigir, integrar, testar, commitar, abrir **PR draft**, mergear só quando
trivialmente seguro) sem pedir confirmação, **salvo risco alto** (perda de
dados, segredo/credencial, custo relevante, decisão irreversível — nesses casos
para e pergunta). Inclui pré-voo obrigatório (ler o CLAUDE.md do repo, checar
handoff, confirmar branch), checkpoints frequentes e resumo final honesto.
Leia o arquivo antes de operar nesse modo; em sessão de nuvem, operações GitHub
vão pelas ferramentas `mcp__github__*` (o `gh` CLI não está disponível lá).
