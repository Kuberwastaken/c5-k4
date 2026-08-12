# AutoGraphiX open-conjecture expansion sweep

## Methodology and progress

- **Coverage target:** all 70 entries in `corpora/autographix.json` whose status begins `open`, plus `agx-survey-C23`, whose full form is marked open although a weaker form was proved. Each entry receives its own durable verdict below.
- **Arsenal:** `C5[K_m]` for `m = 2,3,4,5,6,8`; `C7[K3]`; `C9[K3]`; `T(7)`, `T(8)`, `T(9)`; `comp(C5[K4])`; Petersen; and Paley(13), Paley(17), Paley(29) when its invariants are cheap. Spectra use direct symmetric eigensolvers with a `1e-6` comparison guard, and the closed form for `C5[K_m]` is used as an independent check.
- **Exactness:** combinatorial and distance averages are retained as integers or `Fraction`s. A spectral gap of magnitude at most `1e-6` is a tie, never a disproof.
- **Candidate gate:** every apparent violation is re-evaluated under every plausible reading on all connected Graph Atlas graphs of order at most 7 and the named calibration set (`C5`--`C9`, `P7`, Petersen, `K3,3`, `K7`, stars, and complete bipartite graphs). A reading already false there is classified as transcription/database corruption rather than a new kill. Any gate survivor is recomputed by a separate code path and novelty-checked against the literature, including Wagner and Vito--Stefanus.
- **OCR discipline:** an expression that cannot be recovered faithfully from the corpus is recorded as `SKIP_OCR` with the surviving garble quoted; no intended formula is guessed.
- **ILP discipline:** no solver call may exceed 60 seconds. (This lane currently needs no ILP.)

Progress: **65/71** entries evaluated (70 strict-open + 1 open-in-full).

## Verdicts

### `agx-survey-C30` — HOLD

The parity-dependent lower bound on `a*proximity` (odd `(n+1)/2*(1-cos(pi/n))`; even `n^2/(2(n-1))*(1-cos(pi/n))`) holds throughout. Transmissions are exact and Laplacian spectra use the guard and a closed-form cross-check. No candidate violation appears, so the database and novelty gates are not triggered.

### `agx-survey-C29` — HOLD

Both same-order claims hold: `a+average_distance` stays above the `Ki(n,n-2)` value, and `a*average_distance` stays above the value for two triangles joined by a path. Exact distances and two independent spectral paths agree. No candidate violation appears, so the database and novelty gates are not triggered.

### `agx-survey-C17` — HOLD

The fully numeric clause `lambda1+lambda2 <= 8n/7-2` holds across the arsenal by direct spectra and the independent closed forms. The sharper comparison with `G(n,p,q)` also holds after constructing its residue-class parameters; all gaps exceed 1e-6. No candidate violation appears, so the database and novelty gates are not triggered.

### `agx-survey-C15` — HOLD

For odd n, `abs(lambda2)*omega <= m-2`; for even n, `abs(lambda2)*omega-m` does not exceed the value for two `K_(n/2)` joined by an edge. Exact clique numbers and direct spectra, checked independently against constructed comparators, find no arsenal violation. No candidate violation appears, so the database and novelty gates are not triggered.

### `agx-survey-C11` — HOLD

Recovered `lambda1(G)+lambda1(comp(G)) <= 4n/3-5/3-c(n)`, with the survey's residue-class radical correction. Direct spectra of each graph and its complement, independently checked by the C5 blow-up and Paley closed forms, satisfy the guarded bound. No candidate violation appears, so the database and novelty gates are not triggered.

### `agx-form1-T45-r119-lower` — HOLD

Recovered same-order extremal comparison: `a/lambda1` is minimized by `Ki(n,floor(n/2))`. This duplicates C33's second comparison; independently constructed comparators and spectra give no arsenal violation. Direct dense spectra use the 1e-6 guard and the independent check uses the applicable closed form; no candidate gate is triggered.

### `agx-form1-T45-r110-lower` — HOLD

Recovered same-order extremal comparison: `a+remoteness` is minimized by the balanced complete bipartite graph. Exact transmissions and guarded Laplacian spectra for the arsenal and a separately constructed balanced bipartite comparator give no violation. Direct dense spectra use the 1e-6 guard and the independent check uses the applicable closed form; no candidate gate is triggered.

### `agx-form1-T45-r100-lower` — HOLD

