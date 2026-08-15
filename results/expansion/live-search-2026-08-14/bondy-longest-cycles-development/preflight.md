# Bondy longest-cycles DEVELOPMENT preflight

**Audit date:** 2026-08-14 UTC

**Disposition:** `GO_FOR_FREEZE`, not evaluated

**Evidence class:** contaminated `DEVELOPMENT`, not held out

**Selected target:** `Arxiv.«2606.03696».bondy_conjecture`

This is a read-only source, status, resolution-shape, and construction
preflight for the next counterexample-discovery rotation after the completed
A109908/A109909 bounded zero and the A103151 defer. It does not freeze a
manifest, evaluate a target instance, claim a bounded result, or authorize a
workflow, candidate, release, issue, or pull request.

Written on the Wall I is not represented in
`google-deepmind/formal-conjectures`. It was not treated as part of the
DeepMind corpus and supplied no target to this selection.

## Current source and identity lock

The final live recheck resolved
[`google-deepmind/formal-conjectures@5a5af706fa5bef3f09606554d393c9170d2b27e8`](https://github.com/google-deepmind/formal-conjectures/commit/5a5af706fa5bef3f09606554d393c9170d2b27e8)
as `main`, with tree
`0ef534e06d27e22e68e4cfd5081f2a5e28ebe73a`.

The exact target is at
`FormalConjectures/Arxiv/2606.03696/BondyLongestCycles.lean:57-64`:

```lean
@[category research open, AMS 5]
theorem bondy_conjecture :
    answer(sorry) ↔ ∀ (k : ℕ), 1 ≤ k → ∀ (V : Type) [Fintype V] [DecidableEq V]
      (G : SimpleGraph V) [DecidableRel G.Adj], IsKConnected G k →
      ((Fintype.card V : ℝ) + k * (k - 1)) / (k + 1) ≤ G.minDegree →
      ∀ (a : V) (C : G.Walk a a), C.IsCycle → C.length = G.circumference →
      ∀ (u v : offWalk C) (P : (G.induce (offWalk C)).Walk u v), P.IsPath →
        P.support.length + 1 ≤ k := by
  sorry
```

Identity pins:

- target-file Git blob SHA-1:
  `c4c5cb1983936860d5a4a7208b3f04bd201290d4`;
- target-file SHA-256:
  `562fbbb0ec47041a61017bb85ec0c7e9aa6fc98cf132be3022268a7dc60e9004`;
- connectivity-support blob SHA-1:
  `b0ca5f605fd601c24ef43ab5a0bdaa8b5050e926`;
- main commit introducing the module:
  `8781428a922a53914450550218bf14be703d8d69`;
- merged statement PR:
  [#4879](https://github.com/google-deepmind/formal-conjectures/pull/4879),
  merged at `2026-08-14T20:25:50Z`;
- closed ingestion issue:
  [#4858](https://github.com/google-deepmind/formal-conjectures/issues/4858).

Exact-name, exact-path, paper-ID, and title searches over open and closed
issues and pull requests found only issue #4858 and PR #4879. The final open-PR
changed-file audit found no open pull request touching the target file. A
public repository search for a Bondy-longest-cycle counterexample repository
returned no result. These negative searches are not a proof that private or
unindexed work does not exist and must be repeated immediately before a
future dispatch.

## Primary source and theorem boundaries

The governing current source is Jie Ma, Bo Ning, and Ziyuan Zhao,
[*Longest cycles and Dirac-type results in highly connected graphs*](https://arxiv.org/abs/2606.03696v1),
arXiv:2606.03696v1. The downloaded PDF had SHA-256
`56213cd6384cc2111864d67150c41e1426608c59b1b009c6752acab9be3487fb`.
It was classified as a 19-page text-based PDF with no pages requiring OCR and
no encoding warning.

The paper states the following boundaries explicitly:

- the cases `k = 1, 2, 3` are proved;
- the cases `k >= 4` remain open;
- Zhang proved the conjecture for claw-free graphs;
- Ma--Ning--Zhao prove the conjecture for
  `n >= 5*k^2 + 7*k`;
- the 1980 Bondy source used a stronger Ore-type formulation, while the paper
  and the Lean module use the minimum-degree specialization.

Therefore the first open finite slice is `k = 4`, and the paper's theorem
restricts any counterexample in that slice to

```text
5 <= n < 5*4^2 + 7*4 = 108.
```

Search results also found older partial results, degree-sum variants, and work
around the related Jung conjecture. None claimed a proof or counterexample to
the exact minimum-degree statement for every finite graph. The primary 2026
paper remains the status authority for this preflight.

## Answer-wrapper caveat and exact resolution shape

The Lean declaration is not a bare universal theorem. It is

```text
answer(sorry) <-> RHS.
```

A finite graph cannot literally falsify that opaque biconditional without
first fixing the hidden answer. A finite witness instead proves `not RHS` and
thereby resolves the intended question as `False`. The source-faithful formal
resolution would replace the placeholder by `answer(False)` and prove the
resulting biconditional from the witness.

Accordingly, any future crossing must be described as an **intended-question
finite disproof** or answer correction, not as a direct falsification of the
opaque current theorem.

For one explicit finite graph `G` and integer `k`, the certificate must prove:

1. `1 <= k` and `IsKConnected G k`;
2. the exact real-valued minimum-degree premise;
3. `C.IsCycle` for an explicit closed walk `C`;
4. `C.length = G.circumference`, including a global longest-cycle upper
   certificate;
5. `P.IsPath` in `G.induce (offWalk C)` for an explicit path `P`; and
6. `P.support.length + 1 > k`.

This is finite and replayable. Failure merely to find a long cycle or short
off-cycle path is not a disproof.

## The source sharp family and the minus-one wall

For integers `t >= k >= 1`, let

```text
S(k,t) = K_k join ((k+1) disjoint copies of K_t).
```

Write `n = k + (k+1)t`. A peripheral vertex has degree `k+t-1`, so

```text
(k+1)*delta(S(k,t)) - n - k(k-1)
  = (k+1)(k+t-1) - (k+(k+1)t) - k(k-1)
  = -1.
```

Equivalently, the source sharp family misses the rounded minimum-degree
premise by exactly one degree. The obstruction is also exact. Removing the
universal `K_k` leaves `k+1` clique components, while a cycle can traverse at
most `k` peripheral path-segments through the `k` separator vertices. Every
longest cycle therefore leaves one `K_t`, which contains a path on `t >= k`
vertices and would violate the conclusion if the degree wall could be
crossed.

This supplies all four required ingredients before search:

- a nontrivial finite carrier;
- a one-rounded-step premise wall;
- a named obstruction identity, separator traversal capacity;
- and a direction for separating degree from path capacity.

## Join/path-cover reduction

Let `H` be a finite peripheral graph on `h` vertices and set

```text
G = K_k join H.
```

Provided the peripheral vertices determine the minimum degree,

```text
delta(G) = k + delta(H),
```

and the degree premise is equivalent to

```text
delta(H) >= ceil((h-k)/(k+1)).
```

A cycle in `G` meets `H` in at most `k` pairwise vertex-disjoint paths:
between successive peripheral segments it must use a distinct vertex of the
`K_k` separator. Conversely, a spanning cover of `H` by at most `k`
vertex-disjoint paths can be stitched through distinct clique vertices into a
Hamilton cycle of `G`; unused clique vertices can be inserted consecutively
because `K_k` is complete.

Define `pcov_k(H)` to be the maximum number of vertices of `H` coverable by at
most `k` vertex-disjoint paths, allowing singleton paths. Then

```text
circumference(K_k join H) = k + pcov_k(H).
```

This is the separating invariant. A particularly compact candidate shape has
a designated induced path `Q` on `k` vertices such that:

```text
pcov_k(H) = h-k,
H-Q has a spanning cover by at most k paths.
```

The explicit cover of `H-Q` stitches to a cycle of length `h`; the exact upper
bound on `pcov_k(H)` proves that cycle is longest; and its complement contains
the designated forbidden path `Q`.

## Separating grammar

The first frozen search should use `k=4`, `t=4`, hence `h=20` and `n=24`.
Label peripheral vertices `(i,j)` with `i in Z/5Z` naming the source clique
and `j in {0,1,2,3}` naming its port.

The construction grammar starts at `5 K_4` and performs a balanced port
rewiring:

1. in each source block, delete one of its three perfect matchings;
2. add a loopless cross-block 2-factor on the 20 labelled ports, represented
   by a fixed quotient multigraph and fixed port permutations;
3. retain only rows in which every peripheral vertex has degree exactly four.

Thus every retained `H` raises the rounded source wall while changing the
separator-side path geometry:

```text
delta(H)=4,
delta(K_4 join H)=8,
ceil((24+4*3)/5)=8.
```

Before execution, a separate immutable manifest must freeze:

- the complete ordered quotient-multigraph catalogue;
- the three within-block matching choices and their order;
- the allowed port permutations and canonical orientation;
- the lexicographic row limit;
- labelled-isomorphism and ordinary-isomorphism rejection;
- the MILP/DP encodings and solver versions; and
- the exact digest of every constructor and verifier.

No quotient, permutation, edit, or row limit may be added after a residual is
seen. This grammar is a deliberately small structural test, not a claim to
enumerate all graphs with `n<108`.

## Theorem shadows that must be subtracted first

### Monotone edge addition is neutral

Adding even one edge between two of the `k+1` peripheral cliques joins their
two Hamilton paths. The resulting peripheral graph has a spanning cover by
at most `k` paths, so its join with `K_k` is Hamiltonian. Any degree lift that
only adds cross-clique edges and retains every original clique edge stays in
this neutral domain.

Therefore the naive one-edge, matching-only, or other monotone-addition lift
is `KNOWN_PROOF_DOMAIN` for this construction and must not receive target
evaluation. The balanced add/delete rewiring is essential, not cosmetic.

### Claw-free outputs are proved

The primary source records Zhang's proof for claw-free graphs. Every retained
constructor output must therefore exhibit an explicit induced `K_1,3` before
the target evaluator runs. A claw-free output is `KNOWN_PROOF_DOMAIN`, not a
hold or prospective row.

The large-graph theorem also forbids any `k=4` row with `n>=108`; the first
grammar stays at `n=24`.

## Target-free constructor gates

These gates run before circumference, off-cycle paths, or `pcov_4` are
evaluated:

1. **source lock:** re-read current `main`, the target blob, all open PR
   changed-file lists, exact-name issue/PR searches, and the primary-source
   hash;
2. **label integrity:** round-trip the complete labelled edge list and role
   map, reject loops, duplicates, missing ports, and digest drift;
3. **grammar integrity:** replay the declared deletions and additions from the
   source seed and verify that no undeclared edge changed;
4. **order and theorem boundary:** verify `k=4`, `n=24`, and `n<108`;
5. **degree wall:** independently compute every degree, verify
   `delta(H)=4`, `delta(G)=8`, and the exact rounded threshold equality;
6. **connectivity premise:** prove `G` is 4-connected both from the universal
   `K_4` join argument and by deletion of every vertex set of size below four;
7. **proof-domain subtraction:** serialize an induced-claw witness and reject
   claw-free rows;
8. **neutral-family subtraction:** reject monotone supergraphs of `5K_4` and
   any other row covered by the spanning-path-cover lemma above; and
9. **deduplication:** reject the source seed, duplicate labelled rows, and
   isomorphic repeats under the frozen canonicalizer.

A gate failure is `GATE_FAIL` or `KNOWN_PROOF_DOMAIN`. It is never a target
hold. No target residual is called during these tests.

## Exact capped search shape

The future executable contract should contain one externally capped process:

```text
timeout --signal=TERM --kill-after=1s 60s <frozen-runner>
```

Internal timing and terminal discipline:

| window | permitted work |
|---:|---|
| `0-8s` | source/status/hash gate and exact replay of the known `S(4,4)` minus-one control |
| `8-18s` | constructor-only generation, target-free gates, and canonical deduplication |
| `18-50s` | exact target evaluation of surviving rows in frozen order; maximize `pcov_4(H)` and construct the corresponding cycle |
| `50-55s` | for the first apparent hit only, independent path-cover/cycle replay using a separately written encoder |
| `55-59s` | fsync, hash-chain finalization, process audit, and terminal record |
| `60s` | external hard stop; no result written after the cap is admissible |

The discovery evaluator may use a binary path-cover MILP with a per-row cap
bounded by the remaining process time. A candidate must then be replayed by an
exact subset/path dynamic program that does not import the discovery helper.
Every solver child receives its own shorter process-group cap.

Terminal meanings:

- `CANDIDATE_FOUND`: one row has passed both exact encodings and all
  certificate checks; stop immediately;
- `DOMAIN_EXHAUSTED`: every row in the frozen grammar completed;
- `CAP_PREFIX`: the process finalized before the internal deadline without
  exhausting the frozen rows;
- `NO_APPLICABLE_CANDIDATES`: every generated row failed a premise or
  theorem-domain gate;
- `NO_TARGET_RAISING_CANDIDATES`: applicable nonduplicate rows existed, but
  none retained the preregistered path-cover pressure needed to reach the
  target evaluator;
- `GATE_FAIL`: any source, constructor, independent-replay, digest, or process
  audit failed.

No timeout prefix is a bounded zero. No post-result increase of `t`, edit
radius, quotient catalogue, port permutations, row count, or solver semantics
belongs to this trial.

## Candidate certificate

An apparent hit is not accepted without all of the following:

- `k`, the complete labelled edge lists of `H` and `G`, and the exact
  separator/block/port role map;
- graph6 only as an additional abstract-graph checksum;
- exact order, degree, rounded-wall, and 4-connectivity witnesses;
- an explicit induced-claw witness excluding the proved domain;
- a designated four-vertex path `Q` in `H`;
- an explicit cover of `H-Q` by at most four vertex-disjoint paths;
- the stitched cycle `C` in `K_4 join H` and direct cycle replay;
- an exact global certificate that no four-path packing covers more than
  `|H|-4` vertices, independently replayed from the full DP state table or an
  equivalently checkable upper-bound proof;
- the induced off-cycle path `P=Q` in the same labelled coordinates and the
  literal check `P.support.length+1>4`;
- discovery and independent-verifier outputs, versions, timings, exit codes,
  digests, and process-tree audit; and
- a fresh same-day source, open/closed PR/issue, standalone-repository, and
  literature duplicate search.

Only after this artifact exists can a later lane attempt a no-`sorry` Lean
certificate or any release preflight. This document authorizes neither.

## Contamination classification

This target is fresh relative to the completed local corpus sweeps. It merged
at `2026-08-14T20:25:50Z`, after the repository's `19:15Z` upstream-delta
audit. Before this scout, exact local searches found no occurrence of
`bondy_conjecture`, `BondyLongestCycles`, `2606.03696`, or OpenConjecture ID
`4126`, and no target instance, constructor output, proof, release, or public
claim existed in this project.

The present preflight itself exposes the target, wall identity, and proposed
operation. Every future run is therefore explicitly **contaminated
DEVELOPMENT evidence** and cannot enter a held-out success-rate denominator.
This does not weaken the mathematical novelty gates for a candidate; it only
classifies the method evidence honestly.

## Ranked alternatives and selection

| rank | target | disposition | reason |
|---:|---|---|---|
| 1 | Bondy longest cycles, `Arxiv.«2606.03696».bondy_conjecture` | **`GO_FOR_FREEZE`** | Fresh current-main graph declaration; finite intended-question disproof shape; exact minus-one sharp family; identifiable separator/path-cover separation; first open slice is finite below 108. |
| 2 | OEIS A103151 | `DEFER` | It remains the best direct finite arithmetic reserve, but the committed preflight correctly finds no sharp least-escape wall, a large certificate, and historical computation through `10^9`. No new evidence justifies overriding that defer. |
| 3 | Barker sequences | `PRIOR_RANGE_STRICT_STOP` | A counterexample would be finite, but odd lengths above 13 are theorem-closed and even lengths `4<n<=4*10^33` are already excluded. A 60-second catalogue search cannot reach novel territory without a new theorem-derived reduction. |

A109908/A109909 remain a completed bounded-zero stop. Previously evaluated,
preempted, released, theorem-closed, or public-PR-claimed targets remain
subtracted. Bondy is the only `GO` in this rotation.

No target was evaluated, no workflow was dispatched, and no public or release
action was taken in preparing this preflight.
