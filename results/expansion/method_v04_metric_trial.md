# Method v0.4 trial: WOWII 184/185

Status: **HOLD_BOUNDED — COMPLETE FIXED GRID, NO CROSSING**

## Source normalization lock

The primary recovered definitions are the verbatim text in
`data/INVARIANT-GLOSSARY.md`, extracted from DeLaViña's `wowIIdefs.js`.
They define:

```text
B(H) = the vertices of maximum eccentricity in H;
dist_avg(B,V) = the average of all positive dist_H(b,v)
                with b in B(H), v in V(H);
dist_avg(V) = the average of all dist_H(u,v) with u != v.
```

Consequently both averages use ordered pairs with zero self-pairs omitted.
For a connected graph of order `n`, their denominators are respectively
`|B(H)|(n-1)` and `n(n-1)`. This agrees with the formulas preregistered in
`method_v04_metric_selection.md`; no correction to the residual identity is
needed.

There is a contradictory editorial compute hint in the glossary that says
`dist_avg(B,V)` is the average over `v` of `dist(v,B)`. That is not the quoted
primary definition and would produce zero whenever `B=V`, contradicting the
eleven recorded equality controls. The trial therefore follows the primary
definition and records the discrepancy rather than silently switching
readings.

The execution ledger is `method_v04_metric_trial.jsonl`. Gate and grid results
will be summarized below only after their respective fixed stages finish.

## Database-sanity gate

**PASSED.** All 32 gate shards closed before the first comet row was
evaluated. The gate contains 1,057 exact control rows, with zero process or
optimization timeouts, zero negative residuals for either conjecture, and
zero equality-control mismatches. The minimum residual for both 184 and 185
was zero; each had 32 zero rows after named duplicates required by the frozen
gate were retained.

The fixed 270-row `K(m,L)` grid is now being appended in increasing `m` and
`L`. No adaptive graph has been introduced.

The first 30-row `m=5` process reached its explicit 60-second process cap
after durably writing `K(5,24)`. No individual solve timed out. The ledger
records that aborted process and the missing interval `K(5,25)` through
`K(5,30)`. Execution resumes with one `(m,L)` row per externally capped
60-second process; completed `(m,L)` keys are checked first and never rerun.

## Fixed-grid result

**HOLD_BOUNDED.** The complete preregistered grid was evaluated:

```text
2 <= m <= 10, 1 <= L <= 30: 270/270 unique graphs
missing keys: 0
duplicate completed keys: 0
individual optimization timeouts: 0
WOWII 184 crossings: 0
WOWII 185 crossings: 0
```

Both conjectures remain strictly on the holding side throughout this family.
The closest graph for each is `K(2,2)`:

```text
R184(K(2,2)) = 69/121,
R185(K(2,2)) = 20/33.
```

There are no equality rows in the fixed comet grid. For every row `T173=1`;
the handle immediately moves the carrier one unit off the proved 173 wall.
As the handle grows, the square maximum-degree deficit grows essentially with
its length (`q-L` is always `-2` or `-1`), while the two distance averages do
not compensate for that price. The largest observed metric averages were
`d_B=708/95` at `K(2,29)` and `d=1273/198` at `K(3,30)`, yet the residuals
grow rather than cross. The frozen prediction that core weight could amplify
the average without proportional `q` growth therefore failed in this quotient.

The complete grid exhibits the following exact pinning pattern in every one
of its 270 rows:

```text
gamma_c(K(m,L)) = L+2,
L_s(K(m,L))     = 5m-2,
b(K(m,L))       = L+4,
T173(K(m,L))    = 1,
q(K(m,L)^2)     = max(0,L-2).
```

These identities explain the numerical failure more sharply: the core size
`m` cancels out of `L_s+b-(n+1)`, while every new handle layer after the second
adds one unit to `q`. The optimization witnesses certify these values on the
fixed box; this report does not promote the observed formulas to an unbounded
family theorem.

All exact large-graph optimizations terminated optimally. The slowest
maximum-induced-bipartite solve took 14.794416 seconds (`K(9,1)`), and the
slowest connected-domination solve took 32.553515 seconds (`K(9,29)`), below
the 55-second internal and 60-second external limits.

`scripts/verify_method_v04_metric_trial.py` independently audits gate closure,
the complete unique `(m,L)` key set, absence of timeout/crossing rows, every
serialized residual identity, and both exact minima. No candidate existed, so
the candidate-only independent graph recomputation rule was not triggered.

## Method consequence

Rooted carrier comets do change the intended metric coordinate, but not in the
required direction after theorem subtraction. A longer handle raises `q` at
least as decisively as it raises `2(d_X-1)`, and attaching the handle also fixes
`T173` at one instead of zero. This bounded failure does not prove WOWII 184 or
185. It removes this exact quotient/parameter box from the discovery program;
no nonuniform weights, alternate attachment, or wider handle was tested.
