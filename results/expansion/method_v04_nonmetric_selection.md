# Method v0.4 non-metric selection: WOWII 179

Date: 2026-08-13  
Disposition: **SELECTED, NOT EVALUATED**  
Frozen target: WOWII 179 only  
Frozen prospective family: private-neighborhood split cliques only

This document is a selection contract. No member of the prospective family was
generated, solved, or scored while preparing it.

## 1. Selection and exclusions

Select WOWII 179:

> If \(G\) is a simple connected graph on at least two vertices, then
> \[
> L_s(G)+b(G)\geq \Delta(G)+\gamma(G)+\lambda_{\max}(G).
> \]

Here \(L_s\) is the maximum number of leaves in a spanning tree, \(b\) is the
maximum order of an induced bipartite subgraph, \(\gamma\) is domination
number, and \(\lambda_{\max}(G)=\max_v\alpha(G[N(v)])\) is maximum local
independence.

The local source ledger, `data/wowii-conjectures.json`, records the exact
formula above, the hypotheses “simple connected graph on at least 2 vertices,”
page marker `O`, note date 2005-08-08, no claimed proof or counterexample, and
no formal-conjectures file. `data/INVARIANT-GLOSSARY.md` independently fixes the
readings of \(L_s,b,\gamma,\Delta\), and \(\lambda(v)\). There is no metric or
ambiguous quotient in the statement.

The selection was made only after reading `METHOD.md`, the Method v0.1--v0.4
selection/outcome reports, the local source/status/priority ledgers, and the
local tag/release and upstream-history records. The following are out of scope:

- released 172, 176, 181, and 430a;
- external claims 64 and 309;
- active theorem/proof shadows 61, 133, 183, and 382e;
- prior Method searches 422b, 430c, 434c, 169, 174, 180, 182, 184, and 185;
- WoW I / Graph Brain work and all previously searched material.

In particular, WOWII 177 is **not fresh**. Commit `2a1abb7` is explicitly
titled `wow1<450: evaluate wow-177` and adds `### wow-177 — HOLD` to
`results/expansion/wow1_part1.md`. That discovery supersedes the initially
plausible 177 direction. No project report, tag, release, Lean file, or
target-specific commit was found for 179 in the local records inspected.
This is a freshness finding, not a claim of mathematical novelty; status must
be re-audited if a crossing is ever found.

## 2. Signed residual and theorem wall

Use the signed residual

\[
R_{179}(G)=L_s(G)+b(G)-\Delta(G)-\gamma(G)-\lambda_{\max}(G).
\]

Thus a negative value is a counterexample. Subtract the established WOWII 173
baseline

\[
L_s(G)+b(G)\geq n(G)+1
\]

by defining

\[
T_{173}(G)=L_s(G)+b(G)-(n(G)+1)\geq0
\]

and the obstruction demand

\[
Q_{179}(G)=\Delta(G)+\gamma(G)+\lambda_{\max}(G)-(n(G)+1).
\]

The exact obstruction identity is

\[
\boxed{R_{179}(G)=T_{173}(G)-Q_{179}(G).}
\]

Consequently a crossing requires \(Q_{179}>T_{173}\). This is the development
criterion: a useful transformation must raise the combined degree/domination/
local-independence demand faster than it raises the surplus in WOWII 173.

## 3. Exact equality and unit-wall evidence

Two infinite analytic controls lie exactly on the proposed wall; these are
source-reading checks, not evaluation of the frozen family.

For every complete graph \(K_n\), \(n\ge2\),

\[
L_s=n-1,\quad b=2,\quad \Delta=n-1,\quad\gamma=1,
\quad\lambda_{\max}=1,
\]

so both sides equal \(n+1\), with \(T_{173}=Q_{179}=R_{179}=0\).

For every star \(K_{1,r}\), \(r\ge2\),

\[
L_s=r,\quad b=r+1,\quad\Delta=r,\quad\gamma=1,
\quad\lambda_{\max}=r,
\]

so both sides equal \(2r+1\). Here
\(T_{173}=Q_{179}=r-1\) and again \(R_{179}=0\). Hence rounding or a one-unit
implementation error can reverse the classification on infinitely many
nonisomorphic graphs. The database gate must reproduce these equalities
exactly before any development-family row is admitted.

## 4. Frozen prospective separating family

For integers \(p\ge3\), \(2\le s\le p\), and a positive integer vector
\({\bf a}=(a_1,\ldots,a_s)\), define \(H(p;{\bf a})\) as follows:

1. begin with a clique on labelled hubs \(h_1,\ldots,h_p\);
2. for each \(1\le i\le s\), add \(a_i\) new private vertices adjacent only
   to \(h_i\);
