# TxGraffiti C-C phase one: exact child-side correction result

Date: **2026-08-14 UTC**

Evidence split: **DEVELOPMENT**

Final status: **ZERO_BOUNDED**

Phase one tested the correction preregistered in
[`txgraffiti-cc-phase1.md`](txgraffiti-cc-phase1.md): replace the invalid
parent-witness destruction score with signed graph covers and an exact
child-side expansion guard.  All three arms completed within their hard
60-second process caps, and all three durable streams pass the strict Method
v1.5 hash-chain and nauty-canonicalization linter.

## Exact denominator

| Frozen arm | Proposed | Canonical unique | Applicable exact | Residual zero | Residual positive | Crossing |
|---|---:|---:|---:|---:|---:|---:|
| `CATALOGUE` | 512 | 3 | 2 | 1 | 1 | 0 |
| `GENERIC` | 5,200 | 42 | 38 | 14 | 24 | 0 |
| `WALL_NAVIGATION` | 389 | 120 | 120 | 47 | 73 | 0 |
| **Total** | **6,101** | **165** | **160** | **62** | **98** | **0** |

The exact residual distributions were:

```text
CATALOGUE:       0:1, 1:1
GENERIC:         0:14, 1:20, 2:4
WALL_NAVIGATION: 0:47, 1:67, 2:6
```

No row is a counterexample candidate, certificate task, release, or novelty
claim.

## What changed—and what failed

The exact child guard removed the phase-zero inference error: an equality
child was expanded only after exact optimization showed that its independent
domination number had not fallen.  But the complete observed switch profile
was one-sided:

```text
115 exact two-switch children
i(child) > i(parent):  0
i(child) = i(parent): 47
i(child) < i(parent): 68
```

The corrected traversal found a broad equality plateau, but no local move in
the frozen sample raised the invariant needed for a crossing.  This rules out
another depth increase of the same degree-preserving two-switch operation as
a justified next step.

Signed two-lifts also concentrated on equality—`14/38` applicable generic
cover classes—but were an inefficient proposal language.  The generic arm
made 5,200 labeled proposals and found only 42 canonical classes, four of
which were disconnected.  The complete `K3,3` two-lift catalogue collapsed
from 512 masks to three canonical classes and only two connected classes.
Further sampling of the same covers would mostly buy duplicates.

## Next revision

Phase two should change the construction, not its random seed or depth.  The
required family should carry a structural certificate that pins a small
maximal matching while allowing independent domination to vary globally.  A
promising construction now under a separate freeze is a subdivided cubic core
whose subdivision vertices receive a perfect matching: the core vertices form
an independent unmatched reservoir, while a cubic counting bound can certify
the resulting maximal matching as minimum.  That directly controls `mu*`
without relying on a parent witness and leaves only `i(G)` to optimize.

## Artifacts

- [`txgraffiti-cc-phase1-manifest.json`](txgraffiti-cc-phase1-manifest.json)
- [`../../../scripts/search_txgraffiti_cc_phase1.py`](../../../scripts/search_txgraffiti_cc_phase1.py)
- [`txgraffiti-cc-phase1-ledgers/`](txgraffiti-cc-phase1-ledgers/)

Together with phase zero, this gives 297 retained exact graph evaluations of
the target and zero crossings.  That is a bounded search result, not evidence
that the universal conjecture is true.
