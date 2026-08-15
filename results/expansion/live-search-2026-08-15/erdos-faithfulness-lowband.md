# Erdős Problems formalization-faithfulness audit — LOW-ID BAND (live search 2026-08-15)

**Lane.** TEXT-vs-TEXT faithfulness at breadth. Companion to
[`erdos-faithfulness-audit.md`](erdos-faithfulness-audit.md) (high band, ids 1212→1026,
retired agent) and to the sibling depth lane in
[`erdos-hunt.md`](erdos-hunt.md) (`CANDIDATE_FOR_DEPTH` computations).

**Why low band.** The high-band predecessor's structural conclusion: every one of its 53
audited declarations was certificate-shape-incompatible with a finite witness (asymptotic /
density / `Set.Infinite` / cardinal / `answer(sorry)` fixed optimum). Ids 1000+ are
overwhelmingly analytic number theory. The low-id band is where Erdős' finite/combinatorial
problems live, so a `FINITELY_FALSE_AS_STATED` verdict has a materially higher prior here.

---

## HANDOFF STATE

**Traversal:** strictly **ascending** numeric id over
`results/expansion/open_targets_oeis_erdos_20260815.json`, `corpus=="ErdosProblems"`,
`previously_touched==false` (364 rows). Ascending id list frozen at
`/tmp/claude-1000/-Users-kuber-mehta-Projects-scratch/21f73cfa-6e97-457f-8bb8-ae31d911cc43/scratchpad/faith/ids_asc.txt`
(line 1 = `1`, line 364 = `1212`).

**AUDITED (60 ids, complete, all in the verdict table), ascending:**

```
1 3 5 7 9 10 11 12 13 14 15 17 18 20 25 28 30 32 33 36 39 40 41 44 50 51 52
60 61 66 68 70 74 75 80 82 85 89 91 94 96 97 98 99 100 101 105 107 108 123
124 125 126 137 138 141 142 143 145 153
```

**RESUME POINT: id `155`** (line 62 of `ids_asc.txt`). Everything from `155` up to `1007` is
unaudited by either lane; the predecessor covered `1007`–`1212` descending (see the companion
file), so the two sweeps will meet somewhere near id `500`.

