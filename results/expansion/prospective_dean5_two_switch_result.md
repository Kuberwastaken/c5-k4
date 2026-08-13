# Dean `k = 5` two-switch trial: bounded hold and theorem-shadow stop

Date: **2026-08-13 UTC**

## Outcome

The frozen degree-preserving two-switch neighborhood of `C5[K2]` produced no
counterexample to the current DeepMind formalization of Dean's `k = 5` cycle
conjecture.

| depth | raw valid switches | unique labelled graphs | exact isomorphism classes | candidates |
|---:|---:|---:|---:|---:|
| 1 | 130 | 130 | 3 | 0 |
| 2 | 16,300 | 6,951 | 20 | 0 |

All **7,081 depth-indexed evaluation rows** are 5-regular on ten vertices.
Each has both an explicitly replayed 5-cycle and an explicitly replayed
Hamilton 10-cycle. Because the depth-one set is contained in depth two, these
rows represent 6,951 globally distinct labelled graphs (20 isomorphism
classes, including the base). The strict verdict is `HOLD_BOUNDED`; it is not
evidence that the full conjecture is proved.

## Source and database gate

The source gate used `google-deepmind/formal-conjectures` at
`d16e05aded22b8c467a0a27c14b2311f53185006` and source blob
`4a65620a7ff37a6d3f005f6db3705e26d793b3cf`. The declaration
`dean_conjecture.variants.five` remains tagged `research open` and says exactly
that `5 <= G.minDegree` forces a cycle length divisible by five.

The exact sanity gate checked all 995 connected Graph Atlas graphs of orders
two through seven. Five graphs meet `minDegree >= 5`; each has a replayed
5-cycle. The `C5[K2]` control independently reproduced `minDegree = 5`, a
5-cycle, and a 10-cycle. There were no gate failures or alternate readings.

## Stronger explanation: this move is theorem-closed

The complete numerical zero has a simple post-development explanation.
Dirac's theorem says that every simple graph on `n >= 3` vertices with minimum
degree at least `n/2` is Hamiltonian. Here `n = 10` and every degree-preserving
switch keeps `minDegree = 5 = n/2`. Therefore every graph reachable by
**any number** of degree-preserving switches—not only the frozen depth-two
neighborhood—has a 10-cycle, whose length is divisible by five.

This closes the entire fixed-order operation class. A future Dean trial must
leave order ten, not deepen or randomize the same switch search. The useful
coordinate is the density ratio: one needs `minDegree >= 5` but
`minDegree < n/2`, hence at least eleven vertices, before Hamiltonicity stops
being automatic from Dirac's theorem.

## Process-cap recovery

The first development process durably wrote all 7,081 graph rows, then reached
the frozen 60-second operating-system cap during the optional isomorphism
census. The ledger records the interruption. A second capped process verified
that the durable counts matched the frozen enumeration, replayed every stored
cycle and minimum degree from graph6, and completed the exact census using
isomorphism-invariant triangle/WL buckets followed by exact VF2 checks. This
changed no graph, budget, prediction, or search scope.

## Independent audit

**PASS.** A medium-Sol subagent independently completed the source/status and
Atlas gates, reconstructed the switch neighborhood without importing the
development helper, and checked all 7,081 durable graph rows. It decoded every
graph6 string and checked its SHA-256, order, size, full degree sequence, both
cycle witnesses, candidate flag, switch provenance, row indices, and
checkpoints. It independently reproduced the `3` and `20` exact isomorphism
class counts, zero candidates, the cap-recovery accounting, and the Dirac
theorem-shadow application. The audit took 36.3 seconds under its own 60-second
process cap and found zero discrepancies.

No public action, release, issue, pull request, or novelty claim is authorized
by this trial.
