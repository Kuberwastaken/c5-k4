# Equation 677 -> Equation 255 column-reduction theory audit

**Audit verdict:** `THEORY_VALID__PRIOR_ART_STRICT_STOP`  
**Audited at:** 2026-08-14T19:14:58Z  
**Local base:** `c5-k4@1251a69e99c06f9582db063ddf909e3c73d8cb53`
on branch `eq677-column-v2`  
**Target evaluation:** none; in particular, this audit did not construct or
solve an order-eight instance  
**Publication status:** do not publish, release, or claim this reduction or an
order-eight exclusion as new

## Immutable sources

| source | immutable revision | object / raw SHA-256 |
|---|---|---|
| `google-deepmind/formal-conjectures`, `FormalConjectures/Other/EquationalTheories_677_255.lean` | commit `6c0950bec7743f5098c0196c6aee7b22c1ec8005`; tree `5af0d2a3a319ee2458f8cd061db7c49aeba1b35e` | Git blob `f5641e3da7b811dca952f00b6fddc3ed3700d0a4`; raw SHA-256 `ce01a0a4c994dfd82b8f14295be7f6c97c8be6e59f5367015c299f95a750f6d5` |
| `teorth/equational_theories`, blueprint `blueprint/src/chapter/677.tex` | commit `54edcda2f320cef0a241f8109fa164f901a69b87`; tree `7f253a76d3abd23fcaeb37cc42ad0337efddd9eb` | Git blob `dbae39254c9d445f0aa27cd6839b545a6c822ecb`; raw SHA-256 `e25f4c8e3ecfe454ad303782b68af69e41eb0572f780c5a7203cc8210b4b152e` |
| same repository, `equational_theories/ManuallyProved/Equation677.lean` | same commit | Git blob `103013d4a798719b0479ed98a07cbd7ac4fd34f8`; raw SHA-256 `dc1050b709dfe6c5ce33b9c2afa264dd70041308356df4045739061942ebbf3f` |
| same repository, `commentary/Equation677.md` | same commit | Git blob `87cea738acf484d0affefd85cd3fdb078a90cad4`; raw SHA-256 `50e8789c98d777309e5737a0d4284579e499a291cf62f816297cfd05dc7e4603` |
| local reference encoder, `scripts/prospective_equation677_255_sat.py` | local base above | raw SHA-256 `636bc6c53fb9e4d99a98f8d9419e5b5baa58da691cb6bbf55d3359aa82299066` |

The Formal Conjectures source defines

```text
Equation255(G) := forall x, x = ((x diamond x) diamond x) diamond x
Equation677(G) := forall x y, x = y diamond (x diamond ((y diamond x) diamond y)).
```

The teorth blueprint's Lemma `677-basic(ii)` proves, for a finite
Equation-677 magma, that

```text
y diamond x = x  ->  y = (x diamond x) diamond x.
```

