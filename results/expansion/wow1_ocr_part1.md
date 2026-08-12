# WoW I source-recovery sweep — numeric ids below 450

## Method and progress

This lane revisits every below-450 row reported with a `SKIP_OCR` component in
`results/expansion/wow1_part1.md`.  The source is the canonical July 2004
*Written on the Wall* scan.  `pdf-inspector --detect` classified the 216-page
PDF as text-based, but its embedded font mapping produces unusable extracted
text; therefore every relevant statement is read from a rasterized image of
the original page and not reconstructed from the damaged transcription.

Recovered statements are evaluated against the complete HANDOFF arsenal.  Any
apparent violation must pass the identical-reading DB-sanity gate (all connected
nonempty Graph Atlas graphs through order 7 and all named calibration graphs),
independent recomputation, and a novelty search.  Exact arithmetic is used for
combinatorial and distance quantities, spectral comparisons have a `1e-6`
guard, and any ILP solve is capped at 60 seconds.  Entries remain `SKIP_OCR`
when the scan itself does not define a historical program-dependent invariant.

Progress is committed and pushed one recovered row at a time.

