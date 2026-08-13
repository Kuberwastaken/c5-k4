import GraphConjecture141UniqueParent

/-!
# WOWII 141: maximum-rank cycle peak and the closed radius-three branch

On a finite simple cycle, choose a support vertex of maximum BFS rank.  The
two incident cycle neighbors cannot have equal rank by layer independence and
cannot have larger rank by maximality, so adjacency forces both exactly one
layer lower.  This supplies the last field of the radius-three forest
certificate.
-/

namespace WrittenOnTheWallII.GraphConjecture141CyclePeak

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture141DistanceFour
open WrittenOnTheWallII.GraphConjecture141RadiusThreeAcyclic
open WrittenOnTheWallII.GraphConjecture141RadiusThreeLayers
open WrittenOnTheWallII.GraphConjecture141UniqueParent

universe u
variable {V : Type u} [DecidableEq V]

/-- A maximum-distance vertex of an arbitrary simple cycle is a genuine BFS
peak: its two cycle neighbors are distinct and both one rank lower. -/
theorem cyclePeak_of_radiusThreeCenter
    (G : SimpleGraph V) (hconn : G.Connected) (hgirth : 9 ≤ G.girth)
    (r : V) (hrad : RadiusThreeCenter G r) :
    ∀ v (c : G.Walk v v), c.IsCycle →
      ∃ i x y,
        i ≠ r ∧ G.Adj i x ∧ G.Adj i y ∧ x ≠ y ∧
        G.dist r x + 1 = G.dist r i ∧
        G.dist r y + 1 = G.dist r i := by
  intro v c hc
  let S : Finset V := c.support.toFinset
  have hS : S.Nonempty := ⟨v, by simp [S]⟩
  obtain ⟨i, hiS, hiMax⟩ := S.exists_mem_eq_sup hS (G.dist r)
  have hi : i ∈ c.support := by simpa [S] using hiS
  let q := c.rotate hi
  have hq : q.IsCycle := hc.rotate hi
  have hqnil : ¬q.Nil := hq.not_nil
  let x := q.snd
  let y := q.penultimate
  have hxq : x ∈ q.support :=
    List.mem_of_mem_tail (q.snd_mem_tail_support hqnil)
  have hyq : y ∈ q.support := by
    exact List.mem_of_mem_dropLast (q.penultimate_mem_dropLast_support hqnil)
  have hmax (z : V) (hzq : z ∈ q.support) : G.dist r z ≤ G.dist r i := by
    have hzc : z ∈ c.support := (c.mem_support_rotate_iff hi).mp hzq
    have hzS : z ∈ S := by simpa [S] using hzc
    rw [← hiMax]
    exact Finset.le_sup hzS
  have hir : i ≠ r := by
    intro hir
    subst i
    have hxle := hmax x hxq
    have hix : G.Adj r x := by simpa [q, x] using q.adj_snd hqnil
    rw [SimpleGraph.dist_self] at hxle
    have hzero : G.dist r x = 0 := Nat.eq_zero_of_le_zero hxle
    exact hix.ne ((hconn.dist_eq_zero_iff).mp hzero)
  have hix : G.Adj i x := by simpa [q, x] using q.adj_snd hqnil
  have hiy : G.Adj i y := by simpa [q, y] using (q.adj_penultimate hqnil).symm
  have hxy : x ≠ y := by simpa [q, x, y] using hq.snd_ne_penultimate
  have hiRank : G.dist r i ≤ 3 := hrad i
  have hxne : G.dist r x ≠ G.dist r i := by
    intro heq
    have hind := bfsLayer_independent_of_eight_le_girth
      G hconn (by omega) r (G.dist r i) hiRank
    exact hind (by rfl) heq hix.ne hix
  have hyne : G.dist r y ≠ G.dist r i := by
    intro heq
    have hind := bfsLayer_independent_of_eight_le_girth
      G hconn (by omega) r (G.dist r i) hiRank
    exact hind (by rfl) heq hiy.ne hiy
  have hxle := hmax x hxq
  have hyle := hmax y hyq
  have hxrank : G.dist r x + 1 = G.dist r i := by
    rcases hix.diff_dist_adj (u := r) with h | h | h <;> omega
  have hyrank : G.dist r y + 1 = G.dist r i := by
    rcases hiy.diff_dist_adj (u := r) with h | h | h <;> omega
  exact ⟨i, x, y, hir, hix, hiy, hxy, hxrank, hyrank⟩

/-- The complete radius-three forest certificate, with both `uniqueParent`
and `cyclePeak` derived from connectedness and girth. -/
noncomputable def radiusThreeForestCertificate
    (G : SimpleGraph V) (hconn : G.Connected) (hgirth : 9 ≤ G.girth)
    (r : V) (hrad : RadiusThreeCenter G r) :
    RadiusThreeForestCertificate G :=
  radiusThreeForestCertificate_of_cyclePeak G hconn hgirth r hrad
    (cyclePeak_of_radiusThreeCenter G hconn hgirth r hrad)

/-- The previously abstract BFS-peak property is now unconditional for
connected graphs of girth at least nine. -/
theorem radiusThreeBfsPeakProperty_of_connected_of_nine_le_girth
    (G : SimpleGraph V) (hconn : G.Connected) (hgirth : 9 ≤ G.girth) :
    RadiusThreeBfsPeakProperty G := by
  intro r hrad
  exact ⟨radiusThreeForestCertificate G hconn hgirth r hrad, rfl, rfl⟩

/-- **Closed radius-three branch.** A connected graph of girth at least ten
has no radius-three center; equivalently every root reaches distance four. -/
theorem everyVertexHasDistanceAtLeastFour_of_connected_of_ten_le_girth
    (G : SimpleGraph V) (hconn : G.Connected) (hgirth : 10 ≤ G.girth) :
    EveryVertexHasDistanceAtLeastFour G := by
  exact everyVertexHasDistanceAtLeastFour_of_radiusThreeBfsPeak G hgirth
    (radiusThreeBfsPeakProperty_of_connected_of_nine_le_girth
      G hconn (by omega))

end WrittenOnTheWallII.GraphConjecture141CyclePeak
