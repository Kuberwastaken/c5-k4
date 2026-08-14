# TxGraffiti product v2 preparation report

Date: 2026-08-14 UTC  
Outcome: **frozen and unexecuted**

V2 is a narrow method correction derived from the v1 bounded zero. It does
not extend v1's domains. It replaces the greedy-only Cartesian coordinate
with monotonically descending exact-size decisions, and it admits a
direct-product value only when exact.

The frozen implementation has 69 catalogue pairs, 192 deterministic generic
proposals, and 32 wall-navigation pairs. Every fixed-cardinality decision is
individually capped at four seconds; each arm retains the existing 54-second
internal and 60-second external limits. Exact subproblem rows are written to
the durable hash chain as they finish, rather than being buffered until the
factor pair completes.

An independent verifier reconstructs both products and labelled identities,
checks the Cartesian total-dominating witness and exact direct dominating
witness, and independently proves the decisive absent cardinality. A direct
timeout produces no parameter value and cannot become a candidate.

Only syntax, imports, constructor controls, fixed-domain counts,
determinism, receipt honesty, mutation rejection, hash-chain replay and frozen
file hashes were validated. The read-only source/Atlas/product control gate
also replayed all 995 Atlas identities, the four named product identities and
the two tiny exact parameter calibrations. No v2 target pair, proposal stream
row, or arm was evaluated. No workflow was dispatched and no public action
was taken.
