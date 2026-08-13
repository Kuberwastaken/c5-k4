# Reed color-blocker trial: escaped claw-free, no crossing

Date: **2026-08-13 UTC**

Status: **completed; no counterexample candidate and no public claim**

## Frozen hypothesis

Starting from the exact equality carrier `C5[K3]`, add one vertex `x` adjacent
to all three vertices of bag 0, the first two vertices of bags 1 and 4, and
the first vertex of bags 2 and 3. No alternative neighborhood was tested.

Before chromatic evaluation, this fixed the structural coordinates
`omega=6` and `Delta=9`. It also created the explicit induced claw

`center 0; leaves 15, 5, 14`,

where vertex 15 is `x`. The prospective question was therefore binary:
`chi=9` would give doubled Reed slack -1, while `chi=8` would give slack 1.

## Sanity and status gates

The fresh database gate exhausted all 995 connected Atlas graphs of orders
2--7 with exact coloring, clique, and degree witnesses. It found zero Reed
violations.

Upstream `main` still marks the finite declaration `research open` (blob SHA
`526ca28f41ba9e18646d53ac8cf995cb771fa51a`), and issue #159 remains open.

The frozen graph is not in the static proved domains checked during the audit:

- it has an induced claw, so is neither claw-free nor quasi-line;
- its complement is connected and its independence number is 3;
- it contains an induced `P5`, an induced chair, and a high-degree induced
  `C5`;
- its vertices of degree at least 5 do not form a stable set.

There was also a decisive conditional safety gate. Rabern proved Reed's
conjecture whenever `chi > (n+3-alpha)/2`. Here `n=16` and `alpha=3`, so the
threshold is 8. Any computed `chi=9` would therefore have triggered a
known-theorem conflict rather than a disproof claim. See
[Rabern 2008](https://doi.org/10.1137/060659193).

## Exact result

The single frozen graph has

`(chi, omega, Delta) = (8, 6, 9)`

and hence

`omega + Delta + 2 - 2*chi = 1`.

The exact DSATUR search rejected 6 and 7 colors and supplied the eight-coloring

`[0,1,2,3,4,5,1,2,6,0,5,7,3,4,6,5]`.

Exact clique search supplied the six-clique `[0,1,2,3,4,5]`. Vertex 0 has
maximum degree 9. A separate static-order coloring search independently
rejected seven colors in 1,947 states, and exhaustive enumeration of all
`2^16` vertex subsets independently confirmed clique number 6.

The canonical graph digest is
`sha256(graph6) = 26cbe80ea749b0c3fdedc80b5e67c04287ab43910f8691a635be67c3f849034a`.

## Interpretation

This is a useful stricter negative than the preceding one-edge trial. The
gadget genuinely leaves the claw-free proved class and achieves the desired
`omega/Delta` coordinates, but its neighborhood is not a color blocker: `x`
can reuse color 5 in an optimal carrier coloring. The failure is entirely in
the `chi` coordinate, not compensation by `omega` or `Delta`.

Any next intervention must be frozen as a new trial. In light of Rabern's
theorem, this exact `n=16, alpha=3` route cannot yield a valid `chi=9` crossing;
the next design should change the order/independence-number geometry rather
than adaptively modifying this neighborhood.

Reproduction:

```text
timeout 60s python3 scripts/method_v46_reed_weighted_surgery.py atlas
timeout 60s python3 scripts/method_v47_reed_color_blocker.py audit
timeout 60s python3 scripts/method_v47_reed_color_blocker.py evaluate
```
