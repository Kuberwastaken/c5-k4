# Confirmed findings ledger — 2026-08-15 OEIS/Erdős sweep

**Upstream pin:** `2411d22e1bd550d050d0eac6c1fb379a76a3e7c5`.
**Status of this file:** decision-ready summary. Nothing here has been written
upstream; `UPSTREAM_PROTOCOL.md` requires explicit per-turn authorization.

## Classification note (METHOD_V1_6 §A6)

Every confirmed item below is a **formalization defect**: a statement about
what the Lean declaration in `formal-conjectures` asserts. **None is a
counterexample to the underlying mathematics**, and in several cases the
literal declaration is trivially *true*. None is eligible for the
`UPSTREAM_PROTOCOL.md` release path, which is for counterexamples. The
appropriate artifact is an upstream issue in the style of the live trackers.

## Published upstream, 2026-08-15

Eight issues filed after an offline duplicate gate (1734 issues + 3226 PRs
with per-PR file lists, matched on title, body and changed path) and
re-verification against then-current main `638da20e`, not the ledger pin:

| Item | Issue |
|---|---|
| OEIS A237271 `observation_carmichael` | [#4974](https://github.com/google-deepmind/formal-conjectures/issues/4974) |
| Erdős 1093 `deficiency` | [#4975](https://github.com/google-deepmind/formal-conjectures/issues/4975) |
| Erdős 1055 `IsOfClass` | [#4976](https://github.com/google-deepmind/formal-conjectures/issues/4976) |
| Erdős 40 `erdos_40` | [#4977](https://github.com/google-deepmind/formal-conjectures/issues/4977) |
| Erdős 33 `.variants.one_mem_lowerBounds` | [#4978](https://github.com/google-deepmind/formal-conjectures/issues/4978) |
| Erdős 15 `Summable` | [#4979](https://github.com/google-deepmind/formal-conjectures/issues/4979) |
| Erdős 477 index set | [#4980](https://github.com/google-deepmind/formal-conjectures/issues/4980) |
| Erdős 952 asserted direction | [#4981](https://github.com/google-deepmind/formal-conjectures/issues/4981) |
| Erdős 142 (partial duplicate) | [comment on #4922](https://github.com/google-deepmind/formal-conjectures/issues/4922#issuecomment-5303863018) |

New provenance surfaced while drafting, now in the issue bodies: **1093** —
PR #1328's first commit had `IsKSmooth … p ≤ k` correct, and a review
suggestion swapped in `smoothNumbers k` with no discussion of the threshold;
**477** — PR #1242 replaced `Set.range f.eval` with `f.eval '' {n | 0 < n}`
and set the docstring to `n > 0`, then #1510 re-synced the docstring to the
site's `{f(n) : n ∈ ℤ}` while carrying the one-sided set into every
declaration, which is why docstring and code now contradict each other inside
the same declaration.

## Crossings — finite disproofs of open declarations (strongest class)

These two are **counterexamples**: an explicit finite witness makes the open
declaration's right-hand side false, forcing `answer := False`. They remain
statements about the formalization — in both cases the underlying OEIS
conjecture is untouched and *not* refuted — but unlike the vacuity findings
below, something is genuinely false rather than trivially true.

Both were independently re-verified by a second code path in the parent
session (sieve-based, no shared code with the discovering lane).

| Target | Witness | Why the declaration fails | Duplicate status |
|---|---|---|---|
| **OEIS A110854** `conjecture` | **d = 3** (premise via 5 − 2) | `a n = p(2n+2) − p(2n+1) − p(2n) + p(2n−1)`. `a 1 = 7−5−3+2 = 1`; for `n ≥ 2` all four primes are odd, so `a n` is even. Hence `{\|a n\| : n>0} ⊆ {1} ∪ 2ℕ` and 3 is unreachable. Confirmed: all `a n` even for `n = 2..3000`, 3 absent. Further witnesses d = 5, 9, 11, 15, 17, 21 | Novel — 0 hits on `A110854`/`110854` (only PR #4450, the AutoOeis batch that created the file); absent from #4896/#4923/#4927 |
| **OEIS A108864** `conjecture` | **n = 67**, `a 67 = 8925` (odd) | Declaration says `answer(sorry) ↔ ∀ n > 58, Even (a n)` over the set `\|σ(n) − 2n\| ≤ 10`. 8925 = 3·5²·7·17, σ = 17856, 2n = 17850, deviation 6 ≤ 10; indices 59–66 are **2336**, 4030, 4096, 5830, 8128, 8192, 8384, 8768 — all even, so 67 is minimal. Confirmed by three disjoint implementations. **Root cause:** A108864 is "perfect deficiency (A109883) ≤ 10" — a greedy divisor-subtraction quantity, not `\|σ(n) − 2n\|`. Decisive: 24 is in the published DATA but `\|σ(24) − 48\| = 12 > 10` | Novel — 0 hits on `A108864`/`108864`/`A109883`; absent from the collector issues |

The A108864 forensics are worth preserving: re-implementing A109883 literally
reproduces its own 79 published terms, and its `≤ 10` filter reproduces
A108864's first 61 DATA terms exactly, placing **1155 at 0-indexed position
58** — precisely the bound the declaration uses. In the (incorrect) Lean set
1155 sits at index 52. The OEIS conjecture itself ("is 1155 the last odd
term?") is **not** refuted: A109883(8925) = 2969 ≫ 10.

## Confirmed, apparently unclaimed

| Target | Defect | Witness / proof | Duplicate status |
|---|---|---|---|
| **OEIS A237271** `observation_carmichael` | Hypothesis quantifies over every nonzero `a : ZMod k` instead of units coprime to `k`; unsatisfiable for composite `k`, so the open declaration is vacuously true | General proof: composite `k` has prime `p∣k` with `(p : ZMod k) ≠ 0`; `p^(k−1)=1` would make `p` a unit. No `k ≤ 20000` satisfies it | Novel. `observation_carmichael` → 0 hits; absent from #4896/#4923/#4927. File is 3 days old — **re-check immediately before any write** |
| **Erdős 1093** `deficiency` | Mathlib `smoothNumbers n` means prime factors `< n`; source says `≤ k` | All 23 site catalogue entries reproduce under `≤`; exactly 3 change under `<` (C(7,3) 1→0, C(23,5) 1→0, C(47,11) 4→3). Fix is one token: `smoothNumbers (k+1)` | Novel. Provenance: PR #1328's first commit was correct; a review suggestion introduced it with no threshold discussion |
| **Erdős 1055** `IsOfClass` / `p` | At `r = 2` the equality clause is vacuous in `ℕ+`, so `IsOfClass 2 2` holds and `p 2 = 2` | A005113(2) = 13 (confirmed live). Defect confined to `r=2`; `r = 1,3,4,5` reproduce A005113 exactly. No declaration becomes false | Novel. `IsOfClass` → 1 hit (introducing PR #1197) |
| **Erdős 40** `erdos_40` | `Erdos40ForSet G := ∀ g ∈ G, …` with no extremality wrapper, so the `answer(sorry)` hole closes vacuously | Witness `answer := (∅ : Set (ℕ → ℝ))`. Same file's `variants.implies_erdos_28` uses `.univ`, showing the strong reading was intended | Not listed upstream |
| **Erdős 33** `.variants.one_mem_lowerBounds` | States `∃ A, … ∧ 1 < limsup …` while name/docstring claim a lower bound; the "finite" half is carried only by the junk `Real.sInf_empty : sInf ∅ = 0` | ~~Witness `A = ℕ`: `k = k + 0²`, `limsup N/√N = ⊤`~~ **RETRACTED 2026-08-15** — that `limsup` elaborates in `ℝ`, not `EReal`, so for `A = ℕ` it is the junk `0` and `1 < 0` fails. Machine-checked refutation in `publication/erdos33_limsup_probe.lean`; correction posted on #4978. Defect survives as a name/docstring-fidelity + junk-value issue (severity is **not** `VACUOUS_AS_STATED`), with provenance: #631 stated `1 ∈ lowerBounds …`, #1206 replaced it with `∃ A, … → …` while moving the two neighbours to `EReal`, #2226 patched `→` to `∧` | Not listed upstream (the file's headline self-answer *is* already in #4923) |
| **Erdős 15** | RHS is provably **False** as encoded — Mathlib `Summable` is unconditional (absolute over `ℝ`) and `∑ n/pₙ ~ ∑ 1/log n` diverges — while Erdős's actual question (conditional convergence) is open | Divergence argument | Not listed upstream |
| **Erdős 477** | Source says `b ∈ {f(k) : k ∈ ℤ}`; all five declarations use `f.eval '' {n \| 0 < n}` = `{f(k) : k ≥ 1}`. The site's own published degree-2 proof uses `f(k) − f(−k)`, which the Lean set excludes | Repaired the `X²` case (`f(k+1) − f(k−1)`, `k ≥ 2`); the general `a ∣ b` variant is **not** repaired by that argument | Not listed upstream |
| **Erdős 952** | Source asks a question and quotes [Er80] "the answer is almost certainly negative"; the Lean asserts the positive existence as a bare `theorem` rather than `answer(sorry) ↔` | Checked for a trivial-truth loophole: none (the norm is the squared step; injectivity forces escape to infinity) | Not listed upstream |

## Confirmed but partially claimed

| Target | Defect | Duplicate status |
|---|---|---|
| **Erdős 142** `erdos_142`, `.variants.upper`, `.variants.three` | All three `answer(sorry)` holes close by copying the LHS (`isTheta_refl` / `isBigO_refl`) | **Partial**: #4922 reports `.variants.upper`; #4923 lists the same reflexive-asymptotic pattern for EP 422/539/789 but **not** for `erdos_142` or `.variants.three` |

## Status-sync findings (not discovery claims, METHOD rule 9)

> **⚠ CONTESTED, 2026-08-15 — do not publish these without re-verification.**
> The publication lane could not reach erdosproblems.com (Cloudflare 403 for
> curl and WebFetch; headless browser could not bind a port; archive.org
> blocked), so it checked the offline mirror `teorth/erdosproblems@data/problems.yaml`
> instead — and that mirror still records **all seven of these as `open`**,
> directly contradicting several rows below (notably 1054 "Tao's disproof" and
> 36 "`c < 0.380876` now recorded"). Either the mirror is stale or the
> originating audit misread the live page; both are possible and neither is
> established. All seven were therefore **held back from upstream**, correctly:
> an unverified "this is already solved" claim is the expensive direction to be
> wrong in. Re-run against the live site before treating any row here as a
> finding. The rows are kept for traceability, not as confirmed results.

| Target | Issue |
|---|---|
| **Erdős 1084** `triangular_optimal_d2` | `research open` though Harborth (1974) proved the declared `=` form; docstring writes `<` where the source says `=` |
| **Erdős 1106** `.parts.i` | `research open` though Schinzel–Wirsing settles it |
| **Erdős 1054** `.parts.i` | `research open` though the site records Tao's disproof |
| **Erdős 36** `.variants.upper` | Asks `c < 0.380926853433087`; site now records `c < 0.380876` |
| **Erdős 44** `.variants.empty_start` | Exactly Singer (1938), cited by the corpus itself on EP 30 |
| **Erdős 60** `.variants.two_copies` | Tagged `research solved`; the site records no proof — mis-tagged in the *solved* direction |
| **OEIS A357513** | Proved by Kutal, Jul 2026, with a Lean formalization; not tracked upstream |

## Closed brackets and negative results worth keeping

- **Erdős 242** (Erdős–Straus with distinctness): predecessor's timeout bracket is
  **closed**. Exact divisor enumeration (`(py−q)(pz−q) = q²`) settles every
  `x ∈ (n/4, 3n/4]` completely, plus a divisor lift. Every `n = 3..2,000,000` has an
  explicit verified `(x,y,z)`; 148,933 exhaustive, 1,851,065 lifted, 45.5 s, third
  code path agrees to `n ≤ 400`. `HOLD_BOUNDED`.
- **Erdős 779**: first run ever; least prime witness for every `n = 1..200`
  (largest `p = 3559` at `n = 180`). `HOLD_BOUNDED`, bracket at `n ≥ 201`.
- **Erdős 982**: the one genuinely finite target; faithful. Exhaustive integer
  searches for `n = 6..9` found nothing. Its concyclic obstruction is **already
  upstream** (open PR #4694 / issue #4691) — no novelty available there. Live lane
  continues via Danzer's 9-gon and the Fishburn–Reeds 20-gon.
- **Erdős 274**: the predecessor's flagged `ENat.card`/index-0 loophole **does not
  exist** — Neumann's lemma forces finite index on every part of a finite exact
  cover, so the declaration is exactly Herzog–Schönheim. Minimal counterexample needs
  `k ≥ 5`; 89 groups searched exhaustively, 0 hits.

## Refuted predecessor claims (recorded so they are not re-raised)

- **Erdős 1084** "finitely false as stated" — the `<` is only in the docstring; the
  declaration asserts `=`, which is exactly Harborth's theorem. Lattice recomputation
  matches `9n²+3n` for n = 0..5.
- **Erdős 931** "closed interval trivialises it" — on the repo's own witness the strict
  reading is satisfied by the same prime; 280 premise-satisfying tuples show **zero**
  disagreements between readings. Also: the docstring sentence attributed to the source
  is **not present** on erdosproblems.com/931 (live and cached byte-identical); Wayback
  check unresolved (HTTP 429).

## Timing risk

Upstream contributor **KitaKen1** is running a parallel misformalization audit
(#4896 "Tracking: possible misformalizations found in statement audits", updated
2026-08-14; #4923 "Possible misformalizations II", 2026-08-13). There are 23 open
issues matching the misformalization/vacuous/`answer(sorry)` surface. The duplicate
surface for everything above is therefore **moving daily**, and each item must be
re-checked immediately before any write.

Hard evidence of how fast: while the OEIS lane was running on 2026-08-15, upstream
PR **#4964** was opened at 07:12Z covering **A103425**, a target that lane was
mid-way through triaging. It stopped on the duplicate. A second target, **A100434**,
was already covered by PR #4560 (closed unmerged). Treat any delay before writing
as a real risk of losing priority, not a neutral choice.

## Non-open declaration defect (out of target scope, recorded)

- **Erdős 50** `erdos_50_singular` (`research solved`) is false as stated:
  `IsDistributionOfPhiRatio f` pins `f` only on `[0,1]` while `IsPurelySingular f`
  asserts `Continuous f` on all of `ℝ`; take the true distribution on `[0,1]` plus a
  jump at `x = 2`. The *open* `erdos_50` is immune.

## Wikipedia collection, M–Z lane (2026-08-15)

51 files triaged (FIN 11 · FIN-HARD 9 · INF 26 · TERM 5) at pin `638da20e`.

**Apparently unclaimed — candidates for filing**

| Target | Defect | Status |
|---|---|---|
| `SparseRuler.wichmann_conjecture` | Wikipedia says Wichmann speculated all **sufficiently large** optimal rulers are of this type ("no others up to length 213"); the Lean substitutes a hard threshold `13 < g.length`. The docstring's justification is also off by one in unit — by A004137 the length-58 exception has 13 **marks** = 12 **segments** | unclaimed; no finite certificate reachable (`C(78,13) ≈ 1.6·10¹⁴`) |
| `UnionClosed.variants.cardinality_even_of_union_closed_tight` | `UCC_tight` demands *every* element of the ambient type lie in exactly half the family — strictly stronger than "tight" (`max_i = #A/2`), and it silently forces the type finite and exactly covered. Shadowed binder `hA` used twice | unclaimed; direction precludes a counterexample. Exhaustive check over all subfamilies of `P([n])`, `n ≤ 4`: `#A` a power of 2 every time |

**Already claimed — stopped, no filing**

- `RudinsConjecture.rudins_conjecture_unique` is finitely false (witness `N = 6, q = 120, a = 49`; second witness `(168,121)`), re-verified by two disjoint code paths — but upstream issue **#4568** (Terry-cyx, 2026-07-23, open) already carries the identical witness. New material we hold that #4568 does not: the root cause is Wikipedia's *Super-Strong* form restricting uniqueness to `N = GP_k+1 ≥ 8`, and the failure set for `6 ≤ N ≤ 30` is exactly `{6,7,9,10,11,12,15,19,20,21,22,24,25,26}`, whose complement contains every `GP_k+1` value `{8,13,16,23,27}`. Worth a comment on #4568, not a new issue.

**Out of declared scope (`research solved`, not open targets)**

- `Sendov.variants.le_nine` claims `n ∈ Icc 2 9`; Brown–Xiang proved `n < 9`, i.e. `n ≤ 8`. A genuine overclaim in a solved declaration.
- `SnakeInTheBox.snake_upper_bound` omits the `− 7` present in its own docstring formula; `sidorenko_tree` is tagged `research solved` with an open `sorry` in its inductive step.

**Verified clean with brackets** (recorded so they are not re-run): `(2,5)`-perfect `σ(σ(n)) = 5n` none for `n ≤ 1.2·10⁶`; 3×3 semi-magic square of distinct cubes none (roots ≤ 220, third row to 317); Pollock 5-tetrahedral holds for `N ≤ 3·10⁶` with Salzer–Levine reproduced exactly (343867 not a sum of four tetrahedra; 241 exceptions); Oppermann for `2 ≤ x ≤ 50000`; no Wall–Sun–Sun prime `p < 2·10⁶`.

## Wikipedia collection, A–L lane (2026-08-15)

80/80 triaged (59 certificate-shape-incompatible · 13 finite · 8 faithfulness
surfaces) at pin `638da20e`, re-verified unchanged at end of run.

**Crossing — finitely false as written, novel**

| Target | Witness | Why |
|---|---|---|
| `EllipticCurveRank.…rank_height_count_asymptotic` | **`H = 2`** (also `H = 3`), any `r ∈ [1,20]` | Asserts an exact equality `{E ∈ heightLE H \| r ≤ E.rank}.ncard = (H:ℝ)^((21−r)/24 + f H)` for every `H > 1`. But `naiveHeight E = max(4\|A\|³, 27B²) ≤ 3` forces `A = B = 0`, excluded by `Δ_ne_zero` and `reduced`, so `heightLE 2 = ∅` and `ncard = 0` while `Real.rpow 2 x > 0` for every real exponent — no `f` can satisfy it. Two code paths; first non-empty is `heightLE 4 = {(±1,0)}` |

Provenance: PR #252 ("fix(EllipticCurveRank): corner cases and a sanity check")
introduced the `1 < H` guard for exactly this failure mode and stopped one step
short — the set stays empty until `H = 4`. The sibling
`twentyone_le_rank_height_count_asymptotic`, edited in the same diff, uses `≤`
and is immune. The PPVW 8.2(b) heuristic itself is untouched.

**Faithfulness defects, apparently unclaimed**

| Target | Defect |
|---|---|
| `HardyLittlewood.first_hardy_littlewood_conjecture` | Two: (i) states `=O[atTop]` where the docstring and source both say `∼`, which for admissible tuples is a classical Brun/Selberg sieve theorem rather than the open conjecture; (ii) offsets are not required distinct — at `m = ![0,1,1]` the Euler product diverges (partials 1.63 → 8.12 for `Q = 10…10⁶`), so Mathlib's `tprod` returns junk `1`, giving `C = 4` and an RHS `≍ n/log³n` that is false conditional on the twin-prime conjecture. The constant is otherwise right: `m = ![0,1]` gives `1.320324` vs `2C₂ = 1.320323632…` |
| `Dickson.polignac_conjecture` | Not de Polignac: the source requires **consecutive** primes; the Lean states the strictly weaker generalized-twin form, and admits `k = 0` where the instance is Euclid's theorem |
| `Wikipedia.…same_parity_betrothed` | Omits `m ≠ n`; `IsBetrothed n n ⟺ σ(n) = 2n+1` (quasiperfect), so it is satisfiable by a different open problem. Sibling `infinitely_many_betrothed` does enforce `p.1 < p.2`. No `n ≤ 5·10⁶` with `σ(n) = 2n+1`; 35 betrothed pairs `≤ 5·10⁶`, all opposite parity |
| `Koethe.…matrixOver_KotherRadical` | `{I}`/`hI` do not occur in the conclusion (spurious, not vacuous — satisfiable at `I = ⊥`); docstring misstates the code, which correctly gives Wikipedia's formulation 6 |
| `DedekindNumber.M_eq` | The `answer(sorry)` hole is closed by `kisielewiczFormula`, at which point it *is* the `research solved` declaration directly above it. **Partially claimed**: issue #3490 (closed) raised it; resolving PR #3895 reworded the docstring and *added* the closing witness while leaving the hole open |

**Already claimed — stopped**: `bounded_burnside_problem` (`research open` on a
question Novikov–Adian settled in 1968) is issue **#4518** + PR **#4519**, open
since 2026-07-21 with the same proposed fix.

**Self-refuted candidate**: `feit_thompson_primes` — the omitted direction is
trivially true (`x ↦ (x−1)/log x` increasing on `[2,∞)`), so the Lean keeps
exactly the non-trivial half. No defect.

**Bounded holds**: 4-D Euler brick exhaustive to sides `≤ 10⁵` — 1714 3-D Euler
bricks (smallest `(44,117,240)`), **zero** 4-D; idoneal completeness exact to
`10⁵` (and `10⁶` over-budget, recorded); Büchi `M = 5` none in range; Gilbreath
`d^k(0) = 1` for `k ≤ 5000`; Goormaghtigh only 31 and 8191 up to `10¹³`.

## Correction 7 — the database-boundary figure was unsourced (2026-08-15)

The README asserted for two weeks that Graffiti.pc's verification database ran
to "roughly n ≤ 11", and that figure carried the whole cliff narrative ("C₅[K₄]
lives past the edge of that database"). Writing the paper exposed it: **there is
no source**. It is not traceable to DeLaViña's site (unreachable from this host)
or to any paper, and the paper draft refused to cite it.

Replaced with a claim we can actually verify — all 995 connected graphs of order
≤ 7 satisfy the conjectures in question — which is what the argument needs
anyway. The mechanism survives; the specific number did not.

Three further premise corrections from the same pass, all previously stated in
this repo and all wrong:

| Was claimed | Actually |
|---|---|
| `f = b = tree = 4` for `m ≥ 2` | true for **every** `m ≥ 1` |
| `n mod Δ = 2m+1` | only for `m ≥ 3` (`m=1` gives 1, `m=2` gives 0 — which is why conjecture 64's RHS is 2 there) |
| "≈40 exactly tight" | defensible count is **≈36**; four naive-parse hits are tight only under gate-*discarded* readings, and one (401b) is corrupt |

## Other collections lane (2026-08-15) — 131/131 triaged

GreensOpenProblems 50 · Arxiv 24 · Paper 23 · Mathoverflow 10 · Books 8 ·
Kourovka 4 · Millenium 4 · OpenQuantumProblems 3 · Other 3 · Subsets 2.
Millenium triaged out as a block (every open declaration quantifies over
function spaces, manifolds, infinite language sets, or an L-function). Its RH
file actually *pre-empts* our defect shape, documenting why a naive ERH via
`dedekindZeta` would be provably false.

**Crossing — novel, in a collection no active auditor has touched**

| Target | Witness | Why |
|---|---|---|
| `Books/…/Equidistribution.lean` `isEquidistributedModuloOne_transcendental_three_halves_pow` | nested-interval Cantor construction, `λ = 3/2`, `c = 1/10`, `G = 8` | Asserts **every** transcendental `x` makes `(x·(3/2)ⁿ)` equidistributed mod 1; the cited source (Kuipers–Niederreiter Cor. 4.2) says **almost all**. Since `c·λ^G = 6561/2560 ≥ 2+c`, two blocks survive per level, giving a Cantor set of cardinality `2^ℵ₀` — hence containing transcendentals — each with density `≥ 1/8 > 1/10` in `[0,1/10]`. Exact `Fraction` arithmetic, 45 levels, zero violations. Provenance: PR #3609, an 8-line diff with no citation. The `x = 1` question is untouched |

**Further unclaimed defects**

- `Paper/VoronovskajaTypeFormula` `bezier_bernstein_operators` (+2 variants): constant `f` telescopes to `c`, so the sequence is identically 0 and `answer` is **forced to 0** — contradicting the file's own note that numerics indicate a non-zero limit.
- **GreensOpenProblems degenerate-`answer` cluster** (machine-checked, `lean` exit 0): reflexive — `green_25`, `green_51` (closed by `rfl`), `green_27.equivalent`, `green_37_theta`; mis-scoped, no closed answer exists — `green_24`, `green_16`, `green_37`, `green_37_asymptotic`, `green_41`; content-free — `green_35.lower` (closed by the zero function).
- `green_40.variants.all_n`: machine-proved `(atTop : Filter ℝ≥0∞) = pure ⊤`, so the statement says "`f_all r = ⊤` eventually", not "→ ∞". The sibling `green_40` gets this right via `𝓝 ⊤`.
- `Paper/LatinSquare.lean`: `molsExistenceProblem` closed by `rfl`; two further holes sit outside a `variable {n}`, making `answer := False` unreachable. **Live race: PR #4965 is editing this file today** — re-gate immediately before any write.
- Status sync: `green_35.upper` (`ub ∞ < 0.7505`) is answerable from Green's own Update 2025 (`c_∞ ≤ 0.75026`).

**Dropped as duplicates** (4): Green 19 (#4927), `green_72` (#4941/#4896), Green 14 `W_3_20…W_3_39` (#4854/#4584 — caught *before* a planned SAT run was spent), `green_37_bigO` (#4943).

**Own hypotheses refuted** (recorded so they are not re-raised): Green 50 `10 • A` is `Finset.nsmul`, the iterated sumset, not pointwise scaling — faithful; `Other/VCDimConvex` has no `n = 0` contradiction (`HasAddVCNDimAtMost A 0 d` unfolds to `A = ∅ ∨ A = univ`); `EquationalTheories_677_255` is correctly tagged per arXiv 2512.07087.

**Computational holds** (exact, two code paths each): Arxiv/2501.03234 — no violations for odd primes ≤ 5987, and all three thresholds confirmed **exactly sharp**, last failures at `k` = 5, 233, **3119**; Arxiv/2607.05739 — no integer `xₙ` for `5 ≤ n ≤ 119,503` (the file claims only `n ≤ 3000`); Arxiv/1601.03081 — odd `n ≤ 1,922,151`, 115 crystals, zero with two component pairs.

## Correction 8 — three briefs corrected at filing time (2026-08-15)

The Wikipedia filing lane overturned three things I had stated as settled when
briefing it. Recorded because the pattern (claims degrading on contact with
verification) is now the campaign's most reliable regularity.

1. **`3 < H` is not the minimal fix for the EllipticCurveRank defect — and no
   numeral guard works at all.** `heightLE H = {(1,0), (−1,0)}` for every
   `4 ≤ H ≤ 26`, and both curves (conductors 64 and 32) have rank 0, so the
   *filtered* set is still empty there for every `r ≥ 1`. The first non-empty
   `H` depends on `r`: at `r = 1` the minimal-conductor rank-1 curve 37a1
   reduces to `y² = x³ − 16x + 16`, height 16384; at `r = 20` no bound is
   known. PR #4995 therefore uses `∀ᶠ H in atTop`, matching the docstring's own
   `o(1)`, and both artifacts explain why a guard cannot work.
2. **A Hardy–Littlewood partial product in our scan does not reproduce.** The
   scan reported `1.628` at `Q = 10`; recomputation gives `1.4954` (values for
   `Q ≥ 10²` agree). Issue #4996 uses the recomputed table.
3. **The betrothed finding is stronger than recorded.** The repo already
   contains `QuasiperfectNumbers.Quasiperfect n := σ 1 n = 2n + 1` as its own
   `research open` declaration, so the missing `m ≠ n` does not merely resemble
   another open problem — it silently entangles two of them. Both artifacts now
   lead with that.
