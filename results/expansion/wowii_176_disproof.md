# WOWII 176: counterexamples from two triangles joined by a path

Date: **2026-08-12**. Verdict: **DISPROVED**, source-faithful and apparently
unrecorded after the database gate, independent recomputation, and targeted
novelty search.

The live WOWII entry, still marked open, states

```text
L_s(G)+b(G) >= n+dist_min(M^2),
```

where `M^2` is the maximum-degree vertex set of `G^2`. Definition 19 explicitly
defines `dist_min(M)` using `dist_G`, so the source-faithful reading selects the
set in the square but measures its distance back in `G`.

Let `D_L` be two disjoint triangles whose distinguished vertices are joined by
a path of `L` edges. For every `L>=5`:

```text
n=L+5, b=L+3, gamma_c=L+1, L_s=4,
M(G^2)={p_1,p_(L-1)}, dist_G(p_1,p_(L-1))=L-2.
```

Hence the conjecture asserts `L+7 >= 2L+3`, false for every `L>=5`.
Even the alternative all-in-`G^2` reading fails for every `L>=7`, because the
distance becomes `ceil((L-2)/2)`. Thus `D_7` is an ambiguity-free witness; it
is NetworkX's `barbell_graph(3,6)`, graph6 `KxCGGC@?G?_B`, with
`L_s+b=14<17` under the published reading and `<15` under the alternative.

The exact verifier checks both readings on all 995 connected atlas graphs of
orders 2--7, then recomputes every invariant by subset enumeration for
`D_5,...,D_12`. Independent spanning-tree enumeration and bitmask routines
agreed. An additional eight-vertex witness (`GRQAcW`) shows order 8 is minimal
for the published reading. Exact-phrase, conjecture-number, GitHub, and current
formal-conjectures searches found no prior resolution; the claim remains
deliberately phrased **apparently unrecorded**, not absolute priority.

Reproduce with [`verify_wowii_176.py`](../../scripts/verify_wowii_176.py).
