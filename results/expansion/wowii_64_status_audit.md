# WOWII 64: source, status, priority, and formalization audit

Audit date: **2026-08-12 UTC**

## Executive conclusion

WOWII Conjecture 64 is already disproved. The primary Written on the Wall II
list still marks entry 64 `O`, but Jonas J. Gebendorfer published the explicit
resolution on 2026-07-26 in *Clique Blow-ups of the 5-Cycle and Written on the
Wall II Conjecture 64*, DOI
[10.5281/zenodo.21595503](https://doi.org/10.5281/zenodo.21595503).

The local Lean work is therefore a **Lean formalization of an already-disproved,
source-listed-open entry**. It is not a new disproof, and no novelty or first-
resolution claim should be made. Gebendorfer must receive explicit credit for
the published Conjecture 64 resolution. His note in turn credits the earlier
Kuberwastaken `C5[K4]` certificate for priority on that carrier and its
forest-number computation.

## 1. Primary source and exact reading

The current primary pages inspected were:

- [the complete WOWII list](http://cms.uhd.edu/faculty/delavinae/research/wowII/all.html);
- [the open WOWII list](http://cms.uhd.edu/faculty/delavinae/research/wowII/open.html);
- [the definition table](http://cms.uhd.edu/faculty/delavinae/research/wowII/wowIIdefs.js).

Both lists display entry 64 with marker `O`, date 25 March 2004, and the
source text

```text
If G is a simple connected graph, then
f(G) >= CEIL[(sqrt[alpha(G) * (1 + (n mod Delta(G))] ]
```

The brackets are unbalanced in the primary HTML. The definitions link is
`printDefinitions(41,5,32,16,0)`: forest number, independence number,
`n modulus maximum degree`, and ceiling. Definition 32 states that, when
`Delta(G) >= 2`, `n mod Delta(G)` is the remainder upon division of the
number of vertices by the maximum degree. Thus `%` is an operation on natural
numbers and is an atomic source invariant.

The conservative intended repair is

```text
f(G) >= ceil(sqrt(alpha(G) * (1 + (n mod Delta(G))))).
```

This is also Gebendorfer's reading. The multiplication sign and definition-32
atom rule out reparses that move `mod` outside its displayed operands. Earlier
adversarial checking in `results/verification.md` records the other plausible
bracket repairs; every bracket-defensible reading is violated by `C5[K4]`.

## 2. Published status and priority

The Zenodo API record was read directly on the audit date and returned HTTP
200 with:

```text
title: Clique Blow-ups of the 5-Cycle and Written on the Wall II Conjecture 64
author: Jonas Jakob Gebendorfer
publication date: 2026-07-26
DOI: 10.5281/zenodo.21595503
```

The seven-page PDF is text-based, has no pages requiring OCR, and reports no
encoding warning. It explicitly:

1. identifies `C5[K4]` as a 20-vertex counterexample with
   `n=20`, `Delta=11`, `alpha=2`, and `f=4`;
2. says the earlier Kuberwastaken certificate has priority for this graph and
   its forest-number computation;
3. supplies the smaller 18-vertex witness `B(4,4,3,4,3)`;
4. gives an infinite counterexample family; and
5. proves order 18 minimal and dihedrally unique only within positive
   `C5`-clique blow-ups, while expressly making no global minimum-order claim.

Accordingly, the defensible attribution is:

> Jonas J. Gebendorfer published the disproof of WOWII 64 and the smaller
> 18-vertex/infinite-family analysis, while crediting the earlier
> Kuberwastaken `C5[K4]` certificate for that carrier and its induced-forest
> computation. The present contribution is a complete Lean formalization of
> the already-published disproof.

Do not say "new counterexample", "new disproof", "first disproof", or
"previously unsolved" about the present Lean work. The live `O` marker is
lagging curated status, not evidence that the mathematical result is unknown.

## 3. Independent exact certificate

The dependency-free verifier
[`verify_wowii_64.py`](../../scripts/verify_wowii_64.py) reconstructs
`C5[K4]` without reading the Lean file or any saved graph artifact. It checks:

```text
n = 20
connected = true
degree sequence = (11)^20, hence Delta = 11
alpha = 2
largest induced forest = 4
20 mod 11 = 9 in the natural numbers
ceil(sqrt(2 * (1 + 9))) = ceil(sqrt(20)) = 5
4 < 5
```

The upper bounds are exact hereditary certificates:

- `{0,8}` is independent and all `C(20,3)=1,140` triples are checked to be
  non-independent, proving `alpha=2`;
- `{0,4,8,12}` induces a four-vertex path and all
  `C(20,5)=15,504` five-subsets are checked to be non-forests. Any larger
  induced forest would contain an induced forest on five vertices, proving
  `f=4`.

The arithmetic uses `math.isqrt`, never floating point. The search space is
fixed and bounded. A 60-second alarm guards the run where `SIGALRM` is
available, and the verifier also rejects a completed run at or above 60
seconds. The optional NetworkX Atlas gate is deliberately omitted so the
publication certificate remains standard-library-only and focused on the
actual witness; the broader 995-graph reading audit is separately recorded in
`results/verification.md`.

Reproduce with:

```bash
python3 scripts/verify_wowii_64.py
```

## 4. Lean statement and proof audit

The complete local certificate is `lean/GraphConjecture64.lean`, checkpointed
at full commit `8c0a76079e5c7153bdc2dd6d97a9821ee25b2620` (resolved with
`git rev-parse`, not inferred from the short hash). The working copy and that
commit have matching SHA-256
`5c0c356b710140a1e7b18c521faf48611ff21ec8eb71c806896960ca2d70f08c`.
It defines the same `C5[K4]` graph and proves connectedness, `maxDegree=11`,
`indepNum=2`, an induced-forest upper bound of four, the exact ceiling lemma,
and the final contradiction without `sorry` or a custom axiom.

Two elaboration details are mathematically essential:

1. The radicand is written with an explicit natural-number annotation before
   coercion to the reals:

   ```lean
   ((G.indepNum * (1 + Fintype.card alpha % G.maxDegree) : Nat) : Real)
   ```

   Without that annotation, the surrounding `Real.sqrt` makes Lean elaborate
   `%` as real Euclidean remainder. Then `20 % 11` reduces to zero and the
   displayed bound becomes `ceil(sqrt(2))`, which is not the source invariant.
2. The quantified statement includes `[DecidableRel G.Adj]`, required by the
   current `maxDegree` API.

The external check

```bash
(cd ../formal-conjectures && \
  lake env lean -DwarningAsError=true ../c5-k4/lean/GraphConjecture64.lean)
```

passes against the current `formal-conjectures` toolchain. A temporary
`#print axioms` audit, removed after inspection, reported only `propext`,
`Classical.choice`, `Quot.sound`, and the standard `Lean.ofReduceBool` /
`Lean.trustCompiler` assumptions introduced by `native_decide`; there is no
project-specific axiom or `sorryAx`.

## 5. Upstream scope gate

Read-only searches of `google-deepmind/formal-conjectures` on 2026-08-12 used:

```text
code:   GraphConjecture64 conjecture64
issues: "Conjecture 64" OR "WOWII 64" OR "WOWII Conjecture 64"
PRs:    "Conjecture 64" OR "WOWII 64" OR "WOWII Conjecture 64"
```

They found no WOWII 64 file/declaration, focused issue, or focused PR. The
numeric-only results were unrelated Erdős Problem 64 and repository PR #64.
This satisfies the duplicate portion of the protocol's local scope audit at
this time, but it must be rerun immediately before any future public action.

The collection is Written on the Wall **II**, and the result is complete.
However, `UPSTREAM_PROTOCOL.md` also requires sequential artifact commits and
a committed checklist under `results/expansion/publication/` before a public
write. This audit itself does not authorize publication and does not claim
those later gates are complete.

## Recommended public wording

Use wording no stronger than:

> This formalizes in Lean the already-published disproof of WOWII Conjecture
> 64. Jonas J. Gebendorfer's 2026 note records the Conjecture 64 resolution,
> credits the earlier Kuberwastaken `C5[K4]` certificate for that carrier and
> its forest-number computation, and supplies a smaller 18-vertex witness and
> an infinite family. The primary WOWII page has not yet updated its `O`
> marker.

No GitHub issue, PR, comment, push, or other public action was performed as
part of this audit.
