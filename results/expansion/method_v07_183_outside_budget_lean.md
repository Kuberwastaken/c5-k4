# Method v0.7: Lean extraction of the #183 outside-neighborhood budget

> **Correction (method v0.8):** the `RootedTrunkPrinciple` interface defined
> in this checkpoint is inconsistent on singleton induced subgraphs, so the
> corresponding conditional assembly premise is vacuous. The formal diagnosis
> and corrected nontrivial-component interface are recorded in
> `method_v08_183_component_assembly.md`. The certificate-to-invariant transfer
> proved below remains valid; only the proposed source of the certificate
> required repair.

## Result

`lean/GraphConjecture183OutsideBudget.lean` formalizes the complete
invariant-transfer layer of

```text
gamma_c(G) <= b(G - N_G(x)).
```

Here `N_G(x)` is the open neighborhood, so `x` remains in the induced outside
graph.  The final Lean corollary uses the repository's real-valued
`SimpleGraph.b` definition, not an ad hoc replacement.

The rooted DeLaViña--Waller trunk construction and its componentwise assembly
are not yet formalized.  They are exposed as named propositions and passed as
ordinary theorem hypotheses.  They are **not** axioms.

## Formal interfaces

The file introduces:

- `outsideVertices G x = (G.neighborSet x)ᶜ`;
- `outsideGraph G x = G.induce (outsideVertices G x)`;
- `RootedTrunkPrinciple G`, the rooted connected-dominating-trunk statement;
- `OutsideBudgetCertificate G x`, containing an ambient connected dominating
  set `D`, an induced-bipartite outside witness `B`, and `|D| <= |B|`;
- `RootedComponentAssembly G x`, the exact interface asserting that rooted
  trunks assemble into such a certificate.

No classical graph-theory claim is hidden in a definition returning data: the
two unfinished mathematical steps are propositions that callers must prove and
supply.

## Proved Lean chain

The following pieces are complete:

1. An explicit connected dominating set bounds the repository's `sInf`
   definition of `connectedDominationNumber`.
2. An explicit induced-bipartite witness bounds the repository's `sSup`
   definition of `largestInducedBipartiteSubgraphSize`.
3. An `OutsideBudgetCertificate` therefore proves the natural-valued budget
   inequality.
4. Casting gives the requested repository-level statement
   `(G.connectedDominationNumber : ℝ) <= SimpleGraph.b (outsideGraph G x)`.
5. The budget inequality implies exactly
   `outsideOddTransversalNumber G x <= outsideSlack G x`.
6. The outside subtype cardinality is proved to be
   `Fintype.card V - G.degree x`, and the slack is rewritten in this ambient
   notation.

Thus the formal implication to the paper-coordinate wall is:

```text
tau_odd(G - N(x)) <= n - degree(x) - gamma_c(G).
```

## Remaining trunk

A full unconditional proof must instantiate `RootedTrunkPrinciple` from the
rooted DeLaViña--Waller construction and then prove
`RootedComponentAssembly`.  This requires formal connected-component bookkeeping
and the construction that joins the component trunks through the root and its
neighbors.  The current extraction deliberately isolates that work from the
already-verified `sInf`/`sSup`, cardinal, cast, and subtraction reasoning.

## Verification

From `/Users/kuber.mehta/Projects/formal-conjectures`:

```bash
timeout 60s lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture183OutsideBudget.lean
```

Result: exit code `0`.

Temporary `#print axioms` checks, removed before commit, reported only:

```text
[propext, Classical.choice, Quot.sound]
```

There is no `sorry`, `admit`, `sorryAx`, or custom axiom declaration.
