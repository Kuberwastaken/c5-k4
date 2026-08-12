# WoW I expansion sweep — numeric ids below 450

## Method and progress

This lane covers every row of `corpora/graffiti_wow.json` whose id matches
`^wow-(\d+)` with numeric base id below 450 and whose normalized status begins
with `open` or `unannotated`.  The frozen corpus contains **201** such rows:
154 unannotated, 45 open per Aouchiche–Hansen (2010), and 2 open per the WoW
annotation.  Suffixes such as `(2)` retain their numeric base id and are separate
rows.  Eligibility was counted independently with Python and `jq`.

For each row I test every legible, plausible reading against the required
arsenal: `C5[K_m]` for `m in {2,3,4,5,6,8}`, `C7[K3]`, `C9[K3]`, triangular
graphs `T(7),T(8),T(9)`, and the complement of `C5[K4]`.  A hypothesis that
none of these graphs satisfies is reported `N/A_ARSENAL`; a statement whose
mathematics cannot be recovered without guessing is reported `SKIP_OCR` with
the damaged text quoted.  Historical prose inside an otherwise unannotated row
is respected: an explicit proof or counterexample in that prose is not promoted
to a new open target.

Every apparent violation must first pass the DB-sanity gate under the identical
reading: all connected Graph Atlas graphs through order 7, cycles `C5`–`C9`,
`P7`, Petersen, `K3,3`, `K7`, stars, and complete bipartite calibration graphs.
A failure there is classified as corrupt OCR/misreading, not a kill.  A
gate-surviving violation is recomputed by an independent code path and checked
for novelty on the web before it can be called a counterexample.  Distance and
degree arithmetic is exact; spectral comparisons use a `1e-6` guard band.  Any
CBC/ILP invocation in this lane uses `timeLimit=60`.

Progress below is append-only at conjecture granularity.  Each completed row is
committed and pushed before the next row is recorded.

### wow-5 — HOLD

> average distance is not more than mode of distance + sum of reciprocals of degrees.

Reading `mode of distance` as the modal value among unordered-pair distances
(including diagonal zeroes is the only plausible alternative, and only increases
the right side when zero wins), every arsenal graph satisfies the bound.  The
regular diameter-two members have pair-distance mode 1 or 2 and
`sum_v 1/deg(v)=n/d`; for the carrier this gives
`27/19 <= 1 + 20/11` (and also `<= 2 + 20/11` under the other modal tie rule).
The other required blow-ups and triangular graphs have still larger margins.
All distance averages and reciprocal sums were evaluated exactly as rational
numbers.  No candidate violation arose, so the DB-sanity and novelty gates were
not triggered.

### wow-7 — HOLD

> mode of distance is not more than radius + Randic index.

Under both pair-distance conventions (unordered off-diagonal, or all
distance-matrix coordinates), direct evaluation gives the claimed bound
throughout the arsenal.  For `C5[K4]`, the pair mode is 1 (or 0/1 under matrix
counting), while `rad+R=2+10=12`.  No candidate violation arose.

### wow-8 — HOLD

> mode of distance is not more than average distance + Randic index.

Both plausible modal-distance conventions hold throughout the arsenal.  On
`C5[K4]`, the left side is 1 (with a possible zero/one tie if diagonal entries
are included) and the exact right side is `27/19+10=217/19`.  No candidate
violation arose.

### wow-10 — HOLD — source says proved

> average temperature is not more than rank. … This conjecture is correct.

With `temp(v)=deg(v)/(n-deg(v))` and adjacency-matrix rank, every arsenal graph
holds.  The low-rank complement of `C5[K4]` gives `2/3 <= 5`; the carrier gives
`11/9 <= 20`.  The historical row itself says the result is correct.

### wow-12 — HOLD

> radius is not more than 1 + Randic index.

Using `R=sum_{uv in E}1/sqrt(deg(u)deg(v))`, all arsenal graphs hold.  The
carrier gives `2 <= 11`; `C9[K3]`, the largest-radius arsenal member, gives
`4 <= 29/2`.  No candidate violation arose.

### wow-14 — HOLD

> radius is not more than average distance + Randic Index.

All arsenal graphs satisfy the standard reading.  For `C5[K4]`,
`2 <= 27/19+10`; for `C9[K3]`, `4 <= 31/13+27/2`.  Distance terms were
computed as exact rationals.

### wow-20 — HOLD

> The number of positive eigenvalues of a graph is not more than their sum.

Adjacency eigenvalues were counted with the `1e-6` zero guard.  Every arsenal
graph holds.  The carrier has 3 positive eigenvalues and positive-eigenvalue sum
approximately `21.944272`; no comparison lies within the guard band.

