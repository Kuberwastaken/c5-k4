# Method v0.6 Lane P1: the attachment obligation as component parity

Date: **2026-08-13**. Status: **the remaining attachment problem is reduced
exactly to a bounded component-coloring compatibility test; the reduction is
proved and survives every frozen control and both mandatory equality
families, but existence of the required compatible pair is not proved**.

This note continues `method_v05_183_slack_budget.md`. It edits no earlier
result, widens no catalogue, and uses only the frozen connected Graph Atlas
and McKay order-eight controls. Every subprocess was externally capped at 60
seconds.

## Setup

Let `G` satisfy the live hypotheses:

```text
G is connected, nonbipartite, and claw-free;
L3(x)={z}, with no vertex farther from x;
gamma_c(G)>=5.
```

Write

```text
A = N_G(x),
H = G-A,
d = |A|,
s = n-d-gamma_c(G).
```

The neighborhood is open, so `x` is an isolated vertex of `H`. The universal
theorem in the preceding note proves

```text
tau_odd(H) <= s.
```

Hence there is an odd-cycle transversal `U subset V(H)-{x}` with `|U|<=s`.
Put

```text
K = H-U.
```

The graph `K` is bipartite and still contains the isolated vertex `x`.

For such a set `U`, recall

```text
rho_x(U) = max |P| over P subset A
           such that G[(V(K)) union P] is bipartite.
```

The exact identity from the preceding note shows that the remaining target is

```text
rho_x(U) >= |U|+2-s
```

for at least one bipartizing `U` of order at most `s`.

## General component-coloring formulation

Fix a bipartition of every nontrivial component `C` of `K`; let its reference
color be `chi_C`. Each component may be flipped independently, represented by
a Boolean variable `epsilon_C`.

Fix `x` to color zero. Every retained vertex `p in P` is adjacent to `x`, so
every such `p` must have color one. Consequently:

1. `P` must be independent in `G[A]`;
2. for every component `C` and every `v in N(p) intersect C`, the chosen flip
   must put `v` in color zero.

Using a Boolean selection variable `y_p` for each `p in A`, every attachment
condition is the implication

```text
y_p ==> (chi_C(v) xor epsilon_C = 0),
```

which is a two-literal clause after the right side is written as a literal in
`epsilon_C`. Every edge `pq` of `G[A]` adds

```text
not y_p or not y_q.
```

Thus compatible attachment is a component-flip 2-SAT instance, followed by a
cardinality requirement on the selected `y_p`. In the present claw-free
setting that instance collapses further and no general cardinality encoding
is needed.

## Claw-free collapse

> **Attachment clique lemma.** For each `p in A`, the set
>
> ```text
> N_G(p) intersect (V(H)-{x})
> ```
>
> is a clique.

Proof. If two vertices `u,v` in that set were nonadjacent, then
`{x,u,v}` would be an independent triple in `N(p)`: neither `u` nor `v` is
adjacent to `x`, by the definition of `H`. The four vertices centered at `p`
would induce a claw. QED.

After deleting `U`, that attachment clique lies in the bipartite graph `K`.
It therefore has order at most two. If it has order two, its vertices are
adjacent and occupy opposite color classes of one component, so no flip can
place both in color zero.

This gives an exact criterion.

> **Clean-vertex criterion.** A vertex `p in A` can occur by itself in a
> compatible retention set if and only if
>
> ```text
> |N_G(p) intersect (V(K)-{x})| <= 1.
> ```

Call such a vertex **`U`-clean**. Notice that the always-present neighbor `x`
is deliberately excluded from the count.

For a `U`-clean vertex `p`, write `a_U(p)` for its unique neighbor in
`V(K)-{x}`, if it has one. Two `U`-clean vertices `p,q` can be retained
together if and only if:

1. `pq` is not an edge; and
2. if `a_U(p)` and `a_U(q)` lie in the same component of `K`, their distance
   parity in that component is even.

The parity condition says exactly that the two attachment vertices lie in the
same side of the component bipartition. If either attachment is absent or the
attachments lie in different components, independent component flips make
the pair compatible automatically.

## Exact conflict-graph formula

Define the **attachment conflict graph** `F_U` on the `U`-clean vertices of
`A`. Join `p` and `q` in `F_U` when either

```text
pq is an edge of G,
```

or their unique attachments lie in the same component of `K` at odd distance.

> **Proposition.**
>
> ```text
> rho_x(U) = alpha(F_U).
> ```

Proof. The clean-vertex criterion is necessary for every selected vertex.
Within one component, all selected unique attachments must occupy the same
bipartition side, which is equivalent to every pair having even distance.
Different components can be flipped independently. Finally, all selected
vertices have the same color opposite `x`, so they must be independent in
`G[A]`. These are precisely the nonedges of `F_U`. Conversely, an independent
set in `F_U` supplies consistent flip requirements in each component and
therefore extends to a bipartition after the selected vertices are added.
QED.

Claw-freeness at `x` gives `alpha(G[A])<=2`; otherwise three independent
neighbors of `x` induce a claw. Hence

```text
rho_x(U) <= 2.
```

Since `|U|<=s`, the required quantity

```text
r(U)=|U|+2-s
```

is also at most two. The complete attachment test is therefore:

```text
r(U)<=0: automatic;
r(U)=1: F_U must have a vertex;
r(U)=2: F_U must have a nonedge.
```

This is a finite vertex/pair scan after bipartizing `H`; no larger SAT or ILP
instance is hidden in the final step.

## Why the parity clause cannot be dropped

The frozen graph

