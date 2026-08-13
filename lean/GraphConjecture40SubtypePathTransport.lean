import GraphConjecture40IncludeRankComposition

/-!
# WOWII 40: subtype path-family transport and cut allocation

Recursive side certificates live on induced subtype graphs. This file lifts
their supports and paths canonically into the ambient graph and proves that
allocating the shared cut away from one side produces the join required by the
include-branch rank theorem.
-/

namespace WrittenOnTheWallII.GraphConjecture40SubtypePathTransport

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture40OneVertexSeparation
open WrittenOnTheWallII.GraphConjecture40BlockTreeRecurrence
open WrittenOnTheWallII.GraphConjecture40IncludeBranchRecurrence
open WrittenOnTheWallII.GraphConjecture40IncludeRankComposition

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]
variable {G : SimpleGraph V}

/-- Injective ambient image of a finite support on an induced subtype. -/
def supportLiftEmbedding (A : Finset V) :
    Finset ↥(↑A : Set V) ↪ Finset V where
  toFun s := s.map (Function.Embedding.subtype _)
  inj' := Finset.map_injective _

/-- Canonical ambient lift of a subtype path family. -/
def liftFamily (A : Finset V)
    (P : Finset (Finset ↥(↑A : Set V))) : Finset (Finset V) :=
  P.map (supportLiftEmbedding A)

omit [Fintype V] in
/-- Subtype path families lift to ambient path families. -/
theorem liftFamily_isPathSupportFamily
    (A : Finset V) (P : Finset (Finset ↥(↑A : Set V)))
    (hP : GraphConjecture40PathFamily.IsPathSupportFamily
      (G.induce (↑A : Set V)) P) :
    GraphConjecture40PathFamily.IsPathSupportFamily G (liftFamily A P) := by
  constructor
  · intro s hs t ht hne
    obtain ⟨s₀, hs₀, rfl⟩ := mem_map.mp hs
    obtain ⟨t₀, ht₀, rfl⟩ := mem_map.mp ht
    have hne₀ : s₀ ≠ t₀ := by
      intro h
      subst t₀
      exact hne rfl
    simpa [supportLiftEmbedding] using hP.1 s₀ hs₀ t₀ ht₀ hne₀
  · intro s hs
    obtain ⟨s₀, hs₀, rfl⟩ := mem_map.mp hs
    obtain ⟨a, z, p, hp, hsupp⟩ := hP.2 s₀ hs₀
    let e := SimpleGraph.Embedding.induce (G := G) (↑A : Set V)
    refine ⟨a.1, z.1, p.map e.toHom,
      Walk.map_isPath_of_injective e.injective hp, ?_⟩
    subst s₀
    rw [Walk.support_map]
    ext x
    simp [supportLiftEmbedding, e]

omit [Fintype V] [DecidableEq V] in
/-- Lifting preserves family cardinality. -/
@[simp] lemma card_liftFamily (A : Finset V)
    (P : Finset (Finset ↥(↑A : Set V))) :
    (liftFamily A P).card = P.card := by
  simp [liftFamily]

omit [Fintype V] in
/-- Covered vertices of the lifted family are exactly the ambient image of
the subtype covered vertices. -/
lemma coveredVertices_liftFamily (A : Finset V)
    (P : Finset (Finset ↥(↑A : Set V))) :
    GraphConjecture40PathFamily.coveredVertices (liftFamily A P) =
      (GraphConjecture40PathFamily.coveredVertices P).map
        (Function.Embedding.subtype _) := by
  ext x
  constructor
  · intro hx
    obtain ⟨s, hs, hxs⟩ :=
      GraphConjecture40PathFamily.mem_coveredVertices_iff.mp hx
    obtain ⟨s₀, hs₀, rfl⟩ := mem_map.mp hs
    obtain ⟨x₀, hx₀, rfl⟩ := mem_map.mp hxs
    exact mem_map.mpr ⟨x₀,
      GraphConjecture40PathFamily.mem_coveredVertices_iff.mpr
        ⟨s₀, hs₀, hx₀⟩, rfl⟩
  · intro hx
    obtain ⟨x₀, hx₀, rfl⟩ := mem_map.mp hx
    obtain ⟨s₀, hs₀, hxs₀⟩ :=
      GraphConjecture40PathFamily.mem_coveredVertices_iff.mp hx₀
    exact GraphConjecture40PathFamily.mem_coveredVertices_iff.mpr
      ⟨s₀.map (Function.Embedding.subtype _),
        mem_map.mpr ⟨s₀, hs₀, rfl⟩,
        mem_map.mpr ⟨x₀, hxs₀, rfl⟩⟩

omit [Fintype V] in
/-- Lifting preserves covered cardinality and hence every rank certificate. -/
theorem liftFamily_rank
    (A : Finset V) (P : Finset (Finset ↥(↑A : Set V))) {r : ℕ}
    (hrank : P.card + r ≤
      (GraphConjecture40PathFamily.coveredVertices P).card) :
    (liftFamily A P).card + r ≤
      (GraphConjecture40PathFamily.coveredVertices (liftFamily A P)).card := by
  rw [card_liftFamily, coveredVertices_liftFamily]
  simpa using hrank

