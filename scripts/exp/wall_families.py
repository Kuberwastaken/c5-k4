"""Step 4 of the wall-arm method: the separating-family constructors.

Every constructor takes a *tight member of the wall* and moves one structural
coordinate while preserving the rest of the extremal structure.  These are the
transformations the campaign's own case studies used (clique blow-up of C5 ->
C5[K_m]; non-uniform blow-up of P7 -> the 430a family; line graph of K_n ->
T(n); complement of the carrier -> WoWI 889; path-joined lobes -> WOWII 176).

Each family is a parameterised sequence whose first two members feed the
mandatory G3-lite sign check (METHOD §A3) before the rest is ever built.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wall_arm as W  # noqa: E402


def fam_clique_blowup(base, ms=(1, 2, 3, 4, 5, 6)):
    """G[K_m]: substitute a clique of order m for every vertex."""
    return [("G[K%d]" % m, W.blowup(base, [m] * base.n, clique=True)) for m in ms]


def fam_indep_blowup(base, ms=(1, 2, 3, 4, 5)):
    """G[\\bar K_m]: substitute an independent set of order m for every vertex."""
    return [("G[I%d]" % m, W.blowup(base, [m] * base.n, clique=False)) for m in ms]


def fam_nonuniform_blowup(base, v, ms=(1, 2, 3, 4, 5, 6), clique=True):
    """Grow one blob only -- the non-uniform variant that carried WOWII 430a."""
    out = []
    for m in ms:
        sizes = [1] * base.n
        sizes[v] = m
        out.append(("G[v%d<-K%d]" % (v, m) if clique else "G[v%d<-I%d]" % (v, m),
                    W.blowup(base, sizes, clique=clique)))
    return out


def fam_subdivision(base, ks=(0, 1, 2)):
    return [("sub^%d(G)" % k, W.subdivide(base, k)) for k in ks]


def fam_corona(base, ks=(0, 1, 2)):
    return [("G o %dK1" % k, W.corona(base, k) if k else base) for k in ks]


def fam_join_clique(base, ks=(0, 1, 2, 3)):
    return [("G + K%d" % k, base if k == 0 else W.join(base, W.complete(k)))
            for k in ks]


def fam_join_indep(base, ks=(0, 1, 2, 3)):
    return [("G + I%d" % k, base if k == 0 else
             W.join(base, W.G(k, []))) for k in ks]


def fam_prism(base, ks=(1, 2, 3)):
    return [("G x K%d" % k, base if k == 1 else W.cartesian(base, W.complete(k)))
            for k in ks]


def fam_pendant_path(base, v, ks=(0, 1, 2, 3, 4)):
    """Attach a path of length k at vertex v (the WOWII 176 lobe-stretch move)."""
    out = []
    for k in ks:
        edges = list(base.edges())
        nn = base.n
        prev = v
        for _ in range(k):
            edges.append((prev, nn))
            prev = nn
            nn += 1
        out.append(("G+P%d@%d" % (k, v), W.G(nn, edges)))
    return out


def fam_complement(base):
    c = W.complement(base)
    return [("G", base), ("comp(G)", c)]


def fam_line(base):
    return [("G", base), ("L(G)", W.line_graph(base))]


def fam_scaled_multipartite(parts_fn, ks):
    return [("K(%s)" % ",".join(map(str, parts_fn(k))),
             W.blowup(W.complete(len(parts_fn(k))), parts_fn(k), clique=False))
            for k in ks]


ALL = {
    "clique_blowup": fam_clique_blowup,
    "indep_blowup": fam_indep_blowup,
    "subdivision": fam_subdivision,
    "corona": fam_corona,
    "join_clique": fam_join_clique,
    "join_indep": fam_join_indep,
    "prism": fam_prism,
    "complement": fam_complement,
    "line": fam_line,
}
