# Prior-art assessment: "the union of two edge-disjoint C4-factors is Hamiltonian"

Date: 2026-08-15. Adversarial search; default hypothesis = already known.

## The statement under test

> Let F0, F1 be edge-disjoint spanning 2-factors of H, all of whose components are 4-cycles,
> with H = F0 ∪ F1. If H is connected, then H is Hamiltonian. Hence every spanning
> supergraph of H is Hamiltonian. (H is 4-regular, n ≡ 0 mod 4.)

---

## VERDICT: (b) — an immediate corollary that any expert would call known.

Borderline (a). It is not (c) and emphatically not (d).

Three independent reasons, in decreasing order of force:

1. **An equivalent statement is explicitly published, with the identical proof.**
   Boyd & Sebő, *Lemma 2* (2017/2021) is the same theorem after contracting a perfect
   matching, and its printed proof is the same scaffold-plus-Kotzig argument, forbidden
   bitransitions and all. See §1.
2. **The core theorem is 57 years old and is the standard tool for exactly this.**
   Kotzig 1968 Theorem 1 is an iff-characterisation; degree 4 is the threshold case
   where it applies with equality. See §2.
3. **The construction has two standard names.** The scaffold transition system is the
   **A-trail** condition, and H is the **medial graph** of the scaffold. Both are textbook
   (Fleischner, *Eulerian Graphs and Related Topics*, Ch. VI). See §3.

The *phrase* "two edge-disjoint C4-factors" appears nowhere in the reachable literature.
That is a vocabulary gap, not a mathematical one. A referee's response would be
"this is Kotzig's theorem applied to the medial graph."

**Canonical citation to use instead of claiming novelty:**

> A. Kotzig, *Moves without forbidden transitions in a graph*,
> Matematický časopis (Slovenská Akadémia Vied) **18** (1968), no. 1, 76–80.
> Theorem 1. Full text: http://dml.cz/dmlcz/136066

and, for the packaged Hamiltonicity form,

> S. Boyd, A. Sebő, *The salesman's improved tours for fundamental classes*,
> IPCO 2017, LNCS 10328; Math. Programming **186** (2021) 289–307.
> Lemma 2 and Theorem 11. arXiv:1705.02385

---

## 1. Strongest prior art — Boyd & Sebő, Lemma 2

Verified firsthand from arXiv:1705.02385 (PDF pulled and converted; §2.1
"Eulerian Trails with Forbidden Bitransitions").

Their statement of Kotzig, verbatim:

> **Theorem 3.** *[19] Let G = (V,E) be a 4-regular connected multigraph with a forbidden
> bitransition for every v ∈ V. Then G has an Eulerian trail not using the forbidden
> bitransition of any node.*
>
> [19] A. Kotzig, Moves without forbidden transitions in a graph, Mat. Casopis Sloven.
> Akad. Vied **18**, 76–80 (1968)

Their definition and lemma, verbatim:

> A *square graph* is defined as a pair (G,M) where G = (V,E) is a cubic 2-edge-connected
> graph, and M is a perfect matching of G such that the edges E \ M form squares.
>
> **Lemma 2.** *A square graph (G,M) has a Hamiltonian cycle containing M.*

Their proof, verbatim (abridged):

> Contracting all squares of G, we obtain a 4-regular connected multigraph G′ = (V′,E′)
> whose edges are precisely M and whose nodes are precisely the squares of G \ M. To each
> contracted square C we associate the forbidden bitransition consisting of the pairs of
> edges of M incident with the diagonally opposite nodes of C in G … By Theorem 3, there
> is an Eulerian trail K of G′ that does not use these forbidden bitransitions. The two
> pairs of consecutive edges in K at each node in G′ can then be completed by a perfect
> matching of the corresponding square in G, forming the desired Hamiltonian cycle.

The abstract even advertises the method:

> "A key role in the proof of this result is played by finding Hamiltonian cycles whose
> existence is equivalent to Kotzig's result on 'compatible Eulerian tours'…"

### Why this *is* the statement under test

The two are interchangeable by splitting/contracting a perfect matching:

- **Ours ⇐ theirs.** Given H connected, 4-regular, edges decomposing into 4-cycles, split
  each vertex x (which lies in exactly two of the 4-cycles, A and B) into x_A — x_B joined
  by a new edge; give x_A the two A-edges and x_B the two B-edges. The result G is cubic,
  M = the split edges is a perfect matching, and E(G) \ M is exactly a C4-factor (the
  4-cycles of H on the split copies). So (G,M) is a square graph; Boyd–Sebő give a
  Hamilton cycle of G containing M; contracting M returns a Hamilton cycle of H.
- **Theirs ⇐ ours.** Contract M in a square graph: G/M is connected 4-regular with its
  edges decomposing into 4-cycles, i.e. an H.

