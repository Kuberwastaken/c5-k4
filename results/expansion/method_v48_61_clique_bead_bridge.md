# Method v0.48: WOWII 61 clique-bead bridge surgery

## Outcome

The frozen degree-changing trial returns **`HOLD_BOUNDED`**. It successfully
raises diameter from four to eight and forces almost every added clique vertex
out of a maximum induced forest, but the same dense degrees reduce the
Havel--Hakimi residue from eight to seven. Every one of the 832 constructions
has residual four, so this operation moves sharply away from a crossing.

This family is closed. No parameter was changed after evaluation, and no
commit, push, issue, PR, release, or other public action was taken by the
trial.

Artifacts:

- `results/expansion/prospective_wowii61_clique_bead_bridge_contract.md`;
- `results/expansion/prospective_wowii61_clique_bead_bridge_ledger.jsonl`;
- `results/expansion/prospective_wowii61_clique_bead_bridge_records.jsonl`;
- `scripts/prospective_wowii61_clique_bead_bridge.py`;
- `scripts/verify_wowii61_clique_bead_bridge.py`.

## Frozen construction

The three bases were exactly the protocol-exact neutral endpoints from the
order-twelve corridor trial. For every diametral pair `{u,v}`, and every
ordered `(q,r)` in `[3,10]^2`, the construction attaches disjoint `K_q` and
`K_r` beads to `u` and `v` through one bridge each.

The base list contains 3, 4, and 6 diametral pairs respectively. Thus the
mechanical frozen family contains

```text
(3 + 4 + 6) * 8 * 8 = 832
```

labelled graphs, well below the 8,000-graph cap.

## Database and base gates

Before development, direct exact search replayed all 1,030 controls:

| residual | 0 | 1 | 2 | 3 | 4 | 5 |
|---:|---:|---:|---:|---:|---:|---:|
| graphs | 159 | 574 | 281 | 10 | 5 | 1 |

There were no violations or timeouts. Each of the three bases was then
recomputed from graph6. Every base retained the fixed degree sequence
`[6,6,4,3,2,1,1,1,1,1,1,1]`, residue eight, diameter four, maximum induced
forest ten, and residual zero.

Two implementation failures occurred before the first development evaluation:
an invalid convenience assertion and a NetworkX-version mismatch for the
`is_bridge` API. Both are preserved in the ledger. They were replaced by the
intended direct simple-graph/self-loop check and exact membership in the
enumerated bridge set. The frozen family, bounds, and ranking were unchanged.

## Exact structural certificate

For each transformed graph, the two joining edges are bridges. Therefore every
cycle lies wholly within one of the three blocks: the base, `K_q`, or `K_r`.
The base contributes at most ten vertices to an induced forest, while a clique
contributes at most two. Conversely, a stored maximum forest of the base plus
two vertices from each clique is an induced forest. Hence

```text
forest(B) = 10 + 2 + 2 = 14
```

exactly for every clique size. This is also the intended feedback-set effect:
at least `q-2` left-bead vertices and `r-2` right-bead vertices must be deleted
to destroy all clique cycles.

All-source BFS gives diameter eight in every case. A nonattachment vertex of
one clique, a length-four base geodesic from `u` to `v`, and a nonattachment
vertex of the other clique give the lower certificate; the bridge-block
geometry gives the matching upper bound.

## Results

| base | diametral pairs | evaluations | distinct within base | residual |
|---|---:|---:|---:|---:|
| `KniA@A?_A?G?` | 3 | 192 | 64 | 4 |
| `K~Q?PA?_A?G?` | 4 | 256 | 128 | 4 |
| `K~IA?Q?_A?G?` | 6 | 384 | 64 | 4 |
| **total** | **13** | **832** | — | **4** |

For every graph, independently of attachments and `q,r`:

```text
residue = 7
diameter = 8
forest = 14
R61 = 14 - 7 - ceil(8/3) = 4.
```

There are no tight graphs, candidates, timeouts, or certificate mismatches.

## Independent replay

A separately written verifier decoded all 832 graph6 records and independently
recomputed:

- every labelled edge list and degree sequence;
- every full Havel--Hakimi trajectory and residue;
- diameter by explicit all-source BFS;
- acyclicity of every 14-vertex forest witness;
- both clique blocks and attachment bridges; and
- the additive forest upper certificate and final residual.

It returned 832 agreements and zero mismatches.

## Interpretation

The experiment isolates a useful obstruction. Dense clique beads are very
efficient at forcing new vertices into feedback sets and bridge placement
raises the diameter ceiling exactly as designed. But Havel--Hakimi residue is
not monotone under this dense attachment: it falls by one even as the graph
grows by six to twenty vertices. The forest penalty and diameter gain therefore
cannot be considered without their effect on the degree-sequence reduction.

The next distinct prospective operation, if any, should preserve the seed's
large terminal zero state while adding cyclic distance. Retuning clique sizes
or attachments inside this closed family is not justified by these results.

