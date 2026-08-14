# Fernandes Conjecture 1: public-prior-art strict stop

**Audit time:** 2026-08-14 UTC  
**Declaration:** `Arxiv.«2605.12342».conjecture_1`  
**Disposition:** `PRIOR_ART_STRICT_STOP`  
**Evaluation performed:** none

This is a source, status, and prior-art audit. It does not evaluate any
unresolved pair `(m,n)`, freeze a computational search, claim a result, or
authorize a release or upstream action.

## Decisive result

Do **not** open a Fernandes search lane. A public, exact-statement, no-`sorry`
Lean proof already exists, and
[google-deepmind/formal-conjectures PR #4868](https://github.com/google-deepmind/formal-conjectures/pull/4868)
is already open to mark the declaration solved. The external proof covers
every pair admitted by the formal theorem, rather than only a finite grid.
Consequently there is no admissible small pair left for an independent
non-2-generation search under the project's duplicate-work gate.

The upstream `main` file still literally says `@[category research open]` and
ends in `sorry`, because PR #4868 has not yet merged. That does not make the
target eligible: an open resolving PR with a public proof is a strict stop.

## Current Formal Conjectures identity

Two live reads resolved `google-deepmind/formal-conjectures` `main` to:

- commit `7eb70784eab1a3c6f4c3d99f8920b970cd7f68c4`;
- tree `98d5a3b3c3fe79873d5d420446e89e7430c54425`;
- commit time `2026-08-14T17:53:28Z`;
- file `FormalConjectures/Arxiv/2605.12342/Conjecture1.lean`;
- Git blob `f73b53887c73ead0785e12ee7a0ad8685ec57b41`;
- file SHA-256
  `801f72780b61b37f5c589842cff6a341fbfcf5af0fcee8833f30f2e38ef48b6d`.

The blob and file SHA-256 are unchanged from the earlier local rotation audit.
The declaration is:

```lean
theorem conjecture_1 {m n : ℕ} (hm2 : 2 ≤ m) (hn2 : 2 ≤ n) (hmn : n ≤ m)
    (h_except : (m, n) ∉ ({(2, 2), (3, 3), (4, 3), (4, 4)} : Set (ℕ × ℕ))) :
    ∃ g₁ g₂ : gammaSubgroup m n, Subgroup.closure {g₁, g₂} = ⊤
```

The formal conclusion is 2-generation, meaning rank at most two. Fernandes'
paper observes that every case other than `(2,2)` has rank at least two; since
`(2,2)` is excluded by the declaration, this matches the paper's exact-rank-two
claim on the formal domain.

## Paper-level coverage before the new proof

The authoritative source is Vítor H. Fernandes,
[*Groups of permutations that are even on maximal proper subsets, and related monoids*](https://arxiv.org/abs/2605.12342),
arXiv:2605.12342v1, submitted 2026-05-12. The checked PDF has 18
text-based pages, no pages requiring OCR, and no encoding warning.

The paper itself supplies the following partial coverage.

1. Proposition 3 gives three generators for every `Γ_(m⊕n)`.
2. Write `q(r)=r` for odd `r` and `q(r)=r-1` for even `r`. Corollary 4
   proves rank two whenever `gcd(q(m),q(n))=1`, using the displayed generators.
3. GAP calculations establish rank three for the three genuine exceptions
   `(3,3)`, `(4,3)`, and `(4,4)`.
4. The paper explicitly reports rank-two calculations for `(5,5)`, `(6,6)`,
   `(7,7)`, `(8,8)`, `(9,3)`, and `(9,4)`, followed by “etc.”
5. Theorem 6 also proves two-generation for a related family `Γ_N`; through
   the paper's odd-`N` identification this includes `(3,2)` and consecutive
   pairs `(k+1,k)` for `k≥4`. Its even-`N` statement concerns the larger
   group containing the parity-preserving product component and must not be
   misread as a theorem about every diagonal pair.

On only the named theorems and explicitly printed examples, every admissible
pair through `m≤8` is covered. `(9,9)` is the first pair not directly supplied
by those displayed items. Because the paper says “etc.”, the source does not
support claiming that `(9,9)` was uncomputed; it supports only saying it was
not explicitly enumerated. This historical distinction is now moot for target
selection because the public Lean proof below covers all admissible pairs.

## Resolving PR #4868

Live GitHub inspection found:

- title: `feat(Arxiv): mark Fernandes conjecture 1 as solved`;
- URL: <https://github.com/google-deepmind/formal-conjectures/pull/4868>;
- opened `2026-08-11T03:18:32Z` by `KitaKen1`;
- state: open, non-draft;
- head commit `9df981b69d1a25aade8ac2ac2e659760713f9105`;
- base-at-opening commit `8adf5b7d199d83d7c69d2f89d0e7327362ead98a`;
- GitHub currently reports the PR mergeable, but `blocked` because review is
  required;
- review decision: `REVIEW_REQUIRED`; no review has yet been submitted;
- the Lean project build, test scripts, copyright check, security scan,
  change scan, labeler, and CLA check all succeeded; optional/deployment jobs
  were skipped as designed.

The PR changes only the category metadata: `research open` becomes
`research solved`, with a pinned `formal_proof using lean4` link. It does not
replace the repository's `sorry` body, consistent with Formal Conjectures'
external-proof metadata convention.

The earlier issue
[#4815](https://github.com/google-deepmind/formal-conjectures/issues/4815)
and merged PR #4836 only introduced the conjecture. PR #4868 is the later
resolving item that controls the current eligibility decision.

## External Lean proof identity and exact-statement check

PR #4868 pins
[`KitaKen1/fernandes-conjecture-1-lean@c9360c5`](https://github.com/KitaKen1/fernandes-conjecture-1-lean/tree/c9360c5608ed2bb3bb5670a68d683cd5a83089d6):

- commit `c9360c5608ed2bb3bb5670a68d683cd5a83089d6`;
- tree `615f1f90021c106dda0ab5a0905af9977800caed`;
- commit time `2026-08-11T02:58:42Z`;
- current external-repository `main` still resolves to that exact commit.

Relevant files at that pin are:

| file | SHA-256 |
|---|---|
| `lean/FernandesConjecture/Proof.lean` | `96f439f6cf5db1201acf6946a5e6eb38bcff97d7bb11e30f18aeb83e9ec6b314` |
| `lean/FernandesConjecture/FormalConjecturesWrapper.lean` | `02c602ea194b6bfe59e65c9df9af64aac4d3db739fde1267251a449811fc98b3` |
| `lean/FernandesConjectureAudit.lean` | `5f214b3dd4e75e410589d1945adee7fb9afbed2e39359bcd574ec86e25513c56` |

The wrapper repeats the Formal Conjectures proposition with the same binder
order, bounds, ordering hypothesis, exception set, group, and closure
conclusion. The audit defines one explicit `Conjecture1Statement` and asks Lean
to type both the FC declaration and the proved declaration as that proposition.
This is stronger than a prose assertion that the statements are similar.

The repository reports no `sorry`, `admit`, `native_decide`, or `bv_decide` in
the proof. Its final `#print axioms` reports only `propext`,
`Classical.choice`, and `Quot.sound`, with no `sorryAx`. PR #4868's upstream
project build succeeded against the linked artifact. This audit read the proof
and CI record but deliberately did not launch another build or evaluate a
target pair.

## Mathematical coverage of the public proof

The construction is universal, not a ledger of checked orders.

- For each `r≥2`, it defines an odd transposition `a_r` and an even
  permutation `b_r`: the full rotation when `r` is odd and a
  parity-corrected rotation when `r` is even. The pair generates `S_r`.
- For unequal degrees it takes
  `Ineq = closure {(a_m,a_n),(b_m,b_n)}`. Both projections are surjective.
  Explicit powers and commutators put a three-cycle in a Goursat kernel;
  normality then puts the corresponding alternating group in that kernel,
  forcing `Ineq = gammaSubgroup m n`.
- The unequal-degree proof splits all parity and low-degree cases, including
  `(3,2)`, `(4,2)`, even second degree `2` or `3`, and the same-parity gap.
  Its sole unequal exception is exactly `(4,3)`, already excluded by the FC
  hypothesis.
- For equal degrees the exclusions force `r≥5`. It takes
  `Ieq = closure {(c_r,a_r),(b_r,b_r)}`, where `c_r=a_r b_r`, and again uses
  a concrete three-cycle in a Goursat kernel to prove
  `Ieq = gammaSubgroup r r`.
- The final theorem separates `m=n` from `n<m`, discharges the complete case
  split, packages the ambient generators as subtype elements, and proves the
  exact FC closure equality.

Thus `(9,9)`, `(10,3)`, `(10,4)`, `(10,10)`, and every other admissible pair
that could have looked attractive after subtracting the paper's named cases
are already within the theorem. There is no residual finite grid and no
legitimate maximal-subgroup or orbit-reduced non-2-generation certificate to
seek: such a certificate would contradict the public universal construction.

The three source exceptions also are not fallback targets. They are outside
the conjecture's domain, already computed in the paper, and their corresponding
Formal Conjectures variants are marked solved.

## Bounded-freeze decision

The best freeze is an empty one:

```text
target = Arxiv.2605.12342.conjecture_1
status = PRIOR_ART_STRICT_STOP
public_resolving_pr = google-deepmind/formal-conjectures#4868
public_proof_commit = c9360c5608ed2bb3bb5670a68d683cd5a83089d6
pair_grid = empty
evaluation_budget = 0 seconds
release = forbidden
```

If PR #4868 is withdrawn because its proof is found invalid, eligibility must
be re-audited from scratch. Even in that contingency, no target pair should be
evaluated until the failure is identified precisely and a nonoverlapping
contract is frozen. Until then, spending a 60-second cap on any admissible pair
would duplicate public solved work.

## Correction to the local rotation report

`next-rotation-after-equation677.md` says that issue #4815 and merged PR #4836
only introduced the statement and that “no later resolving item was found.”
That sentence is stale and false under a fresh live audit: PR #4868 opened on
2026-08-11, three days before the 2026-08-14 rotation report, and links the
full proof described above.

The runner-up ranking must therefore be retired as
`PRIOR_ART_STRICT_STOP`. It must not be converted into a freeze, CI run,
candidate, release, issue, or PR by this project.
