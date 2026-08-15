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
### A108864 — `conjecture` — RHS is FALSE at `n = 67` — **NEW, no duplicate found**

**Blob:** `git show 2411d22e:FormalConjectures/OEIS/108864.lean`.

**Lean (verbatim):**
```lean
def A (n : ℕ) : Prop :=
  let sigmaOneN : ℕ := (Nat.divisors n).sum id
  0 < n ∧ ((sigmaOneN : ℤ) - 2 * (n : ℤ)).natAbs ≤ 10

noncomputable def a (n : ℕ) : ℕ := n.nth A

@[category research open, AMS 11]
theorem conjecture : answer(sorry) ↔ ∀ n > 58, Even (a n)
```
(file docstring: "Numbers `n` such that the perfect deficiency of `n` is `≤ 10`".)

**OEIS pin.** A108864, OFFSET 1,2, NAME
`Numbers n such that the perfect deficiency of n (A109883) is <= 10`;
the only COMMENT is `Is 1155 the last odd number in this sequence?`
DATA `1,2,3,4,5,6,7,8,9,10,11,12,14,15,16,18,20,21,22,24,26,28,30,32,40,42,44,50,52,60,64,68,72,110,120,126,128,130,136,144,150,152,180,184,204,228,256,315,462,496,512,528,592,656,750,884,1012,1024,1155,1188,1248`.

A109883 NAME (pinned): `Start subtracting from n its divisors beginning from 1 until one
reaches a number smaller than the last divisor subtracted or reaches the last nontrivial
divisor < n. Define this to be the perfect deficiency of n.`  This is a **greedy
divisor-subtraction** quantity; it is **not** `|σ(n) − 2n|`.

**The divergence — proof by one value.** `A109883(24) = 0 ≤ 10`, so `24 ∈ A108864` (and 24 is
in the OEIS DATA), but `σ(24) = 60`, `2·24 = 48`, `|60 − 48| = 12 > 10`, so the Lean predicate
`A 24` is **false**. Symmetrically `56 ∉ A108864` but `σ(56) = 120 = 2·56`, so `A 56` holds.

Reimplementing A109883 literally (`scratch/c109883b.py`) reproduces its published values
`0,1,2,1,4,0,6,1,5,2,10,2,12,4,6,1,16,6,18,8,…` exactly (first 79 terms match), and its
`≤ 10` filter reproduces the A108864 DATA head exactly (first 61 terms match). So the source
side is pinned with certainty; the Lean predicate is the thing that differs.

**Consequence — the Lean statement is false.** Let `L = {n > 0 : |σ(n) − 2n| ≤ 10}` (the set
the Lean `A` actually defines). `L` is infinite (every `2^k ∈ L`, since `|σ(2^k) − 2^{k+1}| = 1`),
so `Nat.nth A` is total. Enumerated exactly (`scratch/c108864.py`, σ-sieve to 10⁷, and
independently by direct divisor enumeration in `scratch/c108864b.py`):

```
L (0-indexed) = 1,2,3,4,5,6,7,8,9,10,11,12,14,15,16,18,20,21,22,26,28,32,40,44,50,52,56,64,
                68,70,88,104,110,128,130,136,152,184,196,256,315,368,464,496,512,592,650,656,
                836,884,1012,1024,1155,1696,1888,1952,2048,2144,2272,2336,4030,4096,5830,
                8128,8192,8384,8768,8925,11096,16384,...
odd elements of L with their Lean index n:
  (0,1) (2,3) (4,5) (6,7) (8,9) (10,11) (13,15) (17,21) (40,315) (52,1155)
  (67,8925)  (74,32445)  (94,442365)
```

- **Minimal witness: `n = 67`.** `a 67 = 8925`, and `67 > 58`, and `8925` is **odd**, so
  `Even (a 67)` is false. Premise check: `8925 = 3 · 5² · 7 · 17`,
  `σ(8925) = 4 · 31 · 8 · 18 = 17856`, `2 · 8925 = 17850`, `|17856 − 17850| = 6 ≤ 10` ✓,
  so `A 8925` holds. Indices 59..66 of `L` are `4030, 4096, 5830, 8128, 8192, 8384, 8768`, all
  even, so 67 is the least violating index.
- Further witnesses: `n = 74` (`a 74 = 32445`) and `n = 94` (`a 94 = 442365`).
- Therefore the RHS is false and `answer` is forced to `False`.

**Independent recomputation.** Two disjoint code paths agree on `L` and on the index of 8925:
(i) numpy divisor-sum sieve to 10⁷; (ii) plain trial-division `sigma` with no sieve, listing
`L ∩ [1, 9000]` (68 elements, `L[67] = 8925`). Both give `L.index(1155) = 52` and
`L.index(8925) = 67`.

