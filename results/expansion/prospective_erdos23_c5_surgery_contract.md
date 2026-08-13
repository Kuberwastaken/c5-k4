# Frozen prospective trial: Erdős 23 from the balanced `C5` blow-up wall

Frozen: 2026-08-13 UTC, before database-gate or development evaluation.

## Exact current formal statement and status

The checked source is
`FormalConjectures/ErdosProblems/23.lean` at local upstream commit
`ee4aaef5655f8aa4a29d59391a822f398891a2b3`. The theorem `Erdos23.erdos_23`
is tagged `research open` and asks whether every triangle-free graph on `5*n`
vertices has a bipartite spanning subgraph obtained by deleting at most `n^2`
edges. Equivalently, its minimum edge bipartization number

```text
beta_edge(G) = |E(G)| - maxcut(G)
```

is at most `n^2`.

The same file tags the order-25 (`n=5`) case solved and records the balanced
independent-set blow-up of `C5` as tight. The complement of `C5[K4]` is exactly
the balanced independent-set blow-up with part sizes `(4,4,4,4,4)` and has
`beta_edge=16=floor(20^2/25)`.

This is a major human conjecture. The trial is counterexample reconnaissance,
not an upstream/public lane.

## Frozen mechanism

Search for a triangle-free graph whose odd-cycle edge burden grows faster than
the balanced wall while preserving order divisible by five.

1. **Nonuniform independent-set `C5` blow-ups.** Five nonempty independent
   parts with complete joins only between cyclically adjacent parts. Frozen
   orders: 15, 20, and 25. Frozen part sizes are 1 through 8, summing to the
   selected order, canonicalized under dihedral symmetry.
2. **Bounded triangle-free edge surgery.** Starting only from blow-ups with
   exact slack at most two, deterministically try one edge deletion and one
   nonedge addition. Retain additions only after an explicit triangle-free
   check. Canonically deduplicate results. At most 500 surgeries, ordered by
   parent slack, order, graph6, operation, and endpoints.

No other family or operation may be added after results are observed.

## Frozen limits and exact evidence

- at most 1,000 nonuniform blow-ups and 500 surgeries;
- graph orders at most 25;
- every process at most 60 seconds;
- every maximum-cut solve at most 10 seconds with zero MIP gap;
- exact cut partition, kept crossing edges, and deleted same-side edges emitted;
- direct replay verifies that deleting the witness edges leaves a bipartite
  graph and that every input is triangle-free.

## Gate order

1. Before development evaluation, test every triangle-free Graph Atlas graph
   on five vertices, plus `C5`, balanced `C5` blow-ups of part sizes 1 through
   5, complete bipartite controls, and Petersen.
2. Reject the reading if any gate graph contradicts a solved finite case.
3. Evaluate the frozen nonuniform blow-ups, incrementally appending results.
4. Evaluate only the predeclared near-wall surgeries.

Any strict crossing receives adversarial validation before it is reported:

- independent maximum-cut recomputation using a separately implemented exact
  branch-and-bound/enumeration method;
- triangle-free replay from adjacency, without trusting construction metadata;
- witness replay and arithmetic audit;
- current source, issue/PR, literature, and known-catalogue novelty audit;
- an attempt to falsify the candidate through relabeling and alternate solver.

## Classifications

- `DB_SANITY_REJECT`
- `CANDIDATE_ADVERSARIAL`: only after every crossing check passes
- `HOLD_BOUNDED`
- `INCONCLUSIVE`

No commit, push, release, PR, issue, or other public action is authorized.
