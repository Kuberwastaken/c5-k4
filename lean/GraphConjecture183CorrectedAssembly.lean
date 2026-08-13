import GraphConjecture183ComponentAssembly

/-!
# WOWII 183: non-vacuous corrected assembly rungs

This file develops two pieces of the repaired component argument.  First, it
checks that `NontrivialRootedTrunkPrinciple` is genuinely satisfiable by proving
it for every finite complete graph.  Second, it proves the bipartite-witness
and arithmetic additivity lemmas needed when independently treated outside
components are assembled.
-/

namespace WrittenOnTheWallII.GraphConjecture183CorrectedAssembly

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture183OutsideBudget
open WrittenOnTheWallII.GraphConjecture183ComponentAssembly

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

omit [Fintype V] in
/-- Bipartite induced witnesses on anticomplete vertex sets can be patched by
using the two given colorings independently. -/
lemma induce_union_isBipartite_of_anticomplete
    (G : SimpleGraph V) (A B : Finset V)
    (hA : (G.induce (↑A : Set V)).IsBipartite)
    (hB : (G.induce (↑B : Set V)).IsBipartite)
    (hcross : ∀ a ∈ A, ∀ b ∈ B, ¬G.Adj a b) :
    (G.induce (↑(A ∪ B) : Set V)).IsBipartite := by
  rw [induce_isBipartite_iff_exists_coloring] at hA hB ⊢
  obtain ⟨cA, hcA⟩ := hA
  obtain ⟨cB, hcB⟩ := hB
  refine ⟨fun v => if v ∈ A then cA v else cB v, ?_⟩
  · intro x hx y hy hxy
    by_cases hxA : x ∈ A
    · by_cases hyA : y ∈ A
      · simpa [hxA, hyA] using hcA x hxA y hyA hxy
      · have hyB : y ∈ B := (mem_union.mp hy).resolve_left hyA
        exact (hcross x hxA y hyB hxy).elim
    · have hxB : x ∈ B := (mem_union.mp hx).resolve_left hxA
      by_cases hyA : y ∈ A
      · exact (hcross y hyA x hxB hxy.symm).elim
      · have hyB : y ∈ B := (mem_union.mp hy).resolve_left hyA
        simpa [hxA, hyA] using hcB x hxB y hyB hxy

omit [Fintype V] in
/-- The patched witness has the sum of the component witness orders when the
component vertex sets are disjoint. -/
lemma card_union_eq_add_of_disjoint (A B : Finset V) (hAB : Disjoint A B) :
    (A ∪ B).card = A.card + B.card := by
  exact card_union_of_disjoint hAB

/-- Two anticomplete component witnesses give the expected additive lower
bound on the largest induced bipartite order. -/
theorem add_card_le_largestInducedBipartiteSubgraphSize
    (G : SimpleGraph V) (A B : Finset V)
    (hAB : Disjoint A B)
    (hA : (G.induce (↑A : Set V)).IsBipartite)
    (hB : (G.induce (↑B : Set V)).IsBipartite)
    (hcross : ∀ a ∈ A, ∀ b ∈ B, ¬G.Adj a b) :
    A.card + B.card ≤ G.largestInducedBipartiteSubgraphSize := by
  rw [← card_union_eq_add_of_disjoint A B hAB]
  exact card_le_largestInducedBipartiteSubgraphSize G (A ∪ B)
    (induce_union_isBipartite_of_anticomplete G A B hA hB hcross)

/-- Summing `dᵢ+1≤bᵢ` pays one unit for every nontrivial component. -/
lemma sum_component_trunk_budgets
    {ι : Type*} [DecidableEq ι] (I : Finset ι) (d b : ι → ℕ)
    (h : ∀ i ∈ I, d i + 1 ≤ b i) :
    (∑ i ∈ I, d i) + I.card ≤ ∑ i ∈ I, b i := by
  have hs : ∑ i ∈ I, (d i + 1) ≤ ∑ i ∈ I, b i := by
    exact sum_le_sum fun i hi => h i hi
  simpa [sum_add_distrib] using hs

/-- Singleton components contribute equally to both sides and therefore do
not consume the one-unit surplus supplied by nontrivial components. -/
lemma sum_component_trunk_budgets_with_singletons
    {ι : Type*} [DecidableEq ι] (I : Finset ι) (d b : ι → ℕ)
    (singletons : ℕ) (h : ∀ i ∈ I, d i + 1 ≤ b i) :
    (∑ i ∈ I, d i) + I.card + singletons ≤
      (∑ i ∈ I, b i) + singletons := by
  have hsum := sum_component_trunk_budgets I d b h
  omega

