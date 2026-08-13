# WOWII #141 `K3,3-e` two-lift parity extraction

Date: **2026-08-13 UTC**

Status: **WARNING-CLEAN ALGEBRAIC OBSTRUCTION; GRAPH ADAPTER EXPOSED**

No commit, push, issue, PR, release, or other public action was taken in this
lane.

## Formal artifact

`lean/Wow141K33eTwoLiftParity.lean` formalizes the three gauge-fixed cotree
voltages

```text
(x15,x23,x35) in Bool^3
```

and the five frozen base-C4 parity forms, in the exact trial order:

```text
0415: x15
0435: x35
1234: x23
1235: x15 xor x23 xor x35
1435: x15 xor x35.
```

The constructive selector uses cycle `0415` if `x15=0`, cycle `0435` if
`x35=0`, and cycle `1435` otherwise.  The final case has
`x15=x35=1`, hence `x15 xor x35=0`.  Lean proves:

- `survivingCycleIndex_even`: the selected form is even for every triple;
- `five_cycle_parities_not_all_odd`: the five forms cannot all be odd;
- `sevenVoltage_ne_zero`: every frozen `001`--`111` row is nonzero;
- `sevenVoltage_injective`: the seven rows are distinct;
- `sevenVoltage_exhaustive`: they exhaust all nonzero Bool triples;
- `sevenVoltage_has_even_fourCycle`: every frozen row has an explicit even
  base-C4 parity form;
- `nonzeroVoltage_has_even_fourCycle`: the same conclusion without table
  enumeration.

Thus the empirical seven-row observation has been replaced by a general
`Bool`/F2 parity theorem.

## Honest adapter boundary

This artifact deliberately stops at the voltage algebra.  It does **not** yet
formalize:

1. the labelled `K3,3-e` base graph and the derivation of the five formulas
   from its edge lists;
2. switching/gauge normalization to zero voltage on the five spanning-tree
   edges;
3. the graph-cover lemma that an even-voltage simple base cycle lifts to a
   simple cycle of the same length;
4. the resulting graph-level statement that every connected two-lift has
   girth four.

Those are the exact adapters needed to turn the algebraic obstruction into a
fully graph-level Lean theorem.  No such conclusion is smuggled into the
current theorem names.  The seven exact assignments themselves are connected
to the algebraic result, while “connected two-lift” remains a fact established
by the audited prospective computation rather than by this file.

## Verification

From `/Users/kuber.mehta/Projects/formal-conjectures`:

```bash
timeout 55s lake env lean -DwarningAsError=true \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  /Users/kuber.mehta/Projects/c5-k4/lean/Wow141K33eTwoLiftParity.lean
```

Result: exit `0` in approximately 6.5 seconds.

The theorem audit printed only the standard axiom `propext` for the three
audited public results.  The source contains no `sorry`, `admit`,
`native_decide`, or custom `axiom`.