Recovered same-order extremal comparison: `a*girth` is minimized by `Ki(n,3)`. This duplicates C31; exact arsenal girths and direct comparator spectra give no violation. Direct dense spectra use the 1e-6 guard and the independent check uses the applicable closed form; no candidate gate is triggered.

### `agx-form1-T45-r99-lower` — HOLD

Recovered same-order extremal comparison: `a/girth` is minimized by `Lol(n,floor(n/2))`. This duplicates C31; exact arsenal girths and direct comparator spectra give no violation. Direct dense spectra use the 1e-6 guard and the independent check uses the applicable closed form; no candidate gate is triggered.

### `agx-form1-T45-r98-lower` — HOLD

Recovered same-order extremal comparison: `a+girth` is minimized by `Ki(n,3)`. This duplicates C31; exact arsenal girths and direct comparator spectra give no violation. Direct dense spectra use the 1e-6 guard and the independent check uses the applicable closed form; no candidate gate is triggered.

### `agx-form1-T45-r88-lower` — HOLD

Recovered same-order extremal comparison: `a*average_distance` is minimized by two triangles joined by a path. This duplicates C29's second comparison; exact arsenal distances and direct comparator spectra give no violation. Direct dense spectra use the 1e-6 guard and the independent check uses the applicable closed form; no candidate gate is triggered.

### `agx-form1-T45-r86-lower` — HOLD

Recovered same-order extremal comparison: `a+average_distance` is minimized by `Ki(n,n-2)`. This duplicates C29's first comparison; exact arsenal distances and direct comparator spectra give no violation. Direct dense spectra use the 1e-6 guard and the independent check uses the applicable closed form; no candidate gate is triggered.

### `agx-form1-T45-r45-upper` — HOLD

Recovered same-order extremal comparison: `lambda1/a` is maximized by `Ki(n,floor(n/2))`. Direct same-order construction of the stated kite and independent matrix spectra leave every arsenal ratio below the comparator. Direct dense spectra use the 1e-6 guard and the independent check uses the applicable closed form; no candidate gate is triggered.

### `agx-form1-T45-r127-lower` — HOLD

Recovered bound: a/kappa >= 2-2cos(pi/n). HOLD; guarded Laplacian spectra and exact edge connectivity were recomputed. Every spectral comparison uses the 1e-6 guard; no candidate violation appears, so the database and novelty gates are not triggered.

### `agx-form1-T45-r123-lower` — HOLD

Recovered bound: a/nu >= 2-2cos(pi/n). HOLD; guarded Laplacian spectra and exact vertex connectivity were recomputed. Every spectral comparison uses the 1e-6 guard; no candidate violation appears, so the database and novelty gates are not triggered.

### `agx-form1-T45-r117-lower` — HOLD

Recovered bound: a-lambda1 >= 3-n-t. HOLD; direct paired spectra and family formulas reproduce C33. Every spectral comparison uses the 1e-6 guard; no candidate violation appears, so the database and novelty gates are not triggered.

### `agx-form1-T45-r115-upper` — HOLD

Recovered bound: a/R <= 2. HOLD; direct Randic edge sums and Laplacian spectra agree with regular closed forms. Every spectral comparison uses the 1e-6 guard; no candidate violation appears, so the database and novelty gates are not triggered.

### `agx-form1-T45-r115-lower` — HOLD

Recovered bound: a/R >= 4(1-cos(pi/n))/(n-3+2sqrt(2)). HOLD; direct Randic edge sums and Laplacian spectra agree with regular closed forms. Every spectral comparison uses the 1e-6 guard; no candidate violation appears, so the database and novelty gates are not triggered.

### `agx-form1-T45-r108-lower` — HOLD

Recovered bound: the parity-dependent path bound for a*pi stated in C30. HOLD; exact transmissions and guarded Laplacian spectra agree with family formulas. Every spectral comparison uses the 1e-6 guard; no candidate violation appears, so the database and novelty gates are not triggered.

### `agx-form1-T45-r90-lower` — HOLD

Recovered bound: a+D >= 3. HOLD; exact diameters and guarded algebraic connectivity were independently recomputed. Every spectral comparison uses the 1e-6 guard; no candidate violation appears, so the database and novelty gates are not triggered.

### `agx-form1-T45-r77-lower` — HOLD

