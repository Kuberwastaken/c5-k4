# Latin Tableau order-15 corner-transfer trial

**Classification:** development, `FINITE_SANITY_ONLY`  
**Upstream:** `google-deepmind/formal-conjectures@7a38c469ec329d0c97c068e03c58834f61628e7e`  
**Exact declaration:** `LatinTableau.SimpleGraph.LatinTableauConjecture`

One finite Young diagram without a CDS coloring would literally refute the
current Lean declaration, so the target passes Method v1.0's certificate-shape
gate. This run does not find such a diagram and makes no truth claim beyond its
frozen block.

## Frozen development contract

- Enumerate exactly all 176 integer partitions of 15.
- For each partition, compute every prefix optimum independently by a
  capacitated bipartite max-flow and the Ferrers corner-minimum formula.
- Seek a proper row/column coloring whose class sizes are the successive
  optimum increments; directly check the returned assignment.
- Apply one deterministic transformation only: delete the bottommost removable
  corner. A transfer is eligible exactly when the parent-minus-child increment
  profile is one standard basis vector; require the deleted corner to receive
  that color.
- Do not retry with another corner or recoloring rule.
- Cap the outer process at 60 seconds and each exact feasibility call at five
  seconds.

The contract was frozen in the agent conversation before evaluation, but it
was not committed or machine-hashed beforehand. Its canonical post-hoc digest
is recorded only as `posthoc_contract_digest`; it is not a preregistration
hash. The trial is development because it follows the known order-at-most-14
run and 168 rows were already inside the source paper's 12-by-12 computation.

## Primary run

- Environment: Python 3.9.25, SciPy 1.13.1/HiGHS, NumPy 2.0.2, NetworkX 3.2.1.
- Runtime: 2.631 seconds under `timeout 60s`.
- Prefix flow/formula disagreements: 0.
- CDS-colorable diagrams: 176/176.
- Eligible bottom-corner transfers: 172/176.
- Successful eligible transfers: 172/172.
- Eligible transfer failures: 0.
- Primary row serialization SHA-256:
  `473606fff5cb72fb419af132dd90957f3524852764c33c1021e8dbdd6918695f`.

The four structurally ineligible transfers are:

- `(7,3,3,1,1)`;
- `(5,5,2,1,1,1)`;
- `(4,4,4,2,1)`;
- `(4,4,4,1,1,1)`.

In each case the profile difference redistributes mass across several colors
rather than deleting one color-class cell, so the deterministic induction move
cannot apply. Each parent nevertheless has an independently certified CDS
coloring.

The eight order-15 shapes outside the reported 12-by-12 box are:

- `(15)`; `(14,1)`; `(13,2)`; `(13,1,1)`;
- `(3,1,1,1,1,1,1,1,1,1,1,1,1)`;
- `(2,2,1,1,1,1,1,1,1,1,1,1,1)`;
- `(2,1,1,1,1,1,1,1,1,1,1,1,1,1)`;
- `(1,1,1,1,1,1,1,1,1,1,1,1,1,1,1)`.

All eight are CDS-colorable in this exact run. This is finite evidence only.

## Independent verification

A second implementation used Edmonds-Karp flow, the same independently derived
corner-minimum formula, and a separate exhaustive MRV/backtracking coloring
solver. It completed in 24.695 seconds under the same 60-second cap and agreed
on all mathematical fields: 176 colorable diagrams, 172 eligible and successful
transfers, the same four ineligible shapes, and the same eight outside-box
shapes. Its canonical sorted-key JSONL is 33,439 bytes with SHA-256
`ff97992bcbd109ec863cd5744d6afe8709cad0c114cda6411694bfd76d6faa68`.
The two row digests are not expected to match because their serialization
schemas differ; no mathematical discrepancy was found.

## Outcome and next wall

Primary outcome: `FINITE_SANITY_ONLY`. No counterexample, issue, PR, release,
or Lean disproof is authorized.

The useful obstruction is precise: bottom-corner deletion usually changes one
profile coordinate, but four shapes redistribute the optimum increments. A
future trial must freeze a different transformation capable of controlling
that redistribution; it may not silently try a different corner on these rows.