### wow-21 — HOLD

> The number of negative eigenvalues of a graph is not more than the sum of its positive eigenvalues.

Adjacency inertia uses the `1e-6` zero guard.  All arsenal graphs hold.  The
carrier gives `17 <= 21.944272…`; its complement has only 2 genuinely negative
eigenvalues (15 numerical zeroes are excluded), against positive sum
`12.944272…`.  No near-boundary case arose.

### wow-27 — HOLD — historical support recorded

> The standard deviation of the degree sequence < Randic.

Every arsenal member is regular, so its degree standard deviation is exactly
zero and the bound holds.  The row's truncated commentary records supporting
proof results; it is not treated as a new open claim.

### wow-32 — HOLD; alternate reading rejected

> The negative of the largest negative distance eigenvalue is not more than the matching number.

The Aouchiche–Hansen spectral-order reading, `-max{lambda<0} <= mu`, holds on
all arsenal graphs (left side 1 on the cycle blow-ups). Reading “largest” as
largest magnitude instead fails on `C7[K3]` and `C9[K3]`, but contradicts the
survey's explicit formula and is not a faithful reading.

### wow-54 — HOLD — historically proved

Regular-graph bound `n/d <= rank(A)` holds throughout: `C5[K4]` gives `20/11 <= 20`, and its rank-5 complement gives `5/2 <= 5`. The row explicitly records independent proofs.

### wow-63 — HOLD where applicable

The inherited triangle-free hypothesis selects only `complement(C5[K4])`; its average degree is 8 and its Randić index is 10. All other arsenal members contain triangles.

### wow-70 — RETRO-VIOLATION — already refuted

On the natural clique-coordinate reading, `C5[K4]` has `chi=10 > 8=max frequency`; the cycle blow-ups similarly fail. The same row explicitly records Staton's counterexample and Rödl's arbitrarily large gaps, so this is only a retro-witness.

### wow-71 — HOLD — historically proved

Every arsenal graph is bridgeless, so the cut-edge count is zero. The row explicitly records proofs by Shearer and Staton.

### wow-72 — HOLD — historically proved

All arsenal graphs are regular; direct temperature/depth evaluation holds (carrier `11/9 <= 18`). The row records independent proofs.

### wow-73 — HOLD

Every arsenal graph has no cut vertices, so the cut-vertex coordinate vector is empty/zero and its maximum is 0, at most `alpha`.

### wow-74 — HOLD

Every arsenal graph has no cut vertices, hence the relevant maximum coordinate is 0, at most the positive matching number.

### wow-75 — HOLD

Every arsenal graph has no cut vertices, hence the cut-vertex-coordinate variance is 0, at most `alpha`.

### wow-76 — HOLD

Every arsenal graph has no cut vertices; under the zero-vector convention its mode is 0, at most the matching number.

### wow-77 — HOLD

For all maximal/maximum-independent-set coordinate readings, the modal coordinate is at most the diameter (at most 4), whereas `n-residue` is at least 8 in the arsenal.

### wow-78 — HOLD

The maximal-independent-set coordinate mode is at most 4, while the smallest arsenal Randić index is 5.

### wow-80 — HOLD — historically proved

The coordinate mean is at most the diameter (at most 4), while `n-residue>=8`; the row also cites its proof from #79 and #98.

### wow-82 — HOLD — historically validated

Coordinate range for any maximal clique is at most `diameter+1<=5`, and `max Even>=5`; the row itself says the conjecture is valid for all maximal cliques.

### wow-83 — HOLD under surviving reading

The row says the unrestricted strongest version was refuted and retains dominating cliques. For a dominating clique its coordinate scope is at most 4, while `max Even>=5`.

### wow-84 — HOLD

A distance-to-clique coordinate vector supported in `[0,diam]` has variance at most `diam^2/4<=4`; every arsenal graph has `n-residue>=8`.

### wow-85 — HOLD

The same variance is at most 4, while the smallest adjacency rank in the arsenal is 5.

### wow-86 — SKIP_OCR

Garble: `variance of coordinates of a maximal clique maximum of Even.` The comparison operator is absent. Supplying one would be guessing; if intended `<=`, the arsenal holds.

### wow-87 — HOLD

Direct ordered distance-matrix variance is at most `1070/729` on the arsenal, while the smallest sum of reciprocal temperatures is 10.

### wow-88 — HOLD

Every plausible distance-matrix mode lies between 0 and 4; the smallest inverse-temperature sum is 10.

### wow-89 — HOLD

Exact average distance is at most `31/13`, while the smallest inverse-temperature sum is 10.

### wow-90 — HOLD on settled reading

