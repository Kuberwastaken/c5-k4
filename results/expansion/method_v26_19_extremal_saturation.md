# Method v26: WOWII #19/#13 extremal saturation

## Scope

This rung isolates the equality case in the remaining diameter--maximum-degree
incidence count.  It builds on the committed tree-plus-one-edge decomposition
and fundamental-cycle path package, but it does **not** claim the final surplus
theorem.

Lean source:
`lean/GraphConjecture19ExtremalSaturation.lean`

## Certified statements

For a diametral-path vertex set `P` with `|P| = d + 1` and a
maximum-degree open neighborhood `N` with `|N| = Delta`, assume the extremal
equality

`d + Delta = |V| + 1`.

The file proves the following finite-set consequences.

1. **Maximum-degree vertex on the path.**  If `|P ∩ N| <= 2`, then equality
   forces both

   - `|P ∩ N| = 2`, and
   - `P ∪ N = V`.

2. **Maximum-degree vertex off the path.**  If `c` lies in neither `P` nor its
   open neighborhood `N`, and `|P ∩ N| <= 3`, then equality forces both

   - `|P ∩ N| = 3`, and
   - `{c} ∪ P ∪ N = V`.

3. For the canonical tree-plus-one-edge decomposition, these saturation
   identities classify each endpoint of the added edge.  In the on-path case
   each endpoint lies in `P` or `N`; in the off-path case each endpoint is `c`
   or lies in `P` or `N`.

These conclusions are exact: no slack remains in either the intersection
bound or the vertex-covering count.

## Exact residual

The remaining theorem is now a graph-incidence exclusion, not a cardinality
identity or a unique-path construction.  Starting from the canonical simple
tree path between the endpoints of the added edge (whose union with that edge
is the fundamental cycle), one must show that an odd unicyclic graph cannot
realize either saturated classification above.  Equivalently, extract a
fundamental-cycle/support vertex outside the asserted path-neighborhood cover,
or derive a forbidden extra adjacency/cycle from the endpoint classification.

Thus the unresolved work is:

- connect `P` to an actual diametral path and `N` to the open neighborhood of
  an actual maximum-degree vertex;
- use geodesicity to control how `N` can meet consecutive vertices of `P`;
- use uniqueness of the fundamental cycle to rule out the resulting saturated
  endpoint-incidence configurations.

Once that exclusion is proved, the strict surplus needed by the existing
`OddUnicyclicCoreCertificate` fields follows from the two saturation lemmas.

## Verification

From `/Users/kuber.mehta/Projects/formal-conjectures`:

```text
LEAN_PATH=/Users/kuber.mehta/Projects/c5-k4/lean lake env lean \
  -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture19ExtremalSaturation.lean
```

Result: exit code 0, with no warnings or output.  No `sorry`, `admit`,
`native_decide`, or custom axioms are used.
