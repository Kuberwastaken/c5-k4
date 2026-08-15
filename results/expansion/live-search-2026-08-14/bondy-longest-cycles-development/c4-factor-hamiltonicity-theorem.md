# C4-factor Hamiltonicity theorem shadow

> **Correction, 2026-08-15 — this result is NOT novel.** A prior-art review
> ([`c4-factor-novelty-prior-art.md`](c4-factor-novelty-prior-art.md)) found an
> equivalent statement already in print, with the same proof: Boyd & Sebő,
> *The salesman's improved tours for fundamental classes*, IPCO 2017 / Math.
> Programming 186 (2021) 289–307, **Lemma 2** (arXiv:1705.02385): "A square
> graph `(G,M)` has a Hamiltonian cycle containing `M`." Their proof contracts
> the squares, takes the diagonally-opposite pairs as forbidden transitions,
> and applies Kotzig — i.e. the scaffold argument below. The two statements
> interconvert by splitting/contracting a perfect matching. Boyd & Sebő also
> give a Kotzig-free proof (their Theorem 11) matching the trail-splicing
> variant below. The correct canonical citations for this fact are Boyd–Sebő
> Lemma 2 and Kotzig 1968 Theorem 1; **nothing here should be published or
> cited as a new theorem.** The material below stands as a correct,
> independently reconstructed proof and as the symbolic stop rule that
> retired this coordinate, which is its actual value to the campaign.

- Classification: `PROVED_THEOREM_SHADOW` (superseded: `KNOWN_RESULT_RECOVERED`)
- Frozen grammar covered: Bondy v3.5 rows `0..95`
- Exact rows replayed: `96 / 96`
- Hamilton cycles replayed: `96 / 96`
- Search standing: this entire balanced `C4/C4` coordinate is retired
- Candidate or release: none

## Theorem

Let `F_0` and `F_1` be edge-disjoint spanning 2-factors whose components are
all four-cycles. If their union `H = F_0 union F_1` is connected, then `H` is
Hamiltonian. Consequently, every supergraph of `H` on the same vertex set is
Hamiltonian as well.

The connected-union hypothesis is essential. It is not enough for an ambient
graph to contain two edge-disjoint `C4`-factors whose own union is
disconnected.

## Proof

Build a bipartite incidence scaffold `B`. Its left vertices are the cycles of
`F_0`, its right vertices are the cycles of `F_1`, and each vertex `x` of `H`
becomes an edge `e_x` joining the two factor cycles that contain `x`. Every
scaffold vertex has degree four. Connectivity of `H` makes `B` connected.

At a scaffold vertex, the corresponding four-cycle in `H` cyclically orders
the four incident scaffold edges. Partition those edges into the two pairs
that are opposite on the four-cycle. Each class has size two, exactly half the
scaffold degree. Kotzig's compatible-Euler theorem therefore gives an Euler
tour of `B` in which every transition uses edges from different classes. Such
a transition is exactly an edge of the local four-cycle in `H`.

If the Euler tour reads

```text
e_(x_1), e_(x_2), ..., e_(x_n),
```

then `x_1, x_2, ..., x_n, x_1` is a cycle in `H`. The Euler tour uses every
scaffold edge exactly once, so this cycle uses every vertex of `H` exactly
once and is Hamiltonian.

There is also a direct proof that removes any citation or multigraph concern.
At each scaffold vertex choose either of the two allowed perfect matchings of
its four incident edges. These local transitions decompose all scaffold edges
into compatible closed trails. Choose a decomposition with the fewest trails.
If two trails remain, connectedness supplies a scaffold vertex used by both;
switching from one allowed local perfect matching to the other splices those
two trails while preserving compatibility. Repeating yields one compatible
Euler tour and hence the Hamilton cycle above.

The primary theorem is Anton Kotzig, "Moves Without Forbidden Transitions in
a Graph," *Matematický časopis* 18(1) (1968), 76--80, MR 0242709,
[DML-CZ 136066](https://dml.cz/handle/10338.dmlcz/136066), Theorem 1 on
pages 78--79. The original text-based PDF was checked directly with no OCR
gaps. Its criterion is precisely that every forbidden partition class at a
vertex have size at most half that vertex's even degree.

## Exact frozen specialization

Every raw v3.5 constructor row has two such factors:

1. deleting one perfect matching from each of the five internal `K4` blocks
   leaves five internal four-cycles;
2. the declared cross factor is another five edge-disjoint four-cycles; and
3. their union is exactly the 4-regular peripheral graph `H`.

For all 96 rows, the factor-incidence scaffold is more specifically
`K_(5,5)` minus a perfect matching. It is simple and connected. The executable
replay in
[`verify_bondy_c4_factor_theorem.py`](../../../../scripts/verify_bondy_c4_factor_theorem.py)
reconstructs every exact row, checks both factors and the scaffold, constructs
a compatible Euler tour, maps it back to `H`, and verifies the resulting
Hamilton cycle edge by edge.

This proves that the v3.5 observation was stronger than traceability:
`pc(H)=1` and `q_4(H)=20` at the empty deletion set because every frozen
peripheral graph is Hamiltonian. Expanding matching choices, quotient
four-cycle orders, port permutations, or scaffold isomorphism types cannot
help while the construction remains a connected union of two `C4`-factors.

## Method consequence

This is a theorem recovery, not a counterexample and not evidence for the
Bondy declaration outside the frozen construction class. It converts an
empirical 96-row zero into a symbolic stop rule. Any honest next coordinate
must destroy the local four-cycle transition system—for example by changing a
factor's cycle-length partition or by degree-balanced asymmetric internal
rewiring—before any target evaluation is justified.
