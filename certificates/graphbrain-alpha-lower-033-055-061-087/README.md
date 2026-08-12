# Graph Brain alpha lower retro-kills: 033, 055, 061, 087

This executable certificate verifies four counterexamples to lines still
listed as open in the author-project issue #421. They are reported as
**retro-kills**, not as claims of mathematical novelty.

Run:

```bash
/home/ec2-user/.venvs/wowii/bin/python verify.py
/home/ec2-user/.venvs/wowii/bin/python -m unittest -v test_verify.py
```

Witnesses and failures:

* lower-033: `C5[K3]`, alpha 2, while
  `-girth + min(min_degree,tan(average_distance)) = -3+tan(10/7)` is
  approximately 3.983645.
* lower-055: `C5[K5]`, alpha 2, while
  `min(radius^2,min_common_neighbors/2)=min(4,5/2)=5/2`.
* lower-061: `C9[K3]`, alpha 4, while
  `min(szekeres_wilf,-average_degree+matching_number)=min(9,-8+13)=5`.
* lower-087: the same `C9[K3]`, alpha 4, while
  `min(2*girth,matching_number-max_degree)=min(6,13-8)=5`.

The verifier also runs the literal reading over every nontrivial connected
Graph Atlas graph (995 graphs of orders 2--7) and the campaign's named gate.
None violates these four statements. All integer-valued witness invariants
are independently checked against the closed forms for odd-cycle clique
blow-ups; lower-033 retains a `1e-6` numerical guard.

