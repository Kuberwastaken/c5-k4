# Executable certificate for Written on the Wall I #889

This directory certifies a counterexample to S. Fajtlowicz's *Written on the
Wall I* conjecture #889. The witness is

\[
G=\overline{C_5[K_4]},
\]

the complement of the lexicographic product of the five-cycle and the
four-clique.

## The statement and its blue graph

The July 2004 source states:

> If G is a regular (connected) triangle-free graph, w(v) the number of
> vertices at odd distance from v, and w - the maximum of w(v) then then G has
> a blue clique with w/4 vertices.

The duplicated “then” and the dash before “the maximum” are retained from the
source. Thus `w = max_v w(v)`.

Conjecture #822 supplies the color convention. For a graph class `P`, it colors
a nonedge `xy` red if adding `xy` takes the graph outside `P`, and blue
otherwise. Here `P` is the class of triangle-free graphs. Consequently, a
nonedge is blue precisely when its endpoints have no common neighbor; adding
such an edge creates no triangle.

## The witness

Label the vertices `(i,j)`, where `i` is in `Z/5Z` and `0 <= j < 4`. Put an
edge between `(i,j)` and `(i',j')` exactly when `i-i'` is `2` or `3` modulo
five. This is `complement(C5[K4])`: its five four-vertex blobs are independent,
and its quotient on the blobs is again a five-cycle.

- It has 20 vertices and 80 edges. Every vertex is joined to all four vertices
  in each of two blobs, so it is 8-regular.
- It is connected because its five-blob quotient is a cycle.
- It is triangle-free: each blob is independent, and the quotient cycle has no
  triangle.
- It has diameter two. Different nonadjacent blobs are two steps apart in the
  quotient; two vertices in one blob share every vertex in either neighboring
  quotient blob.

Since the diameter is two, the vertices at odd distance from any vertex are
exactly its eight neighbors. Therefore `w(v)=8` for every `v`, and `w=8`.

Every nonedge has a common neighbor by the same diameter-two description.
Adding any nonedge creates a triangle, so every colored pair is red and the
blue graph has no edges. It still has 20 vertices, hence its largest clique is
a singleton:

\[
\omega(B(G))=1 < 2=\frac{w}{4}.
\]

This disproves #889 under its own #822 color definition.

## Reproduce

The verifier uses only the Python standard library and exact integer/rational
arithmetic. It constructs the graph independently from the blob description,
computes all distances, colors every nonedge according to #822, and calculates
the blue clique number by exhaustive search.

From the repository root, run:

```sh
python3 certificates/wow1-889/verify_certificate.py
python3 certificates/wow1-889/verify_certificate.py --json
python3 -m unittest discover -s certificates/wow1-889 -p 'test_*.py' -v
```

The concise verifier output is:

```text
verified WoW-I #889 counterexample: complement of C5[K4] is connected, 8-regular, triangle-free, diameter 2; w=8, omega(blue)=1 < w/4=2
```

The test suite contains three regression tests and completes without external
packages. The `--json` form emits deterministic machine-readable evidence,
including the complete 20-entry list of odd-distance counts.

## Source and sanity audit

- Source: S. Fajtlowicz, *Written on the Wall*, July 2004 version. The #889
  wording and the #822 red/blue definition were checked against the surviving
  scan (page 213 for #889), not inferred from a damaged inequality.
- Repository provenance and the normalized OCR records are in
  [`../../corpora/ACQUISITION.md`](../../corpora/ACQUISITION.md) and
  [`../../corpora/graffiti_wow.json`](../../corpora/graffiti_wow.json).
- The mandatory database-sanity gate found no violation among the seven
  connected regular triangle-free graph-atlas graphs through order seven
  (including `K1`), nor on the named Petersen, `K3,3`, cube, and Heawood
  calibration graphs.
- Independent checks agree: the executable certificate uses explicit
  all-pairs distances and exhaustive clique search, while the quotient/blow-up
  proof above derives the same values structurally.
- Targeted searches by conjecture number and wording found no earlier
  refutation. The result should remain labeled a gate-surviving, provisionally
  novel candidate until its eventual publication review.

The full 208-entry lane audit is
[`../../results/expansion/wow1_part2.md`](../../results/expansion/wow1_part2.md).
