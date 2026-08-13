# Method v0.49: WOWII 61 cycle/theta bead bridges

## Outcome

The frozen low-degree bead trial returns **`HOLD_BOUNDED`**. It repairs the
specific failure of clique beads: 4,199 of 4,212 constructions preserve or
raise the seed's Havel--Hakimi residue, with residue reaching sixteen and
diameter reaching eighteen. Nevertheless, every graph remains at least four
units inside WOWII 61.

The obstruction is now complementary to the clique result. Low-degree cyclic
beads preserve residue, but each bead loses only one vertex to a feedback set,
so maximum induced-forest order grows too quickly. The frozen family is closed;
no parameter was retuned after evaluation.

No commit, push, issue, PR, release, or other public action was taken by this
trial.

Artifacts:

- `results/expansion/prospective_wowii61_cycle_theta_bead_contract.md`;
- `results/expansion/prospective_wowii61_cycle_theta_bead_ledger.jsonl`;
- `results/expansion/prospective_wowii61_cycle_theta_bead_records.jsonl`;
- `scripts/prospective_wowii61_cycle_theta_bead.py`;
- `scripts/verify_wowii61_cycle_theta_bead.py`.

## Frozen family

The bases were the three protocol-exact neutral endpoints from the order-12
corridor. The rooted bead menu was fixed before evaluation:

- cycles `C_3` through `C_12`; and
- equal-arm theta graphs `Theta(p,L)` for `p in {3,4}` and
  `L in {2,3,4,5}`.

Every ordered bead pair was bridge-attached to every unordered diametral pair
of every base. The bases have 3, 4, and 6 diametral pairs, giving exactly

```text
(3 + 4 + 6) * 18^2 = 4,212
```

labelled constructions. All degrees internal to cycles are two. Theta graphs
have degree-two internal vertices and terminal degree at most four.

## Exact coordinate certificate

For a bead `X`, write `n_X` for its order and `rho_X` for the eccentricity of
its root. Each bead is cyclic but becomes a forest after deleting one fixed
vertex. Since its attachment to the base is a bridge, cycles cannot cross
blocks. Consequently every transformed graph `T` satisfies exactly

```text
forest(T)   = 10 + (n_A - 1) + (n_B - 1),
diameter(T) = 6 + rho_A + rho_B.
```

Every record contains the full base-plus-beads forest witness. The matching
upper certificate is additive: the base contributes at most ten, and each
cyclic bead contributes at most its order minus one.

## Sanity gates

The exact predevelopment gate replayed 1,030 controls with no violation or
timeout:

| residual | 0 | 1 | 2 | 3 | 4 | 5 |
|---:|---:|---:|---:|---:|---:|---:|
| graphs | 159 | 574 | 281 | 10 | 5 | 1 |

All three bases independently recomputed to degree sequence
`[6,6,4,3,2,1,1,1,1,1,1,1]`, residue eight, diameter four, exact forest ten,
and residual zero. The mechanical family count also matched the frozen 4,212.

## Results

All 4,212 graphs completed with no certificate mismatch or timeout.

| measurement | result |
|---|---:|
| residue preserved or raised | 4,199 / 4,212 |
| residue range | 7--16 |
| diameter range | 8--18 |
| minimum residual | 4 |
| candidates | 0 |

The residue histogram was:

| residue | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| graphs | 13 | 299 | 546 | 858 | 949 | 754 | 442 | 234 | 104 | 13 |

The thirteen residue-seven graphs are exactly the `C_3,C_3` choice at each of
the thirteen diametral attachment pairs. Every other graph preserves or raises
the seed residue.

Residuals range from four to twenty-two. The 52 minimum-residual graphs are
the four ordered cycle pairs `(C_3,C_3)`, `(C_3,C_4)`, `(C_4,C_3)`, and
`(C_4,C_4)` at each diametral pair. Even these closest graphs remain four units
safe.

## Independent replay

A separately written verifier reconstructed every bead from its specification
and checked all 4,212 records independently:

- graph6 isomorphism against the labelled edge list;
- full Havel--Hakimi trajectory and residue;
- all-source BFS diameter and the frozen coordinate formula;
- the explicit forest witness;
- cyclicity and one-vertex deletion certificate of each bead;
- the two joining bridges and block-additive upper certificate; and
- crossing threshold and final residual.

It returned zero mismatches and zero candidates. The verifier's first attempt
incorrectly assumed NetworkX graph6 serialization preserved the labelled
edge-list numbering. That process failure is logged; the corrected verifier
requires exact isomorphism to graph6 before checking labelled witnesses. No
trial record or mathematical result changed.

## Interpretation

Together with the clique-bead experiment, this produces a clear design
tradeoff:

```text
dense clique beads:
  strong feedback forcing, but residue collapses to 7;

low-degree cycle/theta beads:
  residue usually rises, but forest grows by n_bead - 1.
```

The missing object would need both properties simultaneously: bounded-degree
or residue-friendly degree geometry, and feedback deletion substantially
larger than one per bead. A future prospective family should be frozen around
that combined requirement rather than tuning this completed cycle/theta menu.

