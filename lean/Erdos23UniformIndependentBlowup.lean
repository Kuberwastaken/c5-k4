import FormalConjecturesUtil

/-!
# Erdős 23: uniform independent-blow-up certificate API

This module packages the exact optimization mechanism used by the audited
Andrásfai-successor trial.  It does not assume a graph blow-up API that Mathlib
does not currently provide.  Instead, an adapter for a concrete construction
must supply two honest operations:

* normalize every lifted assignment to a whole-bag quotient assignment with
  no worse objective value;
* lift every quotient assignment, with objective multiplied exactly by the
  square of the uniform bag size.

Those obligations are sufficient to transport exact maximum-cut and minimum
bipartization certificates.  The final section checks only the audited
`A_14`/bag-five arithmetic; it makes no claim about an all-`k` Andrásfai
bipartization formula.
-/

namespace Erdos23.UniformIndependentBlowup

/-- An exact certificate that `value` is the maximum of `score`. -/
structure MaxCertificate {C : Type} (score : C → ℕ) (value : ℕ) where
  witness : C
  witness_eq : score witness = value
  upper : ∀ c, score c ≤ value

/-- An exact certificate that `value` is the minimum of `cost`. -/
structure MinCertificate {C : Type} (cost : C → ℕ) (value : ℕ) where
  witness : C
  witness_eq : cost witness = value
  lower : ∀ c, value ≤ cost c

/-- Certificate boundary for transporting a maximization problem through a
uniform independent blow-up.  `normalize_dominates` is the whole-bag rounding
obligation; `lift_exact` is the edge-multiplicity obligation. -/
structure UniformMaxAdapter (s : ℕ) {Q L : Type}
    (quotientScore : Q → ℕ) (liftedScore : L → ℕ) where
  normalize : L → Q
  lift : Q → L
  normalize_dominates : ∀ x, liftedScore x ≤ s ^ 2 * quotientScore (normalize x)
  lift_exact : ∀ q, liftedScore (lift q) = s ^ 2 * quotientScore q

/-- Certificate boundary for transporting a minimization problem through a
uniform independent blow-up.  Here normalization cannot increase deletion
cost, while lifting multiplies every quotient interface by `s^2`. -/
structure UniformMinAdapter (s : ℕ) {Q L : Type}
    (quotientCost : Q → ℕ) (liftedCost : L → ℕ) where
  normalize : L → Q
  lift : Q → L
  normalize_improves : ∀ x, s ^ 2 * quotientCost (normalize x) ≤ liftedCost x
  lift_exact : ∀ q, liftedCost (lift q) = s ^ 2 * quotientCost q

/-- Exact maximum cut scales by `s^2` once the concrete construction supplies
the whole-bag normalization and exact-lift certificates. -/
def MaxCertificate.uniformScale {s qmax : ℕ} {Q L : Type}
    {quotientScore : Q → ℕ} {liftedScore : L → ℕ}
    (A : UniformMaxAdapter s quotientScore liftedScore)
    (C : MaxCertificate quotientScore qmax) :
    MaxCertificate liftedScore (s ^ 2 * qmax) where
  witness := A.lift C.witness
  witness_eq := by rw [A.lift_exact, C.witness_eq]
  upper x := (A.normalize_dominates x).trans
    (Nat.mul_le_mul_left (s ^ 2) (C.upper (A.normalize x)))

/-- Exact minimum bipartization cost scales by `s^2` once the concrete
construction supplies its normalization and exact-lift certificates. -/
def MinCertificate.uniformScale {s qmin : ℕ} {Q L : Type}
    {quotientCost : Q → ℕ} {liftedCost : L → ℕ}
    (A : UniformMinAdapter s quotientCost liftedCost)
    (C : MinCertificate quotientCost qmin) :
    MinCertificate liftedCost (s ^ 2 * qmin) where
  witness := A.lift C.witness
  witness_eq := by rw [A.lift_exact, C.witness_eq]
  lower x := (Nat.mul_le_mul_left (s ^ 2) (C.lower (A.normalize x))).trans
    (A.normalize_improves x)

/-- Exact edge-count, maximum-cut, and edge-bipartization coordinates.  The
balance equation makes explicit the usual complementarity between retained
cut edges and deleted edges. -/
structure CutCoordinates where
  edges : ℕ
  maxCut : ℕ
  bipartization : ℕ
  balanced : maxCut + bipartization = edges

