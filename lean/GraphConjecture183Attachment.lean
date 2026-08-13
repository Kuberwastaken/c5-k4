import FormalConjecturesUtil

/-!
# WOWII 183: attachment conflict reductions

This file formalizes the unconditional local reductions isolated in
`results/expansion/method_v06_183_attachment.md`.  It deliberately does not
assert that a clean vertex or a compatible clean pair exists.
-/

namespace WrittenOnTheWallII.GraphConjecture183Attachment

open SimpleGraph Finset

variable {V : Type*}

/-- A graph is claw-free when every three distinct neighbors of one vertex
contain an adjacent pair.  This is the induced-`K₁,₃` exclusion in the
local form used by the attachment argument. -/
def IsClawFree (G : SimpleGraph V) : Prop :=
  ∀ ⦃p x u v : V⦄, G.Adj p x → G.Adj p u → G.Adj p v →
    x ≠ u → x ≠ v → u ≠ v →
    G.Adj x u ∨ G.Adj x v ∨ G.Adj u v

/-- The neighbors of `p` lying beyond the open neighborhood of `x`, with
`x` itself removed.  In the paper notation this is
`N(p) ∩ (V(G - N(x)) - {x})`. -/
def outsideAttachments (G : SimpleGraph V) (x p : V) : Set V :=
  {v | G.Adj p v ∧ v ≠ x ∧ ¬G.Adj x v}

/-- **Attachment clique lemma.**  If `p` is a neighbor of `x` in a claw-free
graph, then all attachments of `p` beyond the open neighborhood of `x` form
a clique. -/
theorem isClique_outsideAttachments_of_isClawFree (G : SimpleGraph V)
    (hclaw : IsClawFree G) {x p : V} (hpx : G.Adj p x) :
    G.IsClique (outsideAttachments G x p) := by
  rw [isClique_iff]
  intro u hu v hv huv
  rcases hu with ⟨hpu, hux, hxu⟩
  rcases hv with ⟨hpv, hvx, hxv⟩
  rcases hclaw hpx hpu hpv hux.symm hvx.symm huv with hxu' | hxv' | huv'
  · exact (hxu hxu').elim
  · exact (hxv hxv').elim
  · exact huv'

/-- Every finite clique in a bipartite graph has at most two vertices. -/
theorem IsClique.card_le_two_of_isBipartite {G : SimpleGraph V}
    (hG : G.IsBipartite) {s : Finset V} (hs : G.IsClique s) :
    s.card ≤ 2 := by
  exact hs.card_le_of_colorable hG

/-- Bipartiteness of a finite induced graph is inherited when its vertex set
is restricted. -/
theorem induce_isBipartite_of_finset_subset (G : SimpleGraph V)
    {s t : Finset V} (hst : s ⊆ t) (ht : (G.induce (↑t : Set V)).IsBipartite) :
    (G.induce (↑s : Set V)).IsBipartite := by
  classical
  rw [induce_isBipartite_iff_exists_coloring] at ht ⊢
  obtain ⟨color, hcolor⟩ := ht
  exact ⟨color, fun u hu v hv huv ↦ hcolor u (hst hu) v (hst hv) huv⟩

/-- A finite clique whose own induced subgraph is bipartite has cardinality
at most two. -/
theorem card_le_two_of_isClique_of_induce_isBipartite (G : SimpleGraph V)
    (s : Finset V) (hclique : G.IsClique s)
    (hbip : (G.induce (↑s : Set V)).IsBipartite) :
    s.card ≤ 2 := by
  classical
  rw [induce_isBipartite_iff_exists_coloring] at hbip
  obtain ⟨color, hcolor⟩ := hbip
  let f : ↑s → Fin 2 := fun v ↦ color v
  have hf : Function.Injective f := by
    intro u v huv
    apply Subtype.ext
    by_contra huv'
    exact (hcolor u u.property v v.property
      (hclique u.property v.property huv')) huv
  simpa [f] using Fintype.card_le_of_injective f hf

/-- The attachment clique has order at most two whenever the graph induced by
those attachments is bipartite. -/
theorem attachment_card_le_two (G : SimpleGraph V) (hclaw : IsClawFree G)
    {x p : V} (hpx : G.Adj p x) (A : Finset V)
    (hA : ↑A ⊆ outsideAttachments G x p)
    (hbip : (G.induce (↑A : Set V)).IsBipartite) :
    A.card ≤ 2 := by
  apply card_le_two_of_isClique_of_induce_isBipartite G A
  · exact (isClique_outsideAttachments_of_isClawFree G hclaw hpx).subset hA
  · exact hbip

/-- **Clean-vertex necessity.**  If `p` and a finite collection `A` of its
remaining outside attachments induce a bipartite graph, then `A` has at most
one vertex.  Thus any individually retainable neighbor of `x` is clean.

The ambient retained induced graph may be larger: bipartiteness can first be
restricted to the displayed subset `insert p A`. -/
theorem attachment_card_le_one_of_induce_insert_isBipartite
    [DecidableEq V] (G : SimpleGraph V) (hclaw : IsClawFree G) {x p : V}
    (hpx : G.Adj p x) (A : Finset V)
    (hA : ↑A ⊆ outsideAttachments G x p)
    (hbip : (G.induce (↑(insert p A : Finset V) : Set V)).IsBipartite) :
    A.card ≤ 1 := by
  classical
  have hpA : p ∉ A := by
    intro hpA
    exact G.loopless p ((hA hpA).1)
  have hcliqueA : G.IsClique A :=
    (isClique_outsideAttachments_of_isClawFree G hclaw hpx).subset hA
  have hcliqueInsert : G.IsClique (↑(insert p A : Finset V) : Set V) := by
    simpa only [Finset.coe_insert] using
      hcliqueA.insert (fun v hv _ ↦ (hA hv).1)
  have hcard := card_le_two_of_isClique_of_induce_isBipartite
    G (insert p A : Finset V) hcliqueInsert hbip
  rw [card_insert_of_notMem hpA] at hcard
  omega

/-- Ambient form of clean-vertex necessity.  It is enough that `p` and all
the displayed attachments lie in any larger retained vertex set whose induced
graph is bipartite. -/
theorem attachment_card_le_one_of_retained_isBipartite
    [DecidableEq V] (G : SimpleGraph V) (hclaw : IsClawFree G) {x p : V}
    (hpx : G.Adj p x) (A R : Finset V)
    (hA : ↑A ⊆ outsideAttachments G x p)
    (hsub : insert p A ⊆ R)
    (hbip : (G.induce (↑R : Set V)).IsBipartite) :
    A.card ≤ 1 := by
  apply attachment_card_le_one_of_induce_insert_isBipartite G hclaw hpx A hA
  exact induce_isBipartite_of_finset_subset G hsub hbip

end WrittenOnTheWallII.GraphConjecture183Attachment
