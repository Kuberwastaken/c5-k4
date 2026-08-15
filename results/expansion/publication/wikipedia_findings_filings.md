# Wikipedia-collection findings — upstream filings, 2026-08-15

Campaign turn authorized upstream submission for the Wikipedia-collection scan
(`live-search-2026-08-15/CONFIRMED_LEDGER.md`, sections "Wikipedia collection, A–L lane"
and "M–Z lane"). This file is the preflight/postflight record required by
`UPSTREAM_PROTOCOL.md`.

## Upstream state at time of writing

| item | value |
|---|---|
| upstream `main` | `638da20efd8eeeed2993fc2550fc596dc90c1ce8` ("Mark OEIS A105565 as solved (#4958)", 2026-08-15T09:23:12Z) |
| checked live via | `gh api repos/google-deepmind/formal-conjectures/commits/main` at 22:04Z, unchanged at 22:16Z |
| relation to scan pin | **identical** — the A–L and M–Z lanes pinned `638da20e`, and main had not moved |
| c5-k4 audit SHA used in every filing | `d8a0c47da83203e1cd2c739b383f7a436435549f` (== `origin/main`) |
| c5-k4 permalinks | `wikipedia-scan-A-L.md`, `wikipedia-scan-M-Z.md`, `CONFIRMED_LEDGER.md` — all HTTP 200 |

Every declaration was re-read verbatim from `upstream/main` before writing about it.
Blob SHAs matched the scan for the two files the scan recorded them for
(`EllipticCurveRank.lean` = `63b538269af3…`, `HardyLittlewood.lean` = `1f4439a73541…`).

## Results

