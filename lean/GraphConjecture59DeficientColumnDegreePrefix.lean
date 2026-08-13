import GraphConjecture59OppositeColumnClosure

/-!
# WOWII 59: exact deficient-column patterns and descending degree prefix

The two forced covers at the endpoint of the unique missing core edge have
six disjoint Boolean realizations.  Only one realizes the minimum degree
five; all other realizations force degree at least six.  The resulting named
degree bounds are then converted to order-statistic counts in the actual
descending degree sequence.
-/

namespace WrittenOnTheWallII.GraphConjecture59DeficientColumnDegreePrefix

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture59CornerStructure
open WrittenOnTheWallII.GraphConjecture59FullFanPropagation
open WrittenOnTheWallII.GraphConjecture59OppositeColumnClosure

universe u
variable {V : Type u} [Fintype V] [DecidableEq V]

/-- Six disjoint attachment patterns surviving the two opposite-column
covers, in coordinate order `u,c,v,p`. -/
def ExactDeficientColumnPattern (G : SimpleGraph V)
    (t u c v p : V) : Prop :=
  (¬G.Adj t u ∧ G.Adj t c ∧ G.Adj t v ∧ G.Adj t p) ∨
  (G.Adj t u ∧ ¬G.Adj t c ∧ G.Adj t v ∧ ¬G.Adj t p) ∨
  (G.Adj t u ∧ ¬G.Adj t c ∧ G.Adj t v ∧ G.Adj t p) ∨
  (G.Adj t u ∧ G.Adj t c ∧ ¬G.Adj t v ∧ G.Adj t p) ∨
  (G.Adj t u ∧ G.Adj t c ∧ G.Adj t v ∧ ¬G.Adj t p) ∨
  (G.Adj t u ∧ G.Adj t c ∧ G.Adj t v ∧ G.Adj t p)

omit [Fintype V] [DecidableEq V] in
/-- The two cover constraints are equivalent to the exact six-pattern table.
-/
theorem two_covers_iff_exact_six_patterns
    (G : SimpleGraph V) (t u c v p : V) :
    (ThirdCoreCover G t p v u ∧ ThirdCoreCover G t v c u) ↔
      ExactDeficientColumnPattern G t u c v p := by
  simp only [ThirdCoreCover, ExactDeficientColumnPattern]
  tauto

/-- The unique degree-five attachment pattern: both path endpoints and
neither the center nor `p`. -/
def MinimalDeficientColumnPattern (G : SimpleGraph V)
    (t u c v p : V) : Prop :=
  G.Adj t u ∧ ¬G.Adj t c ∧ G.Adj t v ∧ ¬G.Adj t p

/-- A noduplicated list of known neighbors bounds the ambient degree. -/
theorem length_le_degree_of_nodup_neighbors
    (G : SimpleGraph V) [DecidableRel G.Adj] (x : V) (L : List V)
    (hnodup : L.Nodup) (hadj : ∀ y ∈ L, G.Adj x y) :
    L.length ≤ G.degree x := by
  let N : Finset V := L.toFinset
  have hNcard : N.card = L.length := by
    simpa [N] using List.toFinset_card_of_nodup hnodup
  have hsub : N ⊆ G.neighborFinset x := by
    intro y hy
    have hyL : y ∈ L := by simpa [N] using hy
    simpa [G.mem_neighborFinset] using hadj y hyL
  have hcard := card_le_card hsub
  rw [hNcard, G.card_neighborFinset_eq_degree] at hcard
  exact hcard

/-- Among the six exact patterns, only the minimal endpoint-pair pattern can
remain at degree five.  Every other pattern supplies three frame neighbors
in addition to `b,d,q`. -/
theorem degree_six_or_minimal_pattern
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (t b d q u c v p : V)
    (hnodup : [b, d, q, u, c, v, p].Nodup)
    (htb : G.Adj t b) (htd : G.Adj t d) (htq : G.Adj t q)
    (hpattern : ExactDeficientColumnPattern G t u c v p) :
    6 ≤ G.degree t ∨ MinimalDeficientColumnPattern G t u c v p := by
  rcases hpattern with h | h | h | h | h | h
  · left
    apply length_le_degree_of_nodup_neighbors G t [b, d, q, c, v, p]
    · exact List.Nodup.sublist (by simp) hnodup
    · intro x hx
      simp only [List.mem_cons, List.not_mem_nil, or_false] at hx
      rcases hx with rfl | rfl | rfl | rfl | rfl | rfl <;> simp_all
  · exact Or.inr h
  · left
    apply length_le_degree_of_nodup_neighbors G t [b, d, q, u, v, p]
    · exact List.Nodup.sublist (by simp) hnodup
    · intro x hx
      simp only [List.mem_cons, List.not_mem_nil, or_false] at hx
      rcases hx with rfl | rfl | rfl | rfl | rfl | rfl <;> simp_all
  · left
    apply length_le_degree_of_nodup_neighbors G t [b, d, q, u, c, p]
    · exact List.Nodup.sublist (by simp) hnodup
    · intro x hx
      simp only [List.mem_cons, List.not_mem_nil, or_false] at hx
      rcases hx with rfl | rfl | rfl | rfl | rfl | rfl <;> simp_all
  · left
    apply length_le_degree_of_nodup_neighbors G t [b, d, q, u, c, v]
    · exact List.Nodup.sublist (by simp) hnodup
    · intro x hx
      simp only [List.mem_cons, List.not_mem_nil, or_false] at hx
      rcases hx with rfl | rfl | rfl | rfl | rfl | rfl <;> simp_all
  · left
    apply length_le_degree_of_nodup_neighbors G t [b, d, q, u, c, v]
    · exact List.Nodup.sublist (by simp) hnodup
    · intro x hx
      simp only [List.mem_cons, List.not_mem_nil, or_false] at hx
      rcases hx with rfl | rfl | rfl | rfl | rfl | rfl <;> simp_all