omit [Fintype V] in
/-- A singleton is a connected dominating set in a complete graph. -/
lemma completeGraph_singleton_isConnectedDominating
    {S : Set V} (r : S) :
    ((⊤ : SimpleGraph V).induce S).IsConnectedDominating ({r} : Set S) := by
  constructor
  · intro v
    by_cases hvr : v = r
    · exact Or.inl hvr
    · exact Or.inr ⟨r, by simp, by simpa using hvr⟩
  · exact induce_singleton_connected ((⊤ : SimpleGraph V).induce S) r

omit [Fintype V] in
/-- Any two distinct vertices of an induced complete graph form an explicit
bipartite induced witness. -/
lemma completeGraph_pair_isBipartite
    {S : Set V} (r q : S) :
    ((((⊤ : SimpleGraph V).induce S).induce
      (↑({r, q} : Finset S) : Set S))).IsBipartite := by
  rw [induce_isBipartite_iff_exists_coloring]
  refine ⟨fun v => if v = r then (0 : Fin 2) else 1, ?_⟩
  intro x hx y hy hxy
  have hx' : x = r ∨ x = q := by simpa [mem_insert, mem_singleton] using hx
  have hy' : y = r ∨ y = q := by simpa [mem_insert, mem_singleton] using hy
  by_cases hxr : x = r
  · by_cases hyr : y = r
    · exact (hxy.ne (hxr.trans hyr.symm)).elim
    · simp [hxr, hyr]
  · have hxq : x = q := hx'.resolve_left hxr
    by_cases hyr : y = r
    · simp [hxr, hyr]
    · have hyq : y = q := hy'.resolve_left hyr
      exact (hxy.ne (hxq.trans hyq.symm)).elim

/-- The repaired trunk principle is non-vacuous: every finite complete graph
satisfies it.  This explicitly rules out the singleton inconsistency found in
the previous interface audit. -/
theorem completeGraph_nontrivialRootedTrunkPrinciple :
    NontrivialRootedTrunkPrinciple (⊤ : SimpleGraph V) := by
  intro S r _hconnected hS
  letI : Fintype S := Fintype.ofFinite S
  obtain ⟨q, hqS, hqr⟩ := S.exists_ne_of_one_lt_ncard (by omega) r
  let qS : S := ⟨q, hqS⟩
  have hrq : r ≠ qS := by
    intro h
    exact hqr (congrArg Subtype.val h).symm
  have hdom : ((⊤ : SimpleGraph V).induce S).IsConnectedDominating
      (↑({r} : Finset S) : Set S) := by
    simpa using completeGraph_singleton_isConnectedDominating r
  refine ⟨{r}, by simp, hdom, ?_⟩
  have hp := card_le_largestInducedBipartiteSubgraphSize
    ((⊤ : SimpleGraph V).induce S) ({r, qS} : Finset S)
    (completeGraph_pair_isBipartite r qS)
  simpa [hrq] using hp

/-- For a complete ambient graph, the outside graph at `x` consists only of
`x`; the same singleton pays for both sides of the certificate. -/
def completeGraphOutsideCertificate (x : V) :
    OutsideBudgetCertificate (⊤ : SimpleGraph V) x := by
  let ox : outsideVertices (⊤ : SimpleGraph V) x := ⟨x, by simp [outsideVertices]⟩
  refine
    { D := {x}
      B := {ox}
      dominating := ?_
      bipartite := ?_
      card_le := by simp }
  · constructor
    · intro v
      by_cases hvx : v = x
      · exact Or.inl (by simpa using hvx)
      · exact Or.inr ⟨x, by simp, by simpa using hvx⟩
    · letI : Subsingleton (↥(↑({x} : Finset V) : Set V)) :=
        ⟨fun a b => Subtype.ext
          ((Finset.mem_singleton.mp a.property).trans
            (Finset.mem_singleton.mp b.property).symm)⟩
      rw [connected_iff]
      exact ⟨Preconnected.of_subsingleton, ⟨⟨x, by simp⟩⟩⟩
  · rw [induce_isBipartite_iff_exists_coloring]
    refine ⟨fun _ => (0 : Fin 2), ?_⟩
    intro a _ha b _hb hab
    have haeq : a = ox := Finset.mem_singleton.mp _ha
    have hbeq : b = ox := Finset.mem_singleton.mp _hb
    subst a
    subst b
    exact ((outsideGraph (⊤ : SimpleGraph V) x).loopless ox hab).elim

omit [Fintype V] in
/-- The corrected *full* construction boundary is satisfiable as well: on a
complete graph it is witnessed by the explicit singleton outside certificate.
This theorem consumes, but does not exploit vacuity in, the corrected trunk
principle (which was proved independently above). -/
theorem completeGraph_nontrivialComponentConstruction (x : V) :
    NontrivialComponentConstruction (⊤ : SimpleGraph V) x := by
  intro _hconnected _htrunk
  exact ⟨completeGraphOutsideCertificate x⟩

end WrittenOnTheWallII.GraphConjecture183CorrectedAssembly