| # | Finding | Gate outcome | Artifact | Verification status |
|---|---|---|---|---|
| 1 | `EllipticCurveRank.…rank_height_count_asymptotic` finitely false | **clear** — `rank_height_count_asymptotic` 0 hits; `heightLE` → #252 only; `EllipticCurveRank` → #3596, #4685, PRs #4422/#4355/#3536/#252/#3125/#2601/#3532, none on this; absent from #4896/#4923/#4927; no matching issue in the 2026-08-10→15 sweep | issue [#4994](https://github.com/google-deepmind/formal-conjectures/issues/4994) + PR [#4995](https://github.com/google-deepmind/formal-conjectures/pull/4995) | witness re-derived (`heightLE H = ∅` for `H ≤ 3`, `{(±1,0)}` for `4 ≤ H ≤ 26`, 8 curves at `H = 27`); PR file elaborates clean under `lean -DwarningAsError=true` + `google.answer=postpone`; statement type-printed (`(21 : ℝ) - ↑r`, `Real.rpow`); **no `lake build`** |
| 2 | `HardyLittlewood.first_hardy_littlewood_conjecture` — `=O` for `∼`, offsets not distinct | **clear** — `first_hardy_littlewood_conjecture`/`FirstHardyLittlewoodConjectureFor`/`prime constellation`/`numResidues` 0 hits; `hardy littlewood` → #4990, #136, #104, #4724, #1248, #195, #2492, #1772, none about `=O` vs `∼`; absent from trackers | issue [#4996](https://github.com/google-deepmind/formal-conjectures/issues/4996) | constant re-computed: `m = ![0,1]` → `1.320323674` vs `2C₂ = 1.320323632…`; `m = ![0,1,1]` partials `1.4954 / 2.7485 / 4.0773 / 5.4215 / 6.7705 / 8.1224 / 9.4759` at `Q = 10…10⁷` (Q ≥ 10² match the scan; the scan's `Q = 10` value `1.628` does **not** reproduce — this record uses the recomputed `1.4954`). No PR: fixing defect 1 changes the antecedent of `not_first_and_secondHardyLittlewoodConjecture` |
| 3 | `Dickson.polignac_conjecture` not de Polignac; admits `k = 0` | **clear for this declaration** — `polignac` → #4673 (WIP, *new* consecutive-aware file) and #4684 (closed, proposed `Wikipedia/Polignac.lean`); **neither reports the defect in the existing declaration**, #4684's own table only records that the consecutive form is stronger. #4673 read in full before filing | issue [#4997](https://github.com/google-deepmind/formal-conjectures/issues/4997) | source text (Wikipedia + de Polignac 1849 "consécutifs") re-read; `k = 0` degeneracy checked by inspection; `k = 1` coincidence argument (`p+1` even) checked; cross-referenced #4673/#4684 and `TwinPrimes.twin_primes` in the issue |
| 4 | `same_parity_betrothed` omits `m ≠ n` | **clear** — `same_parity_betrothed` 0 hits; `betrothed`/`IsBetrothed` → #2243, #2246, PR #2264, none raising `m = n`; `quasiperfect` → #2239, PR #2419, #644 | issue [#4998](https://github.com/google-deepmind/formal-conjectures/issues/4998) + PR [#4999](https://github.com/google-deepmind/formal-conjectures/pull/4999) | σ-sieve to `5·10⁶` re-run: **0** `n` with `σ(n) = 2n+1`; **35** betrothed pairs `m<n`, all opposite parity. New: the repo's own `QuasiperfectNumbers.Quasiperfect` is *literally* `σ 1 n = 2*n+1`, so the loophole links two open declarations — this is stronger than the scan's framing and is in the issue. PR elaborates clean + `postpone`; **no `lake build`** |
| 5 | `SparseRuler.wichmann_conjecture` hard threshold for "sufficiently large" | **clear** — `wichmann_conjecture`/`sparse ruler` 0 relevant hits; `Wichmann`/`SparseRuler` → PR #4166 (introducing), #2486, #2520, #1226, #1885; absent from trackers | issue [#5000](https://github.com/google-deepmind/formal-conjectures/issues/5000) | A004137 marks→length correspondence re-derived and the offset **independently anchored against Wikipedia's own sentence** *"for 6 marks the upper bound is 15, but the maximal length is 13"*, which fixes 6 marks ↔ length 13 and hence 13 marks ↔ length 58. So the exceptional lengths `1, 13, 17, 23, 58` have `2, 6, 7, 8, 13` marks and `1, 5, 6, 7, 12` segments: the docstring's "13 segments" is a mark count. Wikipedia's "sufficiently large" / "no others up to length 213" sentence re-fetched verbatim on 2026-08-15. No finite certificate reachable (`C(78,13) ≈ 1.6·10¹⁴`) — stated as such in the issue |
| 6 | `UnionClosed.variants.cardinality_even_of_union_closed_tight` hypothesis stronger than "tight" | **clear** — `cardinality_even_of_union_closed_tight`/`UCC_tight` 0 hits; `UnionClosed` → #3596, #2285, PRs #3123/#2599; `union-closed` → #1255 (the earlier fix to this very declaration), #3749, others unrelated | issue [#5001](https://github.com/google-deepmind/formal-conjectures/issues/5001) | exhaustive `n ≤ 4` re-run **and extended**: families satisfying the Lean `∀ i` = 1/2/5/15, families satisfying the natural `max_i = #A/2` = 1/4/14/51, `#A` a power of 2 in **all** of both — quantifies the strictness and confirms no counterexample either way. Finiteness-forcing consequence derived. NAW Conjecture 3 **not** retrieved — said so in the issue |
| 7 | `Koethe.…matrixOver_KotherRadical` spurious `{I}`/`hI`, wrong docstring | **clear** — `matrixOver_KotherRadical`/`KotheRadical` 0 hits; `Koethe`/`Kothe` → PR #2994, #202; #3596 does not mention it | issue [#5002](https://github.com/google-deepmind/formal-conjectures/issues/5002) | declaration re-read; `I = ⊥` satisfiability (⇒ spurious, not vacuous) and `n = Empty` harmlessness re-checked by inspection; Wikipedia formulation 6 quoted. Low severity; no PR (binder removal left to maintainers, file also has the `KotherConjecture` namespace typo) |
| 8a | Rudin root cause (comment, not a new issue) | **duplicate confirmed** — #4568 (Terry-cyx, open) carries the identical `(6,120,49)` witness | [comment on #4568](https://github.com/google-deepmind/formal-conjectures/issues/4568#issuecomment-5304495794) | failure set independently reproduced **exactly**: `{6,7,9,10,11,12,15,19,20,21,22,24,25,26}` for `6 ≤ N ≤ 30` (`q ≤ 1500`, squares to `1.6·10⁷`); complement contains every `GP_k+1 ≥ 8` value `{8,13,16,23,27}`, which are also exactly the `Qmax` jump points. Second witness `(168,121)` reproduced. Super-Strong statement **re-verified live against Wikipedia** ("`N = GP_k + 1 ≥ 8`", "up to equivalence"). Full argmax table posted. Priority explicitly credited to #4568 |
| 8b | Dedekind `M_eq` hole survives | **partially claimed** — #3490 closed via #3895; residual hole untracked, absent from #4923's "Exact self-answers" | [comment on #3490](https://github.com/google-deepmind/formal-conjectures/issues/3490#issuecomment-5304498888) | re-verified on current main: `M_eq : M = answer(sorry)` (`research open`, L269) sits directly under `M_eq_kisielewiczFormula : M = kisielewiczFormula` (`research solved`, L261); #3895's diff confirmed to have *added* both `kisielewiczFormula` and `M_eq_kisielewiczFormula` while renaming `DedekindNumbers → M_eq` and leaving the hole. Original observation credited to @franzhusch |