**Precondition checked computationally**: over 120 random connected instances (H on 8–32
vertices), the splitting G was in every case cubic, connected and **bridgeless**, i.e. a
legitimate 2-edge-connected square graph. So the reduction is not obstructed by their
2-edge-connectivity hypothesis. (In any case the direct Kotzig application needs only
connectivity.)

Boyd–Sebő also supply, in their Theorem 11 / Greedy (HAM), a **self-contained proof
avoiding the Kotzig citation** — the "replace each square by one of its two perfect
matchings, at least one choice keeps the graph connected" argument. That is the published
analogue of the trail-splicing argument in the statement's provenance.

## 2. Kotzig 1968 — exact text (verified against the original)

Downloaded and converted the original from DML-CZ. Verbatim, p. 78:

> **Theorem 1.** *Let G be a connected graph, and let its every vertex v_i be of an even
> degree (i.e. let d_i = 2c_i, where c_i is a natural number). Let Q = {Q_1, Q_2, …, Q_n}
> be a given system of decompositions of the sets (E_i, i = 1,2,…,n) into classes of
> edges. A Eulerian line of G, admissible with respect to Q exists if and only if for all
> i ∈ {1,2,…,n} we have: the number of elements of an arbitrary class of Q_i is not
> greater than c_i.*

"Admissible w.r.t. Q" (p. 77) = at every vertex, the two edges of every transition lie in
*different* classes. Kotzig records that the problem was posed by **Nash-Williams at
Tihany, September 1966**.

Notes that matter:

