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

