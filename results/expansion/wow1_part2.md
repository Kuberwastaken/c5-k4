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

Progress: 183 / 208.

### wow-450 — N/A_ARSENAL

> "If G is the RG(n)-graph then the matching = n — independence."

The assertion is restricted to the specifically constructed `RG(n)` graph; none
of the campaign graphs is asserted or evidenced to be an `RG(n)` instance.
Accordingly this carrier arsenal cannot test the equality. The text is readable
enough to preserve the hypothesis, so this is `N/A_ARSENAL`, not `SKIP_OCR`.

### wow-454 — N/A_ARSENAL

> "The number of primes not more than n is not more than the number of distinct
> eigenvalues of RP[2..n] (defined in 434)."

This is a statement about the number-theoretic graph `RP[2..n]`, not an arbitrary
connected graph. No arsenal member has that construction, so the carrier sweep
does not furnish an instance. `N/A_ARSENAL`.

### wow-456 — SKIP_OCR

> "The residue of the graph RP[2..n] is not more than n(n). RP is defined in
> 484 ... A457. The number of quadratic residues mod n is not more than the rank
> of Two vertices in RP are adjacent iff they are relatively prime."

The record has merged at least two numbered assertions, and the right side
`n(n)` plus the object following "rank of" are missing. There is no faithful
inequality to evaluate, and the `RP` restriction would in any case exclude the
arsenal. No intended notation is guessed.

### wow-458 — SKIP_OCR

> "Let e(v) be the number of vertices at even distance from v in RP[2..n]/ ...
> The sum of reciprocals of e(v) is not more than n(n). A70. Let S be ..."

The unknown `n(n)` right-hand side and the merge into a different `PR[S]`
conjecture make this unusable. Both surviving clauses concern constructed
number-theoretic graphs rather than the arsenal. No repair is inferred.
### wow-496 — SKIP_OCR

> "sum of coordinates of Maxine < length of S. A97. size - order < the number of triangles."

Two assertions are fused, `S` is undefined, and the first inequality has no recoverable graph object. No interpretation is guessed.
### wow-503 — SKIP_OCR

> "frequency of minimum of rainbow < a(n)."

Neither `rainbow` nor `a(n)` is defined in this record, and OCR has lost the surrounding construction. There is no determinate numerical assertion to test.

### wow-504 — N/A_ARSENAL

> "the number of square-free integers not exceeding n and being products of even number of primes [inequality lost] sum of reciprocals of coordinates of Maxine."

The comparison sign is lost and the left side is number-theoretic. None of the arsenal graphs supplies the required integer construction; no repair is guessed.

### wow-509 — SKIP_OCR

> "mean rainbow < frequency of maximum of eigenvalues of Laplacian."

`Rainbow` is an undocumented coordinate try-out in this extracted record, so its mean cannot be recovered faithfully. The Laplacian side alone is insufficient.

### wow-513 — N/A_ARSENAL

> "chromatic number of a Paley graph with n vertices is not more than the number of primes not more than n."

The hypothesis is specifically a Paley graph. The WoW-I handoff arsenal contains no Paley graph (Paley additions belong only to the AGX lane), so this lane has no admissible instance.

### wow-515 — SKIP_OCR

> "pi(n) sum of reciprocals of coordinates of a maximum clique."

The relation symbol between the two quantities is absent. Consequently no inequality or equality survives to evaluate.

### wow-516 — SKIP_OCR

> "deviation of S < frequency of mode of eigenvalues of Laplacian."

The set/vector `S` is undefined in the surviving record. Testing a guessed spectral sequence would violate the no-guess OCR rule.

### wow-523 — N/A_ARSENAL

> "mode of eigenvalues of Laplacian < number of square-free integers not greater than n."

The right side is tied to the preceding number-theoretic construction rather than a graph invariant supplied for arbitrary arsenal graphs. No arsenal instance is established.

### wow-528 — N/A_ARSENAL

> "the number of square-free integers not exceeding n and being products of odd number of primes < 2(chromatic number)."

This belongs to the number-theoretic graph sequence in the surrounding section. The carrier arsenal is not that sequence, so it provides no admissible test.

### wow-529 — SKIP_OCR

> "deviation of S < number of cubic residues less than n."

`S` is missing from the extracted statement and the number-theoretic construction is not recoverable from this record. No guessed vector is evaluated.

### wow-536 — N/A_ARSENAL

> "The number of cubic nonresidues < n / average distance of Paley graph with n vertices."

This is explicitly restricted to Paley graphs. None occurs in this WoW-I arsenal, hence no campaign graph can witness or refute it.

### wow-537 — N/A_ARSENAL

> "If G is a connected Cayley graph of cyclic groups with at least two vertices then chromatic number < rank."

No arsenal graph is supplied with a cyclic Cayley representation satisfying the stated hypothesis. The lane therefore has no admissible instance.

### wow-538 — N/A_ARSENAL

> "If G is a connected Cayley graph of cyclic groups ... maximum of the rainbow ... < number of negative eigenvalues."

The cyclic-Cayley hypothesis is not established for any arsenal member, and `rainbow` is not recoverable as an invariant from the record. No carrier test is admissible.

### wow-543 — HOLD

> "n — independence < the sum of positive eigenvalues."

Interpreting WoW's comparison convention as `n-alpha <= sum(lambda_i>0)`, all
arsenal members hold with spectral gaps safely above `1e-6`. The closest is the
complement of `C5[K4]`: `n-alpha=12`, while the positive adjacency spectral sum
is exactly `8 + 8((sqrt(5)-1)/2) = 4+4sqrt(5) ~= 12.944271910`, slack
`0.944271910`. Direct symmetric eigensolution and an independent dense-matrix
`eigvalsh` recomputation agree. An initial mental-arithmetic concern was
withdrawn before the DB gate because exact recomputation showed no violation.
### wow-547 — SKIP_OCR

