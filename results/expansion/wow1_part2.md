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

Progress: 22 / 208.

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
+### wow-496 — SKIP_OCR

> "sum of coordinates of Maxine < length of S. A97. size - order < the number of triangles."

Two assertions are fused, `S` is undefined, and the first inequality has no recoverable graph object. No interpretation is guessed.
+### wow-503 — SKIP_OCR

> "frequency of minimum of rainbow < a(n)."

Neither `rainbow` nor `a(n)` is defined in this record, and OCR has lost the surrounding construction. There is no determinate numerical assertion to test.

+### wow-504 — N/A_ARSENAL

> "the number of square-free integers not exceeding n and being products of even number of primes [inequality lost] sum of reciprocals of coordinates of Maxine."

The comparison sign is lost and the left side is number-theoretic. None of the arsenal graphs supplies the required integer construction; no repair is guessed.

+### wow-509 — SKIP_OCR

> "mean rainbow < frequency of maximum of eigenvalues of Laplacian."

`Rainbow` is an undocumented coordinate try-out in this extracted record, so its mean cannot be recovered faithfully. The Laplacian side alone is insufficient.

+### wow-513 — N/A_ARSENAL

> "chromatic number of a Paley graph with n vertices is not more than the number of primes not more than n."

The hypothesis is specifically a Paley graph. The WoW-I handoff arsenal contains no Paley graph (Paley additions belong only to the AGX lane), so this lane has no admissible instance.

+### wow-515 — SKIP_OCR

> "pi(n) sum of reciprocals of coordinates of a maximum clique."

The relation symbol between the two quantities is absent. Consequently no inequality or equality survives to evaluate.

+### wow-516 — SKIP_OCR

> "deviation of S < frequency of mode of eigenvalues of Laplacian."

The set/vector `S` is undefined in the surviving record. Testing a guessed spectral sequence would violate the no-guess OCR rule.

+### wow-523 — N/A_ARSENAL

> "mode of eigenvalues of Laplacian < number of square-free integers not greater than n."

The right side is tied to the preceding number-theoretic construction rather than a graph invariant supplied for arbitrary arsenal graphs. No arsenal instance is established.

+### wow-528 — N/A_ARSENAL

> "the number of square-free integers not exceeding n and being products of odd number of primes < 2(chromatic number)."

This belongs to the number-theoretic graph sequence in the surrounding section. The carrier arsenal is not that sequence, so it provides no admissible test.

+### wow-529 — SKIP_OCR

> "deviation of S < number of cubic residues less than n."

`S` is missing from the extracted statement and the number-theoretic construction is not recoverable from this record. No guessed vector is evaluated.

+### wow-536 — N/A_ARSENAL

> "The number of cubic nonresidues < n / average distance of Paley graph with n vertices."

This is explicitly restricted to Paley graphs. None occurs in this WoW-I arsenal, hence no campaign graph can witness or refute it.

+### wow-537 — N/A_ARSENAL

> "If G is a connected Cayley graph of cyclic groups with at least two vertices then chromatic number < rank."

No arsenal graph is supplied with a cyclic Cayley representation satisfying the stated hypothesis. The lane therefore has no admissible instance.

+### wow-538 — N/A_ARSENAL

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
+### wow-547 — SKIP_OCR

> "independence < n — modeofmid — Degree."

The OCR leaves two subtraction marks around a fused `modeofmid-Degree` token; the intended grouping and invariant are not reliably recoverable.

+### wow-548 — SKIP_OCR

> "mode of mid-Degree < size independence."

The corpus does not preserve the mid-Degree sequence definition with enough precision to reproduce its mode for this sweep. No substitute invariant is guessed.

+### wow-552 — SKIP_OCR

> "independence < n- mean of mid-Degree."

The `mid-Degree` derived sequence is not recoverable faithfully from this isolated OCR record, so its mean cannot be certified.

+### wow-553 — SKIP_OCR

> "mean of mid-Degree < size independence."

As in wow-552, the operative derived-sequence definition is unavailable in a sufficiently reliable form. No guessed Havel-Hakimi variant is used.


