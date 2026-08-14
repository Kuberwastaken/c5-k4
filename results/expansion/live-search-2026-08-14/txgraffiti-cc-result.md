# TxGraffiti C-C live trial: exact bounded result

Date: **2026-08-14 UTC**

Evidence split: **DEVELOPMENT**

Final status: **ZERO_BOUNDED_WITH_GENERIC_TIMEOUT_PREFIX**

This trial tested the still-open TxGraffiti conjecture

```text
for every connected r-regular finite simple graph G with r >= 3,
i(G) <= mu*(G),
```

where `i(G)` is the independent domination number and `mu*(G)` is the
minimum size of a maximal matching.  The source/status audit, exact residual,
database gate, frozen proposal arms, and publication conditions were fixed
before execution in [`txgraffiti-cc-phase0.md`](txgraffiti-cc-phase0.md).

## Result

No evaluated graph crossed the wall `mu*(G) - i(G) = 0`.  There is therefore
no counterexample candidate, formal-certificate task, release, or novelty
claim from this trial.

| Frozen arm | Proposed | Exact canonical rows | Residual zero | Residual positive | Terminal status |
|---|---:|---:|---:|---:|---|
| `CATALOGUE` | 41 | 35 | 16 | 19 | `COMPLETED` in 2.835 s |
| `GENERIC` | 66 | 65 | 1 | 64 | `TIMEOUT_PREFIX`; no summary row |
| `WALL_NAVIGATION` | 331 | 37 | 21 | 16 | `COMPLETED` in 45.045 s |
| **Total retained** | **438** | **137** | **38** | **99** | **zero crossings** |

The exact residual distributions were:

```text
CATALOGUE:       0:16, 1:9, 2:5, 3:2, 4:1, 5:1, 7:1
GENERIC prefix:  0:1,  1:15, 2:20, 3:16, 4:10, 5:3
WALL_NAVIGATION: 0:21, 1:16
```

Every retained row is an exact optimum pair from independently constrained
binary ILPs.  Every process first passed the repeated nine-row Graph Atlas
database-sanity gate.  The two completed streams pass the strict Method v1.5
hash-chain/canonicalization linter.  The generic stream passes the same linter
only with its explicit `--allow-timeout-prefix` mode, because the hard
60-second process cap killed the worker during the next exact solve before it
could append a summary.  Its 65 already-fsynced exact rows remain valid, but
the arm is not reported as a completed bounded hold.

## What the arm comparison says

The targeted arm concentrated strongly on the conjectured boundary:
`21/37 = 56.8%` of its exact rows had residual zero, compared with
`1/65 = 1.5%` in the generic prefix.  That is useful prospective evidence
that equality geometry can aim computation at a relevant wall even when it
does not produce a counterexample.

The separating move itself failed for a specific structural reason.  It kept
one small maximal matching feasible while deleting edges chosen to destroy
the parent's minimum independent dominating sets.  But destroying those old
sets often exposed *new, smaller* independent dominating sets:

- a switch from `complement(C5[K4])` destroyed four of five parent minimum
  sets, yet moved from `i=mu*=8` to the safe side `i=6 < 7=mu*`;
- a `K3,3` child destroyed both parent size-three sets, but acquired
  `i=mu*=2`;
- circular-ladder children repeatedly stayed on equality or reduced `i`
  before `mu*` could be separated.

Call this **replacement-set collapse**.  The parent's list of minimum sets is
not a lower-bound certificate for the child, so the destruction score is not
monotone in `i(G)`.

## Revision forced by the zero

Do not deepen this two-switch tree unchanged.  A successor arm must either:

1. preserve an independently checkable lower bound on independent domination
   while pinning the maximal matching; or
2. score proposals by an exact or certified relaxation of the *child's*
   residual, rather than by the number of parent witnesses destroyed.

This is the useful negative outcome: the wall-ranking idea worked, but the
chosen local coordinate did not control the invariant it was meant to raise.
The next trial should test the revised coordinate on a fresh frozen arm, not
reinterpret these rows after the fact.

## Reproduction

The exact contract artifacts are:

- [`txgraffiti-cc-statement.txt`](txgraffiti-cc-statement.txt)
- [`txgraffiti-cc-manifest.json`](txgraffiti-cc-manifest.json)
- [`txgraffiti-cc-resolution-card.json`](txgraffiti-cc-resolution-card.json)
- [`../../../scripts/search_txgraffiti_cc_live.py`](../../../scripts/search_txgraffiti_cc_live.py)
- [`txgraffiti-cc-ledgers/`](txgraffiti-cc-ledgers/)

The discovery worker used the frozen nauty `labelg` binary named in the
manifest, exact SciPy MILPs capped at eight seconds each, and the repository's
hard 60-second Method v1.5 process wrapper.