**Why the `> 58` bound is the giveaway.** In the **true** A108864, `1155` is at 0-indexed
position **58** (verified: `true_terms.index(1155) = 58`), which is exactly the bound the Lean
declaration uses. So the declaration's index arithmetic was calibrated against the real
sequence, while its predicate `A` defines a different one — in which `1155` sits at index 52
and three further odd terms appear at indices 67, 74, 94.

**The source conjecture is NOT refuted.** In the true A108864 (perfect deficiency ≤ 10) the
odd terms up to `n = 3·10⁵` are exactly `1, 3, 5, 7, 9, 11, 15, 21, 315, 1155` — nothing beyond
1155 (103 terms total in that range). And `A109883(8925) = 2969 ≫ 10`, so the Lean witness
8925 is not even a member of the real sequence.

**Classification (METHOD §A6):**
`NEW_FORMALIZED_READING_DISPROOF` — a **formalization counterexample**. Coordinate (1), the
mathematical status of "is 1155 the last odd term of A108864?", is **untouched and open**;
coordinate (3)/(4) — the Lean declaration's faithfulness and literal content — fail, because
`A` implements `|σ(n) − 2n| ≤ 10` instead of A109883's perfect deficiency.

**Duplicate audit:** `gh issue/pr list --state all --search A108864` → 0 hits;
`--search 108864` → only PR #4450 (AutoOeis batch, MERGED, the file's origin);
`--search A109883` → 0 hits. Collector issues #4896 / #4923 / #4927 do not list A108864.
No upstream write performed.

---

### Bounded holds — no counterexample found

Each entry: exact Lean statement, OEIS pin, search bound, result. All arithmetic exact;
each computation under the 60 s cap unless a longer explicit bound is stated.

#### A112521 — `∀ n ≥ 1, (a n : ℤ) = T n n` — `HOLD_BOUNDED`
OEIS pin: COMMENT (Gerald McGarvey, Oct 07 2008) "Conjecture: Starting with n=1, a(n) is the
main diagonal of the array defined as T(1,1)=1, T(i,j)=0 if i<1 or j<1,
T(n,k)=T(n,k-2)+T(n,k-1)-2T(n-1,k-1)+T(n-1,k)+T(n-2,k)." Faithful; the ℕ index truncations
`k-2 → 0`, `n-2 → 0` coincide with the source's "0 if i<1 or j<1" convention.
Computed `a n` (exact, including `.toNat`) and `T n n` for **n = 1..90**: **0 mismatches**;
`a n` reproduces the OEIS DATA `0,1,0,6,4,60,84,700,1440,8910,…` exactly; the alternating sum
is never negative, so `.toNat` causes no damage. `scratch/c112521.py`.

#### A105020 — semiprime between consecutive odd entries — `HOLD_BOUNDED`
OEIS pin: COMMENT (Michael Hiebl, Jul 15 2007) — a "Goldbach conjecture" for the array. The
Lean `a` reproduces the DATA `1,3,4,5,8,9,7,12,15,16,9,16,21,24,25,11,20,27,…` exactly.
Note the Lean quantifies over **all** index pairs with `a i = 2n+1`, `a j = 2n+3`, `j = i+n+1`,
not only the row-start pairs the comment describes — a strictly stronger reading.
Enumerated **all** `i < 2·10⁶` with `a i` odd ≥ 3 (1 000 499 candidates); **1998** triples
satisfied the full premise; **0 failures** (`Nat.IsSemiprime` = `n>1 ∧ Ω(n)=2`, sieved to
3 996 003). `scratch/c105020b.py` (runtime ≈ 100 s, declared bound).

#### A108306 — `invertSeqD a b n = (genMatrix a b ^ n) 0 0` — `HOLD_BOUNDED`
OEIS pin: COMMENT (Gary W. Adamson, Jul 31 2016) "The INVERT transform of a sequence starting
(1, a, a*b, a*b^2, …) is equivalent to extracting the upper left terms of powers of the 2x2
matrix [(1,a); (1,b)]." Faithful. Checked all `a, b ∈ 0..7`, `n ∈ 0..15` (1024 rows):
**0 mismatches**. `scratch/c108306.py`.

#### A112970 — `conjecture1/2/3` — hold, but all three are **trivially provable**
OEIS pin: COMMENT "Conjectures: a(2^n)=a(2^(n+1)+1)=**A033638(n)**; a(2^n-1)=a(3*2^n-1)=1."
Verified n = 0..16 for all three; `a` reproduces the DATA
`1,1,1,1,2,1,2,1,3,2,2,1,4,2,2,1,5,3,3,2,5,…` exactly.
Each Lean declaration is a one-line consequence of the recurrence:
- `conjecture1`: `2^(n+1)+1` is odd and `(2^(n+1)+1) / 2 = 2^n` in ℕ, so the odd branch gives
  `a (2^(n+1)+1) = a (2^n)` **definitionally**.