For maximum independent sets the row invokes Chung's theorem; direct arsenal checks hold. The source distinguishes an all-maximal-set question and notes star failures of a stronger size reading.

### wow-91 — HOLD

Ordered distance-matrix variance is at most `1070/729`, below the smallest arsenal matching number 5.

### wow-92 — HOLD; strongest reading historically refuted

All plausible arsenal evaluations hold. The row itself reports that odd cycles above order 10 refute the strongest maximum-mode/maximum-set interpretation.

### wow-93 — HOLD

Exact average distances are at most their residues: `C9[K3]` gives `31/13 <= 3`, and `C5[K4]` gives `27/19 <= 2`.

### wow-94 — HOLD

Distance-matrix variance is at most `1070/729`, while every arsenal graph has independence number at least 2.

### wow-96 — HOLD — historically proved

The even-distance vector is constant on every vertex-transitive arsenal graph, so it has one distinct component value, at most residue 2 or 3. The row cites `[FMS1]`.

### wow-96(2) — SKIP_OCR

Garble: `William Staton. April 88.` This parser row is orphan commentary with no mathematical statement.

### wow-98 — HOLD — historically proved

All arsenal graphs satisfy `mu <= n-residue`; the closest small member gives `5 <= 8`. The row explicitly says the result is true for all graphs.

### wow-99 — HOLD

Distance-matrix variance is below 1.5, while `n-residue>=8` throughout the arsenal.

### wow-100 — HOLD

The even-distance vector is constant on every arsenal graph, so the maximum frequency is `n`, trivially at least `chi`.

### wow-102 — HOLD

For visible #102, degree variance is zero on every regular arsenal graph, below mean Even. OCR-appended #103/#104 also hold because these graphs have no cut vertices.

### wow-105 — N/A_ARSENAL

The tree hypothesis excludes every mandated arsenal graph.

### wow-106 — N/A_ARSENAL — historically proved

The tree hypothesis excludes every arsenal graph; the row cites `[FMS]` and characterizes equality.

### wow-109 — HOLD / historically refuted elsewhere

The even-distance-vector range is 0 on all vertex-transitive arsenal graphs. The row explicitly reports Puget's counterexample to the general statement.

### wow-111 — HOLD where applicable

The triangle-free hypothesis selects the carrier complement, where `floor(n/2)=10 <= mean Even=12`. The row discusses earlier stronger readings and counterexamples.

### wow-113 — HOLD

Every arsenal graph is regular, so maximal frequency in its degree sequence is `n`, far above average distance.

### wow-114 — RETRO-VIOLATION — already refuted

Under ordered distance-matrix coordinates, `C5[K4]` gives frequency 220 versus `sum Even=180`; `C5[K_m]`, `m>=3`, also fail. The row itself describes asymptotically unbounded counterexamples.

### wow-115 — HOLD

The even-distance vector has one distinct value; `sum_v 1/Even(v)=n/E` exceeds 1 throughout (minimum `40/17`).

### wow-120 — HOLD — historically proved

All arsenal graphs satisfy `alpha <= n-radius`; the carrier gives `2 <= 18` and its complement `8 <= 18`. The row says this follows from a theorem.

### wow-121 — HOLD where applicable

Inherited triangle-free reading selects the carrier complement: `2m=160 <= sum Even=240`.

### wow-122 — HOLD

Both binary Maxine-coordinate readings give a very loose RHS `n/mean = n^2/|I|`; all arsenal graphs hold.

### wow-123 — SKIP_OCR

Garble/ambiguity: `size/2 < the rank of the gravity matrix.` Literal edge-count reading already fails `K7`, so the intended formula cannot be recovered safely.

### wow-125 — HOLD

Matching number is at most the full gravity-matrix ranks found throughout the arsenal.

### wow-126 — HOLD

Radius is at most the number of negative gravity eigenvalues throughout; the carrier gives `2 <= 17`.

### wow-129 — HOLD

With standard normalized Laplacian spectral deviation, all regular arsenal members hold against Randić. An unnormalized sum reading fails basic graphs and is rejected.

### wow-130 — HOLD

Vertex deficiency is constant on every regular vertex-transitive arsenal graph, so its range is 0.

### wow-131 — HOLD

Direct exact evaluation gives `min deficiency <= |E|/average_distance` throughout the arsenal.

### wow-132 — HOLD — historically proved

Direct evaluation gives mean deficiency at most `|E|-mu`; the row cites `[FMS1]` and an equality characterization.

### wow-133 — SKIP_OCR

Garble: `Sum of reciprocals of components of twister < harmonic.` The invariant `twister` is undefined in the recovered material.