It consequently states that Equation 255 holds at `x` if and only if the
equation `y diamond x = x` has a solution. The merged Lean source independently
kernel-checks the nontrivial direction as `eq255_from_fixer_exists`; the easy
reverse direction is immediate by choosing the displayed triple-product as
`y`. That source entered teorth through merged PR
[#1434](https://github.com/teorth/equational_theories/pull/1434).

## Step-by-step equivalence at the distinguished element

Fix a finite magma `M` satisfying Equation 677. Write

```text
P(x) := x = ((x diamond x) diamond x) diamond x
F(x) := exists y, y diamond x = x.
```

Then:

1. Assume `P(x)` and set `y := (x diamond x) diamond x`. The right side of
   `P(x)` is exactly `y diamond x`, so symmetry of equality gives
   `y diamond x = x`. Hence `F(x)`. This direction needs neither finiteness nor
   Equation 677.
2. Assume `F(x)` and choose `y` with `y diamond x = x`.
3. The finite Equation-677 fixer lemma gives
   `y = (x diamond x) diamond x`.
4. Substitute this value of `y` into `y diamond x = x`. This yields
   `((x diamond x) diamond x) diamond x = x`.
5. Symmetry of equality is `P(x)`. Therefore `P(x) <-> F(x)`.

At the distinguished label `x=0`, this specializes to

```text
0 = ((0 diamond 0) diamond 0) diamond 0
  <-> exists y, y diamond 0 = 0.
```

Negating both sides over the explicit finite SAT domain gives

```text
not P(0)
  <-> not (exists y, y diamond 0 = 0)
  <-> forall y, y diamond 0 != 0.
```

Thus failure of Equation 255 at `0` is encoded exactly by the `n` unit
clauses

```text
-v(y, 0, 0)        for y = 0, ..., n-1.
```

This is a theorem-derived equivalent only in the presence of the finite
Equation-677 assumptions. Used without those assumptions, these units would
be an invalid strengthening of the original Equation-255 negation.

## Operand-orientation audit against the local SAT encoder

The local encoder defines

```python
variable(n, i, j, k) = 1 + (i*n + j)*n + k
```

with the documented meaning `i diamond j = k`. Therefore:

- `v(y,0,0)` means `y diamond 0 = 0`;
- the theorem-derived units belong to the **right-operand-zero column**;
- `v(0,y,0)` would instead mean `0 diamond y = 0` and is the wrong
  orientation.

The existing Equation-677 clause loop is also correctly oriented. For each
`x,y,a,b,c`, its clause

```text
-v(y,x,a)  -v(a,y,b)  -v(x,b,c)  +v(y,c,x)
```

means

```text
a = y diamond x
b = (y diamond x) diamond y
c = x diamond ((y diamond x) diamond y)
------------------------------------------
y diamond c = x,
```

which is precisely
`x = y diamond (x diamond ((y diamond x) diamond y))`.

The older direct negation in that encoder emits, for every `a,b`,

```text
-v(0,0,a)  -v(a,0,b)  -v(b,0,0).
```

Under the exact-one table constraints, the unique actual `a=0 diamond 0` and
`b=a diamond 0` make these clauses say that `b diamond 0` is not `0`, exactly
the literal negation of Equation 255 at `0`. Hence the old cubic-chain clauses
and the new units have the same models once finite Equation 677 is enforced.
The units are a propagation improvement, not a new mathematical restriction.

The row-permutation constraint in the local encoder fixes the left operand and
varies the right operand. This also has the correct orientation: Equation 677
exhibits every `x` as `y diamond z` for fixed `y`, so every left translation
`z |-> y diamond z` is surjective and therefore bijective on a finite set.

## Current status and prior-art gate

At the pinned Formal Conjectures head, both
`Finite.Equation677_not_implies_Equation255` and
`Finite.Equation677_implies_Equation255` remain marked `research open` with
`sorry`. Merged PR
[#2401](https://github.com/google-deepmind/formal-conjectures/pull/2401)
settled the opposite finite direction (`255` does not imply `677`), not this
one. The other closed automated submissions found by exact declaration/name
search likewise concern the infinite non-implication and/or that opposite
finite direction; none resolves the finite `677 -> 255` implication.

However, open teorth issue
[#1464](https://github.com/teorth/equational_theories/issues/1464), created
2026-07-22T22:46:20Z and last updated 2026-07-22T23:41:45Z, publicly claims:

- the same fixer-column consequence: if Equation 255 fails at relabelled `0`,
  then `f(y)=y diamond 0` avoids `0`;
- a Lean-verified structural orbit lemma on an unmerged branch;
- 45 exhaustive order-ten orbit cases, all UNSAT, with Glucose DRAT proofs
  reportedly checked by `drat-trim`;
- consequently, subject to review, no finite counterexample below order 11;
- two order-eleven near-models and one certified **local** Hamming-ball
  exclusion, explicitly not an order-eleven exclusion.

The issue is still open. Its author explicitly requests review of the SAT
encoding, orbit coverage, and symmetry argument. There are no maintainer
review comments on the issue as of the audit timestamp, and its 963-MB
compressed certificate archive is described by hash but not linked from a
durable public host. Accordingly, this audit does **not** promote the claimed
order-ten result to a reviewed theorem. For reproducibility, canonicalized
GitHub API snapshots at the audit timestamp had SHA-256
`a334b929f37e364b5a44846b7d9c9fd8bcc45a749782d5cc89c5cc3f0c56cb43`
for the issue metadata/body and
`5e0c2c311fe732189e3dcf1d5fd8918ca33ade745e809e0f080305f31cdc0ce1`
for its two comments.

Nevertheless, the public claim and its explicit use of the same column
reduction trigger the campaign's novelty gate. A proposed order-eight CI
search is strictly subsumed by the claimed order-ten exclusion and cannot
produce a novel bounded result. Classification:

```text
PRIOR_ART_STRICT_STOP
```

No order-eight solver run, GitHub workflow, candidate evaluation, release,
README discovery entry, issue, or pull request should be launched from this
lane. The full finite implication remains mathematically open, but advancing it
would require genuinely new structure beyond the public column/orbit method or
a review/reproduction contribution explicitly framed as such—not a novelty
claim.

## Caveats

- The equivalence proved above is exact and is supported by a merged no-sorry
  teorth Lean development, but the proposed unit-clause encoder itself was not
  run in this audit.
- Formal Conjectures' `research open` label establishes formal target status;
  it does not erase external prior art on bounded computations.
- Issue #1464 is a public claimant's report, not a merged or maintainer-reviewed
  result. Its status is sufficient for a novelty stop but insufficient for an
  unconditional mathematical claim that order ten has been excluded.
- A finite countermodel, if one exists, may be relabelled so that a failing
  element is `0`; this justifies the distinguished label but does not justify
  any additional symmetry assumptions without separate proof.
