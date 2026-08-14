# TxGraffiti C-C live trial: source/status and frozen arm contract

Date: **2026-08-14 UTC**
Evidence split: **DEVELOPMENT**; this is not part of the held-out Method v1.5
benchmark.

## Exact target

The source-faithful TxGraffiti conjecture is

```text
for every connected r-regular finite simple graph G with r >= 3,
i(G) <= mu*(G),
```

where `i(G)` is the minimum size of a maximal independent set and `mu*(G)`
is the minimum size of a maximal matching (the edge-domination number).
The connected restriction survives both surveyed source readings and makes a
negative result robust to the wording difference recorded in
`results/expansion/txgraffiti.md`.

Primary sources:

- Caro, Davila, Henning, and Pepper, *New results relating independence and
  matchings* (2019), Conjecture 1;
- Davila et al., *In Reverie Together: Ten Years of Mathematical Discovery
  with a Machine Collaborator*, arXiv:2507.17780, the list of open TxGraffiti
  conjectures.

Searches on 2026-08-14 for the exact invariant pair, title fragments, and the
displayed inequality found no resolving paper or counterexample. The 2026
survey still calls it open. The 2022 TxGraffiti paper proves neighboring
matching/domination conjectures but does not resolve this mirror inequality.

## Resolution shape

This is a finite universal statement. One finite connected regular graph with

```text
R(G) = mu*(G) - i(G) < 0
```

is a complete counterexample. Both optima have bounded exact binary-ILP
certificates. Any negative residual must additionally be replayed without the
discovery ILPs: enumerate independent dominating sets, then maximize the
independent unmatched set whose deletion leaves a perfect matching.

## Database-sanity gate

Before any arm evaluates a development candidate, it must recompute every
connected regular graph of degree at least three in the NetworkX Graph Atlas
and the named controls `K4`, `K3,3`, and Petersen. Every applicable row must
have nonnegative residual. A gate failure terminates the worker and invalidates
all subsequent rows.

This repeats rather than merely cites the earlier atlas gate. It protects the
new evaluator and the exact interpretation simultaneously.

## Frozen arms

Every arm is a separate process under the existing hard 60-second process-
group cap and writes a fresh, hash-chained, `fsync`ed Method v1.5 scientific
JSONL stream. Exact graph identity is supplied only by the frozen nauty
`labelg` binary.

### `CATALOGUE`

Evaluate the applicable Graph Atlas rows and this fixed named-family list:
complete graphs `K4..K10`, balanced complete bipartite graphs `K3,3..K8,8`,
Petersen, Heawood, Möbius--Kantor, Pappus, Desargues, dodecahedral, Frucht,
circular ladders `CL3..CL10`, `C5[K2..K5]`, and the complement of `C5[K4]`.
Rows above order 24 are excluded before proposal.

### `GENERIC`

With seed `0xCC20260814`, repeatedly sample connected simple random regular
graphs with `8 <= n <= 20` and `3 <= r <= min(8,n-1)`, subject to `nr` even.
No objective or equality information changes the proposal distribution.

### `WALL_NAVIGATION`

Start from the exact equality seeds complement(`C5[K4]`), Petersen, `K3,3`,
and circular ladders of cycle lengths 3, 5, 6, and 9. At an equality state,
freeze one minimum maximal matching `M` and its unmatched independent set `U`.
Generate degree-preserving two-switches that neither delete an edge of `M` nor
add an edge inside `U`; consequently `M` remains a maximal matching and
`mu*(child) <= |M|`. Rank the switches only by how many of the parent's
minimum independent dominating sets they destroy. Exact evaluation, not this
ranking score, decides the residual. Equality children may continue to depth
two; no safe or worse child is expanded.

The predicted separating move is therefore explicit:

```text
pin a small maximal matching while destroying every independent dominating
set of the same size.
```

## Stops and publication gate

- Each binary ILP receives at most 8 seconds and every process at most 60.
- A non-optimal solver status terminates the arm; it is not a bounded hold.
- No adaptive family change is allowed inside this frozen trial.
- A negative residual stops interpretation. It must pass independent replay,
  current source/status and duplicate searches, and a formal certificate
  before any release is considered.
- Zero crossings are committed as a bounded development result, never as a
  proof of the conjecture.