### wow-134 — HOLD

The Randić index is at most gravity-matrix rank throughout; even the largest arsenal value is `20 <= 40`.

### wow-135 — SKIP_OCR

Garble: `chromatic number / clique < independence of D2.` The historical `D2` construction and its independence invariant are not defined.

### wow-136 — HOLD

All arsenal graphs are regular, hence temperature deviation is 0 and the Randić RHS is positive.

### wow-142 — HOLD

The minimum positive adjacency eigenvalue is below exact `n/average_distance` throughout, outside the `1e-6` guard.

### wow-143 — HOLD

Variance of positive adjacency eigenvalues is at most `|E|/average_distance` throughout; spectral guard applied.

### wow-144 — HOLD

Variance of positive adjacency eigenvalues is at most `|E|-mu` throughout; spectral guard applied.

### wow-148 — HOLD

Exact average distance is at most the harmonic index throughout the regular arsenal.

### wow-149 — HOLD

Under both mean-entry conventions for the printed gravity matrix, mean gravity is at most `sum Odd` throughout.

### wow-150 — HOLD

The minimum consecutive gravity-eigenvalue gap is 0 because of multiplicities. A distinct-values-only parse is nonstandard and rejected.

### wow-151 — HOLD

Positive gravity inertia is at most matching number: cycle blow-ups have 3 positives; `T(n)` has `n`, still below its matching number.

### wow-152 — HOLD

Even- and odd-parity vectors are constant on every vertex-transitive arsenal graph, so both ranges are 0.

### wow-153 — HOLD

The odd-parity vector range is 0, at most the positive matching number.

### wow-154 — HOLD

Standard normalized adjacency spectral deviation is at most exact `n/average_distance`; an unnormalized-sum parse fails DB sanity and is rejected.

### wow-155 — SKIP_OCR

Garble: `mean of autocoordinates of Maxine of D2 < the matching number.` The construction is undefined/order-dependent.

### wow-156 — SKIP_OCR

Garble: `mean of autocoordinates of Maxine of D2 < the chromatic number.` The construction is undefined/order-dependent.

### wow-157 — HOLD

Radius is at most the smaller of minimum Odd and minimum Even counts throughout the arsenal.

### wow-159 — HOLD

Under edge-count `size`, `|E|/omega <= sum Even` throughout; the order reading also holds.

### wow-161 — SKIP_OCR

Garble: `maximum of autocoordinates of Maxine of the complement`. This representation-dependent historical construction is undefined.

### wow-162 — HOLD

`chi/omega` is at most the range of positive adjacency eigenvalues throughout; `1e-6` guard applied.

### wow-163 — HOLD

`chi/omega <= min Even` holds with wide margin throughout.

### wow-164 — HOLD

Degree mode is at most `|E|/average_distance` throughout; the alternative order reading also holds.

### wow-168 — HOLD

Minimum consecutive Laplacian-eigenvalue gap is 0 from multiplicities, below `n/alpha`.

### wow-169 — HOLD

Randić index is at most Laplacian rank `n-1` for every connected arsenal graph.

### wow-170 — HOLD

Temperature deviation is 0 on every regular arsenal graph.

### wow-171 — HOLD

Temperature deviation is 0 on every regular arsenal graph.

### wow-172 — HOLD

Minimum consecutive adjacency-eigenvalue gap is 0 from multiplicities, below `n/alpha`.

### wow-173 — HOLD

Exact `n/average_distance` is at most the Euclidean norm of the Laplacian spectrum throughout.

### wow-174 — HOLD

Because Even is constant, `sum 1/Even=n/E <= n/average_distance` throughout.

### wow-175 — SKIP_OCR

Garble: `mean of autocoordinates of Maxine of D2`. The construction is undefined/order-dependent.

### wow-176 — HOLD

Exact `n/alpha` is at most the sum of all temperatures throughout.

### wow-177 — HOLD

Even-parity range is 0 on all vertex-transitive arsenal members.

### wow-180 — HOLD

`sum 1/Even` is at most chromatic number throughout.

### wow-181 — SKIP_OCR

Garble: `range of resolution of Maxine < maximum of E.` Resolution of Maxine is undefined/order-dependent.

### wow-182 — SKIP_OCR

Garble: `mean of autocoordinates of Maxine of the complement`. The construction is undefined.

### wow-183 — SKIP_OCR

Garble: `length of autocoordinates of Maxine of the complement`. The construction is undefined.

### wow-184 — SKIP_OCR

Garble: `maximum of autocoordinates of Maxine of the complement`. The construction is undefined.

### wow-185 — HOLD where applicable