- `conjecture3`: `2^n − 1` is odd with `(2^n−1)/2 = 2^(n-1)−1`; descend to `a 0 = 1`.
- `conjecture2`: same descent on `3·2^n − 1` reaches `a 2 = a 1 + 0 = 1`; combined with
  `conjecture3` both sides are 1.
**Faithfulness defect:** the OEIS conjecture's actual content is the clause `= A033638(n)`
(quarter-squares plus one), which the formalization **drops**. Computed
`a(2^n) = 1,1,2,3,5,7,10,13,17,21,…` = A033638 ✓ — that is the nontrivial half and it is not
formalized. Recorded as `STATUS_SYNC` (three `research open` declarations that are trivial
lemmas). `scratch/c112970.py`.

#### A113250 / A113252 / A113255 — `∀ n, IsSquare (a (2n+1))` — `HOLD_BOUNDED`
OEIS pin: identical COMMENT on all three, "Conjecture: a(m, 2*n+1) is a perfect square for all
m,n (see A113249)". Lean initial values and recurrences match each NAME/FORMULA and each DATA
head exactly. Computed 404 terms of each (n = 0..201 for the odd indices), exact ℤ, `IsSquare`
tested as "≥ 0 and `isqrt` exact": **0 failures** in all three. No odd-index term is ever
negative (the sign pattern puts negatives only at even indices).
`scratch/c1132xx.py`.

#### A105210 — five trajectories pairwise disjoint — `HOLD_BOUNDED`
OEIS pin: COMMENT quoting Math. Mag. 48 (1975) 301 — Cormier and Selfridge: "There appear to be
five sequences beginning with integers less than 1000 which do not merge. These sequences were
carried out to 10^8 or more. The five sequences are A003508, A105210-A105213." The Lean start
set `{1, 393, 412, 668, 932}` matches. The trajectory from 393 reproduces the DATA
`393,528,545,660,682,727,728,751,752,802,1206,1279,…` exactly.
Ran all five to the first term ≥ 2·10⁷ (225/262/272/301/296 terms): all **10** pairwise
intersections empty. Source verification (10⁸) already exceeds ours. `scratch/c105210.py`.

#### A063880 — `n % 216 = 108` and `unique primitive = 108` — `HOLD_BOUNDED`
OEIS pin: NAME `Numbers k such that sigma(k) = 2*usigma(k)`; COMMENTS "Numbers so far are all
== 108 (mod 216) [Confirmed up to 10^7 by Robert G. Wilson v]" and "The only primitive term
below 10^18 is 108". Lean `unitaryDivisors`/`usigma`/`A` are faithful; `Set.IsPrimitive S n`
= `n ∈ S ∧ Disjoint properDivisors S` matches "proper divisors not in the sequence".
Computed all **28 141** terms ≤ 10⁷ (first: 108, 540, 756, 1188, 1404, … = DATA ✓):
**0** with `n % 216 ≠ 108`; the only primitive term is **108**. Source already verified to
10⁷ / 10¹⁸ respectively. `scratch/c063880.py`.

#### A067720 — `A k ∧ k ≠ 8 → (k+1).Prime` — `HOLD_BOUNDED`
OEIS pin: COMMENT "a(n)+1 is prime except for a(5)=8" and "Superset of A070689. Is a(5)=8 the
only additional value?" Faithful (`A 0` is false: `φ(1)=1 ≠ 0`, so no vacuity at 0).
All `k ≤ 3162` (bound: `k²+1 ≤ 10⁷` φ-sieve): 76 members
`1,2,4,6,8,10,16,36,40,66,126,130,…` = DATA ✓; **0** members with `k ≠ 8` and `k+1` composite.
`scratch/batchA.py`.

#### A056777 — `A n → ComesFromPrimeQuadruple n` — `HOLD_BOUNDED`
OEIS pin: COMMENT (Jud McCranie, Oct 11 2000) "I conjecture that all members of the sequence
are of this form", and (Himaghna Roy Choudhury, Jun 05 2026) "verified up to 10^12".
Faithful. All 8 members ≤ 10⁷ — `65, 209, 11009, 38009, 680609, 2205209, 3515609, 4347209`
(= DATA ✓) — are `p(p+8)` for a prime quadruple `p, p+2, p+6, p+8`: **0 violations**.
Source verification (10¹²) far exceeds ours. `scratch/batchA.py`.
*Cosmetic defect:* the file's title line reads `# Divisibility of $2^n + 1$ by $n$`, which
belongs to a different sequence; the body and statement are about A056777.

