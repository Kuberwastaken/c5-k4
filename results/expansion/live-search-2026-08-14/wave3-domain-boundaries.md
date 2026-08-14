# Wave 3: domain and endpoint boundaries

Date: 2026-08-14 UTC. Frozen source:
`google-deepmind/formal-conjectures@b33d8678a28118c95d8d4f60b11faaf39ccff1e6`.
This is a live audit, not part of the uncontaminated benchmark. Every executable
arm and every replay was externally capped with `timeout -s KILL 60s`.

## Terminal result

One fresh source/formalization defect was found, but it does **not** falsify the
mathematical conjecture:

```text
FormalConjectures/Wikipedia/BatemanHornConjecture.lean
CountSimultaneousPrimes polys x
```

is documented locally as counting positive integers `n <= x`, while its
`Finset.range (floor x + 1)` includes `n = 0`. The cited source is narrower
again: it counts positive integers `n < x`. For the admissible test polynomial
`f(X)=X+2`, the frozen helper returns `1` at `x=0`, while both intended positive-
integer readings return `0`. At `x=1` it returns `2`, versus `1` for positive
`n <= x` and `0` for positive `n < x`.

This is an endpoint/domain transcription defect in the helper. It changes the
count by a bounded amount and therefore leaves the stated `~[atTop]`
asymptotic equivalence unchanged. It is **not a disproof of Bateman--Horn** and
not a false instance of the open theorem.

The other two fresh executable target clusters returned bounded zeroes. No
integer/domain-boundary counterexample was found for the Firoozbakht/Andrica
prime-root cluster or for the exponential-square-root variant of Erdős 683.

## Status and source gate

The gate was performed before computation.

- All selected declarations are still `@[category research open]` in the
  frozen tree. Exact frozen blobs are Bateman--Horn `10af1913...`, Firoozbakht
  `d7a38386...`, Andrica `179b354a...`, and Erdős 683 `15c1bfb1...`.
- Exact GitHub searches in `google-deepmind/formal-conjectures`, including open
  and closed issues and pull requests, returned no target-specific item for
  `BatemanHorn`/`CountSimultaneousPrimes`, Firoozbakht, Andrica, or
  `erdos_683`/`exp_sqrt`.
- An exact scan of the current live-search reports and expansion reports found
  no prior evaluation of these declarations. Benchmark inventory mentions were
  not treated as mathematical work.