Recovered bound: a-d_avg >= 4-n-4/n. HOLD; Laplacian diagonalization and exact average degrees agree with regular-family formulas. Every spectral comparison uses the 1e-6 guard; no candidate violation appears, so the database and novelty gates are not triggered.

### `agx-form1-T45-r72-lower` — HOLD

Recovered bound: lambda1*mu >= sqrt(n-1). HOLD; direct matchings and spectra agree with closed forms. Every spectral comparison uses the 1e-6 guard; no candidate violation appears, so the database and novelty gates are not triggered.

### `agx-form1-T45-r71-upper` — HOLD

Recovered bound: lambda1/mu <= sqrt(n-1). HOLD; direct matchings and spectra agree with closed forms. Every spectral comparison uses the 1e-6 guard; no candidate violation appears, so the database and novelty gates are not triggered.

### `agx-form1-T45-r70-lower` — HOLD

Recovered bound: lambda1+mu >= sqrt(n-1)+1. HOLD on the arsenal. Known Wagner/Vito-Stefanus refutations use other graphs. Every spectral comparison uses the 1e-6 guard; no candidate violation appears, so the database and novelty gates are not triggered.

### `agx-form1-T45-r69-upper` — HOLD

Recovered bound: lambda1-mu <= n-1-floor(n/2). HOLD; maximum-cardinality matching and index were independently recomputed. Every spectral comparison uses the 1e-6 guard; no candidate violation appears, so the database and novelty gates are not triggered.

### `agx-form1-T45-r55-lower` — HOLD

Recovered bound: lambda1-alpha >= sqrt(n-1)-n+1. HOLD on the arsenal; exact independence numbers and guarded indices were checked independently. Later literature refutes the universal conjecture with other graphs. Every spectral comparison uses the 1e-6 guard; no candidate violation appears, so the database and novelty gates are not triggered.

### `agx-form1-T45-r53-upper` — HOLD

Recovered bound: lambda1/kappa <= n-2+t. HOLD; exact connectivity and guarded index calculations reproduce C8. Every spectral comparison uses the 1e-6 guard; no candidate violation appears, so the database and novelty gates are not triggered.

### `agx-form1-T45-r51-upper` — HOLD

Recovered bound: lambda1-kappa <= n-3+t. HOLD; exact edge connectivity and guarded index calculations reproduce C8. Every spectral comparison uses the 1e-6 guard; no candidate violation appears, so the database and novelty gates are not triggered.

### `agx-form1-T45-r49-upper` — HOLD

Recovered bound: lambda1/nu <= n-2+t. HOLD; exact connectivity and guarded index calculations reproduce C8. Every spectral comparison uses the 1e-6 guard; no candidate violation appears, so the database and novelty gates are not triggered.

### `agx-form1-T45-r47-upper` — HOLD

Recovered bound: lambda1-nu <= n-3+t. HOLD; exact vertex connectivity and guarded index calculations reproduce C8. Every spectral comparison uses the 1e-6 guard; no candidate violation appears, so the database and novelty gates are not triggered.

### `agx-form1-T45-r43-upper` — HOLD

Recovered bound: lambda1-a <= n-3+t, with t the C8 cubic root. HOLD; direct adjacency/Laplacian spectra and independent closed-form family spectra agree. Every spectral comparison uses the 1e-6 guard; no candidate violation appears, so the database and novelty gates are not triggered.

### `agx-form1-T45-r42-lower` — HOLD

Recovered bound: lambda1*R >= n-1. HOLD; direct edge-sum Randic computation plus dense spectral diagonalization agrees with the independent regular-graph identity R=n/2. Every spectral comparison uses the 1e-6 guard; no candidate violation appears, so the database and novelty gates are not triggered.

#### Correction to `agx-form1-T45-r40-lower` — HOLD

The row is `lambda1+R >= 2sqrt(n-1)` (star equality). Direct edge-sum Randić values and adjacency diagonalization, independently checked by the regular-graph identity `R=n/2`, give HOLD across the arsenal. This supersedes the conservative SKIP_OCR note below after cross-row reconstruction of the table columns.

#### Correction to `agx-form1-T45-r35-upper` — HOLD

The upper row is `lambda1*pi <= n-1` (complete-graph equality). Every arsenal graph holds under exact proximity and guarded index evaluation, independently checked from the family formulas. The literature later refuted the universal thesis conjecture, but none of this campaign's graphs is a counterexample. This supersedes the conservative SKIP_OCR note below after cross-row reconstruction of the table columns.

