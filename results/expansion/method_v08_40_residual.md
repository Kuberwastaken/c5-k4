# WOWII 40 residual: maximum-core colour imbalance

**Date:** 2026-08-13

**Outcome:** a no-`sorry` Lean proof of the complete conjectured inequality
whenever a maximum induced bipartite core has colour imbalance at least
`pathCoverNumber G - 1`.

**Project snapshot before this lane:** `c5-k4` `8f4b72d`

**Read-only upstream snapshot:** `formal-conjectures`
`9a1636c4030039f70cf78b866c216d8b6c5f35b0`

## Exact statement proved

Let `S` be a maximum induced bipartite witness, let `c : V → Fin 2` be a
proper two-colouring on `S`, and write its colour classes as `A` and `C`,
ordered so that `|C| <= |A|`. The new file proves

```text
pathCoverNumber G <= |A| - |C| + 1
    ->
pathCoverNumber G + largestInducedBipartiteSubgraphSize G + 1
  <= 2 * largestInducedForestSize G.
```

It then proves the same result in the exact real/ceiling shape of upstream
WOWII 40:

```text
⌈((pathCoverNumber G : ℝ) + b G + 1) / 2⌉
  <= largestInducedForestSize G.
```

The hypotheses encode maximum bipartiteness without an unused redundant
predicate: `S.card` equals the repository invariant and `c` is proper on
every edge induced by `S`.

## Why this advances the baseline

The source baseline constructs a forest from a larger colour class plus one
vertex outside it. Keeping the colour imbalance rather than discarding it
gives

```text
2f >= 2|A| + 2
   = (|A| + |C|) + (|A| - |C|) + 2
   = B + imbalance + 2.
```

Thus the imbalance pays exactly for the residual `p - 1`. The previously
formalized traceable case `p = 1` discarded this surplus. This result is a
strict structural extension: for example, it includes `p = 2` whenever a
maximum bipartite core has unequal colour-class sizes, and it permits larger
path-cover number when the imbalance grows with it.

## Verification

The file is:

```text
lean/GraphConjecture40Residual.lean
```

After compiling `GraphConjecture40Baseline.lean` as its local imported
module, the independent check was:

```text
timeout 60s env LEAN_PATH=/Users/kuber.mehta/Projects/c5-k4/lean \
  lake env lean -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture40Residual.lean
```

It exited `0` in 7.01 seconds with no output. The source contains no
`sorry`, `admit`, or custom axiom.

## Exact remaining boundary

This does **not** prove WOWII 40 in full. The surviving graphs are precisely
the nearly balanced maximum-core regime not paid for by this argument:

```text
for every maximum bipartite two-colouring with |C| <= |A|,
|A| - |C| <= pathCoverNumber G - 2.
```

The proof also does not establish the deeper deficiency inequality
`ell + o >= 2*tau + 1`. The next honest target remains either its bipartite
base case or a slack-aware maximum-core transfer. The frozen `EQKo` control
still rules out the already-recorded pointwise insertion shortcut.

Classification: **FORMAL PARTIAL THEOREM; no counterexample, release, or
external claim.**
