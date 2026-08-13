import GraphConjecture19CenterTreeAttachment

/-!
# WOWII 19/13: reverse lifting a locally contained walk
-/

namespace WrittenOnTheWallII.GraphConjecture19ReverseWalkLift

open SimpleGraph
open WrittenOnTheWallII.GraphConjecture19UnicyclicDecomposition
open WrittenOnTheWallII.GraphConjecture19DistanceTwoRoute
open WrittenOnTheWallII.GraphConjecture19CenterAttachmentClassification

universe u

variable {V : Type u}

/-- Rebuild a walk in `T` from a walk in `G` when each edge appearing in the
walk is certified to belong to `T`.  Unlike `Walk.mapLe`, this is local to one
walk and therefore works in the reverse (supergraph-to-subgraph) direction. -/
def liftWalkEdges {G T : SimpleGraph V} {a b : V} :
    (p : G.Walk a b) →
      (∀ e ∈ p.edges, e ∈ T.edgeSet) → T.Walk a b
  | .nil, _ => .nil
  | .cons hadj p, h =>
      .cons ((T.mem_edgeSet).mp (h s(_, _) (by simp)))
        (liftWalkEdges p (by
          intro e he
          exact h e (by simp [he])))

/-- The reverse lift preserves the vertex support exactly. -/
@[simp] theorem support_liftWalkEdges
    {G T : SimpleGraph V} {a b : V} (p : G.Walk a b)
    (h : ∀ e ∈ p.edges, e ∈ T.edgeSet) :
    (liftWalkEdges p h).support = p.support := by
  induction p with
  | nil => rfl
  | cons hadj p ih =>
      simp [liftWalkEdges, ih]

/-- The reverse lift preserves length. -/
@[simp] theorem length_liftWalkEdges
    {G T : SimpleGraph V} {a b : V} (p : G.Walk a b)
    (h : ∀ e ∈ p.edges, e ∈ T.edgeSet) :
    (liftWalkEdges p h).length = p.length := by
  induction p with
  | nil => rfl
  | cons hadj p ih =>
      simp [liftWalkEdges, ih]

/-- Pathhood transfers because the vertex list is unchanged. -/
theorem isPath_liftWalkEdges
    {G T : SimpleGraph V} {a b : V} (p : G.Walk a b)
    (hp : p.IsPath) (h : ∀ e ∈ p.edges, e ∈ T.edgeSet) :
    (liftWalkEdges p h).IsPath := by
  rw [Walk.isPath_def, support_liftWalkEdges]
  exact hp.support_nodup

/-- Every edge of a walk avoiding the right endpoint of the added edge lies
in the spanning tree. -/
theorem walk_edges_mem_tree_of_extraRight_not_mem
    {G : SimpleGraph V} (D : TreePlusOneEdge G)
    {a b : V} (p : G.Walk a b)
    (hRightOff : D.extraRight ∉ p.support) :
    ∀ e ∈ p.edges, e ∈ D.tree.edgeSet := by
  induction p with
  | nil =>
      intro e he
      simp at he
  | @cons u v w hadj p ih =>
      intro e he
      simp only [Walk.edges_cons, List.mem_cons] at he
      rcases he with rfl | heTail
      · apply D.tree.mem_edgeSet.mpr
        rcases D.adj_iff.mp hadj with htree | hextra
        · exact htree
        · rcases hextra with hforward | hbackward
          · have : D.extraRight ∈ (Walk.cons hadj p).support := by
              simp
              exact Or.inr (hforward.2 ▸ p.start_mem_support)
            exact (hRightOff this).elim
          · have : D.extraRight ∈ (Walk.cons hadj p).support := by
              simp [hbackward.1]
            exact (hRightOff this).elim
      · apply ih (fun hmem => hRightOff (by simp [hmem])) e heTail

/-- Canonical reverse lift of a walk avoiding `extraRight` into the spanning
tree, retaining support, length, and pathhood. -/
theorem exists_tree_walk_same_support_of_extraRight_not_mem
    {G : SimpleGraph V} (D : TreePlusOneEdge G)
    {a b : V} (p : G.Walk a b)
    (hRightOff : D.extraRight ∉ p.support) :
    ∃ q : D.tree.Walk a b,
      q.support = p.support ∧ q.length = p.length ∧
      (p.IsPath → q.IsPath) := by
  let h := walk_edges_mem_tree_of_extraRight_not_mem D p hRightOff
  let q := liftWalkEdges p h
  exact ⟨q, support_liftWalkEdges p h, length_liftWalkEdges p h,
    fun hp => isPath_liftWalkEdges p hp h⟩

