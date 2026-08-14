# TxGraffiti product v2 campaign: bounded zero

Date: 2026-08-14 UTC

Status: **BOUNDED ZERO; NO CERTIFICATE; NO RELEASE**

Frozen campaign commit: `f6e4a6f88b00ed7b1fb8a4767490e2b6e2181fe5`

GitHub Actions run:
[`31794226395`](https://github.com/Kuberwastaken/c5-k4/actions/runs/31794226395)

All three frozen v2 arms passed the source/database gate, exhausted their
declared domains, and found no counterexample to TxGraffiti Conjecture 3,
`gamma_t(G square H) >= gamma(G direct H)`.

| Arm | Proposed | Evaluated | Ledger rows | Cartesian subproblems | Direct subproblems | Terminal reason |
|---|---:|---:|---:|---:|---:|---|
| catalogue | 69 | 69 | 286 | 29 | 117 | `DOMAIN_EXHAUSTED` |
| generic | 192 | 192 | 825 | 98 | 341 | `DOMAIN_EXHAUSTED` |
| wall navigation | 32 | 32 | 124 | 8 | 50 | `DOMAIN_EXHAUSTED` |
| **total** | **293** | **293** | **1,235** | **135** | **508** | 3 exhausted domains |

## Independent audit

The audit downloaded all three run artifacts and replayed every artifact
`SHA256SUMS` manifest. It then replayed all 1,235 canonical ledger row hashes,
previous-row links, sequences, schemas and campaign bindings. In each arm the
first row is a passing source/database gate, the last row is the exhausted
summary, and the terminal receipt binds the exact final-row hash, row count,
proposal count and evaluation count.

Every recorded factor was reconstructed from its edge list. Every Cartesian
and direct product was independently rebuilt, and all orders, sizes, edge
lists, graph6 strings and labelled-identity hashes matched the ledger.

The 643 durable fixed-cardinality receipts were also replayed independently:

- 339 `ABSENT` receipts exhaust exactly the recorded binomial number of
  subsets and have no covering subset;
- 304 `WITNESS` receipts contain the first lexicographic covering subset at
  exactly the recorded examination count;
- zero receipts are `TIMEOUT`, and no incomplete decision was used as an
  exact value or admitted candidate evidence.

The subproblem rows emitted incrementally in the hash chain match, field for
field, the descent records embedded in their final evaluated-pair rows. Every
Cartesian witness total-dominates and every direct-product witness dominates.

Finally, the audit independently exhaustively recomputed both parameters for
all 293 evaluated pairs. The direct-product value is exact in every worker
row. The worker also marks 286 Cartesian values exact. Seven rows retain a
conservative `exact: false` flag after a successful descent reaches the
cardinality lower bound; independent exhaustive replay confirms that all
seven reported upper bounds are exact as well. This metadata conservatism has
no effect on the candidate rule, which only requires a valid Cartesian upper
bound, but the audit closes it for the result interpretation.

The exact parameter-pair distribution was:

| `(gamma_t(square), gamma(direct))` | Pairs |
|---|---:|
| `(2,2)` | 80 |
| `(3,3)` | 60 |
| `(4,3)` | 22 |
| `(4,4)` | 79 |
| `(5,3)` | 2 |
| `(5,4)` | 22 |
| `(5,5)` | 6 |
| `(6,4)` | 15 |
| `(7,4)` | 2 |
| `(8,6)` | 5 |

Thus 225 pairs are equality cases and 68 satisfy the conjecture strictly;
none crosses it. No certificate/candidate file is present in any artifact.

## Comparison with v1

V1 durably evaluated 801 pairs, but its two broad arms ended as deadline
prefixes and its greedy-only Cartesian witness left a possible false-negative
mechanism: a nonminimal size `k` could conceal a case with
`gamma_t(square) < gamma(direct) <= k`.

V2 deliberately searches smaller, revised domains: 293 pairs rather than the
801 v1 prefixes. In exchange, all three v2 domains are exhausted, every
direct-product value is exact, and the Cartesian upper bound is monotonically
descended. The full independent replay further establishes exact Cartesian
values for every v2 row. Therefore the v1 greedy-witness ambiguity is removed
for these 293 pairs, and the zero result survives the method correction.

This remains a bounded zero, not evidence that the conjecture holds in
general and not a completion of the broader v1 prefixes. The appropriate next
step is a structurally new or larger exact domain, not publication of a
counterexample claim.

The frozen campaign definition remains in [CONTRACT.md](CONTRACT.md).
