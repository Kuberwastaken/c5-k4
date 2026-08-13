# Independent domination leaf transfer: equality is balance-sensitive

Date: **2026-08-13 UTC**

Status: **completed hold in an open degree range; no candidate or public claim**

## Status gate and target

The current DeepMind declarations formalize Cho--Choi--Park Conjecture 1.6
for finite isolate-free graphs, split by parity of maximum degree.

The source proves the conjecture through maximum degree four and reports
omitted checks for degrees five through eight. The exact carrier was selected
at degree nine and the transformed graph has degree ten, outside those
recorded domains. Upstream still labels both declarations `research open`.

## Equality carrier and frozen move

For `H(q,p)`, begin with a `q`-clique and attach `p` private pendant leaves to
each center. The paper identifies
`H(floor(D/2)+1,ceil(D/2))` as its extremal family.

The selected `H(5,5)` carrier has

`(n,D,i)=(30,9,21)`

and exact odd-case residual zero:

`84*30 - 120*21 = 0`.

Before development evaluation, the trial froze one move: transfer canonical
leaf 5 from center 0 to center 1. No other leaf or repeated move was tested.

## Database gate

Every one of the 995 connected isolate-free Atlas graphs of orders 2--7 was
evaluated by exhaustive independent-dominating-set search. The gate checked
13,921 subsets and found zero violations.

Four small paper-family controls reproduced equality:

| graph | `D` | `i` | residual |
|---|---:|---:|---:|
| `H(2,1)` | 2 | 2 | 0 |
| `H(2,2)` | 3 | 3 | 0 |
| `H(3,2)` | 4 | 5 | 0 |
| `H(3,3)` | 5 | 7 | 0 |

An exact MILP independently reproduced `i(H(5,5))=21` with zero gap.

## Exact development result

The transformed graph remains isolate-free and has center degrees

`(8,10,9,9,9)`.

Its exact coordinates are

`(n,D,i)=(30,10,20)`.

The even-case inequality evaluates as

`144*20 = 2880 <= 3120 = 104*30`,

giving safe-side residual 240. The exact MILP returned zero gap and an
explicit independent dominating set of order 20.

The canonical graph digest is
`14a3c025cfada4fc36bcaea850d95b0ce0b05b59f5070b5846de76f78b5465ac`.

## Independent structural audit

The result has a closed-form explanation. For a clique of `q>=2` centers with
positive private-leaf counts `p_j`, an independent dominating set can contain
at most one center.

- With no center, it must contain every private leaf.
- With center `j`, it must contain every leaf owned by the other centers, and
  no leaf owned by `j` is needed.

Therefore

`i = 1 + sum_j p_j - max_j p_j`.

For leaf counts `(4,6,5,5,5)`, the six structurally possible minima have sizes
`22,20,21,21,21,25`; the exact optimum is 20. The independent verifier replayed
each candidate's independence and domination and reproduced the MILP witness.

## Interpretation

The equality family is balance-sensitive. Moving one leaf increases the
maximum degree from odd 9 to even 10, while concentrating six leaves at one
center makes that center cheaper to choose and lowers independent domination
from 21 to 20. Both coordinate changes push the conjecture strongly toward
the safe side.

The premise is fully preserved, so this is genuine prospective negative
evidence rather than a vacuous hold or known-domain calibration. It also gives
a reusable structural coordinate formula for future nonuniform private-leaf
experiments. No adaptive extension, random search, WoW I source, commit,
release, or public action occurred.
