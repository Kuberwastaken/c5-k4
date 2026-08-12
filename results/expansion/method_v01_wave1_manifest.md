# Method v0.1 development Wave 1: frozen manifest

Frozen: **2026-08-12T22:35:40Z**
Method commit: `0287c2eb53eaa29cc2e11aabfc9ba58f5e5ae12e`
WOWII transcription: `data/wowii-conjectures.json` at the method commit
Upstream comparison base: `google-deepmind/formal-conjectures` `upstream/main`
at `547f309edcc2069c1f61c2465729031c10385540`

This manifest was committed before any Wave 1 scout returned a verdict. These
are development-set trials: every target or cluster was discussed or ranked
before Method v0.1 and cannot later count as held-out evidence.

## Shared gates

Every trial uses the phases and outcome ledger in [`METHOD.md`](../../METHOD.md):

- source/readings frozen before witness evaluation;
- connected Graph Atlas through order seven plus named controls;
- exact arithmetic and a 60-second optimization cap;
- prediction recorded before construction;
- independent recomputation for every apparent crossing;
- source/status/novelty audit before any new-disproof claim;
- no-`sorry`, warning-clean Lean certificate before an upstream submission.

Searches write incrementally. A zero, theorem shadow, rejected reading, or
timeout is a reportable outcome rather than an invitation to move the bound.

## Trial A: WOWII 422b

Source statement:

```text
i(G) <= alpha(G[M]) + gamma(G[V-M])^2,
```

for connected `G` of order greater than three, where `M` is the set of
maximum-degree vertices.

Observed wall before Wave 1: equality on uniform odd-cycle clique blow-ups and
on `comp(C5[K4])`. Regularity forces `M=V`, so the residual becomes the
universal `i(G)<=alpha(G)` equality/inequality and cannot cross.

Pre-evaluation prediction: nonuniform clique blow-ups can make the maximum-
degree subgraph have small independence while preserving a larger independent
dominating set. A crossing additionally requires `gamma(G[V-M])` to be zero or
one; otherwise the square term is likely too expensive.

Frozen bounds:

- connected quotient graphs of order at most nine;
- exact positive integer blob weights;
- expanded order at most 100;
- continuous/linear feasibility prefilter where applicable;
- each exact independent-domination or domination solve capped at 60 seconds.

Primary report: `method_v01_422b.md`.

## Trial B: WOWII 430c and 434c

Source statements:

```text
430c: i(G) <= lambda_max(G) * residue(G^2) + Delta(G[M]).

434c: i(G) <= delta(G[V-M]) + 1 + SW(complement G),
      with the +1 omitted when delta(G)=1.
```

Observed state before Wave 1: both hold with substantial slack on `C5[K4]`;
430a showed that nonuniform path-clique blow-ups can decouple independent
domination from a center/Caro--Wei correction.

Pre-evaluation prediction for 430c: a useful family needs `i` at least three,
small local independence, small square residue, and a maximum-degree induced
subgraph with very small maximum degree. Nonuniform weights may isolate the
maximum-degree vertices rather than making `M=V`.

Pre-evaluation prediction for 434c: make `G[V-M]` sparse while keeping the
Szekeres--Wilf number of the complement small; the likely obstruction is that
the same sparsity makes the complement locally dense and raises `SW`. This may
produce a theorem signal rather than a crossing.

Frozen bounds are the Trial A quotient/weight/order bounds, with the same
60-second exact-solve cap. The cluster is counted as one method trial even if
both formulas move.

Primary report: `method_v01_430c_434c.md`.

## Trial C: WOWII 169/174/180/182 barbell neighborhood

Source statements:

```text
169: L_s >= 1 + max dist_even(v) - min dist_even(v).
174: L_s + b >= n + max lambda(v) - 1.
180: L_s + b >= 1 + alpha + max dist_even(v).
182: L_s + b >= Delta(B(G^2)) + diam(G).
```

Observed wall before Wave 1: even barbell members are tight on 169 and 180 and
one unit safe on nearby 174/182 cases. The proved 173 baseline must be
subtracted wherever it controls `L_s+b`.

Pre-evaluation prediction: one or two symmetry-orbit edge edits, or replacing
the endpoint triangles by small cliques, may move a parity-distance or square-
periphery term by one while preserving the small connected domination core.
The main failure mode is that the same edit increases `L_s` or `b` enough to
restore the inequality.

Frozen bounds:

- base barbells `D6`, `D8`, and `D10`;
- every automorphism-orbit representative through two edge additions or
  deletions;
- endpoint clique substitutions `K2` through `K5`;
- no expansion beyond the smallest path parameters needed to realize these
  cases;
- every exact optimization call capped at 60 seconds.

The four formulas form one method trial. Primary report:
`method_v01_barbell_cluster.md`.

## Trial D: WOWII 183 theory lane

Source statement:

```text
L_s(G) + b(G) >= Delta(G^2) + 2 rad(G^2).
```

Pre-Wave reduction: with `r=rad(G^2)` and
`q=n-1-Delta(G^2)`, a geodesic argument gives `q>=2r-3`. Subtracting the
proved 173 baseline leaves only the extremal case `q=2r-3`; the remaining
candidate lemma is essentially

```text
q=2r-3 and G nonbipartite  =>  b(G) >= gamma_c(G)+2.
```

Pre-evaluation prediction: this is more likely a theorem/equality-
characterization problem than a counterexample lane. A valid outcome is a
proof, a smaller structural subcase, a counterexample to the proposed lemma,
or a sharpened theorem signal. Search bounds remain those already recorded in
`wowii_183_theorem_signal.md`; new computation must be justified by a new
structural reduction and capped at 60 seconds per solve.

Primary report: `method_v01_183_theory.md`.

## Trial E: upstream-manifest refresh

This is a selection audit, not a counterexample search. Refresh the current
open finite-`SimpleGraph` universal declarations at upstream commit `547f309e`,
compare them with the earlier `c9052e8` sweep, record every inclusion/exclusion,
and rank only existing eligible declarations by the frozen transformation
catalogue. No result from this audit is held out.

Primary report: `method_v01_upstream_manifest.md`.
