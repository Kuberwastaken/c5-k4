# TxGraffiti C-C phase four: canonical domain exhausted

Date: 2026-08-14 UTC

Status: **DOMAIN_EXHAUSTED_ZERO; NO COUNTEREXAMPLE; NO RELEASE**

Portable replay commit: `757f0883c97fbe67ec6f2a536979c3a797385b3a`

GitHub Actions run:
[`31789793381`](https://github.com/Kuberwastaken/c5-k4/actions/runs/31789793381)

The target-blind constructor enumerated all 5,320 frozen order-20 construction
states and reduced them to 4,961 nauty-canonical identities. Phase three had
already scored 2,575 of those identities. Twenty-four disjoint exact workers
scored every one of the remaining 2,386 identities:

| Quantity | Exact count |
|---|---:|
| construction states | 5,320 |
| canonical identities | 4,961 |
| phase-three identities | 2,575 |
| newly evaluated identities | 2,386 |
| worker terminal receipts | 24 `DOMAIN_EXHAUSTED` |
| verified crossings | 0 |
| aggregate audit errors | 0 |

The aggregate independently verified the target-blind domain and selection
manifests, partition disjointness, complete coverage, worker wrappers, terminal
bindings, ledger chains, and canonical-identity replay. Its final status is
`DOMAIN_EXHAUSTED_ZERO`.

This closes the evidence ambiguity in the earlier 2,575-row prefix: the union
of prior and new identities is exactly the frozen canonical denominator. It
does **not** prove the TxGraffiti inequality `i(G)<=mu*(G)` for all connected
regular graphs. It proves only that the complete phase-four construction
domain contains no counterexample. The strong equality concentration from
phase three therefore becomes a finished negative family result rather than a
reason to spend more compute on the same constructors.

The first phase-four dispatch,
[`31788725249`](https://github.com/Kuberwastaken/c5-k4/actions/runs/31788725249),
is retained as `INVALID_RUN`: its preparation runner built a CPU-specific
`labelg`, which failed on heterogeneous workers. It admitted zero new
identities and supplies no mathematical evidence. The portable replay changed
only nauty build flags and transport smoke gates; the target, domain,
partitions, objective, and proposal order remained frozen.

The frozen [contract](txgraffiti-cc-phase4.md) and
[manifest](txgraffiti-cc-phase4-manifest.json) record the full chronology.
