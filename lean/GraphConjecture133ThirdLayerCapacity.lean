import GraphConjecture133ChoiceSwitching

/-!
# WOWII 133: third-layer overlap and target capacity

C4-freeness makes the third-neighbor sets of different second choices in one
branch disjoint.  Independently, degree four sharply bounds how many outside
blockers each early geodesic target can support.
-/

namespace WrittenOnTheWallII.GraphConjecture133ThirdLayerCapacity

open SimpleGraph
open WrittenOnTheWallII.GraphConjecture133Cubic

variable {V : Type*} [Fintype V] [DecidableEq V] [Nonempty V]

/-- Third choices after removing the preceding first-handle vertex. -/
def thirdHandleChoices (G : SimpleGraph V) (c b : V)
    [DecidableRel G.Adj] : Finset V :=
  (G.neighborFinset b).erase c

omit [Nonempty V] in
/-- Every valid second vertex has three third choices in a four-regular
graph. -/
theorem card_thirdHandleChoices_eq_three
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hreg : G.IsRegularOfDegree 4) {c b : V} (hcb : G.Adj c b) :
    (thirdHandleChoices G c b).card = 3 := by
  have hcmem : c ∈ G.neighborFinset b := by simpa using hcb.symm
  unfold thirdHandleChoices
  rw [Finset.card_erase_of_mem hcmem, G.card_neighborFinset_eq_degree, hreg b]

omit [Nonempty V] in
/-- Within one first-choice branch, distinct second choices have disjoint
third-choice sets.  A common third vertex would create `c-b₁-a-b₂-c`. -/
theorem thirdHandleChoices_disjoint_same_branch
    (G : SimpleGraph V) [DecidableRel G.Adj] (hc4 : ¬HasC4 G)
    {c b₁ b₂ : V} (hcb₁ : G.Adj c b₁) (hcb₂ : G.Adj c b₂)
    (hb : b₁ ≠ b₂) :
    Disjoint (thirdHandleChoices G c b₁) (thirdHandleChoices G c b₂) := by
  rw [Finset.disjoint_left]
  intro a ha₁ ha₂
  have hab₁ : G.Adj a b₁ := by
    simpa [thirdHandleChoices, adj_comm] using Finset.mem_of_mem_erase ha₁
  have hab₂ : G.Adj a b₂ := by
    simpa [thirdHandleChoices, adj_comm] using Finset.mem_of_mem_erase ha₂
  apply hc4
  refine ⟨c, b₁, a, b₂, ?_, ?_, ?_, ?_, ?_, ?_,
    hcb₁, hab₁.symm, hab₂, hcb₂.symm⟩
  · exact hcb₁.ne
  · exact (Finset.ne_of_mem_erase ha₁).symm
  · exact hcb₂.ne
  · exact hab₁.ne.symm
  · exact hb
  · exact hab₂.ne

/-- Outside neighbors of a geodesic target: remove its one or two path
neighbors. -/
def outsideTargetNeighbors {u v : V} (G : SimpleGraph V) (p : G.Walk u v)
    (k : ℕ) [DecidableRel G.Adj] : Finset V :=
  if k = 0 then (G.neighborFinset (p.getVert k)).erase (p.getVert 1)
  else ((G.neighborFinset (p.getVert k)).erase (p.getVert (k - 1))).erase
    (p.getVert (k + 1))

omit [Nonempty V] in
/-- At index zero a four-regular geodesic target has exactly three outside
neighbor slots. -/
theorem card_outsideTargetNeighbors_zero_eq_three
    (G : SimpleGraph V) [DecidableRel G.Adj] {u v : V}
    (p : G.Walk u v) (hp : 0 < p.length) (hreg : G.IsRegularOfDegree 4) :
    (outsideTargetNeighbors G p 0).card = 3 := by
  have hmem : p.getVert 1 ∈ G.neighborFinset (p.getVert 0) := by
    simpa using p.adj_getVert_succ hp
  change ((G.neighborFinset (p.getVert 0)).erase (p.getVert 1)).card = 3
  rw [Finset.card_erase_of_mem hmem, G.card_neighborFinset_eq_degree,
    hreg (p.getVert 0)]

omit [Nonempty V] in
/-- At an internal index `k`, a path in a four-regular graph leaves exactly
two outside neighbor slots. -/
theorem card_outsideTargetNeighbors_internal_eq_two
    (G : SimpleGraph V) [DecidableRel G.Adj] {u v : V}
    (p : G.Walk u v) (hpPath : p.IsPath) (hreg : G.IsRegularOfDegree 4)
    {k : ℕ} (hk0 : 0 < k) (hklen : k < p.length) :
    (outsideTargetNeighbors G p k).card = 2 := by
  have hprev : p.getVert (k - 1) ∈ G.neighborFinset (p.getVert k) := by
    have := p.adj_getVert_succ (i := k - 1) (by omega)
    simpa [Nat.sub_add_cancel (by omega : 1 ≤ k), adj_comm] using this
  have hnext : p.getVert (k + 1) ∈ G.neighborFinset (p.getVert k) := by
    simpa using p.adj_getVert_succ hklen
  have hne : p.getVert (k - 1) ≠ p.getVert (k + 1) := by
    intro h
    have hkprev : k - 1 ≤ p.length := by omega
    have hknext : k + 1 ≤ p.length := by omega
    have := hpPath.getVert_injOn hkprev hknext h
    omega
  have hnextErase : p.getVert (k + 1) ∈
      (G.neighborFinset (p.getVert k)).erase (p.getVert (k - 1)) := by
    exact Finset.mem_erase.mpr ⟨hne.symm, hnext⟩
  simp only [outsideTargetNeighbors, if_neg (by omega : k ≠ 0)]
  rw [Finset.card_erase_of_mem hnextErase, Finset.card_erase_of_mem hprev,
    G.card_neighborFinset_eq_degree, hreg (p.getVert k)]

end WrittenOnTheWallII.GraphConjecture133ThirdLayerCapacity
