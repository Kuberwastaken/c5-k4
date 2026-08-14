# Wave 2: fresh DeepMind-corpus live search

Date: 2026-08-14 UTC. Source pin:
`google-deepmind/formal-conjectures@b33d8678a28118c95d8d4f60b11faaf39ccff1e6`.
This is a live exploratory lane, not an uncontaminated benchmark result. Every
discovery subprocess had the same hard wall-clock cap of 60 seconds. A bounded
zero below is evidence only.

## Terminal outcome

Three current, previously unsearched declarations received literal-shape,
repository-status, source/database, and three-arm search gates. One arm found a
new exact witness:

```text
OeisA113019.a 387420489 = 387420489
387420489 = 9^9, has 9 decimal digits, and has digital root 9.
```

Thus `387420489` is a fixed point other than `1` and `32`. It falsifies the
universal right-hand side of `OeisA113019.conjecture` and answers the source's
question "Are there any others?" affirmatively. Because the Lean declaration is
written as `answer(sorry) ↔ <universal statement>`, this is a resolution of the
intended answer and a source-record correction, not a claim that the opaque
`answer(sorry)` biconditional itself has been refuted. Exact GitHub and web
searches after discovery found no prior A113019 report containing this witness.

The other two targets returned bounded zeroes: no Dean `k=5` counterexample and
no zero-free ternary expansion of `2^n` beyond the known endpoint.

## Selection and pre-compute gates

An exact text scan of every existing
`results/expansion/live-search-2026-08-14/*.md` found no occurrence of
`DeanCycles`, `dean_conjecture`, `A104320`, or `A113019`. The targets are actual
modules in the pinned DeepMind tree, not reconstructed Written on the Wall I
items.

| declaration | pinned blob / file SHA-256 | resolution shape |
|---|---|---|
| `Arxiv.2605.02731.dean_conjecture.variants.five` | blob `4a65620a7ff37a6d3f005f6db3705e26d793b3cf`; `c3d4a7ba8473304689b0d03548157376ce7958155085a9feb8d08552fc7e025e` | A finite graph with minimum degree at least five and no cycle of length divisible by five makes the intended answer false. |
| `OeisA104320.conjecture` | blob `f5f1d45bd5ccbc9659c87a9a39a6b5e07a4fd505`; `ca9a738cafdda5231e6b37e0190051857d7c1a0adfe42306297dbf781abef9b8` | This is a direct universal theorem, with no answer wrapper. One `n > 15` for which the ternary expansion of `2^n` has no zero is a literal counterexample. |
| `OeisA113019.conjecture` | blob `ee208238e42c4ed41e77bdac7ec065c2021efca3`; `10cd6398dc5228795841ee606603316bb1d14fc73ff20397ebd348f7fe4dc2ff` | A fixed point other than `1,32` falsifies the proposed universal RHS and determines the intended Boolean answer. |

