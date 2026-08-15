# Adversarial verification of five predecessor candidates

**Lane:** verification-only. No upstream issue, PR, comment, tag, release, or commit
was created. Nothing here is authorized for publication.

**Date:** 2026-08-15 UTC
**Upstream pin:** `google-deepmind/formal-conjectures` @ `2411d22e1bd550d050d0eac6c1fb379a76a3e7c5`
(`git rev-parse upstream/main` in `/Users/kuber.mehta/Projects/formal-conjectures`).
All Lean text below is read from that commit, not from the working tree.
**Python:** `/home/ec2-user/.venvs/wowii/bin/python`, all computations under a 60 s cap.
**Sources:** erdosproblems.com pages re-fetched live 2026-08-15 into
`…/scratchpad/verify/live_<id>.html` (A2 pre-flight item 3: source reachable now);
OEIS entries fetched live.

**Method reference:** METHOD.md Phase 0A/0B/7, METHOD_V1_6.md §A2 (pre-flight),
§A6 (four-coordinate status). Every verdict below states which of the four
coordinates it is about.

---

## Candidate 1 — Erdős 1084 `erdos_1084.variants.triangular_optimal_d2`

### Claim under test

Predecessor summary handed to this lane: "**FINITELY FALSE AS STATED** — the Lean
docstring/statement uses `f₂(3n²+3n+1) < 9n²+3n` where the source says `=`; the
triangular lattice attains the bound, so `<` fails at `n = 1`. ALSO a status-sync
(declared `research open` though Harborth (1974) proved the `=` version)."

### (a) Primary re-derivation

**Actual Lean declaration at the pin** (`FormalConjectures/ErdosProblems/1084.lean`,
`variable {n : ℕ}` at namespace scope, so `n` is auto-bound universally):

```lean
/-- Erdős conjectured that the triangular lattice is best possible in 2D, in particular that
$f_2(3n^2 + 3n + 1) < 9n^2 + 3n$.

Note: in [Er75f] is read $9n^2 + 6n$, but this seems to be a typo.
-/
@[category research open, AMS 52]
theorem erdos_1084.variants.triangular_optimal_d2 : f 2 (3 * n ^ 2 + 3 * n + 1) = 9 * n ^ 2 + 3 * n := by
  sorry
```

**The statement uses `=`. Only the docstring uses `<`.** The strict form is *narrated*,
never *declared*. This is the decisive fact and it contradicts the "finitely false as
stated" headline. (The predecessor's own long-form report, `erdos-hunt.md` D8, says the
same thing — "The Lean *statement* uses `=` and is the correct reading, so the defect is
confined to the docstring." The escalated headline handed to this lane is stronger than
the evidence behind it.)

**Definitional audit of `f` (not trusted from the predecessor):**

- `FormalConjectures/ErdosProblems/1084.lean:42`
  `noncomputable def f (d n : ℕ) : ℕ := ⨆ (s : Finset (ℝ^ d)) (_ : s.card = n) (_ : IsSeparated' 1 (s : Set (ℝ^ d))), unitDistNum s`
