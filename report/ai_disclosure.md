# AI-Use Disclosure



## 1. Where and how AI was used

- [x] **Framing / understanding the paper and design** — an AI assistant helped
  unpack the DID design, the FTE definition, the closure-adjustment rule, and the
  identification strategy, and drafted `docs/plan.md` with the target numbers
  from the published tables.
- [x] **Data cleaning and variable construction** — the assistant wrote
  `src/config.py` and `src/common.py` (FTE, wage gap, meal price, dummies,
  closure adjustment) and `src/build_sample.py`.
- [x] **Writing analysis code** — the assistant drafted `src/table2.py`,
  `src/table3.py`, `src/table4.py`, `src/figure1.py`, and `src/extension.py`, plus
  the `src/run_all.py` orchestrator.
- [x] **Generating figures/tables** — the assistant produced the Table 2–4 CSVs,
  Figure 1, and the permutation-distribution figure, choosing a colorblind-safe
  two-color palette.
- [x] **Drafting / editing the report** — the assistant drafted `report/report.md`
  from the replication numbers and the extension results; I reviewed and edited it.
- [x] **Debugging / interpreting results** — the assistant diagnosed several
  mismatches against the paper (see Section 3) and the `statsmodels` import issue
  on Windows.

## 2. How AI-generated code, analysis, and writing were checked

- [x] Ran every script (`python src/run_all.py`) and inspected each output
  against the published Table 2–4 and Figure 1 values.
- [x] Verified variable definitions against `01_DID/DATA_DICTIONARY.md` and the
  paper's table notes (e.g. FTE = (EMPFT + NMGRS) + 0.5·EMPPT).
- [x] Manually recomputed key numbers — the 2.75 DID, the 85.5% NJ share at
  $5.05, and the Table 4 coefficients — from the processed sample.
- [x] Cross-checked standard errors and t-statistics against the paper (the
  balanced-sample t = 2.05 vs. the paper's 2.03).

## 3. Important AI errors or suggestions that I corrected or rejected

- **"% full-time employees" mis-specified.** The assistant initially defined the
  Table 2 variable as (EMPFT + NMGRS)/(EMPFT + NMGRS + EMPPT), which produced
  37.7% for NJ against the paper's 32.8. I identified the mismatch and corrected
  the definition to EMPFT/FTE, which reproduces the paper's value (32.85).
- **Standard-error convention.** The assistant first reported the unpaired DID
  standard error (t ≈ 1.53), but the paper's headline t = 2.03 requires the
  *paired/balanced-sample* standard error (t = 2.05). I confirmed the convention
  from the paper's table notes and fixed `src/table3.py` to report both.
- **Wrong sample in the extension's cluster-robust SEs.** The assistant first ran
  the cluster-robust regressions on the employment-balanced sample (N = 384),
  which produced `GAP` coefficients that did not match Table 4. I corrected it to
  use Table 4's exact balanced sample (employment + both wages, N = 351), after
  which the coefficients (17.05/16.36/13.88) matched Table 4 exactly.
- **$5.05 share denominator.** The assistant reported two different "share at
  $5.05" figures (89% over wage-reporting stores vs. 85.5% over all NJ stores).
  I clarified that the paper's ~85% corresponds to the all-stores denominator and
  documented both in the report.
- **Rejected suggestion to drop missing wave-2 employment.** The assistant
  initially considered dropping stores with missing wave-2 employment; I rejected
  this because the paper's closure adjustment sets permanently-closed stores to
  zero and temporarily-closed stores to missing.
