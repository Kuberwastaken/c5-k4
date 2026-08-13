import GraphConjecture59PathObstructionSplit

/-!
# WOWII 59: closure of the complete-fan path obstruction

When `q` avoids the outside triple, discard both aligned cores.  The outside
path together with `p,q` is a five-vertex forest: the extensions are
anticomplete to the path, apart from the unrestricted edge `p-q`.  Hence the
complete core-extension fan from v25 is irrelevant; only an outside neighbor
of `q` survives.
-/

namespace WrittenOnTheWallII.GraphConjecture59PathFanClosure

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture59AlignedTripleBridge
open WrittenOnTheWallII.GraphConjecture59TwoVertexCompatibility
open WrittenOnTheWallII.GraphConjecture59PathBranch
open WrittenOnTheWallII.GraphConjecture59PathObstructionSplit

universe u
variable {V : Type u} [Fintype V] [DecidableEq V]

/-- Distinctness for a labeled path and the two extension vertices. -/
def PairwiseDistinctPathExtensions (u c v p q : V) : Prop :=
  u ≠ c ∧ u ≠ v ∧ u ≠ p ∧ u ≠ q ∧
  c ≠ v ∧ c ≠ p ∧ c ≠ q ∧
  v ≠ p ∧ v ≠ q ∧ p ≠ q

omit [Fintype V] in
/-- A three-vertex path and an extension pair induce a forest when both
extensions avoid the path.  The edge `p-q` is unrestricted. -/
theorem path_extensions_isAcyclic
    (G : SimpleGraph V) (u c v p q : V)
    (huv : ¬G.Adj u v)
    (hpu : ¬G.Adj p u) (hpc : ¬G.Adj p c) (hpv : ¬G.Adj p v)
    (hqu : ¬G.Adj q u) (hqc : ¬G.Adj q c) (hqv : ¬G.Adj q v) :
    (G.induce (({u, c, v, p, q} : Finset V) : Set V)).IsAcyclic := by
  have hI : G.IsIndepSet (({u, v, p} : Finset V) : Set V) := by
    intro r hr s hs hrs hadj
    change r ∈ ({u, v, p} : Finset V) at hr
    change s ∈ ({u, v, p} : Finset V) at hs
    simp only [mem_insert, mem_singleton] at hr hs
    rcases hr with rfl | rfl | rfl <;> rcases hs with rfl | rfl | rfl <;>
      simp_all [G.adj_comm]
  have hX : G.IsIndepSet (({c, q} : Finset V) : Set V) := by
    intro r hr s hs hrs hadj
    change r ∈ ({c, q} : Finset V) at hr
    change s ∈ ({c, q} : Finset V) at hs
    simp only [mem_insert, mem_singleton] at hr hs
    rcases hr with rfl | rfl <;> rcases hs with rfl | rfl <;>
      simp_all [G.adj_comm]
  have huniq : ∀ i ∈ (({u, v, p} : Finset V) : Set V),
      ∀ x ∈ (({c, q} : Finset V) : Set V),
      ∀ y ∈ (({c, q} : Finset V) : Set V),
      G.Adj i x → G.Adj i y → x = y := by
    intro i hi x hx y hy hix hiy
    change i ∈ ({u, v, p} : Finset V) at hi
    change x ∈ ({c, q} : Finset V) at hx
    change y ∈ ({c, q} : Finset V) at hy
    simp only [mem_insert, mem_singleton] at hi hx hy
    rcases hi with rfl | rfl | rfl <;> rcases hx with rfl | rfl <;>
      rcases hy with rfl | rfl <;> simp_all [G.adj_comm]
  have hacyc :=
    _root_.WrittenOnTheWallII.GraphConjecture40Baseline.induce_union_isAcyclic_of_left_unique_neighbor
      G (({u, v, p} : Finset V) : Set V) (({c, q} : Finset V) : Set V)
      hI hX huniq
  have hset :
      (({u, c, v, p, q} : Finset V) : Set V) =
        (({u, v, p} : Finset V) : Set V) ∪
        (({c, q} : Finset V) : Set V) := by
    ext r
    change r ∈ ({u, c, v, p, q} : Finset V) ↔
      r ∈ ({u, v, p} : Finset V) ∨ r ∈ ({c, q} : Finset V)
    simp only [mem_insert, mem_singleton]
    tauto
  rw [hset]
  exact hacyc

