# An exact counterexample to Written on the Wall I conjecture 191

This directory gives a self-contained, executable certificate that
Fajtlowicz's *Written on the Wall I* conjecture 191 is false. The first
counterexample is the triangular graph

```text
T(7) = L(K_7).
```

The verification is exact and uses only the Python standard library.

## Statement and conventions

The primary July 2004 scan, page 70, prints the conjecture in the section for
graphs satisfying `sum Odd <= sum Even`:

```text
minimum deficiency <= size / clique.
```

Here `size` is the number of edges and `clique` is the clique number. The
same source explicitly defines the deficiency of a vertex later, at
conjecture 838, as the number of nonedges among its neighbors. Thus

```text
def(v) = C(deg(v), 2) - |E(G[N(v)])|.
```

`Odd(v)` and `Even(v)` count vertices at odd and even graph distance from
`v`, respectively; `v` itself is included in `Even(v)` at distance zero.

There is one source-critical transcription detail: the OCR-derived corpus
row records `<`, while visual inspection of the primary scan confirms `<=`.
This certificate uses the primary scan. The source and audit trail are
recorded in:

- [`../../corpora/ACQUISITION.md`](../../corpora/ACQUISITION.md), including
  the canonical-file provenance and surviving PDF mirror;
- [`../../corpora/graffiti_wow.json`](../../corpora/graffiti_wow.json), rows
  `wow-191` and `wow-838`;
- [`../../results/expansion/wow1_part1.md`](../../results/expansion/wow1_part1.md),
  including the page-70 visual audit and the complete database-sanity gate.

## The witness, with exact arithmetic

Represent a vertex of `T(7)` by an edge `{a,b}` of `K_7`; two such vertices
are adjacent exactly when the represented edges intersect. Direct exhaustive
evaluation gives:

| quantity | exact value |
|---|---:|
| order | 21 |
| degree | 10 |
| size | 105 |
| clique number | 6 |
| minimum deficiency | 20 |
| each Odd coordinate | 10 |
| each Even coordinate | 11 |
| sum Odd | 210 |
| sum Even | 231 |

The inherited hypothesis holds because `210 < 231`. The claimed bound fails:

```text
20 > 105 / 6 = 35 / 2.
```

The verifier constructs the graph from scratch, checks connectivity and all
distance parities, counts every neighborhood nonedge, and computes the clique
number with an exact Bron--Kerbosch search. Its reported six-clique is the
star `{01,02,03,04,05,06}`.

## Infinite counterexample family

The same argument works for every `T(q) = L(K_q)` with integer `q >= 7`.
For a vertex `{a,b}`, its neighbors split into two `(q-2)`-cliques,
`A = {{a,x}}` and `B = {{b,x}}`. Across the two cliques, only the matched
pairs `{a,x}`--`{b,x}` are adjacent. Consequently the missing cross-pairs,
and hence every vertex deficiency, number

```text
(q-2)^2 - (q-2) = (q-2)(q-3).
```

Also

```text
|E(T(q))| = q(q-1)(q-2)/2,
omega(T(q)) = q-1,
|E(T(q))| / omega(T(q)) = q(q-2)/2.
```

For completeness, a pairwise-intersecting family of two-subsets either has
a common element, giving at most the `q-1` edges of a star, or is contained
in a triangle, giving at most three edges. Hence the star is maximum here.

The claimed inequality is therefore equivalent, after cancelling the
positive factor `q-2`, to `q-3 <= q/2`; it fails exactly when `q > 6`.
Since `T(q)` has diameter two, each Odd coordinate is `2(q-2)` and each Even
coordinate is `C(q,2)-2(q-2)`. The inherited hypothesis also holds exactly
from `q >= 7`. Thus every member in the claimed range is admissible and is a
counterexample.

## Reproduce

From this directory, run:

```sh
python3 verify.py --family-through 12
python3 -m unittest -v test_verify.py
```

The first command emits a deterministic JSON certificate. A compact checked
copy is committed as [`certificate.json`](certificate.json). The tests
construct `T(q)` independently for `3 <= q <= 10` and compare every measured
quantity with the closed forms, in addition to checking the exact `T(7)`
failure and threshold. No floating-point arithmetic, external package, ILP,
or network access is used.
