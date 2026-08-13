import FormalConjecturesUtil

/-!
# Edge-deletion closure for a color-critical Reed candidate

The v50 computation checked every singleton-edge deletion of its frozen base
graph.  The lemma below records the stronger consequence: once all genuine
singleton deletions are `q`-colorable, every nonempty genuine deletion is
`q`-colorable.  This closes the entire multi-edge pruning neighborhood without
enumerating it.
-/

namespace ReedEdgeDeletionClosure

open SimpleGraph

/-- If deleting any one genuine edge makes `G` `q`-colorable, then deleting
any set containing a genuine edge also makes it `q`-colorable. -/
theorem colorable_of_singleton_deletions {V : Type*} (G : SimpleGraph V)
    (q : ℕ)
    (hsingle : ∀ e ∈ G.edgeSet, (G.deleteEdges {e}).Colorable q)
    {s : Set (Sym2 V)} (hgenuine : ∃ e, e ∈ s ∧ e ∈ G.edgeSet) :
    (G.deleteEdges s).Colorable q := by
  obtain ⟨e, hes, heG⟩ := hgenuine
  exact Colorable.mono_left
    (G.deleteEdges_anti (Set.singleton_subset_iff.mpr hes))
    (hsingle e heG)

/-- In particular, an edge-critical nine-chromatic graph whose every
singleton deletion is eight-colorable cannot retain its ninth color after any
genuine edge pruning. -/
theorem no_ninth_color_after_genuine_deletion {V : Type*} (G : SimpleGraph V)
    (hsingle : ∀ e ∈ G.edgeSet, (G.deleteEdges {e}).Colorable 8)
    {s : Set (Sym2 V)} (hgenuine : ∃ e, e ∈ s ∧ e ∈ G.edgeSet) :
    (G.deleteEdges s).chromaticNumber ≤ (8 : ℕ∞) := by
  exact (colorable_of_singleton_deletions G 8 hsingle hgenuine).chromaticNumber_le

end ReedEdgeDeletionClosure
