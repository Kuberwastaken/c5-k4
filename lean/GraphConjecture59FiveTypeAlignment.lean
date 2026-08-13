import GraphConjecture59SynchronizedRows

/-!
# WOWII 59: the sharp five-type synchronization theorem

Encode the four dense subsets of a three-set by `Fin 4`: codes `0,1,2` are
the three complementary pairs, and code `3` is the full set.  A triple fails
to align exactly when its three codes are the distinct values `0,1,2`.

This file proves that every five distinct full row types contain a triple
aligned in both coordinates.  The global proof is symbolic; its sole bounded
classification is normalized to seven four-valued coordinates and certified
with ordinary Lean `decide` (not `native_decide`).  The file also gives an
explicit sharp four-type obstruction and a specialization to encoded graph
attachment rows.
-/

namespace WrittenOnTheWallII.GraphConjecture59FiveTypeAlignment

open SimpleGraph Finset

universe u

/-- Four possible dense subsets of one three-vertex color class. -/
abbrev SideType := Fin 4

/-- A full two-sided dense attachment type. -/
abbrev RowType := SideType × SideType

/-- The rotating-complement exception: three distinct proper side types. -/
abbrev Rotating (a b c : SideType) : Prop :=
  a.val < 3 ∧ b.val < 3 ∧ c.val < 3 ∧
    a ≠ b ∧ a ≠ c ∧ b ≠ c

/-- Three side types are aligned unless they are the rotating exception. -/
abbrev Aligned (a b c : SideType) : Prop := ¬Rotating a b c

/-- Simultaneous alignment in both color coordinates. -/
abbrev BiAligned (a b c : RowType) : Prop :=
  Aligned a.1 b.1 c.1 ∧ Aligned a.2 b.2 c.2

/-- A row family contains a three-element bi-aligned subfamily. -/
abbrev HasBiAlignedTriple (R : Finset RowType) : Prop :=
  ∃ a ∈ R, ∃ b ∈ R, ∃ c ∈ R,
    a ≠ b ∧ a ≠ c ∧ b ≠ c ∧ BiAligned a b c

/- The ten triples from five named rows. -/
abbrev FiveAligned (a b c d e : RowType) : Prop :=
  BiAligned a b c ∨ BiAligned a b d ∨ BiAligned a b e ∨
  BiAligned a c d ∨ BiAligned a c e ∨ BiAligned a d e ∨
  BiAligned b c d ∨ BiAligned b c e ∨ BiAligned b d e ∨
  BiAligned c d e

private def rotatingB (a b c : SideType) : Bool :=
  a.val < 3 && b.val < 3 && c.val < 3 && a != b && a != c && b != c

private def biAlignedB (a b c : RowType) : Bool :=
  !rotatingB a.1 b.1 c.1 && !rotatingB a.2 b.2 c.2

private def fiveAlignedB (a b c d e : RowType) : Bool :=
  biAlignedB a b c || (biAlignedB a b d || (biAlignedB a b e ||
  (biAlignedB a c d || (biAlignedB a c e || (biAlignedB a d e ||
  (biAlignedB b c d || (biAlignedB b c e ||
  (biAlignedB b d e || biAlignedB c d e))))))))

private theorem rotatingB_iff (a b c : SideType) :
    rotatingB a b c = true ↔ Rotating a b c := by
  simp [rotatingB, Rotating]
  tauto

private theorem biAlignedB_iff (a b c : RowType) :
    biAlignedB a b c = true ↔ BiAligned a b c := by
  simp [biAlignedB, BiAligned, Aligned, Bool.eq_false_iff, rotatingB_iff]

private theorem fiveAlignedB_iff (a b c d e : RowType) :
    fiveAlignedB a b c d e = true ↔ FiveAligned a b c d e := by
  simp only [fiveAlignedB, Bool.or_eq_true, biAlignedB_iff, FiveAligned]

private theorem fiveAligned_subset
    {R : Finset RowType} {a b c d e : RowType}
    (ha : a ∈ R) (hb : b ∈ R) (hc : c ∈ R) (hd : d ∈ R) (he : e ∈ R)
    (hab : a ≠ b) (hac : a ≠ c) (had : a ≠ d) (hae : a ≠ e)
    (hbc : b ≠ c) (hbd : b ≠ d) (hbe : b ≠ e)
    (hcd : c ≠ d) (hce : c ≠ e) (hde : d ≠ e)
    (h : FiveAligned a b c d e) : HasBiAlignedTriple R := by
  rcases h with h | h | h | h | h | h | h | h | h | h
  · exact ⟨a, ha, b, hb, c, hc, hab, hac, hbc, h⟩
  · exact ⟨a, ha, b, hb, d, hd, hab, had, hbd, h⟩
  · exact ⟨a, ha, b, hb, e, he, hab, hae, hbe, h⟩
  · exact ⟨a, ha, c, hc, d, hd, hac, had, hcd, h⟩
  · exact ⟨a, ha, c, hc, e, he, hac, hae, hce, h⟩
  · exact ⟨a, ha, d, hd, e, he, had, hae, hde, h⟩
  · exact ⟨b, hb, c, hc, d, hd, hbc, hbd, hcd, h⟩
  · exact ⟨b, hb, c, hc, e, he, hbc, hbe, hce, h⟩
  · exact ⟨b, hb, d, hd, e, he, hbd, hbe, hde, h⟩
  · exact ⟨c, hc, d, hd, e, he, hcd, hce, hde, h⟩