> "independence < n — modeofmid — Degree."

The OCR leaves two subtraction marks around a fused `modeofmid-Degree` token; the intended grouping and invariant are not reliably recoverable.

### wow-548 — SKIP_OCR

> "mode of mid-Degree < size independence."

The corpus does not preserve the mid-Degree sequence definition with enough precision to reproduce its mode for this sweep. No substitute invariant is guessed.

### wow-552 — SKIP_OCR

> "independence < n- mean of mid-Degree."

The `mid-Degree` derived sequence is not recoverable faithfully from this isolated OCR record, so its mean cannot be certified.

### wow-553 — SKIP_OCR

> "mean of mid-Degree < size independence."

As in wow-552, the operative derived-sequence definition is unavailable in a sufficiently reliable form. No guessed Havel-Hakimi variant is used.

### wow-561 — SKIP_OCR

> "If G is a connected graph then the mean of Rainbow < size independence."

`Rainbow` is an undocumented coordinate try-out here. Its mean is not a standard invariant and cannot be reconstructed from the OCR text.

### wow-568 — SKIP_OCR

> "IfG is a connected graph then the number of positive eigenvalues - number Size independence. of negative eigenvalues <"

The inequality is scrambled: `size independence` occurs inside the spectral expression and the right-hand side is absent. No plausible reading is privileged.

### wow-574 — SKIP_OCR

> "If G is a connected graph then the BromaticnumberofcomplementofG < mode independence of Even."

The fused text does not determine whether the right side is a mode of an `Even` coordinate sequence or an independence expression; the invariant and grouping are unrecoverable.

### wow-578 — N/A_ARSENAL

> "If G is a tree then the radius < range of positive eigenvalues."

Every arsenal member contains cycles, so none satisfies the tree hypothesis. No carrier test is admissible.

### wow-582 — N/A_ARSENAL

> "If G is a tree then the independence < number of componnents of 1-Residue."

No arsenal member is a tree. The hypothesis fails throughout the lane.

### wow-595 — DB_REJECTED / CORRUPT_READING

> "chromatic number of the complement of G = n - the matching number."

The literal standard reading appears false on the carrier (`C5[K4]`: `chi(bar G)=3`, `n-nu(G)=10`) but is rejected by the mandatory database gate: it fails on 665 of the 996 connected atlas graphs through order 7 (the count includes `K1`; the usual nontrivial count is 995). In particular `K3` gives `chi(bar K3)=1 != 3-nu(K3)=2`, and named calibration `K7` also fails. An independent direct coloring/matching enumeration on `K3` gives the same result. Thus the printed broad equality cannot be the faithful tested conjecture and is not a campaign kill.

### wow-597 — SKIP_OCR

> "radius < maximal frequency of Even."

`Even` is an undefined coordinate sequence in the surviving text; its maximal frequency cannot be computed without guessing the missing definition.

### wow-598 — SKIP_OCR

> "range of coordinates of matching < quoragedistance."

The right-hand token `quoragedistance` is OCR garble and no unique standard invariant follows from it.

### wow-600 — SKIP_OCR

> "mean of rainbow < inverse Odd."

Both `rainbow` and `Odd` refer to lost coordinate-sequence definitions. No faithful numerical reading survives.

### wow-602 — SKIP_OCR

> "n / independence < range of coordinates of Maxine."

Although the left side is clear, `coordinates of Maxine` depends on an unspecified run/tie-breaking and normalization absent from this record. No guessed algorithm is used.

### wow-603 — SKIP_OCR

> "mean of dual degree < mean of Even."

The OCR corpus does not preserve definitions of either derived coordinate sequence sufficiently to evaluate the comparison.

### wow-604 — SKIP_OCR

> "mean of Even < chromatic number + chromatic number of the complement."

The chromatic side is clear but `Even` is undefined here; no distance-parity invariant is substituted for this named coordinate sequence.

### wow-605 — SKIP_OCR

> "maximum of Odd < chromatic number + chromatic number of the complement of G."

`Odd` lacks a recoverable definition in the record, so the left side cannot be certified.

### wow-607 — SKIP_OCR

> "mean Rainbow < md Tene."

The right side is irrecoverable OCR garble and `Rainbow` is likewise undefined. The following prose only introduces the hypotheses for conjectures 634--654.

### wow-634 — SKIP_OCR

> "inverse of coordinates of Maxine < n /2."

The phrase does not specify whether `inverse` means reciprocal sum, reversed vector, or another defined try-out, and Maxine coordinates depend on missing conventions.

### wow-635 — N/A_ARSENAL

> "size/independence < chromatic number of G + chromatic number of the complement of G."

The surrounding text explicitly restricts conjectures 634--654 to graphs satisfying `chi(bar G)=n-nu(G)`. None of the non-triangle-free blow-ups or triangular graphs is certified in that class; the triangle-free complement of `C5[K4]` also fails it (`chi(C5[K4])=4`, while `20-nu=10`). No admissible arsenal instance.

### wow-638 — SKIP_OCR

> "maximum of Rainbow < n /2."

The `Rainbow` coordinate sequence is undefined in the extracted source, preventing faithful evaluation.

### wow-639 — SKIP_OCR

> "mean Rainbow < Randic."

The Randić index is standard, but the left coordinate sequence is not defined in this record. A one-sided computation cannot establish the verdict.

