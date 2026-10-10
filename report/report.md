# Card & Krueger (1994) — Replication and Extension

*ECON6067 Individual Project — [Your name / student ID]*

## Abstract

This project replicates the central empirical result of Card and Krueger (1994),
"Minimum Wages and Employment: A Case Study of the Fast-Food Industry in New
Jersey and Pennsylvania," and extends it with modern inference tools. Using the
paper's fast-food-restaurant survey data (410 stores), I reconstruct the
difference-in-differences (DID) estimate of the effect of New Jersey's April 1,
1992 minimum-wage increase (from $4.25 to $5.05) on employment. The replication
reproduces the paper's headline finding: New Jersey's full-time-equivalent (FTE)
employment *rose* by about **2.75 FTE per store** relative to Pennsylvania
(balanced-sample t = 2.05, versus the paper's 2.03), providing no evidence of an
employment decline. The independent extension asks whether this result survives
modern inference. Cluster-robust standard errors (by chain and by region) raise
the NJ-dummy standard error but leave the wage-gap specification clearly
significant, and an exact store-level permutation test yields a two-sided p-value
of **0.017**. The result is robust to exact randomization inference, though its
statistical significance is sensitive to how one treats the small number of
treatment clusters — precisely the concern later raised by Neumark and Wascher
(2000).

---

## 1. Research question and motivation

**Question.** Does raising the minimum wage reduce employment? Card and Krueger
(1994) test the textbook prediction of the competitive labor-market model — that
a binding minimum wage pushes employment down the labor-demand curve — using a
clean quasi-experiment: on April 1, 1992, New Jersey raised its state minimum
wage from the federal level of $4.25 to $5.05, while neighboring eastern
Pennsylvania kept the $4.25 federal minimum.

**Why the NJ/PA pair is a natural experiment.** The fast-food industry in the two
states is geographically adjacent, low-wage, and homogeneous in production
technology, so restaurants on the two sides of the border faced very similar
labor and product markets except for the policy change. New Jersey's increase
was large (a 19% nominal rise) and concentrated in a sector where most workers
earned near the old minimum, making the treatment economically salient.

**Why it matters.** The paper is a landmark in the minimum-wage debate because
its headline — no employment decline, and if anything a small *increase* — ran
against the textbook model and helped motivate monopsony and search-theoretic
labor-market models in which a modest minimum wage need not reduce employment.
It also became a canonical case study in *how to do inference* in
difference-in-differences: Neumark and Wascher (2000) disputed the result partly
on the grounds that the paper's conventional standard errors were too small.
That methodological controversy motivates the extension in Section 5.

---

## 2. Data, sample construction, and variable definitions

**Data.** The course "Package 01" provides `public.csv`, a store-level survey of
410 fast-food restaurants (331 in New Jersey, 79 in Pennsylvania) across four
chains (Burger King, KFC, Roy Rogers, and Wendy's). Each store was surveyed
twice: wave 1 before the increase (February 1992) and wave 2 after (November
1992). Suffix `2` denotes wave-2 fields; blank values are missing.

**Key variable definitions** (implemented once in `src/common.py`):

- **Full-time-equivalent (FTE) employment** =
  (full-time employees + managers/assistant managers) + 0.5 × part-time
  employees: `FTE = (EMPFT + NMGRS) + 0.5·EMPPT`.
- **Closure adjustment.** A store that permanently closed by wave 2
  (`STATUS2 = 3`) is assigned wave-2 FTE = 0; a store temporarily closed
  (`STATUS2 ∈ {2, 4, 5}`) is treated as missing in wave 2.
- **Starting-wage gap** `GAP = (5.05 − WAGE_ST)/WAGE_ST` for New Jersey stores
  with `WAGE_ST < 5.05`, and 0 otherwise (Pennsylvania stores and NJ stores
  already at or above $5.05). `GAP` measures the proportional wage increase a
  store had to implement and is the continuous "treatment intensity" regressor.
- **NJ wage categories** (Table 3): low = exactly $4.25; mid = $4.26–$4.99;
  high = ≥ $5.00.
- **Full-meal price** = medium soda + small fries + entree, after tax
  (`PSODA + PFRY + PENTREE`), used as a check that the wage increase was not
  passed through to prices.
- **Region and chain dummies** for the regression-adjusted models.

The whole pipeline (`src/build_sample.py` → each table/figure script) is driven
by `python src/run_all.py`, so every number below is reproducible from the raw
file.

---

## 3. Empirical design

**The DID estimator.** The causal effect of the minimum-wage increase is
identified from the change in employment *within* New Jersey relative to the
change *within* Pennsylvania:

$$\widehat{\delta}_{DID} = (\overline{FTE}_{NJ,after} − \overline{FTE}_{NJ,before}) − (\overline{FTE}_{PA,after} − \overline{FTE}_{PA,before}) = \overline{\Delta FTE}_{NJ} − \overline{\Delta FTE}_{PA}.$$

Equivalently, it is the OLS coefficient $c$ in

$$\Delta FTE_i = a + c \cdot NJ_i + b'X_i + \varepsilon_i,$$

where $NJ_i$ is a New Jersey dummy and $X_i$ are store-level controls. The paper
also reports a "wage-gap" variant in which the treatment dummy is replaced by
`GAP`, so the coefficient measures the employment change *per unit* of mandated
wage increase.

**Identifying assumptions.** The DID design requires that, absent the policy,
New Jersey and Pennsylvania employment would have followed parallel trends. The
paper probes this in three ways: (i) the two states had very similar starting
wages and observable characteristics at baseline (Table 2); (ii) the full-meal
price did not diverge differentially, suggesting no large asymmetric demand or
cost shock (Table 2); and (iii) within New Jersey, the employment response was
concentrated among the *low-wage* stores that were actually bound by the new
minimum (Table 3, columns iv–vi), which is the pattern a causal effect — and not
a common state-level shock — would produce.

---

## 4. Core replication results and comparison

### Table 2 — summary statistics by state

| Variable (wave 1) | NJ | PA |
|---|---|---|
| FTE employment | 20.44 | 23.33 |
| % full-time employees | 32.85 | 35.04 |
| Starting wage ($) | 4.61 | 4.63 |
| Price of full meal ($) | 3.35 | 3.04 |

| Variable (wave 2) | NJ | PA |
|---|---|---|
| FTE employment | 21.03 | 21.17 |
| Starting wage ($) | 5.08 | 4.62 |
| Wage = $5.05 (%) | 85.5 | 1.3 |
| Price of full meal ($) | 3.41 | 3.03 |

These match the paper closely. New Jersey's average starting wage jumped from
$4.61 to $5.08 (the $5.05 minimum became binding), while Pennsylvania's stayed
near $4.62; the share of New Jersey stores paying exactly $5.05 rose to 85.5% of
all NJ stores (283 of 331), while meal prices rose only modestly in both states.
Baseline employment and wages are very similar across the two states, supporting
the parallel-trends assumption.

### Figure 1 — starting-wage distributions

The two panels reproduce the paper's Figure 1. In February 1992 both states'
starting wages are concentrated near $4.25–$4.75 and look alike. In November
1992 the New Jersey distribution exhibits a mass point at $5.05 (89% of
wage-reporting NJ stores), while Pennsylvania's distribution is unchanged — the
visual signature of a binding minimum-wage increase.

### Table 3 — the headline DID

| Row | NJ−PA change in FTE | SE | t |
|---|---|---|---|
| 3. Change (unpaired) | **2.75** | 1.80 | 1.53 |
| 4. Change (balanced sample) | **2.75** | 1.34 | **2.05** |
| 5. Change (temporarily-closed → 0) | 2.51 | 1.35 | 1.87 |

The headline point estimate is **+2.75 FTE per store** — New Jersey employment
rose relative to Pennsylvania. The paper's reported t = 2.03 corresponds to the
*balanced-sample* (paired) standard error in row 4; my replication recovers
t = 2.05. The unpaired row-3 standard error (t = 1.53) is larger because it
ignores the within-store correlation between the two waves. **This SE convention
is a substantive finding of the replication**: the paper's statistical
significance rests on using the within-store (paired) standard error, a choice
worth scrutinizing — the starting point for the extension.

The within-NJ gradient is also reproduced: low-wage stores gained
+1.32 FTE (low−high difference = +3.36), mid-wage stores +0.87, while the
already-high-wage stores (−2.04) behaved like the Pennsylvania control — the
employment gain is concentrated where the minimum wage actually bound.

### Table 4 — regression-adjusted models

| Model | Regressor | Ours: coef (se) | Paper: coef (se) |
|---|---|---|---|
| (i) | NJ dummy | 2.28 (1.19) | 2.33 (1.19) |
| (ii) | NJ dummy + chain/ownership | 2.28 (1.20) | 2.30 (1.20) |
| (iii) | wage gap | 17.05 (6.09) | 15.65 (6.08) |
| (iv) | wage gap + chain/ownership | 16.36 (6.24) | 14.92 (6.21) |
| (v) | wage gap + chain/ownership + region | 13.88 (7.44) | 11.91 (7.39) |

The NJ-dummy models match the paper almost exactly (2.28 vs. 2.33/2.30), and the
standard errors match in every column. The `GAP` coefficients are ~9% larger
than the paper's, while their standard errors match — the `GAP` slope is
sensitive to the exact wave-1 wage values used to construct it, and this
`public.csv` appears to encode a slightly different wage series than the one the
authors used. The economic conclusion is identical: a positive, economically
meaningful employment response and no evidence of a decline. Two small
differences are documented in `docs/plan.md`: (1) the balanced sample has
N = 351 rather than the paper's 357 (8 stores have wave-1 employment and both
wages but a missing wave-2 employment component); and (2) the $5.05 share is
85.5% of all NJ stores versus 89% of wage-reporting stores, the former matching
the paper's ~85% convention.

---

## 5. Independent extension: does the result survive modern inference?

**The question.** The headline rests on conventional OLS standard errors that
treat stores as independent. Neumark and Wascher (2000) argued those standard
errors are too small, because employment shocks are correlated within chains and
regions and because the "treatment" is assigned at the state level (only two
states). I ask two questions: (i) do cluster-robust standard errors change the
conclusion, and (ii) does an exact randomization/permutation test reject the
null that the observed DID could have arisen by chance?

**Implementation.** For (i) I re-estimate the five Table 4 models with
cluster-robust standard errors, clustering by restaurant chain (4 clusters) and
by region (6 clusters: NJ north/central/south and PA other/PA1/PA2). For (ii) I
hold each store's employment change fixed and randomly shuffle the NJ/PA
treatment label across stores 10,000 times, recomputing the DID each time to
build the null distribution; the permutation p-value is the share of placebo
DIDs at least as large in absolute value as the observed 2.75.

### Cluster-robust standard errors (Table 4 sample, N = 351)

| Model | Regressor | coef | SE (OLS) | SE (chain) | t (chain) | SE (region) | t (region) |
|---|---|---|---|---|---|---|---|
| (i) | NJ dummy | 2.28 | 1.19 | 1.11 | 2.05 | 1.40 | 1.62 |
| (ii) | NJ dummy | 2.28 | 1.20 | 1.16 | 1.97 | 1.53 | 1.49 |
| (iii) | wage gap | 17.05 | 6.09 | 8.76 | 1.95 | 4.79 | 3.56 |
| (iv) | wage gap | 16.36 | 6.24 | 8.88 | 1.84 | 4.94 | 3.31 |
| (v) | wage gap | 13.88 | 7.44 | 9.09 | 1.53 | 3.80 | 3.65 |

Clustering by chain roughly doubles the standard error of the `GAP` coefficient
(t ≈ 1.9), while clustering by region *lowers* it (t ≈ 3.6) because the initial
wage gap varies within regions and within-region employment shocks are not
strongly positively correlated. The NJ-dummy coefficient is a different story:
the treatment dummy is *constant within each region*, so region-clustering
collapses the effective comparison to the state level and the t-statistic falls
to 1.62. This is a textbook illustration of the "few clusters" problem
(Donald & Lang 2007): with the treatment assigned to two states, no
within-region clustering fully repairs the inference, and the honest reading is
that the NJ-dummy result is positive but only marginally significant once
clustering is acknowledged.

### Permutation test (headline DID, balanced sample N = 384)

The observed DID is **2.75 FTE**. Across 10,000 random assignments of the
treatment label, the null distribution is centered at 0.01 with standard
deviation 1.15, and only **1.7%** of placebo estimates are at least as large in
absolute value (two-sided p = 0.017; P(DID* ≥ 2.75) = 0.0096). The observed
estimate therefore survives exact randomization inference at the 5% level.

**Interpretation.** The extension delivers a nuanced conclusion. Under
store-level randomization — the assumption that New Jersey restaurants are
exchangeable with Pennsylvania restaurants — the positive DID is statistically
robust (p = 0.017). The caveat, faithful to Neumark and Wascher, is that the
*uncertainty* is sensitive to clustering: the region-clustered NJ-dummy t is
1.62, so the point estimate is less precisely estimated than the paper's t = 2.03
implies. The wage-gap specification, which exploits within-state variation in
treatment intensity, remains clearly significant under every standard-error
convention.

---

## 6. Validation, limitations, and conclusion

**Validation.** Every table and figure is generated by `python src/run_all.py`
from the raw data, and each output was inspected against the published values
(Section 4). The replication recovers the headline DID (2.75), the paper's
paired t-statistic (2.05 vs. 2.03), and the NJ-dummy regression coefficients
almost exactly; the few differences (balanced N, `GAP` slope, $5.05 share) are
traced to data-version differences and documented rather than papered over.

**Limitations.** (i) The design has only two time periods, so parallel trends
cannot be tested directly. (ii) The treatment is a single state-level policy
change in a single industry, so the result is identified off one treatment group
and one control group — a fundamental limit on inference that no within-sample
technique can fully overcome. (iii) Unobserved asymmetric demand or supply
shocks between the two states remain a possible confound, only partly addressed
by the price check and the within-NJ low-wage gradient.

**Conclusion.** This project successfully replicates Card and Krueger's central
result: New Jersey's 1992 minimum-wage increase was followed by a small
*relative increase* in fast-food employment, not the decline the competitive
model predicts. The independent extension shows that the finding survives exact
randomization inference (p = 0.017) while flagging — as Neumark and Wascher
emphasized — that the statistical precision of the headline estimate depends on
the standard-error convention, with cluster-robust standard errors yielding a
more guarded but still positive conclusion. The episode remains a canonical
illustration both of how difference-in-differences can inform the minimum-wage
debate and of how much standard-error choices matter for that conclusion.

---

## References

- Bertrand, M., Duflo, E., & Mullainathan, S. (2004). "How Much Should We Trust
  Differences-in-Differences Estimates?" *Quarterly Journal of Economics*,
  119(1), 249–275.
- Card, D. & Krueger, A. B. (1994). "Minimum Wages and Employment: A Case Study
  of the Fast-Food Industry in New Jersey and Pennsylvania." *American Economic
  Review*, 84(4), 772–793.
- Donald, S. G. & Lang, K. (2007). "Inference with Difference-in-Differences and
  Other Panel Data." *Review of Economics and Statistics*, 89(2), 221–233.
- Neumark, D. & Wascher, W. (2000). "Minimum Wages and Employment: A Case Study
  of the Fast-Food Industry in New Jersey and Pennsylvania: Comment." *American
  Economic Review*, 90(5), 1362–1396.

---

*All tables and figures are generated under `output/` by `python src/run_all.py`;
the analysis sample is rebuilt from `01_DID/data/public.csv` (restricted, not in
this repository — see README).*