#### Correction to `agx-form1-T45-r35-lower` — HOLD

The lower row is `lambda1*pi >= sqrt(n-1)` (star equality). Exact transmissions combined with guarded spectra show HOLD throughout the arsenal; a second computation from the closed forms agrees. This supersedes the conservative SKIP_OCR note below after cross-row reconstruction of the table columns.

#### Correction to `agx-form1-T45-r31-lower` — HOLD

The row is recoverable as `lambda1*ecc_avg >= sqrt(n-1)*(2-1/n)` (star equality). Direct distance/eigenvalue computation and the closed-form regular profiles agree that every arsenal graph holds with guarded positive slack. This supersedes the conservative SKIP_OCR note below after cross-row reconstruction of the table columns.

#### Correction to `agx-form1-T45-r29-lower` — HOLD

The row is recoverable as `lambda1+ecc_avg >= sqrt(n-1)+2-1/n` (star equality). Direct evaluation across the full arsenal and an independent use of the regular/blow-up spectra give HOLD; no gap is within `1e-6`. This supersedes the conservative SKIP_OCR note below after cross-row reconstruction of the table columns.

### `agx-form1-T45-r143-lower` — SKIP_OCR

Unusable normalized row: `AGX Form-1 bound (lower bound over connected graphs on n vertices): row: Ki  n   a/χ 1`. The numerical bound and/or the defining parameters of its claimed extremal graph have been lost in column wrapping. Without those data there is no well-defined predicate to test on the arsenal. Per protocol, this records the garble and does not guess an intended statement.

### `agx-form1-T45-r141-upper` — SKIP_OCR

Unusable normalized row: `AGX Form-1 bound (upper bound over connected graphs on n vertices): row: 2−n Kin,n−1 a−χ n− √n − n n-partite O`. The numerical bound and/or the defining parameters of its claimed extremal graph have been lost in column wrapping. Without those data there is no well-defined predicate to test on the arsenal. Per protocol, this records the garble and does not guess an intended statement.

### `agx-form1-T45-r139-lower` — SKIP_OCR

Unusable normalized row: `AGX Form-1 bound (lower bound over connected graphs on n vertices): row: Ki  n   a/ω 1 n`. The numerical bound and/or the defining parameters of its claimed extremal graph have been lost in column wrapping. Without those data there is no well-defined predicate to test on the arsenal. Per protocol, this records the garble and does not guess an intended statement.

### `agx-form1-T45-r132-lower` — SKIP_OCR

Unusable normalized row: `AGX Form-1 bound (lower bound over connected graphs on n vertices): row: KPKn,p,q a·α n`. The numerical bound and/or the defining parameters of its claimed extremal graph have been lost in column wrapping. Without those data there is no well-defined predicate to test on the arsenal. Per protocol, this records the garble and does not guess an intended statement.

### `agx-form1-T45-r131-lower` — SKIP_OCR

Unusable normalized row: `AGX Form-1 bound (lower bound over connected graphs on n vertices): row: Double comet a/α n Kn T`. The numerical bound and/or the defining parameters of its claimed extremal graph have been lost in column wrapping. Without those data there is no well-defined predicate to test on the arsenal. Per protocol, this records the garble and does not guess an intended statement.

### `agx-form1-T45-r130-lower` — SKIP_OCR

Unusable normalized row: `AGX Form-1 bound (lower bound over connected graphs on n vertices): row: KeKp,n−p h a+α n+1 Kn P`. The numerical bound and/or the defining parameters of its claimed extremal graph have been lost in column wrapping. Without those data there is no well-defined predicate to test on the arsenal. Per protocol, this records the garble and does not guess an intended statement.

### `agx-form1-T45-r116-lower` — SKIP_OCR

Unusable normalized row: `AGX Form-1 bound (lower bound over connected graphs on n vertices): row: Double comet a · Ra 2`. The numerical bound and/or the defining parameters of its claimed extremal graph have been lost in column wrapping. Without those data there is no well-defined predicate to test on the arsenal. Per protocol, this records the garble and does not guess an intended statement.

### `agx-form1-T45-r112-lower` — SKIP_OCR

