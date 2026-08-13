import GraphConjecture59IndependentBranch

/-!
# WOWII 59: exact boundary of the one-edge outside branch

One outside edge creates a triangle with either aligned core, so the original
seven-set is not bipartite.  Deleting a suitable endpoint of that edge restores
the v21 coloring on six vertices.  This file formalizes that sharp local drop
from seven to six.
-/

namespace WrittenOnTheWallII.GraphConjecture59OneEdgeBranch

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture59AlignedTripleBridge
open WrittenOnTheWallII.GraphConjecture59TwoVertexCompatibility

universe u
variable {V : Type u} [Fintype V] [DecidableEq V]

/-- Pairwise distinctness for two aligned cores, two retained outside
vertices, and the two compatible extensions. -/
def PairwiseDistinctSix (a b u v p q : V) : Prop :=
  a ≠ b ∧ a ≠ u ∧ a ≠ v ∧ a ≠ p ∧ a ≠ q ∧
  b ≠ u ∧ b ≠ v ∧ b ≠ p ∧ b ≠ q ∧
  u ≠ v ∧ u ≠ p ∧ u ≠ q ∧ v ≠ p ∧ v ≠ q ∧ p ≠ q

/-- The retained outside pair and the extensions obey exactly the within-side
nonedges of the inherited coloring. -/
def SixSideCompatible (G : SimpleGraph V) (a b u v p q : V) : Prop :=
  ¬G.Adj a b ∧ ¬G.Adj u v ∧
  ¬G.Adj p u ∧ ¬G.Adj p v ∧ ¬G.Adj q a ∧ ¬G.Adj q b

omit [Fintype V] in
/-- Deleting one endpoint of the outside edge restores the inherited
bipartition `{a,b,q} | {u,v,p}`. -/
theorem aligned_six_isBipartite
    (G : SimpleGraph V) (a b u v p q : V)
    (hdist : PairwiseDistinctSix a b u v p q)
    (hcompat : SixSideCompatible G a b u v p q) :
    (G.induce (({a, b, u, v, p, q} : Finset V) : Set V)).IsBipartite := by
  rw [induce_isBipartite_iff_exists_coloring]
  refine ⟨fun r ↦ if r = a ∨ r = b ∨ r = q then 0 else 1, ?_⟩
  intro r hr s hs hrs
  simp only [mem_insert, mem_singleton] at hr hs
  rcases hdist with
    ⟨habV, hauV, havV, hapV, haqV, hbuV, hbvV, hbpV, hbqV,
      huvV, hupV, huqV, hvpV, hvqV, hpqV⟩
  rcases hcompat with ⟨hab, huv, hpu, hpv, hqa, hqb⟩
  by_cases hr0 : r = a ∨ r = b ∨ r = q
  · by_cases hs0 : s = a ∨ s = b ∨ s = q
    · exfalso
      rcases hr0 with rfl | rfl | rfl <;> rcases hs0 with rfl | rfl | rfl <;>
        simp_all [G.adj_comm]
    · simp [hr0, hs0]
  · by_cases hs0 : s = a ∨ s = b ∨ s = q
    · simp [hr0, hs0]
    · exfalso
      rcases hr with rfl | rfl | rfl | rfl | rfl | rfl <;>
        rcases hs with rfl | rfl | rfl | rfl | rfl | rfl <;>
        simp_all [G.adj_comm]

/-- The explicit restored six-set yields `b(G) ≥ 6`. -/
theorem six_le_b_of_aligned_pair
    (G : SimpleGraph V) (a b u v p q : V)
    (hdist : PairwiseDistinctSix a b u v p q)
    (hcompat : SixSideCompatible G a b u v p q) :
    6 ≤ G.largestInducedBipartiteSubgraphSize := by
  have hbip := aligned_six_isBipartite G a b u v p q hdist hcompat
  have hcard : ({a, b, u, v, p, q} : Finset V).card = 6 := by
    rcases hdist with
      ⟨habV, hauV, havV, hapV, haqV, hbuV, hbvV, hbpV, hbqV,
        huvV, hupV, huqV, hvpV, hvqV, hpqV⟩
    simp [habV, hauV, havV, hapV, haqV, hbuV, hbvV, hbpV, hbqV,
      huvV, hupV, huqV, hvpV, hvqV, hpqV]
  have hbound :=
    _root_.WrittenOnTheWallII.GraphConjecture40Baseline.card_le_largestInducedBipartiteSubgraphSize
      G ({a, b, u, v, p, q} : Finset V) hbip
  simpa [hcard] using hbound