### wow-640 — N/A_ARSENAL

> "chromatic number < maximal frequency of coordinates of maximum clique."

This lies under the explicit 634--654 hypothesis `chi(bar G)=n-nu(G)`, which no campaign member is established to satisfy. Additionally clique-vector coordinates are not defined here.

### wow-641 — N/A_ARSENAL

> "chromatic number < frequency of maximum of Rainbow."

The section's 634--654 hypothesis fails throughout the usable arsenal, and `Rainbow` is not recoverably defined.

### wow-642 — N/A_ARSENAL

> "scope of Dual Degree < independence."

The section restriction `chi(bar G)=n-nu(G)` excludes the arsenal instances checked; moreover the Dual Degree sequence is unavailable.

### wow-643 — N/A_ARSENAL

> "scope of Dual Degree < number of components of mid-degree."

No arsenal member is certified under the section hypothesis, and both derived sequences lack faithful definitions.

### wow-644 — SKIP_OCR

> "minimum of Dual Degree mean of Odd."

The comparison sign is missing and neither named coordinate sequence is defined. No inequality can be reconstructed.

### wow-645 — N/A_ARSENAL

> "mean of Dual Degree < chromatic number + chromatic number of complement of G."

The inherited 634--654 hypothesis is not met by the arsenal; the Dual Degree mean is also unavailable.

### wow-646 — N/A_ARSENAL

> "Randic < maximal frequency of coordinates of a maximum clique."

The section hypothesis is not met by any established arsenal instance, and the maximum-clique coordinate convention is missing.

### wow-647 — NON_UNIVERSAL / N/A

> "there are graphs with chromatic number of complement of G / independence > residue of the complement."

This is an existential assertion, not a universal wall that an arsenal graph can disprove. Failure of the displayed inequality on campaign members would not refute existence; no counterexample verdict is meaningful.

### wow-650 — HOLD

> "maximum eigenvalue < chromatic number of G + chromatic number of the complement of G."

Under non-strict bound convention, every arsenal graph holds. Closest is `T(8)`: `lambda1=12` and `chi(T(8))+chi(bar(T(8)))=7+6=13`, slack 1. For `C5[K_m]`, exact values are `lambda1=3m-1`, `chi=3m`, and `chi(complement)=3`, slack 4. Structured colorings and dense eigensolutions agree; gaps exceed `1e-6`.

### wow-651 — HOLD

> "average distance < maximal frequency of Degree."

Reading Degree as the degree-sequence mode frequency, every regular arsenal graph has right side `n`, whereas its exact average pair distance is below its diameter (at most 4 here). All hold with large slack.

### wow-652 — SKIP_OCR

> "average distance < inverse dual degree ... (co 653. average distance frequency of mode of 1-Residue."

At least two conjectures are merged, `inverse dual degree` has no surviving definition, and embedded 653 has no comparison sign. No reading is selected.

### wow-654 — N/A_ARSENAL

> "minimum of Even < chromatic number of G + chromatic number of the complement of G."

This remains in the explicitly restricted 634--654 block, whose equality hypothesis is not met by the tested arsenal. `Even` is also undefined in the OCR extract.

### wow-656 — SKIP_OCR

> "——“+ < sum of coordinates of a maximum clique. independence . Size"

The left expression is destroyed and the remaining words do not determine an operand or grouping. No repair is attempted.

### wow-657 — SKIP_OCR

> "mean Rainbow < independence."

`Rainbow` is not defined in the surviving source record, so its mean cannot be evaluated.

### wow-662 — SKIP_OCR

> "deviation of eigenvalues < n - independence. mo and m, denote respectively the multiplicity of 0 and 1 as the eigenvalues over the 2-element field."

The statement does not identify the spectrum or normalization for `deviation`; the GF(2) prose creates a materially different reading. None is guessed.

### wow-693 — SKIP_OCR

> "independence <n — my."

The token `my` is an unrecovered symbol/subscript. Without its definition the right side is indeterminate.

### wow-694 — SKIP_OCR

> "there is an eigenvector E belonging to the smallest eigenvalue such that the frequency of maximum of E < independence."

Repeated minimum eigenspaces, normalization, and quantification over choices are unresolved; the bipartite-equality comment also conflicts with literal strict inequality. No faithful reading is selected.

### wow-695 — SKIP_OCR

> "range of nonpositive eigenvalues <1+n— mo."

`mo` may mean ordinary or GF(2) nullity, and `range` is ambiguous. These readings differ, so none is guessed.

### wow-696 — HOLD

> "- (mean of nonpositive eigenvalues) < chromatic number of complement of G."

For every arsenal member, the negated arithmetic mean of adjacency eigenvalues `<=0` (zeros included) is below `chi(bar G)` by more than `1e-6`. Dense eigendecomposition and closed forms for `C5[K_m]` agree.

### wow-697 — SKIP_OCR

> "range of the largest eigenvector <n — my."

The unknown `my` symbol and unspecified Perron-vector normalization prevent a determinate comparison.

### wow-698 — HOLD

> "lenght of negative eigenvalues < the Randic Index."

Reading length as Euclidean norm of the negative adjacency eigenvalue vector, all regular arsenal graphs hold: Randić is exactly `n/2`, while the negative spectral norm is smaller. Closed-form and dense spectra agree beyond `1e-6`.

### wow-699 — HOLD

> "average distance < sum of reciprocals of square roots of degrees."

For each regular arsenal graph the right side is `n/sqrt(d)`; exact average pair distance is smaller. Independent all-pairs totals and distance histograms agree.

### wow-700 — HOLD

> "deviation of distance < residue."