/-- In a tree, a vertex outside a simple path cannot be adjacent to two
distinct vertices of that path. -/
theorem no_two_attachments_to_tree_path
    [DecidableEq V] {T : SimpleGraph V} (hT : T.IsAcyclic)
    {a b c x z : V} (q : T.Walk a b) (hq : q.IsPath)
    (hc : c ∈ q.support) (hx : x ∈ q.support)
    (hz : z ∉ q.support) (hcx : c ≠ x)
    (hcz : T.Adj c z) (hxz : T.Adj x z) : False := by
  let pc := q.takeUntil c hc
  let px := q.takeUntil x hx
  have hzpc : z ∉ pc.support := fun h => hz (q.support_takeUntil_subset hc (by simpa [pc] using h))
  have hzpx : z ∉ px.support := fun h => hz (q.support_takeUntil_subset hx (by simpa [px] using h))
  let rc : T.Walk a z := pc.concat hcz
  let rx : T.Walk a z := px.concat hxz
  have hrc : rc.IsPath := (hq.takeUntil hc).concat hzpc hcz
  have hrx : rx.IsPath := (hq.takeUntil hx).concat hzpx hxz
  have heq : rc = rx := Subtype.mk.inj (hT.path_unique ⟨rc, hrc⟩ ⟨rx, hrx⟩)
  have hxpc : x ∈ pc.support := by
    have hxrx : x ∈ rx.support := by
      dsimp [rx]
      exact px.support_subset_support_concat hxz px.end_mem_support
    rw [← heq] at hxrx
    dsimp [rc] at hxrx
    rw [Walk.support_concat] at hxrx
    rw [List.concat_eq_append, List.mem_append] at hxrx
    simp only [List.mem_singleton] at hxrx
    exact hxrx.resolve_right (by simpa using hxz.ne)
  have hcpx : c ∈ px.support := by
    have hcrc : c ∈ rc.support := by
      dsimp [rc]
      exact pc.support_subset_support_concat hcz pc.end_mem_support
    rw [heq] at hcrc
    dsimp [rx] at hcrc
    rw [Walk.support_concat] at hcrc
    rw [List.concat_eq_append, List.mem_append] at hcrc
    simp only [List.mem_singleton] at hcrc
    exact hcrc.resolve_right (by simpa using hcz.ne)
  exact (q.notMem_support_takeUntil_support_takeUntil_subset
    hcx.symm hc hxpc) hcpx

/-- Application to the center-attained branch: an ordinary off-path vertex
cannot have any noncenter attachment to the geodesic. -/
theorem ordinary_off_path_vertex_has_no_noncenter_path_attachment
    [Fintype V] [DecidableEq V]
    {G : SimpleGraph V} [DecidableRel G.Adj]
    (D : TreePlusOneEdge G) {a b : V} (p : G.Walk a b) (hp : p.IsPath)
    (c z x : V)
    (hcLeft : D.extraLeft = c)
    (hcP : c ∈ p.support.toFinset)
    (hRightOff : D.extraRight ∉ p.support.toFinset)
    (hsat : p.support.toFinset ∪ G.neighborFinset c = Finset.univ)
    (hcenter : G.IsIndepSet (G.neighborSet c))
    (hzOff : z ∈ Finset.univ \ p.support.toFinset)
    (hzRight : z ≠ D.extraRight)
    (hzx : G.Adj z x) (hxCenter : x ≠ c) : False := by
  have hclass := classify_off_path_attachments_center_left D
    p.support.toFinset c hcLeft hRightOff hsat hcenter z hzOff
  have hczTree : D.tree.Adj c z := hclass.2.1 hzRight
  have hxData := hclass.2.2 x hzx hxCenter
  have hxP : x ∈ p.support.toFinset := hxData.1
  have hzxTree : D.tree.Adj z x := hxData.2
  have hRightList : D.extraRight ∉ p.support := by
    simpa using hRightOff
  let hedge := walk_edges_mem_tree_of_extraRight_not_mem D p hRightList
  let q : D.tree.Walk a b := liftWalkEdges p hedge
  have hqPath : q.IsPath := isPath_liftWalkEdges p hp hedge
  have hqSupport : q.support = p.support := support_liftWalkEdges p hedge
  have hcq : c ∈ q.support := by
    rw [hqSupport]
    simpa using hcP
  have hxq : x ∈ q.support := by
    rw [hqSupport]
    simpa using hxP
  have hzq : z ∉ q.support := by
    rw [hqSupport]
    exact fun hz => (Finset.mem_sdiff.mp hzOff).2 (by simpa using hz)
  exact no_two_attachments_to_tree_path D.tree_acyclic q hqPath
    hcq hxq hzq hxCenter.symm hczTree hzxTree.symm

