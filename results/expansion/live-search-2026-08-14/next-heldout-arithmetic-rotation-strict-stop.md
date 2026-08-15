# Next held-out arithmetic/combinatorics rotation: strict stop

**Audit date:** 2026-08-14 UTC  
**Disposition:** `STRICT_STOP_EMPTY_QUALIFIED_SET`  
**qualified_target_count:** `0`

This artifact records a source/status scout only. It did not evaluate a target
instance, select or freeze a target, run a search, create a workflow, produce a
candidate, or authorize a release or upstream action.

## Exact chronology and pins

The local audit was performed from repository commit

```text
6a80fcdcb0489dc196162554cd4fec4f41ad2187
```

on branch `catchup-parity-packed-freeze`. Unrelated, pre-existing Bondy
development edits were present in the shared worktree and were not read as
arithmetic evidence, modified, staged, or otherwise touched by this audit.

The GitHub commits API resolved `google-deepmind/formal-conjectures` `main` to

```text
commit  2411d22e1bd550d050d0eac6c1fb379a76a3e7c5
tree    f6b52f1d3f63b365d6f8c405623d5f7a4e674efc
date    2026-08-14T19:16:38Z
message Disprove WOWII 59 (#4574)
```

The most recent committed arithmetic scout used upstream pin
`6c0950bec7743f5098c0196c6aee7b22c1ec8005`. GitHub's compare endpoint reports
exactly eight commits from that pin to the current pin. The only newly added
OEIS module in that delta is `OEIS/303639.lean`, whose declarations were added
already tagged `research solved` with a public counterexample. The other new
finite module is the already exposed Bondy DEVELOPMENT lane; Erdős 506 is
added as a resolved statement. The remaining changes are resolutions,
variants, metadata, or docstrings. No new open arithmetic/combinatorics
counterexample lane enters through this delta.

For independent Erdős status, `teorth/erdosproblems` `main` resolved to

```text
commit  3cbe2cffad0267952de3523089549009ea6fe5dc
tree    f7932ab6470b175d527155029193ab245885057b
date    2026-08-14T22:13:30Z
```

These are point-in-time pins, not a promise about later upstream state.

## Why the qualified set is necessarily empty

Method v1.4's sole frozen registry build is terminal. Its preserved result at
[`results/benchmark/v1.4-f0a/README.md`](../../benchmark/v1.4-f0a/README.md)
records:

```text
registry population                         728 open question clusters
eligible after exact S0 contamination replay 0
terminal code NO_ELIGIBLE_BENCHMARK_PRE_C0
clusters selected                            0
```

Method v1.5 does not reinterpret those 728 clusters as held out. Its protocol
at [`METHOD_V1_5_BENCHMARK.md`](../../../METHOD_V1_5_BENCHMARK.md) defines the
new confirmatory population as clusters first introduced strictly after a
public P1 freeze. The same document records that no P1 freeze, U1 capture,
future-cohort observation, entropy, selection, or target-semantic inspection
has occurred. Consequently:

1. every declaration already present is in the exhausted pre-P1 population;
2. no valid post-P1 population exists yet; and
3. the eight-commit live delta cannot retroactively create held-out status,
   because it also precedes P1 and in any event adds no eligible open lane.

Returning a nonempty ranking would require relaxing chronology or
contamination after seeing the zero. The method forbids that move.

## Rejected diagnostic near-targets

These entries explain tempting false positives. They are not a fallback
ranking and do not authorize evaluation.

### Erdős 375 / Grimm's conjecture

- Current target:
  `FormalConjectures/ErdosProblems/375.lean::Erdos375.erdos_375`, still
  `research open` at the pinned DeepMind tree.
- Literal finite obstruction: a composite block whose position-to-prime-factor
  bipartite graph contains a Hall-deficient subset `S` with
  `|N(S)|-|S|<0`.
- Tempting transfer: place more selected consecutive integers than available
  primes inside one smooth/S-unit support set.
- Rejection: this cluster occurs in the frozen 728-cluster pre-P1 registry and
  is explicitly `eligible: false` after production contamination
  intersection. The source page records verification through
  `n <= 1.9 * 10^10`; a later public computational claim reports `10^11`.
  More decisively, Laishram--Murty, *Grimm's Conjecture and Smooth Numbers*
  (arXiv:1306.0765), Lemma 2.4 already uses the same pigeonhole transfer from
  too many smooth numbers in a short interval to failure of prime
  representation. The proposed family is therefore neither held out nor a
  clean structural novelty. The separate DEVELOPMENT preflight records its
  strict stop.

### OEIS A232174, A239957, and A280831

All three remained syntactically open when first noticed, but exact local
provenance searches found target-specific prior campaigns in the sibling
`breakthroughmaxxing` repository:

- A232174 was exhaustively checked through `100000`;
- A239957 was checked through `10000000`, with a reported sharp witness at
  `p=6922081`, `k=51`;
- A280831 was checked through `100000`, including a sharp cutoff campaign.

They fail the local duplicate/source-bound gate and cannot be relabelled as
held out.

### OEIS A281976, A287616, A303656, A306477, and A308734

Upstream pull requests #3394--#3398 publicly claim solutions for this group.
The exclusion rule covers claimed resolutions in pull requests even when a
declaration or merge state has not yet caught up. These are not unclaimed
targets.

### Erdős 287

The attractive wall coordinate reduces the maximum allowed denominator gap
to a word over gaps `{1,2}`. Public target-specific work already reports exact
computation through `k <= 18` and a large gap-word search. A new search in the
same grammar would be duplicate/source-bound, not a separating transfer.

### Erdős 458

The prime-power-basis/product identity gives a genuine structural wall, but
the public problem discussion already states that mechanism and reports
verification through `10^20`. The exact proposed geometry is publicly
occupied.

### Kurepa's left-factorial conjecture

Public records report verification for primes below `2^40`. No construction
was found that changes the residue sign or reaches a violation independently
of flat prime scanning. It fails both the source-bound and
crossing-reachability gates.

### Erdős 488

The public discussion contains extensive structured families and competing
readings of the exact multiples/nonmultiples statement. With no frozen source
resolution of that ambiguity and no unoccupied wall transfer, the
resolution-shape and duplicate gates fail before computation.

### Other already closed local lanes

The current rotation reports already exhaust or stop A063880, A105720,
A105565, A108081, A231201, A056777, A067720, A108569, A109908/A109909,
A103151, Erdős 373's earlier source-bound lane, equation `677 -> 255`,
2-increasing tuples, Barker sequences, Catch-Up, and prior finite
graph/algebra campaigns. None may be recycled into a held-out ranking.

## Terminal state and reopening condition

```text
qualified_target_count = 0
ranked_targets         = []
selected_target        = null
target_instances_read  = 0
candidate              = null
workflow_dispatched    = false
release_authorized     = false
upstream_action        = false
```

The next strict held-out arithmetic/combinatorics rotation may reopen only
after a valid Method v1.5 P1 activation and U1 capture, followed by a genuinely
new upstream cluster inside the authenticated future cohort. A DEVELOPMENT
scout may proceed under its own label, but it is not confirmatory held-out
evidence.

