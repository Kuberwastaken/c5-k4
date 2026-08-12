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

Progress: 43 / 54.
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
### wow-598 — HOLD

PDF p.100 restores `range of coordinates of matching <= n/average distance`, under the triangle-free heading. The applicable complement carrier has a perfect matching, so the endpoint set is all vertices and its coordinate vector is the constant degree vector; range `0 <= 20/(30/19)`. Any maximum matching gives the same endpoint set.
### wow-600 — HOLD

PDF p.101: `mean(Rainbow) <= inverse Odd`, still under the triangle-free heading. On the complement carrier, Odd is the constant vector 8, so inverse Odd is `20/8=5/2`; twin-class greedy-color recomputation gives mean Rainbow at most `8/5` (canonical and randomized order checks agree). Positive slack `9/10`.
### wow-602 — HOLD

PDF p.101: `n/independence <= range of coordinates of Maxine`, under the triangle-free heading. Every Maxine run on the complement carrier leaves an 8-vertex independent set; its coordinate values are `0,4,8`, so `5/2 <= 8`.
### wow-603 — HOLD

PDF p.101: `mean(dual degree) <= mean(Even)`, under the triangle-free heading. The complement carrier is 8-regular and has constant Even value 12, giving `8 <= 12`.
### wow-604 — HOLD

PDF p.101: `mean(Even) <= chi(G)+chi(complement G)`. For the complement carrier, exact structured colorings give `12 <= 3+10=13`.
### wow-605 — HOLD

PDF p.101: `maximum(Odd) <= chi(G)+chi(complement G)`. The complement carrier gives `8 <= 13`.
### wow-607 — HOLD

PDF p.101 restores `mean(Rainbow) <= size/independence`. As for 561, `mean(Rainbow) <= 2m/n` for any coloration, and every arsenal member has `alpha <= n/2`, so all try-out readings hold.
### wow-634 — HOLD_READINGS

PDF p.101, under the inherited condition `chi(complement G)=n-matching`: `inverse of coordinates of Maxine <= n/2`. The complement carrier is applicable. Maxine coordinates are eight 0s, eight 4s, and four 8s; the standard reciprocal sum over positive coordinates is `5/2 <= 10`. A literal reciprocal-of-zero reading is undefined, not a violation.
### wow-638 — HOLD

PDF p.102: `maximum(Rainbow) <= n/2`, under the 634--654 hypothesis. The complement carrier is applicable; its twin-class colorations give Rainbow values at most 2, versus `n/2=10`.
### wow-639 — HOLD

PDF p.102: `mean(Rainbow) <= Randic`, under the same hypothesis. On the 8-regular complement carrier, `Randic=n/2=10`, while every Rainbow component is at most the degree 8; all coloration readings hold.
### wow-644 — SOURCE_UNRECOVERABLE

The primary image on PDF p.102 itself reads `minimum of Dual Degree  mean of Odd` with no relation symbol. This is not an OCR loss: the printed source lacks the operator, so no mathematical assertion can be selected.
### wow-652 — HOLD

PDF p.103 separates the merged lines and gives `average distance <= inverse dual degree`. On the applicable complement carrier, dual degree is constantly 8, hence inverse dual degree is `20/8=5/2`, while average distance is `30/19`.
### wow-656 — HOLD

PDF p.103, under `sum(Even) <= sum(Odd)`: `size/independence <= sum of coordinates of a maximum clique`. The applicable C5[K_m] graphs have `alpha=2`, clique size `2m`, and degree `3m-1`; exact incidence counting proves the inequality for every `m` tested.
### wow-657 — HOLD

PDF p.103: `mean(Rainbow) <= size/independence`, under the same inherited condition. All applicable C5[K_m] members satisfy `mean(Rainbow)<=2m/n` and `alpha<=n/2`; hence the restored inequality holds for every coloration.
### wow-662 — HOLD