Taking standard deviation of unordered-pair distances, exact histograms give values below Havel-Hakimi residue for every arsenal graph, beyond `1e-6`. Ordered pairs excluding the diagonal give the same verdict.

### wow-701 — SKIP_OCR

> "The average distance < the inverse rainbow."

`inverse rainbow` has no recoverable definition or normalization. No surrogate is used.

### wow-702 — SKIP_OCR

> "The mean temperature < the mean rainbow."

Temperature is defined, but `rainbow` is not, so the inequality cannot be evaluated faithfully.

### wow-704 — SKIP_OCR

> "The range range of rainbow n — m4"

The sign and grouping are absent, with duplicated `range` and unrecovered `m4`. This is unusable OCR.

### wow-707 — SKIP_OCR

> "The radius < number of positive components of the smallest eigenvector."

Arsenal graphs have repeated smallest eigenvalues, so sign support varies by chosen vector. The source gives no quantifier/normalization making it invariant.

### wow-708 — SKIP_OCR

> "let V be the vector of positive components of the smallest eigenvector ... average distance < [its squared norm]."

The smallest eigenspace is multidimensional and scaling/orientation changes the right side. No invariant reading survives.

### wow-709 — HOLD

> "the maximum of the largest eigenvector < the residue."

With source normalization `sum |x_i|=n`, connected regular arsenal graphs have Perron vector all ones, maximum 1. Residues are at least 2, so all hold. Symmetry and normalized numerical eigenvectors agree.

### wow-710 — SKIP_OCR

> "mo < n— the residue."

`mo` is not pinned to ordinary versus GF(2) nullity. No value is guessed.

### wow-712 — HOLD

> "The minimum temperature < number of nonpositive eigenvalues."

For regular arsenal graphs temperature is exact `d/(n-d)`; guarded inertia counts are safely larger for every member.

### wow-714 — HOLD

> "- mean of nonpositive eigenvalues < sum of reciprocals of all temperatures."

For regular graphs the right side is exact `n(n-d)/d`; direct spectral means are much smaller throughout. Closed-form and dense spectra agree.

### wow-716 — HOLD

> "the diameter - radius < the matching number."

All arsenal members have `diameter=radius`, left side 0, and a positive matching. Exact BFS eccentricities and Edmonds matching agree.

### wow-717 — SKIP_OCR

> "The mean degree < mean dual degree."

`dual degree` is a nonstandard derived sequence whose definition is absent. It is not replaced by complement degree.

### wow-718 — SKIP_OCR

> "mean of dual degree - mean degree < scope of degree."

The degree range is clear, but the dual-degree mean is not defined. Since regularity makes the right side zero, guessing could manufacture a false candidate; none is made.

### wow-719 — SKIP_OCR

> "mean of dual degree - mean degree < scope of dual degree."

Both uses of Dual Degree depend on a missing definition. No verdict from a guessed sequence is trustworthy.

### wow-726 — N/A_ARSENAL

> "every simple polygon contains three mutually visible vertices."

This is a computational-geometry assertion, not a graph-universal statement. None of the arsenal objects is a polygon instance.

### wow-727 — N/A_ARSENAL

> "The distance matrix of p distinct points on the plane, p > 1, has exactly one positive eigenvalue."

The matrix is Euclidean distances among planar points, not a graph distance matrix. The graph arsenal does not instantiate it.

### wow-730 — N/A_ARSENAL

> "If P is a polygon without multiple points then its minimum angle is not more than than the mean degree of its visibility graph."

No campaign object is a polygon with a specified embedding, so the geometric hypothesis cannot be met.

### wow-731 — N/A_ARSENAL

> "Minimum angle of a polygon without multiple vertices is not more than the minimum degree of the complement of its colinearity graph."

The arsenal contains abstract graphs without polygonal point configurations. No admissible instance.

### wow-733 — N/A_ARSENAL

> "The number of distinct degrees of the interval graph of a polygon is not more than the number of vertices of the convex hull of the polygon."

This requires a polygon and its derived interval graph, neither supplied by the campaign arsenal.

### wow-734 — N/A_ARSENAL

> "The sum of reciprocals of nonzero degrees of the colinearity graph of a polygon is not more than the chromatic number of its visibility graph."

The geometric construction is absent from every arsenal member.

### wow-735 — N/A_ARSENAL

> "The sum of reciprocals of nonzero degrees of colinearity graph is not more than the number of distinct eigenvalues of its distance matriz."

This is restricted to a colinearity graph derived from a planar configuration. The abstract carrier graphs are not instances.

### wow-736 — N/A_ARSENAL

> "For every polygon the minimum degree of its visibility graph is not more than the chromatic number of its visibility graph."

No polygon/visibility representation is part of the arsenal; the graph inequality `delta<=chi` alone is not the stated claim.

### wow-737 — N/A_ARSENAL

> "The three triangles obtained by joining the center to vertices of a triangle have the same area."

This is elementary Euclidean geometry and has no graph-arsenal instance.

### wow-738 — N/A_ARSENAL

> "Let a and s be lengths of angle and side bisectors drawn from the same vertex of a triangle. Then a < s."

The statement concerns Euclidean triangle lengths, outside the graph arsenal.

### wow-741 — N/A_ARSENAL

> "The distance from Erdos-Mordell point to the smallest vertex is not more than the sum of distances from the orthocenter of a triangle to its sides."

No geometric triangle is represented by an arsenal graph.

### wow-742 — N/A_ARSENAL

> "The distance from center of the triangle to the smallest vertex is not more than the maximum distance from Erdos-Mordell point to vertices."

This needs a Euclidean triangle and named centers; the arsenal is inapplicable.

