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

Progress: 85 / 208.

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


