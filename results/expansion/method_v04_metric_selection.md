# Method v0.4 metric-wall selection: WOWII 184/185

Status: **FROZEN PROSPECTIVE TRIAL / NOT EVALUATED**

Frozen: **2026-08-12 UTC**

Scope: existing Written on the Wall II statements only. This document selects
one bounded trial; it reports no generated candidate, residual value, hold, or
counterexample.

## Selection and exclusions

The selected cluster is WOWII **184/185**, in the lower-bound run for
`L_s(G)+b(G)`:

```text
184: L_s(G)+b(G) >= Delta(G^2)+2 dist_avg(B(G^2),V(G^2)),
185: L_s(G)+b(G) >= Delta(G^2)+2 dist_avg(G^2).
```

Both source records are marked `O` (open), dated 8 August 2005, in
`data/wowii-conjectures.json`. They belong to a collection represented in
`formal-conjectures`, although these two individual statements do not yet
have Lean source files there. The repository's literature and status ledgers
contain no external proof or counterexample claim for either statement, and
neither has been released by this campaign. A live novelty/status check is
still mandatory before any later result is promoted.

This is a fresh metric direction. The completed v0.1 barbell trial exhausted
`K_a-P_L-K_b` for `2 <= a <= b <= 5`, `2 <= L <= 10`, and every one- and
two-edge orbit edit of its designated equality controls, but it targeted
169/174/180/182. The earlier family table merely recorded equality for
184/185 on eleven carrier/barbell controls. It did not test the rooted
odd-cycle quotient frozen below. WOWII 183 is not selected: it is already an
active theorem-signal lane. WOWII 40 has an external partial-result/status
claim, while 61 and 133 already received bounded method trials. WoW I and
Graph Brain are outside scope.

## Exact residuals and theorem subtraction

For a connected nontrivial graph `G`, put

```text
n       = |V(G)|,
H       = G^2,
q(H)    = n-1-Delta(H),
T173(G) = L_s(G)+b(G)-(n+1).
```

The proved WOWII 173 baseline gives `T173(G) >= 0`. For this trial, `B(H)` is
the source boundary/periphery set and both distance averages are measured in
`H`. The source-glossary normalization must be locked before execution. The
proposed primary reading is

```text
d_B(H) = (1 / (|B(H)|(n-1)))
         * sum_{u in B(H)} sum_{v in V(H), v != u} dist_H(u,v),
d(H)   = (1 / (n(n-1)))
         * sum_{u in V(H)} sum_{v in V(H), v != u} dist_H(u,v).
```

Thus the signed residuals, with negative meaning a crossing, are exactly

```text
R184(G) = L_s(G)+b(G)-Delta(H)-2d_B(H)
        = T173(G)+q(H)+2-2d_B(H),

R185(G) = L_s(G)+b(G)-Delta(H)-2d(H)
        = T173(G)+q(H)+2-2d(H).
```

If the recovered glossary uses unordered pairs or a different exclusion rule,
the implementation must use that source convention and recompute the gate;
it may not silently retain the formulas above under a changed normalization.

## Obstruction identity

After subtracting theorem 173, a crossing is possible exactly when

```text
2(d_X(H)-1) > q(H)+T173(G),
```

where `d_X=d_B` for 184 and `d_X=d` for 185. This is the trial's obstruction
identity. It exposes three coordinates rather than treating the right side as
one opaque number:

- `T173` is the structural price paid in leaf/bipartite slack;
- `q` is the number of nonneighbors of a maximum-degree vertex of the square;
- `2(d_X-1)` is the metric gain that must outrun both prices.

The identity also explains why the diameter-two equality controls do not
decide the conjectures: `H=K_n` gives `q=0`, `d_B=d=1`, and hence
`R184=R185=T173`. Unlike the radius correction in the active 183 lane, a
boundary-to-all average can be moved by putting a large dense core far from a
small boundary set. No known theorem in the current method reports forces the
sign of `q+2-2d_B`; consequently 184 is not being treated as a theorem shadow.

