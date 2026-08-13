import GraphConjecture183GammaThree

/-!
# WOWII 183: the connected-domination-four tier

This file formalizes the multi-vertex augmentation theorem from
`results/expansion/method_v04_183_multiext.md`.
-/

namespace WrittenOnTheWallII.GraphConjecture183GammaFour

open SimpleGraph Finset

variable {V : Type*} [Fintype V] [DecidableEq V]

omit [Fintype V] in
private lemma insert_two_anticomplete_isBipartite
    (G : SimpleGraph V) (P : Finset V) (r s : V) (cP : V → Fin 2)
    (hrs : r ≠ s) (hrP : r ∉ P) (hsP : s ∉ P)
    (hPcolor : ∀ u ∈ P, ∀ w ∈ P, G.Adj u w → cP u ≠ cP w)
    (hrAnti : ∀ u ∈ P, ¬G.Adj r u)
    (hsAnti : ∀ u ∈ P, ¬G.Adj s u) :
    (G.induce (↑(insert r (insert s P)) : Set V)).IsBipartite := by
  classical
  let c : V → Fin 2 := fun u ↦
    if u = r then 0 else if u = s then (if G.Adj r s then 1 else 0) else cP u
  rw [induce_isBipartite_iff_exists_coloring]
  refine ⟨c, ?_⟩
  intro u hu w hw huw
  simp only [mem_insert] at hu hw
  rcases hu with rfl | rfl | hu <;> rcases hw with rfl | rfl | hw
  · exact (G.loopless _ huw).elim
  · simp [c, hrs.symm, huw]
  · exact (hrAnti w hw huw).elim
  · simp [c, hrs.symm, huw.symm]
  · exact (G.loopless _ huw).elim
  · exact (hsAnti w hw huw).elim
  · exact (hrAnti u hu huw.symm).elim
  · exact (hsAnti u hu huw.symm).elim
  · have hur : u ≠ r := fun h ↦ hrP (h ▸ hu)
    have hus : u ≠ s := fun h ↦ hsP (h ▸ hu)
    have hwr : w ≠ r := fun h ↦ hrP (h ▸ hw)
    have hws : w ≠ s := fun h ↦ hsP (h ▸ hw)
    simpa [c, hur, hus, hwr, hws] using hPcolor u hu w hw huw

omit [Fintype V] in
private lemma induce_three_connected_of_path
    (G : SimpleGraph V) {p q r : V} (hpq : G.Adj p q) (hqr : G.Adj q r) :
    (G.induce (↑({p, q, r} : Finset V) : Set V)).Connected := by
  let D : Finset V := {p, q, r}
  letI : Nonempty (↑D : Set V) := ⟨⟨q, by simp [D]⟩⟩
  constructor
  intro u v
  have hu : u.1 = p ∨ u.1 = q ∨ u.1 = r := by simpa [D] using u.2
  have hv : v.1 = p ∨ v.1 = q ∨ v.1 = r := by simpa [D] using v.2
  rcases hu with hu | hu | hu <;> rcases hv with hv | hv | hv
  · have huv : u = v := Subtype.ext (hu.trans hv.symm)
    subst v
    exact .rfl
  · apply Adj.reachable
    change G.Adj u.1 v.1
    simpa [hu, hv] using hpq
  · apply Reachable.trans (v := ⟨q, by simp⟩)
    · apply Adj.reachable
      change G.Adj u.1 q
      simpa [hu] using hpq
    · apply Adj.reachable
      change G.Adj q v.1
      simpa [hv] using hqr
  · apply Adj.reachable
    change G.Adj u.1 v.1
    simpa [hu, hv] using hpq.symm
  · have huv : u = v := Subtype.ext (hu.trans hv.symm)
    subst v
    exact .rfl
  · apply Adj.reachable
    change G.Adj u.1 v.1
    simpa [hu, hv] using hqr
  · apply Reachable.trans (v := ⟨q, by simp⟩)
    · apply Adj.reachable
      change G.Adj u.1 q
      simpa [hu] using hqr.symm
    · apply Adj.reachable
      change G.Adj q v.1
      simpa [hv] using hpq.symm
  · apply Adj.reachable
    change G.Adj u.1 v.1
    simpa [hu, hv] using hqr.symm
  · have huv : u = v := Subtype.ext (hu.trans hv.symm)
    subst v
    exact .rfl

