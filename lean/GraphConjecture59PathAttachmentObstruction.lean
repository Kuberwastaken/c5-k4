import GraphConjecture59PathAttachmentSplit

/-!
# WOWII 59: exact obstruction after the two-hit path split

For a labeled outside path `u-c-v`, the remaining two-or-three-hit cases have
three exact algebraic residues.  Missing any required extension edge gives a
different five-vertex induced forest.
-/

namespace WrittenOnTheWallII.GraphConjecture59PathAttachmentObstruction

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture59AlignedTripleBridge
open WrittenOnTheWallII.GraphConjecture59TwoVertexCompatibility
open WrittenOnTheWallII.GraphConjecture59PathFanClosure
open WrittenOnTheWallII.GraphConjecture59PathAttachmentSplit

universe u
variable {V : Type u} [Fintype V] [DecidableEq V]

/-- The three residual attachment types for a labeled path `u-c-v`:

* center plus exactly one endpoint requires the full `p-{a,b,q}` fan;
* both endpoints but not the center requires both core edges from `p`;
* all three path vertices requires two of the three fan edges.
-/
def LabeledPathAttachmentObstruction (G : SimpleGraph V)
    (a b u c v p q : V) : Prop :=
  (G.Adj q c ∧
      ((G.Adj q u ∧ ¬G.Adj q v) ∨ (¬G.Adj q u ∧ G.Adj q v)) ∧
      G.Adj p a ∧ G.Adj p b ∧ G.Adj p q) ∨
  (G.Adj q u ∧ ¬G.Adj q c ∧ G.Adj q v ∧
      G.Adj p a ∧ G.Adj p b) ∨
  (G.Adj q u ∧ G.Adj q c ∧ G.Adj q v ∧
      ((G.Adj p a ∧ G.Adj p b) ∨
       (G.Adj p a ∧ G.Adj p q) ∨
       (G.Adj p b ∧ G.Adj p q)))

/-- Orientation-independent packaging of the labeled obstruction, including
the path orientation that identifies its center. -/
def PathAttachmentObstruction (G : SimpleGraph V)
    (a b x y z p q : V) : Prop :=
  (G.Adj x y ∧ G.Adj x z ∧ ¬G.Adj y z ∧
    LabeledPathAttachmentObstruction G a b y x z p q) ∨
  (G.Adj x y ∧ G.Adj y z ∧ ¬G.Adj x z ∧
    LabeledPathAttachmentObstruction G a b x y z p q) ∨
  (G.Adj x z ∧ G.Adj y z ∧ ¬G.Adj x y ∧
    LabeledPathAttachmentObstruction G a b x z y p q)

omit [Fintype V] [DecidableEq V] in
lemma pairwiseDistinctSeven_swap_xy
    (a b x y z p q : V) (h : PairwiseDistinctSeven a b x y z p q) :
    PairwiseDistinctSeven a b y x z p q := by
  rcases h with ⟨⟨hab, hax, hay, haz, hbx, hby, hbz, hxy, hxz, hyz⟩,
    hpa, hpb, hpx, hpy, hpz, hqa, hqb, hqx, hqy, hqz, hpq⟩
  exact ⟨⟨hab, hay, hax, haz, hby, hbx, hbz, hxy.symm, hyz, hxz⟩,
    hpa, hpb, hpy, hpx, hpz, hqa, hqb, hqy, hqx, hqz, hpq⟩

omit [Fintype V] [DecidableEq V] in
lemma pairwiseDistinctSeven_swap_yz
    (a b x y z p q : V) (h : PairwiseDistinctSeven a b x y z p q) :
    PairwiseDistinctSeven a b x z y p q := by
  rcases h with ⟨⟨hab, hax, hay, haz, hbx, hby, hbz, hxy, hxz, hyz⟩,
    hpa, hpb, hpx, hpy, hpz, hqa, hqb, hqx, hqy, hqz, hpq⟩
  exact ⟨⟨hab, hax, haz, hay, hbx, hbz, hby, hxz, hxy, hyz.symm⟩,
    hpa, hpb, hpx, hpz, hpy, hqa, hqb, hqx, hqz, hqy, hpq⟩

