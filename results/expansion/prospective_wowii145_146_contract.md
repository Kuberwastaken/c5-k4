# Frozen prospective trial: current DeepMind WOWII 145/146

Frozen: **2026-08-13 UTC**, before evaluating any trial construction.

## Scope and readings

Only the current declarations in DeepMind Formal Conjectures are in scope:

```text
145: 2 eccSet_G(B(G)) <= tree(G) lMin(complement G)
146: 2 eccSet_G(B(G)) <= tree(G) radius(G^2)
```

Here `B(G)` is the set of maximum-eccentricity vertices, `eccSet` is the
maximum over vertices outside the set of their minimum distance to the set,
and `tree(G)` is the maximum order of an induced tree.  Empty outside domains
have set eccentricity zero, matching the formal helper.  The complement local
independence term is the minimum, over vertices of the complement, of the
independence number of its open neighbourhood.  Candidates with a zero
denominator term are inapplicable and may not be counted as crossings.

## Frozen mechanism

The carrier and its uniform blow-ups have small induced-tree number but too
little periphery-set eccentricity.  The prospective move is to introduce
metric asymmetry while preserving dense blocks:

1. **Unequal cycle blow-ups.** Replace the five vertices of `C5` by cliques of
   unequal orders 1--6, with complete joins on cycle edges.
2. **Tails.** Attach a path of length 1--8 to one carrier vertex, or two paths
   of lengths 1--6 at vertices in the same, adjacent, or distance-two blobs.
3. **Pendant blocks.** Attach one or two cliques of order 2--6 by a single
   bridge, with the attachment at a carrier vertex or at a tail endpoint.
4. **Diameter/radius surgery.** Delete one complete join between adjacent
   blobs and replace it by one or two portal edges; optionally append one
   preregistered tail of length 1--6 to a portal.

No additional family may be introduced after results are seen.  Canonical
lexicographic representatives are used and duplicate graph6 strings are
discarded.

## Frozen bounds

- at most 4,000 discovery graphs;
- order at most 30;
- every process at most 60 seconds;
- exact subset enumeration for the induced-tree number when order is at most
  22; larger constructions may be retained only if a separately certified
  exact solver result finishes within 60 seconds;
- record all crossings and the twenty smallest residuals for each target.

Signed residuals are

```text
R145 = tree(G) lMin(complement G) - 2 eccSet_G(B(G))
R146 = tree(G) radius(G^2)       - 2 eccSet_G(B(G)).
```

A negative residual is an apparent crossing.

## Mandatory gate for any crossing

Before reporting a candidate:

1. independently recompute connectivity, all-pairs distances, the periphery,
   set eccentricity, complement local independence, square radius, and the
   exact induced-tree optimum through a separate implementation;
2. exhibit an induced-tree witness and an exact upper-bound certificate;
3. evaluate the identical readings on every connected Atlas graph through
   order seven and on `C5--C9`, `P7`, Petersen, `K3,3`, `K7`, stars, complete
   bipartite graphs, and the uniform `C5[K_m]` controls;
4. reject the reading if a gate graph creates an unexplained crossing;
5. append all evidence to the ledger before alerting the parent.

No novelty claim, public action, issue, PR, release, commit, or push is
authorized in this trial.

## Verdicts

- `CANDIDATE`: strict exact crossing surviving every mandatory gate.
- `HOLD_BOUNDED`: no crossing within the frozen construction and compute
  budget.
- `INCONCLUSIVE`: a potentially crossing graph lacks an exact invariant or
  upper-bound certificate within the cap.
