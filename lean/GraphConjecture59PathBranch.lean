import GraphConjecture59OneEdgeBranch

/-!
# WOWII 59: path outside-triple core exchange

Delete the center of the outside path and one aligned core.  The two path
endpoints are nonadjacent, leaving a five-vertex `3 × 2` incidence graph.
Controlling double neighbors across that cut gives an induced forest of order
five.  A four-cycle records the first missing adjacency obstruction.
-/

namespace WrittenOnTheWallII.GraphConjecture59PathBranch

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture59AlignedTripleBridge
open WrittenOnTheWallII.GraphConjecture59TwoVertexCompatibility

universe u
variable {V : Type u} [Fintype V] [DecidableEq V]

/-- Distinctness for one aligned core, two path endpoints, and both extension
vertices. -/
def PairwiseDistinctExchangeFive (a u v p q : V) : Prop :=
  a ≠ u ∧ a ≠ v ∧ a ≠ p ∧ a ≠ q ∧
  u ≠ v ∧ u ≠ p ∧ u ≠ q ∧
  v ≠ p ∧ v ≠ q ∧ p ≠ q

/-- Exact data used by the simple forest builder.  The left side
`{u,v,p}` is independent; `a,q` is a nonedge; and every left vertex has at
most one neighbor on the right. -/
def EndpointForestCompatible (G : SimpleGraph V) (a u v p q : V) : Prop :=
  ¬G.Adj u v ∧ ¬G.Adj p u ∧ ¬G.Adj p v ∧
  ¬G.Adj q a ∧ ¬G.Adj q u ∧ ¬G.Adj q v ∧
  (¬G.Adj p a ∨ ¬G.Adj p q)

omit [Fintype V] in
/-- The exchanged five-set is acyclic under the endpoint compatibility data.
The aligned edges `a-u` and `a-v` are allowed but not needed by acyclicity. -/
theorem endpoint_exchange_isAcyclic
    (G : SimpleGraph V) (a u v p q : V)
    (hcompat : EndpointForestCompatible G a u v p q) :
    (G.induce (({a, u, v, p, q} : Finset V) : Set V)).IsAcyclic := by
  rcases hcompat with ⟨huv, hpu, hpv, hqa, hqu, hqv, hpa | hpq⟩
  all_goals
    have hI : G.IsIndepSet (({u, v, p} : Finset V) : Set V) := by
      intro r hr s hs hrs hadj
      change r ∈ ({u, v, p} : Finset V) at hr
      change s ∈ ({u, v, p} : Finset V) at hs
      simp only [mem_insert, mem_singleton] at hr hs
      rcases hr with rfl | rfl | rfl <;> rcases hs with rfl | rfl | rfl <;>
        simp_all [G.adj_comm]
    have hX : G.IsIndepSet (({a, q} : Finset V) : Set V) := by
      intro r hr s hs hrs hadj
      change r ∈ ({a, q} : Finset V) at hr
      change s ∈ ({a, q} : Finset V) at hs
      simp only [mem_insert, mem_singleton] at hr hs
      rcases hr with rfl | rfl <;> rcases hs with rfl | rfl <;>
        simp_all [G.adj_comm]
    have huniq : ∀ i ∈ (({u, v, p} : Finset V) : Set V),
        ∀ x ∈ (({a, q} : Finset V) : Set V),
        ∀ y ∈ (({a, q} : Finset V) : Set V),
        G.Adj i x → G.Adj i y → x = y := by
      intro i hi x hx y hy hix hiy
      change i ∈ ({u, v, p} : Finset V) at hi
      change x ∈ ({a, q} : Finset V) at hx
      change y ∈ ({a, q} : Finset V) at hy
      simp only [mem_insert, mem_singleton] at hi hx hy
      rcases hi with rfl | rfl | rfl <;> rcases hx with rfl | rfl <;>
        rcases hy with rfl | rfl <;> simp_all [G.adj_comm]
    have hacyc :=
      _root_.WrittenOnTheWallII.GraphConjecture40Baseline.induce_union_isAcyclic_of_left_unique_neighbor
        G (({u, v, p} : Finset V) : Set V) (({a, q} : Finset V) : Set V)
        hI hX huniq
    have hset :
        (({a, u, v, p, q} : Finset V) : Set V) =
          (({u, v, p} : Finset V) : Set V) ∪
          (({a, q} : Finset V) : Set V) := by
      ext r
      change r ∈ ({a, u, v, p, q} : Finset V) ↔
        r ∈ ({u, v, p} : Finset V) ∨ r ∈ ({a, q} : Finset V)
      simp only [mem_insert, mem_singleton]
      tauto
    rw [hset]
    exact hacyc

/-- The exchanged five-set yields the desired `f(G) ≥ 5` exit. -/
theorem five_le_f_of_endpoint_exchange
    (G : SimpleGraph V) (a u v p q : V)
    (hdist : PairwiseDistinctExchangeFive a u v p q)
    (hcompat : EndpointForestCompatible G a u v p q) :
    5 ≤ G.largestInducedForestSize := by
  have hacyc := endpoint_exchange_isAcyclic G a u v p q hcompat
  have hcard : ({a, u, v, p, q} : Finset V).card = 5 := by
    rcases hdist with ⟨hau, hav, hap, haq, huv, hup, huq, hvp, hvq, hpq⟩
    simp [hau, hav, hap, haq, huv, hup, huq, hvp, hvq, hpq]
  have hbound :=
    _root_.WrittenOnTheWallII.GraphConjecture40Baseline.card_le_largestInducedForestSize
      G ({a, u, v, p, q} : Finset V) hacyc
  simpa [hcard] using hbound

