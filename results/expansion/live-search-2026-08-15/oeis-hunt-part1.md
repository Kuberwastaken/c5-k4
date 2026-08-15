# OEIS open-declaration counterexample hunt — part 1 (ids < 130000)

**Campaign:** finite counterexamples to `@[category research open]` / `answer(sorry)`
declarations in `google-deepmind/formal-conjectures`, OEIS corpus.

**Upstream pin:** `google-deepmind/formal-conjectures` @ `2411d22e1bd550d050d0eac6c1fb379a76a3e7c5`
(`upstream/main`, "Disprove WOWII 59 (#4574)"). All Lean text read via
`git show upstream/main:FormalConjectures/OEIS/<id>.lean` in
`/Users/kuber.mehta/Projects/formal-conjectures`.

**Target list:** `results/expansion/open_targets_oeis_erdos_20260815.json`, entries with
`corpus=="OEIS"`, `id < 130000`, `previously_touched == false` — 61 files, sorted ascending.
(12 in-range files with `previously_touched==true` are skipped: 103151, 105565, 105720,
108081, 108211, 108569, 109074, 109908, 109909, 111291, 113019, 115257.)

**Protocol:** `METHOD.md` v1.0 (Phase 0A certificate-shape gate first; 60 s hard cap per
computation; exact integer arithmetic; second independent code path for every candidate;
no upstream write of any kind).

**Compute:** `/home/ec2-user/.venvs/wowii/bin/python` (3.9.25, numpy 2.0.2, no sympy —
Miller-Rabin/sieve helpers in `scripts/nt.py`).

**OEIS source:** `https://oeis.org/search?q=id:A<id>&fmt=json` (browser UA required;
plain curl is Cloudflare-challenged) plus `https://oeis.org/A<id>/b<id>.txt` where used.

---

## Running summary

| # | A-number | open decls | verdict | refuting witness |
|---|---|---|---|---|

*(populated incrementally below; one section per target)*

---

## Phase A — triage of all 61 targets (METHOD v1.6 §A4)

Certificate-shape gate (METHOD Phase 0A) applied to every open declaration before any
compute. `FIN-U` = finite universal (one finite object refutes); `ANS` = `answer(sorry)`
placeholder (never literally false, but a finite witness can still refute the *source*
conjecture and force the answer); `SHAPE-FAIL` = no finite artifact can settle it
(asymptotic / `Set.Infinite` / `∃`-inside-`∀` / irrationality / eventual-quantifier).

