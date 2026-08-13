# Method v0.5 prospective selection: WOWII 305

Date: **2026-08-13 UTC**  
Disposition: **SELECTED, NOT EVALUATED**  
Frozen target: **WOWII 305 only**  
Frozen prospective family: **partial-join cyclic complements only**

This document is a selection contract. No member of the prospective family was
generated, scored, or solved while preparing it. It authorizes no publication,
repository operation, adaptive search, or replacement family.

## 1. Scope, source, and status lock

Select the source-listed-open WOWII Conjecture 305:

> If `G` is a simple connected graph with `n(G)>2`, then
> \[
> \gamma_t(G)\leq
> \left\lceil\frac23\max_{e\in E(\overline G)}
>       |N_{\overline G}(e)|\right\rceil.
> \]

The local transcription is `data/wowii-conjectures.json`, row 305, section
“Upper bounds for Total Domination,” source marker `O`, dated 2007-03-01. The
recovered definition of an edge neighborhood is the set of vertices adjacent
to at least one endpoint. The locally audited source reading, recorded in
`results/literature.md`, applies that definition wholly in the complement:
`e` is an edge of `bar(G)` and `N_bar(G)(e)` is computed in `bar(G)`. Because
the endpoints of an edge are adjacent to each other, both endpoints belong to
that union. The maximum and the outer ceiling leave no competing precedence
reading.

The operator has an empty domain when `bar(G)` has no edges. Such complete
graphs are retained in the database manifest as `NOT_APPLICABLE_EDGE_DOMAIN`;
no numerical empty-maximum convention will be invented. Every prospective
family member has a nonempty complement edge set.

WOWII is a collection already represented in
`google-deepmind/formal-conjectures`; individual WOWII 305 does not currently
have a local upstream Lean module. The locked local status audit in
`results/literature.md` found no paper, preprint, issue, pull request, or
campaign release claiming 305 as of 2026-08-12. That is sufficient for
development selection, not for a later novelty claim: any crossing must receive
a fresh, separate novelty audit.

## 2. Why this is the sole next trial

The previously computed development table supplies an exact unit wall. On
`C5[K2]`, under the source-faithful complement-edge reading,

```text
gamma_t = 3,
max |N_bar(G)(e)| = 6,
ceil((2/3) * 6) = 4,
R305 = 1.
```

Thus one unit separates the carrier sibling from a crossing. This is prior
calibration evidence, not an evaluation of the family frozen below.

The target is selected after excluding the following higher-looking but
ineligible directions:

- 61, 133, 179, 183, and 438b are active completed-trial or proof lanes;
- 172, 176, 181, and 430a are released, while 63/85 are already publicly
  completed and 64/309 are externally claimed;
- 169/174/180/182, 184/185, 382e, 422b, 430c, and 434c have already received
  bounded structured Method trials;
- 19 and 40 have active proof/status work and existing structural reductions;
- 141, 142, 145, 146, 160, 198a, 200, 291, 314, and other currently claimed or
  resolved upstream targets are not fresh development trials;
- 308 has a materially tie-order-dependent `Maxine` term and therefore fails
  this selection's unambiguous-reading requirement;
- 66 and 103 have prior family-wide obstruction arguments but no comparably
  clean untested separating coordinate;
- 401b, 412f, and 448b are corrupt or unusable as printed;
- WoW I and Graph Brain are outside the formal-conjectures-covered programme.

WOWII 186 is also excluded. The prior family report contains an unresolved
internal discrepancy: its Wave 2 table prints `co-Petersen` with slack `-1 @
186`, while the same report's no-kill summary and the release-backlog audit
report no 186 candidate. That is already-observed material requiring an
independent audit, not a prospective v0.5 trial.

## 3. Residual and theorem subtraction

For every applicable graph put `H=bar(G)` and define

```text
M(G) = max_{uv in E(H)} |N_H(u) union N_H(v)|,
m(G) = min_{uv in E(H)} |N_H(u) union N_H(v)|,
R305(G) = ceil(2 M(G) / 3) - gamma_t(G).
```

A negative residual is a counterexample.

The immediately neighboring WOWII 306 is source-marked proved and uses the
same recovered complement-edge convention:

```text
gamma_t(G) <= 2 floor(m(G) / 2).
```

Subtract that theorem by defining

```text
T306(G) = 2 floor(m(G) / 2) - gamma_t(G) >= 0.
```

The exact obstruction identity is

```text
R305(G)
  = T306(G)
    + ceil(2 M(G) / 3)
    - 2 floor(m(G) / 2).
```

Consequently a crossing requires both:

1. the complement edge-neighborhood distribution to be sufficiently narrow
   and sufficiently small that the correction after theorem subtraction is
   negative; and
2. total domination to remain close enough to the proved 306 cap that `T306`
   does not absorb that negative correction.

On the full-join `C5[K2]` calibration graph the target residual is one. The
obstruction is not simply “make the complement sparse”: arbitrary sparsening
can create a two-vertex total dominating set in `G`, moving `gamma_t` down as
fast as the right-hand side. A useful transformation must lower all large
complement edge neighborhoods globally while preserving the obstruction to a
two-vertex total dominating set.

## 4. Frozen separating family

For integers `s>=2` and `1<=d<s`, define an auxiliary graph `H(s,d)` on