### wow-743 — N/A_ARSENAL

> "The distance from center of the triangle to the largest vertex is not more than the distance from Erdos-Mordell point to the largest vertex."

This is not an assertion over abstract connected graphs, so the carrier cannot test it.

### wow-744a — N/A_ARSENAL

> "For every two points p and q inside of a triangle, the distance from p to sides is not more than the distance from q to vertices."

The quantified objects are Euclidean points in a triangle. No arsenal member supplies them.

### wow-749 — HOLD

> "the average distance of G is not more than the market value of G."

Direct max-min evaluation of the stated two-player game gives market values `6,9,12,15,18,24` on `C5[K_m]` (`m=2,3,4,5,6,8`), `12,15` on `C7[K3],C9[K3]`, `14,19,25` on `T(7..9)`, and 12 on `bar(C5[K4])`. Exact average distances range only 1.41--2.38, so all hold.

### wow-752 — HOLD

> "residue of G is not less than p*n ... p*n = max deg/av. deg."

Every arsenal graph is regular, hence the stationary maximum gives `p*n=Delta/d_avg=1`. Exact Havel-Hakimi residues are at least 2, so the original and graph-theoretic readings both hold.

### wow-753 — HOLD

> "Let h be min h(v) ... chromatic number of G is at most h+2."

Direct BFS-layer edge counts give minimum horizontal-edge values `12,34,67,111,166,309,40,46,55,96,154,16` in arsenal order. Exact/structured chromatic numbers are safely at most `h+2`; no candidate.

### wow-754 — SKIP_OCR

> "The chip-firing game ... if the game terminates th"

The record truncates before any conjectural assertion. Definitions alone cannot be tested, and no continuation is guessed.

### wow-755 — HOLD

> "a-m+h is not more than n."

Every arsenal member is Hamiltonian, so longest-path length in edges is `h=n-1`; exact independence and maximum matching give `alpha-nu+h<=n` throughout. The alternative vertex-count convention adds one but the displayed commentary explicitly uses edge-length; under a vertex-count reading the gate would reject familiar Hamiltonian graphs, so it is discarded.

### wow-756 — HOLD

> "The length of the longest path is > than the global minimum degree."

Reading the prose's non-strict intent, Hamiltonicity gives path length `n-1`, at least the degeneracy/global minimum degree for every arsenal graph. Exact core numbers and Hamilton cycles independently certify this.

### wow-757 — HOLD

> "Let C be the set of non cut vertices ... independence ... greater or equal than [number of components of C]."

All arsenal members are 2-connected, so `C=V` induces one component. Since `alpha>=2`, all hold.

### wow-759 — HOLD

> "smallest expanding coefficient is not more than 1 + the number of red edges."

Under the standard vertex-expansion reading, taking the full allowed vertex set yields coefficient at most 1 (and common proper-subset readings are also nonnegative minima), while the right side is at least 1. Every coloring reading holds; no apparent violation.

### wow-760 — HOLD

> "smallest expanding coefficient ... not more than min d(v) ... over all blue vertices."

For a maximum-cut minimizing monochromatic edges, each blue vertex has at least one red neighbor unless its recoloring would improve the cut. Thus the right side is at least 1, while the same expansion minimum is at most 1. Degenerate empty-color-class readings are excluded by the stated two-color optimization.

### wow-761 — SKIP_OCR

> "The smallest expanding coefficient ... not more than 1 + spectral measure of a lar"

The record truncates mid-noun and loses the set whose spectral measure forms the bound. No completion is guessed.

### wow-762 — HOLD

> "independence of G is not less than the maximum of [reciprocal degree] r(v)."

For a `d`-regular graph, each `r(v)=sum_{u in N(v)}1/d(u)=1`. All arsenal members have `alpha>=2`, so the bound holds exactly computed.

### wow-763 — HOLD

> "The mean reciprocal degree = 1."

For any graph without isolates, averaging `r(v)=sum_{u in N(v)}1/d(u)` gives `(1/n)sum_u d(u)/d(u)=1`. All connected arsenal members satisfy it.

### wow-765 — HOLD

> "the length of the longest path is greater or equal to the average degree."

Hamiltonicity gives path edge-length `n-1`; every simple arsenal graph has average degree at most `n-1`. Direct degrees verify the bound.

### wow-765(2) — SKIP_OCR

> "Nov. 98. [B] Bela Bollobas, Extremal Graph Theory,"

This suffix record is only a bibliographic fragment and contains no mathematical assertion.

### wow-766 — N/A_ARSENAL

> "If G is a cubic graph then ..."

No arsenal member is 3-regular, so neither the odd nor mentioned even version has an admissible instance.

### wow-767 — N/A_ARSENAL

> "If G is cubic then ..."

Every arsenal member has degree other than 3. The cubic hypothesis fails.

### wow-768 — N/A_ARSENAL

> "If G is cubic then ..."

No campaign graph is cubic.

### wow-769 — N/A_ARSENAL

> "If G is a cubic graph ..."

The cubic hypothesis fails throughout the arsenal; the record also says an 18-vertex counterexample was already known.

### wow-770 — N/A_ARSENAL

> "If G is cubic ..."

No degree-3 arsenal member exists.

### wow-772 — N/A_ARSENAL

> "If G is a cubic graph ..."

The graph class excludes the arsenal, and the commentary already reports a 20-vertex counterexample.

### wow-773 — N/A_ARSENAL

> "The radius of a cubic connected graph ..."

No arsenal member is cubic.

### wow-775 — N/A_ARSENAL

> "If G is cubic then diameter ..."

