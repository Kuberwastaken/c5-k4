# Bondy longest-cycles development lane: mathematical and formal audit

## Verdict

**REVISE.** The pinned formal target and the cited source agree, but two proposed
development assumptions do not survive audit:

1. any purely additive cross-component degree lift of the sharp join family
   immediately destroys its path-cover obstruction; and
2. proving only `pc(H) > k` proves non-Hamiltonicity of `K_k ∨ H`, not that a
   longest cycle omits at least `k` vertices or leaves the desired `k`-vertex
   path.

The additive port-rewiring sublane is therefore a **strict stop**. A redesigned
family can proceed only with the stronger `q_k` certificate described below.

## Exact pinned formal target

Audited file:

`FormalConjectures/Arxiv/2606.03696/BondyLongestCycles.lean`

at upstream main pin:

`5a5af706fa5bef3f09606554d393c9170d2b27e8`.

The conjecture has the following quantifier order and content:

```lean
answer(sorry) ↔
  ∀ (k : ℕ), 1 ≤ k →
  ∀ (V : Type) [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj],
    IsKConnected G k →
    ((Fintype.card V : ℝ) + k * (k - 1)) / (k + 1) ≤ G.minDegree →
    ∀ (a : V) (C : G.Walk a a),
      C.IsCycle →
      C.length = G.circumference →
      ∀ (u v : offWalk C)
        (P : (G.induce (offWalk C)).Walk u v),
        P.IsPath →
        P.support.length + 1 ≤ k
```

The large-graph variant has

```lean
∀ k, 1 ≤ k → ∃ N, ∀ V G, N ≤ Fintype.card V → ...
```

so `N` depends only on `k`, as intended.

### `answer` wrapper

The repository default is `google.answer = always_true`. At expected type
`Prop`, `answer(sorry)` elaborates to `True`. Consequently the theorem proof
target is definitionally of the shape

```lean
True ↔ P
```

rather than directly `P`. A proof port must first eliminate/simplify this
wrapper (for example through `true_iff`) or prove both implications. Merely
proving the right-hand proposition without resolving the outer equivalence
does not match the declaration.

### Graph notions used by the statement

- `IsKConnected G k` means both `k < Fintype.card V` and: for every finite
  vertex set `S` with `S.card < k`, the induced graph on the complement of `S`
  is connected.
- `G.minDegree : ℕ` is the minimum of the finite vertex degrees, with value
  zero on an empty vertex type. In the displayed hypothesis it is coerced to
  `ℝ`. The surrounding expected type also makes the displayed arithmetic,
  including `k - 1`, real arithmetic rather than truncated natural
  subtraction.
- `G.circumference` is the natural-number supremum of the lengths of cycles in
  `G`; it is zero for an acyclic graph. `C.length` counts edges.
- `offWalk C := {v | v ∉ C.support}`. The induced graph in the theorem
  therefore has exactly the vertices outside the support of `C`.
- A walk's support is its ordered list of visited vertices and satisfies
  `P.support.length = P.length + 1`. Thus the conclusion really counts path
  vertices.
- `P.IsPath` means that `P.support` has no repeated vertex. The nil walk at a
  vertex is a legitimate singleton path. There is no empty path object in this
  endpoint-indexed representation.
- `C.IsCycle` is a nonempty edge-simple closed walk whose tail support has no
  repeated vertex. In a simple graph such a cycle has length at least three.

It follows that

```lean
P.support.length + 1 ≤ k
```

is exactly the subtraction-safe rendering of "the path has at most `k - 1`
vertices." In particular, a `k`-vertex path violates it.

## Source and theorem ranges

The source is arXiv:2606.03696v1, *Longest cycles and Dirac-type results in
highly connected graphs*, by Jie Ma, Bo Ning, and Ziyuan Zhao.

- Conjecture 1 is exactly the minimum-degree statement formalized above.
- The cases `k = 1`, `k = 2`, and `k = 3` are proved. The general conjecture
  remains open for every `k ≥ 4`.
