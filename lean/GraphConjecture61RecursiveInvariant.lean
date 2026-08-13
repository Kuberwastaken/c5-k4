import FormalConjecturesUtil

/-!
# WOWII 61: a sum-corrected recursive invariant

This file tests weak prefix dominance together with the potential
`2 * residueAux s + s.sum`.  The correction permits Havel--Hakimi successor
lists to have different sums.  The general graphical theorem is named but is
not asserted.
-/

namespace WrittenOnTheWallII.GraphConjecture61RecursiveInvariant

open SimpleGraph

/-- Descending degree list of an explicit finite simple graph. -/
def descendingDegreeList {n : ℕ} (G : SimpleGraph (Fin n))
    [DecidableRel G.Adj] : List ℕ :=
  (Finset.univ.val.map fun v ↦ G.degree v).sort (· ≥ ·)

/-- Realization-aware graphicality; arithmetic conditions alone do not
qualify. -/
def IsGraphical (s : List ℕ) : Prop :=
  ∃ n : ℕ, ∃ G : SimpleGraph (Fin n), ∃ h : DecidableRel G.Adj,
    @descendingDegreeList n G h = s

/-- Every realized degree is smaller than the order of its witness graph. -/
theorem IsGraphical.mem_lt_length {s : List ℕ} (hs : IsGraphical s)
    {d : ℕ} (hd : d ∈ s) : d < s.length := by
  obtain ⟨n, G, h, hseq⟩ := hs
  letI : DecidableRel G.Adj := h
  have hd' : d ∈ descendingDegreeList G := by simpa [hseq] using hd
  have hv : ∃ v : Fin n, G.degree v = d := by
    simpa [descendingDegreeList, eq_comm] using hd'
  obtain ⟨v, rfl⟩ := hv
  have hlen := congrArg List.length hseq
  simp [descendingDegreeList] at hlen
  simpa [hlen] using G.degree_lt_card_verts v

/-- Weak descending prefix dominance.  Unlike ordinary majorization, total
sums need not agree.  Prefix indices are finite data from zero through the
full list length. -/
def WeakPrefixDominates (s t : List ℕ) : Prop :=
  s.Pairwise (· ≥ ·) ∧
  t.Pairwise (· ≥ ·) ∧
  s.length = t.length ∧
  (List.ofFn (fun k : Fin (s.length + 1) ↦
    decide ((t.take k).sum ≤ (s.take k).sum))).all id = true

instance instDecidableWeakPrefixDominates (s t : List ℕ) :
    Decidable (WeakPrefixDominates s t) := by
  unfold WeakPrefixDominates
  infer_instance

/-- The even-scaled potential avoids division by two.  On a graphical list it
is twice `residueAux + edgeCount`. -/
def residuePotential (s : List ℕ) : ℕ :=
  2 * residueAux s + s.sum

/-- Degree-sum loss in one canonical reduction. -/
def stepLoss (s : List ℕ) : ℕ :=
  s.sum - (havelHakimiStep s).sum

/-- A canonical step never increases the degree sum. -/
theorem havelHakimiStep_sum_le (s : List ℕ) :
    (havelHakimiStep s).sum ≤ s.sum := by
  cases s with
  | nil => simp [havelHakimiStep]
  | cons d rest =>
      let a := rest.take d
      let b := rest.drop d
      have hdec : (a.map (· - 1)).sum ≤ a.sum := by
        induction a with
        | nil => simp
        | cons x xs ih =>
            simp only [List.map_cons, List.sum_cons]
            omega
      have hperm :
          ((a.map (· - 1) ++ b).mergeSort (· ≥ ·)).sum =
            (a.map (· - 1) ++ b).sum :=
        (List.mergeSort_perm _ _).sum_eq
      rw [show havelHakimiStep (d :: rest) =
          (a.map (· - 1) ++ b).mergeSort (· ≥ ·) by
        simp [havelHakimiStep, a, b, List.splitAt_eq]]
      rw [hperm, List.sum_append]
      calc
        (a.map (· - 1)).sum + b.sum ≤ a.sum + b.sum :=
          Nat.add_le_add_right hdec _
        _ = rest.sum := by
          rw [← List.sum_append]
          simp [a, b]
        _ ≤ d + rest.sum := Nat.le_add_left _ _

