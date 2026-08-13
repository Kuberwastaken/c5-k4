import FormalConjecturesUtil

/-!
# WOWII 133: the cubic C4-free specialization

This file states the corrected specialization proved on paper in
`results/expansion/method_v03_133_proof.md`.  In particular, C4-free is not
silently strengthened to triangle-free.
-/

namespace WrittenOnTheWallII.GraphConjecture133Cubic

open SimpleGraph

variable {V : Type*} [Fintype V] [DecidableEq V] [Nonempty V]

/-- Four distinct vertices forming a (not necessarily induced) four-cycle. -/
def HasC4 (G : SimpleGraph V) : Prop :=
  ∃ a b c d : V,
    a ≠ b ∧ a ≠ c ∧ a ≠ d ∧ b ≠ c ∧ b ≠ d ∧ c ≠ d ∧
      G.Adj a b ∧ G.Adj b c ∧ G.Adj c d ∧ G.Adj d a

/-- The exact two-case conclusion of the paper proof. -/
def CubicC4FreeSplit (G : SimpleGraph V) : Prop :=
  (G.CliqueFree 3 → ⌊l G⌋ = (3 : ℤ) ∧ G.radius.toNat + 3 ≤ path G) ∧
  (¬G.CliqueFree 3 → ⌊l G⌋ = (2 : ℤ) ∧ G.radius.toNat + 2 ≤ path G)

/-- The actual cubic C4-free specialization of WOWII 133. -/
def CubicC4FreeConclusion (G : SimpleGraph V) : Prop :=
  (G.radius.toNat : ℝ) + (⌊l G⌋ : ℝ) ≤ (path G : ℝ)

omit [Nonempty V] in
/-- A concrete induced-path witness is the currently missing bridge into the
`path` invariant's `Finset.max` implementation. -/
lemma path_ge_of_isInducedPath (G : SimpleGraph V) (xs : List V)
    (hxs : G.isInducedPath xs) : xs.length ≤ path G := by
  classical
  unfold path
  let paths := Finset.univ.filter (fun s : Finset V =>
    ∃ l : List V, l.toFinset = s ∧ G.isInducedPath l)
  have hmem : xs.toFinset ∈ paths := by
    simp only [paths, Finset.mem_filter, Finset.mem_univ, true_and]
    exact ⟨xs, rfl, hxs⟩
  have hnodup : xs.Nodup := hxs.1
  have hcard : xs.toFinset.card = xs.length := List.toFinset_card_of_nodup hnodup
  have himage : xs.toFinset.card ∈ paths.image Finset.card :=
    Finset.mem_image.mpr ⟨xs.toFinset, hmem, rfl⟩
  obtain ⟨m, hm⟩ := Finset.max_of_mem himage
  rw [← hcard]
  change xs.toFinset.card ≤ (paths.image Finset.card).max.getD 0
  rw [hm]
  simpa using Finset.le_max_of_eq himage hm

omit [Nonempty V] in
/-- The exact split implies the source-shaped real inequality by integer
arithmetic alone; all graph theory is isolated in `CubicC4FreeSplit`. -/
lemma conclusion_of_split (G : SimpleGraph V) (h : CubicC4FreeSplit G) :
    CubicC4FreeConclusion G := by
  unfold CubicC4FreeSplit at h
  unfold CubicC4FreeConclusion
  by_cases htri : G.CliqueFree 3
  · obtain ⟨hl, hp⟩ := h.1 htri
    rw [hl]
    exact_mod_cast hp
  · obtain ⟨hl, hp⟩ := h.2 htri
    rw [hl]
    exact_mod_cast hp

/-- Precise theorem target.  The two branches deliberately match the paper
proof: `radius+3` only under triangle-freeness, and otherwise the local-average
floor is two and `radius+2` is proved. -/
def CubicC4FreeTheorem : Prop :=
  ∀ (G : SimpleGraph V),
    [DecidableRel G.Adj] →
    G.Connected →
    G.IsRegularOfDegree 3 →
    ¬HasC4 G →
    CubicC4FreeSplit G ∧ CubicC4FreeConclusion G

end WrittenOnTheWallII.GraphConjecture133Cubic
