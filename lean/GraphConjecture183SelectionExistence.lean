import GraphConjecture183AttachmentSelection

/-!
# WOWII 183: existence of outside-component attachment choices

The v0.11 interface quantified attachment edges over *all* outside components,
including the isolated component containing `x`.  That component cannot have
an attachment edge through `x`.  This file repairs the quantification and
proves existence of one attachment/root pair for every other component from
ambient connectedness alone.
-/

namespace WrittenOnTheWallII.GraphConjecture183SelectionExistence

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture183OutsideBudget

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

omit [Fintype V] [DecidableEq V] in
/-- A walk from outside a set to inside it crosses the set boundary. -/
lemma Walk.exists_boundary_edge (G : SimpleGraph V) (S : Set V)
    {u v : V} (p : G.Walk u v) (hu : u ∉ S) (hv : v ∈ S) :
    ∃ a ∉ S, ∃ b ∈ S, G.Adj a b := by
  induction p with
  | nil => exact (hu hv).elim
  | @cons u w v huw p ih =>
      by_cases hw : w ∈ S
      · exact ⟨u, hu, w, hw, huw⟩
      · exact ih hw hv

omit [Fintype V] [DecidableEq V] in
/-- A walk starting at a vertex with no neighbors must be trivial. -/
lemma Walk.eq_end_of_forall_not_adj (G : SimpleGraph V) {u v : V}
    (p : G.Walk u v) (hiso : ∀ w, ¬G.Adj u w) : u = v := by
  cases p with
  | nil => rfl
  | @cons _ w _ huw _ => exact (hiso w huw).elim

/-- The ambient image of one connected-component support of `G-N(x)`. -/
def ambientComponentSupport (G : SimpleGraph V) (x : V)
    (c : (outsideGraph G x).ConnectedComponent) : Set V :=
  Subtype.val '' c.supp

/-- The outside component containing `x` itself. -/
def rootOutsideComponent (G : SimpleGraph V) (x : V) :
    (outsideGraph G x).ConnectedComponent :=
  (outsideGraph G x).connectedComponentMk ⟨x, by simp [outsideVertices]⟩

omit [Fintype V] [DecidableEq V] in
/-- `x` does not lie in the ambient support of any other outside component. -/
lemma x_not_mem_ambientComponentSupport (G : SimpleGraph V) (x : V)
    {c : (outsideGraph G x).ConnectedComponent}
    (hc : c ≠ rootOutsideComponent G x) :
    x ∉ ambientComponentSupport G x c := by
  rintro ⟨y, hyc, hyv⟩
  apply hc
  have hyx : y = (⟨x, by simp [outsideVertices]⟩ : outsideVertices G x) := by
    apply Subtype.ext
    exact hyv
  rw [ConnectedComponent.mem_supp_iff] at hyc
  simpa [rootOutsideComponent, hyx] using hyc.symm

omit [Fintype V] [DecidableEq V] in
/-- Every component support is nonempty after forgetting the outside subtype. -/
lemma ambientComponentSupport_nonempty (G : SimpleGraph V) (x : V)
    (c : (outsideGraph G x).ConnectedComponent) :
    (ambientComponentSupport G x c).Nonempty := by
  obtain ⟨y, hy⟩ := c.nonempty_supp
  exact ⟨y.1, y, hy, rfl⟩

omit [Fintype V] [DecidableEq V] in
/-- In a connected ambient graph, every outside component other than the
`x`-component has an edge to a neighbor of `x`. -/
theorem exists_attachment_for_component (G : SimpleGraph V)
    (hconnected : G.Connected) (x : V)
    (c : (outsideGraph G x).ConnectedComponent)
    (hc : c ≠ rootOutsideComponent G x) :
    ∃ (p : V) (r : outsideVertices G x),
      r ∈ c.supp ∧ G.Adj x p ∧ G.Adj p r.1 := by
  obtain ⟨v, hv⟩ := ambientComponentSupport_nonempty G x c
  obtain ⟨walk⟩ := hconnected.preconnected x v
  obtain ⟨p, hpout, r0, hrin, hpr⟩ :=
    Walk.exists_boundary_edge G (ambientComponentSupport G x c) walk
      (x_not_mem_ambientComponentSupport G x hc) hv
  obtain ⟨r, hrc, hrv⟩ := hrin
  subst r0
  have hxp : G.Adj x p := by
    by_contra hxpn
    let pOut : outsideVertices G x := ⟨p, hxpn⟩
    have hH : (outsideGraph G x).Adj pOut r := hpr
    have hpc : pOut ∈ c.supp :=
      (c.mem_supp_congr_adj hH).mpr hrc
    exact hpout ⟨pOut, hpc, rfl⟩
  exact ⟨p, r, hrc, hxp, hpr⟩

