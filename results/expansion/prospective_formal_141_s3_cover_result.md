# WOWII #141 nonabelian `S3` permutation-lift result

Date: 2026-08-13 UTC

Frozen contract SHA-256:
`48975702b8a4dc91fa37f79e088eb5df23131ef31d11a0d8ccd1e90c3ff9669d`

## Verdict

`NO_APPLICABLE_CANDIDATES`

The exact frozen `S3` constraint system is infeasible.  No permutation lift
was constructed, so the candidate cover/local-independence/girth gates and
induced-tree decision oracle were correctly not entered.  There was no
crossing, status audit, commit, or public action.

## Database gate

The lane independently reran the complete parent gate before solving any
permutation assignment:

```text
controls = 1057, failures = 0, timeouts = 0.
```

Every row retained exact girth, all neighborhood-independence values, exact
maximum induced-tree order, and a replayed tree witness.  The residual-one
seed was again reproduced as

```text
tree = 8, girth = 4, lambda_max = 6, target = 7, residual = 1.
```

## Exact nonabelian solver outcome

After BFS gauge fixing, the seed has 31 cotree permutation variables and 423
simple cycles of length four or five.  Domains initially contain all six
elements of `S3`.  Every short-cycle product was required to be one of the two
fixed-point-free 3-cycles.

The deterministic generalized-arc-consistency solver exhausted the frozen
system in 0.063 seconds:

```text
states = 3, cache entries = 529, status = infeasible.
```

This is an exact finite-domain exhaustion, not a relaxed or numerical solver
result.

## Reduction certificate: why noncommutativity cannot help

The follow-up audit exposes the obstruction completely.

For every one of the 31 cotree edges, the lexicographic BFS tree contains a
fundamental base cycle of length four or five using that cotree edge and only
tree edges otherwise.  Its cycle-product constraint therefore contains a
single nonidentity variable.  Requiring that product to be fixed-point-free
forces the variable itself to be one of

```text
(0 -> 1 -> 2 -> 0),  (0 -> 2 -> 1 -> 0).
```

Thus all 31 cotree permutations are forced into

```text
A3 = {identity, the two 3-cycles} isomorphic to Z3.
```

The audit checked all 31 singleton constraints, closure of the forced subgroup,
and commutativity.  It passed exactly.  Once every edge permutation lies in
`A3`, the supposedly nonabelian lift is precisely a cyclic `Z3` voltage lift,
whose 423-constraint system the parent lane independently proved infeasible.

This explains the three-state search: root propagation restricts every domain
to the two 3-cycles; the two possible ranks of the first cotree edge both
immediately lead to contradiction.

## Reusable obstruction

Moving from cyclic voltages to arbitrary `S3` edge permutations does not add a
usable degree of freedom for this seed.  The short fundamental cycles force
every local monodromy into the cyclic normal subgroup before longer-cycle
constraints are considered.

Any further cover experiment seeking genuinely nonabelian behavior must alter
at least one of:

- fiber size/group, so fixed-point-free elements are not confined to a cyclic
  subgroup;
- gauge/tree geometry, through a different seed whose short fundamental
  cycles do not isolate every cotree variable; or
- the demand to eliminate every 4-/5-cycle simultaneously.

The last option would no longer perform the frozen girth separation and would
need a new prospective contract.  Nothing here is evidence against WOWII #141;
it is exact evidence that this second cover mechanism cannot reach the wall.

## Artifacts

- Frozen addendum:
  `results/expansion/prospective_formal_141_s3_cover_contract.md`
- Append-only 1,063-line ledger:
  `results/expansion/prospective_formal_141_s3_cover_ledger.jsonl`
- Exact solver and reduction audit:
  `scripts/prospective_formal_141_s3_cover.py`

No commit, push, release, issue, PR, or other public action was made by this
lane.
