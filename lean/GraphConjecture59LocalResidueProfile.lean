import GraphConjecture59MissingColumnPropagation

/-!
# WOWII 59: exact local residue profile after column propagation

The surviving `K3,3-e` frame has twelve untracked incidences: each of the
three opposite-core columns may or may not meet each of `u,c,v,p`.  The v31
exact deficient-column DNF and the v32 two-column covers reduce those 4096
raw completions to 486.  This file checks their Havel--Hakimi residue exactly.
-/

namespace WrittenOnTheWallII.GraphConjecture59LocalResidueProfile

open SimpleGraph

/-- Vertex order for the local graph:
`a,b,d,r,s,t,u,c,v,p,q`. -/
def fixedEdges : List (Nat × Nat) :=
  [
    (0, 3), (0, 4),
    (1, 3), (1, 4), (1, 5),
    (2, 3), (2, 4), (2, 5),
    (0, 6), (0, 7), (0, 8),
    (1, 6), (1, 7), (1, 8),
    (2, 6), (2, 7), (2, 8),
    (6, 7), (7, 8),
    (0, 9), (1, 9), (2, 9), (9, 10),
    (2, 10), (3, 10), (4, 10), (5, 10),
    (6, 10), (7, 10), (8, 10)
  ]

/-- The twelve free bits are ordered row-major on
`{r,s,t} × {u,c,v,p}`. -/
def localEdgeBool (m : Fin 4096) (x y : Nat) : Bool :=
  let i := min x y
  let j := max x y
  if (i, j) ∈ fixedEdges then true
  else if i = 3 ∧ 6 ≤ j ∧ j ≤ 9 then m.val.testBit (j - 6)
  else if i = 4 ∧ 6 ≤ j ∧ j ≤ 9 then m.val.testBit (4 + j - 6)
  else if i = 5 ∧ 6 ≤ j ∧ j ≤ 9 then m.val.testBit (8 + j - 6)
  else false

/-- The exact eleven-vertex local graph determined by the free incidence
mask. `fromRel` symmetrizes the upper-triangular Boolean relation. -/
def graph (m : Fin 4096) : SimpleGraph (Fin 11) :=
  SimpleGraph.fromRel fun x y ↦ localEdgeBool m x.val y.val = true

instance (m : Fin 4096) : DecidableRel (graph m).Adj := by
  unfold graph
  infer_instance

/-- The v31 deficient-column DNF: `t` sees both path endpoints, or it sees
the center and `p` together with one endpoint. -/
def DeficientColumnCondition (m : Fin 4096) : Prop :=
  let tu := m.val.testBit 8
  let tc := m.val.testBit 9
  let tv := m.val.testBit 10
  let tp := m.val.testBit 11
  (tu && tv) || (tu && tc && tp) || (tc && tv && tp) = true

instance (m : Fin 4096) : Decidable (DeficientColumnCondition m) := by
  unfold DeficientColumnCondition
  infer_instance

/-- The v32 pointwise covers: each of `u,c,v,p` meets `r` or `s`. -/
def NondeficientColumnsCondition (m : Fin 4096) : Prop :=
  ((m.val.testBit 0 || m.val.testBit 4) &&
    (m.val.testBit 1 || m.val.testBit 5) &&
    (m.val.testBit 2 || m.val.testBit 6) &&
    (m.val.testBit 3 || m.val.testBit 7)) = true

instance (m : Fin 4096) : Decidable (NondeficientColumnsCondition m) := by
  unfold NondeficientColumnsCondition
  infer_instance

