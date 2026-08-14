# Graffiti³ Conjecture 2: frozen development-search contract

Status: **FROZEN SERIALIZATION REPLAY**

Freeze date: 2026-08-14 UTC

Scope: development evidence only; not a held-out benchmark and not a release.

The first execution at commit `b168383` found a candidate in two arms, but its
ledger used integer-keyed `d₂` objects. JSON parsing turns those keys into
strings, changing canonical sort order for two-digit labels and making the
internal row hashes unreplayable. Artifact-level checksums remain valid, but
that execution cannot supply the promised chain evidence. Version 1.1 changes
only the ledger schema and serializes `d₂` as sorted `[vertex,value]` pairs;
the frozen proposal order, graph constructors, objective, arithmetic, sanity
gate, seeds, and caps are unchanged. This is an explicitly post-signal replay,
not a second prospective trial.

## Source and exact reading

Primary source: Randy Davila, *Graffiti³: Compact Theory Libraries for
Automated Mathematical Discovery*, Research Square preprint rs-8493329/v1,
posted 2026-01-19, DOI
[`10.21203/rs.3.rs-8493329/v1`](https://doi.org/10.21203/rs.3.rs-8493329/v1),
page 8, Conjecture 2.

The source defines `d₂(u)` as "the number of vertices within distance at most
two of `u`". This contract reads that literally as

```text
d₂(u) = |{v in V(G) : dist_G(u,v) <= 2}|,
```

including `u` itself because `dist_G(u,u)=0`. For a nontrivial connected
finite simple graph, the conjecture is

```text
alpha(G) <= RGA2(G),
RGA2(G) = sum_{uv in E(G)} 2*sqrt(d₂(u)*d₂(v))/(d₂(u)+d₂(v)).
```

The exact negation searched here is an adjacency-labelled connected simple
graph with at least two vertices, together with an explicit independent set
`I`, such that a rigorous rational upper bound proves

```text
RGA2(G) < |I| <= alpha(G).
```

The search never needs to assert that `I` is maximum. A candidate certificate
is the graph edge list, `I`, every exact `d₂` value, and one outward rational
upper bound for every radical summand whose total is strictly below `|I|`.

## Status and novelty gate

The January 2026 primary source calls the statement open and sharp on its
snapshot. Exact-formula, invariant-name, and quoted-statement searches were
repeated on 2026-08-14 and found no later proof or counterexample. That is a
search result, not a guarantee. Any numerical crossing must stop as
`CANDIDATE_ONLY` until a fresh source/status search, author/source check,
independent implementation, small-graph sanity replay, and prior-art search
all pass.

This target is absent from the repository's earlier TxGraffiti audit, which
covered the conjectures in the older TxGraffiti paper rather than these new
Graffiti³ statements.

## Mandatory database-sanity gate

Before an arm may emit target rows, it must enumerate NetworkX's connected
Graph Atlas graphs of orders 2 through 7 and establish all of the following:

- exactly 995 nontrivial connected graphs are present;
- none violates the inequality, using an exact maximum independent set and
  outward rational interval arithmetic;
- exact radical normal forms classify exactly six equality graphs;
- those six equality graphs are precisely `K1,1`, ..., `K1,6`.

Failure is terminal `DB_GATE_FAILED`; no target result after a failed gate is
valid.

## Frozen arms

Every arm has an internal 54-second deadline and an external 60-second hard
cap. Rows are exactly isomorphism-deduplicated within invariant buckets and
store a deterministic representative graph6 string. They are appended
incrementally with a SHA-256 chain and `fsync`. A separate canonical terminal receipt distinguishes
`DOMAIN_EXHAUSTED`, `DEADLINE_PREFIX`, `CANDIDATE_FOUND`, and failure.

1. `CATALOGUE`: the 995 gate graphs followed by deterministic named trees,
   brooms, double stars, spiders, coronas, split graphs, and clique/independent
   blow-ups through order 30. Gate rows are not counted again as search rows.
2. `GENERIC`: 6,000 deterministic seeded connected `G(n,p)` proposals for
   `8 <= n <= 30`, with sparse, medium, and dense strata. A deterministic
   multi-order greedy independent set supplies only a certified lower bound.
3. `WALL_NAVIGATION`: equality stars `K1,m` for `2 <= m <= 29`, perturbed by
   one spoke subdivision, hub splitting, leaf cloning, and sparse edges between
   branches. Every proposal retains an explicit independent set and is ranked
   only by the certified residual upper bound.

No adaptive construction may be added after seeing target values. A new move
requires a new contract/version.

## Outcome discipline

- `CANDIDATE_FOUND` means only that the first implementation produced a strict
  rational certificate. It is not a public disproof.
- `DOMAIN_EXHAUSTED` is allowed only after the complete finite arm list was
  evaluated.
- `DEADLINE_PREFIX` is a bounded prefix, never exhaustion.
- No issue, PR, release, README claim, or novelty count follows automatically.