/- With the rotating coordinate normalized to `0,1,2`, only seven four-valued
coordinates remain.  This is the sole bounded kernel certificate. -/
set_option maxHeartbeats 1000000 in
private theorem fixed012
    (ay byy cy : SideType) (d e : RowType)
    (had : (0, ay) ≠ d) (hae : (0, ay) ≠ e)
    (hbd : (1, byy) ≠ d) (hbe : (1, byy) ≠ e)
    (hcd : (2, cy) ≠ d) (hce : (2, cy) ≠ e) (hde : d ≠ e) :
    FiveAligned (0, ay) (1, byy) (2, cy) d e := by
  apply fiveAlignedB_iff _ _ _ _ _ |>.mp
  revert ay byy cy d e
  decide

private theorem first_rotating_in
    {R : Finset RowType} (a b c d e : RowType)
    (ha : a ∈ R) (hb : b ∈ R) (hc : c ∈ R) (hd : d ∈ R) (he : e ∈ R)
    (hrot : Rotating a.1 b.1 c.1)
    (hab : a ≠ b) (hac : a ≠ c) (had : a ≠ d) (hae : a ≠ e)
    (hbc : b ≠ c) (hbd : b ≠ d) (hbe : b ≠ e)
    (hcd : c ≠ d) (hce : c ≠ e) (hde : d ≠ e) :
    HasBiAlignedTriple R := by
  rcases a with ⟨ax, ay⟩
  rcases b with ⟨bx, byy⟩
  rcases c with ⟨cx, cy⟩
  fin_cases ax <;> fin_cases bx <;> fin_cases cx <;> simp [Rotating] at hrot
  · exact fiveAligned_subset ha hb hc hd he hab hac had hae hbc hbd hbe hcd hce hde
      (fixed012 ay byy cy d e had hae hbd hbe hcd hce hde)
  · exact fiveAligned_subset ha hc hb hd he hac hab had hae hbc.symm
      hcd hce hbd hbe hde (fixed012 ay cy byy d e had hae hcd hce hbd hbe hde)
  · exact fiveAligned_subset hb ha hc hd he hab.symm hbc hbd hbe hac
      had hae hcd hce hde (fixed012 byy ay cy d e hbd hbe had hae hcd hce hde)
  · exact fiveAligned_subset hc ha hb hd he hac.symm hbc.symm hcd hce hab
      had hae hbd hbe hde (fixed012 cy ay byy d e hcd hce had hae hbd hbe hde)
  · exact fiveAligned_subset hb hc ha hd he hbc hab.symm hbd hbe hac.symm
      hcd hce had hae hde (fixed012 byy cy ay d e hbd hbe hcd hce had hae hde)
  · exact fiveAligned_subset hc hb ha hd he hbc.symm hac.symm hcd hce hab.symm
      hbd hbe had hae hde (fixed012 cy byy ay d e hcd hce hbd hbe had hae hde)

private def swapRow (a : RowType) : RowType := (a.2, a.1)

private theorem swapRow_injective : Function.Injective swapRow := by
  rintro ⟨a₁, a₂⟩ ⟨b₁, b₂⟩ h
  simpa [swapRow] using congrArg swapRow h

private theorem hasBiAlignedTriple_image_swap (R : Finset RowType)
    (h : HasBiAlignedTriple R) : HasBiAlignedTriple (R.image swapRow) := by
  rcases h with ⟨a, ha, b, hb, c, hc, hab, hac, hbc, halign⟩
  refine ⟨swapRow a, mem_image.mpr ⟨a, ha, rfl⟩,
    swapRow b, mem_image.mpr ⟨b, hb, rfl⟩,
    swapRow c, mem_image.mpr ⟨c, hc, rfl⟩, ?_, ?_, ?_, ?_⟩
  · exact swapRow_injective.ne hab
  · exact swapRow_injective.ne hac
  · exact swapRow_injective.ne hbc
  · simpa [swapRow, BiAligned, and_comm] using halign