PDF p.103: `deviation of eigenvalues <= n-independence`, under the same condition. For each regular graph the eigenvalue RMS deviation is exactly `sqrt(d)`; on all applicable C5[K_m], `sqrt(3m-1) < 5m-2`, safely beyond the spectral guard.
### wow-693 — HOLD

PDF p.104 defines `m1` as the multiplicity of 1 as an adjacency eigenvalue over GF(2), then states `independence <= n-m1`. Exact binary row reduction gives RHS 5 on every C5[K_m], 7 on C7/C9 blow-ups, 15/28/28 on T(7/8/9), and 20 on the complement carrier; all hold.
### wow-694 — N/A_TRYOUT

PDF p.104: for an eigenvector `E` of the smallest adjacency eigenvalue, `frequency(max E) <= independence`. The source immediately warns eigenvectors are try-outs and suggests uniqueness as an additional hypothesis. Every arsenal member has a multiple smallest eigenvalue, so none meets that reading; the all-eigenvectors reading already fails on K3 and is DB-rejected.
### wow-695 — DB_REJECTED

PDF p.104: `range(nonpositive real adjacency eigenvalues) <= 1+n-m0`, with `m0` the GF(2) nullity of adjacency. The complement carrier violates: `2+2sqrt(5)=6.472135955 > 5` (`m0=16`). However two connected 7-vertex atlas graphs also violate (`F]rE?`: `sqrt(10)>3`; `FreRW`: `2sqrt(3)>3`, each `m0=5`). Mandatory gate therefore rejects this as a historical/source-level false entry, not a new kill.
### wow-697 — HOLD

PDF p.104: `range of the largest eigenvector <= n-m1`. Connected regular arsenal graphs have the unique Perron vector constant after the prescribed normalization, hence range zero; exact GF(2) values make every right side nonnegative.
### wow-701 — HOLD

PDF p.105: `average distance <= inverse Rainbow`. For any coloration, each positive Rainbow component is at most degree, so inverse Rainbow is at least `n/d` on these regular graphs. Exact distance sums verify `average distance <= n/d` throughout the arsenal.
### wow-702 — HOLD

PDF p.105: `mean temperature <= mean Rainbow`. The historical temperature is `d(v)/(n-d(v))`; on each regular arsenal graph its mean is `d/(n-d)`. Direct coloration evaluation and the lower bound Rainbow>=1 verify every member (the maximum temperature here is below the observed Rainbow mean).
### wow-704 — SOURCE_UNRECOVERABLE

The primary page itself prints `The range range of rainbow n - m1` without a relation symbol. This is not repairable from OCR: no inequality survives in the canonical source.
### wow-707 — N/A_TRYOUT

PDF p.105: `radius <= number of positive components of the smallest eigenvector`. The surrounding source says smallest-eigenvector statements are try-outs and proposes uniqueness as an added hypothesis. Every arsenal graph has a multiple smallest eigenvalue; all-vector readings fail the small-graph gate.
### wow-708 — N/A_TRYOUT

PDF p.105 defines `V` as the positive-component vector of a smallest eigenvector and `v=<V,V>`, then states `average distance <= v`. The smallest eigenspace is nonunique for every arsenal member, so the source's uniqueness reading has no admissible graph; unrestricted choices are representation-dependent and DB-unsafe.
### wow-710 — HOLD

PDF p.105: `m0 <= n-residue`, with GF(2) nullity `m0`. Exact binary elimination and independent Havel--Hakimi residue computation agree. The closest arsenal case is the complement carrier: `16 <= 20-3=17`; all others hold.
### wow-717 — HOLD

PDF p.106 restores `mean degree <= mean dual degree` and records it as proved. Every arsenal graph is regular, so neighbor-average degree equals degree at every vertex and equality holds exactly.
### wow-718 — HOLD_TIGHT

PDF p.107: `mean(dual degree)-mean degree <= scope(degree)`. Every arsenal member is regular, making both sides zero. Exact equality throughout.