#### A109905 — `{n > 0 : a n = 0} = {1, 6, 30, 54}` — `HOLD_BOUNDED`
OEIS pin: COMMENT (Robert Israel, Feb 23 2018) "a(n)=0 for k = 1, 6, 30 and 54. Are there any
others?" and (Mauro Fiorentini, Jul 24 2023) "There are none for n up to 10^9". Faithful
(`Finset.sup id` of the empty filtered set is `0`, matching "0 if no such prime exists").
Scanned `n = 1..2·10⁶`: the zero set is exactly `{1, 6, 30, 54}`. Source verification (10⁹)
exceeds ours. `scratch/batchA.py`.

---
#### A034693 — `exists_k` and `exists_k_stronger` — `HOLD_BOUNDED`
OEIS pin: COMMENTS "Conjecture: for every n > 1 there exists a number k < n such that n*k + 1
is a prime. - Amarnath Murthy"; "A stronger conjecture: for every n there exists a number
k < 1 + n^(.75) such that n*k + 1 is a prime … verified this up to n = 10^6. - Joseph L. Pe";
"Stronger version of the conjecture verified up to 10^9. - Mauro Fiorentini". Both Lean
statements are faithful (`Real.nthRoot 4 n ^ 3 = n^(3/4)`). Recomputed `a(1..30) =
1,1,2,1,2,1,4,2,2,1,2,1,4,2,2,1,6,1,10,2,2,1,2,3,4,2,4,1,2,1` = DATA ✓.
Scanned `n = 1..10⁶` with a prime sieve to 10⁷ (877 735 of the 10⁶ values resolved; the rest
have `n·k+1 > 10⁷` before a prime appears): **0 violations** of either statement.
The two remaining declarations in this file (`a_isBigO`, `a_unbounded`) are asymptotic —
`CERTIFICATE_SHAPE_FAIL`; note they are *mutually contradictory* as stated
(Ordowski's `a(n) = O(log n log log n)` vs. Greathouse's "I conjecture the opposite"),
so at most one can be true. `scratch/c034693.py`.

