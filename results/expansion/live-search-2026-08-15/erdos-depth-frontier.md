# Erdős depth frontier — continuation of the 2026-08-15 live search

Continues `erdos-hunt.md` (triage COMPLETE there: 603 declarations, 575
`NOT_FINITELY_REFUTABLE`, 28 `CANDIDATE_FOR_DEPTH`; depth sections D1–D11).
This file covers the **remaining depth frontier** only. Nothing in
`erdos-hunt.md` is re-run.

**Corpus pin (METHOD v1.6 §A2.1).** `google-deepmind/formal-conjectures` at
`2411d22e1bd550d050d0eac6c1fb379a76a3e7c5`, tree
`FormalConjectures/ErdosProblems/` (610 files extracted to
`<scratch>/fcerdos/`). Blob SHAs recorded per target below.

**Budget (METHOD v1.6 §A2.4).** Hard 60 s wall-clock cap on every computation;
exact integer / `fractions.Fraction` arithmetic only;
`/home/ec2-user/.venvs/wowii/bin/python`. A timeout is a `TIMEOUT_BRACKET`,
never a hold.

**Publication.** None. No upstream issue, PR, comment, or fork push. No `git`
run by this agent (single-writer rule, METHOD v1.6 §A5).

---

# HANDOFF STATE (kept current)

## Scope of this file

19 targets: the 28 `CANDIDATE_FOR_DEPTH` declarations minus the 9 already
closed in `erdos-hunt.md` (931, 10, 11 ×3, 677, 364, 406, 324) — i.e. 189,
241, 242, 274, 349, 409*, 477 ×2, 535, 617, 779, 952, 982, 1041, 1044, 1055,
1084*, 1113, 1135. (* 409 and 1084 were already closed in D8/D9; carried here
only as pointers.)

## Status table

| target | verdict | status |
|---|---|---|
| 477 `X_pow_three`, `monomial` | `CERTIFICATE_SHAPE_FAIL` + **formalization divergence** | DONE (F1) |
| 952 `erdos_952` | `CONSTRUCTION_ONLY` + **formalization defect (asserted direction)** | DONE (F2) |
| 982 `erdos_982` | pending | IN PROGRESS |
| 242 `erdos_242` | pending | queued |
| 779 `erdos_779` | pending | queued |
| 274 `herzog_schonheim` | pending | queued |
| 189 `parallelogram` | pending | queued |
| 349, 241, 535, 617, 1041, 1044, 1055, 1113, 1135 | pending | queued |

## Rules being followed

* Append after **every** target (§A5). Never buffer.
* Any candidate violation: independent second-code-path recomputation, then
  source comparison against erdosproblems.com/<id>, then §A6 classification
  (mathematics vs. formal declaration), then duplicate check.
* No upstream writes.

---

# Findings

## F1 — Erdős 477, `variants.X_pow_three` and `variants.monomial`

**Blob** `95bc9c4afdceb802fcd936535f2b2cb54a9efdaa` (`477.lean`).

**Lean (both open variants, and the two `research solved` siblings) quantify
`b` over `f.eval '' {n | 0 < n}`:**

```lean
theorem erdos_477.variants.X_pow_three :
    letI f := X ^ 3
    ∀ A : Set ℤ, ∃ z, ¬ ∃! a ∈ A ×ˢ (f.eval '' {n | 0 < n}), z = a.1 + a.2
```

**Source (erdosproblems.com/477, state `open`, prize `OPEN`, edited
11 April 2026).** "Is there a polynomial $f:\mathbb{Z}\to\mathbb{Z}$ of degree
at least $2$ and a set $A\subset\mathbb{Z}$ such that for any $n\in\mathbb{Z}$
there is exactly one $a\in A$ and $b\in\{f(k):k\in\mathbb{Z}\}$ such that
$n=a+b$?"

### Finding — formalization divergence (index set of the second summand)

Source: `b ∈ {f(k) : k ∈ ℤ}`. Lean: `b ∈ f.eval '' {n | 0 < n}` = `{f(k) : k ≥ 1}`.
The Lean set is a proper subset (it drops `k ≤ 0`), in every declaration in the
file — the open `erdos_477`, the two `research solved` variants, and both open
variants above.