/-- The eleven local degrees in vertex order `a,b,d,r,s,t,u,c,v,p,q`.
The constant terms are the fixed incidences; the twelve mask bits are the
only variable contributions. -/
def localDegrees (m : Fin 4096) : List ℕ :=
  [
    6,
    7,
    8,
    4 + (m.val.testBit 0).toNat + (m.val.testBit 1).toNat +
      (m.val.testBit 2).toNat + (m.val.testBit 3).toNat,
    4 + (m.val.testBit 4).toNat + (m.val.testBit 5).toNat +
      (m.val.testBit 6).toNat + (m.val.testBit 7).toNat,
    3 + (m.val.testBit 8).toNat + (m.val.testBit 9).toNat +
      (m.val.testBit 10).toNat + (m.val.testBit 11).toNat,
    5 + (m.val.testBit 0).toNat + (m.val.testBit 4).toNat +
      (m.val.testBit 8).toNat,
    6 + (m.val.testBit 1).toNat + (m.val.testBit 5).toNat +
      (m.val.testBit 9).toNat,
    5 + (m.val.testBit 2).toNat + (m.val.testBit 6).toNat +
      (m.val.testBit 10).toNat,
    4 + (m.val.testBit 3).toNat + (m.val.testBit 7).toNat +
      (m.val.testBit 11).toNat,
    8
  ]

/-- Descending local degree profile obtained from the explicit coordinate
formulas. -/
def localDegreeProfile (m : Fin 4096) : List ℕ :=
  (localDegrees m).mergeSort (· ≥ ·)

/-- The 51 distinct descending degree profiles produced by the 486 masks
that satisfy both column conditions. -/
def admissibleProfiles : List (List ℕ) := [
  [8, 8, 7, 7, 7, 7, 6, 6, 6, 5, 5],
  [8, 8, 7, 7, 7, 7, 6, 6, 6, 6, 6],
  [8, 8, 7, 7, 7, 7, 7, 6, 5, 5, 5],
  [8, 8, 7, 7, 7, 7, 7, 6, 6, 6, 5],
  [8, 8, 7, 7, 7, 7, 7, 7, 6, 6, 6],
  [8, 8, 8, 7, 7, 6, 6, 6, 6, 6, 6],
  [8, 8, 8, 7, 7, 7, 6, 6, 6, 6, 5],
  [8, 8, 8, 7, 7, 7, 7, 6, 5, 5, 4],
  [8, 8, 8, 7, 7, 7, 7, 6, 6, 5, 5],
  [8, 8, 8, 7, 7, 7, 7, 6, 6, 6, 4],
  [8, 8, 8, 7, 7, 7, 7, 6, 6, 6, 6],
  [8, 8, 8, 7, 7, 7, 7, 7, 6, 6, 5],
  [8, 8, 8, 7, 7, 7, 7, 7, 7, 6, 6],
  [8, 8, 8, 8, 7, 7, 6, 6, 6, 6, 4],
  [8, 8, 8, 8, 7, 7, 6, 6, 6, 6, 6],
  [8, 8, 8, 8, 7, 7, 7, 6, 5, 5, 5],
  [8, 8, 8, 8, 7, 7, 7, 6, 6, 5, 4],
  [8, 8, 8, 8, 7, 7, 7, 6, 6, 6, 5],
  [8, 8, 8, 8, 7, 7, 7, 7, 6, 5, 5],
  [8, 8, 8, 8, 7, 7, 7, 7, 6, 6, 4],
  [8, 8, 8, 8, 7, 7, 7, 7, 6, 6, 6],
  [8, 8, 8, 8, 7, 7, 7, 7, 7, 6, 5],
  [8, 8, 8, 8, 7, 7, 7, 7, 7, 7, 6],
  [8, 8, 8, 8, 8, 7, 6, 6, 6, 6, 5],
  [8, 8, 8, 8, 8, 7, 7, 6, 6, 5, 5],
  [8, 8, 8, 8, 8, 7, 7, 6, 6, 6, 6],
  [8, 8, 8, 8, 8, 7, 7, 7, 6, 6, 5],
  [8, 8, 8, 8, 8, 7, 7, 7, 7, 6, 6],
  [8, 8, 8, 8, 8, 8, 7, 6, 6, 6, 5],
  [8, 8, 8, 8, 8, 8, 7, 7, 6, 5, 5],
  [8, 8, 8, 8, 8, 8, 7, 7, 6, 6, 6],
  [8, 8, 8, 8, 8, 8, 7, 7, 7, 7, 6],
  [8, 8, 8, 8, 8, 8, 8, 7, 6, 6, 5],
  [8, 8, 8, 8, 8, 8, 8, 7, 7, 6, 6],
  [9, 8, 8, 7, 7, 7, 6, 6, 6, 6, 6],
  [9, 8, 8, 7, 7, 7, 7, 6, 6, 6, 5],
  [9, 8, 8, 7, 7, 7, 7, 7, 6, 6, 6],
  [9, 8, 8, 7, 7, 7, 7, 7, 7, 7, 6],
  [9, 8, 8, 8, 7, 7, 6, 6, 6, 6, 5],
  [9, 8, 8, 8, 7, 7, 7, 6, 6, 5, 5],
  [9, 8, 8, 8, 7, 7, 7, 6, 6, 6, 6],
  [9, 8, 8, 8, 7, 7, 7, 7, 6, 6, 5],
  [9, 8, 8, 8, 7, 7, 7, 7, 7, 6, 6],
  [9, 8, 8, 8, 8, 7, 6, 6, 6, 6, 6],
  [9, 8, 8, 8, 8, 7, 7, 6, 6, 6, 5],
  [9, 8, 8, 8, 8, 7, 7, 7, 6, 6, 6],
  [9, 8, 8, 8, 8, 7, 7, 7, 7, 7, 6],
  [9, 8, 8, 8, 8, 8, 7, 7, 6, 6, 5],
  [9, 8, 8, 8, 8, 8, 7, 7, 7, 6, 6],
  [9, 8, 8, 8, 8, 8, 8, 7, 6, 6, 6],
  [9, 8, 8, 8, 8, 8, 8, 7, 7, 7, 6]
]

