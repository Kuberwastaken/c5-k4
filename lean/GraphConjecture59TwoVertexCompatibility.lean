import GraphConjecture59AlignedTripleBridge

/-!
# WOWII 59: two-vertex compatibility beyond the aligned five-set

The favorable aligned five-set has bipartition `{a,b} | {x,y,z}`.  Two new
vertices extend it to seven whenever one is compatible with each color side.
-/

namespace WrittenOnTheWallII.GraphConjecture59TwoVertexCompatibility

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture59AlignedTripleBridge

universe u
variable {V : Type u} [Fintype V] [DecidableEq V]

/-- Pairwise distinctness of the aligned five vertices and two extensions. -/
def PairwiseDistinctSeven (a b x y z p q : V) : Prop :=
  PairwiseDistinctFive a b x y z ∧
  p ≠ a ∧ p ≠ b ∧ p ≠ x ∧ p ≠ y ∧ p ≠ z ∧
  q ≠ a ∧ q ≠ b ∧ q ≠ x ∧ q ≠ y ∧ q ≠ z ∧ p ≠ q

/-- The smallest color-side compatibility data for the asymmetric extension:
`p` joins the outside color class and therefore avoids the outside triple,
while `q` joins the core color class and avoids the two cores.  No condition
on `p-q` or on cross-color edges is needed. -/
def OppositeSideCompatible (G : SimpleGraph V)
    (a b x y z p q : V) : Prop :=
  ¬G.Adj p x ∧ ¬G.Adj p y ∧ ¬G.Adj p z ∧
  ¬G.Adj q a ∧ ¬G.Adj q b

omit [Fintype V] in
/-- The aligned five coloring extends to seven vertices from exactly the
within-color nonedges; every cross-color adjacency is unrestricted. -/
theorem aligned_seven_isBipartite
    (G : SimpleGraph V) (a b x y z p q : V)
    (halign : AlignedOutsideTriple G a b x y z)
    (hdist : PairwiseDistinctSeven a b x y z p q)
    (hab : ¬G.Adj a b)
    (hout : RealizesOutsideType G x y z .independent)
    (hcompat : OppositeSideCompatible G a b x y z p q) :
    (G.induce (({a, b, x, y, z, p, q} : Finset V) : Set V)).IsBipartite := by
  rw [induce_isBipartite_iff_exists_coloring]
  refine ⟨fun v ↦ if v = a ∨ v = b ∨ v = q then 0 else 1, ?_⟩
  intro r hr s hs hrs
  simp only [mem_insert, mem_singleton] at hr hs
  rcases hdist with
    ⟨⟨habV, haxV, hayV, hazV, hbxV, hbyV, hbzV, hxyV, hxzV, hyzV⟩,
      hpa, hpb, hpx, hpy, hpz, hqa, hqb, hqx, hqy, hqz, hpq⟩
  rcases hout with ⟨hxy, hxz, hyz⟩
  rcases hcompat with ⟨hpxE, hpyE, hpzE, hqaE, hqbE⟩
  by_cases hr0 : r = a ∨ r = b ∨ r = q
  · by_cases hs0 : s = a ∨ s = b ∨ s = q
    · exfalso
      rcases hr0 with rfl | rfl | rfl <;> rcases hs0 with rfl | rfl | rfl <;>
        simp_all [G.adj_comm]
    · simp [hr0, hs0]
  · by_cases hs0 : s = a ∨ s = b ∨ s = q
    · simp [hr0, hs0]
    · exfalso
      rcases hr with rfl | rfl | rfl | rfl | rfl | rfl | rfl <;>
        rcases hs with rfl | rfl | rfl | rfl | rfl | rfl | rfl <;>
        simp_all [AlignedOutsideTriple, G.adj_comm]

/-- The compatible two-vertex extension supplies the desired seven-vertex
induced-bipartite witness. -/
theorem seven_le_b_of_aligned_compatible_extensions
    (G : SimpleGraph V) (a b x y z p q : V)
    (halign : AlignedOutsideTriple G a b x y z)
    (hdist : PairwiseDistinctSeven a b x y z p q)
    (hab : ¬G.Adj a b)
    (hout : RealizesOutsideType G x y z .independent)
    (hcompat : OppositeSideCompatible G a b x y z p q) :
    7 ≤ G.largestInducedBipartiteSubgraphSize := by
  have hbip := aligned_seven_isBipartite G a b x y z p q
    halign hdist hab hout hcompat
  have hcard : ({a, b, x, y, z, p, q} : Finset V).card = 7 := by
    rcases hdist with
      ⟨⟨habV, haxV, hayV, hazV, hbxV, hbyV, hbzV, hxyV, hxzV, hyzV⟩,
        hpa, hpb, hpx, hpy, hpz, hqa, hqb, hqx, hqy, hqz, hpq⟩
    have hn : [a, b, x, y, z, p, q].Nodup := by
      simp_all [ne_comm]
    calc
      ({a, b, x, y, z, p, q} : Finset V).card =
          [a, b, x, y, z, p, q].toFinset.card := by
            congr 1
            ext r
            simp
      _ = 7 := by simpa using List.toFinset_card_of_nodup hn
  have hbound :=
    _root_.WrittenOnTheWallII.GraphConjecture40Baseline.card_le_largestInducedBipartiteSubgraphSize
      G ({a, b, x, y, z, p, q} : Finset V) hbip
  simpa [hcard] using hbound

omit [Fintype V] in
/-- One missing within-side nonedge is genuinely necessary for this fixed
coloring: if `q-a` is an edge, the proposed coloring cannot be proper. -/
theorem edge_to_core_blocks_fixed_extension_coloring
    (G : SimpleGraph V) (a b x y z p q : V) (hqa : G.Adj q a) :
    ¬(∀ r ∈ ({a, b, x, y, z, p, q} : Finset V),
      ∀ s ∈ ({a, b, x, y, z, p, q} : Finset V), G.Adj r s →
        (if r = a ∨ r = b ∨ r = q then (0 : Fin 2) else 1) ≠
        (if s = a ∨ s = b ∨ s = q then (0 : Fin 2) else 1)) := by
  intro hc
  have := hc q (by simp) a (by simp) hqa
  simp at this

end WrittenOnTheWallII.GraphConjecture59TwoVertexCompatibility
