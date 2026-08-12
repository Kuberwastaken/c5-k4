# Graph Brain alpha lower bound 082 — executable retro-kill

The Graph Brain project's still-open issue #421 posts the exact line

> `independence_number(x) >= floor(log(tan(order(x))^2)/log(10))`

Source: [math1um/objects-invariants-properties issue #421](https://github.com/math1um/objects-invariants-properties/issues/421),
opened 2017-09-07.  The primary Graph Brain paper reproduces it in Figure 14:
[arXiv:1801.01814v1](https://arxiv.org/abs/1801.01814).

Under Sage/Python's standard real-radian convention:

- `K11`: `alpha=1`, while the raw right side is `4.708027945...`, hence
  the floored right side is `4`.
- `C5[K11]`: `alpha=2`, while the raw right side is `3.309951816...`,
  hence the floored right side is `3`.

The values are more than `1e-6` from an integer boundary.  `K11` is the
smallest complete-graph witness and shows this is a stale **retro-kill**, not a
counterexample special to the campaign's carrier family.  The issue is still
open-as-posted; this certificate does not claim that no unpublished or
unindexed prior refutation exists.

Run:

```bash
python3 verify.py
python3 -m unittest -v
```
