# Catalogue arm — experiment v2

Ran 3001 s; frozen catalogue scripts/exp/catalogue.py (68 graphs, unchanged from v1);
values via certify2.py (frozen backends own paths, 60 s per-invariant caps).

| verdict | n |
|---|---|
| CROSSED | 9 |
| HELD | 7 |
| BRACKET | 14 |

## CROSSED (each re-verified on backend A independently)

| target | witness | slack | backend-A agrees |
|---|---|---|---|
| FP2-010 | comp(C5[K3]) | -1 | True |
| FP2-014 | C5[K3] | -2 | True |
| FP2-017 | MobiusKantor | -1 | True |
| FP2-019 | comp(doublestar(12,12)) | -1 | True |
| FP2-020 | comp(prism(C6)) | -1 | True |
| FP2-021 | C5[K4] | -2 | True |
| FP2-023 | Paley(17) | -1 | True |
| FP2-028 | C5[K2] | -1 | True |
| FP2-029 | comp(C5[K5]) | -1 | True |

## BRACKET pairs

- **FP2-001**: comp(C9[K3]):disp_max, T(8):disp_max, comp(T(8)):disp_max, Paley(29):disp_max, comp(Paley(29)):disp_max, C5[K6]:disp_max ...(9 total)
- **FP2-002**: comp(C9[K3]):disp_min, T(8):disp_min, comp(T(8)):disp_min, Paley(29):disp_min, comp(Paley(29)):disp_min, C5[K6]:disp_min ...(9 total)
- **FP2-005**: comp(Paley(29)):b, T(9):b
- **FP2-006**: comp(C9[K3]):cutv, T(8):cutv, comp(T(8)):cutv, Paley(29):cutv, comp(Paley(29)):b, comp(Paley(29)):cutv ...(11 total)
- **FP2-007**: comp(Paley(29)):b, T(9):b
- **FP2-008**: C5[K5]:chi, comp(Paley(29)):f, C5[K6]:chi, T(9):chi, T(9):f, comp(T(9)):f
- **FP2-009**: C5[K5]:chi, C5[K6]:chi, T(9):chi
- **FP2-011**: comp(Paley(29)):f, T(9):f, comp(T(9)):f
- **FP2-012**: comp(Paley(29)):f, T(9):f, comp(T(9)):f
- **FP2-013**: comp(C9[K3]):cutv, T(8):cutv, comp(T(8)):cutv, Paley(29):cutv, comp(Paley(29)):f, comp(Paley(29)):cutv ...(12 total)
- **FP2-024**: comp(Paley(29)):b, T(9):b
- **FP2-026**: comp(C9[K3]):disp_min, T(8):disp_min, comp(T(8)):disp_min, Paley(29):disp_min, comp(Paley(29)):disp_min, C5[K6]:disp_min ...(9 total)
- **FP2-027**: comp(Paley(29)):f, T(9):f, comp(T(9)):f
- **FP2-030**: comp(C9[K3]):disp_max, T(8):disp_max, comp(T(8)):disp_max, Paley(29):disp_max, comp(Paley(29)):disp_max, C5[K6]:disp_max ...(9 total)
