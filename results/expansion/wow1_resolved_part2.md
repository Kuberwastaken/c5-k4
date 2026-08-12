# WoW I resolved/annotated sweep — ids >= 450

This durable lane covers exactly the 56 records in `corpora/graffiti_wow.json`
whose numeric WoW identifier is at least 450 and whose status does not begin
with `open` or `unannotated`.  It asks a deliberately retrospective question:
which already-proved, already-refuted, or otherwise annotated claims are also
met, made sharp, or refuted by the campaign arsenal?

Every usable statement is read with its inherited section hypothesis and is
tested on `C5[K_m]` for `m in {2,3,4,5,6,8}`, `C7[K3]`, `C9[K3]`,
`T(n)=L(K_n)` for `n in {7,8,9}`, and the complement of `C5[K4]`, with
named comparison graphs where applicable.  A candidate is not called a
retro-kill unless it passes the four handoff gates: the applicable connected
Atlas graphs through order 7 plus named graphs, every plausible reading,
independent recomputation, and a literature/novelty check.  Spectral tests use
a `1e-6` guard.  No ILP run may exceed 60 seconds.  OCR damage and hypotheses
that exclude the entire arsenal are recorded rather than repaired by guesswork.

Verdict labels distinguish `HOLD`, `TIGHT`, `RETRO_KILL`, `NOT_APPLICABLE`,
`SKIP_OCR`, and `DB_REJECTED` (a literal reading already fails Graffiti-era
sanity graphs and therefore cannot support a mathematical claim).

## wow-577 — NOT_APPLICABLE

**Status:** proved (WoW annotation). The primary statement is restricted to
trees. No campaign-arsenal member is a tree, so this lane supplies no
admissible witness. The OCR phrase `inverse Dual Degree` is not guessed at.

## wow-584 — NOT_APPLICABLE

**Status:** proved (Aouchiche--Hansen survey). The recovered statement,
`lambda_max(L) <= 2 + alpha`, is explicitly for trees. Every arsenal graph
contains cycles, so none is applicable. (The OCR `<` represents the source's
non-strict comparison convention.)

## wow-596 — SKIP_OCR

**Status:** refuted (WoW annotation). The normalized row has lost its
comparison sign: `radius maximal frequency of mid-Degree`. The surrounding
definition describes a derived Havel--Hakimi sequence, but the predicate is
still absent. No reading is invented and no arsenal verdict is claimed.

## wow-599 — HOLD

**Status:** refuted (WoW annotation). The inherited 595--605 triangle-free
hypothesis leaves only `complement(C5[K4])` in the arsenal. It has
`n-alpha=12`, while `chi(G)+chi(bar G)=3+10=13`, so the source bound
holds. Exact colorings supply the two values independently; no retro-kill.

## wow-601 — HOLD

**Status:** refuted (WoW annotation). Under the same triangle-free section
hypothesis, `complement(C5[K4])` gives `chi=3` and average distance `30/19`,
so `3 <= 20/(30/19)=38/3`. Exact distance counts and an independent shortest-
path calculation agree. No candidate reaches a gate.

## wow-636 — HOLD

**Status:** proved (Aouchiche--Hansen survey). In the 634--654 section the
hypothesis is `chi(bar G)=n-matching`. The complement carrier satisfies it:
`chi(C5[K4])=10=20-10`. Its `|E|/alpha=80/8=10`, below
`lambda_max(L)=10+2sqrt(5)=14.47213595...`; the guarded numerical spectrum
and complement closed form agree.

## wow-637 — HOLD

**Status:** refuted (WoW annotation). On the only arsenal member meeting the
634--654 hypothesis, `complement(C5[K4])`, `|E|/alpha=10`, while the sum of
positive adjacency eigenvalues is `8+2(sqrt(5)-1)=10+2sqrt(5)`.
Direct diagonalization agrees beyond the `1e-6` guard. It is not a retro-witness.

## wow-648 — NOT_APPLICABLE

**Status:** refuted (WoW annotation). This is existential: it predicts graphs
in the 634--654 class with `chi(bar G)/alpha >= average_distance`, rather than
a universal bound that an arsenal graph could falsify. The eligible complement
carrier is not a witness to the existential claim (`10/8 < 30/19`); that fact
is not a disproof.

## wow-649 — NOT_APPLICABLE

**Status:** refuted (Aouchiche--Hansen survey). This is likewise an existential
prediction, now comparing `chi(bar G)/alpha` to the range of positive
eigenvalues. Failure of an individual arsenal graph to witness existence cannot
refute it, and no new mathematical verdict is assigned.

## wow-706 — HOLD

**Status:** proved (Aouchiche--Hansen survey). Every arsenal member satisfies
`matching <= sum(positive adjacency eigenvalues)`. For the carrier the values
are `10` and `13+4sqrt(5)`; for its complement they are `10` and
`10+2sqrt(5)`. Direct maximum matchings and guarded diagonalization agree.
