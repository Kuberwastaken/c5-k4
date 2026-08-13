import FormalConjecturesUtil

/-!
# Reed complete-join coordinate extraction

The prospective complete-join trial isolates a purely arithmetic mechanism.
This file packages that mechanism independently of the concrete graph family:
once exact invariant changes under a join have been certified, the new Reed
slack follows without any further graph search.

Mathlib currently has no simple-graph complete-join constructor together with
finite chromatic-, clique-, and maximum-degree formulae.  Accordingly, this
module does not pretend to prove those missing graph API results.  It records
them as explicit certificate equalities and proves the reusable coordinate
transform and its odd `C5[K_m]` specialization.
-/

namespace ReedCompleteJoinCoordinates

open SimpleGraph

universe u

/-- Exact natural-number coordinates for the finite Reed expression. -/
structure ExactCoordinates where
  chi : ℕ
  omega : ℕ
  maxDegree : ℕ

/-- `slack c s` says that the Reed right side exceeds twice the chromatic
coordinate by exactly `s`. -/
def ExactCoordinates.Slack (c : ExactCoordinates) (s : ℕ) : Prop :=
  c.omega + c.maxDegree + 2 = 2 * c.chi + s

/-- Exact finite-graph invariant data whose arithmetic coordinates have known
Reed slack.  The graph operation itself is deliberately abstract: this is the
certificate boundary needed when a graph construction has no library API. -/
structure GraphCertificate {V : Type u} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj] where
  coordinates : ExactCoordinates
  slack : ℕ
  chi_eq : G.chromaticNumber = (coordinates.chi : ℕ∞)
  omega_eq : G.cliqueNum = coordinates.omega
  maxDegree_eq : G.maxDegree = coordinates.maxDegree
  balanced : coordinates.Slack slack

/-- A certified exact slack immediately proves the finite Reed inequality. -/
theorem GraphCertificate.reed_bound {V : Type u} [Fintype V] [DecidableEq V]
    {G : SimpleGraph V} [DecidableRel G.Adj]
    (C : GraphCertificate G) :
    2 * G.chromaticNumber ≤ G.cliqueNum + G.maxDegree + 2 := by
  have hnat : 2 * C.coordinates.chi ≤
      C.coordinates.omega + C.coordinates.maxDegree + 2 := by
    have hb := C.balanced
    unfold ExactCoordinates.Slack at hb
    omega
  rw [C.chi_eq, C.omega_eq, C.maxDegree_eq]
  exact_mod_cast hnat

/-- Generic complete-join arithmetic.  Suppose a base has exact slack `s`,
its order exceeds `Delta+1` by `q`, and joining a `t`-clique changes
`(chi,omega,Delta)` to `(chi+t,omega+t,n+t-1)`.  Then the new exact slack is
`s+q`.

The theorem is phrased without subtraction, using `n = Delta+1+q`; this keeps
all coordinates in `Nat` and exposes the precise uncancelled term. -/
theorem completeJoin_coordinate_transform
    (base joined : ExactCoordinates) (n t s q : ℕ)
    (hbase : base.Slack s)
    (horder : n = base.maxDegree + 1 + q)
    (hchi : joined.chi = base.chi + t)
    (homega : joined.omega = base.omega + t)
    (hDelta : joined.maxDegree + 1 = n + t) :
    joined.Slack (s + q) := by
  unfold ExactCoordinates.Slack at hbase ⊢
  omega

/-- Odd carrier coordinates, writing `m=2k+1` so no floor or ceiling is
needed: `chi=5k+3`, `omega=4k+2`, `Delta=6k+2`. -/
def oddCarrierCoordinates (k : ℕ) : ExactCoordinates where
  chi := 5 * k + 3
  omega := 4 * k + 2
  maxDegree := 6 * k + 2

/-- The odd `C5[K_(2k+1)]` coordinate profile lies exactly on Reed's wall. -/
theorem oddCarrierCoordinates_slack_zero (k : ℕ) :
    (oddCarrierCoordinates k).Slack 0 := by
  simp only [ExactCoordinates.Slack, oddCarrierCoordinates]
  omega

/-- The order of `C5[K_(2k+1)]` exceeds `Delta+1` by `4k+2`, which is
`2(2k+1)`.  This is exactly the slack created by a complete clique join. -/
theorem oddCarrier_order_decomposition (k : ℕ) :
    10 * k + 5 = (oddCarrierCoordinates k).maxDegree + 1 + (4 * k + 2) := by
  simp only [oddCarrierCoordinates]
  omega

/-- Concrete arithmetic specialization of the prospective trial.  Any joined
graph whose exact coordinates are the predicted ones has slack `4k+2`,
independently of the joined clique order `t`. -/
theorem oddCarrier_completeJoin_slack (k t : ℕ) (joined : ExactCoordinates)
    (hchi : joined.chi = (oddCarrierCoordinates k).chi + t)
    (homega : joined.omega = (oddCarrierCoordinates k).omega + t)
    (hDelta : joined.maxDegree + 1 = (10 * k + 5) + t) :
    joined.Slack (4 * k + 2) := by
  simpa using completeJoin_coordinate_transform
    (oddCarrierCoordinates k) joined (10 * k + 5) t 0 (4 * k + 2)
    (oddCarrierCoordinates_slack_zero k)
    (oddCarrier_order_decomposition k) hchi homega hDelta

/-- Graph-facing specialization: exact invariant certificates for a predicted
odd-carrier join prove both its exact slack and the finite Reed inequality. -/
theorem reed_bound_of_oddCarrier_completeJoin_certificate
    {V : Type u} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (k t : ℕ)
    (hchi : G.chromaticNumber = ((oddCarrierCoordinates k).chi + t : ℕ))
    (homega : G.cliqueNum = (oddCarrierCoordinates k).omega + t)
    (hDelta : G.maxDegree + 1 = (10 * k + 5) + t) :
    2 * G.chromaticNumber + (4 * k + 2) =
      G.cliqueNum + G.maxDegree + 2 ∧
    2 * G.chromaticNumber ≤ G.cliqueNum + G.maxDegree + 2 := by
  let joined : ExactCoordinates :=
    { chi := (oddCarrierCoordinates k).chi + t
      omega := (oddCarrierCoordinates k).omega + t
      maxDegree := (10 * k + 5) + t - 1 }
  have hDeltaEq : G.maxDegree = joined.maxDegree := by
    simp only [joined]
    omega
  have hslack : joined.Slack (4 * k + 2) :=
    oddCarrier_completeJoin_slack k t joined (by rfl) (by rfl) (by
      simp only [joined]
      omega)
  have hnat : 2 * joined.chi + (4 * k + 2) =
      joined.omega + joined.maxDegree + 2 := by
    unfold ExactCoordinates.Slack at hslack
    omega
  constructor
  · rw [hchi, homega, hDeltaEq]
    exact_mod_cast hnat
  · have hle : 2 * joined.chi ≤ joined.omega + joined.maxDegree + 2 := by omega
    rw [hchi, homega, hDeltaEq]
    exact_mod_cast hle

end ReedCompleteJoinCoordinates
