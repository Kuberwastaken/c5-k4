# Wave 2: OEIS boundary and b-file audit

Date: 2026-08-14 (UTC)

## Scope calibration

- Frozen upstream commit: `b33d8678a28118c95d8d4f60b11faaf39ccff1e6`.
- Source PR: [google-deepmind/formal-conjectures#4450](https://github.com/google-deepmind/formal-conjectures/pull/4450), merged 2026-08-13 12:46:43 UTC as `d7032450c559849f2a345f80582688c76b25ffcb`.
- The PR title says “first 64 files”, but the merged diff actually contains 75 files, of which **73 are `FormalConjectures/OEIS/*.lean` modules**. The live audit therefore uses all 73 actual OEIS files as the authoritative scope. The “64” is stale metadata, not the file count at merge.
- A109074 was already found, certified, and released before this wave. It is retained only as a calibration row and is excluded from new findings.
- Every invoked subprocess was capped at 60 seconds. No issue, PR, release, or repository change was opened from this audit.

## Result so far

No new finding was identified. Two previously released boundary failures calibrate the method:

1. A109074 fails at its literal lower endpoint `n = 1` (already released; excluded).
2. A111291 fails at the real-domain lower boundary `x = 3/2` (independently reproduced here, but already released by the time of this status audit; not new).

All other concretely executable lower-endpoint or small-boundary instances checked below passed. This is finite boundary testing, not a proof of any surviving universal conjecture.

## Calibration candidate: A111291 (known/released, not new)

Exact frozen declaration (`FormalConjectures/OEIS/111291.lean::OeisA111291.conjecture`):

```lean
theorem conjecture : ∀ (x : ℝ), x > 1 →
    (countRefactorable x : ℝ) ≥ x / (2 * Real.log x) := by
  sorry
```

Exact input and values:

- Input: `x = 3/2`.
- `floor (3/2) = 1`.
- The only integer in `Icc 1 1` is `1`; `1.divisors.card = 1` and `1 ∣ 1`, hence `countRefactorableNat 1 = 1` and `countRefactorable (3/2) = 1`.
- `log(3/2) < 3/2 - 1 = 1/2`, so `2 log(3/2) < 1` and
  `(3/2) / (2 log(3/2)) > 3/2 > 1`.
- The conclusion therefore requires `1 ≥` a quantity strictly greater than `3/2`, which is false.

Source reconciliation:

- [OEIS A111291](https://oeis.org/A111291) defines `a(n)` as the number of refactorable numbers `≤ 10^n`; its b-file begins `0→1, 1→4, 2→16, 3→92, ...`, exactly matching the module's four term theorems.
- The OEIS comment says that “the number of refactorables less than x is at least x/(2 log(x))”. It states no explicit lower threshold. The Lean module makes the domain precise as every real `x > 1` and implements the count through `floor x`, exposing the small-real counterexample. This is a source/formalization boundary defect, not a disagreement in A111291's tabulated sequence values.

Status audit performed before classification:

- Repository-wide GitHub searches in `google-deepmind/formal-conjectures` for `A111291`, `111291`, and `countRefactorable` returned no open or closed issue and no open or merged PR.
- Project release [`oeis-111291-formalization-v1`](https://github.com/Kuberwastaken/c5-k4/releases/tag/oeis-111291-formalization-v1) existed at the final audit (published 2026-08-14 06:38:21 UTC).
- Classification here: **known/released calibration; not novel**.

## Calibration candidate: A109074 (excluded)

Exact frozen declaration:

```lean
theorem conjecture (n : ℕ) (h_pos : n ≥ 1) :
    frac n = (b (n + 1) : ℚ) / (b n : ℚ) := by
  sorry
```

At `n = 1`, the module computes `frac 1 = 1`, `b 1 = 1`, and `b 2 = 3`, so the declaration asserts `1 = 3`. [OEIS A109074](https://oeis.org/A109074) prints the same shifted ratio comment involving A005156. This was already certified and published as [`oeis-109074-formalization-v1`](https://github.com/Kuberwastaken/c5-k4/releases/tag/oeis-109074-formalization-v1), and is excluded from new findings.

## Authoritative b-file reconciliation

All 73 authoritative OEIS b-files were downloaded directly from `https://oeis.org/Axxxxxx/bxxxxxx.txt` and compared with the frozen modules.

- 70 modules state numeric `a_i` term theorems: **335 local numeric statements**.
- Five statements are explicit local sentinel values at index `0` for OEIS sequences whose b-files begin at index `1` (A105720, A109227, A110854, A117027, A034693). They are implementation padding, not claimed b-file entries.
- After removing those five sentinels and applying the modules' documented index shifts, **all 330 mapped primary-`a` numeric statements agree exactly** with their authoritative b-files.
- Documented shifts used: A100478 `local a(n) = OEIS a(n+1)`; A108569 `+1`; A108864 `+1`; A109845 `+1`; A228828 `+1`.
- The three predicate/set modules without numeric `a_i` theorems also match their first b-file members: A056777 has `65, 209, 11009`; A063880 has `108, 540, 756`; A067720 has `1, 2, 4, 6, 8, 10`. Thus **342 mapped primary numeric/member checks** agree in total.
- Locally redefined reference sequences were checked separately. A100434's `c` and `d` initial values agree with the signed bisections of A002315/A001541 and A075870/A005319 printed in the authoritative A100434 entry. A102371 imports (rather than redefines) the audited A105033 module and agrees at `n=1..5`.
- **Known A109074 reference mismatch:** its local helper `b n = binom(3n,n)/(2n+1)` is not A005156. Local `b` begins `1,1,3,12,...`, while the [A005156 b-file](https://oeis.org/A005156/b005156.txt) begins `1,1,3,26,...`; the first discrepancy is exactly `b 3=12 ≠ 26`. This second defect is already documented in the released A109074 audit and remains excluded from new findings.
- A111291's b-file agreement and A109074's primary numerator b-file agreement show why term-only testing is insufficient: both failures live in a universal relation layered on top of correctly transcribed primary sequence terms.

## Rejected candidate: A100434 (already reported upstream)

The frozen module contains three exact declarations:

```lean
theorem conjecture1 (n : ℕ) : c n + d n = b n := by sorry
theorem conjecture2 (n : ℕ) : e n + f n = b n := by sorry
theorem conjecture3 (n : ℕ) : g n + a n = b n := by sorry
```

At the literal input `n = 0`, the frozen definitions give:

- `c 0 = 1`, `d 0 = 2`, hence `c 0 + d 0 = 3`;
- `e 0 = d 0 / 2 = 1`, `f 0 = d 1 / 2 = 2`, hence `e 0 + f 0 = 3`;
- `g 0 = 0`, `a 0 = 3`, hence `g 0 + a 0 = 3`;
- but `b 0 = c 1 = -3`.

Thus all three declarations reduce to `3 = -3` and are false. The same sign discrepancy recurs at `n = 2`: `c 2 + d 2 = -17`, while `b 2 = c 3 = 17`.

Source reconciliation: [OEIS A100434](https://oeis.org/A100434/internal) itself defines `b(2n)=c(2n+1)` and then states the incompatible conjecture `c(n)+d(n)=b(n)`. Its displayed auxiliary terms give exactly the values above. The primary sequence b-file remains correct and matches the module.

Required status gate: exact repository searches found closed upstream PR [#4560, “Add OEIS A100434 disproof”](https://github.com/google-deepmind/formal-conjectures/pull/4560). That PR was closed without merge on 2026-07-25, but its body already records the `n=2` counterexample `-17 ≠ 17`. Therefore this is **known upstream and rejected as a novel finding**, even though `n=0` is an even smaller witness and all three frozen declarations fail there.

## Literal executable-boundary ledger

The table records the smallest admissible input, plus nearby values where they distinguish the two sides. “Pass” means only that the displayed finite instances pass.

| Module / exact declaration | Inputs evaluated | Literal values | Result |
|---|---|---|---|
| A100434 `a_even`, `a_odd` | `n=0,1` | `a 0=3=-c 1`; `a 1=4=d 1`; next parity cases also agree | pass |
| A100434 `conjecture1/2/3` | `n=0,2` | every LHS is `3` at `0`, while `b 0=-3`; at `2`, first LHS `=-17`, `b 2=17` | **known failure, PR #4560** |
| A100800 `∀ n, n ≠ 0 → a n ≠ 0` | `n=1..5` | `2,4,6,8,10`, all nonzero | pass |
| A101779 `∀ n, 1 ≤ n → ∃ k, Ak n k` | `n=1..4` | witnesses are the b-file values `k=2,2,3,5`; at `n=1`, `1·2+0=2` prime | pass |
| A102371 universal RHS | `n=1..5` | `a n = 2^n-1-A105033(n-1)` gives `1,2,7,12,29` | pass; declaration is answer-wrapped |
| A103151 `conjecture n (n≥4)` | `n=4,5,6` | `a=1,1,2`, hence `a≥1` | pass |
| A104320 `∀ n, 15<n → a n>0` | `n=16..20` | b-file/local definition gives `4,2,3,3,3` zeros in ternary `2^n` | pass |
| A105020 `conjecture` | smallest realized `n=1`, `i=1`, `j=3` | endpoints `a 1=3`, `a 3=5`, `j=i+n+1`; interior `k=2`, `a 2=4=2·2` semiprime | pass; analogous b-file checks through `n=15` passed |
| A105210 `conjecture_disjoint_starting_values` | all ten unordered pairs of starts; first 200 iterates each | no intersection among starts `1,393,412,668,932`; first A105210 orbit begins `393,528,545,660,682,...` | pass finite prefix |
| A105565 `conjecture n` | `n=1..30` | at `1`: `S=0`, `α≈0.784971967`, `β≈0.672275938`; `-1.327724062 < -0.784971967 < -0.327724062` | pass |
| A105720 square biconditional | `n=1..20` | at `1`, `a=5` and RHS false; at `3`, `a=36` square and RHS true; at `6`, `a=169` square | pass |
| A105751 `prime_divides_some_term` | `p=2,3,5` | `a 0=0`, so each prime divides the zero sentinel with witness `n=0` | pass but vacuous boundary |
| A108081 `count_words_in_x_is_a_shifted` | `n=1` | `xN 1` contains only `[0]`, so ncard `=1=a 0` | pass |
| A108211 `conjecture n` | `n=1..5` | reciprocal-floor side is `17,65,145,257,401`, equal to `16n²+1` | pass |
| A108306 `a_is_invert_transform_case` | `n=0,1,2` | upper-left values of `m^(n+1)` are `1,6,21`, equal to `a 0,a 1,a 2` | pass |
| A108306 general `conjecture a_val b_val n` | arbitrary `a,b`, `n=0,1,2` | both sides simplify to `1`, `1`, `a+1` | pass |
| A108569 `∀ n, 0<n → Even (a n)` | `n=1..8` | local values `4,8,16,32,64,110,128,220`, all even; local index is OEIS index `n+1` | pass |
| A108866 prime biconditional | `n=4..20` | at `4`, numerator `61`, `61 mod 16=13`, both sides false; at `5`, numerator `50`, divisible by `25`, both sides true; every tested value agreed | pass |
| A109074 ratio | `n=1` | `frac 1=1`, but `b 2/b 1=3` | **released calibration; excluded** |
| A109908 `∀ n>3, a n>0` | `n=4..20` | begins `3,5,7,11,11,...`, all positive | pass |
| A109909 `∀ n>3, a n>0` | `n=4..20` | begins `2,2,1,2,1,...`, all positive | pass |
| A110475 representation biconditional | `m=1..15` | at first nonexception `m=8`, choose `x=y=4`: `a 4=1` and `8=4+4`; listed exceptions have no smaller representation | pass |
| A110566 odd-value coverage | `m=1,3,5,7,9` | b-file witnesses `n=1,6,105,44,63` respectively | pass |
| A110835 `∀ n>0, a n≥n` | `n=1..20` | starts `8≥1, 4≥2, 8≥3, 6≥4, ...`; all twenty pass | pass |
| A110854 prime-difference coverage | smallest differences `d=1,2,4,6` | `d=1` from primes `3,2` and `|a 1|=1`; b-file witnesses for `2,4,6` are `n=9,4,30` | pass |
| A111291 real lower bound | `x=3/2` | count `=1`, RHS `>3/2` | **released calibration** |
| A112521 diagonal identity | `n=1..5` | `(a n,T n n)=(1,1),(0,0),(6,6),(4,4),(60,60)` | pass |
| A112970 `conjecture1/2/3` | `n=0..5` | at `0`: `a1=a3=1`, `a0=a2=1`, `a0=1`; all three identities also pass through `5` | pass |
| A113250 odd-index squares | `n=0,1,2` | `a1=4=2²`, `a3=64=8²`, `a5=4096=64²` | pass |
| A113252 odd-index squares | `n=0,1,2` | `a1=4=2²`, `a3=784=28²`, `a5=33856=184²` | pass |
| A113255 odd-index squares | `n=0,1,2` | `a1=4=2²`, `a3=5329=73²`, `a5=206116=454²` | pass |
| A1146 `divisibility_fact` | `n=2` | `a2=16`; `16⁴-1=65535=2¹⁶-1` | pass |
| A1146 universal converse | `k=0..1000` | premise holds at `k=0,16,256`; `k>1` removes `0`, and `16=a2`, `256=a3` | pass finite range |
| A115257 irreducibility pair | `n=1` | `polyP 1=1+4X`, `polyQ 1=1+2X`, both nonconstant linear polynomials over `ℚ` | pass |
| A11545 no-square conjecture | `n=0..19` | b-file begins `3,31,314,3141,...`; none of tested prefixes is square | pass |
| A11545 collision-interval conjecture | `n=0,1` | at `0`, interval is `(π,4)` and contains no integer; at `1`, numerical interval is approximately `(31.4159,31.516...)` | pass |
| A1157 distinct fractional parts | `k=2..6`, `n=1..100` pairwise | at boundary `k=2`, fractions for `n=1,2` have fractional parts `0` and `1/4`; no collision in tested grid | pass |
| A034693 `exists_k` | `n=2` | witness `k=1<2`, with `2·1+1=3` prime | pass |
| A034693 `exists_k_stronger` | `n=1` | witness `k=1`, bound `1 < 1+(fourth-root 1)^3=2`, and `2` prime | pass |
| A357513 supercongruence | `p=3,5` | at `3`, `a(p-1)=a2=81≡0 mod 3⁴`; at `5`, `a4=956875≡0 mod 5⁴` | pass |
| A056777 universal implications | first predicate members `65,209,11009` | source predicates hold; `209 mod 100=9` at the first admissible `n>65` | pass |
| A063880 structural universals | first predicate members `108,540,756` | `108` is the stated primitive term; initial decomposition/modulo checks agree | pass |
| A067720 reverse implication | `k=0,1,2,4,6,10` | `A 0` is false; for first nonexception members, `k+1=2,3,5,7,11` is prime | pass |
| A087719 `a_exists` | `n=0` | choose `m=3`: among `1..3`, two values exceed `minFac(k)^0=1` and one does not, so `2>1` | pass |
| A087719 `a_formula` | `n=1..3` | RHS values `15,27,57`, exactly the b-file/local values | pass |

### Universal-looking declarations not reduced to a finite literal boundary

The remaining declarations are not omitted; their quantifier shape prevents a decisive literal finite evaluation. They comprise answer-wrapped questions, eventual/asymptotic/filter statements, irrationality, infinitude, or an outer existential over an unknown witness. Their locally computable sequence terms are still covered by the b-file audit above.

- Answer-wrapped or unknown-minimum declarations: A100474, A100475, A100478, A102847, A103425, A107247, A108301, A108864, A109227, A109671, A109905, A113010, A113019, A113257, A113258, A113271, A113609, A114137, A114216, A116150.
- Eventual/asymptotic/infinitude declarations: A102722, A103662, A105751 (two `Tendsto` claims), A105801, A109845, A111114, A113213, A114362 `conjecture2`, A114831, A115366, A117027, A228828, A034693 `a_isBigO`/`a_unbounded`.
- Higher-order existential or analytic declarations whose boundary proposition is not decidable by literal computation: A103885, A114362 `conjecture1`, A105210's outer infinite-family conjecture, A115257 beyond the explicitly checked linear boundary.

## Complete module inventory

This is the exact 73-file PR-diff scope, included to make the all-module coverage auditable:

`100434`, `100474`, `100475`, `100478`, `100800`, `101779`, `102371`, `102722`,
`102847`, `103151`, `103425`, `103662`, `103885`, `104320`, `105020`, `105033`,
`105210`, `105565`, `105720`, `105751`, `105801`, `107247`, `108081`, `108129`,
`108211`, `108301`, `108306`, `108569`, `108864`, `108866`, `109074`, `109227`,
`109671`, `109845`, `109905`, `109908`, `109909`, `110475`, `110566`, `110835`,
`110854`, `111114`, `111291`, `112521`, `112970`, `113010`, `113019`, `113213`,
`113250`, `113252`, `113255`, `113257`, `113258`, `113271`, `113609`, `114137`,
`114216`, `114362`, `1146`, `114831`, `115257`, `115366`, `11545`, `1157`, `116150`,
`117027`, `228828`, `34693`, `357513`, `56777`, `63880`, `67720`, `87719`.

Every module was source-inspected. Every primary numeric/member prefix was reconciled as described above. Modules absent from the executable ledger have no direct finite universal boundary beyond their already checked term/member tests, or fall into one of the explicitly listed non-finite quantifier classes.

## Final disposition

- New findings: **0**.
- Known/released calibration failures independently reproduced: **A109074, A111291**.
- Known upstream failure rejected by status gate: **A100434**, closed unmerged PR #4560.
- Primary-sequence/reference-prefix transcription defects newly discovered in this wave: **0**. The A109074 local-A005156 mismatch is known and excluded.
- Surviving finite boundary instances: no failure in the displayed checks.
- Terminal handoff: no git commit, branch, tag, push, issue, PR, release, or other publication action was performed. The only in-repository file written by this lane is this report.
