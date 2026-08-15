# Erdős Problems formalization-faithfulness audit (live search 2026-08-15)

## HANDOFF STATE (agent 1 stopped mid-sweep, 2026-08-15)

**Stopped by coordinator instruction (model rotation). No new target started after `1026`.**

**Traversal:** strictly descending numeric id over
`results/expansion/open_targets_oeis_erdos_20260815.json`,
`corpus=="ErdosProblems"`, `previously_touched==false` (364 rows). The full descending
id list is written to
`/tmp/claude-1000/-Users-kuber-mehta-Projects-scratch/21f73cfa-6e97-457f-8bb8-ae31d911cc43/scratchpad/faith/ids.txt`
(line 1 = `1212`, line 364 = smallest). Ids audited = lines 1–53 of that file.

**AUDITED (53 ids, complete, all in the table below), descending:**

```
1212 1210 1209 1203 1201 1199 1192 1176 1175 1167 1150 1146 1145 1142 1139
1137 1135 1133 1119 1113 1110 1109 1108 1107 1106 1101 1095 1094 1093 1085
1084 1082 1074 1073 1068 1065 1063 1062 1061 1060 1059 1057 1056 1055 1054
1052 1049 1047 1044 1041 1038 1026 1007*
```

`1007` (*) — **IN PROGRESS / NOT AUDITED.** Its page is cached but the Lean file was
never read. Treat `1007` as the resume point.

**REACHED:** id `1026` fully audited; `1007` is the next unaudited id.

**REMAINS (311 ids):** everything from `1007` downward in `ids.txt`, i.e. lines 53–364:
`1007 1004 1003 1002 996 985 982 979 978 975 973 972 971 968 967 962 961 959 955 952
951 950 949 945 944 943 942 …` down to the smallest id. **Resume at `1007` and keep
descending** — the sibling finite-counterexample agent works the `finite_signals`
ranking, not this order, so descending traversal remains the collision-free lane.

**Pages already fetched and cached** (no re-fetch needed): the first **180** ids of
`ids.txt`, i.e. down to roughly id `700`, in
`…/scratchpad/faith/epcache/<id>.html`.

