# Erdős Problems formalization-faithfulness audit — LOW-ID BAND (live search 2026-08-15)

**Lane.** TEXT-vs-TEXT faithfulness at breadth. Companion to
[`erdos-faithfulness-audit.md`](erdos-faithfulness-audit.md) (high band, ids 1212→1026,
retired agent) and to the sibling depth lane in
[`erdos-hunt.md`](erdos-hunt.md) (`CANDIDATE_FOR_DEPTH` computations).

**Why low band.** The high-band predecessor's structural conclusion: every one of its 53
audited declarations was certificate-shape-incompatible with a finite witness (asymptotic /
density / `Set.Infinite` / cardinal / `answer(sorry)` fixed optimum). Ids 1000+ are
overwhelmingly analytic number theory. The low-id band is where Erdős' finite/combinatorial
problems live, so a `FINITELY_FALSE_AS_STATED` verdict has a materially higher prior here.

---

## HANDOFF STATE

**Traversal:** strictly **ascending** numeric id over
`results/expansion/open_targets_oeis_erdos_20260815.json`, `corpus=="ErdosProblems"`,
`previously_touched==false` (364 rows). Ascending id list frozen at
`/tmp/claude-1000/-Users-kuber-mehta-Projects-scratch/21f73cfa-6e97-457f-8bb8-ae31d911cc43/scratchpad/faith/ids_asc.txt`
(line 1 = `1`, line 364 = `1212`).

**AUDITED so far:** see the verdict table. **RESUME POINT:** first id in `ids_asc.txt`
after the last table row.