- Zhang proved the conjecture for claw-free graphs, for all `k`.
- Theorem 1.1 proves the conjecture for sufficiently large graphs and the paper
  gives the explicit sufficient range

  ```text
  n ≥ 5k² + 7k.
  ```

  The Lean `large` variant correctly records only the existential `N` form.
- The paper's Theorem 1.2 applies for `k ≥ 2`, minimum degree `δ ≥ 6k`,
  and the presence outside a longest cycle of a path on at least `k - 1`
  vertices; its conclusion is `|C| ≥ k(δ - k + 2)`.

Accordingly, any prospective counterexample must at minimum satisfy all of:

```text
k ≥ 4,
n < 5k² + 7k,
the graph contains an induced claw.
```

These are theorem-shadow gates, not optional search heuristics.

## Sharp family and residual computation

Let

```text
S(k,t) = K_k ∨ ((k+1)K_t),   t ≥ k ≥ 1.
```

Its order and minimum degree are

```text
n = k + (k+1)t,
δ = t + k - 1.
```

Consequently its scaled residual is exactly

```text
(k+1)δ - n - k(k-1) = -1,
```

or equivalently

```text
δ = (n + k(k-1) - 1)/(k+1).
```

This is the source's claimed sharpness gap.

In the nondegenerate range, a cycle can use vertices from at most `k` of the
`k+1` peripheral cliques: every nonempty peripheral segment on a cycle must be
separated from the next by a hub vertex. A longest cycle uses all `k` hubs and
all `t` vertices of exactly `k` peripheral cliques. It has length

```text
k(t+1)
```

and leaves one whole `K_t`, which contains a path on `t ≥ k` vertices.

There is one endpoint caveat in the informal sharpness sentence. For
`k = t = 1`, the graph is `P₃` and has no cycle. Thus "each longest cycle"
has no witness in the formal sense. State the family with `k ≥ 2`, or treat
`k = 1` separately with `t ≥ 2`.

## Hamilton cycles in `K_k ∨ H` and path covers of `H`

Use the standard convention that paths are nonempty, singleton paths count,
and a spanning path cover consists of pairwise vertex-disjoint paths whose
vertex sets partition `V(H)`.

For `k ≥ 1` and total order `|V(K_k ∨ H)| ≥ 3`, the exact equivalence is

```text
K_k ∨ H has a Hamilton cycle
  ⇔
H has a spanning cover by at most k vertex-disjoint paths.
```

### Forward implication

Delete the hub vertices from a Hamilton cycle. Its remaining nonempty blocks
are vertex-disjoint paths in `H`, span `H`, and there are at most as many
blocks as used hub vertices, hence at most `k`. If the Hamilton cycle uses no
hub at all, it lies wholly in `H`; cutting one cycle edge gives one spanning
path, which is allowed because `k ≥ 1`.

### Reverse implication

Arrange the nonempty cover paths cyclically and separate consecutive paths by
distinct hub vertices. Every required endpoint-to-hub edge exists by the join
definition. Insert any unused hubs consecutively in one separator position,
using clique edges between hubs. This produces a spanning cycle.

Singleton paths cause no problem when the resulting graph has at least three
vertices. The only apparent failure is the two-vertex construction where the
same hub edge would have to be traversed twice.

### Small exceptions

- `k = 0` is excluded: a Hamilton cycle in `H` is not equivalent to a cover by
  zero paths.
- If `H` is empty, the right side has the empty cover; the join is `K_k`, which
  is Hamiltonian exactly when `k ≥ 3`.
- If `k = 1` and `H` is a singleton, the cover side is true but the join is
  `K₂`, which has no simple cycle.
- If `k = 1` and `H` has at least two vertices, a one-path spanning cover has
  distinct endpoints and closes through the hub correctly.

The compact hypotheses `k ≥ 1` and total order at least three subsume these
small exceptions.

## Strict stop: additive port rewiring

Let the peripheral graph initially be

```text
H₀ = (k+1)K_t.
```

Adding even one edge `xy` between two distinct peripheral cliques gives a
spanning path cover of the new `H` by `k` paths:

1. take Hamilton paths in the two cliques incident with `xy` and concatenate
   them through `xy`; and
2. take one Hamilton path in each of the remaining `k-1` cliques.