---

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
| 1082 | open (**FALSIFIABLE**) | `.parts.i` | none. `A.card / 2` is ℕ floor = `⌊n/2⌋` ✓; in the solved `.parts.ii` the `- 1` correctly removes the self-distance, since `distinctDistancesFrom pts pt = #(pts.image (dist · pt))` includes `dist a a = 0` and `a ∈ A` is assumed, so the ℕ subtraction cannot truncate | FAITHFUL | ⌊n/2⌋ bound |
| 1074 | open | `.parts.i`–`.parts.iv`, `.variants.EHSNumbers_one_half` | **`.variants.EHSNumbers_one_half : EHSNumbers.HasDensity (1/2)` truncates the site's Hardy–Subbarao quote exactly before its correction.** The full quote continues "…makes us believe that their asymptotic density exists and **is unity**. Erdős, though initially hesitant, later agreed with this view." The Lean therefore asserts, as an open conjecture, a density value the cited authors explicitly retract; no `HasDensity 1` variant exists. (Set definitions and the `S`-initial-segment test are correct — independently recomputed: first seven EHS numbers are 8, 9, 13, 14, 15, 16, 17) | MATERIAL_BUT_STILL_TRUE (mis-attributed conjecture) | density |
| 1073 | open | `erdos_1073` | `∀ x` (rather than `∀ᶠ x`) strengthens the source's asymptotic `A(x) ≤ x^{o(1)}`, but is harmless because `o` is existential and unconstrained on any finite prefix | FAITHFUL | asymptotic |
| 1068 | open | `erdos_1068` | source says "countable **subgraph**", Lean uses the **induced** subgraph `G.induce s`; equivalent because adding edges preserves infinite connectivity. `V : Type` (universe 0) rather than `Type*` | COSMETIC | cardinal |
| 1065 | open | `.parts.i`, `.parts.ii` | none | FAITHFUL | `Set.Infinite` |
| 1063 | open | `.better_upper` | headline `.better_upper` is an **editorial reformulation**: the source asks "Estimate `n_k`", the Lean asks for an `upper_bound` that is `o(k·lcm(1..k-1))`, i.e. strictly better than Cambie's bound. `n 0 = n 1 = 0` via `sInf ∅` junk (harmless under `atTop`). `.variants.small_values` independently rechecked (`n₄ = 9` because `C(8,4)=70` fails at both `8` and `6`; `n₅=12`) | MATERIAL (editorial) | `FIXED_OPTIMUM` shape |
| 1062 | open | `.parts.ii` | `-- TODO: Add erdos_1062.parts.i` — "How large can `f(n)` be?" is not formalized; `.parts.ii` bundles limit-existence with irrationality (source presumes existence). `ForkFree`, `f`, and the (fully proved) `⌈2n/3⌉` lower bound are correct | COSMETIC | irrationality of a limit |
| 1061 | open | `erdos_1061` | `S` counts **ordered** pairs — explicitly documented; changes the constant `c` by a factor 2 but not the `~ c·x` shape | FAITHFUL | asymptotic |
| 1060 | open | `.parts.i`, `.parts.ii` | none | FAITHFUL | asymptotic |
| 1059 | open | `erdos_1059` | none. `Set.range Nat.factorial` correctly yields `{1,2,6,24,…}` (`0! = 1! = 1`, and `0 ∉ range`), matching "each `k` with `1 ≤ k! < p`"; the site's second (easier) Erdős variant is not formalized | FAITHFUL | `Set.Infinite` |
| 1057 | open | `erdos_1057`, `.variants.pomerance` | none | FAITHFUL | asymptotic |
| 1056 | open | `erdos_1056`, `.variants.noll_simmons` | (a) `.variants.noll_simmons` **adds** `∀ i, Q i < p`, which is absent from the source but **necessary** — without it `Q = (p, p+1, …)` makes every `(Q i)! ≡ 0 [MOD p]` and the statement trivially true; the addition is undocumented; (b) headline docstring says "intervals `I_0,…,I_k`" (k+1) while the code builds `k` intervals from `Fin (k+1)` boundaries; `Fin (k+1)` successor cannot wrap because `i.castSucc ≤ k-1` | COSMETIC | `∃ p` + finite interval data |
| 1055 | open | `erdos_1055`, `.variants.erdos_limit`, `.variants.selfridge_limit` | **`IsOfClass 2` wrongly contains every class-1 prime**, so `Erdos1055.p 2 = 2` whereas the source's `p₂ = 13` (A005113 `2, 13, 37, 73, 1021`). Reason: for `r = 2` the "equality for at least one prime factor" clause reads `∀ m ≤ 1, IsOfClass m q → m = 1`, which is vacuous in `ℕ+`. Hand-verified: `IsOfClass 1 3` holds (`primeFactors 4 = {2} ⊆ {2,3}`), hence `IsOfClass 2 2` holds. Separately, `p` is `Nat.find (exists_p r)` where `exists_p` is itself `sorry`'d. The `p−1` variant of the question is not formalized | MATERIAL_BUT_STILL_TRUE | `Set.Infinite` / asymptotic in `r` |
| 1054 | open | `.parts.i`, `.parts.ii`, `.parts.iii` | **`.parts.i` (`f(n) = o(n)`) is recorded on the site as disproved by Tao** ("The strong claim that `f(n)=o(n)` was disproved by Tao in the comments to [468]…upper density of `{n : f(n) ≤ δn}` is `≪ δ²`") yet carries `research open` + `answer(sorry)`. Also `.parts.iii` conjoins a **vacuous** `∃ A, A.HasDensity 1` that the limsup expression never mentions (copy-paste from `.parts.ii`). Lemma `f_undefined_at_3` actually proves `f 5 = 0` (misnamed) | STATUS_SYNC + COSMETIC | asymptotic |
| 1052 | open | `erdos_1052` | none (`properUnitaryDivisors` correctly excludes `n` itself via `Ico 1 n`; `6` and `60` recheck) | FAITHFUL | `Set.Finite` |
| 1049 | open | `erdos_1049` | none | FAITHFUL | irrationality |
| 1047 | **solved (DISPROVED (LEAN))** | `.variants.max_non_convex_components` | headline correctly `research solved` + `answer(False)`; the open declaration is Goodman's follow-up (max number of non-convex components as a function of `deg f`), an `IsGreatest … answer(sorry)` fixed-optimum | FAITHFUL | `FIXED_OPTIMUM` |
| 1044 | **solved (SOLVED (LEAN))** | `.variants.fixed_degree` | headline correctly `research solved` + `answer(2)`; open declaration is Tang's fixed-degree suggestion, encoded as `IsLeast` (i.e. attained), matching "is attained by `fₙ(z) = zⁿ − 1`" | FAITHFUL | `FIXED_OPTIMUM` |
| 1041 | open (**FALSIFIABLE**) | `erdos_1041` | **degenerate case admitted**: the witness condition is `({z₁,z₂} : Multiset ℂ) ≤ f.roots`, which allows `z₁ = z₂` at a **repeated** root; the constant path then has `H¹`-measure `0 < 2` and lies in the sublevel set, making the declaration *trivially true for every `f` with a multiple root*. Also `length (Set.range γ)` measures the `H¹` trace of the path, not its parametrised arc length | MATERIAL_BUT_STILL_TRUE (`MULTI_READING`) | path in ℂ |
| 1038 | open | `.parts.i` | `(n : ℕ)` is an **unused parameter** in all four declarations; `.parts.ii` alone omits the non-constant guard `f ≠ 1` (harmless: `f = 1` contributes volume `0` and cannot raise a supremum); declaration name typo `erdos_1038.varaints.inf_lowerBound`. The "all roots real and in `[-1,1]`" encoding via `(f.roots.filter (· ∈ Icc (-1) 1)).card = f.natDegree` is correct | COSMETIC | `FIXED_OPTIMUM` |
| 1026 | **solved (SOLVED (LEAN))** | — (0 open decls) | in target list only via `answer_sorry`; site and Lean agree the van Doorn/Cambie form is settled (`c = 1`) | — | — |

