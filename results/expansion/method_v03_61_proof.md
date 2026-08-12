# Method v0.3 Lane P3: residue/diameter proof extraction

Date: **2026-08-12 UTC**

Frozen input: `results/expansion/method_v02_61_search.jsonl`

Input SHA-256: `0a71a74b64b682e733026c9ed24e21808f7336b0d13aee21c3eb7ac7cf942e98`

This is a proof-ladder report, not a proof or disproof of WOWII 61. It uses
only the 823 saved switch extrema from Method v0.2. It does not traverse a new
switch, deepen a component, or introduce a degree sequence.

## 1. Source target

For a connected nontrivial graph `G`, WOWII 61 asks for

```text
f(G) >= residue(G) + ceil(diameter(G)/3),
```

where `f(G)` is the maximum order of an induced forest and `residue(G)` is the
number of zeros left by the iterated nonincreasing Havel--Hakimi reduction.
Write `r=residue(G)` and `D=diameter(G)`.

## 2. What residue means structurally

Let `d` be a graphical degree sequence. Run **Maxine** on a realization `H` of
`d`: while an edge remains, delete a vertex of maximum current degree, with
arbitrary tie choices. Let `m(H,sigma)` be the order of the terminal independent
set for tie sequence `sigma`.

The exact structural interpretation recovered here is

```text
r(d) = min { m(H,sigma) : H realizes d and sigma is a Maxine tie sequence }.
```

There are two parts.

1. Griggs--Kleitman's maximum-degree deletion argument gives
   `m(H,sigma) >= r(d)` for every realization and every tie sequence. At one
   deletion step, if `rho` is the degree sequence after deleting a
   maximum-degree vertex and `HH(d)` is the Havel--Hakimi reduction, then
   `rho` dominates `HH(d)` and residue is monotone in the needed direction;
   induction reaches the terminal independent graph.
2. Equality is attained by a recursively constructed Havel--Hakimi
   realization. Realize `HH(d)`, add the laid-off maximum-degree vertex back
   adjacent to the entries that were decremented, and repeat. Deleting the
   added vertices in forward Havel--Hakimi order is a legal Maxine run and
   leaves exactly `r(d)` vertices.

Thus residue is an exact extremum over the **realization class**, not the size
of a distinguished core in the given realization `G`.

This distinction is essential. On the frozen 823 graphs, every Maxine tie
sequence was evaluated exactly. The outcome relative to residue was:

| `(minimum-r, maximum-r)` | graphs |
|---:|---:|
| `(0,0)` | 423 |
| `(0,1)` | 144 |
| `(0,2)` | 2 |
| `(1,1)` | 246 |
| `(1,2)` | 1 |
| `(2,2)` | 7 |

In 254 of 823 fixed realizations, **no** Maxine run leaves exactly `r`
vertices. The smallest countermodel is graph6 `DLS`, with edges

```text
03, 12, 14, 23, 34
```

and degree sequence `(3,2,2,2,1)`. Its Havel--Hakimi trace is

```text
(3,2,2,2,1) -> (1,1,1,1) -> (1,1,0) -> (0,0),
```

so `r=2`, but every Maxine run leaves an independent set of order `3`.
Consequently the phrase "the residual independent/core set of `G`" has no
literal meaning of the required order in general. One may obtain an
independent set of at least `r` by Maxine and discard surplus vertices, but
that is the classical inequality `r<=alpha` and adds no residue-specific
geometry inside the fixed realization.

References for the residue/Maxine inequality are Griggs and Kleitman,
*Independence and the Havel--Hakimi residue*, Discrete Mathematics 127 (1994),
209--212, DOI `10.1016/0012-365X(92)00479-B`, and Favaron, Mahéo, and Saclé,
*On the residue of a graph*, Journal of Graph Theory 15 (1991), 39--64.

## 3. A rigorous geodesic packing lemma

The residue certificate still yields a valid weaker theorem.

**Lemma (safe three-separated augmentation).** Let `I` be an independent set
in `G`, let `P=(v_0,...,v_D)` be a geodesic, and let
`X subseteq V(P)\I`. If distinct vertices of `X` have path-index distance at
least three, then `G[I union X]` is a forest.

**Proof.** A subpath of a geodesic is shortest, so
`dist_G(v_i,v_j)=|i-j|`. Hence distinct vertices of `X` are nonadjacent and
have no common neighbor. The set `I` is independent, and every vertex of `I`
has at most one neighbor in `X`. A cycle in `G[I union X]` would have to
alternate between the two independent sides and give each participating
vertex of `I` two neighbors in `X`, a contradiction. `square`

**Counting lemma.** If `I` is independent, then `P\I` contains a set `X` as
above with

```text
|X| >= ceil(D/4).
```

