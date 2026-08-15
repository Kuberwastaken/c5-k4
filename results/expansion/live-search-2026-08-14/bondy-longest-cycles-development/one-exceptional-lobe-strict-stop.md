# Bondy one-exceptional-lobe strict stop

- Classification: `STRICT_STOP_G3_ONE_EXCEPTIONAL_LOBE`
- Stage reached: target-free constructor reachability (`G2`)
- Stage failed: signed invariant separation (`G3`)
- Exact scope: universal join with `s-1` minimum-order filler cliques and one
  exceptional connected lobe
- Circumference, `q_4`, or proposed-target calls: `0`
- Search workflow, candidate, release, issue, or pull request: none

## Frozen design class

Let `s>=4`, `d>=1`, and let `L` be a connected graph of order `m` with
`delta(L)>=d`. Define

```text
H = (s-1) K_(d+1) disjoint_union L
G = K_s join H.
```

This is the natural one-factor-breaking-lobe continuation after the balanced
`C4/C4` theorem stop. The `s-1` cliques are minimum-order degree-balancing
lobes; `L` is intended to consume at least two peripheral paths and leave a
simple four-vertex path outside a longest cycle.

The proof below applies to the universal join exactly. An earlier exploratory
formulation allowed arbitrary non-universal separator attachments. Independent
audit rejected that broader scope: a maximum abstract path packing of `H`
need not be stitchable into a cycle when the separator is not universal. No
claim about arbitrary attachments is made here.

## Degree-wall bound

The graph has

```text
n = s + (s-1)(d+1) + m.
```

A filler vertex has degree exactly `s+d`, so Bondy's fixed-`k=4` premise
`n+12<=5 delta(G)` implies

```text
m <= 3s - 11 + (6-s)d.                 (1)
```

This is target-free constructor algebra; no longest-cycle evaluator is
required.

## Large lobe degree forces traceability

When `d>=3`, subtracting `2d+1` from the right side of (1) gives

```text
(s-4)(3-d) <= 0.
```

Thus `m<=2d+1`, or equivalently `delta(L)>=d>=(m-1)/2`. The Hamilton-path
form of Dirac's theorem makes `L` traceable. One path covers `L`, one path
covers each filler clique, and `H` therefore has a spanning cover by `s`
paths. The universal `K_s` stitches those paths into a Hamilton cycle of `G`.
The intended extra path-cover cost does not exist.

## Small lobe degree absorbs every four-vertex path

Let `P` be a collection of at most `s` pairwise vertex-disjoint nonempty
paths in `H` that maximizes the number of covered peripheral vertices. A
feasible packing covers each filler clique with one path and at least one
vertex of `L`, for a total of

```text
(s-1)(d+1) + 1
```

vertices.

For `d=1`, (1) gives `m<=2s-5`, while the displayed packing covers `2s-1`
vertices. For `d=2`, (1) gives `m<=s+1`, while the displayed packing covers
`3s-2` vertices. In either case, a maximum packing cannot use paths only in
`L`; it must include a filler-clique path. Such a path has at most
`d+1<=3` vertices.

If the uncovered vertices of `L` contained a simple four-vertex path,
replacing one filler path by that path would cover more vertices, a
contradiction. Hence no maximum `s`-path packing leaves the path required by a
Bondy violation.

For a universal join, the correspondence is exact:

```text
circ(K_s join H) = s + q_s(H),
```

where `q_s(H)` is the maximum order coverable by at most `s` peripheral
paths. Every longest cycle uses all `s` hub vertices and its peripheral
vertices form a maximum `s`-path packing. The packing contradiction therefore
rules out a four-vertex path in the induced subgraph on the vertices outside
every longest cycle, not merely in a proxy solution.

## Standing

The degree-balanced `s-1` filler cliques plus one exceptional connected lobe
grammar fails `G3`: for `d>=3` the exceptional lobe is traceable, and for
`d<=2` any residual four-vertex path is economically absorbed. This is a
rigorous strict stop for that exact universal-join coordinate, not a stop for
all conceivable non-universal transition systems.

Together with the broader
[`universal-separator stop`](next-coordinate-strict-stop.md) and the
[`C4`-factor Hamiltonicity theorem](c4-factor-hamiltonicity-theorem.md), it
shows why simply replacing one balanced factor component by a denser lobe is
not an admissible next search. A future arm needs a target-free stitching
model whose signed leakage survives non-universal routing constraints before
`G4` or any target call is allowed.
