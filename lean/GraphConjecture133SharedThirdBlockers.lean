import FormalConjecturesUtil

/-!
# WOWII 133: shared third vertices and blocker coexistence

A third vertex shared by two first-choice branches imposes strong
non-incidence: its two second parents cannot see the opposite first choice.
If the third vertex is also an endpoint blocker, its parents cannot contact
that endpoint target either.
-/

namespace WrittenOnTheWallII.GraphConjecture133SharedThirdBlockers

open SimpleGraph

variable {V : Type*} [Fintype V] [DecidableEq V] [Nonempty V]

/-- Four distinct vertices forming a not-necessarily-induced four-cycle. -/
def HasC4 (G : SimpleGraph V) : Prop :=
  ∃ a b c d : V,
    a ≠ b ∧ a ≠ c ∧ a ≠ d ∧ b ≠ c ∧ b ≠ d ∧ c ≠ d ∧
      G.Adj a b ∧ G.Adj b c ∧ G.Adj c d ∧ G.Adj d a

omit [Fintype V] [DecidableEq V] [Nonempty V] in
lemma not_adj_both_ends_of_edge_of_triangleFree {G : SimpleGraph V}
    (htri : G.CliqueFree 3) {a x y : V}
    (hxy : G.Adj x y) (hax : G.Adj a x) : ¬G.Adj a y := by
  intro hay
  exact G.isIndepSet_neighborSet_of_triangleFree htri a
    (by simpa [G.mem_neighborSet, adj_comm] using hax)
    (by simpa [G.mem_neighborSet, adj_comm] using hay)
    hxy.ne hxy

omit [Fintype V] [DecidableEq V] [Nonempty V] in
/-- In a shared-third configuration `c₁-b₁-a-b₂-c₂`, C4-freeness
forbids each second parent from seeing the opposite first choice. -/
theorem sharedThird_forbids_cross_parent_first {G : SimpleGraph V}
    (hc4 : ¬HasC4 G) {a b₁ b₂ c₁ c₂ : V}
    (hb₁a : G.Adj b₁ a) (hab₂ : G.Adj a b₂)
    (hc₁b₁ : G.Adj c₁ b₁) (hb₂c₂ : G.Adj b₂ c₂)
    (hb : b₁ ≠ b₂) (hc₁a : c₁ ≠ a) (hac₂ : a ≠ c₂) :
    ¬G.Adj b₁ c₂ ∧ ¬G.Adj b₂ c₁ := by
  constructor
  · intro hb₁c₂
    apply hc4
    refine ⟨b₁, a, b₂, c₂, ?_, ?_, ?_, ?_, ?_, ?_,
      hb₁a, hab₂, hb₂c₂, hb₁c₂.symm⟩
    · exact hb₁a.ne
    · exact hb
    · exact hb₁c₂.ne
    · exact hab₂.ne
    · exact hac₂
    · exact hb₂c₂.ne
  · intro hb₂c₁
    apply hc4
    refine ⟨b₂, a, b₁, c₁, ?_, ?_, ?_, ?_, ?_, ?_,
      hab₂.symm, hb₁a.symm, hc₁b₁.symm, hb₂c₁.symm⟩
    · exact hab₂.ne.symm
    · exact hb.symm
    · exact hb₂c₁.ne
    · exact hb₁a.ne.symm
    · exact hc₁a.symm
    · exact hc₁b₁.ne.symm

omit [Fintype V] [DecidableEq V] [Nonempty V] in
/-- If a shared third vertex `a` contacts a target `x`, neither second parent
can also contact `x`: each would form a triangle with `a`. -/
theorem sharedThird_blocker_forbids_parent_target {G : SimpleGraph V}
    (htri : G.CliqueFree 3) {a b₁ b₂ x : V}
    (hb₁a : G.Adj b₁ a) (hab₂ : G.Adj a b₂)
    (hax : G.Adj a x) :
    ¬G.Adj b₁ x ∧ ¬G.Adj b₂ x := by
  constructor
  · exact not_adj_both_ends_of_edge_of_triangleFree htri hax hb₁a
  · exact not_adj_both_ends_of_edge_of_triangleFree htri hax hab₂.symm

omit [Fintype V] [DecidableEq V] [Nonempty V] in
/-- If the blocker target is the common endpoint `u`, C4-freeness additionally
forbids either second parent from seeing the opposite first choice. -/
theorem sharedThird_endpoint_blocker_signature {G : SimpleGraph V}
    (htri : G.CliqueFree 3) (hc4 : ¬HasC4 G)
    {u a b₁ b₂ c₁ c₂ : V}
    (hc₁b₁ : G.Adj c₁ b₁) (hb₁a : G.Adj b₁ a)
    (hab₂ : G.Adj a b₂) (hb₂c₂ : G.Adj b₂ c₂)
    (hau : G.Adj a u) (hb : b₁ ≠ b₂)
    (hc₁a : c₁ ≠ a) (hac₂ : a ≠ c₂) :
    ¬G.Adj b₁ u ∧ ¬G.Adj b₂ u ∧
    ¬G.Adj b₁ c₂ ∧ ¬G.Adj b₂ c₁ := by
  obtain ⟨hb₁u, hb₂u⟩ :=
    sharedThird_blocker_forbids_parent_target htri hb₁a hab₂ hau
  obtain ⟨hb₁c₂, hb₂c₁⟩ :=
    sharedThird_forbids_cross_parent_first hc4 hb₁a hab₂
      hc₁b₁ hb₂c₂ hb hc₁a hac₂
  exact ⟨hb₁u, hb₂u, hb₁c₂, hb₂c₁⟩

end WrittenOnTheWallII.GraphConjecture133SharedThirdBlockers