/-- Generic corrected recursion identity: the potential before a positive-head
step is the successor potential plus the exact degree-sum loss. -/
theorem residuePotential_cons_eq_step_add_loss
    (d : ℕ) (rest : List ℕ) (hd : d ≠ 0) :
    residuePotential (d :: rest) =
      residuePotential (havelHakimiStep (d :: rest)) + stepLoss (d :: rest) := by
  have hsum := havelHakimiStep_sum_le (d :: rest)
  unfold residuePotential stepLoss
  rw [residueAux.eq_3 d rest hd]
  omega

/-- The general realization-aware candidate.  It is recorded as a proposition
for subsequent proof work, not installed as an axiom or theorem. -/
def GraphicalWeakPotentialMonotone : Prop :=
  ∀ s t : List ℕ,
    IsGraphical s → IsGraphical t → WeakPrefixDominates s t →
      residuePotential t ≤ residuePotential s

/-- Weak dominance plus the corrected potential is already false on arbitrary
natural lists.  `[1]` weakly dominates `[0]`, but their potentials are one and
two. -/
theorem unrestricted_weakPotential_counterexample :
    WeakPrefixDominates [1] [0] ∧
      ¬ residuePotential [0] ≤ residuePotential [1] := by
  native_decide

/-- The bad source `[1]` is not graphical: its sole degree would have to be
strictly smaller than one. -/
theorem not_graphical_singleton_one : ¬ IsGraphical [1] := by
  intro hs
  have := hs.mem_lt_length (by simp : 1 ∈ ([1] : List ℕ))
  simp at this

/-- Every graphical singleton is the zero list. -/
theorem graphical_singleton_eq_zero {d : ℕ} (hs : IsGraphical [d]) :
    d = 0 := by
  have hd := hs.mem_lt_length (by simp : d ∈ ([d] : List ℕ))
  simp at hd
  omega

/-- Therefore the corrected weak-dominance candidate is true at order one. -/
theorem graphicalWeakPotentialMonotone_singletons
    {a b : ℕ} (ha : IsGraphical [a]) (hb : IsGraphical [b])
    (_hdom : WeakPrefixDominates [a] [b]) :
    residuePotential [b] ≤ residuePotential [a] := by
  rw [graphical_singleton_eq_zero ha, graphical_singleton_eq_zero hb]

/-- The committed first graphical transfer before recursion: the concentrated
source dominates the balanced target, and the corrected potential decreases
from ten to eight. -/
theorem first_transfer_weakPotential :
    WeakPrefixDominates [2, 1, 1, 0] [1, 1, 1, 1] ∧
    residuePotential [1, 1, 1, 1] ≤ residuePotential [2, 1, 1, 0] ∧
    residuePotential [2, 1, 1, 0] = 10 ∧
    residuePotential [1, 1, 1, 1] = 8 := by
  native_decide

/-- After one Havel--Hakimi step the dominance orientation reverses, but weak
dominance remains applicable because it permits the sums zero and two.  The
corrected potentials are exactly equal. -/
theorem first_transfer_successor_weakPotential :
    havelHakimiStep [2, 1, 1, 0] = [0, 0, 0] ∧
    havelHakimiStep [1, 1, 1, 1] = [1, 1, 0] ∧
    WeakPrefixDominates [1, 1, 0] [0, 0, 0] ∧
    residuePotential [0, 0, 0] = residuePotential [1, 1, 0] ∧
    residuePotential [0, 0, 0] = 6 := by
  native_decide

/-- Exact potential accounting for the committed example.  The current-state
potential equals the successor potential plus twice the removed head degree.
This is the correction that the equal-sum majorization attempt lacked. -/
theorem first_transfer_recursive_accounting :
    residuePotential [2, 1, 1, 0] =
      residuePotential (havelHakimiStep [2, 1, 1, 0]) + 2 * 2 ∧
    residuePotential [1, 1, 1, 1] =
      residuePotential (havelHakimiStep [1, 1, 1, 1]) + 2 * 1 := by
  native_decide

end WrittenOnTheWallII.GraphConjecture61RecursiveInvariant
