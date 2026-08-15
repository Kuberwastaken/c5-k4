# OEIS A108864 — upstream submission record

**Target:** `google-deepmind/formal-conjectures`,
`FormalConjectures/OEIS/108864.lean`, declaration `OeisA108864.conjecture`.

**Result class:** formalization counterexample (`NEW_FORMALIZED_READING_DISPROOF`).
The Lean predicate encodes a different set than the one A108864 names. The exhibited
counterexample refutes the *Lean declaration*, not the OEIS conjecture.

**Authorization:** explicit upstream-submission authorization given for this campaign
turn. Issue authorized and posted; PR left unopened for parent review.

---

## 1. Upstream state and eligible collection

| Item | Value |
|---|---|
| Upstream `main` at submission | `638da20efd8eeeed2993fc2550fc596dc90c1ce8` |
| Target file blob | `d621e6438f9ea7acf518f7d3208e8127ea0fa905` |
| Collection | `FormalConjectures/OEIS/` |
| File origin | PR #4450 "Add the first 64 files from AutoOeis to formal-conjectures" (MERGED), commit `d7032450` — the only commit ever to touch the file |
| Toolchain | Lean `v4.27.0`, mathlib pinned by the repo (`a3a10db…`) |

Permalink used in the issue:
`https://github.com/google-deepmind/formal-conjectures/blob/638da20efd8eeeed2993fc2550fc596dc90c1ce8/FormalConjectures/OEIS/108864.lean`

---

## 2. Duplicate gate (re-run immediately before submission)

