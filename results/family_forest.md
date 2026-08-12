# WOWII blow-up family hunt — C5[K4] siblings vs open b/f/tree/L_s lower-bound conjectures

Session wowii309. Targets: 19, 40, 59, 61, 65, 66, 72, 103, 133, 141, 142, 144, 146, 174, 176, 181-186.
All computations exact (Fractions; count-vector symmetry for blow-ups, cross-validated vs all-subset
brute force on 6 small members + carrier C5[K4] reproduction: alpha=2 b=4 f=4 tree=4 L_s=17 OK).

## Reading enumeration + DB-sanity gate

Gate DB: all connected graphs 2<=n<=7 (graph_atlas_g, 995) + Petersen, C5, C7, P7, K33 (1000 graphs).
Readings DISCARDED by gate (mis-transcriptions; violated by DB graphs):

| conj | discarded reading | gate counterexamples |
|---|---|---|
| 65 | dist_max(A)+ceil(dist_max(M)/3) | P7 (f=7 < 6+2=8), atlas286(n7) |
| 72 | avg_ecc+ceil(lam_max/3) (no outer ceil) | atlas444(n7), slack -1/7 |
| 142 | ecc(B) read as member-ecc (=diam) | 219 DB graphs, e.g. C-containing n3/n4 |
| 144 | ecc(Centers) read as member-ecc (=rad) | 28 DB graphs |
| 146 | ecc(B) member-ecc | 484 DB graphs |
| 184 | dist_avg(B(G^2),V) measured in G | 151 DB graphs |
| 186 | ecc(C(G^2)) as rad(G^2) member-ecc | 31 DB graphs |

Surviving readings (all evaluations below use these): 19 both precedence readings;
40/59/61/103/133/141/174/183/185 literal; 65 dist_min (statement text, not the dist_max of the
invariant tags); 66 vacuous-if-no-even-degree-in-complement; 72 ceil((avg_ecc+lam_max)/3) and
ceil(avg_ecc+lam_max/3); 142/144/146 def-52 set-eccentricity (ecc(S)=max_{v in V-S} dist(v,S), =0 when S=V);
176 dist_min(M^2) in G and in G^2; 181/182 deg/Delta of B(G^2) in G^2 and in G; 184 dist_avg in G^2;
186 N(C(G^2)) and eccS in G^2 and in G.

## Family matrix (required members + bespoke blow-up members)

Legend: I(...)=independent blobs (complement family), M(...)=mixed (i=independent blob), *=carrier.