omit [Fintype V] [DecidableEq V] in
lemma oppositeSideCompatible_swap_xy
    (G : SimpleGraph V) (a b x y z p q : V)
    (h : OppositeSideCompatible G a b x y z p q) :
    OppositeSideCompatible G a b y x z p q := by
  rcases h with ⟨hpx, hpy, hpz, hqa, hqb⟩
  exact ⟨hpy, hpx, hpz, hqa, hqb⟩

omit [Fintype V] [DecidableEq V] in
lemma oppositeSideCompatible_swap_yz
    (G : SimpleGraph V) (a b x y z p q : V)
    (h : OppositeSideCompatible G a b x y z p q) :
    OppositeSideCompatible G a b x z y p q := by
  rcases h with ⟨hpx, hpy, hpz, hqa, hqb⟩
  exact ⟨hpx, hpz, hpy, hqa, hqb⟩

omit [Fintype V] in
/-- An independent triple, one arbitrary center, and a final vertex with at
most one old neighbor form a forest. -/
theorem star_extension_isAcyclic
    (G : SimpleGraph V) (a b w p q : V)
    (hab : ¬G.Adj a b) (hqa : ¬G.Adj q a) (hqb : ¬G.Adj q b)
    (hpw : ¬G.Adj p w)
    (hp : ¬((G.Adj p a ∧ G.Adj p b) ∨
      (G.Adj p a ∧ G.Adj p q) ∨ (G.Adj p b ∧ G.Adj p q))) :
    (G.induce (({a, b, w, p, q} : Finset V) : Set V)).IsAcyclic := by
  have hI : G.IsIndepSet (({a, b, q} : Finset V) : Set V) := by
    intro r hr s hs hrs hadj
    change r ∈ ({a, b, q} : Finset V) at hr
    change s ∈ ({a, b, q} : Finset V) at hs
    simp only [mem_insert, mem_singleton] at hr hs
    rcases hr with rfl | rfl | rfl <;> rcases hs with rfl | rfl | rfl <;>
      simp_all [G.adj_comm]
  have hstar :=
    _root_.WrittenOnTheWallII.GraphConjecture40Baseline.induce_insert_isAcyclic_of_indep
      G ({a, b, q} : Finset V) w hI
  have hstar' :
      (G.induce (insert w ((({a, b, q} : Finset V) : Set V)))).IsAcyclic := by
    have hset :
        insert w ((({a, b, q} : Finset V) : Set V)) =
          (({w, a, b, q} : Finset V) : Set V) := by
      ext r
      simp [or_left_comm]
    rw [hset]
    exact hstar
  have hplus := induce_insert_isAcyclic_of_acyclic_of_unique_neighbor
    G (insert w ((({a, b, q} : Finset V) : Set V))) p hstar' (by
      intro x hx y hy hpx hpy
      by_contra hxy
      simp only [Set.mem_insert_iff] at hx hy
      rcases hx with rfl | hx <;> rcases hy with rfl | hy
      · exact hxy rfl
      · exact False.elim (hpw hpx)
      · exact False.elim (hpw hpy)
      · change x ∈ ({a, b, q} : Finset V) at hx
        change y ∈ ({a, b, q} : Finset V) at hy
        simp only [mem_insert, mem_singleton] at hx hy
        rcases hx with rfl | rfl | rfl <;>
          rcases hy with rfl | rfl | rfl <;> simp_all [G.adj_comm])
  have hset :
      (({a, b, w, p, q} : Finset V) : Set V) =
        insert p (insert w ((({a, b, q} : Finset V) : Set V))) := by
    ext r
    simp [or_left_comm]
  rw [hset]
  exact hplus

/-- The star-extension witness yields `f(G) ≥ 5`. -/
theorem five_le_f_of_star_extension
    (G : SimpleGraph V) (a b w p q : V)
    (hdist : PairwiseDistinctPathExtensions a b w p q)
    (hab : ¬G.Adj a b) (hqa : ¬G.Adj q a) (hqb : ¬G.Adj q b)
    (hpw : ¬G.Adj p w)
    (hp : ¬((G.Adj p a ∧ G.Adj p b) ∨
      (G.Adj p a ∧ G.Adj p q) ∨ (G.Adj p b ∧ G.Adj p q))) :
    5 ≤ G.largestInducedForestSize := by
  have hacyc := star_extension_isAcyclic G a b w p q hab hqa hqb hpw hp
  have hcard : ({a, b, w, p, q} : Finset V).card = 5 := by
    rcases hdist with ⟨habV, haw, hap, haq, hbw, hbp, hbq, hwp, hwq, hpq⟩
    simp [habV, haw, hap, haq, hbw, hbp, hbq, hwp, hwq, hpq]
  have hbound :=
    _root_.WrittenOnTheWallII.GraphConjecture40Baseline.card_le_largestInducedForestSize
      G ({a, b, w, p, q} : Finset V) hacyc
  simpa [hcard] using hbound

