# Method v0.5: WOWII 133 beyond the cubic specialization

Date: 2026-08-13 UTC

Status: **NONCUBIC REDUCTION FORMALIZED / TRIANGLE-CORRECTION BRIDGE OPEN**

Local artifact: `lean/GraphConjecture133Next.lean`

## Exact source target

The corrected upstream statement remains

```text
path(G) >= radius(G) + floor(l(G))^cC4(G),
```

where `l(G)` is the average independence number of open neighborhoods and
`cC4(G)=1` exactly when `G` contains no not-necessarily-induced four-cycle.
The completed preceding lane proves the whole cubic C4-free specialization.
This pass addresses the remaining noncubic C4-free structure and does not
claim full WOWII 133.

## Frozen exact gate before formalization

No new graph was generated.  An exact Python check read only the frozen
`method_v02_133_search.jsonl` rows and reconstructed their saved graph6
graphs.  Every subprocess was capped at 60 seconds.

The proposed triangle-free identity was checked on all applicable frozen
rows:

| check | result |
|---|---:|
| graph6 rows read | 1,042 |
| triangle-free rows | 135 |
| `l(G) = average degree(G)` | 135 / 135 |
| triangle-free and C4-free rows | 75 |
| rows with completed exact path solve | 74 |
| `path >= radius + floor(average degree)` | 74 / 74 |
| saved path timeout omitted from verdict | 1 |

The omitted row is the already logged Hoffman--Singleton path timeout; no
verdict was inferred from it.

The gate also rejected an attractive but false generalization.  Substituting
average degree for `l(G)` on every C4-free graph fails on frozen row
`atlas:Bw`, the triangle `K3`:

```text
path = 2, radius = 1, average degree = 2,
so 2 < 1 + floor(2) = 3,
while l(K3)=1 and the actual source inequality is equality.
```

Thus average degree is the correct exact coordinate only after selecting the
triangle-free stratum.

Finally, the triangle-corrected identity

```text
l(G) = (2 |E(G)| - 3 t(G)) / |V(G)|
```

was checked on all 131 frozen C4-free graph6 rows, with zero failures.  Here
`t(G)` is the number of triangles.  This check is evidence for the next proof
bridge, not a formal theorem in the present artifact.

## Formal result 1: exact triangle-free coordinate

For every finite triangle-free simple graph, with no regularity assumption,
the file proves

```lean
indepNeighborsCard_eq_degree_of_triangleFree
```

at each vertex.  The proof uses mathlib's theorem that a triangle-free graph
has an independent open neighborhood, then exhibits the whole neighborhood
subtype as a maximum independent set of its induced graph.

Summing the pointwise equality gives

```lean
l_eq_averageDegree_of_triangleFree
```

in the exact repository types:

```text
l(G) = (averageDegree(G) : Rational cast to Real).
```

The floor equality is packaged separately as
`floor_l_eq_floor_averageDegree_of_triangleFree`.

## Formal result 2: exact noncubic reduction

The source-shaped C4-free inequality is defined as
`C4FreeBranchConclusion`.  The theorem

```lean
c4FreeBranch_iff_averageDegree_of_triangleFree
```

proves that, throughout the triangle-free stratum, it is logically equivalent
to

```text
radius(G) + floor(average degree(G)) <= path(G).
```

This is a genuine noncubic reduction: the entire local-independence invariant
has disappeared, leaving one induced-path wall in standard degree and metric
coordinates.

For a triangle-free `d`-regular graph, the further lemmas

```lean
l_eq_regularDegree_of_triangleFree
c4FreeBranch_iff_radius_add_degree_of_regular_triangleFree
```

reduce the source branch exactly to `radius(G)+d <= path(G)`.  This extends
the coordinate reduction behind the cubic proof to every regular degree,
without asserting that the remaining path inequality has been proved.

## Formal result 3: C4-free neighborhoods are matchings

The theorem

```lean
degree_induce_neighborSet_le_one_of_c4Free
```

proves that every vertex of every graph induced by an open neighborhood has
degree at most one whenever `G` is C4-free.  If a neighborhood vertex had two
distinct neighbors, those three neighborhood vertices together with the
center would form a four-cycle.  No regularity or triangle-free hypothesis is
used.

This is the structural half of the observed triangle-correction formula:
each induced neighborhood is a disjoint union of isolated vertices and
edges.

## Exact remaining boundary

The highest-leverage next formal bridge is now isolated cleanly.

1. Prove for every finite graph `H` of maximum degree at most one that

   ```text
   indepNum(H) + |E(H)| = |V(H)|.
   ```

   Such an `H` is a matching plus isolated vertices, so a maximum independent
   set chooses every isolated vertex and one endpoint from each edge.
2. Apply this to every induced open neighborhood using the compiled
   degree-at-most-one theorem.
3. Double-count neighborhood edges: every triangle contributes one such edge
   at each of its three vertices.  This gives

   ```text
   l(G) = (2|E(G)| - 3t(G)) / |V(G)|
   ```

   for every C4-free graph.
4. The remaining full conjecture is then the path wall using the floor of
   that triangle-corrected average.

Mathlib has subgraph matching infrastructure, but no directly applicable
theorem connecting a degree-at-most-one simple graph to this exact
independence-number formula.  The present pass stops at that honest API and
finite-choice boundary rather than postulating it.

## Verification

The final warning-as-error build was run from the unmodified
`formal-conjectures` Lake project:

```text
timeout 60s lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture133Next.lean
```

It exited successfully in approximately seven seconds.  Temporary
`#print axioms` audits of the average-degree identity, the equivalence theorem,
and the C4-free neighborhood theorem reported only `propext`,
`Classical.choice`, and `Quot.sound`; they reported no `sorryAx` or custom
axiom.  The temporary commands were removed.  A source scan finds no `sorry`,
`admit`, or custom `axiom` in the Lean artifact.

## Claim boundary

This pass proves an exact noncubic reduction and a general C4-free structural
lemma.  It does not prove the average-degree path wall, the triangle-corrected
identity, the remaining triangle-containing path wall, or full WOWII 133.
