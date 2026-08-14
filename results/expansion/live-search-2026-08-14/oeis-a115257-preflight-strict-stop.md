# OEIS A115257 preflight: strict stop before evaluation

**Disposition:** `STRICT_STOP_BEFORE_EVALUATION` as a held-out or
invariant-wall-navigation trial. At most, retain the target for a separately
authorized generic finite-algebra development baseline.

**Audit date:** 2026-08-14 UTC.

This report is a Phase-0 methodological and status preflight. It does not
freeze or authorize a search. **No target evaluation was run as part of this
preflight, no result is claimed, and no release or upstream action is
authorized.** Written on the Wall I is outside this audit and was neither used
nor inspected.

## Exact target and immutable identities

At audit time, `google-deepmind/formal-conjectures` `main` resolved to:

- commit `942fb149e782a56c2719c543ab58e093f733acb4`;
- commit URL:
  <https://github.com/google-deepmind/formal-conjectures/commit/942fb149e782a56c2719c543ab58e093f733acb4>;
- declaration path: `FormalConjectures/OEIS/115257.lean`;
- declaration Git blob SHA-1:
  `f65f9b8f5cfa8bf3726e9a22b53b57498eed488e`;
- declaration SHA-256:
  `571f1deeb4caa4980f5760b8a7eeea7927853e9b320c255e3b1e5ca5aae17473`;
- benchmark statement-header SHA-256:
  `db7a94cad91b3db020dd86b3067bf8fdfa81a3090f4afb8fe5231a96376b812c`;
- immutable blob URL:
  <https://github.com/google-deepmind/formal-conjectures/blob/942fb149e782a56c2719c543ab58e093f733acb4/FormalConjectures/OEIS/115257.lean>;
- immutable raw URL:
  <https://raw.githubusercontent.com/google-deepmind/formal-conjectures/942fb149e782a56c2719c543ab58e093f733acb4/FormalConjectures/OEIS/115257.lean>.

The declaration remained `@[category research open, AMS 11]`. Define over
`Q[X]`

```text
P_n(X) = sum_{k=0}^n binom(2k,k)^2 X^k,
Q_n(X) = sum_{k=0}^n (binom(2k,k)^2/(k+1)) X^k.
```

The exact statement is

```text
forall n : Nat, 1 <= n -> Irreducible(P_n) and Irreducible(Q_n).
```

