# WOWII 181: formalized-reading status, priority, and release audit

Audit date: **2026-08-12 UTC**  
Audit mode: read-only except for this report. No Lean, GitHub, tag, or release
state was changed.

## Decision

**Mathematical result:** `T(7)=L(K_7)` is a valid counterexample to the
explicitly formalized **square-degree reading**

```text
L_s(G) + b(G) >= alpha(G)
  + average_{v in B(G^2)} degree_{G^2}(v).
```

It is **not** a counterexample to the alternative reading that selects
`B(G^2)` but measures those vertices' degrees back in `G`.

**Release posture:** recommend a `c5-k4` release in principle, but only under
an ambiguity-bearing title such as

```text
WOWII Conjecture 181 (formalized square-degree reading):
counterexample and formal certificate
```

and only after the remaining `UPSTREAM_PROTOCOL.md` artifact and preflight
gates are committed. **Do not release it under the unqualified title**
“WOWII Conjecture 181: counterexample and formal certificate,” because the
primary notation does not uniquely force the ambient graph in which degrees
of the square-periphery vertices are measured.

At this audit, immediate release is **NO-GO**: there is no committed 181 source
audit or publication checklist, and the newly added independent verifier
`scripts/verify_wowii_181.py` is still untracked. (The older report names a
`verify_181_T7.py`, which is not present.) The qualified release is
**recommended once those omissions, warning-as-error evidence, axiom audit,
immutable-link checks, and tag preflight are completed**.

## 1. Exact primary wording and current status