---

## Severity roll-up over the 53 audited ids

| severity | count | ids |
|---|---|---|
| `FINITELY_FALSE_AS_STATED` | **0** | — |
| `MATERIAL_BUT_STILL_TRUE` | **10** | 1175, 1145, 1110, 1108, 1095, 1093, 1085, 1074, 1055, 1041 |
| `MATERIAL (editorial reformulation)` | **1** | 1063 |
| `STATUS_SYNC` | **5** | 1176, 1119 (benign), 1106, 1084, 1054 |
| `COSMETIC` | **16** | 1203, 1201, 1192, 1167, 1146, 1142, 1139, 1137, 1135, 1101, 1068, 1062, 1056, 1038, (+1106, 1084, 1054 also carry cosmetic defects) |
| `FAITHFUL` | **20** | 1212, 1210, 1209, 1199, 1150, 1133, 1113, 1109, 1107, 1082, 1073, 1065, 1061, 1060, 1059, 1057, 1052, 1049, 1047, 1044 |
| not a target (0 open decls) | 2 | 1119, 1026 |

**Certificate shape:** every one of the 53 audited declarations is
`CERTIFICATE_SHAPE_FAIL` for a finite-counterexample lane — the literal negations are
asymptotic limits/densities, `Set.Infinite`/`Set.Finite` claims, `∃`-over-infinite-object,
cardinal statements, or `answer(sorry)` fixed-optimum holes. **This is the single most
important structural fact of the sweep so far:** in the `1000+` id band, Erdős problems are
overwhelmingly number-theoretic and asymptotic, so a `FINITELY_FALSE_AS_STATED` verdict is
structurally very unlikely there. If the goal is finitely-false Lean declarations, the next
agent should expect a much higher hit rate in the **low-id graph/combinatorics band** than in
the descending sweep. Descending order was mandated for collision avoidance; note the
trade-off explicitly if the mandate is revisited.

---

## FINITELY_FALSE_AS_STATED findings

**None found in ids 1212 → 1026.** No explicit finite witness refutes any audited Lean
declaration. Every candidate divergence either (a) made the declaration *easier* rather than
false (degenerate cases admitted: 1041, 1108, 1056), or (b) landed inside a statement whose
negation needs an infinite object.

Two divergences came closest to a finite refutation and are recorded in full below (1093,
1055) — both are exact, replayable, and independently recomputed, but neither falsifies a
declaration because the declarations they sit under are `answer(sorry) ↔ …Infinite` /
`…Finite` shapes.

### Near-miss 1 — EP 1093, wrong smoothness threshold (exact, verified)

`FormalConjectures/ErdosProblems/1093.lean` defines

```lean
noncomputable def deficiency (n k : ℕ) : ℕ :=
  #{i ∈ range k | n - i ∈ smoothNumbers k}
```

Mathlib (`Mathlib/NumberTheory/SmoothNumbers.lean:274`):