**Nothing was dropped.** All seven findings and both comments were filed.

## Deviations from the brief, and why

1. **`3 < H` is not the minimal fix for #4994.** The brief proposed guarding `3 < H`
   (or `4 ≤ H`) and asked for that to be verified. It **fails verification**:
   `heightLE H = {(1,0), (−1,0)}` for `4 ≤ H ≤ 26` and both curves have rank 0
   (conductors 64 and 32; the latter is Fermat's non-congruence of 1), so the *filtered*
   set `{E ∈ heightLE H | r ≤ E.rank}` is still empty throughout. No fixed numeral works
   at all, because the first non-empty `H` depends on `r` — already for `r = 1` the
   minimal-conductor rank-1 curve 37a1 has reduced model `y² = x³ − 16x + 16`, naïve
   height `16384`. The filed PR therefore uses `∀ᶠ H in atTop`, matching the docstring's
   own `o(1)`, and the issue and PR both state explicitly why a numeric guard cannot
   serve.
2. **The sibling is confirmed immune.** `twentyone_le_rank_height_count_asymptotic` uses
   `≤`, so `0 ≤ positive` holds. Verified in the #252 diff (both were edited in the same
   commit) and left untouched by PR #4995.
3. **HL `Q = 10` partial product does not reproduce.** The scan reported `1.628`; an
   independent recomputation gives `1.4954` (`(1−2/3)/(2/3)³ · (1−2/5)/(4/5)³ ·
   (1−2/7)/(6/7)³`). `Q ≥ 10²` agree to 4 significant figures. The issue uses the
   recomputed table.
4. **Betrothed framing strengthened.** The scan called the `m = n` instance
   "quasiperfectness, a different open problem". The repo *already contains* that problem
   as `QuasiperfectNumbers.exists_quasiperfect` with
   `Quasiperfect n := σ 1 n = 2 * n + 1` — so the defect entangles two `research open`
   declarations, which is what the issue and PR lead with.
5. **SparseRuler docstring unit.** Confirmed: exceptions at lengths `1, 13, 17, 23, 58`
   have `2, 6, 7, 8, 13` marks and `1, 5, 6, 7, 12` segments. The docstring's "13
   segments" is a mark count. The threshold `13 < g.length` is therefore conservative,
   not tight — stated that way in the issue rather than as an error in the bound.

## Verification method for the two PRs

`lake build` was **not** run (shared checkout, `.lake` ≈ 7.2 GB, disk pressure). Each
file was elaborated read-only against the existing package oleans:

```
LEAN_PATH=<repo>/.lake/build/lib/lean:<each package>/.lake/build/lib/lean
~/.elan/bin/lean -DwarningAsError=true -Dpp.unicode.fun=true -DautoImplicit=false \
  -DrelaxedAutoImplicit=false -Dwarn.sorry=false \
  -Dlinter.style.copyright.formalConjectures=true -Dlinter.style.namespace=true \
  -Dlinter.style.openClassical=true -Dlinter.style.ams_attribute=true \
  -Dlinter.style.category_attribute=true -Dlinter.style.conditional_formal_proof=true \
  -Dlinter.style.moduleDocstring=true -Dlinter.style.latex_docstring=true <file>
```