omit [Fintype V] in
/-- If `q` and `p` both avoid one core-side chain, the five vertices can be
built by successive leaf extensions. -/
theorem missing_core_chain_isAcyclic
    (G : SimpleGraph V) (a b w p q : V)
    (hab : ¬G.Adj a b) (hpb : ¬G.Adj p b) (hpw : ¬G.Adj p w)
    (hqa : ¬G.Adj q a) (hqb : ¬G.Adj q b) (hqw : ¬G.Adj q w) :
    (G.induce (({a, b, w, p, q} : Finset V) : Set V)).IsAcyclic := by
  have haI : G.IsIndepSet (({a} : Finset V) : Set V) := by
    intro r hr s hs hrs hadj
    change r ∈ ({a} : Finset V) at hr
    change s ∈ ({a} : Finset V) at hs
    simp only [mem_singleton] at hr hs
    exact hrs (hr.trans hs.symm)
  have haw :=
    _root_.WrittenOnTheWallII.GraphConjecture40Baseline.induce_insert_isAcyclic_of_indep
      G ({a} : Finset V) w haI
  have haw' :
      (G.induce (insert w ({a} : Set V))).IsAcyclic := by
    have hset :
        insert w ({a} : Set V) =
          (({w, a} : Finset V) : Set V) := by ext r; simp
    rw [hset]
    exact haw
  have habw := induce_insert_isAcyclic_of_acyclic_of_unique_neighbor
    G (insert w ({a} : Set V)) b haw' (by
      intro x hx y hy hbx hby
      by_contra hxy
      simp only [Set.mem_insert_iff, Set.mem_singleton_iff] at hx hy
      rcases hx with rfl | rfl <;> rcases hy with rfl | rfl <;>
        simp_all [G.adj_comm])
  have hpast := induce_insert_isAcyclic_of_acyclic_of_unique_neighbor
    G (insert b (insert w ({a} : Set V))) p habw (by
      intro x hx y hy hpx hpy
      by_contra hxy
      simp only [Set.mem_insert_iff, Set.mem_singleton_iff] at hx hy
      rcases hx with rfl | rfl | rfl <;>
        rcases hy with rfl | rfl | rfl <;> simp_all [G.adj_comm])
  have hqast := induce_insert_isAcyclic_of_acyclic_of_unique_neighbor
    G (insert p (insert b (insert w ({a} : Set V)))) q hpast (by
      intro x hx y hy hqx hqy
      by_contra hxy
      simp only [Set.mem_insert_iff, Set.mem_singleton_iff] at hx hy
      rcases hx with rfl | rfl | rfl | rfl <;>
        rcases hy with rfl | rfl | rfl | rfl <;> simp_all [G.adj_comm])
  have hset :
      (({a, b, w, p, q} : Finset V) : Set V) =
        insert q (insert p (insert b (insert w ({a} : Set V)))) := by
    ext r
    simp [or_comm, or_left_comm]
  rw [hset]
  exact hqast

/-- The missing-core chain yields `f(G) ≥ 5`. -/
theorem five_le_f_of_missing_core_chain
    (G : SimpleGraph V) (a b w p q : V)
    (hdist : PairwiseDistinctPathExtensions a b w p q)
    (hab : ¬G.Adj a b) (hpb : ¬G.Adj p b) (hpw : ¬G.Adj p w)
    (hqa : ¬G.Adj q a) (hqb : ¬G.Adj q b) (hqw : ¬G.Adj q w) :
    5 ≤ G.largestInducedForestSize := by
  have hacyc := missing_core_chain_isAcyclic
    G a b w p q hab hpb hpw hqa hqb hqw
  have hcard : ({a, b, w, p, q} : Finset V).card = 5 := by
    rcases hdist with ⟨habV, haw, hap, haq, hbw, hbp, hbq, hwp, hwq, hpq⟩
    simp [habV, haw, hap, haq, hbw, hbp, hbq, hwp, hwq, hpq]
  have hbound :=
    _root_.WrittenOnTheWallII.GraphConjecture40Baseline.card_le_largestInducedForestSize
      G ({a, b, w, p, q} : Finset V) hacyc
  simpa [hcard] using hbound