No arsenal member meets the degree-3 hypothesis; chip-firing initialization is also unspecified.

### wow-779 — HOLD

> "counter-independence number of G is greater or equal to half of the radius."

Exact counter-independence values are at least 2 and every arsenal radius is at most 4, so all hold (including equality cases). Independent clique computations on the corresponding relation graphs agree.

### wow-780 — HOLD

> "The jet number of any connected graph is greater or equal to half of the radius."

Exact jet values are `2,2,2,2,2,2,3,4,3,3,4,2` in arsenal order and dominate `radius/2`. The source explicitly corrects an earlier reversed listing.

### wow-781 — HOLD

> "jet number of G is not more than 1 + g/2"

With `g` the global minimum degree/degeneracy of the complement as stated, exact jet and core-number computations satisfy the bound for every arsenal graph. No violation.

### wow-782 — HOLD

> "jet number is not more than (n-s(k)+k)/2."

Enumerating each `k<jet(G)` and the minimum span size `s(k)` verifies all readings across the arsenal. Closest brackets are `T(7),k=2: 3<=7/2` and `T(9),k=3:4<=9/2`; no ILP was used.

### wow-784 — SKIP_OCR

> "I decided to try to obtain conjectures related to the twin prime conjecture ... q(3) is 8"

This is truncated number-theory setup; no complete conjectural assertion survives.

### wow-786 — N/A_ARSENAL

> "If G is a critical Ramsey graph r(3,a) ..."

No arsenal member is supplied as a critical Ramsey graph of the required order/class.

### wow-787 — N/A_ARSENAL

> "If G is a complement of a r(3,n) graph ..."

No arsenal member is established as the complement of a critical Ramsey graph. Triangle-freeness alone is insufficient.

### wow-788 — SKIP_OCR

> "do > az."

The coordinate definitions and even the OCR subscripts are lost; the following commentary cannot restore the assertion.

### wow-789 — N/A_ARSENAL

> "market value of critical Ramsey triangle-free graphs ..."

The assertion is restricted to critical Ramsey graphs, a class not instantiated by the arsenal.

### wow-791 — N/A_ARSENAL

> "A span of a vertex of critical Ramsey graph ..."

No campaign graph is certified critical Ramsey.

### wow-793 — HOLD

> "largest independent set ... not more than 1 + global minimum degree of the complement of G."

Exact independence and complement degeneracy/core numbers satisfy `alpha<=1+gmin(bar G)` for every arsenal member. This also follows from the chromatic-number explanation in the source.

### wow-794 — HOLD

> "lower quotient of the degree sequence ... not more than its independence number."

Applying the stated iterative deletion to each regular degree sequence gives a lower quotient at most exact alpha throughout. Direct simulation and its closed form for constant sequences agree.

### wow-795 — HOLD

> "lower quotient ... not less than the Turan bound."

With the source's integral quotient convention and Caro-Wei/Turán bound, direct constant-degree simulations satisfy the bound for all regular arsenal members. Rounding the nonintegral bound upward yields the same integral comparison.

### wow-796 — HOLD

> "upper quotient ... not more than the Turan bound."

The stated dual deletion on constant regular degree sequences was simulated exactly; all arsenal graphs hold under the source's rounded/integral Turán convention.

### wow-797 — HOLD

> "Turan bound = 1 + the average temperature of the complement of G."

For a `d`-regular order-`n` graph, complement temperature is `(n-1-d)/(d+1)`, so the right side is exactly `n/(d+1)`, the Caro-Wei/Turán bound. All arsenal graphs are regular.

### wow-798 — N/A_ARSENAL

> "Let p=4k+4+1 be a prime ... [quadratic-residue word sequence]"

This is a number-theoretic sequence assertion, not a universal graph bound. The commentary also records Odlyzko's proof.

### wow-799 — HOLD

> "independence number ... greater or equal to the number of elements of a maximum principal filter of [the] quasi-ordering."

For the regular vertex-transitive arsenal, equal-size open neighborhoods cannot properly contain one another; after quotienting twins, the poset is an antichain and a maximum principal filter has size 1. Thus `alpha>=1` throughout.

### wow-801 — N/A_ARSENAL

> "Every performance of Maxine and MIN produces a maximum independent set in G."

Primary context restricts this to graphs satisfying the special neighborhood-intersection/PR-domain construction described in the same record. No arsenal member is established in that domain; the universal isolated reading is not faithful.

### wow-802 — N/A_ARSENAL (universal alternate DB_REJECTED)

> "independence ... not more than the Turan bound + largest eigenvalue - second largest eigenvalue."

Context says "for these graphs" and discusses `PR[2..n]`, which the arsenal does not instantiate. The isolated universal reading apparently fails on `bar(C5[K4])`: `8 > 20/9+8-(2sqrt(5)-2) ~=7.750086`; however it also fails 118/995 connected nontrivial atlas graphs and named `P7,C8,C9` and large stars. The mandatory gate discards that alternate, so this is not a kill.

### wow-803 — N/A_ARSENAL (universal alternate DB_REJECTED)

> "independence ... not more than residue of complement + minimum phi function."

The construction is a PR[S] try-out depending on a chosen maximum independent set, not a general invariant. Universal reading fails on `bar(C5[K4])` by `8>2+0`, but also on `K1,3` and 182/995 atlas graphs under every-MIS semantics (310 under any-MIS). Gate rejected; no kill.

### wow-804 — N/A_ARSENAL / DB_REJECTED

> "independence ... greater or equal to upper quotient ... + number of eigenvalues greater or equal to 1."