- **No planarity.** Much of the literature quotes the weaker planar statement ("every
  4-regular *plane* graph has an A-trail"), which comes from Kotzig's *other* 1968 paper,
  *Eulerian lines in finite 4-valent graphs and their transformations*, Theory of Graphs
  (Proc. Colloq. Tihany 1966), Academic Press 1968, 219–230. The Mat. časopis Theorem 1 is
  the general one and is the correct citation here — the scaffold carries an arbitrary
  rotation, not a planar one.
- **Degree 4 is the exact threshold.** d_i = 4 ⇒ c_i = 2, so classes of size 2 satisfy the
  condition *with equality*.
- **No conflict with the hard compatibility problems.** Compatible *Euler tours* (Kotzig,
  settled 1968) are easy; compatible *cycle decompositions* (Sabidussi's conjecture,
  Fleischner) are hard. The K5 example that blocks compatible cycle decompositions does
  not block compatible Euler tours.

Modern restatement — Fleischner, Genest & Jackson, *Compatible circuit decompositions of
4-regular graphs*, J. Graph Theory **56** (2007) 167–182 (preprint
https://webspace.maths.qmul.ac.uk/b.jackson/conjSUBMIT.pdf), §1, verbatim:

> "Kotzig [7] showed that if T is a (partial) transition system for an Eulerian graph G,
> then G has an Euler tour which is compatible to T if and only if each (transition)
> vertex of G has degree at least four."

## 3. The construction already has standard names

**A-trails.** An A-trail of a graph with a rotation system is an Euler tour in which
consecutive edges are adjacent in the cyclic order at their shared vertex. At a degree-4
vertex with rotation (e1,e2,e3,e4) this forbids exactly {e1,e3} and {e2,e4} — precisely
the scaffold's transition system. So the middle step of the proof is literally
"every connected 4-regular map has an A-trail", which is how the A-trail literature states
Kotzig's theorem, e.g.:

> "Kotzig proved that if, for each vertex v of a 4-regular graph we select a set B_v of two
> edges incident with v, then there is an Euler tour of G that never has consecutive edges
> from any B_v. In particular, every medial graph has an A-trail."

**Medial graphs.** H *is* the medial graph of the scaffold B: V(Med(B)) = E(B), edges =
corners. Since B is 4-regular every vertex-face of Med(B) is a 4-gon, each edge of Med(B)
lies in one vertex-face and each vertex in exactly two — that is the C4-decomposition. B
bipartite is exactly the condition that these 4-cycles 2-colour into two spanning
C4-factors. So the statement is the special case of:

> *The medial graph of a connected 4-regular graph embedded in any surface is Hamiltonian.*

**Fleischner's book** (*Eulerian Graphs and Related Topics*, Ann. Discrete Math. 45, 1990)
Chapter VI, "Various Types of Eulerian Trails", has sections *Eulerian Trails Avoiding
Certain Transitions*, *Pairwise Compatible Eulerian Trails*, *A-Trails in Plane Graphs*,
***The Duality between A-Trails in Plane Eulerian Graphs and Hamiltonian Cycles in Plane
Cubic Graphs***, ***A-Trails and Hamiltonian Cycles in Eulerian Graphs***. The published
dualities run the *other* way (A-trails encode a hard Hamiltonicity problem — Barnette's
conjecture; cf. Theorem VI.71: "A 2-connected plane cubic bipartite graph has a
hamiltonian cycle if and only if its dual graph has a non-separating A-trail"). Using the
*unconditional* degree-4 case to *produce* a Hamilton cycle is the direction Boyd–Sebő take.

**Gap:** the body text of Chapter VI could not be read (archive.org copy
`euleriangraphsre0001flei` is lending-restricted; `_djvu.txt` and search-inside both 403).
Section VI's "A-Trails and Hamiltonian Cycles in Eulerian Graphs" is the one remaining
place a verbatim collision could sit. This does not change the verdict, since Boyd–Sebő
already settle it.

## 4. Definitely known vs. definitely not found

### Definitely known
- Kotzig 1968 Thm 1: compatible Euler tour exists iff every class ≤ d(v)/2. Iff, general
  even graphs, no planarity.
- Boyd–Sebő Lemma 2 (square graphs) — the equivalent statement, published, same proof.
- Boyd–Sebő Theorem 11 — a delta-matroid strengthening; the Hamilton cycles containing M
  form a delta-matroid, with a greedy algorithm, giving min-cost such cycles in poly time.
- Jackson, *Compatible Euler tours for transition systems in Eulerian graphs*, Discrete
  Math. **66** (1987) 127–131, and *A characterisation of graphs having three pairwise
  compatible Euler tours*, JCTB **53** (1991) 80–92 — direct extensions of Kotzig.
- A-trail existence is NP-complete once 4-regularity is dropped (Bent & Manber, Discrete
  Appl. Math. **18** (1987) 87–94; Andersen & Fleischner, Discrete Appl. Math. **59**
  (1995) 203–214). Sharp confirmation that degree 4 does all the work.
- Kotzig's A-trail/spanning-tree bijection for 4-regular plane graphs.

### Definitely NOT found (searched hard, zero hits)
- Any statement using "C4-factor", "quadrilateral factor", "two edge-disjoint C4-factors",
  "C4-factorization + Hamiltonian", in arXiv metadata + full text (Google `site:arxiv.org`),
  OpenAlex, Semantic Scholar, zbMATH, SearXNG.
- Any Hamiltonicity sufficient condition of the supergraph form ("G contains a spanning
  union of two C4-factors ⇒ G Hamiltonian") in Gould's Hamiltonian surveys (full text of
  *Advances on the Hamiltonian Problem* pulled — no C4/quadrilateral-factor condition).
- Nothing in the design-theory stream. Hamilton–Waterloo / Oberwolfach / resolvable
  4-cycle-system literature (Adams, Billington, Bryant, Danziger, El-Zanati, Fu, Huang,
  Keranen, Özkan, Odabaşı, Traetta, Burgess) studies the same object for different
  properties. Closest: Gionfriddo–Milici et al., arXiv:2003.10032, Thm 2.2 — "the union of
  two parallel classes of C4 is decomposable into two parallel classes of P4 and one
  further class which is a perfect matching." Not Hamiltonicity.
- Citation sweep of Kotzig 1968 (OpenAlex W122054064, **63 citing works**, full list
  retrieved): none states the C4-factor corollary. The bulk is alternating trails in
  edge-coloured graphs, genome rearrangement/DCJ, Chinese postman, forbidden-transition
  complexity. The Hamiltonicity-adjacent ones are Krivelevich–Lee–Sudakov (compatible
  Hamilton cycles in Dirac/random graphs), Jackson 1987/1991, Fleischner–Genest–Jackson
  2007, Dorninger 1972, and **D. L. Powers, *Some Hamiltonian Cayley Graphs*, Ann. Discrete
  Math. 27 ("Cycles in Graphs", Alspach & Godsil eds.) 1985, 129–140** — whose abstract
  ("we use the eulerian or hamiltonian structure of one graph to find a hamiltonian cycle
  in another") is the same transfer idea, applied to *trivalent* Cayley graphs. Full text
  not obtainable (ScienceDirect paywall/403; no OA copy).
- Recent Sabidussi work (arXiv:2607.13225) — cites Kotzig only in passing, no Hamiltonicity.

## 5. Where the C4/C4 case sits — sharpness (own results, verified)

### The general claim is FALSE
The **Meredith graph** (4-regular, 4-connected, 70 vertices, non-Hamiltonian) is by
Petersen's theorem the union of two edge-disjoint 2-factors and is connected. So
"union of two 2-factors ⇒ Hamiltonian" is false outright.

### The C3/C3 case is FALSE — explicit counterexample constructed and verified here
The union of two edge-disjoint **triangle**-factors is exactly `L(X)` for `X` a connected
cubic **bipartite** graph (the two factors are the two bipartition classes' vertex-triangles).
By Harary–Nash-Williams, `L(X)` is Hamiltonian iff `X` has a dominating closed trail; for
cubic `X` a closed trail has all degrees 0 or 2, so this is iff **X has a dominating cycle**.
Cubic graphs without dominating cycles exist, so the C3 analogue must fail. Constructed one:

- `X`: 20 vertices, cubic, bipartite, connected, simple. Three copies of `K(3,3) − e`
  (legs at the two degree-2 vertices `a1`, `b1`); a vertex `u` joined to the three `a1`'s;
  a vertex `w` joined to the three `b1`'s. Any cycle must use `u` and `w`, hence exactly two
  gadgets, leaving the third gadget entirely untouched and its interior edges undominated.
- Verified by exhaustive cycle enumeration: **X has no dominating cycle.**
- `L(X)`: 30 vertices, 4-regular, connected, edge set = 20 triangles splitting into two
  spanning C3-factors of 10 triangles each.
- Verified by exhaustive DFS (2.4M nodes): **L(X) is NOT Hamiltonian.**

So the C4/C4 theorem is *not* an instance of a general "union of two C_k-factors" phenomenon.
(Note: a subagent's random search reported "no C3/C3 counterexample found" — random cubic
bipartite graphs are Hamiltonian, so random search cannot find this. Disregard that report;
the structured counterexample above is verified.)

### Why C4 is the unique cycle length this argument reaches
Kotzig requires the *allowed*-transition relation at each scaffold vertex to be
"different class", i.e. complete multipartite. For a C_k block the allowed pairs form C_k
itself, and the only cycles that are complete multipartite are C3 (= K(1,1,1)) and
C4 (= K(2,2)). C3 gives odd scaffold degree — no Euler tour at all. So **C4 is the only
case**. For C6 the two "opposite/near-opposite" classes are not a partition and Kotzig's
trail-merging swap produces forbidden transitions.

### C6/C6: not implied, no counterexample found
Random search over connected, genuinely edge-disjoint C6/C6 instances (H 4-regular and
simple) found no non-Hamiltonian example, but the Kotzig route provably does not apply.
**Status: open, not known either way.** Do not assert it.

### Structural facts about H worth recording
- For any k, a connected union of two edge-disjoint C_k-factors is 4-edge-connected and
  1-tough, so no cut/toughness obstruction can ever certify non-Hamiltonicity here; any
  counterexample must be of Meredith type.

## 6. True statements stronger than the one under test

All follow from the same argument, and are worth stating in place of the weaker one:

1. **Bipartiteness is unnecessary.** Every connected 4-regular (multi)graph whose edge set
   decomposes into 4-cycles is Hamiltonian. (Each vertex then automatically lies in exactly
   two of them; the scaffold is 4-regular but need not be bipartite.)
2. **The cycle can be taken alternating.** When the two factors are distinguished, the
   scaffold is bipartite, its Euler tour alternates sides, and the resulting Hamilton cycle
   alternates F0- and F1-edges — equivalently it meets every 4-cycle of F0 and of F1 in a
   perfect matching of that 4-cycle. This is the same strengthening Boyd–Sebő state
   ("Hamiltonian cycle containing M").
3. **Delta-matroid / optimisation form.** Via Boyd–Sebő Theorem 11, the Hamilton cycles
   arise as the bases of a delta-matroid, so a min-cost one is computable greedily in
   polynomial time.
4. **Cayley corollary.** Cay(G, {a^±1, b^±1}) with |a| = |b| = 4 is exactly such an H, so
   every connected Cayley graph on a group generated by two elements of order 4 with that
   connection set is Hamiltonian — with a 1968 proof.
5. The supergraph clause is trivial (a Hamilton cycle of a spanning subgraph is one of the
   supergraph) and adds nothing.

## 7. Computational verification of the statement itself

No counterexample in any run:

| scope | result |
|---|---|
| n = 8, exhaustive (F0 fixed WLOG), 34 pairs | 0 non-Hamiltonian |
| n = 12, exhaustive, 14,328 pairs | 0 non-Hamiltonian |
| n = 16, **exhaustive, 21,747,132 pairs** (3,468 disconnected) | 0 non-Hamiltonian |
| n = 20, 24, 200,000 random pairs each | 0 non-Hamiltonian |
| random scaffolds, n = 8–32, ~19,000 connected instances total | 0 non-Hamiltonian |
| exhaustive transition-choice enumeration, 475 4-regular scaffolds | compatible tour always exists |

The statement is true. That was never in doubt; the issue is authorship.

## 8. Bottom line

Do not present this as new. Present it as an observation, cite **Kotzig 1968, Theorem 1**
for the engine and **Boyd & Sebő, Lemma 2** for the fact that the Hamiltonicity packaging
is already in print. The genuinely reportable content is the *sharpness*: the verified
30-vertex C3/C3 counterexample, and the complete-multipartite argument showing C4 is the
unique cycle length for which the Kotzig route exists.
