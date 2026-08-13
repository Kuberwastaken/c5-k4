# Phase 1 result: R(5,5) cyclic-orbit flip

Date: **2026-08-13 UTC**

Verdict: **HOLD_BOUNDED**.  The complete four-candidate frozen family produced
no 43-vertex `(5,5)`-Ramsey graph and therefore no improved lower-bound
candidate.

## Live gate

Immediately before activation, DeepMind upstream `main` remained
`d16e05aded22b8c467a0a27c14b2311f53185006`; the exact source retained blob
`41b81b68621b270892a3b0f238302b4823a99e4b` and the fixed-value declaration
remained `research open` with `answer(sorry)`.  The scoped issue/PR refresh
found no exact-value claim or improved lower bound.  The relevant repository
state remained merged formalization PR #2436, closed duplicate PR #3409, and
open intake issue #2364.

## Baseline sanity

The evaluator reconstructed `Cyclic(43)` from the red distance set

```text
{1,2,7,10,12,13,14,16,18,20,21}.
```

Exact enumeration of all `binom(43,5) = 962598` five-subsets found:

- exactly **43** red `K5`s;
- exactly **0** blue `K5`s;
- the red cliques were exactly the 43 cyclic translates of
  `{0,1,2,22,23}`;
- first red witness: `[0,1,2,22,23]`;
- red adjacency SHA-256:
  `64c36ec01706913e2e6c475b1c2b9dc9b648a52ce4a1b8a16bd5e5a3c9c2ac36`;
- blue adjacency SHA-256:
  `f0f3e5a184af51b7db791ab39e6c8b0d8967e6b4d096c979cb1148d607ca4256`.

This reproduces the exact near-miss geometry reported in
arXiv:2212.12630v3.  The gate completed in 1.604471 seconds.

## Complete frozen-family result

Each child deletes one entire critical red distance orbit and was evaluated in
a separate externally capped process.  Every process checked all 962,598
five-subsets and completed far below 60 seconds.

| deleted distance | red `K5`s | blue `K5`s | first blue witness | seconds |
|---:|---:|---:|---|---:|
| 1 | 0 | 172 | `[0,1,4,5,9]` | 1.542973 |
| 2 | 0 | 1,634 | `[0,2,4,6,8]` | 1.745491 |
| 20 | 0 | 1,849 | `[0,3,6,9,26]` | 1.569386 |
| 21 | 0 | 473 | `[0,3,9,24,35]` | 1.547128 |

The full labelled red/blue adjacency SHA-256 values and retained distance sets
are preserved in the append-only ledger for every row.

## Interpretation and stop

The directional prediction was half-correct in every case: deleting any one
of the four critical cyclic orbits destroys all 43 old red `K5`s.  But the
recolored orbit creates many blue `K5`s immediately.  Distance 1 is the
closest child in this family, with 172 monochromatic `K5`s, still far from the
required double zero.

No row triggered the independent Bron--Kerbosch oracle because no child had
both exhaustive counts zero.  The four-member family is exhausted.  Per the
frozen contract there was no second flip, local repair, new distance, or
adaptive expansion.

There is no Lean or novelty candidate and no basis for a lower-bound claim.
No commit, push, release, issue, PR, or other public action was performed by
this trial.