- The [Bateman--Horn source](https://en.wikipedia.org/wiki/Bateman%E2%80%93Horn_conjecture)
  says that `P(x)` counts prime-generating integers among the **positive
  integers less than `x`**. The frozen local docstring instead says positive
  integers `n <= x`, and the implementation includes zero. Thus both the zero
  endpoint and, relative to the cited source, integer upper endpoints are
  broader than advertised.
- The [Firoozbakht source](https://en.wikipedia.org/wiki/Firoozbakht%27s_conjecture)
  uses one-based primes and `n >= 1`. The formal `Nat.nth Prime` is zero-based,
  while the exponent is `1/(n+1)`, so formal `n=0` is exactly source `n=1`, not
  an extra mathematical case. The [Andrica source](https://en.wikipedia.org/wiki/Andrica%27s_conjecture)
  has the same one-based/zero-based translation.
- [Erdős Problem 683](https://www.erdosproblems.com/683) is currently open and
  states the heuristic bound `P(binomial(n,k)) > exp(c sqrt(k))` for
  `k <= n/2`. The formal variant adds the necessary `0 < k`; it does not expose
  an unintended `k=0` case.

Required exclusions were applied before target selection. A111291, A109074,
and A100434 were excluded by instruction and by their existing reports. The
tempting `OeisA211417.general_divisibility` degeneracy (`D=0`) was also rejected
before compute because upstream issue
[#4923](https://github.com/google-deepmind/formal-conjectures/issues/4923)
already records it. The broader known-misformalization lists in issues #4896
and #4923 were treated as excluded status, not as discovery leads.

## Target 1: Bateman--Horn counting domain -- fresh defect

Frozen definition and theorem:

```lean
noncomputable def CountSimultaneousPrimes (polys : Finset ℤ[X]) (x : ℝ) : ℕ :=
  Finset.card (Finset.filter
    (fun n : ℕ => ∀ f ∈ polys, (f.eval ↑n).natAbs.Prime)
    (Finset.range (⌊x⌋₊ + 1)))

theorem bateman_horn_conjecture ... :
  (fun x : ℝ => (CountSimultaneousPrimes polys x : ℝ)) ~[atTop] ...
```

The executable probe used `f(X)=X+2`, so `f(0)=2` is prime.

| arm | exact work | time | result |
|---|---|---:|---|
| literal boundary | `x=-1,-1/2,0,1/2,1,3/2,2,5/2,3`; direct primality | 0.02 s | formal/local-positive/cited-positive-strict counts at `x=0` are `1/0/0`; at `x=1`, `2/1/0` |
| catalogue | every half-integer `x` from `-10` through `1000` (2,021 rows) | 0.91 s | formal count exceeds local positive-`<=` count by exactly 1 on every row; against cited positive-`<`, offset is 1 on 1,854 rows and 2 on 167 rows |
| domain wall | all integer walls `x=0..10000` | 7.96 s | offset from the cited strict count is 1 normally and 2 at 1,228 positive walls where `x+2` is prime; no timeout |

Independent replay used divisor enumeration rather than the sieve/prefix
evaluator. It obtained:

```text
x=0: formal {n=0} count 1; positive <= count 0; positive < count 0
x=1: formal {n=0,1} count 2; positive <= count 1; positive < count 0
x=3: formal {n=0,1,2,3} count 3; positive <= count 2; positive < count 1
```

Classification: **FRESH FORMALIZATION/SOURCE DEFECT, ASYMPTOTICALLY INERT**.
Removing `n=0`, and choosing `< x` versus `<= x`, changes the counting function
by at most a fixed finite amount for a fixed polynomial family. Such a bounded
perturbation does not attack the intended asymptotic mathematics.

## Target 2: Firoozbakht and Andrica lower endpoint

These two declarations share the same prime-index boundary and were treated as
one correlated cluster. For formal index `i`, with `p=prime(i)` and
`q=prime(i+1)`, the checks were exact integer comparisons:

- Firoozbakht: `q^(i+1) < p^(i+2)`;
- Andrica: if `d=q-p-1 > 0`, then `d^2 < 4p`.

| arm | exact work | time | result |
|---|---|---:|---|
| literal boundary | formal `i=0..9` | 0.02 s | both inequalities pass all ten; formal `i=0` is source `n=1` |
| catalogue | first 3,000 consecutive-prime pairs, ending `27449,27457` | 0.40 s | zero failures for either declaration |
| domain wall | all 20 record-prime-gap indices among primes through 2,000,000 | 0.60 s | zero failures; largest observed Andrica value is the known `sqrt(11)-sqrt(7) ~= 0.670873` at formal `i=3` |

An independent deterministic Miller--Rabin prime check and fresh integer-power
comparison replayed formal indices `0,1,3,104070`. The last row is
`p=1357201`, `q=1357333`; both exact inequalities pass, and the Andrica squared
margin is `4p-(q-p-1)^2 = 5411643 > 0`.

Classification: **HOLD_BOUNDED / SOURCE-ALIGNED**. The apparent zero endpoint
is only the correct zero-based encoding of the source's first prime.

## Target 3: Erdős 683 exponential-square-root wall

For `P(n,k)`, the largest prime factor of `binomial(n,k)`, the bounded probe
fixed the positive constant `c=log(2)/17`. Its inequality

```text
P(n,k) > exp(c sqrt(k))
```

was checked without floating point. Every tested row has `k <= 249 < 17^2`
and exact largest prime factor `P(n,k) >= 2`; hence
`sqrt(k)/17 < 1`, so `exp(c sqrt(k)) < exp(log 2) = 2 <= P(n,k)`.

| arm | exact work | time | result |
|---|---|---:|---|
| literal boundary | `k=1`, `n=2..30` | 0.02 s | 29/29 pass; minimum `P=2` |
| catalogue | every `1 <= k <= n/2` for `2 <= n <= 500` (62,500 pairs) | 0.31 s | zero failures; minimum observed `log(P)/sqrt(k)` is about `0.392684` at `(498,249)`, `P=491` |
| wall | `1 <= k <= 200`, `2k <= n <= 2k+500` (100,200 pairs) | 0.57 s | zero failures; wall minimum about `0.423128` at `(400,200)`, `P=397` |

The discovery evaluator used descending factorial valuations. Independent replay
instead formed the exact binomial coefficients and trial-factored them. It
recovered `P(2,1)=2`, `P(498,249)=491`, and `P(400,200)=397`. Together with
the exact bounds `k ∈ {1, 249, 200}` and hence `k < 17^2`, this independently confirms the displayed
fixed-constant inequality in all three rows.

Classification: **HOLD_BOUNDED / SOURCE-ALIGNED**. This finite witness-constant
probe is not evidence for a global existential constant beyond the tested
domain.

## Disposition

- Fresh false open declarations: **0**.
- Fresh source/formalization defects: **1**, the Bateman--Horn counting helper's
  zero and upper-endpoint convention.
- Intended mathematical conjectures attacked: **0**.
- Executed target clusters: **3**; discovery arms: **9**; replay failures or
  timeouts: **0**.
- No git add, commit, push, issue, PR, release, or other outward action was
  performed.