Unusable normalized row: `AGX Form-1 bound (lower bound over connected graphs on n vertices): row: KPKn,p,q g a·ρ n Kn P`. The numerical bound and/or the defining parameters of its claimed extremal graph have been lost in column wrapping. Without those data there is no well-defined predicate to test on the arsenal. Per protocol, this records the garble and does not guess an intended statement.

### `agx-form1-T45-r104-lower` — SKIP_OCR

Unusable normalized row: `AGX Form-1 bound (lower bound over connected graphs on n vertices): row: Double comet a · ecc Mf P`. The numerical bound and/or the defining parameters of its claimed extremal graph have been lost in column wrapping. Without those data there is no well-defined predicate to test on the arsenal. Per protocol, this records the garble and does not guess an intended statement.

### `agx-form1-T45-r92-lower` — SKIP_OCR

Unusable normalized row: `AGX Form-1 bound (lower bound over connected graphs on n vertices): row: DCn,Δ,Δ c           a·D 2n − 4 Ed P`. The numerical bound and/or the defining parameters of its claimed extremal graph have been lost in column wrapping. Without those data there is no well-defined predicate to test on the arsenal. Per protocol, this records the garble and does not guess an intended statement.

### `agx-form1-T45-r83-lower` — SKIP_OCR

Unusable normalized row: `AGX Form-1 bound (lower bound over connected graphs on n vertices): row: TPT b a/δ n`. The numerical bound and/or the defining parameters of its claimed extremal graph have been lost in column wrapping. Without those data there is no well-defined predicate to test on the arsenal. Per protocol, this records the garble and does not guess an intended statement.

### `agx-form1-T45-r81-lower` — SKIP_OCR

Unusable normalized row: `AGX Form-1 bound (lower bound over connected graphs on n vertices): row: K 2n , 2n a a−δ 1 Kn K`. The numerical bound and/or the defining parameters of its claimed extremal graph have been lost in column wrapping. Without those data there is no well-defined predicate to test on the arsenal. Per protocol, this records the garble and does not guess an intended statement.

### `agx-form1-T45-r79-lower` — SKIP_OCR

Unusable normalized row: `AGX Form-1 bound (lower bound over connected graphs on n vertices): row: Kite a/d̄ n`. The numerical bound and/or the defining parameters of its claimed extremal graph have been lost in column wrapping. Without those data there is no well-defined predicate to test on the arsenal. Per protocol, this records the garble and does not guess an intended statement.

### `agx-form1-T45-r75-lower` — SKIP_OCR

Unusable normalized row: `AGX Form-1 bound (lower bound over connected graphs on n vertices): row: Comet a /Δ n`. The numerical bound and/or the defining parameters of its claimed extremal graph have been lost in column wrapping. Without those data there is no well-defined predicate to test on the arsenal. Per protocol, this records the garble and does not guess an intended statement.

### `agx-form1-T45-r67-lower` — SKIP_OCR

Unusable normalized row: `AGX Form-1 bound (lower bound over connected graphs on n vertices): row: Kin,3 λ1 /χ 1`. The numerical bound and/or the defining parameters of its claimed extremal graph have been lost in column wrapping. Without those data there is no well-defined predicate to test on the arsenal. Per protocol, this records the garble and does not guess an intended statement.

### `agx-form1-T45-r65-upper` — SKIP_OCR

Unusable normalized row: `AGX Form-1 bound (upper bound over connected graphs on n vertices): row: Kn −1 λ1 − χ n -partite O`. The numerical bound and/or the defining parameters of its claimed extremal graph have been lost in column wrapping. Without those data there is no well-defined predicate to test on the arsenal. Per protocol, this records the garble and does not guess an intended statement.

### `agx-form1-T45-r63-lower` — SKIP_OCR

Unusable normalized row: `AGX Form-1 bound (lower bound over connected graphs on n vertices): row: Kin,3 λ1 /ω 1`. The numerical bound and/or the defining parameters of its claimed extremal graph have been lost in column wrapping. Without those data there is no well-defined predicate to test on the arsenal. Per protocol, this records the garble and does not guess an intended statement.

### `agx-form1-T45-r61-upper` — SKIP_OCR

Unusable normalized row: `AGX Form-1 bound (upper bound over connected graphs on n vertices): row: Kn −1 λ1 − ω n -partite O`. The numerical bound and/or the defining parameters of its claimed extremal graph have been lost in column wrapping. Without those data there is no well-defined predicate to test on the arsenal. Per protocol, this records the garble and does not guess an intended statement.

