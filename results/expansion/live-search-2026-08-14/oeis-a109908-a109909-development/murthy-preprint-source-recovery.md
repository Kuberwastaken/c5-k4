# Murthy preprint source recovery and novelty gate

Status: `TARGET_NOT_EVALUATED`

Audit date: 2026-08-14 UTC

## Source identity

- Pengcheng Niu and Junli Zhang, *On Two Conjectures of A. Murthy*, seven-page preprint, September 2024.
- DOI: [`10.13140/RG.2.2.16430.11848`](https://doi.org/10.13140/RG.2.2.16430.11848).
- ResearchGate publication record: <https://www.researchgate.net/publication/383734495_On_Two_Conjectures_of_A_Murthy?channel=doi&linkId=66d82c09f84dd1716c94a815&showFulltext=true>.
- ResearchGate PDF URL: <https://www.researchgate.net/profile/Pengcheng-Niu/publication/383734495_On_Two_Conjectures_of_A_Murthy/links/66d82c09f84dd1716c94a815/On-Two-Conjectures-of-A-Murthy.pdf>.
- ResearchGate publication ID: `383734495`; full-text link ID: `66d82c09f84dd1716c94a815`.

The current ResearchGate record identifies the authors as Pengcheng Niu (Northwestern Polytechnical University) and Junli Zhang (Shaanxi University of Science and Technology), says that the author uploaded the content on 2024-09-04, and labels it a preprint that may not have been peer reviewed.

## Exact scope and sequence equivalence

The recovered seven-page full text is about the two relevant number-theory conjectures, not the unrelated commutative-algebra conjectures of M. P. Murthy that appear under a similar title elsewhere.

- Theorem 1.1 claims that for every integer `n > 1` there is an integer `0 < k < n` such that `kn + 1` is prime. This is the conjecture recorded in OEIS A034693.
- Theorem 1.2 claims that every integer `n > 3` can be written `n = a + b`, with positive integers `a,b`, such that `ab - 1` is prime. Substituting `b = n-a`, this is exactly the existential statement that some `a(n-a)-1` is prime.
- Therefore Theorem 1.2, if valid, would prove the conjecture `A109909(n) > 0` for `n > 3`. It would also prove the equivalent conjecture `A109908(n) > 0`: A109909 counts primes of the form `k(n-k)-1`, while A109908 is the greatest such prime (or zero when none exists). Their positivity assertions have the same witnesses.

The manuscript cites A109909 and the A034693 comments. It does not name A109908, but its Theorem 1.2 is logically equivalent to the positivity conjecture recorded there.

## Fatal proof defect

The paper does **not** establish either claimed theorem. Its shared constrained-optimization argument reverses the roles of a minimum and maximum.

In Section 2, equations (2.2)--(2.5), the objective is

```text
f(x,y,u,z) = sum_i (y_i^2 + y_i).
```

The Lagrange equations in (2.6) split into `mu = 0` and `mu != 0`. In the `mu = 0` branch, the paper correctly obtains

```text
y_i = -1/2,
f = -l/4 < 0.
```

It then calls this value `f_max` and concludes that the distinguished prime-indicator point `P` satisfies `f(P) <= f_max < 0`, contradicting `f(P) >= 0`. That classification and inequality are backwards. For every real `y`,

```text
y^2 + y = (y + 1/2)^2 - 1/4 >= -1/4.
```

Thus `y_i = -1/2` gives the global **minimum** `-l/4` of the objective, not a maximum. These are not merely formal stationary values that can be discarded: feasible points in this branch exist. Set all `y_i = -1/2`; choose the free `x_i,u_j` so that the quadratic constraint `h = 0` holds (one free `x_i` is enough, since its quadratic has unbounded positive range), and then choose `z` from the linear-in-`z` constraint `g = 0`. Consequently the negative stationary branch is compatible with the constraint set.

The paper next labels a positive value from the `mu != 0` branch as `f_min` and infers `f(P) > 0`. That inference is invalid because the already-found feasible `mu = 0` branch has objective `-l/4`.

Section 3 does not supply an independent proof of Theorem 1.2. For both parity cases it constructs analogous variables and identities, then says that "the remainder is treated as in Section 2." Theorem 1.2 therefore inherits the same fatal extrema reversal. The unsupported statement that cases through `10^3` can be checked directly does not repair the proof for general `n`.

## Current external status

As recovered on 2026-08-14:

- [OEIS A109909](https://oeis.org/A109909) still says `Conjecture: a(n) > 0 for n > 3` and records only verification through `10^9`; it links this preprint but does not mark the conjecture proved.
- [OEIS A109908](https://oeis.org/A109908) likewise still says `Conjecture: a(n) > 0 for n > 3` and records verification through `10^9`.
- OEIS GitHub export snapshots:
  - <https://raw.githubusercontent.com/oeis/oeisdata/main/seq/A109/A109908.seq>, header revision `#19 Oct 06 2025 14:31:54`, SHA-256 `e4620604bc977981e6233a970a105027ab34cdc03d9f0f07166a2c685e091aba` as retrieved on 2026-08-14.
  - <https://raw.githubusercontent.com/oeis/oeisdata/main/seq/A109/A109909.seq>, header revision `#13 Sep 29 2024 11:56:45`, SHA-256 `8ba71aab83ac2d1cf7a6843ab5c5fcc0d15796e07b27a70c216ef3ed56adc44b` as retrieved on 2026-08-14.

## Registry and index metadata

DataCite API record: <https://api.datacite.org/dois/10.13140/RG.2.2.16430.11848>.

- DOI: `10.13140/rg.2.2.16430.11848`
- resource type: `Preprint` / `Text`
- publisher: `Unpublished`
- publication year: 2024
- registered/created: `2024-09-04T09:45:10.000Z`
- updated: `2025-10-21T22:06:18.000Z`
- complete API response SHA-256 as retrieved on 2026-08-14: `327f7eaa79cf87cdca8aa1cb65a71071412fe6cd3b92d026bbbf391fe76c38e8`

OpenAlex API record: <https://api.openalex.org/works/https://doi.org/10.13140/RG.2.2.16430.11848>.

- work ID: `https://openalex.org/W6941228502`
- citation count: 0 in the recovered response
- only recorded location: the DOI landing page; no PDF URL or repository full text
- complete API response SHA-256 as retrieved on 2026-08-14: `79ad521380c0f7c72523101c066d643571203273934fbdff5dfeb59c60f97f82`

Crossref returned no registered work for the DOI. Semantic Scholar returned no paper for the DOI. Searches of current web indexes, the authors' indexed profiles, arXiv, institutional domains, Zenodo, and Figshare found no independent copy or subsequent reviewed version.

## PDF-byte recovery limitation

The ResearchGate PDF was accessible to the web document parser as a seven-page `application/pdf`, and every page relevant to the theorem statements and proofs was read, including all of Sections 2 and 3. Direct byte retrieval from the VPS repeatedly returned a Cloudflare HTTP 403 for the canonical PDF URL and its `origin`, `download`, and user-agent/referrer variants. The DOI landing page also returned a Cloudflare 403 to direct retrieval. Internet Archive and Common Crawl recovery attempts produced no usable capture, and registry/index services exposed no alternate PDF URL.

Accordingly:

- no local PDF file was obtained;
- no PDF SHA-256 is asserted;
- no claim is made that local `pdf-inspector` processed the file;
- the hashes above identify the recovered registry responses and OEIS exports, not the PDF.

Inventing or substituting a hash from the similarly titled 2017 paper by Mrinal Kanti Das would be incorrect; that paper concerns different Murthy conjectures.

## Novelty gate

`CAVEATED_OPEN_WITH_FAILED_PRIOR_PROOF`

The preprint is directly on target and explicitly claims a proof, so it must be disclosed in any novelty review. However, its central argument contains a concrete fatal extrema reversal, and both OEIS entries continue to record the assertion as a conjecture rather than a theorem. It is therefore not a valid prior resolution of A109908/A109909 on the evidence recovered here.

Any future positive result must still pass an independent full literature/status gate. Public wording should say that it follows an unreviewed 2024 attempted proof with the defect above; it should not say that no one previously claimed the result. No target search, evaluation, counterexample claim, commit, release, issue, pull request, or other public action was performed in this recovery audit.
