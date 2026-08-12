# Executable certificate: Graph Brain alpha upper bound 081

The author-posted connected-graph conjecture is

`alpha(G) <= 2 diameter(G)/(edge_connectivity(G)-vertex_connectivity(G))`.

For `C5[K_m]`, the four relevant invariants are

`alpha=2`, `diameter=2`, `edge_connectivity=3m-1`, and
`vertex_connectivity=2m`.

Consequently the conjectured right side is `4/(m-1)`.  At the campaign
carrier `C5[K4]`, it asserts `2 <= 4/3`, false by exact margin `2/3`; the same
family refutes it for every `m>=4`.

Run `python3 verify.py`.  The verifier uses only exact integer and rational
arithmetic from Python's standard library.
