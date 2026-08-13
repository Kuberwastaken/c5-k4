# Erdős 128 canonical Hajós join: density boundary collapses

Date: **2026-08-13 UTC**

Status: **completed; premise false, no counterexample candidate**

## Rotation and frozen trial

This lane moved away from Reed to the induced-density/triangle cluster of the
current DeepMind declaration `Erdos128.erdos_128`. Its exact carrier was the
balanced independent-set `C5` blow-up `B2`, whose minimum five-vertex induced
edge count is two:

`50*2 - 10^2 = 0`.

That is exact equality at the boundary of the formal strict premise.

Before development evaluation, the trial froze one canonical Hajós join of
two labeled `B2` copies: delete canonical edges `(0,2)` and `(10,12)`, identify
vertices 0 and 10, and add the edge joining the two surviving opposite
endpoints. No alternate join was evaluated.

## Database gate

The gate evaluated 97 connected triangle-free Atlas and named controls with
192,202 exact subset checks. No control unexpectedly satisfied the strict
premise, and `B2` reproduced its exact zero-margin calibration.

## Exact development result

The sole joined graph has:

| coordinate | exact value |
|---|---:|
| order | 19 |
| edges | 39 |
| triangles | 0 |
| minimum eligible size | 9 |
| strict-premise edge requirement | at least 8 |
| exact minimum induced edges | 2 |
| premise margin `50e-n^2` | -261 |

The primary exhaustive search checked all 92,378 nine-vertex subsets. Its
minimizing witness is

`{1,2,3,6,7,13,14,17,18}`,

which directly replays with two induced edges.

A separately implemented include/exclude branch-and-bound search independently
reached the same minimum and witness in 10,403 states. A separate triangle
count returned zero. Both methods reconstructed graph digest

`72e76e037ac111ce932c4bcbc10061d2c59335f31f344f0e6eebff4d54c9d7f6`.

## Interpretation

Hajós composition preserves triangle-freeness here but catastrophically fails
to preserve the carrier's induced-density boundary. The required subset size
nearly doubles, yet a minimizing set can draw sparse pieces from both sides of
the one-vertex join and retain only the carrier-scale two edges. The strict
threshold rises from three edges on order ten to eight edges on order nineteen,
so the margin moves from zero to -261.

This closes the single canonical Hajós-join trial and provides evidence that
low-order-separator compositions are directionally incompatible with the
Erdős 128 premise. It does not claim that every Hajós join fails without a
separate general proof.

No WoW I source, random search, timeout, candidate, commit, release, or public
action occurred.
