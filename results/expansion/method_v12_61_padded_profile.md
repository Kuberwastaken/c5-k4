# Method v0.12: WOWII 61 padded-profile scope and partial-loss identity

Date: **2026-08-13 UTC**

Outcome: **the exact zero-padded profile audit now reaches order ten, and Lean
now identifies the precise residual degree-sum condition behind every partial
profile comparison.**

The repaired coupling has no failure among all 105,582,418 graphical weak-
dominance pairs across orders one through ten.  This remains finite evidence;
no general implication theorem is claimed from the search.

The formal result is exact and unbounded: the first `k` excess entries plus
the `2k` baseline equal the degree sum lost in the first `k` canonical
Havel--Hakimi steps.

This lane does not prove WOWII 61 or general graphical weak-potential
monotonicity.

## Frozen scope

- New Lean certificate only:
  `lean/GraphConjecture61PaddedProfile.lean`.
- New report only:
  `results/expansion/method_v12_61_padded_profile.md`.
- New fixed-scope ledger only:
  `results/expansion/method_v12_61_padded_profile_ledger.json`.
- No existing file was edited.  No commit, push, release, issue, PR, or other
  external mutation was made.
- Every subprocess was individually capped at 60 seconds.

## Extended exact falsification scope

The v0.11 audit exhaustively covered orders one through eight.  The new search
uses the same mathematical scope and tests, but vectorizes the pair comparisons:

1. generate every descending length-`n` sequence with entries in `[0,n-1]`;
2. retain exactly the simple-graphical sequences by Havel--Hakimi reduction;
3. compute all degree-prefix sums;
4. compute the canonical excess profile `stepLoss - 2` and all cumulative
   profile prefixes, zero-padded through order `n`;
5. for every weak degree-prefix ordered pair, compare every padded profile
   prefix.

New exact counts:

| order | graphical sequences | weak-dominance pairs | failures | runtime |
|---:|---:|---:|---:|---:|
| 9 | 4,361 | 7,477,797 | 0 | 1.29 s |
| 10 | 16,016 | 97,447,686 | 0 | 14.85 s |

Together with v0.11, orders one through ten contain 22,083 graphical sequences
across the separate orders and 105,582,418 tested weak-dominance pairs.  No
zero-padded profile failure occurred.

The JSON ledger fixes the generation domain, graphicality test, pair filter,
profile convention, comparison method, counts, runtimes, timeout, and claim
limit.

## Exact partial-profile identity

For a certified trajectory with chronological profile `p`, Lean proves for
every `k <= length(p)`:

```text
sum(p.take k) + 2*k
  = sum(initial) - sum(havelHakimiStep^[k](initial)).
```

The proof is structural induction on the complete trajectory.  It separately
proves that canonical Havel--Hakimi iteration never increases degree sum, so
every natural-number subtraction in the identity is exact.

This result is the missing algebraic link between chronological profile
prefixes and partial degree loss.  It is stronger than the previous final
closed form because it applies at every intermediate step.

## Weak degree prefixes and residual gaps

The certificate uses the direct mathematical relation

```text
DegreePrefixDominates source target
```

meaning equal list lengths and target degree-prefix sum at most source
degree-prefix sum at every index.  Lean first derives the full degree-sum order.

At coupled time `k`, define residual-gap preservation by

```text
sum(target) + sum(step^[k](source))
  <= sum(source) + sum(step^[k](target)).
```

Equivalently, the source's initial degree-sum advantage has not shrunk after
the two `k`-step eliminations.

Combining this residual condition with the two exact partial-profile identities
gives the formal theorem

```text
sum(targetProfile.take k) <= sum(sourceProfile.take k).
```

Lean also packages the pointwise result: if the residual gap is preserved at
every common active time, all common chronological profile prefixes are
ordered.

## What remains for zero padding

The theorem handles times for which both trajectories are active.  The padded
tail, where one profile has already ended, is simpler algebraically because its
prefix sum has stabilized, but proving the full candidate still requires a
structural residual-gap theorem:

```text
weak graphical degree-prefix dominance
  -> residual gap never shrinks along canonical coupled elimination.
```

That implication is not asserted here.  The 105-million-pair audit is evidence
for it through order ten, not a replacement for proof.

The result narrows the next proof search substantially: instead of manipulating
residue or profile lists directly, it can target preservation of one explicit
degree-sum gap after each coupled Havel--Hakimi step.

## Concrete certificate

`two_one_one_zero_partial_identity` certifies the first non-unit-loss source

```text
[2,1,1,0] -> [0,0,0]
```

with profile `[2]`.  At `k=1`, Lean verifies

```text
2 + 2 = 4 - 0.
```

The trajectory is constructed through the same exact step and loss gates used
by the general theorem.

## Verification

From the pinned `formal-conjectures` checkout:

```bash
timeout 60s lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture61PaddedProfile.lean
```

Result: **PASS** in approximately eight seconds.  The source contains no
`sorry`, `admit`, or custom `axiom`.

## Verdict

The padded profile candidate has now survived an exact order-ten audit of more
than one hundred million graphical weak-dominance pairs.  More importantly,
its prefix condition has been reduced formally to preservation of the source-
target residual degree-sum gap under coupled canonical elimination.  That gap
preservation, not additional scalar potential algebra, is the next substantive
proof obligation.