#### A110475 — `∀ m > 0, m ∉ exceptionalSet ↔ ∃ x y, a x = 1 ∧ a y = 1 ∧ m = x + y` — `HOLD_BOUNDED`
OEIS pin: COMMENT (Jonathan Vos Post, Sep 11 2005) "It is conjectured that 1,2,3,4,5,6,7,9,11
are the only positive integers which cannot be represented as the sum of two elements of
indices n such that a(n) = 1." Faithful. The Lean `a` reproduces the DATA
`0,0,0,1,0,1,0,1,1,1,0,2,0,1,1,1,0,2,0,2,…` exactly (note `numAsterisks = k - 1` truncates to
`0` at `n = 1`, giving `a 1 = 0`, matching the source's `a(1) = 0`).
`{x : a x = 1}` = semiprimes ∪ prime powers `p^e, e ≥ 2` = `4,6,8,9,10,14,15,16,21,22,25,…` ✓.
Checked the `↔` for every `m = 1..3·10⁵`: **0 violations**. `scratch/c110475.py`.

#### A110835 — Sierpiński `∀ n > 0, a n ≥ n` — `HOLD_BOUNDED`
OEIS pin: COMMENT (Charles R Greathouse IV, Oct 09 2010) "Sierpinski's conjecture (1958) is
precisely that a(n) >= n for all n"; and "the 'inclusive' condition for the range affects only
n=1" — the Lean predicate uses `n*m ≤ p ∧ p ≤ n*(m+1)` (inclusive) ✓ and indeed reproduces
`a(1) = 8`. Recomputed `a(1..30) = 8,4,8,6,18,15,17,25,13,20,29,44,87,81,35,83,79,74,70,67,
118,330,58,223,172,229,179,471,292,360` = DATA ✓.
Sieve to 3·10⁷; **156 values of n (all n ≤ 194 that resolve in that window)**: `a n ≥ n`
always, minimum slack `a n − n = 2` at `n = 2`. Beyond that the first prime gap of length `n`
exceeds the sieve. `scratch/c110835b.py`.

#### A104320 — `∀ n > 15, a n > 0` — `HOLD_BOUNDED`
OEIS pin: COMMENT "Conjecture from N. J. A. Sloane: a(n) > 0 for n > 15, see A102483."
Faithful. Base-3 representation of `2^n` maintained incrementally (exact), `n = 0..12000`:
`a` reproduces the DATA head exactly; the only `n` with a zeroless base-3 `2^n` are
`n ∈ {0,1,2,3,4,15}`. **0 violations**. `scratch/c104320.py`.

#### A108866 — `(ratExpression n).num ≡ 0 [ZMOD n²] ↔ n.Prime` for `n > 3` — `HOLD_BOUNDED`
OEIS pin: COMMENT (Thomas Ordowski, Mar 02 2020) "Conjecture: for n > 3,
numerator(-2/n + Sum_{k=1..n} 2^k/k) == 0 (mod n^2) if and only if n is prime." Faithful,
including the reduced-`num` reading. Exact `Fraction` arithmetic, `n = 4..1200`:
**0 violations** in either direction. `scratch/c108866.py`.

#### A001146 — `(k⁴−1) ∣ (2ᵏ−1) → k > 1 → ∃ n ≥ 2, k = 2^(2ⁿ)` — `HOLD_BOUNDED`
OEIS pin: COMMENT (M. F. Hasler, Jul 25 2015) "I conjecture that { a(n) ; n>1 } are the
numbers such that n^4-1 divides 2^n-1, intersection of A247219 and A247165." Faithful.
`k⁴−1` must be odd (it divides the odd `2ᵏ−1`), so only even `k` can qualify; scanned every
even `k` in `2..2·10⁶` by exact modular exponentiation: the solutions are exactly
`16, 256, 65536` `= 2^(2ⁿ)` for `n = 2,3,4`. **0 violations**. `scratch/cbatchC.py`.

#### A113010 — `a n = n ∧ n > 0 → n = 1 ∨ n = 32` — `HOLD_BOUNDED` (near-complete)
OEIS pin: COMMENT "n=1 and 32 are two fixed points. Are there any others? There are no other
fixed points less than 10^1000. - Chai Wah Wu, Feb 28 2019." Faithful.
Direct scan `n ≤ 10⁷` → `{1, 32}`. Additionally an **exhaustive** scan over the only possible
shape (`d` = digit count, `s` = digit sum, `n = d^s`) for every `d ≤ 39`, `s ≤ 9d` gives exactly
`(d,s,n) ∈ {(1,1,1), (2,5,32)}` — i.e. no other fixed point below 10³⁹. `scratch/cbatchC.py`.

#### A114216 — `∀ n > 33900, a n ≠ 1` — `HOLD_BOUNDED`
OEIS pin: COMMENT "a(33899) = 123729 and the 33900th prime is 400559, hence 123729 + 400559 =
524288 = 2^19 and a(33900) = 1. Is a(33900) the last term equal to 1? No other terms with
a(n) = 1 for n < 10000000." Faithful. Recomputed with a sieve to 2·10⁷ (1 270 607 primes),
`n = 1..1 270 607`: `a n = 1` exactly at `n ∈ {1, 2, 5, 12, 14, 20, 75, 33900}`; **0** with
`n > 33900`. Source verification (10⁷) exceeds ours. `scratch/cbatchC.py`.

#### A102371 — `a n = 2^n − 1 − A105033.a (n−1)` for `n > 0` — `HOLD_BOUNDED`
OEIS pin: COMMENT (David A. Corneth, May 07 2020) "Do we have a(n) = 2^n-1-A105033(n-1)?"
Faithful; the Lean `OeisA105033.a` matches A105033's published FORMULA.
`a(1..12) = 1,2,7,12,29,62,123,248,505,1018,2047,4084` = DATA ✓.
Checked `n = 1..400` (exact, ℕ-truncation applied): **0 violations**. `scratch/c102371.py`.

#### A011545 — `conjecture1` (no π-prefix is a square) and `conjecture2` — `HOLD_BOUNDED`
OEIS pin: COMMENT "Wolfgang Haken (1977) conjectured that no term of this sequence is a
perfect square…" (→ `conjecture1`), and the Jianing Song note "this property … is equivalent
to the statement that the interval (m*Pi, Pi/arctan(1/m)) does not contain an integer for all
m = 10^n, is not known to be true for sure" (→ `conjecture2`). Both faithful.
π computed to 3025 digits by Machin's formula in exact integer arithmetic:
`a(n) = ⌊π·10ⁿ⌋` reproduces the DATA; **no `a(n)` is a perfect square for n < 3005**, and
**no integer lies in `(π·10ⁿ, π/arctan(10⁻ⁿ))` for n < 600**. `scratch/c011545.py`.

#### A108301 — `answer ↔ ∃ n > 11, (a n).Prime` — `HOLD_BOUNDED` (construction lane, no hit)
OEIS pin: COMMENT "a(0), a(1), a(5), a(6), a(7) and a(11) are primes. Are there any more?"
Faithful. Recomputed digit sums of `2^(2^n)+1` from scratch for `n = 0..18` — exact match with
the DATA. Primality-tested every published term `n = 12..27`
(`5624, 11120, 22166, 44222, 88262, 176180, 353042, 707648, 1419974, 2836751, 5679620,
11365592, 22723865, 45445442, 90899234, 181828850`): **none is prime**
(the only odd candidates, 2836751 and 22723865, are composite). No resolution.
`scratch/c108301.py`.

#### A103662 — `conjecture.variants.a_40 : ¬∃ b, IsValidZerolessPower 40 b` — `HOLD_BOUNDED`
OEIS pin: "a(40), if it exists, is not known." Faithful; the Lean `a` reproduces
`1,2,4,8,16,32,64,128,256,512,9765625,177147,531441` = DATA ✓.
Scanned every base `b = 2 .. 51 725 559` for a zeroless decimal `b⁴⁰`: **none found**.
(The companion `conjecture : ∃ N, ∀ n > N, a n = 0` is `CERTIFICATE_SHAPE_FAIL`.)
`scratch/c103662.py`.

#### A000041 — `answer ↔ ∀ k, ¬IsPerfectPower (p k)` — `HOLD_BOUNDED`
OEIS pin: the Zhi-Wei Sun (Dec 02 2013) comment; `Nat.IsPerfectPower n := ∃ k m, 1 < k ∧
1 < m ∧ k^m = n` correctly excludes `p(0) = p(1) = 1`, so there is **no** `n = 1` triviality.
Computed `p(n)` for `n = 0..30000` by the pentagonal recurrence (exact; `p(50) = 204226` ✓)
and tested each for perfect-power-ness by exact integer `m`-th roots: **none is a perfect
power**. `scratch/c000041.py`.

#### A001157 — Zhi-Wei Sun, pairwise distinct `Int.fract (σ_k(n)/n^k)` — `HOLD_BOUNDED`
OEIS pin: COMMENT (Zhi-Wei Sun, Oct 15 2015) "For each k = 2,3,..., all the rational numbers
sigma_k(n)/n^k = Sum_{d|n} 1/d^k (n = 1,2,3,...) have pairwise distinct fractional parts."
Faithful. Exact `Fraction` fractional parts for `k = 2,3,4,5,6` and `n = 1..2·10⁵`
(10⁶ values total): **0 collisions**. `scratch/c001157.py`.

---
## Phase C — `answer(sorry)` shape defects (no finite counterexample, but the declaration
does not capture its source)