i.e. exactly the `leanOptions` the `FormalConjectures` library declares in
`lakefile.toml`, plus `warningAsError`. Both files were also run with
`-Dgoogle.answer=postpone`. Both clean, exit 0.

**Negative controls** (linters demonstrably live in this configuration):

| control | result |
|---|---|
| `AMS 11 14` → `AMS 14 11` in `EllipticCurveRank.lean` | `error: The AMS tags should be ordered as AMS 11 14` |
| delete `@[category research open, AMS 11 14]` in `EllipticCurveRank.lean` | `Missing AMS attribute` + `Missing problem category attribute` |
| delete `@[category research open, AMS 11]` in `BetrothedNumbers.lean` | `Missing AMS attribute` + `Missing problem category attribute` |

Extra check on #4995 only: `#check` with `pp.numericTypes` prints the exponent as
`((21 : ℝ) - ↑r) / (24 : ℝ) + f H`, confirming real (not `ℕ`) subtraction and
`Real.rpow`.

**Not verified**, and said so in both PR bodies: no `lake build`, so downstream modules,
the test driver, and `decide`-based elaboration elsewhere were not exercised; CI is
authoritative. Rank facts for `y² = x³ ± x` and for 37a1 are quoted from the classical
literature and standard tables, not recomputed.

Both PRs were made in dedicated `git worktree`s off `upstream/main`, committed as
`Kuber Mehta <kuberhob@gmail.com>` with no co-author trailers, pushed to
`Kuberwastaken/formal-conjectures`, and the worktrees removed afterwards. The shared
checkout at `/Users/kuber.mehta/Projects/formal-conjectures` was used read-only (fetch,
`git show`, and the olean `LEAN_PATH`); no file in it was modified.

## Classification (METHOD_V1_6 §A6), stated in every filing

Each issue names which of the four coordinates it speaks to and asserts explicitly that
the underlying mathematics is unaffected:

| finding | (1) math status | (2) formal solution | (3) faithfulness | (4) literal content |
|---|---|---|---|---|
| #4994 EllipticCurveRank | untouched, open | none | **unfaithful** (pointwise vs asymptotic) | **false** |
| #4996 HardyLittlewood | untouched, open | none | **unfaithful** ×2 | classical theorem (distinct offsets); conditionally false (repeated offsets) |
| #4997 Polignac | untouched, open | none | **unfaithful** (consecutive dropped) | weaker open statement; `k = 0` is Euclid |
| #4998 betrothed | untouched, open | none | **unfaithful** (`m ≠ n`) | disjunction of two open problems |
| #5000 Wichmann | untouched, open | none | **unfaithful** (fixed threshold; unit error) | stronger open statement |
| #5001 UnionClosed | untouched, open | none | **unfaithful** (`∀ i` vs `max_i`) | weaker open statement |
| #5002 Koethe | untouched, open | none | **docstring** unfaithful; code faithful | correct, with two unused binders |

No finding is a counterexample to any piece of mathematics. None is eligible for the
`UPSTREAM_PROTOCOL.md` release path.

## Duplicate-gate discipline

The gate was re-run immediately before each write, not once at the start: searches on the
declaration name, the file/namespace name, and the conjecture name, over issues **and**
PRs in all states, plus a full sweep of upstream issues created `>= 2026-08-10` and PRs
created `>= 2026-08-12`, plus a full read of the three audit trackers #4896, #4923 and
#4927, plus `git log` on each target file. Timestamps of the per-filing gate runs:
22:05Z (#4994), 22:09Z (#4996), 22:10Z (#4997), 22:11Z (#4998), 22:13Z (#5000), 22:15Z
(#5001), 22:16Z (#5002). `main` was re-confirmed at `638da20e` at 22:04Z and 22:16Z.

Two findings from the same scan were **already claimed** and were not filed as issues:
Burnside (#4518 + #4519) — no artifact taken at all — and Rudin (#4568) — comment only,
with priority credited. Dedekind `M_eq` was **partially** claimed (#3490 closed via
#3895) and likewise got a comment, not an issue. That is 2 fully-claimed and 1
partially-claimed out of the 10 candidates carried into this turn, consistent with the
ledger's warning about a moving duplicate surface.
