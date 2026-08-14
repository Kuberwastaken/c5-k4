# TxGraffiti product campaign: bounded zero

Date: 2026-08-14 UTC

Status: **BOUNDED ZERO; NO CERTIFICATE; NO RELEASE**

Frozen campaign commit: `b9bb628abc8458188f9995c2613d27465e53639c`

GitHub Actions run:
[`31790804083`](https://github.com/Kuberwastaken/c5-k4/actions/runs/31790804083)

The three frozen arms passed the source/database gate and completed without a
candidate for TxGraffiti Conjecture 3,
`gamma_t(G square H) >= gamma(G direct H)`. The catalogue and generic arms are
durable deadline prefixes; only the 72-pair wall-navigation domain is fully
exhausted.

| Arm | Proposed | Durably evaluated | Terminal reason | Certificates |
|---|---:|---:|---|---:|
| catalogue | 706 | 705 | `DEADLINE_PREFIX` | 0 |
| generic | 25 | 24 | `DEADLINE_PREFIX` | 0 |
| wall navigation | 72 | 72 | `DOMAIN_EXHAUSTED` | 0 |
| **total** | **803** | **801** | 3 receipts | **0** |

The proposed/evaluated difference in each deadline arm is the proposal whose
exact subset search met the deadline before a ledger row could be admitted.
It is not counted as an evaluated pair. No evaluated row claimed a crossing:
each supplied size-`k` Cartesian total-dominating witness was accompanied by
an explicit size-`k` dominating witness in the direct product.

Independent audit replayed all three artifact `SHA256SUMS` manifests, all 807
canonical ledger rows, every previous-row link and row digest, and every
terminal final-row/counter binding. It also reconstructed every recorded
factor and product edge list, identity digest, Cartesian total-dominating
witness, and direct-product dominating witness. No certificate file was
present. Representative exact recomputations gave:

| Pair | Product order | `gamma_t(square)` | `gamma(direct)` |
|---|---:|---:|---:|
| `atlas:0:0` (`K2,K2`) | 4 | 2 | 2 |
| `atlas:15:22` | 25 | 6 | 6 |
| `generic:12:4:4:0.0:0.0` | 16 | 6 | 4 |
| `tight:K2,K3` | 6 | 2 | 2 |
| `tight:K2,K3:both:parity-path-2:parity-path-2` | 20 | 6 | 4 |

This is not evidence that every evaluated pair satisfies the conjecture. The
campaign searches for a sufficient certificate using a greedy Cartesian
total-dominating set of size `k`; if that witness is nonoptimal, finding a
size-`k` direct dominating set can hide a genuine smaller-`gamma_t` crossing.
The next method revision should therefore strengthen the Cartesian side with
exact `gamma_t` values or certified upper-bound descent before spending more
time extending the same catalogue/generic prefixes. The exhausted wall domain
does show that the frozen one-move perturbations of `(K2,K2)` and `(K2,K3)` do
not yield a certificate under the current rule.

The frozen campaign definition remains in [CONTRACT.md](CONTRACT.md).