```lean
def smoothNumbers (n : ℕ) : Set ℕ := {m | m ≠ 0 ∧ ∀ p ∈ primeFactorsList m, p < n}
```

i.e. prime factors **strictly less than `k`**. The source (erdosproblems.com/1093) defines
`k`-smooth as "divisible only by primes **≤ k**". The two differ exactly when `k` is prime.
Exact recomputation against the site's own catalogue of examples
(`/home/ec2-user/.venvs/wowii/bin/python`, trial division, exact):

```
   n     k   source deficiency (p<=k)   Lean deficiency (p<k)
   7     3            1                        0     <-- DIFFERS
  23     5            1                        0     <-- DIFFERS
  47    11            4                        3     <-- DIFFERS
  13,14  4            1                        1
  62     6            1                        1
  94,95 10            1                        1
  44 8 / 74 10 / 174 12 / 239 14 / 5179 27 / 8413 28 / 8414 28 / 96622 42 : 2 == 2
  46 10 / 47 10 / 241 16 / 2105 25 / 1119 27 / 6459 33                    : 3 == 3
 284    28            9                        9
```

Consequences: `C(7,3)` and `C(23,5)` — two of the seven deficiency-1 examples the site
lists — are **not** deficiency-1 under the Lean encoding, and `C(47,11)`, the unique known
deficiency-4 example, becomes deficiency-3. `erdos_1093.parts.i` ("infinitely many with
deficiency 1") and `.parts.ii` ("finitely many with deficiency > 1") are therefore about a
different function than the source's. Not finitely false (both are `Infinite`/`Finite`
claims). **Novelty: not checked against upstream issues/PRs — UNVERIFIED.**

Witness arithmetic for the smallest case (replayable by hand):
`k=3, n=7`; `i ∈ {0,1,2}` gives `n-i ∈ {7,6,5}`; `6 = 2·3` is 3-smooth for `p ≤ 3` but not
for `p < 3`; `7` and `5` are neither. Source deficiency `1`, Lean deficiency `0`.

### Near-miss 2 — EP 1055, class 2 swallows class 1 (exact, hand-verified)

`FormalConjectures/ErdosProblems/1055.lean`, `IsOfClass` step case:

```lean
(∀ r ∈ (p + 1).primeFactors, ∃ (m : ℕ+) (hm : m ≤ n), H m hm r) ∧
(∃ r ∈ (p + 1).primeFactors, ∀ (m : ℕ+) (hm : m ≤ n), H m hm r → m = n)
```

At `r = 2` we have `n = 1`, and `m : ℕ+` with `m ≤ 1` forces `m = 1`, so the second conjunct
("equality for at least one prime factor") is **vacuously true**. Then:

- `IsOfClass 1 3` holds: `primeFactors (3+1) = primeFactors 4 = {2} ⊆ {2,3}`.
- Hence for `p = 2`: `primeFactors (2+1) = {3}`, and `∃ m ≤ 1, IsOfClass m 3` holds.
- Hence **`IsOfClass 2 2` is true**, so `Erdos1055.p 2 = 2`.

The source and OEIS A005113 give `p₂ = 13` (`2, 13, 37, 73, 1021`). `13` is genuinely class 2
(`14 = 2·7`, `7+1 = 8 = 2³` so `7` is class 1; and `13` is not class 1 since `7 ∉ {2,3}`).
So the Lean `p` function does not compute A005113. Not finitely false because no upstream
declaration asserts `p 2 = 13`; the two open declarations
(`erdos_1055.variants.erdos_limit`, `.selfridge_limit`) are asymptotic in `r`.
Additional structural note: `p r := Nat.find (exists_p r)` where `exists_p` is itself a
`sorry`'d `textbook` theorem. **Novelty: UNVERIFIED.**

---

## STATUS_SYNC findings (METHOD rule 9 — reconciliation, never a discovery claim)

1. **EP 1106 `.parts.i` — solved in the literature, `research open` in Lean.**
   Declaration: `erdos_1106.parts.i : answer(sorry) ↔ Tendsto (fun n => #(∏ i ∈ Icc 1 n, p i).primeFactors) atTop atTop`.
   Site records: "Schinzel noted … that `F(n) → ∞` follows from the asymptotic formula for
   `p(n)` and a result of Tijdeman [Ti73] … details are given in a paper of Erdős and Ivić",
   and separately "Schinzel and Wirsing [ScWi87] have proved `F(n) ≫ log n`", which implies
   `F(n) → ∞` outright. The Lean file records neither Schinzel–Wirsing nor Ono as a variant.
   Expected repair: `.parts.i` → `research solved`, `answer(True)`. Only `.parts.ii`
   (`F(n) > n` eventually) is genuinely open. Site-level state stays `open` because of
   `.parts.ii`. Also a doc defect: module header link text reads `erdosproblems.com/1064`
   while the URL is `/1106`.

