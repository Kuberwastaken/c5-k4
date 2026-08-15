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

## Status table — **frontier CLOSED, 0 counterexamples, 3 new formalization defects**

| target | verdict | section |
|---|---|---|
| 477 `X_pow_three`, `monomial` | `CERTIFICATE_SHAPE_FAIL` + **divergence: `{f(k):k∈ℤ}` formalized as `{f(k):k≥1}`** | F1 |
| 952 `erdos_952` | `CONSTRUCTION_ONLY` + **defect: open question asserted in the direction [Er80] calls "almost certainly negative"** | F2 |
| 982 `erdos_982` | `HOLD_BOUNDED` (n=6,7 complete to N=30; n=8,9 to N=9) | F3 |
| 242 `erdos_242` | `HOLD_BOUNDED` — predecessor's `TIMEOUT_BRACKET` **closed**, all n ≤ 2,000,000 witnessed | F4 |
| 779 `erdos_779` | `HOLD_BOUNDED` n = 1..200 (bracket at n ≥ 201) | F5 |
| 274 `herzog_schonheim` | `HOLD_BOUNDED` over 89 groups + **`ENat.card` loophole closed by Neumann's lemma** | F6 |
| 1055 `selfridge_limit` | `CERTIFICATE_SHAPE_FAIL` + **defect: `IsOfClass` non-exclusive at r=2, `p 2 = 2 ≠ 13`** | F7 |
| 189, 241, 349, 535, 617, 1041, 1044, 1113, 1135 | strict stops (`CERTIFICATE_SHAPE_FAIL` / prior-art), each re-derived | F8 |
| 409, 1084 | already closed by the predecessor (D9, D8) | — |

**Nothing is left queued.** Open brackets, for a future agent:
`982` (`n=6, N=45` at 37 % of radius-groups; `n ≥ 10` untouched; irrational
coordinates outside every run), `779` (`n ≥ 201`), `274` (`S₅` order 120 and
`D₃₆` order 72 not enumerated), `242` (`n > 2·10⁶`, but prior art reaches
`10^18` so this is worthless), `617` (needs a balanced 12-colouring of `K₁₄₅`).

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

## F4 — Erdős 242, `erdos_242` — predecessor's `TIMEOUT_BRACKET` **CLOSED**, now `HOLD_BOUNDED`

**Blob** `597f7a04f2b128b1fbaf8a000a0ab642aa201d1f` (`242.lean`).

```lean
theorem erdos_242 (n : ℕ) (hn : 2 < n) :
    ∃ x y z : ℕ, 1 ≤ x ∧ x < y ∧ y < z ∧ (4 / n : ℚ) = 1 / x + 1 / y + 1 / z
```

Source faithfulness was already settled in `erdos-hunt.md` D10 (site carries the
strict `1 ≤ x < y < z`, Lean division is rational): **no divergence**. This
entry only closes the open computational bracket.

### What was left open

`erdos-hunt.md` D10: phase 1 of `verify_erdos_misc.py es242 3000` covered
`n = 3..2901` with a per-`n` op cap and left **178 values unresolved by the
cap**; phase 2 (the exhaustive pass) hit the 52 s wall having checked none of
them. Verdict recorded there: `TIMEOUT_BRACKET`, explicitly **not** a hold.

### Why the old run was slow, and the replacement (independent code path)

The old routine enumerated `y` one at a time inside `(q/p, 2q/p]`, whose length
is `~n²/(16j)` at `x = ⌊n/4⌋+j` — that is the op blow-up. Replace the `y`-loop
by exact divisor enumeration:

```
4/n − 1/x = p/q  in lowest terms  (n/4 < x ≤ 3n/4, since 1/x is the largest term)
1/y + 1/z = p/q  ⟺  (p·y − q)(p·z − q) = q²,  with d := p·y − q a divisor of q², d ≤ q
             ⟹  y = (q+d)/p,  z = (q + q²/d)/p     (both required integral)
```

so each `x` is settled **completely** rather than up to a cap. `q ∣ n·x`, so
`q`'s factorisation is read off from a smallest-prime-factor sieve on `x` plus
the factorisation of `n` — no big-number factoring. Two further exact
accelerations, both certificate-preserving:

