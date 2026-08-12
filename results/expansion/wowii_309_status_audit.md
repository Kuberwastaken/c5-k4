# WOWII 309 source, status, priority, and publication audit

Audit date: **2026-08-12 UTC**  
Audit mode: read-only except for this report; no Lean edit, commit, push, issue,
PR, or other GitHub write was made.

## Publication verdict

`C₅[K₄]` is a valid and very strong counterexample to the exact primary-source
reading of WOWII 309. The exact values are

```text
gamma_t(C₅[K₄]) = 3,
max_v (dist_even(v) - even_horizontal(v)) = 9 - 28 = -19,
min_{e in E(complement G)} |N_{complement G}(e)| = 16,
```

so the conjectured upper bound is `(-19 + 16)/2 = -3/2`, and the claimed
inequality is `3 <= -3/2`, which is false.

This is **not a new disproof**. Jonas J. Gebendorfer publicly recorded the
stronger family `C₅[K_k]`, `k >= 3`, on 2026-07-25 in
[*An Infinite Family of Counterexamples to Written on the Wall II, Conjecture
309*](https://doi.org/10.5281/zenodo.21553295). That note includes the smaller
15-vertex witness `C₅[K₃]`, for which the proposed inequality is `3 <= 2`.
The note explicitly credits Kuber Mehta's 2026-07-23 public use of the
`C₅[K₄]` carrier for the distinct WOWII conjectures 63 and 85, while identifying
309 as a new application of that carrier.

The correct public posture is therefore:

> Formalize/certify Gebendorfer's recorded disproof of WOWII 309, using
> `C₅[K₄]` as a convenient Lean witness and crediting both the prior 309 result
> and the earlier carrier provenance.

Do **not** describe a future issue or PR as discovering, newly disproving, or
having priority for Conjecture 309. The live WOWII page still displays `O`, but
that source marker is stale relative to the dated Zenodo record.

## 1. `UPSTREAM_PROTOCOL.md` scope gates

| Gate | Result | Evidence / qualification |
|---|---|---|
| Existing problem from a represented collection | **yes** | WOWII is represented by many files in `FormalConjectures/WrittenOnTheWallII/`. |
| Written on the Wall II | **yes** | The primary row is WOWII 309, not WoW I or Graph Brain. |
| No current upstream duplicate | **yes, as of audit** | At upstream `main` commit [`547f309edcc2069c1f61c2465729031c10385540`](https://github.com/google-deepmind/formal-conjectures/commit/547f309edcc2069c1f61c2465729031c10385540), there is no `GraphConjecture309.lean`, declaration, focused issue, or focused PR. Searches are recorded below. |
| Primary source/status/readings audited | **yes** | Raw live `all.html`, `open.html`, and `wowIIdefs.js` were inspected; the complement overline and all five definition IDs were checked. |
| Complete result, not a theorem signal | **yes mathematically** | Gebendorfer gives a closed-form proof for every `C₅[K_k]`, `k >= 3`; the concrete `k=3` and `k=4` values were independently recomputed here. |

The scope gate permits a contribution whose claim is **formalization of an
already recorded disproof**. It does not permit a novelty claim.

This report is not the required publication preflight checklist. The artifact
and immutable-link gates still require their own committed evidence before any
public write: a warning-as-error build, axiom/trust audit, full immutable SHA
resolved with Git, HTTP-200 and content checks, and the canonical issue/PR body
layout. The current local Lean certificate contains no `sorry`, but build and
trust verification are deliberately not inferred from source inspection in
this report.

## 2. Exact primary source and status

The live primary materials inspected on 2026-08-12 were:

- [complete WOWII list](http://cms.uhd.edu/faculty/delavinae/research/wowII/all.html);
- [open list](http://cms.uhd.edu/faculty/delavinae/research/wowII/open.html);
- [definition database](http://cms.uhd.edu/faculty/delavinae/research/wowII/wowIIdefs.js);
- [menu](http://cms.uhd.edu/faculty/delavinae/research/wowII/menu.htm),
  which says `last update 8/6/26`;
- [status legend](http://cms.uhd.edu/faculty/delavinae/research/wowII/comments.htm),
  which defines `O` as “open (as far as I know).”

The complete list contains one row 309 under **Upper bounds for Total
Domination**. Its raw HTML says:

```text
O  309. If G is a simple connected graph such that n(G) > 2, then

gamma_t(G) <= (1/2) * [
  maximum { dist_even(v) - even horizontal(v) : v in V(G) }
  + minimum of |N_{complement G}(e)|
].

Mar. 1, 2007.
```

The important DOM fragment is
`N<sub><span style="text-decoration: overline">G</span></sub>(e)`:
the overline is on the graph in the subscript, not on `e`.

The row links `printDefinitions(94,10,93,28,31)`:

- 94: total domination number `gamma_t`;
- 10: `dist_even(v)`, the number of vertices at even distance from `v`;
- 93: `even horizontal(v)`, the number of edges whose endpoints are at the
  same even distance from `v`;
- 28: neighborhood of an edge `e=(u,v)`, defined for adjacent `u,v` as the
  vertices adjacent to at least one endpoint;
- 31: the complement graph.

The local normalized record in `data/wowii-conjectures.json` preserves this
statement, hypothesis, date, and `O` marker correctly.

The generated `open.html` copy drops `n(G)>2` and some absolute-value markup,
while the complete `all.html` retains them. This appears to be abbreviated or
malformed list generation, not a substantive alternative statement. The
complete list is the safer verbatim source. It does not affect `C₅[K₄]`, which
has 20 vertices and satisfies either displayed hypothesis.

The current source status and mathematical status must be distinguished:

- **source-maintained status:** `O` as of the live page updated 2026-08-06;
- **known mathematical status:** false, with a dated public disproof from
  2026-07-25.

Thus “currently marked open on WOWII” is accurate only with the qualifier
“marked”; “currently open” is not an accurate literature-status claim.

## 3. Exact complement-neighborhood reading

The notation in 309 is `N_{complement G}(e)`, not
`N_G(complement e)`. The site's definitions distinguish these explicitly:

- definition 8 uses `N_G(overline e)` for the neighborhood **in `G` of a
  nonedge of `G`**;
- row 309 instead links definitions 28 and 31 and prints
  `N_{overline G}(e)`.

Composing definitions 28 and 31 gives the natural literal reading used by the
priority paper:

```text
e ranges over E(complement G), and
N_{complement G}(e) = N_{complement G}(x) union N_{complement G}(y)
for e = xy.
```

The two endpoints are included. Since `x` and `y` are adjacent in the
complement, each is adjacent to the other and therefore belongs to the union
specified by definition 28. This is why the exact `C₅[K₄]` value is 16 rather
than 14.

The source does not print the range `e in E(complement G)` inline, but it is
forced by definition 28 (“such that `u` and `v` are adjacent in the graph”)
applied to the graph named in the subscript. Gebendorfer's note makes this
range explicit.

There is one genuine source-domain wrinkle: if `G` is complete, its complement
has no edge, so the displayed minimum is undefined. An `Option`-valued Lean
definition with a vacuous proposition in the `none` case is a reasonable total
extension, but it is a formalization choice rather than text printed by WOWII.
It is irrelevant to the counterexample because the complement of `C₅[K₄]`
has 80 edges. A public statement should disclose the choice instead of silently
claiming the source handled the empty minimum.

## 4. Independent `C₅[K₄]` witness audit

Let `G=C₅[K₄]`, with five four-vertex clique fibers `F_0,...,F_4` and complete
joins between consecutive fibers.

### Hypotheses

`G` is a finite simple connected graph with 20 vertices, 110 edges, and degree
11 at every vertex. Hence it satisfies the source's `n(G)>2` hypothesis.

### Total domination

One vertex from each of `F_0,F_1,F_2` forms a totally dominating set and
covers all five fibers. No one-vertex set totally dominates a simple graph.
For a two-vertex set:

- two vertices in one fiber miss both fibers at cyclic distance two;
- vertices in consecutive fibers miss the fiber at cyclic distance two from
  both;
- vertices in nonconsecutive fibers are nonadjacent, so the selected vertices
  do not dominate one another.

Therefore `gamma_t(G)=3`.

### Even-distance correction

For `v in F_i`, the even-distance vertices are `v` itself (distance zero) and
the eight vertices in `F_{i-2} union F_{i+2}` (distance two), so
`dist_even(v)=9`. Those two distance-two fibers are consecutive on the
underlying 5-cycle; together they induce `K_8`. The distance-zero layer has
only `v`. Therefore

```text
even_horizontal(v) = |E(K_8)| = 28,
dist_even(v) - even_horizontal(v) = -19.
```

This is constant over all vertices, hence the maximum is `-19`.

Distance zero is even, so the primary definition includes `v`. Even if one
used the nonliteral convention excluding `v`, the correction would decrease
to `-20` and the violation would remain.

### Complement-edge minimum

The complement has five independent fibers, with complete joins between the
fiber pairs at cyclic distance two; it is isomorphic, after relabeling the
5-cycle, to `C₅[overline K₄]`. For every complement edge `xy`, the union of the
two complement neighborhoods consists of exactly four fibers. Hence every
value is 16 and the minimum is 16.

Combining the terms gives

```text
RHS = (1/2) * (-19 + 16) = -3/2,
gamma_t(G) = 3 > -3/2.
```

An independent finite enumeration reproduced `gamma_t=3`, the constant tuple
`(dist_even, even_horizontal, difference)=(9,28,-19)`, 80 complement edges,
and complement-neighborhood minimum/maximum both 16. It also reproduced the
paper's smaller `C₅[K₃]` values `(7,15,-8)`, minimum 12, and RHS 2.

For robustness only—not as substitutes for the exact parse:

- excluding the two edge endpoints gives 14 and RHS `-5/2`;
- taking the neighborhood in `G` of a nonedge gives 18 and RHS `-1/2`;
- excluding `v` from `dist_even(v)` makes the bound smaller again.

Thus no nearby convention saves the statement on `C₅[K₄]`, although the
published formalization should use the exact value 16.

## 5. Recorded disproof and priority

The decisive prior record is:

- Jonas J. Gebendorfer,
  [*An Infinite Family of Counterexamples to Written on the Wall II,
  Conjecture 309*](https://zenodo.org/records/21553295),
  version DOI [`10.5281/zenodo.21553295`](https://doi.org/10.5281/zenodo.21553295),
  concept DOI `10.5281/zenodo.21553294`.
- Zenodo/DataCite creation time: `2026-07-25T10:54:38Z`; publication date:
  2026-07-25; sole author: Jonas Jakob Gebendorfer.
- The deposited PDF checksum is
  `md5:3557268111649e7a246f3ebc4f5a5045`.

The four-page PDF was downloaded from the Zenodo record and inspected in full.
It is text-based with confidence 1.0, has no pages needing OCR, and reports no
encoding issue. It proves in closed form that every `C₅[K_k]`, `k>=3`, is a
counterexample; gives the concrete graph6 encoding and exact values for
`C₅[K₃]`; discusses the complement-neighborhood and distance-zero conventions;
and makes no order-minimality claim.

The paper's chronology is careful and should be preserved. Kuber Mehta's
[issue #4590](https://github.com/google-deepmind/formal-conjectures/issues/4590)
publicly used `C₅[K₄]` on 2026-07-23 for Conjectures 63 and 85. Neither that
issue nor the later merged [PR #4592](https://github.com/google-deepmind/formal-conjectures/pull/4592)
mentions 309, total domination, or even-horizontal edges. Gebendorfer cites
that carrier use and claims only the new 309 application. Accordingly:

- Mehta has the earlier public carrier/campaign record cited by the paper;
- Gebendorfer has the located public priority for the disproof of 309 and the
  `C₅[K_k]`, `k>=3`, family;
- the current `C₅[K₄]` Lean certificate is a later formal certification of
  that known 309 result.

Targeted DataCite search for `"Conjecture 309"` returned the version and concept
records above. OpenAlex indexes the same work. Exact-title, formula,
conjecture-number, arXiv, web, scholarly-web, and repository searches found no
earlier 309 resolution, but absence from those indexes is not a proof of global
priority. It is unnecessary to establish global absence here: the July 25
record alone is sufficient to defeat any new-discovery claim now.

## 6. Upstream duplicate audit

Audit baseline:
[google-deepmind/formal-conjectures `main` at `547f309edcc2069c1f61c2465729031c10385540`](https://github.com/google-deepmind/formal-conjectures/tree/547f309edcc2069c1f61c2465729031c10385540).

Read-only searches performed on 2026-08-12:

| Surface | Queries | Result |
|---|---|---|
| Upstream tree | paths matching `WrittenOnTheWallII/*309*`, `GraphConjecture309`, `309.lean` | no file |
| Repository issues | `"Conjecture 309"`, `"WOWII 309"`, `GraphConjecture309`, `"even horizontal"`, `"21553295"` | no focused issue |
| Repository PRs | same five queries | no focused PR |
| Repository code | `GraphConjecture309`, `conjecture309`, `evenHorizontal` | no declaration or implementation |
| Global GitHub code | `GraphConjecture309`, `conjecture309Statement`, `"WOWII 309"` | no indexed copy |

Three repository search hits were manually read and rejected as false
positives:

- [issue #309](https://github.com/google-deepmind/formal-conjectures/issues/309)
  is “Erdős Problem 80”; its number is coincidental;
- [PR #1844](https://github.com/google-deepmind/formal-conjectures/pull/1844)
  cites page 309 of an unrelated reference;
- [PR #3820](https://github.com/google-deepmind/formal-conjectures/pull/3820)
  has an unrelated `+309` diffstat/comment context and does not include WOWII
  309 in its enumerated conjectures.

Therefore the current upstream duplicate gate is clear, despite the external
literature priority. The local `c5-k4/lean/GraphConjecture309.lean` is not an
upstream declaration and does not change that conclusion.

## 7. Local metadata discrepancies

`corpora/graffiti_pc_wow2.json` contains `wow2-309` and `wow2-309(2)` under
unrelated matching-number and independence-number sublists. The live complete
primary page contains one 309 row under total domination. These are scraper
duplication/sublist-attribution artifacts, consistent with the acquisition
warning that sublist attribution is approximate. They do not create alternate
source statements and should not be cited as such.

The normalized `data/wowii-conjectures.json` record has the correct total-
domination section and formula. Its `status: open`, `in_formal_conjectures:
false`, and `lean_file: null` describe the source marker and current upstream
inventory, not the current mathematical literature status.

## 8. Required wording and next gate

A future upstream submission may accurately say:

> WOWII 309 is still marked `O` on the source page but was disproved by
> Gebendorfer (2026), who proved that `C₅[K_k]` is a counterexample for every
> `k>=3`. This contribution formalizes the disproof in Lean using the
> `C₅[K₄]` member, following the carrier used publicly in the earlier
> Conjecture 63/85 certification.

It should not say “we disprove,” “new counterexample,” “previously open” without
the source-marker qualification, or imply that `C₅[K₄]` is the smallest known
witness. `C₅[K₃]` is smaller and already recorded.

Before any public write, create the separate committed preflight required by
`UPSTREAM_PROTOCOL.md`; verify the exact certificate commit with `git
rev-parse`; confirm all immutable URLs return HTTP 200 and contain the intended
file; run the warning-as-error target build and exact axiom audit; and generate
the issue/PR bodies in the canonical section order. The issue's source/status
note should prominently disclose both the stale `O` marker and Gebendorfer's
priority.

## 9. Dated query log and limits

All searches below were run on **2026-08-12 UTC**:

- primary HTML: row `309`, neighboring rows `308`/`310`, definition call
  `94,10,93,28,31`, and contrasting definition 8;
- DataCite: `query="Conjecture 309"`;
- OpenAlex: `Written on the Wall II Conjecture 309`;
- arXiv API: full-metadata query `"Written on the Wall II"` (two unrelated
  current WOWII papers, no 309 note);
- web/SearXNG: exact title, `"Written on the Wall II" "Conjecture 309"`,
  `"even horizontal" "dist_even" graph`, and formula variants;
- GitHub: the issue/PR/code queries listed in Section 6.

The broad search engines indexed the Zenodo note poorly; DataCite and OpenAlex
were the reliable discovery surfaces. Search coverage cannot exclude an
unindexed older observation, private correspondence, or differently notated
result. The conservative conclusion does not require such exclusion: a
verified, dated prior record already exists.
