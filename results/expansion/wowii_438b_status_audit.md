# WOWII 438b: source, status, notation, and novelty audit

Audit date: **2026-08-12 (UTC)**
Scope: WOWII entry 438b, the stronger arbitrary-subset inequality, DeepMind
Formal Conjectures [issue #4915](https://github.com/google-deepmind/formal-conjectures/issues/4915)
and [PR #4916](https://github.com/google-deepmind/formal-conjectures/pull/4916).

## Executive conclusion

The Lean theorem in PR #4916 is a faithful formalization of the primary WOWII
438b statement. In particular, the source's `a` glyphs are Greek alpha in the
Symbol font: `alpha_2` is the order of a largest vertex set inducing maximum
degree at most one, while un-subscripted `alpha` is the ordinary independence
number. `H_2` really is the set of vertices of degree at most two. The theorem
does **not** accidentally formalize the annihilation number or signed
2-independence.

The primary WOWII site, last updated 2026-08-06, still labels 438b `O`; the
site explains `O` as "open (as far as I know)." I found no source recording a
resolution of the exact entry. Thus it is supportable to describe #4916 as a
formal proof of an item that the source currently lists as open. The GitHub
issue was opened by the PR author immediately before the PR and is not
independent evidence of historical status. The PR is open, not merged, and its
main build check was still pending at the audit time.

The mathematical novelty position needs to be more conservative. I did not
locate the exact arbitrary-`H` formula in the targeted searches below, but its
content is an immediate corollary of the explicitly recorded inequality

```text
diss(G) <= alpha(G) + nu_s(G),
```

where `nu_s` is the induced matching number. Bock--Pardey--Penso--Rautenbach
recorded that inequality in 2022 and called it straightforward. For any vertex
set `H`, every induced matching has at most `|E(G[H])|` edges wholly in `H`, and
choosing an outside endpoint from each remaining edge gives an independent set
in `G[V-H]`. Hence

```text
nu_s(G) <= |E(G[H])| + alpha(G[V-H]),
```

and the PR's stronger inequality follows. Therefore the exact displayed
arbitrary-`H` formulation may be unrecorded, but it should not be advertised as
a new standalone mathematical theorem without a deeper literature review and
author contact. The robust claim is: **a new Lean formalization/proof of WOWII
438b, using an elementary strengthening whose mathematical content is already
subsumed by a known dissociation/induced-matching bound**.

## 1. Primary WOWII record

The authoritative current pages inspected were:

- [WOWII landing page](http://cms.uhd.edu/faculty/delavinae/research/wowII/),
  whose menu reports `last update 8/6/26`;
- [the complete list](http://cms.uhd.edu/faculty/delavinae/research/wowII/all.html),
  where 438b occurs once under **Dalmatian Heuristic / Upper Bounds on the
  2-independence number for connected graphs**;
- [the open list](http://cms.uhd.edu/faculty/delavinae/research/wowII/open.html),
  where 438b is marked `O` and dated January 2012;
- [the site's definition table](http://cms.uhd.edu/faculty/delavinae/research/wowII/wowIIdefs.js).

The complete page renders the statement as

```text
Let G be a connected graph on n > 3 vertices. Then
alpha_2(G) <= alpha(G) + alpha(G[V-H_2]) + |E(G[H_2])|,
where H_2 is the set of vertices of degree at most 2 in G.
```

The entry's definitions link calls `printDefinitions(118,5,100,0,0)`.
Definition 118 says that a `k`-independent set induces maximum degree at most
`k-1`, and defines `alpha_k` as its largest order. Definition 5 says that
`alpha(G)` is the largest number of pairwise nonadjacent vertices. The Symbol
font HTML `<font face="Symbol">a</font>` is the source of plain-text/OCR
renderings such as `a_2` and `a`; it is not Latin `a` and not the annihilation
number. The adjacent DeLaViña--Pepper preprint independently uses the same
definition (there denoted `beta_k` in the extracted text).

The page's general legend says `O` means "open (as far as I know)." This is a
maintainer knowledge marker, not a proof of worldwide novelty. It does,
however, establish the source-maintained status as of the page's current
update.

## 2. Adjacent DeLaViña/Pepper and DLP-family material

The WOWII page itself links E. DeLaViña and R. Pepper,
[*Graffiti.pc on the k-independence number of a graph* (2012 preprint)](http://cms.uhd.edu/faculty/delavinae/research/DeLaVina_Pepper_CN2012.pdf).
The PDF was classified as text-based (11 pages, no OCR gaps or encoding warning)
and checked in full.

Relevant findings:

- It defines `k`-independence exactly as WOWII does: induced maximum degree at
  most `k-1`.
- It records the general bound `beta_k(G) <= k beta(G)`.
- It proves several nearby Graffiti.pc conjectures, including #436a and #445a,
  and gives the arbitrary-set bound
  `beta_k(G) <= k beta(G[V-A]) + |A|` as Theorem 2.10 (a generalization of
  #451).
- It does not state or prove #438b, and #438b is not among its explicitly listed
  remaining conjectures. This omission is neutral: the paper says it presents
  only some results from the full list, while the current primary list still
  marks #438b open.

Targeted inspection of adjacent DeLaViña--Larson--Pepper(-Waller) work found
consistent notation but no 438b result. In particular, the 2-domination paper
[*Graffiti.pc on the 2-domination number of a graph*](https://math1um.github.io/Research/r07.pdf)
is about domination bounds; it is useful as notation/context, not evidence that
438b was solved. No claim should be inferred merely from author overlap or from
nearby conjecture numbers.

## 3. Relation to recorded dissociation-number results

For `k=2`, WOWII's `alpha_2(G)` is the parameter now commonly called the
dissociation number `diss(G)`. A 2-independent set induces a disjoint union of
isolated vertices and edges, and those edges form an induced matching.

Bock, Pardey, Penso, and Rautenbach,
[*Relating dissociation, independence, and matchings*](https://arxiv.org/abs/2202.01004)
(published in *Discrete Applied Mathematics* 322 (2022), 160--165,
[DOI](https://doi.org/10.1016/j.dam.2022.07.012)), explicitly record

```text
max{alpha(G), 2 nu_s(G)} <= diss(G)
  <= alpha(G) + nu_s(G) <= 2 alpha(G).
```

Their paper labels these inequalities straightforward and also records the
identity

```text
diss(G) = max { alpha(G-M) : M is an induced matching in G }.
```

The 10-page arXiv PDF was checked in full (text-based, no OCR gaps or encoding
warning). The exact arbitrary-subset formula does not appear in it.

Their companion paper
[*Relating the independence number and the dissociation number*](https://arxiv.org/abs/2205.03404)
([journal DOI](https://doi.org/10.1002/jgt.22965)) studies improvements of the
basic `diss(G) <= 2 alpha(G)` inequality for special graph classes. Its 17-page
arXiv PDF was also checked in full (text-based, no OCR gaps or encoding
warning); it does not record the arbitrary-`H` formula.

Nevertheless, the arbitrary-`H` formula follows immediately from the first
paper's recorded bound. Let `M` be any induced matching and partition it into
edges wholly in `H` and the rest. The first part has size at most
`|E(G[H])|`. Choose an endpoint outside `H` from every remaining edge. Since
`M` is induced, the chosen vertices are independent in `G[V-H]`, so the second
part has size at most `alpha(G[V-H])`. Maximizing over `M` gives

```text
nu_s(G) <= |E(G[H])| + alpha(G[V-H]).
```

Combining this with `diss(G) <= alpha(G)+nu_s(G)` proves exactly the PR's
stronger statement. This is also essentially the same matching-edge partition
as the direct proof in #4916.

Consequences for claims:

- **Correct:** the arbitrary-`H` theorem is logically stronger than the source
  specialization and removes connectivity/order/degree-layer assumptions.
- **Correct:** the source specialization currently has an `O` marker, so the
  Lean contribution proves a source-listed-open conjecture.
- **Not established:** that no mathematician previously observed the exact
  arbitrary-`H` corollary.
- **Too strong without qualification:** “new mathematical theorem” or
  “first-ever solution.” The result is a one-line consequence of a published
  bound, even if the exact formula was not found verbatim.

## 4. Lean statement fidelity

The immutable PR-head file is
[GraphConjecture438b.lean at `cd907f0a1e3331d2430b1fa1b2b8a18c1798258a`](https://github.com/google-deepmind/formal-conjectures/blob/cd907f0a1e3331d2430b1fa1b2b8a18c1798258a/FormalConjectures/WrittenOnTheWallII/GraphConjecture438b.lean).
The external certificate is
[the `c5-k4` copy at `e62f216625438bc099707e466d2825ab483717a4`](https://github.com/Kuberwastaken/c5-k4/blob/e62f216625438bc099707e466d2825ab483717a4/lean/GraphConjecture438b.lean).

Definition-by-definition comparison:

| Source object | Lean object | Audit |
|---|---|---|
| finite simple graph | `SimpleGraph V`, `[Fintype V]` | faithful |
| connected | `G.Connected` | faithful; unused by stronger theorem |
| `n > 3` | `3 < Fintype.card V` | faithful |
| `alpha_2(G)` | `alphaTwo G`, maximum `S` satisfying `IsTwoIndependent` | faithful: neighbor count in `S` is at most 1 |
| `alpha(G)` | `G.indepNum` | faithful |
| `alpha(G[V-H])` | `indepNumOn G (univ \ H)` | extensionally faithful: maximum independent subset contained in the complement |
| `H_2` | `lowDegreeLayer G = univ.filter (degree <= 2)` | faithful |
| `|E(G[H])|` | `(internalEdges G H).card` | faithful |

The arbitrary-subset theorem quantifies over every finite simple graph and every
finite vertex set `H`; specializing it to `lowDegreeLayer G` proves the source
theorem. Nothing in the notation comparison suggests that the proof addresses a
different invariant.

At audit time PR #4916 was open. `Test scripts`, copyright, change scan,
security scan, CLA, and labeler checks passed; `Build project` was still
pending. That is evidence of a submitted and partially CI-verified artifact,
not yet evidence of upstream acceptance or merge.

## 5. Metadata mismatch

The local raw corpus `corpora/graffiti_pc_wow2.json` contains two records,
`wow2-438b` and `wow2-438b(2)`, and assigns one to an unrelated sublist called
“bounds on the matching number of connected bipartite graphs.” The normalized
`data/wowii-conjectures.json` instead places 438b in the correct section,
“Upper Bounds on the 2-independence number for connected graphs.”

The live primary `all.html` and `open.html` each contain **one** 438b occurrence,
under the correct 2-independence heading. Therefore the duplicate and matching
sublist are extraction/catalog metadata artifacts, not meaningful alternate
statements. They do not undermine the Lean parse or proof.

They do matter for provenance wording:

- do not claim that the primary source itself contains two independent 438b
  occurrences;
- do not use the matching-number sublist as support for interpreting any symbol;
- update or annotate the corpus eventually, and revise the sentence in
  `method_v02_438b.md` saying “the statement itself and its duplicate,” because
  the live authoritative page does not support a source-level duplicate.

The normalized fields `in_formal_conjectures: false` and `lean_file: null`
remain factually appropriate until #4916 is merged; an open PR is not yet part
of the base repository.

## 6. Search log and limits

All searches below were run on **2026-08-12 UTC**. Exact-string searches are
especially brittle here because the same parameter appears as `alpha_2`,
`beta_2`, `diss`, and legacy Symbol-font `a_2`.

| Surface | Queries / inspection | Result relevant to 438b |
|---|---|---|
| Primary WOWII HTML and JS | `438b`, neighboring entries, definition IDs `118,5,100`, section headings | one current 438b entry; `O`; exact intended definitions confirmed |
| DeLaViña--Pepper 2012 PDF | full-text inspection; `438`, `beta_2`, `H_2`, induced subgraphs, edge terms | no 438b theorem; nearby results and notation confirmed |
| Web / scholarly search | `"alpha_2(G)" "G[V-H_2]" graph`; `"2-independence number" graph DeLaViña Pepper`; `"dissociation number" "independence number" induced edges bound`; `"diss(G) <= alpha(G) + nu_s(G)"`; `"beta_2(G)" "E(G[A])"`; `"alpha_2(G)" "E(G[H])"` ([reproducible Scholar query](https://scholar.google.com/scholar?q=%22dissociation+number%22+%22induced+matching+number%22+%22independence+number%22)) | no exact arbitrary-`H` formula located; Bock et al. 2022 chain located |
| DeLaViña/Larson/Pepper search | `DeLaViña Larson Pepper 2-independence graph`; `site:uhd.edu DeLaVina Larson Pepper k-independence`; `"Graffiti.pc" "2-independence"` | adjacent papers/context, no 438b resolution located |
| OpenAlex citation-forward check | [work W4293490188](https://openalex.org/W4293490188), all five indexed citing works as of the audit date | no title/record indicating the arbitrary-`H` corollary; the companion independence/dissociation paper was the directly relevant citation |
| GitHub code search | [`GraphConjecture438b`](https://github.com/search?q=%22GraphConjecture438b%22&type=code); [`alphaTwo_arbitrary_subset_bound`](https://github.com/search?q=%22alphaTwo_arbitrary_subset_bound%22&type=code); exact ASCII approximation of 438b | no separately indexed implementation located; the new fork/PR file was inspected through the PR API |
| GitHub state | issue #4915, PR #4916, PR files, checks | issue and PR author are the same; one Lean file; PR open; build pending at audit time |

This is a targeted status/novelty audit, not a systematic-review proof of
absence. Search indexing misses paywalled text, non-digitized papers, alternate
notation, unpublished notes, and observations treated as folklore. Author
contact or citation-forward/backward review of the 2022 dissociation papers
would be appropriate before making a priority claim.

## Recommended public wording

Use wording at approximately this strength:

> PR #4916 gives a complete Lean proof of WOWII 438b, which the primary WOWII
> list currently marks open. The formal proof establishes an arbitrary-subset
> strengthening. That strengthening is elementary and can also be derived from
> the known bound `diss(G) <= alpha(G) + nu_s(G)`, so we make no claim that the
> underlying mathematical inequality is novel.

Avoid “new theorem,” “first solution,” or “previously unknown” unless a more
complete literature/author check supports it. “New formalization,” “complete
Lean proof,” and “proof of a source-listed-open entry” are supported by the
evidence above, subject to being explicit that the PR is not yet merged.
