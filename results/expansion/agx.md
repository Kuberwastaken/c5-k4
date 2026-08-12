# AutoGraphiX open-conjecture expansion sweep

## Methodology and progress

- **Coverage target:** all 70 entries in `corpora/autographix.json` whose status begins `open`, plus `agx-survey-C23`, whose full form is marked open although a weaker form was proved. Each entry receives its own durable verdict below.
- **Arsenal:** `C5[K_m]` for `m = 2,3,4,5,6,8`; `C7[K3]`; `C9[K3]`; `T(7)`, `T(8)`, `T(9)`; `comp(C5[K4])`; Petersen; and Paley(13), Paley(17), Paley(29) when its invariants are cheap. Spectra use direct symmetric eigensolvers with a `1e-6` comparison guard, and the closed form for `C5[K_m]` is used as an independent check.
- **Exactness:** combinatorial and distance averages are retained as integers or `Fraction`s. A spectral gap of magnitude at most `1e-6` is a tie, never a disproof.
- **Candidate gate:** every apparent violation is re-evaluated under every plausible reading on all connected Graph Atlas graphs of order at most 7 and the named calibration set (`C5`--`C9`, `P7`, Petersen, `K3,3`, `K7`, stars, and complete bipartite graphs). A reading already false there is classified as transcription/database corruption rather than a new kill. Any gate survivor is recomputed by a separate code path and novelty-checked against the literature, including Wagner and Vito--Stefanus.
- **OCR discipline:** an expression that cannot be recovered faithfully from the corpus is recorded as `SKIP_OCR` with the surviving garble quoted; no intended formula is guessed.
- **ILP discipline:** no solver call may exceed 60 seconds. (This lane currently needs no ILP.)

Progress: **0/71** entries evaluated (70 strict-open + 1 open-in-full).