omit [Fintype V] in
private lemma endpoint_leaf_forces_connected_dominating_triple
    (G : SimpleGraph V) {x a d z y : V}
    (hdist : G.dist x z = 3)
    (hxa : G.Adj x a) (had : G.Adj a d) (hdz : G.Adj d z)
    (hyP : y ∉ ({x, a, d, z} : Finset V))
    (hyx : G.Adj y x) (hya : ¬G.Adj y a) (hyd : ¬G.Adj y d)
    (hyz : ¬G.Adj y z)
    (hnoSix : ∀ S : Finset V, S.card = 6 →
      ¬(G.induce (↑S : Set V)).IsBipartite) :
    ∃ D : Finset V, D.card = 3 ∧ G.IsConnectedDominating (↑D : Set V) := by
  classical
  let P : Finset V := {x, a, d, z}
  let A : Finset V := {x, d}
  let B : Finset V := insert y P
  have hxd : ¬G.Adj x d := by
    intro h
    have hle := G.dist_le (h.toWalk.append hdz.toWalk)
    simp only [Walk.length_append, Walk.length_cons, Walk.length_nil,
      zero_add] at hle
    omega
  have hxz : ¬G.Adj x z := by
    intro h
    have hle := G.dist_le h.toWalk
    simp only [Walk.length_cons, Walk.length_nil, zero_add] at hle
    omega
  have haz : ¬G.Adj a z := by
    intro h
    have hle := G.dist_le (hxa.toWalk.append h.toWalk)
    simp only [Walk.length_append, Walk.length_cons, Walk.length_nil,
      zero_add] at hle
    omega
  have hPcard : P.card = 4 := by
    have hxa_ne : x ≠ a := hxa.ne
    have had_ne : a ≠ d := had.ne
    have hdz_ne : d ≠ z := hdz.ne
    have hxd_ne : x ≠ d := by
      intro h
      subst d
      exact hxz hdz
    have hxz_ne : x ≠ z := by
      intro h
      subst z
      simp at hdist
    have haz_ne : a ≠ z := by
      intro h
      subst z
      exact hxz hxa
    simp [P, hxa_ne, had_ne, hdz_ne, hxd_ne, hxz_ne, haz_ne]
  let cP : V → Fin 2 := fun u ↦ if u ∈ A then 0 else 1
  have hPcolor : ∀ u ∈ P, ∀ w ∈ P, G.Adj u w → cP u ≠ cP w := by
    intro u hu w hw huw heq
    have huP : u = x ∨ u = a ∨ u = d ∨ u = z := by
      simpa only [P, mem_insert, mem_singleton] using hu
    have hwP : w = x ∨ w = a ∨ w = d ∨ w = z := by
      simpa only [P, mem_insert, mem_singleton] using hw
    by_cases huA : u ∈ A
    · have hwA : w ∈ A := by
        by_contra hn
        simp [cP, huA, hn] at heq
      have huPair : u = x ∨ u = d := by simpa [A] using huA
      have hwPair : w = x ∨ w = d := by simpa [A] using hwA
      rcases huPair with rfl | rfl <;> rcases hwPair with rfl | rfl
      · exact G.loopless _ huw
      · exact hxd huw
      · exact hxd huw.symm
      · exact G.loopless _ huw
    · have hwA : w ∉ A := by
        intro hwA
        simp [cP, huA, hwA] at heq
      have huPair : u = a ∨ u = z := by
        rcases huP with rfl | rfl | rfl | rfl
        · exact (huA (by simp [A])).elim
        · exact Or.inl rfl
        · exact (huA (by simp [A])).elim
        · exact Or.inr rfl
      have hwPair : w = a ∨ w = z := by
        rcases hwP with rfl | rfl | rfl | rfl
        · exact (hwA (by simp [A])).elim
        · exact Or.inl rfl
        · exact (hwA (by simp [A])).elim
        · exact Or.inr rfl
      rcases huPair with rfl | rfl <;> rcases hwPair with rfl | rfl
      · exact G.loopless _ huw
      · exact haz huw
      · exact haz huw.symm
      · exact G.loopless _ huw
  let c : V → Fin 2 := fun u ↦ if u = y then 1 else cP u
  have hBcolor : ∀ u ∈ B, ∀ w ∈ B, G.Adj u w → c u ≠ c w := by
    intro u hu w hw huw
    simp only [B, mem_insert] at hu hw
    rcases hu with rfl | hu <;> rcases hw with rfl | hw
    · exact (G.loopless _ huw).elim
    · have hwCases : w = x ∨ w = a ∨ w = d ∨ w = z := by
        simpa only [P, mem_insert, mem_singleton] using hw
      have hwx : w = x := by
        rcases hwCases with rfl | rfl | rfl | rfl
        · rfl
        · exact (hya huw).elim
        · exact (hyd huw).elim
        · exact (hyz huw).elim
      subst w
      simp [c, cP, A, huw.ne.symm]
    · have huCases : u = x ∨ u = a ∨ u = d ∨ u = z := by
        simpa only [P, mem_insert, mem_singleton] using hu
      have hux : u = x := by
        rcases huCases with rfl | rfl | rfl | rfl
        · rfl
        · exact (hya huw.symm).elim
        · exact (hyd huw.symm).elim
        · exact (hyz huw.symm).elim
      subst u
      simp [c, cP, A, huw.ne]
    · have huy : u ≠ y := by
        intro h
        subst u
        exact hyP hu
      have hwy : w ≠ y := by
        intro h
        subst w
        exact hyP hw
      simpa [c, huy, hwy] using hPcolor u hu w hw huw
  have hBcard : B.card = 5 := by
    rw [show B = insert y P by rfl, card_insert_of_notMem (by simpa [P] using hyP), hPcard]
  have houtside : ∀ v, v ∉ B → G.Adj v x ∨ G.Adj v d := by
    intro v hvB
    by_contra hv
    push_neg at hv
    let c' : V → Fin 2 := fun u ↦ if u = v then 0 else c u
    have hSixBip : (G.induce (↑(insert v B) : Set V)).IsBipartite := by
      apply WrittenOnTheWallII.GraphConjecture183GammaThree.induce_insert_isBipartite_of_coloring G B v c'
      · intro u hu w hw huw
        have huv : u ≠ v := fun h ↦ hvB (h ▸ hu)
        have hwv : w ≠ v := fun h ↦ hvB (h ▸ hw)
        simpa [c', huv, hwv] using hBcolor u hu w hw huw
      · intro u hu huv
        have huv_ne : u ≠ v := huv.ne.symm
        have huA : u ∉ A := by
          intro huA
          have huPair : u = x ∨ u = d := by simpa [A] using huA
          rcases huPair with rfl | rfl
          · exact hv.1 huv
          · exact hv.2 huv
        simp only [c', if_pos, c, cP]
        by_cases huy : u = y
        · have hyv : y ≠ v := by
            intro h
            exact huv_ne (huy.trans h)
          simp [huy, hyv]
        · simp [huy, huA, huv_ne]
    have hSixCard : (insert v B).card = 6 := by
      rw [card_insert_of_notMem hvB, hBcard]
    exact hnoSix (insert v B) hSixCard hSixBip
  let D : Finset V := {x, a, d}
  refine ⟨D, ?_, ?_⟩
  · have hxa_ne : x ≠ a := hxa.ne
    have had_ne : a ≠ d := had.ne
    have hxd_ne : x ≠ d := by
      intro h
      subst d
      exact hxz hdz
    simp [D, hxa_ne, had_ne, hxd_ne]
  · constructor
    · intro v
      by_cases hvD : v ∈ D
      · exact Or.inl hvD
      · right
        by_cases hvB : v ∈ B
        · have hvCases : v = y ∨ v = x ∨ v = a ∨ v = d ∨ v = z := by
            simpa only [B, P, mem_insert, mem_singleton] using hvB
          rcases hvCases with rfl | rfl | rfl | rfl | rfl
          · exact ⟨x, by simp [D], hyx⟩
          · exact (hvD (by simp [D])).elim
          · exact (hvD (by simp [D])).elim
          · exact (hvD (by simp [D])).elim
          · exact ⟨d, by simp [D], hdz.symm⟩
        · rcases houtside v hvB with hvx | hvd
          · exact ⟨x, by simp [D], hvx⟩
          · exact ⟨d, by simp [D], hvd⟩
    · letI : Nonempty (↑D : Set V) := ⟨⟨a, by simp [D]⟩⟩
      constructor
      intro u v
      have hu : u.1 = x ∨ u.1 = a ∨ u.1 = d := by
        simpa [D] using u.2
      have hv : v.1 = x ∨ v.1 = a ∨ v.1 = d := by
        simpa [D] using v.2
      rcases hu with hu | hu | hu <;> rcases hv with hv | hv | hv
      · have huv : u = v := Subtype.ext (hu.trans hv.symm)
        subst v
        exact .rfl
      · apply Adj.reachable
        change G.Adj u.1 v.1
        simpa [hu, hv] using hxa
      · apply Reachable.trans (v := ⟨a, by simp [D]⟩)
        · apply Adj.reachable
          change G.Adj u.1 a
          simpa [hu] using hxa
        · apply Adj.reachable
          change G.Adj a v.1
          simpa [hv] using had
      · apply Adj.reachable
        change G.Adj u.1 v.1
        simpa [hu, hv] using hxa.symm
      · have huv : u = v := Subtype.ext (hu.trans hv.symm)
        subst v
        exact .rfl
      · apply Adj.reachable
        change G.Adj u.1 v.1
        simpa [hu, hv] using had
      · apply Reachable.trans (v := ⟨a, by simp [D]⟩)
        · apply Adj.reachable
          change G.Adj u.1 a
          simpa [hu] using had.symm
        · apply Adj.reachable
          change G.Adj a v.1
          simpa [hv] using hxa.symm
      · apply Adj.reachable
        change G.Adj u.1 v.1
        simpa [hu, hv] using had.symm
      · have huv : u = v := Subtype.ext (hu.trans hv.symm)
        subst v
        exact .rfl

/-- Explicit-geodesic form of the multi-vertex augmentation theorem.

The conclusion retains the actual six-vertex induced-bipartite witness. -/
theorem exists_induced_bipartite_six_of_dist_three
    (G : SimpleGraph V) (hconn : G.Connected) {x a d z : V}
    (hdist : G.dist x z = 3)
    (hxa : G.Adj x a) (had : G.Adj a d) (hdz : G.Adj d z)
    (hgamma : ∀ D : Finset V,
      G.IsConnectedDominating (↑D : Set V) → 4 ≤ D.card) :
    ∃ S : Finset V, S.card = 6 ∧ (G.induce (↑S : Set V)).IsBipartite := by
  classical
  by_contra hExists
  push_neg at hExists
  let P : Finset V := {x, a, d, z}
  let A : Finset V := {x, d}
  have hxd : ¬G.Adj x d := by
    intro h
    have hle := G.dist_le (h.toWalk.append hdz.toWalk)
    simp only [Walk.length_append, Walk.length_cons, Walk.length_nil,
      zero_add] at hle
    omega
  have hxz : ¬G.Adj x z := by
    intro h
    have hle := G.dist_le h.toWalk
    simp only [Walk.length_cons, Walk.length_nil, zero_add] at hle
    omega
  have haz : ¬G.Adj a z := by
    intro h
    have hle := G.dist_le (hxa.toWalk.append h.toWalk)
    simp only [Walk.length_append, Walk.length_cons, Walk.length_nil,
      zero_add] at hle
    omega
  have hPcard : P.card = 4 := by
    have hxa_ne : x ≠ a := hxa.ne
    have had_ne : a ≠ d := had.ne
    have hdz_ne : d ≠ z := hdz.ne
    have hxd_ne : x ≠ d := by
      intro h
      subst d
      exact hxz hdz
    have hxz_ne : x ≠ z := by
      intro h
      subst z
      simp at hdist
    have haz_ne : a ≠ z := by
      intro h
      subst z
      exact hxz hxa
    simp [P, hxa_ne, had_ne, hdz_ne, hxd_ne, hxz_ne, haz_ne]
  let cP : V → Fin 2 := fun u ↦ if u ∈ A then 0 else 1
  have hPcolor : ∀ u ∈ P, ∀ w ∈ P, G.Adj u w → cP u ≠ cP w := by
    intro u hu w hw huw heq
    have huP : u = x ∨ u = a ∨ u = d ∨ u = z := by
      simpa only [P, mem_insert, mem_singleton] using hu
    have hwP : w = x ∨ w = a ∨ w = d ∨ w = z := by
      simpa only [P, mem_insert, mem_singleton] using hw
    by_cases huA : u ∈ A
    · have hwA : w ∈ A := by
        by_contra hn
        simp [cP, huA, hn] at heq
      have huPair : u = x ∨ u = d := by simpa [A] using huA
      have hwPair : w = x ∨ w = d := by simpa [A] using hwA
      rcases huPair with rfl | rfl <;> rcases hwPair with rfl | rfl
      · exact G.loopless _ huw
      · exact hxd huw
      · exact hxd huw.symm
      · exact G.loopless _ huw
    · have hwA : w ∉ A := by
        intro hwA
        simp [cP, huA, hwA] at heq
      have huPair : u = a ∨ u = z := by
        rcases huP with rfl | rfl | rfl | rfl
        · exact (huA (by simp [A])).elim
        · exact Or.inl rfl
        · exact (huA (by simp [A])).elim
        · exact Or.inr rfl
      have hwPair : w = a ∨ w = z := by
        rcases hwP with rfl | rfl | rfl | rfl
        · exact (hwA (by simp [A])).elim
        · exact Or.inl rfl
        · exact (hwA (by simp [A])).elim
        · exact Or.inr rfl
      rcases huPair with rfl | rfl <;> rcases hwPair with rfl | rfl
      · exact G.loopless _ huw
      · exact haz huw
      · exact haz huw.symm
      · exact G.loopless _ huw
  let IsR : V → Prop := fun r ↦ r ∉ P ∧ ∀ u ∈ P, ¬G.Adj r u
  have hmiddle : ∀ y, y ∉ P → (∃ u ∈ P, G.Adj y u) →
      G.Adj y a ∨ G.Adj y d := by
    intro y hyP ⟨u, huP, hyu⟩
    by_contra hmid
    push_neg at hmid
    have huCases : u = x ∨ u = a ∨ u = d ∨ u = z := by
      simpa only [P, mem_insert, mem_singleton] using huP
    rcases huCases with rfl | rfl | rfl | rfl
    · have hyz : ¬G.Adj y z := by
        intro hyz
        have hle := G.dist_le (hyu.symm.toWalk.append hyz.toWalk)
        simp only [Walk.length_append, Walk.length_cons, Walk.length_nil,
          zero_add] at hle
        omega
      obtain ⟨D, hDcard, hD⟩ :=
        endpoint_leaf_forces_connected_dominating_triple G hdist hxa had hdz
          hyP hyu hmid.1 hmid.2 hyz hExists
      have hfour := hgamma D hD
      omega
    · exact (hmid.1 hyu).elim
    · exact (hmid.2 hyu).elim
    · have hyx : ¬G.Adj y x := by
        intro hyx
        have hle := G.dist_le (hyx.symm.toWalk.append hyu.toWalk)
        simp only [Walk.length_append, Walk.length_cons, Walk.length_nil,
          zero_add] at hle
        omega
      have hdist' : G.dist u x = 3 := by
        rw [G.dist_comm]
        exact hdist
      have hyP' : y ∉ ({u, d, a, x} : Finset V) := by
        intro h
        apply hyP
        rcases (show y = u ∨ y = d ∨ y = a ∨ y = x by
          simpa only [mem_insert, mem_singleton] using h) with rfl | rfl | rfl | rfl <;>
          simp [P]
      obtain ⟨D, hDcard, hD⟩ :=
        endpoint_leaf_forces_connected_dominating_triple G hdist'
          hdz.symm had.symm hxa.symm hyP' hyu hmid.2 hmid.1 hyx hExists
      have hfour := hgamma D hD
      omega
  have hRunique : ∀ r s, IsR r → IsR s → r = s := by
    intro r s hr hs
    by_contra hrs
    have hSixBip := insert_two_anticomplete_isBipartite G P r s cP hrs
      hr.1 hs.1 hPcolor hr.2 hs.2
    have hSixCard : (insert r (insert s P)).card = 6 := by
      rw [card_insert_of_notMem]
      · rw [card_insert_of_notMem hs.1, hPcard]
      · simp only [mem_insert]
        exact fun h ↦ h.elim hrs hr.1
    exact hExists (insert r (insert s P)) hSixCard hSixBip
  by_cases hR : ∃ r, IsR r
  · obtain ⟨r, hrP, hrAnti⟩ := hR
    have hrx : r ≠ x := by
      intro h
      subst r
      exact hrP (by simp [P])
    obtain ⟨p, _hpPath, _hpLength⟩ := hconn.exists_path_of_dist r x
    have hpPos : 0 < p.length := by
      apply Nat.pos_of_ne_zero
      intro hpZero
      exact hrx (p.eq_of_length_eq_zero hpZero)
    let y := p.getVert 1
    have hry : G.Adj r y := by
      simpa [y] using p.adj_getVert_succ hpPos
    have hyP : y ∉ P := by
      intro hyP
      exact hrAnti y hyP hry
    have hyTouches : ∃ u ∈ P, G.Adj y u := by
      by_contra hnone
      push_neg at hnone
      have hyR : IsR y := ⟨hyP, hnone⟩
      have hyr := hRunique y r hyR ⟨hrP, hrAnti⟩
      exact hry.ne hyr.symm
    have hyMid := hmiddle y hyP hyTouches
    let D : Finset V := {a, d, y}
    have hDcard : D.card = 3 := by
      have had_ne : a ≠ d := had.ne
      have hya_ne : y ≠ a := by
        intro h
        apply hyP
        simp [P, h]
      have hyd_ne : y ≠ d := by
        intro h
        apply hyP
        simp [P, h]
      simp [D, had_ne, hya_ne.symm, hyd_ne.symm]
    have hDdom : G.IsDominating (↑D : Set V) := by
      intro v
      by_cases hvD : v ∈ D
      · exact Or.inl hvD
      · right
        by_cases hvP : v ∈ P
        · have hvCases : v = x ∨ v = a ∨ v = d ∨ v = z := by
            simpa only [P, mem_insert, mem_singleton] using hvP
          rcases hvCases with rfl | rfl | rfl | rfl
          · exact ⟨a, by simp [D], hxa⟩
          · exact (hvD (by simp [D])).elim
          · exact (hvD (by simp [D])).elim
          · exact ⟨d, by simp [D], hdz.symm⟩
        · by_cases hvTouches : ∃ u ∈ P, G.Adj v u
          · rcases hmiddle v hvP hvTouches with hva | hvd
            · exact ⟨a, by simp [D], hva⟩
            · exact ⟨d, by simp [D], hvd⟩
          · push_neg at hvTouches
            have hvR : IsR v := ⟨hvP, hvTouches⟩
            have hvr := hRunique v r hvR ⟨hrP, hrAnti⟩
            subst v
            exact ⟨y, by simp [D], hry⟩
    have hDconn : (G.induce (↑D : Set V)).Connected := by
      rcases hyMid with hya | hyd
      · rw [show D = ({y, a, d} : Finset V) by
          ext q
          simp only [D, mem_insert, mem_singleton]
          tauto]
        exact induce_three_connected_of_path G hya had
      · simpa [D] using induce_three_connected_of_path G had hyd.symm
    have hfour := hgamma D ⟨hDdom, hDconn⟩
    omega
  · push_neg at hR
    let D : Finset V := {a, d}
    have hDdom : G.IsDominating (↑D : Set V) := by
      intro v
      by_cases hvD : v ∈ D
      · exact Or.inl hvD
      · right
        by_cases hvP : v ∈ P
        · have hvCases : v = x ∨ v = a ∨ v = d ∨ v = z := by
            simpa only [P, mem_insert, mem_singleton] using hvP
          rcases hvCases with rfl | rfl | rfl | rfl
          · exact ⟨a, by simp [D], hxa⟩
          · exact (hvD (by simp [D])).elim
          · exact (hvD (by simp [D])).elim
          · exact ⟨d, by simp [D], hdz.symm⟩
        · have hvTouches : ∃ u ∈ P, G.Adj v u := by
            by_contra hnone
            push_neg at hnone
            exact hR v ⟨hvP, hnone⟩
          rcases hmiddle v hvP hvTouches with hva | hvd
          · exact ⟨a, by simp [D], hva⟩
          · exact ⟨d, by simp [D], hvd⟩
    have hDconn : (G.induce (↑D : Set V)).Connected := by
      letI : Nonempty (↑D : Set V) := ⟨⟨a, by simp [D]⟩⟩
      constructor
      intro u v
      by_cases huv : u = v
      · subst v
        exact .rfl
      · have hu : u.1 = a ∨ u.1 = d := by simpa [D] using u.2
        have hv : v.1 = a ∨ v.1 = d := by simpa [D] using v.2
        rcases hu with hu | hu <;> rcases hv with hv | hv
        · exact (huv (Subtype.ext (hu.trans hv.symm))).elim
        · apply Adj.reachable
          change G.Adj u.1 v.1
          simpa [hu, hv] using had
        · apply Adj.reachable
          change G.Adj u.1 v.1
          simpa [hu, hv] using had.symm
        · exact (huv (Subtype.ext (hu.trans hv.symm))).elim
    have hfour := hgamma D ⟨hDdom, hDconn⟩
    have hDcard : D.card = 2 := by simp [D, had.ne]
    omega

/-- Connected paper form: the intermediate vertices of the distance-three
geodesic are extracted from a shortest path. -/
theorem exists_induced_bipartite_six_of_connected
    (G : SimpleGraph V) (hconn : G.Connected) {x z : V}
    (hdist : G.dist x z = 3)
    (hgamma : ∀ D : Finset V,
      G.IsConnectedDominating (↑D : Set V) → 4 ≤ D.card) :
    ∃ S : Finset V, S.card = 6 ∧ (G.induce (↑S : Set V)).IsBipartite := by
  obtain ⟨p, _hpPath, hpLength⟩ := hconn.exists_path_of_dist x z
  let a := p.getVert 1
  let d := p.getVert 2
  have hpThree : p.length = 3 := hpLength.trans hdist
  have hzero : 0 < p.length := by omega
  have hone : 1 < p.length := by omega
  have htwo : 2 < p.length := by omega
  have hxa : G.Adj x a := by
    simpa [a] using p.adj_getVert_succ hzero
  have had : G.Adj a d := by
    simpa [a, d] using p.adj_getVert_succ hone
  have hdz : G.Adj d z := by
    rw [← p.getVert_length]
    simpa [d, hpThree] using p.adj_getVert_succ htwo
  exact exists_induced_bipartite_six_of_dist_three G hconn hdist hxa had hdz hgamma

/-- Repository-invariant form of the explicit-witness theorem. -/
theorem six_le_largestInducedBipartiteSubgraphSize_of_connected
    (G : SimpleGraph V) (hconn : G.Connected) {x z : V}
    (hdist : G.dist x z = 3)
    (hgamma : ∀ D : Finset V,
      G.IsConnectedDominating (↑D : Set V) → 4 ≤ D.card) :
    6 ≤ G.largestInducedBipartiteSubgraphSize := by
  obtain ⟨S, hScard, hSbip⟩ :=
    exists_induced_bipartite_six_of_connected G hconn hdist hgamma
  unfold largestInducedBipartiteSubgraphSize
  apply le_csSup
  · exact ⟨Fintype.card V, fun n ⟨t, _ht, htn⟩ ↦ htn ▸ t.card_le_univ⟩
  · exact ⟨S, hSbip, hScard⟩

/-- Invariant-native statement of the proved tier. -/
theorem six_le_largestInducedBipartiteSubgraphSize_of_connectedDominationNumber
    (G : SimpleGraph V) (hconn : G.Connected) {x z : V}
    (hdist : G.dist x z = 3)
    (hgamma : 4 ≤ G.connectedDominationNumber) :
    6 ≤ G.largestInducedBipartiteSubgraphSize := by
  apply six_le_largestInducedBipartiteSubgraphSize_of_connected G hconn hdist
  intro D hD
  apply hgamma.trans
  unfold connectedDominationNumber
  apply csInf_le
  · exact ⟨0, fun n _hn ↦ Nat.zero_le n⟩
  · exact ⟨D, hD, rfl⟩

/-- The same theorem in the real-valued upstream notation `b G`. -/
theorem six_le_b_of_connectedDominationNumber
    (G : SimpleGraph V) (hconn : G.Connected) {x z : V}
    (hdist : G.dist x z = 3)
    (hgamma : 4 ≤ G.connectedDominationNumber) :
    (6 : ℝ) ≤ b G := by
  unfold b
  exact_mod_cast
    six_le_largestInducedBipartiteSubgraphSize_of_connectedDominationNumber
      G hconn hdist hgamma


end WrittenOnTheWallII.GraphConjecture183GammaFour