| Query | Result |
|---|---|
| `gh api search/issues q='repo:google-deepmind/formal-conjectures 108864'` | 1 hit — PR #4450 (MERGED), the file's own origin. No triage, no repair. |
| `… q='… A108864'` | 0 hits |
| `… q='… A109883'` | 0 hits |
| `… q='… OEIS/108864'` | 1 hit — PR #4450 again |
| `… q='… 8925'` | 0 hits |
| `… q='… deficiency'` | 10 hits, all unrelated (Erdős 944/1093, WOWII 65/191, Kourovka 1.12) |
| `gh pr list --state all --search 108864` | PR #4450 only |
| Tracker #4896 (misformalizations I) read in full | A108864 not listed |
| Tracker #4923 (misformalizations II) read in full | A108864 not listed; the only OEIS entry is A211417 |
| Tracker #4927 (open statements with known solutions) read in full | A108864 not listed |
| `git log upstream/main -- FormalConjectures/OEIS/108864.lean` | single commit `d7032450` (PR #4450) |
| Open PR #4946 (`feat(OEIS) 45 conjectures from auto_oeis`) file list | does not touch 108864 or 109883 |

**Gate result: PASS — no upstream coverage of any kind.**

---

## 3. Source pin

- **A108864** — <https://oeis.org/A108864>. OFFSET `1,2`.
  NAME: *"Numbers n such that the perfect deficiency of n (A109883) is <= 10"*.
  The only COMMENT is *"Is 1155 the last odd number in this sequence?"* — the statement
  the Lean file formalizes.
  DATA (61 terms):
  `1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16, 18, 20, 21, 22, 24, 26, 28, 30, 32,
  40, 42, 44, 50, 52, 60, 64, 68, 72, 110, 120, 126, 128, 130, 136, 144, 150, 152, 180,
  184, 204, 228, 256, 315, 462, 496, 512, 528, 592, 656, 750, 884, 1012, 1024, 1155,
  1188, 1248`.
- **A109883** — <https://oeis.org/A109883>. NAME: *"Start subtracting from n its divisors
  beginning from 1 until one reaches a number smaller than the last divisor subtracted or
  reaches the last nontrivial divisor < n. Define this to be the perfect deficiency of n."*
  This is a **greedy divisor-subtraction** quantity. It is not `|σ₁(n) − 2n|`.

**Status:** the OEIS conjecture is open and remains open after this submission.

---

## 4. The mismatch

The Lean file's own docstring says *"its perfect deficiency is ≤ 10"*. The Lean says

```lean
def A (n : ℕ) : Prop :=
  let sigmaOneN : ℕ := (Nat.divisors n).sum id
  0 < n ∧ ((sigmaOneN : ℤ) - 2 * (n : ℤ)).natAbs ≤ 10
```

Docstring and Lean disagree, so by AGENTS.md ("The docstring quotes the source. The Lean
must agree with the docstring. If they disagree, the Lean is incorrect.") the Lean is the
incorrect side.

**Decisive single value.** `24` is a published term of A108864 (twentieth in DATA), and its
perfect deficiency is `0`: `24 − 1 − 2 − 3 − 4 − 6 − 8 = 0`. But `σ₁(24) = 60` and
`|60 − 48| = 12 > 10`, so the Lean predicate `A 24` is **false**. The two sets are therefore
provably different from published data alone; no conjecture is involved.

The divergence runs both ways: `56 ∉ A108864` (perfect deficiency `20`), yet
`σ₁(56) = 112 = 2·56`, so the Lean `A 56` holds.

---

## 5. Counterexample to the Lean declaration

`conjecture` is `answer(sorry) ↔ ∀ n > 58, Even (a n)` with `a n = Nat.nth A n`.

Let `L = {n > 0 : |σ₁(n) − 2n| ≤ 10}` — the set the Lean `A` actually defines. `L` is
infinite (`|σ₁(2^k) − 2^{k+1}| = 1` for every `k`), so `Nat.nth A` is total and the
statement is not vacuous.

`L` (0-indexed):

```
1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16, 18, 20, 21, 22, 26, 28, 32, 40, 44,
50, 52, 56, 64, 68, 70, 88, 104, 110, 128, 130, 136, 152, 184, 196, 256, 315, 368, 464,
496, 512, 592, 650, 656, 836, 884, 1012, 1024, 1155, 1696, 1888, 1952, 2048, 2144, 2272,
2336, 4030, 4096, 5830, 8128, 8192, 8384, 8768, 8925, 11096, 16384, ...
```

- **Minimal witness `n = 67`.** `a 67 = 8925`, odd, and `67 > 58`, so `Even (a 67)` fails.
  Premise check: `8925 = 3 · 5² · 7 · 17`, `σ₁(8925) = 4 · 31 · 8 · 18 = 17856`,
  `2 · 8925 = 17850`, `|17856 − 17850| = 6 ≤ 10`, so `A 8925` holds.
- Indices `59..66` are `2336, 4030, 4096, 5830, 8128, 8192, 8384, 8768` — all even, so `67`
  is the least violating index.
- Further odd terms: `a 74 = 32445`, `a 94 = 442365`.
- Odd elements of `L` with their Lean index: `(0,1) (2,3) (4,5) (6,7) (8,9) (10,11)
  (13,15) (17,21) (40,315) (52,1155) (67,8925) (74,32445) (94,442365)`.

Hence the right-hand side is **false** and `answer` is forced to `False`: a `research open`
declaration that is already decided.

**The `> 58` bound is the giveaway.** In the *true* A108864, `1155` sits at 0-indexed
position **58** — exactly the bound the declaration uses. In the set the Lean predicate
defines, `1155` sits at index **52**. The index arithmetic was calibrated against the real
sequence while the predicate defines a different one.

**The OEIS conjecture is NOT refuted.** `8925` is not a term of A108864 at all: its perfect
deficiency is `2969`. In the real sequence the odd terms up to `3·10⁵` are exactly
`1, 3, 5, 7, 9, 11, 15, 21, 315, 1155` (103 terms in that range) — nothing past `1155`.

---

## 6. Independent verification (three disjoint code paths)

1. **Discovering lane** — `results/expansion/live-search-2026-08-15/scripts/part1/c108864.py`
   (numpy divisor-sum sieve to `10⁷`).
2. **Parent session** — `…/scripts/part1/c108864b.py` (plain trial-division `σ`, no sieve,
   listing `L ∩ [1, 9000]`).
3. **Publication lane (this record)** — fresh trial-division recomputation of
   `L ∩ [1, 6·10⁵]`, 101 terms.

All three agree: `L.index(1155) = 52`, `L[67] = 8925`, `L[59:67] = [2336, 4030, 4096, 5830,
8128, 8192, 8384, 8768]`, odd indices `{0,2,4,6,8,10,13,17,40,52,67,74,94}`.

**Root cause verification** — `…/scripts/part1/c109883b.py`, re-run in this lane, plus an
independently written re-implementation in the publication lane using a different stopping
rule formulation (`subtract d only while r ≥ d`, iterating over *all* divisors including
`n`, versus `subtract then compare to the next divisor`):

- A109883 first **79** published terms reproduced exactly by both.
- The `≤ 10` filter reproduces A108864's **61** published DATA terms exactly by both.
- `perfectDeficiency(1155)` puts `1155` at 0-indexed position **58** in the true sequence.
- `perfectDeficiency(24) = 0`, `perfectDeficiency(56) = 20`, `perfectDeficiency(8925) = 2969`.

---

## 7. Repair chosen, and the trade-off

Two defensible repairs exist.

**(a) Close the declaration.** Keep `|σ₁(n) − 2n| ≤ 10` and set `answer(False)`, certified
by the `n = 67` witness.

**(b) Fix the encoding.** Replace the predicate by the perfect deficiency A109883 and leave
`conjecture` `research open`.

**Chosen: (b).** Reasons:

1. AGENTS.md: *"Each statement must say what its source says"* and *"If they disagree, the
   Lean is incorrect."* The docstring already says "perfect deficiency"; only the Lean
   drifted.
2. (a) would record, inside a benchmark of open problems, a refutation of a conjecture that
   has **not** been refuted. The Lean would read as "A108864's odd-term conjecture is
   false", which is not true — `8925` is not a term of A108864.
3. (a) would leave the file's module docstring, its `A108864` reference and its `a 58 = 1155`
   index arithmetic all inconsistent with the surviving predicate.
4. Precedent: PR #4933 (Erdős 940, from tracker #4896) repaired a drifted quantifier bound
   in place, kept the statement `research open`, and used the internal contradiction as the
   *argument in the PR description* rather than as Lean content. Same shape here.

The `n = 67` counterexample is not discarded — it is the *proof that the encoding is wrong*,
and it is stated in full in the issue. If maintainers prefer (a), the switch is mechanical
and the issue says so explicitly.

### Corrected Lean definition

```lean
def perfectDeficiency (n : ℕ) : ℕ :=
  (n.divisors.sort (· ≤ ·)).foldl (fun r d => if r < d then r else r - d) n

def A (n : ℕ) : Prop :=
  0 < n ∧ perfectDeficiency n ≤ 10
```

The single guard `if r < d` captures both stopping rules of the A109883 description: once
the remainder is smaller than one divisor it is smaller than every later divisor, so the
fold is constant from that point on; and for `n > 1` the divisor `n` itself is never
subtracted, because the remainder is already `< n` once `1` has been subtracted. For `n = 1`
the only divisor `1` is subtracted, giving `0`, which is the value A109883 records.
`perfectDeficiency 0 = 0` (mathlib's `Nat.divisors 0 = ∅`), and the `0 < n` guard in `A`
keeps that junk value out of the sequence.

Added regression tests: `perfectDeficiency_values` (A109883's first ten terms) and
`a_19 : a 19 = 24` — the term that separates the two readings, and the one that fails under
the old predicate.

`conjecture` is unchanged, still `research open`, still `answer(sorry) ↔ ∀ n > 58, Even (a n)`
— and now correct, because `1155` really is `a 58`.

---

## 8. Build status

Command (per AGENTS.md, build only the changed module):

```bash
lake --wfail build 'FormalConjectures.OEIS.«108864»'
```

Result: see §8.1 below.

Trust assumptions: `conjecture` is deliberately `sorry` (`research open`); the `test`
theorems are closed by `decide`.

### 8.1 Recorded outcome

BUILD_STATUS_PLACEHOLDER

---

## 9. Immutable links (HTTP 200 verified)

LINKS_PLACEHOLDER

---

## 10. Submission

- Issue: ISSUE_URL_PLACEHOLDER
- Branch: `fix-oeis-108864-encoding` (local, on `Kuberwastaken/formal-conjectures`), based on
  upstream `638da20efd8eeeed2993fc2550fc596dc90c1ce8`.
- PR: **not opened** — left for parent review. Exact command in §11.

Section order confirmed against `UPSTREAM_PROTOCOL.md`: issue uses `Summary`,
`Counterexample`, (`Suggested fix`, from the repo's own misformalization template),
`Relationship to the C₅[K₄] campaign`, immutable audit/verifier links, `Source/status note`,
`AI assistance disclosure`.

---

## 11. Exact PR command

PR_COMMAND_PLACEHOLDER