omit [Fintype V] in
/-- Every support in a path-support family is nonempty. -/
lemma support_nonempty_of_mem_pathFamily
    {W : Type*} [DecidableEq W] (H : SimpleGraph W)
    (P : Finset (Finset W))
    (hP : GraphConjecture40PathFamily.IsPathSupportFamily H P)
    {s : Finset W} (hs : s ∈ P) : s.Nonempty := by
  obtain ⟨a, z, p, -, rfl⟩ := hP.2 s hs
  exact ⟨a, by simp⟩

/-- Canonical shared-cut allocation. Lift the left and right subtype families;
if the right certificate avoids its subtype cut, the two lifts satisfy the
ambient join interface. -/
theorem liftedFamilies_join_of_right_avoids_cut
    (D : OneVertexSeparation G)
    (P : Finset (Finset ↥(↑D.left : Set V)))
    (Q : Finset (Finset ↥(↑D.right : Set V)))
    (hP : GraphConjecture40PathFamily.IsPathSupportFamily
      (G.induce (↑D.left : Set V)) P)
    (hcutQ : (⟨D.cut, D.cut_mem_right⟩ : ↥(↑D.right : Set V)) ∉
      GraphConjecture40PathFamily.coveredVertices Q) :
    PathFamilyJoin G (liftFamily D.left P) (liftFamily D.right Q) := by
  have hcross : ∀ s ∈ liftFamily D.left P, ∀ t ∈ liftFamily D.right Q,
      Disjoint s t := by
    intro s hs t ht
    obtain ⟨s₀, hs₀, rfl⟩ := mem_map.mp hs
    obtain ⟨t₀, ht₀, rfl⟩ := mem_map.mp ht
    rw [Finset.disjoint_left]
    intro x hxs hxt
    obtain ⟨xL, hxLs, hxL⟩ := mem_map.mp hxs
    obtain ⟨xR, hxRt, hxR⟩ := mem_map.mp hxt
    have hxval : xL.1 = xR.1 := by simpa [supportLiftEmbedding] using hxL.trans hxR.symm
    have hxinter : xL.1 ∈ D.left ∩ D.right :=
      mem_inter.mpr ⟨xL.2, hxval ▸ xR.2⟩
    have hxc : xL.1 = D.cut := by simpa [D.inter] using hxinter
    apply hcutQ
    apply GraphConjecture40PathFamily.mem_coveredVertices_iff.mpr
    refine ⟨t₀, ht₀, ?_⟩
    have hxRcut : xR = ⟨D.cut, D.cut_mem_right⟩ := by
      apply Subtype.ext
      exact hxval.symm.trans hxc
    simpa [hxRcut] using hxRt
  refine ⟨?_, hcross⟩
  rw [Finset.disjoint_left]
  intro s hsP hsQ
  have hss : Disjoint s s := hcross s hsP s hsQ
  have hsempty : s = ∅ := (Finset.disjoint_self_iff_empty s).mp hss
  obtain ⟨s₀, hs₀, hsmap⟩ := mem_map.mp hsP
  have hs₀ne := support_nonempty_of_mem_pathFamily
    (G.induce (↑D.left : Set V)) P hP hs₀
  have hne : (s₀.map (Function.Embedding.subtype _)).Nonempty := hs₀ne.map
  have hzero : s₀.map (Function.Embedding.subtype _) = ∅ := by
    rw [← hsempty, ← hsmap]
    rfl
  rw [hzero] at hne
  exact not_nonempty_empty hne

/-- End-to-end include composition directly from subtype side certificates. -/
theorem conjecture40_of_bipartite_of_include_subtype_families
    (D : OneVertexSeparation G) (hG : G.IsBipartite)
    (hdom : excludeStateSum D ≤ includeStateSum D)
    {kL kR : ℕ}
    (hL : includeDeficiency (G.induce (↑D.left : Set V))
      ⟨D.cut, D.cut_mem_left⟩ = kL)
    (hR : includeDeficiency (G.induce (↑D.right : Set V))
      ⟨D.cut, D.cut_mem_right⟩ = kR)
    (P : Finset (Finset ↥(↑D.left : Set V)))
    (Q : Finset (Finset ↥(↑D.right : Set V)))
    (hP : GraphConjecture40PathFamily.IsPathSupportFamily
      (G.induce (↑D.left : Set V)) P)
    (hQ : GraphConjecture40PathFamily.IsPathSupportFamily
      (G.induce (↑D.right : Set V)) Q)
    (hcutQ : (⟨D.cut, D.cut_mem_right⟩ : ↥(↑D.right : Set V)) ∉
      GraphConjecture40PathFamily.coveredVertices Q)
    (hPL : P.card + (2 * kL + 1) ≤
      (GraphConjecture40PathFamily.coveredVertices P).card)
    (hQR : Q.card + (2 * kR + 1) ≤
      (GraphConjecture40PathFamily.coveredVertices Q).card) :
    ⌈(((pathCoverNumber G : ℝ) + b G + 1) / 2)⌉ ≤
      G.largestInducedForestSize := by
  have hPlift := liftFamily_isPathSupportFamily D.left P hP
  have hQlift := liftFamily_isPathSupportFamily D.right Q hQ
  have hjoin := liftedFamilies_join_of_right_avoids_cut D P Q hP hcutQ
  exact conjecture40_of_bipartite_of_include_branch_join
    D hG hdom hL hR _ _ hPlift hQlift hjoin
      (liftFamily_rank D.left P hPL) (liftFamily_rank D.right Q hQR)

end WrittenOnTheWallII.GraphConjecture40SubtypePathTransport