The source is [OEIS A115257](https://oeis.org/A115257), whose current page
still displays Zhi-Wei Sun's March 23, 2013 conjecture in the same form. The
source b-file is
<https://oeis.org/A115257/b115257.txt>; the retrieved file contains 201
ordered rows from `n=0` through `n=200` and has SHA-256
`666eeb314527f257913ac2a9499ae1d8b8449fdfa2babd0c9a1809a59cb91c14`.
The b-file records the partial sums `P_n(1)`; it is not evidence for either
irreducibility claim. OEIS's page-level `approved` status is sequence metadata,
not a declaration that the conjecture is solved.

The local protocol used for this decision was `METHOD.md` with SHA-256
`c41cfc7b43f3da3ad6a55525a71b8ac2a6d1a56299efd19d056155fd868d0322`.

## Literal counterexample certificate shape

The declaration does pass the finite-certificate-shape gate. Its literal
negation is one integer `n >= 1` and an exact proof that at least one of `P_n`
or `Q_n` is reducible over `Q`.

A replayable certificate should contain:

1. `n` and the selected branch, `P` or `Q`;
2. two explicit primitive integer polynomials of positive degree;
3. their nonunit witnesses, including degrees and constant terms;
4. a complete coefficient-by-coefficient convolution proving that their
   product is the selected polynomial; and
5. an independent reconstruction of every central-binomial coefficient.

Both target polynomials have constant coefficient one, and the coefficients of
`Q_n` are integers. Gauss's lemma therefore permits a primitive integral
factorization certificate. A Lean disproof could expand the exact product,
prove both factors are nonunits, infer reducibility of the product, and then
select the corresponding failed conjunct.

A modular factorization is not by itself a disproof: reducibility modulo a
prime does not imply reducibility over `Q`. Any crossing would require an exact
rational or integral factorization. Conversely, an irreducible modular
reduction can certify a bounded hold for that one polynomial when its leading
coefficient remains nonzero modulo the chosen prime.

## Current status and duplicate audit

The dated preflight found:

- zero GitHub issues or pull requests containing `A115257` in
  `google-deepmind/formal-conjectures`, including open and closed records;
- zero records from the broader exact `115257` query in that repository;
- no local Lean theorem, result, tag, release, or commit claiming a proof or
  disproof of the exact conjecture;
- no proof or refutation in exact-identifier, exact-formula, and exact-phrase
  web searches; the matching mathematical records were the OEIS source and
  its formalization.

This is a cheap duplicate/status audit, not an exhaustive mathematical
literature review. It supports only the statement that the declaration is
currently upstream-open and no obvious duplicate resolution was located. A
future candidate would require a fresh, broader novelty audit before any
public claim.

## Contamination and exposure

This target cannot supply held-out evidence. It was already explicitly
inspected in this repository at commit `77b3ed9` in
`wave2-oeis-boundary.md`, which evaluated the `n=1` linear boundary. It also
appears in the committed benchmark registries.

The v1.4 contamination inventory, SHA-256
`6ddaa087fe195a7e924d22d81115488c38164beedd5a9d2859e3426eba6c5fb0`,
classifies cluster
`fc-module:FormalConjectures/OEIS/115257` as:

```text
exposure_status: EXPOSED
exposure_basis: SEMANTIC_OR_UNKNOWN_IDENTITY_EVIDENCE
identity_sha256: 9860961d7f830dea9599ac02919d7cdabfee3f04719ff753f760a41d5c39eec3
evidence_total: 10
evidence_sha256: 7b98599687489f9b50c9eaba46e1dafe83f509ff5945ac558d4bf37cb9b8e0b7
```

Calling a later run "held-out-style" would not repair that exposure. It may
only be labeled developmental.

## Why this is not an invariant-wall method trial

Although a finite counterexample would resolve the declaration, the available
search coordinates are only the original index `n`, the branch `P/Q`, and a
possible factor degree. The preflight found no signed residual, equality or
near-equality wall, theorem baseline to subtract, obstruction identity, graph
transformation, or prospectively predicted separating direction.

Splitting successive values of `n` among catalogue, generic, and
wall-navigation workers would change scheduling rather than mathematical
geometry. It would be ordinary exact polynomial factorization mislabeled as
the method. The conjecture is also a human-authored OEIS contribution rather
than a machine-fitted graph-invariant inequality. It can be a generic
finite-algebra comparator under a separate contract, but it cannot count as a
replication of invariant-wall navigation or as held-out evidence.

If a later development-only contract deliberately supersedes this stop, it
must freeze a complete ascending prefix, evaluate both branches for every
index, cap every polynomial factorization subprocess at 60 seconds, and fail
closed on timeouts. A smallest-index claim is forbidden unless both branches
at every smaller positive index completed. Its database gate must reconstruct
the coefficients independently, check the excluded `n=0` unit boundary,
verify both linear polynomials at `n=1`, match every available `P_n(1)` against
the 201-row b-file, and cross-check fixed low-index factorization fixtures with
two independent engines.

## Quarantined scratch diagnostic

During the read-only preflight, before this classification was finalized, an
ad hoc SymPy factorization loop examined increasing indices under one outer
60-second timeout. It reported both branches irreducible through `n=79` and
reported `P_80` irreducible before the outer timeout ended.

This computation had no frozen manifest, source-bound gate, independent
verifier, per-polynomial timeout record, terminal hash chain, or complete
prefix through both branches at `n=80`. It is therefore **explicitly excluded
from the evidence ledger**. It is not a bounded hold, does not update the
conjecture's status, and must not be cited as a result. A future authorized
lane must start from its own frozen contract rather than inheriting these
scratch observations.

## Terminal record

- Frozen search lane: **no**.
- Target evaluation under a protocol: **not run**.
- Mathematical result: **none**.
- Counterexample or proof: **none claimed**.
- Release: **not authorized and not created**.
- Upstream issue or pull request: **not authorized and not created**.
- Written on the Wall I: **excluded; not inspected or used**.
- Recommended disposition: **strict stop as a held-out/method trial; optional
  generic finite-algebra development baseline only under a new explicit
  contract**.
