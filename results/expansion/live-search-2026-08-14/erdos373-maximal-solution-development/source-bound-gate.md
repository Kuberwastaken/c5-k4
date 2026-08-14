# Erdős 373 maximal solution: source/database-bound gate

**Audit date:** 2026-08-14 UTC

**Disposition:** `STRICT_STOP_SOURCE_BOUND`

**Proposed band:** `17 <= n <= 256`

**Band classification:** `CATALOGUE_CONTROL`

**Evaluation state:** `NOT_EVALUATED`

**Authorization:** none

No Erdős 373 target instance with `n >= 17` was constructed or evaluated in
this gate. No search implementation, workflow, dispatch, release, issue, pull
request, commit, or push was created. The source gate stops the proposed band
before activation for two independent reasons:

1. Nair--Shorey's unconditional published range confirms the
   Surányi--Hickerson catalogue for `n <= exp(80)`. The entire proposed band is
   far inside that range.
2. Three currently open upstream pull requests touch the exact target path.
   None resolves the declaration, but the committed preflight makes *any* open
   exact-path PR a race-gate strict stop.

This is a stop for the proposed bounded experiment, not a proof of the global
conjecture. The range above `exp(80)` remains open in the sources inspected.

## Exact target and strict semantics

At audit time, `google-deepmind/formal-conjectures` `main` resolved to:

```text
commit     2411d22e1bd550d050d0eac6c1fb379a76a3e7c5
tree       f6b52f1d3f63b365d6f8c405623d5f7a4e674efc
path       FormalConjectures/ErdosProblems/373.lean
blob       e4d534288b0e5eade9169f8b5d23fb22b1d3b286
bytes      3342
SHA-256    032d4e1e4f9ae9ecd3281873ebd75ecac9c200f4476aa2214d18624d24a36204
declaration Erdos373.erdos_373.variants.maximal_solution
```

