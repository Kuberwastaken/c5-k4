# Graffiti³ energy Conjecture 3: exhausted frozen-domain zero

Date: 2026-08-14 UTC

Status: **DOMAIN_EXHAUSTED_ZERO; NO COUNTEREXAMPLE; NO RELEASE**

Frozen campaign commit: `58c1cee3927d6c973e20a1fff918bfb591c8777d`

GitHub Actions run:
[`31793052228`](https://github.com/Kuberwastaken/c5-k4/actions/runs/31793052228)

Target: Conjecture 3 of Randy Davila, *Graffiti³: Compact Theory Libraries
for Automated Mathematical Discovery*, DOI
[`10.21203/rs.3.rs-8493329/v1`](https://doi.org/10.21203/rs.3.rs-8493329/v1),
under the literal closed-distance-two reading specified by the frozen contract.

All three deterministic domains terminated `DOMAIN_EXHAUSTED`. The artifacts
contain no candidate file and no candidate-binding ledger row.

| Arm | Proposed | Canonical unique / evaluated | Applicable | Least literal residual | Crossings |
|---|---:|---:|---:|---:|---:|
| catalogue | 950 | 938 | 875 | `2.375` (`star:8`) | 0 |
| generic | 1,800 | 1,797 | 915 | `6.09464882278818` | 0 |
| wall navigation | 1,073 | 1,073 | 1,073 | `3.125` (`book-pages:6`) | 0 |
| **total** | **3,823** | **3,808** | **2,863** |  | **0** |

An independent full replay verified all three `SHA256SUMS` manifests, every
ledger schema, sequence, predecessor hash and record hash, each terminal's
ledger SHA/final-row/terminal-hash binding, the exact campaign commit, and all
zero exit assignments. It then reconstructed every one of the 3,808 graph6
rows and independently recomputed order, size, connectivity, planarity,
diameter, closed distance-two values, adjacency energy, rounding, literal
right side, residual and verdict. There were zero mismatches. The 945
non-applicable rows failed the printed graph premises; no applicable row had a
negative literal residual.

The immutable 335-row source table also replayed at its frozen SHA-256, with
97 eligible rows, no reported scalar violation and the nine frozen
implementation-equality ids. Independently recomputing all 995 connected
Graph Atlas graphs of orders two through seven recovered zero literal
violations, zero literal equalities and the least literal gap `1/2` on `K2`.

The center-excluding implementation reading remains **`DB_REJECTED`**, not a
second search result: the same Atlas replay recovers violations on `K2` and
`K3` (`A_`, `Bw`). Its published equality rows therefore remain calibration
evidence only and cannot generate a claim.

Method implication: none of the frozen named, generic Apollonian-deletion, or
false-twin/book/double-star coordinates approaches the literal wall; even the
best new residual is `2.375`. More volume in these same domains is not
motivated. Any successor should introduce a genuinely new structural move
that shrinks selected closed radius-two balls while keeping adjacency energy
inside a fixed rounding shelf, rather than extending these exhausted
constructors.

The frozen [contract](graffiti3-energy-c3-contract.md),
[manifest](graffiti3-energy-c3-manifest.json), and
[source/status attestation](graffiti3-energy-c3-source-status.md) delimit this
negative result. It is not a proof of the universal conjecture.
