# Written on the Wall I source-recovery sweep — IDs >= 450

## Method and progress

Scope is the 54 records marked `SKIP_OCR` in `wow1_part2.md`. The canonical
July 2004 *Written on the Wall* PDF was classified first with `pdf-inspector`.
Although its lightweight classifier labels the container text-based, requested
page extraction reports every page as requiring OCR and warns of broken font
encoding. Consequently no extracted formula is trusted: relevant pages are
rasterized and read from the page image.

Each recovered statement is tested against the full handoff arsenal. Candidate
violations must pass the connected graph-atlas and named-graph DB-sanity gate,
an independent recomputation, and a novelty search. Exact arithmetic is used
where possible; spectral gaps at most `1e-6` are ties, and any ILP solve is
capped at 60 seconds. A source statement that is recovered but restricted to an
inapplicable construction is recorded as `N/A_ARSENAL`.

Progress: 1 / 54.
### wow-456 — N/A_ARSENAL

PDF p.95: `The residue of the graph RP[2..n] is not more than pi(n).` The source cleanly restores `pi(n)` and identifies RP/residue definitions, but this is restricted to the number-theoretic RP construction; no arsenal graph is admissible.