**Proof.** Mark the indices whose path vertices are outside `I`. No two
unmarked indices are consecutive. Greedily choose the leftmost marked index
and thereafter the leftmost marked index at least three positions after the
last choice. The first choice has index at most one. Each later choice occurs
at most four positions after its predecessor, because among the next two
eligible positions at least one is marked. When the process stops, the final
index is at distance at most three from `D`. If there are `t` choices, then
`D<=4t`, hence `t>=ceil(D/4)`. `square`

Choose an independent set of order exactly `r` from any Maxine terminal set
and apply both lemmas to a diametral geodesic. This proves the unconditional
partial theorem

```text
f(G) >= residue(G) + ceil(diameter(G)/4).
```

The checker verifies the quarter-diameter packing conclusion for every
residue-sized independent set and every diametral geodesic in all 823 saved
extrema. The proof above is general; the ledger check is a guard against a
misstated quantifier or rounding convention.

## 4. Why the same route does not reach one per three layers

Replacing `ceil(D/4)` by `ceil(D/3)` in the counting lemma is false. For
example, on a path the membership pattern of `I` can alternate, and the
available path vertices can force four path indices per safely separated
choice. The fixed ledger confirms the exact quantifier gap:

| third-diameter safe packing claim | graphs satisfying it |
|---|---:|
| every residue-set, every diametral geodesic | 731 / 823 |
| every residue-set, some diametral geodesic | 751 / 823 |
| some residue-set, every diametral geodesic | 817 / 823 |
| some residue-set, some diametral geodesic | 823 / 823 |

The last row is only a bounded observation. Promoting it would require a rule
that selects the favorable residue-sized set and geodesic in an arbitrary
graph; the structural interpretation in Section 2 supplies neither.

One can try a more permissive local exchange: allow deletion of vertices from
`I`, but require the replacement forest to remain inside `I union V(P)`.
Formally:

> For every independent `I` of order `r` and every diametral geodesic `P`,
> `G[I union V(P)]` has an induced forest of order at least
> `r+ceil(D/3)`.

This stronger exchange mechanism succeeds on 821 of the 823 saved extrema,
but it is false. The two exact countermodels are graph6 `FHAXG` and `FXAXG`.

For `FHAXG`, the edges are

```text
05, 12, 23, 26, 35, 45, 56.
```

Its degree sequence is `(4,3,2,2,1,1,1)`, its Havel--Hakimi residue is `4`,
and its diameter is `4`. Take

```text
I = {0,1,3,6},
P = (0,5,3,2,1).
```

Then `I` is independent and `P` is diametral, but the largest induced forest
inside `I union V(P)={0,1,2,3,5,6}` has order `5`, below
`r+ceil(D/3)=6`. The induced union contains the four-cycle
`2-3-5-6-2`, so its full order-six vertex set is not a forest. The original
graph nevertheless has `f=6`: every order-six forest witness uses vertex `4`,
which lies outside this union. Thus WOWII 61 holds on the graph; what fails is
exactly the proposed geodesic-local exchange.

For `FXAXG`, the same obstruction persists after adding edge `02`; direct
enumeration again gives local optimum `5` against target `6`, while the full
graph has `f=6`. One explicit failing pair is

```text
I = {0,1,3,4},
P = (1,2,0,5,4).
```

The remaining weaker quantifiers all hold in this ledger:

| local exchange claim | graphs satisfying it |
|---|---:|
| every residue-set, some diametral geodesic | 823 / 823 |
| some residue-set, every diametral geodesic | 823 / 823 |
| some residue-set, some diametral geodesic | 823 / 823 |

These are theorem signals only. The 823 graphs do not prove them, and no
selection theorem follows from Havel--Hakimi residue.

## 5. Ladder verdict

Lane P3 stops at the frozen structural gate.

1. The exact meaning of residue is an extremum over all realizations and
   Maxine tie sequences. It is not an exact core size in the fixed graph.
2. A rigorous geodesic packing/exchange argument proves the denominator-four
   partial theorem.
3. The natural denominator-three packing count is false.
4. Even arbitrary induced-forest exchange inside a fixed residue-set/geodesic
   union is false, with saved countermodels `FHAXG` and `FXAXG`.
5. Favorable choices of the residue-sized set or geodesic survive all 823
   tests, but residue supplies no rigorous choice mechanism. Treating that
   observation as a lemma would silently replace the missing structure by an
   existential independent-set assertion.

Therefore the frozen lemma ladder does **not** prove WOWII 61. The exact false
step is the assumption that the degree-sequence residue identifies a
compatible independent/core set in the given realization which can be
augmented locally along an arbitrary diameter geodesic at one vertex per
three layers. No alpha substitution is made, and no wider search is warranted
under Method v0.3.

## 6. Reproduction

```bash
python3 scripts/method_v03_61_proof_check.py
```

Expected terminal lines include:

```text
PASS: 823 saved switch extrema only; no graph generation
PASS: Maxine >= residue throughout; strict in 254 extrema (first DLS)
REFUTED: third-diameter exchange inside I union P for every I,P
COUNTERMODELS: FHAXG, FXAXG (821/823 graphs satisfy the universal local form)
```
