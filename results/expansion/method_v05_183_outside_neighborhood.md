# Method v0.5 Lane P1: the outside-neighborhood obligation is false

Date: **2026-08-13**. Status: **the first obligation from
`method_v04_183_pendant_wall.md` is refuted by an infinite exact family; the
counterfamily still attains WOWII 183 at equality, and it identifies the
connected-domination slack that a repaired attachment lemma must spend**.

This note tests only the proposed implication

```text
G connected and claw-free,
L3(x)={z}, with no vertex farther from x, and gamma_c(G)>=5
  ==>  G-N(x) is bipartite.
```

The implication is false. No graph catalogue was generated or enlarged. The
only catalogue computations repeat the already frozen connected Graph Atlas
and McKay order-eight gates. Every subprocess was externally capped at 60
seconds. The counterfamily below is a direct structural perturbation of the
mandatory equality family `H_m`.

## Frozen-catalogue check

An exact subset checker was run on the live tier. It enumerates minimum
connected dominating sets, tests claw-freeness by neighborhood independence,
and tests `G-N(x)` directly for every qualifying orientation `(x,z)`.

| catalogue | qualifying graphs | qualifying `(x,z)` pairs | failures of `G-N(x)` bipartite |
|---|---:|---:|---:|
| Graph Atlas, orders at most 7 | 0 | 0 | 0 |
| McKay connected order 8 | 5 | 9 | 0 |

The McKay input is the previously frozen 11,117-graph file
`/tmp/graph8c.g6`, with SHA-256

```text
0002354f1ab3344a2706626a037ad15367bf23a2163aa68f552c3a169ca9a036
```

Thus the earlier bounded observation was correct but does not extend to a
theorem.

## Mandatory control: `H_m`

Recall that `H_m`, for `m>=4`, has a clique `Q={q0,...,q_(m-1)}`, one private
neighbor `ri` joined to each `qi`, and the additional edge `r1-z`. Take
`x=q0`. The proved values are

```text
n=2m+1,  d(x)=m,
gamma_c(H_m)=m+1,
b(H_m)=m+3,
tau_odd(H_m)=m-2.
```

Moreover, `H_m-N(x)` is a forest: apart from the isolated centre `x`, it
consists of the edge `r1-z` and isolated vertices. Hence the proposed
obligation holds on every mandatory control, and both the degree/leaf
inequality and the target are equalities:

```text
gamma_c(H_m)=n-d(x),
b(H_m)=gamma_c(H_m)+2.
```

## Counterfamily `J_m`

For every `m>=5`, derive `J_m` from `H_m` by adding exactly the three edges
that make `{r2,r3,r4}` a triangle. There are no other new edges, and again
take `x=q0`.

Equivalently, `J_m` is a line graph. In a root graph, take edges `qi=c-ui`
for all `i`; take `r2=u2-v`, `r3=u3-v`, and `r4=u4-v`; make every other `ri`
a private continuation edge at `ui`; and extend `r1` by the edge `z`. This
also gives a short structural proof of claw-freeness: the neighbors of any
vertex of a line graph split into the two cliques of edges incident with the
two endpoints of the corresponding root edge, so they contain no independent
triple.

The distance layers from `x=q0` are unchanged:

```text
L0={q0},
L1=(Q-{q0}) union {r0},
L2=R-{r0},
L3={z}.
```

In particular, `z` is the unique third-layer vertex and no vertex is farther
from `x`. The graph is connected and nonbipartite. But
`{r2,r3,r4}` is contained in `V(J_m)-N(x)`, so `J_m-N(x)` contains a triangle
and is not bipartite. This refutes the obligation for every `m>=5`.

## Exact connected domination number

> **Proposition.** `gamma_c(J_m)=m` for every `m>=5`.

For an upper bound, the set

```text
{q0,q1,q2,q5,...,q_(m-1),r1,r2}
```

has order `m`, is connected, and dominates `J_m`. The vertices `r3,r4` are
dominated through the new triangle, every `ri` with `i>=5` is dominated by
`qi`, and `z` is dominated by `r1`.

For the reverse inequality, let `D` be a connected dominating set. The
vertices `r0,r5,...,r_(m-1)` are leaves. Since `D` is nontrivial, domination
and connectivity force their supports `q0,q5,...,q_(m-1)` into `D`,
contributing `m-4` vertices. Dominating the leaf `z` and connecting its arm
to the rest force both `r1` and `q1` into `D`, contributing two more.

Finally, the triangle `{r2,r3,r4}` and its three supports require at least two
vertices. If no triangle vertex belongs to `D`, then all three supports are
needed merely to dominate the triangle. If a triangle vertex belongs to `D`,
at least one support `q2,q3,q4` is also needed to connect that triangle
portion to the clique portion of `D`. Therefore

```text
|D| >= (m-4)+2+2 = m.
```

This proves the proposition. In particular, `gamma_c(J_m)>=5` throughout the
family.

## Exact induced-bipartite number

> **Proposition.** `b(J_m)=m+2` for every `m>=5`.