| A-number | open decls | shape | triage decision |
|---|---|---|---|
| A000041 | 1 | ANS (`↔ ∀k, ¬IsPerfectPower (a k)`) | bounded scan of `p(n)` for perfect powers |
| A000945 | 1 | SHAPE-FAIL (`∀p ∃n`, Euclid–Mullin) | stop |
| A001146 | 1 | FIN-U (`k⁴−1 ∣ 2ᵏ−1 → k = 2^(2ⁿ)`) | bounded scan of even `k` |
| A001157 | 1 | FIN-U (Sun: distinct `Int.fract σ_k(n)/n^k`) | bounded collision search |
| A011545 | 2 | FIN-U (π-prefix square; π-prefix interval) | bounded scan |
| A034693 | 4 | 2×FIN-U (`∃k<n`; `∃k<1+n^{3/4}`), 2×SHAPE-FAIL (O/unbounded) | bounded scan |
| A037274 | 1 | SHAPE-FAIL (home primes, `∃k` inside `∀n`) | stop |
| A056777 | 1 | FIN-U (φ/σ +12 ⇒ prime quadruple) | bounded scan |
| A063880 | 2 | FIN-U (`n%216=108`; unique primitive 108) | bounded scan |
| A067720 | 1 | FIN-U (`φ(k²+1)=kφ(k+1)`, `k≠8` ⇒ `k+1` prime) | bounded scan |
| A081091 | 1 | SHAPE-FAIL (`Set.Infinite`) | stop |
| A100434 | 3 | FIN-U (three auxiliary-sequence identities) | **compute — hit** |
| A100474 | 2 | ANS/FIXED_OPTIMUM | shape stop, faithfulness spot-check |
| A100475 | 1 | ANS + uniform-over-`x` periodicity | shape stop (noted below) |
| A100478 | 1 | ANS + uniform-over-`v` periodicity | shape stop (noted below) |
| A100800 | 1 | SHAPE-FAIL (`∃k` inside `∀n`) | stop |
| A101779 | 1 | SHAPE-FAIL (`∀n ∃k`) | stop |
| A102371 | 1 | ANS (identity vs A105033) | bounded identity check |
| A102722 | 1 | SHAPE-FAIL (`~[atTop]`) | stop |
| A102847 | 1 | FIXED_OPTIMUM (`sInf`) | stop |
| A103425 | 1 | ANS (`∃` weighted tribonacci, prime-free) | **compute — trivially true** |
| A103662 | 2 | 1×SHAPE-FAIL (`∃N ∀n>N`), 1×FIN-U (`¬∃b`, n=40) | bounded base scan |
| A103885 | 1 | CONSTRUCTION_ONLY (`∃P Q` polynomials) | stop |
| A104320 | 1 | FIN-U (`∀n>15`, base-3 zero) | bounded scan |
| A105020 | 1 | FIN-U (semiprime between consecutive odds) | **compute** |
| A105210 | 2 | 1×FIN-U (5 trajectories disjoint), 1×CONSTRUCTION_ONLY | **compute** |
| A105751 | 2 | SHAPE-FAIL (`Tendsto`) | stop |
| A105801 | 1 | SHAPE-FAIL (`∀k ∃m ∀n>m`) | stop |
| A107247 | 1 | FIXED_OPTIMUM (`sInf`) | stop |
| A108129 | 1 | SHAPE-FAIL (Riesel; needs covering-set certificate) | stop |
| A108301 | 1 | ANS + `∃n>11` (construction) | bounded digit-sum primality scan |
| A108306 | 1 | FIN-U (matrix/invert-sequence identity) | **compute** |
| A108864 | 1 | ANS (`∀n>58, Even (a n)`) | bounded scan |
| A108866 | 1 | FIN-U (`num ≡ 0 [ZMOD n²] ↔ n.Prime`) | **compute** |
| A108866 | | | |
| A109227 | 1 | ANS + `∃n` (construction) | bounded scan |
| A109671 | 1 | SHAPE-FAIL (`∀m ∃n`) | stop |
| A109845 | 1 | SHAPE-FAIL (`Set.Infinite`) | stop |
| A109905 | 1 | ANS (set equality `{n | a n = 0} = {1,6,30,54}`) | bounded scan |
| A110475 | 1 | FIN-U (`↔` per `m`) | bounded scan |
| A110566 | 1 | SHAPE-FAIL (`∀m odd ∃n`) | stop |
| A110835 | 1 | FIN-U (Sierpiński `a(n) ≥ n`) | bounded scan |
| A110854 | 1 | FIN-U (`∀d`, prime-difference ⇒ attained) | **compute — hit** |
| A111114 | 1 | SHAPE-FAIL (`∃ᶠ … atTop`) | stop |
| A112521 | 1 | FIN-U (`a n = T n n`) | **compute** |
| A112970 | 3 | FIN-U ×3 (Stern-like identities) | **compute** |
| A113010 | 1 | ANS (`a n = n ⇒ n ∈ {1,32}`) | bounded scan |
| A113213 | 1 | SHAPE-FAIL (`=O[atTop]`) | stop |
| A113250 | 1 | FIN-U (`IsSquare (a (2n+1))`) | **compute** |
| A113252 | 1 | FIN-U (`IsSquare (a (2n+1))`) | **compute** |
| A113255 | 1 | FIN-U (`IsSquare (a (2n+1))`) | **compute** |
| A113257 | 2 | FIXED_OPTIMUM ×2 | stop |
| A113258 | 1 | ANS + `∃n>4` (construction) | stop |
| A113271 | 1 | FIXED_OPTIMUM | stop |
| A113609 | 1 | ANS + `∃q≥10⁶` (construction) | stop |
| A114137 | 2 | SHAPE-FAIL (`Set.Infinite`; `∀k odd ∃n`) | stop |
| A114216 | 1 | ANS (`∀n>33900, a n ≠ 1`) | bounded scan |
| A114362 | 2 | SHAPE-FAIL (irrationality; `=O`) | stop |
| A114831 | 1 | SHAPE-FAIL (`Tendsto`) | stop |
| A115366 | 1 | SHAPE-FAIL (`Tendsto` + numeric bracket) | stop |
| A116150 | 1 | FIXED_OPTIMUM | stop |
| A117027 | 1 | SHAPE-FAIL (`Tendsto` + bracket) | stop |

