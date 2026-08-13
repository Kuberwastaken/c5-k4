# Method v0.7 Lane P1: Lean certification of the attachment collapse

Date: **2026-08-13**. Status: **the local claw-free attachment reductions are
formalized warning-clean and without `sorry`; the existence of a clean vertex
or compatible clean pair remains unresolved and is not asserted**.

This note continues `method_v06_183_attachment.md`. It adds only

```text
lean/GraphConjecture183Attachment.lean
```

and does not change any earlier theorem, report, or upstream checkout.

## Formalized definitions

The module introduces the local induced-claw exclusion actually used by the
paper proof:

```lean
def IsClawFree (G : SimpleGraph V) : Prop :=
  ∀ ⦃p x u v : V⦄, G.Adj p x → G.Adj p u → G.Adj p v →
    x ≠ u → x ≠ v → u ≠ v →
    G.Adj x u ∨ G.Adj x v ∨ G.Adj u v
```

This is exactly the statement that three distinct leaves at a common center
cannot be pairwise nonadjacent. The outside attachment set is

```lean
outsideAttachments G x p = {v | G.Adj p v ∧ v ≠ x ∧ ¬G.Adj x v}.
```

It is the set-theoretic form of
`N_G(p) ∩ (V(G - N_G(x)) - {x})`; the explicit `v ≠ x` matters because the
open-neighborhood deletion retains `x`.

## Certified reductions

### 1. Attachment clique lemma

```lean
theorem isClique_outsideAttachments_of_isClawFree
```

If `p` is adjacent to `x` and `G` is claw-free, then
`outsideAttachments G x p` is a clique. For two distinct alleged
nonadjacent attachments `u,v`, the vertices `x,u,v` are three distinct
pairwise nonadjacent neighbors of `p`, contradicting `IsClawFree G`.

### 2. Bipartite cliques have order at most two

The module proves both the ambient and induced forms:

```lean
theorem IsClique.card_le_two_of_isBipartite
theorem card_le_two_of_isClique_of_induce_isBipartite
```

The ambient proof applies Mathlib's clique bound for a coloring to a
two-coloring. The induced proof extracts the repository's finite induced
two-coloring and proves that its restriction to the clique is injective.

The reusable restriction bridge

```lean
theorem induce_isBipartite_of_finset_subset
```

shows that bipartiteness of an induced graph on a finite retained set passes
to every finite subset.

### 3. Attachment order and clean-vertex necessity

```lean
theorem attachment_card_le_two
```

says that any finite collection of outside attachments has order at most two
when its induced graph is bipartite. This is the formal version of the paper
step that an attachment clique inside the bipartite remainder cannot have
three vertices.

The sharper statements

```lean
theorem attachment_card_le_one_of_induce_insert_isBipartite
theorem attachment_card_le_one_of_retained_isBipartite
```

formalize clean-vertex necessity. If `p` and a finite attachment collection
`A` lie in a retained vertex set whose induced graph is bipartite, then

```text
|A| <= 1.
```

Indeed `A` is a clique by claw-freeness, and adjoining its common neighbor
`p` gives the clique `{p} ∪ A`. Bipartiteness bounds this larger clique by
two; looplessness proves `p ∉ A`, leaving `|A| <= 1`.

The ambient theorem is directly applicable after taking `A` to be all
remaining outside attachments of a retained neighbor `p`. It therefore
certifies the necessity direction of the `U`-clean criterion. No converse is
claimed here: extending a bipartition after retaining a clean vertex also
requires choosing the relevant component flip.

## Verification

The file was elaborated from the unmodified current
`formal-conjectures` checkout at
`9a1636c4030039f70cf78b866c216d8b6c5f35b0`, using Lean 4.27.0:

```bash
timeout 60s lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture183Attachment.lean
```

Result: exit status `0`, no output. A source scan found no `sorry`, `admit`, or
`axiom`. Temporary `#print axioms` audits, removed after inspection, reported:

```text
attachment clique lemma: propext
attachment cardinality/clean lemmas: propext, Classical.choice, Quot.sound
```

These are Lean/Mathlib foundations; there are no custom axioms.

Every subprocess used for this formalization was externally capped at 60
seconds or completed well below that bound.

## Exact formal boundary

The module proves only universal local implications. It does **not** assert
any of the following unresolved statements:

1. that an admissible odd-cycle transversal `U` exists with the additional
   required attachment property;
2. that the equality tier contains a `U`-clean vertex or a compatible clean
   pair;
3. the same-component even-distance compatibility criterion;
4. the attachment conflict-graph identity `rho_x(U) = alpha(F_U)`;
5. WOWII 183 itself.

Items 3 and 4 remain mathematically justified by the component-flip argument
in Method v0.6, but were not added here because the current proof value is in
the claw-free cardinality collapse and clean necessity, while formalizing
component parity requires substantially more connectivity/distance plumbing.
Most importantly, even a future formalization of the conflict-graph identity
would still be a reduction, not the missing existence proof.

Thus the certified endpoint is exact: **every retainable attachment vertex is
clean, and at most two outside attachments can survive in a bipartite
remainder; finding the required clean vertex or parity-compatible clean pair
remains the sole paper-level existence obstruction.**