* **divisor lift:** if `d ∣ n`, `3 ≤ d < n`, and `4/d = 1/x+1/y+1/z` with
  `x<y<z`, then `4/n = 1/(kx)+1/(ky)+1/(kz)` with `k = n/d`, still strictly
  ordered. So only `n` with no solved proper divisor `≥ 3` reach the
  exhaustive routine (in practice: the primes).
* every produced triple, lifted or exhaustive, is re-verified with
  `fractions.Fraction` before being accepted (`1 ≤ x < y < z` and exact
  equality) — this is a second arithmetic path over **every** witness, not a
  sample.

Script: `<scratch>/e242.py`.

### Result

| range | status | n needing exhaustive search | n solved by lift | **n with no triple** | secs |
|---|---|---|---|---|---|
| `n = 3..3,000` | COMPLETE | 430 | 2,568 | **0** | 0.1 |
| `n = 3..100,000` | COMPLETE | 9,592 | 90,406 | **0** | 2.0 |
| `n = 3..2,000,000` | COMPLETE | 148,933 | 1,851,065 | **0** | 45.5 |

Sample exact witnesses (all Fraction-verified):
`n=3 → (1,4,12)`; `n=4 → (2,3,6)`; `n=5 → (2,5,10)`;
`n=97 → (25,810,392850)`; `n=2,000,000 → (1000000,1500000,3000000)`.

**Third independent path** (naive `x`-then-`y` scan with `Fraction`
arithmetic, no divisor algebra, no lifting): `n = 3..400`, **398/398 solved,
0 unsolved**, 14.7 s. Agrees with the divisor method on the whole overlap.

**Verdict: `HOLD_BOUNDED`.** The predecessor's 178-value bracket at `n ≤ 2901`
is fully closed — every `n` in `3..2,000,000` now has an explicit, exactly
verified `(x,y,z)` with `1 ≤ x < y < z`. No counterexample. Prior art
(verified `n ≤ 10^18` [MiDu25]) already excluded a small one, so this is
calibration; the contribution is that the campaign's own record no longer
carries an unverified interval.

**Duplicate check.** "242": #2049 (closed, statement request), #2859 (closed,
`variants.known_result`), #1864 and #3952 (open, claimed *proofs* of
Erdős–Straus — proof attempts, not counterexamples, and not touched here). No
upstream action taken.

## F5 — Erdős 779, `erdos_779` (Deaconescu) — `HOLD_BOUNDED`, first run of this target

**Blob** `ed251a0942abf6f9b9d0ae2ec02f989155510c88` (`779.lean`).

```lean
@[category research open, AMS 11]
theorem erdos_779 (n : ℕ) (hn : n ≥ 1) : let P := ∏ i ∈ range (n + 1), nth Nat.Prime i
    ∃ p, p.Prime ∧ (P + p).Prime ∧ nth Nat.Prime n < p ∧ p < P
```

**Source (erdosproblems.com/779, state `open`, prize `FALSIFIABLE`).** "Let
$n>1$ and $p_1<\cdots<p_n$ the first $n$ primes. Let $P=\prod p_i$. Does there
always exist some prime $p$ with $p_n<p<P$ such that $P+p$ is prime?"

**Faithfulness: clean.** `nth Nat.Prime` is 0-indexed, so `∏ i ∈ range (n+1)`
is the product of the first `n+1` primes and `nth Nat.Prime n` is the largest
of them; the Lean's `n` is the site's `N − 1`, and `hn : n ≥ 1` is exactly the
site's `N > 1`. The docstring documents the shift ("Needed to index shift in
order to avoid trivial case n = 0"). No divergence. Confirms the predecessor's
reading.

**Certificate shape.** For a *fixed* `n` the negation is finite — "every prime
`p ∈ (p_max, P)` has `P + p` composite" ranges over finitely many `p` — so the
triage label `CANDIDATE_FOR_DEPTH` is technically right. But `P` is a
primorial, so that exhaustion is only executable for `n ≤ 3` or so; in practice
the reachable work is confirming the positive direction.

### Bounded run (`<scratch>/e779.py`)

