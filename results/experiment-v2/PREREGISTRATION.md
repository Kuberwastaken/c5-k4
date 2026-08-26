# Experiment v2 — execution preregistration

**Committed before any generic or wall arm output exists.** The catalogue arm
has already run (see below); nothing about the rule, endpoint, budgets, or
adjudication depends on its outcome.

## Order-of-record

1. `scripts/exp2/adjudicate2.py` was committed (80e4778) **before any v2 arm
   wrote a verdict**, together with the shared evaluator (`common_eval2.py`),
   the selective certifier (`certify2.py`), and the catalogue driver
   (`catalogue2.py`). That commit is the preregistration artifact for the
   scoring rule; the decision rule itself is unchanged from the frozen
   `DESIGN.md`.
2. Arms run **strictly sequentially, as deterministic script invocations by the
   orchestrator** — no LLM agent participates inside an arm, no arm process
   reads another arm's files, and each arm's session exits before the next
   starts (METHOD v1.7 R2: isolation covers files and process tables; a
   non-agent script cannot read `ps`, which is how the v1 contamination event
   happened). Non-arm research lanes ran concurrently on this box throughout;
   they never touch `results/experiment-v2/arm-*`.

## Budgets (frozen here, before the remaining two arms report)

- **Catalogue**: no budget beyond the standing per-solver cap (60 s wall per
  invariant per graph); an unresolved pair scores BRACKET for every target
  needing it. DONE: ran 3001 s, outputs `arm-catalogue.{json,md}`.
- **Generic** (adapted from v1 `scripts/exp/generic/search.py`): simulated
  annealing + random construction without structural insight, evaluated through
  the same `certify2`/`expressions2` exact paths. Budget: **3600 CPU-seconds
  per target**, staged (600 / 1200 / 1800), single process per target,
  evaluation-order caps per GENERATION.md section 5 (targets naming `f`/`tree`
  capped at n = 30; others n = 40; sparse constructions may exceed the nominal
  cap only with the cap recorded). R3 requires HELD/CROSSED on >= 75% of
  scored targets; the bracket count is reported either way.
- **Wall** (fresh implementation of the v1 wall method): reads only
  `population/population.json` tightness data, applies the R1 step-aware sign
  check, designs separating families, bounded trials at the same per-solver
  caps. Runs only after the generic arm's process has exited.
- **Adjudication**: `adjudicate2.py --partial` may be run at any time for
  observability; the binding adjudication happens once all three arms exist.

## Deviations

None as of this commit.