---

## Running summary

| # | A-number | open decls | verdict | refuting witness |
|---|---|---|---|---|
| 1 | A100434 | 3 | `RETRO_COUNTEREXAMPLE` (duplicate: upstream PR #4560) | `n = 0`: `c 0 + d 0 = 3`, `b 0 = c 1 = -3` |
| 2 | A110854 | 1 | **`NEW_FORMALIZED_READING_DISPROOF`** (no duplicate found) | `d = 3` (`= \|5 - 2\|`); `\|a n\| ∈ {1} ∪ 2ℕ` for all `n > 0` |
| 3 | A103425 | 1 | `RETRO` / trivially true (duplicate: upstream PR #4964, opened 2026-08-15 07:12Z) | `a=3, b=1, c=-3, x ≡ 1` |

---

### A100434 — `conjecture1`, `conjecture2`, `conjecture3` — all three FALSE at `n = 0`

**Blob:** `git show 2411d22e:FormalConjectures/OEIS/100434.lean`.

**Lean (verbatim):**
```lean
@[category research open, AMS 11] theorem conjecture1 (n : ℕ) : c n + d n = b n
@[category research open, AMS 11] theorem conjecture2 (n : ℕ) : e n + f n = b n
@[category research open, AMS 11] theorem conjecture3 (n : ℕ) : g n + a n = b n
```
with `b n = if n % 2 = 0 then c (n + 1) else c (n - 1)`.

**OEIS pin** (A100434, OFFSET 0,1; NAME "Expansion of g.f. (1+x)*(3+x)/(1+6*x^2+x^4)"),
COMMENT by Creighton Dement, Dec 18 2004, verbatim:
> `b(2n) = c(2n+1), b(2n+1) = c(2n); (c(n)) = (1, -3, -7, 17, 41, -99, -239, 577, …)`
> … `Then a(2n) = - c(2n+1), a(2n+1) = d(2n+1) and we have the following conjectures:`
> `c(n) + d(n) = e(n) + f(n) = g(n) + a(n); c(n) + d(n) = b(n).`

**Computation** (exact ℤ, replaying the Lean definitions; `scratch/c100434.py`):

```
c   [1, -3, -7, 17, 41, -99, -239, 577, 1393, -3363, -8119, 19601]      (= OEIS comment string)
d   [2, 4, -10, -24, 58, 140, -338, -816, 1970, 4756, -11482, -27720]   (= OEIS comment string)
a   [3, 4, -17, -24, 99, 140, -577, -816, 3363, 4756, -19601, -27720]   (= OEIS DATA)
b   [-3, 1, 17, -7, -99, 41, 577, -239, -3363, 1393, 19601, -8119]
e   [1, -1, -5, 5, 29, -29, -169, 169, 985, -985, -5741, 5741]          (= OEIS comment string)
f   [2, 2, -12, -12, 70, 70, -408, -408, 2378, 2378, -13860, -13860]    (= OEIS comment string)
g   [0, -3, 0, 17, 0, -99, 0, 577, 0, -3363, 0, 19601]                  (= OEIS comment string)

c+d = e+f = g+a = [3, 1, -17, -7, 99, 41, -577, -239, 3363, 1393, -19601, -8119]
```

- The **three-way** equality `c+d = e+f = g+a` is **TRUE** (verified n = 0..39).
- The extra clause `c(n)+d(n) = b(n)` is **FALSE at every even n** and true at every odd n:
  `c n + d n = (-1)^(n+1) · b n` (verified n = 0..39).
- Minimal witness: **n = 0**, `c 0 + d 0 = 1 + 2 = 3`, `b 0 = c 1 = -3`, `3 ≠ -3`.
  Same at n = 2: `-7 + (-10) = -17`, `b 2 = c 3 = 17`.

**Second code path:** the OEIS COMMENT itself lists `c` and `d` literally; reading
`c(0)=1, d(0)=2, c(1)=-3` off the source text and applying the source's own
`b(2n)=c(2n+1)` gives `3 ≠ -3` with no code at all.

**Classification (METHOD §A6):** the defect is in the *source comment* (the sign slip
`c+d = b` instead of `c+d = -b` on even indices) and is inherited verbatim by the Lean
declaration. All three Lean declarations are literally false.

**Duplicate status: HIT — NOT NOVEL.** Upstream PR
[#4560](https://github.com/google-deepmind/formal-conjectures/pull/4560) "Add OEIS A100434
disproof" (opened 2026-07-23, CLOSED unmerged 2026-07-25) states exactly this counterexample
with witness `n = 2`. Recorded as `RETRO_COUNTEREXAMPLE`; **no upstream write performed.**

---

### A110854 — `conjecture` — FALSE at `d = 3` — **NEW, no duplicate found**

**Blob:** `git show 2411d22e:FormalConjectures/OEIS/110854.lean`.

**Lean (verbatim):**
```lean
noncomputable def a (n : ℕ) : ℤ :=
  let p (k : ℕ) : ℤ := (Nat.nth Nat.Prime (k - 1)).cast
  if n = 0 then 0
  else p (2 * n + 2) - p (2 * n + 1) - p (2 * n) + p (2 * n - 1)

@[category research open, AMS 11]
theorem conjecture :
  ∀ d > 0, (∃ p1 p2 : ℕ, p1.Prime ∧ p2.Prime ∧ d = (p1 - p2 : ℤ).natAbs) →
  ∃ n > 0, d = (a n).natAbs
```

**OEIS pin** (A110854, OFFSET 1,4;
NAME `A155750(n)-A155067(n) = prime(2n+2)-prime(2n+1)-prime(2n)+prime(2n-1)`;
DATA `1,0,0,4,0,-4,4,-4,2,2,0,-2,0,0,0,-2,…`).
The **only** COMMENT is:
> `Do the absolute values cover A004275?`

A004275 = "1 together with nonnegative even numbers" = `0,1,2,4,6,8,10,…` (pinned from
`https://oeis.org/search?q=id:A004275&fmt=json`).

**The divergence.** The source asks whether `{|a(n)|} ⊇ A004275`. The Lean declaration
replaces the hypothesis "`d ∈ A004275`" by "`d` is the absolute difference of two primes".
Those sets are *not* equal: every `d = p − 2` with `p` an odd prime is an absolute prime
difference and is **odd and > 1**, hence not in A004275. So the Lean hypothesis is strictly
weaker and the declaration is strictly stronger than its source.

**Exact witness: `d = 3`.**
- Premise satisfied: `3 > 0`, and `p1 = 5`, `p2 = 2` are prime with `(5 - 2 : ℤ).natAbs = 3`.
- Conclusion fails: **for every `n > 0`, `(a n).natAbs ≠ 3`.** Proof (complete, not a bounded
  check):
  - `n = 1`: `p 4 - p 3 - p 2 + p 1 = 7 - 5 - 3 + 2 = 1`, so `(a 1).natAbs = 1 ≠ 3`.
  - `n ≥ 2`: then `2n - 1 ≥ 3`, so all four indices `2n−1, 2n, 2n+1, 2n+2` are `≥ 3`, i.e.
    `Nat.nth Nat.Prime (k-1)` with `k-1 ≥ 2`, so all four primes are `≥ 5` and **odd**.
    A signed sum `odd − odd − odd + odd` is **even**. Hence `(a n).natAbs` is even, `≠ 3`.
  Therefore `{(a n).natAbs : n > 0} ⊆ {1} ∪ 2ℕ`, and `3` is in neither.

**Independent recomputation** (`scratch/c110854.py`, sieve to 4·10⁶, 283 146 primes,
n = 1..141 570, 60 s cap):
```
a(1..12) = [1, 0, 0, 4, 0, -4, 4, -4, 2, 2, 0, -2]      (= OEIS DATA, exact match)
n > 0 with a(n) odd : [1]        (count 1)
|a(n)| == 3 anywhere in 1..141570 : False
set of odd |a(n)| values : [1]
```
The bounded scan agrees with the parity proof; the proof is what settles the ∀.

**Further witnesses** (same argument): every `d = p − 2` with `p` an odd prime `> 3`, i.e.
`d = 5, 9, 11, 15, 17, 21, 27, 29, 35, …`, refutes the declaration identically.

**Classification (METHOD §A6):**
`NEW_FORMALIZED_READING_DISPROOF` — a **formalization counterexample**. The underlying OEIS
question ("do the absolute values cover A004275?") is **untouched and remains open**; what is
false is the Lean declaration, whose hypothesis was broadened from A004275 to "difference of
two primes".

**Duplicate audit:**
- `gh issue list --state all --search A110854` → 0 hits; `--search 110854` → 0 hits.
- `gh pr list --state all --search A110854` → 0 hits; `--search 110854` → only PR #4450
  ("Add the first 64 files from AutoOeis to formal-conjectures", MERGED 2026-07-17), which is
  the batch that introduced the file, not a defect report.
- Known-defect collector issues #4896 / #4923 / #4927 checked — see HANDOFF STATE.
- No upstream write performed.

---

### A103425 — `conjecture` — statement is **trivially true** (degenerate instantiation)

**Blob:** `git show 2411d22e:FormalConjectures/OEIS/103425.lean`.

**Lean (verbatim):**
```lean
def IsWeightedTribonacci (a b c : ℤ) (x : ℕ → ℤ) : Prop :=
  ∀ n, x (n + 3) = a * x (n + 2) + b * x (n + 1) + c * x n

@[category research open, AMS 11]
theorem conjecture : answer(sorry) ↔
    ∃ (a b c : ℤ) (x : ℕ → ℤ),
      Nat.gcd (Int.gcd a b) c.natAbs = 1 ∧
      IsWeightedTribonacci a b c x ∧
      ∀ n, ¬ (x n).natAbs.Prime
```

**OEIS pin** (A103425, OFFSET 0,2; NAME `a(n) = 3*a(n-1) + a(n-2) - 3*a(n-3)`),
COMMENT by Jonathan Vos Post, Feb 05 2005, verbatim:
> `This is a (3, 1, -3) weighted tribonacci sequence … Is there an (a, b, c) weighted`
> `tribonacci sequence with a, b, c relatively prime which is prime-free?`

**Triviality certificate.** Take the source's *own* coefficients `a = 3, b = 1, c = -3` and
the constant sequence `x n = 1`:
- `Nat.gcd (Int.gcd 3 1) (-3).natAbs = Nat.gcd 1 3 = 1` ✓
- `x (n+3) = 1 = 3·1 + 1·1 + (-3)·1` ✓
- `(x n).natAbs = 1`, and `¬ Nat.Prime 1` ✓

An even more degenerate witness is `a=1, b=0, c=0, x ≡ 0` (`Nat.gcd (Int.gcd 1 0) 0 = 1`,
`0` not prime). The source clearly intends a nonconstant/nondegenerate integer sequence; the
Lean declaration omits every such condition, so `answer := True` and the open question
collapses.

**Duplicate status: HIT — NOT NOVEL.** Upstream PR
[#4964](https://github.com/google-deepmind/formal-conjectures/pull/4964) "Mark OEIS A103425 as
solved" (KitaKen1, **opened 2026-08-15 07:12:09Z**, OPEN at time of this run) changes
`answer(sorry)` → `answer(True)` with a kernel-checked proof of the identical statement.
Recorded as duplicate; **no upstream write performed.**

---
