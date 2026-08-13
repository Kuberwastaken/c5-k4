# Method v0.15: WOWII 133 cross-row contacts

Date: 2026-08-13

Local certificate: `lean/GraphConjecture133CrossRowContacts.lean`

## Abstract contact-matrix enumeration

The v0.14 allowable nonempty rows are

```text
{4}, {3}, {2}, {1}, {1,4}, {0}, {0,4}, {0,3}.
```

Three forward candidates share the same parent `b`.  If two distinct rows
contained the same target index `k`, the vertices would form the C4

```text
b -- a₁ -- x_k -- a₂ -- b.
```

Therefore the three rows must be pairwise disjoint.  Enumerating unordered
triples of allowable nonempty rows under this cross-row condition leaves 20
abstract matrices:

```text
{4},{3},{2}        {4},{3},{1}        {4},{3},{0}
{4},{2},{1}        {4},{2},{0}        {4},{2},{0,3}
{4},{1},{0}        {4},{1},{0,3}      {3},{2},{1}
{3},{2},{1,4}      {3},{2},{0}        {3},{2},{0,4}
{3},{1},{0}        {3},{1},{0,4}      {3},{1,4},{0}
{2},{1},{0}        {2},{1},{0,4}      {2},{1},{0,3}
{2},{1,4},{0}      {2},{1,4},{0,3}
```

This exact enumeration establishes an important negative conclusion: the C4
cross-row restriction alone does **not** eliminate every three-nonempty-row
cover.  Twenty local incidence types survive.

## Formal cross-row results

`not_common_target_of_shared_parent` proves the generic shared-target C4
obstruction, including the necessary freshness condition separating the
common parent from the target.

`earlyContactSet_disjoint_of_shared_parent` defines the exact early contact
sets over indices `0..4` and proves that two distinct fresh siblings have
disjoint rows.

`not_adj_of_shared_parent_of_triangleFree` records the companion constraint:
distinct candidates sharing `b` are pairwise nonadjacent, since an edge
between them would form a triangle with `b`.

Finally:

- `exists_distinct_contacts_of_two_blocked_siblings` shows two blocked rows
  require two distinct target indices;
- `exists_three_distinct_contacts_of_three_blocked_siblings` shows a full
  three-row obstruction requires three pairwise distinct target indices.

These are symbolic Lean theorems and use no enumeration oracle.

## Strongest honest classification

Combining v0.14 and v0.15, any obstruction to a clean depth-three vertex must
have all of the following properties:

1. exactly three nonempty rows, one for each forward candidate;
2. every row is one of the eight allowable row types;
3. the rows are pairwise disjoint;
4. the three candidates are pairwise nonadjacent;
5. at least three distinct geodesic target indices occur.

The 20 matrices above are the complete abstract survivors of conditions
1--3.  Conditions 4--5 are already implicit in their graph realization but
do not remove an abstract row triple.

Further progress must use more than girth-five incidence at the shared parent.
The natural next discriminator is global metric compatibility: combine two
different rows to construct an alternative path between their target indices,
then compare that path with the geodesic segment.  Because all early target
differences are at most four and the route through `b` has length four, only
equal-length boundary cases survive; those cases need induced-path or
eccentricity information rather than a strict shortest-path contradiction.

## Lean audit

The module uses no native computation, proof holes, or custom axioms.  It was
checked with local dependencies and warnings promoted to errors:

```text
LEAN_PATH=/tmp/c5k4-133-cross-row:/tmp/c5k4-133-depth3:\
/tmp/c5k4-133-early-comb:/tmp/c5k4-133-handle-existence:\
/tmp/c5k4-133-deep-handle:/tmp/c5k4-133-degree-four:\
/tmp/c5k4-133-regular:/tmp/c5k4-133-specialization:/tmp/c5k4-133-v07-check \
  timeout 60s lake env lean \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture133CrossRowContacts.lean
```

Result: exit code 0 in 9.5 seconds.

This is a complete local cross-row classification, not unrestricted handle
existence and not a counterexample release candidate.
