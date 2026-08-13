# Method v0.8: #183 component-assembly audit

## Outcome

The attempted component formalization exposed a logical bug in the v0.7
interface before any connected-component bookkeeping was needed.

`RootedTrunkPrinciple G` quantifies over **every** connected induced set `S`
and requests a rooted connected dominating set `D` satisfying

```text
|D| + 1 <= b(G[S]).
```

For a singleton `S={v}`, the root condition forces `|D|>=1`, while every
induced bipartite set has size at most the ambient order `1`.  The requested
inequality would therefore say `2<=1`.

The new Lean file proves:

```text
not_rootedTrunkPrinciple (G) [Nonempty V] : ¬ RootedTrunkPrinciple G
```

without `sorry`, `admit`, or custom axioms.

## Consequence for the committed assembly interface

The old definition was

```text
RootedComponentAssembly G x :=
  RootedTrunkPrinciple G -> Nonempty (OutsideBudgetCertificate G x).
```

Because its premise is contradictory on every inhabited graph, this proposition
is trivially true.  The file proves
`rootedComponentAssembly_vacuous`, but labels it explicitly as a diagnostic,
not as the desired mathematical construction.

This also means that the conditional theorem in v0.7 is formally sound but its
premises cannot jointly encode the intended classical proof.

## Corrected boundary

The file introduces `NontrivialRootedTrunkPrinciple G`, which asks for the
`|D|+1` rooted estimate only when the connected induced set has at least two
vertices.

The exact remaining lemma is isolated as:

```text
NontrivialComponentConstruction G x :=
  G.Connected -> NontrivialRootedTrunkPrinciple G ->
    Nonempty (OutsideBudgetCertificate G x).
```

This proposition is the finite construction that must:

1. decompose the appropriate outside graph into connected components;
2. choose attachment neighbors for non-singleton components;
3. apply rooted trunks inside those components;
4. handle singleton components separately (including the isolated outside
   vertex represented by `x`);
5. join the ambient dominating set through `x` and selected neighbors; and
6. combine componentwise induced-bipartite witnesses with the singleton budget.

The Lean theorem `certificate_of_nontrivialComponentConstruction` proves that
this one corrected construction lemma supplies exactly the certificate consumed
by v0.7's already-verified invariant transfer.

## Additional proved rung

The audit also proves the reusable upper bound

```text
largestInducedBipartiteSubgraphSize H <= Fintype.card W
```

directly from the repository's `sSup` definition, plus connectedness of every
singleton induced graph.  These are the two ingredients of the inconsistency
certificate.

## Verification

The parent module was compiled to a temporary `.olean`, then the new file was
checked with the repository source directory as its module root.  The strict
child command was bounded by 60 seconds:

```bash
LEAN_PATH=/tmp/c5k4_183_assembly_check \
  timeout 60s lake env lean \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture183ComponentAssembly.lean
```

Result: exit code `0`.

Temporary axiom-audit commands reported only:

```text
[propext, Classical.choice, Quot.sound]
```

There is no `sorry`, `admit`, `sorryAx`, or custom axiom declaration.
The audit commands were removed before the final warning-as-error build.
