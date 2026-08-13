# Frozen prospective addendum: neighborhood closure at the #40 wall

Frozen: 2026-08-13 UTC, before evaluating any transformed graph.

## Exact identity learned from the checkpoint

This trial uses exactly the ten equality rows named in the frozen #40
block-surgery checkpoint.  Write

```text
f = largest induced-forest order,
b = largest induced-bipartite order,
p = minimum path-cover number,
epsilon = (p + b + 1) mod 2,
tau_F = n - f,
tau_B = n - b,
L = n - p.
```

Every one of the ten rows satisfies the same parity-sensitive identity

```text
2*f = p + b + 1 + epsilon,
```

or equivalently

```text
R := L + tau_B - 2*tau_F = 2 - epsilon.
```

Thus the eight odd-parity rows have `R=2`, while the two even-parity rows
have `R=1`.  This is the common equality wall; it is stronger than merely
recording that `R` belongs to `{1,2}`.

## Frozen separating transformation

For each checkpoint seed `G` and each vertex `v`, form the neighborhood
closure `C_v(G)` by adding every missing edge between two vertices in the
open neighborhood `N_G(v)`.  Incident edges at `v` and all edges outside its
neighborhood are unchanged.  Retain only transformations that add an edge,
and canonically deduplicate isomorphic outputs.

This is a local many-edge closure, not an ear surgery, block substitution,
bipartite block tree, one/two-edge mutation, or line-graph construction.  It
was selected before evaluation because it turns one existing neighborhood
into an overlapping clique while preserving connectivity and order.

Adding edges cannot increase `f`, `b`, or `p`.  If

```text
a = tau_F(C_v(G)) - tau_F(G),
c = tau_B(C_v(G)) - tau_B(G),
d = p(C_v(G)) - p(G),
```

then the new residual is exactly `R' = R - d + c - 2*a`.  The prospective
separator is therefore a closure where the doubled feedback burden `2*a`
outpaces the bipartite and path-cover safeguards enough to make `R' <= 0`.

No other transformation may be added after seeing results.

## Frozen gate and budget

1. Before evaluating any closure, rerun exact sanity on every connected
   Graph Atlas graph of orders three through seven, paths/cycles/complete
   graphs of orders three through nine, Petersen, and `K(a,b)` for
   `2 <= a <= b <= 6`.
2. Decode the ten fixed graph6 seeds and verify their recorded `f,b,p` values
   and the exact parity identity above.
3. Generate at most one closure per seed vertex, retain connected outputs of
   orders 3--12, and deduplicate isomorphic outputs.
4. Evaluate at most 120 distinct outputs exactly.
5. Every process and exact solve is capped at 60 seconds.  A timeout is
   `INCONCLUSIVE`, never a crossing.

Every retained result must carry graph6 plus exact induced-forest,
induced-bipartite, and path-cover witnesses.  A strict crossing triggers an
independent implementation and a fresh source/status/novelty audit.

Verdicts are `DB_SANITY_REJECT`, `CANDIDATE`, `HOLD_BOUNDED`, or
`INCONCLUSIVE`.  No commit, push, release, issue, PR, or other public action is
authorized.
