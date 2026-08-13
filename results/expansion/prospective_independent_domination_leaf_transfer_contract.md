# Frozen prospective trial: independent-domination leaf transfer

Frozen: **2026-08-13 UTC, after theorem/status audit and before development evaluation**

## Current target and known-domain gate

The current DeepMind declarations `independentDominationEven` and
`independentDominationOdd` formalize Conjecture 1.6 of Cho--Choi--Park for
finite isolate-free graphs of maximum degree `D`.

The source paper proves the conjecture for `D<=4` and reports omitted
case-checks for `D in {5,6,7,8}`. The current upstream declarations remain
`research open`. This trial starts at `D=9`, outside those recorded proved or
checked degrees. The development graph has `D=10`; no source found in the
pre-freeze audit establishes the general conjecture at that degree.

## Exact equality carrier

For integers `q,p`, let `H(q,p)` be a clique on `q` centers with `p` private
pendant leaves attached to each center. The paper identifies
`H(floor(D/2)+1,ceil(D/2))` as the extremal family.

Freeze `H(5,5)`, with centers `0..4` and five leaves at each center. It has

- `n=30`;
- maximum degree `D=9`;
- independent domination number `i=21`;
- odd-case equality `120*21 = 84*30 = 2520`.

## Sole frozen transformation

Move the canonical first private leaf of center 0 to center 1: delete its edge
to center 0 and add its edge to center 1. Make no other change.

No alternate leaf, reverse transfer, second transfer, center-edge change, or
adaptive variant is permitted. The development cap is one graph.

## Predicted coordinate direction

The graph remains isolate-free. Center degrees change from `(9,9,9,9,9)` to
`(8,10,9,9,9)`, so maximum degree becomes even `D=10`.

For any `H`-type private-leaf graph, an independent dominating set either
chooses one center and every leaf belonging to other centers, or chooses every
leaf. The predicted optimum therefore chooses center 1, which now owns six
leaves, plus all 19 leaves at the other centers: `i=20`.

The even-case residual is predicted to be

`(D^2+4)n - (D+2)^2 i = 104*30 - 144*20 = 240`,

strictly safe. The transformation preserves the isolate-free premise rather
than making the statement vacuous.

## Mandatory protocol

1. Exhaust every connected isolate-free Atlas graph of orders 2--7, compute
   exact independent domination by exhaustive maximal-independent-set search,
   and require zero violations.
2. Reproduce small `H(q,p)` controls and exact `H(5,5)` equality using an
   independently checkable structural certificate.
3. Construct only the frozen one-leaf transfer and exactly compute `n,D,i`
   with an exact ILP capped at 60 seconds.
4. Independently prove the optimum by exhaustive center-choice reduction and
   replay an explicit independent dominating witness.
5. Stop on any numerical violation, status ambiguity, or known-domain match.

The JSONL ledger is append-only. No WoW I source, random search, commit, push,
release, issue, PR, or other public action is authorized.
