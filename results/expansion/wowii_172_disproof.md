# WOWII 172: the same barbell family gives another disproof

Date: **2026-08-12**. Verdict: **DISPROVED**, source-faithful and apparently
unrecorded. This was found by evaluating the full nearby `L_s` wall after the
WOWII 176 family had survived its gates.

WOWII 172 states

```text
L_s(G) >= -1 + Delta(B) + dist_min(M^2),
```

where `B` is the periphery and `M^2` is the maximum-degree set of `G^2`.
For the two-triangles-and-a-path family `D_L` from the 176 disproof,

```text
L_s=4, Delta(B)=2, dist_G(M^2)=L-2.
```

Thus the published definition-conformant reading requires `4>=L-1`, false for
every `L>=6`. Under the alternative reading that measures distance in `G^2`,
the right side is `1+ceil((L-2)/2)`, so the conjecture is false for every
`L>=9`. Consequently `D_9` is an ambiguity-free joint counterexample to both
172 and 176.

The expanded [`verify_wowii_176.py`](../../scripts/verify_wowii_176.py)
checks both readings of 172 on all 995 connected atlas graphs through order 7
and verifies the family formulas through `D_12`. Targeted exact-statement,
conjecture-number, GitHub, and current-corpus searches found no prior
resolution. As elsewhere, “apparently unrecorded” is not absolute priority.