This is not cosmetic: **the published proof cited on the source page uses
negative arguments.** The site's degree-2 argument is "for any infinite `A`
there exist `a,b ∈ A` with `a−b = 2c₁k`, `k ≥ 1`, whence `0 ≠ a−b = f(k)−f(−k)`
and `n = a+f(−k) = b+f(k)` has two solutions". `f(−k)` is not in the Lean's `B`.

**Repair check for `variants.S_sq` (`f = X²`, marked `research solved`, so this
is a control not a target).** The site's own `c₁ = 0` branch is already
one-sided-safe: it uses `a−b = 4c₂k = f(k+1) − f(k−1)`. Taking `k ≥ 2` keeps
both `k−1 ≥ 1` and `k+1 ≥ 1` positive. Any infinite `A ⊆ ℤ` has two elements
congruent mod 4 with difference `≥ 8` (infinitely many in one residue class
⇒ unbounded differences), so `a−b = 4k` with `k ≥ 2`, and
`z = a + (k−1)² = b + (k+1)²` has two distinct representations. So the `X²`
`research solved` declaration survives the divergence. The general
`degree_two_dvd_condition_b_ne_zero` variant (`f = aX²+bX+c`, `a ∣ b`) is
**not** repaired by this argument as stated: its site proof is exactly the
`f(k) − f(−k)` one, and a one-sided replacement has to realise the needed
differences as `a(m−m′)(m+m′+s)` with `m,m′ ≥ 1`, which does not obviously
cover the same modulus class. Flagged, not resolved — it is a `research solved`
declaration, outside this lane's target set.

### Certificate shape

Literal negation of `X_pow_three` / `monomial`: `∃ A : Set ℤ` (necessarily
infinite — the source says so explicitly) with `∀ z` a *unique* representation.
No finite object certifies that.

**Verdict:** `CERTIFICATE_SHAPE_FAIL` for both open variants (confirms the
predecessor's triage), **plus** a recorded band-1 divergence
(`{f(k) : k ∈ ℤ}` → `{f(k) : k ≥ 1}`) affecting all five declarations in the
file. §A6 class: a claim about **the formal declaration only**; the underlying
mathematics is untouched.

**Duplicate check.** Upstream issue/PR search "477": #2085 (closed, statement
request), #3191 (closed, "formally solved erdos_477 S_sq and degree_two_dvd"),
#1510 (merged, unrelated chore). No issue/PR raises the `0 < n` index-set
divergence. No upstream action taken.

## F2 — Erdős 952, `erdos_952` (Gaussian moat)

**Blob** `ed1275eb3ac6e545e22125202bc3fcf7d30b91cd` (`952.lean`).

```lean
@[category research open, AMS 11]
theorem erdos_952 :
  ∃ (x : ℕ → GaussianInt) (C : ℤ),
    Function.Injective x ∧
      ∀ n, Prime (x n) ∧ (x (n + 1) - x n).norm < C
```

**Source (erdosproblems.com/952, state `open`, prize `OPEN`, edited
08 April 2026).** "Is there an infinite sequence of distinct Gaussian primes
$x_1,x_2,\ldots$ such that $\lvert x_{n+1}-x_n\rvert \ll 1$?" Remarks: "The
Gaussian moat problem. … In [Er80] Erdős writes **'the answer is almost
certainly negative'**."

### Finding — formalization defect (the declaration asserts the disbelieved direction)

The source poses a *question* and records the cited author's expectation that
the answer is **no**. The Lean declaration is not `answer(sorry) ↔ ∃ …` (the
repo's convention for an undetermined question, used in 477, 1113, 349, 274 in
this same sweep); it is a bare `theorem` **asserting the existence**, i.e. it
asserts the "yes" branch that [Er80] calls almost certainly false. Under §A6
this is a defect in coordinate (3)/(4) — declaration faithfulness and literal
content — with coordinate (1), the mathematics, untouched and open.

Semantics check, in case the assertion is trivially satisfiable: `GaussianInt =
ℤ√-1`, so `Zsqrtd.norm z = z.re² + z.im² ≥ 0`, and `norm < C` is a bound on the
*squared* step length — faithful to `|x_{n+1}−x_n| ≪ 1`. `Prime` is primality
in `ℤ[i]`, and `Function.Injective x` forces infinitely many distinct primes, so
an infinite injective sequence must leave every bounded set; there is no
associates/conjugates escape (a single prime has only 4 associates × 2
conjugates). So the declaration is exactly the moat problem's positive branch:
no trivial-truth loophole, and the defect is purely that an open question is
stated as a one-directional assertion whose cited expectation is the opposite.

