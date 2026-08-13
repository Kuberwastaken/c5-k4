# Reed weighted-surgery trial: negative known-domain result

Date: **2026-08-13 UTC**

Status: **completed; no counterexample candidate and no public claim**

## Question

The exact finite statement currently formalized in
`FormalConjectures/Paper/ReedOmegaDeltaChi.lean` is

`2 chi(G) <= omega(G) + Delta(G) + 2`.

Uniform odd clique blow-ups of `C5` sit on the equality wall. The prospective
trial asked whether a frozen one-edge addition between distance-two bags of a
nonuniform weighted blow-up could increase `chi` without enough compensation
from `omega + Delta`.

This is a deliberately conservative experiment against a major human open
conjecture. King and Reed proved Reed's conjecture for all claw-free graphs
(Journal of Graph Theory, 2014, DOI `10.1002/jgt.21797`). Consequently every
claw-free output was stopped before transformed-invariant optimization.

## Database sanity gate

The gate exhausted all **995** connected unlabeled Atlas graphs of orders
2--7. Exact DSATUR feasibility searches supplied a proper minimum coloring and
infeasibility searches below it; exact clique branch-and-bound supplied a
maximum-clique witness; direct degree computation supplied a maximum-degree
vertex.

- Reed violations: **0**
- coloring-search states: **8,000**
- clique-search states: **6,422**

Named controls reproduced the expected `(chi, omega, Delta, slack)` values:

| graph | chi | omega | Delta | `omega+Delta+2-2chi` |
|---|---:|---:|---:|---:|
| `K5` | 5 | 5 | 4 | 1 |
| `C5` | 3 | 2 | 2 | 0 |
| `C7` | 3 | 2 | 2 | 0 |
| Petersen | 3 | 2 | 3 | 1 |
| `C5[K2]` | 5 | 4 | 5 | 1 |
| `C5[K3]` | 8 | 6 | 8 | 0 |
| `C5[K4]` | 10 | 8 | 11 | 1 |

## Frozen family result

There are **852** dihedral-canonical positive weight vectors with each weight
at most 6 and total order at most 24. Only two have exact zero slack:

| weights | chi | omega | Delta | slack |
|---|---:|---:|---:|---:|
| `(1,1,1,1,1)` | 3 | 2 | 2 | 0 |
| `(3,3,3,3,3)` | 8 | 6 | 8 | 0 |

For each base, the protocol generated the five predeclared additions joining
canonical vertices in distance-two bags. All **10/10** resulting graphs were
still claw-free. They therefore received `KNOWN_PROOF_DOMAIN` stops at the
class gate. No transformed graph proceeded to exact `chi/omega/Delta`
profiling, and there was no numerical crossing.

## Interpretation

This intervention does not escape the theorem class, so it cannot provide the
requested second prospective crossing. That is useful negative information:
one interbag edge is too local a perturbation of the odd `C5` blow-up equality
wall. A future Reed experiment would need a pre-frozen move that provably
creates an induced claw (or otherwise leaves every known proved class) before
its invariant coordinates are evaluated. Such a trial requires a fresh
contract and fresh bibliographic gate; it is not an adaptive extension of this
one.

Reproduction:

```text
timeout 60s python3 scripts/method_v46_reed_weighted_surgery.py atlas
timeout 60s python3 scripts/method_v46_reed_weighted_surgery.py family
```
