import GraphConjecture141RadiusFive

/-!
# WOWII 141: scalable tail assembly and closure through girth fifteen
-/

namespace WrittenOnTheWallII.GraphConjecture141GirthFifteenClosure

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture141Extraction
open WrittenOnTheWallII.GraphConjecture141GirthSeven
open WrittenOnTheWallII.GraphConjecture141GirthSevenExistence
open WrittenOnTheWallII.GraphConjecture141GirthThirteenClosure
open WrittenOnTheWallII.GraphConjecture141RadiusFive
open WrittenOnTheWallII.GraphConjecture141RadiusGirth

universe u
variable {V : Type u} [Fintype V] [DecidableEq V] [Nonempty V]

/-- A fixed six-edge geodesic prefix.  Storing the path rather than all
pairwise chord fields makes the representation scalable. -/
structure SixEdgeGeodesicPrefix (G : SimpleGraph V) where
  start : V
  finish : V
  path : G.Walk start finish
  isPath : path.IsPath
  length_eq : path.length = 6
  geodesic : path.length = G.dist start finish

omit [Fintype V] [DecidableEq V] [Nonempty V] in
lemma exists_sixEdgeGeodesicPrefix_of_connected_of_six_le_dist
    (G : SimpleGraph V) (hconn : G.Connected) (v w : V)
    (hdist : 6 ≤ G.dist v w) :
    ∃ P : SixEdgeGeodesicPrefix G, P.start = v := by
  obtain ⟨p, hpPath, hpLength⟩ := hconn.exists_path_of_dist v w
  have hlen : 6 ≤ p.length := by omega
  let q := p.take 6
  have hqLength : q.length = 6 := by simp [q, Walk.take_length, hlen]
  have hqPath : q.IsPath := Walk.isPath_of_isSubwalk
    (Walk.isSubwalk_take p 6) hpPath
  have hqGeodesic : q.length = G.dist v (p.getVert 6) :=
    length_eq_dist_of_subwalk hpLength (Walk.isSubwalk_take p 6)
  exact ⟨{
    start := v
    finish := p.getVert 6
    path := q
    isPath := hqPath
    length_eq := hqLength
    geodesic := hqGeodesic
  }, rfl⟩

