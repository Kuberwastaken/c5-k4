# Erdős 184 Phase-0 source/status contract

Audit time: **2026-08-13T11:11:51Z**
Outcome: **STRICT_STOP_THEOREM_CLOSED_VARIANT_AND_UNBOUNDED_MAIN**
Scope: source/status only; no family is frozen or evaluated.

## Source lock

Current upstream `google-deepmind/formal-conjectures` `main` was resolved by
`git ls-remote` and read from an isolated depth-one clone at
`d16e05aded22b8c467a0a27c14b2311f53185006`.

- Lean source: [`FormalConjectures/ErdosProblems/184.lean`](https://github.com/google-deepmind/formal-conjectures/blob/d16e05aded22b8c467a0a27c14b2311f53185006/FormalConjectures/ErdosProblems/184.lean),
  Git blob `374dbab4aedf0e82c2b13d4efcf3fe58d8079ec3`, SHA-256
  `a059dafb84d739ec6d148462fc0aa6d132a1c6bc17fbbaa3438e2d0c33f57953`.
- `answer()` semantics: [`FormalConjecturesUtil/Answer.lean`](https://github.com/google-deepmind/formal-conjectures/blob/d16e05aded22b8c467a0a27c14b2311f53185006/FormalConjecturesUtil/Answer.lean),
  Git blob `1ef64b8c99fa0af0a89cb02100da3df2b25eaf91`, SHA-256
  `c8b3b31e9bb25c511e577b1812159a210e9346720f19ec6c6b30905a0802db7a`.
- The community status database `teorth/erdosproblems` current `main`
  `eb73c078b5c94ed3b31db5c7adfe95be0dc42d22` records problem 184 as `open`
  (status last updated 2025-08-31) and formalized (updated 2026-03-16).

The direct website returned a Cloudflare challenge in this headless session;
the versioned public data repository is therefore the reproducible status
source.

## Exact readings

### Reading A: edge-disjoint decomposition — live and unambiguous

`erdos_184` states directly, with no answer placeholder:

> There exists `f : Nat -> Real` with `f = O(n)` such that every finite simple
> graph `G` admits a finite set `D` of subgraphs, pairwise edge-disjoint and
> covering `G.edgeSet`, each member a connected 2-regular graph or a one-edge
> graph, with `|D| <= f(|V(G)|)`.

This is the positive Erdős--Gallai cycle-decomposition conjecture. The
quantification over one global big-O function makes it an asymptotic/uniform
statement. No finite bounded list of graphs can disprove it: a finite list can
always be absorbed into the constant implicit in `O(n)`.

Classification: **UNAMBIGUOUS, RESEARCH OPEN, NOT BOUNDEDLY FALSIFIABLE**.

### Reading B: non-disjoint covering by at most `n-1` pieces — positive orientation but theorem-closed

`erdos_184.variants.covering` has the literal shape

```text
answer(sorry) <-> forall nonempty finite G,
  exists D,
    every H in D is a cycle or one-edge graph
    and union(H.edgeSet) = G.edgeSet
    and |D| <= |V(G)| - 1.
```

The repository option `google.answer` defaults to `.alwaysTrue`; its elaborator
explicitly replaces proposition-valued `answer(sorry)` by `True`. Thus the
compiled default statement is definitionally oriented as

```text
True <-> covering_property,
```

not as an unknown Boolean and not as a negative answer. Operationally, proving
the theorem requires the positive covering property. The `answer` annotation
still marks a human answer slot and does not itself certify that the answer is
unknown.

That positive property is already a theorem. Pyber's 1985 paper
[*An Erdős--Gallai conjecture*](https://doi.org/10.1007/BF02579444) states in
its abstract that every `n`-vertex graph can be covered by `n-1` circuits and
edges. Bucić and Montgomery's primary research paper
[*Towards the Erdős-Gallai Cycle Decomposition Conjecture*](https://arxiv.org/abs/2211.07689v2),
Introduction, “Covering problems,” likewise says that Pyber proved the covering
version in 1985 with exactly `n-1` cycles and edges.

Classification: **FORMALIZED_POSITIVE_READING, RESEARCH SOLVED SINCE 1985**.
The upstream `@[category research open]` tag and `answer(sorry)` are stale for
this variant. This audit makes no upstream correction because no public action
was authorized.

## Primary-literature audit

1. L. Pyber, *An Erdős--Gallai conjecture*, Combinatorica 5 (1985), 67--79,
   DOI `10.1007/BF02579444`: proves the exact covering statement represented by
   Reading B.
2. M. Bucić and R. Montgomery, *Towards the Erdős-Gallai Cycle Decomposition
   Conjecture*, arXiv:2211.07689v2 (2023): calls Reading A a major open problem,
   proves the current `O(n log* n)` general decomposition bound, and explicitly
   records Pyber's theorem for Reading B. The downloaded PDF was text-based,
   had no OCR gaps, and had SHA-256
   `609d9697be408af76e1026951c2480deae9d35780f18f9ba887da10f38c1dfef`.
3. P. Erdős, *Some unsolved problems in graph theory and combinatorial
   analysis* (1971): the source scan was located at the Rényi Institute, but
   all eight pages require OCR and were not readable with the mandated local
   PDF parser. No wording is attributed directly to that scan in this audit.
   The orientation is instead independently fixed by Pyber's theorem and the
   Bucić--Montgomery literature account.

## Live issue and pull-request audit

GitHub searches covered `Erdős/Erdos Problem 184`, the source path,
`Erdős-Gallai`, `cycle decomposition`, `Pyber`, `n-1 cycles and edges`, and
`covering version`.

- [Issue #410](https://github.com/google-deepmind/formal-conjectures/issues/410)
  requested the open linear edge-disjoint conjecture and is closed.
- [PR #2287](https://github.com/google-deepmind/formal-conjectures/pull/2287)
  added the current module and merged on 2026-03-16.
- No open issue or PR specifically addressing Erdős 184, the covering variant,
  or its stale status was found as of the audit timestamp.

Issue #184 returned by number/text searches is unrelated (“Hall's
conjecture”) and is not evidence about Erdős problem 184.

## Local `c5-k4` coverage

Before this Phase-0 contract, exact searches found Erdős 184 only in:

- `results/expansion/formal_conjectures.md`, where both declarations were
  enumerated and excluded from fixed-arsenal evaluation as requiring unbounded
  auxiliary search; and
- `results/expansion/current_finite_graph_target_ranking_20260813T110249Z.*`,
  where the cluster was ranked but explicitly not selected or evaluated.

There is no Erdős-184 constructor, development ledger, result, certificate, or
local theorem. Generic mentions of cycle decomposition in unrelated WOWII
proof lanes do not cover this target.

## Strict stop

```text
PHASE0_OUTCOME = STRICT_STOP
selected_declaration = null
selected_direction = null
family_frozen = false
family_evaluated = false
```

Reasons:

1. The bounded, exact-looking covering direction is theorem-closed by Pyber
   (1985), so a development trial would be prior-art work against a stale
   source category.
2. The genuinely live edge-disjoint declaration is an asymptotic `O(n)`
   statement. A bounded family/grid cannot falsify it and therefore cannot
   produce a Method-valid negative residual under the requested bounded round.

The only unambiguous live mathematical direction is Reading A, but it belongs
in an asymptotic proof/improvement programme, not this prospective bounded
family round. Erdős 184 is removed from the next-round queue; ranking should
advance to the next untouched cluster.

No graph family was frozen or evaluated, and no commit, push, issue, PR,
release, or other public action was performed.
