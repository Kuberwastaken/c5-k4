# Second prospective WOWII 19 trial: equality-seed squares

## Outcome

`HOLD_BOUNDED`.

The second trial froze one genuinely new move before evaluation: take the graph
square of every retained equality seed from the completed #19 lane. The 56
seed rows collapsed to 20 isomorphism classes. All 20 were solved exactly;
none crossed the conjectured wall, ten remained tight, and ten moved to slack
one. There were no timeouts.

## Prospective rationale

The prior equality rows exposed the identity

```text
b(G) - max_v alpha(G[N(v)]) = floor(average_v eccentricity(v)).
```

with observed integer values from one through five. The frozen prediction was
that global distance-two closure might destroy induced-bipartite capacity
faster than it lowered the other side of this identity. Unlike the first
trial's block constructions, substitutions, and bounded surgeries, graph
squaring changes every distance-two nonedge simultaneously.

The prediction did not cross the wall. Instead, squaring pushed the observed
slack distribution to `{0: 10, 1: 10}`. Complete and near-complete squares
often reset to the familiar exact identity `b = 2`, local independence `= 1`,
and average eccentricity `= 1`. Less compressed squares retained one unit of
safety rather than producing negative slack.

## Gate and exactness

- The contract/addendum was written before any square was evaluated.
- The repeated database gate checked all 995 connected Graph Atlas graphs of
  orders two through seven: zero crossings and 599 equality cases.
- The trial process completed in 3.8 seconds under the 60-second cap.
- Nineteen transformed graphs were closed by exhaustive deletion enumeration.
  The one order-20 dense case used the bounded exact retained/color MILP and
  returned an optimum at zero MIP gap.
- Every returned bipartite witness was checked directly.

The deterministic output has SHA-256
`e0ca42caeceae886fd6246f7c3b11d264036da9dedd3722942cedf4faf2689f0`.
Representative certificates and the aggregate result are in
`prospective_wowii19_square_ledger.jsonl`.

## Interpretation

This is a useful failed separating move. The equality identity selected a
specific coordinate to attack, but global distance closure compressed
eccentricity at least as effectively as it reduced the relative
induced-bipartite capacity. A third #19 trial should not enlarge the graph-power
menu after seeing this result. It would need a separately frozen operation
that raises the eccentricity floor while recycling existing odd-cycle
constraints instead of adding freely retainable path vertices.

No source/novelty audit was triggered because there was no crossing. No commit,
push, release, issue, PR, or other public action was taken.
