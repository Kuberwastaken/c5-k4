# Graph Brain alpha lower-bound sweep

Audit date: **2026-08-12**. Primary manifest:
`corpora/graphbrain_open_alpha.json`, preserving author-project issue #421.
This ledger covers all **89** `graphbrain-alpha-lower-*` lines exactly once.

## Method and invariant semantics

Statements are quoted exactly from the issue-derived corpus. Evaluation uses
the campaign arsenal and the required DB-sanity gate: all 995 nontrivial
connected graphs in `networkx.graph_atlas_g()` (orders 2--7), plus cycles,
paths, Petersen, complete, star, and complete-bipartite controls. Expressions
outside their real domain or containing a zero denominator are not silently
extended. Trigonometric functions use radians, matching the author code.

Crucially, Graph Brain's primary `src/Invariants/invariants.sage` defines
`max_even_minus_even_horizontal` with an accumulator initialized to zero. It
returns `max(0, |Even(v)|-|E(G[Even(v)])|)` on a connected component. Thus it
is **0**, not the WoW-style signed value -19, on `C5[K4]`. Every entry below
uses the author implementation. This source check prevents a false apparent
violation of lower-078.

Verdicts mean: `HOLD_ARSENAL` (no arsenal violation); `HOLD_TIGHT` (an arsenal
equality); `RETRO_KILL` (the open-as-posted line has a gate-surviving
counterexample, without a novelty claim); `DB_REJECTED` (an apparent arsenal
violation is already present in the required small database); and
`SKIP_UNDEFINED` (the expression is not real/defined on a relevant graph and
the source supplies no totalization).

