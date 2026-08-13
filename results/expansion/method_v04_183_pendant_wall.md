# Method v0.4 Lane P1: the pendant-clique degree/transversal wall

Date: **2026-08-13**. Status: **a sufficient structural lemma is isolated and
is exact on the pendant-clique family and every fixed high-tier control; the
lemma is not proved, so WOWII 183 remains open in this lane**.

This note continues `method_v04_183_transversal.md`.  It uses the exact
pendant-clique family `H_m` as a compulsory equality test and asks for the
smallest near-centre odd-cycle-transversal statement that would finish the
remaining unique-third-layer claw-free core.

No graph was generated and no catalogue bound was widened.  The only finite
checks use the already frozen connected Graph Atlas graphs through order seven
and the McKay connected order-eight catalogue.  Every subprocess was
externally capped at 60 seconds.

## Live tier and notation

Let `G` be connected, nonbipartite and claw-free.  Fix a vertex `x` such that

```text
L3(x)={z},
and no vertex is farther than distance three from x.
```

Write

```text
d = deg_G(x),
tau_odd(G) = n-b(G).
```

The preceding distance-three arguments prove the desired inequality through
`gamma_c(G)<=4`.  Hence the only live tier in this note is

```text
gamma_c(G)>=5.
```

## A proved universal half of the factorization

> **Degree/leaf lemma.**  For every finite connected graph and every vertex
> `x`,
>
> ```text
> gamma_c(G) <= n-deg_G(x).
> ```

Proof.  The assertion is immediate in orders one and two.  Otherwise, the
star consisting of all edges incident with `x` is a forest, so it extends to a
spanning tree `T` of `G`.  The degree of `x` in `T` is `d`.  The components of
`T-x` each contain a leaf of `T`, giving at least `d` leaves.  In a tree of
order at least three, the nonleaves form a connected dominating set.  Therefore
`gamma_c(G)<=n-d`.  QED.

Equivalently,

```text
d <= n-gamma_c(G) = L_s(G).
```

Thus the full live-core inequality would follow from the single numerical
bound

```text
tau_odd(G) <= d-2.
```

Indeed, the two inequalities compose as

```text
tau_odd(G) <= d-2 <= n-gamma_c(G)-2,
```

which is exactly

```text
b(G) >= gamma_c(G)+2.
```

## Precise remaining structural lemma

The numerical bound has the following stronger, near-centre witness form.

> **Two-neighbor retention lemma (unproved).**  Under the live hypotheses and
> `gamma_c(G)>=5`, there are distinct vertices `p,q in N(x)` such that
>
> ```text
> G[(V(G)-N(x)) union {p,q}]
> ```
>
> is bipartite.

If the lemma holds, then

```text
T = N(x)-{p,q}
```

is an odd-cycle transversal contained entirely in the open neighborhood of
the distinguished centre, and

```text
|T|=d-2.
```