**Cache:** `…/scratchpad/faith/epcache/<id>.html` — the first 90 ascending ids are cached
(plus the predecessor's 180 descending ids ≥ ~700). Re-fetch with the desktop `User-Agent`
recipe recorded in the predecessor's file.

**Frozen provenance**

| coordinate | value |
|---|---|
| upstream repo | `google-deepmind/formal-conjectures` |
| upstream pin | `2411d22e1bd550d050d0eac6c1fb379a76a3e7c5`, read via `git show upstream/main:<path>` (read-only) |
| canonical source | `https://www.erdosproblems.com/<id>` (fetched 2026-08-15; page `last edited` recorded per target) |
| target list | `results/expansion/open_targets_oeis_erdos_20260815.json` |
| traversal order | **ascending numeric id** (predecessor took descending; sibling takes `finite_signals` rank) |
| compute | `/home/ec2-user/.venvs/wowii/bin/python`, exact integer arithmetic, 60 s cap per process |

**Severity ledger** (same as the predecessor's, plus one new label needed here)

- `FAITHFUL` — no divergence beyond notation.
- `COSMETIC` — junk/edge values, index shifts, ordered-vs-unordered counting, dropped
  "sufficiently large" that is provably harmless; truth value unchanged.
- `MATERIAL_BUT_STILL_TRUE` — genuinely a different statement, but no finite object refutes it.
- `MATERIAL_TRIVIALLY_DETERMINED` — **new label.** The Lean encodes a question whose answer is
  settled by routine mathematics while the source question is open. Not finitely certifiable,
  but the declaration no longer poses the Erdős problem.
- `FINITELY_FALSE_AS_STATED` — an explicit finite witness refutes the literal declaration.
- `VACUOUS_AS_STATED` — the literal declaration is trivially satisfiable.
- `STATUS_SYNC` — status coordinates disagree. Per METHOD rule 9, never a discovery claim.

**Publication.** No upstream issue, PR, comment, or any other public write was made or is
proposed. No `git` mutation was run. Internal reading record only.

---

## Verdict table

| id | site state / prize | open decl(s) | divergence | severity | cert. shape |
|---|---|---|---|---|---|
| 1 | open / OPEN | `erdos_1`, `.variants.real` | none material. `N ≠ 0` guard is *necessary* (`A = ∅ ⊆ Icc 1 0` would force `C·2⁰ < 0`); strict `<` vs source `≫` is absorbed by the `∃ C > 0`. `IsSumDistinctSet` injectivity is over `A.powerset`, correct. `.variants.real` matches "subset sums all differ by at least 1" via `Pairwise (1 ≤ dist ·)` | FAITHFUL | `∃ C` global constant |
| 3 | open / OPEN | `erdos_3` | `Set.IsAPOfLength` = `∃ a d, ENat.card s = l ∧ s = {a + n•d | n < l}`. The `ENat.card s = l` clause **forces `d ≠ 0`** for `l ≥ 2`, so no degenerate constant-AP vacuity. `¬ Summable (1/a)` over the subtype is the right reading of `∑ 1/n = ∞` (positive terms). `0 ∈ A` gives `1/0 = 0`, harmless | FAITHFUL | `∃ᶠ k` over ℕ |
| 5 | open / OPEN | `erdos_5`, `.variants.limit_point_set`, `.variants.dense` | `primeGap n = nth Prime (n+1) − nth Prime n` is 0-indexed, so `normalizedGap m = (p_{m+2}−p_{m+1})/log m` in the source's 1-indexing — a **uniform index shift of 1** between numerator and `log`; harmless for limit points since `log(n−1)/log n → 1`. `normalizedGap 0 = normalizedGap 1 = 0` junk (`log 1 = 0`, `x/0 = 0`) — cannot move an `atTop` cluster set. Restriction of `limitPointSet` to *finite* limit points is documented and `.variants.westzynthius` carries `∞` | COSMETIC | limit-point set |
| 7 | open / VERIFIABLE | `erdos_7` | `StrictCoveringSystem` extends `CoveringSystem` with `injective_moduli`, which **is** the source's "distinct" — without it, `{0,1,2 mod 3}` would settle the problem trivially. `ne_bot` kills modulus 0; `¬ (moduli i ≤ Ideal.span {2})` ⇔ `¬ 2 ∣ n` (ℤ is a PID) ⇔ odd; the extra `moduli i ≠ ⊤` is redundant (already a `CoveringSystem` field) but harmless. Lean parses as `(¬ ≤) ∧ (≠ ⊤)` (`¬` binds at 40, `∧` at 35) | FAITHFUL | `∃` covering system — construction can prove, cannot disprove |
| 9 | open / OPEN | `erdos_9` | `Erdos9A = {n | Odd n ∧ ¬∃ p k l, p.Prime ∧ n = p + 2^k + 2^l}` matches "odd integers ≥ 1 not of the form p+2^k+2^l, k,l ≥ 0" exactly (`Odd n` in ℕ ⇒ `n ≥ 1`). `upperDensity` matches "upper density". Doc nit: the site credits Crocker [Cr71] for infinitude, the Lean variant credits Schinzel via [Er77c] | FAITHFUL | `0 < upperDensity` |
| 10 | open / OPEN | `erdos_10`, `.variants.granville_soundararajan_odd`, `.variants.grechuk` | `erdos_10` **drops "large"**: it asserts `sumPrimeAndTwoPows k = Set.univ \ {0,1}`, i.e. *every* `n ≥ 2`. Provably harmless: every `n ≥ 2` is `2 + (popcount(n−2) powers of 2)`, so each small `n` has *some* representation and `k` can absorb the finite exceptional set — the "all n" and "all large n" forms are equivalent. `= Set.univ \ {0,1}` also asserts `0,1 ∉` the set, true since `p ≥ 2`. GS variant likewise drops "large" — **exhaustively checked**: no odd `n < 3·10⁵` outside `sumPrimeAndTwoPows 3`, no even `n < 3·10⁵` outside `sumPrimeAndTwoPows 4` | COSMETIC | `∃ k` / infinite set |
| 11 | open / OPEN | `erdos_11`, `.variants.not_four_dvd`, `.variants.two_pow_two` | all three **drop "large"** and substitute `1 < n`. Exhaustively checked to `3·10⁵`: zero failures for (a) odd `n > 1`, (b) `¬ 4 ∣ n`, `n > 1`, (c) odd `n > 1` with exactly two powers. Consistent with Odlyzko (10⁷) and Hercher (2⁵⁰). `Squarefree 1` holds and `Squarefree 0` fails in Mathlib, both correct here. `1 < n` is necessary (`n = 1` has no representation, min value 2) | COSMETIC | universal over ℕ (sibling lane is depth-testing these) |
| 12 | open / OPEN | `.parts.iii` | `IsGood` renders "no **distinct** a,b,c with a ∣ b+c, b,c > a" as `a ∣ b+c → a < b → a < c → b = c`, which correctly permits `b = c` (contrast EP 13, where the source omits distinctness and the Lean correctly omits it too). `0 ∈ A` is unconstrained but `1/0 = 0` cannot affect summability | FAITHFUL | `∀ A` infinite → Summable |
| 13 | **solved / PROVED** | `.variants.general` | headline `erdos_13` correctly `research solved` (Bedert). In `.variants.general`, `r = 0` makes the hypothesis `∀ a ∈ A, ¬ (a ∣ 0)`, i.e. `A = ∅` — **vacuous but not false** (conclusion `0 ≤ N/1 + C`). `b : Fin r → ℕ` allows repeats, matching the source's non-distinct `b_1,…,b_r` and reducing at `r = 2` to the (repeat-allowing) `IsForbiddenTripleFree` of the headline | COSMETIC (`r = 0` lobe vacuous) | `∀ r ∃ C ∀ N` |
| 14 | open / OPEN | `.parts.i`, `.parts.ii` | `allUniqueSums` is "exactly one **unordered** pair", and it admits `p.1 = p.2` (so `2a` is a legal representation) — the standard reading of "sum of two elements". `f ≫ g` unfolds to `IsBigO atTop g f`, so `.parts.i` is `N^{1/2−ε} = O(|{1..N}\B|)`, correct for `≫_ε`. `.parts.i` quantifies `∀ A` including `A = ∅` (then `|{1..N}\B| = N`), harmless | FAITHFUL | asymptotic |
| 15 | open / OPEN | `erdos_15` | **`Summable` used for a conditionally convergent alternating series.** See the finding block below. Index/sign bookkeeping is otherwise exactly right (`(−1)^(k+1)·(k+1)/nth Prime k` ↔ `(−1)^n·n/p_n`) | **MATERIAL_TRIVIALLY_DETERMINED** | RHS provably `False`; no finite cert |
| 17 | open / OPEN | `erdos_17` | none. `(p − 3 : ℤ)` deliberately avoids ℕ truncation (`p = 2 ⇒ −1`, vacuous). `n = 0` admitted and satisfiable (`2 − 2`). Database gate: the file's own `isClusterPrime_97_isLeast_non_cluster` matches the site's "the first prime without this property is 97" | FAITHFUL | `Set.Infinite` |

---

## Findings requiring detail

### EP 15 — `Summable` encodes absolute/unconditional convergence; the source asks about conditional convergence

`FormalConjectures/ErdosProblems/15.lean`:

```lean
@[category research open, AMS 11]
theorem erdos_15 : answer(sorry) ↔
    Summable (fun k : ℕ => (-1 : ℚ) ^ (k + 1) * (k + 1) / (k.nth Nat.Prime)) := by
  sorry
```

Site statement (`erdosproblems.com/15`, last edited: not shown): *"Is it true that
$\sum_{n=1}^\infty(-1)^n\frac{n}{p_n}$ converges, where $p_n$ is the sequence of primes?"* —
Erdős' question, and Tao's conditional theorem [Ta23], are about **convergence of the
sequence of partial sums**, i.e. conditional convergence of an alternating series.

Mathlib's `Summable f` means `∃ a, HasSum f a`, and `HasSum f a` is convergence of the net of
**finite-subset** partial sums — i.e. *unconditional* summability. Over ℝ (finite dimensional)
unconditional ⇔ absolute. Here the absolute series is
$\sum_n n/p_n$, and $p_n \sim n\log n$ gives $n/p_n \sim 1/\log n$, whose sum diverges.
Hence the RHS is **provably false**. (The codomain is ℚ, which only makes it stronger:
`HasSum` in ℚ pushes forward along the continuous additive embedding ℚ ↪ ℝ to `HasSum` in ℝ.)

Consequence: the correct `answer(...)` for this declaration is `False`, obtainable from
Mertens/PNT alone, whereas the Erdős problem the file cites is open. The declaration therefore
does not encode the source question. The faithful encoding is the usual partial-sum idiom,
e.g. `∃ l : ℝ, Tendsto (fun N => ∑ k ∈ Finset.range N, f k) atTop (𝓝 l)`.

- **Severity:** `MATERIAL_TRIVIALLY_DETERMINED`. Not `FINITELY_FALSE_AS_STATED`: refuting the
  RHS needs the divergence of `∑ 1/log n`, not a finite witness.
- **Certificate shape:** no finite replayable certificate.
- **Duplicate check:** NOT YET RUN (no upstream issue/PR search performed).
- Cross-check inside the corpus: the same file's neighbours use `Summable` correctly for
  positive-term series (EP 3 `¬ Summable (1/a)`, EP 12 `.parts.iii Summable (1/n)`), so this is
  an isolated idiom slip rather than a corpus-wide convention.

---

## Running severity roll-up

| severity | count | ids |
|---|---|---|
| `FINITELY_FALSE_AS_STATED` | 0 | — |
| `VACUOUS_AS_STATED` | 0 | — |
| `MATERIAL_TRIVIALLY_DETERMINED` | 1 | 15 |
| `MATERIAL_BUT_STILL_TRUE` | 0 | — |
| `STATUS_SYNC` | 0 | — |
| `COSMETIC` | 4 | 5, 10, 11, 13 |
| `FAITHFUL` | 7 | 1, 3, 7, 9, 12, 14, 17 |
