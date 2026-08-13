import FormalConjecturesUtil

/-!
# WOWII 133: matching neighborhoods and the triangle correction

This file proves the finite maximum-degree-one independence formula isolated
by the preceding #133 reduction, applies it to C4-free open neighborhoods, and
rewrites the source invariant using their edge counts.
-/

namespace WrittenOnTheWallII.GraphConjecture133MatchingNeighborhood

open SimpleGraph

variable {W V : Type*} [Fintype W] [DecidableEq W]
  [Fintype V] [DecidableEq V] [Nonempty V]

/-- Two neighbors of a vertex in a maximum-degree-one graph must coincide. -/
lemma adj_right_unique_of_degree_le_one (H : SimpleGraph W)
    [DecidableRel H.Adj] (hdeg : ∀ v, H.degree v ≤ 1)
    {p a b : W} (hpa : H.Adj p a) (hpb : H.Adj p b) :
    a = b := by
  by_contra hab
  have hlarge : 1 < (H.neighborFinset p).card :=
    Finset.one_lt_card.mpr
      ⟨a, by simpa [H.mem_neighborFinset] using hpa,
       b, by simpa [H.mem_neighborFinset] using hpb, hab⟩
  rw [H.card_neighborFinset_eq_degree] at hlarge
  have := hdeg p
  omega

/-- In a maximum-degree-one graph, two edges sharing a vertex are equal. -/
lemma edge_eq_of_common_vertex_of_degree_le_one (H : SimpleGraph W)
    [DecidableRel H.Adj] (hdeg : ∀ v, H.degree v ≤ 1)
    {e f : H.edgeFinset} {p : W} (hpe : p ∈ e.val) (hpf : p ∈ f.val) :
    e = f := by
  rcases e with ⟨⟨x, y⟩, hxy⟩
  rcases f with ⟨⟨z, w⟩, hzw⟩
  simp only [mem_edgeFinset, mem_edgeSet] at hxy hzw
  simp only [Sym2.mem_iff] at hpe hpf
  apply Subtype.ext
  rcases hpe with rfl | rfl <;> rcases hpf with rfl | rfl
  · have h := adj_right_unique_of_degree_le_one H hdeg hxy hzw
    simp [h]
  · have h := adj_right_unique_of_degree_le_one H hdeg hxy hzw.symm
    simp [h]
  · have h := adj_right_unique_of_degree_le_one H hdeg hxy.symm hzw
    simp [h]
  · have h := adj_right_unique_of_degree_le_one H hdeg hxy.symm hzw.symm
    simp [h]

/-- General lower bound `|V| ≤ alpha + |E|`.  Select one endpoint of every
edge as a vertex cover; its complement is independent. -/
lemma card_le_indepNum_add_card_edgeFinset (H : SimpleGraph W)
    [DecidableRel H.Adj] :
    Fintype.card W ≤ H.indepNum + H.edgeFinset.card := by
  classical
  let C : Finset W :=
    H.edgeFinset.attach.image (fun e ↦ e.val.out.1)
  have hCcard : C.card ≤ H.edgeFinset.card := by
    simpa [C] using
      (Finset.card_image_le : C.card ≤ H.edgeFinset.attach.card)
  have hcover : H.IsVertexCover (C : Set W) := by
    intro v w hvw
    have he : s(v, w) ∈ H.edgeFinset := by
      rw [mem_edgeFinset, mem_edgeSet]
      exact hvw
    let e : H.edgeFinset := ⟨s(v, w), he⟩
    have houtC : e.val.out.1 ∈ C := by
      apply Finset.mem_image.mpr
      exact ⟨e, by simp, rfl⟩
    have houtmem : e.val.out.1 ∈ e.val := Sym2.out_fst_mem e.val
    have hout : e.val.out.1 = v ∨ e.val.out.1 = w := by
      simpa [e, Sym2.mem_iff] using houtmem
    rcases hout with hout | hout
    · left
      simpa [hout] using houtC
    · right
      simpa [hout] using houtC
  let I : Finset W := Finset.univ \ C
  have hc : H.IsIndepSet (↑C : Set W)ᶜ :=
    (@SimpleGraph.isIndepSet_compl_iff_isVertexCover
      W H (↑C : Set W)).mpr hcover
  have hIset : (I : Set W) = (↑C : Set W)ᶜ := by
    ext x
    simp [I]
  have hI : H.IsIndepSet (I : Set W) := by
    rw [hIset]
    exact hc
  have hIle : I.card ≤ H.indepNum := hI.card_le_indepNum
  have hIcard : I.card = Fintype.card W - C.card := by
    simp only [I]
    rw [Finset.card_sdiff_of_subset (Finset.subset_univ C)]
    simp
  have hCle : C.card ≤ Fintype.card W := Finset.card_le_univ C
  omega

