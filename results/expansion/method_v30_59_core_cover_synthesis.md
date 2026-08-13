# Method v30: WOWII #59 core/cover synthesis

Date: 2026-08-13

Local certificate: `lean/GraphConjecture59CoreCoverSynthesis.lean`

## Outcome

This checkpoint composes the v28 relabeled deletion-critical core with the
v29 full-fan cover.  The result is an exact remaining incidence table, not a
new contradiction.

Let `a,b,d` be the three rows of the `3+3` core, with `d` the third same-side
core vertex in the v29 frame.  Let `t` be the number of vertices among
`{q,p,w}` adjacent to `d`.  Lean converts `ThirdCoreCover G d w p q` into

```text
2 <= t <= 3.
```

It then proves the following exhaustive cases.

| core | location of missing edge | marked row totals `(a,b,d)` |
|---|---|---|
| `K3,3` | none | `(7,7,5)` or `(7,7,6)` |
| `K3,3-e` | incident with `d` | `(7,7,4)` or `(7,7,5)` |
| `K3,3-e` | incident with `a` or `b` | `(6,7,5/6)` up to swapping `a,b` |

Here `a` and `b` are marked with the four known full-fan/outside incidences,
while `d` is marked with its `t` cover incidences.  These marked totals are
not yet asserted to equal ambient `SimpleGraph.degree`: that final conversion
must also carry the distinctness and core/outside-disjointness facts for the
named vertices.

The matrix statement is exact, not merely numerical.  Lean proves that the
nine-edge branch has every cross-edge, and that the eight-edge branch has a
unique missing cross-edge.  It locates that edge in row `d`, or in exactly one
of the aligned rows `a,b`, according to the corresponding row degree.

## End-to-end graph theorem

`exists_relabeling_with_exact_core_cover_profile` starts from the abstract
six-set and its proper two-coloring.  It constructs both `Fin 3`
equivalences, locates the named vertices `a,b,d` in the resulting coordinate
system, transports all six cyclic-card rectangles to deletion criticality,
converts the actual v29 cover to `t`, and returns the exact table above.

Thus the relabeling and cover are no longer parallel observations: they are
joined by a single graph-level Lean theorem.

## Honest boundary

Deletion criticality plus one forced cover does not itself force a
five-forest or a residue contradiction.  The Lean theorem
`representative_synthesis_cases_are_realizable` gives explicit coordinate
models for all three rows of the table:

- the complete matrix;
- one edge missing at `d`; and
- one edge missing at an aligned row.

All three models remain deletion critical with `t=2`.  Therefore the next
step needs genuinely new graph data, rather than more arithmetic on the same
premises.  The sharp targets are:

1. certify the four marked outside incidences as disjoint ambient neighbors
   and push the resulting three-vertex degree prefix into the residue list;
2. use the column endpoint of the unique missing edge to choose an opposite
   core vertex for a second five-forest exchange; or
3. obtain a second v29 cover with a different missed endpoint, intersecting
   the two allowed incidence patterns at `d`.

The third option is the most local: two distinct two-of-three covers can
force `d` to see all of a larger frame without requiring a global degree
argument.

## Lean audit

The v28 relabeling dependency was rebuilt from source in 11.50 seconds.  The
new synthesis module was then rebuilt with the repository-pinned Lean 4.27
toolchain, warnings as errors, and the mandatory 60-second cap:

```text
ELAN_TOOLCHAIN=leanprover/lean4:v4.27.0 \
LEAN_PATH=/tmp/c5k4-59-v30-synthesis:/tmp/c5k4-59-v29-audit.BoHebr:\
/tmp/c5k4-59-v27-audit.Q5a01Z:/tmp \
timeout 60s lake env lean \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture59CoreCoverSynthesis.lean
```

Result: exit code 0 in 24.83 seconds.  The bounded Boolean matrix checks use
ordinary kernel reduction.  The source contains no proof holes, native
evaluation shortcut, custom axioms, or diagnostic print commands.

WOWII #59 is already externally disproved.  This remains theorem extraction,
not a new counterexample or release candidate.