/-- The unique missing row has six known neighbors, while the other aligned
row has seven. -/
theorem aligned_rows_have_degrees_six_and_seven
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (a b r s t u c v p : V)
    (haNodup : [r, s, u, c, v, p].Nodup)
    (hbNodup : [r, s, t, u, c, v, p].Nodup)
    (har : G.Adj a r) (has : G.Adj a s)
    (hau : G.Adj a u) (hac : G.Adj a c) (hav : G.Adj a v)
    (hap : G.Adj a p)
    (hbr : G.Adj b r) (hbs : G.Adj b s) (hbt : G.Adj b t)
    (hbu : G.Adj b u) (hbc : G.Adj b c) (hbv : G.Adj b v)
    (hbp : G.Adj b p) :
    6 ≤ G.degree a ∧ 7 ≤ G.degree b := by
  constructor
  · apply length_le_degree_of_nodup_neighbors G a [r, s, u, c, v, p]
      haNodup
    intro x hx
    simp only [List.mem_cons, List.not_mem_nil, or_false] at hx
    rcases hx with rfl | rfl | rfl | rfl | rfl | rfl <;> assumption
  · apply length_le_degree_of_nodup_neighbors G b [r, s, t, u, c, v, p]
      hbNodup
    intro x hx
    simp only [List.mem_cons, List.not_mem_nil, or_false] at hx
    rcases hx with rfl | rfl | rfl | rfl | rfl | rfl | rfl <;> assumption

/-- Vertices meeting a degree threshold. -/
def highDegreeVertices (G : SimpleGraph V) [DecidableRel G.Adj]
    (k : ℕ) : Finset V :=
  univ.filter fun x ↦ k ≤ G.degree x

/-- Number of entries meeting a threshold in the actual descending degree
sequence. -/
noncomputable def descendingThresholdCount
    (G : SimpleGraph V) [DecidableRel G.Adj] (k : ℕ) : ℕ :=
  (descendingDegreeSequence G).filter (fun d ↦ decide (k ≤ d)) |>.length

omit [DecidableEq V] in
/-- Sorting does not change threshold multiplicity. -/
theorem descendingThresholdCount_eq_card_highDegreeVertices
    (G : SimpleGraph V) [DecidableRel G.Adj] (k : ℕ) :
    descendingThresholdCount G k = (highDegreeVertices G k).card := by
  unfold descendingThresholdCount descendingDegreeSequence highDegreeVertices
  let s := univ.val.map fun x ↦ G.degree x
  have hs : (↑(s.sort (· ≥ ·)) : Multiset ℕ) = s :=
    Multiset.sort_eq s (· ≥ ·)
  have hf :
      (↑((s.sort (· ≥ ·)).filter (fun d ↦ decide (k ≤ d))) : Multiset ℕ) =
        Multiset.filter (fun d ↦ k ≤ d) s := by
    rw [← Multiset.filter_coe]
    exact congrArg (Multiset.filter fun d ↦ k ≤ d) hs
  have hc := congrArg Multiset.card hf
  simpa [s, Multiset.filter_map, Function.comp_def] using hc

/-- Distinct named vertices above one threshold give a threshold-count lower
bound. -/
theorem length_le_descendingThresholdCount_of_named_degrees
    (G : SimpleGraph V) [DecidableRel G.Adj] (k : ℕ) (L : List V)
    (hnodup : L.Nodup) (hdeg : ∀ x ∈ L, k ≤ G.degree x) :
    L.length ≤ descendingThresholdCount G k := by
  rw [descendingThresholdCount_eq_card_highDegreeVertices]
  have hsub : L.toFinset ⊆ highDegreeVertices G k := by
    intro x hx
    simp only [highDegreeVertices, mem_filter, mem_univ, true_and]
    apply hdeg x
    simpa using hx
  have hcard := card_le_card hsub
  simpa [List.toFinset_card_of_nodup hnodup] using hcard

