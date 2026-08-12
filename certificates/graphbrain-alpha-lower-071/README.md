# Graph Brain alpha lower bound 071 — executable retro-kill

The Graph Brain project's still-open issue #421 posts the exact line

> `independence_number(x) >= floor(2*tan(matching_number(x)) - 2)`

Source: [math1um/objects-invariants-properties issue #421](https://github.com/math1um/objects-invariants-properties/issues/421),
opened 2017-09-07.  The primary Graph Brain paper reproduces it in Figure 14:
[arXiv:1801.01814v1](https://arxiv.org/abs/1801.01814).

Under Sage/Python's standard real-radian convention, matching number `14`
gives `2*tan(14)-2 = 12.489213...`, whose floor is `12`:

- `K28` has `alpha=1` and matching number `14`.
- `C7[K4]` has `alpha=3` and matching number `14` (pair vertices within
  each four-vertex clique fiber to exhibit a perfect matching).

The value is more than `1e-6` from an integer boundary.  `K28` is the simpler
witness and shows this is a stale **retro-kill**, not a counterexample special
to the campaign's carrier family.  The issue is still open-as-posted; this
certificate does not claim that no unpublished or unindexed prior refutation
exists.

Run:

```bash
python3 verify.py
python3 -m unittest -v
```
