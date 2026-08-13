# WOWII 40 prospective line-graph trial

## Outcome

`HOLD_BOUNDED`.

The trial extracted a deficiency-coordinate obstruction from the ten tight
rows in the frozen #40 checkpoint, froze line graphs as one new separating
transformation, repeated the exact database gate, and only then evaluated the
transformed graphs. Eight of the ten line graphs met the frozen order bound;
all eight were exact, with no crossing or timeout.

## Equality obstruction

Let `tau_F = n-f`, `tau_B = n-b`, and `L = n-p`, where `f` is maximum induced
forest order, `b` maximum induced-bipartite order, and `p` minimum path-cover
number. WOWII 40 is equivalent to

```text
L + tau_B >= 2*tau_F + 1.
```

All ten checkpoint wall rows have residual

```text
R = L + tau_B - 2*tau_F
```

equal to one or two. These are the two parity-adjacent equality positions
created by the ceiling. The frozen line-graph prediction was that converting
high-degree incidence stars into overlapping cliques might raise `tau_F`
faster than `L + tau_B`.

## Exact results

The repeated sanity set comprised 1,031 exact controls and produced zero
crossings. The ten checkpoint inputs then gave:

- eight admissible distinct line graphs of orders 5 through 18;
- two exclusions of orders 20 and 24, fixed by the predeclared order-18 cap;
- slack distribution `{0: 2, 1: 2, 2: 3, 3: 1}`;
- residual distribution `{1: 1, 2: 1, 3: 2, 5: 3, 7: 1}`;
- zero timeouts and zero crossings.

All eight line graphs had a Hamiltonian path, certified by emitted vertex
orders. Hence `p=1` and `L=n-1` exactly. This is the new obstruction revealed
by the negative trial: the incidence cliques did raise feedback burden, but
line-graph Hamiltonicity raised the compensating linear-forest coordinate even
more. Rather than crossing, six of eight outputs moved away from the wall.

Induced-forest and induced-bipartite maxima were computed by exhaustive subset
search. Returned forest, bipartite, and path-cover witnesses were separately
validated against the decoded graph6 records. The output fingerprint is
`8c4e0f3cc2204acd215943b5c6c22808b7b1ef62d53adfbe6bf01ad46c75a2b6`.

## Consequence for another trial

A future transformation should avoid automatically producing Hamiltonian
graphs. The coordinate target is now sharper: increase `tau_F` while keeping
`L=n-p` from growing, meaning the transformed graph should have a deliberately
large path-cover number. That requires a new frozen family; it must not be
added retrospectively to this completed line-graph trial.

No crossing occurred, so no source/novelty audit was triggered. No commit,
push, release, issue, PR, or other public action was taken.