By the equivalence above, `K_k ∨ H` is then Hamiltonian.

The peripheral cliques are already complete, so every purely additive degree
lift must add a cross-component edge. Therefore **no additive port-rewiring
lift of the sharp family can preserve the obstruction**, even before checking
whether every minimum-degree vertex has been lifted. A Hamiltonian result also
makes it impossible for a longest cycle to leave the intended `k`-vertex
path.

A construction that deletes internal edges while adding cross edges is not
covered by this impossibility argument, but it is a genuinely different
family. It must reprove all block path properties and the global longest-cycle
bound; the old clique-cover argument cannot be inherited.

Merely keeping a designated `k`-vertex path induced or visibly outside one
chosen cycle is not enough. Added ports can let another cycle absorb that path
or omit fewer vertices elsewhere.

## Why `pc(H) > k` is insufficient

The join/path-cover equivalence shows only

```text
pc(H) > k  ⇒  K_k ∨ H is non-Hamiltonian.
```

This bounds the circumference by `n - 1`, not by `n - k`. Even the exact value
`pc(H) = k + 1` does not prevent deletion of one or a few vertices from
reducing the path-cover number to at most `k`.

An explicit path cover is weaker still: it is an *upper* bound on `pc(H)` and
therefore points toward Hamiltonicity. It cannot certify that a proposed
nonspanning cycle is longest.

## Sound longest-cycle certificate

Define the maximum `k`-path-packing order

```text
q_k(H) = max { |U| : U ⊆ V(H) and H[U] is coverable
                     by at most k vertex-disjoint paths }.
```

For every cycle `D` in `K_k ∨ H`, the vertices of `D` lying in `H` split
into at most `k` path blocks after deleting the hubs. If `D` uses no hub, cut
one edge of the cycle in `H` to obtain one path. Hence

```text
|D| ≤ k + q_k(H).
```

A complete certificate for a counterexample must provide:

1. a `k`-vertex path `Q` in `H`;
2. an explicit cycle `C` in `K_k ∨ H` using every hub and exactly the
   vertices `V(H) \ V(Q)`; and
3. a checked upper bound

   ```text
   q_k(H) ≤ |V(H)| - k.
   ```

Then every cycle has length at most

```text
k + (|V(H)| - k) = |V(H)| = |V(K_k ∨ H)| - k,
```

while the exhibited `C` attains that length and its off-cycle induced graph
contains `Q`. This simultaneously certifies

```lean
C.length = G.circumference
```

and a path that falsifies `P.support.length + 1 ≤ k`.

An equivalent deletion-resilience form of the upper bound is

```text
∀ X ⊆ V(H), |X| < k → pc(H - X) > k.
```

Indeed, a set coverable by at most `k` paths and larger than `|H|-k` has a
complement of size less than `k`, and conversely.

For finite exact certification, `q_k(H)` can be encoded as the maximum number
of selected vertices in a linear forest `F ⊆ H` satisfying

```text
maximum degree(F) ≤ 2,
F is acyclic,
|V(F)| - |E(F)| ≤ k.
```

The last expression is the number of path components, including singleton
vertices. A computational optimum must be accompanied by an independently
checkable certificate: for example, a complete finite ledger for all deletion
sets of size `< k`, a verified combinatorial separator/capacity argument, or a
solver dual plus a checker that validates every constraint. A bare optimizer
claim is not enough for the formal longest-cycle obligation.

## Required lane corrections

1. Freeze the exact formal target including its outer `True ↔ ...` wrapper.
2. Enforce `k ≥ 4`, `n < 5k²+7k`, and non-claw-free as hard theorem-shadow
   gates.
3. Exclude the degenerate sharp-family endpoint `k=t=1`.
4. Stop all purely additive port-rewiring proposals based on
   `(k+1)K_t`.
5. For any redesigned family, replace the whole-graph `pc(H)>k` target with
   the robust `q_k(H) ≤ |H|-k` target.
6. Require both sides of the exact certificate: a witnessed cycle omitting a
   witnessed `k`-vertex path, and an independently checked global upper bound
   proving that cycle is longest.