2. **EP 1084 `.variants.triangular_optimal_d2` — proved by Harborth, `research open` in Lean.**
   Declaration: `f 2 (3 * n ^ 2 + 3 * n + 1) = 9 * n ^ 2 + 3 * n`, tagged `research open`.
   Site records: "Harborth [Ha74b] **proved** this, and more generally
   `f₂(n) = ⌊3n − √(12n−3)⌋` for all `n ≥ 2`."
   Symbolic check that the two agree exactly (so the Lean statement is a true theorem):
   at `n ↦ 3n²+3n+1`, `3(3n²+3n+1) − √(12(3n²+3n+1)−3) = 9n²+9n+3 − √(36n²+36n+9)
   = 9n²+9n+3 − (6n+3) = 9n²+3n`, and the radicand is the exact square `(6n+3)²`, so the
   floor is exact. Expected repair: retag `research solved` and add Harborth's general
   formula as a variant. Docstring also writes `<` where both code and source have `=`.
   File additionally carries `-- TODO: Add erdos_1084.` (no headline declaration).

3. **EP 1054 `.parts.i` — disproved by Tao, `research open` in Lean.**
   Declaration: `erdos_1054.parts.i : answer(sorry) ↔ (fun n ↦ (f n : ℝ)) =o[atTop] (fun n ↦ (n : ℝ))`.
   Site records: "The strong claim that `f(n) = o(n)` was **disproved by Tao** in the comments
   to [468], in which he proves that the upper density of `{n : f(n) ≤ δn}` is `≪ δ²`."
   Expected repair: `answer(False)`, `research solved`. Note `.parts.iii` additionally
   conjoins a **vacuous** `∃ A, A.HasDensity 1` that the `limsup` expression never mentions,
   and `f_undefined_at_3` actually proves `f 5 = 0` (misnamed).

4. **EP 1176 — site status class is "NOT DISPROVABLE", Lean is plain `research open`.**
   Site tooltip: "Open in general, but there exist models of set theory where the result is
   true" (Hajnal–Komjáth consistency). The Lean docstring mentions the consistency result in
   prose but no declaration or category records the independence-flavoured status.

5. **EP 1119 — benign.** Site `solved` / "INDEPENDENT of ZFC"; Lean already `research solved`
   but with `answer(sorry)` because the answer is not expressible in Lean's fixed model. The
   Kumar–Shelah and Schilhan–Weinert results live only in a **prose comment block**, not in
   any declaration. Comparable pattern at EP 1175, where
   `.variants.shelah_consistency` is tagged `research solved` yet states a **bare ZFC
   negation** (which is only *consistent*, not a ZFC theorem) with `answer(sorry)`.

---

## Time-savers for the next agent

### erdosproblems.com fetch quirks

- **Plain `curl` gets a Cloudflare managed-challenge page** ("Just a moment…"). Adding a
  desktop browser `User-Agent` defeats it completely and returns HTTP 200 static HTML:
  ```
  curl -s --max-time 25 -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) \
    AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36" \
    https://www.erdosproblems.com/<id>
  ```
  No JS, no cookies, no browser needed. `xargs -P 5` parallel fetching worked fine; 180 pages
  pulled with zero failures and no rate limiting observed.
- The `/latex/<id>` endpoint returns the **same HTML shell**, not raw LaTeX — not worth using.
- Page structure worth parsing:
  - `<div class="problem-text" id="open|solved|…">` — the coarse state.
  - `<div id="prize">` — the **status class label** (`OPEN`, `SOLVED (LEAN)`,
    `DISPROVED (LEAN)`, `INDEPENDENT`, `NOT DISPROVABLE`, `FALSIFIABLE`, `$500`, …) plus a
    tooltip sentence. **This label is where the status-sync signal lives** — richer than the
    div id. Always read it.
  - `<div id="content">` — the canonical statement.
  - `<div class="problem-additional-text">` — the remarks. **Read the remarks in full: three
    of the five status-sync findings and the strongest MATERIAL finding (1074) came from the
    remarks, not the statement.**
  - `This page was last edited <date>` — record it as provenance.