omit [Fintype V] in
/-- A core with the two nonadjacent path endpoints and `p` is a forest;
adding `q` is harmless when it sees at most one endpoint and avoids core and
`p`. -/
theorem core_endpoint_extension_isAcyclic
    (G : SimpleGraph V) (a u v p q : V)
    (huv : ¬G.Adj u v) (hpu : ¬G.Adj p u) (hpv : ¬G.Adj p v)
    (hqa : ¬G.Adj q a) (hq : ¬(G.Adj q u ∧ G.Adj q v))
    (hp : ¬(G.Adj p a ∧ G.Adj p q)) :
    (G.induce (({a, u, v, p, q} : Finset V) : Set V)).IsAcyclic := by
  have hI : G.IsIndepSet (({u, v} : Finset V) : Set V) := by
    intro r hr s hs hrs hadj
    change r ∈ ({u, v} : Finset V) at hr
    change s ∈ ({u, v} : Finset V) at hs
    simp only [mem_insert, mem_singleton] at hr hs
    rcases hr with rfl | rfl <;> rcases hs with rfl | rfl <;>
      simp_all [G.adj_comm]
  have hbase :=
    _root_.WrittenOnTheWallII.GraphConjecture40Baseline.induce_insert_isAcyclic_of_indep
      G ({u, v} : Finset V) a hI
  have hbase' :
      (G.induce (insert a ((({u, v} : Finset V) : Set V)))).IsAcyclic := by
    have hset :
        insert a ((({u, v} : Finset V) : Set V)) =
          (({a, u, v} : Finset V) : Set V) := by ext r; simp
    rw [hset]
    exact hbase
  have hqplus := induce_insert_isAcyclic_of_acyclic_of_unique_neighbor
    G (insert a ((({u, v} : Finset V) : Set V))) q hbase' (by
      intro x hx y hy hqx hqy
      by_contra hxy
      simp only [Set.mem_insert_iff] at hx hy
      rcases hx with rfl | hx <;> rcases hy with rfl | hy
      · exact hxy rfl
      · exact False.elim (hqa hqx)
      · exact False.elim (hqa hqy)
      · change x ∈ ({u, v} : Finset V) at hx
        change y ∈ ({u, v} : Finset V) at hy
        simp only [mem_insert, mem_singleton] at hx hy
        rcases hx with rfl | rfl <;> rcases hy with rfl | rfl <;>
          simp_all [G.adj_comm])
  have hpplus := induce_insert_isAcyclic_of_acyclic_of_unique_neighbor
    G (insert q (insert a ((({u, v} : Finset V) : Set V)))) p hqplus (by
      intro x hx y hy hpx hpy
      by_contra hxy
      change x = q ∨ x = a ∨ x ∈ ({u, v} : Finset V) at hx
      change y = q ∨ y = a ∨ y ∈ ({u, v} : Finset V) at hy
      simp only [mem_insert, mem_singleton] at hx hy
      rcases hx with rfl | rfl | rfl | rfl <;>
        rcases hy with rfl | rfl | rfl | rfl <;> simp_all [G.adj_comm])
  have hset :
      (({a, u, v, p, q} : Finset V) : Set V) =
        insert p (insert q (insert a ((({u, v} : Finset V) : Set V)))) := by
    ext r
    simp [or_comm, or_left_comm]
  rw [hset]
  exact hpplus