```text
graph6 = GCQ`e_
E = {03,05,07,14,17,25,26,36,37}
```

already refutes the tempting simplification that any two nonadjacent
`U`-clean vertices are compatible. Take `(x,z)=(0,4)`. Then

```text
A={3,5,7}, U=empty, s=0.
```

All three vertices of `A` are clean. The vertices `3` and `5` are
nonadjacent, but their unique outside attachments are respectively `6` and
`2`. These are the endpoints of the edge `2-6` in `K`, hence have odd
distance and impose opposite flips. The pair `{3,5}` is incompatible.

The pair `{5,7}` is compatible because its attachments lie in different
components. Thus the graph satisfies the real attachment obligation while
showing that component parity is logically essential.

## Frozen exact audit

The exact checker enumerated every bipartizing `U` through order `s`, computed
`rho_x(U)` both by direct induced-bipartite subset testing and by the
clean/parity conflict graph, and asserted equality of the two answers.

| catalogue | qualifying graphs | qualifying `(x,z)` pairs | admissible `U` checked | formula mismatches | attachment failures |
|---|---:|---:|---:|---:|---:|
| Graph Atlas, orders at most 7 | 0 | 0 | 0 | 0 | 0 |
| McKay connected order 8 | 5 | 9 | 9 | 0 | 0 |

Every frozen live orientation has `s=0`, so `U` is empty and the required
value is `rho_x(empty)=2`. The conflict graph has a nonedge in all nine cases.

The McKay input remains the frozen 11,117-graph file `/tmp/graph8c.g6` with
SHA-256

```text
0002354f1ab3344a2706626a037ad15367bf23a2163aa68f552c3a169ca9a036.
```

## Mandatory family `H_m`

For `H_m`, `m>=4`, at `x=q0`,

```text
s=0, U=empty.
```

The vertices `r0` and any `qj`, `j!=0`, are clean and nonadjacent. The vertex
`r0` has no attachment beyond `x`, while `qj` has the unique attachment `rj`.
They are therefore compatible, and

```text
rho_x(empty)=2=|U|+2-s.
```

The attachment inequality is exact. Direct and conflict-graph computations
agree for every `m=4,...,12`; the displayed pair proves every `m>=4`.

## Mandatory family `J_m`

For `J_m`, `m>=5`, at `x=q0`,

```text
s=1, tau_odd(H)=1.
```

Choose `U={r2}`. The vertices `r0` and `q3` are `U`-clean, nonadjacent, and
compatible: `r0` has no outside attachment, while `q3` attaches only to `r3`.
Thus

```text
rho_x(U)=2=|U|+2-s.
```

Again the attachment inequality is exact. The checker enumerated every
bipartizing `U` through order one, not merely the displayed witness. Direct
and conflict-graph values agree on all 24 admissible sets across
`J_5,...,J_12`; the construction proves every `m>=5`.

Together with the nine `H_m` cases, 33 admissible family transversals were
checked with zero formula mismatches.

## Slack trichotomy

Let

```text
t = tau_odd(H)
```

and choose a minimum odd-cycle transversal `U`, so `|U|=t<=s`. The required
conflict-graph independence number becomes

```text
2-(s-t).
```

Consequently the remaining lane separates into only three cases:

```text
s-t >= 2: already proved, with P empty;
s-t  = 1: it is enough to find one U-clean vertex;
s-t  = 0: it is necessary and sufficient to find a compatible clean pair.
```

There is no fourth case. In particular, all hard frozen orientations and both
mandatory families lie on the equality wall `s=t`, which explains why their
certificates require two retained neighbors. Any proof may therefore focus
first on equality in the universal theorem

```text
gamma_c(G) <= b(G-N(x));
```

one unit of strictness reduces the attachment task to a single clean vertex,
and two units finish the target without any attachment at all.

## The formalizable remaining condition

The sole unresolved statement can now be recorded without informal coloring
language.

> **Attachment-pair condition.** Under the live hypotheses, there exists an
> odd-cycle transversal `U subset V(H)-{x}` with `|U|<=s` such that the
> attachment conflict graph `F_U` has an independent set of order at least
>
> ```text
> |U|+2-s.
> ```

By the proposition and the exact `rho_x(U)` identity, this condition is
equivalent to the remaining live instance of WOWII 183. It is immediately
formalizable using:

1. induced bipartiteness of `H-U`;
2. the predicate that a neighbor of `x` has at most one remaining attachment;
3. connectivity and even-distance parity within `H-U`; and
4. a vertex-or-pair witness, since the requested order never exceeds two.

No proof was found forcing the required vertex or pair from claw-freeness and
the unique third layer alone. In particular, the frozen `GCQ`e_` orientation
shows that merely producing two clean nonadjacent vertices is insufficient;
their attachment parity must also be controlled.

## Reproduction discipline and honest stop point

All finite checks used the repository's pinned environment and an external
timeout:

```bash
timeout 60s /home/ec2-user/.venvs/wowii/bin/python <exact-attachment-checker>
```

The checker reused the exact invariant routines in
`scripts/method_v03_183_lemma_check.py`. It generated no catalogue and wrote
no auxiliary result file.

The result is:

1. compatible attachment is exactly a component-flip constraint problem;
2. claw-freeness collapses it to clean vertices plus a pairwise parity
   conflict graph;
3. the conflict-graph formula is proved and independently matches direct
   computation on every permitted control;
4. `H_m` and `J_m` remain mandatory equality families;
5. the parity clause is essential, with an exact frozen counterexample to its
   removal;
6. existence of the required independent vertex/pair remains the final open
   paper step.

Accordingly WOWII 183 remains open in this lane. No counterexample, complete
proof, public claim, or catalogue extension follows from this report.
