# Method v0.17: WOWII 133 pivot contacts

Date: 2026-08-13

Local certificate: `lean/GraphConjecture133PivotContacts.lean`

## The independent constraint v0.16 missed

The v0.16 four-edge metric route compared contacts made by **different**
siblings through their shared parent.  A row containing two contacts has a
much shorter route:

```text
x_i -- a -- x_j.
```

Replacing the corresponding geodesic segment gives a two-edge detour.
Therefore one row can only contain contacts whose indices differ by at most
two.

`sameContact_index_gap_le_two` proves this formally by constructing the full
prefix--detour--suffix walk.  `not_sameContacts_of_gap_three` packages the
strict exclusion for gaps at least three.

## All multi-contact rows disappear

Within a single row:

- gap one is impossible by triangle-freeness;
- gap two is impossible by C4-freeness;
- gap at least three is impossible by the new two-edge metric shortcut.

The theorem `early_contacts_unique` combines those three cases and proves
that a fresh vertex has at most one contact among geodesic indices `0..4`.

Consequently the three multi-contact rows retained in v0.14 were artifacts of
applying only local short-cycle filtering:

```text
{1,4}, {0,4}, {0,3}
```

All three are now eliminated.

## Exact re-enumeration

The allowable nonempty rows reduce to the five singletons

```text
{0}, {1}, {2}, {3}, {4}.
```

Cross-row C4-freeness requires the three rows to be distinct.  Thus the 20
v0.15 matrices collapse to the ten three-element subsets of five targets:

```text
012, 013, 014, 023, 024,
034, 123, 124, 134, 234.
```

All ten remain compatible with the different-row four-edge metric bound from
v0.16.  Three contain the gap-four pivot pair `{0,4}`: `014`, `024`, and
`034`.  Rerouting that pair produces an equal-length alternative geodesic,
not a strict contradiction.  The other seven have maximum separation at most
three.

## Strongest honest conclusion

Any obstruction to a clean depth-three vertex is now exactly an injective
assignment of the three forward candidates to three distinct early geodesic
targets.  No candidate can carry multiple contacts.

This materially simplifies the remaining problem: instead of arbitrary
contact rows, one need only analyze ten matchings between three siblings and
five ordered targets.  The next genuinely independent constraint is the
choice of the clean first vertex `c` and valid second vertex `b`.  Both stages
offer multiple choices in a four-regular graph; an obstruction must realize
one of these ten injective patterns for **every** valid `(c,b)` pair.  The
bounded controls show this never happens, but a proof must compare patterns
across different choices rather than continue filtering a single fixed
matrix.

## Lean audit

The module uses no native computation, proof holes, or custom axioms.  It was
checked with local dependencies and warnings promoted to errors:

```text
LEAN_PATH=/tmp/c5k4-133-pivot:/tmp/c5k4-133-metric:\
/tmp/c5k4-133-cross-row:/tmp/c5k4-133-depth3:\
/tmp/c5k4-133-early-comb:/tmp/c5k4-133-handle-existence:\
/tmp/c5k4-133-deep-handle:/tmp/c5k4-133-degree-four:\
/tmp/c5k4-133-regular:/tmp/c5k4-133-specialization:/tmp/c5k4-133-v07-check \
  timeout 60s lake env lean \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture133PivotContacts.lean
```

Result: exit code 0 in 6.1 seconds.

This is a decisive matrix reduction, not unrestricted handle existence and
not a counterexample release candidate.
