# Prospective WOWII 133 distance-three fold contract

Frozen: **2026-08-13 UTC**, before constructing or evaluating any folded graph.

## Phase-zero source and status gate

- Upstream repository: `google-deepmind/formal-conjectures`.
- Refreshed upstream commit: `d16e05aded22b8c467a0a27c14b2311f53185006`
  (fetched directly on 2026-08-13 UTC).
- Source: `FormalConjectures/WrittenOnTheWallII/GraphConjecture133.lean`.
- Source blob: `9a8dca984e87efc2fb1ffd68f5d4185e4645a8e8`.
- Declaration: `WrittenOnTheWallII.GraphConjecture133.conjecture133`.
- Current category: `@[category research open, AMS 5]`.
- Source URL:
  `https://github.com/google-deepmind/formal-conjectures/blob/d16e05aded22b8c467a0a27c14b2311f53185006/FormalConjectures/WrittenOnTheWallII/GraphConjecture133.lean`.
- Reading class: `UNAMBIGUOUS` for the current Lean declaration. The target is
  the literal formalized reading, including the non-induced four-cycle test,
  natural radius, maximum induced-path **order**, and floor of average local
  neighborhood independence.

For a connected graph `G`, define

```text
hasC4(G) = G contains a not-necessarily-induced 4-cycle
cC4(G) = 0 if hasC4(G), otherwise 1
R133(G) = path(G) - radius(G) - floor(l(G))^cC4(G).
```

The declaration holds exactly when `R133(G) >= 0`.

Live duplicate/status searches were completed before this freeze. Exact
GitHub issue and open-PR searches for `"Conjecture 133"` in
`google-deepmind/formal-conjectures` returned no resolution item. The broader
PR search returned only merged source-addition PR #3820 and merged definition
fix PR #4282. Web searches for `"Written on the Wall II" "Conjecture 133"`,
`WOWII 133 graph conjecture radius induced path`, and the exact formula found
the live open declaration and general induced-path/radius literature, but no
proof, disproof, or prior use of the distance-three fold below.

## Local theorem-domain and operation-history gate

The repository does not prove the universal declaration. It proves the cubic
C4-free specialization and several low-degree/sufficient cases, while the
four-regular graph-level splice remains open in `OVERARCHING_PLAN.md`. Prior
prospective #133 families include subdivisions/attachments, named cages,
covers, switches, Petersen splices, and Heawood edge contractions. None
identifies a nonadjacent distance-three vertex pair. The frozen output is not
known in advance to lie in a proved class: pair identification can create a
degree-six vertex and can create triangles or four-cycles.

## Equality wall, obstruction, and one frozen transformation

The Heawood graph has the exact C4-free coordinates

```text
(path, radius, floor(l), R133) = (7, 3, 3, 1).
```

The one-unit obstruction is that its 14 distinct vertices leave enough room
for a seven-vertex induced path while cubic triangle-free regularity pins
`floor(l)=3` and its incidence geometry pins `radius=3`.

The **only** prospective transformation is a distance-three vertex fold:
for each unordered Heawood pair `{u,v}` with `dist(u,v)=3`, identify `u` and
`v`, delete loops, and coalesce parallel edges to obtain a simple quotient.
No other distance, deletion, contraction, edge edit, second fold, or parameter
extension may be substituted in this trial.

The directional prediction is frozen term by term:

| coordinate | predicted effect |
|---|---|
| order | decreases exactly from 14 to 13 |
| connectivity | preserved |
| C4-free predicate | unknown; a C4-present output stops in a locally proved domain |
| radius | predicted pinned at 3 on a useful output |
| `floor(l)` | predicted pinned at 3 on a useful output |
| maximum induced-path order | predicted to decrease; the crossing direction requires at most 5 |
| residual | predicted to decrease from 1; a negative value is the desired crossing |

This is an intentionally hard prediction. A safe-side movement is retained as
a failed directional prediction, not retuned.

## Mandatory pre-candidate gates

Before any fold is constructed or any candidate row is written, the evaluator
must:

1. verify this contract digest and the upstream commit/blob/category lock;
2. record the source/status, local theorem-domain, live issue/PR/prior-art, and
   implementation-semantic gates;
3. reproduce a nonnegative literal residual on every connected Graph Atlas
   graph of orders 2 through 7 and on `C5`--`C9`, `P7`, Petersen, `K3,3`,
   `K7`, stars `K1,2`--`K1,7`, `K2,3`, `K2,4`, `K3,4`, and `K4,4`;
4. reproduce the exact Heawood wall `(7,3,3,1)`.

Any failure locks the constructor and ends as `GATE_FAIL`.

## Bounds, exactness, and append-only evidence

- The complete family has at most 91 unordered pairs and retains only exact
  distance-three pairs; every retained labelled output is evaluated.
- Each process is externally capped at 60 seconds; the evaluator also has an
  internal 55-second deadline.
- All invariants are exact: BFS for distances, subset enumeration for local
  independence, pairwise common-neighbor detection for C4, and exhaustive
  endpoint extension for maximum induced-path order.
- The theorem-domain check precedes expensive profiling on every output. A
  C4-present quotient is covered by the local universal theorem
  `sourceConclusion_of_hasC4` and is logged with an exact four-cycle witness,
  labelled structure, and role map, but its remaining invariants are not
  evaluated. If every output is C4-present, the primary outcome is
  `KNOWN_PROOF_DOMAIN` with zero candidate evaluations.
- Every candidate row stores the complete labelled edge list, a role map from
  quotient labels to original Heawood vertices (including the merged pair),
  graph6 only as an abstract checksum, and a SHA-256 digest of the combined
  labelled record.
- Rows append chronologically to
  `results/expansion/heldout_wowii133_distance3_fold_ledger.jsonl`.
- No row is rewritten. A timeout yields `TIMEOUT_BRACKET`, never a hold.

Primary outcomes follow `METHOD.md`: `GATE_FAIL`, `NO_APPLICABLE_CANDIDATES`,
`KNOWN_PROOF_DOMAIN`, `PREDICTION_CONFIRMED`, `HOLD_BOUNDED`,
`TIMEOUT_BRACKET`, or a provisional crossing requiring independent
verification and a fresh novelty audit.

No commit, push, issue, PR, release, or upstream write is authorized.
