# WOWII 186 co-Petersen status audit

**Audit date:** **2026-08-13 UTC**

**Decision:** **READING BUG** — no gate-surviving counterexample
**Candidate:** `complement(Petersen)`, equivalently the triangular graph
`T(5)=L(K5)`

## Bottom line

The `-1 @ 186` entry in the Wave 2 table of
[`results/family_forest.md`](../family_forest.md) is exactly the value obtained
by replacing DeLaViña's set eccentricity `ecc(S)` with the maximum vertex
eccentricity of members of `S` in `G^2`. The same report had already rejected
that reading at its database-sanity gate.

Under the recovered definition of `ecc(S)`, the co-Petersen graph has

```text
L_s+b = 7+4 = 11,
C(G^2) = V,
|N(C(G^2))| = 10,
ecc(C(G^2)) = 0,
R_186 = 11-(10+2*0) = +1.
```

Thus it **satisfies** WOWII 186 with slack one. It is not a candidate for Lean
certification, novelty work, or a release.

## Frozen source and status record

The local source ledger, `data/wowii-conjectures.json`, records entry 186 as:

> If G is a simple connected graph on at least 2 vertices, then
> `L_s(G) + b(G) >= |N(C(G^2))| + 2*ecc(C(G^2))`, where `C(G^2)` is the set
> of center vertices of the second power graph.

It records page marker `O`, note date 2005-08-08, and status `open`. It also
records `in_formal_conjectures: false` and no Lean file. A literal local search
of `/Users/kuber.mehta/Projects/formal-conjectures` found no 186 declaration.
Consequently #186 is not represented in the current DeepMind corpus and is
outside the current programme's formal-conjectures-only publication scope,
independently of the failed candidate.

The page-linked invariant glossary fixes the relevant meanings:

- `N(S)` is the set of vertices adjacent to at least one member of `S`;
- `C(H)` is the set of all minimum-eccentricity vertices of `H`;
- `ecc(S)` is the maximum, over vertices in `V-S`, of distance to `S`;
- `L_s` is maximum spanning-tree leaf count and `b` is maximum induced
  bipartite-subgraph order.

The recovered prose does not explicitly discuss the maximum over an empty
set. The already-gated project convention is `ecc(V)=0`, consistent with set
distance and the Graffiti computations. If one refuses that convention, the
formula is undefined on graphs with `C(G^2)=V`; it still does not yield the
member-eccentricity value used by the apparent crossing.

## Exact witness reconstruction

The independent verifier
[`scripts/verify_wowii_186.py`](../../scripts/verify_wowii_186.py) constructs
the complement directly from NetworkX's Petersen graph. Its stable certificate
in that labelling is:

```text
graph6       IUX|}vh|G
n,m          10,30
degrees      6,6,6,6,6,6,6,6,6,6
diameter     2
G^2          K10 (45 edges)
C(G^2)       all ten vertices
b            4; induced-P4 witness {0,1,2,3}
gamma_c      3; connected dominating witness {0,1,3}
L_s          10-gamma_c = 7
L_s+b        11
```

There is also an explicit seven-leaf spanning tree with edges

```text
03, 31, 02, 14, 15, 06, 07, 08, 09.
```

The optima have short independent structural checks. The co-Petersen graph is
the strongly regular graph with parameters `(10,6,3,4)`, hence has diameter
two. Its independence number is two, so every bipartite induced subgraph has
at most four vertices; the displayed induced `P4` proves `b=4`. An adjacent
pair in the complement is a nonadjacent pair in Petersen. Petersen's
`(10,3,0,1)` parameters give that pair a common Petersen neighbor, which is
undominated by the pair in the complement. No connected dominating pair
exists, while `{0,1,3}` is connected and dominating, so `gamma_c=3` and
`L_s=7`.

## Every relevant reading on the candidate

Here “definition neighborhood” means DeLaViña's union of open neighborhoods,
which may contain vertices of `S` when they are adjacent to another member of
`S`. “External-only” is the non-source alternative `N(S)-S`, included only as
a stress test. The scope columns say whether the outer operation is evaluated
in `G^2` or back in `G`.