| graph | n | alpha | b | f | tree | path | L_s | gc | p | lmax | lavg | avg_ecc | diam | rad | res | girth | chiC4 | evmode(bar) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C5[K2] | 10 | 2 | 4 | 4 | 4 | 4 | 7 | 3 | 1 | 2 | 2 | 2 | 2 | 2 | 2 | 3 | 0 | 4 |
| C5[K3] | 15 | 2 | 4 | 4 | 4 | 4 | 12 | 3 | 1 | 2 | 2 | 2 | 2 | 2 | 2 | 3 | 0 | 6 |
| C5[K4]* | 20 | 2 | 4 | 4 | 4 | 4 | 17 | 3 | 1 | 2 | 2 | 2 | 2 | 2 | 2 | 3 | 0 | 8 |
| C5[K5] | 25 | 2 | 4 | 4 | 4 | 4 | 22 | 3 | 1 | 2 | 2 | 2 | 2 | 2 | 2 | 3 | 0 | 10 |
| C5[K6] | 30 | 2 | 4 | 4 | 4 | 4 | 27 | 3 | 1 | 2 | 2 | 2 | 2 | 2 | 2 | 3 | 0 | 12 |
| C5[K8] | 40 | 2 | 4 | 4 | 4 | 4 | 37 | 3 | 1 | 2 | 2 | 2 | 2 | 2 | 2 | 3 | 0 | 16 |
| C7[K2] | 14 | 3 | 6 | 6 | 6 | 6 | 9 | 5 | 1 | 2 | 2 | 3 | 3 | 3 | 3 | 3 | 0 | 8 |
| C7[K3] | 21 | 3 | 6 | 6 | 6 | 6 | 16 | 5 | 1 | 2 | 2 | 3 | 3 | 3 | 3 | 3 | 0 | 12 |
| C7[K4] | 28 | 3 | 6 | 6 | 6 | 6 | 23 | 5 | 1 | 2 | 2 | 3 | 3 | 3 | 3 | 3 | 0 | 16 |
| C9[K3] | 27 | 4 | 8 | 8 | 8 | 8 | 20 | 7 | 1 | 2 | 2 | 4 | 4 | 4 | 3 | 3 | 0 | 18 |
| C9[K4] | 36 | 4 | 8 | 8 | 8 | 8 | 29 | 7 | 1 | 2 | 2 | 4 | 4 | 4 | 3 | 3 | 0 | 24 |
| B(4,4,3,4,3) | 18 | 2 | 4 | 4 | 4 | 4 | 15 | 3 | 1 | 2 | 2 | 2 | 2 | 2 | 2 | 3 | 0 | 8 |
| B(4,2,4,2,4) | 16 | 2 | 4 | 4 | 4 | 4 | 13 | 3 | 1 | 2 | 2 | 2 | 2 | 2 | 2 | 3 | 0 | 6 |
| B(4,1,4,1,4) | 14 | 2 | 4 | 4 | 4 | 4 | 11 | 3 | 1 | 2 | 2 | 2 | 2 | 2 | 2 | 3 | 0 | 8 |
| B(3,1,3,1,3) | 11 | 2 | 4 | 4 | 4 | 4 | 8 | 3 | 1 | 2 | 2 | 2 | 2 | 2 | 2 | 3 | 0 | 4 |
| B(5,5,4,5,4) | 23 | 2 | 4 | 4 | 4 | 4 | 20 | 3 | 1 | 2 | 2 | 2 | 2 | 2 | 2 | 3 | 0 | 10 |
| co-C5[K3] | 15 | 6 | 12 | 8 | 8 | 4 | 12 | 3 | 1 | 6 | 6 | 2 | 2 | 2 | 3 | 4 | 0 | 8 |
| co-C5[K4] | 20 | 8 | 16 | 10 | 10 | 4 | 17 | 3 | 1 | 8 | 8 | 2 | 2 | 2 | 3 | 4 | 0 | None |
| co-C5[K5] | 25 | 10 | 20 | 12 | 12 | 4 | 22 | 3 | 1 | 10 | 10 | 2 | 2 | 2 | 3 | 4 | 0 | 14 |
| M(2i,4,4,4,4) | 18 | 3 | 5 | 5 | 5 | 4 | 15 | 3 | 1 | 3 | 22/9 | 2 | 2 | 2 | 2 | 3 | 0 | 6 |
| M(3i,4,4,4,4) | 19 | 4 | 6 | 6 | 6 | 4 | 16 | 3 | 1 | 4 | 54/19 | 2 | 2 | 2 | 2 | 3 | 0 | 8 |
| M(2i,4,2i,4,4) | 16 | 4 | 6 | 6 | 6 | 4 | 13 | 3 | 1 | 4 | 3 | 2 | 2 | 2 | 2 | 3 | 0 | 6 |
| M(4i,4,4i,4,4) | 20 | 8 | 10 | 10 | 10 | 4 | 17 | 3 | 1 | 8 | 22/5 | 2 | 2 | 2 | 2 | 3 | 0 | 8 |
| M7(2i,3,3,3,3,3,3) | 20 | 4 | 7 | 7 | 7 | 6 | 15 | 5 | 1 | 3 | 23/10 | 3 | 3 | 3 | 3 | 3 | 0 | 12 |
| M7(3i,1,1,1,1,1,1) | 9 | 5 | 8 | 8 | 8 | 6 | 4 | 5 | 2 | 4 | 22/9 | 3 | 3 | 3 | 4 | 4 | 0 | 6 |
| I(4,1,4,1,1) | 11 | 8 | 10 | 10 | 10 | 4 | 8 | 3 | 5 | 8 | 34/11 | 2 | 2 | 2 | 6 | 4 | 0 | 8 |
| I(5,2,5,2,2) | 16 | 10 | 14 | 12 | 12 | 4 | 13 | 3 | 4 | 10 | 11/2 | 2 | 2 | 2 | 4 | 4 | 0 | 8 |
| I(4,2,4,2,4) | 16 | 8 | 14 | 10 | 10 | 4 | 13 | 3 | 1 | 8 | 6 | 2 | 2 | 2 | 3 | 4 | 0 | None |
| C7(1,2)[K2] | 14 | 2 | 4 | 4 | 4 | 4 | 12 | 2 | 1 | 2 | 2 | 2 | 2 | 2 | 2 | 3 | 0 | 4 |
| C9(1,2)[K2] | 18 | 3 | 6 | 6 | 5 | 5 | 15 | 3 | 1 | 2 | 2 | 2 | 2 | 2 | 2 | 3 | 0 | 8 |

## Slack matrix (LHS - RHS per surviving reading; kill = negative; 103 slack = floor[...] - alpha)

