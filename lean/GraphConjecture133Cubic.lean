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

omit [Fintype V] [DecidableEq V] [Nonempty V] in
/-- The ordered support of a shortest walk is an induced path in the exact
list-based sense used by the WOWII `path` invariant. -/
lemma isInducedPath_support_of_length_eq_dist {G : SimpleGraph V} {u v : V}
    (p : G.Walk u v) (hp : p.length = G.dist u v) :
    G.isInducedPath p.support := by
  constructor
  · exact (p.isPath_of_length_eq_dist hp).support_nodup
  · intro i j
    have hgeti : p.support.get i = p.getVert i.val := by
      simpa [Function.comp_apply] using congrFun p.getVert_comp_val_eq_get_support i |>.symm
    have hgetj : p.support.get j = p.getVert j.val := by
      simpa [Function.comp_apply] using congrFun p.getVert_comp_val_eq_get_support j |>.symm
    rw [hgeti, hgetj]
    constructor
    · intro hij
      have hi : i.val ≤ p.length := by grind [p.length_support]
      have hj : j.val ≤ p.length := by grind [p.length_support]
      have hne : i.val ≠ j.val := by
        intro heq
        rw [heq] at hij
        exact G.loopless _ hij
      rcases lt_or_gt_of_ne hne with hijlt | hjilt
      · left
        let q : G.Walk u v :=
          ((p.take i.val).append hij.toWalk).append (p.drop j.val)
        have hq : G.dist u v ≤ q.length := G.dist_le q
        have htake : (p.take i.val).length = i.val := by simp [Walk.take_length, hi]
        have hdrop : (p.drop j.val).length = p.length - j.val := by
          simp [Walk.drop_length]
        simp only [q, Walk.length_append, Walk.length_cons, Walk.length_nil,
          zero_add] at hq
        rw [htake, hdrop, ← hp] at hq
        omega
      · right
        let q : G.Walk u v :=
          ((p.take j.val).append hij.symm.toWalk).append (p.drop i.val)
        have hq : G.dist u v ≤ q.length := G.dist_le q
        have htake : (p.take j.val).length = j.val := by simp [Walk.take_length, hj]
        have hdrop : (p.drop i.val).length = p.length - i.val := by
          simp [Walk.drop_length]
        simp only [q, Walk.length_append, Walk.length_cons, Walk.length_nil,
          zero_add] at hq
        rw [htake, hdrop, ← hp] at hq
        omega
    · rintro (hij | hji)
      · have hi : i.val < p.length := by
          have hjlt := j.isLt
          have hlen := p.length_support
          omega
        simpa [hij] using p.adj_getVert_succ hi
      · have hj : j.val < p.length := by
          have hilt := i.isLt
          have hlen := p.length_support
          omega
        simpa [hji] using (p.adj_getVert_succ hj).symm

omit [DecidableEq V] in
/-- In a finite connected graph, some shortest walk realizes the radius, and
its ordered support is an induced path with exactly `radius + 1` vertices. -/
lemma exists_radius_geodesic_support (G : SimpleGraph V) (hconn : G.Connected) :
    ∃ (u v : V) (p : G.Walk u v),
      p.length = G.radius.toNat ∧
      G.isInducedPath p.support ∧
      p.support.length = G.radius.toNat + 1 := by
  obtain ⟨u, v, huv⟩ := G.exists_edist_eq_radius_of_finite
  obtain ⟨p, _hpPath, hpLength⟩ := hconn.exists_path_of_dist u v
  refine ⟨u, v, p, ?_, isInducedPath_support_of_length_eq_dist p hpLength, ?_⟩
  · rw [hpLength]
    exact congrArg ENat.toNat huv
  · rw [p.length_support, hpLength]
    exact congrArg (fun n : ℕ ↦ n + 1) (congrArg ENat.toNat huv)

omit [Nonempty V] in
/-- A concrete induced-path witness gives a lower bound for the `path`
invariant's `Finset.max` implementation. -/
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

/-- Every finite connected graph has an induced path containing at least
`radius + 1` vertices. -/
lemma radius_add_one_le_path (G : SimpleGraph V) (hconn : G.Connected) :
    G.radius.toNat + 1 ≤ path G := by
  obtain ⟨u, v, p, _hpLength, hpInduced, hpSupport⟩ :=
    exists_radius_geodesic_support G hconn
  rw [← hpSupport]
  exact path_ge_of_isInducedPath G p.support hpInduced

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
