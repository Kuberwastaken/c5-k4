import GraphConjecture141RadiusThreeAcyclic

/-!
# WOWII 141: simple-cycle path decomposition

This file packages the standard operation needed by the remaining radius-three
cycle-peak argument: rotate a simple cycle at a chosen intersection vertex and
remove that vertex, leaving a simple path between its two cycle neighbors.
-/

namespace WrittenOnTheWallII.GraphConjecture141CyclePathIntersection

open SimpleGraph

universe u
variable {V : Type u} [DecidableEq V]

/-- Every simple cycle, rotated at a vertex on it, has two distinct incident
cycle neighbors and a simple tail path.  Removing the last edge of that tail
still gives a simple path, namely the cycle with the chosen vertex deleted.

The equality of lengths records that rotation loses no edge; this is the
bookkeeping needed when a root path is spliced into one of the two cycle arcs.
-/
theorem simple_cycle_path_decomposition_at_intersection
    {G : SimpleGraph V} {v i : V} (c : G.Walk v v)
    (hc : c.IsCycle) (hi : i ∈ c.support) :
    ∃ q : G.Walk i i,
      q.IsCycle ∧ q.length = c.length ∧
      q.tail.IsPath ∧ q.tail.dropLast.IsPath ∧
      i ∉ q.tail.dropLast.support ∧
      G.Adj i q.snd ∧ G.Adj q.penultimate i ∧
      q.snd ≠ q.penultimate := by
  let q := c.rotate hi
  have hq : q.IsCycle := hc.rotate hi
  have hqnil : ¬q.Nil := hq.not_nil
  have htailPath : q.tail.IsPath := by
    rw [Walk.isPath_def, Walk.support_tail_of_not_nil q hqnil]
    exact hq.support_nodup
  have hdropPath : q.tail.dropLast.IsPath := by
    exact Walk.isPath_of_isSubwalk (Walk.isSubwalk_take q.tail _) htailPath
  have hiNot : i ∉ q.tail.dropLast.support := by
    have hn := htailPath.support_nodup
    rw [Walk.support_eq_concat q.tail] at hn
    rw [List.nodup_concat] at hn
    have hiDrop : i ∉ q.tail.support.dropLast := hn.1
    have htailLen : 1 ≤ q.tail.length := by
      have hthree := hq.three_le_length
      have htail := Walk.length_tail_add_one hqnil
      omega
    have hsupp : q.tail.dropLast.support = q.tail.support.dropLast := by
      rw [Walk.dropLast, Walk.take_support_eq_support_take_succ,
        List.dropLast_eq_take, Walk.length_support]
      congr 1
      omega
    intro hi
    apply hiDrop
    rwa [← hsupp]
  have hlen : q.length = c.length := by
    obtain ⟨n, hn⟩ := Walk.rotate_darts c hi
    have h := congrArg List.length hn
    simpa [q, Walk.length_darts] using h
  exact ⟨q, hq, hlen, htailPath, hdropPath, hiNot,
    q.adj_snd hqnil, q.adj_penultimate hqnil,
    hq.snd_ne_penultimate⟩

/-- A walk support meets a cycle support in a subsingleton whenever any two
common vertices agree.  This explicit set-level intersection formulation is
the shape used after choosing the last common vertex of two root paths. -/
lemma support_inter_cycle_subsingleton_of_pairwise
    {G : SimpleGraph V} {a b v : V} (p : G.Walk a b) (c : G.Walk v v)
    (hpair : ∀ x ∈ p.support, x ∈ c.support →
      ∀ y ∈ p.support, y ∈ c.support → x = y) :
    Set.Subsingleton ((p.support.toFinset : Set V) ∩
      (c.support.toFinset : Set V)) := by
  intro x hx y hy
  exact hpair x (by simpa using hx.1) (by simpa using hx.2)
    y (by simpa using hy.1) (by simpa using hy.2)

end WrittenOnTheWallII.GraphConjecture141CyclePathIntersection
