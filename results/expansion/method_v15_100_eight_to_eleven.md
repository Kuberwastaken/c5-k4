# Method v0.15 — WOWII 100, independence eight through eleven

Date: 2026-08-13  
Outcome: `PARTIAL_THEOREM`  
Formal artifact: `lean/GraphConjecture100EightToEleven.lean`

## Reading warning

This proves the exact upstream Lean expression using `degreeL2Norm Gᶜ`. The
upstream prose instead discusses complement diameter. The two readings must
remain visibly separated.

## Integration

Let `S` be a maximum independent set and choose `s in S`. Connectedness gives
a `G`-neighbor `y` of `s`, necessarily outside `S`. Let `t` be the number of
complement attachments from `y` into `S`.

The proof splits exactly where the preceding development predicts:

### Zero attachment

If `t=0`, the v0.12 one-witness tradeoff gives `L>=|S|` and its exact finite
margin closes every value `8<=|S|<=11`.

### Positive attachment

If `t>0`, choose an attached `r in S`. The v0.14 connectedness lemma supplies
a second distinct outside cross-edge witness `z`. Its attachment count `u` and
the original count both satisfy `t,u<=|S|-1`. The v0.14 graph theorem supplies
the exact aggregate energy certificate

```text
q^2 >= a(a-1)^2 + (2a-1)(t+u) + t^2+u^2.
```

The two nonattachment sets give `L>=a-min(t,u)`. The exact v0.13 coordinate
optimization then crosses the residual for every pair of counts when
`8<=a<=11`.

## Formal result

The final warning-clean theorem is:

```text
G.Connected -> 8 <= alpha(G) -> alpha(G) <= 11 ->
alpha(G) <= ceil((L + degreeL2Norm(Gᶜ)/2)/2).
```

Complement connectedness is unnecessary. The file also retains the explicit
zero-attachment branch as an API lemma.

The finite optimizer is included locally because generating an object file for
the earlier optimizer module approached the fixed subprocess wall-clock cap;
the proof is mathematically identical and remains exact. It uses neither
`native_decide` nor an external oracle.

## Verification

With v0.8--v0.12 and v0.14 dependencies compiled into a temporary module path:

```bash
LEAN_PATH=/tmp/c5k4-proof100-8to11 timeout 60s lake env lean \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture100EightToEleven.lean
```

The checker completed within the mandatory 60-second wall-clock cap with no
diagnostics. The artifact contains no `native_decide`, `sorry`, `admit`, custom
axiom, or diagnostic command.

## Updated residue

Combining v0.9--v0.15 closes the exact degree-norm reading for

```text
alpha(G) in {2,3} or alpha(G)>=8.
```

The remaining connected independence range is now exactly

```text
4 <= alpha(G) <= 7.
```

The v0.13 negative audit already shows that two witnesses are not uniformly
enough there. The next honest move is an aggregate three-witness theorem or a
connectedness constraint that rules out the worst two-witness coordinates.
