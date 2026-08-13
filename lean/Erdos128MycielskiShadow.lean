import FormalConjecturesUtil

/-!
# Erdős 128: the Mycielski shadow obstruction

The classical Mycielski construction has one original and one shadow copy of
every input vertex, plus an apex.  Its entire shadow level is independent and
has exactly the threshold size in the formal Erdős 128 premise.  Consequently
no classical Mycielski graph can satisfy that strict positive induced-density
premise.
-/

namespace Erdos128.MycielskiShadow

open SimpleGraph

universe u

/-- Vertices of the classical Mycielski graph: original/shadow levels and one
apex. -/
abbrev MycVerts (V : Type u) : Type u := (Bool × V) ⊕ Unit

/-- Symmetric adjacency relation for the classical Mycielski construction.
`false` is the original level and `true` is the shadow level. -/
def mycAdj {V : Type u} (G : SimpleGraph V) : MycVerts V → MycVerts V → Prop
  | Sum.inl (false, u), Sum.inl (false, v) => G.Adj u v
  | Sum.inl (false, u), Sum.inl (true, v) => G.Adj u v
  | Sum.inl (true, u), Sum.inl (false, v) => G.Adj u v
  | Sum.inl (true, _), Sum.inl (true, _) => False
  | Sum.inl (false, _), Sum.inr () => False
  | Sum.inr (), Sum.inl (false, _) => False
  | Sum.inl (true, _), Sum.inr () => True
  | Sum.inr (), Sum.inl (true, _) => True
  | Sum.inr (), Sum.inr () => False

/-- The classical Mycielski graph. -/
def mycielski {V : Type u} (G : SimpleGraph V) : SimpleGraph (MycVerts V) :=
  SimpleGraph.fromRel (mycAdj G)

/-- The shadow level as a vertex set. -/
def shadowSet (V : Type u) : Set (MycVerts V) :=
  Set.range fun v : V ↦ Sum.inl (true, v)

/-- The shadow embedding is injective. -/
lemma shadowEmbedding_injective (V : Type u) :
    Function.Injective (fun v : V ↦ (Sum.inl (true, v) : MycVerts V)) := by
  intro u v huv
  simpa using huv

/-- The shadow level has exactly one vertex per input vertex. -/
theorem shadowSet_ncard [Fintype V] :
    (shadowSet V).ncard = Fintype.card V := by
  rw [shadowSet, Set.ncard_range_of_injective (shadowEmbedding_injective V)]
  exact Nat.card_eq_fintype_card

/-- The classical Mycielski graph has order `2*n+1`. -/
theorem card_mycVerts [Fintype V] :
    Fintype.card (MycVerts V) = 2 * Fintype.card V + 1 := by
  simp [MycVerts]

/-- Shadow vertices are pairwise nonadjacent in the full Mycielski graph. -/
theorem shadowSet_independent (G : SimpleGraph V) :
    (mycielski G).IsIndepSet (shadowSet V) := by
  intro x hx y hy hxy hadj
  obtain ⟨u, rfl⟩ := hx
  obtain ⟨v, rfl⟩ := hy
  simp [mycielski, mycAdj] at hadj

/-- The shadow level meets the formal Erdős 128 eligible-set threshold with
equality. -/
theorem shadowSet_meets_half_threshold [Fintype V] :
    2 * (shadowSet V).ncard + 1 ≥ Fintype.card (MycVerts V) := by
  rw [shadowSet_ncard, card_mycVerts]

/-- An independent finite set induces no edges. -/
theorem induced_edgeSet_ncard_eq_zero_of_independent
    {W : Type u} (H : SimpleGraph W) (S : Set W)
    (hS : H.IsIndepSet S) :
    (H.induce S).edgeSet.ncard = 0 := by
  have hbot : H.induce S = ⊥ := by
    ext x y
    simp only [induce_adj, bot_adj, iff_false]
    intro hxy
    exact hS x.property y.property hxy.ne hxy
  rw [hbot]
  simp

/-- Abstract obstruction behind the computation: any independent eligible set
refutes the strict positive induced-density premise, for every positive
coefficient and in particular for coefficient `50`. -/
theorem strict_density_premise_fails_of_independent_eligible
    {W : Type u} [Fintype W] (H : SimpleGraph W) (S : Set W)
    (hS : H.IsIndepSet S)
    (heligible : 2 * S.ncard + 1 ≥ Fintype.card W) :
    ¬(∀ T : Set W, 2 * T.ncard + 1 ≥ Fintype.card W →
        50 * (H.induce T).edgeSet.ncard > Fintype.card W ^ 2) := by
  intro hpremise
  have hpositive := hpremise S heligible
  rw [induced_edgeSet_ncard_eq_zero_of_independent H S hS] at hpositive
  simp at hpositive

/-- No classical Mycielski graph satisfies the strict premise in the current
Formal Conjectures statement of Erdős Problem 128. -/
theorem mycielski_strict_density_premise_fails [Fintype V] (G : SimpleGraph V) :
    ¬(∀ T : Set (MycVerts V),
      2 * T.ncard + 1 ≥ Fintype.card (MycVerts V) →
        50 * ((mycielski G).induce T).edgeSet.ncard >
          Fintype.card (MycVerts V) ^ 2) := by
  exact strict_density_premise_fails_of_independent_eligible
    (mycielski G) (shadowSet V) (shadowSet_independent G)
      shadowSet_meets_half_threshold

end Erdos128.MycielskiShadow
