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

omit [DecidableEq V] in
/-- Strengthened radius-geodesic package retaining the distance equality
needed by later metric shortcut arguments. -/
lemma exists_radius_geodesic_support_with_dist (G : SimpleGraph V)
    (hconn : G.Connected) :
    ∃ (u v : V) (p : G.Walk u v),
      p.length = G.dist u v ∧
      p.length = G.radius.toNat ∧
      G.isInducedPath p.support ∧
      p.support.length = G.radius.toNat + 1 := by
  obtain ⟨u, v, huv⟩ := G.exists_edist_eq_radius_of_finite
  obtain ⟨p, _hpPath, hpLength⟩ := hconn.exists_path_of_dist u v
  refine ⟨u, v, p, hpLength, ?_, isInducedPath_support_of_length_eq_dist p hpLength, ?_⟩
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

omit [Fintype V] [DecidableEq V] [Nonempty V] in
/-- Prepending a fresh vertex adjacent to the old head and to no later vertex
preserves the repository-local list representation of an induced path. -/
lemma isInducedPath_cons_of_adj_head_of_not_adj_tail {G : SimpleGraph V}
    {a b : V} {xs : List V} (hpath : G.isInducedPath (b :: xs))
    (hab : G.Adj a b) (hafresh : a ∉ b :: xs)
    (hclean : ∀ x ∈ xs, ¬G.Adj a x) :
    G.isInducedPath (a :: b :: xs) := by
  constructor
  · simp only [List.nodup_cons]
    exact ⟨hafresh, by simpa only [List.nodup_cons] using hpath.1⟩
  · intro i j
    refine Fin.cases ?_ (fun i' ↦ ?_) i
    · refine Fin.cases ?_ (fun j' ↦ ?_) j
      · simp
      · refine Fin.cases ?_ (fun k ↦ ?_) j'
        · simpa using hab
        · have hnot : ¬G.Adj a (xs.get k) := hclean (xs.get k) (List.get_mem xs k)
          simp only [Fin.val_succ]
          constructor
          · exact fun hadj ↦ (hnot hadj).elim
          · intro hij
            simp at hij
    · refine Fin.cases ?_ (fun j' ↦ ?_) j
      · refine Fin.cases ?_ (fun k ↦ ?_) i'
        · simpa using hab.symm
        · have hnot : ¬G.Adj a (xs.get k) := hclean (xs.get k) (List.get_mem xs k)
          simp only [Fin.val_succ]
          constructor
          · exact fun hadj ↦ (hnot hadj.symm).elim
          · intro hij
            simp at hij
      · simp only [Fin.val_succ]
        constructor
        · intro hadj
          rcases (hpath.2 i' j').mp hadj with hij | hji
          · left; omega
          · right; omega
        · intro hij
          apply (hpath.2 i' j').mpr
          rcases hij with hij | hji
          · left; omega
          · right; omega

/-- Every finite connected graph has an induced path containing at least
`radius + 1` vertices. -/
lemma radius_add_one_le_path (G : SimpleGraph V) (hconn : G.Connected) :
    G.radius.toNat + 1 ≤ path G := by
  obtain ⟨u, v, p, _hpLength, hpInduced, hpSupport⟩ :=
    exists_radius_geodesic_support G hconn
  rw [← hpSupport]
  exact path_ge_of_isInducedPath G p.support hpInduced

/-- A finite connected cubic graph without a four-cycle has radius at least
two.  This isolates the small-radius exclusion used by both extension branches
of the paper proof. -/
lemma two_le_radius_toNat_of_cubic_c4Free (G : SimpleGraph V)
    [DecidableRel G.Adj] (hconn : G.Connected)
    (hreg : G.IsRegularOfDegree 3) (hc4 : ¬HasC4 G) :
    2 ≤ G.radius.toNat := by
  have hnontrivial : Nontrivial V := by
    let v : V := Classical.ofNonempty
    apply G.nontrivial_of_degree_ne_zero (v := v)
    rw [hreg v]
    omega
  letI : Nontrivial V := hnontrivial
  have hrne : G.radius ≠ ⊤ := G.radius_ne_top_iff.mpr hconn
  by_contra hr
  have hrsmall : G.radius.toNat = 0 ∨ G.radius.toNat = 1 := by omega
  rcases hrsmall with hrzero | hrone
  · have : G.radius = 0 := by
      rcases ENat.toNat_eq_zero.mp hrzero with hz | htop
      · exact hz
      · exact (hrne htop).elim
    exact G.radius_ne_zero_of_nontrivial this
  · have hradius : G.radius = 1 := (ENat.toNat_eq_iff one_ne_zero).mp hrone
    obtain ⟨c, hc⟩ := G.exists_eccent_eq_radius
    have hcadj : ∀ v, c ≠ v → G.Adj c v := by
      exact (G.eccent_eq_one_iff c).mp (hc.trans hradius)
    have huniv : Finset.univ = insert c (G.neighborFinset c) := by
      ext v
      simp only [Finset.mem_univ, Finset.mem_insert, G.mem_neighborFinset, true_iff]
      exact eq_or_ne c v |>.imp Eq.symm (hcadj v)
    have hcard : Fintype.card V = 4 := by
      have hcnot : c ∉ G.neighborFinset c := G.notMem_neighborFinset_self c
      have hdeg : (G.neighborFinset c).card = 3 := by
        rw [G.card_neighborFinset_eq_degree, hreg c]
      have := congrArg Finset.card huniv
      simp [hcnot, hdeg] at this
      omega
    have hcompreg : Gᶜ.IsRegularOfDegree 0 := by
      simpa [hcard] using hreg.compl
    have hcomp : Gᶜ = ⊥ := by
      ext u v
      simp only [bot_adj, iff_false]
      intro huv
      have hpos : 0 < Gᶜ.degree u := huv.degree_pos_left
      rw [hcompreg u] at hpos
      omega
    have htop : G = ⊤ := by
      simpa using congrArg (fun H : SimpleGraph V ↦ Hᶜ) hcomp
    let e : V ≃ Fin 4 := (Fintype.equivFin V).trans (finCongr hcard)
    let a : V := e.symm 0
    let b : V := e.symm 1
    let c' : V := e.symm 2
    let d : V := e.symm 3
    apply hc4
    refine ⟨a, b, c', d, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_⟩
    all_goals simp [a, b, c', d, htop]

omit [Nonempty V] in
/-- At the head of a nontrivial walk in a cubic C4-free graph, one can choose
an off-walk-direction neighbor which is not adjacent to the walk's second
vertex.  This is the finite-neighbor selection step in the one-extension
argument for WOWII 133. -/
lemma exists_neighbor_head_ne_snd_not_adj_snd_of_cubic_c4Free
    (G : SimpleGraph V) [DecidableRel G.Adj] {u v : V} (p : G.Walk u v)
    (hp : ¬p.Nil) (hreg : G.IsRegularOfDegree 3) (hc4 : ¬HasC4 G) :
    ∃ a : V, G.Adj a u ∧ a ≠ p.snd ∧ ¬G.Adj a p.snd := by
  classical
  have hus : G.Adj u p.snd := p.adj_snd hp
  let s := (G.neighborFinset u).erase p.snd
  have hsCard : s.card = 2 := by
    have hmem : p.snd ∈ G.neighborFinset u := by simpa using hus
    simp only [s]
    rw [Finset.card_erase_of_mem hmem, G.card_neighborFinset_eq_degree, hreg u]
  by_contra h
  push_neg at h
  have hsLarge : 1 < s.card := by omega
  obtain ⟨a, ha, b, hb, hab⟩ := Finset.one_lt_card.mp hsLarge
  have hau : G.Adj a u := by
    simpa [adj_comm] using (Finset.mem_of_mem_erase ha)
  have hbu : G.Adj b u := by
    simpa [adj_comm] using (Finset.mem_of_mem_erase hb)
  have has : a ≠ p.snd := Finset.ne_of_mem_erase ha
  have hbs : b ≠ p.snd := Finset.ne_of_mem_erase hb
  have hav1 : G.Adj a p.snd := h a hau has
  have hbv1 : G.Adj b p.snd := h b hbu hbs
  apply hc4
  refine ⟨u, a, p.snd, b, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_⟩
  · exact hau.ne.symm
  · exact hus.ne
  · exact hbu.ne.symm
  · exact has
  · exact hab
  · exact hbs.symm
  · exact hau.symm
  · exact hav1
  · exact hbv1.symm
  · exact hbu

omit [Fintype V] [DecidableEq V] [Nonempty V] in
/-- A vertex of a geodesic support adjacent to its head is necessarily the
second vertex (apart from the impossible loop at the head). -/
lemma eq_snd_of_mem_support_of_adj_head_of_geodesic {G : SimpleGraph V}
    {u v a : V} (p : G.Walk u v) (hp : p.length = G.dist u v)
    (ha : a ∈ p.support) (hau : G.Adj a u) : a = p.snd := by
  have hinduced := isInducedPath_support_of_length_eq_dist p hp
  obtain ⟨k, hka, hklen⟩ := Walk.mem_support_iff_exists_getVert.mp ha
  let i : Fin p.support.length := ⟨0, by simp⟩
  let j : Fin p.support.length := ⟨k, by grind [p.length_support]⟩
  have hgeti : p.support.get i = p.getVert i.val := by
    simpa [Function.comp_apply] using congrFun p.getVert_comp_val_eq_get_support i |>.symm
  have hgetj : p.support.get j = p.getVert j.val := by
    simpa [Function.comp_apply] using congrFun p.getVert_comp_val_eq_get_support j |>.symm
  have hadj : G.Adj (p.support.get i) (p.support.get j) := by
    rw [hgeti, hgetj]
    simpa [i, j, Walk.getVert_zero, hka] using hau.symm
  have hk : k = 1 := by
    rcases (hinduced.2 i j).mp hadj with hij | hji
    · simpa [i, j] using hij.symm
    · simp [i, j] at hji
  rw [← hka, hk]

omit [Fintype V] [DecidableEq V] [Nonempty V] in
/-- An off-direction neighbor of the head of a length-at-least-two geodesic,
chosen not adjacent to the second vertex, has no contact with any positive
geodesic index in a C4-free graph. -/
lemma not_adj_getVert_pos_of_geodesic_of_c4Free {G : SimpleGraph V}
    {u v a : V} (p : G.Walk u v) (hp : p.length = G.dist u v)
    (hlen : 2 ≤ p.length) (hc4 : ¬HasC4 G) (hau : G.Adj a u)
    (hane : a ≠ p.snd) (hanot : ¬G.Adj a p.snd) :
    ∀ k, 1 ≤ k → k ≤ p.length → ¬G.Adj a (p.getVert k) := by
  intro k hkpos hklen
  by_cases hk1 : k = 1
  · subst k
    exact hanot
  by_cases hk2 : k = 2
  · subst k
    intro ha2
    have hpPath : p.IsPath := p.isPath_of_length_eq_dist hp
    have hnil : ¬p.Nil := by simpa [Walk.not_nil_iff_lt_length] using (show 0 < p.length by omega)
    have h01 : G.Adj u p.snd := p.adj_snd hnil
    have h12 : G.Adj p.snd (p.getVert 2) := by
      simpa using p.adj_getVert_succ (show 1 < p.length by omega)
    have hu2 : u ≠ p.getVert 2 := by
      intro heq
      have hidx : (0 : ℕ) = 2 := hpPath.getVert_injOn
        (by simp) (by simp; omega) (by simpa [Walk.getVert_zero] using heq)
      omega
    have h12ne : p.snd ≠ p.getVert 2 := by
      intro heq
      have hidx : (1 : ℕ) = 2 := hpPath.getVert_injOn
        (by simp; omega) (by simp; omega) heq
      omega
    apply hc4
    refine ⟨u, p.snd, p.getVert 2, a, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_⟩
    · exact h01.ne
    · exact hu2
    · exact hau.ne.symm
    · exact h12ne
    · exact hane.symm
    · exact ha2.ne.symm
    · exact h01
    · exact h12
    · exact ha2.symm
    · exact hau
  · intro hak
    let q : G.Walk u v := ((hau.symm.toWalk).append hak.toWalk).append (p.drop k)
    have hq : G.dist u v ≤ q.length := G.dist_le q
    have hdrop : (p.drop k).length = p.length - k := by simp [Walk.drop_length]
    simp only [q, Walk.length_append, Walk.length_cons, Walk.length_nil,
      zero_add] at hq
    rw [hdrop, ← hp] at hq
    omega

omit [Nonempty V] in
/-- Cubicity supplies an off-direction neighbor at the head of a geodesic;
C4-freeness and shortestness make it fresh and clean against the whole tail. -/
lemma exists_clean_neighbor_of_geodesic_of_cubic_c4Free
    (G : SimpleGraph V) [DecidableRel G.Adj] {u v : V} (p : G.Walk u v)
    (hp : p.length = G.dist u v) (hlen : 2 ≤ p.length)
    (hreg : G.IsRegularOfDegree 3) (hc4 : ¬HasC4 G) :
    ∃ a : V, G.Adj a u ∧ a ∉ p.support ∧
      ∀ x ∈ p.support.tail, ¬G.Adj a x := by
  have hnil : ¬p.Nil := by
    simpa [Walk.not_nil_iff_lt_length] using (show 0 < p.length by omega)
  obtain ⟨a, hau, hane, hanot⟩ :=
    exists_neighbor_head_ne_snd_not_adj_snd_of_cubic_c4Free G p hnil hreg hc4
  refine ⟨a, hau, ?_, ?_⟩
  · intro hamem
    exact hane (eq_snd_of_mem_support_of_adj_head_of_geodesic p hp hamem hau)
  · intro x hx
    have hinduced := isInducedPath_support_of_length_eq_dist p hp
    have hutail : u ∉ p.support.tail := by
      have hnodup := hinduced.1
      rw [p.support_eq_cons] at hnodup
      exact (List.nodup_cons.mp hnodup).1
    have hxmem : x ∈ p.support := by
      rw [p.support_eq_cons]
      exact List.mem_cons_of_mem u hx
    obtain ⟨k, hkx, hklen⟩ := Walk.mem_support_iff_exists_getVert.mp hxmem
    have hkpos : 1 ≤ k := by
      by_contra hk
      have hkzero : k = 0 := by omega
      subst k
      apply hutail
      have hxu : x = u := by simpa [Walk.getVert_zero] using hkx.symm
      simpa [hxu] using hx
    have hnot := not_adj_getVert_pos_of_geodesic_of_c4Free
      p hp hlen hc4 hau hane hanot k hkpos hklen
    simpa [hkx] using hnot

omit [Nonempty V] in
/-- A length-at-least-two geodesic in a cubic C4-free graph admits a clean
one-vertex prepend in the repository-local induced-list representation. -/
lemma exists_inducedPath_cons_support_of_geodesic_of_cubic_c4Free
    (G : SimpleGraph V) [DecidableRel G.Adj] {u v : V} (p : G.Walk u v)
    (hp : p.length = G.dist u v) (hlen : 2 ≤ p.length)
    (hreg : G.IsRegularOfDegree 3) (hc4 : ¬HasC4 G) :
    ∃ a : V, G.isInducedPath (a :: p.support) ∧
      (a :: p.support).length = p.length + 2 := by
  obtain ⟨a, hau, hafresh, hclean⟩ :=
    exists_clean_neighbor_of_geodesic_of_cubic_c4Free G p hp hlen hreg hc4
  refine ⟨a, ?_, by simp [p.length_support]⟩
  rw [p.support_eq_cons]
  apply isInducedPath_cons_of_adj_head_of_not_adj_tail
  · simpa [← p.support_eq_cons] using isInducedPath_support_of_length_eq_dist p hp
  · exact hau
  · simpa [← p.support_eq_cons] using hafresh
  · exact hclean

/-- The one-extension branch needed for the triangle-containing case of the
cubic C4-free specialization of WOWII 133. -/
lemma radius_add_two_le_path_of_cubic_c4Free (G : SimpleGraph V)
    [DecidableRel G.Adj] (hconn : G.Connected)
    (hreg : G.IsRegularOfDegree 3) (hc4 : ¬HasC4 G) :
    G.radius.toNat + 2 ≤ path G := by
  obtain ⟨u, v, p, hpDist, hpLength, _hpInduced, _hpSupport⟩ :=
    exists_radius_geodesic_support_with_dist G hconn
  have hlen : 2 ≤ p.length := by
    rw [hpLength]
    exact two_le_radius_toNat_of_cubic_c4Free G hconn hreg hc4
  obtain ⟨a, haInduced, haLength⟩ :=
    exists_inducedPath_cons_support_of_geodesic_of_cubic_c4Free
      G p hpDist hlen hreg hc4
  rw [← hpLength, ← haLength]
  exact path_ge_of_isInducedPath G (a :: p.support) haInduced

omit [Nonempty V] in
/-- Cubicity exposes the two neighbours of a geodesic head other than its
second vertex.  In the triangle-free branch these two neighbours are
nonadjacent.  Keeping the witnesses explicit is useful for the four-forward-
neighbour count. -/
lemma exists_two_off_geodesic_neighbors_of_cubic_triangleFree
    (G : SimpleGraph V) [DecidableRel G.Adj] {u v : V} (p : G.Walk u v)
    (hp : ¬p.Nil) (hreg : G.IsRegularOfDegree 3) (htri : G.CliqueFree 3) :
    ∃ a b : V,
      a ≠ b ∧ G.Adj a u ∧ G.Adj b u ∧
      a ≠ p.snd ∧ b ≠ p.snd ∧ ¬G.Adj a b := by
  classical
  have hus : G.Adj u p.snd := p.adj_snd hp
  let s := (G.neighborFinset u).erase p.snd
  have hsCard : s.card = 2 := by
    have hmem : p.snd ∈ G.neighborFinset u := by simpa using hus
    simp only [s]
    rw [Finset.card_erase_of_mem hmem, G.card_neighborFinset_eq_degree, hreg u]
  obtain ⟨a, b, hab, hs⟩ := Finset.card_eq_two.mp hsCard
  have ha : a ∈ s := by simp [hs]
  have hb : b ∈ s := by simp [hs]
  have hau : G.Adj a u := by
    simpa [adj_comm] using (Finset.mem_of_mem_erase ha)
  have hbu : G.Adj b u := by
    simpa [adj_comm] using (Finset.mem_of_mem_erase hb)
  have has : a ≠ p.snd := Finset.ne_of_mem_erase ha
  have hbs : b ≠ p.snd := Finset.ne_of_mem_erase hb
  have hindep := G.isIndepSet_neighborSet_of_triangleFree htri u
  have hnab : ¬G.Adj a b := by
    apply hindep
    · simpa [G.mem_neighborSet, adj_comm] using hau
    · simpa [G.mem_neighborSet, adj_comm] using hbu
    · exact hab
  exact ⟨a, b, hab, hau, hbu, has, hbs, hnab⟩

omit [Nonempty V] in
/-- A specified neighbour in a cubic graph has exactly two further
neighbours. -/
lemma exists_two_forward_neighbors_of_cubic
    (G : SimpleGraph V) [DecidableRel G.Adj] {a u : V}
    (hau : G.Adj a u) (hreg : G.IsRegularOfDegree 3) :
    ∃ x y : V,
      x ≠ y ∧ G.Adj x a ∧ G.Adj y a ∧ x ≠ u ∧ y ≠ u := by
  classical
  let s := (G.neighborFinset a).erase u
  have hsCard : s.card = 2 := by
    have hmem : u ∈ G.neighborFinset a := by simpa [adj_comm] using hau
    simp only [s]
    rw [Finset.card_erase_of_mem hmem, G.card_neighborFinset_eq_degree, hreg a]
  obtain ⟨x, y, hxy, hs⟩ := Finset.card_eq_two.mp hsCard
  have hx : x ∈ s := by simp [hs]
  have hy : y ∈ s := by simp [hs]
  refine ⟨x, y, hxy, ?_, ?_, Finset.ne_of_mem_erase hx, Finset.ne_of_mem_erase hy⟩
  · simpa [adj_comm] using (Finset.mem_of_mem_erase hx)
  · simpa [adj_comm] using (Finset.mem_of_mem_erase hy)

omit [Nonempty V] in
/-- The two off-geodesic branches in the triangle-free cubic case have four
distinct forward neighbours.  A common forward neighbour would form a C4. -/
lemma exists_four_distinct_forward_neighbors_of_cubic_triangleFree_c4Free
    (G : SimpleGraph V) [DecidableRel G.Adj] {u a b : V}
    (hab : a ≠ b) (hau : G.Adj a u) (hbu : G.Adj b u)
    (hnab : ¬G.Adj a b) (hreg : G.IsRegularOfDegree 3) (hc4 : ¬HasC4 G) :
    ∃ x₁ x₂ y₁ y₂ : V,
      ({x₁, x₂, y₁, y₂} : Finset V).card = 4 ∧
      G.Adj x₁ a ∧ G.Adj x₂ a ∧
      G.Adj y₁ b ∧ G.Adj y₂ b ∧
      x₁ ≠ u ∧ x₂ ≠ u ∧ y₁ ≠ u ∧ y₂ ≠ u := by
  classical
  obtain ⟨x₁, x₂, hxne, hx₁a, hx₂a, hx₁u, hx₂u⟩ :=
    exists_two_forward_neighbors_of_cubic G hau hreg
  obtain ⟨y₁, y₂, hyne, hy₁b, hy₂b, hy₁u, hy₂u⟩ :=
    exists_two_forward_neighbors_of_cubic G hbu hreg
  have hcross : ∀ {x y : V}, G.Adj x a → x ≠ u →
      G.Adj y b → y ≠ u → x ≠ y := by
    intro x y hxa hxu hyb hyu hxy
    subst y
    have hxb : x ≠ b := by
      intro h
      subst x
      exact hnab hxa.symm
    have hxa' : x ≠ a := hxa.ne
    apply hc4
    refine ⟨u, a, x, b, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_⟩
    · exact hau.ne.symm
    · exact hxu.symm
    · exact hbu.ne.symm
    · exact hxa'.symm
    · exact hab
    · exact hxb
    · exact hau.symm
    · exact hxa.symm
    · exact hyb
    · exact hbu
  have hx₁y₁ := hcross hx₁a hx₁u hy₁b hy₁u
  have hx₁y₂ := hcross hx₁a hx₁u hy₂b hy₂u
  have hx₂y₁ := hcross hx₂a hx₂u hy₁b hy₁u
  have hx₂y₂ := hcross hx₂a hx₂u hy₂b hy₂u
  refine ⟨x₁, x₂, y₁, y₂, ?_, hx₁a, hx₂a, hy₁b, hy₂b,
    hx₁u, hx₂u, hy₁u, hy₂u⟩
  simp [hxne, hyne, hx₁y₁, hx₁y₂, hx₂y₁, hx₂y₂]

omit [Fintype V] [DecidableEq V] [Nonempty V] in
/-- A forward neighbour of an off-geodesic branch can contact a shortest
walk only at indices two or three.  Triangle-freeness excludes index zero,
C4-freeness excludes index one, and a later contact shortcuts the geodesic. -/
lemma forward_contact_index_eq_two_or_three
    {G : SimpleGraph V} {u v a x : V} (p : G.Walk u v)
    (hp : p.length = G.dist u v) (hau : G.Adj a u) (hxa : G.Adj x a)
    (hxu : x ≠ u) (hane : a ≠ p.snd)
    (htri : G.CliqueFree 3) (hc4 : ¬HasC4 G)
    (k : ℕ) (hklen : k ≤ p.length) (hxk : G.Adj x (p.getVert k)) :
    k = 2 ∨ k = 3 := by
  have hnil : ¬p.Nil := by
    rw [Walk.not_nil_iff_lt_length]
    by_contra hlen
    have hkzero : k = 0 := by omega
    subst k
    have hindep := G.isIndepSet_neighborSet_of_triangleFree htri a
    exact (hindep (by simpa [G.mem_neighborSet] using hau)
      (by simpa [G.mem_neighborSet, adj_comm] using hxa) hxu.symm)
      (by simpa [Walk.getVert_zero] using hxk.symm)
  have hus : G.Adj u p.snd := p.adj_snd hnil
  by_cases hk0 : k = 0
  · subst k
    exfalso
    have hindep := G.isIndepSet_neighborSet_of_triangleFree htri a
    exact (hindep (by simpa [G.mem_neighborSet] using hau)
      (by simpa [G.mem_neighborSet, adj_comm] using hxa) hxu.symm)
      (by simpa [Walk.getVert_zero] using hxk.symm)
  by_cases hk1 : k = 1
  · subst k
    apply (hc4 ⟨u, a, x, p.snd, hau.ne.symm, hxu.symm, hus.ne,
      hxa.ne.symm, hane, (by simpa using hxk.ne),
      hau.symm, hxa.symm, (by simpa using hxk), hus.symm⟩).elim
  by_cases hk2 : k = 2
  · exact Or.inl hk2
  by_cases hk3 : k = 3
  · exact Or.inr hk3
  exfalso
  have hk4 : 4 ≤ k := by omega
  let q : G.Walk u v :=
    (((hau.symm.toWalk).append hxa.symm.toWalk).append hxk.toWalk).append (p.drop k)
  have hq : G.dist u v ≤ q.length := G.dist_le q
  have hdrop : (p.drop k).length = p.length - k := by simp [Walk.drop_length]
  simp only [q, Walk.length_append, Walk.length_cons, Walk.length_nil,
    zero_add] at hq
  rw [hdrop, ← hp] at hq
  omega

omit [Fintype V] [DecidableEq V] [Nonempty V] in
/-- Such a forward neighbour is not itself a vertex of the geodesic. -/
lemma forward_neighbor_not_mem_geodesic_support
    {G : SimpleGraph V} {u v a x : V} (p : G.Walk u v)
    (hp : p.length = G.dist u v) (hlen : 2 ≤ p.length)
    (hau : G.Adj a u) (hxa : G.Adj x a) (hxu : x ≠ u)
    (hane : a ≠ p.snd)
    (htri : G.CliqueFree 3) (hc4 : ¬HasC4 G) :
    x ∉ p.support := by
  intro hxmem
  obtain ⟨k, hkx, hklen⟩ := Walk.mem_support_iff_exists_getVert.mp hxmem
  subst x
  by_cases hk0 : k = 0
  · subst k
    exact hxu (by simp [Walk.getVert_zero])
  have hnil : ¬p.Nil := by
    simpa [Walk.not_nil_iff_lt_length] using (show 0 < p.length by omega)
  have hus : G.Adj u p.snd := p.adj_snd hnil
  by_cases hk1 : k = 1
  · subst k
    have hindep := G.isIndepSet_neighborSet_of_triangleFree htri u
    have hnot : ¬G.Adj a p.snd := by
      apply hindep
      · simpa [G.mem_neighborSet, adj_comm] using hau
      · simpa [G.mem_neighborSet] using hus
      · exact hane
    exact hnot (by simpa using hxa.symm)
  by_cases hk2 : k = 2
  · subst k
    have h01 : G.Adj u p.snd := hus
    have h12 : G.Adj p.snd (p.getVert 2) := by
      simpa using p.adj_getVert_succ (show 1 < p.length by omega)
    have hu2 : u ≠ p.getVert 2 := by
      have hpPath : p.IsPath := p.isPath_of_length_eq_dist hp
      intro heq
      have hidx : (0 : ℕ) = 2 := hpPath.getVert_injOn
        (by simp) (by simp; omega) (by simpa [Walk.getVert_zero] using heq)
      omega
    have ha2 : a ≠ p.getVert 2 := by
      intro heq
      exact hxa.ne heq.symm
    apply hc4
    refine ⟨u, a, p.getVert 2, p.snd, hau.ne.symm, hu2, h01.ne,
      ha2, hane, h12.ne.symm, hau.symm, ?_, h12.symm, h01.symm⟩
    exact hxa.symm
  have hk3 : 3 ≤ k := by omega
  let q : G.Walk u v := ((hau.symm.toWalk).append hxa.symm.toWalk).append (p.drop k)
  have hq : G.dist u v ≤ q.length := G.dist_le q
  have hdrop : (p.drop k).length = p.length - k := by simp [Walk.drop_length]
  simp only [q, Walk.length_append, Walk.length_cons, Walk.length_nil,
    zero_add] at hq
  rw [hdrop, ← hp] at hq
  omega

omit [Nonempty V] in
/-- Four fresh candidates whose geodesic contacts are confined to indices two
and three cannot all make contact in a cubic graph.  The available contact
slots are respectively `2`, `1+2`, and `1+1` when the geodesic length is
`2`, `3`, or at least `4`. -/
lemma exists_contact_free_of_four_candidates_of_cubic
    (G : SimpleGraph V) [DecidableRel G.Adj] {u v : V} (p : G.Walk u v)
    (hp : p.length = G.dist u v) (hlen : 2 ≤ p.length)
    (hreg : G.IsRegularOfDegree 3) (X : Finset V) (hXcard : X.card = 4)
    (hfresh : ∀ x ∈ X, x ∉ p.support)
    (hrestrict : ∀ x ∈ X, ∀ k, k ≤ p.length →
      G.Adj x (p.getVert k) → k = 2 ∨ k = 3) :
    ∃ x ∈ X, ∀ z ∈ p.support, ¬G.Adj x z := by
  classical
  have hpPath : p.IsPath := p.isPath_of_length_eq_dist hp
  have hget_ne : ∀ {i j : ℕ}, i ≤ p.length → j ≤ p.length → i ≠ j →
      p.getVert i ≠ p.getVert j := by
    intro i j hi hj hij heq
    exact hij (hpPath.getVert_injOn (by simpa) (by simpa) heq)
  have h12 : G.Adj (p.getVert 1) (p.getVert 2) := by
    simpa using p.adj_getVert_succ (show 1 < p.length by omega)
  have hsnd : p.getVert 1 = p.snd := by rfl
  by_contra hex
  push_neg at hex
  have hall : ∀ x ∈ X, ∃ k, k ≤ p.length ∧ G.Adj x (p.getVert k) := by
    intro x hx
    obtain ⟨z, hz, hxz⟩ := hex x hx
    obtain ⟨k, hkz, hklen⟩ := Walk.mem_support_iff_exists_getVert.mp hz
    refine ⟨k, hklen, ?_⟩
    simpa [hkz] using hxz
  rcases eq_or_lt_of_le hlen with hlen2 | hlen2
  · have hsub : X ⊆ (G.neighborFinset (p.getVert 2)).erase (p.getVert 1) := by
      intro x hx
      obtain ⟨k, hklen, hxk⟩ := hall x hx
      have hk : k = 2 := by
        rcases hrestrict x hx k hklen hxk with hk | hk
        · exact hk
        · omega
      subst k
      have hxne : x ≠ p.getVert 1 := by
        intro heq
        apply hfresh x hx
        rw [heq]
        exact Walk.getVert_mem_support p 1
      simp only [Finset.mem_erase, G.mem_neighborFinset]
      exact ⟨hxne, hxk.symm⟩
    have hmem1 : p.getVert 1 ∈ G.neighborFinset (p.getVert 2) := by
      simpa using h12.symm
    have hslot : ((G.neighborFinset (p.getVert 2)).erase (p.getVert 1)).card = 2 := by
      rw [Finset.card_erase_of_mem hmem1, G.card_neighborFinset_eq_degree,
        hreg (p.getVert 2)]
    have := Finset.card_le_card hsub
    rw [hXcard, hslot] at this
    omega
  have hlen3 : 3 ≤ p.length := by omega
  have h23 : G.Adj (p.getVert 2) (p.getVert 3) := by
    simpa using p.adj_getVert_succ (show 2 < p.length by omega)
  rcases eq_or_lt_of_le hlen3 with hlen3eq | hlen3lt
  · let S₂ := ((G.neighborFinset (p.getVert 2)).erase (p.getVert 1)).erase
        (p.getVert 3)
    let S₃ := (G.neighborFinset (p.getVert 3)).erase (p.getVert 2)
    have hsub : X ⊆ S₂ ∪ S₃ := by
      intro x hx
      obtain ⟨k, hklen, hxk⟩ := hall x hx
      rcases hrestrict x hx k hklen hxk with hk | hk
      · apply Finset.mem_union.mpr
        left
        subst k
        have hx1 : x ≠ p.getVert 1 := by
          intro heq; apply hfresh x hx; rw [heq]
          exact Walk.getVert_mem_support p 1
        have hx3 : x ≠ p.getVert 3 := by
          intro heq; apply hfresh x hx; rw [heq]
          exact Walk.getVert_mem_support p 3
        simp [S₂, hx1, hx3, hxk.symm]
      · apply Finset.mem_union.mpr
        right
        subst k
        have hx2 : x ≠ p.getVert 2 := by
          intro heq; apply hfresh x hx; rw [heq]
          exact Walk.getVert_mem_support p 2
        simp [S₃, hx2, hxk.symm]
    have hmem1 : p.getVert 1 ∈ G.neighborFinset (p.getVert 2) := by
      simpa using h12.symm
    have hne13 : p.getVert 1 ≠ p.getVert 3 :=
      hget_ne (by omega) (by omega) (by omega)
    have hmem3 : p.getVert 3 ∈
        (G.neighborFinset (p.getVert 2)).erase (p.getVert 1) := by
      simp [hne13.symm, h23]
    have hS₂ : S₂.card = 1 := by
      simp only [S₂]
      rw [Finset.card_erase_of_mem hmem3, Finset.card_erase_of_mem hmem1,
        G.card_neighborFinset_eq_degree, hreg (p.getVert 2)]
    have hmem2 : p.getVert 2 ∈ G.neighborFinset (p.getVert 3) := by
      simpa using h23.symm
    have hS₃ : S₃.card = 2 := by
      simp only [S₃]
      rw [Finset.card_erase_of_mem hmem2, G.card_neighborFinset_eq_degree,
        hreg (p.getVert 3)]
    have hcard := Finset.card_le_card hsub
    have hunion : (S₂ ∪ S₃).card ≤ S₂.card + S₃.card := Finset.card_union_le _ _
    rw [hXcard] at hcard
    rw [hS₂, hS₃] at hunion
    omega
  have hlen4 : 4 ≤ p.length := by omega
  have h34 : G.Adj (p.getVert 3) (p.getVert 4) := by
    simpa using p.adj_getVert_succ (show 3 < p.length by omega)
  let S₂ := ((G.neighborFinset (p.getVert 2)).erase (p.getVert 1)).erase
    (p.getVert 3)
  let S₃ := ((G.neighborFinset (p.getVert 3)).erase (p.getVert 2)).erase
    (p.getVert 4)
  have hsub : X ⊆ S₂ ∪ S₃ := by
    intro x hx
    obtain ⟨k, hklen, hxk⟩ := hall x hx
    rcases hrestrict x hx k hklen hxk with hk | hk
    · apply Finset.mem_union.mpr
      left
      subst k
      have hx1 : x ≠ p.getVert 1 := by
        intro heq; apply hfresh x hx; rw [heq]
        exact Walk.getVert_mem_support p 1
      have hx3 : x ≠ p.getVert 3 := by
        intro heq; apply hfresh x hx; rw [heq]
        exact Walk.getVert_mem_support p 3
      simp [S₂, hx1, hx3, hxk.symm]
    · apply Finset.mem_union.mpr
      right
      subst k
      have hx2 : x ≠ p.getVert 2 := by
        intro heq; apply hfresh x hx; rw [heq]
        exact Walk.getVert_mem_support p 2
      have hx4 : x ≠ p.getVert 4 := by
        intro heq; apply hfresh x hx; rw [heq]
        exact Walk.getVert_mem_support p 4
      simp [S₃, hx2, hx4, hxk.symm]
  have hmem1 : p.getVert 1 ∈ G.neighborFinset (p.getVert 2) := by
    simpa using h12.symm
  have hne13 : p.getVert 1 ≠ p.getVert 3 :=
    hget_ne (by omega) (by omega) (by omega)
  have hmem3 : p.getVert 3 ∈
      (G.neighborFinset (p.getVert 2)).erase (p.getVert 1) := by
    simp [hne13.symm, h23]
  have hS₂ : S₂.card = 1 := by
    simp only [S₂]
    rw [Finset.card_erase_of_mem hmem3, Finset.card_erase_of_mem hmem1,
      G.card_neighborFinset_eq_degree, hreg (p.getVert 2)]
  have hmem2 : p.getVert 2 ∈ G.neighborFinset (p.getVert 3) := by
    simpa using h23.symm
  have hne24 : p.getVert 2 ≠ p.getVert 4 :=
    hget_ne (by omega) (by omega) (by omega)
  have hmem4 : p.getVert 4 ∈
      (G.neighborFinset (p.getVert 3)).erase (p.getVert 2) := by
    simp [hne24.symm, h34]
  have hS₃ : S₃.card = 1 := by
    simp only [S₃]
    rw [Finset.card_erase_of_mem hmem4, Finset.card_erase_of_mem hmem2,
      G.card_neighborFinset_eq_degree, hreg (p.getVert 3)]
  have hcard := Finset.card_le_card hsub
  have hunion : (S₂ ∪ S₃).card ≤ S₂.card + S₃.card := Finset.card_union_le _ _
  rw [hXcard] at hcard
  rw [hS₂, hS₃] at hunion
  omega

omit [Fintype V] [DecidableEq V] [Nonempty V] in
/-- In the triangle-free branch, either off-direction neighbour of the head
is fresh and clean against the positive part of a geodesic. -/
lemma fresh_and_clean_off_neighbor_of_geodesic_triangleFree_c4Free
    {G : SimpleGraph V} {u v c : V} (p : G.Walk u v)
    (hp : p.length = G.dist u v) (hlen : 2 ≤ p.length)
    (hcu : G.Adj c u) (hcne : c ≠ p.snd)
    (htri : G.CliqueFree 3) (hc4 : ¬HasC4 G) :
    c ∉ p.support ∧ ∀ z ∈ p.support.tail, ¬G.Adj c z := by
  have hnil : ¬p.Nil := by
    simpa [Walk.not_nil_iff_lt_length] using (show 0 < p.length by omega)
  have hus : G.Adj u p.snd := p.adj_snd hnil
  have hcnot : ¬G.Adj c p.snd := by
    have hindep := G.isIndepSet_neighborSet_of_triangleFree htri u
    apply hindep
    · simpa [G.mem_neighborSet, adj_comm] using hcu
    · simpa [G.mem_neighborSet] using hus
    · exact hcne
  constructor
  · intro hcmem
    exact hcne (eq_snd_of_mem_support_of_adj_head_of_geodesic p hp hcmem hcu)
  · intro z hz
    have hinduced := isInducedPath_support_of_length_eq_dist p hp
    have hutail : u ∉ p.support.tail := by
      have hnodup := hinduced.1
      rw [p.support_eq_cons] at hnodup
      exact (List.nodup_cons.mp hnodup).1
    have hzmem : z ∈ p.support := by
      rw [p.support_eq_cons]
      exact List.mem_cons_of_mem u hz
    obtain ⟨k, hkz, hklen⟩ := Walk.mem_support_iff_exists_getVert.mp hzmem
    have hkpos : 1 ≤ k := by
      by_contra hk
      have hkzero : k = 0 := by omega
      subst k
      apply hutail
      have hzu : z = u := by simpa [Walk.getVert_zero] using hkz.symm
      simpa [hzu] using hz
    have hnot := not_adj_getVert_pos_of_geodesic_of_c4Free
      p hp hlen hc4 hcu hcne hcnot k hkpos hklen
    simpa [hkz] using hnot

omit [Nonempty V] in
/-- A length-at-least-two geodesic in the triangle-free cubic C4-free branch
admits a clean two-edge prepend, hence an induced list with three more
vertices than the walk length. -/
lemma exists_inducedPath_two_cons_support_of_geodesic_of_cubic_triangleFree_c4Free
    (G : SimpleGraph V) [DecidableRel G.Adj] {u v : V} (p : G.Walk u v)
    (hp : p.length = G.dist u v) (hlen : 2 ≤ p.length)
    (hreg : G.IsRegularOfDegree 3) (htri : G.CliqueFree 3)
    (hc4 : ¬HasC4 G) :
    ∃ x c : V, G.isInducedPath (x :: c :: p.support) ∧
      (x :: c :: p.support).length = p.length + 3 := by
  classical
  have hnil : ¬p.Nil := by
    simpa [Walk.not_nil_iff_lt_length] using (show 0 < p.length by omega)
  obtain ⟨a, b, hab, hau, hbu, hane, hbne, hnab⟩ :=
    exists_two_off_geodesic_neighbors_of_cubic_triangleFree G p hnil hreg htri
  obtain ⟨x₁, x₂, y₁, y₂, hcard, hx₁a, hx₂a, hy₁b, hy₂b,
      hx₁u, hx₂u, hy₁u, hy₂u⟩ :=
    exists_four_distinct_forward_neighbors_of_cubic_triangleFree_c4Free
      G hab hau hbu hnab hreg hc4
  let X : Finset V := {x₁, x₂, y₁, y₂}
  have hfresh : ∀ x ∈ X, x ∉ p.support := by
    intro x hx
    simp only [X, Finset.mem_insert, Finset.mem_singleton] at hx
    rcases hx with rfl | rfl | rfl | rfl
    · exact forward_neighbor_not_mem_geodesic_support
        p hp hlen hau hx₁a hx₁u hane htri hc4
    · exact forward_neighbor_not_mem_geodesic_support
        p hp hlen hau hx₂a hx₂u hane htri hc4
    · exact forward_neighbor_not_mem_geodesic_support
        p hp hlen hbu hy₁b hy₁u hbne htri hc4
    · exact forward_neighbor_not_mem_geodesic_support
        p hp hlen hbu hy₂b hy₂u hbne htri hc4
  have hrestrict : ∀ x ∈ X, ∀ k, k ≤ p.length →
      G.Adj x (p.getVert k) → k = 2 ∨ k = 3 := by
    intro x hx k hklen hxk
    simp only [X, Finset.mem_insert, Finset.mem_singleton] at hx
    rcases hx with rfl | rfl | rfl | rfl
    · exact forward_contact_index_eq_two_or_three
        p hp hau hx₁a hx₁u hane htri hc4 k hklen hxk
    · exact forward_contact_index_eq_two_or_three
        p hp hau hx₂a hx₂u hane htri hc4 k hklen hxk
    · exact forward_contact_index_eq_two_or_three
        p hp hbu hy₁b hy₁u hbne htri hc4 k hklen hxk
    · exact forward_contact_index_eq_two_or_three
        p hp hbu hy₂b hy₂u hbne htri hc4 k hklen hxk
  obtain ⟨x, hxX, hxclean⟩ :=
    exists_contact_free_of_four_candidates_of_cubic
      G p hp hlen hreg X (by simpa [X] using hcard) hfresh hrestrict
  have hbranch : ∃ c : V, G.Adj x c ∧ G.Adj c u ∧ c ≠ p.snd := by
    simp only [X, Finset.mem_insert, Finset.mem_singleton] at hxX
    rcases hxX with rfl | rfl | rfl | rfl
    · exact ⟨a, hx₁a, hau, hane⟩
    · exact ⟨a, hx₂a, hau, hane⟩
    · exact ⟨b, hy₁b, hbu, hbne⟩
    · exact ⟨b, hy₂b, hbu, hbne⟩
  obtain ⟨c, hxc, hcu, hcne⟩ := hbranch
  obtain ⟨hcfresh, hcclean⟩ :=
    fresh_and_clean_off_neighbor_of_geodesic_triangleFree_c4Free
      p hp hlen hcu hcne htri hc4
  have hcpath : G.isInducedPath (c :: p.support) := by
    rw [p.support_eq_cons]
    apply isInducedPath_cons_of_adj_head_of_not_adj_tail
    · simpa [← p.support_eq_cons] using isInducedPath_support_of_length_eq_dist p hp
    · exact hcu
    · simpa [← p.support_eq_cons] using hcfresh
    · exact hcclean
  refine ⟨x, c, ?_, by simp [p.length_support]⟩
  apply isInducedPath_cons_of_adj_head_of_not_adj_tail hcpath hxc
  · simp only [List.mem_cons, not_or]
    exact ⟨hxc.ne, hfresh x (by simpa [X] using hxX)⟩
  · exact hxclean

/-- The two-edge extension supplies the path inequality needed by the
triangle-free branch of the cubic C4-free specialization. -/
lemma radius_add_three_le_path_of_cubic_triangleFree_c4Free
    (G : SimpleGraph V) [DecidableRel G.Adj] (hconn : G.Connected)
    (hreg : G.IsRegularOfDegree 3) (htri : G.CliqueFree 3)
    (hc4 : ¬HasC4 G) :
    G.radius.toNat + 3 ≤ path G := by
  obtain ⟨u, v, p, hpDist, hpLength, _hpInduced, _hpSupport⟩ :=
    exists_radius_geodesic_support_with_dist G hconn
  have hlen : 2 ≤ p.length := by
    rw [hpLength]
    exact two_le_radius_toNat_of_cubic_c4Free G hconn hreg hc4
  obtain ⟨x, c, hxcInduced, hxcLength⟩ :=
    exists_inducedPath_two_cons_support_of_geodesic_of_cubic_triangleFree_c4Free
      G p hpDist hlen hreg htri hc4
  rw [← hpLength, ← hxcLength]
  exact path_ge_of_isInducedPath G (x :: c :: p.support) hxcInduced

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