omit [Fintype V] in
/-- Any outside edge forms a triangle with the aligned core `a`, blocking the
full aligned seven-set from being bipartite. -/
theorem outside_edge_blocks_aligned_seven
    (G : SimpleGraph V) (a b x y z p q : V)
    (halign : AlignedOutsideTriple G a b x y z)
    (hedge : G.Adj x y ∨ G.Adj x z ∨ G.Adj y z) :
    ¬(G.induce (({a, b, x, y, z, p, q} : Finset V) : Set V)).IsBipartite := by
  rw [induce_isBipartite_iff_exists_coloring]
  rintro ⟨c, hc⟩
  rcases hedge with hxy | hxz | hyz
  · exact fin_two_not_three_pairwise (c a) (c x) (c y) ⟨
      hc a (by simp) x (by simp) halign.1,
      hc a (by simp) y (by simp) halign.2.1,
      hc x (by simp) y (by simp) hxy⟩
  · exact fin_two_not_three_pairwise (c a) (c x) (c z) ⟨
      hc a (by simp) x (by simp) halign.1,
      hc a (by simp) z (by simp) halign.2.2.1,
      hc x (by simp) z (by simp) hxz⟩
  · exact fin_two_not_three_pairwise (c a) (c y) (c z) ⟨
      hc a (by simp) y (by simp) halign.2.1,
      hc a (by simp) z (by simp) halign.2.2.1,
      hc y (by simp) z (by simp) hyz⟩

/-- Sharp local boundary for the one-edge branch: the full seven-set is
blocked, but deleting a suitable endpoint gives an induced bipartite six-set.
-/
theorem oneEdge_branch_exact_boundary
    (G : SimpleGraph V) (a b x y z p q : V)
    (halign : AlignedOutsideTriple G a b x y z)
    (hdist : PairwiseDistinctSeven a b x y z p q)
    (hab : ¬G.Adj a b)
    (hout : RealizesOutsideType G x y z .oneEdge)
    (hcompat : OppositeSideCompatible G a b x y z p q) :
    6 ≤ G.largestInducedBipartiteSubgraphSize ∧
      ¬(G.induce (({a, b, x, y, z, p, q} : Finset V) : Set V)).IsBipartite := by
  rcases hdist with ⟨hfive, hpa, hpb, hpx, hpy, hpz,
    hqa, hqb, hqx, hqy, hqz, hpq⟩
  rcases hfive with ⟨habV, haxV, hayV, hazV, hbxV, hbyV, hbzV,
    hxyV, hxzV, hyzV⟩
  rcases hcompat with ⟨hpxE, hpyE, hpzE, hqaE, hqbE⟩
  have hblock :
      ¬(G.induce (({a, b, x, y, z, p, q} : Finset V) : Set V)).IsBipartite :=
    outside_edge_blocks_aligned_seven G a b x y z p q halign <| by
      rcases hout with h | h | h
      · exact Or.inl h.1
      · exact Or.inr (Or.inl h.1)
      · exact Or.inr (Or.inr h.1)
  refine ⟨?_, hblock⟩
  rcases hout with hxy | hxz | hyz
  · exact six_le_b_of_aligned_pair G a b x z p q
      ⟨habV, haxV, hazV, hpa.symm, hqa.symm, hbxV, hbzV, hpb.symm,
        hqb.symm, hxzV, hpx.symm, hqx.symm, hpz.symm, hqz.symm, hpq⟩
      ⟨hab, hxy.2.1, hpxE, hpzE, hqaE, hqbE⟩
  · exact six_le_b_of_aligned_pair G a b x y p q
      ⟨habV, haxV, hayV, hpa.symm, hqa.symm, hbxV, hbyV, hpb.symm,
        hqb.symm, hxyV, hpx.symm, hqx.symm, hpy.symm, hqy.symm, hpq⟩
      ⟨hab, hxz.2.1, hpxE, hpyE, hqaE, hqbE⟩
  · exact six_le_b_of_aligned_pair G a b x y p q
      ⟨habV, haxV, hayV, hpa.symm, hqa.symm, hbxV, hbyV, hpb.symm,
        hqb.symm, hxyV, hpx.symm, hqx.symm, hpy.symm, hqy.symm, hpq⟩
      ⟨hab, hyz.2.1, hpxE, hpyE, hqaE, hqbE⟩

end WrittenOnTheWallII.GraphConjecture59OneEdgeBranch