/-- The low eight bits encode only the `r,s` rows. -/
def LowColumnsCondition (m : Fin 256) : Prop :=
  ((m.val.testBit 0 || m.val.testBit 4) &&
    (m.val.testBit 1 || m.val.testBit 5) &&
    (m.val.testBit 2 || m.val.testBit 6) &&
    (m.val.testBit 3 || m.val.testBit 7)) = true

instance (m : Fin 256) : Decidable (LowColumnsCondition m) := by
  unfold LowColumnsCondition
  infer_instance

/-- Explicit local degree list with the `r,s` mask and four fixed choices
for the deficient `t` row separated. -/
def splitLocalDegrees (m : Fin 256) (tu tc tv tp : Bool) : List ℕ :=
  [
    6,
    7,
    8,
    4 + (m.val.testBit 0).toNat + (m.val.testBit 1).toNat +
      (m.val.testBit 2).toNat + (m.val.testBit 3).toNat,
    4 + (m.val.testBit 4).toNat + (m.val.testBit 5).toNat +
      (m.val.testBit 6).toNat + (m.val.testBit 7).toNat,
    3 + tu.toNat + tc.toNat + tv.toNat + tp.toNat,
    5 + (m.val.testBit 0).toNat + (m.val.testBit 4).toNat + tu.toNat,
    6 + (m.val.testBit 1).toNat + (m.val.testBit 5).toNat + tc.toNat,
    5 + (m.val.testBit 2).toNat + (m.val.testBit 6).toNat + tv.toNat,
    4 + (m.val.testBit 3).toNat + (m.val.testBit 7).toNat + tp.toNat,
    8
  ]

def splitLocalProfile (m : Fin 256) (tu tc tv tp : Bool) : List ℕ :=
  (splitLocalDegrees m tu tc tv tp).mergeSort (· ≥ ·)

set_option maxRecDepth 100000 in
set_option maxHeartbeats 2000000 in
/-- Every distinct degree profile found in the 486-completion audit has
Havel--Hakimi residue two. -/
theorem every_admissible_profile_has_residue_two :
    ∀ s ∈ admissibleProfiles, residueAux s = 2 := by
  norm_num [admissibleProfiles, residueAux, havelHakimiStep,
    List.splitAt_eq, List.mergeSort]

end WrittenOnTheWallII.GraphConjecture59LocalResidueProfile