The live [complete WOWII list](http://cms.uhd.edu/faculty/delavinae/research/wowII/all.html)
and [open list](http://cms.uhd.edu/faculty/delavinae/research/wowII/open.html)
each contain one entry 181:

```text
O  181. If G is a simple connected graph on at least 2 vertices, then

L_s(G) + b(G) >= alpha(G) + deg_avg(B(G^2)).

Aug 8, 2005.
```

The live menu says `last update 8/6/26`. The site's
[legend](http://cms.uhd.edu/faculty/delavinae/research/wowII/comments.htm)
defines `O` as “open (as far as I know).” Thus the precise status claim is:

> WOWII 181 is still **marked O by the source** as of its 2026-08-06 update.

The marker is a maintainer-knowledge statement, not proof that the problem was
globally unresolved until the present work.

The normalized local row in `data/wowii-conjectures.json` preserves the
wording, date, section (“Lower bounds for `L_s(G)+b(G)`”), and `O` marker.

### Linked definitions

Entry 181 calls `printDefinitions(15,5,23,55,75)` in the live
[definition database](http://cms.uhd.edu/faculty/delavinae/research/wowII/wowIIdefs.js):

- 15: `b(G)` is the maximum number of vertices in an induced bipartite
  subgraph;
- 5: `alpha(G)` is the maximum number of pairwise nonadjacent vertices;
- 23: `deg_avg(G)` is “the average of the degrees of all vertices of the
  graph”;
- 55: `B` is the set of vertices of maximum eccentricity of the graph;
- 75: `G^2` has the same vertices as `G`, with distinct vertices adjacent iff
  their distance in `G` is at most two.

These definitions support treating the graph named inside the expression as
the square: `B(G^2)` is selected in `G^2`, and `deg_avg` is a graph invariant.
This is the **source-natural and campaign gate-preferred** parse. The
family-search gate gives it additional empirical support: it is tight on the
`C_5[K_4]` carrier and many neighboring calibration graphs, whereas measuring
the degrees back in `G` produces large slack.

That evidence does not make the parse textually unique. Definition 55 calls
`B` a set, while definition 23 expects a graph; the source does not explicitly
write either `degree_{G^2}` or `degree_G`, nor does it spell out whether
`B(G^2)` is being regarded as an induced graph. A formal statement must choose
an ambient graph and disclose that choice.

The local Lean choice is

```text
average_{v in B(G^2)} degree_{G^2}(v),
```

not the average degree in the original graph. Calling this the “formalized
square-degree reading” is accurate. Calling it the uniquely “exact intended
reading” is stronger than the source evidence warrants.

## 2. `T(7)` under the two readings

Let `G=T(7)=L(K_7)`, the triangular graph on the 21 edges of `K_7`. It is a
connected strongly regular graph with parameters `(21,10,5,4)` and diameter
two. The certified quantities used by the counterexample are

```text
alpha(G) = 3,
b(G) = 6,
gamma_c(G) = 5,
L_s(G) = 21 - gamma_c(G) = 16.
```

For the formal contradiction, the Lean certificate only needs and proves the
upper bound `L_s(G) <= 16`, together with the exact other values.

Because `diam(G)=2`, its square is `G^2=K_21`. Every vertex is peripheral in
the square.

### Formalized square-degree reading

Every selected vertex has degree 20 in `G^2`, so

```text
LHS <= 16 + 6 = 22,
RHS  = 3 + 20 = 23.
```

The asserted lower bound would require `22 >= 23`. Therefore `T(7)` is a
valid counterexample to this reading.

### Degrees measured back in `G`

The selected set is still all 21 vertices, but each has degree 10 in `G`:

```text
LHS = 16 + 6 = 22,
RHS = 3 + 10 = 13.
```

The inequality holds with slack 9. Hence `T(7)` does not refute this
alternative reading. Any public title, summary, or social claim must retain
the square-degree qualification.

For this particular witness, “average degree of the induced subgraph on the
square periphery” and “average square-degree of the square-periphery vertices”
coincide, since that periphery is all of `V(K_21)`. The witness therefore does
not resolve that secondary distinction for general graphs.

## 3. Priority and recorded history

### Source and literature

No earlier exact disproof or proof of 181 was located in the following targeted
checks performed on 2026-08-12:

- the live WOWII complete/open pages and linked definitions;
- exact/general web searches for `Written on the Wall II Conjecture 181`,
  `WOWII 181`, the displayed formula, and `T(7)` with 181;
- DataCite, Crossref, Zenodo, and arXiv queries for the same identifiers and
  formula fragments;
- `results/literature.md`, which records no 181 result.

The searches returned other WOWII conjectures and irrelevant uses of the
number 181, but no independent 181 resolution. Registry and search-engine
coverage is incomplete, and notation-only observations can be unindexed.
Therefore the defensible wording is:

> No earlier recorded resolution of the formalized square-degree reading was
> located in the targeted audit; it appears to have been unrecorded before
> Kuber Mehta's 2026-08-12 public commit and upstream issue.

Do not shorten this to “the first counterexample,” “previously unknown,” or a
claim of worldwide priority.

### `c5-k4` public record

The complete Lean certificate first appears in public commit
[`3bfa33d7470055a9a11d9ffde29186245dc3a329`](https://github.com/Kuberwastaken/c5-k4/commit/3bfa33d7470055a9a11d9ffde29186245dc3a329),
dated 2026-08-12 18:56:39 UTC. Its immutable
[blob link](https://github.com/Kuberwastaken/c5-k4/blob/3bfa33d7470055a9a11d9ffde29186245dc3a329/lean/GraphConjecture181.lean)
returned HTTP 200 during this audit.

No local or remote `wowii-181*` tag and no `wowii-181-v1` GitHub release
existed at audit time.

### Formal Conjectures history

Kuber Mehta opened
[`google-deepmind/formal-conjectures` issue #4905](https://github.com/google-deepmind/formal-conjectures/issues/4905)
at 2026-08-12 18:57:30 UTC and
[PR #4907](https://github.com/google-deepmind/formal-conjectures/pull/4907)
at 19:29:43 UTC. Both explicitly disclose the reading caveat. The issue is
open; the PR is open, not merged, and is no longer a draft. Its build, test,
copyright, scan, CLA, and related reported checks were successful at audit
time; it had no review or merge.

At upstream `main` commit
[`547f309edcc2069c1f61c2465729031c10385540`](https://github.com/google-deepmind/formal-conjectures/commit/547f309edcc2069c1f61c2465729031c10385540),
there is no `GraphConjecture181.lean` declaration. Focused issue, PR, and code
searches found only #4905/#4907 for the result; unrelated item number 181 is a
false positive. Thus a `c5-k4` release would package an already public result,
not establish a new publication date, and must link the existing issue/PR.

Under the standing protocol, no new upstream issue or PR should be opened.
The existing PR may only be monitored or repaired in response to CI/review.

## 4. Release gate and recommended language

### Scope/novelty assessment

- WOWII 181 is an eligible WoW II problem in the represented collection.
- The square-degree statement has a complete finite counterexample and Lean
  certificate, rather than a bounded search signal.
- The source/status/readings have now been audited, but this report still needs
  to become a logical committed checkpoint.
- No earlier independent result was located, subject to the “apparently
  unrecorded” qualification above.
- The proposed tag `wowii-181-v1` is currently absent.

### Missing publication artifacts

Before release, the protocol still requires:

1. commit this source/readings/status audit;
2. identify a committed proof/discovery report for 181;
3. review and commit the current `scripts/verify_wowii_181.py` independent
   verifier; it passed locally during this audit, checking the exact `T(7)`
   values, both degree readings, and 995 connected Atlas graphs, but remained
   untracked at the audit snapshot. Reconcile the stale `verify_181_T7.py`
   filename in `results/family_forest.md`;
4. commit warning-as-error and exact axiom/trust audit evidence for the final
   certificate revision;
5. add the required `results/expansion/publication/` checklist, resolve the
   release SHA with `git rev-parse`, verify every planned immutable URL by
   HTTP and content, and recheck local/remote tags.

The green upstream CI is useful corroboration but does not substitute for the
campaign's committed release preflight.

### Recommended release claims

Use:

> Under the explicitly formalized reading in which degrees of the periphery
> of `G^2` are measured in `G^2`, WOWII 181 is false. The Lean-certified
> counterexample is `T(7)=L(K_7)`, for which the proposed inequality becomes
> `22 >= 23`. The live source still marks 181 `O`. No earlier recorded
> resolution of this reading was located in our targeted audit.

Also state immediately:

> If the same selected vertices' degrees are instead measured in `G`, this
> witness gives `22 >= 13` and is not a counterexample.

Avoid:

- “the exact intended reading” without the square-degree qualifier;
- “WOWII 181 is unambiguously false”;
- “first counterexample,” “newly disproved,” or “previously unrecorded” without
  the dated, search-limited qualification;
- implying that the release predates the public commit, issue, or PR;
- implying upstream acceptance while PR #4907 remains open.

## Bottom line

**Recommend the qualified `c5-k4` release after the missing artifact/preflight
gates are satisfied. Deny an immediate release and deny any unqualified WOWII
181 counterexample title.** This preserves the real result—an apparently
unrecorded, fully formalized counterexample to the square-degree parse—without
turning a genuine source ambiguity into an inflated claim.