These are recorded because the campaign's band-1 vein is *formalization faithfulness*
(METHOD v1.6 §A1), and because upstream issue **#4923** ("Possible misformalizations II")
already treats exactly these two shapes for the Erdős corpus. **None of the OEIS declarations
below appears in #4896 / #4923 / #4927.** No upstream write performed.

### C1 — Exact self-answer (`answer(sorry) = <closed target term>`), 7 declarations / 6 files

`answer(...)` is a plain term elaborator (`FormalConjecturesUtil/Answer/Syntax.lean:27`:
`syntax (name := Google.answer) "answer(" term ")" : term`); it places no restriction on the
supplied term. Therefore any declaration of the literal form
`answer(sorry) = E` with `E` a **closed** term is discharged by
`answer(E) = E := rfl`, without answering the mathematical question. This is precisely the
defect class issue #4923 lists under "Exact self-answers" (Erdős 33, 329, 348, 409) and
"Reflexive asymptotic answers" (Erdős 422, 539, 789).

| file | declaration | closed target term `E` | OEIS question it is meant to encode |
|---|---|---|---|
| A100474 | `next_semiprime` | `a (sInf {n \| 11 < n ∧ (a n).IsSemiprime})` | "a(11) is the first semiprime … What is the next?" |
| A102847 | `conjecture` | `sInf {n \| 4 < n ∧ (a n).Prime}` | "When is the next prime in the sequence?" |
| A107247 | `conjecture` | `a (sInf {n \| 8 < n ∧ (a n).Prime})` | "Primes … include a(9) = 2, which is next?" |
| A113257 | `conjecture1` | `a (sInf {n \| 2 < n ∧ (a n).Prime})` | "The smallest prime … is a(2) = 5. What is the next prime?" |
| A113257 | `conjecture2` | `a (sInf {n \| 1 < n ∧ IsSquare (a n)})` | "What is the first square value after 1?" |
| A113271 | `conjecture1` | `a (sInf {n \| 5 < n ∧ (a n).Prime})` | "The smallest primes … a(1)=3, a(3)=41 and a(5)=135457. What is the next prime?" |
| A116150 | `conjecture` | `a (sInf {n \| 431 < n ∧ (a n).Prime})` | "First primes are a(11), a(17) … Additional primes: a(71), a(91), a(431). More primes?" |

