# TxGraffiti product campaign preparation report

Date: 2026-08-14 UTC  
Outcome: **frozen and unexecuted**

An isolated DEVELOPMENT campaign is prepared for TxGraffiti Conjecture 3:

```text
gamma_t(G square H) >= gamma(G direct H)
```

for connected factor graphs of order at least two. No campaign proposal or
target pair was evaluated during preparation, and there is no result claim.

## Audit outcome

- The current primary record is arXiv:2409.19379v2, revised 11 May 2026,
  rather than only the v1 record cited by the local corpus. It still labels
  the exact statement “Conjecture 3 (TxGraffiti)” and calls it table-true with
  many sharp instances.
- The source defines `square` as Cartesian adjacency (one coordinate fixed),
  and `direct`/tensor adjacency as simultaneous edges in both coordinates. It
  defines domination through closed neighborhoods and total domination
  through open neighborhoods.
- Exact-statement/formula/title searches through the freeze date found no
  indexed proof or counterexample. This negative search cannot exclude
  private or unindexed work and is rechecked after any candidate.
- Repository-wide search found only the corpus transcription at
  `corpora/txgraffiti.json:82-89`; no earlier target campaign, certificate, or
  resolution was found. The nearby tracked Graffiti³ campaign is a different
  conjecture about the RGA2 index.

## Frozen implementation

The campaign has exactly three deterministic arms: connected Atlas plus named
factor pairs, fixed-seed generic connected factor pairs, and fixed
leaf/twin/subdivision/parity moves from two equality pairs. Every execution
must pass the pinned source attestation, the 995-graph Atlas fingerprint,
four named product identities, and exact small domination checks before target
rows are permitted.

A candidate carries exact labelled identities for both factors and products,
an explicit size-`k` total dominating set in the Cartesian product, exhaustive
absence proofs for size `k` and size `k-1` dominating sets in the direct
product, and a replaying verifier. The size-`k` absence proof is intentionally
stronger than the requested size-`k-1` check and is what makes the inequality
strict. Search receipts record both the total number of combinations and the
number actually examined, so an early witness is never mislabeled as
exhaustion. The verifier independently reimplements products, domination, and
exhaustive enumeration and also checks applicability and all identity fields.

Workers use a 54-second internal stop under a 60-second external cap. Ledger
rows are canonical, incrementally SHA-256 chained, flushed, and `fsync`ed;
terminal receipts are separately durable and use an explicit closed reason
vocabulary. The GitHub Actions workflow is manual-only, read-only, pinned to a
literal commit and immutable action revisions, and was not dispatched.

## Validation performed

Only constructor/contract tests were run. They verify product distinction,
domination-definition distinction, deterministic arm construction, fixed wall
moves, replayable hash chaining, honest early-witness counts, independent
identity and absence-receipt mutation rejection, and timeout/reason constants.
All eight tests passed. The freeze verifier confirms all seven hashed campaign
inputs. Neither validation enumerates an arm.

No tracked file, README, branch, commit, issue, PR, release, or public action
was created by this preparation.