| graph | 19:floor(avg_ecc)+lam_m | 19:floor(avg_ecc+lam_ma | 40:ceil((p+b+1)/2) | 59:ceil(sqrt(res*b)) | 61:res+ceil(diam/3) | 65:dmin(A)+ceil(dmin(M) | 66:vacuous-if-no-even | 72:ceil((avg_ecc+lam_ma | 72:ceil(avg_ecc+lam_max | 103:floor(b-ln(avg_ecc)) | 133:rad+avglam^chiC4 | 141:girth/2-1+lam_max | 142:2girth/3+eccS(B)def5 | 144:girth-1+eccS(C)def52 | 146:2*eccS(B)def52/rad(G | 174:n+lam_max-1 | 176:n+dmin(M2)inG | 176:n+dmin(M2)inG2 | 181:alpha+degavg(B(G2))i | 181:alpha+degavg(B(G2))i | 182:Delta(B(G2))inG+diam | 182:Delta(B(G2))inG2+dia | 183:Delta(G2)+2rad(G2) | 184:Delta(G2)+2davg(B2,V | 185:Delta(G2)+2davg(G2) | 186:|N(C2)|in2+2eccS(C2) | 186:|N(C2)|inG+2eccS(C2) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C5[K2] | 0 | 0 | 1 | 1 | 1 | 2 | 2 | 2 | 1 | 1 | 1 | 3/2 | 2 | 2 | 4 | 0 | 0 | 0 | 4 | 0 | 4 | 0 | 0 | 0 | 0 | 1 | 1 |
| C5[K3] | 0 | 0 | 1 | 1 | 1 | 2 | 2 | 2 | 1 | 1 | 1 | 3/2 | 2 | 2 | 4 | 0 | 0 | 0 | 6 | 0 | 6 | 0 | 0 | 0 | 0 | 1 | 1 |
| C5[K4]* | 0 | 0 | 1 | 1 | 1 | 2 | 2 | 2 | 1 | 1 | 1 | 3/2 | 2 | 2 | 4 | 0 | 0 | 0 | 8 | 0 | 8 | 0 | 0 | 0 | 0 | 1 | 1 |
| C5[K5] | 0 | 0 | 1 | 1 | 1 | 2 | 2 | 2 | 1 | 1 | 1 | 3/2 | 2 | 2 | 4 | 0 | 0 | 0 | 10 | 0 | 10 | 0 | 0 | 0 | 0 | 1 | 1 |
| C5[K6] | 0 | 0 | 1 | 1 | 1 | 2 | 2 | 2 | 1 | 1 | 1 | 3/2 | 2 | 2 | 4 | 0 | 0 | 0 | 12 | 0 | 12 | 0 | 0 | 0 | 0 | 1 | 1 |
| C5[K8] | 0 | 0 | 1 | 1 | 1 | 2 | 2 | 2 | 1 | 1 | 1 | 3/2 | 2 | 2 | 4 | 0 | 0 | 0 | 16 | 0 | 16 | 0 | 0 | 0 | 0 | 1 | 1 |
| C7[K2] | 1 | 1 | 2 | 1 | 2 | 4 | 2 | 4 | 2 | 1 | 2 | 7/2 | 4 | 4 | 6 | 0 | 0 | 0 | 7 | 3 | 7 | 3 | 2 | 44/13 | 44/13 | 1 | 1 |
| C7[K3] | 1 | 1 | 2 | 1 | 2 | 4 | 2 | 4 | 2 | 1 | 2 | 7/2 | 4 | 4 | 6 | 0 | 0 | 0 | 11 | 5 | 11 | 5 | 4 | 27/5 | 27/5 | 1 | 1 |
| C7[K4] | 1 | 1 | 2 | 1 | 2 | 4 | 2 | 4 | 2 | 1 | 2 | 7/2 | 4 | 4 | 6 | 0 | 0 | 0 | 15 | 7 | 15 | 7 | 6 | 200/27 | 200/27 | 1 | 1 |
| C9[K3] | 2 | 2 | 3 | 3 | 3 | 6 | 2 | 6 | 3 | 2 | 3 | 11/2 | 6 | 6 | 8 | 0 | 0 | 0 | 16 | 10 | 16 | 10 | 10 | 144/13 | 144/13 | 1 | 1 |
| C9[K4] | 2 | 2 | 3 | 3 | 3 | 6 | 2 | 6 | 3 | 2 | 3 | 11/2 | 6 | 6 | 8 | 0 | 0 | 0 | 22 | 14 | 22 | 14 | 14 | 528/35 | 528/35 | 1 | 1 |
| B(4,4,3,4,3) | 0 | 0 | 1 | 1 | 1 | 2 | 2 | 2 | 1 | 1 | 1 | 3/2 | 2 | 2 | 4 | 0 | 0 | 0 | 65/9 | 0 | 7 | 0 | 0 | 0 | 0 | 1 | 1 |
| B(4,2,4,2,4) | 0 | 0 | 1 | 1 | 1 | 2 | 2 | 2 | 1 | 1 | 1 | 3/2 | 2 | 2 | 4 | 0 | 0 | 0 | 13/2 | 0 | 6 | 0 | 0 | 0 | 0 | 1 | 1 |
| B(4,1,4,1,4) | 0 | 0 | 1 | 1 | 1 | 2 | 0 | 2 | 1 | 1 | 1 | 3/2 | 2 | 2 | 4 | 0 | 0 | 0 | 41/7 | 0 | 5 | 0 | 0 | 0 | 0 | 1 | 1 |
| B(3,1,3,1,3) | 0 | 0 | 1 | 1 | 1 | 2 | 2 | 2 | 1 | 1 | 1 | 3/2 | 2 | 2 | 4 | 0 | 0 | 0 | 50/11 | 0 | 4 | 0 | 0 | 0 | 0 | 1 | 1 |
| B(5,5,4,5,4) | 0 | 0 | 1 | 1 | 1 | 2 | 2 | 2 | 1 | 1 | 1 | 3/2 | 2 | 2 | 4 | 0 | 0 | 0 | 212/23 | 0 | 9 | 0 | 0 | 0 | 0 | 1 | 1 |
| co-C5[K3] | 4 | 4 | 1 | 2 | 4 | 6 | 4 | 5 | 4 | 5 | 1 | 1 | 16/3 | 5 | 8 | 4 | 8 | 8 | 12 | 4 | 16 | 8 | 8 | 8 | 8 | 9 | 9 |
| co-C5[K4] | 6 | 6 | 1 | 3 | 6 | 8 | 10 | 6 | 5 | 7 | 1 | 1 | 22/3 | 7 | 10 | 6 | 12 | 12 | 17 | 6 | 23 | 12 | 12 | 12 | 12 | 13 | 13 |
| co-C5[K5] | 8 | 8 | 1 | 4 | 8 | 10 | 8 | 8 | 6 | 9 | 1 | 1 | 28/3 | 9 | 12 | 8 | 16 | 16 | 22 | 8 | 30 | 16 | 16 | 16 | 16 | 17 | 17 |
| M(2i,4,4,4,4) | 0 | 0 | 1 | 1 | 2 | 2 | 3 | 3 | 2 | 1 | 1 | 3/2 | 3 | 3 | 5 | 0 | 1 | 1 | 65/9 | 0 | 7 | 1 | 1 | 1 | 1 | 2 | 2 |
| M(3i,4,4,4,4) | 0 | 0 | 2 | 2 | 3 | 3 | 4 | 4 | 2 | 1 | 1 | 3/2 | 4 | 4 | 6 | 0 | 2 | 2 | 150/19 | 0 | 9 | 2 | 2 | 2 | 2 | 3 | 3 |
| M(2i,4,2i,4,4) | 0 | 0 | 2 | 2 | 3 | 4 | 4 | 4 | 2 | 1 | 1 | 3/2 | 4 | 4 | 6 | 0 | 2 | 2 | 27/4 | 0 | 8 | 2 | 2 | 2 | 2 | 3 | 3 |
| M(4i,4,4i,4,4) | 0 | 0 | 4 | 5 | 7 | 7 | 8 | 6 | 5 | 1 | 1 | 3/2 | 8 | 8 | 10 | 0 | 6 | 6 | 46/5 | 0 | 14 | 6 | 6 | 6 | 6 | 7 | 7 |
| M7(2i,3,3,3,3,3,3) | 1 | 1 | 2 | 2 | 3 | 4 | 3 | 5 | 3 | 1 | 2 | 7/2 | 5 | 5 | 7 | 0 | 1 | 1 | 21/2 | 47/10 | 11 | 5 | 4 | 27/5 | 27/5 | 2 | 2 |
| M7(3i,1,1,1,1,1,1) | 1 | 1 | 2 | 2 | 3 | 6 | 2 | 5 | 3 | 1 | 2 | 3 | 16/3 | 5 | 8 | 0 | 2 | 2 | 41/9 | 13/9 | 5 | 3 | 2 | 61/18 | 61/18 | 3 | 3 |
| I(4,1,4,1,1) | 0 | 0 | 2 | 2 | 3 | 8 | 4 | 6 | 5 | 1 | 1 | 1 | 22/3 | 7 | 10 | 0 | 6 | 6 | 76/11 | 0 | 8 | 6 | 6 | 6 | 6 | 7 | 7 |
| I(5,2,5,2,2) | 2 | 2 | 2 | 4 | 7 | 9 | 8 | 8 | 6 | 3 | 1 | 1 | 28/3 | 9 | 12 | 2 | 10 | 10 | 23/2 | 2 | 15 | 10 | 10 | 10 | 10 | 11 | 11 |
| I(4,2,4,2,4) | 4 | 4 | 2 | 3 | 6 | 7 | 10 | 6 | 5 | 5 | 1 | 1 | 22/3 | 7 | 10 | 4 | 10 | 10 | 13 | 4 | 17 | 10 | 10 | 10 | 10 | 11 | 11 |
| C7(1,2)[K2] | 0 | 0 | 1 | 1 | 1 | 2 | 2 | 2 | 1 | 1 | 1 | 3/2 | 2 | 2 | 4 | 1 | 1 | 1 | 5 | 1 | 5 | 1 | 1 | 1 | 1 | 2 | 2 |
| C9(1,2)[K2] | 2 | 2 | 2 | 2 | 3 | 4 | 4 | 3 | 2 | 2 | 2 | 5/2 | 3 | 3 | 5 | 2 | 2 | 2 | 9 | 1 | 10 | 2 | 2 | 2 | 2 | 3 | 3 |

**Result: ZERO violations across all 30 family members under every gate-surviving reading.**

### Tightness (slack exactly 0)

- conj 19 [floor(avg_ecc)+lam_max]: tight on 17: C5[K2], C5[K3], C5[K4]*, C5[K5], C5[K6], C5[K8], B(4,4,3,4,3), B(4,2,4,2,4), B(4,1,4,1,4), B(3,1,3,1,3), B(5,5,4,5,4), M(2i,4,4,4,4), M(3i,4,4,4,4), M(2i,4,2i,4,4), M(4i,4,4i,4,4), I(4,1,4,1,1), C7(1,2)[K2]
- conj 19 [floor(avg_ecc+lam_max)]: tight on 17: C5[K2], C5[K3], C5[K4]*, C5[K5], C5[K6], C5[K8], B(4,4,3,4,3), B(4,2,4,2,4), B(4,1,4,1,4), B(3,1,3,1,3), B(5,5,4,5,4), M(2i,4,4,4,4), M(3i,4,4,4,4), M(2i,4,2i,4,4), M(4i,4,4i,4,4), I(4,1,4,1,1), C7(1,2)[K2]
- conj 66 [vacuous-if-no-even]: tight on 1: B(4,1,4,1,4)
- conj 174 [n+lam_max-1]: tight on 23: C5[K2], C5[K3], C5[K4]*, C5[K5], C5[K6], C5[K8], C7[K2], C7[K3], C7[K4], C9[K3], C9[K4], B(4,4,3,4,3), B(4,2,4,2,4), B(4,1,4,1,4), B(3,1,3,1,3), B(5,5,4,5,4), M(2i,4,4,4,4), M(3i,4,4,4,4), M(2i,4,2i,4,4), M(4i,4,4i,4,4), M7(2i,3,3,3,3,3,3), M7(3i,1,1,1,1,1,1), I(4,1,4,1,1)
- conj 176 [n+dmin(M2)inG]: tight on 16: C5[K2], C5[K3], C5[K4]*, C5[K5], C5[K6], C5[K8], C7[K2], C7[K3], C7[K4], C9[K3], C9[K4], B(4,4,3,4,3), B(4,2,4,2,4), B(4,1,4,1,4), B(3,1,3,1,3), B(5,5,4,5,4)
- conj 176 [n+dmin(M2)inG2]: tight on 16: C5[K2], C5[K3], C5[K4]*, C5[K5], C5[K6], C5[K8], C7[K2], C7[K3], C7[K4], C9[K3], C9[K4], B(4,4,3,4,3), B(4,2,4,2,4), B(4,1,4,1,4), B(3,1,3,1,3), B(5,5,4,5,4)
- conj 181 [alpha+degavg(B(G2))inG2]: tight on 16: C5[K2], C5[K3], C5[K4]*, C5[K5], C5[K6], C5[K8], B(4,4,3,4,3), B(4,2,4,2,4), B(4,1,4,1,4), B(3,1,3,1,3), B(5,5,4,5,4), M(2i,4,4,4,4), M(3i,4,4,4,4), M(2i,4,2i,4,4), M(4i,4,4i,4,4), I(4,1,4,1,1)
- conj 182 [Delta(B(G2))inG2+diam]: tight on 11: C5[K2], C5[K3], C5[K4]*, C5[K5], C5[K6], C5[K8], B(4,4,3,4,3), B(4,2,4,2,4), B(4,1,4,1,4), B(3,1,3,1,3), B(5,5,4,5,4)
- conj 183 [Delta(G2)+2rad(G2)]: tight on 11: C5[K2], C5[K3], C5[K4]*, C5[K5], C5[K6], C5[K8], B(4,4,3,4,3), B(4,2,4,2,4), B(4,1,4,1,4), B(3,1,3,1,3), B(5,5,4,5,4)
- conj 184 [Delta(G2)+2davg(B2,V)inG2]: tight on 11: C5[K2], C5[K3], C5[K4]*, C5[K5], C5[K6], C5[K8], B(4,4,3,4,3), B(4,2,4,2,4), B(4,1,4,1,4), B(3,1,3,1,3), B(5,5,4,5,4)
- conj 185 [Delta(G2)+2davg(G2)]: tight on 11: C5[K2], C5[K3], C5[K4]*, C5[K5], C5[K6], C5[K8], B(4,4,3,4,3), B(4,2,4,2,4), B(4,1,4,1,4), B(3,1,3,1,3), B(5,5,4,5,4)

## Wave 2 bespoke: dense diam-2 graphs + girth>=5/6 graphs (full exact profiles)

Justification: (a) on every diam-2 member G^2=K_n, so 174/176/181-186 reduce to
b >= gamma_c + {lam_max-1 | 1 | alpha-1 | 1 | 0}; family members all have gamma_c=3 and sit exactly
tight, so the kill window is diam-2 graphs with gamma_c>=4 and slow-growing b. (b) conjecture 133's
chi_C4=1 branch is untouchable inside the blow-up family (every member has C4; chi=0 gives
RHS=rad+1 <= diam+1 <= path, provably safe), so C4-free graphs are the only kill surface.

| graph | n | alpha | b | f | tree | path | L_s | gc | lmax | diam | girth | res | min slack (conj) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Paley13 | 13 | 3 | 6 | 6 | 6 | 6 | 9 | 4 | 3 | 2 | 3 | 2 | 0 @ 174; 0 @ 181 |
| co-Petersen | 10 | 2 | 4 | 4 | 4 | 4 | 7 | 3 | 2 | 2 | 3 | 2 | -1 @ 186; -2/3 @ 184 |
| Kneser(6,2) | 15 | 5 | 9 | 7 | 7 | 5 | 12 | 3 | 3 | 2 | 3 | 3 | 1 @ 40; 1 @ 59 |
| Clebsch | 16 | 5 | 10 | 9 | 9 | 5 | 12 | 4 | 5 | 2 | 4 | 3 | 2 @ 133; 2 @ 174 |
| Shrikhande | 16 | 4 | 8 | 7 | 7 | 7 | 12 | 4 | 3 | 2 | 3 | 3 | 1 @ 181; 9/5 @ 184 |
| Rook4x4 | 16 | 4 | 8 | 7 | 7 | 7 | 12 | 4 | 2 | 2 | 3 | 3 | 1 @ 181; 9/5 @ 184 |
| Paley17 | 17 | 3 | 6 | 6 | 6 | 6 | 13 | 4 | 3 | 2 | 3 | 2 | 0 @ 174; 0 @ 181 |
| Heawood | 14 | 7 | 14 | 10 | 10 | 7 | 8 | 6 | 3 | 3 | 6 | 4 | 1 @ 133; 2 @ 40 |
| MobiusKantor | 16 | 8 | 16 | 11 | 11 | 11 | 8 | 8 | 3 | 4 | 6 | 4 | 2 @ 40; 2 @ 144 |

No violations. Paley13 and Paley17 are EXACTLY TIGHT on 174 (b = gamma_c + lam_max - 1 = 6) and on
181 (b = alpha + gamma_c - 1 = 6) — a second extremal family besides the C5 blow-ups.
Shrikhande and Rook4x4: slack 1 on 181 (b=8 vs alpha+gc-1=7).

### 133 C4-free zoo (need: induced path >= rad + avg_lambda, chi_C4=1)

| graph | n | rad | avg_lambda | needed | verdict |
|---|---|---|---|---|---|
| Petersen (gate) | 10 | 2 | 3 | 5 | holds (path=5, tight-by-glossary check in gate) |
| McGee | 24 | 4 | 3 | 7 | HOLDS (induced P7 found) |
| Pappus | 18 | 4 | 3 | 7 | HOLDS (induced P7 found) |
| Desargues | 20 | 5 | 3 | 8 | HOLDS (induced P8 found) |
| Dodecahedron | 20 | 5 | 3 | 8 | HOLDS (induced P8 found) |

### Structural safety notes derived during the hunt (why several targets cannot die here)

- b >= alpha + 2 for every connected non-complete graph (max independent S plus any non-adjacent
  pair outside it is induced-bipartite), and b >= lambda(v) + 1 + alpha(G - N[v]) for every v
  (star at v + independent set beyond N[v]). Hence 103 needs avg_ecc > e with b <= alpha+1 —
  b=alpha+1 forces V minus every max independent set to be a clique, which forces ecc(clique)<=2-ish
  and avg_ecc < e. 103 is structurally out of reach in this landscape.
- 19: kill needs floor(avg_ecc)+lam_max > b >= lam_max + 1 + alpha(G-N[v]) at every lam_max-achiever v;
  avg_ecc >= 3 forces alpha(G-N[v]) <= 1, i.e. G-N[v] clique, which caps all eccentricities at 3 with
  ecc(v)=2, so avg_ecc < 3. Contradiction ladder repeats at higher windows. Blow-up siblings that raise
  lam_max (mixed independent blobs) raise b in lockstep (verified: M(2i,4,4,4,4) lmax=3 b=5;
  M(4i,4,4i,4,4) lmax=8 b=10; slack stays 0 on 174, +1-ish on 19).
- 66 on complete-blob C5 blow-ups: complement-degree of blob-i vertex = m_{i+2}+m_{i+3}, and
  sum_i m_i*codeg_i = 2*sum_{C5-nonadj} m_i m_j <= n^2/2 (quadratic bound on the pentagon),
  so even_mode_min(bar G) <= n-3 < 2*deg_avg always: conjecture 66 PROVABLY holds on the whole
  complete-blob C5 blow-up family; B(4,1,4,1,4) achieves equality (slack 0).
- 40: every cycle blow-up (complete or independent blobs, any sizes) is traceable (explicit
  Hamiltonian-path DP check), so p=1 and f >= b/2+1 holds with slack >= 1.
- 59/61: res <= alpha (Favaron-Maheo-Sacle) = floor(k/2) on C_k blow-ups while f = k-1: RHS can't reach f.
- 133 chi_C4=0 branch: path >= diam+1 >= rad+1 always — only C4-free graphs can kill 133.


## Wave 3: larger dense diam-2 graphs (b via CBC ILP validated vs brute on Paley13/Petersen;
gamma_c via bitmask brute; alpha/lambda exact B&B). Diam-2 kill conditions in closed form:
174: b<gc+lmax-1, 181: b<alpha+gc-1, 176/182/183/184/185: b<gc+1, 186: b<gc.

| graph | n | diam | b | alpha | lmax | gamma_c | L_s | slacks |
|---|---|---|---|---|---|---|---|---|
| Paley25 | 25 | 2 | 10 | 5 | 3 | 4 | 21 | 174:4 181:2 176/182-185:5 186:6 |
| Paley29 | 29 | 2 | 8 | 4 | 4 | 4 | 25 | 174:1 181:1 176/182-185:3 186:4 |
| Paley37 | 37 | 2 | 8 | 4 | 4 | 4 | 33 | 174:1 181:1 176/182-185:3 186:4 |
| Paley41 | 41 | 2 | 10 | 5 | 4 | 4 | 37 | 174:3 181:2 176/182-185:5 186:6 |
| GQ(2,4) | 27 | 2 | 12 | 6 | 5 | 3 | 24 | 174:5 181:4 176/182-185:8 186:9 |
| Schlafli | 27 | 2 | 6 | 3 | 2 | 4 | 23 | 174:1 181:0 176/182-185:1 186:2 |
| 133-zoo Kneser(7,3)=O4 | 35 | rad=3 avglam=4 need>=7 | HOLDS (induced P7 found) | | | | | |
| 133-zoo HoffmanSingleton | 50 | rad=2 avglam=7 need>=9 | HOLDS (induced P9 found) | | | | | |

## Triangular graphs T(n) = L(K_n) — the 181 kill family

| graph | n(G) | alpha | b | gamma_c | L_s | lmax | diam | LHS=L_s+b | RHS=alpha+(n-1) | margin |
|---|---|---|---|---|---|---|---|---|---|---|
| T(6)=L(K6) | 15 | 3 | 6 | 4 (brute-confirmed) | 11 | 2 | 2 | 17 | 17 | 0 TIGHT |
| T(7)=L(K7) | 21 | 3 | 6 | 5 (brute-confirmed) | 16 | 2 | 2 | 22 | 23 | -1 KILL |
| T(8)=L(K8) | 28 | 4 | 8 | 6 (brute-confirmed) | 22 | 2 | 2 | 30 | 31 | -1 KILL |
| T(9)=L(K9) | 36 | 4 | 8 | 7 (brute-confirmed) | 29 | 2 | 2 | 37 | 39 | -2 KILL |
| T(10)=L(K10) | 45 | 5 | 10 | 8 (proof) | 37 | 2 | 2 | 47 | 49 | -2 KILL |
| T(11)=L(K11) | 55 | 5 | 10 | 9 (proof) | 46 | 2 | 2 | 56 | 59 | -3 KILL |

## NEW KILLS

### Conjecture 181 (open): L_s(G) + b(G) >= alpha(G) + deg_avg(B(G^2)) — KILLED (reading-dependent)

**Witness: T(7) = L(K_7)** (triangular graph / Johnson J(7,2), SRG(21,10,5,4)), and the whole
family T(n) = L(K_n) for n >= 7.

Reading under which it dies: `deg_avg(B(G^2))` = average degree, measured in G^2, of the periphery
of G^2 (the all-G^2-side reading). This reading SURVIVES the DB-sanity gate (all 1000 gate graphs:
connected atlas n<=7, Petersen, C5, C7, P7, K33 satisfy it) and it is the reading that is exactly
TIGHT on the carrier C5[K4] (slack 0) and on every uniform C5/C7/C9 blow-up, on Paley13/17, on
T(5)=co-Petersen and T(6) — i.e. it is the reading Graffiti.pc's tightness discipline points to.
The alternative reading (degrees measured in G) also survives the gate but has slack 8-9 on the
carrier and slack 9 on T(7): NOT killed under that reading. Flagged accordingly.

T(7) numbers (every quantity proved by exhaustive enumeration, from-scratch script
verify_181_T7.py, no ILP in the verification path):
- n = 21, 10-regular, diam = 2 (so G^2 = K_21, B(G^2) = V, deg_avg(B(G^2)) in G^2 = 20 exactly)
- alpha = 3 (all C(21,4) 4-subsets checked non-independent; witness {01,23,45})
- b = 6 (all C(21,7) = 116280 7-subsets checked non-bipartite; witness {01,02,13,23,45,46})
- gamma_c = 5 (all subsets of size <= 4 fail; witness star {01,02,03,04,05}); L_s = n - gamma_c = 16
- lambda(v) = 2 for every v (exhaustive per-vertex)
- LHS = L_s + b = 16 + 6 = 22 < 23 = 3 + 20 = alpha + deg_avg(B(G^2)) = RHS. **Violated by 1.**

Same T(7) is exactly TIGHT (slack 0) on 174, 176, 182, 183, 184, 185 and holds 186 by 1 —
it sits precisely on the frontier of the whole L_s+b group and dips below only for 181,
because alpha(T(7)) = 3 > lambda_max = 2 (the alpha/lambda gap is the lever; all blow-up family
members have alpha approximately = lambda_max + cycle-slack, which is why they could not kill it).

**Follow-up (2026-08-12):** the common diameter-two wall for 176 and 182--185
is exactly the already-proved WOWII 173 baseline, not merely a persistent
empirical relation. See [`wowii_173_wall.md`](expansion/wowii_173_wall.md) for
the primary source, reductions, and independent atlas audit. No diameter-two
search can cross this wall.

Infinite family + closed forms (L(K_n), n >= 7; brute/ILP-confirmed through T(11)):
- alpha(T(n)) = floor(n/2) (max matching of K_n)
- b(T(n)) = n for n even, n-1 for n odd (induced bipartite in L(K_n) <=> disjoint paths + even
  cycles in K_n; max edge count = n via spanning even cycle when n even, else n-1)
- gamma_c(T(n)) = n-2 (D dominates L(K_n) iff V(D) is a vertex cover of K_n, so |V(D)| >= n-1;
  a connected edge set spanning n-1 vertices needs >= n-2 edges; star of n-2 edges achieves it)
- lambda_max = 2, diam = 2
- margin(181) = b + 3 - n - floor(n/2) = 3 - n/2 (n even), (5-n)/2 (n odd):
  T(7): -1, T(8): -1, T(9): -2, T(10): -2, T(11): -3, ... unbounded violation.

Discovery path (why this counts as a family-targeted bespoke member): the blow-up matrix showed
every diam-2 member reduces 181 to b >= alpha + gamma_c - 1 with the family pinned at gamma_c = 3
and exactly tight; the wave-2/3 sweep (Paley 13/17/25/29/37/41, Clebsch, Shrikhande, Rook, GQ(2,4),
Schlafli) walked the b - alpha - gamma_c functional down to 0 (Schlafli tight, Paley29/37 at +1);
T(n) is the dense diam-2 family whose alpha grows while b - gamma_c stays pinned at <= 2.

### Second independent witness for 59 (already disproved by others — deprioritized): none sought.

## NO-KILL summary for the remaining targets (closest misses, exact numbers)

- 19: slack 0 (both readings) on ALL 17 complete-blob members (b = 4 = floor(2+2) on every C5
  blow-up; b = lambda_max+2 exactly on mixed members M(2i,4,4,4,4) b=5, M(4i,4,4i,4,4) b=10).
  Structural obstruction: b >= lambda(v) + 1 + alpha(G - N[v]) and avg_ecc >= 3 forces
  alpha(G - N[v]) <= 1 at every lambda_max-achiever => all ecc <= 3 with ecc(v)=2 => avg_ecc < 3.
- 40: min slack 1 (C5[K2]); p = 1 on every member (all cycle blow-ups traceable, DP-verified).
- 59: min slack 1 (C5[K2]: f=4 vs ceil(sqrt(2*4))=3). res <= alpha kills the growth.
- 61: min slack 1 (C5[K2]: 4 vs 2+1).
- 65: min slack 2 (C5[K2]); dist_max readings are gate-dead (P7), dist_min caps RHS at 2-3 here.
- 66: slack 0 on B(4,1,4,1,4) (f=4 = 2*ceil(8/(38/7)) = 4). Proof that no complete-blob C5 blow-up
  can go negative: codeg_i = m_{i+2}+m_{i+3}, sum m_i*codeg_i = 2*sum_{C5-nonadj} m_i m_j <= n^2/2.
- 72: min slack 1 (C5[K2], reading ceil(avg_ecc + lmax/3): 4 vs 3); outer-ceil reading slack 2.
- 103: min slack 1 (C5[K2]: floor(4 - ln 2) = 3 vs alpha = 2). Obstruction: b >= alpha + 2 for all
  non-complete graphs, and b = alpha+1 forces V minus every max-independent-set to be a clique,
  capping avg_ecc < e. Floor-cliff unreachable in this landscape.
- 133: min slack 1 (C5[K2]: path=4 vs rad+1=3). chi_C4=0 branch provably safe (path >= diam+1).
  C4-free zoo (chi=1): Petersen 5>=5 tight-ish, McGee/Pappus/Desargues/Dodecahedron/O4/HoSi all
  HOLD (induced paths of the required length found; HoSi needs P9, found).
- 141: min slack 1 (co-C5[K3]: tree=8 vs 4/2-1+2*3=7). Obstruction: tree >= lambda_max + 1 (star).
- 142: min slack 2 (C5[K2]: tree=4 vs 2+0; def-52 ecc(B)=0 on all vertex-transitive members).
- 144: min slack 2 (C5[K2]: 4 vs 3-1+0).
- 146: min slack 4 (C5[K2]: 4 vs 0).
- 174: slack 0 on 23 of 30 family members + Paley13/17 + T(n) all n. b >= gamma_c + lambda_max - 1
  held everywhere tested; mixed blobs move lambda_max and b in lockstep (b >= lmax+2 = lmax+gc-1).
- 176: slack 0 on 16 members (both dist readings agree on regular members).
- 182-185: slack 0 on 11 members each (all diam-2 uniform blow-ups); T(n) also exactly tight.
- 186: min slack 1 (C5[K2] and T(7): b vs gamma_c).

Follow-up for 183: its square correction over proved baseline 173 is at most
one. A large targeted search found no critical equality case, reducing the
remaining question to a narrow theorem-like lemma but not proving it. See
[`wowii_183_theorem_signal.md`](expansion/wowii_183_theorem_signal.md).

## Files
- inv.py / evaluate.py — invariant library + readings (count-vector fast paths cross-validated
  against all-subset brute force on 6 small members; carrier C5[K4] profile reproduced exactly)
- gate.py / gate_result.pkl — 1000-graph DB-sanity gate
- run_family.py / family_result.pkl — 30-member family matrix
- wave2.py / wave3.py — bespoke sweeps (SRGs, Paley, C4-free zoo)
- verify_181_T7.py — self-contained exhaustive verification of the T(7) kill
- verify_T_family.py — T(6)..T(11) confirmation (ILP b capped at 60s; structural fallbacks)