All three declarations are tagged `@[category research open]` at the pin. Git
history shows Dean's module was introduced by commit `547f309edcc2` / merged PR
[#4878](https://github.com/google-deepmind/formal-conjectures/pull/4878), and
both OEIS modules by commit `d7032450c559` / merged PR
[#4450](https://github.com/google-deepmind/formal-conjectures/pull/4450).
There are no later commits touching any of the three pinned files. Before
compute, exact issue/PR searches for each module and declaration name found no
mathematical resolution; the only result was Dean's statement-introduction PR.
After the A113019 crossing, searches for `387420489`, `9^9 A113019`, and
`A113019 fixed point` likewise returned no repository issue or PR.

A superficially attractive fourth target, A100434, was rejected before compute:
closed PR [#4560](https://github.com/google-deepmind/formal-conjectures/pull/4560)
already reports its sign/index discrepancy. This demonstrates that the status
gate was applied rather than merely documented after search.

## Frozen arms and receipts

`CATALOGUE`, `GENERIC`, and `WALL_NAVIGATION` were separately invoked for each
target under `timeout -s KILL 60s`. All final invocations exited normally below
the cap.

| target | arm | exact work | elapsed | outcome |
|---|---|---|---:|---|
| Dean `k=5` | `CATALOGUE` | All 996 connected Graph Atlas graphs through order 7; exact minimum degree and simple-cycle enumeration | 0.185 s | 5 eligible, each had a 5-cycle; zero crossings |
| Dean `k=5` | `GENERIC` | Seeded `G(n,p)`, orders 6--14, 4,000 proposals; exact hypothesis and cycle test | 0.794 s | 1,460 eligible; zero crossings |
| Dean `k=5` | `WALL_NAVIGATION` | Deletion walks from complete graphs on 6--10 vertices, retaining minimum degree five and minimizing exact 5-cycle count | 0.108 s | 43 accepted/evaluated deletion states; zero crossings; best wall `K6`, graph6 `E~~w`, with 72 unoriented 5-cycles |
| A104320 | `CATALOGUE` | Every `16 <= n <= 5000`, exact integer conversion of `2^n` to base 3 | 4.409 s | 4,985 checked; zero crossings; minimum count 2 at `n=17` |
| A104320 | `GENERIC` | Seed `0x104321`; 160 uniform exponents in `5001..40000` | 7.066 s | zero crossings; smallest observed count 1,067 at `n=5029` |
| A104320 | `WALL_NAVIGATION` | Low-zero records on a stride-11 scan of `5001..15000`, then deterministic radius-64 neighborhoods of record setters | 6.748 s | 1,039 final evaluated points; zero crossings; smallest observed count 993 at `n=5009` |
| A113019 | `CATALOGUE` | Direct evaluation for every `0 <= n <= 1,000,000` | 1.534 s | fixed points exactly `1,32` in this prefix |
| A113019 | `GENERIC` | Seeded 50,000 integers with independently chosen decimal lengths 1--1,000 | 0.881 s | fixed points `1,32`; no unexpected witness |
| A113019 | `WALL_NAVIGATION` | Necessary-form candidates `n=d^r`, `1 <= d <= 10000`, `0 <= r <= 9` | 0.202 s | 100,000 candidate pairs; fixed points `1,32,387420489`; one crossing |

The target-specific wall coordinate for A113019 is exact: if `n` is a positive
fixed point, and `d` and `r` are its decimal digit count and digital root, then
the definition forces `n=d^r`, with `1 <= r <= 9`. This converts an enormous
flat integer search into a tiny structured candidate family.

## Independent replay and source/database sanity

### A113019 crossing

A second evaluator did not use the source's modulo-nine digital-root formula.
It converted `387420489` to the decimal string, counted nine characters, and
repeatedly summed its digits: `3+8+7+4+2+0+4+8+9 = 45`, then `4+5 = 9`.
Separately, integer exponentiation gave

```text
9^9 = 387420489.
```

The inequalities against `1` and `32` are immediate. A separate finite
candidate enumeration for digit counts `d=1..10` returned exactly
`(d,r,n) = (1,1,1), (2,5,32), (9,9,387420489)`. This range is exhaustive:
for every `d >= 11`, `d^9 < 10^(d-1)`, so no `d^r` with `r <= 9` can have `d`
decimal digits. At `d=11` this inequality is direct, and
`9 log10(d) - (d-1)` is strictly decreasing thereafter. The independent replay
therefore not only confirms the witness but identifies all fixed points of the
literal function.

The current [OEIS A113019](https://oeis.org/A113019) page matches the Lean
definition and still says only that `1` and `32` are fixed points and asks
whether there are others. Its published initial values also agree with the
local evaluator. The new witness is consequently a source-answer correction,
not an indexing or definition mismatch.

### A104320 source replay

The current [OEIS A104320](https://oeis.org/A104320) definition is exactly the
number of zero digits in the base-three representation of `2^n`, and it states
the same `n>15` conjecture. The official b-file contains 10,001 rows for
`n=0..10000`. An independent exact recomputation compared every row and found
zero mismatches; the last row is `(10000,2063)`. The related OEIS A102483 page
records `0,1,2,3,4,15` as the known zero-free exponents and reports much larger
prior bounds. The present arm is therefore a calibration/confirmation, not a
novel bound.

### Dean graph replay

The Graph Atlas order counts independently matched the standard connected
counts `1,1,2,6,21,112,853` for orders 1--7. The five eligible graphs were

```text
(6,E~~w), (7,Fvx~w), (7,F~^nw), (7,F~^~w), (7,F~~~w).
```

A second permutation-based cycle checker, separate from the discovery DFS,
reconfirmed minimum degree at least five and produced an explicit 5-cycle in
each. For the wall graph `E~~w = K6`, the count 72 also follows independently
from `C(6,5) * 4! / 2`.

The source-status check agrees with
[arXiv:2605.02731](https://arxiv.org/abs/2605.02731): Dean's conjecture is known
for all `k != 5`, leaving exactly the selected finite case. The bounded search
does not approach a proof and found no candidate requiring external database
lookup.

## Classification and method observation

- A113019: **ANSWER-RHS DISPROVED / SOURCE CORRECTION CANDIDATE**, with exact
  witness `387420489` and an independent exhaustive fixed-point argument.
- A104320: **HOLD_BOUNDED**, zero direct counterexamples in the frozen arms and
  exact agreement with the official 10,001-row b-file.
- Dean `k=5`: **HOLD_BOUNDED**, zero finite graph witnesses in 5 catalogue plus
  1,460 generic eligible graphs and the wall walk.

The useful selector lesson is that answer-wrapped declarations should not all
be discarded: when the RHS has a finite witness shape, a witness can determine
the intended answer even though it does not falsify the opaque biconditional.
Conversely, the A100434 rejection shows that literal endpoint failures must be
status-gated before compute, because a closed, unmerged PR can already contain
the same observation.
