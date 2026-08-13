# WOWII #133 decision-first path-suppression trial

Date: 2026-08-13 UTC

Frozen addendum SHA-256:
`9fff7eee1ec53f6266ec6fd57b7275aa093d72862284f90dba2b535c3d8d1489`

## Verdict

`HOLD_BOUNDED` — the complete frozen stream contained 76 distinct applicable
C4-free candidates.  Every candidate has a replayable induced path of order

```text
radius + floor(average local neighborhood independence).
```

There were no decision timeouts, exact timeouts, or crossings.  Consequently
the exact-maximum fallback was never invoked and no source/status/novelty
audit or public action was triggered.

## Sanity and artifact gates

The decision oracle and the existing exact maximum-path evaluator agreed on
all 1,014 predeclared controls.  Every exact residual was nonnegative:

```text
controls = 1014, disagreements = 0, timeouts = 0.
```

An independent replay audit decoded every retained graph6 record, recomputed
the target and C4 status, and checked every ordered witness edge and every
possible chord.  It passed all 76 discovery rows.  The largest search used 17
endpoint-extension states.

The append-only ledger also preserves an earlier failed artifact audit.  That
audit exposed a coordinate-serialization defect: vertex-deletion candidates
were evaluated correctly, but their witnesses retained sparse pre-deletion
labels while graph6 used dense labels.  The evaluator was changed to normalize
the graph before all invariant work, the 1,014-row gate and full discovery
stream were rerun, and the final replay audit passed 76/76.  No failed row is
silently discarded.

## Frozen family outcomes

| Family | Candidates | Order range | Target range | Maximum decision states |
|---|---:|---:|---:|---:|
| orthogonal polarity bases | 3 | 13--57 | 4--6 | 6 |
| polarity vertex deletions | 38 | 11--56 | 4--6 | 6 |
| witness-blocking cycle closures | 23 | 8--30 | 6--17 | 17 |
| dense common-hub amalgams | 6 | 19--49 | 4--5 | 5 |
| dense chain amalgams | 6 | 19--49 | 4--6 | 6 |
| **Total** | **76** | **8--57** | **4--17** | **17** |

The three polarity bases were rejected immediately:

| Graph | `(n,m)` | `radius` | `floor(l)` | target | decision states |
|---|---:|---:|---:|---:|---:|
| polarity `q=3` | `(13,24)` | 2 | 2 | 4 | 4 |
| polarity `q=5` | `(31,90)` | 2 | 3 | 5 | 5 |
| polarity `q=7` | `(57,224)` | 2 | 4 | 6 | 6 |

Deleting one or two signature-representative vertices never changed those
target values enough to obstruct a witness.  All 38 deletions were certified
in at most six states.

For dense block amalgams, a common hub kept radius at two.  A four-block chain
raised radius only to three; target orders were five or six and were found in
the same number of states.  Amalgamation therefore increased metric depth too
slowly to suppress paths.

## The chord-closure obstruction

The most informative negative result came from the explicitly
counterexample-directed family.  For each cycle `C8` through `C30`, the
deterministic first target path was found.  The closure algorithm then tried
every nonconsecutive pair on that witness and required the added edge to:

1. destroy that witness;
2. preserve C4-freeness; and
3. not lower `radius + floor(l)`.

No cycle admitted even a first blocker.  Thus all 23 retained rows are the
round-zero cycles.  In this geometry, the useful chords either create a C4 or
reduce the target; path destruction and target preservation are not
independent coordinates.

## Reusable method data

The decision-first protocol is a clear improvement over exact maximization.
The previous alternate-geometry lane spent seconds trying to establish exact
maximum path orders on large graphs which a target witness rejected in 6--9
states.  Here all 76 candidates were decided in 4--17 states, including the
57-vertex polarity graph.  Future #133 searches should retain this oracle.

The construction evidence is negative but sharper:

- dense diameter-two C4-free polarity graphs make `floor(l)` grow, yet the
  required path remains extremely easy to realize;
- deleting a bounded number of vertices does not separate the target from
  path existence;
- vertex-amalgamating dense blocks raises radius and path capacity together;
- adding witness-destroying chords to a cycle cannot simultaneously preserve
  both C4-freeness and the target, even at the first move in this frozen range.

A next construction would need a genuinely nonlocal path-blocking mechanism
that does not operate by a single chord, sparse deletion, or articulation
amalgamation.  The repeated immediate witnesses also add evidence that #133's
wall may be theorem-driven rather than a nearby counterexample wall.

## Artifacts

- Addendum:
  `results/expansion/prospective_wowii133_decision_first_addendum.md`
- Append-only 2,190-line ledger:
  `results/expansion/prospective_wowii133_decision_first_ledger.jsonl`
- Evaluator and replay audit:
  `scripts/prospective_wowii133_decision_first.py`

No commit, push, release, issue, PR, or other public action was made.
