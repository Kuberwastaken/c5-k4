# Confirmed findings ledger — 2026-08-15 OEIS/Erdős sweep

**Upstream pin:** `2411d22e1bd550d050d0eac6c1fb379a76a3e7c5`.
**Status of this file:** decision-ready summary. Nothing here has been written
upstream; `UPSTREAM_PROTOCOL.md` requires explicit per-turn authorization.

## Classification note (METHOD_V1_6 §A6)

Every confirmed item below is a **formalization defect**: a statement about
what the Lean declaration in `formal-conjectures` asserts. **None is a
counterexample to the underlying mathematics**, and in several cases the
literal declaration is trivially *true*. None is eligible for the
`UPSTREAM_PROTOCOL.md` release path, which is for counterexamples. The
appropriate artifact is an upstream issue in the style of the live trackers.

## Confirmed, apparently unclaimed

| Target | Defect | Witness / proof | Duplicate status |
|---|---|---|---|
| **OEIS A237271** `observation_carmichael` | Hypothesis quantifies over every nonzero `a : ZMod k` instead of units coprime to `k`; unsatisfiable for composite `k`, so the open declaration is vacuously true | General proof: composite `k` has prime `p∣k` with `(p : ZMod k) ≠ 0`; `p^(k−1)=1` would make `p` a unit. No `k ≤ 20000` satisfies it | Novel. `observation_carmichael` → 0 hits; absent from #4896/#4923/#4927. File is 3 days old — **re-check immediately before any write** |
| **Erdős 1093** `deficiency` | Mathlib `smoothNumbers n` means prime factors `< n`; source says `≤ k` | All 23 site catalogue entries reproduce under `≤`; exactly 3 change under `<` (C(7,3) 1→0, C(23,5) 1→0, C(47,11) 4→3). Fix is one token: `smoothNumbers (k+1)` | Novel. Provenance: PR #1328's first commit was correct; a review suggestion introduced it with no threshold discussion |
| **Erdős 1055** `IsOfClass` / `p` | At `r = 2` the equality clause is vacuous in `ℕ+`, so `IsOfClass 2 2` holds and `p 2 = 2` | A005113(2) = 13 (confirmed live). Defect confined to `r=2`; `r = 1,3,4,5` reproduce A005113 exactly. No declaration becomes false | Novel. `IsOfClass` → 1 hit (introducing PR #1197) |
| **Erdős 40** `erdos_40` | `Erdos40ForSet G := ∀ g ∈ G, …` with no extremality wrapper, so the `answer(sorry)` hole closes vacuously | Witness `answer := (∅ : Set (ℕ → ℝ))`. Same file's `variants.implies_erdos_28` uses `.univ`, showing the strong reading was intended | Not listed upstream |
| **Erdős 33** `.variants.one_mem_lowerBounds` | States `∃ A, … ∧ 1 < limsup …` while name/docstring claim a lower bound | Witness `A = ℕ`: `k = k + 0²`, `limsup N/√N = ⊤` | Not listed upstream (the file's headline self-answer *is* already in #4923) |
| **Erdős 15** | RHS is provably **False** as encoded — Mathlib `Summable` is unconditional (absolute over `ℝ`) and `∑ n/pₙ ~ ∑ 1/log n` diverges — while Erdős's actual question (conditional convergence) is open | Divergence argument | Not listed upstream |
| **Erdős 477** | Source says `b ∈ {f(k) : k ∈ ℤ}`; all five declarations use `f.eval '' {n \| 0 < n}` = `{f(k) : k ≥ 1}`. The site's own published degree-2 proof uses `f(k) − f(−k)`, which the Lean set excludes | Repaired the `X²` case (`f(k+1) − f(k−1)`, `k ≥ 2`); the general `a ∣ b` variant is **not** repaired by that argument | Not listed upstream |
| **Erdős 952** | Source asks a question and quotes [Er80] "the answer is almost certainly negative"; the Lean asserts the positive existence as a bare `theorem` rather than `answer(sorry) ↔` | Checked for a trivial-truth loophole: none (the norm is the squared step; injectivity forces escape to infinity) | Not listed upstream |

## Confirmed but partially claimed

| Target | Defect | Duplicate status |
|---|---|---|
| **Erdős 142** `erdos_142`, `.variants.upper`, `.variants.three` | All three `answer(sorry)` holes close by copying the LHS (`isTheta_refl` / `isBigO_refl`) | **Partial**: #4922 reports `.variants.upper`; #4923 lists the same reflexive-asymptotic pattern for EP 422/539/789 but **not** for `erdos_142` or `.variants.three` |

## Status-sync findings (not discovery claims, METHOD rule 9)

| Target | Issue |
|---|---|
| **Erdős 1084** `triangular_optimal_d2` | `research open` though Harborth (1974) proved the declared `=` form; docstring writes `<` where the source says `=` |
| **Erdős 1106** `.parts.i` | `research open` though Schinzel–Wirsing settles it |
| **Erdős 1054** `.parts.i` | `research open` though the site records Tao's disproof |
| **Erdős 36** `.variants.upper` | Asks `c < 0.380926853433087`; site now records `c < 0.380876` |
| **Erdős 44** `.variants.empty_start` | Exactly Singer (1938), cited by the corpus itself on EP 30 |
| **Erdős 60** `.variants.two_copies` | Tagged `research solved`; the site records no proof — mis-tagged in the *solved* direction |
| **OEIS A357513** | Proved by Kutal, Jul 2026, with a Lean formalization; not tracked upstream |

## Closed brackets and negative results worth keeping

- **Erdős 242** (Erdős–Straus with distinctness): predecessor's timeout bracket is
  **closed**. Exact divisor enumeration (`(py−q)(pz−q) = q²`) settles every
  `x ∈ (n/4, 3n/4]` completely, plus a divisor lift. Every `n = 3..2,000,000` has an
  explicit verified `(x,y,z)`; 148,933 exhaustive, 1,851,065 lifted, 45.5 s, third
  code path agrees to `n ≤ 400`. `HOLD_BOUNDED`.
- **Erdős 779**: first run ever; least prime witness for every `n = 1..200`
  (largest `p = 3559` at `n = 180`). `HOLD_BOUNDED`, bracket at `n ≥ 201`.
- **Erdős 982**: the one genuinely finite target; faithful. Exhaustive integer
  searches for `n = 6..9` found nothing. Its concyclic obstruction is **already
  upstream** (open PR #4694 / issue #4691) — no novelty available there. Live lane
  continues via Danzer's 9-gon and the Fishburn–Reeds 20-gon.
- **Erdős 274**: the predecessor's flagged `ENat.card`/index-0 loophole **does not
  exist** — Neumann's lemma forces finite index on every part of a finite exact
  cover, so the declaration is exactly Herzog–Schönheim. Minimal counterexample needs
  `k ≥ 5`; 89 groups searched exhaustively, 0 hits.

## Refuted predecessor claims (recorded so they are not re-raised)

- **Erdős 1084** "finitely false as stated" — the `<` is only in the docstring; the
  declaration asserts `=`, which is exactly Harborth's theorem. Lattice recomputation
  matches `9n²+3n` for n = 0..5.
- **Erdős 931** "closed interval trivialises it" — on the repo's own witness the strict
  reading is satisfied by the same prime; 280 premise-satisfying tuples show **zero**
  disagreements between readings. Also: the docstring sentence attributed to the source
  is **not present** on erdosproblems.com/931 (live and cached byte-identical); Wayback
  check unresolved (HTTP 429).

## Timing risk

Upstream contributor **KitaKen1** is running a parallel misformalization audit
(#4896 "Tracking: possible misformalizations found in statement audits", updated
2026-08-14; #4923 "Possible misformalizations II", 2026-08-13). There are 23 open
issues matching the misformalization/vacuous/`answer(sorry)` surface. The duplicate
surface for everything above is therefore **moving daily**, and each item must be
re-checked immediately before any write.

## Non-open declaration defect (out of target scope, recorded)

- **Erdős 50** `erdos_50_singular` (`research solved`) is false as stated:
  `IsDistributionOfPhiRatio f` pins `f` only on `[0,1]` while `IsPurelySingular f`
  asserts `Continuous f` on all of `ℝ`; take the true distribution on `[0,1]` plus a
  jump at `x = 2`. The *open* `erdos_50` is immune.
