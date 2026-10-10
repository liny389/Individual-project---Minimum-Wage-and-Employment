# Card & Krueger (1994) — Replication and Extension

*ECON6067 Individual Project — [Your name / student ID]*

> TODO: 1–2 paragraph abstract summarizing the research question, the DID
> design, the replication result (no employment decline; the headline DID
> estimate), and the independent extension.

---

## 1. Research question and motivation

- What question does the paper answer?
- The economic mechanism (textbook competitive model predicts employment falls;
  monopsony/search models can rationalize the opposite).
- Why New Jersey / Pennsylvania is a natural quasi-experiment.
- Why this paper matters (the minimum-wage debate; the later Neumark–Wascher
  controversy over the standard errors).

## 2. Data, sample construction, and variable definitions

- Data source: course Package 01 (`public.csv`), 410 fast-food restaurants.
- Sample design (waves 1 and 2; treatment/control; chain composition).
- Variable definitions: FTE, full-meal price, wage gap GAP, region dummies,
  closure adjustment. (Cross-reference `src/common.py` and `docs/plan.md`.)
- Data-cleaning choices: missing values, closed-store treatment.

## 3. Empirical design

- The difference-in-differences estimator:
  `(NJ_after − NJ_before) − (PA_after − PA_before)`.
- Regression form: `ΔFTE_i = a + c·NJ_i + b·X_i + ε_i`, and the GAP variant.
- Identifying assumptions (parallel trends, no differential shocks) and how the
  paper probes them (within-NJ high-wage comparison, price check).

## 4. Core replication results and comparison

- Table 2 (summary statistics by state).
- Figure 1 (wage distributions).
- Table 3 (DID of FTE employment) — headline estimate 2.76 (t = 2.03).
- Table 4 (regression-adjusted models).
- Side-by-side comparison with the paper; explain any numeric differences
  (sample restriction, SE convention, rounding).

## 5. Independent extension

- The economic question the extension answers.
- Empirical approach and implementation.
- Results, validation, and interpretation.

## 6. Validation, limitations, and conclusion

- Robustness checks performed (balanced sample, closure treatment, alternative
  FTE weights, weighted regressions).
- Limitations (two waves only, single industry/state pair, unobserved demand
  shocks).
- Conclusion.

## References

- Card & Krueger (1994), AER 84(4), 772–793.
- [Add: Neumark & Wascher (2000), etc., as relevant to the extension.]

---

*Tables and figures referenced above are generated under `output/` by
`python src/run_all.py`.*