This remains in the PR/RP context and no arsenal member instantiates it. A universal reading fails 490/995 connected nontrivial atlas graphs, including small calibration graphs, so it cannot support a carrier claim.

### wow-805 — HOLD

> "largest eigenvalue ... not more than 1 + sum temperatures."

Exact regular values give `lambda1=d <= 1+n*d/(n-d)` for every arsenal member. Dense spectra independently confirm `lambda1` beyond the guard.

### wow-806 — SKIP_OCR / DB_REJECTED

> "largest eigenvalue ... not more than number of vertices of different degrees. 807 the second largest eigenvalue ..."

The record visibly fuses 806 and 807 and likely loses an operator. Literal 806 fails `K3` and 480/995 atlas graphs, so the mandatory gate rejects it; no repair is guessed.

### wow-808 — HOLD

> "largest eigenvalue ... greater or equal to mean dual degree."

On every regular arsenal member both sides equal the common degree under the source's dual-degree construction. Direct spectrum and degree-sequence computation agree.

### wow-809 — N/A_ARSENAL / DB_REJECTED

> "number of positive eigenvalues ... not more than -1 + residue."

In the surrounding PR/RP block the arsenal is inapplicable. Literal universal reading fails 767/995 connected nontrivial atlas graphs (including tiny calibration graphs), so apparent carrier failures are discarded.

### wow-810 — N/A_ARSENAL / DB_REJECTED

> "second largest eigenvalue ... product of global minimum degree and counterindependence number."

The contextual/derived-invariant reading is not instantiated by the arsenal. Literal universal form fails 984/995 atlas graphs, proving transcription/context loss rather than a new kill.

### wow-811 — N/A_ARSENAL / DB_REJECTED

> "second largest eigenvalue ... product of frequency of maximum degree and jet number."

Literal universal reading fails 829/995 nontrivial connected atlas graphs and small calibrators; the contextual PR/RP statement cannot be tested on the arsenal.

### wow-812 — N/A_ARSENAL / DB_REJECTED

> "largest eigenvalue - second largest ... not more [than] deviation of degree sequence + k/l"

The PR/RP context and OCR-damaged `l` make the arsenal inapplicable. Literal reading fails 528/995 atlas graphs, so the gate rejects every apparent carrier violation.

### wow-813 — N/A_ARSENAL / DB_REJECTED

> "largest eigenvalue - second largest ... not more [than] deviation ... + mean temperature."

A universal literal reading fails 710/995 atlas graphs, including small database members. Context does not establish an arsenal instance, hence no kill.

### wow-814 — N/A_ARSENAL

> "Invariant Interpolation problems ... [for] RP[n]"

This is a problem asking for a new invariant tailored to `RP[n]`, not a fixed universal inequality for testing.

### wow-815 — N/A_ARSENAL

> "Let G(1) be the 3-vertex clique ... Solve the lower interpolation problem for G(k)."

No arsenal member is one of the recursively amalgamated-triangle graphs, and no candidate inequality is supplied.

### wow-816 — N/A_ARSENAL

> "Solve the lower interpolation problem for generalized Petersen graphs ..."

This is an open-ended invariant-design problem, not an assertion falsifiable by the arsenal.

### wow-817 — N/A_ARSENAL

> "Solve ... interpolation problem for Cayley graphs over cyclic groups ..."

No concrete inequality is stated and no arsenal construction is certified.

### wow-818 — N/A_ARSENAL

> "Solve ... interpolation problem for Paley graphs."

This asks for an invariant rather than stating a bound; the WoW-I arsenal also contains no Paley instance.

### wow-819 — N/A_ARSENAL

> "Let G_n be the cycle ... J the join ... Solve the upper interpolation problem for J_n."

No arsenal member is the specified join construction and no fixed conjectural inequality exists to test.

### wow-820 — N/A_ARSENAL

> "Solve the upper interpolation problem for complements of generalized Petersen graphs ..."

This is an open-ended construction problem, not a carrier wall.

### wow-821 — N/A_ARSENAL

> "Solve the upper interpolation problem for complements of buckyballs ..."

The campaign arsenal contains no such planar cubic construction; no inequality is stated.

### wow-825 — N/A_ARSENAL (missing P)

> "chromatic number ... non-positive eigenvalues of the complement of the blue graph."

The red/blue graphs depend on a Ramseyan property `P` introduced at 822, but this extracted record does not specify `P`. The arsenal cannot instantiate the derived graph without guessing.

### wow-827 — HOLD

> "Chromatic number of G is not more than its average dual degree plus the number of positive eigenvalues."

On regular arsenal graphs, mean dual degree equals the common degree; exact chromatic numbers are at most `d+n_+(A)`. Guarded inertia and structured coloring independently agree.

### wow-829 — N/A_ARSENAL (missing P)

> "maximal frequency of c defined in 822 ... components of B(G)."

The property `P`, coloring coordinate `c`, and hence blue graph `B_P(G)` are absent. No derived object can be formed faithfully.

### wow-830 — N/A_ARSENAL (missing P)

> "residue of the blue graph ... Laplacian of G."

Without the Ramseyan class/property `P`, the blue graph is undefined for an arsenal member.

### wow-831 — N/A_ARSENAL (missing P)

> "residue of the blue graph ... degree of R(G) ..."

Both red and blue graphs require missing parameter `P`; no evaluation is possible.

### wow-832 — N/A_ARSENAL (missing P)

> "average distance ... minimum degree of B(G) ..."

The blue graph depends on unspecified `P`, so its minimum degree is not an arsenal invariant.

### wow-833 — N/A_ARSENAL (missing P)

> "residue of B(G) ... residue of complement of G."

The left graph cannot be constructed without the missing Ramseyan property parameter.

