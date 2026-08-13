import FormalConjecturesUtil

/-!
# Alon--Tarsi fixed-edge subdivision: exact arithmetic shadow

The completed Petersen experiment has two graph-theoretic certificates:
suppressing a subdivided path gives the lower bound `21+t`, while extending
a Petersen cover that uses the selected edge once gives the matching upper
bound.  This file packages that honest certificate interface and proves the
resulting exact `7/5` arithmetic.

No graph suppression theorem is asserted here.  The abstract certificate
requires both graph-theoretic inequalities as inputs.
-/

namespace AlonTarsi.FixedEdgeSubdivisionArithmetic

/-- Abstract lower/upper certificates for an invariant after inserting `t`
degree-two vertices on one fixed edge.  In the intended application,
`lower` comes from suppressing the path in every cover and `upper` comes from
extending a base cover that uses the selected edge exactly once. -/
structure SuppressExtendCertificate
    (baseScc subdividedScc subdivisions : ℕ) : Prop where
  lower : baseScc + subdivisions ≤ subdividedScc
  upper : subdividedScc ≤ baseScc + subdivisions

/-- Matching suppression and extension certificates determine the invariant
exactly. -/
theorem scc_eq_base_add
    {baseScc subdividedScc subdivisions : ℕ}
    (certificate : SuppressExtendCertificate
      baseScc subdividedScc subdivisions) :
    subdividedScc = baseScc + subdivisions := by
  exact Nat.le_antisymm certificate.upper certificate.lower

/-- Subdividing one edge `t` times transports the integer Alon--Tarsi
residual by exactly `2*t`, provided both the edge count and shortest cover
length increase by `t`.  Integer coordinates avoid hiding any truncated
natural subtraction. -/
theorem integer_residual_transport
    {baseScc baseEdges subdividedScc subdividedEdges subdivisions : ℕ}
    (hscc : subdividedScc = baseScc + subdivisions)
    (hedges : subdividedEdges = baseEdges + subdivisions) :
    (7 : ℤ) * subdividedEdges - 5 * subdividedScc =
      ((7 : ℤ) * baseEdges - 5 * baseScc) + 2 * subdivisions := by
  norm_num [hscc, hedges]
  ring

/-- Petersen's baseline point lies exactly on the integer `7/5` wall. -/
theorem petersen_baseline_residual :
    (7 : ℕ) * 15 = 5 * 21 := by
  norm_num

/-- Exact closed form for the fixed-edge subdivision family. -/
theorem petersen_subdivision_exact_identity (t : ℕ) :
    7 * (15 + t) = 5 * (21 + t) + 2 * t := by
  omega

/-- Therefore every member of the family satisfies the denominator-cleared
Alon--Tarsi inequality. -/
theorem petersen_subdivision_satisfies_wall (t : ℕ) :
    5 * (21 + t) ≤ 7 * (15 + t) := by
  omega

/-- In natural subtraction coordinates the residual is exactly `2*t`. -/
theorem petersen_subdivision_residual_eq (t : ℕ) :
    7 * (15 + t) - 5 * (21 + t) = 2 * t := by
  omega

/-- The residual is strict after every nontrivial subdivision. -/
theorem petersen_subdivision_strict {t : ℕ} (ht : 0 < t) :
    5 * (21 + t) < 7 * (15 + t) := by
  omega

/-- Full theorem shadow with an honest graph-certificate boundary.  Once the
caller supplies the suppression lower bound, extension upper bound, and edge
count, Lean recovers `scc=21+t`, the conjectured inequality, and residual
`2*t`. -/
theorem petersen_fixed_edge_subdivision_shadow
    {t subdividedScc subdividedEdges : ℕ}
    (certificate : SuppressExtendCertificate 21 subdividedScc t)
    (hedges : subdividedEdges = 15 + t) :
    subdividedScc = 21 + t ∧
      5 * subdividedScc ≤ 7 * subdividedEdges ∧
      7 * subdividedEdges - 5 * subdividedScc = 2 * t := by
  have hscc := scc_eq_base_add certificate
  subst subdividedScc
  subst subdividedEdges
  exact ⟨rfl, petersen_subdivision_satisfies_wall t,
    petersen_subdivision_residual_eq t⟩

end AlonTarsi.FixedEdgeSubdivisionArithmetic

#print axioms AlonTarsi.FixedEdgeSubdivisionArithmetic.scc_eq_base_add
#print axioms AlonTarsi.FixedEdgeSubdivisionArithmetic.integer_residual_transport
#print axioms AlonTarsi.FixedEdgeSubdivisionArithmetic.petersen_fixed_edge_subdivision_shadow
