"""Replicate Table 4: reduced-form regressions for the change in FTE employment.

OLS of dFTE (= fte2 - fte1) on the NJ dummy or the initial wage gap, with
progressively more controls. Five columns:

  (i)   NJ dummy, no controls             -> coef 2.33 (se 1.19)
  (ii)  NJ dummy + chain/ownership        -> coef 2.30 (se 1.20)
  (iii) wage gap (GAP), no controls       -> coef 15.65 (se 6.08)
  (iv)  GAP + chain/ownership             -> coef 14.92 (se 6.21)
  (v)   GAP + chain/ownership + region    -> coef 11.91 (se 7.39)

Sample: stores with valid employment AND starting wage in both waves (paper:
357; this data version: 351 — see docs/plan.md "Open items"). Each model
reports the standard error of the regression (SER) and the joint-F p-value of
the included control variables.

Output: output/tables/table4.csv (long: model | regressor | coef | se | ser | p_controls).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
import pandas as pd
from statsmodels.regression.linear_model import OLS
from statsmodels.tools import add_constant

from config import ANALYSIS_SAMPLE, TABLES_DIR

CHAIN_OWN = ["kfc", "roy_rogers", "wendys", "co_owned"]
REGION = ["nj_central", "nj_south", "pa_ne_philly", "pa_easton"]

# column -> (key regressor, control groups in order)
SPECS = [
    ("i", "STATE", []),
    ("ii", "STATE", [CHAIN_OWN]),
    ("iii", "gap", []),
    ("iv", "gap", [CHAIN_OWN]),
    ("v", "gap", [CHAIN_OWN, REGION]),
]


def _fit(frame, y, cols):
    X = frame[cols] if cols else pd.DataFrame(index=frame.index)
    return OLS(y, add_constant(X)).fit()


def run() -> None:
    df = pd.read_csv(ANALYSIS_SAMPLE)
    df["nj"] = df["STATE"]  # readable NJ dummy name

    # Balanced sample: employment AND starting wage in both waves.
    bal = df[df.fte1.notna() & df.fte2.notna() & df.WAGE_ST.notna() & df.WAGE_ST2.notna()].copy()
    y = bal["dfte"]

    records = []
    for col, key, control_groups in SPECS:
        cols = [key] + [c for g in control_groups for c in g]
        model = _fit(bal, y, cols)
        controls = [c for g in control_groups for c in g]

        # Joint-F p-value for excluding all controls (restricted model).
        p_controls = np.nan
        if controls:
            model_r = _fit(bal, y, [key])
            _, p_controls, _ = model.compare_f_test(model_r)

        records.append(
            {
                "model": f"({col})",
                "regressor": "NJ dummy" if key == "STATE" else "wage gap",
                "coef": model.params[key],
                "se": model.bse[key],
                "ser": np.sqrt(model.ssr / model.df_resid),
                "p_controls": p_controls,
                "n": int(model.nobs),
            }
        )

    out = pd.DataFrame(records)
    out.to_csv(TABLES_DIR / "table4.csv", index=False)

    print("Table 4 — reduced-form models for change in FTE employment")
    print(f"Balanced sample N = {len(bal)}; dep.var mean = {y.mean():.3f}, sd = {y.std():.3f}")
    for r in records:
        print(
            f"{r['model']:>4s} {r['regressor']:>10s} | coef {r['coef']:7.3f} (se {r['se']:5.2f})"
            f" | SER {r['ser']:.3f} | p(controls) {r['p_controls']:.3f}"
        )
    print(f"Wrote {TABLES_DIR / 'table4.csv'}")


if __name__ == "__main__":
    run()
