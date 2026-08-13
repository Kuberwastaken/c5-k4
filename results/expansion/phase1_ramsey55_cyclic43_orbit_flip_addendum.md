# Phase 1 addendum: R(5,5) cyclic-orbit flip

Date activated: **2026-08-13 UTC**

This addendum activates exactly the four-candidate family frozen in
`phase0_ramsey55_cyclic43_orbit_flip_contract.md`.  It was written together
with the separate zero-candidate Phase 1 ledger row before the baseline or any
development child was evaluated.

## Refreshed live-status gate

Immediately before this addendum was frozen, DeepMind upstream `main` remained
at `d16e05aded22b8c467a0a27c14b2311f53185006`, and
`FormalConjectures/Wikipedia/RamseyNumbers.lean` retained blob
`41b81b68621b270892a3b0f238302b4823a99e4b`.  The fixed-value declaration was
still `research open` with `answer(sorry)` and the bound statements still used
`sorry`.

The refreshed scoped issue/PR search found no exact-value claim or improved
lower bound.  The directly relevant state remained merged formalization PR
#2436, closed unmerged duplicate PR #3409, and open intake issue #2364.  Open
Ramsey-theory PRs #4236 and #3588 concern other Ramsey declarations, not a
solution of `R(5,5)`.

## Activated evaluation and exact outputs

The baseline process must reconstruct the cyclic red graph on `Fin 43` from

```text
{1,2,7,10,12,13,14,16,18,20,21}
```

and enumerate all `962598` five-subsets exactly once, simultaneously counting
red cliques and blue/complement cliques.  It must return exactly 43 red and
zero blue `K5`s and verify that the red set equals all 43 cyclic translates of
`{0,1,2,22,23}`.  Any mismatch stops Phase 1 before development.

Only after that gate passes, run one separate externally capped process for
each frozen orbit deletion, in the exact order

```text
1, 2, 20, 21.
```

Every process is capped at 60 seconds.  Each completed row must include:

- the retained red distance set and deleted distance;
- SHA-256 of the complete sorted labelled red and blue edge lists;
- exact number of all five-subsets checked;
- exact red and blue `K5` counts;
- the lexicographically first red and blue witness, or `null` when absent;
- elapsed time and the strict lower-bound-candidate Boolean.

If and only if both counts are zero, a separate exact Bron--Kerbosch search
must compute maximum clique size in the red graph and its complement.  The row
is a candidate only if both independently return at most four.  Such a row is
only a candidate improvement `44 ≤ R(5,5)` requiring later Lean and novelty
gates; it is not permission for a claim or public action.

No other distance, edge edit, repair, relabeling, retry with a changed family,
or adaptive expansion is permitted.  A timeout, source drift, baseline
mismatch, or independent-oracle disagreement stops the phase immediately.
