# Method v0.1: current DeepMind WOWII 314 frozen trial

## Outcome

The prospective trial found no counterexample and terminated at a prior-art
gate.  Current WOWII 314 is already the subject of open upstream PR
[#4496](https://github.com/google-deepmind/formal-conjectures/pull/4496),
which marks it solved and links an immutable external Lean development at
commit `a5e35542007274589f7b88a1fd0244048abb7abd`.

The pre-evaluation contract and append-only ledger are:

- `results/expansion/prospective_wowii314_contract.md`;
- `results/expansion/prospective_wowii314_ledger.jsonl`.

No novelty claim or public action is warranted.

## Frozen target

Only the current DeepMind statement was tested: every connected nontrivial
triangle-free graph with largest induced-path order at most four is well
totally dominated.  Equivalently, the graph is induced-`P5`-free and every
inclusion-minimal total dominating set must have the same size.

The contract was written before any trial graph was evaluated.

## Exact bounded evidence

The frozen lanes produced 17,172 evaluated records:

| Lane | Records | Outcome |
|---|---:|---|
| independent blowups | included in 9,102 blowup records | no crossing |
| bipartite nested-neighborhood families | 7,590 | no crossing |
| named graphs and deterministic regular samples | 328 | no crossing |
| endpoint/module two-switch surgery | 145 retained of 942 generated | no crossing |
| extra Andrasfai/Clebsch checks | 7 | no crossing |

Across the principal family run, 7,591 records failed an antecedent and 9,429
applicable records held.  Every applicable minimal-total-dominating-set
spectrum was the singleton `[2]` or `[3]`.

All processes completed below 60 seconds.  The path evaluator exactly searched
for an induced `P5`; applicable graphs were then checked through induced-path
orders one to four.  Total domination was computed by exhaustive subset
enumeration, retaining exactly the sets minimal under single-vertex deletion.
For independent blowups, the false-twin reduction gives the exact spectrum on
the quotient: a minimal total dominating set cannot contain duplicate members
of one independent twin bag.

## Mandatory Atlas sanity

Two independent implementations evaluated every connected triangle-free
Graph Atlas graph through order seven.

- Both found 89 connected triangle-free graphs.
- Both found exactly the same 40 graphs satisfying the induced-`P5` gate.
- Their complete minimal-total-dominating-set spectra agreed on all 40.
- Neither found a crossing.

The first implementation tested induced subgraphs and used bitset domination.
The second searched ordered chordless five-vertex paths and used direct set
intersection plus combination enumeration.  Thus the agreement is not a
shared-code-path check.

The 40 applicable Atlas graphs expose the same structural split later stated
by the existing proof:

- all 35 bipartite examples have a dominating edge and spectrum `[2]`;
- all five nonbipartite examples have false-twin quotient `C5` and spectrum
  `[3]`.

## Theorem shadow and prior art

The negative search is high-information rather than merely empty.  It points
to the classification wall

```text
connected + triangle-free + induced-P5-free
  -> bipartite dominating-edge/chain region
     or nonbipartite C5-blowup region.
```

In the first region every minimal total dominating set has order two; in the
second it has order three.  This is exactly the proof outline recorded in
upstream PR #4496: bipartite chain graphs versus nonbipartite induced-`C5`
blowups.

The PR's immutable blob link was fetched successfully.  Its root theorem file
imports the detailed development and closes the exact `conjecture314`
signature by `conjecture314_proved`.

## Verdict

`HOLD_BOUNDED`, with a mandatory `PRIOR_ART_STOP`.

The trial independently calibrates the theorem geometry, but WOWII 314 is not
a counterexample target and is not a claimable new solution.  The correct next
move is to exclude it from discovery queues while retaining its two-case
classification as a positive example of tightness analysis detecting a
theorem wall.