/-- Hence every ordinary off-path vertex is a leaf attached to the center at
the adjacency level. -/
theorem ordinary_off_path_vertex_neighbors_eq_center
    [Fintype V] [DecidableEq V]
    {G : SimpleGraph V} [DecidableRel G.Adj]
    (D : TreePlusOneEdge G) {a b : V} (p : G.Walk a b) (hp : p.IsPath)
    (c z : V)
    (hcLeft : D.extraLeft = c)
    (hcP : c ∈ p.support.toFinset)
    (hRightOff : D.extraRight ∉ p.support.toFinset)
    (hsat : p.support.toFinset ∪ G.neighborFinset c = Finset.univ)
    (hcenter : G.IsIndepSet (G.neighborSet c))
    (hzOff : z ∈ Finset.univ \ p.support.toFinset)
    (hzRight : z ≠ D.extraRight) :
    ∀ x : V, G.Adj z x → x = c := by
  intro x hzx
  by_contra hxc
  exact ordinary_off_path_vertex_has_no_noncenter_path_attachment
    D p hp c z x hcLeft hcP hRightOff hsat hcenter hzOff hzRight hzx hxc

/-- The off-path added-edge endpoint has at most one spanning-tree neighbor;
all such neighbors are forced onto the lifted geodesic, where tree acyclicity
excludes two distinct attachments. -/
theorem extraRight_tree_neighbor_unique
    [Fintype V] [DecidableEq V]
    {G : SimpleGraph V} [DecidableRel G.Adj]
    (D : TreePlusOneEdge G) {a b : V} (p : G.Walk a b) (hp : p.IsPath)
    (c : V)
    (hcLeft : D.extraLeft = c)
    (hRightOff : D.extraRight ∉ p.support.toFinset)
    (hsat : p.support.toFinset ∪ G.neighborFinset c = Finset.univ)
    (hcenter : G.IsIndepSet (G.neighborSet c)) :
    ∀ x y : V, D.tree.Adj D.extraRight x →
      D.tree.Adj D.extraRight y → x = y := by
  intro x y hrightX hrightY
  by_contra hxy
  have hrightOffDiff : D.extraRight ∈ Finset.univ \ p.support.toFinset := by
    simp [hRightOff]
  have hclass := classify_off_path_attachments_center_left D
    p.support.toFinset c hcLeft hRightOff hsat hcenter
      D.extraRight hrightOffDiff
  have hxCenter : x ≠ c := by
    intro hxc
    apply D.extra_not_tree
    simpa [hcLeft, hxc, adj_comm] using hrightX
  have hyCenter : y ≠ c := by
    intro hyc
    apply D.extra_not_tree
    simpa [hcLeft, hyc, adj_comm] using hrightY
  have hxG : G.Adj D.extraRight x := D.adj_iff.mpr (Or.inl hrightX)
  have hyG : G.Adj D.extraRight y := D.adj_iff.mpr (Or.inl hrightY)
  have hxP := (hclass.2.2 x hxG hxCenter).1
  have hyP := (hclass.2.2 y hyG hyCenter).1
  have hRightList : D.extraRight ∉ p.support := by simpa using hRightOff
  let hedge := walk_edges_mem_tree_of_extraRight_not_mem D p hRightList
  let q : D.tree.Walk a b := liftWalkEdges p hedge
  have hqPath : q.IsPath := isPath_liftWalkEdges p hp hedge
  have hqSupport : q.support = p.support := support_liftWalkEdges p hedge
  have hxq : x ∈ q.support := by rw [hqSupport]; simpa using hxP
  have hyq : y ∈ q.support := by rw [hqSupport]; simpa using hyP
  have hrightq : D.extraRight ∉ q.support := by
    rw [hqSupport]
    exact hRightList
  exact no_two_attachments_to_tree_path D.tree_acyclic q hqPath
    hxq hyq hrightq hxy hrightX.symm hrightY.symm

end WrittenOnTheWallII.GraphConjecture19ReverseWalkLift