/-- The descending order-statistic coordinate forced by the named degrees:
at least two entries are at least eight, three at least seven, five at least
six, and six at least five. -/
def ForcedDescendingPrefix (G : SimpleGraph V) [DecidableRel G.Adj] : Prop :=
  2 ≤ descendingThresholdCount G 8 ∧
  3 ≤ descendingThresholdCount G 7 ∧
  5 ≤ descendingThresholdCount G 6 ∧
  6 ≤ descendingThresholdCount G 5

/-- Convert six named ambient-degree bounds into the sorted prefix
coordinate.  The fifth vertex can be either nondeficient column. -/
theorem forcedDescendingPrefix_of_named_degrees
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (d q b a x t : V) (hnodup : [d, q, b, a, x, t].Nodup)
    (hd : 8 ≤ G.degree d) (hq : 8 ≤ G.degree q)
    (hb : 7 ≤ G.degree b) (ha : 6 ≤ G.degree a)
    (hx : 6 ≤ G.degree x) (ht : 5 ≤ G.degree t) :
    ForcedDescendingPrefix G := by
  refine ⟨?_, ?_, ?_, ?_⟩
  · apply length_le_descendingThresholdCount_of_named_degrees
      G 8 [d, q] (List.Nodup.sublist (by simp) hnodup)
    intro y hy
    simp only [List.mem_cons, List.not_mem_nil, or_false] at hy
    rcases hy with rfl | rfl <;> assumption
  · apply length_le_descendingThresholdCount_of_named_degrees
      G 7 [d, q, b] (List.Nodup.sublist (by simp) hnodup)
    intro y hy
    simp only [List.mem_cons, List.not_mem_nil, or_false] at hy
    rcases hy with rfl | rfl | rfl <;> omega
  · apply length_le_descendingThresholdCount_of_named_degrees
      G 6 [d, q, b, a, x] (List.Nodup.sublist (by simp) hnodup)
    intro y hy
    simp only [List.mem_cons, List.not_mem_nil, or_false] at hy
    rcases hy with rfl | rfl | rfl | rfl | rfl <;> omega
  · apply length_le_descendingThresholdCount_of_named_degrees
      G 5 [d, q, b, a, x, t] hnodup
    intro y hy
    simp only [List.mem_cons, List.not_mem_nil, or_false] at hy
    rcases hy with rfl | rfl | rfl | rfl | rfl | rfl <;> omega

/-- Branch-sensitive refinement: outside the single minimal attachment
pattern, all six named vertices occur at degree at least six in the sorted
sequence. -/
theorem forcedPrefix_and_sixth_degree_or_minimal
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (d q b a x t u c v p : V)
    (hnodup : [d, q, b, a, x, t].Nodup)
    (hd : 8 ≤ G.degree d) (hq : 8 ≤ G.degree q)
    (hb : 7 ≤ G.degree b) (ha : 6 ≤ G.degree a)
    (hx : 6 ≤ G.degree x) (ht : 5 ≤ G.degree t)
    (hsharp : 6 ≤ G.degree t ∨ MinimalDeficientColumnPattern G t u c v p) :
    ForcedDescendingPrefix G ∧
      (6 ≤ descendingThresholdCount G 6 ∨
        MinimalDeficientColumnPattern G t u c v p) := by
  constructor
  · exact forcedDescendingPrefix_of_named_degrees
      G d q b a x t hnodup hd hq hb ha hx ht
  · rcases hsharp with htSix | hminimal
    · left
      apply length_le_descendingThresholdCount_of_named_degrees
        G 6 [d, q, b, a, x, t] hnodup
      intro y hy
      simp only [List.mem_cons, List.not_mem_nil, or_false] at hy
      rcases hy with rfl | rfl | rfl | rfl | rfl | rfl <;> omega
    · exact Or.inr hminimal

/-- The exact sorted prefix does not by itself contradict residue three: the
existing split graph realizes a much stronger prefix and has residue exactly
three. -/
theorem forcedDescendingPrefix_does_not_exclude_residue_three :
    ForcedDescendingPrefix
      WrittenOnTheWallII.GraphConjecture59ResidueThreshold.SplitResidueThreeCountermodel.graph ∧
    residue
      WrittenOnTheWallII.GraphConjecture59ResidueThreshold.SplitResidueThreeCountermodel.graph = 3 := by
  constructor
  · unfold ForcedDescendingPrefix descendingThresholdCount
    rw [WrittenOnTheWallII.GraphConjecture59ResidueThreshold.SplitResidueThreeCountermodel.descending_degree_profile]
    simp [WrittenOnTheWallII.GraphConjecture59ResidueThreshold.SplitResidueThreeCountermodel.profile]
  · exact
      WrittenOnTheWallII.GraphConjecture59ResidueThreshold.SplitResidueThreeCountermodel.residue_eq_three

end WrittenOnTheWallII.GraphConjecture59DeficientColumnDegreePrefix
