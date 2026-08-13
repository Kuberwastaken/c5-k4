# WOWII #133 Petersen 3-edge-splice trial: bounded hold

Date: **2026-08-13 UTC**

## Primary outcome: protocol deviation / known proof domain

This trial is **not prospective evidence**. The independent audit found that
the required pre-freeze theorem-domain audit was wrong: project commit
`c54cfc520b2f6f07d74e29ae4e0ec6217ce8373a`, already on `origin/main` at
02:40 UTC, contains
`lean/GraphConjecture133Specialization.lean::cubicSpecialization`. That theorem
proves the exact source-shaped WOWII #133 conclusion for every connected cubic
graph. The contract was frozen more than eight hours later, and every frozen
splice output is connected and cubic.

The strict classification is therefore `PROTOCOL_DEVIATION` with a
`KNOWN_PROOF_DOMAIN` stop. Candidate evaluations for prospective scorekeeping
are zero. The development rows are preserved only as calibration.

Numerically, all six portal bijections give the same exact coordinate profile:

```text
n = 18, m = 27, cubic, triangle-free, C4-free
path = 11, radius = 4, floor(l) = 3
R133 = 11 - 4 - 3 = 4.
```

The six labelled edge sets form one exact isomorphism class. There are zero
candidate crossings, construction failures, timeouts, or unresolved rows.

## Source and public-upstream status

The theorem/status audit occurred before the contract was frozen. Current
upstream commit `d16e05aded22b8c467a0a27c14b2311f53185006`, source blob
`9a8dca984e87efc2fb1ffd68f5d4185e4645a8e8`, and the live
`@[category research open]` declaration were then replayed by executable
literal git commands. The gate checked the corrected induced-path reading,
floor of average local independence, and the non-induced C4 characteristic.

GitHub search found no proof/disproof issue or PR for WOWII #133. The only
target-specific merged upstream PR is #4282, which corrected the definition
of `path` and the C4 characteristic; it did not settle the conjecture. Those
public-upstream facts were correct. The failure was missing the repository's
own earlier covering theorem, which the contract explicitly required the audit
to detect.

## Database sanity

All 1,014 frozen controls passed under the exact current reading:

- every connected Graph Atlas graph of orders two through seven;
- `C5--C9`, `P7`, Petersen, `K3,3`, and `K7`;
- the frozen stars and complete-bipartite graphs.

There were zero crossings and zero timeouts. Petersen reproduced exact
equality `(path,radius,floor(l))=(5,2,3)`, with the induced path
`[0,1,2,3,8]` replayed edge and chord-wise.

## Frozen move and diagnosis

The trial deleted vertex zero from each of two labelled Petersen copies and
restored cubicity with every perfect matching between their three exposed
neighbor portals. This nonlocal 3-edge splice was distinct from the previous
cover, switch, contraction, subdivision, attachment, deletion, polarity,
chord, and articulation-amalgam lanes.

The intended coordinate separation failed strongly. The cross-cut raises the
radius from two to four, but it also permits an eleven-vertex induced path.
Thus the path coordinate gains six while `radius + floor(l)` gains only two,
moving four units away from the wall. Reordering the portal matching changes
labels but not the abstract graph or invariant profile.

This closes only the frozen two-Petersen splice. It does not justify a theorem
for repeated cubic splices; any repetition would require a new frozen law for
how exact induced-path order scales with the splice tree.

## Independent numerical audit

**PASS, calibration only.** A medium-Sol subagent independently recomputed all
1,014 controls with zero crossings and replayed Petersen equality. It rebuilt
all six labelled splices and checked every graph6/hash, matching, connectedness,
cubicity, triangle/C4 absence, radius, and local independence value.

A distinct descending-subset algorithm rejected all 31,180 subsets of orders
12 through 18 for each graph and then found an induced path of order 11. Thus
all six exact residuals really are four, and the six labelled edge sets form
one isomorphism class. This validates the arithmetic but does not cure the
pre-freeze eligibility failure.

No commit, push, release, issue, pull request, or public action is authorized
by this trial.
