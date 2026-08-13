# Method v0.4: WOWII 133 two-edge bridge

Date: 2026-08-13

Local artifact: `lean/GraphConjecture133Cubic.lean`

## Result

This bounded formalization pass closes the triangle-free path-extension
boundary left by `method_v04_133_neighbor_bridge.md`.  It does not prove the
full WOWII 133 conjecture or the complete local `CubicC4FreeSplit` statement.

The repaired capacity lemma is:

```lean
exists_contact_free_of_four_candidates_of_cubic
```

For four fresh candidate vertices whose contacts with a shortest walk are
restricted to indices 2 and 3, it proves that one candidate has no contact
with the walk.  The proof counts available cubic neighbor slots separately
when the walk length is 2, 3, or at least 4.  The respective capacities are
2, `1 + 2`, and `1 + 1`, all smaller than four.

The capacity lemma is then assembled with the previously proved branch and
contact lemmas to obtain:

```lean
radius_add_three_le_path_of_cubic_triangleFree_c4Free
    (G : SimpleGraph V) [DecidableRel G.Adj] (hconn : G.Connected)
    (hreg : G.IsRegularOfDegree 3) (htri : G.CliqueFree 3)
    (hc4 : ¬HasC4 G) :
    G.radius.toNat + 3 ≤ path G
```

Thus both path inequalities needed by the proposed cubic split are now
proved locally:

- `radius_add_two_le_path_of_cubic_c4Free`, with no triangle-free assumption;
- `radius_add_three_le_path_of_cubic_triangleFree_c4Free`, for the
  triangle-free branch.

The intermediate theorem
`exists_inducedPath_two_cons_support_of_geodesic_of_cubic_triangleFree_c4Free`
exhibits the actual induced list `x :: c :: p.support`, of length
`p.length + 3`.

## Proof structure

At a geodesic head `u`, triangle-freeness and cubicity provide two distinct
off-direction neighbors `a,b`.  Each has two forward neighbors, and
C4-freeness makes the resulting four candidates distinct.  Every candidate
is outside the geodesic, and any possible geodesic contact is confined to
index 2 or 3.

The capacity lemma selects a contact-free candidate `x`.  Its parent branch
vertex `c` is itself fresh and clean against the positive geodesic tail.
First prepend `c`, then prepend `x`; the repository-local induced-list helper
proves that `x :: c :: p.support` is induced.  Applying the `path` maximum to
the radius-realizing geodesic gives `radius + 3 ≤ path`.

## Verification

All subprocesses were capped at 60 seconds.  The final warning-as-error build
was run from the `formal-conjectures` Lake project:

```text
timeout 60s lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture133Cubic.lean
```

Result: exit status 0 in approximately 10 seconds, with no output.

A temporary `#print axioms` audit of both the capacity lemma and the
`radius + 3` endpoint reported only `propext`, `Classical.choice`, and
`Quot.sound`.  It reported no `sorryAx` or project-specific axiom.  The
temporary commands were removed afterward.  A source scan and `git diff
--check` also passed; there is no `sorry`, `admit`, or custom axiom in the
artifact.

## Remaining boundary

The path-extension work for the cubic C4-free split is closed.  What remains
is the separate local-average calculation:

1. prove `⌊l G⌋ = 3` for triangle-free cubic graphs; and
2. prove `⌊l G⌋ = 2` for cubic C4-free graphs containing a triangle.

Only after those identities are formalized can `CubicC4FreeSplit` be
constructed and fed to the already compiled `conclusion_of_split`.  No claim
is made here about the noncubic C4-free branch of full WOWII 133.
