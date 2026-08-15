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
