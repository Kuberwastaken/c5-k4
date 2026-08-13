# Method v0.32: WOWII 133 residual completion

## Outcome

The six-point triangle-overlap survivor from v0.31 admits a genuine connected
four-regular completion of girth at least five while preserving the selected
length-five geodesic.

The completed graph has 44 vertices.  Lean certifies that it:

- contains the frozen geodesic/first/parent/third/blocker core verbatim;
- is connected;
- is four-regular;
- has no triangle;
- has no four-cycle;
- contains the path `0-1-2-3-4-5`;
- has no walk of length at most four from `0` to `5`.

Thus the distinguished path is still geodesic of length five.

This is a calibrated countermodel to the **local residual-completion
strategy**, not a counterexample to WOWII 133.  It proves that degree
completion, girth constraints, and preservation of the chosen geodesic do not
eliminate the sharp cross-branch overlap pattern.

Lean certificate:

- `lean/GraphConjecture133ResidualCompletion.lean`.

## Frozen constraints

The search fixed the following vertices and edges before introducing any
completion variables.

### Geodesic

```text
x₀-x₁-x₂-x₃-x₄-x₅ = 0-1-2-3-4-5.
```

The distinguished endpoint is `u=x₀=0`.

### First choices and parents

```text
firsts  = 6,7,8,
parents = 9,10,11,

0--6--9,
0--7--10,
0--8--11.
```

Each selected parent was frozen as clean against the geodesic, and each first
choice was frozen as clean away from `x₀`.

### Six thirds

The sharp triangle-overlap pattern is

```text
parent 9:  12,13,15,
parent 10: 12,14,16,
parent 11: 13,14,17.
```

Thus `12,13,14` are the three distinct pair-shared thirds and `15,16,17` are
private.

### Blocker edges

The v0.31 coloring becomes

```text
12--x₁, 13--x₂, 14--x₃,
15--x₃, 16--x₂, 17--x₁.
```

Every third was forbidden from contacting any other geodesic vertex.  The
already saturated endpoint, targets `x₁,x₂,x₃`, and parents received no new
edges.

All added edges were required to preserve:

1. simple-graph adjacency;
2. exact degree four;
3. no triangle;
4. no four-cycle;
5. no `x₀-x₅` path of length below five.

## Bounded exact search

For each proposed order, the completion was encoded with one binary variable
per allowable missing edge.  The model contained:

- one equality for each residual vertex degree;
- a cut for every possible triangle;
- a cut for every possible four-cycle;
- a cut for every possible `x₀-x₅` path of lengths one through four;
- the frozen-edge and frozen-nonedge constraints above.

The exact integer solver returned infeasible for every order

```text
19,20,21,22,23,24,25,26,27.
```

The order-19 lower boundary is also natural because a four-regular
girth-five graph has no completion on the 18 frozen vertices alone.

Orders `28..43` are **not classified**.  Order 28 exceeded the short search
budget, so the 44-vertex completion must not be called globally minimal.  It
is the smallest completion found in this run, with exact nonexistence only
through order 27.

## Construction at order 44

The completion uses the 26-vertex incidence graph of the projective plane
`PG(2,3)`.  That graph is four-regular, bipartite, and has girth six.

The frozen 18-vertex core has twenty residual degree stubs:

```text
x₄: 2, x₅: 3,
first choices: 2+2+2,
pair-shared thirds: 1+1+1,
private thirds: 2+2+2.
```

Ten mutually vertex-disjoint incidence edges were deleted from the projective
plane graph.  Their twenty endpoints were attached bijectively to the twenty
core stubs.  Each projective-plane endpoint loses one edge and gains one core
edge, so every degree returns to four.

The chosen deletion/attachment pattern was filtered against all cross-core
triangles, four-cycles, and short endpoint paths.  The resulting graph has 88
edges.

## Lean representation

`neighbors : Fin 44 -> Finset (Fin 44)` records the exact four neighbors of
every vertex.  Symmetry and looplessness are checked while constructing
`completionGraph`.

Lean proves:

- `neighborFinset_eq_neighbors`;
- `completion_four_regular`;
- `no_triangle`;
- `common_neighbors_le_one` and `no_C4`;
- `no_endpoint_walk_shorter_than_five`;
- `endpoint_path_of_length_five`;
- `frozen_core_preserved`.

Connectivity is not left to an external computation.  The file contains an
explicit rank-decreasing spanning parent map.  `root_or_parent_step` checks
every nonroot parent edge, `reachable_from_zero` builds reachability by strong
induction, and `completion_connected` derives graph connectivity.

`residual_completion_certificate` packages all certified properties.

## What this rules out

The following proposed finishing argument is false:

> The six-point triangle-overlap core cannot complete its nine residual
> degree stubs without creating a triangle, C4, or geodesic shortcut.

The 44-vertex certificate completes all those stubs and avoids all three
failures.

Consequently, another local residual-degree enumeration is unlikely to close
the proof unless it introduces a graph condition absent from the frozen
model.

## What remains available

The completion does not show that the full conjecture fails, and it does not
show that the completed graph lacks some other clean handle.  It only
preserves the selected blocked third triples.  Newly attached neighbors of
the first choices may support alternative handles or induced-path reroutings.

This redirects the proof toward the global alternatives already visible in
the chain:

1. exploit the two additional second choices created when each first-choice
   degree is completed;
2. switch to a different first choice or parent after observing the blocker
   pattern;
3. construct a two-ended induced extension;
4. use a global longest-path or rerouting argument rather than insisting on
   the frozen one-ended handle.

The completion is especially informative because its new first-choice
neighbors are unavoidable: each selected first choice began with degree two
and needed two more neighbors.  The local strategy loses precisely by
allowing those alternative depth-two branches.

## Verification discipline

The search processes were individually capped below 60 seconds.  The Lean
certificate uses ordinary kernel reduction and explicit graph proofs.  It
contains no holes, custom axioms, or native-decision shortcuts.
