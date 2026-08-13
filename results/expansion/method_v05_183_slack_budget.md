# Method v0.5 Lane P1: the outside-transversal budget is a theorem

Date: **2026-08-13**. Status: **the first numerical half of the
slack-funded attachment lemma is proved, in a stronger form valid for every
connected graph and every choice of centre; the remaining attachment half
survives the frozen live controls and the exact `H_m`/`J_m` ranges, but is not
proved**.

This note continues `method_v05_183_outside_neighborhood.md`. It does not
widen a catalogue or generate a new graph collection. The only finite graph
checks use the frozen connected Graph Atlas and McKay order-eight inputs.
Every subprocess was externally capped at 60 seconds.

## Notation and the proposed first half

For a connected graph `G` and vertex `x`, write

```text
d = deg_G(x),
H_x = G-N_G(x),
s_x = n-d-gamma_c(G),
tau_odd(F) = |V(F)|-b(F).
```

Here `N_G(x)` is the **open** neighborhood. Thus `H_x` contains `x` as an
isolated vertex, together with the subgraph induced by all vertices at
distance at least two from `x`. This convention is essential: replacing the
open neighborhood by `N[x]` changes both the order and the bipartite number
by one.

The proposed first half was

```text
tau_odd(H_x) <= s_x.
```

Since `|V(H_x)|=n-d`, it is equivalent to the cleaner inequality

```text
b(H_x) >= gamma_c(G).
```

That inequality is universally true.

## Rooted DeLaViña--Waller lemma

The needed ingredient is a rooted strengthening already implicit in the
proof of DeLaViña and Waller's theorem.

> **Rooted trunk lemma.** Let `C` be a connected graph of order at least two,
> and prescribe any vertex `v in V(C)`. Then `C` has a connected dominating
> set `D` such that
>
> ```text
> v in D and |D| <= b(C)-1.
> ```

DeLaViña and Waller prove the unrooted numerical statement as Theorem 4
(Graffiti.pc 173) in:

> Ermelinda DeLaViña and Bill Waller, *Spanning Trees with Many Leaves and
> Average Distance*, Electronic Journal of Combinatorics **15** (2008), #R33,
> Theorem 4; proof on pp. 10--11.

Official source:

```text
https://www.combinatorics.org/ojs/index.php/eljc/article/download/v15i1r33/pdf
```

Their proof begins with an **arbitrary** vertex `x0`. It grows connected
bipartite colored blocks `B0,B1,...,Bk`, joins them with connector vertices,
and then deletes one chosen leaf `rj` from the spanning tree of each block.
The first block has at least two vertices, and its deleted leaf is explicitly
chosen different from `x0`. Hence `x0` remains in the final connected
dominating trunk. The final order count is

```text
|B0 union ... union Bk| + k-(k+1) <= b(C)-1.
```

Taking the arbitrary starting vertex `x0` to be the prescribed `v` proves the
rooted statement. This is not an assumption beyond their construction; it is
the same proof with its free initial choice retained.

## Universal outside-neighborhood theorem

> **Theorem.** For every finite simple connected graph `G` and every vertex
> `x`,
>
> ```text
> gamma_c(G) <= b(G-N_G(x)).
> ```

Proof. Let `C1,...,Ck` be the connected components of `G-N_G[x]`. Since `G`
is connected, for each `Ci` choose an attachment edge

```text
ai-vi, with ai in N_G(x) and vi in V(Ci).
```

If `Ci` is a singleton, put only `ai` into the set being constructed. This
uses one vertex, equal to `b(Ci)`, and dominates that singleton.

If `Ci` has at least two vertices, apply the rooted trunk lemma inside `Ci`
with root `vi`. It gives a connected dominating set `Di` of `Ci`, containing
`vi`, with

```text
|Di| <= b(Ci)-1.
```

Put `ai` and all of `Di` into the set being constructed. This portion has at
most `b(Ci)` vertices and is connected to `x` along `x-ai-vi`.

Taking the union over all components and adding `x` produces a connected
dominating set of `G`: `x` dominates its entire open neighborhood, while each
component `Ci` is dominated by its allocated portion. Its order is at most

```text
1 + sum_i b(Ci).
```

On the other hand, `G-N_G(x)` is the disjoint union of the isolated vertex
`x` and the components `Ci`. The induced-bipartite number is additive over
components, so

```text
b(G-N_G(x)) = 1 + sum_i b(Ci).
```

This proves the theorem. QED.

## The numerical half follows exactly

The universal theorem immediately gives

```text
tau_odd(H_x)
  = |V(H_x)|-b(H_x)
  <= (n-d)-gamma_c(G)
  = s_x.
```

Thus the first half needs none of the special live hypotheses: not
claw-freeness, not `L3(x)={z}`, not nonbipartiteness, and not
`gamma_c>=5`. It is a local refinement of the global DeLaViña--Waller bound,
obtained by applying their rooted construction independently beyond the
closed neighborhood of `x`.

Equivalently, there always exists a set

```text
U subset V(H_x),  |U|<=s_x,
```

such that `H_x-U` is bipartite. A minimum odd-cycle transversal of `H_x`
supplies such a set.

## Exact frozen-control audit

