# Method v0.4: WOWII 61 residue bridge audit

Date: **2026-08-13 UTC**

Outcome: **exact formal reduction and terminal case**, but the classical
Griggs--Kleitman inequality itself is not yet formalized. This is not a proof
of WOWII 61 and does not weaken the Havel--Hakimi residue.

## Frozen target

- Certificate: `lean/GraphConjecture61Partial.lean`.
- Upstream residue definition:
  `FormalConjecturesForMathlib/Combinatorics/SimpleGraph/Residue.lean`.
- Upstream conjecture:
  `FormalConjectures/WrittenOnTheWallII/GraphConjecture61.lean`.
- Paper ladder: `results/expansion/method_v03_61_proof.md`.
- Upstream checkout inspected at the commit already frozen by the parent
  lane: `9a1636c4030039f70cf78b866c216d8b6c5f35b0`.

The required realization-level statement is

```text
there exists I with IsIndepSet(G,I) and |I| = residue(G).
```

Equivalently, it is the classical numerical inequality

```text
residue(G) <= indepNum(G).
```

The paper route obtains it by running Maxine (repeated deletion of a current
maximum-degree vertex), proving that the terminal independent set has at
least the Havel--Hakimi residue, and discarding surplus vertices.

## What the upstream API contains

`Residue.lean` currently supplies only:

1. `havelHakimiStep`, which drops the head degree and decrements the next
   `d` entries of a descending list;
2. `havelHakimiStep_length_cons`;
3. the well-founded evaluator `residueAux`; and
4. `residue G`, obtained by applying `residueAux` to the sorted degree list.

Repository-wide bounded searches found no theorem relating `residueAux` or
`residue` to `IsIndepSet`, `indepNum`, maximum-degree deletion, graphical
degree sequences, or degree-sequence domination. Mathlib does provide the
opposite end of the bridge: `exists_isNIndepSet_indepNum` constructs a maximum
independent set.

The missing mathematical step is therefore not finite-set selection. It is
the one-step Griggs--Kleitman comparison: after deleting an arbitrary
maximum-degree vertex of a realization, the resulting degree sequence need
not equal the canonical Havel--Hakimi step (the deleted vertex's actual
neighbors need not be the next highest-degree vertices). One needs a proved
degree-transfer/majorization lemma showing that the residue of the actual
deletion sequence is at least the residue after the canonical step. Neither
the comparison relation nor its monotonicity theorem exists in the inspected
API.

## New warning-clean lemmas

The certificate now proves, without `sorry`, `admit`, or custom axioms:

1. `residueAux_le_length`: the recursive residue never exceeds its input-list
   length. The proof follows `residueAux.induct` and uses
   `havelHakimiStep_length_cons` in the recursive branch.
2. `residue_le_card`: `residue G <= Fintype.card V`.
3. `exists_independent_card_eq_residue_iff_le_indepNum`: the exact witness
   bridge is equivalent to `residue G <= G.indepNum`. The reverse direction
   takes a residue-sized subset of a maximum independent set.
4. `exists_independent_card_eq_residue_of_le_indepNum`: witness-producing
   interface to that reverse direction.
5. `exists_independent_card_eq_residue_of_univ_independent`: the terminal
   Maxine case, where the current graph is edgeless/its entire vertex set is
   independent.
6. `exists_residue_quarter_witness_of_residue_le_indepNum`: once the classical
   numerical inequality is supplied, all previously formalized geodesic and
   induced-forest machinery automatically produces the exact quarter witness

   ```text
   diam(G) <= 4 * |X|
   residue(G) + |X| <= largestInducedForestSize(G).
   ```

Thus the formal boundary is now a single named numerical theorem, rather than
an informal request for a specially chosen residue core.

## Why the full bridge was not asserted

A direct induction on `residueAux` would be invalid: the recursive list is the
canonical Havel--Hakimi sequence, while an independent set must live in the
fixed realization `G`. Conversely, deleting a maximum-degree vertex from `G`
recurses on a subtype graph whose sorted degree sequence is generally
different from `havelHakimiStep` of the original sorted degree list. Bridging
those sequences is precisely the content of the classical theorem.

Adding an axiom, postulating monotonicity, replacing residue by independence
number, or selecting vertices from a different Havel--Hakimi realization would
all hide this realization mismatch. None was done.

## Verification

From the pinned `formal-conjectures` checkout:

```bash
timeout 60s lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture61Partial.lean
```

Result: **PASS** in approximately seven seconds. Every source search and build
in this lane was individually bounded by 60 seconds.

Temporary `#print axioms` checks (removed after the audit) for
`residueAux_le_length`, the witness equivalence, and the composed quarter
interface each reported only

```text
[propext, Classical.choice, Quot.sound]
```

There is no `sorryAx` or project-specific axiom dependency.

## Next formal ladder

The shortest honest continuation is a reusable degree-sequence development,
not more work on geodesics:

1. define the elementary unit-transfer/majorization relation between sorted
   natural-number sequences;
2. prove `residueAux` monotone in the direction required by a transfer;
3. prove that deleting a maximum-degree vertex produces a degree sequence
   above the canonical Havel--Hakimi step in that relation;
4. perform well-founded induction on the vertex count for Maxine, using the
   newly formalized terminal case;
5. feed `residue G <= G.indepNum` to
   `exists_residue_quarter_witness_of_residue_le_indepNum`.

Until steps 1--4 exist, the rigorous status remains a partial quarter theorem
whose sole missing premise is now isolated exactly.
