# Erdős 628 Tihany Phase 0: Mycielski near-join edge deletion

Frozen: **2026-08-13 UTC**

Status: **Phase 0 complete; no candidate evaluation performed**

## Exact current target

The sole target is the current DeepMind declaration
`Erdos628.erdos_628` in `FormalConjectures/ErdosProblems/628.lean`:

```text
chi(G)=k, G is K_k-free, a,b>=2, a+b=k+1
  -> some vertex subset induces chromatic number >=a
     and its complement induces chromatic number >=b.
```

At upstream commit `d16e05aded22b8c467a0a27c14b2311f53185006`, the
declaration is `research open`; its blob is
`3aa4c369a1d95b0d9aade18b7739d2f8a4d166a9`. Closed issue #840 and
merged PR #4311 only added the statement. No live issue or PR resolves it.

The local campaign previously classified #628 as a decomposition universal
requiring auxiliary search. It had no equality seed, transformation contract,
or solver lane.

## Proved-domain exclusions

The audit includes more than the three variants currently listed in Lean.
Known domains include:

- exact pairs `(2,2),(2,3),(2,4),(3,3),(3,4),(3,5)`;
- quasi-line graphs and graphs with independence number two;
- graphs with `alpha>=3` and no hole of length `4..2alpha-1`;
- all even-hole-free graphs;
- the 2026 `K_s` and claw-free parameter ranges recorded in the ledger.

These checks matter because a superficially open parameter pair may still be
settled for the chosen graph class.

## Exact open-domain equality seed

Let `H3=C5`, `H4=M(H3)`, and `H5=M(H4)`, using the Mycielski construction.
Thus `H5` is a 5-critical triangle-free graph on 23 vertices. Let `u` be its
latest apex. Add adjacent vertices `x,y`, join both to every vertex of `H5`,
then omit only the cross edge `xu`.

For `(a,b,k)=(2,5,6)` this 25-vertex graph is exact:

- only `x` and `u` can share a color across the two factors, so
  `chi>=2+5-1=6`;
- vertex-criticality gives a four-coloring of `H5-u`; color `x,u` together
  and give `y` a sixth color, so `chi=6`;
- every clique has at most two vertices from triangle-free `H5` and at most
  `x,y`, hence there is no `K6`;
- the displayed factor partition has chromatic numbers exactly two and five.

This is outside every audited proved domain. In particular, `(2,5)` is the
first unsettled `s=2` pair after `(2,4)`; the graph is not claw-free or
quasi-line, has independence number above two, and contains an induced `C4`.

## Sole frozen Phase 1 transformation

Use canonical recursive labels—original vertices, corresponding shadows,
then apex at each Mycielski step. Delete only the embedded original-`C5` edge
`{1,2}` inside `H5`. No other edge, orbit representative, reverse move, or
adaptive continuation is authorized.

The deletion is obstruction-derived: because `H5` is 5-critical, it destroys
the displayed five-chromatic factor. The cost is a real premise risk: the full
graph may fall from chromatic number six to five.

Therefore Phase 1 must first compute and certify `chi` and `K6`-freeness. It
must stop immediately unless the exact premise survives. Only then may it
decide the `(2,5)` partition property for this single graph.

Every future process remains capped at 60 seconds. The ledger is append-only.
No git action, release, issue, pull request, or public action is authorized.