This is the exact multi-vertex replacement for the false one-vertex
closed-neighborhood transversal rung.  It does not say that all odd cycles
lie in `N[x]`; the order-eight graph ``GCQ`e_`` already disproves that idea.
It says only that a bounded deletion *inside* `N(x)` can hit every odd cycle.

## Mandatory equality test: the family `H_m`

Recall that `H_m`, for `m>=4`, consists of a clique

```text
Q={q0,...,q_(m-1)},
```

one pendant neighbor `ri` at every `qi`, and one extra vertex `z` joined to
`r1`.  Take `x=q0`.  The earlier exact calculations give

```text
n=2m+1,
d(x)=m,
gamma_c(H_m)=m+1,
b(H_m)=m+3,
tau_odd(H_m)=m-2.
```

Consequently both halves of the proposed factorization are equalities:

```text
gamma_c(H_m)=n-d(x),
tau_odd(H_m)=d(x)-2,
gamma_c(H_m)+tau_odd(H_m)=n-2.
```

The witness form is also exact.  Choose any `j!=0`, retain

```text
p=r0,   q=qj,
```

and delete

```text
T=Q-{q0,qj} subset N(x).
```

Then `|T|=m-2`, and `H_m-T` is a forest: it contains the edge `q0-qj`, the
available pendant edges, possibly the tail `q1-r1-z`, and isolated vertices.
Hence it is bipartite.

The existential quantifier is necessary.  If two vertices of
`Q-{q0}` are retained instead, those two vertices together with `q0` induce a
triangle.  Thus `H_m` itself refutes the tempting stronger rung that *any* two
neighbors of `x` may be retained.

## Fixed-catalogue audit

An exact checker enumerated connected dominating sets and induced bipartite
sets by subsets, filtered the frozen live claw-free core, and then tested every
qualifying ordered pair `(x,z)` in the remaining `gamma_c>=5` tier.  For each
pair it checked both the numerical bound and every two-subset of `N(x)` for an
explicit retention witness.

| catalogue | qualifying graphs | qualifying `(x,z)` pairs | numerical failures | retention-witness failures |
|---|---:|---:|---:|---:|
| Graph Atlas, orders at most 7 | 0 | 0 | 0 | 0 |
| McKay connected order 8 | 5 | 9 | 0 | 0 |

All nine order-eight orientations have the same exact coordinate profile:

```text
n=8, gamma_c=5, b=7, tau_odd=1, d(x)=3.
```

Thus both `gamma_c=n-d` and `tau_odd=d-2` are equalities on every fixed
high-tier orientation, just as they are throughout `H_m`.  The five graphs
are

```text
G?`aeG  G?b@dG  G?qacg  G?qadO  GCQ`e_.
```

The frozen order-eight file contains 11,117 connected graphs and has SHA-256

```text
0002354f1ab3344a2706626a037ad15367bf23a2163aa68f552c3a169ca9a036.
```

This is a bounded falsification gate, not a proof of the retention lemma.
The Atlas row is vacuous because no live graph through order seven has
`gamma_c>=5`.

## Why the high-tier premise cannot be dropped

The numerical lemma is already false inside the fixed live claw-free core at
lower connected-domination tiers.  The Atlas graph

```text
graph6 = EhNG
edges  = 01 05 12 15 23 24 34 45
```

has qualifying orientations `(x,z)=(0,3)` and `(3,0)`.  For either one,

```text
gamma_c=2, b=4, tau_odd=2, d(x)=2.
```

Hence `tau_odd<=d(x)-2` would read `2<=0`.  In fact
`G-N(x)` is already nonbipartite.  The restriction `gamma_c>=5` is therefore
not cosmetic: it is exactly the tier left after the proved absolute bounds,
and the degree/transversal statement is false before that tier.

## First unresolved proof step

The retention lemma separates into two concrete obligations:

1. prove that `G-N(x)` is bipartite in the live `gamma_c>=5` tier; and
2. after independently flipping the color classes of its components, find
   two vertices of `N(x)` whose complete attachment pattern respects a common
   bipartition.

Both obligations hold for all nine fixed orientations and for every `H_m`.
Claw-freeness gives `alpha(G[N(x)])<=2` and constrains each attachment from one
distance layer to the next, but those local facts alone have not yet been
turned into either obligation.  No argument was found showing that failure of
one obligation necessarily produces a connected dominating set of order at
most four.  That implication is the exact missing paper step.

It would be circular to replace the retention lemma by the bare inequality

```text
gamma_c(G)+tau_odd(G)<=n-2,
```

because that is simply the desired core statement in transversal notation.
The retention lemma is strictly more structural: it prescribes where a
size-`d-2` transversal must live and exposes a concrete attachment problem.

## Honest stop point

This lane has produced a clean equality-wall factorization but not a proof:

1. `gamma_c<=n-d(x)` is proved universally;
2. a near-centre transversal of order at most `d(x)-2` would finish the live
   core;
3. the two-neighbor retention lemma supplies exactly such a transversal;
4. every fixed high-tier orientation and every `H_m` attains both component
   inequalities at equality;
5. `H_m` refutes the stronger universal-pair quantifier, while `EhNG` refutes
   removal of the high-tier premise;
6. the existential retention lemma itself remains unproved and has no
   countermodel in the permitted test set.

Accordingly the outcome remains `THEOREM_SIGNAL`.  No proof of WOWII 183, no
counterexample, and no public release follows from this note.
