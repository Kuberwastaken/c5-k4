# OEIS A056777 v4 exponent-asymmetric reachability preflight

**Audit date:** 2026-08-15 UTC

**Disposition:** `STRICT_STOP_CROSSING_UNREACHABLE`

**Evidence class:** target-free `DEVELOPMENT` constructor audit

**Target evaluations:** zero

This is a separate audit of the exponent-asymmetric power / squarefree-triple
surgery proposed in
[`oeis-a056777-near-wall-surgery.md`](../oeis-a056777-near-wall-surgery.md).
It does not reuse the v3 squarefree-triple / squarefree-triple geometry.

The audit evaluates only whether the frozen block coordinates can satisfy the
two simultaneous integer constructor equations. It does not test either
derived terminal for primality, compute `phi` or `sigma` on a target value,
inspect sequence membership for a constructed value, invoke the formal target
predicate, or create a counterexample candidate. It authorizes no workflow,
dispatch, release, issue, pull request, or other public action.

## Source and duplicate gate

At the audit, independent `git ls-remote` and authenticated GitHub reads both
resolved `google-deepmind/formal-conjectures` `main` to
`2411d22e1bd550d050d0eac6c1fb379a76a3e7c5`. The exact target file remained

```text
FormalConjectures/OEIS/56777.lean
Git blob: a6dd44fb981be19a5a8bc19de54ef8e533519627
size: 9022 bytes
```

and therefore retained the previously audited `research open` reverse
implication `OeisA56777.comesFromPrimeQuadruple_of_a` with body `sorry`.

Exact repository issue/PR searches for the declaration, path, and `A056777`
were complete (`incomplete_results=false`). They returned the ingestion and
forward-direction work, but no resolution of the reverse implication. A fully
paginated changed-file scan of every open pull request found six target-path
touches:

| PR | Role |
|---:|---|
| 3691 | mathlib v4.29 migration |
| 4025 | mathlib v4.30 migration |
| 4198 | older broad maintenance update; explicitly leaves the reverse implication as `sorry` |
| 4356 | mathlib v4.31 migration |
| 4428 | mathlib v4.32 migration |
| 4688 | repository module migration |

Their target-file patches change imports, module exposure, tactic syntax, or
the already-proved forward direction; none supplies or claims the reverse
implication.

The live OEIS b-file was byte-identical to the previous frozen source gate:

```text
SHA-256: 8a4d205fea5761af6deac8c2bf23d709c4e7844e792f48bf8616135376835ccf
rows: 166
last row: 166 967164068009
```

That earlier gate independently replayed all source controls and passed with
attestation SHA-256
`83a707f4887a2930543ae20779eeb8441f0a4f0bdc55c1484fd7d4b014d2112d`.
The live byte identity therefore preserves the exact source input previously
replayed rather than substituting an unverified table.

The authoritative source record remains pinned at
`oeis/oeisdata@8872fa543438401edd424a57b67ad5e0737bebfb`, path
`seq/A056/A056777.seq` (Git blob
`defda2ebcb8366d31d6a5a0e93e9884d21418743`). Because the constructor gate
stops before target evaluation, no catalogue row or arithmetic-function value
was replayed in this preflight.

## Frozen constructor domain

The proposed v4 pilot has a power block and a distinct-prime squarefree block:

```text
power base r: prime ranks 385..640 = 2659..4751
power exponent e: 3..6
triple-block primes t<u: prime ranks 1..640 = 2..4751
orientations: power lower / power upper
historical terminal-value band: 10^12+1 .. 10^14
```

There are 256 power bases, four exponents, 204,480 allowed unordered
`(t,u)` pairs, and 5,355 distinct sums `T=t+u`. Canonical newline-stream
hashes binding the constructor metadata are:

```text
prime ranks 1..640:
  98053b04c463f16a78f0c2c362828994cadae614bf997b5b466aea0eaf8071e8
prime ranks 385..640:
  5ad65fc63834deff2a5b656c737c449e4c8f0d61eb08cfca90dc009de5171f07
distinct pair sums:
  4d33bb7e54941e41ccbba55b5d38d87bbb87d78764852a37000f9cfb2e101c7c
```

No parameter was added after a discriminant was inspected.

## Closed-form block coordinates

Write

```text
W = r^e,
g = r^(e-1),
k = 1+r+...+r^(e-2),
h = k+2g.
```