omit [Fintype V] [Nonempty V] in
/-- A reusable ambient-finset leaf extension.  This is the representation
lemma underlying every later tail rung. -/
lemma induce_insert_isTree_of_isTree_of_unique_adj
    (G : SimpleGraph V) (B : Finset V) (t a : V)
    (htB : t ∉ B) (haB : a ∈ B)
    (hbase : (G.induce (↑B : Set V)).IsTree)
    (huniq : ∀ q ∈ B, G.Adj t q ↔ q = a) :
    (G.induce (↑(insert t B) : Set V)).IsTree := by
  let S := insert t B
  let H := G.induce (↑S : Set V)
  let t' : (S : Set V) := ⟨t, by simp [S]⟩
  have ht_unique : ∃! q : (S : Set V), H.Adj t' q := by
    let a' : (S : Set V) := ⟨a, by simp [S, haB]⟩
    refine ⟨a', ?_, ?_⟩
    · apply SimpleGraph.induce_adj.mpr
      exact (huniq a haB).mpr rfl
    · intro q htq
      apply Subtype.ext
      have htqG : G.Adj t (q : V) := SimpleGraph.induce_adj.mp htq
      have hqS : (q : V) = t ∨ (q : V) ∈ B := by
        simpa [S] using q.property
      rcases hqS with hqt | hqB
      · exact (G.loopless t (hqt ▸ htqG)).elim
      · exact (huniq q hqB).mp htqG
  have hbase' : (H.induce ({t'}ᶜ : Set (S : Set V))).IsTree := by
    let f : (↥({t'}ᶜ : Set (S : Set V))) → (↥(↑B : Set V)) := fun q =>
      ⟨q.val.val, by
        have hqS : q.val.val = t ∨ q.val.val ∈ B := by
          simpa [S] using q.val.property
        exact hqS.resolve_left (fun h => q.property (Subtype.ext h))⟩
    have hf_inj : Function.Injective f := by
      intro q q' h
      apply Subtype.ext
      apply Subtype.ext
      simpa [f] using congrArg Subtype.val h
    have hf_surj : Function.Surjective f := by
      intro q
      let qs : (S : Set V) := ⟨q, by
        change (q : V) ∈ insert t B
        exact Finset.mem_insert_of_mem q.property⟩
      have hqst : qs ≠ t' := by
        intro h
        apply htB
        have hqt : (q : V) = t := congrArg Subtype.val h
        simpa [hqt] using q.property
      let q' : (↥({t'}ᶜ : Set (S : Set V))) := ⟨qs, by
        simpa only [Set.mem_compl_iff, Set.mem_singleton_iff] using hqst⟩
      refine ⟨q', ?_⟩
      apply Subtype.ext
      rfl
    let e : (↥({t'}ᶜ : Set (S : Set V))) ≃ (↥(↑B : Set V)) :=
      Equiv.ofBijective f ⟨hf_inj, hf_surj⟩
    let iso : H.induce ({t'}ᶜ : Set (S : Set V)) ≃g
        G.induce (↑B : Set V) := {
      toEquiv := e
      map_rel_iff' := by intro q q'; rfl
    }
    exact iso.isTree_iff.mpr hbase
  simpa [H, S] using
    isTree_of_induce_compl_singleton_isTree_of_existsUnique_adj
      H t' hbase' ht_unique

omit [DecidableEq V] [Nonempty V] in
/-- In a six-edge geodesic, each later vertex is adjacent among the retained
earlier prefix exactly to its immediate predecessor, and has no neighbor in
the initial open neighborhood once its index is at least two. -/
lemma sixPrefix_unique_attachment
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (P : SixEdgeGeodesicPrefix G)
    (j : ℕ) (hjLower : 3 ≤ j) (hjUpper : j ≤ 6) :
    let t := P.path.getVert j
    (∀ q ∈ G.neighborFinset P.start, ¬G.Adj t q) ∧
    (∀ i < j, G.Adj t (P.path.getVert i) ↔ i = j - 1) := by
  let t := P.path.getVert j
  let a := P.path.getVert (j - 1)
  have hjLen : j ≤ P.path.length := by rw [P.length_eq]; exact hjUpper
  have hpred : j - 1 < P.path.length := by rw [P.length_eq]; omega
  have hadjPred : G.Adj a t := by
    have := P.path.adj_getVert_succ hpred
    have hsucc : j - 1 + 1 = j := by omega
    simpa [a, t, hsucc] using this
  constructor
  · intro q hqN htq
    have hsq : G.Adj P.start q := by
      simpa [G.mem_neighborFinset] using hqN
    let w : G.Walk P.start t := .cons hsq (.cons htq.symm .nil)
    have hdistTwo : G.dist P.start t ≤ 2 := by
      have := G.dist_le w
      simpa [w] using this
    have hpPrefixDist : G.dist P.start t = j := by
      let r := P.path.take j
      have hrSub := Walk.isSubwalk_take P.path j
      have hrGeo := length_eq_dist_of_subwalk P.geodesic hrSub
      have hrLen : r.length = j := by simp [r, Walk.take_length, hjLen]
      rw [hrLen] at hrGeo
      exact hrGeo.symm
    have hjTwo : j ≤ 2 := by
      rw [hpPrefixDist] at hdistTwo
      exact hdistTwo
    omega
  · intro i hi
    constructor
    · intro hti
      by_contra hine
      have hgap : i + 1 < j := by omega
      let r : G.Walk P.start t :=
        (P.path.take i).append hti.symm.toWalk
      have hdistShort := G.dist_le r
      have hiLen : i ≤ P.path.length := by omega
      have hrLen : r.length = i + 1 := by
        simp [r, Walk.take_length, hiLen]
      have hpPrefixDist : G.dist P.start t = j := by
        let s := P.path.take j
        have hsGeo := length_eq_dist_of_subwalk P.geodesic
          (Walk.isSubwalk_take P.path j)
        have hsLen : s.length = j := by simp [s, Walk.take_length, hjLen]
        rw [hsLen] at hsGeo
        exact hsGeo.symm
      rw [hrLen, hpPrefixDist] at hdistShort
      omega
    · intro hiPred
      subst i
      exact hadjPred.symm

omit [Fintype V] [DecidableEq V] [Nonempty V] in
lemma sixPrefix_dist_getVert
    (G : SimpleGraph V) (P : SixEdgeGeodesicPrefix G)
    (j : ℕ) (hj : j ≤ 6) :
    G.dist P.start (P.path.getVert j) = j := by
  have hjLen : j ≤ P.path.length := by rw [P.length_eq]; exact hj
  let r := P.path.take j
  have hrGeo := length_eq_dist_of_subwalk P.geodesic
    (Walk.isSubwalk_take P.path j)
  have hrLen : r.length = j := by simp [r, Walk.take_length, hjLen]
  rw [hrLen] at hrGeo
  exact hrGeo.symm

omit [Fintype V] [DecidableEq V] [Nonempty V] in
lemma sixPrefix_getVert_ne
    (G : SimpleGraph V) (P : SixEdgeGeodesicPrefix G)
    (i j : ℕ) (hi : i ≤ 6) (hj : j ≤ 6) (hij : i ≠ j) :
    P.path.getVert i ≠ P.path.getVert j := by
  intro h
  have := congrArg (G.dist P.start) h
  rw [sixPrefix_dist_getVert G P i hi,
    sixPrefix_dist_getVert G P j hj] at this
  exact hij this

/-- The six-edge prefix and repeated generic leaf extension construct an
induced tree with the maximum local star plus five tail vertices. -/
noncomputable def sixPrefix_inducedTreeWitness
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hgirth : 14 ≤ G.girth) (P : SixEdgeGeodesicPrefix G)
    (hvmax : indepNeighborsCard G P.start =
      Finset.univ.sup (indepNeighborsCard G)) :
    {S : Finset V //
      (G.induce (↑S : Set V)).IsTree ∧
      S.card = Finset.univ.sup (indepNeighborsCard G) + 6} := by
  let v := P.start
  let u := P.path.getVert 1
  let x := P.path.getVert 2
  let y := P.path.getVert 3
  let z := P.path.getVert 4
  let t := P.path.getVert 5
  let s := P.path.getVert 6
  let A := G.neighborFinset v
  have hv0 : P.path.getVert 0 = v := by simp [v]
  have hvu : G.Adj v u := by
    simpa [v, u, hv0] using P.path.adj_getVert_succ (by
      rw [P.length_eq]; omega : 0 < P.path.length)
  have hux : G.Adj u x := by
    simpa [u, x] using P.path.adj_getVert_succ (by
      rw [P.length_eq]; omega : 1 < P.path.length)
  have hxy : G.Adj x y := by
    simpa [x, y] using P.path.adj_getVert_succ (by
      rw [P.length_eq]; omega : 2 < P.path.length)
  have hyz : G.Adj y z := by
    simpa [y, z] using P.path.adj_getVert_succ (by
      rw [P.length_eq]; omega : 3 < P.path.length)
  have hzt : G.Adj z t := by
    simpa [z, t] using P.path.adj_getVert_succ (by
      rw [P.length_eq]; omega : 4 < P.path.length)
  have hts : G.Adj t s := by
    simpa [t, s] using P.path.adj_getVert_succ (by
      rw [P.length_eq]; omega : 5 < P.path.length)
  have hxv : x ≠ v := by
    intro h
    have hne := sixPrefix_getVert_ne G P 2 0 (by omega) (by omega) (by omega)
    exact hne (by simpa [x, v, hv0] using h)
  have hvx : ¬G.Adj v x := by
    intro hadj
    have hdistOne := dist_eq_one_iff_adj.mpr hadj
    have hdistTwo := sixPrefix_dist_getVert G P 2 (by omega)
    change G.dist P.start (P.path.getVert 2) = 1 at hdistOne
    omega
  let D1 : DistanceTwoLeafData G := {
    center := v
    localSet := A
    extra := x
    attachment := u
    localIndependent := by
      simpa [A, v, ← coe_neighborFinset] using
        locallyIndependent_of_six_le_girth G (by omega) v
    localSubset := Finset.Subset.rfl
    localCard := by
      change (G.neighborFinset v).card = indepNeighborsCard G v
      rw [G.card_neighborFinset_eq_degree]
      exact (indepNeighborsCard_eq_degree_of_independent_neighborhood
        G v (locallyIndependent_of_six_le_girth G (by omega) v)).symm
    centerMaximal := by simpa [v] using hvmax
    attachment_mem := by simpa [A, G.mem_neighborFinset] using hvu
    extra_not_mem := by
      simp only [Finset.mem_insert, not_or]
      refine ⟨hxv, ?_⟩
      intro hxA
      exact hvx (by simpa [A, G.mem_neighborFinset] using hxA)
    center_extra_nonadj := hvx
    extra_unique_local := by
      intro q hq
      constructor
      · intro hxq
        apply unique_neighbor_attachment_of_six_le_girth
          G (by omega) hvu hux hxv q
        · simpa [A, G.mem_neighborFinset] using hq
        · exact hxq
      · intro hqu
        subst q
        exact hux.symm
  }
  let B2 := insert x (insert v A)
  have hB2 : (G.induce (↑B2 : Set V)).IsTree := by
    simpa [B2, D1] using distanceTwoLeaf_inducedTree G D1
  have h3 := sixPrefix_unique_attachment G P 3 (by omega) (by omega)
  have h4 := sixPrefix_unique_attachment G P 4 (by omega) (by omega)
  have h5 := sixPrefix_unique_attachment G P 5 (by omega) (by omega)
  have h6 := sixPrefix_unique_attachment G P 6 (by omega) (by omega)
  have hne (i j : ℕ) (hi : i ≤ 6) (hj : j ≤ 6) (hij : i ≠ j) :
      P.path.getVert i ≠ P.path.getVert j :=
    sixPrefix_getVert_ne G P i j hi hj hij
  let B3 := insert y B2
  have hyB2 : y ∉ B2 := by
    simp only [B2, Finset.mem_insert, not_or]
    refine ⟨by simpa [y, x] using hne 3 2 (by omega) (by omega) (by omega),
      by simpa [y, v, hv0] using hne 3 0 (by omega) (by omega) (by omega), ?_⟩
    intro hyA
    have hd1 := dist_eq_one_iff_adj.mpr
      (by simpa [A, v, G.mem_neighborFinset] using hyA)
    have hd3 := sixPrefix_dist_getVert G P 3 (by omega)
    change G.dist P.start (P.path.getVert 3) = 1 at hd1
    omega
  have hB3 : (G.induce (↑B3 : Set V)).IsTree := by
    apply induce_insert_isTree_of_isTree_of_unique_adj G B2 y x hyB2
    · simp [B2]
    · exact hB2
    · intro q hq
      simp only [B2, Finset.mem_insert] at hq
      rcases hq with rfl | rfl | hqA
      · exact ⟨fun _ => rfl, fun _ => hxy.symm⟩
      · constructor
        · intro hyve
          have := (h3.2 0 (by omega)).mp (by simpa [y, v, hv0] using hyve)
          omega
        · intro hvxe
          exact (hne 0 2 (by omega) (by omega) (by omega)
            (by simpa [v, x, hv0] using hvxe)).elim
      · exact ⟨fun hyq => (h3.1 q hqA hyq).elim,
          fun hqx => (hvx (hqx ▸ (by simpa [A, G.mem_neighborFinset] using hqA))).elim⟩
  let B4 := insert z B3
  have hzB3 : z ∉ B3 := by
    simp only [B3, B2, Finset.mem_insert, not_or]
    refine ⟨by simpa [z, y] using hne 4 3 (by omega) (by omega) (by omega),
      by simpa [z, x] using hne 4 2 (by omega) (by omega) (by omega),
      by simpa [z, v, hv0] using hne 4 0 (by omega) (by omega) (by omega), ?_⟩
    intro hzA
    have hd1 := dist_eq_one_iff_adj.mpr
      (by simpa [A, v, G.mem_neighborFinset] using hzA)
    have hd4 := sixPrefix_dist_getVert G P 4 (by omega)
    change G.dist P.start (P.path.getVert 4) = 1 at hd1
    omega
  have hB4 : (G.induce (↑B4 : Set V)).IsTree := by
    apply induce_insert_isTree_of_isTree_of_unique_adj G B3 z y hzB3
    · simp [B3]
    · exact hB3
    · intro q hq
      simp only [B3, B2, Finset.mem_insert] at hq
      rcases hq with rfl | rfl | rfl | hqA
      · exact ⟨fun _ => rfl, fun _ => hyz.symm⟩
      · constructor
        · intro h; have := (h4.2 2 (by omega)).mp (by simpa [z, x] using h); omega
        · intro h; exact (hne 2 3 (by omega) (by omega) (by omega)
            (by simpa [x, y] using h)).elim
      · constructor
        · intro h; have := (h4.2 0 (by omega)).mp (by simpa [z, v, hv0] using h); omega
        · intro h; exact (hne 0 3 (by omega) (by omega) (by omega)
            (by simpa [v, y, hv0] using h)).elim
      · exact ⟨fun h => (h4.1 q hqA h).elim,
          fun h => by subst q; exact (hyB2 (by simp [B2, hqA])).elim⟩
  let B5 := insert t B4
  have htB4 : t ∉ B4 := by
    simp only [B4, B3, B2, Finset.mem_insert, not_or]
    refine ⟨by simpa [t, z] using hne 5 4 (by omega) (by omega) (by omega),
      by simpa [t, y] using hne 5 3 (by omega) (by omega) (by omega),
      by simpa [t, x] using hne 5 2 (by omega) (by omega) (by omega),
      by simpa [t, v, hv0] using hne 5 0 (by omega) (by omega) (by omega), ?_⟩
    intro htA
    have hd1 := dist_eq_one_iff_adj.mpr
      (by simpa [A, v, G.mem_neighborFinset] using htA)
    have hd5 := sixPrefix_dist_getVert G P 5 (by omega)
    change G.dist P.start (P.path.getVert 5) = 1 at hd1
    omega
  have hB5 : (G.induce (↑B5 : Set V)).IsTree := by
    apply induce_insert_isTree_of_isTree_of_unique_adj G B4 t z htB4
    · simp [B4]
    · exact hB4
    · intro q hq
      simp only [B4, B3, B2, Finset.mem_insert] at hq
      rcases hq with rfl | rfl | rfl | rfl | hqA
      · exact ⟨fun _ => rfl, fun _ => hzt.symm⟩
      · constructor
        · intro h; have := (h5.2 3 (by omega)).mp (by simpa [t, y] using h); omega
        · intro h; exact (hne 3 4 (by omega) (by omega) (by omega) (by simpa [y, z] using h)).elim
      · constructor
        · intro h; have := (h5.2 2 (by omega)).mp (by simpa [t, x] using h); omega
        · intro h; exact (hne 2 4 (by omega) (by omega) (by omega) (by simpa [x, z] using h)).elim
      · constructor
        · intro h; have := (h5.2 0 (by omega)).mp (by simpa [t, v, hv0] using h); omega
        · intro h; exact (hne 0 4 (by omega) (by omega) (by omega) (by simpa [v, z, hv0] using h)).elim
      · exact ⟨fun h => (h5.1 q hqA h).elim,
          fun h => by subst q; exact (hzB3 (by simp [B3, B2, hqA])).elim⟩
  let B6 := insert s B5
  have hsB5 : s ∉ B5 := by
    simp only [B5, B4, B3, B2, Finset.mem_insert, not_or]
    refine ⟨by simpa [s, t] using hne 6 5 (by omega) (by omega) (by omega),
      by simpa [s, z] using hne 6 4 (by omega) (by omega) (by omega),
      by simpa [s, y] using hne 6 3 (by omega) (by omega) (by omega),
      by simpa [s, x] using hne 6 2 (by omega) (by omega) (by omega),
      by simpa [s, v, hv0] using hne 6 0 (by omega) (by omega) (by omega), ?_⟩
    intro hsA
    have hd1 := dist_eq_one_iff_adj.mpr
      (by simpa [A, v, G.mem_neighborFinset] using hsA)
    have hd6 := sixPrefix_dist_getVert G P 6 (by omega)
    change G.dist P.start (P.path.getVert 6) = 1 at hd1
    omega
  have hB6 : (G.induce (↑B6 : Set V)).IsTree := by
    apply induce_insert_isTree_of_isTree_of_unique_adj G B5 s t hsB5
    · simp [B5]
    · exact hB5
    · intro q hq
      simp only [B5, B4, B3, B2, Finset.mem_insert] at hq
      rcases hq with rfl | rfl | rfl | rfl | rfl | hqA
      · exact ⟨fun _ => rfl, fun _ => hts.symm⟩
      · constructor
        · intro h; have := (h6.2 4 (by omega)).mp (by simpa [s, z] using h); omega
        · intro h; exact (hne 4 5 (by omega) (by omega) (by omega) (by simpa [z, t] using h)).elim
      · constructor
        · intro h; have := (h6.2 3 (by omega)).mp (by simpa [s, y] using h); omega
        · intro h; exact (hne 3 5 (by omega) (by omega) (by omega) (by simpa [y, t] using h)).elim
      · constructor
        · intro h; have := (h6.2 2 (by omega)).mp (by simpa [s, x] using h); omega
        · intro h; exact (hne 2 5 (by omega) (by omega) (by omega) (by simpa [x, t] using h)).elim
      · constructor
        · intro h; have := (h6.2 0 (by omega)).mp (by simpa [s, v, hv0] using h); omega
        · intro h; exact (hne 0 5 (by omega) (by omega) (by omega) (by simpa [v, t, hv0] using h)).elim
      · exact ⟨fun h => (h6.1 q hqA h).elim,
          fun h => by subst q; exact (htB4 (by simp [B4, B3, B2, hqA])).elim⟩
  refine ⟨B6, hB6, ?_⟩
  have hvA : v ∉ A := by
    intro hvA
    simp [A, G.mem_neighborFinset] at hvA
  rw [Finset.card_insert_of_notMem hsB5,
    Finset.card_insert_of_notMem htB4,
    Finset.card_insert_of_notMem hzB3,
    Finset.card_insert_of_notMem hyB2,
    Finset.card_insert_of_notMem D1.extra_not_mem,
    Finset.card_insert_of_notMem hvA]
  change A.card + 6 = _
  rw [G.card_neighborFinset_eq_degree]
  have hlocal := locallyIndependent_of_six_le_girth G (by omega) v
  rw [← indepNeighborsCard_eq_degree_of_independent_neighborhood G v hlocal]
  simpa [v] using hvmax

/-- **Unconditional girth-fourteen/fifteen closure.** -/
theorem conjecture141_of_girth_fourteen_or_fifteen
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hconn : G.Connected)
    (hgirthLower : 14 ≤ G.girth) (hgirthUpper : G.girth ≤ 15) :
    (G.girth / 2 : ℤ) - 1 +
        ((Finset.univ.sup (indepNeighborsCard G) : ℕ) : ℤ) ≤
      (largestInducedTreeSize G : ℤ) := by
  obtain ⟨v, hvmax⟩ := exists_maximum_local_center G
  obtain ⟨w, hvw⟩ :=
    everyVertexHasDistanceAtLeastSix_of_connected_of_twelve_le_girth
      G hconn (by omega) v
  obtain ⟨P, hpv⟩ :=
    exists_sixEdgeGeodesicPrefix_of_connected_of_six_le_dist G hconn v w hvw
  have hPmax : indepNeighborsCard G P.start =
      Finset.univ.sup (indepNeighborsCard G) := by simpa [hpv] using hvmax
  obtain ⟨S, htree, hcard⟩ :=
    sixPrefix_inducedTreeWitness G hgirthLower P hPmax
  have hbound := card_le_largestInducedTreeSize G S htree
  rw [hcard] at hbound
  have hhalf : G.girth / 2 ≤ 7 := by omega
  have hboundZ :
      ((Finset.univ.sup (indepNeighborsCard G) + 6 : ℕ) : ℤ) ≤
        (largestInducedTreeSize G : ℤ) := by exact_mod_cast hbound
  have hhalfZ : ((G.girth / 2 : ℕ) : ℤ) ≤ 7 := by exact_mod_cast hhalf
  omega

/-- **WOWII 141 is closed unconditionally through girth fifteen.** -/
theorem conjecture141_of_girth_le_fifteen
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hconn : G.Connected) (hgirth : G.girth ≤ 15) :
    (G.girth / 2 : ℤ) - 1 +
        ((Finset.univ.sup (indepNeighborsCard G) : ℕ) : ℤ) ≤
      (largestInducedTreeSize G : ℤ) := by
  by_cases hthirteen : G.girth ≤ 13
  · exact conjecture141_of_girth_le_thirteen G hconn hthirteen
  · exact conjecture141_of_girth_fourteen_or_fifteen
      G hconn (by omega) hgirth

end WrittenOnTheWallII.GraphConjecture141GirthFifteenClosure
