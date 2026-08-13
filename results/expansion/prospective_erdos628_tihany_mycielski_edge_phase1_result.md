# Erdős 628 Mycielski-edge Phase 1: explicit hold

Date: **2026-08-13 UTC**

Final status: **`HOLD_EXPLICIT_SPLIT`**

## Premise gate

The only frozen transformation deleted embedded original-`C5` edge `{1,2}`
from the Phase 0 near-join seed. The resulting graph has 25 vertices and 116
edges, with graph6 digest
`71bdd166b526499c50133bd6c1c29c3fcdd9c34663015ae835bae82607f35405`.

Two independent exact oracle stacks agree:

| oracle | chromatic number | clique number |
|---|---:|---:|
| DSATUR + Bron--Kerbosch | 6 | 4 |
| binary coloring + clique MILPs | 6 | 4 |

Both replayed explicit six-colorings and maximum cliques. The MILPs returned
zero gap. Thus the exact `k=6`, `K6`-free premise survived and authorized the
split search.

## Exact split reduction and result

For `(a,b)=(2,5)`, exhaustive subset search reduces exactly to edge
complements. Any subset inducing chromatic number at least two contains an
edge; replacing the subset by that edge enlarges its complement and cannot
lower complementary chromatic number. Conversely, any edge whose vertex
complement is at least five-chromatic is itself a valid left side.

All 116 edges were evaluated in lexicographic order. DSATUR and a separate
binary four-colorability MILP agreed on every complement:

- 115 complements have chromatic number at least five;
- one complement is four-colorable;
- row digest:
  `c6848c8cb50d69314f225639c7ef25a116537a92cf996652db0a676480d94604`.

The first edge `{0,1}` is already a witness. Its induced side is `K2`, hence
has chromatic number two. Its 23-vertex complement is not four-colorable and
has independently produced, replayed five-colorings, so its chromatic number
is exactly five.

## Independent audit

A third implementation reconstructed `H5` through NetworkX's independent
`mycielskian` implementation and encoded four-colorability as CNF. Glucose4
recomputed all 116 edge complements in 0.33 seconds, reproduced the
`115/1` distribution and row digest, and replayed both stored five-colorings.

The first split implementation is preserved in the append-only ledger as a
nonfinal runner failure: a redundant clique MILP returned `Optimal` after
presolve without a numeric gap field, which the wrapper rejected. It emitted
no mathematical verdict. The corrected computation asked only the exact
four-colorability threshold required by the declaration.

No alternate transformation or adaptive search was performed. No Lean file
was introduced, so no `sorry` or `native_decide` is involved. No commit, push,
release, issue, pull request, or public action was performed.
