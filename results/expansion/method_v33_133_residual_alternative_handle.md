# Method v0.33: WOWII 133 residual alternative handle

## Outcome

The 44-vertex residual completion from v0.32 satisfies the full numerical
path wall relevant to WOWII 133.  It is therefore not a counterexample to the
conjecture; it only defeats the previously frozen local strategy.

The escape is structural and unexpectedly small.  Shift the selected
geodesic endpoint from `0` to `1`:

```text
1-2-3-4-5.
```

This is a geodesic of length four from a vertex of eccentricity four.  The old endpoint `0`, the old
first choice `6`, and its old parent `9` now form a clean handle in reverse:

```text
9-6-0-1-2-3-4-5.
```

That list is an induced path on eight vertices.  Since the completed graph
has radius at most four, it certifies

```text
radius(G) + 4 = 8 <= path(G).
```

Lean certificate:

- `lean/GraphConjecture133ResidualCompletionInterface.lean`;
- `lean/GraphConjecture133ResidualAlternativeHandle.lean`.

The lightweight interface repeats the exact v0.32 adjacency table and its
constructive connectivity proof, but omits the already-certified expensive
all-pairs regularity and girth checks.  This keeps every downstream rebuild
within the process cap without changing the graph under evaluation.

## Exact certificate

The Lean file imports the v0.32 explicit graph and proves by ordinary kernel
reduction that:

1. vertex `1` has computable eccentricity exactly four, hence the graph has
   radius at most four;
2. `dist(1,5)=4`, so `1-2-3-4-5` is a geodesic of length four;
3. `[9,6,0,1,2,3,4,5]` is an induced path;
4. consequently its longest induced-path order is at least eight; and
5. the radius-plus-four wall holds on the graph.

The theorem `shifted_endpoint_handle_certificate` packages the decisive
geometric facts.  The theorem
`completion_satisfies_radius_add_four_wall` packages the resulting invariant
inequality.

## Why the frozen strategy missed it

The v0.30--v0.32 analysis fixed the longer geodesic

```text
0-1-2-3-4-5
```

and tried to extend it outward from `0`.  Relative to that orientation,
`0-6-9` was an outward branch whose third choices could all be blocked by
contacts back into the geodesic.

But the same branch already contains the required handle after changing the
geodesic endpoint.  Delete `0` from the geodesic, take `1` as the new head,
and traverse the old branch backwards as `9-6-0`.  The relevant nonedges are
present, so the concatenation is induced.

The completion work was still informative: it showed that the sharp
cross-branch overlap can survive all local degree and girth constraints, and
the alternative-handle check then identified the global degree of freedom
that the local model omitted.

## Extracted proof direction

Any continuation of the general proof should be invariant under endpoint
shifts.  In particular, after freezing a geodesic

```text
x0-x1-...-xr,
```

an outward chain `x0-c-p` should be tested in both roles:

- as the beginning of a longer handle extending the original geodesic; and
- as the reversed handle `p-c-x0` prepended to the shifted geodesic
  `x1-...-xr`.

The second role needs only that `p` and `c` have no forbidden contacts with
the shifted tail.  It can succeed even when all third vertices below `p` are
blocked.  Thus a local countermodel must constrain not merely third-layer
extensions of one frozen endpoint, but every endpoint shift and branch
reorientation available around the geodesic.

This suggests the next generic lemma:

> If `x0-c-p` is an induced two-edge branch at the head of a geodesic and
> `c,p` are clean against `x1,...,xr`, then
> `p-c-x0-x1-...-xr` is an induced path.

For a geodesic from a vertex of eccentricity `r`, that produces an induced path of
order `r+3`.  One further clean predecessor of `p`, or a compatible extension
at the opposite endpoint, reaches the desired `r+4` wall.  The explicit
completion realizes the first option with the three vertices `9,6,0` because
the shifted geodesic has length four.

## Scope

This is theorem extraction and countermodel calibration, not a new
conjecture disproof and not a proof of WOWII 133.  The calculation concerns
one explicit 44-vertex completion.  Its value is that it falsifies the
frozen-endpoint proof model while simultaneously displaying a concrete
rerouting mechanism that repairs the target inequality.

## Verification discipline

All search and verification processes were individually capped at 60
seconds.  The Lean certificate uses ordinary `decide` and kernel proofs.  It
contains no holes, custom axioms, `native_decide`, or equivalent shortcuts.
