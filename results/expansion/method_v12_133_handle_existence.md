# Method v0.12: WOWII 133 deep-handle existence

Date: 2026-08-13

Local certificate: `lean/GraphConjecture133HandleExistence.lean`

## Bounded truth check

Before strengthening the Lean development, the proposed clean-three-handle
existence statement was tested directly.  For each eligible graph, the check
enumerated radius vertices, antipodes at the radius, all shortest paths
between them, and all three-vertex chains attached at the first endpoint.  It
replayed freshness, adjacency, and every forbidden chord in the exact v0.11
definition.

Two independent named 4-regular, triangle-free, C4-free controls were
available:

| graph | order | radius | result |
|---|---:|---:|---|
| `Kneser(7,3)` | 35 | 3 | clean three-handle found |
| incidence graph of `PG(2,3)` | 26 | 3 | clean three-handle found |

The projective-plane incidence graph was constructed independently from the
13 normalized points and 13 normalized lines over `F_3`; incidence is zero
dot product.  Its exact graph6 record is:

```text
Y?????????????QQPo?ogIGbo?ACcAHGA?M?Ci?@Go?OM??Gp??DO_??
```

The first enumerated radius geodesic already yielded a handle.  As a negative
calibration, the 12-vertex Chvatal graph is connected, triangle-free, and
4-regular but was correctly rejected at the C4-free gate.  A fixed-seed scan
of 4-regular random graphs through order 30 produced no additional eligible
girth-at-least-five controls in its bounded sample.

No countermodel was found.  These checks are evidence only; they are not used
by Lean and do not establish unrestricted existence.

## Late contacts are impossible

The main formal gain is that the infinite-looking clean-tail conditions reduce
to a finite early-contact problem.

Let `p=(u,x1,...,xr)` be a geodesic.

- If `u-c-b` is a two-edge handle and `b` is adjacent to `x_k` for `k>=4`,
  then `u-c-b-x_k` followed by the suffix of `p` is shorter than `p`.
- If `u-c-b-a` is a three-edge handle and `a` is adjacent to `x_k` for
  `k>=5`, the analogous shortcut is again shorter.

Lean certifies these statements as
`not_adj_getVert_ge_four_of_twoStep` and
`not_adj_getVert_ge_five_of_threeStep`.

Therefore the only geodesic contacts that require genuine local control are:

```text
b: indices 1, 2, 3
a: indices 0, 1, 2, 3, 4.
```

The index-zero contact for `b` and the `a-c` contact are automatically
excluded by triangle-freeness once freshness is known.

## Corrected structural class

`HasEarlyEscapeRadiusThreeHandle G` records:

1. a radius geodesic;
2. one clean first off-direction vertex `c`;
3. a fresh neighbor `b` of `c`, checked only at indices `1..3`;
4. a fresh neighbor `a` of `b`, checked only at indices `0..4`.

It contains no universal long-tail conditions for `a` or `b`.
`cleanThreeHandle_of_earlyEscape` derives all of those conditions using the
two shortcut lemmas and triangle-freeness.  Finally,
`degreeFourSpecialization_of_earlyEscape` proves:

```text
connected + 4-regular + triangle-free + early-escape certificate
  ==> exact source-shaped WOWII 133.
```

This is the strongest honest structural class reached here.  The remaining
unrestricted existence question is now finite and sharply localized: among
the three forward neighbors at depths two and three, show that some chain
avoids the eight listed early contacts, or classify the configuration when
all chains are blocked.

## Lean audit

The module contains no proof holes or custom axioms.  It was checked with
local dependencies and warnings promoted to errors:

```text
LEAN_PATH=/tmp/c5k4-133-handle-existence:/tmp/c5k4-133-deep-handle:\
/tmp/c5k4-133-degree-four:/tmp/c5k4-133-regular:\
/tmp/c5k4-133-specialization:/tmp/c5k4-133-v07-check \
  timeout 60s lake env lean \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture133HandleExistence.lean
```

Result: exit code 0 in 6.6 seconds.

This is a structural reduction and sufficient-class theorem, not a proof of
unrestricted handle existence and not a counterexample release candidate.