For each `n` the **least** prime witness `p` is computed. Primality by
Miller–Rabin; deterministic (13 prime bases below `3.317·10^24`) for `n ≤ 17`,
and a 30-prime-base strong probable-prime test above that — labelled as such,
not claimed as a proof.

`n = 1..200`: **every `n` resolved, 0 failures.** `P` has 500 digits at
`n = 200`. Largest witness over the whole range: `p = 3559` at `n = 180`; the
largest number of primes that had to be tried before success was 318.

First rows (exact, deterministic-MR region):

| n | largest prime factor of P | P | least witness p | primes tried |
|---|---|---|---|---|
| 1 | 3 | 6 | 5 | 1 |
| 2 | 5 | 30 | 7 | 1 |
| 3 | 7 | 210 | 13 | 2 |
| 4 | 11 | 2310 | 23 | 4 |
| 5 | 13 | 30030 | 17 | 1 |
| 6 | 17 | 510510 | 19 | 1 |
| 7 | 19 | 9699690 | 23 | 1 |
| 8 | 23 | 223092870 | 37 | 3 |
| 9 | 29 | 6469693230 | 61 | 8 |
| 10 | 31 | 200560490130 | 67 | 8 |

`n = 201..` is a **`TIMEOUT_BRACKET`** (50.8 s wall clock reached at `n = 200`).

**Verdict: `HOLD_BOUNDED`** on `n = 1..200`, with the `n ≥ 201` tail an
explicit bracket. Prior art: Deaconescu verified `n ≤ 1000` (site), so this run
is calibration, not new evidence; its value is that the campaign's own record
for this target now has witnesses instead of "NOT STARTED". The witness sizes
(`p ≤ 3559` for `n ≤ 200`) are consistent with Erdős's `p ≤ n^{O(1)}`
expectation and with Cambie's heuristic that failure has probability
`≪ exp(−n^{−cn})`.

**Duplicate check.** "779": #2095 (closed, statement request), #2960 (closed,
`variants.known_result`). No counterexample claim upstream. No upstream action
taken.

## F6 — Erdős 274, `herzog_schonheim` — `HOLD_BOUNDED` + faithfulness loophole **closed**

**Blob** `8ef2aebf024c6d4c17a3ebfea963986debf8f1de` (`274.lean`).

```lean
@[category research open, AMS 20]
theorem herzog_schonheim {G : Type*} [Group G] (hG : 1 < ENat.card G) {ι : Type*} [Fintype ι]
    (hι : 1 < Fintype.card ι) (P : Group.ExactCovering G ι) :
    ∃ i j, i ≠ j ∧ (P.parts i).index = (P.parts j).index
```

with `Group.ExactCovering` = `parts : ι → Subgroup G`, `reps : ι → G`,
pairwise-disjoint `reps i • parts i`, union `= univ`.

### The predecessor's flagged loophole does not exist

