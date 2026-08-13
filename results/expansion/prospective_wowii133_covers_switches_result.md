# Prospective WOWII #133 covers-and-switches result

Date: **2026-08-13 UTC**

Verdict: **HOLD_BOUNDED**.  The independently frozen cover/switch lane found
no counterexample to the current DeepMind WOWII #133 declaration.

## Scope and audit discipline

The contract in `prospective_wowii133_covers_switches_contract.md` was written
before evaluating any candidate.  This lane deliberately excluded the prior
alternate-handle geometry: it used no pendant path, edge subdivision, or
shifted-endpoint attachment.

The append-only ledger is
`prospective_wowii133_covers_switches_ledger.jsonl`.  All operating-system
processes were capped at 60 seconds.  Rows that exhausted a batch's remaining
internal time were preserved as timeouts and then replayed with a fresh
budget; every frozen index was ultimately resolved exactly.

## Database sanity

The exact evaluator passed all **1,014** gate graphs:

- every connected Graph Atlas graph of orders two through seven;
- `C5--C9`, `P7`, Petersen, `K3,3`, `K7`;
- the frozen stars and complete-bipartite controls.

There were zero negative residuals and zero unresolved gate cases.

## Frozen discovery

Exactly **1,500 distinct graph6 candidates** were completed:

| lane | distinct graphs | minimum residual | equalities |
|---|---:|---:|---:|
| named cages/generalized Petersen | 74 | 0 | 1 |
| projective-plane incidence graphs | 2 | 1 | 0 |
| connected `Z_3` voltage covers | 1,032 | 5 | 0 |
| C4-safe degree-preserving switches | 392 | 3 | 0 |

The only equality was the preregistered Petersen control:

```text
path=5, radius=2, floor(l)=3, R133=0.
```

The closest graph outside that equality control was Heawood (equivalently the
`PG(2,2)` Levi graph in the incidence lane):

```text
path=7, radius=3, floor(l)=3, R133=1.
```

Nontrivial covers and switches did not approach the wall.  Every `Z_3` cover
had residual at least five, and every accepted C4-safe switch had residual at
least three.  Thus the frozen prediction failed in the informative direction:
maximum induced-path order grew at least as fast as the radius term.

## Independent recomputation

`scripts/verify_prospective_wowii133_covers_switches.py` uses descending
vertex-subset enumeration rather than the discovery endpoint-extension DFS.
It independently recomputed the C4 predicate, radius, every local
neighborhood independence number, maximum induced-path order, and residual
on twelve closest order-at-most-20 representatives.  All twelve passed,
including Petersen, Heawood/`PG(2,2)`, and ten C4-safe Petersen switches.

## Current status

The current DeepMind declaration remains tagged `research open`.  A GitHub
search on 2026-08-13 found no issue or PR specifically claiming a solution or
disproof of WOWII #133; the relevant merged result was only batch-addition PR
#3820.  Because the frozen lane found no crossing, no graph/formula novelty
claim or broader web priority search is triggered.

## Diagnosis

This is negative evidence against cover-based radius separation.  It
reinforces the existing theorem signal for the cubic C4-free specialization:

```text
path(G) >= radius(G) + 3.
```

The next high-information action is structural proof work on that inequality,
not wider voltage enumeration.  No commit, release, or public action follows
from this trial.
