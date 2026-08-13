# Method v0.4: bounded Lean extraction for WOWII 61

Date: **2026-08-13 UTC**

Outcome: **partial no-`sorry` formalization**, not a proof or disproof of
WOWII 61.

## Frozen target and input

- Upstream checkout: `google-deepmind/formal-conjectures` commit
  `9a1636c4030039f70cf78b866c216d8b6c5f35b0`.
- Upstream declaration:
  `FormalConjectures/WrittenOnTheWallII/GraphConjecture61.lean`, theorem
  `WrittenOnTheWallII.GraphConjecture61.conjecture61`.
- Paper-proof input:
  `results/expansion/method_v03_61_proof.md`.
- New certificate:
  `lean/GraphConjecture61Partial.lean`.
- Certificate SHA-256 after removing temporary in-file audit commands:
  `16d6ddc12d5493c5e21fd604c5e30f4cad6e0c82950b42bb3f21351c8ca2bed5`.

The upstream conjecture remains the denominator-three statement

```text
residue(G) + ceil(diameter(G)/3) <= f(G).
```

This lane formalizes only the safe denominator-four machinery isolated by the
v0.3 proof report. It does not restate the open conjecture as a theorem.

## Compiled theorem inventory

The certificate proves the following reusable results.

1. `exists_threeSeparated_marked_set`: if every consecutive pair of indices
   `i,i+1` up to `D` contains a marked index, there is a finite marked set `S`
   whose distinct indices are at natural distance at least three and which
   satisfies the exact count

   ```text
   D <= 4 * S.card.
   ```

   The proof is a strong induction implementing the leftmost greedy argument.
   It chooses index zero when marked and index one otherwise, then recurses
   after a shift of three. No finite checking or decision procedure is used.

2. `exists_threeSeparated_indices_outside_independent`: along any graph walk,
   an independent vertex set cannot contain two consecutive walk vertices.
   Applying the counting theorem therefore produces three-separated walk
   indices outside the independent set with
   `p.length <= 4 * S.card`.

3. `isAcyclic_of_independent_parts_of_left_unique_neighbor`: a graph covered
   by two independent parts is acyclic when every vertex in the left part has
   at most one neighbour in the right part. The proof rejects a hypothetical
   cycle by examining its first two vertices and the two distinct cycle
   neighbours of a left-part vertex.

4. `induce_union_isAcyclic_of_left_unique_neighbor`: induced-union form of the
   preceding structural lemma.

5. `safe_threeSeparated_augmentation`: in a connected graph, if `I` is
   independent and distinct vertices of `X` have graph distance at least
   three, then `G.induce (I union X)` is acyclic. Distance at least three makes
   `X` independent and prevents two vertices of `X` from sharing a neighbour;
   the preceding cycle lemma then applies.

6. `card_le_largestInducedForestSize`: any explicit finite induced forest
   gives the corresponding lower bound on the repository definition of
   `largestInducedForestSize`.

7. `add_card_le_largestInducedForestSize_of_threeSeparated`: for disjoint
   finite sets `I,X` satisfying the safe augmentation hypotheses,

   ```text
   I.card + X.card <= G.largestInducedForestSize.
   ```

8. `dist_getVert_eq_natDist_of_length_eq_dist`: vertices at indices `i,j`
   of a shortest walk are at graph distance `Nat.dist i j`. The proof uses
   mathlib's `length_eq_dist_of_subwalk` on the exact walk segment
   `(p.drop i).take (j-i)`.

9. `exists_geodesic_augmentation`: composes the counting, metric, cycle, image
   cardinality, and induced-forest bridges. Given an independent finite set
   `I` and a shortest walk `p`, it constructs a disjoint finite set `X` with

   ```text
   p.length <= 4 * X.card
   I.card + X.card <= G.largestInducedForestSize.
   ```

10. `exists_residue_quarter_witness_of_certificates`: makes the remaining
    premise completely explicit. Given a residue-sized independent set and a
    diametral shortest walk, it constructs `X` satisfying

    ```text
    diameter(G) <= 4 * X.card
    residue(G) + X.card <= G.largestInducedForestSize.
    ```

    This is a conditional certificate theorem, not an assertion that the
    missing residue-sized independent set has been constructed.

11. `exists_residue_quarter_witness_of_independent_set`: discharges the
    diametral-walk premise using mathlib's finite diameter and connected
    shortest-walk existence theorems. Its sole extra mathematical certificate
    is an independent finite set whose cardinality equals `residue G`.

Together these results formally certify the combinatorial counting half, the
cycle-theoretic augmentation half, the shortest-subwalk metric bridge, and the
complete geodesic-to-induced-forest construction used by the rigorous paper
argument.

## Deliberate boundary

The file does **not** claim

```text
f(G) >= residue(G) + ceil(diameter(G)/4).
```

Closing that specialization now requires one substantial missing bridge:

1. a proved realization-level certificate that every graph contains an
   independent set of order at least its Havel--Hakimi `residue`; the current
   `Residue.lean` file defines `residueAux` and `residue` but exposes no such
   theorem.

The metric and injective image/card bookkeeping that initially appeared to be
an API boundary were completed in this lane through the subwalk API. The full
denominator-three statement remains blocked by the exact countermodels and
quantifier failures recorded in `method_v03_61_proof.md`.

## Verification

Run from the pinned `formal-conjectures` checkout:

```bash
timeout 60s lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture61Partial.lean
```

Result: **PASS**, warning-clean, in 6.9 seconds on the campaign VPS. Every
compile/search subprocess in this lane was capped at 60 seconds; the slowest
completed in 7.7 seconds.

The source contains no `sorry`, `admit`, or custom `axiom`. Its two explicit
`#print axioms` audits report only Lean/mathlib's standard foundations:

```text
exists_threeSeparated_indices_outside_independent:
  [propext, Classical.choice, Quot.sound]

exists_residue_quarter_witness_of_independent_set:
  [propext, Classical.choice, Quot.sound]
```

In particular, neither theorem depends on `sorryAx` or a project-specific
axiom.

## Verdict

This bounded lane materially advances the WOWII 61 theorem signal without
overstating it. The safe augmentation and its exact quarter-count are now
machine checked, including its shortest-walk metric and finite-image bridges.
The remaining work is the API/theorem bridge from Havel--Hakimi residue to an
independent-set witness; the original denominator-three conjecture remains
open.