These are the closed-form power-block coordinates appearing in the fixed-block
identities: the power block has coefficient data

```text
alpha = W-g,  k_power = k,  h_power = h.
```

For a squarefree block `X=t*u` with `T=t+u`, the corresponding symbolic data
are

```text
beta = X-T+1,  k_triple = 2,  h_triple = 2T.
```

These formulas are substituted symbolically. No arithmetic-function routine
is called.

For general lower and upper blocks, the development note's two necessary
linear equations for the lower terminal `p` have the form

```text
D*p=N,
C*p=M.
```

An integer construction therefore requires the compatibility equation
`N*C-M*D=0` before terminal selection.

### Power block lower

For lower block `W` and upper squarefree block `X`, define

```text
D = X*k-2W
N = X*(2T-h)+24
C = X*g-W*(T-1)
M = X*(X-T+1-(W-g))+12T-12.
```

Since `X>0`, exact expansion divides the compatibility equation by `X` and
gives the quadratic

```text
-k*X^2 + L*X + C0 = 0,                                  (L)

L  = h*T + W*(k+2) - k - 2g*(k+g),
C0 = -2W*(T-1)^2 - W*(4-h)*(T-1)
     -2W^2 + 2W*g + 24g - 12k*(T-1).
```

Thus an integer squarefree block product requires the exact discriminant

```text
Delta_lower = L^2 + 4k*C0
```

to be a square.

### Power block upper

For lower squarefree block `X` and upper power block `W`, put

```text
N0 = W*(h-2T)+12k,
M0 = W*(T+11+(W-g))-12*(W-g).
```

The compatibility equation is now

```text
-kW*X^2 + B*X + C1 = 0,                                 (U)

B  = -N0*g + 2W^2 + k*M0,
C1 = N0*W*(T-1) - 2W*M0.
```

An integer product requires

```text
Delta_upper = B^2 + 4kW*C1
```

to be a square. These quadratic conditions are necessary before checking
whether a root equals an allowed `t*u`, before solving for `p,q`, and before
any terminal predicate.

## Exhaustive constructor-only diagnostic

An exact arbitrary-precision integer enumeration visited every frozen
`(r,e,T)` coordinate in lexicographic order. It used integer `isqrt` followed
by equality of the square, never floating-point approximation. The two
orientations had separate counters inside one process under the unchanged
60-second external cap.

There are exactly

```text
256 * 4 * 5355 = 5,483,520
```

quadratic profiles per orientation. The full result was:

| `e` | profiles/orientation | lower negative | lower positive nonsquare | lower square | upper negative | upper positive nonsquare | upper square |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 3 | 1,370,880 | 0 | 1,370,880 | **0** | 0 | 1,370,880 | **0** |
| 4 | 1,370,880 | 0 | 1,370,880 | **0** | 0 | 1,370,880 | **0** |
| 5 | 1,370,880 | 0 | 1,370,880 | **0** | 0 | 1,370,880 | **0** |
| 6 | 1,370,880 | 0 | 1,370,880 | **0** | 0 | 1,370,880 | **0** |
| **total** | **5,483,520** | **0** | **5,483,520** | **0** | **0** | **5,483,520** | **0** |

Across both orientations this is 10,967,040 exact compatibility profiles and
zero square discriminants. Consequently:

```text
integer candidate block products X: 0
allowed (t,u) product lookups reached: 0
terminal p equations reached: 0
terminal q equations reached: 0
terminal-primality calls: 0
phi/sigma calls: 0
sequence-membership calls: 0
formal-target calls: 0
```

The empty reachable-row stream has SHA-256
`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.

## Gate decision

The exact decision is **`STRICT_STOP_CROSSING_UNREACHABLE`** for the complete
frozen v4 exponent-asymmetric pilot. Neither orientation can attain even the
necessary integer block-compatibility wall, so dispatching a target evaluator
would be guaranteed to receive no constructed state.

This is a constructor impossibility inside the declared finite rank and
exponent domain, not a bounded hold for A056777 and not a theorem about every
power/triple block. Increasing workers, changing a primality implementation,
or widening only the terminal-value band cannot repair it. Expanding prime
ranks, changing exponents, or changing factor shape would define a new arm and
requires a new source/duplicate and target-free reachability preflight.

There is no frozen target-domain proposal, workflow, candidate, mathematical
result, or publication action from v4.
