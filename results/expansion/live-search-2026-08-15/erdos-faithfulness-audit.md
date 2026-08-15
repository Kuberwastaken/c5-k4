# Erdős Problems formalization-faithfulness audit (live search 2026-08-15)

**Angle.** Text-to-text comparison of the canonical problem statement on
`erdosproblems.com/<id>` against the exact Lean encoding in
`google-deepmind/formal-conjectures`, hunting statement/source divergences that make the
Lean declaration finitely false or materially different from what Erdős posed. This is a
*different lane* from the sibling finite-counterexample search: computation is used only to
confirm a divergence already found by reading.

**Frozen provenance**

| coordinate | value |
|---|---|
| upstream repo | `google-deepmind/formal-conjectures` |
| upstream pin | `2411d22e1bd550d050d0eac6c1fb379a76a3e7c5` (2026-08-14 19:16:38 +0000), read via `git show upstream/main:<path>` |
| canonical source | `https://www.erdosproblems.com/<id>` (live HTML, fetched 2026-08-15; page `last edited` date recorded per target) |
| canonical status data | `teorth/erdosproblems` `data/problems.yaml` @ `66dfe4860f73d94ecb1b09b99990a67272b6d16a` |
| target list | `results/expansion/open_targets_oeis_erdos_20260815.json`, `corpus=="ErdosProblems"`, `previously_touched==false` (364 rows) |
| traversal order | **descending numeric id** (collision avoidance with the sibling `finite_signals` lane) |
| compute | `/home/ec2-user/.venvs/wowii/bin/python`, exact arithmetic, 60 s cap per process |

**Severity ledger (METHOD v1.0 discipline)**

- `FAITHFUL` — no divergence beyond notation.
- `COSMETIC` — junk/edge values, index shifts, ordered-vs-unordered counting, missing
  variant clauses; the truth value of the declaration is unchanged.
- `MATERIAL_BUT_STILL_TRUE` — the encoded statement is genuinely a different statement
  (added/dropped hypothesis, different quantifier shape) but no finite object refutes it.
- `FINITELY_FALSE_AS_STATED` — an explicit finite witness refutes the literal Lean
  declaration. Requires: explicit witness, exact recomputation, upstream duplicate check.
- `STATUS_SYNC` — the four status coordinates disagree (site vs `problems.yaml` vs Lean
  `category` vs `answer(...)`). Per METHOD rule 9 this is **never** a discovery claim.
- `CERT_SHAPE` — recorded alongside severity: the declaration's literal negation has no
  finite replayable certificate (asymptotic / existential-over-infinite-object / cardinal /
  `answer(sorry)` fixed-answer), so the finite-counterexample lane is inapplicable by
  construction.

**Publication.** No upstream issue, PR, comment, or any other public write was made or is
proposed here. Everything below is an internal reading record.

---

## Verdict table

