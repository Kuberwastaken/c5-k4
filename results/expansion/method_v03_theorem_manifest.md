# Method v0.3 proof-extraction wave: frozen manifest

Frozen: **2026-08-12 UTC**
Method commit: `b001771`
Upstream baseline: `google-deepmind/formal-conjectures` `547f309e`
Scope: existing Written on the Wall II statements only

This manifest is committed before the proof agents attempt any lemma below.
The lanes may end in a proof, a counterexample to an intermediate lemma, or a
sharper obstruction. They may not widen their graph-search bounds or introduce
another corpus.

## Lane P1: WOWII 183 radius-three core

Already-proved baseline:

```text
L_s(G) + b(G) >= n + 1,
```

equivalently `b(G) >= gamma_c(G)+1`.

Residual reduction: with `H=G^2`, `r=rad(H)`, and
`q=n-1-Delta(H)`, a geodesic gives `q>=2r-3`. The baseline proves every case
except `q=2r-3`; equality forces singleton distance layers from three onward.
Safe pendant-tail pruning reduces the source conjecture to:

> If a connected nonbipartite graph has a vertex with exactly one vertex at
> distance three and no farther vertex, then `b(G)>=gamma_c(G)+2`.

The published local-independence strengthening proves this when `mu(G)>=4`.
The live core is therefore `mu(G)<=3`.

Frozen proof routes, in order:

1. characterize a minimum connected dominating set relative to the unique
   distance-three vertex and its support;
2. construct a bipartite induced set with two more vertices than that set's
   complement;
3. split `mu<=2` (claw-free neighborhoods) from `mu=3` if necessary;
4. test every proposed intermediate lemma on the already-fixed Atlas/order-8
   critical catalogue before using it.

No new graph generation is authorized. A proof of the core proposition proves
WOWII 183 after the existing reduction; a counterexample to the core must be
checked against the original square residual before any disproof claim.

## Lane P2: WOWII 133 cubic C4-free specialization

The C4-present branch follows from a diameter geodesic. For a connected cubic
C4-free graph, every open neighborhood is independent, so the live source
inequality becomes:

```text
largest induced path order >= radius + 3.
```

Frozen proof routes:

1. start from a center-to-periphery geodesic of `radius+1` vertices;
2. use the three neighbors of the center and C4-freeness to extend or reroute
   the geodesic by two vertices while retaining inducedness;
3. isolate parity/end-neighborhood cases rather than assuming a longest
   geodesic is extendable;
4. test each extension lemma against the six exact lift representatives and
   one minimum-residual representative from every complete cubic order through
   20.

No order-22/24 generation or Hoffman--Singleton optimization is authorized;
those are already recorded timeout strata. Proving this specialization is a
valid partial theorem but does not by itself prove full WOWII 133.

## Lane P3: WOWII 61 residue/diameter compensation

The source statement is

```text
f(G) >= residue(G) + ceil(diameter(G)/3).
```

The completed degree-preserving switch trial suggests that each three new
distance layers forces one additional induced-forest vertex once the degree
sequence, hence Havel--Hakimi residue, is fixed.

Frozen lemma ladder:

1. recover an exact structural interpretation of the Havel--Hakimi residue
   usable in a proof (not merely the deletion algorithm's output);
2. combine a diameter geodesic with the residual independent/core set without
   assuming their union is induced-acyclic;
3. seek an exchange lemma that adds one forest vertex per three uncovered
   geodesic layers;
4. test every exchange lemma against the 823 independently recomputed switch
   extrema before promoting it.

No deeper switch search or new degree sequences are authorized. If the
Havel--Hakimi residue lacks the proposed structural interpretation, record
that exact break and stop rather than replacing it with independence number.

## Deferred signal: WOWII 382e

The 382e lane remains deferred during this wave. Its live inequality

```text
gamma_2(G)-gamma(G) <= Maxine_best(G)
```

is essentially the full conjecture, not yet a narrower structural proposition.
The bounded trial therefore does not meet Method v0.3's lemma-ladder entry
criterion. It may resume only after a graph-theoretic interpretation of Maxine
produces a strictly smaller proof obligation.

## Formalization gate

For any complete paper proof:

1. independently audit source/status and the full implication to the source;
2. write a no-`sorry` Lean proof in `c5-k4` when the available graph API makes
   that honest;
3. compile warning-as-error and audit axioms;
4. commit every durable stage sequentially;
5. open one WoW II issue and one focused PR only after the complete proof and
   immutable link exist.

A partial specialization may be formalized locally, but it must not change the
upstream source conjecture's status.