/-- The core-endpoint witness yields `f(G) ≥ 5`. -/
theorem five_le_f_of_core_endpoint_extension
    (G : SimpleGraph V) (a u v p q : V)
    (hdist : PairwiseDistinctPathExtensions a u v p q)
    (huv : ¬G.Adj u v) (hpu : ¬G.Adj p u) (hpv : ¬G.Adj p v)
    (hqa : ¬G.Adj q a) (hq : ¬(G.Adj q u ∧ G.Adj q v))
    (hp : ¬(G.Adj p a ∧ G.Adj p q)) :
    5 ≤ G.largestInducedForestSize := by
  have hacyc := core_endpoint_extension_isAcyclic
    G a u v p q huv hpu hpv hqa hq hp
  have hcard : ({a, u, v, p, q} : Finset V).card = 5 := by
    rcases hdist with ⟨hau, hav, hap, haq, huvV, hup, huq, hvp, hvq, hpq⟩
    simp [hau, hav, hap, haq, huvV, hup, huq, hvp, hvq, hpq]
  have hbound :=
    _root_.WrittenOnTheWallII.GraphConjecture40Baseline.card_le_largestInducedForestSize
      G ({a, u, v, p, q} : Finset V) hacyc
  simpa [hcard] using hbound

/-- Labeled path split after `q` is known to hit at least two path vertices. -/
theorem five_le_f_or_labeled_path_attachment_obstruction
    (G : SimpleGraph V) (a b u c v p q : V)
    (hdist : PairwiseDistinctSeven a b u c v p q)
    (hab : ¬G.Adj a b)
    (huv : ¬G.Adj u v)
    (hcompat : OppositeSideCompatible G a b u c v p q)
    (htwo : (G.Adj q u ∧ G.Adj q c) ∨
      (G.Adj q u ∧ G.Adj q v) ∨ (G.Adj q c ∧ G.Adj q v)) :
    5 ≤ G.largestInducedForestSize ∨
      LabeledPathAttachmentObstruction G a b u c v p q := by
  rcases hdist with ⟨hfive, hpa, hpb, hpuV, hpcV, hpvV,
    hqaV, hqbV, hquV, hqcV, hqvV, hpqV⟩
  rcases hfive with ⟨habV, hauV, hacV, havV, hbuV, hbcV, hbvV,
    hucV, huvV, hcvV⟩
  rcases hcompat with ⟨hpu, hpc, hpv, hqa, hqb⟩
  by_cases hqu : G.Adj q u <;> by_cases hqc : G.Adj q c <;>
    by_cases hqv : G.Adj q v
  · by_cases hpairs :
      (G.Adj p a ∧ G.Adj p b) ∨
      (G.Adj p a ∧ G.Adj p q) ∨ (G.Adj p b ∧ G.Adj p q)
    · exact Or.inr <| Or.inr (Or.inr ⟨hqu, hqc, hqv, hpairs⟩)
    · exact Or.inl <| five_le_f_of_star_extension G a b c p q
        ⟨habV, hacV, hpa.symm, hqaV.symm, hbcV, hpb.symm,
          hqbV.symm, hpcV.symm, hqcV.symm, hpqV⟩
        hab hqa hqb hpc hpairs
  · by_cases hpaE : G.Adj p a
    · by_cases hpbE : G.Adj p b
      · by_cases hpqE : G.Adj p q
        · exact Or.inr <| Or.inl ⟨hqc, Or.inl ⟨hqu, hqv⟩,
            hpaE, hpbE, hpqE⟩
        · exact Or.inl <| five_le_f_of_core_endpoint_extension G a u v p q
            ⟨hauV, havV, hpa.symm, hqaV.symm, huvV, hpuV.symm,
              hquV.symm, hpvV.symm, hqvV.symm, hpqV⟩
            huv hpu hpv hqa (by tauto) (by tauto)
      · exact Or.inl <| five_le_f_of_missing_core_chain G a b v p q
          ⟨habV, havV, hpa.symm, hqaV.symm, hbvV, hpb.symm,
            hqbV.symm, hpvV.symm, hqvV.symm, hpqV⟩
          hab hpbE hpv hqa hqb hqv
    · exact Or.inl <| five_le_f_of_missing_core_chain G b a v p q
        ⟨habV.symm, hbvV, hpb.symm, hqbV.symm, havV, hpa.symm,
          hqaV.symm, hpvV.symm, hqvV.symm, hpqV⟩
        (by simpa [G.adj_comm] using hab) hpaE hpv hqb hqa hqv
  · by_cases hpaE : G.Adj p a
    · by_cases hpbE : G.Adj p b
      · exact Or.inr <| Or.inr (Or.inl ⟨hqu, hqc, hqv, hpaE, hpbE⟩)
      · exact Or.inl <| five_le_f_of_missing_core_chain G a b c p q
          ⟨habV, hacV, hpa.symm, hqaV.symm, hbcV, hpb.symm,
            hqbV.symm, hpcV.symm, hqcV.symm, hpqV⟩
          hab hpbE hpc hqa hqb hqc
    · exact Or.inl <| five_le_f_of_missing_core_chain G b a c p q
        ⟨habV.symm, hbcV, hpb.symm, hqbV.symm, hacV, hpa.symm,
          hqaV.symm, hpcV.symm, hqcV.symm, hpqV⟩
        (by simpa [G.adj_comm] using hab) hpaE hpc hqb hqa hqc
  · exact False.elim (by tauto)
  · by_cases hpaE : G.Adj p a
    · by_cases hpbE : G.Adj p b
      · by_cases hpqE : G.Adj p q
        · exact Or.inr <| Or.inl ⟨hqc, Or.inr ⟨hqu, hqv⟩,
            hpaE, hpbE, hpqE⟩
        · exact Or.inl <| five_le_f_of_core_endpoint_extension G a u v p q
            ⟨hauV, havV, hpa.symm, hqaV.symm, huvV, hpuV.symm,
              hquV.symm, hpvV.symm, hqvV.symm, hpqV⟩
            huv hpu hpv hqa (by tauto) (by tauto)
      · exact Or.inl <| five_le_f_of_missing_core_chain G a b u p q
          ⟨habV, hauV, hpa.symm, hqaV.symm, hbuV, hpb.symm,
            hqbV.symm, hpuV.symm, hquV.symm, hpqV⟩
          hab hpbE hpu hqa hqb hqu
    · exact Or.inl <| five_le_f_of_missing_core_chain G b a u p q
        ⟨habV.symm, hbuV, hpb.symm, hqbV.symm, hauV, hpa.symm,
          hqaV.symm, hpuV.symm, hquV.symm, hpqV⟩
        (by simpa [G.adj_comm] using hab) hpaE hpu hqb hqa hqu
  · exact False.elim (by tauto)
  · exact False.elim (by tauto)
  · exact False.elim (by tauto)