- `teorth/erdosproblems` `data/problems.yaml` gives status coordinates but **contains no
  problem statements** — the site is the only statement source.

### Scripts written (reusable, absolute paths)

- `/tmp/claude-1000/-Users-kuber-mehta-Projects-scratch/21f73cfa-6e97-457f-8bb8-ae31d911cc43/scratchpad/faith/ep.py`
  — the workhorse. `python ep.py [--norem] <id> <id> …` prints, per id: target metadata
  (bytes / `n_answer_sorry` / `n_research_open`), site state + prize label + last-edited date,
  the canonical statement, the remarks, and the **full upstream Lean file** at the pin
  (header comment stripped). Caches pages in `./epcache/<id>.html`.
- `/tmp/claude-1000/-Users-kuber-mehta-Projects-scratch/21f73cfa-6e97-457f-8bb8-ae31d911cc43/scratchpad/faith/ids.txt`
  — the frozen descending id list (364 lines).
- `/tmp/claude-1000/-Users-kuber-mehta-Projects-scratch/21f73cfa-6e97-457f-8bb8-ae31d911cc43/scratchpad/faith/epcache/`
  — 180 cached pages.
- **Warning:** the parent scratchpad directory is **shared with the sibling agent**, which
  overwrote a file named `fetch_erdos.py` mid-run. Keep everything under the private
  `faith/` subdirectory.

### Divergence patterns: which turned out COSMETIC vs MATERIAL

**Reliably COSMETIC — do not spend time on these (each was checked and cleared at least once):**

- `Real.log 0 = 0` / `x / 0 = 0` junk at `k = 0, 1` inside an `⨆`/`limsup`/`Tendsto`
  (1203, 1139, 1137, 1201) — junk terms never move a sup that already has positive terms, and
  never move an `atTop` limit.
- **ℕ floor division against an integer-valued LHS.** EP 1094's `minFac > max (n/k) k` with
  ℕ division is *provably equivalent* to the real-quotient reading, because for `a ∈ ℤ`,
  `a > r ↔ a > ⌊r⌋`. Check the LHS type before flagging any `n / k`.
- **ℕ truncated subtraction guarded by a hypothesis** (1093 `n - i` under `2k ≤ n`; 1085
  `d/2 - 1` under `4 ≤ d`; 1063 `m - i0` under `2k ≤ m`; 1082 `… - 1` under `a ∈ A`). Always
  check whether the surrounding hypothesis makes truncation unreachable — it usually does.
- 0-indexed `Nat.nth` vs 1-indexed source sequences: the formalizers **consistently
  compensate** (1139 pairs `nth` shift with `log (k+1)`). Verify the compensation, then move on.
- Ordered vs unordered counting (1192 `Fin r → ℕ` tuples, 1061 ordered pairs) — changes a
  constant, never a `≪`/`~ c·x` shape, and 1061 documents it.
- Induced-vs-arbitrary subgraph when the property is edge-monotone (1068).
- `Type` vs `Type*` universe restrictions (1068 vs 1175/1176).

**Reliably MATERIAL — these are where the yield is:**

1. **A Mathlib definition whose convention differs from the source's.** Highest-yield pattern
   found. `Nat.smoothNumbers k` uses `p < k`, sources say `p ≤ k` (EP 1093). **Always open the
   Mathlib `def` for any imported predicate** (`smoothNumbers`, `Full`, `IsSierpinskiNumber`,
   `Composite`, `primeFactors`, `IsCarmichael`, …) rather than trusting the name.
   `Nat.Full`, `Nat.IsSierpinskiNumber`, `distinctDistancesFrom`, `Erdos246.Gamma`,
   `primeGap`, `≪` (= `Asymptotics.IsBigO atTop` on `ℕ → ℝ`) were all checked and are correct.
2. **A recursive/inductive `def` whose base case leaks into the next level** (EP 1055).
3. **Docstring quotes truncated before the source retracts them** (EP 1074: the site's quote
   continues "…density exists and **is unity**. Erdős … later agreed"; the Lean asserts
   `HasDensity (1/2)`). **Read the remark paragraph past the point the docstring stops.**
4. **`\asymp` (bounded ratio) silently rendered as `~[atTop]` (`IsEquivalent`, ratio → 1)**
   — EP 1095 `.variants.log_equivalent`. Strictly stronger than the cited claim.