### Certificate shape

Negation of `∃ x C, …` is `∀ x C, ¬…` — refuting requires ruling out every
sequence and every bound. No finite certificate. (Conversely one construction
would prove it — but no such construction is believed to exist.)

**Verdict:** `CONSTRUCTION_ONLY` (confirms the predecessor's triage) **plus** a
band-1 `STATUS_SYNC`-class formalization defect: an open question with a
recorded "almost certainly negative" expectation is declared as a positive
existence theorem rather than `answer(sorry) ↔`.

**Prior art, for the record (not a refutation of the declaration).** Gethner–
Wagon–Wick and successors computed that no walk to infinity through Gaussian
primes exists with step size ≤ 6 (moats of that width exist). That refutes the
declaration only for fixed small `C`, not for the `∃ C` form.

**Duplicate check.** "952": #1031 (closed, statement request), #2978 (closed,
`variants.known_result` solved). Nothing raising the asserted-direction defect.
No upstream action taken.

## F3 — Erdős 982, `erdos_982` — `HOLD_BOUNDED` (the one genuinely finite target)

**Blob** `33971c07d094160f9b54fc40433c2b0df155ad11` (`982.lean`).

```lean
@[category research open, AMS 52]
theorem erdos_982 (n : ℕ) (hn : 3 ≤ n) (p : Fin n → ℝ²) (hp : Function.Injective p)
    (hp' : EuclideanGeometry.IsConvexPolygon p) :
    ∃ (i : Fin n), { d : ℝ | ∃ j : Fin n, j ≠ i ∧ d = dist (p i) (p j) }.ncard ≥ n / 2
```

**Source (erdosproblems.com/982, state `open`, prize `FALSIFIABLE`, edited
19 October 2025).** "If $n$ distinct points in $\mathbb{R}^2$ form a convex
polygon then some vertex has at least $\lfloor n/2\rfloor$ different distances
to other vertices."

**Faithfulness: clean.** `n / 2` is ℕ-division `= ⌊n/2⌋`; `≥` matches "at
least"; `ncard` of the set of realised distances from `p i` is the count of
*distinct* distances; `Function.Injective p` = "distinct points";
`IsConvexPolygon` in this repo unfolds to `IsCcwConvexPolygon p ∨
IsCcwConvexPolygon (p ∘ Neg.neg)`, i.e. **strict** convexity (no three
collinear vertices). No divergence found. §A6: any counterexample here would be
a claim about **the mathematics**, not merely the declaration.

**Certificate shape:** `FINITE_UNIVERSAL`. Negation = one strictly convex
`n`-point configuration in which **every** vertex has `≤ ⌊n/2⌋ − 1` distinct
distances. This is the only remaining candidate in the frontier whose negation
is a genuinely replayable finite object.

### Calibration (frozen before searching)

Regular `n`-gon, `n = 3..9`: every vertex has exactly `⌊n/2⌋` distinct
distances (`[1,1,1]`, `[2,2,2,2]`, `[2]*5`, `[3]*6`, `[3]*7`, `[4]*8`, `[4]*9`).
So the conjecture is exactly tight and the residual `R = min_i c_i − ⌊n/2⌋` is
`0` on the whole regular family. Unit square: counts `[2,2,2,2]`, strict
convexity `True`.

### Obstruction identity (METHOD Phase 4) — and it is already taken upstream

If all `n` points are **concyclic**, then for any vertex `i` a circle centred at
`p i` meets the common circle in at most 2 points, so each realised distance
from `p i` has multiplicity `≤ 2` among the other `n−1` vertices, giving
`c_i ≥ ⌈(n−1)/2⌉ = ⌊n/2⌋` for every `i`. Hence **no concyclic configuration can
be a counterexample**, for any `n`.

