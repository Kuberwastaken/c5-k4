# Written on the Wall I expansion sweep — IDs >= 450

## Method and progress

Scope is the 208 records in `corpora/graffiti_wow.json` whose identifiers match
`^wow-(\d+)` with numeric base at least 450 and whose status begins `open` or
`unannotated`. Suffix records (for example `wow-765(2)` and `wow-891a`) are
distinct corpus entries. Each record below is written and committed separately.

Every record is tested against the complete handoff arsenal: `C5[K_m]` for
`m in {2,3,4,5,6,8}`, `C7[K3]`, `C9[K3]`, `T(7)`, `T(8)`, `T(9)`, and the
complement of `C5[K4]`. A statement restricted to another graph class or to a
specific constructed graph is marked `N/A_ARSENAL`; this is a tested hypothesis
failure, not a claim about that conjecture. OCR text too damaged to determine a
mathematical assertion is marked `SKIP_OCR`, quoting the surviving text without
repair or guesswork. Apparent violations alone trigger the full database-sanity
gate (all connected atlas graphs through order 7 plus named calibration graphs),
an independent second computation, and a novelty search. Exact rational
arithmetic is used for degree/distance quantities; spectral comparisons have a
`1e-6` guard. No ILP solve is allowed beyond 60 seconds.

Progress: 1 / 208.

### wow-450 — N/A_ARSENAL

> "If G is the RG(n)-graph then the matching = n — independence."

The assertion is restricted to the specifically constructed `RG(n)` graph; none
of the campaign graphs is asserted or evidenced to be an `RG(n)` instance.
Accordingly this carrier arsenal cannot test the equality. The text is readable
enough to preserve the hypothesis, so this is `N/A_ARSENAL`, not `SKIP_OCR`.
