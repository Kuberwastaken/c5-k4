# Erdős 23 Andrásfai-successor trial: protocol correction and audited frontier

Date: **2026-08-13 UTC**

## Initial outcome — reclassified

The canonical successors of the exact `C5` equality quotient moved strictly
into the safe side of the current DeepMind Erdős 23 bound:

| quotient | lifted order | quotient edges | quotient max cut | lifted bipartization | bound | slack |
|---|---:|---:|---:|---:|---:|---:|
| `A_3` | 40 | 12 | 10 | 50 | 64 | 14 |
| `A_4` | 55 | 22 | 18 | 100 | 121 | 21 |
| `A_5` | 70 | 35 | 29 | 150 | 196 | 46 |
| `A_6` | 85 | 51 | 42 | 225 | 289 | 64 |

The numerical rows are exact, but the strict primary classification of the
original trial is **`PROTOCOL_DEVIATION`**, for two independent reasons:

1. Its source gate was tied to a hard-coded upstream commit and blob instead
   of independently establishing the live source/database state before
   development. The later literal source replay does not retroactively cure
   that defect.
2. Its mandatory theorem-domain audit was performed only after evaluation.
   arXiv:2606.28041 reports a computer-assisted proof for every Erdős
   parameter `n <= 40`, including the tested parameters `8,11,14,17`.

The four rows remain useful post-deviation calibration, but they are excluded
from prospective evidence and count as zero candidate evaluations for strict
scorekeeping. The earlier `HOLD_BOUNDED` and
`INCONCLUSIVE_PROTOCOL_DEVIATION / PRIOR_ART_STOP` ledger events remain as
history and are superseded as the original trial's primary classification.

## Corrected frontier frozen before evaluation

After that stop, a v2 contract was appended before any new computation. It
keeps exactly the same preselected Andrásfai-successor mechanism but evaluates
only the first integer outside the reported finite theorem domain:

```text
A_14[bar K_5]: quotient order 41, graph order 205, Erdős parameter 41.
```

The single quotient maximum cut was solved by a binary MILP at zero MIP gap
under a 55-second internal and 60-second process cap. No larger `k`, alternate
solver menu, or adaptive family was authorized.

The corrected row is:

| quotient | graph order | parameter | quotient max cut | lifted bipartization | bound | slack |
|---|---:|---:|---:|---:|---:|---:|
| `A_14` | 205 | 41 | 238 | 1,225 | 1,681 | 456 |

The exact numerical outcome is positive slack `456`, so the v2 classification
is **`HOLD_BOUNDED`**, with zero candidates. Unlike the original low-parameter
rows, it is outside the reported `n <= 40` finite theorem domain. This
separately frozen v2 result is scoreable after the independent audit described
below. It does not alter or cure the original v1 `PROTOCOL_DEVIATION`.

## Source and database gate record

The later replay checked `FormalConjectures/ErdosProblems/23.lean` at upstream
commit `d16e05aded22b8c467a0a27c14b2311f53185006`, blob
`346d29667313a32382bbf42b87588d53bb208400`. `Erdos23.erdos_23` remains
tagged `research open`. It asks whether every triangle-free graph on `5*n`
vertices has edge bipartization number at most `n^2`.

That replay documents the snapshot used for v2 review; it does not repair the
original v1 gate, whose hard-coded source expectation is itself one of the two
recorded protocol defects.

The gate checked all six connected triangle-free order-five Atlas graphs,
with no value above one. Balanced `C5` independent blow-ups of bag sizes one
through five reproduced equality exactly. Petersen has bipartization number
three against allowance four, and every divisible-order complete-bipartite
control has value zero. Every cut and post-deletion bipartite graph was
replayed directly.

## Frozen transformation and exact reduction

The only development move was

```text
A_2 = C5  ->  A_k, k in {3,4,5,6},
```

followed by a uniform independent bag of size five. This is a global quotient
change, not an extension of the completed one-edge-surgery or voltage-lift
menus. Direct triangle enumeration confirms all four lifted graphs are
triangle-free.

For a uniform independent blow-up, a maximum cut may assign each false-twin
bag wholly to one side, because the objective is linear in that bag's split
once all other bags are fixed. Hence both maximum-cut edges and minimum
deleted edges scale by `5^2=25`. Exhaustive quotient enumeration fixed one
vertex side and checked at most `2^16` assignments. The emitted quotient cut
was lifted to all 40--85 vertices and independently replayed edge by edge.

The quotient bipartization values observed are `2,4,6,9`, matching
`floor(k^2/4)` on the four frozen parameters. This is a useful possible
all-family formula, but this trial does not promote four values to a theorem.
It should be investigated symbolically before any broader operation-class
closure is claimed.

## Independent audit

**PASS for the separately frozen parameter-41 v2 row.** An independent,
different binary max-cut MILP implementation finished in 6.7 seconds at zero
MIP gap and reproduced quotient maximum cut `238`, quotient bipartization
`49`, lifted bipartization `1,225`, bound `1,681`, and slack `456`. The literal
source gate replay passed. The theorem-domain audit confirmed that
arXiv:2606.28041 proves the reported range through `n=40` and identifies
`n=41` as the threshold where that finite-range result no longer applies.

Accordingly, v2 is finally classified as scoreable `HOLD_BOUNDED`; original
v1 remains `PROTOCOL_DEVIATION`. No commit, push, release, issue, pull request,
or public action is authorized by this trial.