| id | site state | Lean open decls | divergence found | severity | cert. shape |
|---|---|---|---|---|---|
| 1212 | open | `erdos_1212` | none material | FAITHFUL | infinite path — no finite cert |
| 1210 | open | `erdos_1210`, `.variants.er80_correction` | none | FAITHFUL | `∃ C` global constant |
| 1209 | open | `.parts.iii.b/.c/.d` | none | FAITHFUL | infinite/`∃n` over ℕ |
| 1203 | open | `erdos_1203` | `⨆ k : ℕ` admits junk `k=0,1` (`Real.log 0 = 0`, `x/0 = 0`) and a **negative** `k=2` term; source `max_k` range unspecified | COSMETIC | asymptotic |
| 1201 | open | `erdos_1201` | `n = 0` admits `sSup ∅`-style junk (product is 0, prime-divisor set infinite ⇒ `sSup = 0`); density read as `liminf` (lower density), source says "density" | COSMETIC | density limit |
| 1199 | open | `erdos_1199` | none (pointwise `A+A` correctly includes `2a`, matching the site remark) | FAITHFUL | infinite set |
| 1192 | open | `erdos_1192` | `f_r` counts **ordered** tuples `Fin r → ℕ`; source "number of solutions" ambiguous (differs by ≤ `r!`, invisible to `≪ x`) | COSMETIC | `∃ A` infinite |
| 1176 | open (**NOT DISPROVABLE**) | `erdos_1176` | site status class is "not disprovable" (consistency proved by Hajnal–Komjáth); Lean carries plain `research open` | STATUS_SYNC | cardinal |
| 1175 | open | `erdos_1175`, `.variants.threshold_formulation` | main statement faithful; **`.variants.shelah_consistency` is tagged `research solved` but is a bare ZFC negation with `answer(sorry)`** — a consistency result stated as a ZFC theorem | MATERIAL_BUT_STILL_TRUE (metadata/statement defect) | cardinal |
| 1167 | open | `erdos_1167` + 4 `.variants` | Lean **adds** `2 ≤ γ` (documented, and `unrestricted_is_false` proves it necessary) but **omits** the source-list condition `κ_α > r`, which its own module docstring names | COSMETIC (omission is vacuous: `κ_α ≤ r` makes the conclusion trivially satisfiable) | cardinal |
| 1150 | open | `erdos_1150` | none | FAITHFUL | `∃ c` global constant |
| 1146 | open | `erdos_1146` | Lean uses `(A ∪ {0}) + (B ∪ {0})` where the source writes `A+B`; **documented** in the def docstring as the Schnirelmann convention. Site itself has a variable-name clash (`B` is both the bound variable and the candidate set); Lean resolves it correctly | COSMETIC | Schnirelmann density |
| 1145 | open | `erdos_1145` | source demands `1 ≤ a_1`, `1 ≤ b_1`; Lean drops positivity and **explicitly** formalizes the `0 ∈ A` reading (documented ambiguity, live discussion on the site) | MATERIAL_BUT_STILL_TRUE (declared `MULTI_READING`) | limsup |
| 1142 | open | `erdos_1142` | Lean formalizes only the "infinitely many" half; the site's second question ("or any `n > 105`") has no declaration. `2 < n` guard added per OEIS A039669 convention (documented) | COSMETIC | `Set.Infinite` |
| 1139 | open | `erdos_1139` | `Ω` (with multiplicity) chosen for "at most 2 prime factors" (source ambiguous vs `ω`); 0-indexed `Nat.nth` shift is **correctly** compensated by `log (k+1)`; `k=0` gives `log 1 = 0 ⇒ x/0 = 0` junk | COSMETIC | limsup |
| 1137 | open | `erdos_1137` | `primeGap (n-1)` uses **ℕ truncated subtraction** (`n=0 ↦ primeGap 0`); `primeGap` is 0-indexed so the encoded ratio is `max d_{n+1}d_n / (max d_{n+1})²`, a uniform index shift; `x=0` gives `⊥/⊥ = 0/0 = 0` | COSMETIC | limit |
| 1135 | open | `erdos_1135` | source uses the **accelerated** map `n/2 | (3n+1)/2` and demands `k ≥ 1`; Lean redirects to `CollatzConjecture.collatz_conjecture`, the standard `3n+1` map with `∃ m` (`m = 0` admitted) | COSMETIC (classically equivalent; `m=0` only affects `n=1`, which also has `m≥1` solutions) | Collatz |
| 1133 | open | `erdos_1133` | none | FAITHFUL | asymptotic |
| 1119 | **solved (INDEPENDENT)** | — (0 open decls) | Lean already `research solved`; but the headline carries `answer(sorry)` because the true answer is "independent of ZFC" and is not expressible; the two independence results live only in a **prose comment block**, not in any declaration | STATUS_SYNC (benign) | independence |
| 1113 | open | `erdos_1113`, `.variants.filaseta_finch_kozek` | `Nat.IsSierpinskiNumber` = `¬2∣k ∧ ∀n, Composite (k·2ⁿ+1)`; source says "positive odd", and positivity is *recovered* because `2 ∣ 0`. "None are prime" vs "composite" agree since `k·2ⁿ+1 ≥ 3` | FAITHFUL | `∃ k` + `¬∃` finite cover |
| 1110 | open | `erdos_1110` | "infinitely many **coprime** non-representable numbers" read as `Nat.Coprime n (p*q)` (the alternative reading is *pairwise* coprime); the source's first question (density of non-representables) is **not formalized at all** | MATERIAL_BUT_STILL_TRUE (declared `MULTI_READING`) | `Set.Infinite` |
| 1109 | open | `erdos_1109`, `.variants.polylog` | none; `≪` resolves to `Asymptotics.IsBigO atTop` for `ℕ → ℝ`, so `f(N) ≤ N^{o(1)}` ⇔ `∀ε>0, f ≪ N^ε` is correct | FAITHFUL | asymptotic |
| 1108 | open | `.parts.i`, `.parts.ii` | `FactorialSums = {∑_{n∈S} n! : S : Finset ℕ}` admits `0 ∈ S`, so `0! = 1! = 1` can both be used; the encoded set is **strictly larger** than the `S ⊆ {1,2,…}` reading (128 extra elements ≤ 10⁶; smallest extra `4 = 0!+1!+2!`, which is also an extra square and an extra powerful number) | MATERIAL_BUT_STILL_TRUE (`MULTI_READING`) | `Set.Finite` |
| 1107 | open | `erdos_1107` | none. `Nat.Full r x = ∀ p ∈ x.primeFactors, p^r ∣ x` matches "for every prime p ∣ n, p^r ∣ n"; `List ℕ` correctly allows repeats and `0`/`1` padding, both of which are `r`-full under the source definition too | FAITHFUL | `∀ᶠ n` |
| 1106 | open | `.parts.i`, `.parts.ii` | **`.parts.i` (`F(n) → ∞`) is recorded on the site as already known** (Schinzel via Tijdeman; Erdős–Ivić write-up; and Schinzel–Wirsing's `F(n) ≫ log n` implies it outright) yet carries `research open` + `answer(sorry)`. No variant records Schinzel–Wirsing or Ono. Module header link text says `erdosproblems.com/1064` while the URL is `/1106` | STATUS_SYNC + COSMETIC (doc) | asymptotic |
| 1101 | open | `.parts.i`, `.parts.ii` | `IsGood` bundles the standing hypotheses (StrictMono / pairwise coprime / summable) into the "good" predicate, which the source keeps separate; `t u x` uses `sSup ∅ = 0` junk at `x = 0`; `u₀ = 1` is not excluded by hypothesis but is neutralised because `∏' (1 - 1/uᵢ) = 0` and `0⁻¹ = 0` | COSMETIC | asymptotic |
| 1095 | open | `.variants.upper_conjecture`, `.lower_conjecture`, `.log_equivalent` | (a) file carries `-- TODO: Add erdos_1095.` — **no headline declaration** for the problem; (b) **`.variants.log_equivalent` encodes the source's `\asymp` (bounded ratio) as `~[atTop]` = `Asymptotics.IsEquivalent` (ratio → 1)** — a strictly stronger claim than the cited heuristic | MATERIAL_BUT_STILL_TRUE (strengthened) | asymptotic |
| 1094 | open | `erdos_1094` | `n / k` is ℕ floor division where the source means the real quotient — **provably harmless** here because `minFac` is an integer (`a > r ↔ a > ⌊r⌋` for `a ∈ ℤ`); `0 < k` correctly added (without it every `(n,0)` is an exception and the statement is false). Exact recheck: the Lean predicate's exception set for `n ≤ 400` is **exactly** the 14 pairs conjectured in [ELS88] | FAITHFUL (database-gate passed) | `Set.Finite` |
| 1093 | open | `.parts.i`, `.parts.ii` | **`Nat.smoothNumbers k` is defined in Mathlib with prime factors `< k`, but the source defines `k`-smooth as prime factors `≤ k`.** The two differ exactly when `k` is prime, which happens for infinitely many of the relevant pairs. Verified against the site's own catalogue: `C(7,3)` and `C(23,5)` drop from deficiency **1 → 0**, and `C(47,11)` (the unique known deficiency-4 example) drops from **4 → 3** | MATERIAL_BUT_STILL_TRUE | `Infinite` / `Finite` |
| 1085 | open | `.variants.upper_d3` | (a) `-- TODO: Add erdos_1085.` — no headline declaration, and `.variants.upper_d3` asks a question **not posed in the source** (is `n^{4/3}\log\log n` also an upper bound for `d=3`?); (b) **`.variants.upper_lower_d5_odd` writes the upper constant as `(⌊d/2⌋-1)/⌊d/2⌋` instead of the source's `(p-1)/(2p)` — the factor `2` is missing from the denominator**, weakening Erdős–Pach by a factor of two; its docstring also writes the lower bound with `−c₁n^{4/3}` while the code (correctly, per the source) uses `+c₁n^{4/3}`; `c₂ > 0` is dropped | MATERIAL_BUT_STILL_TRUE (transcription) | asymptotic |
| 1084 | open | `.variants.triangular_optimal_d2` | **`f₂(3n²+3n+1) = 9n²+3n` is tagged `research open` although the site records it as proved by Harborth [Ha74b]**, whose general formula `f₂(n) = ⌊3n − √(12n−3)⌋` specialises to exactly `9n²+3n` at `n ↦ 3n²+3n+1` (checked symbolically). Harborth's general formula has no declaration. Docstring writes `<` where code and source have `=`. `-- TODO: Add erdos_1084.` — no headline declaration. `.variants.upper_lower_d3` drops `c₁ > 0` | STATUS_SYNC + COSMETIC | fixed formula |
