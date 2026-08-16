# Method v1.7 — repairs forced by the three-arm result

**Status:** `DEVELOPMENT`. Unfreezes v1.6 legitimately: the freeze condition was
"no v1.7 until the fresh-generation three-arm test has run and been published,
whatever it returns." It ran; [`results/experiment/RESULTS.md`](results/experiment/RESULTS.md)
published it (wall-unique = 1/30, INCONCLUSIVE, substance close to null).

This version contains **only repairs the experiment forced**. No new apparatus.

## R1 — G3-lite must test across a step, not across neighbours

The experiment's most useful by-product. §A3 as written evaluates the sign of
the residual change on *the two smallest members* of a family. On five of the
fifteen crossings (`FP-007`, `FP-008`, `FP-020`, `FP-023`, `FP-026`) the
residual is a floor/ceiling step function, so consecutive members give
`dR = 0` and the literal test **stops a family that does in fact cross**. All
five needed re-indexing or a different transformation (subdivision rather than
path-stretch) before the check would pass.

Replacement rule:

> Evaluate the residual on a run of members long enough to contain at least one
> discontinuity of every floor/ceiling in the expression — in practice, until
> the argument of each rounding operator has advanced by 1. If the residual is
> constant across that run, the sign is genuinely zero and the trial stops. A
> `dR = 0` reading over adjacent members alone is **not** a stop; it is an
> under-sampled measurement and must be widened before it is acted on.

Cost is small (a few more evaluations) and the failure it prevents is the
expensive kind: silently discarding a working family.

Retained from v1.6 §A3 unchanged: the check is mandatory before any expensive
trial, and every check — including the ones that stop a trial — is recorded.
The 91% stop rate (691 of 756) is the reason to keep it, independent of whether
navigation has discovery value.

## R2 — arms run isolated, and isolation covers process tables

Integrity event E1 in the preregistration: a generation-stage agent read
`<target-id>:<graph6>` pairs for 15 of 30 targets straight out of `pgrep -af`,
because the isolation clause governed *files* and said nothing about *process
visibility*. Event E2: all three arms ran concurrently on one box and cross-arm
process-table leakage could not be excluded after the fact.

> Arms run in separate containers or namespaces, or strictly sequentially with
> the previous session exited. Any concurrent run is disclosed and its targets
> scored `CONTAMINATED`. Isolation means files **and** process tables.

## R3 — the control arm gets a sufficient budget, not merely an equal one

The generic arm returned **16 BRACKETs and zero HELDs**: it never established
that anything holds, it either cracked a target quickly or hit the cap. Its 14
crossings are therefore a lower bound, and the headline endpoint
(wall-unique = 1) may be an overestimate of the method's margin.

> A control arm that cannot reach a verdict is not a control. Budget must be
> large enough that the control returns HELD or CROSSED — not BRACKET — on a
> clear majority of targets, and the bracket count is reported next to the
> endpoint.

## R4 — generator invariants get an independent-path check before freeze

The wall arm found `_spectral_bracket` computing `⌈λ₁⌉` by testing
`det(⌊λ₁⌋·I − A) == 0`, which fires whenever *any* eigenvalue equals `⌊λ₁⌋`:
wrong `spec_ceil` on **19 of 12,112** database members, and wrong tightness data
handed to an arm on `FP-008`.

> Every invariant in a generation vocabulary is validated against a second
> independent implementation over the whole database before the population is
> frozen, not after. Three solver bugs were caught pre-freeze by exactly this
> discipline; the one that escaped was the one implemented only once.

## What is deliberately NOT changed

The decision rule, endpoint, and arm definitions of the three-arm design stand
as written. They produced a usable answer. The population, not the protocol,
is what needs to be harder — see the v2 design in
`results/experiment-v2/DESIGN.md`.