/-- Orientation-independent exact obstruction split for the outside path. -/
theorem five_le_f_or_path_attachment_obstruction
    (G : SimpleGraph V) (a b x y z p q : V)
    (hdist : PairwiseDistinctSeven a b x y z p q)
    (hab : ¬G.Adj a b)
    (hout : RealizesOutsideType G x y z .path)
    (hcompat : OppositeSideCompatible G a b x y z p q) :
    5 ≤ G.largestInducedForestSize ∨
      PathAttachmentObstruction G a b x y z p q := by
  rcases five_le_f_or_q_hits_two_outside G a b x y z p q
      hdist hout hcompat with hf | htwo
  · exact Or.inl hf
  · rcases hout with h | h | h
    · rcases five_le_f_or_labeled_path_attachment_obstruction
        G a b y x z p q
          (pairwiseDistinctSeven_swap_xy a b x y z p q hdist)
          hab h.2.2 (oppositeSideCompatible_swap_xy G a b x y z p q hcompat)
          (by simp only [QHitsTwoOutside] at htwo; tauto) with hf | hobs
      · exact Or.inl hf
      · exact Or.inr <| Or.inl ⟨h.1, h.2.1, h.2.2, hobs⟩
    · rcases five_le_f_or_labeled_path_attachment_obstruction
        G a b x y z p q hdist hab h.2.2 hcompat htwo with hf | hobs
      · exact Or.inl hf
      · exact Or.inr <| Or.inr (Or.inl ⟨h.1, h.2.1, h.2.2, hobs⟩)
    · rcases five_le_f_or_labeled_path_attachment_obstruction
        G a b x z y p q
          (pairwiseDistinctSeven_swap_yz a b x y z p q hdist)
          hab h.2.2 (oppositeSideCompatible_swap_yz G a b x y z p q hcompat)
          (by simp only [QHitsTwoOutside] at htwo; tauto) with hf | hobs
      · exact Or.inl hf
      · exact Or.inr <| Or.inr (Or.inr ⟨h.1, h.2.1, h.2.2, hobs⟩)

end WrittenOnTheWallII.GraphConjecture59PathAttachmentObstruction
