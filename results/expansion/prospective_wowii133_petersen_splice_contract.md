# Frozen prospective trial: Petersen 3-edge splice for current WOWII #133

Frozen: **2026-08-13 UTC**, after the source/status/theorem-domain audit and
before constructing or evaluating any splice graph.

## Source and known-domain audit

- Upstream: `google-deepmind/formal-conjectures` at
  `d16e05aded22b8c467a0a27c14b2311f53185006`.
- Source: `FormalConjectures/WrittenOnTheWallII/GraphConjecture133.lean`, blob
  `9a8dca984e87efc2fb1ffd68f5d4185e4645a8e8`.
- Live declaration: `conjecture133`, tagged `@[category research open]`.
- GitHub issue/PR audit: no issue, proof PR, or disproof PR for WOWII #133.
  The only target-specific merged PR is #4282, which corrected `path` and the
  C4 characteristic; it did not prove the conjecture.
- Repository/literature audit found no theorem covering the frozen cubic
  splice family. This trial must be stopped if the executable live gate or
  independent audit discovers otherwise.

## Exact wall and one frozen transformation

For a connected C4-free graph the current statement has residual

```text
R133(G) = path(G) - radius(G) - floor(l(G)).
```

Petersen is exact equality: `(path,radius,floor(l))=(5,2,3)`.

The only development transformation is a cubic **3-edge splice** of two
labelled Petersen copies:

1. delete vertex zero from each copy;
2. retain their three now-degree-two neighbor portals in sorted order;
3. add a perfect matching between the two portal triples;
4. evaluate all six portal bijections, deduplicating identical labelled edge
   sets but not selecting a favorable matching after evaluation.

This is a nonlocal bottleneck composition, distinct from the completed cover,
2-switch, edge-contraction, subdivision, pendant, polarity, chord, deletion,
and articulation-amalgam lanes. It preserves connectedness and cubicity. The
girth-five portal geometry predicts no triangles or C4s; those properties are
mandatory construction gates rather than trusted metadata.

## Frozen prediction

The splice may raise radius through the cross-cut while allowing fewer than
three additional vertices in a longest induced path. Since every accepted
output is cubic and triangle-free, `floor(l)=3`; a crossing requires

```text
path(G) < radius(G) + 3.
```

If an explicit induced path of target order is found, that graph is safely
rejected without needing its exact maximum. Exact maximum induced-path search
is nevertheless required for the closest representative and every equality
or crossing.

## Mandatory executable gate

Before development:

1. execute literal git commands to verify live upstream commit, blob, open
   tag, corrected induced-path definition, and non-induced C4 branch;
2. run the current exact reading on all 995 connected Graph Atlas graphs of
   orders two through seven plus `C5--C9`, `P7`, Petersen, `K3,3`, `K7`, the
   frozen stars, and complete-bipartite controls;
3. require zero crossings/timeouts and reproduce Petersen equality with an
   independently replayed five-vertex induced path.

Any mismatch gives `DB_SANITY_REJECT` and prohibits splice evaluation.

## Evidence, caps, and verdicts

- Append, flush, and `fsync` the contract, gate, each matching, summaries,
  and audit rows.
- Every operating-system process and exact search is capped at 60 seconds.
- Any crossing requires a separate implementation to reconstruct every
  matching, recompute all coordinates, prove the maximum-path upper bound,
  and redo the current status/theorem-domain audit.
- Verdicts: `DB_SANITY_REJECT`, `CANDIDATE_ADVERSARIAL`, `HOLD_BOUNDED`, or
  `INCONCLUSIVE`.

No commit, push, release, issue, pull request, or public action is authorized.

