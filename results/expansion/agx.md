# AutoGraphiX open-conjecture expansion sweep

## Methodology and progress

- **Coverage target:** all 70 entries in `corpora/autographix.json` whose status begins `open`, plus `agx-survey-C23`, whose full form is marked open although a weaker form was proved. Each entry receives its own durable verdict below.
- **Arsenal:** `C5[K_m]` for `m = 2,3,4,5,6,8`; `C7[K3]`; `C9[K3]`; `T(7)`, `T(8)`, `T(9)`; `comp(C5[K4])`; Petersen; and Paley(13), Paley(17), Paley(29) when its invariants are cheap. Spectra use direct symmetric eigensolvers with a `1e-6` comparison guard, and the closed form for `C5[K_m]` is used as an independent check.
- **Exactness:** combinatorial and distance averages are retained as integers or `Fraction`s. A spectral gap of magnitude at most `1e-6` is a tie, never a disproof.
- **Candidate gate:** every apparent violation is re-evaluated under every plausible reading on all connected Graph Atlas graphs of order at most 7 and the named calibration set (`C5`--`C9`, `P7`, Petersen, `K3,3`, `K7`, stars, and complete bipartite graphs). A reading already false there is classified as transcription/database corruption rather than a new kill. Any gate survivor is recomputed by a separate code path and novelty-checked against the literature, including Wagner and Vito--Stefanus.
- **OCR discipline:** an expression that cannot be recovered faithfully from the corpus is recorded as `SKIP_OCR` with the surviving garble quoted; no intended formula is guessed.
- **ILP discipline:** no solver call may exceed 60 seconds. (This lane currently needs no ILP.)

Progress: **17/71** entries evaluated (70 strict-open + 1 open-in-full).

## Verdicts

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
