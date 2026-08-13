# Frozen prospective trial: current DeepMind WOWII 291

Frozen: 2026-08-13 UTC, before evaluating any trial graph.

## Target

Only the current statement in
`FormalConjectures/WrittenOnTheWallII/GraphConjecture291.lean` is in scope:

```text
gamma_t(G) <= k_zero(G) + freqMinTriangles(G),
```

for a connected simple graph of order greater than two.  Here `k_zero` is the
least Havel--Hakimi iteration index, starting at zero, whose descending degree
list contains a zero or is empty.  `freqMinTriangles` counts vertices attaining
the minimum number of incident triangles.

The historical status, alternative meanings of `k`, and conjectures outside
the current DeepMind repository are out of scope for this frozen trial.

## Predeclared mechanism

Seek graphs simultaneously exhibiting:

1. large exact total domination number;
2. an early zero in the canonical Havel--Hakimi trajectory;
3. a low-frequency minimum triangle-incidence class.

The #61 work motivates changing degree geometry without relying on a fixed
realization of the Havel--Hakimi reductions.

## Frozen construction lanes

The following lanes, and only these lanes, will be evaluated in the discovery
phase.

1. **Nonuniform clique-block paths.** Cliques of pairwise varied orders joined
   in a path by one portal edge between consecutive blocks. Orders 3--9;
   between 2 and 8 blocks; monotone, alternating, and single-small-block size
   patterns.
2. **Regularized sparse triangle blocks.** Replace each vertex of paths,
   cycles, and cubic base graphs by a clique of size 3--6; join designated
   portals along base edges, with cyclic portal rotation where possible.
   Orders at most 42.
3. **Degree-preserving two-switch surgery.** Starting from lane-1 and lane-2
   graphs of order at most 36, enumerate at most 2,000 deterministic valid
   two-switches per seed, retaining connected graphs.  This lane tests whether
   the fixed Havel--Hakimi term can be held while triangle-frequency and total
   domination move.

No random graph family may be added after seeing results.  Deterministic
lexicographic enumeration and a fixed RNG seed of `29120260813` are permitted
only to subsample an already frozen surgery set.

## Budgets

- Discovery: at most 1,500 base constructions and 20,000 surgery graphs.
- Every subprocess: at most 60 seconds.
- Every total-domination ILP: CBC `timeLimit=60`; a nonoptimal solve is logged
  as `TIMEOUT` and cannot support a crossing.
- Exact candidates retained only when
  `gamma_t > k_zero + freqMinTriangles`.
- Near-wall graphs with slack in `[-2,2]` are logged for structural diagnosis.

## Mandatory crossing protocol

For every apparent crossing, before any discovery claim:

1. independently recompute connectivity, triangle incidences, the entire
   Havel--Hakimi trajectory and first-zero index using a separate code path;
2. independently recompute total domination by exhaustive subset enumeration
   when feasible, otherwise by a separately formulated ILP plus witness and
   lower-bound audit;
3. run the same reading on all connected Atlas graphs through order seven and
   the standard sanity set `C5--C9`, `P7`, Petersen, `K3,3`, `K7`, stars, and
   complete bipartite graphs;
4. reject the reading if a sanity/database graph crosses;
5. append all evidence to the ledger before alerting the parent.

No novelty claim, public action, issue, PR, release, commit, or push is
authorized in this lane.

## Frozen verdict rule

- `CANDIDATE`: exact strict crossing surviving all four mandatory checks.
- `HOLD_BOUNDED`: no crossing within the frozen construction and compute
  budget.
- `INCONCLUSIVE`: a potentially crossing graph lacks an exact total-domination
  result within the ILP cap.