### wow-835 — N/A_ARSENAL (missing P)

> "red clique number ... complement of the blue graph."

Red/blue graphs are undefined without `P`; moreover the record explicitly reports known counterexamples. It is not a carrier claim.

### wow-836 — N/A_ARSENAL (missing P)

> "red clique number ... blue jet number ... residue of blue graph."

Every nonstandard graph in the formula depends on missing `P`, so no faithful arsenal instance exists.

### wow-837 — N/A_ARSENAL (missing P)

> "red clique number ... maximum red degree ..."

The derived red graph is unspecified because `P` is missing. The source additionally says this conjecture is correct.

### wow-838 — N/A_ARSENAL (missing P)

> "red clique number < blue residue + maximum deficiency."

The red/blue construction is parameterized by an absent property `P`. No guessing is permitted.

### wow-839 — N/A_ARSENAL (missing P)

> "red clique number < number of blue isolated vertices + maximum of odd vertices."

Both colored graphs and the `odd vertices` coordinate depend on missing surrounding definitions. No arsenal test is defined.

### wow-842 — N/A_ARSENAL

> "If G is a fullerene ..."

Every arsenal graph fails the fullerene hypothesis (a fullerene is planar cubic with pentagonal/hexagonal faces). In particular `bar(C5[K4])` is 8-regular and has 80 edges, exceeding the planar bound `3n-6=54`.

### wow-844 — N/A_ARSENAL

> "The independence number in fullerenes ..."

No arsenal member is a fullerene.

### wow-846 — N/A_ARSENAL

> "The sum of positive eigenvalues [of a fullerene] ..."

This is explicitly in the fullerene block and names a fullerene; the arsenal has none.

### wow-847 — N/A_ARSENAL

> "If G is [a fullerene] ..."

The record's market-game bound is restricted to fullerenes. No admissible campaign graph.

### wow-848 — N/A_ARSENAL

> "number of negative eigenvalues of a fullerene ..."

No arsenal member satisfies the cubic planar fullerene hypothesis.

### wow-849 — N/A_ARSENAL

> "If G is a fullerene ..."

The graph class excludes the arsenal.

### wow-850 — N/A_ARSENAL

> "If G is a cubic graph of girth 5 ..."

No arsenal member is cubic.

### wow-851 — N/A_ARSENAL

> "If G is a fullerene ..."

The fullerene hypothesis fails throughout the arsenal.

### wow-852 — N/A_ARSENAL

> "number of negative eigenvalues of a fullerene ..."

No campaign graph is a fullerene.

### wow-853 — N/A_ARSENAL

> "average distance of a fullerene ..."

No campaign graph is a fullerene.

### wow-854 — N/A_ARSENAL

> "average distance of a fullerene ..."

The explicit fullerene hypothesis is not met.

### wow-855 — N/A_ARSENAL

> "number of positive eigenvalues of a fullerene ..."

No arsenal member is cubic planar/fullerenic.

### wow-856 — N/A_ARSENAL (universal alternate DB_REJECTED)

> "sum of positive eigenvalues ... > 1 + number of eigenvalues greater or equal to -1."

The record sits inside the fullerene block and compares 846, so the arsenal is inapplicable. Isolated universal reading would fail on `bar(C5[K4])`: `4+4sqrt(5)~=12.9443 < 19`; but it also fails 879/995 nontrivial connected atlas graphs, including `K2,K3,C5--C9,P7,K3,3,K7` and stars. The gate decisively rejects that reading.

### wow-857 — N/A_ARSENAL

> "Eigenvectors of 0 of a cubic graph ... Conjecture: m < t."

The operative construction is cubic and the OCR-obscure `largest side of a largest triangle` is not defined. No arsenal member is cubic.

### wow-858 — N/A_ARSENAL

> "number of centers of a fullerene ..."

The fullerene hypothesis fails throughout the arsenal.

### wow-859 — N/A_ARSENAL

> "If G is a fullerene ..."

No arsenal graph is a fullerene.

### wow-860 — N/A_ARSENAL

> "sum of positive eigenvalues of an IP isomer G ..."

No arsenal member is an isolated-pentagon fullerene isomer.

### wow-861 — N/A_ARSENAL

> "sum of positive eigenvalues of an IP isomer ..."

The IP-isomer class excludes the arsenal.

### wow-862 — N/A_ARSENAL

> "independence number of an IP isomer ..."

No arsenal member satisfies the IP-fullerene hypothesis.

### wow-863 — N/A_ARSENAL

> "Let G be a cubic connected graph of girth 5 with 16 vertices."

No arsenal graph is cubic of order 16 and girth 5.

### wow-864 — DB_REJECTED / TERMINOLOGY MISMATCH

> "Let G be triangle-free. Then the red counter-independence number is < the blue clique number."

For `G=bar(C5[K4])`, the natural #822 distance coloring gives red graph `C5[K4]` and empty blue graph, apparently `2<=1`. But the same reading fails 11/89 applicable connected triangle-free nontrivial atlas graphs, including `C4,C5`, and named Petersen and `K3,3`. The printed follow-up about maximal blue cliques is incompatible with this parse on `C5`, confirming a terminology mismatch. Gate rejected; not a kill.

### wow-865 — HOLD / TIGHT

> "If G is triangle-free ... blue clique number > 1/2(red independence number)."

The applicable arsenal member `bar(C5[K4])` has red graph `C5[K4]` with independence 2 and empty blue graph with clique number 1, giving exact non-strict equality `1=2/2`. The source convention uses `>` for at-least bounds; a strict parse fails the `C5` sanity gate and is discarded.