- `FormalConjecturesForMathlib/Topology/MetricSpace/MetricSeparated.lean:38`
  `def IsSeparated' (ε : ℝ≥0∞) (s : Set X) : Prop := s.Pairwise (ε ≤ edist · ·)` —
  **non-strict** `1 ≤ dist`, matching the source's "all of distance at least 1 apart".
  (Upstream PR #2039 "`le` not `lt` in `IsSeparated`" already fixed this direction.)
- `FormalConjecturesForMathlib/Geometry/Metric.lean:29`
  `noncomputable def unitDistNum (s : Finset X) : ℕ := #{p ∈ s.sym2 | dist p.out.1 p.out.2 = 1}` —
  unordered pairs at distance exactly 1; the `Sym2` diagonal contributes 0.

So `f 2 N` is a faithful encoding of the source's `f_2(N)`, and the `⨆` in `ℕ` is a
genuine maximum here because the family is nonempty and bounded above by `N(N−1)/2`.

**Source (erdosproblems.com/1084, live 2026-08-15, page state `open`):**

> In [Er75f] he speculated that the triangular lattice is exactly the best possible, and
> in particular \[f_2(3n^2+3n+1)=9n^2+3n.\] Harborth [Ha74b] proved this, and more
> generally \[f_2(n)=\lfloor 3n-\sqrt{12n-3}\rfloor\] for all $n\geq 2$.

Source has `=`, and records it as **proved**.

### (b) Independent exact computation

`…/scratchpad/verify/v1084.py`, own code path, integer arithmetic only. Triangular
lattice in axial coordinates: point `(i,j) ↦ i·(1,0) + j·(1/2,√3/2)`, so the squared
distance between `(i₁,j₁)` and `(i₂,j₂)` is the **integer** `di² + di·dj + dj²`. The
centered-hexagonal patch of radius `n` is `{(i,j) : |i| ≤ n, |j| ≤ n, |i+j| ≤ n}`.

| n | N = 3n²+3n+1 | #points | min squared distance | unit pairs | 9n²+3n | ⌊3N−√(12N−3)⌋ |
|---|---|---|---|---|---|---|
| 0 | 1 | 1 | — | 0 | 0 | 0 |
| 1 | 7 | 7 | 1 | **12** | **12** | 12 |
| 2 | 19 | 19 | 1 | **42** | **42** | 42 |
| 3 | 37 | 37 | 1 | **90** | **90** | 90 |
| 4 | 61 | 61 | 1 | **156** | **156** | 156 |
| 5 | 91 | 91 | 1 | **240** | **240** | 240 |

min squared distance 1 ⇒ the patch is 1-separated ⇒ it is admissible, so
`f₂(3n²+3n+1) ≥ 9n²+3n` for every `n ≥ 1`, hence **the docstring's strict `<` is false
for every `n ≥ 1`** (`n = 1`: 7 points, 12 unit pairs, `9·1+3·1 = 12`). Confirmed.

Harborth's closed form at the relevant arguments, exactly: `12N − 3 = 36n²+36n+9 = (6n+3)²`
is a perfect square (column 7 above computed as `3N − ⌈√(12N−3)⌉` with exact `isqrt`), so
`⌊3N − √(12N−3)⌋ = (9n²+9n+3) − (6n+3) = 9n²+3n`. Exact for all `n` tested, and
symbolically for all `n`. The `n = 0` edge case (`N = 1`, outside Harborth's `n ≥ 2`) is
`f₂(1) = 0 = 9·0+3·0`. ✓

**Therefore the declared `=` statement is a true theorem (Harborth 1974), not a
counterexample target.**

### (c) METHOD §A6 classification

One sentence: this is a claim about coordinates **(3) faithfulness of the docstring** and
**(2)/(1) status metadata** only — the literal declaration (coordinate 4) is *true*, and
the underlying mathematics is *settled in the affirmative* by Harborth, so there is no
counterexample of any kind here.

### (d) Duplicate / novelty search performed

- `gh api search/issues repo:google-deepmind/formal-conjectures` with queries
  `1084` (12 hits), `Harborth` (1 hit, unrelated issue #104 "Easy formalization targets"),
  `triangular_optimal_d2` (**0 hits**), `erdos_1084` (2 hits, both closed `upper_d1`
  proof PRs). GitHub's `search/issues` covers issues **and** PRs in all states.
- Read closed issue **#2318** "Erdős Problem 1084: status mismatch (repo=solved,
  erdosproblems.com=open)" — an automated *file-level* status bot report, the opposite
  direction, closed by PR #2325; it does not mention Harborth or the
  `triangular_optimal_d2` declaration.
- `git log`/`git blame` of `FormalConjectures/ErdosProblems/1084.lean`: 8 commits.
  The `<`-vs-`=` docstring divergence is present from the original PR #1423 (2025-12-31)
  and untouched by every later commit, including the status sweep #2325 (Daniel Chin,
  2026-02-20) which renamed the declaration and explicitly said 1084 is one of the
  "Estimate f(n)" problems with no agreed formalization standard.
- Local `c5-k4`: `git tag` (11 tags, none Erdős-1084), `gh release list -R
  Kuberwastaken/c5-k4` (11 releases, none Erdős), `git log --all --oneline | grep -i
  '1084|harborth'` → no hits.
- SearXNG (`http://127.0.0.1:8899`): `formal-conjectures erdos_1084 triangular_optimal_d2`,
  `formal-conjectures 1084 Harborth research open`,
  `erdos 1084 Harborth f_2(3n^2+3n+1) formalization` → no prior art; only the upstream
  doc page and the erdosproblems entry itself.

### (e) Verdict

**REFUTED** as handed over. The declaration does **not** assert the strict inequality;
`<` appears only in the docstring, and the declared `=` form is exactly Harborth's
theorem, verified independently above. There is no finite counterexample and nothing
publishable as a counterexample.

**Residual, DOWNGRADED to `STATUS_SYNC` + `COSMETIC`** (METHOD outcome `STATUS_SYNC`):
(i) `@[category research open]` on a statement the canonical source records as proved by
Harborth [Ha74b] — expected repair `research solved`, plus adding the general formula
`f₂(n) = ⌊3n−√(12n−3)⌋` as a variant; (ii) docstring transcription error `<` for `=`.
Both are metadata/prose defects, unclaimed upstream, and would at most support a
courtesy upstream *issue* — never a release. Not authorized here.

---

## Candidate 2 — OEIS A237271 `OeisA237271.observation_carmichael`

### Claim under test

"Novel: the hypothesis quantifies `∀ a : ZMod k, a ≠ 0 → a^(k-1) = 1` instead of over
units coprime to `k`, making it unsatisfiable for composite `k`, so the open declaration
is vacuously true."

### (a) Primary re-derivation

**Actual Lean declaration at the pin** (`FormalConjectures/OEIS/237271.lean`, verbatim):

```lean
/--
Observation: "a(A002997(n)) >= 3, at least for 1 <= n <= 10000."
- _Omar E. Pol_, Oct 21 2025

That is, $a(k) \ge 3$ for every Carmichael number $k$.
A002997 is the sequence of Carmichael numbers.
-/
@[category research open, AMS 11]
theorem observation_carmichael (k : ℕ)
    (hk : ¬ k.Prime ∧ 1 < k ∧ ∀ a : ZMod k, a ≠ 0 → a ^ (k - 1) = 1) :
    3 ≤ a k := by
  sorry
```

Transcription confirmed character-for-character against the pinned blob.

**Sources (live 2026-08-15):**

- A237271 (`%I #308 Aug 13 2026`), `%C` line by _Omar E. Pol_, Oct 21 2025:
  "Observation : a(A002997(n)) >= 3, at least for 1 <= n <= 10000."
- A002997 `%N`: "Carmichael numbers: **composite** numbers `k` such that `a^(k-1) == 1
  (mod k)` for every `a` **coprime to `k`**."

So the source condition is over `a` **coprime to** `k` (i.e. over `(ZMod k)ˣ`); the Lean
condition is over **every nonzero** `a : ZMod k`. Divergence confirmed from the primary
source, not from the predecessor's paraphrase.

### (b) Independent computation and the general proof

**General argument (mine, complete, no computation needed).**
Let `k` satisfy the hypothesis. `1 < k` and `¬ k.Prime` make `k` composite, so `k` has a
prime divisor `p` with `1 < p < k` (write `k = p·m`, `m > 1`, hence `p = k/m < k`).
Then `(p : ZMod k) ≠ 0` because `0 < p < k`. Since `k ≥ 2`, `k − 1 ≥ 1`, so the
hypothesis gives `p^(k−1) = 1`, i.e. `p · p^(k−2) = 1`, so `(p : ZMod k)` is a unit.
But the units of `ZMod k` are exactly the residues coprime to `k`, and `gcd(p, k) = p > 1`.
Contradiction. **Hence no `k` satisfies `hk`: the hypothesis set is empty and the
declaration is vacuously true** (provable by `exact absurd … `, no mathematics used).
`k = 0` and `k = 1` are already excluded by `1 < k`.

**Independent computation** (`…/scratchpad/verify/v237271.py`, own code path: trial-division
divisors, own `isprime`, `pow(x, k-1, k)`; 60 s cap, ran in ~25 s):

```
a matches OEIS DATA n=1..90:                                    True
k in 2..20000 satisfying FULL Lean hypothesis:                  NONE
composite k in 4..4999 with least prime factor p, p^(k-1)=1 mod k:  0
Carmichael numbers <= 20000: [561, 1105, 1729, 2465, 2821, 6601, 8911, 10585, 15841]
a(k) on them:                [  5,    6,    4,    6,    6,    6,    7,     7,     8]  min = 4
```

Explicit premise-falsifying witnesses (METHOD Phase 0B item 6 — replayable witness, not a
scalar flag): `(561, 3) ↦ 375`, `(1105, 5) ↦ 885`, `(1729, 7) ↦ 742`, `(2465, 5) ↦ 1480`,
`(2821, 7) ↦ 2016`; each `a ≠ 0` in `ZMod k` and `a^(k−1) ≠ 1`.

Also confirmed independently: the Lean `a` reproduces OEIS A237271's `%S/%T/%U` DATA
exactly for `n = 1..90` (the predecessor only checked `n = 1..50`), so the *sequence*
encoding is faithful; the defect is entirely in the Carmichael hypothesis. And the
*intended* observation is not refuted: `min a(k) = 4 ≥ 3` over all Carmichael `k ≤ 20000`.

### (c) METHOD §A6 classification

One sentence: this is a claim about coordinate **(4) what the declaration literally
asserts** (a vacuous implication) and coordinate **(3) faithfulness to its cited source**;
coordinate (1), the underlying OEIS observation, is untouched and in fact holds on every
Carmichael number `≤ 20000`.

Note the direction: the literal declaration is **trivially true**, not finitely false. So
this is *not* a counterexample and cannot become a counterexample release under
METHOD Phase 8 / UPSTREAM_PROTOCOL. It is a statement defect with an exact proof.
METHOD ledger label: `PREMISE_FALSE_STRICT` generalized to an empty applicable domain
(no admissible instance exists at all).

### (d) Duplicate / novelty search performed

Upstream (`gh api search/issues`, which covers issues **and** PRs in every state):
`A237271` (1 hit: merged PR #4924, about `conjecture_4`/`conjecture_5` parity only),
`237271` (0), `observation_carmichael` (**0**), `Carmichael in:title` (3 hits: PR #4281
`NumberTheory/Carmichael` import fix, issue #1784 / PR #1836 Carmichael *totient*
conjecture — all unrelated), `A002997` (0), `Carmichael symmetric representation` (0),
`ZMod coprime unit hypothesis vacuous` (0), `unsatisfiable hypothesis` (1, unrelated),
`vacuous hypothesis` (17, inspected), `is:pr 237271 in:title,body` (0).

Read in full the three live audit trackers and confirmed A237271 appears in **none** of
them: **#4896** "Tracking: possible misformalizations found in statement audits" (open;
has a "Boundary cases / vacuous wrappers" section listing Erdős 940/694/939, Green 21 —
not A237271), **#4923** "Possible misformalizations II" (open; self-answers, reflexive
asymptotics, OEIS A211417 degenerate witness — not A237271), **#4927** "Open statements
with known solutions" (open; A287616, Green 3/31, OQP 35, Independent Domination, MO
31809, Green 19, Erdős 272 — not A237271).

`git log` / `git blame` of `FormalConjectures/OEIS/237271.lean`: only two commits —
`d16e05ad` "feat(OEIS): add solutions from AlphaProof Nexus (#4384)" (Moritz Firsching,
**2026-08-12**, which introduced `observation_carmichael` unchanged to this day) and
`6ae3deba` (#4924, parity only). The declaration is three days old at the pin.

Local `c5-k4`: `git tag` (11), `gh release list -R Kuberwastaken/c5-k4` (11),
`git log --all --oneline | grep -iE '237271|carmichael'` → no hits.

SearXNG: `formal-conjectures observation_carmichael`, `"observation_carmichael"`,
`formal-conjectures A237271 Carmichael vacuous hypothesis`,
`formal-conjectures ZMod a^(k-1)=1 nonzero coprime misformalization` → no prior art.

### (e) Verdict

**CONFIRMED_PUBLISHABLE — as a formalization-defect report only, explicitly NOT as a
counterexample.** The divergence from A002997 is real and read from the primary source;
the vacuity is *proved*, not merely searched (the `k ≤ 20000` sweep is corroboration);
the declaration is genuinely `research open` while being trivially provable; and no
upstream issue, PR, commit, blame line, tracker entry, local tag/release/commit, or web
result claims it.

Caveats that must survive into any write-up: (i) the underlying OEIS observation is
untouched and holds on every Carmichael number `≤ 20000` (min `a(k) = 4`); (ii) a vacuous
universal cannot be "refuted", so no release tag and no counterexample language —
the correct artifact is an upstream issue in the style of #4896/#4923, or a local note;
(iii) the declaration is 3 days old, so the duplicate surface must be re-checked
immediately before any write (METHOD_V1_6 §A2.1). **No action taken; publication requires
explicit user authorization.**

---

## Candidate 3 — Erdős 1093 `Erdos1093.deficiency` (`erdos_1093.parts.i` / `.parts.ii`)

### Claim under test

"Mathlib `Nat.smoothNumbers k` means prime factors `< k` but the source says `≤ k`;
this misclassifies the source's own catalogue (C(7,3), C(23,5) deficiency 1→0;
C(47,11), the unique known deficiency-4 example, 4→3)."

### (a) Primary re-derivation

**Actual Lean at the pin** (`FormalConjectures/ErdosProblems/1093.lean`):

```lean
noncomputable def deficiency (n k : ℕ) : ℕ :=
  #{i ∈ range k | n - i ∈ smoothNumbers k}

@[category research open, AMS 5]
theorem erdos_1093.parts.i :
    answer(sorry) ↔ {x : ℕ × ℕ | let k := x.1; let n := x.2; 2 * k ≤ n ∧ deficiency n k = 1 ∧
      ∀ p, p.Prime → (p ∣ choose n k) → k < p}.Infinite

@[category research open, AMS 5]
theorem erdos_1093.parts.ii :
    {x : ℕ × ℕ | let k := x.1; let n := x.2; 2 * k ≤ n ∧ deficiency n k > 1 ∧
      ∀ p, p.Prime → (p ∣ choose n k) → k < p}.Finite
```

**Mathlib at the pinned toolchain** (`lake-manifest.json`: mathlib
`a3a10db0e9d66acbebf76c5e6a135066525ac900`, `v4.27.0`;
`Mathlib/NumberTheory/SmoothNumbers.lean:272-274`):

```lean
/-- `smoothNumbers n` is the set of *`n`-smooth positive natural numbers*, i.e., the
positive natural numbers all of whose prime factors are less than `n`. -/
def smoothNumbers (n : ℕ) : Set ℕ := {m | m ≠ 0 ∧ ∀ p ∈ primeFactorsList m, p < n}
```

**Source (erdosproblems.com/1093, live 2026-08-15, state `open`):**

> Otherwise, the deficiency is the number of `0 ≤ i < k` such that `n−i` is `k`-smooth,
> that is, divisible only by primes **`≤ k`**.

Divergence confirmed from both primaries: `p < k` (Lean) vs `p ≤ k` (source). The two
predicates differ on `m` exactly when `k ∣ m` with `k` prime; machine-checked over
`k < 60`, `m < 4000`: **0** cases where they differ with `k` composite.

Note that the *other* side condition is faithful: the source's "undefined if a prime
`p ≤ k` divides `C(n,k)`" is encoded as `∀ p, p.Prime → p ∣ choose n k → k < p`. Only the
smoothness threshold inside `deficiency` is wrong.

### (b) Independent recomputation (own code path)

`…/scratchpad/verify/v1093.py` — own trial-division factoriser, `math.comb`, exact
integers, ran in <2 s. I recomputed the deficiency of **every one of the 23 examples the
source page lists**, under both thresholds, and also re-checked eligibility (`2k ≤ n` and
no prime `≤ k` dividing `C(n,k)`) for each.

- Under the **source** threshold `p ≤ k`, my values reproduce the site's stated
  deficiencies for **all 23/23** catalogue entries (7 with deficiency 1, 8 with 2, 6
  with 3, 1 with 4, 1 with 9). This is the control that fixes the correct reading.
- Under the **Mathlib** threshold `p < k`, exactly **three** entries change, all with
  `k` prime:

| example | k | k prime | site / source `p ≤ k` | Lean `p < k` | separating value `n−i` |
|---|---|---|---|---|---|
| `C(7,3)` | 3 | yes | **1** | **0** | `6 = 2·3` |
| `C(23,5)` | 5 | yes | **1** | **0** | `20 = 2²·5` |
| `C(47,11)` | 11 | yes | **4** | **3** | `44 = 2²·11` |

All other 20 entries (k = 4,4,6,10,10,8,10,12,14,27,28,28,42,10,10,16,25,27,33,28) are
composite `k` and agree. Consequence, exactly as claimed: two of the seven listed
deficiency-1 examples leave the deficiency-1 set under the Lean encoding, and `C(47,11)`
— the **unique known deficiency-4 example** — is a deficiency-3 example under it.
Predecessor's numbers reproduced independently.

### (c) METHOD §A6 classification

One sentence: this is a claim about coordinate **(3) faithfulness of the declaration to
its cited source** — `deficiency` computes a different function from the one
erdosproblems.com defines, so `parts.i`/`parts.ii` are open questions about a different
object — and it says nothing about coordinate (1), the underlying Erdős–Lacampagne–
Selfridge question, which remains open either way.

**Not a counterexample and not finitely refutable**: `parts.i` is an `answer(sorry) ↔
Set.Infinite` placeholder and `parts.ii` is a `Set.Finite` claim; neither has a finite
negation certificate (METHOD Phase 0A: `answer_placeholder` / infinite-cardinality).

### (d) Duplicate / novelty search performed

Upstream (`gh api search/issues`, issues **and** PRs, all states): `smoothNumbers`
(2 hits: PR #1668 GreensOpenProblems 59, PR #1328 the 1093 PR itself), `1093` (8 hits),
`erdos_1093` (5 hits), `deficiency binomial` (2 hits), `smooth` (37 hits, scanned).
**None** raises the `< k` vs `≤ k` threshold.

`git log`/`git blame` of `FormalConjectures/ErdosProblems/1093.lean`: 4 commits —
`4f97b303` (#1328, Pawan Parida, 2025-12-12, introduced `deficiency` in its current
form), `a22f98ab` (#1489 `answer(sorry) ↔`), `3eac3cf9` (#1532 `k < n` → `2 * k ≤ n`),
`c252a410` (util split).

**Provenance of the defect, recovered from the PR itself** (this is new, and is the
strongest novelty evidence): PR #1328's *first* commit
`3e5947996eff655f7ccb4861aac119a014e84ebb` defined the predicate correctly by hand —

```lean
/-- A number $n$ is $k$-smooth if all its prime factors are $\le k$. -/
def IsKSmooth (k n : ℕ) : Prop := ∀ p, p.Prime → p ∣ n → p ≤ k
```

— and an inline review suggestion (YaelDillies, on `1093.lean:51`) replaced it with
`#{i ∈ .range k | n - i ∈ smoothNumbers k}`, later followed by "Did you not find
[Mathlib/NumberTheory/SmoothNumbers.lean#L275-L277]? Can you try using it?". The author
complied ("Updated to use Mathlib.NumberTheory.SmoothNumbers now"). The `≤ k` → `< k`
change was never discussed in the PR thread, the review comments, or the two later fix
PRs (#1489, #1532), one of which was itself a faithfulness fix to the same file. So the
defect is documented as introduced-by-refactor and unnoticed since 2025-12-12.

Local `c5-k4`: `git log --all --oneline | grep -iE '1093|smooth'` → no hits;
`git tag` / `gh release list` → none; the only files mentioning 1093 are this campaign's
own `erdos-hunt.md` / `erdos-faithfulness-audit.md`.

SearXNG: `formal-conjectures erdos 1093 smoothNumbers deficiency`,
`Mathlib smoothNumbers prime factors less than n convention k-smooth`,
`formal-conjectures 1093 deficiency binomial coefficient misformalization` → no prior art.

### (e) Verdict

**CONFIRMED_PUBLISHABLE — as a formalization-faithfulness defect report only, NOT as a
counterexample.** Every element is independently verified: the two primary definitions,
the exact 23-entry catalogue recomputation under both thresholds (23/23 agreement with
the site under `p ≤ k`, 3 disagreements under `p < k`), the "differs only for prime `k`"
reason, and the PR-level provenance of the substitution.

Caveats for any write-up: (i) neither `parts.i` nor `parts.ii` becomes false — they
become questions about a different function, so no release and no counterexample
language; (ii) the repair is one token — `smoothNumbers (k+1)` is by definition
`{m ≠ 0 | ∀ p ∈ primeFactorsList m, p < k+1}` = "all prime factors `≤ k`", exactly the
source's condition; equivalently restore PR #1328's original local
`IsKSmooth k n := ∀ p, p.Prime → p ∣ n → p ≤ k`; (iii) re-check the duplicate surface
immediately before any write. **No action taken.**

---

## Candidate 4 — Erdős 1055 `Erdos1055.IsOfClass` / `Erdos1055.p`

### Claim under test

"The `r = 2` equality clause is vacuous in `ℕ+`, so `IsOfClass 2 2` holds and
`Erdos1055.p 2 = 2`, where A005113 gives `p₂ = 13`."

### (a) Primary re-derivation

**Actual Lean at the pin** (`FormalConjectures/ErdosProblems/1055.lean`):

```lean
def IsOfClass : ℕ+ → ℕ → Prop := fun r ↦
  PNat.caseStrongInductionOn (p := fun (_ : ℕ+) ↦ ℕ → Prop) r
    (fun p ↦ (p + 1).primeFactors ⊆ {2, 3})
    (fun n H p ↦
      (∀ r ∈ (p + 1).primeFactors, ∃ (m : ℕ+) (hm : m ≤ n), H m hm r) ∧
      (∃ r ∈ (p + 1).primeFactors, ∀ (m : ℕ+) (hm : m ≤ n), H m hm r → m = n))

@[category textbook, AMS 11] theorem exists_p (r : ℕ+) : ∃ p, p.Prime ∧ IsOfClass r p := by sorry
noncomputable def p (r : ℕ+) : ℕ := open scoped Classical in Nat.find (exists_p r)
```

**Recursor semantics checked in Mathlib, not assumed**
(`Mathlib/Data/PNat/Basic.lean:160-168`):
`caseStrongInductionOn (a) (hz : p 1) (hi : ∀ n, (∀ m, m ≤ n → p m) → p (n+1))` — value at
`1` is `hz`, value at `n+1` is `hi n (fun m hm ↦ …)`. So, writing `L r p` for `IsOfClass r p`:

- `L 1 p ↔ (p+1).primeFactors ⊆ {2,3}`
- `L (n+1) p ↔ (∀ q ∈ (p+1).primeFactors, ∃ m ∈ [1..n], L m q) ∧ (∃ q ∈ (p+1).primeFactors, ∀ m ∈ [1..n], L m q → m = n)`

At `n = 1` the inner `∀ m : ℕ+, m ≤ 1` ranges over the single value `m = 1`, so
`L 1 q → 1 = 1` is trivially true and the whole second conjunct collapses to
`(p+1).primeFactors.Nonempty`. **The equality clause is vacuous at `r = 2`.** Confirmed.

**Source (erdosproblems.com/1055, live 2026-08-15, state `open`):**

> A prime `p` is in class 1 if the only prime divisors of `p+1` are 2 or 3. In general, a
> prime `p` is in class `r` if every prime factor of `p+1` is in some class `≤ r−1`, **with
> equality for at least one prime factor.** … The sequence `p_r` begins `2,13,37,73,1021`
> (A005113 in the OEIS).

**OEIS A005113 (live 2026-08-15):** "Smallest prime in class n (sometimes written n+)
according to the Erdős–Selfridge classification of primes."
DATA `2, 13, 37, 73, 1021, 2917, 15013, 49681, …`.

### (b) Independent computation (own code path)

`…/scratchpad/verify/v1055.py` — I implemented **two** predicates from scratch: `lean(r,p)`
transcribing the recursor unfolding above literally (with `m` ranging over `[1..n]`,
mirroring `ℕ+`), and `trueclass(p)` implementing the source's classification directly
(`1` if `p+1` is 3-smooth, else `1 + max` class over prime factors of `p+1`). Exact
integers, memoised, ran in <3 s.

| r | Lean `p r` = least prime with `IsOfClass r` | least prime of **true** class `r` | A005113(r) |
|---|---|---|---|
| 1 | 2 | 2 | 2 ✓ |
| 2 | **2** | **13** | **13** ✗ (Lean disagrees) |
| 3 | 37 | 37 | 37 ✓ |
| 4 | 73 | 73 | 73 ✓ |
| 5 | 1021 | 1021 | 1021 ✓ |

Direct checks: `IsOfClass 1 2` holds (`primeFactors 3 = {3} ⊆ {2,3}`), `IsOfClass 1 3` holds
(`primeFactors 4 = {2}`), and `IsOfClass 2 2` holds — while `2` has **true class 1**.
So `Erdos1055.p 2 = 2 ≠ 13 = A005113(2)`. **Predecessor claim confirmed exactly.**

**Sharper than the predecessor stated — the defect is confined to `r = 2`.** Verified over
all primes `≤ 2000`:

- `IsOfClass 2 p ⟺ true class of p is ≤ 2` (Lean class 2 swallows all of class 1);
  16 primes `≤ 500` differ, all "Lean-true / source-false": `2, 3, 5, 7, 11, 17, 23, 31,
  47, 53, 71, 107, 127, 191, 383, …` — precisely the class-1 primes.
- `IsOfClass 1 p ⟺ true class 1`, `IsOfClass 3 p ⟺ true class 3`, `IsOfClass 4 p ⟺ true
  class 4` — **no** disagreement. Reason: for `r ≥ 3` the clause `∀ m ≤ n, L m q → m = n`
  is non-vacuous and, because `L 2 = (true class ≤ 2)`, it correctly forces "true class
  exactly `n`". The vacuity is a one-level base-case leak, not a cascading one.

### (c) METHOD §A6 classification

One sentence: this is a claim about coordinate **(3)/(4)** — a `def` in the Lean file
computes a predicate that differs from its cited source at exactly one parameter value
(`r = 2`), so `Erdos1055.p` does not compute A005113 — and it makes no claim about
coordinate (1), the underlying Erdős–Selfridge question, which stays open.

**No declaration in the file is falsified**, and I checked the downstream reach explicitly:
`erdos_1055 (r) : {p | p.Prime ∧ IsOfClass r p}.Infinite` becomes, at `r = 2`, the
*weaker* "infinitely many primes of true class ≤ 2" — still an open infinitude claim with
no finite negation certificate; `erdos_1055.variants.erdos_limit`
(`Tendsto (p r)^(1/r) atTop atTop`) and `.selfridge_limit` (`∃ M, ∀ r, (p r)^(1/r) ≤ M`)
are both asymptotic in `r`, and the single wrong term `p 2 = 2` (which is *smaller* than
13) changes neither the limit nor the boundedness. So the material consequence is limited
to the value of `p 2`, which no upstream declaration asserts.

Secondary note (not part of the claim): `p` is `Nat.find (exists_p r)` where `exists_p` is
itself a `sorry`'d `@[category textbook]` theorem, and `IsOfClass` is built by well-founded
recursion through `PNat.caseStrongInductionOn`, so it has no definitional unfolding lemmas
— both are ergonomics defects, not mathematical ones.

### (d) Duplicate / novelty search performed

Upstream (`gh api search/issues`, issues **and** PRs, all states): `1055` (8 hits),
`IsOfClass` (**1 hit** — PR #1197, the PR that introduced the file), `erdos_1055` (2 hits,
closed bot proof PRs for a `variants.class_one_infinite` that does not exist at the pin),
`Selfridge classification class` (**0**), `A005113` (**0**). Nothing raises the `r = 2`
vacuity.

`git log`/`git blame` of `FormalConjectures/ErdosProblems/1055.lean`: 6 commits —
`3f3aa455` (#1197, Paul Lezeau, 2025-11-13, wrote `IsOfClass` in exactly its current form),
then only whitespace (#1840, #1872), category (#3900), util split (#4433), and
classical-reasoning (#4671) changes. The definition has never been revised.

Also re-read #4896, #4923, #4927 (the three live audit trackers, fetched in full for
candidate 2): Erdős 1055 appears in **none** of them.

Local `c5-k4`: `git log --all --oneline | grep -iE '1055|selfridge|isofclass|005113'` →
only false positives (`A105565`, a commit hash `3b10555`); `git tag` / `gh release list` →
none.

SearXNG: `formal-conjectures erdos 1055 IsOfClass Selfridge class`,
`formal-conjectures 1055 A005113 p_2 = 13 misformalization`,
`Erdos Selfridge prime classification Lean formalization class 2` → only the upstream
source file, the doc page, Rosetta Code, and an empty `leangenius.org/proof/erdos-1055`
SPA shell (fetched: 1.1 kB, no content). No prior art.

### (e) Verdict

**CONFIRMED_PUBLISHABLE — as a small definition-level formalization defect, NOT as a
counterexample; and materially narrower than the predecessor implied.** The exact claim
handed over is true and independently reproduced (`IsOfClass 2 2` holds, `p 2 = 2`,
A005113(2) = 13), the source and OEIS readings are re-derived from the primaries, and the
duplicate surface is clean.

Caveats that must survive into any write-up: (i) the divergence exists **only** at `r = 2`
— `r = 1, 3, 4, 5` all reproduce A005113 exactly, which the predecessor did not establish;
(ii) no declaration in the file becomes false, and the two open asymptotic variants are
unaffected by a single perturbed term; (iii) therefore this is at most a one-line upstream
issue ("the `r = 2` step case's equality clause is vacuous because `m : ℕ+`, `m ≤ 1` forces
`m = 1`; consequently class 2 contains every class-1 prime and `p 2 = 2` instead of 13"),
never a release. **No action taken.**

---

## Candidate 5 — Erdős 931 `erdos_931.variants.exists_prime`

### Claim under test

"Prose says a prime strictly *between* `n₁` and `n₂`; Lean uses closed `n₁ ≤ p ≤ n₂`,
which trivialises the conclusion on the repo's own AlphaProof witness `(10,3,0,13)`."

### (a) Primary re-derivation

**Actual Lean at the pin** (`FormalConjectures/ErdosProblems/931.lean`):

```lean
/-- Erdős was unable to prove that if the two products have the same factors
then there must exist a prime between $n_1$ and $n_2$. -/
@[category research open, AMS 11]
theorem erdos_931.variants.exists_prime (k₁ k₂ n₁ n₂ : ℕ) (h₁ : k₂ ≤ k₁) (h₂ : 3 ≤ k₂)
    (h₃ : n₁ + k₁ ≤ n₂) (h₄ : (∏ i ∈ Finset.Icc 1 k₁, (n₁ + i)).primeFactors =
      (∏ j ∈ Finset.Icc 1 k₂, (n₂ + j)).primeFactors) :
    ∃ (p : ℕ), p.Prime ∧ n₁ ≤ p ∧ p ≤ n₂
```

Closed interval in the conclusion, "between" in the docstring: the textual divergence is
real and confirmed.

**Source (erdosproblems.com/931, live 2026-08-15, state `open`).** Full page text
retrieved; the statement is the finiteness question, and the remarks give Tijdeman's
example `19,20,21,22` / `54,55,56,57` and the AlphaProof counterexample
(`10! = 2⁸·3⁴·5²·7`, `14·15·16 = 2⁵·3·5·7`, so `n₁=0, k₁=10, n₂=13, k₂=3`).

**Source-attribution bracket (recorded, not asserted as a defect).** The sentence the
docstring attributes to the source — "Erdős was unable to prove … there must exist a prime
between `n₁` and `n₂`" — does **not** appear on the current page: the live fetch and the
campaign's cached copy are byte-identical (33,924 bytes each) and contain **0** occurrences
of "between" and **0** of "unable"; the `/latex/931` rendering likewise has 0. The
docstring dates to 2025-02-17 (Salvatore Mercuri, then
`OpenConjectures/ErdosProblems/erdos_931.lean`), so the site text may simply have been
edited since. A Wayback Machine check was attempted twice and returned **HTTP 429**
(rate-limited), so this is an **unresolved bracket**, not a finding. Do not claim the
docstring is unsourced on this evidence. (The predecessor's `erdos-hunt.md` D1 quotes this
sentence as "Source (erdosproblems.com/931 …)" — that attribution is unverified.)

### (b) Independent computation (own code path)

`…/scratchpad/verify/v931.py`, own smallest-prime-factor sieve; the key reduction is
`primeFactors (∏_{i=1..k}(n+i)) = ⋃_{i=1..k} primeFactors(n+i)`, so `h₄` is a set equality
that can be indexed and matched. Ran in <10 s.

**The AlphaProof witness `(k₁,k₂,n₁,n₂) = (10,3,0,13)`:** `10! = 3628800`, prime factors
`{2,3,5,7}`; `14·15·16 = 3360`, prime factors `{2,3,5,7}` — `h₄` holds; `h₁,h₂,h₃` hold.

- primes in the **closed** `[0,13]`: `2,3,5,7,11,13`
- primes in the **open** `(0,13)`: `2,3,5,7,11`

**Both readings are satisfied, with the same least witness `p = 2`.** The conclusion is
discharged trivially because `n₁ = 0`, not because the interval is closed. **The claimed
causal link between the closed interval and the trivialisation is false.**

Same for Tijdeman's example (`n₁=18, k₁=4, n₂=53, k₂=4`, common support
`{2,3,5,7,11,19}`): both `[18,53]` and `(18,53)` contain `19,23,29,31,37,…`.

**Bounded exhaustive hunt for premise-satisfying tuples** (this is new work; the
predecessor searched only *inside prime-free runs* and therefore found zero instances of
any kind). Over `n₁ ≤ 500`, `3 ≤ k₂ ≤ k₁ ≤ 25`, `n₂ ≤ 6000`, with `k₂ ≤ k₁` and
`n₁+k₁ ≤ n₂` and `h₄` all enforced:

```
premise-satisfying tuples found:                        280
tuples where the CLOSED and OPEN readings disagree:       0
tuples with NO prime in the closed interval [n1,n2]:      0
first hits: (5,3,0,7) (6,3,0,7) (4,3,1,7) (5,3,1,7) (3,3,2,7) (4,3,2,7) (3,3,3,7) (7,3,0,13)
```

So across every premise-satisfying instance in the searched region, the endpoint
divergence changes nothing, and the conclusion holds under both readings.

**Direction of the divergence.** `(∃ p, n₁ < p < n₂) → (∃ p, n₁ ≤ p ≤ n₂)`, so the Lean
form is strictly **weaker** than the "between" reading. It is therefore *harder* to refute:
any counterexample to the Lean declaration is automatically a counterexample to the
stricter source reading. The divergence is conservative and cannot manufacture a spurious
disproof.

### (c) METHOD §A6 classification

One sentence: this is a claim about coordinate **(3)** only — a docstring-vs-statement
endpoint mismatch in a declaration that is *weaker* than the reading its docstring
describes — and it touches neither coordinate (1) nor produces any finite falsification of
coordinate (4).

### (d) Duplicate / novelty search performed

Upstream (`gh api search/issues`, issues **and** PRs, all states): `931` (6 hits: closed
issue #2106 "Erdős Problem 931", closed PR #11 "add counterexample to Erdős 931", two
closed bot PRs for `additional_condition_nonempty`, plus two unrelated Erdős-768 items),
`erdos_931` (3 hits, same), `exists_prime` (**0**), `Tijdeman` (2 hits, unrelated
Polignac/Green–Tao PR). Nothing about the interval endpoints.

`git log`/`git blame` of `FormalConjectures/ErdosProblems/931.lean`: 14 commits; the
conclusion line `∃ (p : ℕ), p.Prime ∧ n₁ ≤ p ∧ p ≤ n₂` traces to `ffa38e38` (#114, a
`:= sorry` → `:= by sorry` chore) over Salvatore Mercuri's original 2025-02-17 statement;
the docstring sentence is from that same original. No commit ever touched the endpoints.

Also re-checked the three live audit trackers (#4896, #4923, #4927, fetched in full for
candidate 2): Erdős 931 appears in none.

Local `c5-k4`: `git tag` / `gh release list` → none for 931; the only local mentions are
this campaign's own reports.

SearXNG: `formal-conjectures erdos 931 exists_prime prime between n1 n2`,
`erdosproblems 931 prime between n_1 n_2 Erdos unable to prove` → no prior art (the second
query surfaced the erdosproblems forum thread `/forum/discuss/931`, which resolves to a
221-byte redirect stub with no content).

### (e) Verdict

**REFUTED** as handed over. The endpoint divergence (`between` vs `n₁ ≤ p ≤ n₂`) is real,
but it does **not** trivialise the conclusion on the AlphaProof witness — the strict
reading is satisfied there too, by the same `p = 2` — and across all 280 premise-satisfying
tuples I found in a bounded exhaustive region, the two readings never disagree. The
divergence is also in the *conservative* direction (Lean is the weaker statement), so it
can never yield a counterexample the source reading would not also yield.

**Residual, DOWNGRADED to `COSMETIC`** plus one **unresolved bracket**: the docstring's
"prime between `n₁` and `n₂`" sentence is not present on the current
erdosproblems.com/931 page, and the Wayback check to determine whether it once was
returned HTTP 429 twice. That bracket must be closed before the endpoint mismatch could
even be described as a docstring defect. Nothing publishable. **No action taken.**

---

## Summary

| # | Target | Verdict | One-line justification |
|---|---|---|---|
| 1 | Erdős 1084 `triangular_optimal_d2` | **REFUTED** (residual `STATUS_SYNC` + `COSMETIC`) | The declaration asserts `=`, not `<`; the `=` form is exactly Harborth's 1974 theorem, so nothing is finitely false — only the docstring (`<`) and the `research open` tag are wrong. |
| 2 | OEIS A237271 `observation_carmichael` | **CONFIRMED_PUBLISHABLE** (formalization defect, not a counterexample) | Any composite `k > 1` has a prime factor `p` with `0 < p < k`, which is a zero divisor and so cannot satisfy `p^(k−1) = 1`; the hypothesis is unsatisfiable, the `research open` declaration is vacuously true, and nothing upstream or on the web reports it. |
| 3 | Erdős 1093 `deficiency` | **CONFIRMED_PUBLISHABLE** (formalization defect, not a counterexample) | `Nat.smoothNumbers k` is `p < k` while the source is `p ≤ k`; my recomputation reproduces all 23 catalogue entries under `p ≤ k` and changes exactly three under `p < k` (C(7,3): 1→0, C(23,5): 1→0, C(47,11): 4→3), and PR #1328's own first commit shows the correct `≤ k` predicate was replaced by the Mathlib one without discussion. |
| 4 | Erdős 1055 `IsOfClass` / `p` | **CONFIRMED_PUBLISHABLE** (small definition defect; narrower than claimed) | `m : ℕ+`, `m ≤ 1 ⇒ m = 1` makes the `r = 2` equality clause vacuous, so `IsOfClass 2` = "true class ≤ 2" and `p 2 = 2` vs A005113(2) = 13 — but `r = 1,3,4,5` all reproduce A005113 exactly and no declaration in the file becomes false. |
| 5 | Erdős 931 `exists_prime` | **REFUTED** (residual `COSMETIC` + one open bracket) | The closed interval does not trivialise the AlphaProof witness — the strict reading is satisfied there too by `p = 2` — and across 280 premise-satisfying tuples I enumerated, closed and open never disagree; the divergence is in the conservative (weaker) direction. |

### What may and may not be claimed

- **Nothing here is a counterexample.** Candidates 2, 3 and 4 are all *formalization
  defects* (METHOD_V1_6 §A6 coordinates 3 and 4). In each case the underlying
  mathematics (coordinate 1) is untouched, and in candidate 2 the literal declaration is
  trivially **true**, so METHOD Phase 8 / `UPSTREAM_PROTOCOL.md` release machinery does
  not apply. The appropriate artifact for 2/3/4 is an upstream **issue** in the style of
  the live trackers #4896 / #4923, or a local note — **subject to explicit user
  authorization, which has not been given.**
- Candidates 1 and 5 should not be carried forward as counterexamples at all.
- The four-coordinate discipline must be stated in the first sentence of any write-up.

### Pinned blob SHAs (METHOD_V1_6 §A2.1 — re-check immediately before any publish)

```
159a640c86ea311e35d4cc85fb7548358be19bc3  FormalConjectures/ErdosProblems/1084.lean
74d08a37138750c7a607d5f8b7ec216a7ed0b99d  FormalConjectures/OEIS/237271.lean
846eebf592199842d56e9b2a5bc03866e2a497fb  FormalConjectures/ErdosProblems/1093.lean
4835f12e96d618c7e9014f31a85f7549baf2ab79  FormalConjectures/ErdosProblems/1055.lean
b90e2e2595df52da5dbbb6c74afce4a17e81bbef  FormalConjectures/ErdosProblems/931.lean
```

`OEIS/237271.lean` in particular was created only on **2026-08-12** (three days before
this audit), so its duplicate surface is the most volatile of the five.

### Verifier scripts (independent code path, all under the 60 s cap)

- `…/scratchpad/verify/v1084.py` — exact triangular-lattice unit-distance count and
  Harborth floor via `math.isqrt`.
- `…/scratchpad/verify/v237271.py` — Lean `a` re-implementation vs OEIS DATA `n = 1..90`,
  full Lean-hypothesis sweep `k ≤ 20000`, Carmichael numbers and `a(k)` on them.
- `…/scratchpad/verify/v1093.py` — deficiency under both thresholds for all 23 catalogue
  entries plus the "differs only for prime `k`" check.
- `…/scratchpad/verify/v1055.py` — literal `PNat.caseStrongInductionOn` unfolding vs the
  Erdős–Selfridge classification, and `p r` vs A005113 for `r = 1..5`.
- `…/scratchpad/verify/v931.py` — AlphaProof/Tijdeman witnesses and the bounded
  exhaustive premise-satisfying-tuple hunt.

Copies have been placed in the repository at
`results/expansion/live-search-2026-08-15/scripts/verify_candidate_{1084,237271,1093,1055,931}.py`
so the audit is replayable; they are uncommitted (this lane does not write to git) and must
be committed before any of 2/3/4 could enter a publication path
(`UPSTREAM_PROTOCOL.md` artifact gate).
