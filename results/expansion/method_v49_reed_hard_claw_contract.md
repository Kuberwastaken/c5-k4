# Frozen prospective trial: hard-claw Reed blocker CNF

Frozen: **2026-08-13 UTC, before SAT selection or transformed evaluation**

## Fixed carrier and reuse catalogue

The carrier is `C5[K3]`, with vertices `0..14` in consecutive three-vertex
bags. Its exact 9,720 optimal eight-color partitions (seven independent pairs
and one singleton) are the immutable reuse catalogue.

For each new vertex and carrier color class, that old color is reusable iff
the selected carrier neighborhood misses the whole class. For every proper
assignment of old colors to the new-vertex template, the CNF requires at least
one assigned class to be hit. Satisfiability therefore certifies that no
eight-color extension of any carrier optimum exists.

## Hard induced-claw constraint

The first new vertex is `x0`. Every model must contain the explicit induced
claw with center carrier vertex `0` and leaves `x0,5,14`. Thus the CNF fixes

- edge `0-x0` present;
- edges `5-x0` and `14-x0` absent.

Carrier edges already make `0` adjacent to `5,14` while `5` and `14` are
nonadjacent. This is a selection constraint, not a post-selection filter.

## Frozen enumeration order

1. number of new vertices `k = 1,2,3`;
2. total coordinate-increment budget `s = 0,1,2,3,4`;
3. maximum-degree increment `d = 0..s`, with clique increment `w=s-d`;
4. simple new-vertex internal graph by increasing binary edge mask, where
   pairs are lexicographically ordered;
5. Glucose4's deterministic first model under carrier-incidence variable order
   `(x0-v0,...,x0-v14,x1-v0,...)`.

For budget `(d,w)`, hard clauses enforce transformed `Delta<=8+d` and
`omega<=6+w`. Degree clauses cover both carrier loads and new-vertex degrees.
Clique clauses exhaust every carrier clique combined with every clique of the
fixed new-vertex template.

The first SAT model is frozen immediately. No later model, rotation, alternate
claw, or adaptive neighborhood is permitted. If no model exists for `k<=3`
and `d+w<=4`, the verdict is `NO_APPLICABLE` and no transformed evaluation is
run.

## Evaluation gates

Before exact transformed evaluation:

1. re-run the exact 995-graph connected Atlas gate and require zero Reed
   violations;
2. verify the 9,720-pattern catalogue and hard claw;
3. audit the current source/status and known Reed theorem domains;
4. stop without evaluation on a known-domain match or ambiguity.

Only an open-domain first model receives exact DSATUR `chi`, exact clique
search `omega`, direct `Delta`, and independent fixed-order coloring plus
exhaustive clique-subset recomputation.

Reed's conjecture is a major human open problem. Any negative numerical result
is only an adversarial candidate pending theorem-conflict resolution and
expert audit. Every subprocess has a hard 60-second cap. No commit, push,
release, issue, PR, or other public action is authorized.
