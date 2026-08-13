import GraphConjecture59TwoVertexCompatibility

/-!
# WOWII 59: discharge of the independent outside-triple branch

The four-way outside-triple classification is combined with the seven-vertex
builder.  Whenever the two compatible extension vertices exist, the
independent branch gives `b(G) ≥ 7`; below that threshold, an outside edge is
therefore forced and only the one-edge, path, and triangle branches remain.
-/

namespace WrittenOnTheWallII.GraphConjecture59IndependentBranch

open SimpleGraph
open WrittenOnTheWallII.GraphConjecture59AlignedTripleBridge
open WrittenOnTheWallII.GraphConjecture59TwoVertexCompatibility

universe u
variable {V : Type u} [Fintype V] [DecidableEq V]

/-- The three non-independent members of the four-way outside-triple split. -/
def NonIndependentOutsideType (G : SimpleGraph V) (x y z : V) : Prop :=
  RealizesOutsideType G x y z .oneEdge ∨
  RealizesOutsideType G x y z .path ∨
  RealizesOutsideType G x y z .triangle

omit [Fintype V] [DecidableEq V] in
/-- The exhaustive four-type classification, grouped at the exact boundary
needed by the seven-vertex builder. -/
theorem independent_or_nonindependent
    (G : SimpleGraph V) (x y z : V) :
    RealizesOutsideType G x y z .independent ∨
      NonIndependentOutsideType G x y z := by
  obtain ⟨τ, hτ⟩ := outside_triple_type_exhaustive G x y z
  cases τ with
  | independent => exact Or.inl hτ
  | oneEdge => exact Or.inr (Or.inl hτ)
  | path => exact Or.inr (Or.inr (Or.inl hτ))
  | triangle => exact Or.inr (Or.inr (Or.inr hτ))

omit [Fintype V] [DecidableEq V] in
/-- Every non-independent outside type contains an explicit outside edge. -/
theorem nonindependent_has_edge
    (G : SimpleGraph V) (x y z : V)
    (h : NonIndependentOutsideType G x y z) :
    G.Adj x y ∨ G.Adj x z ∨ G.Adj y z := by
  rcases h with h | h | h
  · rcases h with h | h | h
    · exact Or.inl h.1
    · exact Or.inr (Or.inl h.1)
    · exact Or.inr (Or.inr h.1)
  · rcases h with h | h | h
    · exact Or.inl h.1
    · exact Or.inl h.1
    · exact Or.inr (Or.inl h.1)
  · exact Or.inl h.1

/-- **Independent-branch exit.** The independent case of the four-way split
feeds directly into the v21 seven-vertex coloring; otherwise one of the three
non-independent types remains. -/
theorem seven_le_b_or_nonindependent
    (G : SimpleGraph V) (a b x y z p q : V)
    (halign : AlignedOutsideTriple G a b x y z)
    (hdist : PairwiseDistinctSeven a b x y z p q)
    (hab : ¬G.Adj a b)
    (hcompat : OppositeSideCompatible G a b x y z p q) :
    7 ≤ G.largestInducedBipartiteSubgraphSize ∨
      NonIndependentOutsideType G x y z := by
  rcases independent_or_nonindependent G x y z with hout | hout
  · exact Or.inl <| seven_le_b_of_aligned_compatible_extensions
      G a b x y z p q halign hdist hab hout hcompat
  · exact Or.inr hout

/-- In the low-bipartite-number corner, compatible extensions rule out the
independent outside triple and force a concrete outside edge. -/
theorem outside_edge_of_b_lt_seven
    (G : SimpleGraph V) (a b x y z p q : V)
    (halign : AlignedOutsideTriple G a b x y z)
    (hdist : PairwiseDistinctSeven a b x y z p q)
    (hab : ¬G.Adj a b)
    (hcompat : OppositeSideCompatible G a b x y z p q)
    (hb : G.largestInducedBipartiteSubgraphSize < 7) :
    G.Adj x y ∨ G.Adj x z ∨ G.Adj y z := by
  rcases seven_le_b_or_nonindependent G a b x y z p q
      halign hdist hab hcompat with hseven | hnon
  · exact False.elim (by omega)
  · exact nonindependent_has_edge G x y z hnon

end WrittenOnTheWallII.GraphConjecture59IndependentBranch