The complete slack-funded lemma additionally asks, after choosing such a
set `U`, for a subset `P subset N(x)` satisfying

```text
G[((V-N(x))-U) union P] is bipartite,
|P| >= |U|+2-s_x.
```

An exact checker enumerated every admissible `U` through size `s_x` and every
candidate `P` for each qualifying live orientation. It separately checked
the now-proved numerical inequality `b(H_x)>=gamma_c(G)`.

| catalogue | qualifying graphs | qualifying `(x,z)` pairs | numerical failures | full-budget failures |
|---|---:|---:|---:|---:|
| Graph Atlas, orders at most 7 | 0 | 0 | 0 | 0 |
| McKay connected order 8 | 5 | 9 | 0 | 0 |

All nine order-eight orientations have

```text
gamma_c=5, d(x)=3, |H_x|=5,
s_x=0, b(H_x)=5.
```

Hence `U` is empty in every case. Every orientation has an explicit
two-vertex retention set `P`, reproducing the earlier frozen retention audit.
The five graph6 strings are

```text
G?`aeG  G?b@dG  G?qacg  G?qadO  GCQ`e_.
```

The McKay file remains `/tmp/graph8c.g6`, containing 11,117 connected graphs,
with SHA-256

```text
0002354f1ab3344a2706626a037ad15367bf23a2163aa68f552c3a169ca9a036.
```

This is a bounded test of the attachment half, not part of the proof of the
universal numerical half.

## Mandatory equality family `H_m`

For `H_m`, `m>=4`, at `x=q0`, the exact values are

```text
n=2m+1, d=m, gamma_c=m+1,
s_x=0,
H_x a forest of order m+1,
b(H_x)=m+1=gamma_c.
```

Thus the numerical theorem is exact. Take `U` empty and retain

```text
P={r0,qj}, for any j!=0.
```

The resulting induced graph is a forest, so the full attachment budget also
holds exactly with `|P|=2`. Exact finite checks reproduced these witnesses for
every `m=4,...,12`; the displayed construction proves all `m>=4`.

## Perturbed equality family `J_m`

For `J_m`, `m>=5`, formed by making `{r2,r3,r4}` a triangle, the exact values
proved in the preceding note are

```text
n=2m+1, d=m, gamma_c=m,
s_x=1,
tau_odd(H_x)=1,
b(H_x)=m=gamma_c.
```

The numerical theorem is again exact. Delete any one triangle vertex; for
example, take

```text
U={r2}.
```

Then retain

```text
P={r0,q3}.
```

The retained graph is a forest. Moreover,

```text
|P|=2=|U|+2-s_x.
```

Thus both halves of the budget are exact on `J_m`. Exact finite checks
reproduced a witness for every `m=5,...,12`; the displayed construction proves
all `m>=5`.

## The exact attachment-budget identity

The remaining problem can be stated without losing or double-counting a
single unit of slack. For every set `U subset V(H_x)` such that `H_x-U` is
bipartite, define

```text
rho_x(U) = maximum |P| over P subset N(x)
           such that G[(V(H_x)-U) union P] is bipartite.
```

Then the following is an identity, not a conjectural inequality:

```text
tau_odd(G)
  = min over bipartizing U subset V(H_x)
      ( |U| + d-rho_x(U) ).
```

Proof. Any odd-cycle transversal `T` splits uniquely into

```text
U=T intersect V(H_x),
T intersect N(x).
```

Writing `P=N(x)-T`, its size is `|T|=|U|+d-|P|`, and the retained graph is
bipartite. Conversely, every admissible pair `(U,P)` deletes exactly
`U union (N(x)-P)` and leaves the displayed bipartite induced graph. Minimizing
over both descriptions gives the identity. QED.

Since the first half now proves that a bipartizing `U` exists with
`|U|<=s_x`, WOWII 183 in the live core is equivalent to finding one such `U`
with

```text
rho_x(U) >= |U|+2-s_x.
```

This is the next genuine attachment obligation. The outside-transversal cost
itself is no longer a missing lemma; only the number of first-layer vertices
that can be reattached compatibly remains unresolved.

## Reproduction discipline and honest stop point

All finite checks used the repository's pinned environment with an external
timeout:

```bash
timeout 60s /home/ec2-user/.venvs/wowii/bin/python <exact-budget-checker>
```

The checker reused the exact subset routines in
`scripts/method_v03_183_lemma_check.py`. It did not write a new catalogue or
expand the frozen graph bound.

The result is:

1. `tau_odd(G-N(x))<=s_x` is proved for every connected graph and every
   vertex `x` under the open-neighborhood convention.
2. The inequality is exact on every frozen high-tier orientation and on both
   infinite equality families `H_m` and `J_m`.
3. The complete slack-funded attachment statement has zero failures in the
   frozen gate and is exact on `H_m` and `J_m` through the tested ranges, but
   no paper proof is claimed.
4. The exact `rho_x(U)` identity isolates the only remaining issue: compatible
   reattachment of enough vertices from `N(x)` after the outside graph is
   bipartized.

Accordingly this lane advances from a numerical `THEOREM_SIGNAL` to a proved
universal numerical lemma, while WOWII 183 itself remains open in the final
attachment step. No public counterexample or full proof follows from this
note.
