# Reed hard-claw blocker: first feasible gadget is safe by one

Date: **2026-08-13 UTC**

Status: **completed; no counterexample candidate and no public claim**

## Prospective selection

The selection CNF combined two exact requirements:

1. block every extension of all 9,720 optimal eight-color partitions of
   `C5[K3]`;
2. contain the fixed induced claw with carrier center 0 and leaves
   `x0,5,14`.

The search exhausted one, two, and then three new vertices in the frozen
coordinate order. Every one- and two-vertex instance with total
`omega+Delta` increment at most four was infeasible. For three vertices, every
instance through total increment two was infeasible. At total increment three,
the `Delta+2, omega+1` budget was the first feasible budget, and internal-edge
mask zero was its first feasible template.

The deterministic first model adds three mutually nonadjacent vertices with
carrier neighborhoods

```text
N(15) = {0,1,2,3,4,6,7,8,9}
N(16) = {0,1,2,3,4,10,11,12,13,14}
N(17) = {5,6,7,8,9,10,11,12,13,14}.
```

No transformed invariant was evaluated before this model was frozen.

## Gates

The fresh Atlas gate again found zero violations among all 995 connected
graphs of orders 2--7.

The frozen graph genuinely escapes the checked static theorem classes. It has
the encoded induced claw `[0,15,5,14]`, independence number 3, connected
complement, an induced `P5`, an induced chair, and a high-degree induced `C5`.

Rabern's 2008 theorem gives the conditional threshold
`(n+3-alpha)/2 = 9`. It therefore rules out `chi>9` but does not pre-resolve
the nine-chromatic case evaluated here.

## Exact result

The 18-vertex frozen graph has

`(chi, omega, Delta) = (9, 7, 10)`.

Thus its doubled Reed slack is

`omega + Delta + 2 - 2*chi = 1`.

Exact DSATUR rejected eight colors in 17,194 states and supplied a nine-color
witness. Exact clique search supplied the seven-clique
`[0,1,2,12,13,14,16]`; vertex 0 has degree ten.

A separate static-order search independently rejected eight colors in 29,731
states and found a nine-coloring in 144 states. Exhausting all `2^18` vertex
subsets independently confirmed clique number seven, and direct degree
recomputation confirmed maximum degree ten.

The canonical graph digest is
`sha256(graph6) = d662f7a28227f590393b86cda3834a51805ae6a55f93def531b23f6f00f5a7da`.

## Interpretation

The CNF methodology now does exactly what the earlier gadgets did not: it
forces a ninth color while preserving an explicit claw and avoiding the
obvious proved classes. But within the preregistered space of at most three new
vertices, the minimum structural cost is three units in `omega+Delta`.
Increasing `chi` by one gains only two units on the doubled left side, so the
first feasible graph remains safe by one.

This is a useful local obstruction certificate rather than a disproof. A
further Reed trial should not simply enlarge the same search adaptively. It
would need a new frozen mechanism capable of forcing two new colors for at
most three coordinate units, or one new color for at most one coordinate unit,
while remaining outside known theorem classes.