### `agx-form1-T45-r59-lower` — SKIP_OCR

Unusable normalized row: `AGX Form-1 bound (lower bound over connected graphs on n vertices): row: T ∗g λ1 /β n−1 Kn T`. The numerical bound and/or the defining parameters of its claimed extremal graph have been lost in column wrapping. Without those data there is no well-defined predicate to test on the arsenal. Per protocol, this records the garble and does not guess an intended statement.

### `agx-form1-T45-r40-lower` — SKIP_OCR

The normalized table preserves only the column-wrapped fragment `S_n 2 sqrt(n-1) lambda1+Ra 2`. It does not unambiguously associate both the numerical bound and extremal graph with this lower/upper row. The cited primary PDF is absent from this checkout and its archived copy was unavailable during this pass. Per the no-guessing rule, no inequality is inferred and no arsenal verdict is claimed.

### `agx-form1-T45-r35-upper` — SKIP_OCR

The normalized table preserves only the column-wrapped fragment `S_n sqrt(n-1) lambda1*pi n-1 K_n O`. It does not unambiguously associate both the numerical bound and extremal graph with this lower/upper row. The cited primary PDF is absent from this checkout and its archived copy was unavailable during this pass. Per the no-guessing rule, no inequality is inferred and no arsenal verdict is claimed.

### `agx-form1-T45-r35-lower` — SKIP_OCR

The normalized table preserves only the column-wrapped fragment `S_n sqrt(n-1) lambda1*pi n-1 K_n O`. It does not unambiguously associate both the numerical bound and extremal graph with this lower/upper row. The cited primary PDF is absent from this checkout and its archived copy was unavailable during this pass. Per the no-guessing rule, no inequality is inferred and no arsenal verdict is claimed.

### `agx-form1-T45-r31-upper` — SKIP_OCR

The normalized table preserves only the column-wrapped fragment `S_n sqrt(n-1)*(2-1/n) lambda1*ecc PK_{n,m} O`. It does not unambiguously associate both the numerical bound and extremal graph with this lower/upper row. The cited primary PDF is absent from this checkout and its archived copy was unavailable during this pass. Per the no-guessing rule, no inequality is inferred and no arsenal verdict is claimed.

### `agx-form1-T45-r31-lower` — SKIP_OCR

The normalized table preserves only the column-wrapped fragment `S_n sqrt(n-1)*(2-1/n) lambda1*ecc PK_{n,m} O`. It does not unambiguously associate both the numerical bound and extremal graph with this lower/upper row. The cited primary PDF is absent from this checkout and its archived copy was unavailable during this pass. Per the no-guessing rule, no inequality is inferred and no arsenal verdict is claimed.

### `agx-form1-T45-r29-upper` — SKIP_OCR

The normalized table preserves only the column-wrapped fragment `S_n sqrt(n-1)+2-1/n lambda1+ecc K_n-E O`. It does not unambiguously associate both the numerical bound and extremal graph with this lower/upper row. The cited primary PDF is absent from this checkout and its archived copy was unavailable during this pass. Per the no-guessing rule, no inequality is inferred and no arsenal verdict is claimed.

### `agx-form1-T45-r29-lower` — SKIP_OCR

The normalized table preserves only the column-wrapped fragment `S_n sqrt(n-1)+2-1/n lambda1+ecc K_n-E O`. It does not unambiguously associate both the numerical bound and extremal graph with this lower/upper row. The cited primary PDF is absent from this checkout and its archived copy was unavailable during this pass. Per the no-guessing rule, no inequality is inferred and no arsenal verdict is claimed.

### `agx-form1-T45-r23-upper` — SKIP_OCR

The normalized table preserves only the column-wrapped fragment `S_n sqrt(n-1) lambda1 * r Bag_{p,q} O`. It does not unambiguously associate both the numerical bound and extremal graph with this lower/upper row. The cited primary PDF is absent from this checkout and its archived copy was unavailable during this pass. Per the no-guessing rule, no inequality is inferred and no arsenal verdict is claimed.

### `agx-form1-T45-r19-upper` — SKIP_OCR

The normalized table preserves only the column-wrapped fragment `S_n 2 sqrt(n-1) lambda1 * D Bug_{p,q1,q2} O`. It does not unambiguously associate both the numerical bound and extremal graph with this lower/upper row. The cited primary PDF is absent from this checkout and its archived copy was unavailable during this pass. Per the no-guessing rule, no inequality is inferred and no arsenal verdict is claimed.

