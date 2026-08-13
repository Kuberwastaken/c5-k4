# Frozen prospective trial: WOWII 61 clique-bead bridge surgery

Frozen: 2026-08-13 UTC, before constructing or evaluating any development
graph.

## Target and inherited source gate

The sole target remains current DeepMind WOWII 61 at upstream commit
`9a1636c4030039f70cf78b866c216d8b6c5f35b0`, source SHA-256
`54620e7b70a9a98eaaf7ce10154f533046b9f6d36fa276c8923c1a7301a7e091`:

```text
largestInducedForestSize(G)
  >= residue(G) + ceil(diameter(G)/3).
```

The recovered WOWII record and formal-conjectures source classify the
statement as open. The database-sanity and candidate protocols of
`results/expansion/prospective_wowii61_realization_spectrum_contract.md` are
inherited. No public action is authorized.

## Frozen bases

Use exactly the three protocol-exact neutral endpoints from
`results/expansion/prospective_wowii61_higher_order_corridor_literal_records.jsonl`,
ordered first by depth and then by graph6:

```text
KniA@A?_A?G?
K~Q?PA?_A?G?
K~IA?Q?_A?G?
```

Every base has degree sequence `[6,6,4,3,2,1,1,1,1,1,1,1]`, Havel--Hakimi
residue eight, diameter four, maximum induced-forest order ten, and WOWII 61
residual zero. Recompute all values and a maximum-forest witness before
development.

## Frozen transformation

For every unordered diametral pair `{u,v}` in each base and every ordered
pair `(q,r)` with `3 <= q,r <= 10`, form `B(base,u,v,q,r)` as follows:

1. take disjoint cliques `Q = K_q` and `R = K_r`;
2. choose the least-labelled vertex `a` of `Q` and `b` of `R`;
3. add exactly the bridge edges `ua` and `vb`; and
4. add no other edge incident between the three blocks.

Evaluate every labelled construction. Isomorphic duplicates remain valid
development evaluations but are flagged by graph6/isomorphism audit; they do
not consume a separate novelty claim.

This family is distinct from degree-preserving switches and ordinary 2-lifts.
It changes the degree sequence and installs two dense feedback-set beads at
opposite ends of a diametral path.

## Preregistered structural predictions

The frozen transformation predicts, before evaluation:

- `diameter(B) = diameter(base) + 4 = 8`, because a non-attachment vertex in
  each clique is two edges from its base attachment and `{u,v}` is diametral;
- every cycle lies wholly in the base, `Q`, or `R`, since both joining edges
  are bridges;
- a maximum induced forest is the union of a maximum forest of the base and
  any two vertices from each attached clique;
- therefore `forest(B) = 10 + 2 + 2 = 14` exactly; and
- every feedback vertex set contains at least `q-2` vertices of `Q`, at least
  `r-2` vertices of `R`, and at least two base vertices.

Thus `ceil(diameter(B)/3) = 3`, and a candidate occurs precisely when the new
Havel--Hakimi residue is at least twelve:

```text
R61(B) = 14 - residue(B) - 3 = 11 - residue(B).
```

No outcome may alter these predictions or the family bounds.

## Exactness and verification

Before development, replay the parent's 1,030-graph sanity gate with direct
exact induced-forest search. For each development graph:

1. verify simplicity, connectivity, the exact two bridges, and the frozen
   three-block decomposition;
2. recompute the complete Havel--Hakimi trajectory and residue from its degree
   sequence;
3. compute diameter independently by all-source BFS and require eight;
4. record an explicit 14-vertex induced-forest witness;
5. certify the upper bound 14 blockwise: the base contributes at most ten and
   each clique at most two; and
6. independently replay every negative candidate from graph6 with a separately
   written Havel--Hakimi loop, BFS, forest-witness checker, and block upper
   certificate.

The block certificate is exact and replaces exponential subset search above
order twelve. Every subprocess remains capped at 60 seconds.

## Frozen budgets and logging

- all three bases;
- every unordered diametral pair in each base;
- all 64 ordered size pairs `(q,r)` in `[3,10]^2`;
- at most 8,000 labelled constructions globally (pause if the mechanical
  family exceeds this cap);
- at most 8,000 exact invariant evaluations;
- append the gate before construction;
- append after every completed base, every improved residue/residual, every
  certificate mismatch, candidate, timeout, and final verdict;
- record graph6, labelled edge list, base, attachments, clique sizes, degree
  sequence, full Havel--Hakimi trajectory, residue, diameter, forest witness,
  upper certificate, residual, and timings.

## Frozen verdicts

- `CLIQUE_BEAD_CROSSING`: a negative residual surviving independent replay.
- `TIGHT_BEAD`: a new residual-zero graph.
- `HOLD_BOUNDED`: every frozen construction completes with nonnegative
  residual and no timeout.
- `INCONCLUSIVE`: a gate, exactness check, candidate replay, process, or budget
  fails.

No issue, PR, release, commit, push, or other public action is authorized.