/-- The explicit path-plus-extensions forest proves `f(G) ≥ 5`. -/
theorem five_le_f_of_path_extensions
    (G : SimpleGraph V) (u c v p q : V)
    (hdist : PairwiseDistinctPathExtensions u c v p q)
    (huv : ¬G.Adj u v)
    (hpu : ¬G.Adj p u) (hpc : ¬G.Adj p c) (hpv : ¬G.Adj p v)
    (hqu : ¬G.Adj q u) (hqc : ¬G.Adj q c) (hqv : ¬G.Adj q v) :
    5 ≤ G.largestInducedForestSize := by
  have hacyc := path_extensions_isAcyclic G u c v p q
    huv hpu hpc hpv hqu hqc hqv
  have hcard : ({u, c, v, p, q} : Finset V).card = 5 := by
    rcases hdist with ⟨huc, huvV, hup, huq, hcv, hcp, hcq, hvp, hvq, hpq⟩
    simp [huc, huvV, hup, huq, hcv, hcp, hcq, hvp, hvq, hpq]
  have hbound :=
    _root_.WrittenOnTheWallII.GraphConjecture40Baseline.card_le_largestInducedForestSize
      G ({u, c, v, p, q} : Finset V) hacyc
  simpa [hcard] using hbound

/-- **Fan closure.** For the path outside type, either the outside path plus
the two extensions gives `f(G) ≥ 5`, or `q` has an outside neighbor.  The
complete fan is no longer a surviving obstruction. -/
theorem five_le_f_or_q_hits_outside
    (G : SimpleGraph V) (a b x y z p q : V)
    (hdist : PairwiseDistinctSeven a b x y z p q)
    (hout : RealizesOutsideType G x y z .path)
    (hcompat : OppositeSideCompatible G a b x y z p q) :
    5 ≤ G.largestInducedForestSize ∨ QHitsOutside G x y z q := by
  by_cases hq : QHitsOutside G x y z q
  · exact Or.inr hq
  · left
    have hqx : ¬G.Adj q x := fun h ↦ hq (Or.inl h)
    have hqy : ¬G.Adj q y := fun h ↦ hq (Or.inr (Or.inl h))
    have hqz : ¬G.Adj q z := fun h ↦ hq (Or.inr (Or.inr h))
    rcases hdist with ⟨hfive, hpa, hpb, hpx, hpy, hpz,
      hqa, hqb, hqxV, hqyV, hqzV, hpq⟩
    rcases hfive with ⟨habV, haxV, hayV, hazV, hbxV, hbyV, hbzV,
      hxyV, hxzV, hyzV⟩
    rcases hcompat with ⟨hpxE, hpyE, hpzE, hqaE, hqbE⟩
    rcases hout with h | h | h
    · exact five_le_f_of_path_extensions G y x z p q
        ⟨hxyV.symm, hyzV, hpy.symm, hqyV.symm, hxzV, hpx.symm,
          hqxV.symm, hpz.symm, hqzV.symm, hpq⟩
        h.2.2 hpyE hpxE hpzE hqy hqx hqz
    · exact five_le_f_of_path_extensions G x y z p q
        ⟨hxyV, hxzV, hpx.symm, hqxV.symm, hyzV, hpy.symm,
          hqyV.symm, hpz.symm, hqzV.symm, hpq⟩
        h.2.2 hpxE hpyE hpzE hqx hqy hqz
    · exact five_le_f_of_path_extensions G x z y p q
        ⟨hxzV, hxyV, hpx.symm, hqxV.symm, hyzV.symm, hpz.symm,
          hqzV.symm, hpy.symm, hqyV.symm, hpq⟩
        h.2.2 hpxE hpzE hpyE hqx hqz hqy

end WrittenOnTheWallII.GraphConjecture59PathFanClosure