/-- The extra nonedges missing from v21 and sufficient uniformly for all
three labeled path orientations. -/
def PathExchangeCompatible (G : SimpleGraph V) (a x y z p q : V) : Prop :=
  ¬G.Adj q x ∧ ¬G.Adj q y ∧ ¬G.Adj q z ∧
  (¬G.Adj p a ∨ ¬G.Adj p q)

/-- **Path-branch forest exit.** Delete the path center and aligned core `b`;
the remaining five vertices induce a forest under the stated missing
double-neighbor condition. -/
theorem five_le_f_of_path_branch
    (G : SimpleGraph V) (a b x y z p q : V)
    (hdist : PairwiseDistinctSeven a b x y z p q)
    (hout : RealizesOutsideType G x y z .path)
    (hcompat : OppositeSideCompatible G a b x y z p q)
    (hexchange : PathExchangeCompatible G a x y z p q) :
    5 ≤ G.largestInducedForestSize := by
  rcases hdist with ⟨hfive, hpa, hpb, hpx, hpy, hpz,
    hqa, hqb, hqx, hqy, hqz, hpq⟩
  rcases hfive with ⟨habV, haxV, hayV, hazV, hbxV, hbyV, hbzV,
    hxyV, hxzV, hyzV⟩
  rcases hcompat with ⟨hpxE, hpyE, hpzE, hqaE, hqbE⟩
  rcases hexchange with ⟨hqxE, hqyE, hqzE, hpaE⟩
  rcases hout with h | h | h
  · exact five_le_f_of_endpoint_exchange G a y z p q
      ⟨hayV, hazV, hpa.symm, hqa.symm, hyzV, hpy.symm, hqy.symm,
        hpz.symm, hqz.symm, hpq⟩
      ⟨h.2.2, hpyE, hpzE, hqaE, hqyE, hqzE, hpaE⟩
  · exact five_le_f_of_endpoint_exchange G a x z p q
      ⟨haxV, hazV, hpa.symm, hqa.symm, hxzV, hpx.symm, hqx.symm,
        hpz.symm, hqz.symm, hpq⟩
      ⟨h.2.2, hpxE, hpzE, hqaE, hqxE, hqzE, hpaE⟩
  · exact five_le_f_of_endpoint_exchange G a x y p q
      ⟨haxV, hayV, hpa.symm, hqa.symm, hxyV, hpx.symm, hqx.symm,
        hpy.symm, hqy.symm, hpq⟩
      ⟨h.2.2, hpxE, hpyE, hqaE, hqxE, hqyE, hpaE⟩

omit [Fintype V] in
/-- Smallest explicit obstruction to the exchange: if `q` sees both path
endpoints, the candidate five-set contains the four-cycle `a-u-q-v-a`. -/
theorem endpoint_double_neighbor_blocks_exchange
    (G : SimpleGraph V) (a u v p q : V)
    (hdist : PairwiseDistinctExchangeFive a u v p q)
    (hau : G.Adj a u) (hav : G.Adj a v)
    (hqu : G.Adj q u) (hqv : G.Adj q v) :
    ¬(G.induce (({a, u, v, p, q} : Finset V) : Set V)).IsAcyclic := by
  intro hacyc
  rcases hdist with ⟨hauV, havV, hapV, haqV, huvV, hupV, huqV,
    hvpV, hvqV, hpqV⟩
  let A : ↑((({a, u, v, p, q} : Finset V) : Set V)) := ⟨a, by simp⟩
  let U : ↑((({a, u, v, p, q} : Finset V) : Set V)) := ⟨u, by simp⟩
  let Q : ↑((({a, u, v, p, q} : Finset V) : Set V)) := ⟨q, by simp⟩
  let W : ↑((({a, u, v, p, q} : Finset V) : Set V)) := ⟨v, by simp⟩
  have hAU : (G.induce _).Adj A U := hau
  have hUQ : (G.induce _).Adj U Q := hqu.symm
  have hQW : (G.induce _).Adj Q W := hqv
  have hWA : (G.induce _).Adj W A := hav.symm
  let c := Walk.cons hAU (Walk.cons hUQ (Walk.cons hQW (Walk.cons hWA Walk.nil)))
  have hc : c.IsCycle := by
    rw [Walk.isCycle_def]
    refine ⟨?_, ?_, ?_⟩
    · rw [Walk.isTrail_def]
      simp [c, A, U, Q, W, hauV, havV, haqV, huvV, huqV, hvqV, ne_comm]
    · simp [c]
    · simp [c]
      refine ⟨⟨?_, ?_, ?_⟩, ⟨?_, ?_⟩, ?_⟩
      · intro h; exact huqV (congrArg Subtype.val h)
      · intro h; exact huvV (congrArg Subtype.val h)
      · intro h; exact hauV.symm (congrArg Subtype.val h)
      · intro h; exact hvqV.symm (congrArg Subtype.val h)
      · intro h; exact haqV.symm (congrArg Subtype.val h)
      · intro h; exact havV.symm (congrArg Subtype.val h)
  exact hacyc c hc

end WrittenOnTheWallII.GraphConjecture59PathBranch
