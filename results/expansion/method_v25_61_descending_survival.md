# Method v0.25: WOWII 61 descending survival closes `k=2`

Date: **2026-08-13 UTC**

Outcome: **the final indexing bridge is formal. For descending positive
equal-top-two states, full weak prefix dominance implies monotonicity of the
first two canonical Havel--Hakimi heads, with no survival, multiplicity, or
saturation premise. The complete `k=2` case is closed.**

This remains a partial theorem toward WOWII 61; longer elimination prefixes
are not proved.

## Descending survival localization

Let `xs` be descending and suppose

```text
e in xs.drop d.
```

The new Lean proof extracts an index `j` in `xs.drop d` whose value is `e`.
The corresponding absolute index is `d+j` by `List.getElem_drop`.

For any entry `x` in `xs.take (d+1)`, extract its prefix index `i`. Since

```text
i < d+1 <= d+j+1,
```

we have `i <= d+j`. The descending `Pairwise (fun a b => b<=a)` relation and
`Pairwise.rel_get_of_le` give

```text
xs[d+j] <= xs[i].
```

Substituting the two extracted values yields

```text
e <= x.
```

Thus every prefix entry before the surviving maximum is at least that maximum.

## Survival implies exact saturation

The standard descending-head bound supplies the reverse inequality

```text
x <= e
```

for every entry in the relevant state. Target survival also proves the list
has at least `d+1` entries. The v0.24 bounded-both-ways lemma therefore gives

```text
xs.take (d+1) = replicate (d+1) e.
```

This is the exact missing implication from v0.24:

```text
descending + survival -> boundary-prefix saturation.
```

## Full equal-top-two theorem

Consider two descending tails beginning with the same positive second degree
`e`, attached below the same positive first head `d`:

```text
source = d :: e :: sourceTail,
target = d :: e :: targetTail.
```

Assume ordinary weak prefix dominance between `e :: sourceTail` and
`e :: targetTail`:

```text
same length,
every target prefix sum <= the corresponding source prefix sum.
```

The proof splits only implicitly through the v0.22 survival endpoint:

- if the target does not survive, its second head is at most `e-1`, while the
  source second head is at least `e-1`;
- if the target survives, the new indexing lemma saturates its `(d+1)` prefix;
- v0.24 transports that saturation through prefix dominance to the source;
- source saturation gives more than `d` copies of `e`;
- multiplicity gives source survival;
- both second heads then attain `e`.

Lean concludes

```text
cumulativeHeadSum 2 target <= cumulativeHeadSum 2 source.
```

No graphicality assumption is required beyond descending finite degree-list
structure. The theorem therefore applies a fortiori to the graphical states
used in the WOWII 61 induction.

## What is now closed

The earlier v0.21 theorem handled strict top-two prefix advantage. The
v0.22--v0.25 chain now handles the equality case:

```text
v0.22 exact second-head endpoint flag
-> v0.23 multiplicity orders survival
-> v0.24 prefix sums transport saturation
-> v0.25 descending order turns survival into saturation.
```

Together, these establish two-step eliminated-head monotonicity under weak
prefix dominance for descending states. The `C4/P4` example remains a useful
control: identical top-two entries alone fail, but full prefix dominance rules
out precisely that bad orientation.

## Exact remaining residual for WOWII 61

The unresolved theorem is no longer at `k=2`. It begins at cumulative prefixes
of three or more canonical eliminations:

```text
DegreePrefixDominates source target
  -> for every k>=3,
       cumulativeHeadSum k target <= cumulativeHeadSum k source.
```

One cannot obtain this by naively applying the two-step theorem recursively,
because v0.14 formally refuted preservation of ordinary prefix dominance by a
Havel--Hakimi successor. Later steps require the banked cumulative-head credit
from v0.18, not same-time successor dominance.

The next meaningful target is therefore a three-head analogue that conditions
on the exact second-step endpoint flags while carrying the first-step surplus,
or a direct global characterization of cumulative eliminated heads.

## Verification

New file:

```text
lean/GraphConjecture61DescendingSurvival.lean
```

After compiling the local v0.22--v0.24 import chain, the independent check was:

```text
timeout 60s env LEAN_PATH=/Users/kuber.mehta/Projects/c5-k4/lean \
  lake env lean -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture61DescendingSurvival.lean
```

It exited `0` in 5.73 seconds with no output. The source contains no
`native_decide`, `sorry`, `admit`, or custom axiom. Every subprocess remained
below 60 seconds.

## Verdict

The survival-flag program has succeeded completely at depth two. Descending
order localizes the surviving maximum, bounded saturation converts it into a
multiplicity statement, and full prefix dominance transfers that statement
to the source. WOWII 61's proof-extraction frontier is now genuinely the
multi-step cumulative-credit problem at depth three and beyond.
