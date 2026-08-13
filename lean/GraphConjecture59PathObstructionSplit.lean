import GraphConjecture59PathBranch

/-!
# WOWII 59: complete obstruction split for the path exchange

Try the v24 endpoint exchange with aligned core `a`, then with aligned core
`b`.  Simultaneous failure has exactly two causes: `q` meets the outside
triple, or `p` is adjacent to both aligned cores and to `q`.
-/

namespace WrittenOnTheWallII.GraphConjecture59PathObstructionSplit

open SimpleGraph
open WrittenOnTheWallII.GraphConjecture59AlignedTripleBridge
open WrittenOnTheWallII.GraphConjecture59TwoVertexCompatibility
open WrittenOnTheWallII.GraphConjecture59PathBranch

universe u
variable {V : Type u} [Fintype V] [DecidableEq V]

/-- The first obstruction family: `q` has an outside neighbor. -/
def QHitsOutside (G : SimpleGraph V) (x y z q : V) : Prop :=
  G.Adj q x ∨ G.Adj q y ∨ G.Adj q z

/-- The second obstruction family: the extension `p` forms a three-edge fan
to both aligned cores and the other extension. -/
def CoreExtensionFan (G : SimpleGraph V) (a b p q : V) : Prop :=
  G.Adj p q ∧ G.Adj p a ∧ G.Adj p b

omit [Fintype V] [DecidableEq V] in
/-- Exact propositional normal form for simultaneous failure of the two
aligned-core exchanges. -/
theorem both_exchange_failures_iff
    (G : SimpleGraph V) (a b x y z p q : V) :
    (¬PathExchangeCompatible G a x y z p q ∧
      ¬PathExchangeCompatible G b x y z p q) ↔
    QHitsOutside G x y z q ∨ CoreExtensionFan G a b p q := by
  classical
  simp only [PathExchangeCompatible, QHitsOutside, CoreExtensionFan,
    not_and_or, not_not]
  tauto

omit [Fintype V] [DecidableEq V] in
/-- Pairwise distinctness is invariant under swapping the two aligned cores.
-/
theorem pairwiseDistinctSeven_swap_cores
    (a b x y z p q : V)
    (h : PairwiseDistinctSeven a b x y z p q) :
    PairwiseDistinctSeven b a x y z p q := by
  rcases h with ⟨⟨hab, hax, hay, haz, hbx, hby, hbz, hxy, hxz, hyz⟩,
    hpa, hpb, hpx, hpy, hpz, hqa, hqb, hqx, hqy, hqz, hpq⟩
  exact ⟨⟨hab.symm, hbx, hby, hbz, hax, hay, haz, hxy, hxz, hyz⟩,
    hpb, hpa, hpx, hpy, hpz, hqb, hqa, hqx, hqy, hqz, hpq⟩

omit [Fintype V] [DecidableEq V] in
/-- The v21 compatibility data are likewise invariant under swapping the two
aligned cores. -/
theorem oppositeSideCompatible_swap_cores
    (G : SimpleGraph V) (a b x y z p q : V)
    (h : OppositeSideCompatible G a b x y z p q) :
    OppositeSideCompatible G b a x y z p q := by
  rcases h with ⟨hpx, hpy, hpz, hqa, hqb⟩
  exact ⟨hpx, hpy, hpz, hqb, hqa⟩

/-- **Complete path-branch split.** One of the two aligned-core exchanges
gives `f(G) ≥ 5`, unless one of the two exact obstruction families occurs. -/
theorem five_le_f_or_complete_path_obstruction
    (G : SimpleGraph V) (a b x y z p q : V)
    (hdist : PairwiseDistinctSeven a b x y z p q)
    (hout : RealizesOutsideType G x y z .path)
    (hcompat : OppositeSideCompatible G a b x y z p q) :
    5 ≤ G.largestInducedForestSize ∨
      QHitsOutside G x y z q ∨ CoreExtensionFan G a b p q := by
  classical
  by_cases ha : PathExchangeCompatible G a x y z p q
  · exact Or.inl <| five_le_f_of_path_branch
      G a b x y z p q hdist hout hcompat ha
  · by_cases hb : PathExchangeCompatible G b x y z p q
    · exact Or.inl <| five_le_f_of_path_branch G b a x y z p q
        (pairwiseDistinctSeven_swap_cores a b x y z p q hdist) hout
        (oppositeSideCompatible_swap_cores G a b x y z p q hcompat) hb
    · exact Or.inr <| (both_exchange_failures_iff G a b x y z p q).mp ⟨ha, hb⟩

/-- If `q` avoids the outside triple and the three-edge fan is absent, the
alternate-core argument closes the path branch with `f(G) ≥ 5`. -/
theorem five_le_f_of_no_complete_path_obstruction
    (G : SimpleGraph V) (a b x y z p q : V)
    (hdist : PairwiseDistinctSeven a b x y z p q)
    (hout : RealizesOutsideType G x y z .path)
    (hcompat : OppositeSideCompatible G a b x y z p q)
    (hq : ¬QHitsOutside G x y z q)
    (hfan : ¬CoreExtensionFan G a b p q) :
    5 ≤ G.largestInducedForestSize := by
  rcases five_le_f_or_complete_path_obstruction G a b x y z p q
      hdist hout hcompat with hf | hq' | hfan'
  · exact hf
  · exact False.elim (hq hq')
  · exact False.elim (hfan hfan')

end WrittenOnTheWallII.GraphConjecture59PathObstructionSplit
