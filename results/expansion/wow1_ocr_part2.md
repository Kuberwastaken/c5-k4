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

Progress: 16 / 54.
### wow-456 — N/A_ARSENAL

PDF p.95: `The residue of the graph RP[2..n] is not more than pi(n).` The source cleanly restores `pi(n)` and identifies RP/residue definitions, but this is restricted to the number-theoretic RP construction; no arsenal graph is admissible.
### wow-458 — N/A_ARSENAL

PDF p.96: with `e(v)` the number of vertices at even distance from `v` in `RP[2..n]`, `sum_v 1/e(v) <= pi(n)`. The page image separates it from conjecture 470. It remains restricted to RP, outside the arsenal.
### wow-496 — N/A_ARSENAL

PDF p.97, under the explicit heading `Conjectures 494--536 are about Paley graphs`: `sum of coordinates of Maxine <= length of S`, where `S` is the quadratic-residue vector. No WoW-I arsenal member is a Paley graph.
### wow-503 — N/A_ARSENAL

PDF p.97: `frequency of minimum of rainbow <= pi(n)`, still under the Paley-graph heading. The source restores the right side but the inherited graph class excludes the arsenal.
### wow-509 — N/A_ARSENAL

PDF p.97: `mean rainbow <= frequency of maximum of eigenvalues of Laplacian`, under the Paley-graph heading. Source recovered; no admissible arsenal instance.
### wow-515 — N/A_ARSENAL

PDF p.98 restores the relation: `pi(n) <= sum of reciprocals of coordinates of a maximum clique.` It belongs to conjectures 494--536 about Paley graphs, so the arsenal is inapplicable.
### wow-516 — N/A_ARSENAL

PDF p.98: `deviation of S <= frequency of mode of eigenvalues of Laplacian.` Here `S` is the quadratic-residue vector introduced under the Paley heading. No arsenal instance.
### wow-529 — N/A_ARSENAL

PDF p.98: `deviation of S <= number of cubic residues less than n.` This is a number-theoretic/Paley statement, not a carrier-graph inequality.
### wow-547 — HOLD

PDF pp.98--99 defines mid-Degree by applying `ceil(depth/2)` Havel--Hakimi reductions, then states `alpha <= n - mode(mid-Degree)`. Recomputing the sequence from every arsenal degree sequence gives modes from 2 through 11; all inequalities hold. The closest relevant margin is still at least 3.
### wow-548 — HOLD

PDF p.99: `mode(mid-Degree) <= size / independence`. Exact Havel--Hakimi sequence recomputation gives, for example, `5 <= 110/2=55` on C5[K4] and `3 <= 80/8=10` on its complement; every arsenal member holds.
### wow-552 — HOLD

PDF p.99: `independence <= n - mean(mid-Degree)`. Exact rational means from the restored definition were checked for all arsenal graphs; C5[K4] gives `2 <= 20-24/5`, and its complement gives `8 <= 20-16/5`. All hold.
### wow-553 — HOLD

PDF p.99: `mean(mid-Degree) <= size / independence`. Exact rational evaluation holds throughout; the complement carrier gives the smallest observed slack, `16/5 <= 10`.
### wow-561 — HOLD

PDF p.99 restores `mean(Rainbow) <= size/independence`. Rainbow is the color-class-neighborhood vector defined in conjecture 245. For every coloration, `mean(Rainbow) <= average degree = 2m/n`; every arsenal graph has `alpha <= n/2`, hence `2m/n <= m/alpha`. All try-out readings hold.
### wow-568 — HOLD

PDF p.99: `number of positive eigenvalues - number of negative eigenvalues <= size/independence`. Guarded inertia (`1e-6`) and exact closed-form spectra agree. The left side is nonpositive on the blow-ups and triangular graphs and zero on the complement carrier; all hold.
### wow-574 — HOLD

PDF p.99: `chi(complement G)/independence <= mode(Even)`. On each regular diameter-two arsenal graph, Even is constant `n-d` (including the vertex at distance zero), so its mode is `n-d`; exact colorings leave positive slack throughout.
### wow-597 — HOLD

PDF p.100, within `Conjectures 595--605 are about triangle-free graphs`: `radius <= maximal frequency of Even`. The complement carrier is the applicable arsenal member; its Even vector is constant 12, so `2 <= 20`. Named triangle-free calibrators also hold.