Pinned source: [`373.lean`](https://github.com/google-deepmind/formal-conjectures/blob/2411d22e1bd550d050d0eac6c1fb379a76a3e7c5/FormalConjectures/ErdosProblems/373.lean).
The declaration remains tagged `@[category research open]` with a `sorry`
body.

The Lean domain requires a nonincreasing list `l`, entries greater than one,
the factorial-product identity, and the strict condition

```text
l.headI < n - 1.
```

For a nonempty nonincreasing list this is the historical nontriviality
condition `a_1 <= n-2`. It is not the looser `a_1 < n`. In particular,

```text
16! = 15! * 2! * 2! * 2! * 2!
```

is a valid factorial identity but is rejected by the formal set because
`15 < 15` is false. The source catalogue applicable to the formal target is:

```text
 9! = 7! * 3! * 3! * 2!
10! = 7! * 6!
10! = 7! * 5! * 3!
16! = 14! * 5! * 2!
```

The last identity is the asserted maximum. This gate did not recompute any
candidate above it.

## Decisive unconditional range

Chim, Nair, and Shorey's 2018 survey states that Nair and Shorey confirmed the
Hickerson conjecture for `n <= e^80`, and separately says that the complete
unbounded result is conditional on Baker's explicit `abc` conjecture. The
survey formulates the same strict problem as

```text
a_1! a_2! ... a_t! = n!,  n >= a_1 + 2,
```

so this is not a boundary-reading mismatch with the Lean predicate.

The implication for the preflight's fixed band is immediate:

```text
17 <= n <= 256 < e^80.
```

Every point in the proposed band is therefore already excluded by published
mathematics. A computation there could at most reproduce a catalogue control;
it could not produce a new counterexample. This conclusion does not depend on
the older and less readily machine-readable Hickerson computation.

## Source ledger

All PDFs below were passed through the repository-mandated `pdf-inspector`
pipeline. Page/OCR limitations are recorded rather than silently guessed.

| Record | Stable identity and retrieved artifact | PDF inspection | Finding and gate role |
|---|---|---|---|
| Chim--Nair--Shorey, *Explicit abc-conjecture and its applications*, Hardy--Ramanujan Journal 41 (2018), 143--156 | [journal PDF](https://hrj.episciences.org/5117/pdf); retrieved SHA-256 `2c3ee780eb300fcff2fb2215bd11916d6274376ae24258bfa821dbbc5addc78c` | text-based, 14 pages, no OCR gaps, no encoding warning | States that Nair--Shorey confirmed Hickerson for `n <= e^80`; also distinguishes the complete conditional result. **Controlling unconditional range.** |
| Nair--Shorey, *On the equation n!=a1!a2!...at!*, Indagationes Mathematicae 27 (2016), 634--642 | [DOI](https://doi.org/10.1016/j.indag.2015.12.002), PII `S0019357715001147`; retrieved Crossref/Elsevier metadata XML SHA-256 `2480509426d686e6755e9b19bb566afefb183b57c69cb04e2363f18491774e37` | publisher full text was not retrievable without access; no PDF was represented as inspected | Primary bibliographic record for the equation paper. The unconditional range is used only through the readable published survey above, not inferred from inaccessible bytes. |
| Nair--Shorey, *Lower bounds for the greatest prime factor of product of consecutive positive integers*, JNT 159 (2016), 307--328 | [DOI](https://doi.org/10.1016/j.jnt.2015.07.014) | no public PDF was recovered in this audit | Cited by the readable survey in the proof route. Do not conflate the unconditional finite range with the separate complete result under explicit `abc`. **Supporting, not independently controlling here.** |
| Erdős, *Problems and results on number theoretic properties of consecutive integers and related questions* (1975/1976) | [author-hosted scan](https://combinatorica.hu/~p_erdos/1976-39.pdf); SHA-256 `2c098f2c3e5079ef09a44f693c7db43a29428bb1c8bf7df7ab57b020306a9ad0` | 20 pages; all pages flagged as needing OCR; extracted Markdown empty | Indexed records attribute the four-solution catalogue and a Hickerson check through `4^10` to this source. Because the local scan was not machine-readable, that numeric cutoff is **corroborative only and not used to clear the band**. |
| Erdős--Graham, *On products of factorials*, Bull. Inst. Math. Acad. Sinica 4 (1976), 337--355 | [author-hosted scan](https://combinatorica.hu/~p_erdos/1976-25.pdf); SHA-256 `bed77d559ca9ec1e4d028382e590acc198014bd5e14607fe078808a4da8576c7` | 19 pages; all pages flagged as needing OCR; extracted Markdown empty | Primarily contextual work on products of factorials as squares/powers; no independently readable arbitrary-`k` one-sided clearance was taken from it. **Non-controlling.** |
| Luca--Saradha--Shorey, *Squares and factorials in products of factorials*, Monatshefte für Mathematik (2014) | [DOI](https://doi.org/10.1007/s00605-014-0641-3); [public PDF artifact](https://artefacts-discovery.researcher.life/full_text_files/DA-2/bb/bb28c9150b8f31c1b4504d62e8ef004a/full_text/F%2Brk1r14w5c0rgzEiD1EJtRN0DZQhIHsM_MeE1J6JMk%3D.pdf); SHA-256 `acf7a7ecc1706cb5606077e0fdc08a709ed1070807eb9c2a6232005cea786372` | text-based, 18 pages, no OCR gaps, no encoding warning | Studies square/factorial-product variants and gives explicit-`abc` consequences; it does not supply a stronger unconditional one-sided range for this gate. **Non-controlling.** |
| Takeda, doctoral thesis, *The distribution of prime ideals over number fields and Diophantine equations involving factorial functions* | [repository PDF](https://nagoya.repo.nii.ac.jp/record/29377/files/k12980_thesis.pdf); SHA-256 `d15190c98dc364846b868d9e4df0686ee338c76cbec32a4b727342c573aae06c` | 65 pages; page 57 needs OCR; encoding issues and complex layout flagged | Reviews the Surányi--Hickerson problem and historical computations. Because extraction has encoding faults, historical numeric bounds were not made controlling from this artifact. **Contextual/corroborative.** |
| Takeda, RIMS note on factorial products | [RIMS scan](https://www.kurims.kyoto-u.ac.jp/~kyodo/kokyuroku/contents/pdf/2196-15.pdf); SHA-256 `ee0327c4ea264618892ebf74f6f2375ccbb55d8a06304d90b428da2c5dd1fb1d` | image-based, 11 pages, all pages need OCR | Search indexing reports Hickerson checked through `4^10`; the scan could not validate the passage locally. **Corroborative only.** |
| Takeda, *Product of Factorials Equal Another Product of Factorials*, Results in Mathematics (version of record 2024-08-13) | [DOI](https://doi.org/10.1007/s41980-024-00906-8) | publisher download returned a subscription/HTML response rather than valid PDF bytes; the response SHA-256 was `72fe2c3282e860114b9992a9352ba87f1218f243ef540f53dfda017f96da99a8` and was not treated as a PDF | Publisher abstract says the Surányi--Hickerson conjecture remains open and studies a broader product-equals-product generalization. It provides no accessible stronger one-sided unconditional range. **Current-status context, non-controlling.** |
| Novaković, *Products of factorials which are products of factorials*, arXiv:2602.23838v1, 2026-02-27 | [PDF](https://arxiv.org/pdf/2602.23838); SHA-256 `c89fc2ebc9b86d4f85ef14daef187ecd8676a4a37ee78322e02eea948b4b755d` | text-based, 8 pages, no OCR gaps, no encoding warning | Calls the unrestricted problem long-standing and unsolved, records the catalogue, and makes clear that the complete Nair--Shorey list is under explicit `abc`. **Current-status control; not a finite-range clearance.** |
| OEIS A003135 | [record](https://oeis.org/A003135) and [internal view](https://oeis.org/A003135/internal), accessed 2026-08-14 | OEIS returned HTTP 403 to the archival command, so no local response hash is claimed | Uses the exact condition that the largest factor index is `< n-1`, lists `9,10,16`, and records “no other terms < 10^5” (Jud McCranie, 2005). **Independent catalogue corroboration**, weaker than `e^80`. |
| Erdős Problems 373 | [public problem page](https://www.erdosproblems.com/373), last-edited date displayed as 2026-01-29; mirrored database record below | not a PDF | Marks the problem open, gives the strict statement and four historical identities. It does not turn a finite search into a global resolution. **Status control.** |

The historical `4^10`, `18160`, `10^5`, and `10^6` computational reports are
not needed for the decision: each is already larger than 256, while the
readable published `e^80` theorem is both stronger and semantically matched.
Where a scan was OCR-incomplete, this report deliberately does not elevate an
indexed or secondary rendering into a primary-source exact claim.

## Current database and public-status pins

The independent `teorth/erdosproblems` database was read at:

```text
main commit        3cbe2cffad0267952de3523089549009ea6fe5dc
data/problems.yaml blob d018ed352908fb469845b8d75da7d22b608d3382
bytes              397437
SHA-256            69719796f01fbe3a33913d14d1307502fa4361a307fa8e4674d20163a745eb0c
problem 373        status=open, informal_status=open, OEIS=A003135,
                   formalized=yes
```

Exact GitHub searches in `google-deepmind/formal-conjectures` for
`erdos_373`, `Erdos373`, `maximal_solution`, `Suranyi-Hickerson`, and
`Hickerson` found no PR that claims to prove or disprove `maximal_solution`.
Four closed `erdos_373` PRs (#2746, #2755, #3267, #3276) concern only the
conditional `of_limit` or `of_lower_bound` variants.

The mandatory changed-file enumeration nevertheless found these open PRs:

| PR | State at audit | Exact-path change | Resolution effect |
|---|---|---|---|
| [#4688](https://github.com/google-deepmind/formal-conjectures/pull/4688), `chore: modulize FormalConjectures/` | open, non-draft; head `5e22a9f1dac70e763f3a33dd9eeba59dd008b03f`; `mergeStateStatus=DIRTY` | blob `37e260ab5394792a1c771f018b106727faccdf84`; adds `module`, changes to `public import`, opens a public section | none |
| [#4198](https://github.com/google-deepmind/formal-conjectures/pull/4198), `Update 35.lean` | open draft; head `1cda50fe1496260c6fe6177543542dcc7acca1fb`; `mergeStateStatus=UNSTABLE` | blob `e4d534288b0e5eade9169f8b5d23fb22b1d3b286`; import-path refactor | none |
| [#4004](https://github.com/google-deepmind/formal-conjectures/pull/4004), `use LaTeX rather than markdown in docstrings` | open draft; head `a77dee7db6b14ceb53aeb86bfedde832148f7ee5`; `mergeStateStatus=UNKNOWN` | blob `d4154ebf17de631931476fe25eecc7c4d6106348`; docstring delimiters only | none |

The saved #4688 API record has SHA-256
`cf80a745fceca7996c076c909ff03fb60749af89d9dab46bcd2e3dac96d7d632`.
All three PRs leave the theorem open, but all three trip the preflight's
literal exact-path race rule. This corrects the earlier text-only search,
which had reported zero open PRs because their titles and descriptions do not
name Erdős 373.

## Range/control classification

| Range | Classification | Meaning |
|---|---|---|
| `n in {9,10,16}` | `PUBLISHED_CATALOGUE` | Known strict nontrivial identities; controls only. |
| `17 <= n <= 256` | `CATALOGUE_CONTROL` + `STRICT_STOP_SOURCE_BOUND` | Entire proposed experiment is within the unconditional `n <= e^80` confirmation. Do not run. |
| `257 <= n <= floor(e^80)` | `PUBLISHED_EXCLUSION` | Also covered by the same theorem, but outside the fixed preflight and not permission to widen. |
| `n > e^80` | `OPEN_OUTSIDE_AUTHORIZATION` | The inspected sources do not give an unconditional complete classification. A search here would be a materially new, infeasible-scale design requiring a new preflight and source gate. |

## Terminal decision

The proposed freeze cannot pass its database-sanity gate. Activating the
`17..256` shards would spend compute only to reproduce a published exclusion,
and the exact target file is simultaneously under three open upstream PRs.
Therefore:

```text
GO          = false
DEFER       = false
STRICT_STOP = true
reason      = SOURCE_BOUND_ALREADY_EXHAUSTS_FIXED_BAND
secondary   = OPEN_EXACT_PATH_UPSTREAM_PRS
```

The correct next action for this lane is archival only: retain this gate as a
negative result and do not implement or dispatch the search. Any future Erdős
373 experiment must begin from a new sequentially committed preflight with a
different, source-justified target regime; it may not silently widen this one
past `e^80`.
