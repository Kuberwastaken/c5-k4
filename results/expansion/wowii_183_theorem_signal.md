# WOWII 183: narrowed theorem signal, no counterexample found

Date: **2026-08-12**. This is a negative-search result, not a proof.

Write `r=rad(G^2)` and `q=n-1-Delta(G^2)`. Relative to the proved WOWII 173
baseline, 183 asks for the correction

```text
c = 2(r-1)-q.
```

A geodesic argument gives `q>=2r-3`, hence `c<=1`. The 173 theorem handles
every case with `c<=0`. Therefore 183 can fail only in the extremal case
`q=2r-3`, and then only if the graph also lies on the 173 equality wall. The
remaining needed statement is essentially

```text
q=2r-3  =>  b>=gamma_c+2.
```

The bipartite case follows from the bipartite strengthening recorded with
173; the unresolved core is nonbipartite.

Exact searches found no counterexample: the full 995-graph connected atlas,
roughly 21,000 structured/random graphs, 845 one-vertex extensions of all
atlas 173-equality graphs, and 4,130 targeted two-vertex extensions. In the
critical square profile the minimum observed excess was one, never zero.

This looks theorem-like, but no proof is claimed. Proving it likely requires
understanding equality in DeLaViña--Waller's `L_s+b>=n+1`, which their 2008
paper explicitly leaves open.