/-- Coordinate scaling induced by uniform bags of size `s`. -/
def CutCoordinates.uniformScale (s : ℕ) (c : CutCoordinates) : CutCoordinates where
  edges := s ^ 2 * c.edges
  maxCut := s ^ 2 * c.maxCut
  bipartization := s ^ 2 * c.bipartization
  balanced := by
    rw [← Nat.mul_add, c.balanced]

/-- A combined certificate API.  It retains both objective functions and both
normalization adapters instead of inferring either from bare arithmetic. -/
structure UniformBlowupCertificate (s : ℕ)
    {QCut LCut QBip LBip : Type}
    (quotientCut : QCut → ℕ) (liftedCut : LCut → ℕ)
    (quotientBip : QBip → ℕ) (liftedBip : LBip → ℕ)
    (q : CutCoordinates) where
  cutAdapter : UniformMaxAdapter s quotientCut liftedCut
  bipAdapter : UniformMinAdapter s quotientBip liftedBip
  quotientMax : MaxCertificate quotientCut q.maxCut
  quotientMin : MinCertificate quotientBip q.bipartization

/-- The combined certificate transports both exact coordinates. -/
def UniformBlowupCertificate.scaledObjectives
    {s : ℕ} {QCut LCut QBip LBip : Type}
    {quotientCut : QCut → ℕ} {liftedCut : LCut → ℕ}
    {quotientBip : QBip → ℕ} {liftedBip : LBip → ℕ}
    {q : CutCoordinates}
    (C : UniformBlowupCertificate s quotientCut liftedCut quotientBip liftedBip q) :
    MaxCertificate liftedCut (q.uniformScale s).maxCut ×
      MinCertificate liftedBip (q.uniformScale s).bipartization := by
  exact ⟨C.quotientMax.uniformScale C.cutAdapter,
    C.quotientMin.uniformScale C.bipAdapter⟩

/-- Proposition-level specification of the maximum-certificate transport.
This theorem is convenient for axiom auditing while `uniformScale` itself
retains the maximizing witness as data. -/
theorem max_uniformScale_spec {s qmax : ℕ} {Q L : Type}
    {quotientScore : Q → ℕ} {liftedScore : L → ℕ}
    (A : UniformMaxAdapter s quotientScore liftedScore)
    (C : MaxCertificate quotientScore qmax) :
    let D := C.uniformScale A
    liftedScore D.witness = s ^ 2 * qmax ∧
      ∀ x, liftedScore x ≤ s ^ 2 * qmax := by
  exact ⟨(C.uniformScale A).witness_eq, (C.uniformScale A).upper⟩

/-- Proposition-level specification of the minimum-certificate transport. -/
theorem min_uniformScale_spec {s qmin : ℕ} {Q L : Type}
    {quotientCost : Q → ℕ} {liftedCost : L → ℕ}
    (A : UniformMinAdapter s quotientCost liftedCost)
    (C : MinCertificate quotientCost qmin) :
    let D := C.uniformScale A
    liftedCost D.witness = s ^ 2 * qmin ∧
      ∀ x, s ^ 2 * qmin ≤ liftedCost x := by
  exact ⟨(C.uniformScale A).witness_eq, (C.uniformScale A).lower⟩

/-- Audited quotient coordinates for `A_14`.  These are concrete certificate
inputs from the independent zero-gap MILP audit, not a symbolic family claim. -/
def a14Coordinates : CutCoordinates where
  edges := 287
  maxCut := 238
  bipartization := 49
  balanced := by norm_num

/-- Bag-five scaling reproduces the audited 205-vertex coordinates. -/
theorem a14_bagFive_coordinates :
    (a14Coordinates.uniformScale 5).edges = 7175 ∧
    (a14Coordinates.uniformScale 5).maxCut = 5950 ∧
    (a14Coordinates.uniformScale 5).bipartization = 1225 := by
  norm_num [CutCoordinates.uniformScale, a14Coordinates]

/-- Erdős parameter 41 gives allowance `41^2 = 1681`; the audited lifted
bipartization value has exact positive slack 456. -/
theorem a14_bagFive_erdos23_slack :
    (a14Coordinates.uniformScale 5).bipartization + 456 = 41 ^ 2 ∧
    (a14Coordinates.uniformScale 5).bipartization < 41 ^ 2 := by
  norm_num [CutCoordinates.uniformScale, a14Coordinates]

#print axioms max_uniformScale_spec
#print axioms min_uniformScale_spec
#print axioms a14_bagFive_coordinates
#print axioms a14_bagFive_erdos23_slack

end Erdos23.UniformIndependentBlowup