Each index bound was checked against its OEIS COMMENT and is correct
(`4 < n` after `a(4)=15131` prime; `8 < n` after the 0-indexed `a(8)=2`; `431 < n` after
Harvey P. Dale's `a(431)`; etc.), so the *bounds* are faithful — only the answer shape is
degenerate. Verdict for all seven: `FIXED_OPTIMUM` + self-answer shape defect.

### C2 — Uniform-`answer`-under-binders (the repo's own `AnswerLinter` pattern), 2 files

`FormalConjecturesUtil/Linters/AnswerLinter.lean` warns on
`theorem foo (bar : …) : answer(sorry) ↔ …` ("Move the quantifiers outward"). Its check
(`stars_with_answer_sorry_iff`) only fires on `↔`; both declarations below use `=` on `Prop`
and therefore slip past it, while exhibiting exactly the flaw the linter describes.

**A100475** — `theorem conjecture (x : ℕ) (h : x ≠ 1) : answer(sorry) = IsUltimatelyPeriodic (aStartAt x)`
- OEIS pin (A100475, "Prime-th recurrence with reversal at each step"), COMMENT verbatim:
  `Starting at other than a(n) = 1, does this sequence ever go into a loop?`
- The source asks an **existential** question over start values. The Lean form asserts one
  single `answer` Prop equal to the periodicity status of **every** `x ≠ 1` — i.e. that all
  start values behave alike.
- **The answer is pinned by a degenerate start value.** `x = 0` is admitted (`h` only excludes
  `1`), and `aStartAt 0 n = 0` for all `n` (the `if k = 0 then 0` branch fires immediately),
  which is ultimately periodic with `N = 0, P = 1`. Hence `answer` is forced to `True`, and
  the declaration becomes "**every** `x ≠ 1` gives an ultimately periodic sequence" — a much
  stronger claim than the source's question, and one the source explicitly does *not* assert.
- Not finitely refutable (refuting needs a provably aperiodic orbit), so verdict is
  `CERTIFICATE_SHAPE_FAIL` + faithfulness defect, not a counterexample.

**A100478** — `theorem conjecture (v : Fin 5 → ℕ) (h : ∀ i, v i > 0) : answer(sorry) = ∃ N P, P > 0 ∧ (∀ n ≥ N, aGeneral v (n + P) = aGeneral v n)`
- OEIS pin (A100478, "Pentanacci pi function"), COMMENT verbatim:
  `Starting with other values of a(1), a(2), a(3), a(4), a(5) what behaviors are possible?`
  `Does the sequence always stick at a single integer after some point, or can it go into a`
  `loop, or is there a third pattern?`
- The source's open question is a **three-way** classification (fixed point vs. nontrivial
  loop vs. something else). The Lean declaration only asks whether the orbit is eventually
  periodic — and **that is provable**, so the declaration is not open:
  1. `π(5M) ≤ M` for every `M ≥ 66` (checked exhaustively for `66 ≤ M ≤ 1.2·10⁶`, the last
     failure being `M = 65`; for `M ≥ 109` it follows from `π(x) < 1.26x/ln x`).
  2. Hence the window maximum never exceeds `max(max_i v i, 66)`: each new term is
     `π(S)` with `S ≤ 5M`.
  3. A bounded orbit of a deterministic map on 5-tuples of naturals visits finitely many
     states, so by pigeonhole it is eventually periodic. ∎
  Empirically all 48 tested starting tuples (including `(1,1,1,1,1)`, `(66,…)`, `(70,…)` and
  40 random tuples in `[1,5000]⁵`) reach a **fixed point** (cycle length 1); the
  `(1,1,1,1,1)` orbit reproduces the OEIS DATA `1,1,1,1,1,3,4,4,6,7,9,10,11,14,…` exactly.
- Verdict: `STATUS_SYNC` — a `research open` declaration whose literal content is an
  elementary theorem (`answer := True`), while the source question it cites is untouched.
  `scratch/c100478.py`.

---

### A109227 — `answer ↔ ∃ n > 0, n ≠ 2 ∧ n ≠ 121 ∧ (a n).Prime` — `HOLD_BOUNDED`
OEIS pin: COMMENT "a(2) and a(121) are primes. Are there any more?" Faithful; the Lean `a`
reproduces the DATA `1, 11, 1101, 110101, 1101010001, …` exactly (12/12 terms).
Note `a n` has digit sum `n` (its digits are the prime indicator on `2..p_n`), so `3 ∣ a n`
whenever `3 ∣ n` — those `n` are excluded for free. Miller–Rabin over `n = 1..260`
(numbers up to 1657 decimal digits): the only primes are **n = 2 and n = 121**. No resolution.
`scratch/c109227.py`.

---

## Phase D — certificate-shape stops (METHOD Phase 0A), recorded and closed

No finite artifact can settle these; each was stopped before building apparatus. Source
faithfulness was still spot-checked where cheap, and any note is recorded.

