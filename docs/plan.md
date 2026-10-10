# Replication plan & target numbers

Working notes for the Card & Krueger (1994) replication. "Target" numbers are
the values printed in the published AER paper; our job is to reproduce them
from `public.csv` and explain any differences (data coverage, sample
restrictions, standard-error choice).

## Sample construction rules

- 410 stores = 331 NJ + 79 PA. Chain codes: 1 BK, 2 KFC, 3 Roy Rogers, 4 Wendy's.
- **FTE** = full-time workers (incl. managers) + 0.5 × part-time.
  `fte = (EMPFT + NMGRS) + 0.5 * EMPPT`.
- **Full-meal price** = medium soda + small fries + entree, after tax
  (`PSODA + PFRY + PENTREE`).
- **Wave-2 FTE closure adjustment**: permanently closed (`STATUS2 == 3`) → 0;
  temporarily closed (`STATUS2 in {2,4,5}`) → missing.
- **Wage gap** `GAP = (5.05 - WAGE_ST)/WAGE_ST` for NJ stores with
  `WAGE_ST < 5.05`, else 0 (PA and NJ stores already ≥ $5.05).
- **NJ wage categories** (Table 3): low `WAGE_ST == 4.25` (N=101),
  mid `4.26–4.99` (N=140), high `≥ 5.00` (N=73).
- **Balanced sample** (Table 4): 357 stores with employment *and* starting wage
  in both waves.

## Table 2 — means by state

Key targets (NJ vs PA):
- Wave-1 FTE: NJ ≈ 20.4, PA ≈ 23.3 (NJ smaller).
- Wave-1 starting wage: NJ ≈ 4.61, PA ≈ 4.62 (very similar).
- Wave-2 starting wage: NJ ≈ 5.08 (10% rise), PA ≈ 4.62.
- Wave-2 `WAGE_ST2 == 5.05`: NJ ≈ 85%, PA ≈ 0% (the wage spike).
- Full-meal price higher in NJ in both waves.

Full set of rows and exact SEs/t-stats to be filled during implementation.

## Figure 1 — wage distributions

Two panels (Feb 1992 / Nov 1992), NJ and PA distributions of starting wage.
Expected feature: a mass point at $5.05 in the NJ "after" panel.

## Table 3 — average FTE per store

Columns: PA (i), NJ (ii), NJ−PA (iii), NJ-low (iv), NJ-mid (v), NJ-high (vi),
low−high (vii), mid−high (viii). Rows: before / after / change / balanced
change / temp-closed=0 change.

**Headline target**: NJ−PA difference-in-differences = **2.76 FTE, t = 2.03**
(row 3). Balanced-sample DID ≈ 2.82 (row 4).

## Table 4 — reduced-form models for ΔFTE

Five OLS models on the 357-store balanced sample; dep. var. mean −0.237, sd 8.825.

| Model | Regressor | Controls | Coef (se) |
|---|---|---|---|
| (i) | NJ dummy | none | 2.33 (1.19) |
| (ii) | NJ dummy | chain + ownership | 2.30 (1.20) |
| (iii) | GAP | none | 15.65 (6.08) |
| (iv) | GAP | chain + ownership | 14.92 (6.21) |
| (v) | GAP | chain + ownership + region | 11.91 (7.39) |

Report SER and joint-F p-value of controls for each column. Mean GAP among NJ
stores ≈ 0.11 (so col (iii) implies a 15.65 × 0.11 ≈ 1.72 FTE NJ−PA gain).

## Extension (chosen: A — modern inference robustness)

Does the 2.76-FTE DID result survive modern inference? Two parts:
1. **Cluster-robust SEs** for the Table 4 models (cluster by chain and region).
2. **Randomization/permutation test** of the NJ-PA diff-in-diff: shuffle NJ/PA
   assignment, recompute the DID, report the permutation p-value and plot the
   null distribution against the observed 2.76.

Motivation: Neumark & Wascher (2000) argued the paper's conventional SEs were
too small; this is the natural robustness question.

## Open items / known discrepancies (to resolve during implementation)

These are deliberate "explain the difference" items for the report, not bugs:

1. **Balanced-sample N = 351 vs paper's 357.** The straightforward filter
   (`fte1`, `fte2`, `WAGE_ST`, `WAGE_ST2` all non-missing) yields 351 stores,
   but Table 4's note says 357. Diagnosis: 8 stores have wave-1 employment and
   both wages but a missing *component* of wave-2 employment (7 `STATUS2=1`
   answered, 1 `STATUS2=2` renovation), so `fte2` is NaN. Decision needed:
   (a) report N=351 and explain, or (b) reconstruct the 357 rule (e.g. treat a
   missing employment component as 0 / use "available" components). This is a
   known data-version difference in the Card–Krueger public dataset.

2. **Share of NJ stores at $5.05 in wave 2 = 89% vs paper's ~85%.** Over
   non-missing `WAGE_ST2` we get 89.0%; the paper's Table 2 shows ~85%. Likely
   a denominator/rounding difference; verify during Table 2 implementation.

3. **Table 4 GAP coefficients ~9% higher than the paper** (our 17.05/16.36/13.88
   vs paper 15.65/14.92/11.91), while the SEs match almost exactly (6.09/6.24/
   7.44 vs 6.08/6.21/7.39) and the NJ-dummy models match closely (2.28 vs 2.30,
   2.28 vs 2.33). The GAP slope is sensitive to the exact wave-1 wage values
   used to build `GAP = (5.05 - WAGE_ST)/WAGE_ST`; the original `gap` variable
   was constructed from a slightly different wage series than this `public.csv`.
   Mean GAP among NJ matches (0.105 vs 0.11). Same economic conclusion
   (positive, no decline); document the source in the report.

## Validation & limitations (report section)

- Compare each number to the paper; quantify differences.
- Note standard-error convention (paper uses conventional OLS SEs; consider HC
  and clustered SEs as a robustness check).
- Sample-attrition: 11 wave-2 non-respondents handled per closure rules.
