import FormalConjecturesUtil

/-!
# WOWII 61: reusable forest-augmentation lemmas

This file formalizes the cycle-theoretic core of the safe three-separated
augmentation argument recorded in `results/expansion/method_v03_61_proof.md`.
It deliberately does not claim the open denominator-three conjecture.
-/

namespace WrittenOnTheWallII.GraphConjecture61Partial

open SimpleGraph

variable {V : Type*} {G : SimpleGraph V}

/-- A finite interval with no two consecutive unmarked positions contains a
three-separated marked set large enough to certify the quarter bound.

The conclusion is written as `D ≤ 4 * S.card`, which is the exact natural
number form needed to infer `ceil (D / 4) ≤ S.card`. -/
theorem exists_threeSeparated_marked_set
    (A : ℕ → Prop) (D : ℕ)
    (hhit : ∀ i, i < D → A i ∨ A (i + 1)) :
    ∃ S : Finset ℕ,
      (∀ i ∈ S, i ≤ D ∧ A i) ∧
      (∀ i ∈ S, ∀ j ∈ S, i ≠ j → 3 ≤ i.dist j) ∧
      D ≤ 4 * S.card := by
  classical
  induction D using Nat.strong_induction_on generalizing A with
  | h D ih =>
      by_cases hD : D = 0
      · subst D
        exact ⟨∅, by simp⟩
      let x := if A 0 then 0 else 1
      have hx_le_one : x ≤ 1 := by simp [x]; split <;> omega
      have hxA : A x := by
        simp only [x]
        split
        · assumption
        · exact (hhit 0 (Nat.pos_of_ne_zero hD)).resolve_left (by assumption)
      have hxD : x ≤ D := le_trans hx_le_one (Nat.one_le_iff_ne_zero.mpr hD)
      by_cases hsmall : D ≤ 4
      · refine ⟨{x}, ?_, ?_, ?_⟩
        · simp [hxD, hxA]
        · simp
        · simpa using hsmall
      · let shift := x + 3
        let D' := D - shift
        have hshiftD : shift < D := by
          dsimp [shift]
          omega
        have hD'D : D' < D := by
          dsimp [D']
          omega
        have hdecomp : D' + shift = D := by
          dsimp [D']
          exact Nat.sub_add_cancel hshiftD.le
        have hhit' : ∀ i, i < D' → A (i + shift) ∨ A (i + 1 + shift) := by
          intro i hi
          have his : i + shift < D := by
            dsimp [D'] at hi
            omega
          have := hhit (i + shift) his
          simpa [Nat.add_assoc, Nat.add_left_comm, Nat.add_comm] using this
        obtain ⟨S, hS_bound, hS_sep, hS_card⟩ :=
          ih D' hD'D (fun i ↦ A (i + shift)) hhit'
        let f : ℕ → ℕ := fun i ↦ i + shift
        let T : Finset ℕ := insert x (S.image f)
        have hxf : x ∉ S.image f := by
          intro hxmem
          obtain ⟨i, hiS, hix⟩ := Finset.mem_image.mp hxmem
          dsimp [f, shift] at hix
          omega
        refine ⟨T, ?_, ?_, ?_⟩
        · intro i hiT
          simp only [T, Finset.mem_insert, Finset.mem_image] at hiT
          rcases hiT with rfl | ⟨j, hjS, rfl⟩
          · exact ⟨hxD, hxA⟩
          · have hj := hS_bound j hjS
            dsimp [f] at hj ⊢
            constructor
            · omega
            · exact hj.2
        · intro i hiT j hjT hij
          simp only [T, Finset.mem_insert, Finset.mem_image] at hiT hjT
          rcases hiT with rfl | ⟨a, haS, rfl⟩ <;>
            rcases hjT with rfl | ⟨b, hbS, rfl⟩
          · exact (hij rfl).elim
          · dsimp [f, shift]
            unfold Nat.dist
            omega
          · dsimp [f, shift]
            unfold Nat.dist
            omega
          · have hab : a ≠ b := by
              intro hab
              apply hij
              simp [hab]
            simpa only [f, Nat.dist_add_add_right] using hS_sep a haS b hbS hab
        · have hcard_image : (S.image f).card = S.card := by
            rw [Finset.card_image_iff.mpr]
            intro a _ b _ hab
            dsimp [f] at hab
            omega
          have hcardT : T.card = S.card + 1 := by
            dsimp [T]
            rw [Finset.card_insert_of_notMem hxf, hcard_image]
          dsimp [D', shift] at hS_card
          rw [hcardT]
          omega

/-- Counting half of the safe augmentation argument. Along any walk, an
independent set cannot contain two consecutive walk vertices. Consequently
the walk indices outside the independent set contain a three-separated
subcollection `S` satisfying `p.length ≤ 4 * S.card`.

For a geodesic, the selected indices correspond to mutually distance-at-least
three vertices; that metric bridge is intentionally kept separate from this
pure counting statement. -/
theorem exists_threeSeparated_indices_outside_independent
    {u v : V} (p : G.Walk u v) (I : Set V) (hI : G.IsIndepSet I) :
    ∃ S : Finset ℕ,
      (∀ i ∈ S, i ≤ p.length ∧ p.getVert i ∉ I) ∧
      (∀ i ∈ S, ∀ j ∈ S, i ≠ j → 3 ≤ i.dist j) ∧
      p.length ≤ 4 * S.card := by
  apply exists_threeSeparated_marked_set (fun i ↦ p.getVert i ∉ I) p.length
  intro i hi
  by_cases hiI : p.getVert i ∈ I
  · right
    intro hi1I
    have hadj : G.Adj (p.getVert i) (p.getVert (i + 1)) :=
      p.adj_getVert_succ hi
    exact hI hiI hi1I hadj.ne hadj
  · exact Or.inl hiI

/-- Indices on a shortest walk measure their exact graph distance. This is the
metric bridge from the counting lemma's index separation to the augmentation
lemma's graph-distance separation. -/
theorem dist_getVert_eq_natDist_of_length_eq_dist
    {u v : V} (p : G.Walk u v) (hp : p.length = G.dist u v)
    {i j : ℕ} (hi : i ≤ p.length) (hj : j ≤ p.length) :
    G.dist (p.getVert i) (p.getVert j) = i.dist j := by
  have hordered : ∀ {a b : ℕ}, a ≤ b → b ≤ p.length →
      G.dist (p.getVert a) (p.getVert b) = b - a := by
    intro a b hab hb
    let q := (p.drop a).take (b - a)
    have hqsub : q.IsSubwalk p := by
      exact (Walk.isSubwalk_take (p.drop a) (b - a)).trans
        (Walk.isSubwalk_drop p a)
    have hshort := length_eq_dist_of_subwalk hp hqsub
    have hqlen : q.length = b - a := by
      dsimp [q]
      simp only [Walk.take_length, Walk.drop_length]
      rw [Nat.min_eq_left]
      omega
    have hqend : (p.drop a).getVert (b - a) = p.getVert b := by
      rw [Walk.drop_getVert]
      congr 1
      omega
    rw [hqlen, hqend] at hshort
    exact hshort.symm
  rcases le_total i j with hij | hji
  · rw [Nat.dist_eq_sub_of_le hij]
    exact hordered hij hj
  · rw [Nat.dist_comm, SimpleGraph.dist_comm]
    rw [Nat.dist_eq_sub_of_le hji]
    exact hordered hji hi

/-- A bipartition in which every vertex on the left has at most one neighbour
on the right is acyclic.  This is the graph-theoretic core of the safe
augmentation lemma: the residue-sized set is the left side and the selected
geodesic vertices are the right side. -/
theorem isAcyclic_of_independent_parts_of_left_unique_neighbor
    (I X : Set V)
    (hcover : I ∪ X = Set.univ)
    (hI : G.IsIndepSet I)
    (hX : G.IsIndepSet X)
    (huniq : ∀ i ∈ I, ∀ x ∈ X, ∀ y ∈ X,
      G.Adj i x → G.Adj i y → x = y) :
    G.IsAcyclic := by
  intro v p hp
  have hlen : 3 ≤ p.length := hp.three_le_length
  have hvs : G.Adj v p.snd := p.adj_snd hp.not_nil
  have hvp : G.Adj v p.penultimate := (p.adj_penultimate hp.not_nil).symm
  have hv_mem : v ∈ I ∨ v ∈ X := by
    have : v ∈ I ∪ X := by rw [hcover]; trivial
    simpa only [Set.mem_union] using this
  rcases hv_mem with hvI | hvX
  · have hsX : p.snd ∈ X := by
      have hs : p.snd ∈ I ∨ p.snd ∈ X := by
        have : p.snd ∈ I ∪ X := by rw [hcover]; trivial
        simpa only [Set.mem_union] using this
      exact hs.resolve_left (fun hsI ↦ hI hvI hsI hvs.ne hvs)
    have hpX : p.penultimate ∈ X := by
      have hpen : p.penultimate ∈ I ∨ p.penultimate ∈ X := by
        have : p.penultimate ∈ I ∪ X := by rw [hcover]; trivial
        simpa only [Set.mem_union] using this
      exact hpen.resolve_left (fun hpI ↦ hI hvI hpI hvp.ne hvp)
    exact hp.snd_ne_penultimate (huniq v hvI p.snd hsX p.penultimate hpX hvs hvp)
  · have hsI : p.snd ∈ I := by
      have hs : p.snd ∈ I ∨ p.snd ∈ X := by
        have : p.snd ∈ I ∪ X := by rw [hcover]; trivial
        simpa only [Set.mem_union] using this
      exact hs.resolve_right (fun hsX ↦ hX hvX hsX hvs.ne hvs)
    have h12 : G.Adj p.snd (p.getVert 2) := by
      simpa using p.adj_getVert_succ (by omega : 1 < p.length)
    have h2X : p.getVert 2 ∈ X := by
      have h2 : p.getVert 2 ∈ I ∨ p.getVert 2 ∈ X := by
        have : p.getVert 2 ∈ I ∪ X := by rw [hcover]; trivial
        simpa only [Set.mem_union] using this
      exact h2.resolve_left (fun h2I ↦ hI hsI h2I h12.ne h12)
    have hv_ne_h2 : v ≠ p.getVert 2 := by
      simpa using hp.getVert_sub_one_ne_getVert_add_one (i := 1) (by omega : 1 ≤ p.length)
    exact hv_ne_h2 (huniq p.snd hsI v hvX (p.getVert 2) h2X hvs.symm h12)

/-- Induced-subgraph form of
`isAcyclic_of_independent_parts_of_left_unique_neighbor`. -/
theorem induce_union_isAcyclic_of_left_unique_neighbor
    (I X : Set V)
    (hI : G.IsIndepSet I)
    (hX : G.IsIndepSet X)
    (huniq : ∀ i ∈ I, ∀ x ∈ X, ∀ y ∈ X,
      G.Adj i x → G.Adj i y → x = y) :
    (G.induce (I ∪ X)).IsAcyclic := by
  let I' : Set ↑(I ∪ X) := {v | (v : V) ∈ I}
  let X' : Set ↑(I ∪ X) := {v | (v : V) ∈ X}
  apply isAcyclic_of_independent_parts_of_left_unique_neighbor I' X'
  · ext v
    simp only [I', X', Set.mem_union, Set.mem_setOf_eq, Set.mem_univ, iff_true]
    exact v.property
  · intro u hu v hv huv hadj
    apply hI hu hv
    · intro hcoe
      exact huv (Subtype.ext hcoe)
    · exact SimpleGraph.induce_adj.mp hadj
  · intro u hu v hv huv hadj
    apply hX hu hv
    · intro hcoe
      exact huv (Subtype.ext hcoe)
    · exact SimpleGraph.induce_adj.mp hadj
  · intro i hi x hx y hy hix hiy
    apply Subtype.ext
    exact huniq i hi x hx y hy (SimpleGraph.induce_adj.mp hix)
      (SimpleGraph.induce_adj.mp hiy)

/-- **Safe three-separated augmentation.** If `I` is independent and the
vertices of `X` are mutually at graph distance at least three, then the graph
induced by `I ∪ X` is a forest.

This is the augmentation half of the rigorous denominator-four route for
WOWII 61.  A three-separated subset of a geodesic satisfies the distance
hypothesis because every subpath of a geodesic is shortest. -/
theorem safe_threeSeparated_augmentation
    (hconn : G.Connected)
    (I X : Set V)
    (hI : G.IsIndepSet I)
    (hsep : ∀ x ∈ X, ∀ y ∈ X, x ≠ y → 3 ≤ G.dist x y) :
    (G.induce (I ∪ X)).IsAcyclic := by
  apply induce_union_isAcyclic_of_left_unique_neighbor I X hI
  · intro x hx y hy hxy hxy_adj
    have hdist : G.dist x y = 1 := dist_eq_one_iff_adj.mpr hxy_adj
    have := hsep x hx y hy hxy
    omega
  · intro i hi x hx y hy hix hiy
    by_contra hxy
    have hdist_xy : G.dist x y ≤ 2 := by
      calc
        G.dist x y ≤ G.dist x i + G.dist i y := hconn.dist_triangle
        _ = 2 := by rw [dist_eq_one_iff_adj.mpr hix.symm,
          dist_eq_one_iff_adj.mpr hiy]
    exact (by omega : ¬ 3 ≤ G.dist x y) (hsep x hx y hy hxy)

section Finite

variable [Fintype V] [DecidableEq V]

/-- The Havel--Hakimi residue never exceeds the length of the degree list.
This is the elementary size invariant needed at the terminal (edgeless) case
of any future Maxine induction. -/
theorem residueAux_le_length (s : List ℕ) : residueAux s ≤ s.length := by
  induction s using residueAux.induct with
  | case1 => simp [residueAux]
  | case2 s => simp only [residueAux.eq_2, List.length_cons]; omega
  | case3 d rest hd ih =>
      rw [residueAux.eq_3 d rest hd]
      calc
        residueAux (havelHakimiStep (d :: rest))
            ≤ (havelHakimiStep (d :: rest)).length := ih
        _ = rest.length := havelHakimiStep_length_cons d rest
        _ ≤ (d :: rest).length := by simp

omit [DecidableEq V] in
/-- In particular, graph residue is bounded by the vertex count. -/
theorem residue_le_card [DecidableRel G.Adj] : residue G ≤ Fintype.card V := by
  unfold residue
  refine (residueAux_le_length _).trans_eq ?_
  simp

omit [DecidableEq V] in
/-- The realization-level residue bridge is equivalent to the numerical
inequality `residue G ≤ indepNum G`.  The forward implication uses any
residue-sized witness; the reverse implication takes a subset of a maximum
independent set.  This isolates the genuinely missing Griggs--Kleitman
theorem from finite-set selection bookkeeping. -/
theorem exists_independent_card_eq_residue_iff_le_indepNum
    [DecidableRel G.Adj] :
    (∃ I : Finset V, G.IsIndepSet (I : Set V) ∧ I.card = residue G) ↔
      residue G ≤ G.indepNum := by
  constructor
  · rintro ⟨I, hI, hcard⟩
    rw [← hcard]
    exact hI.card_le_indepNum
  · intro hres
    obtain ⟨M, hM⟩ := G.exists_isNIndepSet_indepNum
    obtain ⟨I, hIM, hIcard⟩ :=
      Finset.exists_subset_card_eq (hres.trans_eq hM.card_eq.symm)
    refine ⟨I, hM.isIndepSet.mono ?_, hIcard⟩
    exact_mod_cast hIM

omit [DecidableEq V] in
/-- Convenient witness-producing form of the reverse direction above. -/
theorem exists_independent_card_eq_residue_of_le_indepNum
    [DecidableRel G.Adj] (hres : residue G ≤ G.indepNum) :
    ∃ I : Finset V, G.IsIndepSet (I : Set V) ∧ I.card = residue G :=
  exists_independent_card_eq_residue_iff_le_indepNum.mpr hres

omit [DecidableEq V] in
/-- Terminal Maxine case: if the whole vertex set is independent, a
residue-sized independent set can be selected directly. -/
theorem exists_independent_card_eq_residue_of_univ_independent
    [DecidableRel G.Adj] (hG : G.IsIndepSet (Set.univ : Set V)) :
    ∃ I : Finset V, G.IsIndepSet (I : Set V) ∧ I.card = residue G := by
  have hcard : residue G ≤ (Finset.univ : Finset V).card := by
    simpa using (residue_le_card (G := G))
  obtain ⟨I, _hIuniv, hIcard⟩ := Finset.exists_subset_card_eq hcard
  have hsub : (I : Set V) ⊆ (Set.univ : Set V) := Set.subset_univ _
  exact ⟨I, hG.mono hsub, hIcard⟩

omit [DecidableEq V] in
/-- Any explicit induced forest supplies a lower bound for the project's
`largestInducedForestSize` definition. -/
theorem card_le_largestInducedForestSize
    (S : Finset V) (hS : (G.induce S).IsAcyclic) :
    S.card ≤ G.largestInducedForestSize := by
  unfold SimpleGraph.largestInducedForestSize
  apply le_csSup
  · exact ⟨Fintype.card V, fun n hn ↦ by
      obtain ⟨T, -, rfl⟩ := hn
      exact T.card_le_univ⟩
  · exact ⟨S, hS, rfl⟩

/-- Finite cardinal form of safe three-separated augmentation. The explicit
disjointness hypothesis turns the forest witness's union size into the sum of
the two contributions. -/
theorem add_card_le_largestInducedForestSize_of_threeSeparated
    (hconn : G.Connected)
    (I X : Finset V)
    (hdisj : Disjoint I X)
    (hI : G.IsIndepSet (I : Set V))
    (hsep : ∀ x ∈ X, ∀ y ∈ X, x ≠ y → 3 ≤ G.dist x y) :
    I.card + X.card ≤ G.largestInducedForestSize := by
  rw [← Finset.card_union_of_disjoint hdisj]
  apply card_le_largestInducedForestSize (I ∪ X)
  have hset : (↑(I ∪ X) : Set V) = (I : Set V) ∪ (X : Set V) := by
    ext v
    simp
  rw [hset]
  exact safe_threeSeparated_augmentation hconn (I : Set V) (X : Set V) hI hsep

/-- Fully composed geodesic augmentation package. Given an independent set
`I` and a shortest walk `p`, it constructs a disjoint finite set `X` outside
`I` such that `I ∪ X` is an induced forest and `X` certifies the exact
quarter count. -/
theorem exists_geodesic_augmentation
    (hconn : G.Connected)
    {u v : V} (p : G.Walk u v) (hp : p.length = G.dist u v)
    (I : Finset V) (hI : G.IsIndepSet (I : Set V)) :
    ∃ X : Finset V,
      Disjoint I X ∧
      p.length ≤ 4 * X.card ∧
      I.card + X.card ≤ G.largestInducedForestSize := by
  obtain ⟨S, hS_bound, hS_sep, hS_card⟩ :=
    exists_threeSeparated_indices_outside_independent p (I : Set V) hI
  let X : Finset V := S.image p.getVert
  have hpPath : p.IsPath := p.isPath_of_length_eq_dist hp
  have himage : X.card = S.card := by
    dsimp [X]
    rw [Finset.card_image_iff.mpr]
    intro i hiS j hjS hij
    have hi := (hS_bound i hiS).1
    have hj := (hS_bound j hjS).1
    exact hpPath.getVert_injOn hi hj hij
  have hdisj : Disjoint I X := by
    rw [Finset.disjoint_left]
    intro x hxI hxX
    obtain ⟨i, hiS, rfl⟩ := Finset.mem_image.mp hxX
    exact (hS_bound i hiS).2 hxI
  refine ⟨X, hdisj, ?_, ?_⟩
  · simpa [himage] using hS_card
  · apply add_card_le_largestInducedForestSize_of_threeSeparated
      hconn I X hdisj hI
    intro x hxX y hyX hxy
    obtain ⟨i, hiS, rfl⟩ := Finset.mem_image.mp hxX
    obtain ⟨j, hjS, rfl⟩ := Finset.mem_image.mp hyX
    have hij : i ≠ j := by
      intro hij
      exact hxy (congrArg p.getVert hij)
    rw [dist_getVert_eq_natDist_of_length_eq_dist p hp
      (hS_bound i hiS).1 (hS_bound j hjS).1]
    exact hS_sep i hiS j hjS hij

/-- Exact conditional residue package. If a residue-sized independent set and
a diametral shortest walk have already been supplied, the formalized
augmentation machinery produces the denominator-four witness. The missing
unconditional residue-to-independent-set theorem is deliberately an explicit
hypothesis. -/
theorem exists_residue_quarter_witness_of_certificates
    [DecidableRel G.Adj]
    (hconn : G.Connected)
    {u v : V} (p : G.Walk u v)
    (hp : p.length = G.dist u v)
    (hpdiam : p.length = G.diam)
    (I : Finset V) (hI : G.IsIndepSet (I : Set V))
    (hIcard : I.card = residue G) :
    ∃ X : Finset V,
      G.diam ≤ 4 * X.card ∧
      residue G + X.card ≤ G.largestInducedForestSize := by
  obtain ⟨X, _hdisj, hquarter, hforest⟩ :=
    exists_geodesic_augmentation hconn p hp I hI
  refine ⟨X, ?_, ?_⟩
  · rwa [← hpdiam]
  · rwa [← hIcard]

/-- The diametral-geodesic certificate required above always exists in a
finite connected nonempty graph. Thus the only remaining explicit premise is
the residue-sized independent set. -/
theorem exists_residue_quarter_witness_of_independent_set
    [Nonempty V] [DecidableRel G.Adj]
    (hconn : G.Connected)
    (I : Finset V) (hI : G.IsIndepSet (I : Set V))
    (hIcard : I.card = residue G) :
    ∃ X : Finset V,
      G.diam ≤ 4 * X.card ∧
      residue G + X.card ≤ G.largestInducedForestSize := by
  obtain ⟨u, v, huv⟩ := G.exists_dist_eq_diam
  obtain ⟨p, hp⟩ := hconn.exists_walk_length_eq_dist u v
  exact exists_residue_quarter_witness_of_certificates
    hconn p hp (hp.trans huv) I hI hIcard

/-- Numerical interface to the quarter theorem.  Once the classical
Griggs--Kleitman inequality `residue G ≤ indepNum G` is available, the exact
residue-sized independent set is selected automatically and all remaining
geodesic/forest construction is discharged by the preceding development. -/
theorem exists_residue_quarter_witness_of_residue_le_indepNum
    [Nonempty V] [DecidableRel G.Adj]
    (hconn : G.Connected) (hres : residue G ≤ G.indepNum) :
    ∃ X : Finset V,
      G.diam ≤ 4 * X.card ∧
      residue G + X.card ≤ G.largestInducedForestSize := by
  obtain ⟨I, hI, hIcard⟩ :=
    exists_independent_card_eq_residue_of_le_indepNum (G := G) hres
  exact exists_residue_quarter_witness_of_independent_set
    hconn I hI hIcard

end Finite

end WrittenOnTheWallII.GraphConjecture61Partial
