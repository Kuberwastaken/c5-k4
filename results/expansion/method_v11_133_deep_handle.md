# Method v0.11: WOWII 133 deep-handle classes

Date: 2026-08-13

Local certificate: `lean/GraphConjecture133DeepHandle.lean`

## Outcome

The degree-four target requires an induced path on `radius+4` vertices, hence
three genuinely new vertices beyond a radius geodesic's `radius+1` support.
This checkpoint formalizes two sufficient geometries and proves that each
closes the exact source-shaped conjecture.

## One-ended clean three-handle

`HasCleanRadiusThreeHandle G` records a radius geodesic `p` with a chain

```text
a -- b -- c -- head(p)
```

whose new vertices are fresh and whose forbidden contacts with the previously
constructed tail are explicitly absent.  The conditions are layered:

1. `c` attaches cleanly to the geodesic head;
2. `b` attaches to `c` and has no contact with the old geodesic;
3. `a` attaches to `b` and has no contact with `c` or the old geodesic.

The Lean proof applies the certified one-vertex prepend lemma three times.  It
constructs the induced list

```text
[a,b,c] ++ support(p)
```

and proves its length is exactly `radius+4`.  Thus
`radius_add_four_le_path_of_cleanThreeHandle` closes the degree-four wall.

## Compatible two-ended handle

`HasInducedRadiusTwoEndedHandle G` captures the alternative shape

```text
a -- b -- support(p) -- c,
```

with the complete list required to be induced.  This explicit compatibility
condition matters: separately clean endpoint extensions do not automatically
exclude a cross-end chord.  The theorem
`radius_add_four_le_path_of_twoEndedHandle` proves that this list also has
exactly `radius+4` vertices.

## Structural degree-four classes

Two full source theorems are now certified:

```text
connected + 4-regular + triangle-free
  + (has C4 or has a clean radius three-handle)
  ==> WOWII 133
```

and

```text
connected + 4-regular + triangle-free
  + (has C4 or has a compatible radius two-ended handle)
  ==> WOWII 133.
```

These are `degreeFourSpecialization_of_cleanThreeHandle` and
`degreeFourSpecialization_of_twoEndedHandle`.  The C4 disjunct uses the
source's exponent-zero branch; the handle disjunct proves the exact C4-free
path wall.

## Remaining existence problem

The assembly problem is closed: either handle geometry is sufficient in the
exact Lean representation.  What remains is a graph-theoretic existence
lemma deriving one of these handles from 4-regularity, triangle-freeness, and
C4-freeness alone.

The v0.10 sibling obstruction explains why breadth at the geodesic head does
not establish that existence.  The next useful analysis should inspect
second-neighborhood contacts of an off-direction neighbor.  Contacts at
geodesic indices two and three are the first unresolved configurations;
contacts farther down would contradict geodesic shortestness.

## Lean audit

The file contains no proof holes or custom axioms.  It was checked with local
dependencies and warnings promoted to errors:

```text
LEAN_PATH=/tmp/c5k4-133-deep-handle:/tmp/c5k4-133-degree-four:\
/tmp/c5k4-133-regular:/tmp/c5k4-133-specialization:/tmp/c5k4-133-v07-check \
  timeout 60s lake env lean \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture133DeepHandle.lean
```

Result: exit code 0 in 9.5 seconds.

This is a sufficient-class theorem, not a proof of the unrestricted
degree-four case and not a counterexample release candidate.