5. **Dropped constants in transcribed bounds.** EP 1085 `.variants.upper_lower_d5_odd` writes
   the Erdős–Pach upper constant as `(⌊d/2⌋-1)/⌊d/2⌋` instead of `(p-1)/(2p)` — the factor `2`
   is missing from the denominator only in the upper bound; the lower bound in the same
   declaration has it. Diff the two halves of any two-sided bound against each other.
6. **`ℕ` containing `0` where the source means positive integers**, when `0` changes a
   *set* rather than a single edge case. EP 1108: `S : Finset ℕ` admits `0 ∈ S`, and since
   `0! = 1! = 1` the encoded `FactorialSums` is strictly larger — 128 extra elements below
   `10⁶`, smallest extra `4 = 0!+1!+2!`, which is itself an extra square and an extra powerful
   number, i.e. it lands directly in both open questions.
7. **Degenerate witnesses that trivialise an existential** (EP 1041: `z₁ = z₂` at a repeated
   root makes the constant path a legal witness). Conversely EP 1056 `.variants.noll_simmons`
   shows the formalizer *correctly* adding an undocumented guard (`Q i < p`) to block exactly
   this — check whether such a guard is present, absent-and-needed, or absent-and-harmless.
8. **A headline declaration that is an editorial invention.** EP 1063 `.better_upper` asks for
   a bound `o(k·lcm(1..k-1))` where the source only says "Estimate `n_k`"; EP 1085
   `.variants.upper_d3` asks a question the source never poses. Watch for
   `-- TODO: Add erdos_<id>.` markers (1085, 1084, 1095, 1062) — they mark files where the
   *actual* source question has no declaration at all and the open declarations are side
   questions.

### Cheap high-value gates that paid off

- **Database-sanity against the site's own worked examples.** EP 1094: enumerating the Lean
  predicate for `n ≤ 400` returned **exactly** the 14 pairs conjectured in [ELS88]
  (`(7,3) (13,4) (14,4) (23,5) (44,8) (46,10) (47,10) (47,11) (62,6) (74,10) (94,10) (95,10)
  (241,16) (284,28)`) — instant confirmation of faithfulness. EP 1093: the same gate is what
  *exposed* the smoothness bug. **Run this whenever the site lists explicit examples.**
- Independently recomputed and confirmed correct: EP 1074's EHS initial segment
  (first seven EHS numbers are `8, 9, 13, 14, 15, 16, 17`, via Pollard-rho factoring of
  `m!+1`), EP 1063's `n₂=4, n₃=6, n₄=9, n₅=12`, EP 1052's `6` and `60`, EP 1056's `k=2` and
  `k=3` witnesses mod 11 and 17, EP 1084's Harborth specialisation.

### Explicitly UNVERIFIED / left open

- **Novelty checks were not run for any finding.** No upstream issue/PR/`git log` search was
  performed for EP 1093, 1055, 1074, 1095, 1085, 1106, 1084, or 1054. All eight need a
  duplicate audit before they could ever be described as new.
- EP 1203: whether the source's `max_k` is genuinely over all `k` is unresolved. Under the
  literal all-`k` reading the sup appears to be bounded near `1` (primorial heuristic:
  `ω(m)·loglog m/log m → 1`), which would make `F(n) → ∞` false *in the source itself*, not
  just in Lean. **UNVERIFIED and worth a careful look** — it is the only place in the sweep
  where the printed source statement itself looked suspect.
- EP 1167: the module docstring names three original Erdős–Hajnal side conditions
  (`γ ≥ 2`, `r < ω`, `κ_α > r`) but the Lean adds only the first two. I argued the omission of
  `κ_α > r` is vacuous (for `κ_α ≤ r` the conclusion is trivially satisfiable), but this was a
  pen-and-paper argument only — **UNVERIFIED**.
- EP 1057's `IsCarmichael`, EP 1068's `InfinitelyConnected`, EP 1041's `Path`/`length`
  interaction, and EP 1085/1084's `unitDistNum` / `IsSeparated'` were **not** opened; they are
  the remaining unchecked imported definitions among audited ids.
- EP 1073 `Nat.Composite` was not opened (assumed `¬Prime ∧ 1 < n`); same for EP 1113, where
  the "none are prime" vs "composite" equivalence was argued from `k·2ⁿ+1 ≥ 3` rather than
  from the definition.