private theorem second_rotating_in
    {R : Finset RowType} (a b c d e : RowType)
    (ha : a ∈ R) (hb : b ∈ R) (hc : c ∈ R) (hd : d ∈ R) (he : e ∈ R)
    (hrot : Rotating a.2 b.2 c.2)
    (hab : a ≠ b) (hac : a ≠ c) (had : a ≠ d) (hae : a ≠ e)
    (hbc : b ≠ c) (hbd : b ≠ d) (hbe : b ≠ e)
    (hcd : c ≠ d) (hce : c ≠ e) (hde : d ≠ e) :
    HasBiAlignedTriple R := by
  have hs := first_rotating_in (R := R.image swapRow)
    (swapRow a) (swapRow b) (swapRow c) (swapRow d) (swapRow e)
    (mem_image.mpr ⟨a, ha, rfl⟩) (mem_image.mpr ⟨b, hb, rfl⟩)
    (mem_image.mpr ⟨c, hc, rfl⟩) (mem_image.mpr ⟨d, hd, rfl⟩)
    (mem_image.mpr ⟨e, he, rfl⟩) hrot
    (swapRow_injective.ne hab) (swapRow_injective.ne hac)
    (swapRow_injective.ne had) (swapRow_injective.ne hae)
    (swapRow_injective.ne hbc) (swapRow_injective.ne hbd)
    (swapRow_injective.ne hbe) (swapRow_injective.ne hcd)
    (swapRow_injective.ne hce) (swapRow_injective.ne hde)
  have hi := hasBiAlignedTriple_image_swap _ hs
  simpa [swapRow] using hi

private theorem hasBiAlignedTriple_mono {R S : Finset RowType}
    (hRS : R ⊆ S) (h : HasBiAlignedTriple R) : HasBiAlignedTriple S := by
  rcases h with ⟨a, ha, b, hb, c, hc, hab, hac, hbc, halign⟩
  exact ⟨a, hRS ha, b, hRS hb, c, hRS hc, hab, hac, hbc, halign⟩

/-- **Sharp finite kernel.** Every five distinct full dense row types contain
a triple aligned in both color coordinates. -/
theorem five_distinct_types_have_bialigned_triple :
    ∀ R : Finset RowType, R.card = 5 → HasBiAlignedTriple R := by
  intro R hRcard
  let e : Fin 5 ≃ ↑R := (R.equivFinOfCardEq hRcard).symm
  let f : Fin 5 → RowType := fun i ↦ e i
  have hf : Function.Injective f := fun i j hij ↦ e.injective (Subtype.ext hij)
  let a := f 0
  let b := f 1
  let c := f 2
  let d := f 3
  let z := f 4
  have ha : a ∈ R := (e 0).property
  have hb : b ∈ R := (e 1).property
  have hc : c ∈ R := (e 2).property
  have hd : d ∈ R := (e 3).property
  have hz : z ∈ R := (e 4).property
  have hab : a ≠ b := hf.ne (by decide)
  have hac : a ≠ c := hf.ne (by decide)
  have had : a ≠ d := hf.ne (by decide)
  have haz : a ≠ z := hf.ne (by decide)
  have hbc : b ≠ c := hf.ne (by decide)
  have hbd : b ≠ d := hf.ne (by decide)
  have hbz : b ≠ z := hf.ne (by decide)
  have hcd : c ≠ d := hf.ne (by decide)
  have hcz : c ≠ z := hf.ne (by decide)
  have hdz : d ≠ z := hf.ne (by decide)
  by_cases hbase : BiAligned a b c
  · exact ⟨a, ha, b, hb, c, hc, hab, hac, hbc, hbase⟩
  · have hrot : Rotating a.1 b.1 c.1 ∨ Rotating a.2 b.2 c.2 := by
      simpa [BiAligned, Aligned] using not_and_or.mp hbase
    rcases hrot with hrot | hrot
    · exact first_rotating_in a b c d z ha hb hc hd hz hrot
        hab hac had haz hbc hbd hbz hcd hcz hdz
    · exact second_rotating_in a b c d z ha hb hc hd hz hrot
        hab hac had haz hbc hbd hbz hcd hcz hdz

/-- An explicit four-type family witnessing sharpness of the threshold. -/
def sharpFour : Finset RowType :=
  {(⟨0, by omega⟩, ⟨1, by omega⟩),
   (⟨0, by omega⟩, ⟨2, by omega⟩),
   (⟨1, by omega⟩, ⟨0, by omega⟩),
   (⟨2, by omega⟩, ⟨0, by omega⟩)}

/-- The four-type obstruction has four distinct members and no bi-aligned
triple.  This fixed finite certificate also uses ordinary kernel `decide`. -/
theorem sharpFour_certificate :
    sharpFour.card = 4 ∧ ¬HasBiAlignedTriple sharpFour := by
  decide

/-- Graph-facing specialization.  Once dense attachment rows have been coded
by the four side types, five distinct codes force a controlled bi-aligned
three-type subfamily. -/
theorem five_encoded_graph_rows_have_bialigned_triple
    {W : Type u} [DecidableEq W]
    (X : Finset W) (rowCode : W → RowType)
    (hfive : 5 ≤ (X.image rowCode).card) :
    ∃ R ⊆ X.image rowCode,
      R.card = 5 ∧ HasBiAlignedTriple R := by
  obtain ⟨R, hRsub, hRcard⟩ := exists_subset_card_eq hfive
  refine ⟨R, hRsub, hRcard, ?_⟩
  exact five_distinct_types_have_bialigned_triple R hRcard

end WrittenOnTheWallII.GraphConjecture59FiveTypeAlignment
