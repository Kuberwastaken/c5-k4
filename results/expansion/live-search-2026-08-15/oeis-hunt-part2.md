# OEIS open-declaration counterexample hunt — Part 2 (ids >= 130000)

**Date:** 2026-08-15 UTC
**Corpus:** `google-deepmind/formal-conjectures`, pinned commit `2411d22e1bd550d050d0eac6c1fb379a76a3e7c5`
(`upstream/main`, 2026-08-14 19:16:38 +0000), read via `git show upstream/main:<path>`.
**Target list:** `results/expansion/open_targets_oeis_erdos_20260815.json`, `corpus == "OEIS"`,
ids sorted ascending, second half (`id >= 130000`).
**Skipped:** A231201 (`previously_touched == true`).
**Method gates:** `METHOD.md` v1.0 — Phase 0A certificate shape, Phase 0B provenance freeze,
Phase 7 candidate verification. 60-second hard cap on every computation.
**Publication:** none. No upstream issue/PR/comment opened. Local records only.

## HANDOFF STATE (written 2026-08-15, agent replaced mid-run)

**Assigned share:** the 14 `corpus == "OEIS"` entries with `id >= 130000`, minus A231201
(`previously_touched == true`) = **13 targets**.

### Completed (9 of 13) — full write-ups below

| id | verdict | counterexample? |
|---|---|---|
| A167604 | `CERTIFICATE_SHAPE_FAIL` / NOT_FINITELY_REFUTABLE (`answer(sorry)`) | no |
| A211417 | `HOLD_BOUNDED` to n=3000 + trivially-true `general_divisibility` (**duplicate of upstream open issue #4923**) | no |
| A228828 | `CERTIFICATE_SHAPE_FAIL` / NOT_FINITELY_REFUTABLE (`Set.Infinite`) | no |
| A232174 | `HOLD_BOUNDED` to n=60000; + novel `SOURCE_ERRATUM` in the OEIS comment (n=66) | no |
| A237271 | **`FORMALIZATION_DEFECT / VACUOUS_PREMISE` — NOVEL**, hypothesis satisfied by no k | no (vacuously true) |
| A239957 | `HOLD_BOUNDED` — all 25,997 primes ≤ 300,000 | no |
| A280831 | `HOLD_BOUNDED` — n = 0..43,772 | no |
| A281976 | `HOLD_BOUNDED` — n = 0..781,629 | no |
| A287616 | `HOLD_BOUNDED` — n = 0..30,000,000; + `STATUS_SYNC` (proved 2026, **duplicate of upstream open issue #4927**) | no |

### Mid-way when stopped

**A287616** was fully computed and verified (n ≤ 3·10^7, no gaps; representation counts match OEIS
DATA(0..80) exactly). Only its formatted section was outstanding — it is written below in full.
Nothing was left unresolved on it.

### UNSTARTED (4 of 13) — Lean file and OEIS entry already read; findings recorded below

- **A303656** — Sun, `n = a²+b²+3^c+5^d` for `n > 1`. Encoding verified faithful (OEIS adds
  `a <= b`, a harmless normalization). Finitely refutable. Verified by Sun/Lin to 2.4·10^11.
  **No computation run.**
- **A306477** — Sun 2-4-6-8 conjecture. Encoding verified faithful (Lean's `C(w+2,2)`, `C(x+3,4)`,
  `C(y+5,6)`, `C(z+7,8)` with `w,x,y,z : ℕ` generate exactly the same value sets as the source's
  `C(w,2)+C(x,4)+C(y,6)+C(z,8)` with `w,x,y,z ∈ {2,3,...}`; I checked this by hand, see notes below).
  Verified by Baruch to 2·10^12. **No computation run.**
- **A308734** — Sun four-square, `(2^a·3^b)² + (2^c·5^d)² + x² + y²` for `n > 1`. Encoding faithful
  (OEIS adds `x <= y`, harmless). Verified by Lin to 1.6·10^11. **No computation run.**
- **A357513** — `general_supercongruence`. **Shape analysis done: NOT finitely refutable** — the
  declaration is `∃ (exceptions : Finset ℕ), ∀ p prime, p ∉ exceptions → ...`, so refuting it
  requires infinitely many failing primes. Also a `STATUS_SYNC`: the OEIS entry now records
  *"This conjecture is now proved; see Links"* (Ondrej Kutal, Jul 18 2026, **with Lean
  formalization**), while the declaration is still `category research open` upstream.
  See notes below. **No computation needed; this one can be closed on shape alone.**

### Candidate counterexamples

**None.** Zero refuting integers were found in nine completed targets. The two substantive findings
are statement defects, not counterexamples, and one of the two is already reported upstream.
There is **no UNVERIFIED candidate** pending.

### Notes that will save the next agent time

1. **OEIS fetching.** Plain `curl` on `https://oeis.org/search?...&fmt=text`, `/A<id>`,
   `/A<id>/internal` and `/A<id>/list` all return **403 (Cloudflare challenge)**. Two things work:
   - a browser User-Agent on the plain page:
     `curl -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36" https://oeis.org/A<id>` → 200. Strip tags to text.
   - **b-files are static and need no UA**: `https://oeis.org/A<id>/b<id>.txt` → 200.
2. **Always run Python with `-u`.** A timed-out buffered script prints nothing at all and looks like
   a hang. Also: `while n % 4 == 0: n //= 4` is an infinite loop at `n = 0` — guard it.
3. **Dead-end declaration shapes** (stop at METHOD G0, do not compute):
   - `answer(sorry) ↔ …` (fixed-answer class) — A167604.
   - `Set.Infinite` / "the sequence is infinite" — A228828.
   - `∃ (exceptions : Finset ℕ), ∀ p, …` — A357513.
   These three consumed no compute and should not be reopened.
4. **The productive shape in this half is `∃`-witness Sun conjectures** (`∀ n, ∃ x y z w, …`), which
   *are* finitely refutable — but every one of them has been machine-verified by the proposers to
   10^8–10^12, so a small-`n` sweep is calibration, not a realistic kill. The realistic vein here
   was **defective quantifiers**, and that is where both findings came from
   (`∃ D : ℤ` with no `D ≠ 0`; `∀ a : ZMod k, a ≠ 0` instead of `∀ a` coprime to `k`).
5. **Two upstream open issues already collect this class of defect** — read them before claiming
   novelty on any statement defect:
   - #4896 "Tracking: possible misformalizations found in statement audits"
   - #4923 "Possible misformalizations II" (contains the A211417 `D = 0` item verbatim)
   - #4927 "Open statements with known solutions" (contains the A287616 item)
6. **Scripts written** (all in
   `/tmp/claude-1000/-Users-kuber-mehta-Projects-scratch/21f73cfa-6e97-457f-8bb8-ae31d911cc43/scratchpad/`,
   a session-scoped scratchpad that will not survive — copy anything you want to keep):
   `a167604.py`, `a211417.py`, `a211417b.py`, `a232174.py` (counts), `a232174b.py` (DATA
   cross-check), `a232174c.py` (existence sweep), `a237271.py`, `a239957.py`, `a280831b.py`
   (existence, Gauss–Legendre-reduced), `a280831c.py` (DATA calibration), `a281976.py`,
   `a287616.py` / `a287616b.py` (big-int bitset convolution — this technique covers 3·10^7 in 36 s
   and is the right tool for any "sum of three polygonal numbers" target).
   Fetched OEIS pages/text are in the sibling `oeis/` subdirectory.
7. **Python env:** `/home/ec2-user/.venvs/wowii/bin/python`. **`sympy` is NOT installed** — write
   your own `isqrt`/Miller–Rabin/factorization helpers.

---

## Running summary

| # | OEIS | Lean file | open decls | certificate shape | verdict | refuting integer |
|---|---|---|---|---|---|---|
| 1 | A167604 | `OEIS/167604.lean` | 1 (`answer(sorry)`) | fixed-answer placeholder | `CERTIFICATE_SHAPE_FAIL` | — |
| 2 | A211417 | `OEIS/211417.lean` | 6 | finite universal ×5, degenerate ∃ ×1 | `HOLD_BOUNDED` + defect (dup #4923) | — |
| 3 | A228828 | `OEIS/228828.lean` | 1 | infinitude | `CERTIFICATE_SHAPE_FAIL` | — |
| 4 | A232174 | `OEIS/232174.lean` | 1 | finite universal | `HOLD_BOUNDED` (n ≤ 60000) + OEIS erratum n=66 | — |
| 5 | A237271 | `OEIS/237271.lean` | 1 | finite universal, **empty domain** | **`FORMALIZATION_DEFECT / VACUOUS_PREMISE` (novel)** | — (vacuously true) |
| 6 | A239957 | `OEIS/239957.lean` | 1 | finite universal | `HOLD_BOUNDED` (all p ≤ 300000) | — |
| 7 | A280831 | `OEIS/280831.lean` | 1 | finite universal | `HOLD_BOUNDED` (n ≤ 43772) | — |
| 8 | A281976 | `OEIS/281976.lean` | 1 | finite universal | `HOLD_BOUNDED` (n ≤ 781629) | — |
| 9 | A287616 | `OEIS/287616.lean` | 1 | finite universal | `HOLD_BOUNDED` (n ≤ 3·10^7) + `STATUS_SYNC` (dup #4927) | — |
| 10 | A303656 | `OEIS/303656.lean` | 1 | finite universal | **UNSTARTED** (faithful encoding confirmed) | — |
| 11 | A306477 | `OEIS/306477.lean` | 1 | finite universal | **UNSTARTED** (faithful encoding confirmed) | — |
| 12 | A308734 | `OEIS/308734.lean` | 1 | finite universal | **UNSTARTED** (faithful encoding confirmed) | — |
| 13 | A357513 | `OEIS/357513.lean` | 1 | `∃ Finset` exceptions | **`CERTIFICATE_SHAPE_FAIL` + `STATUS_SYNC`** (analysis below, no compute needed) | — |

---

## 1. A167604 — Chua / Euclid–Mullin variant

**Lean file:** `FormalConjectures/OEIS/167604.lean` (2243 bytes, 1 `answer(sorry)`, 1 `category research open`).
**OEIS:** <https://oeis.org/A167604>

### Verbatim open declaration

```lean
/-- Does Chua's sequence contain every prime? -/
@[category research open, AMS 11]
theorem conjecture :
    answer(sorry) ↔ ∀ p : ℕ, p.Prime → ∃ n ≥ 1, a n = p := by
  sorry
```

with

```lean
def next (n : ℕ) : ℕ := Nat.minFac (∏ d ∈ n.divisors, (d + n / d))
def product : ℕ → ℕ | 0 => 1 | n + 1 => product n * next (product n)
def a : ℕ → ℕ | 0 => 1 | n + 1 => next (product n)
```

### OEIS ground truth

- NAME: "A variant of Euclid-Mullin (A000945): a(1)=2, a(n+1) is the least prime dividing
  [Product_{i in I} a(i) + Product_{i in I'} a(i)], minimized over all subsets I of {1..n}."
- OFFSET: 1,1
- DATA (first 14): `2, 3, 5, 11, 37, 13, 7, 29, 17, 19, 43, 23, 47, 41`
- COMMENT: "By Euclid's argument, the terms are distinct." / "One can ask whether all primes occur
  in this sequence."
- MAPLE program in the entry uses exactly the divisor form
  `p:=proc(N) ... for d in divisors(N) while d^2<=N do S:=S, divisors(d+N/d)[2] od : return(min(S))`.

### Faithfulness check (Phase 0B)

Subset-product form and divisor form agree because the terms are distinct primes, so the total
product is squarefree and its divisors are exactly the subset products; the OEIS entry's own Maple
code uses the divisor form. `Nat.minFac (∏ (d + n/d)) = min_d Nat.minFac (d + n/d)` because every
factor is `>= 2`.

Independent recomputation (subset enumeration over the distinct primes, not the divisor helper):

```
Lean-a(1..14): [2, 3, 5, 11, 37, 13, 7, 29, 17, 19, 43, 23, 47, 41]
OEIS a(1..14): [2, 3, 5, 11, 37, 13, 7, 29, 17, 19, 43, 23, 47, 41]
MATCH: True
```

The Lean `a` is faithful to A167604 (with the harmless extension `a 0 = 1`; Lean `a n` = OEIS `a(n)`
for `n >= 1`).

### Certificate shape (METHOD G0 / Phase 0A)

`answer(sorry) ↔ P` is the fixed-answer class. Its literal negation is not a finite object, and the
right-hand side `∀ p prime, ∃ n >= 1, a n = p` is a `∀∃` statement over an unbounded sequence: a
finite artifact can witness membership of finitely many primes but can never refute the universal.
No finite integer can settle it.

### Verdict

`CERTIFICATE_SHAPE_FAIL` / **NOT_FINITELY_REFUTABLE**. No formalization defect found; the Lean
definition reproduces the OEIS DATA exactly. Not carried further.

---

## 2. A211417 — integral factorial ratio (30n)!n!/((15n)!(10n)!(6n)!)

**Lean file:** `FormalConjectures/OEIS/211417.lean` (4663 bytes, 6 `category research open`).
**OEIS:** <https://oeis.org/A211417>

### Verbatim open declarations

```lean
def a (n : ℕ) : ℕ :=
  (Nat.factorial (30 * n) * Nat.factorial n) /
  (Nat.factorial (15 * n) * Nat.factorial (10 * n) * Nat.factorial (6 * n))

def coprimeIndices (r : ℕ) : Finset ℕ :=
  (Finset.range (r + 1)).filter (fun i => 1 ≤ i ∧ Nat.gcd i 30 = 1)

def divisorProduct (n r : ℕ) : ℤ :=
  (coprimeIndices r).prod (fun i : ℕ => 30 * (n : ℤ) - (i : ℤ))

@[category research open, AMS 11]
theorem seven_mul_a_dvd_two_mul_add_one (n : ℕ) : (2 * (n : ℤ) + 1) ∣ 7 * (a n : ℤ)

@[category research open, AMS 11]
theorem a_dvd_three_mul_add_one (n : ℕ) : (3 * (n : ℤ) + 1) ∣ (a n : ℤ)

@[category research open, AMS 11]
theorem a_dvd_five_mul_add_one (n : ℕ) : (5 * (n : ℤ) + 1) ∣ (a n : ℤ)

@[category research open, AMS 11]
theorem forty_two_mul_a_dvd_product (n : ℕ) :
    ((2 * (n : ℤ) + 1) * (3 * (n : ℤ) + 1) * (5 * (n : ℤ) + 1)) ∣ 42 * (a n : ℤ)

@[category research open, AMS 11]
theorem general_divisibility (r : ℕ) (hr : 1 ≤ r) :
    ∃ D : ℤ, ∀ n : ℕ, (divisorProduct n r) ∣ (D * (a n : ℤ))

@[category research open, AMS 11]
theorem supercongruence (p k : ℕ) (hp : p.Prime) (hp5 : 5 ≤ p) (hk : 0 < k) :
    (p : ℤ) ^ (3 * k) ∣ ((a (p ^ k) : ℤ) - (a (p ^ (k - 1)) : ℤ))
```

### OEIS ground truth

- NAME: "Integral factorial ratio sequence: a(n) = (30*n)!*n!/((15*n)!*(10*n)!*(6*n)!)"
- OFFSET: 0,2
- DATA: `1, 77636318760, 53837289804317953893960, 43880754270176401422739454033276880,
  38113558705192522309151157825210540422513019720,
  34255316578084325260482016910137568877961925210286281393760`
- COMMENT (Peter Bala, Aug 28 2025): "Conjectures: 7*a(n)/(2*n + 1), a(n)/(3*n + 1), a(n)/(5*n + 1)
  and 42*a(n)/((2*n + 1)*(3*n + 1)*(5*n + 1)) are integers for all n (checked up to n = 1000)."
- COMMENT: "for r >= 1, we conjecture that there exists a **constant** D(r) such that
  D(r)*a(n)/Product_{i = 1..r, i coprime to 30} (30*n - i) is integral for all n."
- COMMENT (Peter Bala, Jan 24 2020): "a(p^k) == a(p^(k-1)) ( mod p^(3*k) ) for any prime p >= 5 and
  any positive integer k."
- Integrality of a(n) is proved (Bala link), so the Lean `ℕ`-division never truncates.

### Computation (two independent paths)

Path 1: exact big-int `(30n)! n! / ((15n)!(10n)!(6n)!)`; Path 2: `p`-adic valuations via Legendre's
formula, `v_p(a n) = v_p((30n)!) + v_p(n!) − v_p((15n)!) − v_p((10n)!) − v_p((6n)!)`.

```
A211417 DATA n=0..5 reproduced exactly by big-int path: OK
Legendre valuation path agrees with big-int factorization for n=1..4: OK
n range 0..3000
  7a/(2n+1)                      failures: NONE
  a/(3n+1)                       failures: NONE
  a/(5n+1)                       failures: NONE
  42a/((2n+1)(3n+1)(5n+1))       failures: NONE
```

This extends Bala's reported range (n <= 1000) to **n <= 3000** with no counterexample.

Supercongruence rows (exact, big-int `a(n) = C(30n,15n)*C(15n,5n)/C(6n,n)` cross-checked against the
factorial form):

```
p= 5 k=1 : divisible=True     p= 5 k=2 : divisible=True
p= 7 k=1 : divisible=True     p= 7 k=2 : divisible=True
p=11 k=1 : divisible=True     p=11 k=2 : divisible=True
p=13 k=1 : divisible=True     p=17 k=1 : divisible=True
p=19 k=1 : divisible=True     p=23 k=1 : divisible=True
general form a(n*p^k) == a(n*p^(k-1)) mod p^(3k): True for p in {5,7,11}, n in {1,2,3}, k=1
```

### Formalization defect found (not a counterexample)

`general_divisibility` is **trivially true**: `D : ℤ` is unconstrained, and `D = 0` gives
`divisorProduct n r ∣ 0` for every `n`, closed by `⟨0, fun n => by simp⟩`. The OEIS source says
"there exists a **constant** D(r)" in a context where `D(r) ≠ 0` is intended (`D(r)*a(n)/Prod` must be
*integral*, i.e. the quotient is a genuine integer). The Lean statement therefore does not encode the
conjecture.

`coprimeIndices` values (verified): `r=1..6 -> {1}`, `r=7..10 -> {1,7}`, `r=11,12 -> {1,7,11}`,
`r=13 -> {1,7,11,13}`.

**Duplicate status: ALREADY REPORTED.** Upstream open issue
[#4923 "Possible misformalizations II"](https://github.com/google-deepmind/formal-conjectures/issues/4923)
contains the exact item: *"OEIS A211417 `general_divisibility` — Problem: choose `D = 0`; every
integer divides zero, so `⟨0, fun n => by simp⟩` closes the theorem."* Not novel.

### Minor documentation defect (novel, cosmetic)

The module docstring header of `211417.lean` reads
"`Integrality and supercongruences of the factorial ratio $\frac{(6n)! n!}{(3n)! (2n)!^2}$`",
which is a different factorial ratio from the one the file actually defines
(`(30n)! n! / ((15n)! (10n)! (6n)!)`). The body of the same docstring states the correct formula.
Cosmetic only; no declaration is affected.

### Verdict

`HOLD_BOUNDED` for the five substantive divisibility/supercongruence declarations
(no counterexample for `n <= 3000`, and the supercongruence rows tested).
`general_divisibility`: trivially-true formalization defect, **duplicate of upstream issue #4923**.
No new counterexample.

---

## 3. A228828 — numbers n with n² + π(n) prime

**Lean file:** `FormalConjectures/OEIS/228828.lean` (1633 bytes, 1 `category research open`).
**OEIS:** <https://oeis.org/A228828>

### Verbatim open declaration

```lean
noncomputable def a (n : ℕ) : ℕ := n.nth (fun n => (n ^ 2 + π n).Prime)

/-- Conjecture: the sequence A228828 is infinite. -/
@[category research open, AMS 11]
theorem conjecture : {a n | n}.Infinite := by
  sorry
```

### OEIS ground truth

- NAME: "Numbers n such that n^2 + pi(n) is prime."
- OFFSET: 1,1
- DATA: `2, 3, 7, 12, 18, 21, 36, 37, 42, 45, 52, 55, 60, 61, 65, 68, 70, 79, 84, 95, 98, 113, 130, ...`
- COMMENT: "Conjecture: the sequence is infinite."

`Nat.nth` is 0-indexed, so Lean `a 0 = 2 = ` OEIS `a(1)`; the shift is harmless and the test lemmas
`a_0 = 2`, `a_1 = 3`, `a_2 = 7` agree with the DATA. Faithful.

### Certificate shape (METHOD G0 / Phase 0A)

`Set.Infinite` on an image set. Its literal negation is "the set is finite", which is not exhibited by
any finite integer artifact — a finite computation can only produce more members, never exclude all
further ones. `Nat.nth` returns `0` past the end of a finite predicate set, so the declaration is
exactly the intended infinitude statement.

### Verdict

`CERTIFICATE_SHAPE_FAIL` / **NOT_FINITELY_REFUTABLE**. No formalization defect. Not carried further.

---

## 4. A232174 — Zhi-Wei Sun, x + n·y and x² + n·y² both prime

**Lean file:** `FormalConjectures/OEIS/232174.lean` (2458 bytes, 1 `category research open`).
**OEIS:** <https://oeis.org/A232174> · $200 prize.

### Verbatim open declaration

```lean
def A (n : ℕ) : Prop :=
  ∃ x y : ℕ, 0 < x ∧ 0 < y ∧ n = x + y ∧ (x + n * y).Prime ∧ (x ^ 2 + n * y ^ 2).Prime

@[category research open, AMS 11]
theorem conjecture (n : ℕ) (hn : 1 < n) : A n := by
  sorry
```

### OEIS ground truth

- NAME: "Number of ways to write n = x + y (x, y > 0) with x + n*y and x^2 + n*y^2 both prime."
- OFFSET: 1,3
- COMMENT: "Conjecture: (i) a(n) > 0 for all n > 1. Also, a(n) = 1 only for
  n = 2, 5, 8, 14, 19, 20, 24, 32, 54, 68, 101, 168."
- DATA (100 terms): `0, 1, 2, 2, 1, 2, 3, 1, 2, 2, 3, 2, 5, 1, 4, 3, 2, 2, 1, 1, 2, 5, 4, 1, 7, ...`

The Lean statement is a faithful encoding of conjecture (i): the hypothesis `1 < n` matches
"for all n > 1"; `0 < x`, `0 < y` match "(x, y > 0)"; the two primality conditions match verbatim.

### Computation

Exact recount of `a(n)` for `n = 1..100` (deterministic Miller–Rabin plus trial division as a second
path) reproduces the full 100-term OEIS DATA with **zero** differences.

Existence search under the exact Lean statement:

```
A232174 existence check n=2..20000 : failures = NONE  (5.8s)
A232174 existence check n=2..60000 : failures = NONE  (29.5s)
```

No `n` in `2..60000` falsifies the declaration.

### OEIS source erratum found (novel; not in the Lean file)

The OEIS COMMENT claims `a(n) = 1` **only** for `n = 2, 5, 8, 14, 19, 20, 24, 32, 54, 68, 101, 168`.
Recomputation and the OEIS DATA itself both give `a(66) = 1` (the 66th DATA term is `1`):

```
n<=100 with OEIS a(n)==1: [2, 5, 8, 14, 19, 20, 24, 32, 54, 66, 68]
```

The witness is `n = 66`. Its **unique** representation is `66 = 53 + 13` with
`53 + 66*13 = 911` prime and `53² + 66*13² = 13963` prime; exhaustive enumeration over
`x = 1..65` finds exactly one. **`n = 66` is missing from the comment's list.**
Classification: `SOURCE_ERRATUM` in the OEIS comment, self-contradicted by the same entry's
DATA. This secondary claim is **not formalized in Lean**, so it does not refute any declaration.

### Verdict

`HOLD_BOUNDED` — no counterexample to the Lean declaration for `2 <= n <= 60000`; encoding is
faithful. One `SOURCE_ERRATUM` recorded against the OEIS comment (n = 66), with no upstream Lean
consequence.

---

## 5. A237271 — parts in the symmetric representation of σ(n) (Carmichael observation)

**Lean file:** `FormalConjectures/OEIS/237271.lean` (6976 bytes, 1 `category research open`).
**OEIS:** <https://oeis.org/A237271>

### Verbatim open declaration

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

with

```lean
def a (n : ℕ) : ℕ :=
  let divs_list : List ℕ := (n.divisors.sort (· ≤ ·))
  let consecutive_pairs : List (ℕ × ℕ) := List.zip divs_list divs_list.tail
  let count : ℕ := consecutive_pairs.countP fun pair =>
    Odd pair.snd ∧ pair.snd ≥ 2 * pair.fst
  1 + count
```

### OEIS ground truth

- NAME: "Number of parts in the symmetric representation of sigma(n)." OFFSET 1,3.
- COMMENT (Omar E. Pol, Oct 21 2025): "Observation: a(A002997(n)) >= 3, at least for 1 <= n <= 10000."
- A002997 = Carmichael numbers = **composite** `k` such that `a^(k-1) ≡ 1 (mod k)` for all `a`
  **coprime to `k`**.

Sequence faithfulness: the Lean `a` reproduces the OEIS DATA exactly for `n = 1..50`:
`[1,1,2,1,2,1,2,1,3,2,2,1,2,2,3,1,2,1,2,1,4,2,2,1,3,2,4,1,2,1,2,1,4,2,3,1,2,2,4,1,2,1,2,2,3,2,2,1,3,3]`.

### FORMALIZATION DEFECT — the hypothesis is unsatisfiable, so the declaration is vacuously true

The Carmichael condition quantifies over residues **coprime to `k`**. The Lean hypothesis instead
quantifies over **every nonzero** `a : ZMod k`. Those are not the same, and the Lean version is
satisfied by no `k` at all:

> Let `k` be composite with `1 < k`, and let `p` be a prime divisor of `k`. Then `1 < p < k`, so
> `(p : ZMod k) ≠ 0`. If `p ^ (k-1) = 1` in `ZMod k` then `p * p ^ (k-2) = 1`, i.e. `p` is a unit of
> `ZMod k`, hence `gcd(p, k) = 1` — contradicting `p ∣ k` and `p > 1`. So the third conjunct fails.
> Conversely the third conjunct forces `ZMod k` to be a field, i.e. `k` prime, contradicting the
> first conjunct. **The hypothesis set is empty.**

Exhaustive computational confirmation (independent code path, direct `pow(x, k-1, k)` over all
`1 <= x < k`):

```
k in 2..20000 satisfying the FULL Lean hypothesis
   (composite AND all nonzero a have a^(k-1)=1): NONE
```

Explicit falsifying witnesses on the first genuine Carmichael numbers (each is a concrete
`(k, a)` pair refuting the Lean premise, in the sense of METHOD Phase 0B item 6):

| k (Carmichael) | witness `a` | `a ≠ 0` in `ZMod k` | `a^(k-1) mod k` | premise |
|---|---|---|---|---|
| 561 = 3·11·17 | 3 | yes | **375** ≠ 1 | FALSE |
| 1105 = 5·13·17 | 5 | yes | **885** ≠ 1 | FALSE |
| 1729 = 7·13·19 | 7 | yes | **742** ≠ 1 | FALSE |
| 2465 = 5·17·29 | 5 | yes | **1480** ≠ 1 | FALSE |
| 2821 = 7·13·31 | 7 | yes | **2016** ≠ 1 | FALSE |

Consequence: `observation_carmichael` as written is provable outright (`exact absurd … `; the
premise contradicts itself) and says nothing about Carmichael numbers. It is a `research open`
declaration that is in fact trivially true.

### The intended statement is not refuted

Under the correct Carmichael definition (`a^(k-1) ≡ 1 mod k` for all `a` with `gcd(a,k)=1`):

```
Carmichael numbers <= 20000: [561, 1105, 1729, 2465, 2821, 6601, 8911, 10585, 15841]
a(k):                        [  5,    6,    4,    6,    6,    6,    7,     7,     8]
min a(k) = 4  >= 3
```

So the OEIS observation holds on every Carmichael number `<= 20000`; the defect is purely in the
formalization, not in the mathematics.

### Novelty / duplicate check

- `gh api search/issues repo:google-deepmind/formal-conjectures Carmichael` → 11 hits, none about
  `237271`/`observation_carmichael` (they concern Carmichael's *totient* conjecture and an unrelated
  `NumberTheory/Carmichael` import fix, #4281).
- `gh api search/issues repo:google-deepmind/formal-conjectures 237271` → **0** hits.
- `gh api search/issues repo:google-deepmind/formal-conjectures A237271` → 1 hit, #4924
  "Mark OEIS A237271 parity conjectures as solved" (closed) — about `conjecture_4`/`conjecture_5`,
  **not** about the Carmichael hypothesis.
- Read in full: open issue #4923 "Possible misformalizations II" and #4896 "Tracking: possible
  misformalizations found in statement audits" — neither lists A237271.
- SearXNG web search (`formal-conjectures A237271 Carmichael vacuous hypothesis`,
  `formal-conjectures observation_carmichael`) → no prior art.

**Status: NOVEL, undiscovered upstream.**

### Verdict

`FORMALIZATION_DEFECT / VACUOUS_PREMISE` — the open declaration's hypothesis is satisfied by no
natural number, so the statement is trivially true and does not encode the OEIS observation.
This is **not** a counterexample (a vacuous universal cannot be refuted); it is a statement defect.
Classification per METHOD: closest ledger label is `PREMISE_FALSE_STRICT` generalized to *all*
instances, i.e. the declaration has an empty applicable domain.
No publication action taken.

---

## 6. A239957 — Zhi-Wei Sun, every prime has a primitive root of the form k² + 1

**Lean file:** `FormalConjectures/OEIS/239957.lean` (1531 bytes, 1 `category research open`).
**OEIS:** <https://oeis.org/A239957> · RMB 2,000 prize.

### Verbatim open declaration

```lean
def A (p : ℕ) : Prop :=
  ∃ k : ℤ, k ^ 2 + 1 < p ∧ orderOf (k ^ 2 + 1 : ZMod p) = p - 1

@[category research open, AMS 11]
theorem conjecture (p : ℕ) (hp : p.Prime) : A p := by
  sorry
```

### OEIS ground truth

- NAME: "a(n) = |{0 < g < prime(n): g is a primitive root modulo prime(n) of the form k^2 + 1}|."
- OFFSET: 1,7
- COMMENT: "Conjecture: (i) a(n) > 0 for all n > 0. In other words, every prime p has a primitive
  root 0 < g < p of the form k^2 + 1, where k is an integer."
- PARI (Greathouse): `a(n)=my(p=prime(n)); sum(k=0, sqrtint(p-2), ispr(k^2+1, p))`, i.e. `k` runs
  while `k² + 1 <= p - 1`, exactly matching Lean's strict `k^2 + 1 < p`.
- Table of n, a(n) for n = 1..10000 (so verified through prime(10000) = 104729).

The Lean encoding is faithful: `k : ℤ` matches "k is an integer"; `k^2 + 1 < p` matches `0 < g < p`
(positivity is automatic since `k² + 1 ≥ 1`); `orderOf (… : ZMod p) = p - 1` is the primitive-root
condition, and `ZMod p` is a field so a nonzero element's `orderOf` is its multiplicative order.
Edge case `p = 2`: `k = 0` gives `g = 1 < 2` and `orderOf (1 : ZMod 2) = 1 = p - 1`. ✔

### Computation

Deterministic primitive-root test via the prime factorization of `p - 1`
(`g^((p-1)/q) ≠ 1` for every prime `q ∣ p-1`).

```
A239957: Lean statement  exists k in Z, k^2+1 < p and orderOf(k^2+1 : ZMod p) = p-1
  primes checked: 25997  (all primes <= 300000)  elapsed 28.3s
  primes with NO such k (counterexample to the Lean declaration): NONE
```

Calibration — the recomputed counts reproduce the OEIS DATA for n = 1..80 exactly:
`[1,1,1,1,1,1,2,2,3,3,1,3,2,2,3,4,4,4,2,1,2,1,3,3,6,3,3,7,4,5,2,8,3,5,6,1,2,5,8,10,7,3,2,6,8,2,3,5,8,4,7,4,2,5,8,9,10,5,8,6,10,6,4,9,6,9,5,3,13,5,8,9,5,6,8,13,13,6,6,5]`

### Verdict

`HOLD_BOUNDED` — no counterexample among all 25,997 primes `p ≤ 300,000`. Encoding faithful,
including the `p = 2` endpoint and the strict `<`. No formalization defect.

---

## 7. A280831 — Zhi-Wei Sun's 1680-conjecture

**Lean file:** `FormalConjectures/OEIS/280831.lean` (2327 bytes, 1 `category research open`).
**OEIS:** <https://oeis.org/A280831> · RMB 1,680 prize.

### Verbatim open declaration

```lean
def A (n : ℕ) : Prop :=
  ∃ x y z w : ℕ, n = x ^ 2 + y ^ 2 + z ^ 2 + w ^ 2 ∧ IsSquare (x ^ 4 + 1680 * y ^ 3 * z)

@[category research open, AMS 11]
theorem conjecture (n : ℕ) : A n := by
  sorry
```

### OEIS ground truth

- NAME (of the *counting sequence*): "Number of ways to write 8*n+7 as x^2 + y^2 + z^2 + w^2 with
  x^4 + 1680*y^3*z a square, where x,y,z,w are **positive** integers." OFFSET 0,4.
- COMMENT (the conjecture the Lean file formalizes): "the author's 1680-conjecture which states that
  each n = 0,1,... can be written as x^2 + y^2 + z^2 + w^2 with x,y,z,w **nonnegative** integers such
  that x^4 + 1680*y^3*z is a square. Qing-Hu Hou at Tianjin Univ. has verified it for n up to 10^8."
- COMMENT: "If a natural number n is not of the form 4^k*(8m+7) … there are nonnegative integers
  w,x,y such that n = w^2 + x^2 + y^2 + 0^2 and hence x^4 + 1680*y^3*0 is a square. Thus, the
  conjecture … has the following equivalent form: a(n) > 0 for all n = 0,1,..."

The Lean statement is the nonnegative ("1680-conjecture") form, which is what the COMMENT states.
Faithful. Note the NAME's *positive*-integer counting sequence is a different (stronger) object and
is **not** what the Lean declaration asserts.

### Computation

Using the entry's own Gauss–Legendre reduction: for `n` not of the form `4^k(8m+7)` the Lean
statement is immediate with `z = 0` (then `x⁴ + 1680·y³·0 = (x²)²`). Only the "hard" `n` need search.

```
hard n <= 100000 : (form 4^k(8m+7))
  [time cap reached after n=43772]
  n with NO representation: NONE
  elapsed 45.0s
```

An earlier full pass gave `n = 0..20000 : NONE` in 11.4 s (3,331 hard values).

Calibration — exhaustive positive-integer counts for `8n+7` reproduce the OEIS DATA for n = 0..49
exactly: `[1,1,1,2,1,3,2,1,2,1,1,1,4,2,1,4,5,3,3,1,3,2,3,2,6,5,3,4,4,3,12,6,2,7,5,3,10,4,5,2,7,5,4,5,3,8,2,2,3,4]`.

### Verdict

`HOLD_BOUNDED` — no counterexample for `n = 0..43,772` (with all non-`4^k(8m+7)` values covered by
the certified `z = 0` argument). Encoding faithful. No formalization defect.

---

## 8. A281976 — Zhi-Wei Sun's 24-conjecture

**Lean file:** `FormalConjectures/OEIS/281976.lean` (2906 bytes, 1 `category research open`).
**OEIS:** <https://oeis.org/A281976> · $2,400 prize.

### Verbatim open declaration

```lean
def A (n : ℕ) : Prop :=
  ∃ x y z w : ℕ, n = x ^ 2 + y ^ 2 + z ^ 2 + w ^ 2 ∧ z ≤ w ∧ IsSquare x ∧ IsSquare (x + 24 * y)

@[category research open, AMS 11]
theorem conjecture (n : ℕ) : A n := by
  sorry
```

### OEIS ground truth

- NAME: "Number of ways to write n as x^2 + y^2 + z^2 + w^2 with x,y,z,w nonnegative integers and
  z <= w such that both x and x + 24*y are squares." OFFSET 0,2.
- COMMENT: "Conjecture: a(n) > 0 for all n = 0,1,2,…" / "We have verified a(n) > 0 for all
  n = 0..10^7." / "Qing-Hu Hou … has verified a(n) > 0 for all n = 0..10^10."

Faithful, including the `z ≤ w` normalization, which is carried over verbatim from the NAME
(and is harmless for existence, since `z, w` may be swapped).

### Computation

`x` ranges over perfect squares `t²` with `t⁴ ≤ n`; `y` is constrained by `IsSquare (x + 24y)`;
the remainder is tested against a precomputed sum-of-two-squares (`z ≤ w`) bit table.

```
A281976 counts == OEIS DATA(0..80): True
A281976 Lean-statement existence, n=0..200000 : failures = NONE  (6.8s)
A281976 Lean-statement existence, n=0..781629 : failures = NONE  (50.0s, time cap)
```

### Verdict

`HOLD_BOUNDED` — no counterexample for `n = 0..781,629`; representation counts match the OEIS DATA
for `n = 0..80` exactly. Encoding faithful. No formalization defect.

---

## 9. A287616 — triangular + generalized pentagonal + generalized heptagonal

**Lean file:** `FormalConjectures/OEIS/287616.lean` (2029 bytes, 1 `category research open`).
**OEIS:** <https://oeis.org/A287616> · USD 135 prize.

### Verbatim open declaration

```lean
def A (n : ℕ) : Prop :=
  ∃ x y z : ℕ, n = x * (x + 1) / 2 + y * (3 * y + 1) / 2 + z * (5 * z + 1) / 2

@[category research open, AMS 11]
theorem conjecture (n : ℕ) : A n := by
  sorry
```

### OEIS ground truth and the ℕ-vs-ℤ question (checked explicitly)

- NAME: "Number of ways to write n as x*(x+1)/2 + y*(3*y+1)/2 + z*(5*z+1)/2 with x,y,z
  **nonnegative integers**." OFFSET 0,4.
- COMMENT: "Conjecture: a(n) > 0 for all n = 0,1,2,…, and a(n) = 1 only for n = 0, 1, 2, 4, 7, 9, 22."
- COMMENT: "It was proved in arXiv:1502.03056 that each n can be written as x(x+1)/2 + y(3y+1)/2 +
  z(5z+1)/2 with x,y,z **integers**. The author would like to offer 135 US dollars as the prize for
  the first proof of the conjecture that a(n) is always positive."

This was the prime suspect for a ℕ-vs-ℤ defect (the *generalized* pentagonal/heptagonal numbers
require `y, z ∈ ℤ`, and the ℤ-version is already a theorem). **The suspicion is wrong:** the OEIS
NAME itself restricts to nonnegative integers, and the open prize conjecture is precisely the
nonnegative form. The Lean `x y z : ℕ` encoding is therefore **faithful**, and the Lean file's own
header wording ("with x, y, z nonnegative integers") matches. Value sets used by Lean:
`T = {0,1,3,6,10,…}`, `P = {0,2,7,15,26,…}`, `H = {0,3,11,24,42,…}`.

### Computation (big-int bitset convolution)

```
|T|=7746 |P|=4472 |H|=3465  (parameters range over Nat, exactly as in the Lean statement)
A287616 Lean-statement coverage of 0..30000000 : missing = NONE   (35.6s)
A287616 representation counts == OEIS DATA(0..80): True
```

(Earlier pass: `0..5,000,000 : missing = NONE` in 2.0 s.)

### STATUS_SYNC (already reported upstream)

The OEIS entry now links **Yichuan Cao, Dakai Guo, Ruichen Qiu, Ruyong Feng, Xiao-Shan Gao,
"Every Nonnegative Integer Is a Sum of a Triangular, a Pentagonal, and a Heptagonal Number",
arXiv:2606.26035 (2026), see pp. 1–2, 12 (Lean formalization)** — i.e. this `research open`
declaration is proved.

**Duplicate status: ALREADY REPORTED.** Upstream open issue
[#4927 "Open statements with known solutions"](https://github.com/google-deepmind/formal-conjectures/issues/4927)
lists it: *"OEIS A287616 — `conjecture` — Theorem 1 (arXiv:2606.26035) proves the exact statement →
mark solved."* Not novel.

### Verdict

`HOLD_BOUNDED` (n ≤ 3·10^7, zero gaps) and `STATUS_SYNC` (proved 2026), **duplicate of #4927**.
No counterexample; no formalization defect.

---

## 10–12. A303656, A306477, A308734 — UNSTARTED (Phase 0B freeze only)

No computation was run on these three. Everything below is the frozen Phase-0B provenance record so
the next agent can start directly at the search step.

### A303656 — sum of two squares, a power of 3, and a power of 5

`FormalConjectures/OEIS/303656.lean` (2272 bytes, 1 `category research open`). $3,500 prize.

```lean
def A (n : ℕ) : Prop := ∃ a b c d : ℕ, n = a ^ 2 + b ^ 2 + 3 ^ c + 5 ^ d

@[category research open, AMS 11]
theorem conjecture (n : ℕ) (hn : 1 < n) : A n := by
  sorry
```

- OEIS NAME: "Number of ways to write n as a^2 + b^2 + 3^c + 5^d, where a,b,c,d are nonnegative
  integers **with a <= b**." OFFSET 1,4.
- COMMENT: "Conjecture: a(n) > 0 for all n > 1." / "verified … for all n = 2..2*10^10" /
  "Jiao-Min Lin … has verified a(n) > 0 for all 1 < n <= 2.4*10^11."
- **Faithfulness:** Lean drops `a <= b`; harmless for existence (swap `a, b`). Hypothesis `1 < n`
  matches "for all n > 1". `3^0 = 5^0 = 1`, so the minimum representable value is 2, consistent
  with `a(1) = 0` in the DATA. Encoding looks faithful.
- **Certificate shape:** finite universal — one `n` with no `(a,b,c,d)` refutes it. Cheap to sweep
  (for each `n`, loop `c, d` with `3^c + 5^d ≤ n` and test `n - 3^c - 5^d` for
  sum-of-two-squares via a precomputed table). Realistically a calibration sweep only, given
  2.4·10^11 prior verification.

### A306477 — Sun's 2-4-6-8 conjecture

`FormalConjectures/OEIS/306477.lean` (2279 bytes, 1 `category research open`). $2,468 prize
(**and RMB 2,468 offered for an explicit counterexample**).

```lean
def A (n : ℕ) : Prop :=
  ∃ w x y z : ℕ, n = (w + 2).choose 2 + (x + 3).choose 4 + (y + 5).choose 6 + (z + 7).choose 8

@[category research open, AMS 11]
theorem conjecture (n : ℕ) (hn : 0 < n) : A n := by
  sorry
```

- OEIS NAME: "Number of ways to write n as C(w+2,2) + C(x+3,4) + C(y+5,6) + C(z+7,8) with w,x,y,z
  nonnegative integers." OFFSET 1,2. (The Lean encoding is character-for-character the NAME.)
- COMMENT: "Conjecture: a(n) > 0 for all n > 0. In other words, any positive integer n can be
  written as C(w,2) + C(x,4) + C(y,6) + C(z,8), where w,x,y,z are integers greater than one."
- COMMENT: verified to 3·10^7 (Sun), 5·10^8 (Baruch), 2·10^11 (Alekseyev), **2·10^12 (Baruch,
  Mar 12 2019)**.
- **Offset-shift check (done by hand, no defect):** the two parameterizations generate identical
  value sets. `C(w+2,2)` for `w ≥ 0` gives `{1,3,6,10,…}` = `C(w,2)` for `w ≥ 2`;
  `C(x+3,4)` for `x ≥ 0` gives `{0,1,5,15,…}` = `C(x,4)` for `x ≥ 2` (both include the zeros from
  `x < 4`); likewise `C(y+5,6)` ↔ `C(y,6)` and `C(z+7,8)` ↔ `C(z,8)`. **Encoding faithful.**
- **Certificate shape:** finite universal. Given 2·10^12 prior verification, a small sweep is
  calibration only; the value of this target is the encoding audit above, which is clean.

### A308734 — Sun's four-square conjecture with powers of 2, 3, 5

`FormalConjectures/OEIS/308734.lean` (2414 bytes, 1 `category research open`). $2,500 prize.

```lean
def A (n : ℕ) : Prop :=
  ∃ a b c d x y : ℕ, n = (2 ^ a * 3 ^ b) ^ 2 + (2 ^ c * 5 ^ d) ^ 2 + x ^ 2 + y ^ 2

@[category research open, AMS 11]
theorem conjecture (n : ℕ) (hn : 1 < n) : A n := by
  sorry
```

- OEIS NAME: "Number of ordered ways to write n as (2^a*3^b)^2 + (2^c*5^d)^2 + x^2 + y^2, where
  a,b,c,d,x,y are nonnegative integers **with x <= y**." OFFSET 1,5.
- COMMENT: "Four-square Conjecture: a(n) > 0 for all n > 1." / "verified a(n) > 0 for all
  n = 2..10^9" / Giovanni Resta to 10^10 / **Jiao-Min Lin to 1.6·10^11**.
- COMMENT worth noting as a near-miss control: "16265031 cannot be written as
  (2^a*3^b)^2 + (2^c*3^d)^2 + x^2 + y^2" — that is the **3,3** variant, not the 3,5 variant the
  Lean file states; do not mistake it for a counterexample here.
- Literature: Soumyarup Banerjee, "On a conjecture of Sun about sums of restricted squares",
  J. Number Theory 256 (2024), 253–289 — **check whether this settles the exact statement before
  spending compute; it may be a `STATUS_SYNC` rather than a search target.**
- **Faithfulness:** Lean drops `x <= y`; harmless for existence. Hypothesis `1 < n` matches
  "for all n > 1". Encoding looks faithful.
- **Certificate shape:** finite universal.

---

## 13. A357513 — generalized supercongruence (closed on shape; no compute needed)

**Lean file:** `FormalConjectures/OEIS/357513.lean` (3635 bytes, 1 `category research open`).
**OEIS:** <https://oeis.org/A357513>

### Verbatim open declaration

```lean
noncomputable def u (m : ℕ) (n : ℕ) : ℕ :=
  ∑ k ∈ (Finset.Icc 1 n),
    ((n.choose k : ℚ) ^ 2 * ((n + k).choose k : ℚ) ^ 2) / k ^ (2 * m + 1) |>.num.natAbs

@[category research open, AMS 11]
theorem general_supercongruence (m : ℕ) : ∃ (exceptions : Finset ℕ), ∀ p, p.Prime →
    p ∉ exceptions → u m (p - 1) = (0 : ZMod (p ^ 4)) := by
  sorry
```

### OEIS ground truth

- NAME: "a(n) = numerator of Sum_{k = 1..n} (1/k^3) * binomial(n,k)^2 * binomial(n+k,k)^2 for n >= 1
  with a(0) = 0." OFFSET 0,2.
- DATA: `0, 4, 81, 14651, 956875, 1335793103, 697621869, …` — the Lean test lemmas
  `a 1 = 4`, `a 2 = 81`, `a 3 = 14651`, `a 4 = 956875`, `a 5 = 1335793103` match exactly, which also
  pins the parse: `.num.natAbs` applies to the **whole sum**, not to each summand (summand-wise
  would give `a 2 = 45`, not `81`).
- COMMENT: "Let m be a nonnegative integer and set u(n) = the numerator of
  Sum_{k = 1..n} 1/k^(2*m+1) * binomial(n,k)^2 * binomial(n+k,k)^2. We conjecture that
  u(p-1) == 0 (mod p^4) for all primes p, with a finite number of exceptions that depend on m."
- COMMENT (Ondrej Kutal, Jul 18 2026): **"This conjecture is now proved; see Links.** The
  exceptional primes are exactly the primes p for which p − 1 divides 2*m + 4 and p does not divide
  2*m + 7. In particular, p = 2 is always exceptional, and for m = 1 the exceptions are p = 2 and
  p = 7 … Every exceptional prime satisfies p <= 2*m + 5."
- LINK: "Ondrej Kutal, **A proof of the generalized conjecture, with Lean formalization**, Jul 2026."

### Certificate shape (METHOD G0 / Phase 0A) — dead end for a finite counterexample

The declaration is `∃ (exceptions : Finset ℕ), ∀ p prime, p ∉ exceptions → …`. To refute it one must
show that **no** finite set of exceptions works, i.e. that infinitely many primes fail. A single
integer — indeed any finite list of failing primes — is consistent with the statement, because those
primes can simply be put into `exceptions`. **Not finitely refutable.**

Note also the Lean file's own docstring records a deliberate source correction: "seems like a typo
in the OEIS entry: the sum starts with k=0 there. In order to avoid a division by zero, we replace
start the sum at k=1" — the current OEIS NAME/COMMENT both say `k = 1..n`, so the Lean choice agrees
with the present source text.

### STATUS_SYNC (novel as far as checked — not in #4927)

The declaration is `category research open` at pinned commit `2411d22e`, but the OEIS entry records
the general conjecture as **proved with a Lean formalization** (Kutal, Jul 2026), and the specific
`m = 1` case in the same file is already `category research solved` via AlphaProof. Upstream issue
search: `repo:google-deepmind/formal-conjectures A357513` → 1 hit, #1924 (closed, the original
feature PR). #4927 "Open statements with known solutions" does **not** list A357513.
No verification of Kutal's proof was performed here — this is a metadata observation only.

### Verdict

`CERTIFICATE_SHAPE_FAIL` / **NOT_FINITELY_REFUTABLE**, plus a `STATUS_SYNC` lead (proved upstream of
the repository, still marked open, not currently tracked in #4927). No publication action taken.

---

## Final tally for this share (9 of 13 completed, 4 unstarted)

- **Counterexamples found: 0.** No refuting integer for any declaration.
- `CERTIFICATE_SHAPE_FAIL` / NOT_FINITELY_REFUTABLE: **3** (A167604, A228828, A357513).
- `HOLD_BOUNDED`: **6** (A211417 n ≤ 3000; A232174 n ≤ 60000; A239957 all p ≤ 300000;
  A280831 n ≤ 43772; A281976 n ≤ 781629; A287616 n ≤ 3·10^7).
- Statement defects: **2** — A211417 `general_divisibility` (`D = 0`, **duplicate of #4923**) and
  A237271 `observation_carmichael` (**vacuous premise, novel**).
- Source errata: **1** — A232174 OEIS comment omits `n = 66` from its "a(n) = 1 only for" list
  (**novel**, no Lean consequence).
- Status syncs: **2** — A287616 proved 2026 (**duplicate of #4927**), A357513 proved 2026
  (**not currently tracked upstream**).
- Unstarted: A303656, A306477, A308734 (all with faithful encodings confirmed and Phase-0B
  provenance frozen above).

**No upstream issue, PR, comment, tag, or release was created. Local records only.**