/-- Correctly indexed attachment/root data: edge conditions are requested only
for the selected non-root components. -/
structure SelectedAttachmentData (G : SimpleGraph V) (x : V) where
  C : Finset (outsideGraph G x).ConnectedComponent
  root : (outsideGraph G x).ConnectedComponent → outsideVertices G x
  attach : (outsideGraph G x).ConnectedComponent → V
  covers : ∀ y : outsideVertices G x, y.1 ≠ x →
    (outsideGraph G x).connectedComponentMk y ∈ C
  excludes_root : rootOutsideComponent G x ∉ C
  root_supported : ∀ c ∈ C, root c ∈ c.supp
  root_ne_x : ∀ c ∈ C, (root c).1 ≠ x
  attach_adj_x : ∀ c ∈ C, G.Adj x (attach c)
  attach_adj_root : ∀ c ∈ C, G.Adj (attach c) (root c).1

/-- Ambient connectedness supplies a simultaneous finite choice of one
attachment/root pair for every non-root outside component. -/
noncomputable def selectedAttachmentDataOfConnected (G : SimpleGraph V)
    (hconnected : G.Connected) (x : V) : SelectedAttachmentData G x := by
  classical
  let c0 := rootOutsideComponent G x
  let C : Finset (outsideGraph G x).ConnectedComponent := Finset.univ.erase c0
  have hex : ∀ c ∈ C, ∃ (p : V) (r : outsideVertices G x),
      r ∈ c.supp ∧ G.Adj x p ∧ G.Adj p r.1 := by
    intro c hc
    exact exists_attachment_for_component G hconnected x c
      (Finset.ne_of_mem_erase hc)
  let attach : (outsideGraph G x).ConnectedComponent → V := fun c =>
    if hc : c ∈ C then (hex c hc).choose else x
  let root : (outsideGraph G x).ConnectedComponent → outsideVertices G x := fun c =>
    if hc : c ∈ C then (hex c hc).choose_spec.choose
    else ⟨x, by simp [outsideVertices]⟩
  refine
    { C := C
      root := root
      attach := attach
      covers := ?_
      excludes_root := by simp [C, c0]
      root_supported := ?_
      root_ne_x := ?_
      attach_adj_x := ?_
      attach_adj_root := ?_ }
  · intro y hyx
    simp only [C, Finset.mem_erase, Finset.mem_univ, and_true]
    intro hroot
    have hyroot : y ∈ (rootOutsideComponent G x).supp := by
      rw [ConnectedComponent.mem_supp_iff]
      exact hroot
    have hxy : x = y.1 := by
      have hxmem :
          (⟨x, by simp [outsideVertices]⟩ : outsideVertices G x) ∈
            (rootOutsideComponent G x).supp := by
        simp [rootOutsideComponent, ConnectedComponent.mem_supp_iff]
      have hreach := (rootOutsideComponent G x).reachable_of_mem_supp hxmem hyroot
      have hwalk := hreach.some
      have heq :
          (⟨x, by simp [outsideVertices]⟩ : outsideVertices G x) = y :=
        Walk.eq_end_of_forall_not_adj (outsideGraph G x) hwalk (fun z hxz =>
          z.property hxz)
      exact congrArg Subtype.val heq
    exact hyx hxy.symm
  · intro c hc
    simp only [root, dif_pos hc]
    exact (hex c hc).choose_spec.choose_spec.1
  · intro c hc hcx
    have hroot := (hex c hc).choose_spec.choose_spec.1
    apply Finset.ne_of_mem_erase hc
    have hrootdef : root c = (hex c hc).choose_spec.choose := by
      simp [root, hc]
    have hcx' : ((hex c hc).choose_spec.choose).1 = x := by
      rw [← hrootdef]
      exact hcx
    have hrx : (hex c hc).choose_spec.choose =
        (⟨x, by simp [outsideVertices]⟩ : outsideVertices G x) := by
      apply Subtype.ext
      exact hcx'
    have hxmem :
        (⟨x, by simp [outsideVertices]⟩ : outsideVertices G x) ∈ c0.supp := by
      simp [c0, rootOutsideComponent, ConnectedComponent.mem_supp_iff]
    have hroot0 : (hex c hc).choose_spec.choose ∈ c0.supp := by
      rw [hrx]
      exact hxmem
    exact ConnectedComponent.eq_of_common_vertex hroot hroot0
  · intro c hc
    simp only [attach, dif_pos hc]
    exact (hex c hc).choose_spec.choose_spec.2.1
  · intro c hc
    simp only [attach, root, dif_pos hc]
    exact (hex c hc).choose_spec.choose_spec.2.2

end WrittenOnTheWallII.GraphConjecture183SelectionExistence