## Frozen separating quotient: rooted carrier comets

Let `Q_L` be a 5-cycle `c_0...c_4c_0` with a pendant path
`c_0-y_1-...-y_L`. Define `K(m,L)` by replacing every cycle vertex `c_i` by
a clique of order `m`, making consecutive cycle bags complete to one another,
leaving every `y_j` a singleton, and joining `y_1` to one distinguished vertex
`x` of the `c_0` bag. There are no other handle-to-core edges.

Equivalently, `K(m,L)` is `C5[K_m]` with an induced path of `L` new vertices
attached at one carrier vertex. This is not an endpoint-clique barbell: its
quotient contains an odd cycle, has one dense cyclic core rather than two
terminal cliques, and cannot be reached by the one- or two-edge edit strata
already exhausted around the barbell controls.

The frozen prediction is coordinate-specific, not a claim that a crossing
exists:

- extending the handle changes `d_B(K(m,L)^2)` on every metric scale;
- increasing `m` gives the distant core more weight in the boundary-to-all
  average;
- `q(K(m,L)^2)` is governed mainly by the handle vertices missed by the best
  square neighborhood, rather than by the number of core vertices;
- the carrier starts on the 173 wall, and attaching one handle is expected to
  add at most a constant amount of `T173` independent of handle length.

Therefore the two parameters offer the desired prospective separation:
`m` can amplify the boundary-distance term without proportionally increasing
`q`, while `L` crosses square-distance layers. WOWII 184 is the primary target.
WOWII 185 is evaluated on exactly the same graphs as a correlated secondary
metric wall; no extra family may be introduced on the strength of its results.

## Mandatory database-sanity gate

No `K(m,L)` graph may be evaluated until one implementation has completed all
of the following under the frozen source reading:

1. every connected Graph Atlas graph on two through seven vertices;
2. `P_n` and `C_n` for `2 <= n <= 12`, stars `K_{1,r}` for `2 <= r <= 10`,
   complete graphs `K_n` for `2 <= n <= 10`, and complete bipartite graphs
   `K_{a,b}` for `1 <= a <= b <= 6`;
3. `C5[K_m]` for `1 <= m <= 8`, Petersen, `T(7)`, and the saved
   `D_6,D_8,D_10` barbell equality controls;
4. exact agreement with the existing eleven recorded 184/185 equality rows
   in `results/family_forest.md` wherever their graph encodings are available.

For every row, compute connectivity, `H=G^2`, `B(H)`, both rational distance
averages, `Delta(H)`, exact `L_s`, exact `b`, `T173`, and both residuals. The
gate fails on a convention mismatch, an unexplained negative residual, a
disagreement with a recorded equality, or an optimization timeout. Failure
stops the trial before family generation; it is not permission to choose a
more favorable reading.

## Fixed trial bounds and stop rules

If and only if the gate passes, the complete prospective grid is

```text
2 <= m <= 10,
1 <= L <= 30.
```

This is exactly 270 rooted carrier comets before isomorphism deduplication.
There are no nonuniform cycle weights, extra tails, edge toggles, attachment
orbits, random graphs, or adaptive extensions in v0.4. Every graph receives:

- exact BFS computation of `H`, `B(H)`, `q`, `d_B`, and `d` using rational
  arithmetic;
- exact maximum induced-bipartite optimization for `b`;
- exact connected-domination optimization for `gamma_c`, followed by
  `L_s=n-gamma_c`;
- an independent residual recomputation from explicit witnesses for any row
  with `R184 < 0` or `R185 < 0`.

Every individual optimization solve has a hard **60-second cap**. A timeout is
recorded as an unknown bound and can support neither a hold nor a crossing.
Rows are to be appended incrementally if the trial is later authorized. Stop
after the fixed grid, or earlier only for a gate failure or an independently
verified crossing. No bound may be widened after seeing results.

## Current disposition

**SELECTED, NOT RUN.** No database gate, family generation, invariant solve,
novelty search, Lean work, upstream action, commit, tag, or release belongs to
this selection step.
