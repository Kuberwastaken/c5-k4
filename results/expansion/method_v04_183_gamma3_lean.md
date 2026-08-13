# Method v0.4 Lane P1: Lean proof of the WOWII 183 `gamma_c >= 3` tier

Date: **2026-08-13**. Status: **complete local no-`sorry` formal proof of the
paper proposition; not a proof of full WOWII 183**.

Local artifact:

```text
lean/GraphConjecture183GammaThree.lean
```

## Exact formal result

The strongest top-level theorem in the file is

```lean
theorem five_le_b_of_connectedDominationNumber
    (G : SimpleGraph V) (hconn : G.Connected) {x z : V}
    (hdist : G.dist x z = 3)
    (hgamma : 3 <= G.connectedDominationNumber) :
    (5 : Real) <= b G
```

Thus the formal statement matches the stronger proposition proved on paper in
`method_v04_183_tier_proof.md`: a finite connected graph with a distance-three
pair and connected domination number at least three has induced-bipartite
number at least five.  It does not assume 2-connectivity, claw-freeness,
nonbipartiteness, uniqueness of the distance-three vertex, or an eccentricity
upper bound.

The proof first establishes the stronger witness statement

```lean
exists S : Finset V,
  S.card = 5 and (G.induce (S : Set V)).IsBipartite.
```

It then transfers that witness through the repository definitions
`largestInducedBipartiteSubgraphSize` and `b`.

## Upstream-definition audit

There is currently no `GraphConjecture183.lean` declaration in the checked-out
`formal-conjectures` tree.  The artifact therefore imports
`FormalConjecturesUtil` and uses the upstream support definitions directly:

- `SimpleGraph.b` and
  `SimpleGraph.largestInducedBipartiteSubgraphSize` from
  `FormalConjecturesForMathlib/Combinatorics/SimpleGraph/Induced.lean`;
- `SimpleGraph.IsConnectedDominating` and
  `SimpleGraph.connectedDominationNumber` from
  `FormalConjecturesForMathlib/Combinatorics/SimpleGraph/Domination.lean`;
- `SimpleGraph.dist`, shortest walks, induced subgraphs, and graph
  bipartiteness from Mathlib.

No project-local replacement invariant is introduced.  An intermediate
pointwise premise,

```lean
forall D : Finset V,
  G.IsConnectedDominating (D : Set V) -> 3 <= D.card,
```

is derived from `3 <= G.connectedDominationNumber` using the actual `sInf`
definition; it is not assumed by the final invariant-native theorem.

## Formal proof route

1. Extract a shortest `x`--`z` walk from connectedness and the distance
   hypothesis.  Its length is three, yielding vertices `x-a-d-z`.
2. Prove the three possible chords `x-d`, `x-z`, and `a-z` impossible by
   constructing walks of length at most two and contradicting
   `dist x z = 3`.
3. Color the induced four-vertex path by parity:

   ```text
   A = {x,d},    C = {a,z}.
   ```

4. If an outside vertex misses all neighbors in either color class, extend
   the coloring to obtain an explicit induced bipartite five-set.
5. Otherwise every outside vertex meets both color classes.  Any outside
   vertex not dominated by `{a,d}` would then be adjacent to both `x` and
   `z`, again giving an `x`--`z` walk of length two.  Hence `{a,d}` is a
   connected dominating set of cardinality two, contradicting
   `gamma_c >= 3`.
6. Insert the resulting five-set into the bounded `sSup` defining the largest
   induced bipartite subgraph size, then cast the natural bound to the
   real-valued notation `b G`.

The file also retains a reusable one-vertex coloring-extension lemma and both
the explicit-geodesic and shortest-walk-extraction forms of the proposition.

## Verification

The warning-clean build was run under the campaign's hard external cap:

```text
timeout 60s lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture183GammaThree.lean
```

Result: **exit 0** in 8.5 seconds.

The file contains no `sorry`, `admit`, or custom axiom.  Its in-file axiom
audit reports exactly:

```text
depends on axioms: [propext, Classical.choice, Quot.sound]
```

These are standard Lean/Mathlib foundations; `sorryAx` is absent.

## Exact remaining boundary

This closes the entire `gamma_c = 3` tier of the live WOWII 183 proof lane and,
in fact, proves the same lower bound whenever `gamma_c >= 3`. It does **not**
close WOWII 183: this theorem supplies only `b >= 5`. The separate paper proof
in `method_v04_183_multiext.md` has since closed the `gamma_c = 4` tier with
`b >= 6`, but that second result is not formalized in this file. The remaining
full-core work concerns larger connected-domination values under the source's
unique-distance-three structure.