Inherited section condition `sum Odd < sum Even` selects `T(7..9)` and the carrier complement; all satisfy `|E|/alpha <= ||degree sequence||`.

### wow-191 — VIOLATED — NEW CANDIDATE

The inherited condition `sum Odd < sum Even` selects `T(n)=L(K_n)` and the carrier complement, not the cycle blow-ups. `T(7)` gives `min deficiency=20 > |E|/omega=105/6`; `T(8),T(9)` also fail, while the complement holds. The primary scan p.70 confirms `<=`. Independent exhaustive testing found zero failures on all 996 connected nonempty Atlas graphs through order 7 and all named calibration graphs. Independently, `def_min(T(n))=(n-2)(n-3)` and `|E|/omega=n(n-2)/2`, so every `n>=7` fails. Four novelty searches found no prior refutation of WoW #191 or this statement.

### wow-192 — DB_SANITY_FAIL / corrupt reading

Literal `mean Even <= n-mu` fails 50 applicable connected Atlas graphs through order 7 and also `T(9)` and the carrier complement. It is not a valid kill.

### wow-193 — HOLD where applicable

Under inherited `sum Odd < sum Even`, `mean Odd <= n-mu` holds: `T7` gives `10<=11`, `T8` `12<=14`, `T9` `14<=18`, complement `8<=10`.

### wow-195 — HOLD where applicable

Restoring inherited `sum Odd < sum Even` is essential: applicable `T(7..9)` and the carrier complement satisfy `lambda_max(A)<=max Even`. Cycle blow-ups and `K3` are inapplicable.

### wow-198 — HOLD where applicable

Minimum adjacency eigengap is 0 from multiplicities, at most `n/mean gravity` on all graphs satisfying the inherited section condition.

### wow-202 — HOLD where applicable

Every applicable arsenal graph is regular, so maximum degree frequency is `n`, above average distance.

### wow-203 — HOLD where applicable

Exact average distance is at most `sum 1/degree` on applicable `T(7..9)` and the carrier complement.

### wow-204 — SKIP_OCR

Garble: `length of autocoordinates of Maxine of D2`. The construction is undefined/order-dependent.

### wow-205 — HOLD

All arsenal graphs satisfy `n/2 <= n-residue`.

### wow-210 — HOLD

Average distance is at most the number of negative gravity eigenvalues throughout.

### wow-212 — SKIP_OCR / historically refuted

Garble: `Inverse coordinates of Maxine < n/2.` Maxine is representation-dependent, and the row explicitly gives `P5` as a counterexample.

### wow-213 — DB_SANITY_FAIL / SKIP_OCR

Literal `size/2 <= Randic` fails `K3,3` and the carrier complement, implying a lost radical or different size convention. The intended formula cannot be recovered.

### wow-214 — HOLD where applicable

Inherited triangle-free hypothesis selects the carrier complement: edge-size reading gives `80/8=10 <= 20-8=12`; order reading also holds.

### wow-216 — HOLD where applicable

On the triangle-free carrier complement, `|E|/alpha=10 <= mean Even=12`; order reading also holds.

### wow-217 — HOLD

Temperature deviation is 0 on every regular arsenal graph.

### wow-219 — HOLD

The second-largest gravity eigenvalue is far below the number of nonedges throughout (carrier representative about `2.48 <= 80`).

### wow-220 — HOLD where applicable

Under the following girth-section boundary, the statement's triangle-free reading selects the carrier complement, where `max Odd=8 <= mu=10`.

### wow-221 — N/A_ARSENAL

Inherited `girth>5` section hypothesis excludes every arsenal graph (all have girth 3 or 4).

### wow-222 — N/A_ARSENAL

Inherited `girth>5` section hypothesis excludes every arsenal graph.

### wow-223 — N/A_ARSENAL

Inherited `girth>5` section hypothesis excludes every arsenal graph.

### wow-225 — N/A_ARSENAL

Inherited `girth>5` section hypothesis excludes every arsenal graph.

### wow-226 — N/A_ARSENAL

Inherited `girth>5` section hypothesis excludes every arsenal graph.

### wow-228 — SKIP_OCR

`resolution of Maxine` is historical, order-dependent, and undefined in the recovered material.

### wow-229 — SKIP_OCR

`coordinates of resolution of Maxine` is undefined/order-dependent.

### wow-230 — SKIP_OCR

`autocoordinates of resolution of Maxine` is undefined/order-dependent.

### wow-231 — HOLD

Inherited regular hypothesis applies to all arsenal graphs. Exact evaluation of `chi <= n/average_distance` holds; e.g. `C5[K8]` gives `20 <= 312/11`.

<!-- NEXT -->