| A-number | declaration shape | note |
|---|---|---|
| A000945 | `answer ↔ ∀ p prime, ∃ n ≥ 1, a n = p` | Euclid–Mullin; refuting needs "prime never occurs". Lean `a`/`b` faithful (`a 1..7 = 2,3,7,43,13,53,5` = DATA). |
| A037274 | `∀ n ≥ 2, ReachesPrime n` with `ReachesPrime n := ∃ k, prime` | home primes; negation is `∃n ∀k`. `primeFactorSplice` verified faithful (`foldl decimalAppend 0` = concatenation). |
| A081091 | `answer ↔ Set.Infinite {p \| p.Prime ∧ p.bits.count true = 3}` | faithful: an odd prime with 3 one-bits is exactly `2ⁿ+2ⁱ+1`, `0<i<n`. |
| A100800 | `∀ n ≠ 0, a n ≠ 0` where `a n = 0` iff **no** iterate works | negation is `∃n ∀k`. |
| A101779 | `∀ n ≥ 1, ∃ k, Ak n k` | pure existence; a zero cannot disprove (`CONSTRUCTION_ONLY`). |
| A102722 | `(fun n => a n) ~[atTop] (1 − γ)·n` | asymptotic. |
| A103885 | `∀ m ≥ 1, ∃ P Q : Polynomial ℝ, …` | `CONSTRUCTION_ONLY`. |
| A103662 `conjecture` | `∃ N, ∀ n > N, a n = 0` | eventual quantifier; the *variant* `a_40` was searched (above). |
| A105210 `conjecture` | `∃ K, Set.Infinite K ∧ …` | `CONSTRUCTION_ONLY`; the companion 5-start disjointness was searched (above). |
| A105751 (×2) | `Tendsto … (nhds 1)` | asymptotic (Moll's 2-adic / p-adic valuation conjectures). |
| A105801 | `∀ k > 0, ∃ m, ∀ n > m, a n ≡ a (m+1) [MOD 3^k]` | eventual quantifier. Faithful — OEIS COMMENT (Giovanni Resta, Nov 17 2010) states exactly this. Lean `a` matches DATA `1,2,10,6,8,7,46,160,103,790,2680,1735`; `a n ≡ 7 (mod 9)` for `n ≥ 10` reproduced; the orbit grows (26 digits by `n = 79`), no cycle. |
| A108129 | `a 254602 = -1 ∧ ∀ 1 ≤ n < 254602, a n ≠ -1` | Riesel problem; the first conjunct needs a covering-set proof, not a finite object. `k = 2·254602 − 1 = 509203` ✓ correct. |
| A109671 | `answer ↔ ∀ m > 0, ∃ n > 0, a n = m` | Lean recursion verified faithful to "smallest positive number with `\|a(2n+1) − a(2n−1)\| = a(n)`" (strict `>` correctly forces the `+` branch on ties). |
| A109845 | `Set.Infinite {n \| (a n).Prime}` | Lean `a` matches the lcm±1 source (`2,3,5,31,929,863971,…`), shifted by one index. |
| A110566 | `∀ m odd, ∃ n > 0, a n = m` | faithful (COMMENT: "It is conjectured that every odd number occurs in this sequence"). |
| A111114 | `∃ᶠ n in atTop, a n > a (n+1)` | "infinitely often". `a 0 = a 1 = 0` from `Nat` division by `π(n) = 0` — harmless at `atTop`. |
| A113213 | `=O[atTop] n³` | asymptotic. Note `a 1 = 0` because `m = 0` is admitted and `2¹` is prime. |
| A113258 | `answer ↔ ∃ n > 4, ∃ b > 1, ∃ e > 1, a n = b^e` | `CONSTRUCTION_ONLY`. |
| A113609 | `answer ↔ ∃ q ≥ 10⁶, …` | `CONSTRUCTION_ONLY` (needs two prime powers differing by 2 above 10⁶; cf. 25/27). |
| A114137 (×2) | `Set.Infinite {n \| a n = 1}` ; `∀ k odd, ∃ n, a n = k` | neither is finitely refutable. |
| A114362 (×2) | `Irrational (…)` ; `=O[atTop]` | irrationality + asymptotic. |
| A114831 | `Tendsto (a(n+1)/a n) atTop (nhds √3)` | asymptotic; the fixed-point equation `r = 1 + 2/(r+1) ⇒ r² = 3` confirms the constant is right. |
| A115366 | `∃ L, Tendsto … ∧ 1.77 ≤ L ≤ 1.78` | asymptotic + numeric bracket. |
| A117027 | `∃ L, Tendsto ratioSeq atTop (nhds L) ∧ 0.8 < L < 0.9` | asymptotic + bracket; `a 1 = 2·7 − 3·5 = −1` ✓ matches DATA. |
| A034693 (×2) | `=O[atTop] (log n · log log n)` ; `¬BddAbove …` | asymptotic **and mutually contradictory** — the file formalizes both Ordowski's conjecture and Greathouse's explicit contradiction of it as `research open`; at most one can hold. |

---