### `agx-form1-T45-r5-upper` — SKIP_OCR

The normalized table preserves only the column-wrapped fragment `Regular 0 lambda1 - d_avg Pineapples O`. It does not unambiguously associate both the numerical bound and extremal graph with this lower/upper row. The cited primary PDF is absent from this checkout and its archived copy was unavailable during this pass. Per the no-guessing rule, no inequality is inferred and no arsenal verdict is claimed.

### `agx-survey-C8` — HOLD

Recovered reading (the four displayed comparisons): with adjacency index `lambda1`, vertex connectivity `nu`, edge connectivity `kappa`, and the unique root `t in (0,1)` of
`t^3 + (2n-3)t^2 + (n^2-3n+1)t - 1 = 0`,
`lambda1-nu <= n-3+t`, `lambda1-kappa <= n-3+t`,
`lambda1/nu <= n-2+t`, and `lambda1/kappa <= n-2+t`.

All four inequalities hold on every arsenal graph. The closest arsenal comparison is still far from the boundary: on `C5[K2]`, the minimum slack is `6.014037288...` (the first inequality; `n=10`, `lambda1=5`, `nu=4`, `kappa=5`, `t=0.014037288...`). For the carrier the four slacks are respectively `14.002931619`, `17.002931619`, `16.627931619`, and `17.002931619`; its closed-form regular spectrum gives `lambda1=11` exactly. No apparent violation, so the database-sanity and novelty gates are not triggered.

### `agx-survey-C23` — NOT_APPLICABLE (and subsequently proved)

Statement: among **unicyclic** graphs of order `n`, specified cycles maximize adjacency energy for `n <= 7` and `n in {9,10,11,13,15}`, while the lollipop `Lol(n,6)` does so for every other order. None of the campaign arsenal graphs is unicyclic: each has an edge surplus larger than one, including the smallest `C5[K2]` (`n=10`, `m=25`). Thus the hypothesis excludes the entire arsenal and there is no carrier verdict to test. This is the one corpus entry counted separately from the 70 strict-open entries; its metadata also records that Andriantiana and Wagner proved the full conjecture in 2011.

### `agx-survey-C32` — HOLD

Statement: for every connected graph, algebraic connectivity `a` times matching number `mu` satisfies `a*mu >= 1`, with equality only for a star. It holds throughout the arsenal. The minimum product is `10` on Petersen (`a=2`, `mu=5`); the carrier gives the exact value `10*(10-2sqrt(5)) = 100-20sqrt(5) = 55.278640450...`. Direct Laplacian diagonalization and NetworkX maximum-cardinality matching agree; for `C5[K_m]`, the independently derived value is `a=m(5-sqrt(5))/2` and `mu=floor(5m/2)`. All margins exceed the `1e-6` guard by orders of magnitude, so no candidate gate is triggered.

### `agx-survey-C42` — DB_REJECTED (incomplete/corrupt reading; not a kill)

Literal corpus statement: for a triangle-free graph with `m` edges and independence number `alpha`, both `m/alpha <= p^-(D)` and `m/alpha <= n-p^-(D)`, where `p^-(D)` counts the negative eigenvalues of the distance matrix. The complement carrier is an apparent violation: it is triangle-free with `n=20`, `m=80`, `alpha=8`, and exact distance spectrum
`{30, (2sqrt(5))^2, (-2sqrt(5))^2, (-2)^15}`. Hence `p^-(D)=17` and `m/alpha=10`: the first comparison holds (`10<=17`) but the second fails (`10<=3`).

**Database-sanity gate: failed.** Under the identical reading, `P4` already has `m/alpha=3/2`, distance inertia `(1 positive, 3 negative)`, and so falsely requires `3/2<=1`. Exhaustive re-evaluation of all 90 connected triangle-free Graph Atlas graphs through order 7 (including `K1`) finds 43 failures of the second comparison. An independent path uses direct dense symmetric diagonalization of the distance matrix and exact brute-force independence numbers; its `P4` distance eigenvalues are approximately `5.162278,-0.585786,-1.162278,-3.414214`, again giving three negatives. Therefore the literal wording cannot be the database-tested conjecture: a qualification, sign, or column has been lost. This is not a C5[K4]-campaign counterexample and no novelty claim is made.