`erdos-hunt.md` noted: "`1 < ENat.card G` admits infinite `G`, where
`Subgroup.index = 0` for infinite index, so any two infinite-index parts
already satisfy the conclusion". That escape is **unreachable**, by B. H.
Neumann's lemma: if a group is covered by finitely many cosets, the cosets of
infinite-index subgroups can be deleted and the rest still cover. Here `ι` is a
`Fintype`, so the cover is finite. If some `H_j` had infinite index, deleting
all infinite-index parts still covers `G`; but then the nonempty coset
`g_j • H_j` meets one of the retained cosets, contradicting `disjoint`. If
*every* part had infinite index the retained family would be empty and could
not cover a nonempty `G`. Hence **every part has finite index**, `index` is a
genuine positive integer throughout, and the declaration is exactly
Herzog–Schönheim for arbitrary groups. **Faithful; no vacuous-satisfaction
escape.** (Upstream has already repaired one different misformalization here:
issue #4045 / PR #4057, "use per-index quantifier to avoid vacuous witness".)

### Structure of any counterexample (classical, re-derived, not claimed new)

Disjointness + covering give `Σ_i 1/[G:H_i] = 1`, and the conclusion fails only
if the `[G:H_i]` are pairwise distinct.

*Index-2 reduction.* Suppose some part has index 2, say `H_1`, with quotient
map `φ : G → C_2`. For `i ≠ 1`, if `H_i ⊄ H_1` then `φ(H_i) = C_2`, so
`g_i • H_i` meets both cosets of `H_1`, in particular `g_1 • H_1` — contradicting
disjointness. So `H_i ≤ H_1` for all `i ≠ 1`, each `g_i • H_i` lies in the
*other* coset `xH_1`, and translating by `x^{-1}` gives an exact cover of `H_1`
by the `k−1` parts `H_i` with indices `[H_1 : H_i] = [G:H_i]/2`, still pairwise
distinct. If `k−1 = 1` that part has index 1 in `H_1`, i.e. index 2 in `G`,
duplicating `[G:H_1]` — contradiction. So a counterexample with **minimal `k`
has no index-2 part.**

*Consequence, computed exactly.* Distinct indices `≥ 2` with `Σ 1/n_i = 1`
force `k ≥ 3` (smallest set `{2,3,6}`; 486 such sets with `n_i ≤ 60, k ≤ 7`).
With **no index 2**, i.e. distinct `n_i ≥ 3`: `k ≥ 5`, and the *unique* `k = 5`
set with `n_i ≤ 60` is `{3,4,5,6,20}` (102 sets total for `k ≤ 7`). So a
minimal counterexample has at least 5 parts and, at `k = 5`, `|G|` divisible by
`lcm(3,4,5,6,20) = 60`.

### Bounded finite search (`<scratch>/e274.py`)

Exact: permutation representations, full subgroup enumeration by closure, all
left cosets, then exact-cover DFS over the admissible distinct-index sets
(cover the least uncovered element; one coset per index value).

| family | groups tested | orders | distinct-index sets explored | counterexamples |
|---|---|---|---|---|
| all subgroups of `S₅` of order ≥ 6 | 78 | 6, 8, 10, 12, 20, 24, 60 | 81 | **0** |
| `D_n` (order `2n ≡ 0 mod 6`), `n = 3..33` + `C_n` | 11 | 6, 12, 18, 24, 30, 36, 42, 48, 54, 60, 66 | 71 | **0** |

`S₅` itself (order 120) and `D₃₆` (order 72) are **`TIMEOUT_BRACKET`s** — the
subgroup-closure enumeration exceeded the 50 s cap; they were not tested.

**Verdict: `HOLD_BOUNDED`** over the 89 groups above, plus a recorded
faithfulness resolution (Neumann's lemma closes the `ENat.card` loophole) and
the `k ≥ 5` / `{3,4,5,6,20}` narrowing. Herzog–Schönheim is a well-known open
conjecture with far larger verifications in the literature (and the abelian
case is proved and already linked in this file), so the numbers are calibration
only. The prior-art stop recorded by the predecessor stands.

**Duplicate check.** "274": #4045 (closed, misformalization), #4057 (merged,
fix), #4415 (merged, `formal_proof` link for the abelian variant), #2409
(merged, fix). Nothing claiming a counterexample. No upstream action taken.

## F7 — Erdős 1055, `variants.selfridge_limit` — `CERTIFICATE_SHAPE_FAIL` + **new formalization defect in `IsOfClass`**

**Blob** `4835f12e96d618c7e9014f31a85f7549baf2ab79` (`1055.lean`).

**Certificate shape (confirms the predecessor).** `selfridge_limit : ∃ M, ∀ r,
(p r : ℝ) ^ (1/r : ℝ) ≤ M` is an existentially quantified global constant;
refuting it means ruling out every `M`. Not a finite object.
`erdos_1055` (`{p | Prime ∧ IsOfClass r p}.Infinite`) and
`variants.erdos_limit` (`Tendsto … atTop`) are likewise infinitary. Strict stop.

### But the underlying definition is wrong at `r = 2`

**Source (erdosproblems.com/1055, `open`/`OPEN`).** "A prime `p` is in class 1
if the only prime divisors of `p+1` are 2 or 3. In general, a prime `p` is in
class `r` if every prime factor of `p+1` is in some class `≤ r−1`, with
equality for at least one prime factor. … The sequence `p_r` begins
**2, 13, 37, 73, 1021** (A005113 in the OEIS)."

The classes are a *partition* of the primes (that is what makes `p_r` a
well-defined sequence and A005113 the sequence it is). The Lean

```lean
def IsOfClass : ℕ+ → ℕ → Prop := fun r ↦
  PNat.caseStrongInductionOn r
    (fun p ↦ (p + 1).primeFactors ⊆ {2, 3})
    (fun n H p ↦ (∀ r ∈ (p + 1).primeFactors, ∃ (m : ℕ+) (hm : m ≤ n), H m hm r) ∧
                 (∃ r ∈ (p + 1).primeFactors, ∀ (m : ℕ+) (hm : m ≤ n), H m hm r → m = n))
```

never excludes "`p` is already of class 1", so **the classes are not
exclusive**. Concretely, for any class-1 prime `p`, every prime factor `q` of
`p+1` lies in `{2,3}`, and both 2 and 3 are class 1, so both conjuncts of the
`r = 2` clause are satisfied: **every class-1 prime also satisfies
`IsOfClass 2`.**

Exact computation (`<scratch>/e1055.py`, two independent transcriptions — the
source recursion `class(p) = 1 + max_{q | p+1} class(q)` and the literal Lean
clause):

| r | source `p_r` (A005113) | Lean `p r = Nat.find (exists_p r)` |
|---|---|---|
| 1 | 2 | 2 |
| 2 | **13** | **2** ← wrong |
| 3 | 37 | 37 |
| 4 | 73 | 73 |
| 5 | 1021 | 1021 |
| 6 | 2917 | 2917 |

Primes `< 60` carrying two Lean classes: 2, 3, 5, 7, 11, 17, 23, 31, 47, 53 —
all of them genuinely class 1, all also satisfying `IsOfClass 2`.

**Extent of the damage, checked exactly.** Over all 2,262 primes `< 20,000`:
the Lean class set of `p` is exactly `{true class}`, together with `{2}` when
the true class is 1 — **0 deviations**. So `IsOfClass r = ` true class `r` for
every `r ≠ 2`, and `IsOfClass 2 = ` (true class 1) ∪ (true class 2). The reason
is structural: `IsOfClass 3 p` needs a prime factor `q` of `p+1` whose Lean
class set meets `[1,2]` in exactly `{2}`, and a class-1 `q` has Lean class set
`{1,2}`, so the contamination cannot propagate past `r = 2`.

**Consequence, stated precisely.** `p 2 = 2` instead of 13, so the Lean's `p`
is **not** the source's `p_r` / A005113. Because the two open declarations
(`erdos_limit`, `selfridge_limit`) are asymptotic in `r` and `∃M`-quantified, a
single corrupted index does not change either truth value — so this is a
**definition-faithfulness defect, not a counterexample**. §A6 coordinate (3):
the declaration's definition diverges from its cited source; coordinates (1)
and (4) are unaffected.

**Verdict:** `CERTIFICATE_SHAPE_FAIL` for all three open declarations in the
file, **plus** a recorded band-1 defect: `IsOfClass` makes classes non-exclusive
at `r = 2`, so `Erdos1055.p 2 = 2 ≠ 13 = p_2`.

**Duplicate check.** "1055": #1098 (closed, statement request), #3306 / #2790 /
#3373 (closed, `variants.class_one_infinite` solves). Nothing raising the
non-exclusive-class defect. The file's own TODO ("formalize the rest of the
problems on the page") is unrelated. No upstream action taken.

## F8 — the nine remaining candidates: strict stops, each re-derived from the Lean text

All nine were `CANDIDATE_FOR_DEPTH` in the predecessor's triage and marked
"deprioritised" without a completed certificate-shape derivation. Each is now
derived from the declaration text at the pinned blob, compared against the live
source page, and closed. Blob SHAs in the table.

| decl | blob | site state / prize | verdict |
|---|---|---|---|
| 189 `variants.parallelogram` | `11765f54…` | `solved` / `DISPROVED (LEAN)` (parallelogram case explicitly still open) | `CERTIFICATE_SHAPE_FAIL` |
| 241 `variants.generalization` | `0f767411…` | `open` / `OPEN` | `CERTIFICATE_SHAPE_FAIL` |
| 349 `complete_for_alpha_in_Ioo_one_to_goldenRatio` | `2a95c8a8…` | `open` / `OPEN` | `CERTIFICATE_SHAPE_FAIL` |
| 535 `variants.sunflower_strong` | `720d2187…` | `open` / `OPEN` | `CERTIFICATE_SHAPE_FAIL` |
| 617 `erdos_617` | `00d6f622…` | `open` / **`FALSIFIABLE`** | finite negation, `KNOWN_PROOF_DOMAIN` / prior-art stop |
| 1041 `erdos_1041` | `0bd296db…` | `open` / **`FALSIFIABLE`** | `CERTIFICATE_SHAPE_FAIL` (finite witness, non-finite verification) |
| 1044 `variants.fixed_degree` | `2ab25808…` | `solved` / `SOLVED (LEAN)` (fixed-degree part open) | `CERTIFICATE_SHAPE_FAIL` |
| 1113 `variants.filaseta_finch_kozek` | `4448a7e6…` | `open` / `OPEN` | `CERTIFICATE_SHAPE_FAIL` |
| 1135 `erdos_1135` | `e285a2e1…` | `open` / `OPEN` | finite negation (a cycle), prior-art stop |

**189 `parallelogram`.** The declaration is `¬ Erdos189For (parallelogram) (area)`.
Its negation is `Erdos189For …` = "for every finite colouring of `ℝ²` some
colour class contains a monochromatic parallelogram of every positive area" — a
`∀`-statement over all colourings of `ℝ²`. No finite certificate. Two notes:
(i) the site confirms the parallelogram case is open ("This is false; Kovač
[Ko23] provides an explicit colouring … The question for parallelograms remains
open"), so the `research open` label is correct; (ii) the declaration asserts
the **negative** branch of an open question with nothing in the docstring
("Seems to be open, as of January 2025") supporting that direction — the same
answer-shape pattern as F2, but here it is at least in line with the settled
rectangle and rhombus cases. The area function `dist a b * dist b c * (∡ a b c).sin`
is the correct parallelogram area, and `IsCcwConvexPolygon ![a,b,c,d]` makes
`ab ∥ cd`, `ad ∥ bc` the genuine opposite-side condition. No divergence.

**241 `generalization`.** `BoseChowlaConjecture r = (fun N ↦ f N r) ~[atTop]
(fun N ↦ N ^ (1/r))` — an asymptotic equivalence; refutation needs a rate over
all large `N`. Site matches verbatim ("Bose and Chowla conjectured … `|A| ∼
N^{1/r}` … known only for `r = 2`"), and `f N r` (multisets of card `r`, equal
sums forced equal as multisets) is the correct "aside from the trivial
coincidences" reading. No divergence.

**349 `complete_for_alpha_in_Ioo_one_to_goldenRatio`.** `IsAddComplete A =
∀ᶠ k in atTop, k ∈ subsetSums A`, so its negation is "infinitely many `k` are
not a subset sum" — not a finite object; and `t, α` range over ℝ. Site matches
verbatim, including the golden-ratio endpoint ("It seems likely that the
sequence is complete for all `t>0` and all `1<α<(1+√5)/2`"). No divergence.
Note for the next agent: upstream has **five open PRs** on this file (#4470,
#4476, #4478, #4483, #4485) adding positive results on the strip `1 < α < 3/2`
— an active area, so re-check duplicates before touching it.

**535 `sunflower_strong`.** `∃ c_r > 0, ∀ k, ∀ A, …` — an existentially
quantified global constant; refutation must rule out every `c_r`. (The
predecessor already noted the triage regex missed this because the binder is
`c_r`; confirmed.) Two definitions in the file are deliberately *different* and
both are faithful: `f r N` uses plain constant pairwise gcd, matching the site's
`f_r(N)`; `NoConstantPairwiseGcdCoprimeSubsets` adds coprime quotients, matching
Erdős's stronger `Ω`-based auxiliary conjecture in [Er73]. No divergence.

**617.** Negation *is* finite: one `r ≥ 3` and one `r`-colouring of
`K_{r²+1}` in which every `(r+1)`-subset sees all `r` colours. Site prize is
`FALSIFIABLE`. But METHOD v1.0 already closed this lane at Phase 0: standalone
public artifacts claim computer-assisted proofs for `r = 5..11`, so a
refutation needs `r ≥ 12`, i.e. a balanced 12-colouring of `K_145` — outside any
bounded budget here. Cosmetic wart recorded: `variants.r_eq_3` and
`variants.r_eq_4` both carry an **unused** `(r : ℕ) (hr : r ≥ 3)` binder while
their statements use the literals 3 and 4; harmless, but the binder is dead.

**1041.** The witness for the negation would be a single polynomial — finite —
but the property to be certified is "**no** path of length `< 2` inside
`{|f| < 1}` joins two roots", a statement about an uncountable path space. Not
a replayable finite check, so it fails the METHOD Phase-0A gate even though the
site marks the problem `FALSIFIABLE`; this is a triage-boundary disagreement,
recorded rather than resolved. Faithfulness note: `({z₁, z₂} : Multiset ℂ) ≤
f.roots` permits `z₁ = z₂` at a root of multiplicity `≥ 2`, and then the
constant path has `μH[1] (range γ) = 0 < 2` with `‖f.eval z₁‖ = 0 < 1` — so the
declaration is **trivially true for every polynomial with a repeated root**.
The sibling `exists_connected_component_contains_two_roots` says "two roots
with multiplicity", so this is internally consistent; but a counterexample
search would be confined to squarefree `f`, and the source's "two of the roots"
more likely means two distinct roots. Recorded as a weakening, not a defect.

**1044 `fixed_degree`.** `IsLeast {L | ∃ f, IsAdmissible f ∧ f.natDegree = n ∧
maxBoundaryLength f = L} (maxBoundaryLength (X^n − 1))` — refuting it means
either exhibiting an admissible `f` of degree `n` with strictly smaller maximum
component-boundary Hausdorff measure (an analytic quantity, not a finite
computation) or showing the value is not attained. No finite certificate.
Faithfulness clean: site says Tang "suggests" exactly this and proves `n = 1,2`,
which is precisely how the file splits `fixed_degree` (open) from
`fixed_degree_of_le_two` (solved); `X^n − 1 = ∏(X − ζ^i)` with `|ζ^i| = 1` is
admissible under `IsAdmissible` (`‖z i‖ ≤ 1`, non-strict) ✓.

**1113 `filaseta_finch_kozek`.** Negation needs a `k` that is (a) proved
Sierpiński — itself a `∀ n` compositeness claim — (b) proved to have **no**
finite covering set, and (c) not a perfect power. (b) is not finitely
certifiable. Definitions check out: `Nat.IsSierpinskiNumber k = ¬2∣k ∧ ∀ n,
(k*2^n+1).Composite` matches the site's "positive odd `m` such that none of
`2^k m + 1` are prime"; `HasFinitePrimeCoveringSet` matches "every `2^k m + 1`
is divisible by some `p ∈ P`"; and `Nat.IsPerfectPower n ↔ n > 1 ∧
n.primeFactors.gcd n.factorization > 1` is a proper perfect-power predicate
with **no** `k = k^1` loophole (checked: `¬IsPerfectPower 0/1/2` are `decide`d
in `FormalConjecturesForMathlib/Data/Nat/PerfectPower.lean`). The site's own
evidence example, `m = 734110615000775^4`, is a perfect power, consistent with
the FFK conjecture as stated. No divergence.

**1135.** `type_of% CollatzConjecture.collatz_conjecture`, i.e.
`∀ n > 0, ∃ m, collatzStep^[m] n = 1` with `collatzStep n = if Even n then n/2
else 3*n+1`. A cycle avoiding 1 would be a finite certificate, so this is
finitely refutable in principle — prior-art stop (verified past `2^68`).
Faithfulness note: the site states the **shortcut** map `f(n) = n/2` (even),
`(3n+1)/2` (odd), while the Lean uses the unaccelerated `3n+1`. These are
equivalent for the property in question, because `3n+1` is even whenever `n` is
odd, so one shortcut step equals two unaccelerated steps and the two orbits hit
1 together. Not a defect.