```text
Z/5Z x Z/sZ.
```

There are no edges within a fibre `{i} x Z/sZ`. Between each consecutive pair
of fibres `i` and `i+1`, join `(i,a)` to `(i+1,b)` exactly when

```text
b - a mod s is in {0,1,...,d-1}.
```

There are no other edges. The prospective graph is

```text
G(s,d) = complement(H(s,d)).
```

At the omitted boundary value `d=s`, every consecutive fibre pair is a
complete bipartite join. After relabelling the self-complementary five-cycle,
`G(s,s)` is the already-evaluated `C5[Ks]` calibration family. The prospective
rows use only `d<s`; they replace every complete quotient join by the same
circulant partial join and have not been evaluated in the project records
inspected for this selection.

This is a global orbit transformation, not one- or two-edge surgery. It is
chosen prospectively because decreasing `d` removes the same offset class from
all five complement interfaces. It should therefore lower `M` and `m`
throughout the graph instead of leaving untouched symmetric edges at the old
maximum. Meanwhile, the five cyclic fibres retain repeated common-neighbor
constraints that may keep `gamma_t(G)` at three after a small amount of
thinning. Those are directional predictions, not measured facts.

Freeze the complete grid

```text
2 <= s <= 8,
1 <= d < s.
```

This is exactly 28 labelled parameter rows before canonical graph6
deduplication. The offset set is exactly the initial interval printed above.
No other offset subsets, twists, quotient lengths, weights, random rows,
individual edge edits, adaptive refinements, or parameter extensions are
authorized.

For every row the preregistered term directions are:

| term | prediction as `d` decreases from the full-join boundary |
|---|---|
| `M` | decrease or stay pinned at a lower orbit value |
| `m` | decrease, preferably in step with `M` |
| `ceil(2M/3)` | decrease at its integer thresholds |
| `gamma_t(G)` | initially pinned at three, then possibly decrease |
| `T306` | decrease only if the proved cap approaches actual `gamma_t` |
| `R305` | decrease exactly when the RHS threshold falls before `gamma_t` |

## 5. Mandatory database-sanity gate

No `G(s,d)` row may be constructed or evaluated until the complete gate has
passed under the exact reading above. The gate consists of:

- every connected Graph Atlas graph of order three through seven;
- `P3`--`P12`, `C3`--`C12`, stars `K1,r` for `2<=r<=10`, and complete
  bipartite graphs `K(a,b)` for `1<=a<=b<=6`;
- complete graphs `K3`--`K10`, retained explicitly as
  `NOT_APPLICABLE_EDGE_DOMAIN` rather than assigned an empty maximum;
- Petersen, `K3,3`, `K7`, `T(7)`, the carrier and `C5[Ks]` for `1<=s<=8`,
  and the existing named project controls.

For every applicable graph record canonical graph6, `n`, `m`, `gamma_t`, the
entire multiset of complement edge-neighborhood orders, minimizing and
maximizing complement edges, `m(G)`, `M(G)`, `T306`, and `R305`. Record an
explicit minimum total-dominating set and independently verify both total
domination and minimality.

Two independent implementations are mandatory:

1. a bitset implementation with exact subset enumeration for `gamma_t` and
   direct complement-neighborhood unions; and
2. a NetworkX/set implementation with an independently formulated binary
   optimization for `gamma_t`, followed by direct witness replay.

The gate requires exact agreement on every applicable invariant, `T306>=0` on
every applicable control, reproduction of the `C5[K2]` unit residual above,
and no unexplained source-statement crossing. A disagreement, a failed
certificate, a violation of proved 306, an unexpected 305 control crossing,
or any timeout stops the trial before the prospective grid.

## 6. Runtime caps, incremental output, and strict stops

- One graph is one externally supervised process with a hard wall-clock cap of
  60 seconds. Every optimizer and child process inside it also has a hard
  60-second cap; use an internal 55-second cancellation deadline so status can
  be serialized.
- Append and `fsync` each gate and grid row independently. A timeout is
  `TIMEOUT_BRACKET`, never a hold, equality, or crossing. Do not rerun with a
  larger cap.
- Run no grid row until the entire gate and its independent replay pass.
- Canonically deduplicate the fixed 28 parameter rows, but preserve every
  `(s,d)` alias in the ledger.
- Stop on the first negative `R305` only after a second implementation
  reproduces `gamma_t`, `M`, the complement-edge witnesses, the graph6
  encoding, and the signed residual. Preserve that row and enter a separate
  source, status, novelty, family-proof, minimality, Lean, and release audit.
- If all admitted rows are nonnegative, report only `HOLD_BOUNDED` for the
  printed grid. Do not extend it or infer the conjecture.
- If an exact argument settles every frozen row before execution, record
  `THEOREM_SHADOW` and stop; do not substitute a different family under this
  contract.
- No outcome here authorizes a README edit, tag, release, issue, pull request,
  upstream write, or public claim.

## 7. Frozen outcome

**WOWII 305 / partial-join cyclic complements is the sole next prospective
Method v0.5 trial.** It has a source-faithful single reading, exact unit-slack
evidence, a neighboring proved theorem baseline, an explicit obstruction
identity, and one previously unevaluated transformation designed to move the
controlling complement-neighborhood coordinate globally. Every numerical
result for the frozen family remains unknown at selection time.