An induced bipartite set contains at most two vertices of the clique `Q` and
at most two vertices of the triangle `{r2,r3,r4}`. All remaining vertices
number `(m-3)+1`, namely the other `R` vertices and `z`. Hence

```text
b(J_m) <= 2+2+(m-3)+1 = m+2.
```

Equality is attained by taking all vertices of `R-{r4}`, together with `z`,
`q0`, and `q4`. The induced graph is a forest consisting of the path/edge
pieces `r1-z`, `r2-r3`, `r0-q0-q4`, and isolated vertices. Thus

```text
b(J_m)=m+2=gamma_c(J_m)+2.
```

Consequently the counterfamily is not a counterexample to WOWII 183. It is
another infinite equality family.

## Small explicit member

The smallest member of this construction is `J_5`, of order 11. With labels
`0..4=q0..q4`, `5..9=r0..r4`, and `10=z`, it has

```text
graph6 = J~}A@?PAWC?
edges  = 01 02 03 04 05 12 13 14 16 23 24 27 34 38 49 6A 78 79 89
```

where `A` denotes vertex 10 in the compact edge list. Exact subset enumeration
independently gives

```text
n=11, m_edges=19,
gamma_c=5,
b=7,
tau_odd=4,
d(x)=5,
G-N(x) nonbipartite.
```

The frozen catalogues prove only that no qualifying countermodel has order at
most eight. Orders nine and ten were not searched, so `J_5` is the smallest
member of this exact family, not a claimed globally smallest counterexample.

## Why the preceding factorization breaks

The universal degree/leaf lemma gives `gamma_c(G)<=n-d(x)`. For `H_m` it is
exact. The earlier proposed proof then sought the stronger bound
`tau_odd<=d-2`. On `J_m`, however,

```text
n-d(x)-gamma_c(J_m)=1,
tau_odd(J_m)=m-1=d(x)-1.
```

The new triangle simultaneously raises the needed odd-cycle-transversal
budget by one and lowers connected domination by one. The final inequality
remains exact, but neither half of the old factorization remains exact. This
also refutes the full two-neighbor retention lemma from the preceding note:
deleting vertices only inside `N(x)` cannot destroy the surviving triangle in
`J_m-N(x)`.

## First logically sufficient repaired attachment lemma

Write the available connected-domination slack as

```text
s_x = n-d(x)-gamma_c(G) >= 0.
```

The first structurally meaningful replacement is the following two-budget
statement.

> **Slack-funded outside-transversal lemma (unproved).** Under the live
> hypotheses, there is a set `U subset V(G)-N(x)` with `|U|<=s_x` such that
> `G-N(x)-U` is bipartite; after independently choosing the component color
> classes, there is a set `P subset N(x)` for which
>
> ```text
> G[((V-N(x))-U) union P]
> ```
>
> is bipartite and `|P|>=|U|+2-s_x`.

Indeed, deleting `U` and `N(x)-P` then produces a bipartite induced subgraph,
and the number deleted is at most

```text
|U|+d-|P| <= d+s_x-2 = n-gamma_c(G)-2.
```

Therefore `b>=gamma_c+2` follows. This formulation is not the target written
verbatim: it specifies that the domination slack first pays for odd cycles
wholly outside the neighborhood and then gives an explicit attachment budget
for retaining near-centre vertices.

It contains both equality controls correctly:

* for `H_m`, `s_x=0`, take `U` empty and retain the same two-neighbor witness
  from the preceding note;
* for `J_m`, `s_x=1`, delete one of `r2,r3,r4` and retain, for example, `r0`
  together with a compatible clique neighbor.

The missing paper step is now precise: relate each unit of odd-cycle
transversal required wholly beyond `N(x)` either to one unit of slack
`n-d-gamma_c`, or to one additional compatible vertex that can be retained
inside `N(x)`. Claw-freeness alone does not make the outside graph bipartite.

## Reproduction and honest stop point

All checks used the repository's pinned environment and an external timeout:

```bash
timeout 60s /home/ec2-user/.venvs/wowii/bin/python <exact-subset-checker>
sha256sum /tmp/graph8c.g6
```

The exact checker reused the invariant routines in
`scripts/method_v03_183_lemma_check.py`; it did not write output or construct
a new catalogue. A second direct subset enumeration verified `J_m` for
`m=5,6,7,8`, while the propositions above establish all `m>=5` without
depending on computation.

The result is therefore:

1. `G-N(x)` is bipartite on all nine frozen high-tier orientations and every
   mandatory `H_m` control.
2. The obligation is nevertheless false on the infinite exact family `J_m`.
3. `J_m` is live, claw-free, and exact for `b=gamma_c+2`; it does not refute
   WOWII 183.
4. The failure exposes a budget transfer: an outside odd cycle can lower
   connected domination by the same amount that it raises transversal cost.
5. The slack-funded attachment lemma is sufficient and survives both exact
   families, but is not proved and has not been subjected to any catalogue
   wider than the frozen order-eight gate.

Accordingly this lane remains `THEOREM_SIGNAL`, with one auxiliary lemma
conclusively refuted and a narrower replacement isolated. No full proof or
public counterexample to WOWII 183 follows.
