# Method v0.29: WOWII #141 cycle peak and radius-three closure

Date: 2026-08-13
Status: radius-three BFS forest certificate closed

## Result

[`lean/GraphConjecture141CyclePeak.lean`](../../lean/GraphConjecture141CyclePeak.lean)
closes the last field of `RadiusThreeForestCertificate` and packages the
complete radius-three branch of the WOWII #141 extraction.

For a connected graph of girth at least nine with a radius-three center `r`,
every simple cycle has a vertex `i` whose two cycle neighbors are distinct,
adjacent to `i`, and both lie exactly one BFS layer below `i`.

## Maximum-rank cycle vertex

Given a simple cycle `c`, convert its support to a finite set and select a
support vertex `i` maximizing `dist r`.  Rotate the cycle to start at `i`, and
name its second and penultimate vertices `x` and `y`.  Cycle simplicity gives
`x != y`, while the rotated walk supplies the edges `i--x` and `i--y`.

The maximum cannot be the root.  If `i = r`, then maximality places the
adjacent support vertex `x` at distance zero; connectedness turns that into
`x = r`, contradicting irreflexivity of the edge `r--x`.

Both neighbors have rank at most the rank of `i`.  The v0.27 BFS-layer
independence result rules out equal rank because each is adjacent to `i`.
An edge changes distance from `r` by at most one, so the only remaining
possibility is

```text
dist r x + 1 = dist r i
dist r y + 1 = dist r i.
```

This is exactly the `cyclePeak` hypothesis needed by the constructor from
v0.28.

## Closed branch

The module now exports:

- `radiusThreeForestCertificate`, containing layer independence, unique
  preceding-layer parents, and cycle peaks;
- `radiusThreeBfsPeakProperty_of_connected_of_nine_le_girth`;
- `everyVertexHasDistanceAtLeastFour_of_connected_of_ten_le_girth`.

Consequently, a connected graph of girth at least ten cannot have a
radius-three center: for every proposed root there is a vertex at distance at
least four.  This closes the radius-three obstruction used by the original
#141 proof chain.

## Verification

The complete recursive #141 chain, from `GraphConjecture141Extraction`
through `GraphConjecture141CyclePeak`, was compiled from source into a fresh
temporary directory.  Each invocation used:

```bash
LEAN_PATH=<fresh-audit-directory> timeout 60s lake env lean \
  -DwarningAsError=true \
  -o <fresh-audit-directory>/<MODULE>.olean \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  /Users/kuber.mehta/Projects/c5-k4/lean/<MODULE>.lean
```

Every process was individually capped at 60 seconds.  The new module contains
no `sorry`, `admit`, `native_decide`, `#print`, or custom axiom declaration.
