# Compact audits — read/classified, no development family frozen

Each row: file @ `2411d22e`, what the declaration literally asserts, triage decision, reason.

## EP 108 (`108.lean`) — high-chromatic graphs containing high-girth high-chromatic subgraphs
`∀ r ≥ 4, ∀ k ≥ 2, ∃ f, ∀ G [χG ≥ f], ∃ H ≤ G: girth H ≥ r ∧ χH ≥ k`. Genuine open problem (subgraph,
not induced; K_N contains every small graph as a subgraph so clique obstructions don't refute). Asymptotic
∃ over unbounded f ⇒ not finite-searchable. **AUDIT_CLEAN** (faithful; open).

## EP 141 (`141.lean`) — consecutive primes in arithmetic progression
Main: ∀ k ≥ 3 ∃ k-term AP of consecutive primes; variant k = 11 open. Finite-search flavor but the first
k = 10 examples already sit near record prime-AP territory (≥ 10¹⁸); a bracket to 10⁸ would add nothing.
**STOP_LOW_YIELD_BRACKET** (faithful; open).

## EP 193 (`193.lean`) — lattice S-walks in ℤ³ contain three collinear points
Universal over infinite walks with infinite range; degenerate cases explicitly guarded in the Lean
(range-infinite hypothesis present — checked against the docstring's stated intent). A refutation would be
a periodic walk in ℤ³ avoiding collinear triples — an open problem of substance (Gerver–Ramsey solved ℤ²).
**AUDIT_CLEAN** (faithful; open; not bounded-searchable).

## EP 398 (`398.lean`) — Brocard's problem
`{n | ∃ m, n!+1 = m²} = {4,5,7}`: equality-of-sets form faithfully encodes "no other solutions".
Literature brackets push any further solution beyond n ≥ 10⁹; our budget cannot extend meaningfully.
**STOP_LOW_YIELD_BRACKET** (faithful; open).

## EP 506 (`506.lean`) — minimum number of circles determined by n points
`IsLeast {k | ∃ P : Finset ℝ², ...} answer(sorry)` with n universally quantified — a value placeholder for
the exact optimum function; Elliott's answer known only for n > 393 per the file. Not falsifiable (no
closed-form claim to contradict); exact small-n optima are continuous-geometry search problems outside the
60 s exact-arithmetic cap. **STOP_NOT_FALSIFIABLE**.

## EP 61 / 70 / 74 / 75 — Erdős–Hajnal, continuum Ramsey, EHS82 bipartite distance, ℵ₁-graphs
All four carry deep asymptotic or set-theoretic quantification (∀ᶠ n, cardinal-existentials, Ordinals):
no finite witness can settle or refute any literal reading. Spot-checked faithfulness on each
(EP61's IsErdosHajnalLowerBound matches the induced-free formulation; EP74's edge-distance definitions
carry proved API tests). **GROUP AUDIT_CLEAN** (open/faithful/not-bounded).

## Duplicate surface across this batch
gh issues/PR searches on ids 108, 141, 193, 398, 506, 61, 70, 74, 75 returned no result-bearing artifacts
(beyond upstream's own solved variants recorded inside the files).