**Cache:** `…/scratchpad/faith/epcache/<id>.html` — ascending ids **1 through 247** (the first
90 lines of `ids_asc.txt`) are cached
(plus the predecessor's 180 descending ids ≥ ~700). Re-fetch with the desktop `User-Agent`
recipe recorded in the predecessor's file; `xargs -P 6` worked with zero failures.

**Compute artefacts written this run** (absolute paths, reusable):

- `…/scratchpad/faith/ids_asc.txt` — the frozen ascending id list (364 lines).
- `…/scratchpad/faith/chk_10_11.py` — exhaustive small-`n` verifier for EP 10/11
  ("sufficiently large" dropped): sieve + squarefree sieve to `3·10⁵`, ~20 s.
- `…/scratchpad/faith/chk36.py` — brute-force `M(n)` for EP 36's minimum-overlap database
  gate, `n ≤ 10`, ~40 s.

**Frozen provenance**

| coordinate | value |
|---|---|
| upstream repo | `google-deepmind/formal-conjectures` |
| upstream pin | `2411d22e1bd550d050d0eac6c1fb379a76a3e7c5`, read via `git show upstream/main:<path>` (read-only) |
| canonical source | `https://www.erdosproblems.com/<id>` (fetched 2026-08-15; page `last edited` recorded per target) |
| target list | `results/expansion/open_targets_oeis_erdos_20260815.json` |
| traversal order | **ascending numeric id** (predecessor took descending; sibling takes `finite_signals` rank) |
| compute | `/home/ec2-user/.venvs/wowii/bin/python`, exact integer arithmetic, 60 s cap per process |

**Severity ledger** (same as the predecessor's, plus one new label needed here)

- `FAITHFUL` — no divergence beyond notation.
- `COSMETIC` — junk/edge values, index shifts, ordered-vs-unordered counting, dropped
  "sufficiently large" that is provably harmless; truth value unchanged.
- `MATERIAL_BUT_STILL_TRUE` — genuinely a different statement, but no finite object refutes it.
- `MATERIAL_TRIVIALLY_DETERMINED` — **new label.** The Lean encodes a question whose answer is
  settled by routine mathematics while the source question is open. Not finitely certifiable,
  but the declaration no longer poses the Erdős problem.
- `FINITELY_FALSE_AS_STATED` — an explicit finite witness refutes the literal declaration.
- `VACUOUS_AS_STATED` — the literal declaration is trivially satisfiable.
- `STATUS_SYNC` — status coordinates disagree. Per METHOD rule 9, never a discovery claim.

**Publication.** No upstream issue, PR, comment, or any other public write was made or is
proposed. No `git` mutation was run. Internal reading record only.

---

## Verdict table

| id | site state / prize | open decl(s) | divergence | severity | cert. shape |
|---|---|---|---|---|---|
| 1 | open / OPEN | `erdos_1`, `.variants.real` | none material. `N ≠ 0` guard is *necessary* (`A = ∅ ⊆ Icc 1 0` would force `C·2⁰ < 0`); strict `<` vs source `≫` is absorbed by the `∃ C > 0`. `IsSumDistinctSet` injectivity is over `A.powerset`, correct. `.variants.real` matches "subset sums all differ by at least 1" via `Pairwise (1 ≤ dist ·)` | FAITHFUL | `∃ C` global constant |
| 3 | open / OPEN | `erdos_3` | `Set.IsAPOfLength` = `∃ a d, ENat.card s = l ∧ s = {a + n•d | n < l}`. The `ENat.card s = l` clause **forces `d ≠ 0`** for `l ≥ 2`, so no degenerate constant-AP vacuity. `¬ Summable (1/a)` over the subtype is the right reading of `∑ 1/n = ∞` (positive terms). `0 ∈ A` gives `1/0 = 0`, harmless | FAITHFUL | `∃ᶠ k` over ℕ |
| 5 | open / OPEN | `erdos_5`, `.variants.limit_point_set`, `.variants.dense` | `primeGap n = nth Prime (n+1) − nth Prime n` is 0-indexed, so `normalizedGap m = (p_{m+2}−p_{m+1})/log m` in the source's 1-indexing — a **uniform index shift of 1** between numerator and `log`; harmless for limit points since `log(n−1)/log n → 1`. `normalizedGap 0 = normalizedGap 1 = 0` junk (`log 1 = 0`, `x/0 = 0`) — cannot move an `atTop` cluster set. Restriction of `limitPointSet` to *finite* limit points is documented and `.variants.westzynthius` carries `∞` | COSMETIC | limit-point set |
| 7 | open / VERIFIABLE | `erdos_7` | `StrictCoveringSystem` extends `CoveringSystem` with `injective_moduli`, which **is** the source's "distinct" — without it, `{0,1,2 mod 3}` would settle the problem trivially. `ne_bot` kills modulus 0; `¬ (moduli i ≤ Ideal.span {2})` ⇔ `¬ 2 ∣ n` (ℤ is a PID) ⇔ odd; the extra `moduli i ≠ ⊤` is redundant (already a `CoveringSystem` field) but harmless. Lean parses as `(¬ ≤) ∧ (≠ ⊤)` (`¬` binds at 40, `∧` at 35) | FAITHFUL | `∃` covering system — construction can prove, cannot disprove |
| 9 | open / OPEN | `erdos_9` | `Erdos9A = {n | Odd n ∧ ¬∃ p k l, p.Prime ∧ n = p + 2^k + 2^l}` matches "odd integers ≥ 1 not of the form p+2^k+2^l, k,l ≥ 0" exactly (`Odd n` in ℕ ⇒ `n ≥ 1`). `upperDensity` matches "upper density". Doc nit: the site credits Crocker [Cr71] for infinitude, the Lean variant credits Schinzel via [Er77c] | FAITHFUL | `0 < upperDensity` |
| 10 | open / OPEN | `erdos_10`, `.variants.granville_soundararajan_odd`, `.variants.grechuk` | `erdos_10` **drops "large"**: it asserts `sumPrimeAndTwoPows k = Set.univ \ {0,1}`, i.e. *every* `n ≥ 2`. Provably harmless: every `n ≥ 2` is `2 + (popcount(n−2) powers of 2)`, so each small `n` has *some* representation and `k` can absorb the finite exceptional set — the "all n" and "all large n" forms are equivalent. `= Set.univ \ {0,1}` also asserts `0,1 ∉` the set, true since `p ≥ 2`. GS variant likewise drops "large" — **exhaustively checked**: no odd `n < 3·10⁵` outside `sumPrimeAndTwoPows 3`, no even `n < 3·10⁵` outside `sumPrimeAndTwoPows 4` | COSMETIC | `∃ k` / infinite set |
| 11 | open / OPEN | `erdos_11`, `.variants.not_four_dvd`, `.variants.two_pow_two` | all three **drop "large"** and substitute `1 < n`. Exhaustively checked to `3·10⁵`: zero failures for (a) odd `n > 1`, (b) `¬ 4 ∣ n`, `n > 1`, (c) odd `n > 1` with exactly two powers. Consistent with Odlyzko (10⁷) and Hercher (2⁵⁰). `Squarefree 1` holds and `Squarefree 0` fails in Mathlib, both correct here. `1 < n` is necessary (`n = 1` has no representation, min value 2) | COSMETIC | universal over ℕ (sibling lane is depth-testing these) |
| 12 | open / OPEN | `.parts.iii` | `IsGood` renders "no **distinct** a,b,c with a ∣ b+c, b,c > a" as `a ∣ b+c → a < b → a < c → b = c`, which correctly permits `b = c` (contrast EP 13, where the source omits distinctness and the Lean correctly omits it too). `0 ∈ A` is unconstrained but `1/0 = 0` cannot affect summability | FAITHFUL | `∀ A` infinite → Summable |
| 13 | **solved / PROVED** | `.variants.general` | headline `erdos_13` correctly `research solved` (Bedert). In `.variants.general`, `r = 0` makes the hypothesis `∀ a ∈ A, ¬ (a ∣ 0)`, i.e. `A = ∅` — **vacuous but not false** (conclusion `0 ≤ N/1 + C`). `b : Fin r → ℕ` allows repeats, matching the source's non-distinct `b_1,…,b_r` and reducing at `r = 2` to the (repeat-allowing) `IsForbiddenTripleFree` of the headline | COSMETIC (`r = 0` lobe vacuous) | `∀ r ∃ C ∀ N` |
| 14 | open / OPEN | `.parts.i`, `.parts.ii` | `allUniqueSums` is "exactly one **unordered** pair", and it admits `p.1 = p.2` (so `2a` is a legal representation) — the standard reading of "sum of two elements". `f ≫ g` unfolds to `IsBigO atTop g f`, so `.parts.i` is `N^{1/2−ε} = O(|{1..N}\B|)`, correct for `≫_ε`. `.parts.i` quantifies `∀ A` including `A = ∅` (then `|{1..N}\B| = N`), harmless | FAITHFUL | asymptotic |
| 15 | open / OPEN | `erdos_15` | **`Summable` used for a conditionally convergent alternating series.** See the finding block below. Index/sign bookkeeping is otherwise exactly right (`(−1)^(k+1)·(k+1)/nth Prime k` ↔ `(−1)^n·n/p_n`) | **MATERIAL_TRIVIALLY_DETERMINED** | RHS provably `False`; no finite cert |
| 17 | open / OPEN | `erdos_17` | none. `(p − 3 : ℤ)` deliberately avoids ℕ truncation (`p = 2 ⇒ −1`, vacuous). `n = 0` admitted and satisfiable (`2 − 2`). Database gate: the file's own `isClusterPrime_97_isLeast_non_cluster` matches the site's "the first prime without this property is 97" | FAITHFUL | `Set.Infinite` |
| 18 | open / OPEN | `erdos_18a`, `erdos_18b`, `erdos_18c` | `practicalH n = sup_{m ∈ Icc 1 n} sInf {k | ∃ D ⊆ n.divisors, D.card = k ∧ m ∈ subsetSums D}`. The `sInf` over *containing* sets `D` (not over the representing subset `B`) still computes the minimum `|B|`, because `D := B` is admissible and `m ∈ subsetSums D ⇒ ∃ B ⊆ D`. `Icc 1 n` includes `m = n` where the source has `1 ≤ n < m` — free, since `n ∣ n`. `sInf ∅ = 0` junk exists for non-practical `n` but every open declaration is guarded by `Nat.IsPractical` or by `n.factorial` (practicality proved in-file). `Nat.IsPractical n = ∀ m ≤ n, m ∈ subsetSums n.divisors` and `subsetSums` uses a `Finset`, i.e. **distinct** divisors ✓. Database gate: in-file `practicalH 1 = 1`, `practicalH 6 = 2` (`4 = 1+3`), `practicalH 12 = 3` (`11 = 1+4+6`) all recomputed by hand and correct. Note `erdos_18_upper_bound` weakens Erdős' "h(n!) < n for all n ≥ 1" to `∀ᶠ n` — **necessary**, since `h(1!) = 1 ≮ 1` | FAITHFUL | `∃ᶠ` / `∀ᶠ` asymptotic |
| 20 | open / OPEN | `erdos_20` | `f n k = sInf {m | ∀ {α : Type}, ∀ F, ((∀ f ∈ F, f.ncard = n) ∧ m ≤ F.ncard) → ∃ S ⊆ F, S.ncard = k ∧ IsSunflower S}`. `Set.ncard = 0` on infinite sets, so **infinite families `F` are exempt** from the hypothesis for `m ≥ 1`; immaterial, because any `m` that works for finite families works for infinite ones (pass to a finite subfamily). `n = 0` additionally admits infinite member-sets (`f.ncard = 0` ⇔ `f = ∅` ∨ `f` infinite) but `erdos_20` guards `n > 0`. `IsSunflower = ∃ S, F.Pairwise (A ∩ B = S)` is the standard Δ-system ✓. `c : ℕ → ℕ` may be `0`, but `0^n = 0` for `n > 0` makes that choice useless, so the `∃ c` is not weakened. The set `{m | …}` is upward closed, so `sInf` is a genuine minimum | COSMETIC | `∃ c` global constant |
| 25 | open / OPEN | `erdos_25` | none. `(∀ i, 0 < seq_n i) ∧ StrictMono seq_n` reproduces `1 ≤ n_1 < n_2 < ⋯`; `(x : ℤ) < seq_n i ∨ ¬(x ≡ a_i [ZMOD n_i])` reproduces "either n < n_i or n ≢ a_i" exactly | FAITHFUL | log-density existence over arbitrary sequences |
| 28 | open / OPEN | `erdos_28` | none. `sumRep A = 𝟙_A ∗ 𝟙_A` (ordered pairs — irrelevant to a `limsup = ⊤` claim); `(A + A)ᶜ.Finite` is exactly "contains all but finitely many"; conclusion is a genuine `= ⊤` in `ℕ∞` | FAITHFUL | `limsup = ⊤` |
| 30 | open / OPEN | `erdos_30` | none. `h N − (N : ℝ).sqrt` is **real** subtraction (the `.sqrt` forces the ℝ elaboration, so no ℕ truncation of the `h N − √N` difference, which can be negative). `maxSidonSubsetCard` = `sup` of `card` over Sidon subsets of `Icc 1 N` ✓; `IsSidon` is the standard `B₂` definition allowing `i₁ = i₂` ✓ | FAITHFUL | `∀ ε, =O` asymptotic |
| 32 | open / OPEN | `erdos_32`, `.variants.log_bound` | none. `IsAdditiveComplementToPrimes` uses `∀ᶠ n in atTop`, matching "every large integer". `.variants.liminf_gt_one` is correctly `research solved` (the site poses it as a question, but Ruzsa's `≥ e^γ ≈ 1.781` settles it) | FAITHFUL | `∃ A` infinite object |
| 33 | open / OPEN | `erdos_33` | (a) headline is `⨅ …= answer(sorry)`, a fixed-optimum hole; the "every large integer → every integer" change is **documented and correct** (padding `A` by finitely many elements changes no `limsup/√N`). (b) The site's **second** question (`liminf |A∩[1,N]|/√N > 1`?) has no declaration. (c) **`.variants.one_mem_lowerBounds` is vacuous**: its name and docstring claim "this value is … > 1" (a lower bound on the infimum) but the statement is `∃ A, AdditiveBasisCondition A ∧ 1 < limsup …`, which `A = ℕ` satisfies trivially (`k = k + 0²`; `limsup N/√N = ⊤`). A lower bound needs `∀ A`. Tagged `research solved`, so outside the open-declaration target set, but it is a corpus defect. (d) The headline is *also* self-answerable — the whole `⨅ … limsup …` expression can be copied into `answer` and closed by `rfl`; that half is **already reported upstream** in issue #4923 | VACUOUS_AS_STATED (headline self-answer, DUPLICATE #4923; `.variants.one_mem_lowerBounds`, not listed) | `FIXED_OPTIMUM` |
| 39 | open / OPEN | `erdos_39` | none. `(· ^ (1/2 − ε) : ℕ → ℝ) =O[atTop] (fun N => ((Icc 1 N ∩ A).ncard : ℝ))` is the correct direction for `≫_ε` | FAITHFUL | `∃ A` infinite Sidon set |
| 40 | open / OPEN | `erdos_40` | **`theorem erdos_40 : Erdos40ForSet answer(sorry)` is satisfied by `answer := (∅ : Set (ℕ → ℝ))`.** See the finding block below | **VACUOUS_AS_STATED** | trivially fillable `answer` hole |
| 41 | open / OPEN | `erdos_41` | **`NtupleCondition A n` quantifies over `Finset`s `I, J` of card exactly `n`, so it only forbids coincidences between sums of `n` *pairwise distinct* elements.** The source's "triple sums `a+b+c` … aside from the trivial coincidences" is the multiset (strong `B₃`) reading, which also forbids e.g. `a+a+b = c+c+d`. The Lean hypothesis class is therefore strictly larger, making `erdos_41` a **strictly stronger** claim than the source's. Same issue in the `research solved` `.variants.pairwise` (weak Sidon vs Sidon). Order of magnitude is unchanged (weak `B_h` sets in `[N]` are still `Θ(N^{1/h})`), so no refutation follows | MATERIAL_BUT_STILL_TRUE | `liminf = 0` over infinite `A` |
| 36 | open / OPEN | `erdos_36`, `.variants.lower`, `.variants.upper` | encoding of `M(n)` is correct (`sInf` over `Disjoint A B`, `A ∪ B = Icc 1 (2n)`, `A.card = B.card`; `Overlap` counts ordered pairs). **Database gate passed**: independently brute-forced `M(1..10) = 1,1,2,2,3,3,3,4,4,5`, matching the file's `M_one … M_five` exactly. **`.variants.upper` is a STATUS_SYNC**: it asks for `c < 0.380926853433087` with `limsup ≤ c`, and the site now records the record upper bound `c < 0.380876` due to the TTT-Discover LLM [YKLBMWKCZGS26] (improving AlphaEvolve [GGTW25] and Haugland [Ha16]) — so the declaration is answered in the literature but tagged `research open`. `.variants.lower` (`> 0.379005`, White [Wh22]) is genuinely still open. `MinOverlapQuotient 0 = 0/0 = 0` junk, irrelevant `atTop` | STATUS_SYNC (`.variants.upper`) + FAITHFUL | `FIXED_OPTIMUM` / bound-improvement |
| 44 | open / OPEN | `erdos_44`, `.variants.empty_start` | headline is a verbatim transcription ✓. **`.variants.empty_start` is a STATUS_SYNC**: `∀ ε > 0, ∀ᶠ M, ∃ A ⊆ Icc 1 M, IsSidon A ∧ (1−ε)√M ≤ #A` is precisely Singer's 1938 theorem (`h(N) ≥ (1−o(1))√N`), which the corpus itself cites on the neighbouring EP 30 page; it carries `research open` + `answer(sorry)`. Expected repair: `research solved`, `answer(True)` | STATUS_SYNC | `∃`-construction |
| 50 | open / OPEN | `erdos_50` | open declaration is FAITHFUL: `HasDerivWithinAt f y (Icc 0 1) x` depends only on `f` restricted to `Icc 0 1`, which `IsDistributionOfPhiRatio` pins, so the unconstrained `∀ f` is harmless *there*. **But the `research solved` `erdos_50_singular` is false as stated** — see the finding block | FAITHFUL (open decl); FALSE_AS_STATED on a `research solved` sibling | derivative of a singular distribution |
| 51 | open / OPEN | `erdos_51` | none. `IsLeast (φ ⁻¹' {a}) (n a)` gives both "`∃ n, φ(n) = a`" and "`n_a` is smallest" ✓. `atTop` on the subtype `A` is the right "as `a → ∞`" filter for an infinite `A ⊆ ℕ`. `0 ∈ A` would force `n 0 = 0` and `0/0 = 0`, invisible to an `atTop` limit | FAITHFUL | `∃ A` infinite |
| 52 | open / OPEN | `erdos_52` | added hypothesis `ε < 1` is **not** in the source, but is free: the `ε ≥ 1` instances follow from any `ε' < 1` since `|A|^{2−ε} ≤ |A|^{2−ε'}` for `|A| ≥ 1` and both sides vanish at `|A| = 0`. `A = ∅` gives `0 ≥ C·0^{2−ε} = 0` ✓; singletons force `C ≤ 1`, which the `∃ C` absorbs | COSMETIC | `∃ C` global constant |

| 60 | open / OPEN ("cannot be resolved with a finite computation") | `erdos_60` | headline faithful: `extremalNumber n (cycleGraph 4)` is Mathlib's max-edges-of-an-`H`-free-graph (subgraph, not induced) ✓; copies of `C₄` counted as `{H' : G.Subgraph | Nonempty (H'.coe ≃g cycleGraph 4)}.ncard`, i.e. subgraphs *equal* to a 4-cycle — each `C₄` once ✓. **`.variants.two_copies` is a STATUS_SYNC in the unusual direction**: it is tagged `research solved`, but the site says Erdős and Simonovits "**could not even prove** that at least 2 copies of `C₄` are guaranteed", and records no later proof | STATUS_SYNC (`.variants.two_copies`); headline FAITHFUL | `∃ c` + `∀ᶠ n` |
| 61 | open / OPEN | `erdos_61` | none. `¬∃ g : α ↪ Fin n, H = G.comap g` is the correct "no induced copy of `H`" (`G.comap g` is the graph induced on the image). `α = Empty`/singleton lobes are vacuous, not harmful. `∀ᶠ n in atTop` is a harmless weakening of the source's "every graph on `n` vertices" (absorbed by the `∃ c`) | FAITHFUL | `∃ c(H)` for every `H` |
| 66 | open / OPEN | `erdos_66` | none. `sumRep A n / Real.log n` has `log 0 = log 1 = 0` junk at `n = 0,1` (`x/0 = 0`), invisible to an `atTop` limit. `c ≠ 0` with `c : ℝ` correctly excludes an infinite limit as an answer to "exists and is ≠ 0" | FAITHFUL | limit of a convolution |
| 68 | open / OPEN | `erdos_68` | none. `∑' n : ℕ, 1 / ((n+2)! − 1 : ℝ)` reindexes `∑_{n≥2}` correctly, and the subtraction is in ℝ (no ℕ truncation). Positive terms, so `tsum`/`Summable` is the right idiom here (contrast EP 15) | FAITHFUL | irrationality |
| 70 | open / OPEN | `erdos_70`, `.variants.omega_times_two_four`, `.variants.omega_one` | none found. `OrdinalCardinalRamsey3` requires the colouring predicate to be permutation-invariant on distinct triples, correctly encoding a colouring of *unordered* 3-sets. Red side "order type exactly β", blue side "cardinality exactly n" are both equivalent to the "≥" readings by passing to subsets. `β.card ≤ ℵ₀` = "countable ordinal" ✓ | FAITHFUL | ordinal/cardinal partition relation |
| 74 | open / OPEN | `erdos_74`, `.variants.sqrt` | `maxSubgraphEdgeDistToBipartite` takes `sSup` over **all** `A : Subgraph G` with `A.verts.ncard = n` and `A.verts.Finite`, while the docstring says "induced subgraphs". Immaterial: `minEdgeDistToBipartite` is monotone under adding edges, so the sup is attained on induced subgraphs. `A.verts.Finite` is required alongside `ncard = n`, which correctly blocks the `ncard = 0`-on-infinite-sets trap. `sSup ∅ = 0` when `#V < n`, harmless | COSMETIC (docstring only) | `∀ f ∃ G` over infinite graphs |
| 75 | open / OPEN | `erdos_75` | `G.IsIndepSet ↑I` asks for independence in **G**, not in the subgraph `H`; that is *stronger* than the source's "H contains an independent set" — but since `H` ranges over **all** subgraphs on `n` vertices, including the induced one, the two readings have the same binding constraint, so this is exactly the induced reading ✓. The site's **second** question ("What about an independent set of size `≫ n`?") has no declaration | FAITHFUL (second question unformalized) | cardinal `ℵ₁` graph |
| 80 | open / OPEN | `erdos_80`, `.variants.log` | `f c n = sInf {bookNumber G | Admissible c G}` is the correct "min over admissible `G` of the max book", matching "maximal `m` … must contain a book of size `m`". The declarations **add** `c < 1/2`, which is not in the source ("Let `c > 0`"); the file documents this as a feasibility repair (`#edges ≤ n(n−1)/2 < n²/2`, so `Admissible` is empty and `sInf ∅ = 0` for `c ≥ 1/2`, which would falsify the statement for reasons unrelated to the question). Correct repair, explicitly declared | COSMETIC (documented added hypothesis) | `∃ ε` + `∀ᶠ n` |
| 82 | open / OPEN | `erdos_82` | none. `{k | ∀ G, ∃ S, IsRegularInduced S ∧ k ≤ S.verts.ncard}` is bounded by `n` (verts ⊆ `Fin n`) and contains `0` (empty subgraph is induced and vacuously regular), so `sSup` is a genuine maximum ✓. Independent sets and cliques are both `IsRegularInduced`, matching the classical Erdős–Fajtlowicz–Staton reading in which `F(n) ≫ log n` is the trivial Ramsey bound and `F(n)/log n → ∞` is the content ✓. `F n / log n` junk at `n = 0,1` invisible `atTop` | FAITHFUL | `Tendsto … atTop` |
| 85 | open / OPEN | `erdos_85` | none. `{k | ∀ G : SimpleGraph (Fin n), G.minDegree ≥ k → cycleGraph 4 ⊑ G}` is upward closed and contains `k = n` (no simple graph on `n` vertices has `minDegree ≥ n`), so `sInf` is a genuine minimum. `⊑` is subgraph containment, matching "contains a `C₄`". The source's `n ≥ 4` guard is subsumed by `∀ᶠ n in atTop` | FAITHFUL | `∀ᶠ n, f n ≤ f (n+1)` |

| 89 | open / OPEN | `erdos_89` | none. `minimalDistinctDistances n` = `sInf {distinctDistances P | #P = n}` (the ℝ-coercion in the set-builder is a round-trip through an injective cast, harmless); `distinctDistances` uses `offDiag`, so self-distances are excluded ✓. Question stated as a bare theorem rather than `answer(…) ↔ …`, a corpus convention difference only | FAITHFUL | `=O` asymptotic |
| 91 | open / OPEN | `erdos_91` | none. `DilationEquivSimilar A B := ∃ f : ℝ² ≃ᵈ ℝ², f '' A = B` is exactly plane similarity (a `DilationEquiv` scales all distances by a fixed ratio and is invertible, so the relation is symmetric) ✓. `¬ UniqueMinimizer n` unfolds to "two non-similar minimisers" ✓. Biconditional written `statement ↔ answer(sorry)` (reversed from the corpus norm), cosmetic | FAITHFUL | `∀ᶠ n` |
| 94 | **solved / PROVED (LEAN)** | `.variants.regular_ngon` | headline `erdos_94` correctly `research solved` with a `formal_proof` link matching the site's PROVED (LEAN) ✓. Open declaration is the Erdős–Fishburn strengthening ("`∑ f(u_i)²` is maximal for the regular `n`-gon for large `n`"), transcribed faithfully; `regularNGon n` is the inscribed regular `n`-gon and `∀ᶠ n` avoids degenerate small `n` | FAITHFUL | `∀ᶠ n, ∀ P` |
| 96 | open / OPEN | `erdos_96` | none. `unitDistancePairsCount = #(offDiag.filter (dist = 1)) / 2` counts **unordered** pairs ✓; `sSup` is over a set proved `BddAbove` in-file by `n.choose 2` ✓ | FAITHFUL | `=O n` |
| 97 | open / **FALSIFIABLE** | `erdos_97`, `.variants.k_equidistant` | none. `HasNEquidistantPointsAt n A p := ∃ r > 0, #(A.filter (dist p · = r)) ≥ n` — the `r > 0` guard automatically excludes `q = p`, so the docstring's "other points" is honoured without an explicit `q ≠ p`. `¬ HasNEquidistantProperty 4 A` unfolds to "some vertex has no 4 equidistant vertices" ✓. **Cert-shape note for the sibling lane:** the literal negation is one finite convex-position point set, so this is one of the few genuinely finite-certificate declarations in the low band (site label agrees: FALSIFIABLE) | FAITHFUL | **finite point configuration** |
| 98 | open / OPEN | `erdos_98` | none. `InGeneralPosition X = NonTrilinear X ∧ ∀ T ⊆ X, T.ncard = 4 → ¬ Cospherical T` matches "no three on a line and no four on a circle" ✓ (`ncard = 4` also blocks the infinite-`T`/`ncard = 0` trap) | FAITHFUL | `Tendsto … atTop` |
| 99 | open / OPEN | `erdos_99` | none. `HasMinDist1` correctly demands both "all pairwise ≥ 1" and "some pair `= 1`" ✓. `FormsEquilateralTriangle p q r` = three unit distances, which **forces** `p,q,r` pairwise distinct (`dist p p = 0 ≠ 1`) — the degenerate-triangle trap is closed. `IsMinOn` over `{B | #B = n ∧ HasMinDist1 B}` is the right "chosen to minimise the diameter" ✓ | FAITHFUL | `∀ᶠ n` over ℝ² configurations |
| 100 | open / OPEN | `erdos_100`, `.variants.strong` | `DistancesSeparated` **omits** the source's "all pairwise distances are at least 1", but that is *implied*: taking `p₂ = q₂ = a ∈ A` gives distance `0`, so every nonzero distance `d` satisfies `\|d − 0\| ≥ 1`. `.variants.strong` (`diam ≥ n − 1`) uses **real** subtraction and `∀ᶠ n`, so Piepmeyer's 9-point example (`diam < 5 < 8`) does not refute it — matching the site's "Perhaps the diameter is even ≥ n−1 for sufficiently large n" | COSMETIC (implied hypothesis omitted) | `∃ C` + `∀ᶠ n` |
| 101 | open / OPEN | `erdos_101` | none. `linesWithPointsFor 4 S` counts lines through **exactly** 4 points of `S`, which coincides with "at least 4" under the `NonCollinearFor 5 S` hypothesis ✓; the sup is over a bounded set (`≤ n²`) | FAITHFUL | `=o(n²)` |
| 105 | **solved / DISPROVED (LEAN)** | `.variants.sub_four` | headline correctly `research solved` + `answer(False)` with a `formal_proof` link ✓. Open declaration is the `n − 4` version, transcribed faithfully (`A.card = B.card + 4`, `¬ Collinear ℝ A`, "some line through two points of `A` misses `B`"). The site's other suggested strengthenings (`n − O(1)`, `(1−o(1))n`) are not formalized. **Cert-shape note for the sibling lane:** the literal negation is one finite pair of plane point sets — genuinely finite | FAITHFUL | **finite point configuration** |
| 107 | open / **FALSIFIABLE** | `erdos_107` | none. `cardSet n` is upward closed (`HasConvexNGon` is monotone in the point set), so `sInf` is a genuine minimum ✓; `2^(n−2)` uses ℕ truncated subtraction but is guarded by `n ≥ 3` ✓. Database gate: the in-file `f_three_eq : f 3 = 3` agrees with `2^(3−2)+1 = 3` ✓ | FAITHFUL | Erdős–Szekeres value |
| 108 | open / OPEN | `erdos_108` | none material. `SimpleGraph.girth` returns `⊤` on acyclic graphs, so the `k = 2` lobe is trivially satisfiable by a single edge — matching the source, where `k = 2` is equally trivial. Added `Nonempty V` is harmless; `∀ (V : Type u)` fixes one universe | FAITHFUL | `∃ f(k,r)` over all graphs |

| 123 | **solved / PROVED (LEAN)** | `.variants.powers_2_3_5_snug` | headline `erdos_123` correctly `research solved` + `answer(True)` with a `formal_proof` link ✓. Open declaration transcribes Erdős' snug strengthening exactly: `IsSnug ε A := ∃ hA : A.Nonempty, ∀ a ∈ A, a < (1+ε)·A.min' hA` ⇔ `b_t < (1+ε)b_1` ✓; the `Finset` gives the source's *distinct* summands ✓; `↑(powers 2) * ↑(powers 3) * ↑(powers 5)` is `{2^k 3^l 5^m}` ✓ | FAITHFUL | `∀ ε ∀ᶠ n` |
| 124 | open / OPEN | `erdos124.ne_zero` | none material. The site's own statement contains a typo (`∑ 1/(d_r − 1)` where it means `d_i`); the Lean silently uses the intended `∑_{d ∈ D} (d−1)⁻¹` ✓. `c_i ∈ {0,1}` is encoded by pointwise-summing the sets, which is faithful because `0 ∈ sumsOfDistinctPowers d k` (empty index set) ✓. `(d − 1 : ℚ)⁻¹` is rational subtraction, not ℕ truncation ✓. `D = ∅` is excluded by the `1 ≤ ∑` hypothesis ✓ | FAITHFUL | `∀ k ∀ D ∀ᶠ n` |
| 125 | **solved / DISPROVED (LEAN)** | `.positive_upper_density`, `.zero_density`, `.zero_lower_positive_upper_density` | set definitions correct (`(digits 3 x).toFinset ⊆ {0,1}`; `digits b 0 = []` so `0 ∈ A`, matching the source's `∑ ε_k 3^k` with all `ε_k = 0`) ✓. **Redundancy:** given the already-proved `.variants.positive_lower_density : answer(False)` (i.e. `lowerDensity = 0`), `.zero_lower_positive_upper_density` is *literally equivalent* to `.positive_upper_density`, and `.zero_density` is its negation — three `research open` declarations encoding one open question. The four-case split is the Lean file's own editorial expansion; the site only asks about positive lower density | COSMETIC (redundant open declarations) | density |
| 126 | open / OPEN | `erdos_126`, `.variants.isLittleO` | `A : Finset ℕ` **admits `0 ∈ A`**, which the source's `A ⊆ ℕ` (Erdős' positive-integer convention) does not: `A = {0,1}` gives `∏ = 1` and `f(2) = 0`, whereas the positive-integer `f(2) = 1`. Harmless for the asymptotic question: writing `A = {0} ∪ A'`, the product is `∏_{a∈A'} a² · ∏_{a≠b∈A'}(a+b)`, so `f_pos(n−1) ≤ f_Lean(n) ≤ f_pos(n)`, and `f_pos` is nondecreasing (a sub-`Finset`'s product divides), so `f_Lean(n)/log n → ∞ ⇔ f_pos(n)/log n → ∞`. `offDiag` counts ordered pairs, squaring the product without changing its prime factors ✓ | COSMETIC | `Tendsto … atTop` |
| 137 | open / OPEN | `erdos_137`, `.variants.multiple_powerful_factors` | headline faithful (`Finset.Ioc n (n+k)` = `k` consecutive positive integers ✓; the product is never `0`, so the `Powerful 0` degeneracy is unreachable). In `.variants.multiple_powerful_factors` the Lean product `∏ x ∈ Ioc m (m+n), x = (m+1)⋯(m+n)` has **`n` factors starting at `m+1`**, whereas the source writes `m(m+1)⋯(m+n)` (`n+1` factors starting at `m`) — an index shift, immaterial because `Lean(m,n) = Source(m+1, n−1)` and both quantify `∀ᶠ n, ∀ m > 0` (the only uncovered start, `m = 1`, contributes the factor `1`). **Cert-shape note:** the headline's literal negation is one pair `(k, n)` with a powerful product — genuinely finite | COSMETIC (index shift) | **finite (k,n) pair** |
| 138 | open / OPEN | `erdos_138`, `.variants.quotient`, `.variants.dvd_two_pow` | `monoAP_guarantee_set` is upward closed (restrict a colouring), so `sInf` is a genuine minimum ✓. Database gate: in-file `W 1 = 1`, `W 2 = 3` are the standard values ✓. **Docstring transcription error:** `.variants.prime`'s docstring says "Berlekamp has proved `W(p+1) ≥ p^{2^p}`" while the **code** says `p * 2^p ≤ W (p+1)`; the site confirms the code (`W(p+1) ≥ p2^p`), so the *docstring* is the defect. `.variants.difference` uses ℕ truncated subtraction `W(k+1) − W k`, safe because `W` is nondecreasing (a mono `(k+1)`-AP contains a `k`-AP). Kozik–Shabanov's general lower bound `W(k) ≫ 2^k` and Fox–Hunter's `r ≥ 3` result are not formalized | COSMETIC (docstring) | `Tendsto … atTop` |
| 141 | open / OPEN | `erdos_141`, `.variants.eleven`, `.infinite_three`, `.infinite_general_case` | none. `IsPrimeProgressionOfLength s l := ∃ a, ENat.card s = l ∧ s = {(a+n).nth Prime | n < l}` correctly forces *consecutive* primes ✓, and the conjunction with `IsAPOfLength l` (whose `ENat.card` clause forces `d ≠ 0`) gives a genuine non-trivial AP ✓. Database gate: in-file `{3,5,7}` example, and `.variants.first_cases` (`k ≤ 10`) matches the site's "verified for k ≤ 10" ✓ | FAITHFUL | `∃` construction / `Set.Infinite` |
| 142 | open / OPEN | `erdos_142`, `.variants.upper`, `.variants.three`, `.variants.lower` | **`erdos_142`, `.variants.upper` and `.variants.three` are all satisfied by copying the left-hand side into `answer`** (`isTheta_refl` / `isBigO_refl`). See the finding block below. `.variants.lower` (`r_k(N) = o(N/log N)`, `1 < k`) carries no `answer` hole and is a genuine statement. Definitional layer is correct: `IsAPOfLengthFree s l := ∀ t ⊆ s, t.IsAPOfLength l → l ≤ 1` correctly excludes trivial APs | **VACUOUS_AS_STATED** (3 of 4 open decls) | trivially fillable `answer` holes |
| 143 | open / OPEN | `.parts.i`, `.parts.ii` | `WellSeparatedSet` transcribes the source hypothesis exactly ✓ and `.parts.ii` (`Summable 1/(x log x)`, positive terms — the right `Summable` use, contrast EP 15) is verbatim ✓. **`.parts.i` is an editorial invention**: the source asks the undefined "Does this imply that `A` is sparse?", and the Lean substitutes `liminf \|A ∩ [1,x]\|/x = 0`, a specific and comparatively weak reading (`liminf`, not `lim`). The source's third and fourth questions (`∑_{x<n} 1/x = o(log n)`; `≪ log x/√loglog x`) are commented out as TODO | MATERIAL (editorial reading of "sparse") | density / summability |
| 145 | open / OPEN | `erdos_145` | none. `s = Nat.nth Squarefree` is 0-indexed while the source is 1-indexed, but `A x = {n | s n ≤ x}` collects the *same* gap multiset, so the shift cancels ✓. `(s (n+1) − s n : ℝ)` is real subtraction ✓. `α = 0` is admitted and harmless (all gaps `≥ 1`, so `gap⁰ = 1`) | FAITHFUL | limit existence |
| 153 | open / OPEN | `erdos_153` | none. `f n` is the infimum over Sidon sets of size `n`, so "as `\|A\| → ∞`" becomes `Tendsto f atTop atTop` — the correct uniform reading ✓. Index reshuffle (`∑_{i ∈ Ico 1 t} (s_i − s_{i−1})²` vs the source's `∑_{1≤i<t}(s_{i+1}−s_i)²`) is the same sum ✓; `s` is monotone so no ℕ-subtraction truncation. `f 0 = f 1 = 0` junk (`0/0 = 0`), invisible `atTop` | FAITHFUL | `Tendsto … atTop` |

---

## Findings requiring detail

### EP 15 — `Summable` encodes absolute/unconditional convergence; the source asks about conditional convergence

`FormalConjectures/ErdosProblems/15.lean`:

```lean
@[category research open, AMS 11]
theorem erdos_15 : answer(sorry) ↔
    Summable (fun k : ℕ => (-1 : ℚ) ^ (k + 1) * (k + 1) / (k.nth Nat.Prime)) := by
  sorry
```

Site statement (`erdosproblems.com/15`, last edited: not shown): *"Is it true that
$\sum_{n=1}^\infty(-1)^n\frac{n}{p_n}$ converges, where $p_n$ is the sequence of primes?"* —
Erdős' question, and Tao's conditional theorem [Ta23], are about **convergence of the
sequence of partial sums**, i.e. conditional convergence of an alternating series.

Mathlib's `Summable f` means `∃ a, HasSum f a`, and `HasSum f a` is convergence of the net of
**finite-subset** partial sums — i.e. *unconditional* summability. Over ℝ (finite dimensional)
unconditional ⇔ absolute. Here the absolute series is
$\sum_n n/p_n$, and $p_n \sim n\log n$ gives $n/p_n \sim 1/\log n$, whose sum diverges.
Hence the RHS is **provably false**. (The codomain is ℚ, which only makes it stronger:
`HasSum` in ℚ pushes forward along the continuous additive embedding ℚ ↪ ℝ to `HasSum` in ℝ.)

Consequence: the correct `answer(...)` for this declaration is `False`, obtainable from
Mertens/PNT alone, whereas the Erdős problem the file cites is open. The declaration therefore
does not encode the source question. The faithful encoding is the usual partial-sum idiom,
e.g. `∃ l : ℝ, Tendsto (fun N => ∑ k ∈ Finset.range N, f k) atTop (𝓝 l)`.

- **Severity:** `MATERIAL_TRIVIALLY_DETERMINED`. Not `FINITELY_FALSE_AS_STATED`: refuting the
  RHS needs the divergence of `∑ 1/log n`, not a finite witness.
- **Certificate shape:** no finite replayable certificate.
- **Duplicate check:** NOT YET RUN (no upstream issue/PR search performed).
- Cross-check inside the corpus: the same file's neighbours use `Summable` correctly for
  positive-term series (EP 3 `¬ Summable (1/a)`, EP 12 `.parts.iii Summable (1/n)`), so this is
  an isolated idiom slip rather than a corpus-wide convention.

### EP 40 — `answer(sorry)` hole with no extremality constraint; `∅` settles it

`FormalConjectures/ErdosProblems/40.lean`:

```lean
def Erdos40For (g : ℕ → ℝ) : Prop :=
  ∀ A : Set ℕ,
    (fun N : ℕ ↦ √N / g N) =O[atTop] (fun N ↦ ((A ∩ .Icc 1 N).ncard : ℝ)) →
    limsup (fun N ↦ (sumRep A N : ℕ∞)) atTop = ⊤

def Erdos40ForSet (G : Set (ℕ → ℝ)) : Prop := ∀ g ∈ G, Tendsto g atTop atTop → Erdos40For g

@[category research open, AMS 11]
theorem erdos_40 : Erdos40ForSet answer(sorry) := by
  sorry
```

Site statement (`erdosproblems.com/40`, last edited: not shown): *"For what functions
$g(N)\to\infty$ is it true that $|A\cap\{1,\ldots,N\}| \gg N^{1/2}/g(N)$ implies
$\limsup 1_A*1_A(n)=\infty$?"*

`Erdos40ForSet G` unfolds to `∀ g ∈ G, …`. **Witness: `answer := (∅ : Set (ℕ → ℝ))`.** Then
`∀ g ∈ ∅, …` is vacuously true and the declaration is discharged by `simp`. Every subset of
`{g | ¬ Tendsto g atTop atTop}` works equally well, so the hole is not merely trivially
fillable, it is massively under-determined.

The source asks for the **largest** such class of `g`. A faithful encoding needs an
extremality wrapper — `IsGreatest {G | Erdos40ForSet G} answer(sorry)`, or a fixed
family such as `Erdos40ForSet {g | ∀ᶠ N in atTop, g N ≤ (log N)^C}` — exactly the pattern the
corpus uses elsewhere (`IsLeast`/`IsGreatest` + `answer`).

- **Severity:** `VACUOUS_AS_STATED`. The witness is explicit and requires no computation.
- **Certificate shape:** trivially fillable `answer` hole; no mathematical content is asserted.
- **Duplicate check:** NOT YET RUN.
- Contrast within the same file: `erdos_40.variants.implies_erdos_28` takes the hypothesis
  `Erdos40ForSet .univ`, i.e. the *maximal* instantiation, showing the file's author had the
  strong reading in mind; only the headline lost it.

### EP 33 — `.variants.one_mem_lowerBounds` asserts an existential, not a lower bound

```lean
@[category research solved, AMS 11]
theorem erdos_33.variants.one_mem_lowerBounds : ∃ A, AdditiveBasisCondition A ∧
    1 < Filter.atTop.limsup (fun N => (A ∩ Icc 1 N).ncard / √N) := by
  sorry
```

Docstring: *"Erdos observed that this value is finite and > 1."* — i.e. `1` bounds the
**infimum** from below, a `∀ A` statement. The declaration says `∃ A`, which
`A = ℕ` satisfies at once: `AdditiveBasisCondition ℕ` holds via `k = k + 0²`, and
`limsup (N / √N) = ⊤ > 1`. The declaration name (`one_mem_lowerBounds`) describes the
intended statement, not the encoded one.

- **Severity:** `VACUOUS_AS_STATED` (declaration is `research solved`, so it is not in the
  open-target set; recorded as a corpus defect).
- **Duplicate check:** NOT YET RUN.

### EP 50 — `erdos_50_singular` quantifies over a function that is pinned only on `[0,1]`

```lean
def IsDistributionOfPhiRatio (f : ℝ → ℝ) : Prop :=
  ∀ c ∈ Icc (0 : ℝ) 1, {n : ℕ | (φ n : ℝ) < c * n}.HasDensity (f c)

def IsPurelySingular (f : ℝ → ℝ) : Prop :=
  Continuous f ∧ ∀ᵐ x ∂volume, deriv f x = 0

@[category research solved, AMS 11]
theorem erdos_50_singular (f : ℝ → ℝ) (hf : IsDistributionOfPhiRatio f) : IsPurelySingular f
```

`IsDistributionOfPhiRatio f` constrains `f` **only on `Icc 0 1`**. `IsPurelySingular f` asserts
`Continuous f` on **all of ℝ**. Explicit counterexample: let `F` be the true Schoenberg
distribution function and set

```
f x = F x            for x ∈ [0,1]
f x = 0              for x ∉ [0,1] ∪ {2}
f 2 = 1
```

Then `IsDistributionOfPhiRatio f` holds (its only requirement is on `[0,1]`), and `f` is
discontinuous at `2`, so `IsPurelySingular f` fails. The declaration is therefore **false as
stated**, despite carrying `research solved`.

The *open* declaration `erdos_50` in the same file is immune, because it uses
`HasDerivWithinAt f y (Icc 0 1) x` with `x ∈ Icc 0 1`, which only sees `f` on `Icc 0 1`.
The repair for the solved sibling is to state singularity of the restriction, or to add
`∀ x ∉ Icc 0 1` normalisation to `IsDistributionOfPhiRatio`.

- **Severity:** FALSE_AS_STATED (on a `research solved` declaration, therefore outside the
  open-target set); certificate is an explicit function, not a finite object.
- **Duplicate check:** NOT YET RUN.
- **Pattern to reuse:** *an unconstrained function/parameter in a hypothesis predicate, with the
  conclusion asserting a global property of it.* Worth grepping the corpus for.

### EP 142 — three `answer(sorry)` holes closed by copying the left-hand side

```lean
@[category research open, AMS 11]
theorem erdos_142 (k : ℕ) : (fun N => (r k N : ℝ)) =Θ[atTop] (answer(sorry) : ℕ → ℝ)

@[category research open, AMS 11]
theorem erdos_142.variants.upper (k : ℕ) : (fun N => (r k N : ℝ)) =O[atTop] (answer(sorry) : ℕ → ℝ)

@[category research open, AMS 11]
theorem erdos_142.variants.three : (fun N => (r 3 N : ℝ)) =Θ[atTop] (answer(sorry) : ℕ → ℝ)
```

Site statement (`erdosproblems.com/142`, last edited 04 April 2026): *"Prove an asymptotic
formula for `r_k(N)`."*

Nothing in these declarations forces the `answer` function to be independent of `r`.
`answer := (fun N => (r k N : ℝ))` closes `erdos_142` and `.variants.three` by
`Asymptotics.isTheta_refl`, and closes `.variants.upper` by `isBigO_refl`.

- **Severity:** `VACUOUS_AS_STATED`, three of the file's four open declarations.
  `.variants.lower` is untouched and genuine.
- **Duplicate status:** **PARTIAL DUPLICATE.** Upstream issue
  [#4922](https://github.com/google-deepmind/formal-conjectures/issues/4922) (OPEN) already
  reports `.variants.upper`, via the different trivial witness `fun N => (N : ℝ)`
  (`r k N ≤ N`). The umbrella issue
  [#4923](https://github.com/google-deepmind/formal-conjectures/issues/4923) (OPEN) lists the
  same "reflexive asymptotic answer" pattern for Erdős **422**, **539**, **789** and the
  "exact self-answer" pattern for Erdős **33**, **329**, **348**, **409.iii** — but **not**
  for `erdos_142` (headline) or `erdos_142.variants.three`. Those two are, as of the pin,
  unlisted instances of a pattern the upstream repo is actively tracking.

---

## Duplicate-surface audit (METHOD A2.2 — read-only, no upstream write)

`gh search issues/prs --repo google-deepmind/formal-conjectures`, run 2026-08-15.

| finding | upstream status |
|---|---|
| EP 142 `.variants.upper` trivial answer | **DUPLICATE** — issue #4922 (open) |
| EP 142 headline + `.variants.three` (`=Θ` self-answer) | **NOT LISTED** — same class as #4923's 422/539/789 bullets, but those two declarations are absent from every issue found |
| EP 33 headline `⨅ … = answer(sorry)` self-answer | **DUPLICATE** — #4923 first bullet ("Erdős 33 … the entire unknown infimum/limsup expression can be copied into `answer`") |
| EP 33 `.variants.one_mem_lowerBounds` (∃ instead of ∀) | **NOT LISTED** — #4923's Erdős 33 bullet is about the headline's `answer` hole only |
| EP 40 `Erdos40ForSet answer(sorry)` satisfied by `∅` | **NOT LISTED** — no issue or PR matches `erdos_40`/`Erdos40ForSet` beyond a merged `variants.known_result` proof |
| EP 15 `Summable` for a conditionally convergent series | **NOT LISTED** — cf. #4896's open-PR blocker "PR #4660 — `tsum` without `Summable`/`HasSum`", which is the *opposite* defect |
| EP 50 `erdos_50_singular` false as stated | **NOT LISTED** |
| EP 44 `.variants.empty_start` = Singer 1938 | **NOT LISTED** |
| EP 60 `.variants.two_copies` tagged `research solved` | **NOT LISTED** |
| EP 36 `.variants.upper` superseded by TTT-Discover bound | **NOT LISTED** |
| EP 138 `.variants.prime` docstring `p^{2^p}` vs code `p·2^p` | **NOT LISTED** |
| EP 80 added `c < 1/2` | **ALREADY FIXED UPSTREAM** — issue #4867 (closed); the pin already carries the repair, so this is not a defect |

Context found while searching: #4896 ("Tracking: possible misformalizations found in statement
audits") and #4923 ("Possible misformalizations II") show that an upstream contributor is
running a parallel audit of exactly this kind. Any future write must be diffed against both.

---

## Running severity roll-up (60 ids audited)

| severity | count | ids |
|---|---|---|
| `FINITELY_FALSE_AS_STATED` | **0** | — |
| `VACUOUS_AS_STATED` | **3** | **40** (open decl), **142** (3 of 4 open decls), 33 (headline self-answer + `research solved` variant) |
| `MATERIAL_TRIVIALLY_DETERMINED` | 1 | 15 |
| `MATERIAL_BUT_STILL_TRUE` / `MATERIAL (editorial)` | 2 | 41, 143 |
| `FALSE_AS_STATED` on a non-open declaration | 1 | 50 (`erdos_50_singular`) |
| `STATUS_SYNC` | 3 | 36 (`.variants.upper`), 44 (`.variants.empty_start`), 60 (`.variants.two_copies`) |
| `COSMETIC` | 13 | 5, 10, 11, 13, 20, 52, 74, 80, 100, 125, 126, 137, 138 |
| `FAITHFUL` | 37 | 1, 3, 7, 9, 12, 14, 17, 18, 25, 28, 30, 32, 39, 51, 61, 66, 68, 70, 75, 82, 85, 89, 91, 94, 96, 97, 98, 99, 101, 105, 107, 108, 123, 124, 141, 145, 153 (the headlines of 36, 44, 60 are also faithful; those ids are counted under `STATUS_SYNC` for their variants) |

**Certificate shape.** As in the high band, almost every open declaration in ids 1–153 is
`CERTIFICATE_SHAPE_FAIL` for a finite-counterexample lane. The exceptions worth handing to the
sibling depth lane, whose literal negation *is* one finite object, are:

- **EP 97** `erdos_97` / `.variants.k_equidistant` — one convex-position finite point set
  (site label already says FALSIFIABLE);
- **EP 105** `.variants.sub_four` — one finite pair `(A,B)` of plane point sets, in a file where
  the `n−2` and `n−3` versions were *both* already killed by explicit finite constructions
  (Hickerson; Xichuan). This is the highest-prior finite target found in the low band;
- **EP 137** `erdos_137` — one pair `(k, n)` with `∏_{x ∈ (n, n+k]} x` powerful;
- **EP 107** `erdos_107` — one `n` with `f(n) ≠ 2^{n−2}+1` (site label FALSIFIABLE).

**Divergence patterns that paid in the low band** (complementing the predecessor's list):

1. **`answer(sorry)` holes with no extremality wrapper.** By far the highest-yield low-band
   pattern: EP 40 (`∅`), EP 142 (copy the LHS), EP 33 (copy the `⨅`). Always ask *"what is the
   laziest term of the answer's type?"* before reading the mathematics. Upstream is tracking
   this genre in #4919/#4922/#4923, so check there first.
2. **`Summable` for a series the source only claims converges conditionally** (EP 15). Check
   whether the summand changes sign; if it does, `Summable` is the wrong idiom.
3. **A hypothesis predicate that pins its function argument only on part of its domain**, with
   the conclusion asserting a global property (EP 50 `IsDistributionOfPhiRatio` pins `f` on
   `[0,1]`, `IsPurelySingular` asserts `Continuous f` on ℝ).
4. **A declaration name/docstring that states `∀`, with a body that states `∃`** (EP 33
   `one_mem_lowerBounds`).
5. **`Finset`-of-card-`n` used for a source's multiset condition** (EP 41 `NtupleCondition`:
   only *distinct* `n`-tuples are constrained, so the hypothesis class is strictly larger and
   the conjecture strictly stronger).
6. **Dropped "sufficiently large" is usually harmless but must be *checked*** — EP 10/11 needed
   an exhaustive small-`n` verification (`n < 3·10⁵`, zero failures) before it could be called
   cosmetic.
7. **Docstring ↔ code numeric drift** (EP 138 `p^{2^p}` vs `p·2^p`; the site adjudicates in
   favour of the code).
8. **Status drift both ways**: EP 36/44 are `research open` but answered in the literature;
   EP 60 `.variants.two_copies` is `research solved` although the site says it was never proved.