3. add no other vertices or edges.

This is a simple connected non-metric family. It is prospective and was not
run. It is chosen because its construction separates the three obstruction
terms: changing the largest private block directly pressures \(\Delta\) and
\(\lambda_{\max}\), while distributing nonempty blocks among more hubs
pressures \(\gamma\). Simultaneously, forcing several hubs to be internal in a
leaf-rich spanning tree can pressure \(L_s\), while the clique/private-set
interface constrains \(b\). The identity above, rather than any single raw
invariant, decides whether these opposing movements cross the wall.

Freeze the minimal grid before any computation:

\[
p\in\{3,4,5,6\},\qquad s\in\{2,\ldots,\min(p,4)\},
\]

with exactly these four ordered block profiles (truncated to length \(s\)):

\[
(1,1,1,1),\ (2,1,1,1),\ (3,1,1,1),\ (3,2,1,1).
\]

Profiles are assigned to \(h_1,\ldots,h_s\) in the printed order, then graphs
are canonically deduplicated. No permutations, random cases, zero blocks,
extra edges, edge deletions, weights, graph powers, adaptive bounds, or grid
extensions are authorized. This small grid contains both balanced and
imbalanced pressure without introducing another family.

Prospective direction record (predictions, not measurements):

- increasing one block should concentrate \(\Delta\) and local independence;
- activating an additional private hub should increase domination pressure;
- extra active hubs should reduce the number of hubs that can remain leaves in
  a leaf-maximizing spanning tree;
- the induced-bipartite optimum may compensate by retaining many private
  vertices, so its exact response must be certified rather than guessed;
- a candidate is possible only when the resulting increase in \(Q_{179}\)
  exceeds the resulting \(T_{173}\).

## 5. Mandatory database gate

The gate precedes every row of the frozen family and uses exact integer
arithmetic. Evaluate, record, and certificate-check:

- every connected Graph Atlas graph of order 2 through 7;
- \(C_3,\ldots,C_{12}\), \(P_2,\ldots,P_{12}\), and
  \(K_{1,r}\) for \(2\le r\le10\);
- \(K_n\) for \(2\le n\le10\);
- \(K_{a,b}\) for \(1\le a\le b\le6\);
- Petersen, \(K_{3,3}\), \(K_7\), and the existing named project controls;
- the existing \(C_5[K_m]\) carriers for \(1\le m\le8\).

For every graph record canonical graph6, \(n,m,L_s,b,\Delta,\gamma\), every
local-independence value and its maximizing vertex, \(T_{173},Q_{179}\), and
\(R_{179}\). Store a spanning-tree/connected-domination certificate for
\(L_s\), an induced-bipartite vertex set, a dominating set, and an independent
set in the reported maximizing neighborhood. Independently verify each
certificate and the boxed identity. Required gate assertions are
\(T_{173}\ge0\), exact complete/star equalities above, and agreement of two
independent implementations on every invariant.

Any disagreement, failed certificate, negative baseline, unexpected source
crossing, or timeout is a gate failure and stops the trial before the
prospective family.

## 6. Runtime caps and stop rules

- One graph is one externally supervised process with a hard wall-clock cap of
  60 seconds; every optimizer or exploratory subprocess inside it also has a
  hard 60-second cap. Use an internal 55-second cancellation deadline so the
  process can serialize its status before the outer cap.
- A timeout is recorded as `TIMEOUT_BRACKET`, never as HOLD, equality, or a
  crossing. Do not rerun it with a larger cap and do not enlarge or reshape the
  grid.
- Run nothing from the frozen family until the whole database gate passes.
- Within the frozen grid, stop on the first independently reproduced negative
  residual. Preserve graph6 and all witnesses, then enter a separate source,
  novelty, minimality, and status audit. Selection does not authorize a public
  claim or any upstream action.
- If every admitted row is nonnegative, report only `HOLD_BOUNDED` with the
  printed bounds. Do not infer a theorem and do not extend the family.
- If an exact structural argument settles the entire frozen family before a
  run, stop and classify it as a theorem shadow; do not substitute a new family
  under this contract.
- No result here authorizes a commit, push, tag, release, issue, pull request,
  or formal-conjectures submission.

## 7. Frozen outcome

**WOWII 179 / private-neighborhood split cliques is the sole next non-metric
Method v0.4 development cluster.** It is selected because it is locally fresh,
has unambiguous invariants, admits a precise signed residual and an established
baseline obstruction identity, and has infinite exact-equality controls. The
family and all numerical results remain unevaluated.
