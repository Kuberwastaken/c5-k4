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