| neighborhood | eccentricity | scope | `|N|` | `ecc` | residual |
|---|---|---:|---:|---:|---:|
| definition | set eccentricity | all in `G^2` | 10 | 0 | **+1** |
| definition | set eccentricity | all back in `G` | 10 | 0 | **+1** |
| definition | set eccentricity | either mixed scope | 10 | 0 | **+1** |
| definition | member eccentricity | eccentricity in `G^2` | 10 | 1 | **-1** |
| definition | member eccentricity | eccentricity back in `G` | 10 | 2 | **-3** |
| external-only | set eccentricity | either eccentricity scope | 0 | 0 | +11 |
| external-only | member eccentricity | in `G^2` / in `G` | 0 | 1 / 2 | +9 / +7 |

Therefore every actual **set-eccentricity** interpretation agrees on the
candidate: it holds by one. The only negative rows use member eccentricity,
contrary to the recovered definition.

## Fresh database-sanity gate

The verifier recomputed all quantities independently by subset enumeration on
all 995 connected Graph Atlas graphs of orders two through seven, followed by
38 required named-control rows:

- `C5` through `C9`, `P7`, Petersen, `K3,3`, and `K7`;
- stars `K1,r`, `2<=r<=9`;
- complete bipartite graphs `K(a,b)`, `1<=a<=b<=6`.

Some named rows intentionally repeat isomorphic star/bipartite controls; the
counts below are test rows, not nonisomorphic graph counts. The run took 1.32
seconds under an external 60-second cap.

| reading | Atlas failures | named-row failures | gate verdict |
|---|---:|---:|---|
| definition `N`, set `ecc`, all in `G^2` | 0 | 0 | **PASS** |
| definition `N`, set `ecc`, all back in `G` | 0 | 0 | **PASS** |
| definition `N`, member `ecc` in `G^2`, `N` in `G^2` | 28 | 8 | **REJECT** |
| definition `N`, member `ecc` in `G^2`, `N` in `G` | 27 | 7 | **REJECT** |
| definition `N`, member `ecc` back in `G`, `N` in `G^2` | 632 | 15 | **REJECT** |
| definition `N`, member `ecc` back in `G`, `N` in `G` | 587 | 15 | **REJECT** |

The first rejected reading already fails on `K2` with residual `-1` under the
source convention used throughout the project, and it still fails on 27 other
Atlas graphs if that edge case is omitted. The larger fresh control set
explains why its row count differs from the old
report's shorthand “31 DB graphs”; both computations give the same decisive
classification.

Mixed-scope and external-neighborhood stress readings were also evaluated.
Some pass and some fail the gate, but none makes co-Petersen negative while
retaining set eccentricity. The verifier prints the complete sixteen-reading
table and all gate counts as exact JSON.

## How the contradictory ledger arose

Git commit `2a64adbb` introduced, in the same file:

1. the gate rule rejecting `ecc(C(G^2))` as radius/member eccentricity;
2. the definition-conformant surviving reading with `ecc(V)=0`;
3. the Wave 2 row `co-Petersen ... -1 @ 186`; and
4. immediately below the table, the conclusion “No violations.”

The arithmetic fingerprints the stale value uniquely:

```text
11 - (10 + 2*1) = -1.
```

Commit `93c2887f` later added the correct no-kill summary, “186: min slack 1.”
The release-backlog audit correctly omitted #186. There was no later
mathematical reversal: the Wave 2 cell accidentally retained a value from the
already gate-rejected member-eccentricity parse.

## Local priority and publication consequence

Local git history, tags, releases, Lean files, and the release-backlog audit
contain no #186 claim or formal certificate. The only matching git subject is
an unrelated Written on the Wall **I** entry 186. No Internet novelty search
was performed in this audit, as instructed; the local page ledger is therefore
the limit of the status evidence.

That uncertainty is immaterial here. There is no source-faithful
counterexample to check for priority. The durable disposition is:

```text
READING BUG
co-Petersen satisfies every set-eccentricity reading with residual +1.
Do not formalize, release, or count the -1 Wave 2 cell.
```