/-- In the maximum-degree-one case, every edge needs a distinct vertex outside
a maximum independent set. -/
lemma indepNum_add_card_edgeFinset_le_card_of_degree_le_one
    (H : SimpleGraph W) [DecidableRel H.Adj]
    (hdeg : ∀ v, H.degree v ≤ 1) :
    H.indepNum + H.edgeFinset.card ≤ Fintype.card W := by
  classical
  obtain ⟨s, hs⟩ := H.maximumIndepSet_exists
  have hout : ∀ e : H.edgeFinset, ∃ v : W, v ∈ e.val ∧ v ∉ s := by
    rintro ⟨⟨x, y⟩, hxy⟩
    simp only [mem_edgeFinset, mem_edgeSet] at hxy
    by_cases hx : x ∈ s
    · refine ⟨y, by simp, ?_⟩
      intro hy
      exact hs.isIndepSet hx hy hxy.ne hxy
    · exact ⟨x, by simp, hx⟩
  let C := {v : W // v ∉ s}
  let f : H.edgeFinset → C := fun e ↦
    ⟨Classical.choose (hout e), (Classical.choose_spec (hout e)).2⟩
  have hfmem : ∀ e, (f e).val ∈ e.val := fun e ↦
    (Classical.choose_spec (hout e)).1
  have hfinj : Function.Injective f := by
    intro e e' heq
    apply edge_eq_of_common_vertex_of_degree_le_one
      H hdeg (p := (f e).val) (hfmem e)
    simpa [heq] using hfmem e'
  have hcard := Fintype.card_le_of_injective f hfinj
  rw [Fintype.card_coe H.edgeFinset] at hcard
  have hCcard : Fintype.card C = Fintype.card W - s.card := by
    simp [C, Fintype.card_subtype_compl]
  rw [hCcard] at hcard
  have hsle : s.card ≤ Fintype.card W := Finset.card_le_univ s
  rw [← H.maximumIndepSet_card_eq_indepNum s hs]
  omega

/-- Exact independence formula for every finite graph of maximum degree at
most one: one may take every isolated vertex and one endpoint of each edge. -/
theorem indepNum_add_card_edgeFinset_eq_card_of_degree_le_one
    (H : SimpleGraph W) [DecidableRel H.Adj]
    (hdeg : ∀ v, H.degree v ≤ 1) :
    H.indepNum + H.edgeFinset.card = Fintype.card W :=
  le_antisymm
    (indepNum_add_card_edgeFinset_le_card_of_degree_le_one H hdeg)
    (card_le_indepNum_add_card_edgeFinset H)

/-- Four distinct vertices forming a not-necessarily-induced four-cycle. -/
def HasC4 (G : SimpleGraph V) : Prop :=
  ∃ a b c d : V,
    a ≠ b ∧ a ≠ c ∧ a ≠ d ∧ b ≠ c ∧ b ≠ d ∧ c ≠ d ∧
      G.Adj a b ∧ G.Adj b c ∧ G.Adj c d ∧ G.Adj d a

/-- Number of edges inside the open neighborhood of `v`.  Each such edge is
a triangle incident to `v`. -/
noncomputable def neighborhoodEdgeCount (G : SimpleGraph V)
    [DecidableRel G.Adj] (v : V) : ℕ :=
  (G.induce (G.neighborSet v)).edgeFinset.card

/-- Sum of the neighborhood edge counts over all vertices.  Combinatorially,
this is three times the number of triangles. -/
noncomputable def triangleIncidenceCount (G : SimpleGraph V)
    [DecidableRel G.Adj] : ℕ :=
  ∑ v, neighborhoodEdgeCount G v

omit [DecidableEq V] [Nonempty V] in
/-- C4-freeness makes every open-neighborhood graph have maximum degree at
most one. -/
lemma degree_induce_neighborSet_le_one_of_c4Free (G : SimpleGraph V)
    [DecidableRel G.Adj] (hc4 : ¬HasC4 G) (v : V)
    (w : G.neighborSet v) :
    (G.induce (G.neighborSet v)).degree w ≤ 1 := by
  classical
  let H := G.induce (G.neighborSet v)
  change H.degree w ≤ 1
  by_contra hle
  have hlarge : 1 < (H.neighborFinset w).card := by
    rw [H.card_neighborFinset_eq_degree]
    omega
  obtain ⟨a, ha, b, hb, hab⟩ := Finset.one_lt_card.mp hlarge
  have hwa : H.Adj w a := by
    simpa [H.mem_neighborFinset] using ha
  have hwb : H.Adj w b := by
    simpa [H.mem_neighborFinset] using hb
  have hva : G.Adj v a.val := a.property
  have hvw : G.Adj v w.val := w.property
  have hvb : G.Adj v b.val := b.property
  have haw : G.Adj a.val w.val := by
    simpa [H, induce_adj] using hwa.symm
  have hwb' : G.Adj w.val b.val := by
    simpa [H, induce_adj] using hwb
  apply hc4
  refine ⟨v, a.val, w.val, b.val, ?_, ?_, ?_, ?_, ?_, ?_,
    hva, haw, hwb', hvb.symm⟩
  · exact hva.ne
  · exact hvw.ne
  · exact hvb.ne
  · exact haw.ne
  · exact fun h ↦ hab (Subtype.ext h)
  · exact hwb'.ne

omit [Nonempty V] in
/-- Pointwise triangle-corrected local formula in a C4-free graph. -/
theorem indepNeighborsCard_add_neighborhoodEdgeCount_eq_degree_of_c4Free
    (G : SimpleGraph V) [DecidableRel G.Adj] (hc4 : ¬HasC4 G) (v : V) :
    indepNeighborsCard G v + neighborhoodEdgeCount G v = G.degree v := by
  unfold indepNeighborsCard neighborhoodEdgeCount
  rw [indepNum_add_card_edgeFinset_eq_card_of_degree_le_one]
  · exact G.card_neighborSet_eq_degree v
  · exact degree_induce_neighborSet_le_one_of_c4Free G hc4 v

omit [Nonempty V] in
/-- Subtractive form of the pointwise correction. -/
theorem indepNeighborsCard_eq_degree_sub_neighborhoodEdgeCount_of_c4Free
    (G : SimpleGraph V) [DecidableRel G.Adj] (hc4 : ¬HasC4 G) (v : V) :
    indepNeighborsCard G v = G.degree v - neighborhoodEdgeCount G v := by
  have h :=
    indepNeighborsCard_add_neighborhoodEdgeCount_eq_degree_of_c4Free G hc4 v
  omega

omit [Nonempty V] in
/-- Exact local-average identity for every finite C4-free graph. -/
theorem l_eq_average_degree_sub_neighborhood_edges_of_c4Free
    (G : SimpleGraph V) [DecidableRel G.Adj] (hc4 : ¬HasC4 G) :
    l G =
      (∑ v, (G.degree v - neighborhoodEdgeCount G v : ℕ) : ℝ) /
        (Fintype.card V : ℝ) := by
  unfold l averageIndepNeighbors indepNeighbors
  simp_rw [indepNeighborsCard_eq_degree_sub_neighborhoodEdgeCount_of_c4Free
    G hc4]

omit [Nonempty V] in
/-- Numerator form: twice the edge count minus the sum of triangle incidences
in open neighborhoods. -/
theorem l_eq_two_edges_sub_triangleIncidenceCount_of_c4Free
    (G : SimpleGraph V) [DecidableRel G.Adj] (hc4 : ¬HasC4 G) :
    l G =
      ((2 * G.edgeFinset.card - triangleIncidenceCount G : ℕ) : ℝ) /
        (Fintype.card V : ℝ) := by
  rw [l_eq_average_degree_sub_neighborhood_edges_of_c4Free G hc4]
  have hlocal : ∀ v ∈ (Finset.univ : Finset V),
      neighborhoodEdgeCount G v ≤ G.degree v := by
    intro v _hv
    have h :=
      indepNeighborsCard_add_neighborhoodEdgeCount_eq_degree_of_c4Free G hc4 v
    omega
  have hsum := Finset.sum_tsub_distrib (Finset.univ : Finset V) hlocal
  unfold triangleIncidenceCount
  rw [← Nat.cast_sum]
  congr 1
  rw [hsum, G.sum_degrees_eq_twice_card_edges]

omit [Nonempty V] in
/-- Source-notation corollary once the standard triangle-incidence
double-count is supplied: each 3-clique contributes one neighborhood edge at
each of its three vertices.  The separate hypothesis exposes that remaining
representation bridge rather than assuming it silently. -/
theorem l_eq_two_edges_sub_three_triangles_of_c4Free
    (G : SimpleGraph V) [DecidableRel G.Adj] (hc4 : ¬HasC4 G)
    (htriangles : triangleIncidenceCount G = 3 * (G.cliqueFinset 3).card) :
    l G =
      ((2 * G.edgeFinset.card - 3 * (G.cliqueFinset 3).card : ℕ) : ℝ) /
        (Fintype.card V : ℝ) := by
  rw [l_eq_two_edges_sub_triangleIncidenceCount_of_c4Free G hc4,
    htriangles]

end WrittenOnTheWallII.GraphConjecture133MatchingNeighborhood
