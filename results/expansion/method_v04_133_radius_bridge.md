# Method v0.4: WOWII 133 finite-radius geodesic bridge

Status: **PROVED LOCALLY / NO SORRY**

Date: **2026-08-13 UTC**

Local artifact: `lean/GraphConjecture133Cubic.lean`

This follow-up addresses only the next bounded bridge after
`method_v04_133_geodesic_bridge.md`: selecting radius-realizing endpoints in a
finite connected graph, choosing a shortest walk, and obtaining the resulting
lower bound for the repository-local `path` invariant.  It does not attempt
the cubic/C4-free extension arguments.

## Compiled theorems

```lean
lemma exists_radius_geodesic_support (G : SimpleGraph V)
    (hconn : G.Connected) :
    ∃ (u v : V) (p : G.Walk u v),
      p.length = G.radius.toNat ∧
      G.isInducedPath p.support ∧
      p.support.length = G.radius.toNat + 1
```

Under the file's finite and nonempty vertex assumptions, this packages a
radius-realizing geodesic together with exactly the list facts needed later.
It needs no decidable-equality instance.

```lean
lemma radius_add_one_le_path (G : SimpleGraph V) (hconn : G.Connected) :
    G.radius.toNat + 1 ≤ path G
```

This combines the witness theorem with `path_ge_of_isInducedPath`.  The
decidable-equality assumption here comes only from the finite-set
implementation of the project-local `path` invariant.

## Proof route

1. `SimpleGraph.exists_edist_eq_radius_of_finite` supplies vertices `u,v`
   with `G.edist u v = G.radius`.
2. `Connected.exists_path_of_dist u v` supplies a walk `p` satisfying
   `p.length = G.dist u v`.
3. Since `dist` is `edist.toNat`, applying `ENat.toNat` to the radius equality
   rewrites the shortest-walk length to `G.radius.toNat`.
4. The previously proved
   `isInducedPath_support_of_length_eq_dist` establishes that `p.support` is
   induced.
5. `Walk.length_support` gives
   `p.support.length = p.length + 1 = G.radius.toNat + 1`.
6. `path_ge_of_isInducedPath` inserts this support into the finite maximum
   defining `path G`, yielding `G.radius.toNat + 1 ≤ path G`.

The `Walk.IsPath` proof returned alongside the shortest walk is not required:
the prior bridge proves the stronger list-shaped induced-path property
directly from the distance equality.

## Verification

Every Lean or source-search subprocess was explicitly capped at 60 seconds.
Final command:

```text
timeout 60s lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture133Cubic.lean
```

Result: exit status `0` in approximately 6.1 seconds.  A capped source scan
finds no `sorry`, `admit`, or custom `axiom` in the local file.
`#print axioms` for both new theorems reports only `propext`,
`Classical.choice`, and `Quot.sound`; in particular, neither theorem depends
on `sorryAx` or a project-specific axiom.

## Next boundary

The generic metric baseline is now complete: every finite connected graph has
an induced path on at least `radius + 1` vertices.  The WOWII 133 cubic
specialization still needs one or two additional vertices:

- prove radius at least two from cubicity and C4-freeness (radius zero and one
  must be excluded);
- select off-geodesic neighbors of the chosen center endpoint and prove a
  clean one-vertex extension, obtaining `radius + 2`;
- in the triangle-free branch, prove the two-vertex extension needed for
  `radius + 3`.

Thus the remaining obstruction is no longer an `edist`/`dist`/walk/list API
conversion.  It is the first genuinely cubic local-neighborhood lemma from
the paper proof.