**Duplicate — this is already upstream.** `gh search issues --repo
google-deepmind/formal-conjectures 982 --include-prs` returns issue **#4691**
("Erdős 982: add the solved concyclic variant and Lean proof", open) and PR
**#4694** ("feat(Erdős 982): add the concyclic solved variant", open, created
2026-08-02), which adds `erdos_982.variants.concyclic` with a no-`sorry` Lean
proof (`#print axioms` = `propext, Classical.choice, Quot.sound`). No novelty
is claimed for this lemma here; it is recorded because it is the pruning
principle the search below uses.

The source page states the general form of the same fact: "This would be
implied if there was a vertex such that no three vertices of the polygon are
equally distant to it, which was originally also conjectured by Erdős [Er46b],
but **this is false** (see [97])." So a counterexample must satisfy, at *every*
vertex, "at least three other vertices are equidistant from me".

### Bounded exact search

Both searches are over **integer coordinates** (so all squared distances are
exact integers), with the lex-smallest vertex translated to the origin, box
`x ∈ [0,N]`, `y ∈ [−N,N]`. Target: `c_i ≤ K := ⌊n/2⌋ − 1` for all `i`.

Two monotone prunes, both valid on partial sets because both properties are
hereditary downward:
* **P1** strict convex position (Andrew monotone chain with strict turns;
  `hull_size(S) = |S|`);
* **P2** `c_i(S) ≤ K` for every `i ∈ S` (`c_i` is nondecreasing in `S`).

**Path A** (`<scratch>/e982.py`): DFS over the whole grid with P1+P2.
**Path B** (`<scratch>/e982b.py`), independent: for `K = 2` the other `n−1`
vertices lie on at most 2 circles centred at the origin, so enumerate the
radius set first and DFS only inside that pool. Path B is a structurally
different enumeration, used as the §Phase-7 independent recomputation.

| n | K | box N | path | status | nodes | secs | counterexamples |
|---|---|---|---|---|---|---|---|
| 4 | 1 | 10 | A | COMPLETE | 24,310 | 0.0 | **0** |
| 5 | 1 | 10 | A | COMPLETE | 24,310 | 0.0 | **0** |
| 6 | 2 | 12 | A | COMPLETE | 5,030,452 | 4.8 | **0** |
| 6 | 2 | 12 | B | COMPLETE | 98,243 dfs | 0.7 | **0** (agrees with A) |
| 6 | 2 | 30 | B | COMPLETE | 3,716,438 dfs | 32.8 | **0** |
| 6 | 2 | 45 | B | **TIMEOUT** at 55 s | 6,252,847 dfs | 55.0 | 0 so far (132,460 of 361,425 radius-groups) |
| 7 | 2 | 30 | B | COMPLETE | 3,389,202 dfs | 28.6 | **0** |
| 8 | 3 | 7 | A | COMPLETE | 4,445,090 | 5.7 | **0** |
| 8 | 3 | 9 | A | COMPLETE | 30,135,606 | 35.0 | **0** |
| 9 | 3 | 9 | A | COMPLETE | 30,135,606 | 35.9 | **0** |

(The `n = 8` and `n = 9` node counts coincide because both have `K = 3`: the
pruned tree is identical and no branch ever reaches depth 8, so none reaches
depth 9 either.)

`n = 4,5` are also settled unconditionally: `K = 1` forces all `n` points
pairwise equidistant, impossible in `ℝ²` for `n ≥ 4`. `n = 3` is trivial
(`K = 0`, but a 3-point set has at least one distance).

**Verdict: `HOLD_BOUNDED`.** No counterexample. Explicit bounds: complete
exhaustion of all strictly convex **integer** configurations with `n ∈ {6,7}`
inside `x∈[0,30], y∈[−30,30]` and `n ∈ {8,9}` inside `x∈[0,9], y∈[−9,9]`, plus
the partial `n=6, N=45` bracket. **Limitation, stated honestly:** integer
coordinates only, so the search covers exactly those configurations similar to
a rational one; a counterexample requiring irrational coordinates is outside
the bracket, and so is any `n ≥ 10`. Prior art (Moser; Erdős–Fishburn;
Dumitrescu; Nivasch–Pach–Pinchasi–Zerbib `f(n) ≥ (13/36+1/22701)n − O(1)`)
leaves the conjecture open for all large `n`, so this is calibration, not new
mathematical evidence.

